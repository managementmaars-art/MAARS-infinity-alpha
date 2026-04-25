"""Expanded tool library for workflow_executor — the "n8n-style" nodes.

Each tool is `async def fn(user_id, params, prev_output, ctx) -> dict`.
`ctx` is the full workflow-runtime context (state, trigger, workflow,
run) so tools that need nested access (loop, sub_workflow, merge) can
reach it. Simple tools ignore ctx.

Registered into workflow_executor.TOOL_REGISTRY at import time.
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ── Phase 1: core n8n-parity tools ───────────────────────────────────

async def t_http_request(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Generic HTTP request node. Replaces api_call."""
    url = params.get("url")
    if not url:
        return {"ok": False, "error": "url required"}
    method = str(params.get("method", "GET")).upper()
    headers = dict(params.get("headers") or {})
    body = params.get("body")
    query = params.get("query") or {}
    timeout = float(params.get("timeout_s", 30))
    auth = params.get("auth")          # {"type":"bearer","token":"..."} | {"type":"basic","user":"","pass":""}

    if auth:
        if auth.get("type") == "bearer" and auth.get("token"):
            headers.setdefault("Authorization", f"Bearer {auth['token']}")
        elif auth.get("type") == "basic":
            import base64
            blob = base64.b64encode(f"{auth.get('user','')}:{auth.get('pass','')}".encode()).decode()
            headers.setdefault("Authorization", f"Basic {blob}")
        elif auth.get("type") == "header" and auth.get("name"):
            headers[auth["name"]] = auth.get("value", "")

    from services.http_client import get_client
    client = await get_client()
    try:
        resp = await client.request(
            method, url, headers=headers, params=query,
            json=body if isinstance(body, (dict, list)) else None,
            content=body if isinstance(body, (str, bytes)) else None,
            timeout=timeout,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:400]}

    ct = (resp.headers.get("content-type") or "").lower()
    try:
        if "application/json" in ct:
            payload = resp.json()
        else:
            payload = resp.text
    except Exception:
        payload = resp.text

    return {
        "ok": 200 <= resp.status_code < 400,
        "status": resp.status_code,
        "headers": dict(resp.headers),
        "body": payload,
    }


