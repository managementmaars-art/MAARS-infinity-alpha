# Hotlist HTTP API (Supabase REST)

本文档用于给第三方调用 `hotlist_catalogs` 表。

## 1. 基础信息

- Base URL: `https://<PROJECT_REF>.supabase.co`
- REST Endpoint: `/rest/v1/hotlist_catalogs`
- 数据表: `hotlist_catalogs`
- 字段:
  - `platform_name` (text, required)
  - `rank` (int4, required)
  - `catalog_name` (text, required)
  - `catalog_type` (text)
  - `release_date` (date)
  - `collected_date` (date, required)
  - `created_at` (timestamptz, server default)
- 唯一约束: `(platform_name, collected_date, rank)`

## 2. 鉴权

每个请求都需要以下请求头:

- `apikey: <SUPABASE_ANON_KEY or SERVICE_ROLE_KEY>`
- `Authorization: Bearer <same key>`
- `Content-Type: application/json` (GET 可省略)

注意:

- 对外部调用方不建议暴露 `service_role_key`。
- 推荐通过你自己的后端/Edge Function 转发请求，由服务端持有密钥。

## 3. 查询 API

### 3.1 查询某平台最近 N 天

Supabase REST 不直接支持 `last_days` 参数，调用方请先计算日期区间。

示例: 今天为 `2026-02-28`，最近 7 天起始日为 `2026-02-22`。

```bash
curl -G "https://<PROJECT_REF>.supabase.co/rest/v1/hotlist_catalogs" \
  -H "apikey: <KEY>" \
  -H "Authorization: Bearer <KEY>" \
  --data-urlencode "select=platform_name,rank,catalog_name,catalog_type,release_date,collected_date,created_at" \
  --data-urlencode "platform_name=eq.腾讯视频" \
  --data-urlencode "collected_date=gte.2026-02-22" \
  --data-urlencode "collected_date=lte.2026-02-28" \
  --data-urlencode "order=collected_date.desc,rank.asc" \
  --data-urlencode "limit=200"
```

### 3.2 按平台 + 日期区间查询

```bash
curl -G "https://<PROJECT_REF>.supabase.co/rest/v1/hotlist_catalogs" \
  -H "apikey: <KEY>" \
  -H "Authorization: Bearer <KEY>" \
  --data-urlencode "select=*" \
  --data-urlencode "platform_name=eq.爱奇艺" \
  --data-urlencode "collected_date=gte.2026-02-01" \
  --data-urlencode "collected_date=lte.2026-02-28" \
  --data-urlencode "order=collected_date.desc,rank.asc" \
  --data-urlencode "limit=100"
```

### 3.3 常用过滤语法

- 精确匹配: `platform_name=eq.腾讯视频`
- 大于等于: `collected_date=gte.2026-02-22`
- 小于等于: `collected_date=lte.2026-02-28`
- 排序: `order=collected_date.desc,rank.asc`
- 限制条数: `limit=200`

## 4. Upsert API（写入/更新）

使用 `on_conflict=platform_name,collected_date,rank` 与 `Prefer: resolution=merge-duplicates`，可确保同平台同日期同名次不会重复插入。

```bash
curl -X POST "https://<PROJECT_REF>.supabase.co/rest/v1/hotlist_catalogs?on_conflict=platform_name,collected_date,rank" \
  -H "apikey: <KEY>" \
  -H "Authorization: Bearer <KEY>" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates,return=representation" \
  -d '[
    {
      "platform_name": "腾讯视频",
      "rank": 1,
      "catalog_name": "太平年",
      "catalog_type": "电视剧",
      "release_date": "2026-01-01",
      "collected_date": "2026-02-28"
    }
  ]'
```

## 5. 响应示例

### 5.1 查询成功（200）

```json
[
  {
    "id": 101,
    "platform_name": "腾讯视频",
    "rank": 1,
    "catalog_name": "太平年",
    "catalog_type": "电视剧",
    "release_date": "2026-01-01",
    "collected_date": "2026-02-28",
    "created_at": "2026-02-28T09:31:02.112345+00:00"
  }
]
```

### 5.2 Upsert 成功（201/200）

返回写入后的记录（取决于 `Prefer` 设置）。

## 6. 常见错误

- `401 Unauthorized`:
  - `apikey` 或 `Authorization` 缺失/错误。
- `403 Forbidden`:
  - RLS 策略限制。
- `409 Conflict`:
  - 唯一约束冲突且未使用 merge upsert。
- `400 Bad Request`:
  - 日期格式错误（应为 `YYYY-MM-DD`）或字段类型不匹配。

## 7. 调用建议

- 查询统一按 `collected_date + rank` 排序，结果更稳定。
- 对接方建议固定使用 `select` 白名单字段，避免 schema 变更影响。
- 生产环境建议在服务端做参数校验（`platform_name`、日期格式、`limit` 上限）。
