# rabetbase app add

添加一个新应用到配置文件。默认写入**项目** `process.cwd()` 下解析到的配置文件（一般为 `.rabetbase.json`）；加 **`--global`** 则只写 `~/.rabetbase.json`。若是第一个应用，自动设为 `defaultApp`。其余 CLI 配置仍兼容读取 `.lovrabet.json`。

应用名 **`<name>` 为位置参数**，与 `app use` / `app remove` 一致。

## 命令

```bash
rabetbase app add <name> --appcode <code> [--env <env>] [--apiDir <dir>] [--global] [--cookie ...] [--riskLevel ...]
```

## 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `<name>` | string | **必填（位置参数）** — 应用名（自定义标识，如 `order`、`product`） |
| `--appcode` | string | **必填** — 应用的 App Code |
| `--global` | boolean | 写入全局配置而非项目配置 |
| `--env` | string | 目标环境（`daily` / `production`） |
| `--apiDir` | string | API 目录路径 |
| `--cookie` | string | 该应用专用 Cookie |
| `--accessKey` | string | 该应用专用 Access Key |
| `--defaultFormat` | string | 写入该 app profile 的默认输出格式（与命令行 `--format` 不同） |
| `--pageSize` | number | 分页条数 |
| `--riskLevel` | string | 风险等级 |
| `--locale` | string | 地区设置 |

> 除 `<name>` 与 `--appcode` 必填外，其余均可选。未指定的字段将继承顶层共享值。

## 输出

确认消息，显示添加/更新的应用名和 appcode。

## 提示

- 若应用名已存在，执行更新操作
- 第一个添加的应用自动成为 `defaultApp`
- 添加后可通过 `rabetbase app list` 查看所有应用
- 典型的多应用初始化流程：

```bash
rabetbase app add order --appcode app-order-xxx --env production --apiDir ./apps/order/src/api
rabetbase app add product --appcode app-product-yyy --env daily --apiDir ./apps/product/src/api
rabetbase app use order
```

## 参考

- [SKILL.md](../SKILL.md) — 总索引
- [rabetbase app list](rabetbase-app-list.md) — 查看所有应用
- [rabetbase app use](rabetbase-app-use.md) — 切换默认应用
- [rabetbase app remove](rabetbase-app-remove.md) — 移除应用
