"""
upload_session.py — openclaw session.jsonl → Langfuse

用于 caw-eval 评测流程中将 openclaw session 文件直接上传到 Langfuse（不经过 CAW 后端）。

上报链路:
  upload_session.py → Langfuse ingestion API（直接）

用法:
  python upload_session.py session.jsonl
  python upload_session.py ./sessions/          # 批量上传目录下所有 .jsonl
  python upload_session.py session.jsonl --trace-name "eval-run-001"
  python upload_session.py session.jsonl --dry-run  # 仅解析，不上传

环境变量:
  LANGFUSE_PUBLIC_KEY   Langfuse 公钥（必填）
  LANGFUSE_SECRET_KEY   Langfuse 私钥（必填）
  LANGFUSE_HOST         Langfuse 服务地址（默认 https://langfuse.1cobo.com）
"""

import getpass
import glob
import json
import os
import re
import socket
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# ── caw 操作分类表 ─────────────────────────────────────────────────────────────

CAW_OP_TABLE = [
    (["onboard bootstrap"], "caw.onboard.bootstrap", "onboarding"),
    (["onboard health"], "caw.onboard.health", "onboarding"),
    (["onboard self-test"], "caw.onboard.self_test", "onboarding"),
    (["onboard"], "caw.onboard", "onboarding"),
    (["tx transfer"], "caw.tx.transfer", "transaction"),
    (["tx call"], "caw.tx.call", "transaction"),
    (["tx sign-message"], "caw.tx.sign_message", "transaction"),
    (["tx speedup"], "caw.tx.speedup", "transaction"),
    (["tx drop"], "caw.tx.drop", "transaction"),
    (["tx estimate-transfer-fee"], "caw.tx.estimate_fee", "query"),
    (["tx estimate-call-fee"], "caw.tx.estimate_call_fee", "query"),
    (["tx list"], "caw.tx.list", "query"),
    (["tx get"], "caw.tx.get", "query"),
    (["wallet balance"], "caw.wallet.balance", "query"),
    (["wallet list"], "caw.wallet.list", "query"),
    (["wallet get"], "caw.wallet.get", "query"),
    (["wallet current"], "caw.wallet.current", "query"),
    (["wallet pair-status"], "caw.wallet.pair_status", "wallet"),
    (["wallet pair"], "caw.wallet.pair", "wallet"),
    (["wallet rename"], "caw.wallet.rename", "wallet"),
    (["wallet archive"], "caw.wallet.archive", "wallet"),
    (["wallet update"], "caw.wallet.update", "wallet"),
    (["address create"], "caw.address.create", "wallet"),
    (["address list"], "caw.address.list", "query"),
    (["status"], "caw.status", "query"),
    (["pending approve"], "caw.pending.approve", "auth"),
    (["pending reject"], "caw.pending.reject", "auth"),
    (["pending list"], "caw.pending.list", "auth"),
    (["pending get"], "caw.pending.get", "auth"),
    (["pact submit"], "caw.pact.submit", "auth"),
    (["pact status"], "caw.pact.status", "auth"),
    (["pact show"], "caw.pact.show", "auth"),
    (["pact events"], "caw.pact.events", "auth"),
    (["pact list"], "caw.pact.list", "auth"),
    (["pact revoke"], "caw.pact.revoke", "auth"),
    (["pact withdraw"], "caw.pact.withdraw", "auth"),
    (["pact update-conditions"], "caw.pact.update_conditions", "auth"),
    (["pact update-policies"], "caw.pact.update_policies", "auth"),
    (["approval create"], "caw.approval.create", "auth"),
    (["approval resolve"], "caw.approval.resolve", "auth"),
    (["approval list"], "caw.approval.list", "auth"),
    (["approval get"], "caw.approval.get", "auth"),
    (["track"], "caw.track", "monitor"),
    (["node status"], "caw.node.status", "node"),
    (["node start"], "caw.node.start", "node"),
    (["node stop"], "caw.node.stop", "node"),
    (["node restart"], "caw.node.restart", "node"),
    (["node health"], "caw.node.health", "node"),
    (["node info"], "caw.node.info", "node"),
    (["node logs"], "caw.node.logs", "node"),
    (["meta chain-info"], "caw.meta.chain_info", "meta"),
    (["meta search-tokens"], "caw.meta.search_tokens", "meta"),
    (["meta prices"], "caw.meta.prices", "meta"),
    (["meta chains"], "caw.meta.chains", "meta"),
    (["meta tokens"], "caw.meta.tokens", "meta"),
    (["faucet deposit"], "caw.faucet.deposit", "dev"),
    (["faucet tokens"], "caw.faucet.tokens", "dev"),
    (["update"], "caw.update", "meta"),
    (["fetch"], "caw.fetch", "util"),
    (["export-key"], "caw.export_key", "wallet"),
    (["demo"], "caw.demo", "dev"),
    (["schema"], "caw.schema", "meta"),
    (["version", "--version"], "caw.version", "meta"),
    (["--help", "-h"], "caw.help", "meta"),
]

