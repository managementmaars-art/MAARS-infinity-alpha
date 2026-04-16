---
name: eliteforge-tech-doc
description: 通用技术设计文档归纳技能：扫描当前执行目录中的文档与图（Markdown、PlantUML/Mermaid、drawio、图片等），提炼系统目标、模块边界、核心流程、时序与状态，输出结构化技术设计文档。用户提到“技术设计文档”“方案梳理”“根据现有文档汇总设计”“汇总目录内文档和图”“补全时序图/状态图”时使用。
---

# EliteForge Tech Doc

## 目标

- 基于已有材料生成可评审技术设计文档，不凭空编造事实。
- 覆盖当前执行目录中的全部文档与图：至少纳入来源清单并给出处置结论（已采纳/背景参考/待确认）。
- 优先复用仓库中的既有术语、流程名称和图示风格。

## 执行顺序（每次都做）

1. 在当前执行目录运行 `scripts/list_doc_and_diagram_sources.sh .` 盘点资料。
2. 建立“来源清单”并按优先级读取：
   - P0：`README*`、`*design*`、`*architecture*`、`*spec*`、`docs/**` 中核心文档。
   - P1：接口、数据模型、部署、运维、故障处理文档。
   - P2：长尾说明文档与图像资源（至少做一行摘要，不遗漏）。
3. 建立事实依据（建议字段：`结论`、`证据文件`、`置信度`、`备注`）。
4. 先读 [references/tech-doc-template.md](references/tech-doc-template.md)，按模板起草目标文档。
5. 优先复用已有图：
   - 存在 `.mmd/.mermaid/.puml/.plantuml/.drawio` 时，优先引用或改写为同等语义图块。
   - 仅存在图片图（`.png/.jpg/.jpeg/.webp`）时，只能依据周边文档和文件名归纳，不确定项标记为“待人工确认”。
6. 输出文档到用户指定路径；用户未指定时默认写入当前目录 `./tech-design.md`。
7. 按 [references/quality-checklist.md](references/quality-checklist.md) 自检后再回复结果。

## 强制约束

- 禁止臆造组件、接口、流程、状态、时序关系。
- 每个关键结论至少绑定 1 个来源文件路径。
- 发现冲突信息时，必须显式列出冲突点与取舍依据。
- 不得忽略扫描结果中的任何文档/图文件；无法消费的文件必须写明原因。
- 输出文档必须包含“来源清单”和“待确认项”。
- 涉及插件化、SPI、Hook等可扩展设计时，必须包含“模块扩展点设计”章节，内部接口设计不属于可扩展范围。

## 图与流程提炼规则

1. 对流程类内容，优先输出“场景化结构”：触发条件、输入、步骤、输出、异常分支。
2. 对调用链内容，优先使用 `mermaid` `sequenceDiagram` 表达关键参与者与调用方向。
3. 对状态流转内容，优先使用 `mermaid` `stateDiagram-v2` 表达状态与迁移条件。
4. 对伪代码，保留领域动作名，不替换为空泛描述。
5. 对无法确认的图含义，保留原文件路径并标注“待人工确认”，不要猜测细节。

## 产出文档最低结构

按模板输出，至少包含以下章节：

1. 文档来源清单
2. 背景与目标
3. 术语与边界
4. 核心场景流程（含伪代码）
5. 时序图
6. 状态图
7. 模块扩展点设计（无扩展时写“暂不支持扩展。”，但不能省略标题）
8. 风险与待确认项

便于从业务动作追溯到系统实现。

## 输出风格

- 默认中文输出，关键名词沿用原文（如模块名、接口名、类名）。
- 段落短句化，避免泛化空话。
- 图和伪代码只保留对评审决策有价值的内容，避免冗长重复。

## 参考资料读取策略

- 首次执行先读 [references/tech-doc-template.md](references/tech-doc-template.md)。
- 出稿前必读 [references/quality-checklist.md](references/quality-checklist.md) 做最终检查。

## 快速命令

```bash
# 1) 盘点当前目录文档和图
skills/eliteforge-tech-doc/scripts/list_doc_and_diagram_sources.sh .

# 2) 生成技术设计文档（文件名可改）
# 输出示例：./tech-design-summary.md
```

## 示例触发语句

- “请扫描当前目录所有文档和图，产出技术设计文档。”
- “根据仓库里的 markdown 和时序图，整理一份方案设计稿。”
- “把现有设计资料汇总成可评审的 tech design，并标出缺失信息。”

## 参考文件

- [技术设计文档模板](references/tech-doc-template.md)
- [质量自检清单](references/quality-checklist.md)
