# Harness Engine 架构（2026-07-16完整版）
> 基于 Harness Engineering + Loop Engineering 论文
> Agent = Model + Harness · Workflow优先于自由Agent

详见目录 `skills/bazi/harness-engine/`

## 核心教训（2026-07-16）
1. 数据源用 DS['年干'] 不用 DS['8字段'][0]
2. 十神阴阳：同阳=偏印/七杀，异阳=正印/正官
3. 身强弱4态：身强/中和/身弱/从弱，中和需独立规则
4. 文昌贵人 key='文昌贵人'（不是'文昌'）
5. L2状态按人隔离文件：pipeline_{姓名}.state
6. pre_tool_call_hook.py 是死文件（未在config.yaml引用），应删除
