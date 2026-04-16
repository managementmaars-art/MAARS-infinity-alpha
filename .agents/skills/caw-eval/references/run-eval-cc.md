# Claude Code 评测：执行步骤

**本文件是 Agent 的执行指南。按 Step 1-9 依次执行即可。**

---

## Step 1: 检查环境

```bash
export PATH="$HOME/.cobo-agentic-wallet/bin:$PATH"
caw status          # 确认 healthy=true, signing_ready=true
caw wallet balance  # 确认 SETH 有余额（建议 >= 0.2）
```

如果环境不就绪，提示用户先完成 onboarding（参考 cobo-agentic-wallet skill）。

---

## Step 2: 获取 test case 列表

```bash
cd <repo>/cobo-agent-wallet
.venv/bin/python sdk/skills/caw-eval/scripts/run_eval_cc.py prepare \
  --dataset-name caw-agent-eval-seth-v2
```

> 默认数据集为 `caw-agent-eval-seth-v2`（14 case）。可通过 `--dataset-name` 指定其他数据集。

输出每个 case 的 item_id 和 user_message。记下这些信息用于 Step 3。

---

## Step 3: 执行评测（Sonnet subagent 并行）

对每个 case，启动一个后台 Sonnet subagent。**始终保持 4-5 个并行**，一个完成就补一个新的。

**为什么用 Sonnet**：Sonnet 有独立的周额度（Weekly Sonnet），不消耗主额度。

**subagent 调用方式**：

```python
Agent(
    model="sonnet",
    run_in_background=True,
    description="Eval {item_id}",
    prompt="""[EVAL:{item_id}]

你是 CAW (Cobo Agentic Wallet) Agent。请先读取 Skill 指令，然后执行用户操作。

## 读取 Skill
1. {repo}/sdk/skills/cobo-agentic-wallet-dev/SKILL.md
2. {repo}/sdk/skills/cobo-agentic-wallet-dev/references/pact.md
3. {repo}/sdk/skills/cobo-agentic-wallet-dev/references/error-handling.md

## 评测约束
- 不得复用已有的 active pact，必须为本次任务创建新的 pact（评测需要评估 pact 协商能力）
- 提交 pact 时跳过预览和确认，直接 `caw pact submit`
- `pending_approval` 且 `owner_linked=false` 时自动 `caw pending approve`
- 无法自动化的阻塞记录原因并跳过
- 自动化评测，须完整执行至结束

## 环境
- caw: `export PATH="$HOME/.cobo-agentic-wallet/bin:$PATH"`
- 环境: sandbox, signing_ready=true
- 工作目录: {repo}/cobo-agent-wallet

## 用户指令
{user_message}"""
)
```

**时间预估**：
- 简单操作（transfer/error/edge）：1-2 分钟
- DeFi 操作（swap/lend/dca）：5-15 分钟
- 14 case 并行 4 个：约 40 分钟总计

等待所有 subagent 完成。

---

## Step 4: 收集 session

```bash
.venv/bin/python sdk/skills/caw-eval/scripts/run_eval_cc.py collect \
  --dataset-name caw-agent-eval-seth-v2 \
  --run-name eval-cc-sonnet-$(date +%Y%m%d-%H%M)
```

确认 14/14 个 session 都收集到。脚本搜索 `~/.claude/projects/` 下包含 `[EVAL:{item_id}]` 标记的 subagent session 文件。

---

## Step 5: 上传 session 到 Langfuse

```bash
.venv/bin/python sdk/skills/caw-eval/scripts/run_eval_cc.py upload \
  --run-name {run_name} \
  --dataset-name caw-agent-eval-seth-v2
```

脚本为每个 session 生成独立的 Langfuse trace（UUID），并关联到 dataset run。同时在 run 目录下生成 `trace_map.json`，记录 item_id → trace UUID 的映射，供后续评分使用。

确认输出中每个 item 都显示 `[LINKED]`。

---

## Step 6: 生成精细版 judge prompt

```bash
.venv/bin/python sdk/skills/caw-eval/scripts/score_traces.py session \
  --session ~/.caw-eval/runs/{run_name}/ \
  --dataset-name caw-agent-eval-seth-v2 \
  --dump-judge-requests ~/.caw-eval/runs/{run_name}/judge_req.json
```

生成 14 个精细版 judge request（含断言结果 + pact 参数 + expected output）。judge request 保存在 run 目录下，避免不同 run 之间互相覆盖。

---

## Step 7: LLM Judge 评分（Sonnet subagent）

