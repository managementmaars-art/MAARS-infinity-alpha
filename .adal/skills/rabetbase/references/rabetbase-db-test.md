# db test

用平台已保存的凭据**测试**到数据库的网络与登录是否成功。只读（`read`）。

## 何时用

- 改白名单、换 VPC、更新密码后快速验证
- 新建连接后确认无误再跑长耗时分析

## 命令

```bash
rabetbase db test --id 10157 --format compress
```

## 参数

| Flag | 必填 | 说明 |
|------|------|------|
| `--id` | **是** | dblink id |

## 输出

`data.connected` 为布尔语义；`data.result` 为后端响应的**摘要**（白名单字段或键名列表），不返回完整原始 body，避免泄露敏感细节。

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
