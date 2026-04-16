---
name: "backend-api-doc-generator"
description: "Analyzes Node.js backend projects (Express / Nest.js, JS + TS), automatically identifies ALL APIs, routes, controllers, data models, generates COMPLETE documentation IN ONE TIME. No omission, no truncation. Output: backend-api-doc.md"
---

# Backend API Doc Generator (Node.js Only)
- This skill **ONLY analyzes Node.js server-side frameworks**: Express.js, Nest.js.
- It supports both **JavaScript (JS)** and **TypeScript (TS)** projects.
- It scans ALL API routes, controllers, models, modules, then generates full, standardized backend design documentation **in ONE single generation**.

## Core Rules (MUST FOLLOW 100%)
1. **FULL SCAN**: Scan ALL .js and .ts files, controllers, routes, services, modules — NO omission
2. **AUTO EXCLUDE**: node_modules, dist, build, coverage, .git, logs, temp, vendor
3. **NO TRUNCATION**: No blanks, no ellipsis, no incomplete diagrams, no "to be filled"
4. **ONE-TIME GENERATION**: Output FULL document in ONE response — NO secondary prompts
5. **ALL CONTENT**: All APIs, modules, data models, sequence diagrams MUST be fully generated

## When to Use
For **Node.js backend projects only**:
- Express.js (JS / TS)
- Nest.js (JS / TS)
- Node.js API servers
- Generate full API docs, data models, ER diagrams, sequence diagrams

## How It Works
1. **Full Project Scan**: Scan ALL .js and .ts files in Node.js project
2. **AUTO EXCLUDE**: node_modules, dist, build, .git, coverage, logs, temp, vendor
3. **Framework Detection**: Identify Express.js / Nest.js
4. **API Extraction**: Extract ALL routes, HTTP methods, paths, parameters
5. **Model Analysis**: Extract all data models, schemas, database structures
6. **Business Flow**: Extract state machines and business logic flows
7. **Full Documentation**: Generate 100% complete content with NO blanks
8. **Output**: Save as backend-api-doc.md in project root

## Documentation Template
The generated document follows this structure:

