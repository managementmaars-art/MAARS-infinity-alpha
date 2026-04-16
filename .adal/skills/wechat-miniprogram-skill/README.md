# 🚀 WeChat Mini Program AI Skill (Native JS)

[![NPM Version](https://img.shields.io/npm/v/wechat-miniprogram-skill.svg)](https://www.npmjs.com/package/wechat-miniprogram-skill)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**让 AI 像谷歌工程师一样为你编写微信小程序代码。**

这是一个专门为 AI 编程助手（如 **Cursor**, **Antigravity**, **OpenCode** 等）设计的标准化 Skill（规则集）。它通过注入高质量的工程约束，确保 AI 生成符合微信小程序官方规范、高性能且无 Bug 的 **原生 JavaScript** 代码。

---

## 🌟 为什么需要这个 Skill？

微信小程序采用独特的**双线程架构**，通用的 Web 开发 Prompt 往往会导致 AI 生成以下有问题的代码：
* ❌ **性能瓶颈**：频繁或全量调用 `setData` 导致界面卡顿。
* ❌ **兼容性坑**：例如 iOS 系统下 `new Date()` 不支持横杠 `-` 格式。
* ❌ **布局失准**：错误地使用 `px` 而非 `rpx` 导致多端适配失败。
* ❌ **语法混淆**：AI 可能会混入 Vue、React 或 TypeScript 的语法。

本 Skill 通过在 AI 的上下文里预设 Google 级别的工程标准，从源头解决这些问题。

---

## 📦 安装说明

你可以使用 `add-skill` 工具一键将这些规则安装到你的项目中：

```bash
npx add-skill https://github.com/Gourdbaby/wechat-miniprogram-skill