CAW_BIN_PATTERN = re.compile(
    r"(?:^|&&\s*)"
    r"(?:[^\s]*?/)?caw\s+"
    r"(.*?)(?:\s+&&|\s*$)",
    re.MULTILINE,
)
SKILL_INSTALL_PATTERN = re.compile(
    r"(?:npx\s+skills\s+add|clawhub\s+install|npx\s+skills\s+update)\s+(\S+)"
)
BOOTSTRAP_PATTERN = re.compile(r"bootstrap-env\.sh")
POLICY_DENIAL_PATTERN = re.compile(
    r"(?:TRANSFER_LIMIT_EXCEEDED|POLICY_DENIED|403|policy.*denied|suggestion[\":\s]+([^\n]+))",
    re.IGNORECASE,
)
UPDATE_SIGNAL = re.compile(r'"update"\s*:\s*true')


# ── 配置读取 ──────────────────────────────────────────────────────────────────


def load_caw_config() -> dict[str, str]:
    """从 ~/.cobo-agentic-wallet/ 读取 API key/URL 等，env vars 优先覆盖。"""
    result: dict[str, str] = {}
    config_path = Path.home() / ".cobo-agentic-wallet" / "config"
    if config_path.exists():
        cfg = json.loads(config_path.read_text())
        profile_id = cfg.get("default_profile", "")
        if profile_id:
            cred_path = (
                Path.home()
                / ".cobo-agentic-wallet"
                / "profiles"
                / f"profile_{profile_id}"
                / "credentials"
            )
            if cred_path.exists():
                cred = json.loads(cred_path.read_text())
                result["api_key"] = cred.get("api_key", "")
                result["api_url"] = cred.get("api_url", "")
                result["agent_id"] = cred.get("agent_id", "")
                result["wallet_uuid"] = cred.get("wallet_uuid", "")
                result["env"] = cred.get("env", "")

    if v := os.environ.get("CAW_API_KEY"):
        result["api_key"] = v
    if v := os.environ.get("AGENT_WALLET_API_URL"):
        result["api_url"] = v
    return result


# ── JSONL 解析 ────────────────────────────────────────────────────────────────


def parse_session(path: str) -> dict:
    """
    Supports two formats:
      - OpenClaw otel: type=session + type=message events, id keys
      - Claude Code native: type=user/assistant events, uuid/sessionId keys
    """
    messages: dict = {}
    order: list = []
    session_id_fallback = Path(path).stem

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            ev_type = ev.get("type", "")

            if ev_type in ("user", "assistant"):
                # Claude Code native format: use uuid as key
                eid = ev.get("uuid") or ev.get("id", "")
                if eid and eid not in messages:
                    messages[eid] = ev
                    order.append(eid)
            else:
                # OpenClaw otel format: use id or type as key
                eid = ev.get("id") or ev_type
                if eid:
                    messages[eid] = ev
                    order.append(eid)

    # OpenClaw: dedicated session event
    session_ev = next((messages[i] for i in order if messages[i].get("type") == "session"), {})
    snapshot = next(
        (messages[i]["data"] for i in order if messages[i].get("customType") == "model-snapshot"),
        {},
    )
    # Claude Code: session_id lives in each event's sessionId field
    cc_session_id = next(
        (
            messages[i].get("sessionId", "")
            for i in order
            if messages[i].get("type") in ("user", "assistant") and messages[i].get("sessionId")
        ),
        "",
    )
    # Claude Code: model from assistant message
    cc_model = next(
        (
            messages[i].get("message", {}).get("model", "")
            for i in order
            if messages[i].get("type") == "assistant"
        ),
        "",
    )
    return {
        "session_id": session_ev.get("id") or cc_session_id or session_id_fallback,
        "started_at": session_ev.get("timestamp")
        or next(
            (messages[i].get("timestamp") for i in order if messages[i].get("timestamp")), None
        ),
        "cwd": session_ev.get("cwd")
        or next((messages[i].get("cwd") for i in order if messages[i].get("cwd")), ""),
        "model": snapshot.get("modelId") or cc_model or "unknown",
        "provider": snapshot.get("provider", "unknown"),
        "messages": messages,
        "order": order,
    }


