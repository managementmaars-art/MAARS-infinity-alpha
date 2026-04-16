---
name: analyze-value
description: '决策导向的价值分析（论文、事件、技术方向或产品）——渐进式执行（定位→并行采集→交叉合成→输出报告），找不到目标则提前退出。触发词：分析价值、analyze value、这篇paper值得看吗、论文价值分析、事件分析、这件事值得关注吗、XX技术值得关注吗、技术价值分析、XX值得买吗、产品分析。'
allowed-tools: Agent, WebSearch, WebFetch, Read, Write
context: fork
---

# Analyze Value — 决策价值分析（论文 / 事件 / 技术 / 产品）

输入论文 URL/PDF/标题、事件描述/新闻链接、技术方向名称 或 具体产品型号/系列，渐进式执行（定位 → 并行采集 → 交叉合成），输出一份面向决策的价值分析报告。找不到目标则提前退出，不浪费 agent 调用。

与其他技能的区别：本技能聚焦**决策判断**——是否值得关注/购买/投入、为什么、怎么行动。

## When to Use

**论文分析**：
- "这篇论文值得看吗" / "分析下这篇paper的价值"
- "论文价值分析 https://arxiv.org/abs/..."
- "analyze value: Attention Is All You Need"

**事件分析**：
- "分析下美联储降息这件事" / "这次裁员潮值得关注吗"
- "analyze value: OpenAI发布GPT-5"
- "这个政策/事件对我有什么影响"

**技术价值分析**：
- "光刻机技术值得关注吗" / "EUV技术现在到什么阶段了"
- "analyze value: RISC-V技术" / "分析下具身智能的价值"
- 需要判断一个技术方向是否值得投入关注或资源

**产品价值分析**：
- "ASML NXE:3800E值得采购吗" / "iPhone 16 Pro值得买吗"
- "analyze value: Tesla Model 3" / "分析下这款光刻机的价值"
- 需要判断一个具体产品（型号或系列）是否值得购买/采购/采用

**不触发**：
- 深度学术笔记 → `/analyze-paper`
- 技术全景调研（怎么用、学习路径、生态）→ `/analyze-tech`

---

## Phase 0: 输入分类与目标定位（必须首先执行）

> **⚠️ 关键步骤：必须先完成分类，再进入对应流程。禁止跳过分类直接执行论文定位。**

### Step 1: 判断分析类型（第一步，不可跳过）

根据用户输入判断属于**论文**、**事件**、**技术**还是**产品**分析。**默认规则：没有明确论文/技术/产品信号的输入走事件分析。**

| 信号 | 判定 |
|------|------|
| 有 arXiv/DOI/PDF 链接、明确提到"论文""paper""这篇文章" | → `{analysis_type}` = **paper** → Phase 0A |
| 有品牌+型号/系列名、"值得买吗""买哪个""选哪款""采购""评测" | → `{analysis_type}` = **product** → Phase 0D |
| 技术领域/方向/路线、"XX技术""XX方向""XX趋势"、无品牌型号的技术名词 | → `{analysis_type}` = **tech** → Phase 0C |
| 新闻链接、有明确时间点的事件/政策/发布/事故、"XX事件""加息""降息""裁员" | → `{analysis_type}` = **event** → Phase 0B |
| 确实无法判断 | 向用户确认后再继续 |

**示例**：
- "ASML NXE:3800E" → **product**（品牌+具体型号）
- "iPhone 16 Pro值得买吗" → **product**（品牌+型号+"值得买"）
- "Tesla Model 3系列" → **product**（品牌+产品系列）
- "ASML EUV光刻机系列" → **product**（品牌+产品系列）
- "日元加息事件" → **event**（描述宏观经济事件）
- "OpenAI发布GPT-5" → **event**（描述产品发布事件）
- "分析下美联储降息这件事" → **event**（描述政策事件）
- "光刻机技术" → **tech**（技术方向，无品牌）
- "具身智能值得关注吗" → **tech**（技术领域）
- "RISC-V技术现在到什么阶段了" → **tech**（技术路线）
- "arxiv.org/abs/2401.xxxxx" → **paper**（有 arXiv 链接）
- "Attention Is All You Need" → **paper**（明确论文标题）

