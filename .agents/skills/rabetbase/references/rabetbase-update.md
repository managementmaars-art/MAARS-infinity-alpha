# update

检查并更新 CLI 到最新版本。

## 命令

```bash
# 检查并更新
rabetbase update

# 查看帮助
rabetbase update --help
```

## 行为

1. 显示当前版本
2. 从 npm registry 检查最新稳定版
3. 比较版本（自动跳过 pre-release）
4. 如有新版本，自动执行安装命令（npm 或 bun，依据安装时使用的包管理器）
5. 完成后提示重启终端

## 升级渠道

默认从 npm registry 安装的包更新。如使用 `bun install -g @lovrabet/rabetbase-cli` 安装，命令会自动检测并使用 `bun` 升级。

## 风险等级

`high-risk-write` — 执行全局包安装命令。

## 前置条件

- 全局安装（`npm install -g` 或 `bun install -g`）
- 网络连接 npmjs.org

## 示例

```bash
$ rabetbase update
Current version: 2.0.2+65
⠋ Checking for updates...
ℹ Update available: 2.0.2+65 → 2.1.0
⠋ Updating via npm...
✔ Updated to v2.1.0
  Restart your terminal to use the new version.
```

## 手动升级

如命令失败，可手动执行：

```bash
npm install -g @lovrabet/rabetbase-cli@latest
# 或
bun install -g @lovrabet/rabetbase-cli@latest
```
