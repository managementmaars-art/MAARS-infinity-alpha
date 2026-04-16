# Changelog

## v2.1.0 (2026-04-13)

### 新增

- `scripts/validate-step1.sh`：ingest Step 1 JSON 格式验证脚本，检查必需字段和置信度值合法性
- `templates/synthesis-template.md`：crystallize 结晶化页面模板
- SKILL.md 置信度赋值规则：明确 EXTRACTED/INFERRED/AMBIGUOUS/UNVERIFIED 的判定标准
- SKILL.md Step 1 验证流程：Step 1 完成后调用 validate-step1.sh，失败自动回退
- SKILL.md 工作流 10 crystallize：对话内容沉淀为 wiki/synthesis/sessions/ 页面
- SKILL.md 路由表：新增 crystallize 关键词路由

### 改进

- `scripts/init-wiki.sh`：创建 `wiki/synthesis/sessions/` 子目录和 `.gitignore`（排除 `.wiki-tmp/`）
- `tests/regression.sh`：新增 9 个测试覆盖 validate-step1.sh 行为和 SKILL.md 内容锁定

## v2.0.0 (2026-04-11)

### 新增

- `purpose.md` 研究方向模板：初始化后直接生成，给后续整理提供明确方向
- `.wiki-cache.json` 本地缓存：为重复素材跳过提供基础设施
- `query` 结果持久化模板：支持把综合回答写回 `wiki/queries/`
- delete 工作流说明和辅助脚本：支持级联删除素材并扫描引用
- Claude Code `SessionStart hook` 支持：可在会话开始时注入 wiki 上下文提示

### 改进

- `SKILL.md`：重构 `ingest` 为两步流程，增加缓存检查、置信度标注和降级说明
- `SKILL.md`：`batch-ingest` 增加无变化跳过统计，`status` 增加 `purpose.md` 状态展示
- `SKILL.md`：`query` 增加重复检测、`derived: true` 标记和自引用防护
- `SKILL.md`：`lint` 增加置信度报告和 EXTRACTED 抽查说明
- `wiki-compat.sh`：兼容旧知识库时同时报告 `purpose.md` 和 `.wiki-cache.json` 状态
- `install.sh`：支持注册和移除 Claude Code 的 `SessionStart hook`

## v0.4.0 (2026-04-05)

### 新增

- 多平台原生入口：同时支持 Claude Code、Codex、OpenClaw
- 统一安装器 `install.sh`：按平台一键安装主 skill 和打包依赖
- 平台适配文档：新增 `platforms/claude/CLAUDE.md`、`platforms/codex/AGENTS.md`、`platforms/openclaw/README.md`
- 安装回归用例：覆盖 Claude dry-run、多平台歧义检测、OpenClaw 安装与自定义路径
- 需求与实施文档：新增多平台需求说明、实施计划和后续 TODO

### 改进

- `README.md`：改成多平台总入口，明确 agent-first 安装方式
- `CLAUDE.md`、`AGENTS.md`：收敛成各平台入口文件，不再把仓库写死为单平台项目
- `SKILL.md`、`init-wiki.sh`、schema 模板：去掉平台专属话术，改成通用 agent 表达
- `setup.sh`：保留旧入口，但改为统一安装器的兼容包装，避免双份逻辑长期分叉

## v0.3.0 (2026-04-05)

### 新增

- `digest` 工作流：跨素材生成深度综合报告
- `graph` 工作流：生成 Mermaid 知识图谱可视化
- `batch-ingest` 工作流：批量消化文件夹中的素材
- 双语支持（中文 / English）
- `tests/regression.sh` 回归测试脚本

### 修复

- `setup.sh`：修复 `declare -A` 在 macOS 默认 bash 3.2 上崩溃的问题，改用兼容写法
- `setup.sh`：Chrome 检查改为检测 9222 调试端口，不再只看进程名；未开调试模式时给出正确启动命令
- `setup.sh`：新增 `uv` 检查，避免 YouTube 字幕提取时缺依赖无提示
- `init-wiki.sh`：修复 `{{LANGUAGE}}` 占位符未被替换的问题
- `init-wiki.sh`：修复路径含特殊字符时可能写坏配置文件的问题
- `SKILL.md`：补上 batch-ingest 缺失的步骤 2
- 模板：删除 entity/source/topic 模板中无意义的空 `[[]]` 链接
- `SKILL.md`：收窄 description 触发范围，避免非知识库场景误触发

### 改进

- README：新增"前置条件"和"常见问题"部分
- README：补充 digest、graph 使用示例
- 一键安装：`setup.sh` 集成 bun/npm install + Chrome 检查

## v0.2.0 (2026-04-04)

### 新增

- 多知识库支持（CWD 检查 + `~/.llm-wiki-path` 回退）
- Chrome + 依赖检查前置
- 一键安装（clone + setup.sh 一条命令）
- 双语模板（动态生成，不拆分模板文件）
- 打包依赖 skill 到 `deps/`，无需网络安装

## v0.1.0 (2026-04-04)

### 新增

- 初始化知识库（init 工作流）
- 消化素材（ingest 工作流）：URL 自动路由、内容分级处理
- 查询知识库（query 工作流）
- 健康检查（lint 工作流）：孤立页面、断链、矛盾信息、索引一致性
- 查看状态（status 工作流）
- Obsidian 兼容的双向链接 `[[页面名]]`
