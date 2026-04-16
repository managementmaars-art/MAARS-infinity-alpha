# codegen sql

根据已保存的 SQL 查询生成 TypeScript 调用代码。

## 命令

```bash
rabetbase codegen sql --sqlcode 2305f915-dd48cd4c --format json
rabetbase codegen sql --sqlcode 2305f915-dd48cd4c --target bff --format json
rabetbase codegen sql --sqlcode 2305f915-dd48cd4c > ./src/api/getUserList.ts
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--sqlcode <code>` | string | 是 | — | SQL code 标识符（格式：`xxxxxxxx-xxxxxxxx`） |
| `--target <target>` | string | 否 | `sdk` | 生成目标：`sdk`（SDK 调用） / `bff`（BFF 脚本内调用） |
| `--no-imports` | boolean | 否 | — | 不包含 import 语句 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

生成的 TypeScript 代码直接打印到 stdout。`--target sdk` 生成前端 SDK 调用代码，`--target bff` 生成 BFF 脚本内调用代码。

## 提示

- `--target bff` 生成的代码使用 `context.client.sql.execute()`，注意 BFF 中 SQL 返回直接是数组
- `--target sdk` 生成的代码使用 `client.sql.execute()`，返回 `{ execSuccess, execResult }`

## 参考

- [SKILL.md](../SKILL.md)
