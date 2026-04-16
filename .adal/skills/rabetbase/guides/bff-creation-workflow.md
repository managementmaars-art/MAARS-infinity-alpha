# BFF 工作流规则

前置知识：`backend-function.md`

## 核心原则

平台是唯一 source of truth。修改已有脚本时，从平台拉取最新内容。

## 工作流

```
速查公共函数 → 确认需求 → 校验字段 → [按需]查平台 → 编写本地脚本 → 自检 → status → dry-run → push/pull
```

### 0. 速查公共函数
执行 `rabetbase bff list --format json`（type=COMMON）查看已有公共函数。如有可复用的工具函数，在后续脚本中直接 import，避免重复实现。

### 1. 确认需求
写码前必须明确：类型（ENDPOINT/HOOK/COMMON）、函数名、入参、返回结构、涉及的数据集。缺失则先问用户。

### 2. 校验字段
执行 `rabetbase dataset detail --code <数据集编码> --format json` 确认字段名、类型、枚举值、关联关系。禁止凭经验猜字段名。

### 3. 查平台（按需）
* 新建 → 跳过
* 修改已有 → 执行 `rabetbase bff list --format json`（ENDPOINT 或 COMMON） + `rabetbase bff detail --id <id> --format json` 取 `id` 和最新内容
* 不确定 → 查一下

命中同名脚本时，停下问用户：修改还是另起新名。

### 4. 编写脚本（规范路径）
新建脚本应使用 **`rabetbase bff new`**，在 **`.rabetbase/bff/<appCode>/...`** 下生成脚手架后再编辑（路径与 `bff status` / `bff push` 一致）。**不要**在 `src/` 或仓库任意目录手写 BFF 再期望被 CLI 识别。
已有脚本仅在上述 BFF 树内修改；与 `backend-function.md` 中的目录约定一致。

### 5. 自检
* 方法名正确
* 单条查询用 `getOne`
* BFF 中 `sql.execute` 返回数组，不是 `{ execSuccess, execResult }`
* 参数校验、错误处理、脱敏

### 6. 检查本地状态
执行 `rabetbase bff status --format json`：
* 确认新增脚本进入 `added`
* 确认修改脚本进入 `modified`
* 若状态异常，先不要推送

### 7. 预览推送
执行 `rabetbase bff push --type <type> --name <name> --dry-run --format json`：
* 查看本次是 `create` 还是 `update`
* 检查目标 `lockKey`、`filePath` 和预期状态
* dry-run 不会上传远端，也不会改 lock

### 8. 推送到平台
执行 `rabetbase bff push --yes --type <type> --name <name> --format json`：
* 成功项进入 `uploaded`
* 未变更项进入 `skipped: unchanged`
* 失败项进入 `failed`

### 9. 本地文件
脚本内容直接保存在本地文件中，纳入 Git 管理。路径遵循 `.rabetbase/bff/<appCode>/` 目录约定（详见 `backend-function.md`）：
* ENDPOINT → `.rabetbase/bff/<appCode>/ENDPOINT/<name>.js`
* HOOK → `.rabetbase/bff/<appCode>/HOOK/<alias>/<operationType>/<functionNode>/<name>.js`
* COMMON → `.rabetbase/bff/<appCode>/COMMON/<name>.js`

## 冲突处理

若返回 `failed`：
* 告知用户失败的 `lockKey` 和错误原因
* 不要假装成功
* 已成功推送的其他脚本不会自动回滚

## 本地文件

正常流程：先在本地创建/修改，再通过 `push` 同步远端，路径同 Step 9（`.rabetbase/bff/<appCode>/` 下）。
例外场景：
* 用户主动要求"同步平台最新到本地" → 从平台拉取 → 覆盖本地（`bff pull`）
* 用户要求删除脚本 → `bff delete --yes --target ...`

修改已有脚本时，从平台拉取最新内容。

## 修改已有脚本

`rabetbase bff list --format json` → `rabetbase bff detail --id <id> --format json` 拉最新内容 → 如需覆盖本地则 `bff pull` → 修改本地文件 → `bff status` → `bff push --yes`

## BFF 语义差异

| 场景 | 前端 SDK | BFF (context.client) |
|------|---------|---------------------|
| SQL 返回值 | `{ execSuccess, execResult }` | 直接返回数组 |
| 前端调 BFF | `client.bff.execute({ scriptName, params })` 返回业务数据 | — |