def extract_message_events(session: dict) -> list[dict]:
    """Return message events supporting both OpenClaw and Claude Code formats."""
    result = []
    for i in session["order"]:
        ev = session["messages"][i]
        ev_type = ev.get("type", "")
        if ev_type == "message":
            # OpenClaw otel format
            result.append(ev)
        elif ev_type in ("user", "assistant"):
            # Claude Code native format — normalize tool_use → toolCall
            msg = ev.get("message", {})
            content = msg.get("content", [])
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            normalized: list[dict] = []
            for block in content:
                if block.get("type") == "tool_use":
                    normalized.append(
                        {
                            "type": "toolCall",
                            "id": block.get("id", ""),
                            "name": block.get("name", ""),
                            "arguments": block.get("input", {}),
                        }
                    )
                else:
                    normalized.append(block)
            result.append({**ev, "message": {**msg, "content": normalized}})
    return result


def build_turns(message_events: list[dict]) -> list[list[dict]]:
    turns: list = []
    current: list = []
    for ev in message_events:
        role = ev.get("message", {}).get("role")
        if role == "user" and current:
            turns.append(current)
            current = []
        current.append(ev)
    if current:
        turns.append(current)
    return turns


def build_tool_result_index(message_events: list[dict]) -> dict:
    idx: dict = {}
    for ev in message_events:
        msg = ev.get("message", {})
        role = msg.get("role", "")
        # OpenClaw otel format: dedicated toolResult event
        if role == "toolResult" and msg.get("toolCallId"):
            idx[msg["toolCallId"]] = ev
        # Claude Code native format: tool_result blocks inside user events
        elif role == "user":
            for block in msg.get("content", []):
                if block.get("type") == "tool_result" and block.get("tool_use_id"):
                    raw = block.get("content", [])
                    if isinstance(raw, str):
                        raw = [{"type": "text", "text": raw}]
                    idx[block["tool_use_id"]] = {
                        "message": {
                            "role": "toolResult",
                            "toolCallId": block["tool_use_id"],
                            "content": raw,
                        }
                    }
    return idx


# ── caw 命令解析 ──────────────────────────────────────────────────────────────


def parse_caw_command(command: str) -> Optional[tuple[str, str, str]]:
    m = CAW_BIN_PATTERN.search(command)
    if not m:
        return None
    subcmd = m.group(1).strip()
    if "--help" in subcmd or subcmd.endswith("-h"):
        return "caw.help", "meta", subcmd
    clean = re.sub(
        r"--(?:format|env|profile|timeout|verbose|api-key|api-url)\s*\S*", "", subcmd
    ).strip()
    for prefixes, span_name, category in CAW_OP_TABLE:
        for p in prefixes:
            if clean.startswith(p):
                return span_name, category, subcmd
    return "caw.unknown", "unknown", subcmd


def extract_caw_flags(subcmd: str) -> dict:
    flags = {}
    for flag, key in [
        (r"--to\s+(\S+)", "to_address"),
        (r"--token-id\s+(\S+)", "token_id"),
        (r"--amount\s+(\S+)", "amount"),
        (r"--chain\s+(\S+)", "chain"),
        (r"--request-id\s+(\S+)", "request_id"),
        (r"--wallet-id\s+(\S+)", "wallet_id"),
        (r"--env\s+(\S+)", "env"),
        (r"--contract\s+(\S+)", "contract"),
        (r"--context\s+'([^']+)'", "context"),
    ]:
        hit = re.search(flag, subcmd)
        if hit:
            flags[key] = hit.group(1)
    return flags


def parse_tx_result(text: str) -> dict:
    result: dict = {}
    try:
        data = json.loads(text)
        inner = data.get("result", data)
        for k in ["transaction_id", "tx_hash", "status", "request_id", "error_code", "suggestion"]:
            if k in inner:
                result[k] = str(inner[k])
        if data.get("update"):
            result["caw_update_available"] = "true"
    except Exception:
        m = POLICY_DENIAL_PATTERN.search(text)
        if m:
            result["policy_denial"] = m.group(0)
        if UPDATE_SIGNAL.search(text):
            result["caw_update_available"] = "true"
    return result


# ── 工具函数 ──────────────────────────────────────────────────────────────────


def ts_to_ns(ts: Optional[str]) -> Optional[int]:
    if not ts:
        return None
    try:
        return int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1e9)
    except Exception:
        return None


def safe_str(obj: object, limit: int = 2000) -> str:
    try:
        s = json.dumps(obj, ensure_ascii=False, default=str) if not isinstance(obj, str) else obj
        return s[:limit]
    except Exception:
        return str(obj)[:limit]


