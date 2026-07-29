# 商业化架构集成指南（2026-07-27）

## 引擎 vs 工作流引擎 的关系

`bazi-engine-workflow` 是**引擎层**（确定性Python计算）：
- paipan.py / shen_qiang_ruo.py / ge_ju.py / da_yun.py 等
- 输出结构化JSON（排盘/身强弱/格局/喜用/十神/大运）
- 这些数据是"原始引擎数据"，不可直接作为最终报告

`workflow_engine_v2.py`（architecture/下）是**编排层**：
- 调用引擎获取确定性数据
- 再通过Chroma检索相关知识
- 最后LLM仅做叙事合成（不得重新计算）

## 调用链

```
bazi-engine-workflow（引擎计算）
  → 输出engine.json（确定性数据）
  → workflow_engine_v2.node_engine() 读取engine.json
  → workflow_engine_v2.node_retrieve() 从Chroma检索知识
  → workflow_engine_v2.node_reasoning() LLM叙事合成（Instructor强制JSON）
  → workflow_engine_v2.node_gatekeeper() 校验门禁
  → workflow_engine_v2.node_output() 21§格式输出
```

## 铁律
- 引擎只做计算，不做叙事
- 工作流引擎只做编排，不做计算
- LLM只做叙事，不做计算和检索决定
