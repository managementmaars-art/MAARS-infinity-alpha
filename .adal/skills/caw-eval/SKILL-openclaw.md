---
name: caw-eval-openclaw
metadata:
  version: "2026.04.12.1"
description: |
  在 Openclaw 上跑 CAW Agent 评测。
  Use when: 用户说"跑评测", "测评 CAW", "eval", "评估"。
---

# CAW 评测

按以下 3 步执行。每步完成后继续下一步。

## Step 1: 生成评测任务

运行以下命令：

```bash
cd /home/luochong_cobo_com/skills/caw-eval/scripts
python3 run_eval_openclaw.py prepare --dataset-name caw-agent-eval-seth-v2
```

命令会在 `/tmp/eval-prompts/` 下生成文件。读取 `/tmp/eval-prompts/_all_tasks.txt` 的内容。

## Step 2: 逐个执行任务

对 `_all_tasks.txt` 中的每个 Task：
1. 找到 ```prompt 和 ``` 之间的内容
2. 用 task subagent 执行该内容
3. 等 task 完成
4. 继续下一个 Task

**不需要分析结果，不需要上传，只需要逐个执行完所有 Task。**

## Step 3: 收集并打包

所有 Task 执行完后，运行：

```bash
cd /home/luochong_cobo_com/skills/caw-eval/scripts
python3 run_eval_openclaw.py collect --run-name eval-oc-$(date +%Y%m%d)
python3 run_eval_openclaw.py pack --run-name eval-oc-$(date +%Y%m%d)
```

告诉用户打包文件的路径和下载命令。