**关键区分要点**：
- **product vs tech**：有品牌+型号/系列 → product；只有技术领域名 → tech。"ASML EUV光刻机系列" → product；"EUV光刻技术" → tech。
- **product vs event**：产品本身的价值判断 → product；产品发布这件事的影响 → event。"iPhone 16 Pro值得买吗" → product；"苹果发布iPhone 16" → event。
- **tech vs event**：持续存在的技术方向 → tech；有时间点的具体事件 → event。

判定后进入对应的 Phase 0 流程。

---

### Phase 0A: 论文定位（仅当 analysis_type = paper）

> 如果 Step 1 判定为 event，**跳过本节**，直接到 Phase 0B。

根据用户输入，尝试定位论文：

| 输入类型 | 处理流程 |
|---------|---------|
| **URL** | WebFetch 抓取页面，提取标题、作者、摘要、机构 |
| **PDF 路径** | Read 读取 PDF，提取标题、作者、摘要 |
| **标题/关键词** | WebSearch 搜索定位，再 WebFetch 获取详情 |

#### 早退规则

如果满足以下任一条件，**直接告知用户并结束**，不进入后续 Phase：

- WebSearch 搜索 2 次仍无法定位到具体论文
- 用户输入过于模糊（如"AI论文"），无法确定唯一目标
- URL 无法访问且无替代来源

结束时输出：`未能定位到论文「{用户输入}」，请提供更具体的论文标题、arXiv 链接或 PDF 路径。`

#### 获取论文原文（不可跳过）

按顺序尝试，直到获得包含正文的内容：

1. **arXiv HTML**（首选）：`WebFetch https://arxiv.org/html/{id}`
2. **用户提供的 PDF 路径**：`Read {pdf_path}` 读取全文
3. **会议/期刊页面**：`WebFetch {conference_url}`
4. **Zenodo / 非 arXiv 预印本**：先 WebFetch 主页获取文件列表，再 WebFetch PDF 下载 URL（Zenodo 格式：`https://zenodo.org/records/{id}/files/{filename}.pdf`，文件名从页面 files 区域读取）

将论文原文存入 `{paper_content}`。

#### 确认通讯作者（必须完成，不可跳过）

从 `{paper_content}` 查找通讯作者标注：
- 常见标记：`*` `†` `‡` 上标、`✉`、`Corresponding author`、email 脚注
- 若当前 `{paper_content}` 中未找到以上标记，**必须额外获取 PDF 原文**（重试上方步骤 2 或 4），因为通讯作者标注通常只在 PDF 第一页

确认后存入 `{corresponding_authors}`；确实无法获取 PDF 时，记录 `"未在可获取原文中找到（仅限 PDF 第一页）"`，**禁止从作者顺序或搜索结果推断**。

#### 确定关键变量

- `{paper_title}` — 论文标题
- `{authors}` — 作者列表
- `{corresponding_authors}` — 通讯作者列表（从论文原文标注确认，不可推断）
- `{institution}` — 机构
- `{year}` — 年份
- `{venue}` — 发表会议/期刊（未发表标注 preprint）
- `{abstract}` — 摘要
- `{paper_content}` — 论文原文内容
- `{core_problem}` — 从摘要/Introduction 提取的核心问题（几个关键词）
- `{lang}` — 输出语言（默认中文）
- `{date}` — 分析日期 YYYY-MM-DD
- `{name}` — 英文文件名（小写连字符，如 `msa-memory-sparse-attention`）

→ 进入 Phase 1-3 论文流程。

---

### Phase 0B: 事件定位（analysis_type = event）

根据用户输入，尝试定位事件：

| 输入类型 | 处理流程 |
|---------|---------|
| **新闻 URL** | WebFetch 抓取页面，提取事件标题、时间、主体、核心内容 |
| **事件描述** | WebSearch 搜索定位（至少 2 次不同关键词），WebFetch 获取 2-3 篇一手报道 |
| **模糊描述** | WebSearch 搜索确认具体事件后继续 |

