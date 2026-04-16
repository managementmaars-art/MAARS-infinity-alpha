# codegen sdk

根据 Dataset 操作定义生成 TypeScript SDK 调用代码。

## 命令

```bash
rabetbase codegen sdk --alias order --operation filter --format json
rabetbase codegen sdk --code 097b7361b76c42bcb12b923fa5a08861 --operation create --format json
rabetbase codegen sdk --alias productSku --operation getOne --skip-imports > ./src/api/getSku.ts
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--code <code>` | string | 与 alias 二选一 | — | Dataset code（32 位 hex UUID） |
| `--alias <name>` | string | 与 code 二选一 | — | `api.ts` 中定义的别名 |
| `--operation <name>` | string | 是 | — | 操作名（`filter` `getOne` `create` `update` `delete`） |
| `--skip-imports` | boolean | 否 | — | 不包含 import 语句 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

生成的 TypeScript 代码直接打印到 stdout，可重定向到文件。

## 提示

- 生成前先用 `dataset operations --operation <name>` 确认操作存在
- `--skip-imports` 适合追加到已有文件
- 生成代码包含完整类型标注和注释

## 参考

- [SKILL.md](../SKILL.md)
