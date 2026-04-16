#!/usr/bin/env python3
"""
Script 3: 对本地 session .jsonl 文件进行 S1-S3 各阶段评分（代码断言 + LLM Judge），
          结果写回 Langfuse。

用法:
    # 阶段一：生成 LLM judge prompt 文件
    python score_traces.py session --session /path/to/sessions_dir/ --dump-judge-requests /tmp/judge_req.json

    # 阶段二：通过 LLM API 或 Copilot task subagent 执行评分，将结果写入 /tmp/judge_results.json

    # 阶段三：读取 judge 结果并上传到 Langfuse
    python score_traces.py session --session /path/to/sessions_dir/ --judge-results /tmp/judge_results.json

    # 仅运行断言（跳过 LLM Judge）
    python score_traces.py session --session /path/to/session.jsonl --skip-llm-judge --dry-run

    # 直接从本地 session .jsonl 文件评分（带 item 上下文）
    python score_traces.py session --session /path/to/session.jsonl \
        --item-id E2E-01L1 --dataset-name caw-agent-eval-seth-v2 \
        --judge-results /tmp/judge_results.json

评分架构 (V2 — 代码断言 + LLM Judge):
    各维度分数作为 Langfuse Score 上传到原始 trace。
    评分通过 Langfuse SDK 直接写入，无需 CAW 后端。

    综合分公式:
        E2E = task_completion x 0.3 + (S1 x 0.15 + S2 x 0.45 + S3 x 0.40) x 0.7

    阶段维度:
        S1 意图解析   — intent_understanding (LLM Judge)
        S2 Pact 协商  — pact_structure_valid (断言门槛) + policies_correctness x 0.7
                        + completion_conditions_correctness x 0.3 (LLM Judge)
        S3 交易执行   — execution_correctness x 0.6 + result_reporting x 0.4 (LLM Judge)

环境变量:
    LANGFUSE_HOST          - Langfuse 服务地址（默认 sandbox）
    LANGFUSE_PUBLIC_KEY    - Langfuse 公钥
    LANGFUSE_SECRET_KEY    - Langfuse 私钥
    ANTHROPIC_API_KEY      - 用于实时调用 LLM Judge（可选）
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from assertions import (
    DimensionScore,
    StructuredExtraction,
    check_pact_structure_gate,
    check_refusal_gate,
    classify_diagnostics,
    extract_structured,
    get_best_pact_submit,
)
from judge_cc import (
    JUDGE_SYSTEM_PROMPT,
    build_judge_prompt,
    extract_json_from_response,
    parse_judge_result_to_scores,
)

# 自动加载同目录下的 .env（不覆盖已设置的环境变量）
load_dotenv(Path(__file__).parent / ".env", override=False)

# ── Langfuse 凭证常量 ──────────────────────────────────────────────────────────
# score_traces.py 操作 *results* project（写入评分和 scoring trace）。
# 与 dataset project（generate_dataset.py / eval_utils.py）使用不同凭证。

_DEFAULT_LF_HOST = "https://langfuse.1cobo.com"


# ── Langfuse client helper ────────────────────────────────────────────────────


def _make_langfuse() -> Any:
    """Create a Langfuse client (single unified project for both dataset and results).

    Priority: LANGFUSE_DATASET_* → LANGFUSE_* → default host.
    """
    from langfuse import Langfuse

    def _pick(specific: str, generic: str, default: str = "") -> str:
        return os.environ.get(specific) or os.environ.get(generic) or default

    host = _pick("LANGFUSE_DATASET_HOST", "LANGFUSE_HOST", _DEFAULT_LF_HOST)
    public_key = _pick("LANGFUSE_DATASET_PUBLIC_KEY", "LANGFUSE_PUBLIC_KEY")
    secret_key = _pick("LANGFUSE_DATASET_SECRET_KEY", "LANGFUSE_SECRET_KEY")

    if not public_key or not secret_key:
        print(
            "[WARN] Langfuse credentials not set. "
            "Set LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY "
            "(or LANGFUSE_DATASET_PUBLIC_KEY + LANGFUSE_DATASET_SECRET_KEY)."
        )

    return Langfuse(public_key=public_key, secret_key=secret_key, host=host)


# Alias for dataset reads — same project
_make_dataset_langfuse = _make_langfuse


# ── Stage content extractor ───────────────────────────────────────────────────


def _obs_text(obs: Any) -> str:
    """Extract combined input+output text from an observation."""
    parts: list[str] = []
    if hasattr(obs, "input") and obs.input:
        parts.append(str(obs.input))
    if hasattr(obs, "output") and obs.output:
        parts.append(str(obs.output))
    return "\n".join(parts)


def extract_stage_content(trace: Any) -> dict[str, str]:
    """
    从 Langfuse trace 的 observations 中提取 S1-S3 各阶段相关文本。

    span 命名规范（由 otel_report.py 生成）:
      turn:N    → 对话轮次（含 LLM 输入输出）
      exec:caw  → CAW CLI 工具调用结果
      session:X → 根 span

    S1 (意图解析):    第一个 turn span（或 trace 开头）
    S2 (Pact 协商):   所有 exec:caw pact 调用 + 包含 pact 关键词的 turn
    S3 (交易执行):    所有 exec:caw tx / exec:caw transfer 调用 + 最后一个 turn
    """
    obs_list = getattr(trace, "observations", None) or []
    try:
        obs_list = sorted(obs_list, key=lambda o: getattr(o, "start_time", None) or "")
    except TypeError:
        pass

    turn_texts: list[str] = []
    pact_texts: list[str] = []
    tx_texts: list[str] = []
    full_parts: list[str] = []

    for obs in obs_list:
        name = (getattr(obs, "name", "") or "").lower()
        text = _obs_text(obs)
        if not text.strip():
            continue
        full_parts.append(text)

        if name.startswith("turn:"):
            turn_texts.append(text)

        if "exec:caw pact" in name or ("caw pact" in text.lower() and "exec" in name):
            pact_texts.append(text)
        elif any(s in text.lower() for s in ("caw pact submit", "caw pact create")):
            pact_texts.append(text)

        if any(
            s in name
            for s in (
                "exec:caw tx",
                "exec:caw transfer",
                "exec:caw swap",
                "exec:caw bridge",
                "exec:caw deposit",
                "exec:caw call",
            )
        ):
            tx_texts.append(text)
        elif any(
            s in text.lower()
            for s in (
                "caw tx transfer",
                "caw tx call",
                "caw transfer --to",
                "exactinputsingle",
                "--pact-id",
            )
        ):
            tx_texts.append(text)

    if not full_parts:
        for attr in ("output", "input"):
            val = getattr(trace, attr, None)
            if val:
                full_parts.append(str(val))

    full_text = "\n\n".join(full_parts)

    # S1: first turn (intent parsing)
    s1 = turn_texts[0] if turn_texts else full_text[:2000]
    # S2: pact-related turns + pact exec spans
    pact_turn_texts = [
        t
        for t in turn_texts
        if any(
            kw in t.lower()
            for kw in (
                "pact",
                "pact_id",
                "caw pact",
                "执行计划",
                "完成条件",
                "policies",
                "permission",
                "确认",
                "confirm",
                "shall i",
            )
        )
    ]
    s2 = "\n\n".join(pact_texts + pact_turn_texts)
    # S3: tx execution spans + last turn (result verification)
    last_turn = turn_texts[-1] if len(turn_texts) > 1 else ""
    s3 = "\n\n".join(tx_texts + ([last_turn] if last_turn else [])) or full_text

    return {
        "s1": s1 or full_text[:2000],
        "s2": s2 or full_text[:3000],
        "s3": s3 or full_text,
        "full": full_text,
    }


# ── Session-based stage extraction (no Langfuse read required) ───────────────


def _parse_session_file(path: str) -> dict:
    """
    Parse a session .jsonl file into a structured dict.

    Supports two formats:
      - OpenClaw otel format: type=session + type=message events, id/toolCallId keys
      - Claude Code native format: type=user/assistant events, uuid/sessionId keys,
        tool_use/tool_result content blocks

    Returns {session_id, started_at, cwd, model, provider, messages, order}.
    """
    import pathlib

    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    session_id = ""
    started_at = ""
    cwd = ""
    model = ""
    provider = ""
    messages: dict[str, dict] = {}
    order: list[str] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        ev_type = ev.get("type", "")

        if ev_type == "session":
            # OpenClaw otel format: dedicated session event
            session_id = ev.get("id", "")
            started_at = ev.get("timestamp", "")
            cwd = ev.get("cwd", "")

        elif ev_type == "message":
            # OpenClaw otel format: dedicated message events
            ev_id = ev.get("id", "")
            msg = ev.get("message", {})
            if not model and msg.get("model"):
                model = msg.get("model", "")
            if not provider and msg.get("provider"):
                provider = msg.get("provider", "")
            if ev_id:
                messages[ev_id] = ev
                order.append(ev_id)

        elif ev_type in ("user", "assistant"):
            # Claude Code native format: user/assistant events with uuid + sessionId
            if not session_id and ev.get("sessionId"):
                session_id = ev["sessionId"]
            if not cwd and ev.get("cwd"):
                cwd = ev["cwd"]
            if not started_at and ev.get("timestamp"):
                started_at = ev["timestamp"]
            ev_id = ev.get("uuid") or ev.get("id", "")
            if ev_id and ev_id not in messages:
                # Normalize tool_use blocks → toolCall; tool_result → toolResult role
                msg = ev.get("message", {})
                role = msg.get("role", ev_type)
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
                normalized_ev = {**ev, "message": {**msg, "role": role, "content": normalized}}
                messages[ev_id] = normalized_ev
                order.append(ev_id)

    if not session_id:
        session_id = pathlib.Path(path).stem

    return {
        "session_id": session_id,
        "started_at": started_at,
        "cwd": cwd,
        "model": model,
        "provider": provider,
        "messages": messages,
        "order": order,
    }


def _session_message_events(session: dict) -> list[dict]:
    """Return message events in chronological order."""
    order: list[str] = session.get("order", [])
    messages: dict[str, dict] = session.get("messages", {})
    return [messages[eid] for eid in order if eid in messages]


def _session_tool_result_index(events: list[dict]) -> dict[str, dict]:
    """Build {toolCallId: synthetic_event} from toolResult events (both formats)."""
    idx: dict[str, dict] = {}
    for ev in events:
        msg = ev.get("message", {})
        # OpenClaw otel format: dedicated toolResult event
        if msg.get("role") == "toolResult" and msg.get("toolCallId"):
            idx[msg["toolCallId"]] = ev
        # Claude Code native format: tool_result blocks inside user events
        elif msg.get("role") == "user":
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


def extract_stage_content_from_session(session: dict) -> dict[str, str]:
    """
    从本地 session dict（由 _parse_session_file() 返回）提取 S1-S3 各阶段内容。

    S1 (意图解析):   第一条 user 消息 + 第一条 assistant 回复（第一个工具调用前）
    S2 (Pact 协商):  所有 caw pact submit/create 工具调用 + 含 pact 提案文本的 assistant 消息
    S3 (交易执行):   所有 caw tx transfer/call 工具调用及其结果 + 最后一条 assistant 文本（结果验证）
    """
    evts = _session_message_events(session)
    tr_idx = _session_tool_result_index(evts)

    assistant_msgs = [e for e in evts if e.get("message", {}).get("role") == "assistant"]
    user_msgs = [e for e in evts if e.get("message", {}).get("role") == "user"]

    def get_text_blocks(ev: dict) -> list[str]:
        content = ev.get("message", {}).get("content", [])
        return [b.get("text", "") for b in content if b.get("type") == "text" and b.get("text")]

    def get_tool_calls(ev: dict) -> list[dict]:
        content = ev.get("message", {}).get("content", [])
        return [b for b in content if b.get("type") == "toolCall"]

    def get_tool_result_text(call_id: str) -> str:
        result_ev = tr_idx.get(call_id)
        if not result_ev:
            return ""
        for b in result_ev.get("message", {}).get("content", []):
            if b.get("type") == "text":
                return b.get("text", "")[:600]
        return ""

    def is_pact_call(tc: dict) -> bool:
        name = tc.get("name", "").lower()
        cmd = tc.get("arguments", {}).get("command", "").lower()
        return "pact" in name or (bool(cmd) and "caw pact" in cmd)

    def is_tx_call(tc: dict) -> bool:
        cmd = tc.get("arguments", {}).get("command", "").lower()
        tx_cmds = ("caw tx transfer", "caw tx call", "caw transfer --to", "caw tx sign")
        return any(kw in cmd for kw in tx_cmds)

    # S1: first user message + first assistant response (before any tool calls)
    s1_parts: list[str] = []
    if user_msgs:
        texts = get_text_blocks(user_msgs[0])
        s1_parts.append(f"User: {' '.join(texts)[:800]}")
    for ev in assistant_msgs:
        texts = get_text_blocks(ev)
        tools = get_tool_calls(ev)
        if texts:
            s1_parts.append(f"Assistant: {' '.join(texts)[:1200]}")
        if tools:
            break
    s1 = "\n".join(s1_parts)

    # S2: pact tool calls + assistant messages containing pact proposals
    pact_keywords = (
        "pact",
        "执行计划",
        "execution plan",
        "policies",
        "completion conditions",
        "完成条件",
        "确认",
        "confirm",
        "shall i",
        "以下操作",
        "is this correct",
    )
    s2_items: list[dict] = []
    s2_texts: list[str] = []
    for ev in assistant_msgs:
        texts = get_text_blocks(ev)
        tools = get_tool_calls(ev)
        # Include assistant text that looks like a pact proposal
        if texts:
            combined = " ".join(texts)
            if any(kw in combined.lower() for kw in pact_keywords):
                s2_texts.append(combined[:2000])
        # Collect pact tool calls
        for tc in tools:
            if is_pact_call(tc):
                cmd = tc.get("arguments", {}).get("command", "") if tc.get("name") == "exec" else ""
                s2_items.append(
                    {
                        "command": cmd or tc.get("name", ""),
                        "arguments": tc.get("arguments", {}),
                        "result": get_tool_result_text(tc.get("id", "")),
                    }
                )
    s2_parts = s2_texts + ([json.dumps(s2_items, ensure_ascii=False, indent=2)] if s2_items else [])
    s2 = "\n---\n".join(s2_parts) or "No pact operations found"

    # S3: transaction execution tool calls (non-pact) + last assistant message
    s3_items: list[dict] = []
    for ev in assistant_msgs:
        for tc in get_tool_calls(ev):
            if is_tx_call(tc):
                cmd = tc.get("arguments", {}).get("command", "")
                s3_items.append(
                    {
                        "command": cmd[:400],
                        "result": get_tool_result_text(tc.get("id", "")),
                    }
                )
    # Append last assistant text (result verification)
    last_assistant_text = ""
    for ev in reversed(assistant_msgs):
        texts = get_text_blocks(ev)
        if texts:
            last_assistant_text = " ".join(texts)[:3000]
            break
    s3_exec = (
        json.dumps(s3_items[:20], ensure_ascii=False, indent=2)
        if s3_items
        else "No tx execution calls found"
    )
    s3 = (s3_exec + "\n---\n" + last_assistant_text) if last_assistant_text else s3_exec

    # Full conversation summary
    full_parts: list[str] = []
    for ev in evts:
        role = ev.get("message", {}).get("role", "")
        if role in ("user", "assistant"):
            texts = get_text_blocks(ev)
            tools = get_tool_calls(ev)
            if texts:
                full_parts.append(f"[{role.upper()}] {' '.join(texts)[:300]}")
            for tc in tools:
                cmd = tc.get("arguments", {}).get("command", "") if tc.get("name") == "exec" else ""
                full_parts.append(
                    f"[TOOL:{tc.get('name', '')}] {(cmd or json.dumps(tc.get('arguments', {})))[:200]}"
                )
    full = "\n".join(full_parts)

    return {
        "s1": s1[:3000] or full[:2000],
        "s2": s2[:4000] or full[:3000],
        "s3": s3[:4000] or full,
        "full": full[:8000],
    }


def load_judge_results(path: str) -> dict[str, dict[str, Any]]:
    """
    Load a judge results JSON file and return a mapping keyed by trace_id and/or item_id.

    The file is expected to be a JSON array of objects.  Each entry may carry a
    "trace_id" field, an "item_id" field (e.g. "E2E-01L1"), or both.  Both keys
    are registered so that callers can look up results by either identifier.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        result: dict[str, dict[str, Any]] = {}
        for entry in raw:
            e = {**entry, "available": True}
            if "trace_id" in entry:
                result[entry["trace_id"]] = e
            if "item_id" in entry:
                result[entry["item_id"]] = e
        return result
    raise ValueError(f"judge results file must be a JSON array, got {type(raw).__name__}")


