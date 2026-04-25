"""Phase 3 — polling triggers.

For workflows whose trigger type is one of:
  - "http_poll"      : hit a URL, compare response hash, fire on change
  - "rss"            : poll a feed, fire for each new item
  - "imap"           : IMAP UNSEEN scan, fire per new unread mail
  - "file_watch"     : watch a directory, fire on new / modified files

Each poller is a single scheduler tick that iterates every active
workflow with its trigger type and enqueues runs for new signals.

State (last seen hash, last seen mailbox UID, seen file mtimes) is
kept in Mongo `workflow_poll_state` keyed by workflow_id so MAARS
restarts don't re-fire everything.

Wired into services/scheduler.py as 4 interval jobs (every 60s).
"""
from __future__ import annotations
import email as _email
import email.policy as _email_policy
import hashlib
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


async def _get_state(workflow_id: str) -> dict:
    from db import db
    doc = await db.workflow_poll_state.find_one({"_id": workflow_id})
    return doc or {}


async def _set_state(workflow_id: str, **fields) -> None:
    from db import db
    await db.workflow_poll_state.update_one(
        {"_id": workflow_id},
        {"$set": {**fields, "updated_at": time.time(), "_id": workflow_id}},
        upsert=True,
    )


# ── http_poll ────────────────────────────────────────────────────────

async def _poll_one_http(wf: dict) -> int:
    from services.http_client import get_client
    from services.workflows import workflow_executor
    trig = wf.get("trigger") or {}
    url = trig.get("url")
    if not url:
        return 0
    try:
        client = await get_client()
        r = await client.request(
            trig.get("method", "GET"), url,
            headers=trig.get("headers") or {},
            timeout=float(trig.get("timeout_s", 30)),
        )
    except Exception as exc:
        logger.info("http_poll %s failed: %s", wf.get("workflow_id"), exc)
        return 0

    digest = hashlib.sha256(r.content).hexdigest()
    state = await _get_state(wf["workflow_id"])
    if state.get("last_hash") == digest and not trig.get("always_fire"):
        return 0
    await _set_state(wf["workflow_id"], last_hash=digest, last_status=r.status_code)

    try:
        payload = r.json() if (r.headers.get("content-type") or "").startswith("application/json") else r.text
    except Exception:
        payload = r.text
    await workflow_executor._enqueue_run(
        wf,
        trigger_meta={"source": "http_poll", "status": r.status_code, "digest": digest[:16]},
        overrides={"http_body": payload, "http_headers": dict(r.headers), "http_status": r.status_code},
    )
    return 1


async def http_poll_tick() -> int:
    from db import db
    fired = 0
    async for wf in db.workflows.find({"active": True, "trigger.type": "http_poll"}):
        fired += await _poll_one_http(wf)
    return fired


# ── rss ──────────────────────────────────────────────────────────────

def _parse_rss(xml_bytes: bytes) -> list[dict]:
    """Lightweight feed parser — supports RSS 2.0 + Atom 1.0.
    No external dep; good enough for trigger fan-out."""
    import re as _re
    text = xml_bytes.decode("utf-8", errors="replace")
    items: list[dict] = []

    # RSS 2.0 <item>
    for m in _re.finditer(r"<item\b[^>]*>(.*?)</item>", text, _re.DOTALL):
        inner = m.group(1)
        def _field(tag):
            m2 = _re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", inner, _re.DOTALL)
            return (m2.group(1) if m2 else "").strip()
        items.append({
            "title": _field("title"),
            "link":  _field("link"),
            "guid":  _field("guid") or _field("link"),
            "pubDate": _field("pubDate"),
            "description": _field("description"),
        })

    # Atom <entry>
    if not items:
        for m in _re.finditer(r"<entry\b[^>]*>(.*?)</entry>", text, _re.DOTALL):
            inner = m.group(1)
            def _field(tag):
                m2 = _re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", inner, _re.DOTALL)
                return (m2.group(1) if m2 else "").strip()
            def _link():
                m2 = _re.search(r'<link\b[^>]*href="([^"]+)"', inner)
                return m2.group(1) if m2 else ""
            items.append({
                "title":    _field("title"),
                "link":     _link(),
                "guid":     _field("id") or _link(),
                "pubDate":  _field("updated") or _field("published"),
                "description": _field("summary") or _field("content"),
            })
    return items


async def _poll_one_rss(wf: dict) -> int:
    from services.http_client import get_client
    from services.workflows import workflow_executor
    trig = wf.get("trigger") or {}
    url = trig.get("url")
    if not url:
        return 0
    try:
        client = await get_client()
        r = await client.get(url, timeout=30)
    except Exception as exc:
        logger.info("rss %s failed: %s", wf.get("workflow_id"), exc)
        return 0
    items = _parse_rss(r.content)
    state = await _get_state(wf["workflow_id"])
    seen = set(state.get("seen_guids") or [])
    new_items = [it for it in items if it.get("guid") and it["guid"] not in seen]
    if not new_items:
        await _set_state(wf["workflow_id"], seen_guids=list(seen)[-1000:])
        return 0
    # Enqueue one run per new item.
    n = 0
    for it in new_items[: int(trig.get("max_per_tick", 20))]:
        await workflow_executor._enqueue_run(
            wf,
            trigger_meta={"source": "rss", "feed": url},
            overrides={"rss_item": it},
        )
        seen.add(it["guid"])
        n += 1
    await _set_state(wf["workflow_id"], seen_guids=list(seen)[-1000:])
    return n


