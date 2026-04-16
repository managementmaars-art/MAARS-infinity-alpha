---
name: wechat-daily-report
description: 基于本机已登录微信的本地数据库生成微信群聊日报长图。用于用户要求“生成某个微信群的今日日报/昨日报/群聊总结长图/聊天日报图片”这类任务时。流程包含：检查并刷新本地微信解密数据、选择群聊、分析消息、生成 AI 内容、输出手机端 PNG 长图。
---

# 微信群聊日报生成 Skill

按下面顺序执行：

```bash
python scripts/setup_check.py --ensure-decryptor
python scripts/decrypt_wechat.py
python scripts/list_wechat_groups.py
python scripts/analyze_chat.py --chatroom "<群名或 chatroom id>" --date 2026-04-11 --output-stats stats.json --output-text simplified_chat.txt
python scripts/generate_report.py --stats stats.json --ai-content ai_content.json --output report.png --clean-temp
```

规则：
- 输出目标始终是 `.png` 长图，不要停在 `.html`
- 不要调用第三方聊天导出 API，只使用本地微信数据库与本地解密流程
- `analyze_chat.py` 默认会在分析前再次刷新解密结果，不需要额外重复说明
- 运行产物默认写到当前项目目录
- 先用 `list_wechat_groups.py` 确认群名，再执行分析

AI 内容生成时，读取 [`references/ai_prompt.md`](D:/wechat-daily-report/references/ai_prompt.md)。