# ── 评分管线（代码断言 + LLM Judge）──────────────────────────────────────────


# 阶段权重: E2E = task_completion x 0.3 + (S1 x 0.15 + S2 x 0.45 + S3 x 0.40) x 0.7
STAGE_WEIGHTS = {"s1": 0.15, "s2": 0.45, "s3": 0.40}
_TC_WEIGHT = 0.30
_PROCESS_WEIGHT = 0.70


def build_score_comment(
    stage: str,
    stage_score: float,
    dimensions: dict[str, DimensionScore],
    scoring_source: str,
) -> str:
    """构建阶段评分 comment，只保留计算公式（子维度 reasoning 已在独立 score 中）。"""
    parts = [f"{dim_name}({dim.score:.2f})" for dim_name, dim in dimensions.items()]
    formula = " + ".join(parts) if parts else ""
    return (
        f"{stage} ({scoring_source}) | {stage_score:.2f} = {formula}"
        if formula
        else f"{stage} ({scoring_source}) | {stage_score:.2f}"
    )


def _upload_scores(
    lf: Any,
    trace_id: str,
    s1_score: float,
    s2_score: float,
    s3_score: float,
    composite: float,
    task_completion_score: float,
    scoring_source: str,
    dimensions: dict[str, DimensionScore],
    diagnostics_reasoning: str = "",
    run_metrics: dict | None = None,
    score_metadata: dict | None = None,
) -> None:
    """上传评分到 Langfuse，comment 包含 reasoning，metadata 包含上下文信息。

    Args:
        run_metrics: 运行指标，如 {"duration_seconds": 88, "token_count": 34490, ...}
        score_metadata: 每条 score 携带的结构化上下文，如：
            {"run_name": "eval-cc-sonnet-20260411", "item_id": "E2E-01L1",
             "operation_type": "transfer", "difficulty": "L1", ...}
    """
    meta = score_metadata or {}

    # 按阶段分组 dimensions
    s1_dims = {k: v for k, v in dimensions.items() if k in ("intent_understanding",)}
    s2_dims = {
        k: v
        for k, v in dimensions.items()
        if k
        in ("pact_structure_valid", "policies_correctness", "completion_conditions_correctness")
    }
    s3_dims = {
        k: v for k, v in dimensions.items() if k in ("execution_correctness", "result_reporting")
    }
    tc_dims = {k: v for k, v in dimensions.items() if k in ("task_completion",)}
    refuse_dims = {
        k: v for k, v in dimensions.items() if k in ("correctly_refused", "refusal_quality")
    }

    scores_to_upload: list[tuple[str, float, str]] = [
        (
            "caw.s1_intent",
            s1_score,
            build_score_comment("S1 意图解析", s1_score, s1_dims, scoring_source),
        ),
        (
            "caw.s2_pact",
            s2_score,
            build_score_comment("S2 Pact 协商", s2_score, s2_dims, scoring_source),
        ),
        (
            "caw.s3_execution",
            s3_score,
            build_score_comment("S3 执行", s3_score, s3_dims, scoring_source),
        ),
        (
            "caw.e2e_composite",
            composite,
            f"E2E 综合 ({scoring_source}) | {composite:.2f}\n"
            f"  = task_completion({task_completion_score:.2f})×{_TC_WEIGHT} "
            f"+ process(S1={s1_score:.2f}×{STAGE_WEIGHTS['s1']}+"
            f"S2={s2_score:.2f}×{STAGE_WEIGHTS['s2']}+"
            f"S3={s3_score:.2f}×{STAGE_WEIGHTS['s3']})×{_PROCESS_WEIGHT}",
        ),
        (
            "caw.task_completion",
            task_completion_score,
            build_score_comment("任务完成度", task_completion_score, tc_dims, scoring_source),
        ),
        ("caw.scoring_source", 2.0, f"scoring_source={scoring_source}"),
    ]

    # 子维度作为独立 score 上传，便于 ClickHouse 直接查询
    _dim_score_names = {
        "intent_understanding": "caw.s1_intent_understanding",
        "policies_correctness": "caw.s2_policies_correctness",
        "completion_conditions_correctness": "caw.s2_completion_conditions",
        "execution_correctness": "caw.s3_execution_correctness",
        "result_reporting": "caw.s3_result_reporting",
        "task_completion": "caw.task_completion_judge",
    }
    for dim_key, score_name in _dim_score_names.items():
        dim = dimensions.get(dim_key)
        if dim is not None:
            scores_to_upload.append(
                (
                    score_name,
                    dim.score,
                    f"[{dim.method}] {dim_key}={dim.score:.2f} — {dim.reasoning}",
                )
            )

    if refuse_dims:
        scores_to_upload.append(
            (
                "caw.refusal",
                composite,
                build_score_comment("拒绝评估", composite, refuse_dims, scoring_source),
            )
        )

    # 运行指标作为额外 scores 上传
    if run_metrics:
        metric_names = {
            "duration_seconds": "caw.duration_seconds",
            "token_count": "caw.token_count",
            "tool_call_count": "caw.tool_call_count",
            "caw_command_count": "caw.caw_command_count",
            "pact_submit_count": "caw.pact_submit_count",
            "tx_command_count": "caw.tx_command_count",
            "error_count": "caw.error_count",
        }
        for key, score_name in metric_names.items():
            if key in run_metrics:
                scores_to_upload.append(
                    (score_name, float(run_metrics[key]), f"{key}={run_metrics[key]}")
                )

    for name, value, comment in scores_to_upload:
        try:
            lf.create_score(
                trace_id=trace_id,
                name=name,
                value=float(value),
                comment=comment or "",
                metadata=meta if meta else None,
            )
        except Exception as e:
            print(f"    [SCORE UPLOAD ERROR] {name}: {e}")


