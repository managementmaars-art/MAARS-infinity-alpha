---
name: caw-eval
metadata:
  version: "2026.04.12.3"
description: |
  评测 CAW (Cobo Agentic Wallet) Agent 质量，产出评分数据和分析报告。
  Use when: 用户想运行 CAW 评测、跑评测、测试 Skill、评估 Agent 质量、
  生成评测报告、弱模型验证、模型兼容性测试，
  或说 "跑评测", "测评 CAW", "eval", "评分", "弱模型验证", "openclaw 评测"。
---

# CAW Eval

端到端评测 CAW Agent 质量，产出评分数据和分析报告。

## 流程路由

根据用户意图选择评测方式，然后**读取对应的 reference 文件并按步骤执行**：

| 用户说 | 评测方式 | 读取并执行 |
|--------|---------|-----------|
| "跑评测"、"测评 CAW"、"eval"、"评分"、"claude code 评测" | **Claude Code 评测** | → 读 [run-eval-cc.md](./references/run-eval-cc.md) 按步骤执行 |
| "弱模型验证"、"openclaw 评测"、"模型兼容性" | **Openclaw 弱模型验证** | 本 SKILL 不直接执行。告诉用户按 [run-eval-openclaw.md](./references/run-eval-openclaw.md) 操作：在服务器 openclaw 中说"跑评测"→ 下载 session 到本地 → 在本地 Claude Code 说"导入 session 并评分" |

**默认走 Claude Code 评测**（如果用户没有明确说"弱模型"或"openclaw"）。

---

## 概览

### Claude Code 评测（主要方式）

在本地 Claude Code 中用 Sonnet subagent 并行执行 + 评分。

```
检查环境 → 获取 case 列表 → Sonnet subagent 并行执行 14 case
→ 收集 session → 上传 Langfuse → LLM Judge 评分 → 应用评分 → 生成报告
```

- 时间：约 40 分钟（14 case 并行 4 个）
- 模型：Sonnet（独立额度，不消耗主额度）
- 详细步骤：[run-eval-cc.md](./references/run-eval-cc.md)

### Openclaw 弱模型验证

在 Openclaw 服务器上用弱模型执行，本地 Claude Code 评分。三层分离架构。

```
服务器: 脚本生成 prompt → 弱模型执行 task → 脚本收集 session → 打包
  ↓ gcp scp
本地: 导入 session → LLM Judge 评分 → 上传 Langfuse → 生成报告
```

- 适用：上线前验证 Skill 对弱模型的兼容性
- 详细步骤：[run-eval-openclaw.md](./references/run-eval-openclaw.md)

---

## 评分体系

```
综合分 = task_completion × 0.3 + process_quality × 0.7
process_quality = S1(意图) × 0.15 + S2(Pact) × 0.45 + S3(执行) × 0.4
```

所有分数 0-1。详见 [scoring.md](./references/scoring.md)。

## 数据集

默认：`caw-agent-eval-seth-v2`（14 case，Ethereum Sepolia 测试链）

可通过 `--dataset-name` 指定其他数据集。已有数据集和创建新数据集参见 [dataset-management.md](./references/dataset-management.md)。

## Scripts

| 脚本 | 用途 |
|------|------|
| `run_eval_cc.py` | Claude Code 评测编排（prepare/collect/upload/score/import-sessions） |
| `run_eval_openclaw.py` | Openclaw 评测编排（prepare/collect/upload/pack） |
| `eval_utils.py` | 公共工具（Langfuse 客户端/数据集/上传） |
| `judge_cc.py` | LLM-as-Judge（prompt 构建 + API 调用） |
| `assertions.py` | 结构化断言 + 门槛检查 |
| `score_traces.py` | 评分管线（断言 + judge → 综合分 → Langfuse） |
| `upload_session.py` | session → Langfuse trace |
| `generate_dataset.py` | 数据集生成 |