#### 早退规则

如果满足以下任一条件，**直接告知用户并结束**：

- WebSearch 搜索 2 次仍无法定位到具体事件
- 事件描述过于模糊（如"最近的新闻"），无法确定唯一目标
- 所有新闻源均无法访问

结束时输出：`未能定位到事件「{用户输入}」，请提供更具体的事件描述、新闻链接或关键词。`

#### 采集一手信息（不可跳过）

1. **WebSearch** 搜索 2-3 次（不同关键词组合），收集一手报道和权威分析
2. **WebFetch** 获取至少 2 篇一手来源（官方声明、权威媒体报道）
3. 提取事件的 5W 基本要素：Who / What / When / Where / Why

将采集到的一手信息存入 `{event_sources}`。

#### 确定关键变量

- `{event_title}` — 事件标题（一句话概括）
- `{event_time}` — 事件发生/预期发生时间
- `{event_status}` — 状态（已发生 / 正在进行 / 即将发生 / 传闻未确认）
- `{key_actors}` — 关键主体（决策者、受影响方）
- `{core_content}` — 事件核心内容摘要（200字以内）
- `{event_sources}` — 一手信息源内容
- `{core_problem}` — 事件涉及的核心问题/矛盾（几个关键词）
- `{impact_scope}` — 影响范围（个人/行业/国家/全球）
- `{lang}` — 输出语言（默认中文）
- `{date}` — 分析日期 YYYY-MM-DD
- `{name}` — 英文文件名（小写连字符，如 `fed-rate-cut-2026`）

→ 进入 Phase 1-3 事件流程。

---

### Phase 0C: 技术主题定界（仅当 analysis_type = tech）

> 如果 Step 1 判定为 paper 或 event，**跳过本节**。

#### 粒度校验

技术分析需要适当的粒度。过宽则无法给出有用的决策判断，过窄则退化为单一产品/论文分析。

| 粒度 | 示例 | 处理 |
|------|------|------|
| **过宽** | "AI""半导体" | 向用户确认细分方向（如"大模型推理优化"还是"AI芯片"？） |
| **合适** | "EUV光刻机""RISC-V处理器""具身智能" | 直接继续 |
| **过窄** | 某个具体产品/单篇论文 | 建议转为 paper 或 event 分析 |

#### 采集一手信息（不可跳过）

1. **WebSearch** 搜索 2-3 次（不同关键词组合），收集技术综述、行业报告、权威分析
   - "{tech_title} 技术路线 现状 2025 2026"
   - "{tech_title} technology landscape players"
   - "{tech_title} 发展历程 里程碑 breakthrough"
2. **WebFetch** 获取至少 2 篇高质量来源（行业报告、综述文章、权威媒体深度报道）
3. 提取技术的基本轮廓：核心问题、主要路线、关键玩家、当前阶段

将采集到的一手信息存入 `{tech_sources}`。

#### 早退规则

如果满足以下任一条件，**直接告知用户并结束**：

- WebSearch 搜索 2 次仍无法找到该技术的实质性信息
- 技术过于小众，缺乏足够的公开分析来源

结束时输出：`未能找到关于「{用户输入}」的足够信息，请确认技术名称或提供更多上下文。`

#### 确定关键变量

- `{tech_title}` — 技术名称
- `{tech_scope}` — 分析粒度（核心技术 / 技术路线 / 产业链环节）
- `{maturity_stage}` — 成熟度初判（早期研究 / 工程化 / 规模量产 / 成熟）
- `{key_players}` — 关键玩家（公司/研究机构/国家）
- `{core_problem}` — 核心技术挑战（几个关键词）
- `{tech_sources}` — 采集的一手信息
- `{impact_scope}` — 影响范围（细分领域 / 行业 / 跨行业 / 全球）
- `{lang}` — 输出语言（默认中文）
- `{date}` — 分析日期 YYYY-MM-DD
- `{name}` — 英文文件名（小写连字符，如 `euv-lithography`）

→ 进入 Phase 1-3 技术流程。

---

### Phase 0D: 产品定位（仅当 analysis_type = product）

