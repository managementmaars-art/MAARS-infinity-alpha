# Openclaw 弱模型验证：完整说明

## 概述

在 Openclaw 服务器上用弱模型验证 CAW Skill 的兼容性。三层分离架构：

```
服务器 Openclaw（弱模型）           本地 Claude Code（Sonnet）
┌─────────────────────────┐       ┌─────────────────────────┐
│ 弱模型读 SKILL-openclaw │       │                         │
│   Step 1: prepare       │       │ 导入 session            │
│   Step 2: 逐个 task     │       │ LLM Judge 评分          │
│   Step 3: collect + pack│       │ 上传 Langfuse           │
└─────────────────────────┘       │ 生成报告                │
         ↓ gcloud scp             └─────────────────────────┘
```

---

## 前置条件（一次性准备）

### 服务器环境

```bash
# 1. caw 环境就绪
export PATH="$HOME/.cobo-agentic-wallet/bin:$PATH"
caw status          # healthy=true, signing_ready=true
caw wallet balance  # SETH >= 0.2

# 2. 充值测试币（如果余额不足）
# 从公共 Sepolia faucet 领取：
#   https://www.alchemy.com/faucets/ethereum-sepolia（每次 0.5 SETH）
#   https://faucets.chain.link/sepolia（每次 0.1 SETH）

# 3. cobo-agentic-wallet-sandbox skill 已安装
npx skills add cobosteven/cobo-agent-wallet-manual --skill cobo-agentic-wallet-sandbox-sandbox --yes --global

# 4. caw-eval-openclaw skill 已安装
# 方式 A：从远程安装
npx skills add cobosteven/cobo-agent-wallet-manual --skill caw-eval-openclaw --yes --global
# 方式 B：手动复制（开发阶段）
mkdir -p ~/.openclaw/skills/caw-eval-openclaw
cp SKILL-openclaw.md ~/.openclaw/skills/caw-eval-openclaw/SKILL.md

# 5. 评测脚本已部署到服务器
# 需要以下文件：
#   run_eval_openclaw.py
#   eval_utils.py
#   upload_session.py
#   .env（含 Langfuse 凭证）
# 放到统一目录，如 /home/luochong_cobo_com/skills/caw-eval/scripts/

# 6. Python 依赖
pip install langfuse python-dotenv
```

### 本地环境

确认 Claude Code 能访问项目代码即可。无需额外准备。

---

## 操作流程

### 第一步：在 Openclaw 中跑评测

在服务器上打开 openclaw 对话，输入：

```
跑评测
```

弱模型读 `caw-eval-openclaw` skill 后，自动执行：
1. 运行 `prepare` 生成所有 task prompt
2. 逐个调 `task subagent` 执行 14 个 case
3. 运行 `collect` + `pack` 收集并打包 session

完成后会输出打包文件路径和下载命令。

> **如果弱模型不理解**：改为手动操作——在服务器终端运行 `python3 run_eval_openclaw.py prepare`，然后把 `_all_tasks.txt` 内容粘贴到 openclaw 对话中。

### 第二步：下载到本地

在 Mac 终端执行 Openclaw 给出的下载命令：

```bash
gcloud compute scp <实例名>:/tmp/eval-oc-*.tar.gz ~/Downloads/ \
  --zone=<zone> --project=<project-id>

mkdir -p /tmp/oc-sessions
tar xzf ~/Downloads/eval-oc-*.tar.gz -C /tmp/oc-sessions/
```

### 第三步：在 Claude Code 中评分

在 Claude Code 中说：

```
读 cobo-agent-wallet/sdk/skills/caw-eval/SKILL.md
导入 /tmp/oc-sessions/ 的 openclaw session，run name 为 eval-oc-weak-YYYYMMDD-HHMM，然后评分出报告
```

Claude Code 自动执行：import-sessions → LLM Judge 评分 → 上传 Langfuse → 生成报告。

---

## 对比分析

评分完成后，对比 Sonnet vs 弱模型的分数：

| 情况 | 含义 | 行动 |
|------|------|------|
| Sonnet 过 + 弱模型也过 | Skill 兼容性好 | 上线质量有保障 |
| Sonnet 过 + 弱模型挂 | Skill 指令不够清晰 | 简化 Skill 指令 |
| Sonnet 也挂 | Skill 有 bug | 必须修 |

---

## 服务器端脚本说明

| 脚本 | 子命令 | 说明 |
|------|--------|------|
| `run_eval_openclaw.py` | `prepare` | 从 Langfuse 拉 items，生成 task prompt + 汇总 _all_tasks.txt |
| | `collect` | 在 openclaw session 目录中 grep 搜索 eval 标记，收集到统一目录 |
| | `upload` | 上传 session 到 Langfuse（可选，也可在本地上传） |
| | `pack` | 打包 session 目录为 tar.gz，输出下载命令 |
| `eval_utils.py` | — | 公共工具（Langfuse 客户端/数据集操作/上传函数） |
| `upload_session.py` | — | session.jsonl → Langfuse trace |

---

## Troubleshooting

| 问题 | 解决 |
|------|------|
| openclaw 说"不理解跑评测" | 确认 caw-eval-openclaw skill 已安装（openclaw 中输入 `/skills` 查看） |
| 弱模型跑到一半停了 | 正常，弱模型能力有限。输入"继续执行剩余 task"或手动在终端跑 collect |
| collect 找不到 session | 确认 task 已完成，检查 `~/.openclaw/agents/main/sessions/` 下是否有文件 |
| prepare 报 "Langfuse credentials not set" | 检查 `.env` 文件是否存在且凭证正确 |
| gcloud scp 报错 | 确认 zone/project-id 正确（在服务器上查 metadata） |
| 本地导入后评分报错 | 确认 session 文件是 `.jsonl` 格式，文件名以 `E2E-` 开头 |
