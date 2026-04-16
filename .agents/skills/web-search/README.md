# Web Search Skill

一个功能强大的网络搜索技能，支持多种搜索引擎，无需 API 密钥。

## ✨ 功能特性

- 🔍 **多引擎支持**：百度（Playwright）、必应、DuckDuckGo
- 🌐 **无需 API Key**：使用浏览器自动化和网页抓取
- 🔄 **智能降级**：一个引擎失败时自动切换其他引擎
- 📊 **结构化结果**：返回清晰的搜索结果（标题、URL、摘要）
- 🚀 **高性能**：异步支持，Playwright 浏览器自动化

## 📦 安装

### 依赖安装

```bash
pip install -r requirements.txt
```

### Playwright 浏览器安装（首次使用）

```bash
playwright install chromium
```

> 注意：首次安装会下载 Chromium 浏览器（约 100MB）

## 🚀 快速开始

### 基本搜索

```python
from web_search import main

# 执行搜索
result = main({
    "action": "search",
    "query": "Python 教程",
    "num_results": 5
})

print(f"搜索引擎: {result['engine']}")
for r in result['results']:
    print(f"- {r['title']}: {r['href']}")
```

### 深度搜索

```python
# 深度搜索并抓取详情
result = main({
    "action": "deep_search",
    "query": "machine learning latest research",
    "num_results": 5
})

# 查看详细内容
if result.get('detailed_info'):
    print(result['detailed_info']['extracted_content'])
```

### 网页抓取

```python
# 抓取特定网页
result = main({
    "action": "crawl",
    "url": "https://example.com"
})

if result['success']:
    print(result['markdown'])
```

## 📋 输入参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| action | string | 是 | 操作类型：`search`、`deep_search`、`crawl` |
| query | string | 条件 | 搜索关键词（search/deep_search 必需） |
| url | string | 条件 | 目标 URL（crawl 必需） |
| num_results | int | 否 | 返回结果数量，默认 5，最大 20 |
| region | string | 否 | 地区代码，默认 `cn-zh` |

## 📤 输出格式

### 搜索结果

```json
{
    "success": true,
    "query": "搜索关键词",
    "engine": "baidu+playwright",
    "num_results": 5,
    "results": [
        {
            "title": "结果标题",
            "href": "https://...",
            "body": "摘要内容"
        }
    ],
    "message": "搜索完成"
}
```

### 深度搜索结果

```json
{
    "success": true,
    "query": "搜索关键词",
    "search_results": [...],
    "detailed_info": {
        "extracted_content": "抓取的详细内容..."
    },
    "message": "深度搜索完成"
}
```

## 🔍 搜索策略

技能按以下优先级自动选择搜索引擎：

1. **baidusearch 库** - 最快，无需浏览器
2. **Playwright + 百度** - 最可靠，绕过反爬虫
3. **DuckDuckGo** - 隐私保护
4. **必应** - 国际搜索

## 💡 使用场景

- 📰 **新闻资讯获取**：搜索最新新闻报道
- 📚 **知识查询**：获取技术文档、教程
- 🌐 **信息收集**：网络信息搜集
- 🔍 **研究调研**：学术研究、市场调研

## ⚠️ 注意事项

1. **首次运行**：Playwright 会自动下载 Chromium 浏览器（约 100MB）
2. **搜索频率**：建议合理控制频率，避免被搜索引擎临时限制
3. **网络要求**：需要稳定的互联网连接
4. **结果差异**：搜索结果可能因搜索引擎算法和地理位置而异

## 🔧 故障排除

### 问题：Playwright 浏览器下载失败

**解决**：手动安装浏览器
```bash
playwright install chromium
```

### 问题：搜索结果为空

**可能原因**：
- 网络连接问题
- 搜索引擎反爬虫机制
- 查询词过于特殊

**解决**：技能会自动尝试其他搜索引擎，无需手动干预

### 问题：网页抓取失败

**可能原因**：
- 网站反爬虫机制
- 网站需要登录
- 网站结构复杂

**解决**：尝试使用其他 URL 或简化需求

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE.txt)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 更新日志

### v1.1.0 (2025-03-01)
- ✅ 集成 Playwright 浏览器自动化
- ✅ 支持深度搜索模式
- ✅ 多引擎智能降级策略

### v1.0.0 (2025-03-01)
- 🎉 初始版本发布
- ✅ 支持必应搜索引擎
- ✅ 支持百度搜索引擎
