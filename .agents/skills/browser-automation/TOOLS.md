# Browser Automation Skill Tools

## 概述

这个 skill 使用 Playwright 控制浏览器进行自动化操作。

**特点**：
- 默认复用现有页面，不打开新窗口
- Cookie 和登录状态持久化保存
- 支持所有常见浏览器操作

## 使用方法

调用方式: `cd C:/Users/admin/.openclaw/skills/browser-automation && node -e "const h=require('./index.js'); h.handleXXX({...}).then(console.log)"`

## 快速参考

### 页面操作

```
handleNavigate({url})           // 导航到 URL（复用现有页面）
handleNewPage({url})            // 打开新页面
handleScreenshot({selector?, fullPage?})  // 截图
handleGetContent({selector?})   // 获取页面 HTML
handleClose()                   // 关闭当前页面
```

### 交互操作

```
handleClick({selector})         // 点击
handleFill({selector, value})   // 填写（清空后填）
handleType({selector, text})    // 打字（追加）
handleSelect({selector, value}) // 下拉选择
handleCheck({selector, checked?}) // 勾选
```

### 等待和获取

```
handleWait({selector, timeout?})      // 等待元素
handleWaitForNavigation({timeout?})   // 等待跳转
handleGetText({selector})       // 获取文本
handleGetValue({selector})      // 获取表单值
handleGetAttribute({selector, attribute}) // 获取属性
```

### 高级操作

```
handleEvaluate({script})        // 执行 JS
handleUpload({selector, filePath}) // 上传文件
handlePress({key})              // 按键
handleHover({selector})         // 悬停
handleScroll({direction, amount?}) // 滚动
```

### 状态

```
handleStatus()                  // 查看状态
handleCloseBrowser()            // 关闭浏览器
handleHelp()                    // 帮助信息
```

## 选择器语法

- CSS: `#id`, `.class`, `tag`, `[attr="value"]`
- 文本: `text=登录`, `text=提交`
- 组合: `button:has-text("登录")`, `input:visible`
- XPath: `xpath=//button[@type="submit"]`

## 常见场景

### 1. 登录网站

```javascript
// 打开登录页
handleNavigate({url: 'https://example.com/login'})

// 填写表单
handleFill({selector: '#username', value: 'user@example.com'})
handleFill({selector: '#password', value: 'mypassword'})

// 点击登录
handleClick({selector: 'button[type="submit"]'})

// 等待跳转
handleWaitForNavigation()
```

### 2. 填写表单

```javascript
// 填写文本
handleFill({selector: '#name', value: '张三'})

// 选择下拉
handleSelect({selector: '#country', value: 'china'})

// 勾选复选框
handleCheck({selector: '#agree'})

// 上传文件
handleUpload({selector: 'input[type="file"]', filePath: 'C:/file.pdf'})
```

### 3. 获取页面信息

```javascript
// 获取文本
handleGetText({selector: '.price'})

// 获取链接
handleGetAttribute({selector: 'a.download', attribute: 'href'})

// 截图
handleScreenshot({})
```

## 注意事项

1. **浏览器会保持运行**：直到调用 `closeBrowser()` 或程序结束
2. **登录状态会保存**：存储在 `~/.openclaw/browser-data/`
3. **默认复用页面**：`navigate` 会在当前页面跳转，不会开新窗口
4. **如需新窗口**：使用 `newPage` 而不是 `navigate`
