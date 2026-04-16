# bff new

在本地脚手架创建一个新的 BFF 脚本文件。

## 命令

```bash
rabetbase bff new --type ENDPOINT --name getUserList --description "获取用户列表" --format json
rabetbase bff new --type COMMON --name normalizePayload --format json
rabetbase bff new --type HOOK --name beforeFilter --alias appUser --operation-type filter --function-node before --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--type <type>` | string | 是 | — | 脚本类型：`COMMON` / `ENDPOINT` / `HOOK` |
| `--name <name>` | string | 是 | — | 函数名（合法 JS 标识符） |
| `--description <desc>` | string | 否 | — | 脚本描述 |
| `--alias <alias>` | string | HOOK 时推荐 | — | 数据集 alias |
| `--datasetcode <code>` | string | HOOK 兜底 | — | 数据集编码 |
| `--operation-type <op>` | string | HOOK 必填 | — | 如 `getOne` / `filter` / `create` |
| `--function-node <node>` | string | HOOK 必填 | — | `before` / `after` |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 本地路径

| 类型 | 路径 |
|------|------|
| ENDPOINT | `.rabetbase/bff/<appCode>/ENDPOINT/<name>.js` |
| COMMON | `.rabetbase/bff/<appCode>/COMMON/<name>.js` |
| HOOK | `.rabetbase/bff/<appCode>/HOOK/<alias-or-datasetCode>/<operationType>/<functionNode>/<name>.js` |

BFF 源码**仅**应在此目录树内创建与长期维护（与 `bff status` / `bff push` 扫描一致）；不要在本仓库其他路径手写 BFF 再尝试推送。

## 提示

- `HOOK` 非交互场景建议优先传 `--alias`
- 如果 alias 解析失败，再用 `--datasetcode`
- 创建后先跑 `rabetbase bff status --format json` 确认本地状态

## 参考

- [SKILL.md](../SKILL.md)
- [bff-creation-workflow.md](../guides/bff-creation-workflow.md)

