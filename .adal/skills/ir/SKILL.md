---
name: ir
description: "Generate LP-facing investment reports and updates from internal research. Produces high-level strategic summaries suitable for LP communication — more 'big picture thesis' than granular company analysis. Use when asked to prepare LP update, quarterly letter, investor report, or when user says '帮我写一个给LP的更新' 'LP report' 'quarterly update' '投资人沟通材料'."
---

# IR — LP 沟通材料生成

将内部研究成果提炼为面向 LP 的投资报告。风格比公众号文章更高屋建瓴——不是介绍单个公司，而是传达投资框架、市场判断和 portfolio 逻辑。

## 参考范本

`content-reference/06-How To Play AI Beta：拾象 2026 AGI 投资思考开源.md` 是最佳范本。这篇文章的特征：
- 开篇即是投资框架级别的判断，不是新闻综述
- 每个论点都有"我们怎么想"和"我们怎么做"
- 数据服务于论点，不是罗列
- 适度披露 portfolio 逻辑，建立信任

## 两种输出格式

### 1. 精简版（适合邮件或 1-pager）

```markdown
# {基金名} — {时间段} Investment Update

## Market View
{2-3 段：当前 AI 市场的核心判断，这个季度最重要的变化是什么}

## Portfolio Highlights
{3-5 条：每条一家 portfolio 公司，说清楚为什么投、最新进展}

## Thesis Evolution
{我们的投资框架有什么更新？哪些信念强化了，哪些需要修正？}

## Outlook
{未来 6 个月我们关注什么，准备怎么布局}
```

### 2. 详细版（适合季报或年度 Letter）

```markdown
# {基金名} — {年/季度} Letter to LPs

## I. Executive Summary
{1 页：核心业绩数据 + 3 句话总结本期最重要的事}

## II. Market Landscape
{当前 AI 市场的结构性变化，用我们自己的框架解读}

### 高确定性方向
{列出我们认为确定性最高的 3-5 个方向，每个附 1 段论述}

### 需要观察的信号
{列出我们在等什么信号才会加大投入}

## III. Portfolio Review
{逐一介绍 portfolio 公司，每家 200-400 字}

对每家公司：
- 投资论点（当初为什么投）
- 最新进展（业务数据、产品里程碑、融资）
- 当前判断（论点是否被验证）

## IV. Investment Activity
{本期新增投资、后续跟投、退出事件}

## V. Thesis & Framework
{投资框架的演进。哪些命题被验证，哪些需要修正}

### 我们的核心命题
1. 只在技术增速最快处下注
2. AGI Basket，不赌单一赢家
3. Service-as-Software 颠覆 SaaS
4. Long-Horizon Agent 是下一个范式跃迁
5. 中美互补，不对立

{每条命题附 1-2 句最新验证情况}

## VI. Outlook
{未来 6-12 个月的市场预期和布局计划}
```

## 写作风格

LP 材料的风格与公众号文章不同：

| 维度 | 公众号（sx-writer） | LP 材料（ir） |
|------|-------------------|-------------|
| 读者 | 聪明的科技爱好者 | 专业投资人，时间有限 |
| 语气 | 克制的自信 | 专业、简洁、不卖弄 |
| 结构 | 叙事驱动 | 框架驱动 |
| 数据 | 服务于故事 | 数据本身就是内容 |
| 语言 | 中文为主+英文术语 | 根据 LP 群体选择（中文 LP 用中文，海外 LP 用英文） |
| 篇幅 | 4000-8000字 | 精简版 1-2 页，详细版 5-10 页 |

**核心区别**：LP 想知道的是"你怎么想、你怎么做、结果怎么样"，不是"这个行业有多酷"。

## 素材来源

生成 LP 材料时，从以下位置提取信息：
- `research/` 目录中的 Research Pack 和 Landscape Map
- `content-reference/` 中的已发布文章
- 用户提供的 portfolio 数据和业绩
- 近期的会议纪要（transcript 的输出）

## 关键规则

1. **框架 > 细节** — LP 要的是你的 thesis 和 judgment，不是公司介绍
2. **诚实面对不确定性** — 说清楚什么是已验证的，什么还在等信号
3. **数字精确** — LP 对数字极其敏感，所有业绩数据必须准确
4. **保密意识** — 注意哪些 portfolio 信息可以披露，哪些需要脱敏
5. **不要过度乐观** — 投资人最讨厌的是只报喜不报忧
