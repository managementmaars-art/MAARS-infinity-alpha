# GitLab 仓库集成指南

## 配置 GitLab 访问

### 公开仓库

无需额外配置，直接使用仓库路径：

```bash
/plugin marketplace add my-group/my-plugins --source gitlab
```

### 私有仓库

#### 1. 创建访问令牌

1. 登录 GitLab
2. 进入 **Settings** → **Access Tokens**
3. 创建新的个人访问令牌
4. 勾选 `read_api` 和 `read_repository` 权限
5. 复制生成的令牌

#### 2. 配置凭据

在 `~/.claude/settings.json` 中添加：

```json
{
  "gitlabTokens": {
    "gitlab.com": "your-access-token",
    "gitlab.company.com": "your-self-hosted-token"
  }
}
```

### 自托管 GitLab

#### 配置实例

在 settings.json 中指定自托管实例：

```json
{
  "gitlabInstances": {
    "company": "https://gitlab.company.com",
    "internal": "https://git.internal.com"
  },
  "gitlabTokens": {
    "gitlab.company.com": "company-token",
    "git.internal.com": "internal-token"
  }
}
```

#### 使用实例

```bash
# 使用完整 URL
/plugin marketplace add https://gitlab.company.com/my-group/my-plugins

# 或使用配置的实例名
/plugin marketplace add my-group/my-plugins --instance company
```

## URL 格式

支持以下格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| 命名空间/项目 | `my-group/my-plugins` | 默认 gitlab.com |
| 完整 HTTPS URL | `https://gitlab.com/my-group/my-plugins` | 明确指定 |
| SSH URL | `git@gitlab.com:my-group/my-plugins.git` | SSH 访问 |

## 与 GitHub 的差异

| 特性 | GitHub | GitLab |
|------|--------|--------|
| 路径格式 | `owner/repo` | `namespace/project` |
| 组织/群组 | `org/repo` | `group/project` |
| 子组支持 | 无 | `group/subgroup/project` |

## GitLab CI/CD 自动发布

### .gitlab-ci.yml 示例

```yaml
stages:
  - validate
  - release

validate:
  stage: validate
  image: python:3.11
  script:
    - pip install jsonschema
    - python scripts/validate_plugin.py
  only:
    - merge_requests
    - main

release:
  stage: release
  image: alpine:latest
  script:
    - echo "Release triggered by tag $CI_COMMIT_TAG"
  only:
    - tags
```

## 注意事项

1. **命名空间格式**
   - GitLab 使用 `namespace/project` 格式
   - 支持嵌套子组：`group/subgroup/project`
   - 与 GitHub 的 `owner/repo` 不同

2. **私有项目**
   - 必须配置访问令牌
   - 令牌需要 `read_api` 和 `read_repository` 权限
   - 建议使用项目访问令牌而非个人令牌

3. **自托管实例**
   - 需要在 settings.json 中配置实例 URL
   - 需要为每个实例配置相应的令牌
   - 确保 Claude Code 可以访问该实例

4. **发布标签**
   - 使用语义化版本标签（如 v1.0.0）
   - 在 GitLab 中创建 Release 以便于追踪
   - 可配置 CI/CD 自动发布

## 完整配置示例

### ~/.claude/settings.json

```json
{
  "gitlabInstances": {
    "gitlab": "https://gitlab.com",
    "company": "https://gitlab.company.com"
  },
  "gitlabTokens": {
    "gitlab.com": "glpat-xxxxxxxxxxxxxxxxxxxx",
    "gitlab.company.com": "glpat-yyyyyyyyyyyyyyyyyyyy"
  }
}
```

### 添加和安装

```bash
# 添加 GitLab marketplace
/plugin marketplace add my-group/my-plugins --source gitlab

# 添加自托管 marketplace
/plugin marketplace add https://gitlab.company.com/my-group/my-plugins

# 安装插件
/plugin install my-skill@my-plugins

# 更新插件
/plugin update my-skill@my-plugins
```

## 故障排除

### 认证失败
```
错误：无法访问私有仓库
解决：检查 gitlabTokens 配置，确保令牌有效
```

### 找不到仓库
```
错误：仓库不存在或无权访问
解决：检查命名空间/项目名称是否正确
```

### 配置文件错误
```
错误：无法解析 settings.json
解决：验证 JSON 格式，检查逗号和括号
```
