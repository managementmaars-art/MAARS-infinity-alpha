---
name: hundun
description: 提及混沌课程、课程学习、方法论、思维模型、课程检索、课程文稿提炼时使用；提炼价值点/激发创意/总结卖点/产品&服务定价/挖掘创业机会时使用；问及泛商业决策类问题时使用。
---

# 混沌课程学习与创新工具

用这个技能处理两类任务：

1. 用户明确提及混沌课程时，按搜课、筛课、学习路径、读课流程执行
2. 用户在问商业创新问题但没有明确要课程时，优先匹配对应创新工具并执行

`SKILL.md` 只负责判断任务类型、共享约束、脚本索引和 reference 导航；课程流程细节集中在 `course-workflow.md`。

## 执行总则

- 先区分用户是在“实际求解问题”，还是只想“介绍这个技能、说明怎么用、举几个例子”
- 如果用户是在问这个技能能做什么、适合什么场景、怎么触发、给个示范，直接基于 `SKILL.md` 说明，不要跑脚本
- 所有脚本和资料路径都相对当前技能目录解析，优先使用 `./scripts/...`、`./references/...`
- 看到 `~/.hdxy_config` 只代表“存在配置”；只有真实鉴权成功后，才能对用户说“现在可以直接查”
- 课程或文稿脚本调用失败时，严禁回退到自行从 `hundun.cn` 或其他网页页面检索课程信息、文稿内容或老师信息
- 读取课程文稿时，只在当前执行链路里临时使用；不要把原始文稿保存到本地文件、缓存文本或中间产物
- 对外提到这个技能时，始终展示为“混沌”，不要对用户说“hundun 技能”

## 适用场景

- 用户说“帮我找最适合这个问题的课”
- 用户说“帮我看看混沌有没有讲这个主题的课”
- 用户已经有一门目标课程，想直接提炼最有用的结论
- 用户想按关键词或课程体系检索混沌课程
- 用户明确提到混沌课程、课程体系、学习路径
- 用户想把一句介绍说得更有记忆点、更有传播力
- 用户想找新点子、新方向、新组合，但暂时没有破题路径
- 用户产品同质化、卖点不清、转化低，想重构差异化价值
- 用户不知道该怎么定价、涨价，或觉得现有定价逻辑站不住
- 用户想切入一个热门赛道，但不想和大公司正面竞争，想找错位切口

## 不适用场景

- 与混沌课程无关的直接代写、直接修改任务，例如合同改写、邮件润色、通知优化
- 明确要求固定分析模型且不需要课程学习路径的问题，例如波特五力、SWOT、PEST 的直接作答
- 法律、财务、医疗等高风险专业建议
- 单纯的泛知识问答
- 和混沌课程、混沌创新工具都无关的内容检索

## 路由规则

主路由固定按下面顺序判定：

1. 先看用户是否明确提及混沌课程、搜课、读课、课程学习、课程体系、课程文稿；命中则直接走课程学习路由
2. 如果没有明确提及课程，再按场景描述匹配最贴近的创新工具；命中则走创新工具路由

默认只选一条主路由执行，让当前回答围绕一个主任务展开。

### 1. 课程学习路由

当用户明确要找课、筛课、读课，或明确提到混沌课程、混沌学习、课程体系、课程文稿、学习路径时，走课程学习路由。

- 只要用户明确提及混沌课程，就按课程任务处理
- 先根据 [auth-and-troubleshooting.md](./references/auth-and-troubleshooting.md) 完成用户登录流程
- 进入课程学习路由后，直接判断当前子任务是搜课、课程推荐、学习路径，还是单课解读
- 课程流程统一读取 [course-workflow.md](./references/course-workflow.md)，推荐、搜课、学习路径、单课解读都按这份流程执行

### 2. 创新工具路由

当用户没有明确提及混沌课程，但希望马上把某个商业问题拆开、重构、澄清或找到方向时，先尝试匹配创新工具路由。

按下面的映射选一个最贴近的工具流程文件：

- 想把一句介绍说得更有价值、更有记忆点：读 [value-proposition-one-liner.md](./references/innovation-tools/value-proposition-one-liner.md)
- 想找新点子、新方向、新组合：读 [idea-exploder.md](./references/innovation-tools/idea-exploder.md)
- 产品没卖点、太同质化、转化低：读 [selling-point-innovator.md](./references/innovation-tools/selling-point-innovator.md)
- 不知道怎么定价、涨价、构建价格逻辑：读 [pricing-reframer.md](./references/innovation-tools/pricing-reframer.md)
- 想进入红海市场但要找错位切口：读 [asymmetric-entry-finder.md](./references/innovation-tools/asymmetric-entry-finder.md)

## 输出要求

- 课程推荐重点解释“为什么这门课适合这个问题”
- 课程解读重点提炼课程中的方法论、模型和步骤，并直接落到可用动作

## 脚本目录

保留完整脚本索引，方便在不额外扫目录的情况下快速判断可调用能力：

- `scripts/run.ps1`：Windows 下统一入口
- `scripts/version_check.sh` / `scripts/version_check.ps1`：版本检查
- `scripts/set_api_key.sh` / `scripts/set_api_key.ps1`：写入用户发来的 `hd_sk_` 密钥
- `scripts/get_skill_patch.sh` / `scripts/get_skill_patch.ps1`：获取服务端 Skill 补全内容
- `scripts/search_courses.sh` / `scripts/search_courses.ps1`：关键字搜课
- `scripts/get_trees.sh` / `scripts/get_trees.ps1`：获取课程体系树
- `scripts/get_courses_by_tree.sh` / `scripts/get_courses_by_tree.ps1`：按体系查课程
- `scripts/get_script_version.sh` / `scripts/get_script_version.ps1`：获取文稿版本
- `scripts/get_script.sh` / `scripts/get_script.ps1`：获取课程文稿正文
- `scripts/intent_collect.sh` / `scripts/intent_collect.ps1`：用户意图收集
- `scripts/_common.sh` / `scripts/_common.ps1`：脚本公共能力
- `scripts/_decompress.py`：文稿解压支持
- `scripts/_decrypt_script_url.py`：文稿链接解密支持

## 资料导航

- [auth-and-troubleshooting.md](./references/auth-and-troubleshooting.md)：API Key、初始化、报错处理、常见故障
- [course-workflow.md](./references/course-workflow.md)：课程学习标准流程，包含搜课、推荐、学习路径和单课解读
- `references/innovation-tools/*.md`：创新工具路由下的专用流程
