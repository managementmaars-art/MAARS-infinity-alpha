# Resume Policy

恢复优先级：

1. 用户显式要求 `--resume` 或“继续上次任务”
2. `.codex/tasks/` 中存在明显未完成任务（忽略 `archived/`）
3. 两者都没有时，开始新任务

处理原则：

- 每次运行先扫描 `.codex/tasks/` 根目录；状态已是“已完成”的任务直接移到 `.codex/tasks/archived/`
- 未完成任务只有一个时，直接询问是否继续
- 有多个未完成任务时，列出名称和更新时间，让用户选
- 用户拒绝恢复时，把旧任务移到 `.codex/tasks/archived/` 后再开始新任务
- 已完成任务不留在 `.codex/tasks/` 根目录，完成后移动到 `.codex/tasks/archived/`
- 不要静默覆盖旧任务文件
