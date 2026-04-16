---
name: renaissance-md-html
description: 将 Markdown 转为带「文艺复兴」排版的完整 HTML 文档字符串（与 WeChatMarkdownRenderer 的 themes.ts 中 renaissance 主题一致）。用户提到 md 转 html、Markdown 排版、文艺复兴风格、古典/棕金配色、两端对齐长文、公众号式 HTML、导出静态 HTML、或需要脚本生成样式化 HTML 时，必须使用本 skill；不要手写大段 HTML 替代脚本。
---

# Renaissance Markdown → HTML

## 目标

- **输入**：UTF-8 Markdown 字符串（或 `.md` 文件路径）。
- **输出**：**完整 HTML 文档**字符串（含 `<!DOCTYPE html>`、内联 CSS），正文包在 `<article class="wmr-renaissance">` 内。
- **样式来源**：本 skill 内 `assets/renaissance.css`，与仓库 `src/themes.ts` 的 `renaissanceStyles` 对齐。
- **默认增强**：自动将 Markdown 图片转为 base64 data URI，并在页面右上角注入“一键复制全文（富文本）”按钮。

## 必须执行的命令

在 skill 目录下执行（将 `<SKILL_DIR>` 换为本 skill 根路径，即含 `SKILL.md` 的目录）：

```bash
cd <SKILL_DIR>
# 若首次使用：
npm install
```

**从标准输入传入 Markdown：**

```bash
printf '%s' "$MARKDOWN_STRING" | node scripts/md_to_renaissance_html.mjs --title "页面标题"
```

**从文件读取：**

```bash
node scripts/md_to_renaissance_html.mjs --input /path/to/article.md --title "页面标题"
```

脚本向 **stdout** 打印最终 HTML；将输出保存到变量或文件交给用户即可。

## 参数

| 参数 | 说明 |
| ------ | ------ |
| `--input <path>` | 读取 Markdown 文件（与 stdin 二选一；若同时存在，以 `--input` 为准） |
| `--title <text>` | `<title>` 与浏览器标签页标题，默认 `Document` |
| `--no-embed-images` | 关闭图片 base64 内嵌（默认开启） |
| `--no-copy-button` | 关闭“一键复制全文（富文本）”按钮（默认开启） |

## Agent 注意事项

1. **始终通过脚本生成 HTML**，不要凭记忆拼接样式；CSS 以 `assets/renaissance.css` 为准。
2. 若工作区即本仓库，skill 路径一般为：`.cursor/skills/renaissance-md-html/`（相对仓库根目录）。
3. 若 `node_modules` 不存在，先在该目录执行 `npm install`。
4. 用户只要「片段」时，仍可先跑脚本得到完整文档，再按需截取 `<article>...</article>` 或仅内部 HTML（需说明截取后无全局 `<style>` 时需保留内联或外链 CSS）。
5. 默认输出为“图片已内嵌 + 复制按钮已注入”；如果用户明确不要，则追加 `--no-embed-images` 或 `--no-copy-button`。

## 依赖

- Node.js 18+
- `marked`（见 `package.json`，用于 GFM：表格、删除线等）