def extract_user_text(msg: dict) -> str:
    content = msg.get("content", [])
    # Claude Code native format: content 是 string
    if isinstance(content, str):
        return content.strip()
    # OpenClaw / standard format: content 是 list of blocks
    parts = []
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "text":
            continue
        text = block.get("text", "")
        text = re.sub(
            r"Conversation info \(untrusted metadata\):.*?(?=\n\n|\Z)", "", text, flags=re.DOTALL
        ).strip()
        text = re.sub(r"^System:.*", "", text, flags=re.MULTILINE).strip()
        text = re.sub(
            r"Sender \(untrusted metadata\):\s*```json\s*\{.*?\}\s*```", "", text, flags=re.DOTALL
        ).strip()
        if text:
            parts.append(text)
    return " | ".join(parts)


def extract_sender_id(msg: dict) -> str:
    for block in msg.get("content", []):
        text = block.get("text", "")
        m = re.search(r'"sender_id":\s*"([^"]+)"', text)
        if m:
            return m.group(1)
        m = re.search(r'"id":\s*"([^"]+)"', text)
        if m:
            return m.group(1)
    return ""


def extract_sender_name(msg: dict) -> str:
    for block in msg.get("content", []):
        m = re.search(r'"sender":\s*"([^"]+)"', block.get("text", ""))
        if m:
            return m.group(1)
    return "unknown"


# ── Langfuse 直接上传 ─────────────────────────────────────────────────────────

_DEFAULT_LF_HOST = "https://langfuse.1cobo.com"


def _get_langfuse_config() -> dict[str, str]:
    """从环境变量读取 Langfuse 配置（支持 LANGFUSE_DATASET_* 或 LANGFUSE_* 前缀）。"""

    def _pick(specific: str, generic: str) -> str:
        return os.environ.get(specific) or os.environ.get(generic) or ""

    return {
        "host": _pick("LANGFUSE_DATASET_HOST", "LANGFUSE_HOST") or _DEFAULT_LF_HOST,
        "public_key": _pick("LANGFUSE_DATASET_PUBLIC_KEY", "LANGFUSE_PUBLIC_KEY"),
        "secret_key": _pick("LANGFUSE_DATASET_SECRET_KEY", "LANGFUSE_SECRET_KEY"),
    }


def _make_langfuse():
    from langfuse import Langfuse

    cfg = _get_langfuse_config()
    if not cfg["public_key"] or not cfg["secret_key"]:
        raise RuntimeError(
            "Missing Langfuse credentials. "
            "Set LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY in environment or .env."
        )
    return Langfuse(public_key=cfg["public_key"], secret_key=cfg["secret_key"], host=cfg["host"])


def _ns_to_iso(ns: Optional[int], fallback: str) -> str:
    if not ns:
        return fallback
    return datetime.fromtimestamp(ns / 1e9, tz=timezone.utc).isoformat()


def _attrs_to_fields(attrs: dict) -> dict:
    """Map langfuse.observation.* attribute keys to ingestion body kwargs."""
    fields: dict = {}
    metadata: dict = {}
    for k, v in (attrs or {}).items():
        if v is None:
            continue
        if k == "langfuse.observation.input":
            fields["input"] = v
        elif k == "langfuse.observation.output":
            fields["output"] = v
        elif k == "langfuse.observation.level":
            fields["level"] = v
        elif k == "langfuse.observation.model.name":
            fields["model"] = v
        elif k.startswith("langfuse.observation.metadata."):
            metadata[k[len("langfuse.observation.metadata.") :]] = v
        elif k.startswith("langfuse.trace.metadata."):
            metadata[k[len("langfuse.trace.metadata.") :]] = v
        elif k.startswith("gen_ai."):
            metadata[k] = v
    if metadata:
        fields["metadata"] = metadata
    return fields


def _build_events_from_node(
    node: dict,
    trace_id: str,
    parent_span_id: Optional[str],
    now_iso: str,
) -> list:
    """Recursively convert a span/generation record (+ children) to Langfuse ingestion events."""
    import uuid as _uuid
    from langfuse.api import (
        CreateSpanBody,
        IngestionEvent_SpanCreate,
        CreateGenerationBody,
        IngestionEvent_GenerationCreate,
    )

    events = []
    node_id = str(_uuid.uuid4())
    fields = _attrs_to_fields(node.get("attributes", {}))
    start_iso = _ns_to_iso(node.get("start_time_unix_nano"), now_iso)
    end_iso = _ns_to_iso(node.get("end_time_unix_nano"), now_iso)

    if node.get("record_type") == "generation":
        meta = dict(fields.pop("metadata", {}) or {})
        input_tokens = int(meta.pop("gen_ai.usage.input_tokens", 0) or 0)
        output_tokens = int(meta.pop("gen_ai.usage.output_tokens", 0) or 0)
        body = CreateGenerationBody(
            id=node_id,
            trace_id=trace_id,
            parent_observation_id=parent_span_id,
            name=node["name"],
            start_time=start_iso,
            end_time=end_iso,
            model=fields.pop("model", None),
            input=fields.get("input"),
            output=fields.get("output"),
            metadata=meta or None,
            usage={"input": input_tokens, "output": output_tokens}
            if (input_tokens or output_tokens)
            else None,
        )
        events.append(
            IngestionEvent_GenerationCreate(
                id=str(_uuid.uuid4()),
                timestamp=now_iso,
                body=body,
            )
        )
    else:
        body = CreateSpanBody(
            id=node_id,
            trace_id=trace_id,
            parent_observation_id=parent_span_id,
            name=node["name"],
            start_time=start_iso,
            end_time=end_iso,
            input=fields.get("input"),
            output=fields.get("output"),
            metadata=fields.get("metadata"),
        )
        events.append(
            IngestionEvent_SpanCreate(
                id=str(_uuid.uuid4()),
                timestamp=now_iso,
                body=body,
            )
        )

    for child in node.get("children") or []:
        events.extend(_build_events_from_node(child, trace_id, node_id, now_iso))
    return events


