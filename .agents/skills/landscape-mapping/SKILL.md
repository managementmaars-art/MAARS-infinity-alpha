---
name: landscape-mapping
description: Map out an entire industry sector or technology landscape with layered taxonomy, company positioning, and investment thesis. Produces a structured landscape document with value chain analysis, company profiles, competitive positioning matrix, and investment implications. Use when asked to map a sector, build an investment map, analyze a landscape, create a market overview, or when user says "帮我 map 一下这个赛道" "做一个行业全景" "landscape" "投资地图".
---

# Landscape Mapping — 行业全景研究

把一个行业/赛道系统地拆解清楚：谁在做什么，技术路线怎么分，价值往哪里聚集，什么样的公司最终会赢。

与 company-research（单公司深研）不同，landscape-mapping 关注的是**整个赛道的结构和格局**。它的产出可以直接用于 sx-writer 写投资地图类文章。

## Workflow

### Step 1: 定义研究范围

确认赛道边界：
- **赛道名称**：用户指定的行业/技术领域
- **触发事件**：什么新闻/技术发布/融资事件激发了这次研究？（Why Now）
- **研究深度**：快速扫描（10-15 家公司，1-2 天）vs 深度 mapping（20+ 家，1 周）

### Step 2: 构建价值链分层

每个赛道都有自己的分层逻辑。核心框架是**垂直 stack 模型**，通常 3-5 层：

```
Layer 1: 基础层（Infrastructure）
  └ 计算、存储、网络、硬件
Layer 2: 平台层（Platform / Middleware）
  └ 开发框架、编排工具、数据管道
Layer 3: 应用层（Application）
  └ 面向最终用户的产品
Layer 4: 服务层（Service / Distribution）（可选）
  └ GTM、渠道、生态
```

根据具体赛道调整分层。例如：
- **Agent Infra** → Sandbox → Runtime → Orchestration → Agent Products → Self-builders
- **AI Healthcare** → Provider Adoption → Payer Adoption → BioPharma → Clinical Decision
- **Coding Tools** → Model Layer → IDE Layer → Workflow Layer → Vibe Coding

分层的关键判断：**价值在哪一层聚集？** 这决定了投资的优先级。

### Step 3: 并行搜索与公司定位

对赛道中的每家公司，搜集以下信息（可与 company-research 联动）：

**每家公司的最小信息集：**
- 一句话定位
- 核心产品/技术
- 融资状态（轮次 + 金额 + 领投方）
- 估值（如有）
- 客户/用户信号（标杆客户 or 开源 stars）
- 所在层级（属于 stack 的哪一层）

**搜索策略：**
- `"{赛道关键词}" landscape map companies startups`
- `"{赛道关键词}" funding 2025 2026`
- 查看头部 VC 的 portfolio（a16z, Sequoia, Benchmark 等近期 deal）
- 查看竞品比较文章（"X vs Y vs Z"）
- 查看行业报告（CB Insights, PitchBook, Not Boring 等）

### Step 4: 竞争定位矩阵

用二维矩阵定位所有公司。选择最有区分度的两个维度作为坐标轴：

常用维度组合：
- **X: Agent-Native 程度** × **Y: 隔离强度**（Infra 类）
- **X: 产品成熟度** × **Y: TAM 天花板**（应用类）
- **X: 技术自研程度** × **Y: 商业化进展**（通用类）

输出格式：
```
                    [Y 轴高]
                       │
    ┌──────────────────┼──────────────────┐
    │  Company A       │     Company B    │
    │                  │                  │
    ├──────────────────┼──────────────────┤
    │  Company C       │     Company D    │
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
  [X 轴低] ────────────┼──────────────── [X 轴高]
                    [Y 轴低]
```

### Step 5: 评估框架（可选）

对需要深度对比的赛道，用多维评分矩阵：

| 公司 | 维度1 | 维度2 | 维度3 | 维度4 | 维度5 | 综合 |
|------|-------|-------|-------|-------|-------|------|

评分维度根据赛道调整。例如 Agent Infra：安全性、性能、可扩展性、状态管理、Agent-Native、DX、成本。

### Step 6: 投资论点提炼

每个赛道总结 2-4 条 investment thesis：

```
Thesis 1: [论点名称]
- Problem → Company Type → Moat Source → Outcome
- 代表公司：

Thesis 2: ...
```

同时回答：
- 这个赛道最终是赢者通吃还是多家共存？
- 哪一层捕获了不成比例的价值？
- 大公司（OpenAI/Google/AWS）会不会自己做？如果会，创业公司的壁垒在哪？
- 未来 12 个月的催化剂是什么？

## Output Format

```markdown
# {赛道名} — Landscape Map
生成时间：{日期}

---

## Why Now
{什么变化创造了这个赛道的机会？1-2 段}

## 价值链分层

### Layer 1: {层名}
{这一层做什么，价值和机会在哪}

| 公司 | 定位 | 产品 | 融资 | 信号 |
|------|------|------|------|------|

### Layer 2: {层名}
...

### Layer 3: {层名}
...

---

## 竞争定位矩阵
{二维定位图 + 解读}

---

## 重点公司（按投资优先级排序）

### 1. {公司名}
- **定位**：
- **核心产品**：
- **融资**：
- **为什么值得关注**：
- **主要风险**：

### 2. ...

---

## Investment Thesis

### Thesis 1: {名称}
{论点 + 代表公司 + 催化剂}

### Thesis 2: ...

---

## 赢家特征
{什么样的公司最终会赢？3-5 条特征}

## 关键问题（待验证）
- [ ] {需要进一步研究或等待数据的问题}
- [ ]

---

## 推荐下一步
- 对排名靠前的公司使用 **company-research** 做深度 Pack
- 用 **company-screening** 做 3T 评分排行
- 用 **sx-writer** 写成投资地图文章
```

## 核心原则

1. **结构 > 罗列** — 不是列出 50 家公司就完了，核心价值是分层和定位
2. **观点 > 信息** — 每一层都要有"价值往哪走"的判断
3. **壁垒分析要诚实** — 如果大公司可以轻松做，就明确说出来
4. **动态视角** — 这个赛道 6 个月后会怎样？什么事件会改变格局？
