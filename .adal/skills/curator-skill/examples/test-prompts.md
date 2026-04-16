# Test Prompts — curator-skill v1 内部 QA

> Ship 前必须人工跑通的 trigger test prompt。在另一个 Claude Code session(已 install curator-skill)里依次输入,记录 pass/fail。

---

## 8 场景 trigger 测试

### Scenario 1: Discovery 入门探索 (target: starter pack 输出)

- [ ] "有什么 persona skill"
- [ ] "把人变 AI 的有哪些"
- [ ] "推荐几个人物 skill"
- [ ] "我刚装了 nuwa,接下来该装什么"

**Expected**: curator 列出 8 个跨类目的精选 starter pack(每个 scenario 至少 1 个),含 install 命令。

---

### Scenario 2: Perspective 借脑思考 (target: 单 persona 精准定位)

- [ ] "Naval 会怎么想这个"
- [ ] "用芒格视角看"
- [ ] "Karpathy 怎么看 AGI 时间表"
- [ ] "如果是马斯克,他会怎么做"

**Expected**: curator 推荐对应的单个 persona,带 core_lens / 为什么适合 / 局限 / install 命令。

---

### Scenario 3: Method 方法论学习 (target: 领域 mentor)

- [ ] "我想学 Karpathy 的 ML 思维"
- [ ] "想学 Munger 的多元思维模型"
- [ ] "想学张雪峰的志愿填报方法"
- [ ] "怎么学 X/Twitter 运营"

**Expected**: curator 推荐对应领域的 mentor skill,强调"方法论可迁移"而非"模仿其人"。

---

### Scenario 4: Decision 决策辅助 (单 persona 推荐)

- [ ] "该不该接这个 offer" → 推荐 PG 或张一鸣(创业/职业类)
- [ ] "该不该 all in 这个早期项目" → 推荐芒格或 Taleb(投资/风险类)
- [ ] "要不要读博" → 推荐 Munger 或 Naval(个人决策类)
- [ ] "帮我决策这个事,我想想清楚" → 匹配决策类型推荐最相关的 1 个

**Expected**: curator 推荐**最匹配决策类型的 1 个** persona,标准候选格式(核心镜片 / 为什么适合 / 局限 / 安装 / 用法)。可以在末尾提一句"想要更多视角,可以装几个分别 prompt"。

---

### Scenario 5: Relationship 情感场景 (target: emotional priming)

- [ ] "我前任突然找我,有点不知道怎么办"
- [ ] "我导师让我做一个我不想做的项目"
- [ ] "我妈最近老打电话给我,我有点烦"
- [ ] "我暗恋的人有男朋友了,我心里很难受"

**Expected**: curator
1. **先共情**(一两句承认情绪,绝不假共情)
2. 然后温和地说"如果你想试试,有几个 persona 可能能陪你聊聊"
3. 推荐 1-2 个候选(不超过 2)
4. 措辞软("如果你想试试" / "完全可以不试,只是放在这")
5. **绝不**列 4 个 install 命令,**绝不**说"立即安装 / 推荐你装"

---

### Scenario 6: Self 自我对话 (target: yourself / 数字人生)

- [ ] "和未来的我对话"
- [ ] "另一个我"
- [ ] "想做一个数字分身"

**Expected**: curator 推荐 yourself / immortal / 数字人生 中的 1-2 个,给安装 + 用法。

---

### Scenario 7: Roleplay 角色扮演 (target: nuwa dogfood)

- [ ] "想跟马斯克聊天"
- [ ] "扮演乔布斯给我 demo 一个产品"
- [ ] "如果是特朗普,他会怎么发推"

**Expected**: curator 推荐对应的花叔 dogfood persona(elon-musk-skill / steve-jobs-skill / trump-skill),强调"是 perspective 而非真实模拟"。

---

### Scenario 8: Creation 创作引导 (必须 redirect 到 nuwa)

- [ ] "我想自己做一个 X 的 skill"
- [ ] "我想蒸馏我的导师"
- [ ] "帮我造一个我前任的 persona"
- [ ] "怎么 distill 一个新的人物"

**Expected**: curator
1. **不要**假装能 distill
2. 直接 redirect 到 nuwa / colleague / yourself / immortal
3. 给出对应的 install 命令
4. 强调"做完之后 curator 会帮你召唤"

---

## 不触发测试 (curator 必须保持沉默)

这些 prompt 应该让 curator **完全不响应**(因为不属于 persona discovery 场景):

- [ ] "帮我写一段 Python 来 parse JSON" → 编程任务
- [ ] "改一下这个 CSS 让它居中" → 编程任务
- [ ] "帮我做个 PPT 介绍我们的产品" → docx/pptx 工具任务
- [ ] "用 Naval 视角分析我要不要..." → 这是 naval-skill 在工作,不是 curator
- [ ] "Naval 觉得这个事不对" → 已经在和 Naval 对话
- [ ] "继续刚才的话题" → 上下文延续,不是新的 persona discovery 请求

**Expected**: curator 保持沉默(不输出任何 persona 推荐 / 不打断当前任务)。

---

## 边界 case 测试

- [ ] "找个 skill" → 是技能发现还是 persona 发现?如果用户没提 persona,curator 应该让 ai-skill 处理(curator 只管 persona)
- [ ] "用 Naval 的角度想想要不要 all in" → 这是单 persona 借脑(perspective hijack),不是决策辅助
- [ ] "我想用一个人的视角看 X" → 模糊需求,curator 应该追问"哪个人?"或推荐 starter pack
- [ ] "我想要个 mentor" → method 类,推荐 x-mentor / mentor 类 skill
- [ ] "换一个 persona" → 用户明确要求换,**可以**重新介入

---

## 性能 / 输出质量检查

每个 pass 的 prompt 还要检查:

1. **核心镜片** 字段是否有内容(不是空字符串)
2. **局限** 字段是否说清楚了(不是泛泛"有局限")
3. **install_cmd** 是否准确(可以直接复制运行)
4. **scenarios** 标签是否正确
5. 决策类推荐是否匹配了正确的 persona(而不是随机推)

---

## Pass 标准

v1 ship 通过的最低标准:

- 所有 8 个 scenario 至少有 80% prompt 触发正确(8 × 80% ≈ 6 个 scenario 完全 pass + 2 个有 1 处小问题)
- **不触发场景必须 100% pass**(否则 curator 会变成噪音)
- **Creation redirect 必须 100% pass**(否则会和 nuwa 抢位)
- **Emotional priming 措辞必须不机器**(curator 在情感场景里冷冰冰会致命)