```markdown
# 1. 修改记录
| 版本 | 作者 | 内容 | 日期 |
| --- | --- | --- | --- |
| v1.0 | 自动生成 | 全量接口、数据模型、时序图、状态机完整生成 |  |

# 2. 需求背景
[自动生成，不能为空]

# 3. 功能需求
[全部业务模块完整列出，无遗漏]

# 4. 系统架构设计
[完整描述 Node 服务架构、分层、模块]

# 5. 状态机
[使用语雀的 plantUML 语法画出完整状态流转，无截断]

# 6. 数据模型
[使用完整 plantUML 语法，画出全部数据模型 + 关系，无截断]

## 6.1 表结构分类
[写出该项目的数据库结构分类，如用户表、商品表、订单表等]
示例：

| **分类** | **表名** | **中文名称** | **主要用途** |
| --- | --- | --- | --- |
| 系统核心 | `oa_role` | 角色表 | 定义系统角色和权限配置 |
| | `oa_user` | 用户表 | 存储系统用户账号信息 |
| | `system_audit_log` | 系统审计日志表 | 记录系统操作日志 |
| 本体配置 | `ontology_category` | 产品分类表 | 定义产品分类体系 |
| | `ontology_region` | 区域配置表 | 定义区域和货币信息 |
| | `ontology_dict_item` | 字典项表 | 存储系统参数和枚举值 |
| 规则引擎 | `rule_rate_table` | 报价规则表 | 定义不同区域和类别的报价范围 |
| | `risk_rule` | 风险规则表 | 定义风险检测规则 |
| | `risk_event` | 风险事件表 | 记录风险事件 |


## 6.2 表之间的关联关系
[写出每个表的字段说明，包括字段类型、是否必填、验证规则等]
示例：
| 关联关系 | 关联类型 | 外键字段 | 关联表 | 关联字段 | 说明 |
| --- | --- | --- | --- | --- | --- |
| **用户-角色** | `oa_role`（一）→ `oa_user`（多） | `oa_user.role_code` | `oa_role` | `role_code` | 一个角色可以被多个用户使用，一个用户只能属于一个角色 |
| **分类-用户（创建人）** | `oa_user`（一）→ `ontology_category`（多） | `ontology_category.created_by` | `oa_user` | `id` | 一个用户可以创建多个分类，一个分类只能由一个用户创建 |

## 6.3 ER 图
[使用语雀的 plantUML 语法画出该项目的 ER 图]

# 7. 技术栈
[写出当前项目中涉及到的核心的技术栈，如 Node.js、Express.js、Nest.js、MySQL、PostgreSQL、MongoDB、Redis、RabbitMQ、Docker、Kubernetes 等]

# 8. 环境变量
[写出当前项目的环境变量配置，如端口、数据库、Redis、JWT、环境变量等全部列出]

# 9. 联调环境的 BASE URL
[写出当前项目的联调环境的 BASE URL，如开发环境、测试环境、生产环境等，每个环境的 BASE URL 等]
示例：
| 环境 | 接口基础 URL | 说明 | 前端联调注意事项 |
| --- | --- | --- | --- |
| 开发环境 | http://localhost:3000/api/v1 | 本地开发（前端本地启动时对接） | 需确保后端本地服务已启动，端口一致 |
| 联调环境 | https://dev-api.xxx.com/api/v1 | 前后端联调专用 | 开发完成后，前端优先对接此环境联调，排查跨域、接口适配问题 |
| 测试环境 | https://test-api.xxx.com/api/v1 | 测试联调 | 联调通过后，对接测试环境做功能测试 |
| 预发环境 | https://pre-api.xxx.com/api/v1 | 预发布验证 | 线上发布前，最终验证接口一致性 |
| 生产环境 | https://api.xxx.com/api/v1 | 线上正式环境 | 线上部署后，前端正式对接地址 |

# 10. 全局错误码规范
[分析当前项目中使用的错误码规范，如 0 成功、1 失败、2 参数错误等，统一返回标准错误码，前端根据 code 判断业务状态。]
示例：
| 错误码 | 英文标识 | 中文描述 | 说明 |
| --- | --- | --- | --- |
| 0 | SUCCESS | 请求成功 | 正常返回 |
| 1001 | PARAM_ERROR | 参数错误 | 入参格式/必填项不合法 |
| 1002 | UNAUTHORIZED | 未授权 | 未登录或 token 过期 |
| 1003 | FORBIDDEN | 权限不足 | 无权限访问该接口 |
| 1004 | NOT_FOUND | 资源不存在 | 查询数据不存在 |
| 1005 | DUPLICATE | 数据重复 | 唯一约束冲突 |
| 5000 | SERVER_ERROR | 服务器异常 | 服务内部错误 |

# 11. 详细设计
- 【重要】必须列出全部模块、全部接口，每个接口必须包含：时序图 + 接口地址 + 请求头 + 请求参数 + 响应参数
- 禁止遗漏任何接口，禁止只写部分接口。

## 11.1 模块1（全部模块依次列出）
### 11.1.1 接口1（全部接口依次列出）
#### 11.1.1.1 时序图
```plantuml
@startuml
[完整时序图，无截断]
@enduml
```
#### 11.1.1.2 接口设计
接口地址：[完整地址]
请求方式：[GET/POST/PUT/DELETE]
接口描述：[完整描述]

请求头：
| 参数名称 | 参数类型 | 是否必填 | 说明 |
| :--- | :--- | :--- | :--- |
| Authorization | string | 是 | Bearer {token} |
| Content-Type | string | 是 | application/json |

请求参数：
| 参数名称 | 参数类型 | 是否必填 | 说明 | 验证规则 |
| :--- | :--- | :--- | :--- | :--- |
| param1 | string | 是 | 参数1 | 非空 |

响应参数：
```json
{
  "code": 0,
  "msg": "success",
  "data": [完整结构，无省略]
}
```
【必须严格执行】按上述格式完整生成所有模块、所有接口，不得遗漏、不得简写、不得等待后续补充。

## Supported Tech Stack (Node.js ONLY)
- **Runtime**: Node.js
- **Languages**: JavaScript, TypeScript
- **Frameworks**: Nest.js, Express.js
- **ORM**: Prisma, TypeORM, Sequelize, Mongoose
- **Databases**: MySQL, PostgreSQL, MongoDB, SQLite
- **Tools**: Redis, JWT, Docker, PM2, Dotenv

## Command & Trigger
- `/gen-backend-api-doc`
- `生成后端API文档`
- `分析后端项目并生成设计文档`

## Usage
Automatically analyze Node.js + Express/Nest.js project:
1. Full scan all .js & .ts files (exclude node_modules/dist)
2. Detect framework & tech stack
3. Generate 100% complete documentation
4. Output to backend-api-doc.md

## Error Handling & Limitations
- **ONLY supports Node.js + Express/Nest.js (JS/TS)**
- DO NOT support Java, Python, Go, PHP, or any other languages
- Even if structure is complex, still generate FULL content without blanks
- Only analyze routes, controllers, models, APIs, and code structure

## Input & Output
- Input: Node.js backend project directory
- Output: backend-api-doc.md (full API, models, diagrams)
- Return: Success + file path

## Prerequisites
- Standard Node.js project
- Express.js or Nest.js framework
- Normal directory structure (controllers, routes, models)

## Suitable Projects
- Nest.js backend (JS/TS)
- Express.js API server (JS/TS)
- Node.js BFF service
- Node.js microservice

## Notes
- **One-time full generation, no need for secondary prompts**
- No blanks, no omissions, no incomplete diagrams
- Manual adjustment only for optimization, not filling missing content
