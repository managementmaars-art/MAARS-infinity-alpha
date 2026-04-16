---
name: new-feature
description: 结构化新功能交付工作流，适用于显式 new feature、从需求到实现的一站式功能开发或恢复未完成任务场景；通过项目内 .codex/tasks/ 持久化状态。
---

# New Feature

> **流程主权声明**：本技能是用户显式调用的完整工作流，拥有从需求到实现的全流程控制权。
> 禁止在本流程执行期间调用 `superpowers:brainstorming`、`superpowers:writing-plans` 或任何会接管设计/实现流程的外部 skill。
> 设计文档必须写入 `.codex/tasks/`，不得写入 `docs/superpowers/` 或其他路径。
> 本声明依据 superpowers 自身的优先级规则：用户显式指令 > superpowers skills。

当用户明确要求开发新功能、完整推进一个 feature，或提到 `new-feature`、恢复未完成任务时，使用本技能。

不要用于：

- 小范围 bug 修复
- 纯需求文档或纯设计文档
- 只做一次性代码评审

## 核心方式

1. 运行开始先检查 `.codex/tasks/` 根目录，发现状态已是“已完成”的任务文件时，直接移动到 `.codex/tasks/archived/`。
2. 再检查 `.codex/tasks/` 是否已有未完成任务，检查时忽略 `archived/`；需要恢复时，优先续做而不是重复开题。
3. 先做 3-5 个关键澄清问题，补齐边界、异常和依赖。
4. 再产出实现范围、关键决策和步骤计划；方向明显不止一种时先确认。
5. 使用 `templates/task.md` 在项目内持久化任务状态，边做边更新。
6. 按步骤实现，每完成一步就更新状态、已改文件和验证结果。
7. 完成后做一次 quick review 视角的自查，更新任务状态为“已完成”，再将任务文件移动到 `.codex/tasks/archived/`。

## 协作约束

- 需要需求深挖时，套用 `requirement` 的方式
- 需要技术设计时，套用 `design` 的方式
- 完成前自审时，套用 `cc-review` 的优先级
- 语言和框架细节交给对应语言 skills

## 输出要求

- 明确区分需求澄清、设计决定、实现步骤和验证结果
- 若当前信息不足以安全开工，先问关键问题
- 任务文件始终与当前进度保持一致
- 完成后说明残余风险和后续建议

## 按需展开

- 恢复策略：`references/resume-policy.md`
- 编排方式：`references/orchestration.md`
- 任务模板：`templates/task.md`