def _print_summary(
    trace_id: str,
    s1: float,
    s2: float,
    s3: float,
    composite: float,
    task_completion: float,
    scoring_source: str,
    diagnostics_reasoning: str,
) -> None:
    """打印评分摘要。"""
    print(
        f"    S1={s1:.2f} S2={s2:.2f} S3={s3:.2f} "
        f"TC={task_completion:.2f} → E2E={composite:.2f} [{scoring_source}]"
    )
    if diagnostics_reasoning:
        print(f"    诊断: {diagnostics_reasoning}")


def score_session_file(
    session_path: str,
    item_input: dict,
    item_expected: dict,
    item_metadata: dict,
    dry_run: bool = False,
    lf: Any = None,
    judge_result: dict[str, Any] | None = None,
    skip_llm_judge: bool = False,
    judge_model: str = "claude-sonnet-4-20250514",
    trace_id: str = "",
) -> dict[str, Any]:
    """
    评分管线：代码断言 + LLM Judge。

    流程:
      1. 解析 session → 结构化提取
      2. 运行门槛检查 + 诊断标签
      3. LLM Judge 评判语义维度（或使用预计算结果）
      4. 合并分数 → 综合分
      5. 上传到 Langfuse（含 reasoning comment）

    Args:
        trace_id: 外部指定的 Langfuse trace ID（来自 trace_map.json）。
                  为空时回退到 session_id。
    """
    import pathlib

    session = _parse_session_file(session_path)
    if not trace_id:
        trace_id = session["session_id"] or pathlib.Path(session_path).stem
    if not trace_id:
        raise ValueError(f"No trace_id found in {session_path}")

    print(f"  → session {trace_id[:16]}... ({pathlib.Path(session_path).name})")

    # 1. 结构化提取
    extraction = extract_structured(session)
    stage_text = extract_stage_content_from_session(session)

    if not stage_text["full"].strip():
        print("    [WARN] Empty session")
        return {"skipped": True, "trace_id": trace_id, "session_path": session_path}

    hints = item_expected.get("pact_hints", {})
    should_refuse = hints.get("should_refuse", False)

    # 2. 门槛 + 诊断
    diagnostics = classify_diagnostics(extraction)
    all_dimensions: dict[str, DimensionScore] = {}

    if should_refuse:
        # ── should_refuse 路径 ────────────────────────────────────────────────
        refusal_gate = check_refusal_gate(extraction)
        all_dimensions["correctly_refused"] = DimensionScore(
            dimension="correctly_refused",
            score=1.0 if refusal_gate.passed else 0.0,
            method="assertion",
            reasoning=refusal_gate.reasoning,
        )

        # LLM Judge: refusal_quality + task_completion
        judge_scores = _get_judge_scores(
            judge_result=judge_result,
            skip_llm_judge=skip_llm_judge,
            judge_model=judge_model,
            user_message=extraction.user_message or item_input.get("user_message", ""),
            expected=item_expected,
            metadata=item_metadata,
            stage_text=stage_text,
            extraction=extraction,
            is_refuse=True,
            assertion_context=f"[gate] correctly_refused={'pass' if refusal_gate.passed else 'fail'} — {refusal_gate.reasoning}",
        )
        for s in judge_scores:
            all_dimensions[s.dimension] = s

        refusal_quality = all_dimensions.get(
            "refusal_quality",
            DimensionScore(
                dimension="refusal_quality",
                score=0.5,
                method="default",
                reasoning="LLM judge 不可用",
            ),
        )
        task_completion_score = all_dimensions.get(
            "task_completion",
            DimensionScore(
                dimension="task_completion",
                score=1.0 if refusal_gate.passed else 0.0,
                method="default",
                reasoning="基于 refusal gate 结果",
            ),
        )

        composite = all_dimensions["correctly_refused"].score * 0.5 + refusal_quality.score * 0.5
        s1_score = s2_score = s3_score = 0.0

    else:
        # ── 正常路径 ──────────────────────────────────────────────────────────
        pact_gate = check_pact_structure_gate(extraction)
        all_dimensions["pact_structure_valid"] = DimensionScore(
            dimension="pact_structure_valid",
            score=1.0 if pact_gate.passed else 0.0,
            method="gate",
            reasoning=pact_gate.reasoning,
        )

        # LLM Judge
        best_pact = get_best_pact_submit(extraction)
        assertion_lines = [
            f"[gate] pact_structure_valid={'pass' if pact_gate.passed else 'fail'} — {pact_gate.reasoning}",
            f"[diag] error_type={diagnostics.error_type}, retry_count={diagnostics.retry_count}",
        ]
        judge_scores = _get_judge_scores(
            judge_result=judge_result,
            skip_llm_judge=skip_llm_judge,
            judge_model=judge_model,
            user_message=extraction.user_message or item_input.get("user_message", ""),
            expected=item_expected,
            metadata=item_metadata,
            stage_text=stage_text,
            extraction=extraction,
            is_refuse=False,
            assertion_context="\n".join(assertion_lines),
            best_pact_submit=best_pact,
        )
        for s in judge_scores:
            all_dimensions[s.dimension] = s

        # 计算各阶段分数
        s1_score = all_dimensions.get(
            "intent_understanding",
            DimensionScore(
                dimension="intent_understanding",
                score=0.5,
                method="default",
                reasoning="LLM judge 不可用",
            ),
        ).score

        if not pact_gate.passed:
            s2_score = 0.0
        else:
            pc = all_dimensions.get(
                "policies_correctness",
                DimensionScore(
                    dimension="policies_correctness",
                    score=0.5,
                    method="default",
                    reasoning="LLM judge 不可用",
                ),
            ).score
            cc = all_dimensions.get(
                "completion_conditions_correctness",
                DimensionScore(
                    dimension="completion_conditions_correctness",
                    score=0.5,
                    method="default",
                    reasoning="LLM judge 不可用",
                ),
            ).score
            s2_score = pc * 0.7 + cc * 0.3

        ec = all_dimensions.get(
            "execution_correctness",
            DimensionScore(
                dimension="execution_correctness",
                score=0.5,
                method="default",
                reasoning="LLM judge 不可用",
            ),
        ).score
        rr = all_dimensions.get(
            "result_reporting",
            DimensionScore(
                dimension="result_reporting",
                score=0.5,
                method="default",
                reasoning="LLM judge 不可用",
            ),
        ).score
        s3_score = ec * 0.6 + rr * 0.4

        task_completion_score = all_dimensions.get(
            "task_completion",
            DimensionScore(
                dimension="task_completion",
                score=0.5,
                method="default",
                reasoning="LLM judge 不可用",
            ),
        )

        process_quality = (
            s1_score * STAGE_WEIGHTS["s1"]
            + s2_score * STAGE_WEIGHTS["s2"]
            + s3_score * STAGE_WEIGHTS["s3"]
        )
        tc_val = (
            task_completion_score.score
            if isinstance(task_completion_score, DimensionScore)
            else task_completion_score
        )
        composite = tc_val * _TC_WEIGHT + process_quality * _PROCESS_WEIGHT

    # 确保 task_completion 是 float
    tc_float = (
        task_completion_score.score
        if isinstance(task_completion_score, DimensionScore)
        else float(task_completion_score)
    )
    scoring_source = "assertion+judge" if not skip_llm_judge else "assertion_only"

    _print_summary(
        trace_id,
        s1_score,
        s2_score,
        s3_score,
        composite,
        tc_float,
        scoring_source,
        diagnostics.reasoning,
    )

    result = {
        "trace_id": trace_id,
        "session_path": session_path,
        "scoring_source": scoring_source,
        "item_metadata": item_metadata,
        "composite": round(composite, 4),
        "s1_score": round(s1_score, 4),
        "s2_score": round(s2_score, 4),
        "s3_score": round(s3_score, 4),
        "task_completion": round(tc_float, 4),
        "diagnostics": {
            "error_type": diagnostics.error_type,
            "retry_count": diagnostics.retry_count,
        },
        "dimensions": {
            k: {"score": v.score, "method": v.method, "reasoning": v.reasoning}
            for k, v in all_dimensions.items()
        },
    }

    if dry_run:
        return result

    # 构建 score metadata（用于 ClickHouse JSONExtract 查询）
    score_meta = {
        "run_name": item_metadata.get("run_name", ""),
        "dataset_name": item_metadata.get("dataset_name", ""),
        "item_id": item_metadata.get("id", ""),
        "operation_type": item_metadata.get("operation_type", ""),
        "difficulty": item_metadata.get("difficulty", ""),
        "chain": item_metadata.get("chain", ""),
        "model": item_metadata.get("model", ""),
    }
    # 去除空值
    score_meta = {k: v for k, v in score_meta.items() if v}

    # 构建运行指标
    run_metrics = {
        "duration_seconds": item_metadata.get("duration_seconds", 0),
        "token_count": item_metadata.get("token_count", 0),
        "tool_call_count": item_metadata.get("tool_call_count", 0),
        "caw_command_count": len(extraction.all_tool_calls),
        "pact_submit_count": len(extraction.pact_tool_calls),
        "tx_command_count": len(extraction.tx_tool_calls),
        "error_count": diagnostics.retry_count,
    }
    # 去除零值
    run_metrics = {k: v for k, v in run_metrics.items() if v}

    _lf = lf or _make_langfuse()
    _upload_scores(
        _lf,
        trace_id,
        s1_score,
        s2_score,
        s3_score,
        composite,
        tc_float,
        scoring_source,
        all_dimensions,
        diagnostics.reasoning,
        run_metrics=run_metrics,
        score_metadata=score_meta,
    )
    _lf.flush()
    return result


