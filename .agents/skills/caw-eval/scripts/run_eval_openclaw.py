#!/usr/bin/env python3
"""
Openclaw 弱模型评测脚本 — 三层分离方案的服务器端。

在 Openclaw 服务器上运行，零 LLM 依赖。负责：
  1. prepare  — 从 Langfuse 拉 dataset items，生成 task prompt 文件
  2. collect  — 在 openclaw session 目录中搜索 eval 标记，收集 session 文件
  3. upload   — 将收集的 session 上传到 Langfuse

执行 caw 命令由 openclaw 对话中的弱模型完成（粘贴 prepare 生成的汇总 prompt）。

用法:
    # Step 1: 生成 prompt
    python run_eval_openclaw.py prepare --dataset-name caw-agent-eval-seth-v2

    # Step 2: 在 openclaw 对话中粘贴 _all_tasks.txt 的内容，弱模型逐个执行 task

    # Step 3: 收集 session
    python run_eval_openclaw.py collect --run-name eval-oc-weak-20260412

    # Step 4: 上传到 Langfuse（可选，也可以拉到本地后上传）
    python run_eval_openclaw.py upload --run-name eval-oc-weak-20260412

    # Step 5: 打包 session 供本地下载评分
    python run_eval_openclaw.py pack --run-name eval-oc-weak-20260412
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from eval_utils import batch_upload_sessions, get_dataset_items

_SCRIPTS_DIR = Path(__file__).parent

# Openclaw session 文件的搜索路径
_OC_SESSION_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

# 评测 run 的本地存储目录
_RUNS_DIR = Path.home() / ".caw-eval" / "runs"


def build_task_prompt(item: dict) -> str:
    """构建单个 item 的 task subagent prompt。"""
    item_id = item["id"]
    user_message = item["user_message"]

    return f"""[EVAL:{item_id}]
cobo-agentic-wallet-sandbox skill 已激活。

**评测模式约束 — 仅针对 skill 内部的交互流程，不影响对用户指令本身的响应：**

需要自动跳过的 skill 内部交互（来自 cobo-agentic-wallet-sandbox skill）：
- 提交 pact 时：跳过展示预览和等待用户确认的步骤，直接调用 `caw pact submit` 提交
- 交易返回 `status=pending_approval` 且 `owner_linked=false` 时：立即自动执行 `caw pending approve <pending_operation_id>`
- 如遇到无法自动化处理的真实阻塞（如 `owner_linked=true` 需要 Human App 审批），记录原因并跳过，继续执行其余步骤

这是自动化评测，无人工实时监控，须完整执行至结束，不得因 skill 内部的交互流程而中断。

按照以下用户指令完成操作：