async def rss_tick() -> int:
    from db import db
    fired = 0
    async for wf in db.workflows.find({"active": True, "trigger.type": "rss"}):
        fired += await _poll_one_rss(wf)
    return fired


# ── imap ─────────────────────────────────────────────────────────────
# Uses imaplib via a thread (imaplib is blocking). Good enough at 1/min.

async def _poll_one_imap(wf: dict) -> int:
    import asyncio as _a
    import imaplib as _imap

    trig = wf.get("trigger") or {}
    host = trig.get("host") or os.environ.get("IMAP_HOST")
    user = trig.get("user") or os.environ.get("IMAP_USER")
    passwd = trig.get("password") or os.environ.get("IMAP_PASSWORD")
    port = int(trig.get("port", 993))
    folder = trig.get("folder", "INBOX")
    if not (host and user and passwd):
        return 0

    def _do_scan():
        try:
            c = _imap.IMAP4_SSL(host, port)
            c.login(user, passwd)
            c.select(folder)
            typ, data = c.search(None, "(UNSEEN)")
            uids = (data[0] or b"").split() if typ == "OK" else []
            out = []
            for uid in uids[:50]:
                typ, msg_data = c.fetch(uid, "(RFC822)")
                if typ != "OK" or not msg_data:
                    continue
                raw = msg_data[0][1]
                msg = _email.message_from_bytes(raw, policy=_email_policy.default)
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_content()
                            break
                else:
                    try: body = msg.get_content()
                    except Exception: body = ""
                out.append({
                    "uid": uid.decode(),
                    "from": str(msg.get("From") or ""),
                    "subject": str(msg.get("Subject") or ""),
                    "date": str(msg.get("Date") or ""),
                    "message_id": str(msg.get("Message-ID") or ""),
                    "body": body[:20000],
                })
            c.close(); c.logout()
            return out
        except Exception as e:
            logger.info("imap poll failed: %s", e)
            return []

    messages = await _a.to_thread(_do_scan)
    if not messages:
        return 0

    from services.workflows import workflow_executor
    state = await _get_state(wf["workflow_id"])
    seen = set(state.get("seen_uids") or [])
    fired = 0
    for m in messages:
        if m["uid"] in seen:
            continue
        await workflow_executor._enqueue_run(
            wf,
            trigger_meta={"source": "imap", "folder": folder},
            overrides={"email": m},
        )
        seen.add(m["uid"])
        fired += 1
    await _set_state(wf["workflow_id"], seen_uids=list(seen)[-2000:])
    return fired


async def imap_tick() -> int:
    from db import db
    fired = 0
    async for wf in db.workflows.find({"active": True, "trigger.type": "imap"}):
        fired += await _poll_one_imap(wf)
    return fired


# ── file_watch ───────────────────────────────────────────────────────

async def _poll_one_file(wf: dict) -> int:
    from services.workflows import workflow_executor
    trig = wf.get("trigger") or {}
    directory = trig.get("directory")
    pattern = trig.get("pattern", "*")
    if not directory:
        return 0
    root = Path(directory)
    if not root.exists() or not root.is_dir():
        return 0
    state = await _get_state(wf["workflow_id"])
    seen: dict[str, float] = state.get("mtimes") or {}
    fired = 0
    current: dict[str, float] = {}
    for p in root.glob(pattern):
        if p.is_file():
            key = str(p)
            current[key] = p.stat().st_mtime
    # New or modified
    for key, mt in current.items():
        if key not in seen or seen[key] < mt:
            await workflow_executor._enqueue_run(
                wf,
                trigger_meta={"source": "file_watch"},
                overrides={"file": {"path": key, "mtime": mt, "size": Path(key).stat().st_size}},
            )
            fired += 1
    await _set_state(wf["workflow_id"], mtimes=current)
    return fired


async def file_watch_tick() -> int:
    from db import db
    fired = 0
    async for wf in db.workflows.find({"active": True, "trigger.type": "file_watch"}):
        fired += await _poll_one_file(wf)
    return fired


# ── Registered scheduler entrypoint ──────────────────────────────────

async def run_all_polls() -> dict[str, int]:
    """One unified poller call — returns a count per trigger type.
    Simpler to register one scheduler job than four."""
    http = await http_poll_tick()
    rss  = await rss_tick()
    imap = await imap_tick()
    fw   = await file_watch_tick()
    return {"http_poll": http, "rss": rss, "imap": imap, "file_watch": fw}