def _get_judge_scores(
    judge_result: dict[str, Any] | None,
    skip_llm_judge: bool,
    judge_model: str,
    user_message: str,
    expected: dict,
    metadata: dict,
    stage_text: dict[str, str],
    extraction: StructuredExtraction,
    is_refuse: bool,
    assertion_context: str,
    best_pact_submit: Any = None,
) -> list[DimensionScore]:
    """获取 LLM Judge 评分：优先用预计算结果，否则实时调用 API，最后 fallback 到默认。"""

    # 1. 预计算结果（--judge-results 传入）
    if judge_result and not judge_result.get("error"):
        return parse_judge_result_to_scores(judge_result)

    # 2. 跳过 LLM Judge
    if skip_llm_judge:
        return []

    # 3. 实时调用 API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("    [WARN] ANTHROPIC_API_KEY 未设置，跳过 LLM Judge")
        return []

    try:
        from judge_cc import call_claude_api

        prompt = build_judge_prompt(
            user_message=user_message,
            expected=expected,
            metadata=metadata,
            stage_text=stage_text,
            assertion_context=assertion_context,
            best_pact_submit=best_pact_submit,
            is_refuse=is_refuse,
        )
        response_text = call_claude_api(
            system_prompt=JUDGE_SYSTEM_PROMPT,
            user_prompt=prompt,
            model=judge_model,
        )
        raw = extract_json_from_response(response_text)
        return parse_judge_result_to_scores(raw)
    except Exception as e:
        print(f"    [WARN] LLM Judge 调用失败: {e}")
        return []