{user_message}"""


def build_all_tasks_prompt(items: list[dict]) -> str:
    """构建汇总 prompt——弱模型只需循环调 task subagent。"""
    lines = [
        "你需要依次执行以下评测任务。对每个任务，使用 task subagent 执行。",
        "",
        "## 执行方式",
        "",
        "对下面的每个任务：",
        "1. 调用 task subagent，prompt 为该任务 ```prompt 和 ``` 之间的完整内容",
        "2. 等待 task 完成",
        "3. 继续下一个任务",
        "",
        "不需要上传、不需要评分、不需要分析结果。只需要逐个执行。",
        "",
        f"共 {len(items)} 个任务。",
        "",
        "---",
        "",
    ]

    for i, item in enumerate(items):
        prompt = build_task_prompt(item)
        lines.append(
            f"### Task {i + 1}: {item['id']} ({item['operation_type']} {item['difficulty']})"
        )
        lines.append("")
        lines.append("```prompt")
        lines.append(prompt)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


# ── prepare 子命令 ──────────────────────────────────────────────────────────────


def cmd_prepare(dataset_name: str, output_dir: str | None, item_ids: list[str] | None) -> None:
    """生成 task prompt 文件。"""
    items = get_dataset_items(dataset_name)
    if item_ids:
        items = [i for i in items if i["id"] in item_ids]

    if not items:
        print("[ERROR] 没有匹配的 items")
        sys.exit(1)

    out_dir = Path(output_dir) if output_dir else Path("/tmp/eval-prompts")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== 生成 {len(items)} 个 task prompt ===\n")

    # 生成单个 prompt 文件
    for item in items:
        prompt = build_task_prompt(item)
        prompt_file = out_dir / f"{item['id']}.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        print(
            f"  [{item['id']}] [{item['operation_type']:15s}] [{item['difficulty']}] -> {prompt_file.name}"
        )

    # 生成汇总 prompt
    all_prompt = build_all_tasks_prompt(items)
    all_file = out_dir / "_all_tasks.txt"
    all_file.write_text(all_prompt, encoding="utf-8")

    print(f"\n文件位置: {out_dir}")
    print(f"汇总 prompt: {all_file}")
    print("\n下一步：在 openclaw 对话中粘贴 _all_tasks.txt 的内容，弱模型会逐个执行 task。")


# ── collect 子命令 ─────────────────────────────────────────────────────────────


def cmd_collect(
    dataset_name: str,
    run_name: str,
    item_ids: list[str] | None,
    session_dir: str | None,
) -> None:
    """收集 openclaw session 文件。"""
    items = get_dataset_items(dataset_name)
    if item_ids:
        items = [i for i in items if i["id"] in item_ids]

    search_dir = Path(session_dir) if session_dir else _OC_SESSION_DIR
    run_dir = _RUNS_DIR / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== 收集 session 文件 (run: {run_name}) ===")
    print(f"搜索目录: {search_dir}\n")

    if not search_dir.exists():
        print(f"[ERROR] 搜索目录不存在: {search_dir}")
        sys.exit(1)

    collected = 0
    missing = []

    for item in items:
        item_id = item["id"]
        marker = f"[EVAL:{item_id}]"
        found = []

        for jsonl_file in search_dir.rglob("*.jsonl"):
            try:
                text = jsonl_file.read_text(encoding="utf-8", errors="ignore")
                if marker in text:
                    found.append(jsonl_file)
            except OSError:
                continue

        if found:
            # 按修改时间取最新
            found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            src = found[0]
            dst = run_dir / f"{item_id}.jsonl"
            shutil.copy2(src, dst)
            size_kb = dst.stat().st_size / 1024
            print(f"  [{item_id}] OK  ({size_kb:.0f} KB) <- {src.name}")
            collected += 1
        else:
            print(f"  [{item_id}] MISSING")
            missing.append(item_id)

    print(f"\n收集完成: {collected}/{len(items)} 个 session")
    if missing:
        print(f"缺失: {', '.join(missing)}")
    print(f"文件位置: {run_dir}")

    # 写 manifest
    manifest = {
        "run_name": run_name,
        "dataset_name": dataset_name,
        "source": "openclaw",
        "collected_at": datetime.now(tz=timezone.utc).isoformat(),
        "items": {
            item["id"]: {
                "status": "collected" if item["id"] not in missing else "missing",
                "operation_type": item["operation_type"],
                "difficulty": item["difficulty"],
            }
            for item in items
        },
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


# ── upload 子命令 ──────────────────────────────────────────────────────────────


def cmd_upload(
    run_name: str,
    dataset_name: str,
    item_ids: list[str] | None,
    skill: str,
) -> None:
    """上传 session 到 Langfuse。"""
    run_dir = _RUNS_DIR / run_name
    if not run_dir.exists():
        print(f"[ERROR] Run 目录不存在: {run_dir}")
        sys.exit(1)

    batch_upload_sessions(run_dir, run_name, dataset_name, skill, item_ids)


# ── pack 子命令 ────────────────────────────────────────────────────────────────


def cmd_pack(run_name: str) -> None:
    """打包 session 文件，方便下载到本地。"""
    run_dir = _RUNS_DIR / run_name
    if not run_dir.exists():
        print(f"[ERROR] Run 目录不存在: {run_dir}")
        sys.exit(1)

    archive = f"/tmp/eval-oc-{run_name}.tar.gz"
    subprocess.run(
        ["tar", "czf", archive, "-C", str(run_dir), "."],
        check=True,
    )

    size_mb = Path(archive).stat().st_size / 1024 / 1024
    print(f"打包完成: {archive} ({size_mb:.1f} MB)")
    print("\n下载到本地：")
    print(
        f"  gcloud compute scp <实例名>:{archive} ~/Downloads/ --zone=<zone> --project=<project-id>"
    )


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M")

    parser = argparse.ArgumentParser(
        description="Openclaw 弱模型评测脚本（三层分离方案的服务器端）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    # ── prepare
    p_prepare = sub.add_parser("prepare", help="生成 task prompt 文件")
    p_prepare.add_argument("--dataset-name", default="caw-agent-eval-seth-v2")
    p_prepare.add_argument("--output-dir", help="输出目录（默认 /tmp/eval-prompts）")
    p_prepare.add_argument("--item-id", nargs="*", help="只生成指定 item")

    # ── collect
    p_collect = sub.add_parser("collect", help="收集 openclaw session 文件")
    p_collect.add_argument("--dataset-name", default="caw-agent-eval-seth-v2")
    p_collect.add_argument("--run-name", default=f"eval-oc-weak-{ts}")
    p_collect.add_argument("--item-id", nargs="*", help="只收集指定 item")
    p_collect.add_argument("--session-dir", help="自定义 session 搜索目录")

    # ── upload
    p_upload = sub.add_parser("upload", help="上传 session 到 Langfuse")
    p_upload.add_argument("--run-name", required=True)
    p_upload.add_argument("--dataset-name", default="caw-agent-eval-seth-v2")
    p_upload.add_argument("--item-id", nargs="*", help="只上传指定 item")
    p_upload.add_argument("--skill", default="cobo-agentic-wallet-sandbox")

    # ── pack
    p_pack = sub.add_parser("pack", help="打包 session 文件供下载")
    p_pack.add_argument("--run-name", required=True)

    args = parser.parse_args()

    if args.cmd == "prepare":
        cmd_prepare(
            dataset_name=args.dataset_name,
            output_dir=args.output_dir,
            item_ids=args.item_id,
        )
    elif args.cmd == "collect":
        cmd_collect(
            dataset_name=args.dataset_name,
            run_name=args.run_name,
            item_ids=args.item_id,
            session_dir=args.session_dir,
        )
    elif args.cmd == "upload":
        cmd_upload(
            run_name=args.run_name,
            dataset_name=args.dataset_name,
            item_ids=args.item_id,
            skill=args.skill,
        )
    elif args.cmd == "pack":
        cmd_pack(run_name=args.run_name)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
