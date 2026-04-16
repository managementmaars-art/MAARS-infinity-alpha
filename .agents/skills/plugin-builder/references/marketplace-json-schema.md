# marketplace.json 字段参考

## 顶层字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 是 | Marketplace 名称 |
| `owner` | object | 是 | 所有者信息 |
| `metadata` | object | 否 | 元数据 |
| `plugins` | array | 是 | 插件列表 |

## owner 对象

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 所有者名称 |
| `email` | string | 否 | 邮箱 |

## metadata 对象

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `description` | string | 否 | Marketplace 描述 |
| `website` | string | 否 | 网站 URL |
| `icon` | string | 否 | 图标 URL |

## plugins 数组项

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 插件名称 |
| `source` | string | 是 | 插件目录路径（相对于仓库根目录） |
| `description` | string | 否 | 插件描述 |
| `author` | object | 否 | 作者信息 |
| `homepage` | string | 否 | 主页 URL |
| `repository` | string | 否 | 仓库 URL |
| `license` | string | 否 | 许可证 |
| `keywords` | array | 否 | 关键词 |
| `category` | string | 否 | 分类 |

## 完整示例

```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "Your Name",
    "email": "your.email@example.com"
  },
  "metadata": {
    "description": "我的私有插件市场",
    "website": "https://example.com",
    "icon": "https://example.com/icon.png"
  },
  "plugins": [
    {
      "name": "my-plugins",
      "source": "./",
      "description": "插件集合描述",
      "author": {
        "name": "Your Name"
      },
      "homepage": "https://github.com/username/my-claude-plugins",
      "repository": "https://github.com/username/my-claude-plugins.git",
      "license": "MIT",
      "keywords": ["claude-code", "plugins", "productivity"],
      "category": "utilities"
    }
  ]
}
```

## 多插件示例

一个 marketplace 可以包含多个插件：

```json
{
  "name": "company-plugins",
  "owner": {
    "name": "Company Name"
  },
  "metadata": {
    "description": "公司内部插件市场"
  },
  "plugins": [
    {
      "name": "dev-tools",
      "source": "./packages/dev-tools",
      "description": "开发工具集"
    },
    {
      "name": "docs-helpers",
      "source": "./packages/docs-helpers",
      "description": "文档辅助工具"
    },
    {
      "name": "team-templates",
      "source": "./packages/team-templates",
      "description": "团队模板"
    }
  ]
}
```

## source 字段说明

`source` 字段指定插件目录相对于仓库根目录的路径：

- `"./"` - 仓库根目录即为插件
- `"./packages/my-plugin"` - 子目录中的插件
- `"./plugins/dev-tools"` - plugins 目录下的插件

## 常见分类

| 分类 | 说明 |
|------|------|
| `utilities` | 实用工具 |
| `development` | 开发工具 |
| `documentation` | 文档相关 |
| `automation` | 自动化工具 |
| `integrations` | 第三方集成 |
| `templates` | 模板 |
| `productivity` | 生产力工具 |