> 如果 Step 1 判定为 paper、event 或 tech，**跳过本节**。

#### 粒度校验

| 粒度 | 示例 | 处理 |
|------|------|------|
| **具体型号** | "ASML NXE:3800E""iPhone 16 Pro" | 直接继续 |
| **产品系列** | "Tesla Model 3系列""ASML EUV光刻机系列" | 继续，覆盖系列内对比 |
| **过宽（品牌级）** | "ASML的产品""苹果手机" | 向用户确认具体型号或系列 |

#### 采集一手信息（不可跳过）

1. **WebSearch** 搜索 2-3 次（不同关键词组合），收集官方规格、评测、定价
   - "{product_name} specifications specs official"
   - "{product_name} review 评测 对比"
   - "{product_name} price 价格 competitors alternatives"
2. **WebFetch** 获取至少 2 篇高质量来源（官方产品页、权威评测、行业分析）
3. 提取产品核心信息：规格参数、定价、竞品、目标用户

将采集到的一手信息存入 `{product_sources}`。

#### 早退规则

如果满足以下任一条件，**直接告知用户并结束**：

- WebSearch 搜索 2 次仍无法找到该产品的实质性信息
- 产品尚未正式发布且缺乏可靠泄露信息

结束时输出：`未能找到关于「{用户输入}」的足够信息，请确认产品名称或提供更多上下文。`

#### 确定关键变量

- `{product_name}` — 产品全名（品牌+型号/系列）
- `{manufacturer}` — 品牌/制造商
- `{product_category}` — 品类（用于确定比较范围，如"EUV光刻机""旗舰手机""中型SUV"）
- `{product_tier}` — 定位（旗舰/中端/入门 或 行业等级）
- `{price_range}` — 价格区间
- `{release_status}` — 状态（已发售 / 已发布未发售 / 传闻）
- `{core_specs}` — 核心规格摘要
- `{product_sources}` — 采集的一手信息
- `{lang}` — 输出语言（默认中文）
- `{date}` — 分析日期 YYYY-MM-DD
- `{name}` — 英文文件名（小写连字符，如 `asml-nxe-3800e`）

→ 进入 Phase 1-3 产品流程。

---

## Phase 1-3: 加载详细流程

根据 `{analysis_type}` 加载对应的详细工作流：

- **论文分析**：使用 Read 工具加载 `$CLAUDE_SKILL_DIR/analysis-workflow.md`
- **事件分析**：使用 Read 工具加载 `$CLAUDE_SKILL_DIR/event-workflow.md`
- **技术分析**：使用 Read 工具加载 `$CLAUDE_SKILL_DIR/tech-workflow.md`
- **产品分析**：使用 Read 工具加载 `$CLAUDE_SKILL_DIR/product-workflow.md`

按 Phase 1（并行采集）→ Phase 2（综合分析）→ Phase 3（输出报告）执行。将 Phase 0 中确定的所有变量传递给后续流程。

---

## Error Handling

| 情况 | 处理 |
|------|------|
| 论文/事件/技术/产品无法定位 | **直接结束**，输出未找到提示，不进入 Phase 1 |
| Agent 超时/失败 | 对应部分标注"数据不足"，其余照常 |
| 论文原文无法获取 | 报告开头标注"⚠️ 未获取全文，以下基于摘要和搜索"，降低置信度 |
| 事件/技术/产品信息源不足 | 报告开头标注"⚠️ 一手信息有限，以下基于有限来源"，降低置信度 |
| 新论文/近期事件/新兴技术/未发售产品信息不足 | 合并相关部分，标注"信息较新，数据有限" |

## Notes

- 决策判断必须明确，不骑墙（"值得关注但需注意X"优于"可能值得也可能不值得"）
- 事件分析中，区分事实与预测，预测必须标注"分析认为"
- 事件如有多方立场，必须呈现各方视角，不偏向任一方
- 技术分析中，路线对比必须基于客观指标，避免主观偏好
- 产品分析中，竞品对比必须基于可验证的参数和价格，避免营销话术
- 输出语言跟随 `{lang}`，默认中文
