---
name: bing-search
description: 使用 Bing 搜索引擎进行网页搜索并返回详细结果。当用户说「搜索XXX」「搜一下」「bing搜索」「web search」等时触发。使用 Playwright MCP 插件执行搜索并获取包含标题、链接、摘要、来源站点、日期等完整信息。
---

# Bing 搜索 Skill

当用户需要搜索互联网信息时，使用本 skill 执行 Bing 搜索。

## 触发条件

- 用户说「搜索 XXX」
- 用户说「搜一下 XXX」
- 用户说「bing 搜索 XXX」
- 用户说「web search XXX」
- 用户意图需要获取互联网最新信息

## 工具依赖

必须使用 Playwright MCP 插件 (`mcp__plugin_playwright_playwright__*`)。

## 操作步骤

### 步骤 1: 打开 Bing

使用 `browser_navigate` 打开 Bing 首页：

```
URL: https://www.bing.com
```

### 步骤 2: 输入搜索关键词

使用 `browser_type` 工具：

```
ref: 搜索框的 ref (从 snapshot 获取)
text: [关键词]
submit: true
```

### 步骤 3: 提取搜索结果

使用 `browser_evaluate` 执行提取脚本 `scripts/extract-results.js`：

```javascript
extractBingResults(10);
```

该脚本会提取以下字段：
- **title**: 标题
- **url**: 真实链接（自动去除 Bing 重定向）
- **description**: 内容摘要
- **site**: 来源站点
- **citeFull**: 完整引用信息
- **date**: 发布日期

### 步骤 4: 返回结果

将搜索结果以带详情的格式返回给用户：

```markdown
## 搜索结果: [关键词]

### 1. [标题1](URL)
- **来源**: 站点名
- **日期**: 日期信息
- 摘要内容...

...
```

## 翻页功能（默认跳到第2页）

### 推荐方式：URL 直接跳转

使用 `browser_navigate` 直接跳转到指定页：

```javascript
// 获取第 N 页的 URL
// first 参数: (页码-1) * 10 + 1
const getPageUrl = (keyword, page) => {
  const first = (page - 1) * 10 + 1;
  return `https://www.bing.com/search?q=${encodeURIComponent(keyword)}&first=${first}`;
};

// 示例
getPageUrl('关键词', 2)
// 返回: https://www.bing.com/search?q=关键词&first=11
```

**URL 参数规律：**
| 页码 | first 值 |
|------|----------|
| 1 | 1 |
| 2 | 11 |
| 3 | 21 |
| N | (N-1)×10+1 |

### 备选方式：点击翻页

如果需要点击翻页按钮，使用：

```javascript
// 查找并点击"下一页"链接
const nextLink = document.querySelector('a[href*="first="]') ||
  document.querySelector('[aria-label="下一页"]') ||
  document.querySelector('.sb_pagN');
if (nextLink) nextLink.click();
```

### 获取当前页信息

```javascript
// 从URL解析当前页码
const getCurrentPage = () => {
  const match = window.location.href.match(/[?&]first=(\d+)/);
  return match ? Math.floor(parseInt(match[1]) / 10) + 1 : 1;
};

// 获取当前搜索关键词
const getSearchKeyword = () => {
  const match = window.location.href.match(/[?&]q=([^&]+)/);
  return match ? decodeURIComponent(match[1]) : '';
};
```

## 脚本文件

| 文件 | 用途 |
|------|------|
| `scripts/extract-results.js` | 提取搜索结果核心脚本 |

### extract-results.js 函数

| 函数 | 用途 |
|------|------|
| `extractBingResults(maxResults)` | 提取搜索结果 |
| `getPageUrl(keyword, page)` | 获取指定页URL |
| `getCurrentPage()` | 获取当前页码 |
| `getSearchKeyword()` | 获取当前搜索词 |

## 完整示例

**用户输入**: 「搜索 Claude Code 并翻到第 2 页」

**执行流程**:
1. `browser_navigate` → https://www.bing.com
2. `browser_type` → 输入关键词，回车搜索
3. `browser_evaluate` → `extractBingResults(10)` 获取第1页结果
4. `browser_navigate` → https://www.bing.com/search?q=关键词&first=11 跳到第2页
5. `browser_evaluate` → `extractBingResults(10)` 获取第2页结果
6. 合并返回给用户
