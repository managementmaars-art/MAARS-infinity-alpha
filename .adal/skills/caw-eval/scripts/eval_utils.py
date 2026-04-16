"""
评测脚本公共工具模块。

提供 Langfuse 客户端初始化、数据集读取、session 上传和 dataset run 关联等功能。
供 run_eval_cc.py / run_eval_openclaw.py 等评测编排脚本共用。

环境变量:
    LANGFUSE_HOST         - Langfuse 服务地址
    LANGFUSE_PUBLIC_KEY   - Langfuse 公钥（数据集读写 + session 上传）
    LANGFUSE_SECRET_KEY   - Langfuse 私钥（数据集读写 + session 上传）
"""

import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langfuse import Langfuse

from upload_session import upload_session_file

# 自动加载同目录下的 .env（不覆盖已设置的环境变量）
load_dotenv(Path(__file__).parent / ".env", override=False)

_DEFAULT_HOST = "https://langfuse.1cobo.com"


def get_langfuse_client() -> Langfuse:
    """创建并返回 Langfuse 客户端实例。

    凭据优先级: LANGFUSE_DATASET_* → LANGFUSE_* → .env file.
    """

    def _pick(specific: str, generic: str) -> str:
        return os.environ.get(specific) or os.environ.get(generic) or ""

    pub = _pick("LANGFUSE_DATASET_PUBLIC_KEY", "LANGFUSE_PUBLIC_KEY")
    sec = _pick("LANGFUSE_DATASET_SECRET_KEY", "LANGFUSE_SECRET_KEY")
    if not pub or not sec:
        print(
            "[WARN] Langfuse credentials not set. "
            "Set LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY "
            "(or LANGFUSE_DATASET_PUBLIC_KEY + LANGFUSE_DATASET_SECRET_KEY) in .env or env vars."
        )
    host = _pick("LANGFUSE_DATASET_HOST", "LANGFUSE_HOST") or _DEFAULT_HOST

    return Langfuse(
        public_key=pub,
        secret_key=sec,
        host=host,
    )


def get_dataset_items(dataset_name: str) -> list[dict]:
    """从 Langfuse 拉取 dataset items。

    处理 input 为 str 或 dict 两种情况，返回标准化的 item 列表。
    """
    lf = get_langfuse_client()
    dataset = lf.get_dataset(dataset_name)
    items = sorted(dataset.items, key=lambda i: i.id)
    result = []
    for item in items:
        # input 可能是 str 或 dict
        inp = item.input if isinstance(item.input, dict) else {"user_message": item.input or ""}
        meta = item.metadata if isinstance(item.metadata, dict) else {}
        exp = item.expected_output if isinstance(item.expected_output, dict) else {}
        # 优先用 metadata.id（如 E2E-01L1），回退到 Langfuse UUID
        item_id = meta.get("id", item.id)
        result.append(
            {
                "id": item_id,
                "langfuse_id": item.id,
                "user_message": inp.get("user_message", str(item.input or "")),
                "operation_type": meta.get("operation_type", ""),
                "difficulty": meta.get("difficulty", ""),
                "chain": meta.get("chain", ""),
                "success_criteria": exp.get("success_criteria", ""),
            }
        )
    return result


def upload_session(
    session_path: str,
    skill_name: str = "cobo-agentic-wallet-sandbox",
    trace_id: str = "",
    extra_metadata: dict | None = None,
) -> str | None:
    """上传单个 session.jsonl 到 Langfuse，返回实际 trace_id，失败返回 None。

    Args:
        trace_id: 外部指定的 trace ID（UUID）。为空时使用 session 文件内的 session_id。
        extra_metadata: 额外上下文（item_id、user_message 等），写入 trace metadata。
    """
    try:
        return upload_session_file(
            session_path,
            skill_name=skill_name,
            trace_id=trace_id,
            extra_metadata=extra_metadata,
        )
    except Exception as e:
        print(f"    [UPLOAD ERROR] {e}")
        return None


def link_to_dataset_run(
    lf: Langfuse,
    dataset_item_id: str,
    run_name: str,
    trace_id: str,
) -> None:
    """将 Langfuse trace 关联到 dataset item run。

    Args:
        dataset_item_id: Langfuse dataset item 的 UUID（不是 metadata id）。
    """
    try:
        lf.api.dataset_run_items.create(
            run_name=run_name,
            dataset_item_id=dataset_item_id,
            trace_id=trace_id,
        )
        print(f"    [LINKED] trace={trace_id[:8]}... -> run={run_name}")
    except Exception as e:
        print(f"    [LINK ERROR] {e}")


def batch_upload_sessions(
    run_dir: Path,
    run_name: str,
    dataset_name: str,
    skill: str = "cobo-agentic-wallet-sandbox",
    item_ids: list[str] | None = None,
) -> dict[str, str]:
    """批量上传 session 到 Langfuse 并关联 dataset run。

    为每个 session 生成独立 trace UUID，上传后写 trace_map.json。
    返回 trace_map（item_id → trace UUID）。
    """
    session_files = sorted(run_dir.glob("E2E-*.jsonl"))
    if item_ids:
        session_files = [f for f in session_files if f.stem in item_ids]

    if not session_files:
        print("[ERROR] 没有找到 session 文件")
        return {}

    lf = get_langfuse_client()

    # 建立 metadata_id (E2E-01L1) → langfuse dataset item UUID 映射
    ds_items = get_dataset_items(dataset_name)
    meta_to_langfuse: dict[str, str] = {item["id"]: item["langfuse_id"] for item in ds_items}

    # item 上下文，写入 trace metadata（不写入 input，input 只放 session 级信息）
    item_context: dict[str, dict] = {
        item["id"]: {
            "item_id": item["id"],
            "user_message": item.get("user_message", ""),
            "operation_type": item.get("operation_type", ""),
            "difficulty": item.get("difficulty", ""),
        }
        for item in ds_items
    }

    trace_map: dict[str, str] = {}

    print(f"=== 上传 {len(session_files)} 个 session (run: {run_name}) ===\n")

    for session_file in session_files:
        item_id = session_file.stem
        trace_id = str(uuid.uuid4())
        print(f"  [{item_id}] uploading... (trace_id={trace_id[:8]}...)")

        result_trace_id = upload_session(
            str(session_file),
            skill,
            trace_id=trace_id,
            extra_metadata=item_context.get(item_id),
        )
        if result_trace_id:
            trace_map[item_id] = result_trace_id
            print(f"    [INFO] trace_id: {result_trace_id}")
            langfuse_item_id = meta_to_langfuse.get(item_id)
            if langfuse_item_id:
                link_to_dataset_run(lf, langfuse_item_id, run_name, result_trace_id)
            else:
                print(f"    [WARN] Dataset item not found for {item_id}, skipping link")
        else:
            print(f"    [ERROR] Upload failed for {item_id}")

    lf.flush()

    # 写入 trace_map.json，供 score 阶段使用
    trace_map_path = run_dir / "trace_map.json"
    trace_map_path.write_text(json.dumps(trace_map, indent=2, ensure_ascii=False))
    print(f"\ntrace_map: {trace_map_path} ({len(trace_map)} items)")
    print("上传完成")

    return trace_map