class SessionUploader:
    """解析 session.jsonl，构造 SessionRecord 树，直接上报 Langfuse。"""

    def __init__(self, skill_name: str = "cobo-agentic-wallet-sandbox", trace_name: str = ""):
        self.skill = skill_name
        self.trace_name = trace_name

    def upload(
        self,
        session: dict,
        lf,
        user_id: str = "",
        trace_id: str = "",
        extra_metadata: dict | None = None,
    ) -> str | None:
        """上传 session 到 Langfuse，返回 trace_id 或 None。

        Args:
            trace_id: 外部指定的 Langfuse trace ID。为空时使用 session_id。
            extra_metadata: 额外的上下文信息（如 item_id、user_message 等），
                           合并到 trace 的 input 和 metadata 中。
        """
        import uuid as _uuid
        from langfuse.api import TraceBody, IngestionEvent_TraceCreate

        evts = extract_message_events(session)
        turns = build_turns(evts)
        tr_idx = build_tool_result_index(evts)

        sid = trace_id or session["session_id"]
        model = session["model"]
        prov = session["provider"]

        first_user = next((e for e in evts if e.get("message", {}).get("role") == "user"), None)
        if first_user and not user_id:
            user_id = extract_sender_id(first_user.get("message", {})) or "unknown"

        start_ns = ts_to_ns(session["started_at"])
        all_events = [ev for turn in turns for ev in turn]
        last_ns = ts_to_ns(all_events[-1].get("timestamp")) if all_events else start_ns

        tz_cn = timezone(offset=timedelta(hours=8))
        now_cn = datetime.now(tz=tz_cn)
        time_code = now_cn.strftime("%m%d%H%M")
        user = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
        hostname = socket.gethostname()
        trace_display_name = self.trace_name or f"eval_{user}@{hostname}_{time_code}"
        now_iso = now_cn.isoformat()

        turn_children = [
            self._build_turn_record(turn, i, model, prov, tr_idx) for i, turn in enumerate(turns)
        ]

        # ── Build Langfuse ingestion events ─────────────────────────────
        trace_event = IngestionEvent_TraceCreate(
            id=str(_uuid.uuid4()),
            timestamp=now_iso,
            body=TraceBody(
                id=sid,
                name=trace_display_name,
                session_id=sid,
                user_id=user_id,
                timestamp=now_iso,
                tags=["openclaw", "caw-eval"],
                input=safe_str(
                    {
                        "session_id": sid,
                        "model": model,
                        "turns": len(turns),
                    }
                ),
                metadata={
                    "skill": self.skill,
                    "model": model,
                    "provider": prov,
                    "cwd": session.get("cwd", ""),
                    "session_id": sid,
                    "telemetry_source": "caw-eval",
                    "uploaded_at": now_iso,
                    "session_started_at": _ns_to_iso(start_ns, now_iso),
                    "session_ended_at": _ns_to_iso(last_ns, now_iso),
                    "host": f"{getpass.getuser()}@{socket.gethostname()}",
                    **(extra_metadata or {}),
                },
            ),
        )
        all_events_list: list = [trace_event]
        for turn_node in turn_children:
            all_events_list.extend(_build_events_from_node(turn_node, sid, None, now_iso))

        # Langfuse recommends batches ≤ 15 events; split to avoid timeouts
        _BATCH_SIZE = 15
        try:
            for i in range(0, len(all_events_list), _BATCH_SIZE):
                chunk = all_events_list[i : i + _BATCH_SIZE]
                lf.api.ingestion.batch(batch=chunk)
            lf.flush()
        except Exception as e:
            print(f"[WARN] Langfuse ingestion.batch failed: {e}", file=sys.stderr)
            return None

        total_children = sum(len(t.get("children") or []) for t in turn_children)
        cfg = _get_langfuse_config()
        print(f"\n{'=' * 60}")
        print("  Status:      OK")
        print(f"  Trace Name:  {trace_display_name}")
        print(f"  Session ID:  {sid}")
        print(f"  User ID:     {user_id}")
        print(f"  Model:       {model}")
        print(f"  Turns:       {len(turn_children)}")
        print(f"  Spans:       {total_children}")
        print(f"  Langfuse:    {cfg['host']}")
        print(f"{'=' * 60}")
        return sid

    def _build_turn_record(
        self, turn: list, idx: int, model: str, provider: str, tr_idx: dict
    ) -> dict:
        user_ev = turn[0]
        user_msg = user_ev.get("message", {})
        user_text_raw = extract_user_text(user_msg)
        sender = extract_sender_name(user_msg)
        turn_start_ns = ts_to_ns(user_ev.get("timestamp"))
        turn_end_ns = ts_to_ns(turn[-1].get("timestamp")) if turn else turn_start_ns

        events_after_user = turn[1:]
        children: list = []
        final_text = ""
        for j, ev in enumerate(events_after_user):
            msg = ev.get("message", {})
            role = msg.get("role")
            if role == "assistant":
                next_ts = None
                if j + 1 < len(events_after_user):
                    next_ts = ts_to_ns(events_after_user[j + 1].get("timestamp"))
                llm_children = self._build_assistant_children(ev, model, provider, tr_idx, next_ts)
                children.extend(llm_children)
                for b in msg.get("content", []):
                    if b.get("type") == "text":
                        final_text = b.get("text", "")

        input_preview = (
            user_text_raw[:50].rstrip() + ".." if len(user_text_raw) > 50 else user_text_raw
        )
        turn_name = f'turn:{idx} ("{input_preview}")' if input_preview else f"turn:{idx}"

        return {
            "name": turn_name,
            "record_type": "span",
            "start_time_unix_nano": turn_start_ns,
            "end_time_unix_nano": turn_end_ns,
            "attributes": {
                "langfuse.observation.input": safe_str({"role": "user", "content": user_text_raw}),
                "langfuse.observation.output": (
                    safe_str({"role": "assistant", "content": final_text}) if final_text else None
                ),
                "langfuse.trace.metadata.turn_index": str(idx),
                "langfuse.trace.metadata.sender": sender,
            },
            "children": children if children else None,
        }

    def _build_assistant_children(
        self, ev: dict, model: str, provider: str, tr_idx: dict, next_ev_ts: Optional[int] = None
    ) -> list:
        children: list = []
        msg = ev.get("message", {})
        content = msg.get("content", [])
        usage = msg.get("usage", {})
        ts_ns = ts_to_ns(ev.get("timestamp"))

        tool_calls = [b for b in content if b.get("type") == "toolCall"]

        msg_ts = msg.get("timestamp")
        if msg_ts and ts_ns:
            llm_start = int(msg_ts * 1e6) if isinstance(msg_ts, (int, float)) else ts_ns
            llm_end = ts_ns
        else:
            llm_start = ts_ns
            llm_end = next_ev_ts or ts_ns

        children.append(
            {
                "name": "OpenAI-generation",
                "record_type": "generation",
                "status_code": "OK",
                "start_time_unix_nano": llm_start,
                "end_time_unix_nano": llm_end,
                "attributes": {
                    "gen_ai.request.model": msg.get("model", model),
                    "langfuse.observation.model.name": msg.get("model", model),
                    "gen_ai.usage.input_tokens": (
                        usage.get("input_tokens")  # Claude Code native format
                        or usage.get("input", 0)  # OpenClaw / standard format
                    ),
                    "gen_ai.usage.output_tokens": (
                        usage.get("output_tokens")  # Claude Code native format
                        or usage.get("output", 0)  # OpenClaw / standard format
                    ),
                    "langfuse.observation.output": safe_str(
                        [b.get("name") or b.get("text", "") for b in content]
                    ),
                    "langfuse.trace.metadata.provider": provider,
                    "langfuse.trace.metadata.api": msg.get("api", ""),
                    "langfuse.trace.metadata.stop_reason": msg.get("stopReason", ""),
                    "langfuse.trace.metadata.response_id": msg.get("responseId", ""),
                    "langfuse.observation.metadata.tool_calls_count": str(len(tool_calls)),
                },
            }
        )

        for tc in tool_calls:
            child = self._build_tool_child(tc, tr_idx, ts_ns)
            if child:
                children.append(child)

        return children

    def _build_tool_child(
        self, tc: dict, tr_idx: dict, fallback_ts_ns: Optional[int]
    ) -> Optional[dict]:
        call_id = tc.get("id", "")
        name = tc.get("name", "")
        args = tc.get("arguments", {})

        result_ev = tr_idx.get(call_id)
        result_msg = result_ev.get("message", {}) if result_ev else {}
        details = result_msg.get("details", {})
        result_ts_ns = ts_to_ns(result_ev.get("timestamp")) if result_ev else fallback_ts_ns
        dur_ms = details.get("durationMs", 0)
        if not dur_ms and fallback_ts_ns and result_ts_ns and result_ts_ns > fallback_ts_ns:
            dur_ms = int((result_ts_ns - fallback_ts_ns) / 1e6)
        ts_ns = fallback_ts_ns or result_ts_ns
        exit_code = details.get("exitCode")
        status_ok = exit_code is None or exit_code == 0

        result_text = ""
        for b in result_msg.get("content", []):
            if b.get("type") == "text":
                result_text = b.get("text", "")
                break

        if name in ("exec", "Bash"):
            cmd = args.get("command", "")
            caw_info = parse_caw_command(cmd)
            if caw_info:
                span_name, category, subcmd = caw_info
                return self._build_caw_child(
                    span_name,
                    category,
                    subcmd,
                    result_text,
                    dur_ms,
                    ts_ns,
                    result_ts_ns,
                    status_ok,
                    exit_code,
                )
            if SKILL_INSTALL_PATTERN.search(cmd):
                category = "skill_install"
            elif BOOTSTRAP_PATTERN.search(cmd):
                category = "env_bootstrap"
            else:
                category = "exec"
        elif name == "read":
            category = "file_read"
        elif name == "web_search":
            category = "web_search"
        elif name == "process":
            category = "process_poll"
        else:
            category = name

        attrs: dict = {
            "langfuse.observation.input": safe_str(args, 800),
            "langfuse.observation.output": result_text,
            "langfuse.observation.metadata.tool_call_id": call_id,
            "langfuse.observation.metadata.tool_name": name,
            "langfuse.observation.metadata.category": category,
            "langfuse.observation.metadata.duration_ms": str(dur_ms),
            "langfuse.observation.metadata.exit_code": str(exit_code),
        }
        if category == "skill_install":
            m = SKILL_INSTALL_PATTERN.search(args.get("command", ""))
            if m:
                attrs["langfuse.trace.metadata.skill_package"] = m.group(1)

        end_ns = result_ts_ns or (ts_ns + int(dur_ms * 1e6) if ts_ns and dur_ms else ts_ns)
        return {
            "name": f"{category}:{name}",
            "record_type": "span",
            "start_time_unix_nano": ts_ns,
            "end_time_unix_nano": end_ns,
            "status_code": "OK" if status_ok else "ERROR",
            "status_message": "" if status_ok else result_text,
            "attributes": attrs,
        }

    def _build_caw_child(
        self,
        span_name: str,
        category: str,
        subcmd: str,
        result_text: str,
        dur_ms: int,
        ts_ns: Optional[int],
        result_ts_ns: Optional[int],
        status_ok: bool,
        exit_code: Optional[int],
    ) -> dict:
        flags = extract_caw_flags(subcmd)

        attrs: dict = {
            "langfuse.observation.input": safe_str({"subcmd": subcmd}),
            "langfuse.observation.output": result_text,
            "langfuse.observation.metadata.caw_op": span_name,
            "langfuse.observation.metadata.category": category,
            "langfuse.observation.metadata.duration_ms": str(dur_ms),
            "langfuse.observation.metadata.exit_code": str(exit_code),
            "langfuse.trace.metadata.caw_op": span_name,
            "langfuse.trace.metadata.caw_category": category,
        }
        for k, v in flags.items():
            attrs[f"langfuse.trace.metadata.caw_{k}"] = v

        if category == "transaction":
            tx_fields = parse_tx_result(result_text)
            for k, v in tx_fields.items():
                attrs[f"langfuse.trace.metadata.tx_{k}"] = v
            if "policy_denial" in tx_fields or not status_ok:
                attrs["langfuse.observation.level"] = "WARNING"
                attrs["langfuse.observation.metadata.policy_denied"] = "true"

        if UPDATE_SIGNAL.search(result_text):
            attrs["langfuse.trace.metadata.caw_update_available"] = "true"

        if "context" in flags:
            try:
                ctx = json.loads(flags["context"])
                attrs["langfuse.trace.metadata.openclaw_channel"] = ctx.get("channel", "")
                attrs["langfuse.trace.metadata.openclaw_target"] = ctx.get("target", "")
            except Exception:
                pass

        status = "OK"
        if not status_ok and category not in ("query", "meta", "dev"):
            status = "ERROR"

        end_ns = result_ts_ns or (ts_ns + int(dur_ms * 1e6) if ts_ns and dur_ms else ts_ns)
        return {
            "name": span_name,
            "record_type": "span",
            "start_time_unix_nano": ts_ns,
            "end_time_unix_nano": end_ns,
            "status_code": status,
            "status_message": "" if status == "OK" else result_text,
            "attributes": attrs,
        }