async def t_set(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Reshape the previous node's output into a new object.

    params.fields: {"new_name": "{{prev.first_name}}", "email_lower":
    "{{prev.email | lower}}"}. Expression resolution already applied
    before this function runs — so params.fields values are plain
    strings/values.

    params.mode:
      "merge"   — new fields merged onto prev (default)
      "replace" — ONLY the new fields are output
    """
    fields = params.get("fields") or {}
    mode = params.get("mode", "merge")
    if mode == "replace":
        return {**fields, "ok": True}
    # Merge mode: start from inp, overlay fields, FORCE ok=True last so
    # a failed-upstream output doesn't drag ok:false into this node's result.
    return {**inp, **fields, "ok": True}


async def t_filter(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Keep array items matching a predicate.

    params.array: list or path to array in prev output
    params.predicate: {"field":"status","op":"==","value":"active"}
    op: == != in contains > < exists
    """
    arr = params.get("array")
    if arr is None:
        arr = inp.get("items") or inp.get("data") or []
    pred = params.get("predicate") or {}
    field = pred.get("field", "")
    op = pred.get("op", "==")
    value = pred.get("value")

    def match(item):
        v = item.get(field) if isinstance(item, dict) else item
        if op == "==":       return v == value
        if op == "!=":       return v != value
        if op == "in":       return v in (value or [])
        if op == "contains": return value in (v or "")
        if op == ">":        return (v or 0) > (value or 0)
        if op == "<":        return (v or 0) < (value or 0)
        if op == "exists":   return v is not None
        return False

    kept = [x for x in arr if match(x)]
    return {"ok": True, "items": kept, "count": len(kept), "total": len(arr)}


async def t_loop(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """forEach node — iterate over an array and run a named sub-graph
    (or just collect outputs of a single-tool op) per item.

    params.array: list or path
    params.max_parallel: concurrent item processing (default 4, max 20)
    params.tool: name of a TOOL_REGISTRY tool to run per item
    params.tool_params_template: dict — expressions like {{item}} resolve
                                  against each item.

    Returns {ok, results:[...], errors:[{i, error}]}
    """
    from services import expressions as _ex
    from services.workflows.workflow_executor import TOOL_REGISTRY

    arr = params.get("array")
    if arr is None:
        arr = inp.get("items") or inp.get("data") or []
    if not isinstance(arr, list):
        return {"ok": False, "error": "array must be a list"}

    tool = params.get("tool")
    template = params.get("tool_params_template") or params.get("params_per_item") or {}
    if tool not in TOOL_REGISTRY:
        return {"ok": False, "error": f"unknown per-item tool '{tool}'"}
    fn = TOOL_REGISTRY[tool]

    max_parallel = max(1, min(int(params.get("max_parallel", 4)), 20))
    sem = asyncio.Semaphore(max_parallel)
    results: list[Any] = [None] * len(arr)
    errors: list[dict] = []

    async def _one(i: int, item: Any) -> None:
        async with sem:
            try:
                # Build a per-item ctx: inject `item` + `index`.
                item_ctx = {**(ctx or {}), "item": item, "index": i}
                item_params = _ex.resolve(template, item_ctx)
                r = await _invoke_tool(fn, user_id, item_params, {"item": item, "index": i}, item_ctx)
                results[i] = r
            except Exception as exc:
                errors.append({"i": i, "error": str(exc)[:300]})
                results[i] = {"ok": False, "error": str(exc)[:300]}

    await asyncio.gather(*(_one(i, it) for i, it in enumerate(arr)))
    return {"ok": True, "results": results, "errors": errors, "count": len(arr)}


async def t_merge(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Join outputs of multiple upstream nodes.

    params.sources: list of node ids whose outputs to merge
    params.mode:
      "combine" — produce a single dict of {node_id: output}
      "concat"  — concatenate arrays found at params.key from each source
      "first_ok"— return the first source whose output.ok is true
    """
    state = (ctx or {}).get("state") or {}
    sources = params.get("sources") or []
    mode = params.get("mode", "combine")

    if mode == "concat":
        key = params.get("key", "items")
        out: list = []
        for s in sources:
            part = (state.get(s) or {}).get(key) or []
            if isinstance(part, list):
                out.extend(part)
        return {"ok": True, key: out, "count": len(out)}

    if mode == "first_ok":
        for s in sources:
            val = state.get(s) or {}
            if val.get("ok"):
                return {"ok": True, "source": s, "value": val}
        return {"ok": False, "error": "no source returned ok=true"}

    # combine
    return {"ok": True, **{s: state.get(s) for s in sources}}


async def t_sub_workflow(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Call another workflow by id. Returns the final state of the child run.

    params.workflow_id: id of the workflow to run
    params.overrides: optional dict passed to the child's root nodes
    params.wait: default True — waits for completion. False = fire-and-forget.
    """
    from db import db
    from services.workflows import workflow_executor
    wfid = params.get("workflow_id")
    if not wfid:
        return {"ok": False, "error": "workflow_id required"}
    child = await db.workflows.find_one({"workflow_id": wfid})
    if not child:
        return {"ok": False, "error": f"workflow '{wfid}' not found"}

    overrides = params.get("overrides") or inp

    if not params.get("wait", True):
        run_id = await workflow_executor._enqueue_run(child, overrides=overrides,
                                                       trigger_meta={"source": "sub_workflow", "parent": ctx.get("run", {}).get("id")})
        return {"ok": True, "run_id": run_id, "async": True}

    # synchronous sub-run
    run_id = await workflow_executor._enqueue_run(child, overrides=overrides,
                                                   trigger_meta={"source": "sub_workflow", "parent": ctx.get("run", {}).get("id")})
    final = await workflow_executor.run(run_id, child, overrides=overrides)
    return {"ok": final.get("status") == "completed", "child_run": final}


async def t_code_js(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Sandboxed JavaScript eval via `node` subprocess.

    params.code: JS source. Available globals: `input` (prev output),
    `ctx` (workflow context).
    params.timeout_s: default 5, max 30.

    SECURITY: still executes arbitrary JS. Use feature_flag gating in
    prod. Subprocess isolation + timeout + no network helpers, but the
    JS can still make outbound HTTP unless you run node with --disallow-net
    (not available in all Node versions). Ship this behind an admin flag.
    """
    code = params.get("code") or ""
    if not code:
        return {"ok": False, "error": "code required"}
    timeout = max(1.0, min(float(params.get("timeout_s", 5)), 30.0))

    wrapper = f"""
try {{
  const input = {json.dumps(inp, default=str)};
  const ctx   = {json.dumps({k: v for k, v in (ctx or {}).items() if k != "state"}, default=str)};
  const __r = (async () => {{ {code} }})();
  Promise.resolve(__r).then(v => {{
    process.stdout.write(JSON.stringify({{ok:true,result:v===undefined?null:v}}));
  }}).catch(e => {{
    process.stdout.write(JSON.stringify({{ok:false,error:String(e)}}));
  }});
}} catch (e) {{
  process.stdout.write(JSON.stringify({{ok:false,error:String(e)}}));
}}
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(wrapper)
        path = f.name
    try:
        proc = await asyncio.create_subprocess_exec(
            "node", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return {"ok": False, "error": f"timeout after {timeout}s"}
        if proc.returncode != 0:
            return {"ok": False, "error": (err.decode("utf-8", errors="replace"))[:500]}
        try:
            return json.loads(out.decode("utf-8", errors="replace") or "{}")
        except json.JSONDecodeError:
            return {"ok": False, "error": "invalid stdout", "raw": out[:400].decode("utf-8", errors="replace")}
    except FileNotFoundError:
        return {"ok": False, "error": "Node.js not installed. code_js requires `node` on PATH."}
    finally:
        try: os.unlink(path)
        except Exception: pass


async def t_code_python(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Sandboxed Python eval via subprocess.

    params.code: Python source. Available names: `input`, `ctx`. The script
    should set `result = ...`. Output is that final `result`.
    params.timeout_s: default 5, max 30.

    Subprocess runs with -I (isolated mode), no .pythonrc, no site
    packages — still can make network calls via stdlib. Gate behind
    admin feature flag in prod.
    """
    code = params.get("code") or ""
    if not code:
        return {"ok": False, "error": "code required"}
    timeout = max(1.0, min(float(params.get("timeout_s", 5)), 30.0))

    preamble = (
        "import json, sys\n"
        f"input = {json.dumps(inp, default=str)}\n"
        f"ctx = {json.dumps({k:v for k,v in (ctx or {}).items() if k != 'state'}, default=str)}\n"
        "result = None\n"
    )
    postamble = "\nsys.stdout.write(json.dumps({'ok': True, 'result': result}, default=str))\n"
    script = preamble + code + postamble

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(script)
        path = f.name
    try:
        import sys as _sys
        proc = await asyncio.create_subprocess_exec(
            _sys.executable, "-I", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return {"ok": False, "error": f"timeout after {timeout}s"}
        if proc.returncode != 0:
            return {"ok": False, "error": err.decode("utf-8", errors="replace")[:500]}
        try:
            return json.loads(out.decode("utf-8", errors="replace") or "{}")
        except json.JSONDecodeError:
            return {"ok": False, "error": "invalid stdout", "raw": out[:400].decode("utf-8", errors="replace")}
    finally:
        try: os.unlink(path)
        except Exception: pass


# ── Shared helper: tool invocation supporting both old and new signatures
async def _invoke_tool(fn, user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Newer tools take (user_id, params, inp, ctx); older ones take
    (user_id, params, inp). Detect via parameter count."""
    import inspect
    sig = inspect.signature(fn)
    if len(sig.parameters) >= 4:
        return await fn(user_id, params, inp, ctx)
    return await fn(user_id, params, inp)


# ── Phase 2: database tools ──────────────────────────────────────────

async def t_sql_query(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Run SQL against Postgres or MySQL.

    params.dsn: connection string (postgresql://... or mysql://...).
                falls back to env MAARS_DEFAULT_SQL_DSN.
    params.query: SQL string (parameterized via %s or :named binding)
    params.params: list or dict of bind values
    """
    dsn = params.get("dsn") or os.environ.get("MAARS_DEFAULT_SQL_DSN")
    q = params.get("query")
    if not (dsn and q):
        return {"ok": False, "error": "dsn and query required"}
    try:
        if dsn.startswith("postgres"):
            import asyncpg
            conn = await asyncpg.connect(dsn=dsn)
            try:
                bind = params.get("params") or []
                if q.lstrip().upper().startswith(("SELECT", "WITH")):
                    rows = await conn.fetch(q, *bind)
                    return {"ok": True, "rows": [dict(r) for r in rows], "count": len(rows)}
                status = await conn.execute(q, *bind)
                return {"ok": True, "status": str(status)}
            finally:
                await conn.close()
        if dsn.startswith("mysql"):
            import aiomysql
            from urllib.parse import urlparse
            u = urlparse(dsn)
            pool = await aiomysql.create_pool(
                host=u.hostname, port=u.port or 3306,
                user=u.username, password=u.password,
                db=(u.path or "/").lstrip("/"),
                maxsize=2,
            )
            try:
                async with pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cur:
                        await cur.execute(q, params.get("params") or ())
                        if q.lstrip().upper().startswith("SELECT"):
                            rows = await cur.fetchall()
                            return {"ok": True, "rows": list(rows), "count": len(rows)}
                        await conn.commit()
                        return {"ok": True, "affected": cur.rowcount}
            finally:
                pool.close()
                await pool.wait_closed()
    except ImportError as exc:
        return {"ok": False, "error": f"{exc} — install asyncpg for Postgres or aiomysql for MySQL"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:400]}
    return {"ok": False, "error": f"unsupported DSN scheme: {dsn.split(':',1)[0]}"}


async def t_mongo_query(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Query MongoDB. Defaults to MAARS's own Mongo if no uri passed.

    params.uri: optional override connection string
    params.collection: required
    params.op: "find" | "find_one" | "insert_one" | "update_one" | "delete_one" | "aggregate"
    params.filter / params.doc / params.update / params.pipeline: per op
    params.limit: default 100 (for find)
    """
    from db import db as default_db
    if params.get("uri"):
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(params["uri"])
        dbh = client.get_default_database()
    else:
        dbh = default_db

    coll = params.get("collection")
    if not coll:
        return {"ok": False, "error": "collection required"}
    op = params.get("op", "find")
    c = dbh[coll]
    try:
        if op == "find":
            cursor = c.find(params.get("filter") or {}, params.get("projection") or None).limit(int(params.get("limit", 100)))
            rows = await cursor.to_list(int(params.get("limit", 100)))
            return {"ok": True, "rows": [_mongo_clean(r) for r in rows], "count": len(rows)}
        if op == "find_one":
            r = await c.find_one(params.get("filter") or {}, params.get("projection") or None)
            return {"ok": True, "row": _mongo_clean(r) if r else None}
        if op == "insert_one":
            r = await c.insert_one(params.get("doc") or {})
            return {"ok": True, "inserted_id": str(r.inserted_id)}
        if op == "update_one":
            r = await c.update_one(params.get("filter") or {}, params.get("update") or {}, upsert=bool(params.get("upsert")))
            return {"ok": True, "matched": r.matched_count, "modified": r.modified_count, "upserted_id": str(r.upserted_id) if r.upserted_id else None}
        if op == "delete_one":
            r = await c.delete_one(params.get("filter") or {})
            return {"ok": True, "deleted": r.deleted_count}
        if op == "aggregate":
            rows = await c.aggregate(params.get("pipeline") or []).to_list(int(params.get("limit", 500)))
            return {"ok": True, "rows": [_mongo_clean(r) for r in rows], "count": len(rows)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:400]}
    return {"ok": False, "error": f"unknown op '{op}'"}


def _mongo_clean(row):
    if row is None: return None
    row = dict(row)
    if "_id" in row:
        row["_id"] = str(row["_id"])
    return row


# ── Phase 2: messaging ───────────────────────────────────────────────

async def t_slack_send(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Send a message to a Slack channel via bot token.
    Expects SLACK_BOT_TOKEN in env or params.token."""
    token = params.get("token") or os.environ.get("SLACK_BOT_TOKEN")
    channel = params.get("channel")
    text = params.get("text") or ""
    if not (token and channel and text):
        return {"ok": False, "error": "token, channel, text required"}
    from services.http_client import get_client
    client = await get_client()
    r = await client.post("https://slack.com/api/chat.postMessage",
                          headers={"Authorization": f"Bearer {token}"},
                          json={"channel": channel, "text": text,
                                **({"blocks": params.get("blocks")} if params.get("blocks") else {})})
    data = r.json() if r.text else {}
    return {"ok": bool(data.get("ok")), "status": r.status_code, **data}


async def t_discord_send(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """POST to a Discord webhook URL."""
    url = params.get("webhook_url") or os.environ.get("DISCORD_WEBHOOK_URL")
    content = params.get("content") or ""
    if not url:
        return {"ok": False, "error": "webhook_url required"}
    from services.http_client import get_client
    client = await get_client()
    body = {"content": content}
    if params.get("embeds"):
        body["embeds"] = params["embeds"]
    r = await client.post(url, json=body)
    return {"ok": 200 <= r.status_code < 300, "status": r.status_code}


async def t_telegram_send(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Send via bot token + chat_id."""
    token = params.get("token") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = params.get("chat_id")
    text = params.get("text") or ""
    if not (token and chat_id):
        return {"ok": False, "error": "token and chat_id required"}
    from services.http_client import get_client
    client = await get_client()
    r = await client.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id": chat_id, "text": text,
                                "parse_mode": params.get("parse_mode", "HTML")})
    data = r.json() if r.text else {}
    return {"ok": bool(data.get("ok")), **data}


# ── Phase 2: docs (Google Sheets / Notion / Airtable) ────────────────

async def t_google_sheets_append(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Append a row to a Google Sheet. Uses the user's Google OAuth
    credentials (credential_vault key `google`) with scope
    https://www.googleapis.com/auth/spreadsheets."""
    from services import credential_vault
    cred = await credential_vault.get("google", user_id=user_id, kind="oauth")
    if not cred or not cred.secret:
        return {"ok": False, "error": "no google oauth credential for user"}
    sid = params.get("spreadsheet_id")
    rng = params.get("range", "Sheet1!A:Z")
    values = params.get("values") or [inp.get("row") or list(inp.values())]
    from services.http_client import get_client
    client = await get_client()
    r = await client.post(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{rng}:append",
        params={"valueInputOption": "USER_ENTERED"},
        headers={"Authorization": f"Bearer {cred.secret}", "Content-Type": "application/json"},
        json={"values": values},
    )
    return {"ok": 200 <= r.status_code < 300, "status": r.status_code, "body": r.json() if r.text else {}}


async def t_notion_create(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Create a page in a Notion database."""
    token = params.get("token") or os.environ.get("NOTION_TOKEN")
    db_id = params.get("database_id")
    props = params.get("properties") or {}
    if not (token and db_id):
        return {"ok": False, "error": "token and database_id required"}
    from services.http_client import get_client
    client = await get_client()
    r = await client.post("https://api.notion.com/v1/pages",
                          headers={"Authorization": f"Bearer {token}",
                                   "Notion-Version": "2022-06-28",
                                   "Content-Type": "application/json"},
                          json={"parent": {"database_id": db_id}, "properties": props})
    return {"ok": r.status_code < 400, "status": r.status_code, "body": r.json() if r.text else {}}


async def t_airtable_append(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Create a record in an Airtable base."""
    token = params.get("token") or os.environ.get("AIRTABLE_TOKEN")
    base_id = params.get("base_id")
    table = params.get("table")
    fields = params.get("fields") or inp
    if not (token and base_id and table):
        return {"ok": False, "error": "token, base_id, table required"}
    from services.http_client import get_client
    client = await get_client()
    r = await client.post(f"https://api.airtable.com/v0/{base_id}/{table}",
                          headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                          json={"fields": fields})
    return {"ok": r.status_code < 400, "status": r.status_code, "body": r.json() if r.text else {}}


# ── Phase 2: files (local + S3) ──────────────────────────────────────

async def t_file_read(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Read a local file (rooted under MAARS_WORKSPACE_DIR for safety)."""
    root = Path(os.environ.get("MAARS_WORKSPACE_DIR", "./workspace")).resolve()
    rel = params.get("path", "")
    target = (root / rel).resolve()
    # path-traversal guard
    try:
        target.relative_to(root)
    except ValueError:
        return {"ok": False, "error": "path outside workspace"}
    if not target.exists() or not target.is_file():
        return {"ok": False, "error": "file not found"}
    data = target.read_text(encoding=params.get("encoding", "utf-8"), errors="replace")
    return {"ok": True, "path": str(target.relative_to(root)), "content": data, "size": target.stat().st_size}


async def t_file_write(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Write a local file (rooted under MAARS_WORKSPACE_DIR)."""
    root = Path(os.environ.get("MAARS_WORKSPACE_DIR", "./workspace")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    rel = params.get("path", "")
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return {"ok": False, "error": "path outside workspace"}
    content = params.get("content", "")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(str(content), encoding=params.get("encoding", "utf-8"))
    return {"ok": True, "path": str(target.relative_to(root)), "size": len(str(content))}


async def t_s3_put(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Upload to an S3-compatible store. Uses boto3 with env-var creds
    or params.aws_* overrides."""
    try:
        import boto3
    except ImportError:
        return {"ok": False, "error": "boto3 not installed"}
    bucket = params.get("bucket")
    key = params.get("key")
    body = params.get("body", inp.get("content", ""))
    if not (bucket and key):
        return {"ok": False, "error": "bucket and key required"}
    try:
        s3 = boto3.client("s3",
                          endpoint_url=params.get("endpoint") or os.environ.get("AWS_S3_ENDPOINT"),
                          region_name=params.get("region") or os.environ.get("AWS_REGION"))
        s3.put_object(Bucket=bucket, Key=key, Body=body.encode() if isinstance(body, str) else body,
                      ContentType=params.get("content_type", "application/octet-stream"))
        return {"ok": True, "bucket": bucket, "key": key}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:400]}


async def t_s3_get(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Fetch an object from S3."""
    try:
        import boto3
    except ImportError:
        return {"ok": False, "error": "boto3 not installed"}
    bucket = params.get("bucket")
    key = params.get("key")
    if not (bucket and key):
        return {"ok": False, "error": "bucket and key required"}
    try:
        s3 = boto3.client("s3",
                          endpoint_url=params.get("endpoint") or os.environ.get("AWS_S3_ENDPOINT"),
                          region_name=params.get("region") or os.environ.get("AWS_REGION"))
        r = s3.get_object(Bucket=bucket, Key=key)
        data = r["Body"].read()
        try:
            body = data.decode("utf-8")
        except UnicodeDecodeError:
            import base64 as _b64
            body = _b64.b64encode(data).decode()
        return {"ok": True, "bucket": bucket, "key": key, "content": body, "size": r.get("ContentLength")}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:400]}


# ── Phase 2: data transforms ─────────────────────────────────────────

async def t_sort(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    arr = params.get("array") or inp.get("items") or []
    key = params.get("by")
    reverse = bool(params.get("desc", False))
    try:
        if key:
            s = sorted(arr, key=lambda x: (x.get(key) is None, x.get(key)) if isinstance(x, dict) else x, reverse=reverse)
        else:
            s = sorted(arr, reverse=reverse)
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}
    return {"ok": True, "items": s, "count": len(s)}


async def t_aggregate(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Sum / min / max / avg over a numeric field in an array."""
    arr = params.get("array") or inp.get("items") or []
    field = params.get("field")
    op = params.get("op", "sum")
    vals = []
    for x in arr:
        v = x.get(field) if isinstance(x, dict) else x
        try: vals.append(float(v))
        except (TypeError, ValueError): continue
    if not vals:
        return {"ok": True, "result": 0, "count": 0}
    if op == "sum": r = sum(vals)
    elif op == "min": r = min(vals)
    elif op == "max": r = max(vals)
    elif op == "avg": r = sum(vals) / len(vals)
    else: return {"ok": False, "error": f"unknown op '{op}'"}
    return {"ok": True, "result": r, "count": len(vals)}


async def t_dedupe(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    arr = params.get("array") or inp.get("items") or []
    key = params.get("by")
    seen = set()
    out = []
    for x in arr:
        k = x.get(key) if (isinstance(x, dict) and key) else json.dumps(x, default=str, sort_keys=True)
        if k in seen: continue
        seen.add(k); out.append(x)
    return {"ok": True, "items": out, "count": len(out), "dropped": len(arr) - len(out)}


async def t_group_by(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    arr = params.get("array") or inp.get("items") or []
    key = params.get("by")
    if not key:
        return {"ok": False, "error": "by (field name) required"}
    groups: dict[str, list] = {}
    for x in arr:
        k = str(x.get(key)) if isinstance(x, dict) else "null"
        groups.setdefault(k, []).append(x)
    return {"ok": True, "groups": groups, "count": len(groups)}


# ── Phase 2: AI specialized (beyond generic LLM) ─────────────────────

async def t_summarize(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    text = params.get("text") or inp.get("text") or inp.get("body") or ""
    if not text:
        return {"ok": False, "error": "text required"}
    from services.llm_gateway import complete_text
    sys = ("You summarize text into concise bullets. Output 3-7 bullets, "
           "no preamble. Preserve numbers, names, and direct quotes.")
    length = params.get("length", "short")
    if length == "long":
        sys = sys.replace("3-7 bullets", "8-15 bullets with sub-points")
    result = await complete_text(
        user_id, sys, text[:16000], model=params.get("model", "maars/economy"),
        temperature=0.2, max_tokens=int(params.get("max_tokens", 600)),
        source="workflow.summarize",
    )
    return {"ok": True, "summary": result}


async def t_classify(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    text = params.get("text") or inp.get("text") or ""
    labels = params.get("labels") or []
    if not text or not labels:
        return {"ok": False, "error": "text and labels required"}
    from services.llm_gateway import complete_text
    sys = ("You classify text into one of the provided labels. Reply with "
           "ONLY the chosen label verbatim — no punctuation, no prose.")
    prompt = f"Labels: {', '.join(labels)}\n\nText:\n{text[:4000]}"
    out = await complete_text(
        user_id, sys, prompt, model=params.get("model", "maars/economy"),
        temperature=0.0, max_tokens=50, source="workflow.classify",
    )
    picked = (out or "").strip().split("\n")[0].strip('"').strip("'").strip()
    # normalize case-insensitively against the allowed labels
    match = next((l for l in labels if l.lower() == picked.lower()), picked)
    return {"ok": True, "label": match, "raw": out}


async def t_rag_query(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """RAG: given a query, retrieve from an embedding store and produce
    an answer grounded in retrieved passages.

    params.query: the question
    params.corpus: "default" | a collection name in Mongo containing
                   {text, embedding} docs
    params.k: top-k retrievals, default 5
    """
    q = params.get("query") or inp.get("query") or ""
    if not q:
        return {"ok": False, "error": "query required"}
    from services.semantic_cache import _embed, _cosine
    from db import db
    qvec = await _embed(q)
    if not qvec:
        return {"ok": False, "error": "embedding failed"}

    corpus = params.get("corpus", "rag_docs")
    cursor = db[corpus].find({"embedding": {"$exists": True}},
                             {"text": 1, "embedding": 1, "_id": 0}).limit(500)
    scored = []
    async for d in cursor:
        sim = _cosine(qvec, d["embedding"])
        scored.append((sim, d.get("text", "")))
    scored.sort(reverse=True)
    top = [t for _, t in scored[: int(params.get("k", 5))]]
    if not top:
        return {"ok": False, "error": "no corpus results (is the corpus populated?)"}

    from services.llm_gateway import complete_text
    from services.citation_extractor import build_cite_wrapped_prompt
    src = build_cite_wrapped_prompt(top)
    sys = ("Answer the user's question using ONLY the provided sources. "
           "Cite each claim with [S1], [S2]... inline. If the sources do "
           "not contain the answer, say so.")
    ans = await complete_text(
        user_id, sys + "\n\nSources:\n" + src, q,
        model=params.get("model", "maars/standard"),
        temperature=0.1, max_tokens=800, source="workflow.rag_query",
    )
    return {"ok": True, "answer": ans, "sources": top}


# ── Registration helper — executor imports this to populate TOOL_REGISTRY
PHASE1_TOOLS: dict = {
    "http_request":   t_http_request,
    "api_call":       t_http_request,   # canvas alias
    "set":            t_set,
    "transform":      t_set,
    "filter":         t_filter,
    "loop":           t_loop,
    "forEach":        t_loop,
    "merge":          t_merge,
    "sub_workflow":   t_sub_workflow,
    "code_js":        t_code_js,
    "code":           t_code_js,         # canvas default
    "code_python":    t_code_python,
}

PHASE2_TOOLS: dict = {
    "sql_query":            t_sql_query,
    "mongo_query":          t_mongo_query,
    "slack_send":           t_slack_send,
    "discord_send":         t_discord_send,
    "telegram_send":        t_telegram_send,
    "google_sheets_append": t_google_sheets_append,
    "notion_create":        t_notion_create,
    "airtable_append":      t_airtable_append,
    "file_read":            t_file_read,
    "file_write":           t_file_write,
    "s3_put":               t_s3_put,
    "s3_get":               t_s3_get,
    "sort":                 t_sort,
    "aggregate":            t_aggregate,
    "dedupe":               t_dedupe,
    "group_by":             t_group_by,
    "summarize":            t_summarize,
    "classify":             t_classify,
    "rag_query":            t_rag_query,
}
