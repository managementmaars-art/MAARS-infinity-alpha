---
name: git-proxy
description: 解决 Git clone 失败时的代理设置问题
---

# git-proxy

当 git clone 连接 GitHub 失败时，自动设置代理并还原。

## When to use

当执行 `git clone` 时出现以下错误：
- `Failed to connect to github.com port 443`
- `Could not connect to server`
- 连接超时等网络错误

## Instructions

1. 设置 Git 代理（默认端口 10808）：
   ```powershell
   git config --global http.proxy http://127.0.0.1:10808
   git config --global https.proxy http://127.0.0.1:10808
   ```

2. 执行原本失败的 git clone 命令

3. 操作完成后立即还原代理设置：
   ```powershell
   git config --global --unset http.proxy
   git config --global --unset https.proxy
   ```

## Notes

- 用户常用代理端口是 `10808`
- 完成后务必还原，避免影响其他项目