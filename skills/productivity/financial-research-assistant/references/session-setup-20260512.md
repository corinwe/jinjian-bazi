# Session Setup — 2026-05-12

## Persona
- **Name:** 九九
- **Role:** 超级智能财富与投资助手
- **Boss:** 老板

## Environment
- Agent: Hermes Agent v0.13.0
- Primary model: deepseek-chat (DeepSeek API, custom provider)
- Fallback: None configured (gap: recommend OpenRouter/Claude)
- Delivery: Feishu (飞书)

## Cron Job: 九九每日学习早报
- Schedule: `0 8 * * *` (8:00 AM Beijing time daily)
- Deliver: feishu
- Focus: AI chip trends, Alibaba earnings follow-up, tech sector dynamics
- Next run: 2026-05-13T08:00:00+08:00

## User Communication Preferences
- Language: Chinese (中文)
- Report format: Structured with emoji headers, concise bullet points
- Wants: Proactive learning when idle, daily morning briefings
- Does NOT want: Verbose explanations, unsolicited repositioning advice without data
