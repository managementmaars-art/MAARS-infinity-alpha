# 图鉴.skill / curator.skill

> 「蒸馏了那么多人，该找谁？」

```bash
npx skills add Aar0nPB/curator-skill -g -y
```

## 这是什么

这是一个可以在你跟 AI 对话的时候智能推荐、召唤合适人格的 persona skill 图鉴。

你可能装了好几个 persona skill（Naval、芒格、乔布斯、同事、前任...），但平时用的时候不一定记得该调哪个。curator 根据你说的话，自动从 30 个跨作者 persona skill 里匹配最合适的那个。

## 装完之后

在 Claude Code / Cursor / Codex CLI 里直接说话就行：

> **「Naval 会怎么看这件事？」**
>
> → 智能匹配到 naval-skill（基于 30+ 篇著作蒸馏的完整认知框架），AI 给你推荐，许可后一键安装

> **「有什么好玩的 persona skill？」**
>
> → 按类别展示：大佬 17 个 · 关系延续 10 个 · 自我对话 3 个

> **「我前任突然找我了...」**
>
> → 先听你说完，再轻推荐 ex-skill

## 收录

| 类别     | 数量 | 包含                                                                                                                                               |
| -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **大佬** | 17   | Naval · 芒格 · 塔勒布 · Paul Graham · Karpathy · Ilya · 费曼 · MrBeast · 乔布斯 · 马斯克 · Trump · 张一鸣 · 张雪峰 · 户晨风 · 巴菲特 · 毛选 · 求是 |
| **熟人** | 10   | 同事 · 前任(titanwings) · 前任(小蛮) · 暗恋 · 父母 · 师兄 · 导师 · 老板 · 永生 · 重逢                                                              |
| **自我** | 3    | 自己 · 永生 · 数字人生                                                                                                                             |

完整目录见 [`persona-recommendations.json`](./persona-recommendations.json)。

精选库持续更新。

## 生态分工

curator 只做发现和推荐。其他的事有更好的工具：

- **想蒸馏新 persona** → [女娲 nuwa-skill](https://github.com/alchaincyf/nuwa-skill)
- **想做同事/朋友/亲人角色** → [同事 colleague-skill](https://github.com/titanwings/colleague-skill)
- **想看整个生态全貌** → [dot-skill Gallery](https://titanwings.github.io/colleague-skill-site/gallery/)

## 安装

```bash
npx skills add Aar0nPB/curator-skill -g -y
```

支持 Claude Code · Cursor · Codex CLI · Gemini CLI · OpenCode 等 12+ 个 agent runtime。

## 致谢

- [titanwings](https://github.com/titanwings) — colleague-skill, dot-skill
- [alchaincyf](https://github.com/alchaincyf) — nuwa-skill + persona skills
- [therealXiaomanChu](https://github.com/therealXiaomanChu) · [notdog1998](https://github.com/notdog1998) · [xiaoheizi8](https://github.com/xiaoheizi8) · [agenmod](https://github.com/agenmod)

## License

[MIT](./LICENSE)

---

# curator.skill / 图鉴.skill (English)

> "You've distilled so many minds — but which one do you need right now?"

```bash
npx skills add Aar0nPB/curator-skill -g -y
```

## What is this

A persona skill router that intelligently recommends the right persona when you're talking to your AI agent.

You probably have several persona skills installed (Naval, Munger, Steve Jobs, colleague, ex...) but don't always remember which one to use. curator matches your words to the best fit from 30 cross-author persona skills.

## After installing

Just talk in Claude Code / Cursor / Codex CLI:

> **"What would Naval think about this?"**
>
> → Matches naval-skill (full cognitive framework distilled from 30+ writings), recommends and installs with your permission

> **"What persona skills are out there?"**
>
> → Shows by category: Thought Leaders 17 · Relationships 10 · Self 3

> **"My ex just reached out..."**
>
> → Listens first, then gently recommends ex-skill

## Collection

| Category          | Count | Includes                                                                                                                                                                                |
| ----------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Adepts**        | 17    | Naval · Munger · Taleb · Paul Graham · Karpathy · Ilya · Feynman · MrBeast · Steve Jobs · Elon Musk · Trump · Zhang Yiming · Zhang Xuefeng · Hu Chenfeng · Buffett · Mao Xuan · Qiu Shi |
| **Relationships** | 10    | Colleague · Ex(titanwings) · Ex(XiaomanChu) · Crush · Parents · Senior · Mentor · Boss · Immortal · Reunion                                                                             |
| **Self**          | 3     | Yourself · Immortal · Digital Life                                                                                                                                                      |

Full catalog: [`persona-recommendations.json`](./persona-recommendations.json). Continuously updated.

## Ecosystem

curator only does discovery and recommendation. For everything else, use the right tool:

- **Distill a new persona** → [Nuwa nuwa-skill](https://github.com/alchaincyf/nuwa-skill)
- **Create colleague/friend/family roles** → [Colleague colleague-skill](https://github.com/titanwings/colleague-skill)
- **Browse the full ecosystem** → [dot-skill Gallery](https://titanwings.github.io/colleague-skill-site/gallery/)

## Install

```bash
npx skills add Aar0nPB/curator-skill -g -y
```

Supports Claude Code · Cursor · Codex CLI · Gemini CLI · OpenCode and 12+ agent runtimes.

## License

[MIT](./LICENSE)
