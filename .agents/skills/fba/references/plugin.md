# Plugin Development Standards

## Plugin Types

### App-level

Injected into the system like an application, with a complete route structure

```toml
[app]
router = ['v1']
```

### Extend-level

Injected into an existing application under the app directory, must replicate the target application's api directory
structure 1:1

```toml
[app]
extend = 'admin'
```

## plugin.toml Configuration

### App-level

```toml
# 插件信息
[plugin]
# 图标（插件仓库内的图标路径或图标链接地址）
icon = 'assets/icon.svg'
# 摘要（简短描述）
summary = ''
# 版本号
version = ''
# 描述
description = ''
# 作者
author = ''
# 标签
# 当前支持：ai、mcp、agent、auth、storage、notification、task、payment、other
tags = ['']
# 数据库支持
# 当前支持：mysql、postgresql
database = ['']

# 应用配置
[app]
# 路由器最终实例
# 可参考源码：backend/app/admin/api/router.py，通常默认命名为 v1
router = ['v1']

# 代码中的配置项（全大写）
# 该配置项为可选
[settings]
MY_PLUGIN_CONFIG = 'value'
```

### Extend-level

```toml
# 插件信息
[plugin]
# 图标（插件仓库内的图标路径或图标链接地址）
icon = 'assets/icon.svg'
# 摘要（简短描述）
summary = ''
# 版本号
version = ''
# 描述
description = ''
# 作者
author = ''
# 标签
# 当前支持：ai、mcp、agent、auth、storage、notification、task、payment、other
tags = ['']
# 数据库支持
# 当前支持：mysql、postgresql
database = ['']

# 应用配置
[app]
# 扩展的哪个应用
extend = '应用文件夹名称'

# 接口配置
[api.xxx]
# xxx 对应的是插件 api 目录下接口文件的文件名（不包含后缀）
# 例如接口文件名为 notice.py，则 xxx 应该为 notice
# 如果包含多个接口文件，则应存在多个接口配置
# 路由前缀，必须以 '/' 开头
prefix = ''
# 标签，用于 Swagger 文档
tags = ''

# 代码中的配置项（全大写）
# 该配置项为可选，详情请查看：Hot-pluggable Configuration
[settings]
MY_PLUGIN_CONFIG = 'value'
```

## Plugin Directory Structure

```
xxx                             # Plugin name (required)
├── api                         # API (required)
├── crud                        # CRUD
├── model                       # Models
│   └── __init__.py             # Import all model classes in this file (required if directory exists)
├── schema                      # Data transfer
├── service                     # Services
├── sql                         # Recommended if the plugin needs to execute SQL
│   ├── mysql
│   │   ├── init.sql            # Auto-increment ID mode
│   │   └── init_snowflake.sql  # Snowflake ID mode
│   └── postgresql
│       ├── init.sql            # Auto-increment ID mode
│       └── init_snowflake.sql  # Snowflake ID mode
├── utils                       # Utilities
├── .env.example                # Environment variables
├── __init__.py                 # Kept as a Python package (required)
├── ...                         # More content, e.g. enums.py...
├── plugin.toml                 # Configuration file (required)
├── README.md                   # Usage instructions and your contact info (required)
└── requirements.txt            # Dependency packages file
```

## Hot-pluggable Configuration

**Plugin Environment Variables**

Add `.env.example` in the plugin root directory:

```env
# [ Plugin ] my_plugin
MY_PLUGIN_USERNAME: str
MY_PLUGIN_PASSWORD: str
```

**Plugin Basic Configuration**

Add in the `[settings]` section of `plugin.toml`:

```toml
[settings]
MY_PLUGIN_HOST = 'localhost'
MY_PLUGIN_PORT = 8080
MY_PLUGIN_ENABLED = true
```

**Global Configuration (Optional)**

For IDE type hints, add in `backend/core/conf.py`:

```python
##################################################
# [ Plugin ] my_plugin
##################################################
# .env
MY_PLUGIN_USERNAME: str
MY_PLUGIN_PASSWORD: str

# 基础配置
MY_PLUGIN_HOST: str
MY_PLUGIN_PORT: int
MY_PLUGIN_ENABLED: bool
```

## Important Notes

> ⚠️ **Warning**: Unless necessary, try not to reference existing methods from the architecture in plugin code. If
> existing methods in the architecture change, the plugin must be updated accordingly, otherwise the plugin will be
> broken.
