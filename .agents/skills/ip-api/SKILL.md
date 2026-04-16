---
name: ip-api
description: 查询公网IP地址的地理位置信息，包括国家、省份、城市、ISP、时区等
---

# ip-api

```
ip-api/
├── SKILL.md       # Skill说明文档
├── ip-query.js    # 查询本机公网IP
└── proxy-query.js # 通过HTTP代理查询出口IP
```

使用 ip-api.com 免费API查询公网IP地址的地理位置信息。

## When to use

当用户需要查询当前设备的公网IP及其地理位置信息时使用此skill。

## Instructions

1. 调用 `http://ip-api.com/json/?lang=zh-CN` 获取IP信息
2. 解析返回的JSON数据，包含以下字段：
   - `query` - IP地址
   - `country` / `countryCode` - 国家及代码
   - `regionName` - 省份/州
   - `city` - 城市
   - `isp` - ISP服务商
   - `timezone` - 时区
3. 将结果以友好格式展示给用户

## 注意事项

- 免费版有频率限制：每分钟45次请求
- 使用HTTP协议（非HTTPS）
- 仅返回公网IP信息，无法查询内网IP
- v2ray 的 mixed 端口同时支持 HTTP 代理和 SOCKS5 代理

## 示例代码

项目已提供两个 Node.js 脚本，使用内置 `http` 模块：

```bash
# 查询本机公网IP
node ip-api/ip-query.js

# 通过HTTP代理查询出口IP（默认端口10808）
node ip-api/proxy-query.js

# 指定代理端口
node ip-api/proxy-query.js 1080
```