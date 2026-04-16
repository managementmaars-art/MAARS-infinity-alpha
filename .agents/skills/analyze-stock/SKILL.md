---
name: analyze-stock
description: 一键综合分析某只股票/公司。通过并行子代理同时采集股价、新闻舆论、行业对比、市场环境、公司官网五个维度的数据，然后在主线程进行交叉分析、因果归因和趋势预测，输出标准化 HTML 分析报告（含当日行情和7日趋势）。触发词：分析XX股票、analyze TICKER、XX怎么样、XX值得买吗。支持A股、港股和美股。
allowed-tools: Agent, WebSearch, WebFetch, Write, Bash
disable-model-invocation: true
context: fork
---

# Analyze Stock — 一键股票综合分析

输入公司名称或股票代码，自动并行采集五个维度的数据，综合分析后输出标准报告。

## When to Use

当用户请求以下操作时触发：
- "分析腾讯" / "分析贵州茅台" / "分析 600519"
- "analyze NVDA" / "analyze Tesla"
- "XX股票怎么样" / "XX最近为什么涨/跌"
- "帮我看看XX" / "XX值得买吗"

## Phase 0: 解析输入

根据用户输入，识别以下信息：

先确定此 SKILL.md 文件所在目录为 `SKILL_DIR`，如需调用脚本，统一使用：

```bash
SKILL_DIR="<此 SKILL.md 文件所在目录的绝对路径>"
```

1. **公司名称与股票代码**
   - 如果用户给了代码则直接使用
   - 如果用户给了公司名，通过 WebSearch 查询对应代码
   - A股代码格式: 6位数字 (600519, 000858)
   - 美股代码格式: 英文字母 (NVDA, AAPL, TSLA)

2. **识别市场类型**
   - 6位纯数字 → A股
   - 4-5位数字 或 含 `.HK` 后缀 → 港股
   - 英文字母 → 美股
   - 公司名含中文且为中国公司 → 先搜索确认是A股还是港股
   - 其他 → 美股

3. **确定关键变量** (后续所有 Agent 都需要用到)
   - `{ticker}`: 股票代码
   - `{company_name}`: 公司全称
   - `{company_name_en}`: 公司英文名 (美股用)
   - `{market}`: "A股" / "港股" / "美股"
   - `{industry}`: 所属行业
   - `{website}`: 公司官网 URL

如果无法确定官网或行业，先用一次 WebSearch 快速查询，**不要跳过这一步**。

---

## Phase 1: 并行数据采集 (5 个 Subagent)

**关键要求**: 以下 5 个 Task 必须放在**同一条消息**中发出，确保并行执行。

每个 Agent 使用 `subagent_type: "general-purpose"`。

---

### Agent 1: 股价数据与技术指标

**description**: "采集{ticker}股价数据"

**prompt 模板**:

```
你是股价数据分析师。请获取 {company_name}({ticker}) 近7个交易日的股价数据，并**重点突出最近1个交易日的变化**。

任务:
1. 使用 WebSearch 搜索 "{ticker} stock price last 7 days {market}" 获取最近行情
2. 使用 WebSearch 搜索 "{ticker} stock price today" 获取最新交易日详细数据
3. 整理以下信息:

   **最近1个交易日 (当日行情):**
   - 开盘价、最高价、最低价、收盘价
   - 当日涨跌幅与涨跌金额
   - 当日成交量与成交额，较前一日放量/缩量比例
   - 盘中关键时点走势 (如: 开盘冲高回落、尾盘拉升等)
   - 当日是否有影响股价的即时事件

   **近7个交易日汇总:**
   - 每日收盘价和涨跌幅
   - 7天累计涨跌幅
   - 成交量变化趋势 (放量/缩量)
   - 关键技术信号 (如有: 均线多空排列、RSI超买超卖、明显支撑位/阻力位)
   - 与大盘同期涨跌幅对比

输出要求:
- 以结构化格式返回，**当日行情单独列出**
- 重点突出: 当日涨跌幅、7天涨跌幅、量价配合情况、技术面关键信号
- 控制在 600 字以内
- 不要给出投资建议
- **标注数据来源**: 关键数据注明来源（如东方财富、雪球、Yahoo Finance、Bloomberg 等）及原始链接
```

如果是 A股，且 akshare 已安装，可额外在 prompt 中指示:
```
如果可用，执行以下命令获取精确数据:
python "${SKILL_DIR}/scripts/data_fetcher.py" --code {ticker} --data-type valuation
```

---

### Agent 2: 新闻舆论分析

**description**: "搜索{company_name}近期新闻"

**prompt 模板**:

