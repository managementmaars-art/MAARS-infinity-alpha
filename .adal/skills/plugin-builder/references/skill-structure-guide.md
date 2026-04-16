# Skill 结构指南

## 目录结构

```
skill-name/
├── SKILL.md           # 必需：主定义文件
├── reference.md       # 可选：参考文档
└── scripts/           # 可选：脚本目录
    └── script.py      # 辅助脚本
```

## SKILL.md 格式

### YAML Frontmatter

```yaml
---
name: skill-name
description: 触发条件描述，Claude 根据此判断何时使用
---
```

| 字段 | 说明 |
|------|------|
| `name` | 唯一标识符，kebab-case 格式 |
| `description` | 必须包含触发条件和使用场景描述 |

### 内容结构

```markdown
# Skill Title

详细指令内容...

## 使用场景
- 场景1
- 场景2

## 示例
示例用法...

## 参考
- [reference.md](reference.md) - 参考文档
```

## 关键规则

### name 字段
- 唯一标识符
- kebab-case 格式（小写字母、数字、连字符）
- 不能包含空格或特殊字符
- 示例：`my-skill`、`code-generator`、`api-helper`

### description 字段
- **最重要**：决定 Claude 何时使用该 skill
- 必须描述触发条件
- 包含使用场景关键词
- 示例：
  ```yaml
  description: 生成 RESTful API 客户端代码。当用户需要"生成 API 客户端"、"创建 API 请求"、"添加 API 调用"时使用此 skill。
  ```

### SKILL.md 位置
- 必须位于 skill 目录根目录
- 文件名必须大写：`SKILL.md`
- 子目录中的 SKILL.md 不会被识别

## 示例 Skill

```markdown
---
name: json-fixer
description: 修复和格式化 JSON 文件。当用户遇到"JSON 格式错误"、"修复 JSON"、"格式化 JSON"问题时使用此 skill。
---

# JSON Fixer

帮助你修复和格式化 JSON 文件。

## 常见问题

### 语法错误
- 缺少逗号
- 多余逗号
- 引号不匹配
- 括号不匹配

### 格式问题
- 缩进不一致
- 行尾多余空格

## 修复步骤

1. 读取文件内容
2. 使用 JSON 解析器验证
3. 报告具体错误位置
4. 修复错误
5. 重新格式化
```

## 最佳实践

### 1. 描述清晰
```yaml
# 好的描述
description: 生成 TypeScript 类型定义。当用户需要"生成类型"、"创建 interface"、"从 JSON 生成类型"时使用。

# 不好的描述
description: 这是一个生成类型的 skill。
```

### 2. 场景明确
```markdown
## 使用场景
- 从 OpenAPI 规范生成类型
- 从 JSON schema 生成 interface
- 从数据库 schema 生成模型类型
```

### 3. 内容简洁
- 保持 SKILL.md 在 500 行以内
- 复杂参考文档放在 reference.md
- 使用清晰的标题结构

### 4. 可测试
- 提供具体示例
- 说明输入输出格式
- 包含预期结果

## 与 Agent 的区别

| 特性 | Skill | Agent |
|------|-------|-------|
| 触发方式 | description 匹配 | 显式调用 |
| 独立性 | 在主对话中执行 | 独立上下文 |
| 工具访问 | 全部工具 | 指定工具 |
| 适用场景 | 增强主对话能力 | 独立复杂任务 |

## 调试技巧

### 检查 Skill 是否加载
```bash
# 列出所有 skills
ls ~/.claude/skills/
```

### 测试触发条件
在对话中使用描述中的关键词，观察 skill 是否被激活。

### 常见问题
1. **Skill 未被触发**：检查 description 是否包含足够的关键词
2. **内容过长**：拆分为多个文件或移到 reference.md
3. **路径错误**：确保 SKILL.md 在 skill 根目录
