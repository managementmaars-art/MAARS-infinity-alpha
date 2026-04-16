# Prompt Templates

Use these templates as starting points. Adapt wording to the repository and the user's context, but preserve the sequencing and guardrails.

## 1. Design Clarification

```text
`PRD.md` 里有一份初步的产品需求文档。先完整阅读，再针对性地提出问题，和我讨论清楚需求。等关键问题都明确后，生成一份 Markdown 格式的 `design-document.md`。
```

## 2. Tech Stack Recommendation

```text
基于 `design-document.md`，推荐最合适的技术栈。要求简单但健壮，输出为 Markdown 文件 `tech-stack.md`。请覆盖主要技术选择和简短理由。
```

## 3. Implementation Plan

```text
基于 `design-document.md` 和 `tech-stack.md`，生成一份详细的实施计划，输出到 `implementation-plan.md`。包含一系列给 AI 开发者的分步指令。每一步都要小而具体，每一步都必须包含验证正确性的测试，严禁包含代码，只写清晰、具体的指令。
```

## 4. Memory-Bank Setup

```text
创建 `memory-bank/` 目录，将 `design-document.md`、`tech-stack.md`、`implementation-plan.md` 移动到该目录，并创建两个空文件：`progress.md`、`architecture.md`。检查所有文档里涉及这些文件路径的地方，并同步修正。
```

## 5. Plan Clarification Round

```text
阅读 `memory-bank/` 里的所有文档。检查 `implementation-plan.md` 是否已经对你 100% 清晰。如果还有任何歧义、缺少决策或执行风险，请逐条提问。等我回答后，更新相关文档。
```

## 6. Execute Step 1

```text
阅读 `memory-bank/` 里的所有文档，然后执行实施计划的第 1 步。我会负责跑测试。在我验证通过前，不要开始第 2 步。验证通过后，更新 `progress.md`，记录你做了什么；再更新 `architecture.md`，解释新增或变更文件的作用。
```

## 7. Execute Later Steps

```text
阅读 `memory-bank/` 所有文件，并阅读 `progress.md` 了解之前的工作进度，然后继续实施计划的第 X 步。在我验证当前步骤前，不要开始第 X+1 步。完成后更新 `progress.md` 和 `architecture.md`。
```

## 8. Required Agent Note

Append this block to `AGENTS.md` and/or `CLAUDE.md`:

```md
## 重要提示

- 写任何代码前必须完整阅读 memory-bank/@architecture.md
- 写任何代码前必须完整阅读 memory-bank/@design-document.md
- 每完成一个重大功能或里程碑后，必须更新 memory-bank/@architecture.md
```