```
你是财经新闻分析师。请搜索 {company_name}({ticker}) 最近7天的重要新闻和舆论。

任务:
1. 使用 WebSearch 搜索以下关键词 (至少搜2次不同关键词):
   - "{company_name} 最新新闻" 或 "{company_name} latest news"
   - "{ticker} 股票 本周" 或 "{ticker} stock this week"
2. 从搜索结果中挑选 3-5 条最重要的新闻
3. 使用 WebFetch 访问其中至少 2 条新闻的原文，验证内容真实性
4. 分析舆论整体倾向

输出要求:
- 列出 3-5 条关键新闻，每条包含: 日期、标题、来源名称、**原文URL**、简要内容(1-2句)
- 整体舆论倾向判断: 正面 / 负面 / 中性，并说明理由
- 识别是否有重大事件 (财报发布、政策变化、管理层变动、产品发布、诉讼等)
- 控制在 600 字以内
```

---

### Agent 3: 行业对比分析

**description**: "分析{industry}行业情况"

**prompt 模板**:

```
你是行业分析师。请分析 {company_name}({ticker}) 所在的 {industry} 行业近期情况。

任务:
1. 使用 WebSearch 搜索:
   - "{industry} 行业 近期趋势" 或 "{industry} industry trends"
   - "{company_name} 竞争对手" 或 "{company_name} competitors"
2. 整理以下信息:
   - 行业近期整体趋势 (上升/下行/平稳)
   - 影响行业的关键因素 (政策、技术、需求等)
   - 2-3 个主要竞争对手的近期股价表现
   - {company_name} 在行业中的大致地位

输出要求:
- 行业趋势概述 (2-3句)
- 竞争格局简表: 公司名、近7天涨跌、关键动态
- 该公司的相对优劣势 (1-2条)
- 控制在 500 字以内
- **标注数据来源**: 竞争对手数据注明来源（如 Bloomberg、Wind、东方财富等）及链接
```

---

### Agent 4: 市场环境分析

**description**: "分析当前市场环境"

**prompt 模板**:

```
你是宏观市场分析师。请分析当前全球市场环境，重点关注与 {company_name}({ticker}) 相关的市场因素。

任务:
1. 使用 WebSearch 搜索最新市场数据:
   - 主要指数近期走势:
     - 如果A股: "上证指数 深证成指 创业板指 本周"
     - 如果港股: "恒生指数 恒生科技指数 国企指数 本周"
     - 如果美股: "S&P 500 NASDAQ Dow Jones this week"
   - "VIX index today" (恐慌指数)
   - 近期重大宏观事件或央行动态
2. 评估:
   - 大盘趋势方向: 上涨 / 下跌 / 震荡
   - 市场情绪: Risk-on (追逐风险) / Risk-off (规避风险)
   - VIX 水平及含义
   - 是否有重大宏观事件影响

输出要求:
- 市场环境一句话总结
- 大盘指数近7天表现 (涨跌幅)
- VIX 水平和波动率判断
- 影响当前市场的 1-2 个关键因素
- 控制在 400 字以内
- **标注数据来源**: 各指标注明来源（如 CBOE、Yahoo Finance、MacroTrends 等）及链接
```

---

### Agent 5: 公司官网与公告信息

**description**: "抓取{company_name}官网信息"

**prompt 模板**:

```
你是企业信息研究员。请获取 {company_name}({ticker}) 的官方最新动态。

任务:
1. 使用 WebFetch 访问公司官网: {website}
   - 查看首页是否有最新公告或新闻
2. 使用 WebSearch 搜索 "{company_name} 投资者关系" 或 "{company_name} investor relations"
   - 查找近期公告、财报摘要、业绩预告
3. 如果是上市公司，搜索最近的公告:
   - A股: "{company_name} 公告 巨潮资讯"
   - 港股: "{company_name} 公告 披露易" 或 "{company_name} hkex announcement"
   - 美股: "{company_name} SEC filing" 或 "{company_name} earnings"

输出要求:
- 公司最新官方动态 (产品、战略、人事等)
- 最近一次财报/业绩的关键数据 (如有)
- 近期重要公告摘要 (如有)
- 控制在 400 字以内
- 如果官网无法访问，说明情况并依赖搜索结果
- **标注数据来源**: 公告、财报数据注明来源（如 SEC EDGAR、巨潮资讯、港交所披露易等）及链接
```

---

## Phase 2: 综合分析 (主线程)

等待 5 个 Agent 全部返回后，在主线程中完成以下分析。

### Step 1: 信息汇总

将 5 个 Agent 的结果整合，识别：
- 各维度之间的 **一致性信号** (如: 股价涨 + 新闻利好 + 行业向上 = 强看多)
- 各维度之间的 **矛盾信号** (如: 股价涨但新闻利空 = 可能存在隐患)
- 同时整理各 Agent 返回的所有**来源 URL**，汇总到来源列表，用于报告末尾「参考来源」区块

### Step 2: 因果归因