def session_main() -> None:
    """
    Subcommand: score one or more local session .jsonl files (assertion + LLM Judge).

    用法:
        # 阶段一：生成 judge prompt 文件
        python score_traces.py session --session /path/to/sessions_dir/ --dump-judge-requests /tmp/req.json

        # 阶段三：使用预计算的 judge 评分结果
        python score_traces.py session --session /path/to/sessions_dir/ --judge-results /tmp/results.json

        # 仅断言评分（跳过 LLM Judge）
        python score_traces.py session --session /path/to/session.jsonl --skip-llm-judge --report
        python score_traces.py session --session session.jsonl --item-id E2E-01L1 --dataset-name caw-agent-eval-seth-v2
    """
    import pathlib

    parser = argparse.ArgumentParser(
        prog="score_traces.py session",
        description="Score local session .jsonl files without reading from Langfuse.",
    )
    parser.add_argument(
        "--session",
        required=True,
        help="Path to a session .jsonl file, or directory containing .jsonl files",
    )
    parser.add_argument(
        "--item-id",
        help="Dataset item ID (e.g. E2E-01L1). If set, fetches item context from Langfuse dataset.",
    )
    parser.add_argument(
        "--dataset-name",
        default="caw-agent-eval-seth-v2",
        help="Dataset name to look up --item-id [default: caw-agent-eval-seth-v2]",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Score without uploading to Langfuse"
    )
    parser.add_argument("--report", action="store_true", help="Print summary table after scoring")
    parser.add_argument("--output", help="Save results JSON to file")
    parser.add_argument(
        "--dump-judge-requests",
        metavar="FILE",
        help="Write judge prompt requests to FILE and exit (phase 1 of subagent scoring)",
    )
    parser.add_argument(
        "--judge-results",
        metavar="FILE",
        help="Read pre-computed judge results from FILE (phase 3 of subagent scoring)",
    )
    parser.add_argument(
        "--skip-llm-judge", action="store_true", help="Only run assertions, skip LLM Judge"
    )
    parser.add_argument(
        "--judge-model",
        default="claude-sonnet-4-20250514",
        help="LLM Judge model (default: claude-sonnet-4-20250514)",
    )
    args = parser.parse_args(sys.argv[2:])

    lf = None if (args.dry_run or args.dump_judge_requests) else _make_langfuse()

    # Optionally fetch item context from Langfuse dataset project
    item_input: dict = {}
    item_expected: dict = {}
    item_metadata: dict = {}
    if args.item_id:
        try:
            lf_ds = _make_dataset_langfuse()
            dataset = lf_ds.get_dataset(args.dataset_name)
            matching = [i for i in dataset.items if i.id == args.item_id]
            if matching:
                item = matching[0]
                item_input = item.input or {}
                item_expected = item.expected_output or {}
                item_metadata = item.metadata or {}
                print(
                    f"[INFO] Loaded item context: {args.item_id} "
                    f"({item_metadata.get('operation_type', '?')} / "
                    f"{item_metadata.get('difficulty', '?')})"
                )
            else:
                print(
                    f"[WARN] Item {args.item_id!r} not found in dataset {args.dataset_name!r}. "
                    "Scoring without item context."
                )
        except Exception as e:
            print(
                f"[WARN] Failed to fetch item context for {args.item_id!r}: {e}. "
                "Scoring without item context."
            )

    session_path = pathlib.Path(args.session)
    if session_path.is_dir():
        session_files = sorted(session_path.glob("*.jsonl"))
    else:
        session_files = [session_path]

    if not session_files:
        print(f"[ERROR] No .jsonl files found at {args.session}", file=sys.stderr)
        sys.exit(1)

    # 当处理目录中多个文件且未指定 --item-id 时，按文件名匹配 dataset item（如 E2E-01L1.jsonl → E2E-01L1）
    dataset_items_cache: dict[
        str, tuple[dict, dict, dict]
    ] = {}  # item_id -> (input, expected, metadata)
    if not args.item_id and session_path.is_dir():
        try:
            lf_ds = _make_dataset_langfuse()
            dataset = lf_ds.get_dataset(args.dataset_name)
            for di in dataset.items:
                meta = di.metadata if isinstance(di.metadata, dict) else {}
                mid = meta.get("id", di.id)
                inp = di.input if isinstance(di.input, dict) else {"user_message": di.input or ""}
                exp = di.expected_output if isinstance(di.expected_output, dict) else {}
                dataset_items_cache[mid] = (inp, exp, meta)
            if dataset_items_cache:
                print(
                    f"[INFO] Loaded {len(dataset_items_cache)} items from dataset {args.dataset_name}"
                )
        except Exception as e:
            print(f"[WARN] Failed to load dataset items: {e}")

    if not args.item_id and not item_input and not dataset_items_cache:
        print(
            "[WARN] No --item-id provided and no dataset items loaded. Scoring without expected output / metadata context. "
            "Use --item-id <E2E-XXX> to load item-specific scoring criteria from the dataset."
        )

    def _get_item_context(session_file: pathlib.Path) -> tuple[dict, dict, dict]:
        """按文件名匹配 dataset item 上下文（如 E2E-01L1.jsonl → E2E-01L1）。"""
        if item_input:
            return item_input, item_expected, item_metadata
        stem = session_file.stem
        if stem in dataset_items_cache:
            return dataset_items_cache[stem]
        return {}, {}, {}

    # ── Phase 1: dump judge requests ──────────────────────────────────────────
    if args.dump_judge_requests:
        requests: list[dict] = []
        for sf in session_files:
            try:
                sf_input, sf_expected, sf_metadata = _get_item_context(sf)
                session = _parse_session_file(str(sf))
                trace_id = session["session_id"] or sf.stem
                item_id = args.item_id or sf.stem

                extraction = extract_structured(session)
                stage_text = extract_stage_content_from_session(session)
                pact_gate = check_pact_structure_gate(extraction)
                diagnostics = classify_diagnostics(extraction)
                best_pact = get_best_pact_submit(extraction)

                hints = sf_expected.get("pact_hints", {})
                is_refuse = hints.get("should_refuse", False)

                assertion_lines = [
                    f"[gate] pact_structure_valid={'pass' if pact_gate.passed else 'fail'} — {pact_gate.reasoning}",
                    f"[diag] error_type={diagnostics.error_type}, retry_count={diagnostics.retry_count}",
                ]

                prompt = build_judge_prompt(
                    user_message=sf_input.get("user_message", ""),
                    expected=sf_expected,
                    metadata=sf_metadata,
                    stage_text=stage_text,
                    assertion_context="\n".join(assertion_lines),
                    best_pact_submit=best_pact,
                    is_refuse=is_refuse,
                )

                req = {
                    "trace_id": trace_id,
                    "item_id": item_id,
                    "metadata": sf_metadata or {"session_file": sf.name},
                    "system_prompt": JUDGE_SYSTEM_PROMPT,
                    "prompt": prompt,
                    "session_path": str(sf),
                }
                requests.append(req)
            except Exception as e:
                print(f"  [ERROR] {sf.name}: {e}")
        Path(args.dump_judge_requests).write_text(
            json.dumps(requests, indent=2, ensure_ascii=False)
        )
        print(f"[SAVED] {len(requests)} judge request(s) → {args.dump_judge_requests}")
        print(
            "[NEXT] Run Copilot task subagent for each request, then re-run with --judge-results <file>"
        )
        return

    # ── Phase 3: load pre-computed judge results ──────────────────────────────
    judge_results_map: dict[str, dict] = {}
    if args.judge_results:
        judge_results_map = load_judge_results(args.judge_results)
        print(f"[INFO] Loaded {len(judge_results_map)} judge result(s) from {args.judge_results}")

    skip_judge = getattr(args, "skip_llm_judge", False)
    mode_str = "assertion_only" if skip_judge else "assertion+judge"
    print(f"[INFO] Scoring mode: {mode_str}")

    # ── Load trace_map.json（upload 阶段生成的 item_id → Langfuse trace UUID 映射）
    trace_map: dict[str, str] = {}
    session_dir = pathlib.Path(args.session)
    if session_dir.is_dir():
        trace_map_path = session_dir / "trace_map.json"
        if trace_map_path.exists():
            trace_map = json.loads(trace_map_path.read_text())
            print(f"[INFO] Loaded trace_map.json ({len(trace_map)} entries)")

    print(f"[INFO] Scoring {len(session_files)} session file(s)...")
    results: list[dict] = []
    for sf in session_files:
        try:
            sf_input, sf_expected, sf_metadata = _get_item_context(sf)

            # trace_id 优先从 trace_map 获取（与 upload 创建的 Langfuse trace 一致）
            mapped_trace_id = trace_map.get(sf.stem, "")

            result = score_session_file(
                str(sf),
                item_input=sf_input,
                item_expected=sf_expected,
                item_metadata=sf_metadata or {"session_file": sf.name},
                dry_run=args.dry_run,
                lf=lf,
                judge_result=judge_results_map.get(mapped_trace_id)
                or judge_results_map.get(sf.stem),
                skip_llm_judge=skip_judge,
                judge_model=getattr(args, "judge_model", "claude-sonnet-4-20250514"),
                trace_id=mapped_trace_id,
            )
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] {sf.name}: {e}")

    if args.report or len(session_files) > 1:
        # Print V2 summary
        valid = [r for r in results if "composite" in r]
        if valid:
            avg_e2e = sum(r["composite"] for r in valid) / len(valid)
            avg_tc = sum(r["task_completion"] for r in valid) / len(valid)
            print(f"\n{'=' * 60}")
            print(f"Summary: {len(valid)} sessions  |  E2E={avg_e2e:.3f}  TC={avg_tc:.3f}")
            print(f"{'=' * 60}")

    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"[SAVED] {args.output}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    # Dispatch to subcommands — 'session' is the primary entry point
    if len(sys.argv) > 1 and sys.argv[1] == "session":
        session_main()
        return

    # No subcommand → show help directing to session subcommand
    print(
        "Usage: python score_traces.py session --session <path> [options]\n\n"
        "Use 'python score_traces.py session --help' for details.",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
