# GitHub 上传指南

本指南帮助你将 Office Automation Skill 上传到 GitHub。

---

## 📋 前置准备

### 1. 创建 GitHub 账号

如果没有 GitHub 账号，访问 https://github.com 注册。

### 2. 配置 Git（首次使用）

```bash
# 设置你的 Git 用户名和邮箱
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 设置 SSH 密钥（推荐）

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 将公钥复制到 GitHub: Settings → SSH and GPG keys → New SSH key
```

---

## 🚀 上传步骤

### 步骤 1：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `office-automation-skill`（或你喜欢的名字）
   - **Description**: `Office Automation Skill for OpenClaw - Automate Word and Excel processing`
   - **Visibility**: Public（公开）或 Private（私有）
   - **不要勾选** "Add a README file"（我们已经有 README 了）
   - **不要勾选** ".gitignore"（我们已经有 .gitignore 了）
   - **不要勾选** "Choose a license"（我们已经有 LICENSE 了）
3. 点击 "Create repository"

### 步骤 2：添加远程仓库

创建仓库后，GitHub 会显示设置说明。执行以下命令：

```bash
cd /Users/bbaa/.openclaw/workspace/skills/office-automation

# 使用 HTTPS（需要每次输入密码/token）
git remote add origin https://github.com/YOUR_USERNAME/office-automation-skill.git

# 或使用 SSH（推荐，需要先配置 SSH 密钥）
git remote add origin git@github.com:YOUR_USERNAME/office-automation-skill.git
```

**注意**：将 `YOUR_USERNAME` 替换为你的 GitHub 用户名。

### 步骤 3：推送到 GitHub

```bash
# 推送代码
git push -u origin main

# 如果是首次推送且使用 HTTPS，可能需要：
# - 使用 GitHub Personal Access Token 代替密码
# - 或在 GitHub 设置中启用密码登录
```

### 步骤 4：验证上传

访问你的 GitHub 仓库页面，确认所有文件已上传：
- README.md
- SKILL.md
- scripts/
- docs/
- examples/
- references/

---

## 🔐 使用 Personal Access Token

GitHub 已不再支持使用账户密码进行 Git 操作。需要使用 Personal Access Token：

### 创建 Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写：
   - **Note**: `office-automation-skill`
   - **Expiration**: 选择过期时间（建议 90 天或更长）
   - **Scopes**: 勾选 `repo`（完整仓库权限）
4. 点击 "Generate token"
5. **复制并保存 token**（只显示一次！）

### 使用 Token

推送时使用 token 代替密码：
```bash
git push -u origin main
# Username: YOUR_USERNAME
# Password: 粘贴你的 token（不会显示）
```

---

## 📦 发布到 ClawHub（可选）

如果你想让其他人通过 OpenClaw 安装这个技能：

### 1. 确保仓库是公开的

### 2. 提交到 ClawHub

访问 https://clawhub.com/submit 提交你的技能。

### 3. 用户安装

用户可以使用以下命令安装：
```bash
openclaw skills install github:YOUR_USERNAME/office-automation-skill
```

---

## 🔄 后续更新

### 修改代码后推送

```bash
cd /Users/bbaa/.openclaw/workspace/skills/office-automation

# 查看变更
git status

# 添加变更
git add -A

# 提交
git commit -m "feat: 添加新功能 / fix: 修复问题 / docs: 更新文档"

# 推送
git push
```

### 创建 Release

1. 访问 GitHub 仓库页面
2. 点击 "Releases" → "Create a new release"
3. 填写：
   - **Tag version**: `v1.0.0`
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**: 更新内容（可参考 CHANGELOG.md）
4. 点击 "Publish release"

---

## 🏷️ 添加主题标签

在 GitHub 仓库页面右侧，添加以下 topics：
- `openclaw`
- `office-automation`
- `word`
- `excel`
- `python`
- `automation`
- `skill`

---

## 📊 仓库徽章

在 README 中使用徽章展示项目状态：

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/office-automation-skill.svg)](https://github.com/YOUR_USERNAME/office-automation-skill/stargazers)
```

---

## ❓ 常见问题

### Q: 推送失败 "Permission denied"

**A**: 检查 SSH 密钥是否正确配置，或使用 HTTPS + Token。

### Q: 如何修改远程仓库地址？

**A**: 
```bash
git remote set-url origin https://github.com/NEW_USERNAME/NEW_REPO.git
```

### Q: 如何删除已提交的文件？

**A**:
```bash
git rm filename.txt
git commit -m "remove: 删除文件"
git push
```

### Q: 如何回滚到之前的版本？

**A**:
```bash
git log --oneline  # 查看提交历史
git reset --hard COMMIT_ID  # 回滚到指定提交
git push --force  # 强制推送（小心使用！）
```

---

## 📞 需要帮助？

- GitHub 文档：https://docs.github.com/
- Git 教程：https://git-scm.com/book/zh/v2
- OpenClaw 社区：https://discord.com/invite/clawd

---

**祝你上传顺利！** 🎉