分析股价变动的原因，按影响力排序：
1. **直接驱动因素**: 公司层面事件 (财报、公告、产品、舆论)
2. **行业传导因素**: 行业政策、竞争格局变化
3. **市场环境因素**: 大盘走势、资金面、宏观事件

**特别关注当日变动**: 对最近1个交易日的涨跌单独归因分析，区分日内驱动因素与中期趋势因素。

### Step 3: 趋势预测

基于以上分析，给出：
- **短期展望** (1-2周): 考虑技术面信号 + 即将到来的事件
- **中期展望** (1-3月): 考虑基本面 + 行业趋势
- **主要风险点**: 可能导致走势反转的因素

---

## Phase 3: 输出报告

按以下 HTML 格式输出最终报告。使用内联 CSS 确保在浏览器和飞书中均可良好显示：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{company_name} ({ticker}) 综合分析报告</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #1a1a1a; background: #f8f9fa; }
  .report { background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
  h1 { font-size: 24px; border-bottom: 3px solid #1a73e8; padding-bottom: 12px; }
  h2 { font-size: 18px; color: #1a73e8; margin-top: 28px; border-left: 4px solid #1a73e8; padding-left: 10px; }
  h3 { font-size: 15px; color: #333; margin-top: 16px; }
  .meta { color: #666; font-size: 13px; margin-bottom: 16px; }
  .summary { background: #e8f0fe; border-radius: 8px; padding: 16px; font-size: 16px; font-weight: 500; margin: 16px 0; }
  .daily-highlight { background: #fff8e1; border: 1px solid #ffcc02; border-radius: 8px; padding: 16px; margin: 16px 0; }
  .daily-highlight h2 { color: #f57f17; border-left-color: #f57f17; }
  table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 14px; }
  th { background: #f1f3f4; text-align: left; padding: 10px 12px; font-weight: 600; border-bottom: 2px solid #ddd; }
  td { padding: 8px 12px; border-bottom: 1px solid #eee; }
  tr:hover td { background: #f8f9fa; }
  .up { color: #d32f2f; font-weight: 600; }
  .down { color: #2e7d32; font-weight: 600; }
  .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
  .tag-positive { background: #e8f5e9; color: #2e7d32; }
  .tag-negative { background: #ffebee; color: #c62828; }
  .tag-neutral { background: #f5f5f5; color: #616161; }
  .risk { background: #fff3e0; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }
  .disclaimer { margin-top: 24px; padding-top: 16px; border-top: 1px solid #eee; color: #999; font-size: 12px; }
  .references { margin-top: 20px; padding: 16px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e0e0e0; }
  .references h2 { font-size: 15px; color: #555; border-left-color: #9e9e9e; margin-top: 0; }
  .references ul { margin: 0; }
  .references li { font-size: 12px; color: #666; margin: 4px 0; }
  a.src { color: #1a73e8; text-decoration: none; }
  a.src:hover { text-decoration: underline; }
  ul, ol { padding-left: 20px; }
  li { margin: 6px 0; line-height: 1.6; }
</style>
</head>
<body>
<div class="report">

<h1>{company_name} ({ticker}) 综合分析报告</h1>
<div class="meta">分析日期: {date} | 分析周期: 近7个交易日 | 市场: {market}</div>

<div class="summary">{一句话总结}</div>

<!-- 当日行情 — 黄色高亮区块，放在最前面 -->
<div class="daily-highlight">
<h2>当日行情 ({最近交易日日期})</h2>
<table>
  <tr><th>指标</th><th>数值</th></tr>
  <tr><td>开盘价</td><td>...</td></tr>
  <tr><td>最高 / 最低</td><td>... / ...</td></tr>
  <tr><td>收盘价</td><td>...</td></tr>
  <tr><td>当日涨跌</td><td><span class="up/down">+/-X.XX%</span> (±金额)</td></tr>
  <tr><td>成交量</td><td>XXX万股 (较前日 +/-XX%)</td></tr>
  <tr><td>盘中走势</td><td>简述日内走势特征</td></tr>
</table>
<p><strong>当日变动归因:</strong> 简要说明当日涨跌的直接原因</p>
</div>

<h2>一、7日股价概览</h2>
<table>
  <tr><th>指标</th><th>数值</th></tr>
  <tr><td>当前价格</td><td>¥/$XXX</td></tr>
  <tr><td>7日涨跌幅</td><td><span class="up/down">+/-X.XX%</span></td></tr>
  <tr><td>同期大盘</td><td>+/-X.XX%</td></tr>
  <tr><td>成交量趋势</td><td>放量/缩量/持平</td></tr>
  <tr><td>技术面信号</td><td>...</td></tr>
</table>

<h2>二、股价变动原因分析</h2>
<h3>直接驱动因素</h3>
<ol><li>...</li></ol>
<h3>行业传导因素</h3>
<ol><li>...</li></ol>
<h3>市场环境因素</h3>
<ol><li>...</li></ol>

<h2>三、近期重要新闻</h2>
<table>
  <tr><th>日期</th><th>事件</th><th>来源</th><th>影响</th></tr>
  <tr><td>...</td><td>...</td><td><a href="原文URL" class="src">来源名称</a></td><td><span class="tag tag-positive/negative/neutral">利好/利空/中性</span></td></tr>
</table>
<p>舆论倾向: <strong>正面/负面/中性</strong></p>

<h2>四、行业对比</h2>
<table>
  <tr><th>公司</th><th>7日涨跌</th><th>关键动态</th></tr>
  <tr><td>{company_name}</td><td>...</td><td>...</td></tr>
  <tr><td>竞对A</td><td>...</td><td>...</td></tr>
  <tr><td>竞对B</td><td>...</td><td>...</td></tr>
</table>

<h2>五、市场环境</h2>
<ul>
  <li>大盘趋势: ...</li>
  <li>市场情绪: Risk-on / Risk-off</li>
  <li>VIX: XX (低/正常/高/极高 波动)</li>
  <li>关键宏观因素: ...</li>
</ul>

<h2>六、趋势展望</h2>
<h3>短期 (1-2周)</h3>
<ul><li>...</li></ul>
<h3>中期 (1-3月)</h3>
<ul><li>...</li></ul>
<h3>主要风险</h3>
<div class="risk">
<ol><li>...</li></ol>
</div>

<div class="references">
<h2>参考来源</h2>
<!-- 将 5 个 Agent 返回的所有 Sources 链接按维度分组列出，不得省略，不得使用占位符 -->
<ul>
  <li><strong>股价与技术面</strong>
    <ul>
      <li><a href="URL" class="src">标题 — 来源</a></li>
    </ul>
  </li>
  <li><strong>新闻舆论</strong>
    <ul>
      <li><a href="URL" class="src">标题 — 来源</a></li>
    </ul>
  </li>
  <li><strong>行业对比</strong>
    <ul>
      <li><a href="URL" class="src">标题 — 来源</a></li>
    </ul>
  </li>
  <li><strong>市场环境</strong>
    <ul>
      <li><a href="URL" class="src">标题 — 来源</a></li>
    </ul>
  </li>
  <li><strong>公司公告 / 官网</strong>
    <ul>
      <li><a href="URL" class="src">标题 — 来源</a></li>
    </ul>
  </li>
</ul>
</div>

<div class="disclaimer">声明: 本报告由 AI 自动生成，仅供参考，不构成任何投资建议。投资有风险，决策需谨慎。</div>
</div>
</body>
</html>
```

**HTML 填写规则:**
- 涨跌幅为正时使用 `class="up"`（红色），为负时使用 `class="down"`（绿色）
- 新闻影响标签: 利好用 `tag-positive`，利空用 `tag-negative`，中性用 `tag-neutral`
- 将模板中的占位符替换为实际数据，删除注释
- 确保 HTML 完整可直接在浏览器中打开
- **「参考来源」区块必填**：将 5 个 Agent 返回结果末尾的所有 Sources 链接按维度分组填入；每条格式为 `<a href="原始URL" class="src">标题 — 来源网站</a>`；不得省略、不得保留占位符 URL
- 新闻表格的「来源」列须包含可点击原文链接（`<a href="原文URL" class="src">来源名称</a>`）

将报告保存为文件: `{company_name}-analysis-{date}.html`，保存在当前工作目录。

---

## Phase 4: 生成 PDF 报告

基于 Phase 3 生成的 HTML 文件，通过 Chrome headless 打印 PDF：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-sandbox \
  --print-to-pdf="$(pwd)/{company_name}-analysis-{date}.pdf" \
  --no-pdf-header-footer \
  "file://$(pwd)/{company_name}-analysis-{date}.html"
```

> **注意**: 如果系统没有 Chrome，可使用 `npx -y md-to-pdf "$(pwd)/{company_name}-analysis-{date}.html"` 作为备选方案。

最终输出两份文件：
- `./{company_name}-analysis-{date}.html` — HTML 版本（可在浏览器中打开）
- `./{company_name}-analysis-{date}.pdf` — PDF 版本（可直接分享）

---

## Error Handling

- **Agent 超时或失败**: 如果某个 Agent 未返回结果，在报告中标注该维度为"数据缺失"，其余维度照常分析
- **股票代码无法识别**: 提示用户确认代码或公司名称
- **akshare 未安装** (A股): 降级为纯 WebSearch 方式获取数据
- **官网无法访问**: 跳过官网抓取，依赖搜索引擎结果

## Notes

- 每个 Agent 的输出严格限制字数，防止主线程上下文溢出
- 综合分析阶段重在 **交叉关联**，而非简单罗列
- 因果分析应区分 "相关" 与 "因果"
- 趋势预测需明确标注不确定性