# ── 公开 API ──────────────────────────────────────────────────────────────────


def extract_session_id(jsonl_path: str) -> str:
    """从 JSONL 文件提取 session_id。"""
    try:
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get("type") == "session":
                    return ev.get("id", Path(jsonl_path).stem)
    except Exception:
        pass
    return Path(jsonl_path).stem


def upload_session_file(
    jsonl_path: str,
    user_id: str = "",
    skill_name: str = "cobo-agentic-wallet-sandbox",
    trace_name: str = "",
    trace_id: str = "",
    extra_metadata: dict | None = None,
) -> str | None:
    """上传单个 session.jsonl 直接到 Langfuse。返回实际使用的 trace_id 或 None。"""
    try:
        lf = _make_langfuse()
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return None

    session = parse_session(jsonl_path)
    evts = extract_message_events(session)
    print(f"[INFO] Parsed {session['session_id']}  model={session['model']}  events={len(evts)}")

    uploader = SessionUploader(skill_name, trace_name=trace_name)
    return uploader.upload(
        session, lf, user_id=user_id, trace_id=trace_id, extra_metadata=extra_metadata
    )


# ── dry-run 打印 span 树 ───────────────────────────────────────────────────────


def dry_run_session(jsonl_path: str) -> None:
    session = parse_session(jsonl_path)
    evts = extract_message_events(session)
    turns = build_turns(evts)
    print(f"{'=' * 60}")
    print(f"Session: {session['session_id']}")
    print(f"Model:   {session['model']}")
    print(f"Started: {session['started_at']}")
    print(f"Turns:   {len(turns)}")
    print(f"Events:  {len(evts)}")
    print(f"{'=' * 60}")
    for i, turn in enumerate(turns):
        user_ev = turn[0]
        user_text = extract_user_text(user_ev.get("message", {}))
        ts = user_ev.get("timestamp", "?")
        print(f"[turn:{i}]  [{ts}]  user: {user_text[:80]}")
        for ev in turn[1:]:
            msg = ev.get("message", {})
            if msg.get("role") == "assistant":
                content = msg.get("content", [])
                tool_calls = [b for b in content if b.get("type") == "toolCall"]
                usage = msg.get("usage", {})
                print(
                    f"  +- generation  tokens={usage.get('input', 0)}+{usage.get('output', 0)}"
                    f"  tools={len(tool_calls)}"
                )
        print()


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="upload_session.py",
        description="Upload openclaw session.jsonl directly to Langfuse",
    )
    parser.add_argument(
        "paths", nargs="+", help="Session .jsonl file(s) or directory containing .jsonl files"
    )
    parser.add_argument(
        "--skill",
        default="cobo-agentic-wallet-sandbox",
        help="Skill name tag (default: cobo-agentic-wallet-sandbox)",
    )
    parser.add_argument("--trace-name", default="", help="Override Langfuse trace display name")
    parser.add_argument("--user-id", default="", help="Override user ID in trace metadata")
    parser.add_argument(
        "--dry-run", action="store_true", help="Parse and print span tree without uploading"
    )
    args = parser.parse_args()

    # Collect all .jsonl files from paths
    jsonl_files: list[str] = []
    for p in args.paths:
        if os.path.isdir(p):
            jsonl_files.extend(
                sorted(f for f in glob.glob(os.path.join(p, "*.jsonl")) if not f.endswith(".lock"))
            )
        elif p.endswith(".jsonl") and os.path.isfile(p):
            jsonl_files.append(p)
        else:
            expanded = glob.glob(p)
            jsonl_files.extend(
                f for f in expanded if f.endswith(".jsonl") and not f.endswith(".lock")
            )

    if not jsonl_files:
        print("[ERROR] No .jsonl files found", file=sys.stderr)
        sys.exit(1)

    failed = 0
    for idx, path in enumerate(jsonl_files):
        if len(jsonl_files) > 1:
            print(f"\n[{idx + 1}/{len(jsonl_files)}] {os.path.basename(path)}")
        if args.dry_run:
            dry_run_session(path)
        else:
            result = upload_session_file(
                path,
                user_id=args.user_id,
                skill_name=args.skill,
                trace_name=args.trace_name,
            )
            if not result:
                failed += 1

    if not args.dry_run and failed:
        print(f"\n[ERROR] {failed}/{len(jsonl_files)} uploads failed", file=sys.stderr)
        sys.exit(1)