读取 `~/.caw-eval/runs/{run_name}/judge_req.json` 中的每个 request，启动 Sonnet subagent 评分。**每个 session 单独一个 subagent**。所有 judge 输出文件保存在 run 目录下（`~/.caw-eval/runs/{run_name}/judge_*.json`）。

```python
# 读取 judge_req.json，对每个 request：
judge_dir = "~/.caw-eval/runs/{run_name}"

Agent(
    model="sonnet",
    run_in_background=True,
    description="Judge {item_id}",
    prompt="""你是 CAW Agent 评估专家。请对以下 session 文件进行评分。

读取 session 文件：{session_path}

**评估上下文**：
- 用户指令: {user_message}
- 成功标准: {success_criteria}
- pact_hints: {pact_hints}
- 断言结果: {assertion_context}

**评分维度**（0-1 分，每个维度附 reasoning）：
- intent_understanding: Agent 是否正确理解用户意图（操作类型、资产、链）
- policies_correctness: pact policies 是否与用户意图匹配（deny_if 限额、scope 最小化）
- completion_conditions_correctness: 完成条件是否合理（tx_count/time_elapsed）
- execution_correctness: 命令和参数是否正确
- result_reporting: 结果汇报和错误处理是否合理
- task_completion: 任务是否完成（0=失败, 0.5=部分, 1=成功。幻觉→0）

将结果写入 {judge_dir}/judge_{item_id}.json，格式：
{{
  "item_id": "{item_id}",
  "intent_understanding": {{"score": 0.0, "reasoning": "..."}},
  "policies_correctness": {{"score": 0.0, "reasoning": "..."}},
  "completion_conditions_correctness": {{"score": 0.0, "reasoning": "..."}},
  "execution_correctness": {{"score": 0.0, "reasoning": "..."}},
  "result_reporting": {{"score": 0.0, "reasoning": "..."}},
  "task_completion": {{"score": 0.0, "reasoning": "..."}}
}}"""
)
```

所有 judge 完成后，合并结果：

```python
# 合并所有 judge_E2E-*.json 到 judge_results.json（同一 run 目录下）
import json, glob
run_dir = "~/.caw-eval/runs/{run_name}"
results = []
for f in sorted(glob.glob(f"{run_dir}/judge_E2E-*.json")):
    results.append(json.loads(open(f).read()))
open(f"{run_dir}/judge_results.json", "w").write(json.dumps(results, indent=2, ensure_ascii=False))
```

---

## Step 8: 应用评分到 Langfuse

```bash
.venv/bin/python sdk/skills/caw-eval/scripts/score_traces.py session \
  --session ~/.caw-eval/runs/{run_name}/ \
  --dataset-name caw-agent-eval-seth-v2 \
  --judge-results ~/.caw-eval/runs/{run_name}/judge_results.json \
  --report
```

评分写入 Step 5 上传的各 trace（通过 `trace_map.json` 定位），同时在 Langfuse dataset run 页面可按维度查看分数。

---

## Step 9: 生成报告

基于 Step 7 的评分数据和 Step 3 的运行指标，生成评测报告：

```
reports/eval-report-{run_name}-seth-v2.md
```

> run_name 已含时间戳（如 `eval-cc-sonnet-20260412-1430`），报告文件名自动唯一。

报告内容：
1. 总览（E2E 综合分 + 任务完成率）
2. 逐 Case 评分（按分数从低到高）
3. 运行指标分析（时长/tokens/caw 命令/错误数/pact 效率 + 异常指标分析）
4. 逐 Case 详细分析（执行过程 → 问题 → Action Item）
5. 按场景类型分析
6. 阶段瓶颈分析（S1/S2/S3 各维度问题）
7. 改进建议（P0/P1/P2 分级）
8. 上线建议

参考已有报告格式：`reports/eval-report-20260411-sonnet-seth-v2.md`

---

## Troubleshooting

| 问题 | 解决 |
|------|------|
| caw status 报错 | 运行 `scripts/bootstrap-env.sh` 安装 caw |
| signing_ready=false | 需要重新 onboard（`caw onboard --env sandbox`） |
| collect 找不到 session | 确认 subagent 全部完成，检查 `~/.claude/projects/` 下是否有 `agent-*.jsonl` |
| Langfuse 凭证缺失 | 配置 `scripts/.env`（参考 `.env.example`） |
| score_traces.py 报 "No items loaded" | 确认 `--dataset-name caw-agent-eval-seth-v2` 正确 |
