---
name: maker-checker-workflow
description: Maker/Checker循环 — 分析报告的双人校验工作流
tags: [bazi, maker, checker, review, quality]
related_skills:
  - bazi-paipan-sop
  - bazi-calibration
  - bazi-report-template
---

# Maker/Checker 工作流

> **来源**: SOUL.md Sub-Agent分工体系 + HERMES.md Maker/Checker铁律
> 用于SOP Phase 4.5 — 确保分析报告内容质量

## §1. 核心原则

```
Maker = 内容撰写人（写分析的人）
Checker = 对抗性审查人（找漏洞的人）
两人必须不同 — 同一个人不能既写又审
```

## §2. 检查维度（五轴）

| 维度 | 检查项 | 方法 |
|:----|:-------|:-----|
| **正确性** | 格局判定、身强弱、喜用神 | 对比引擎JSON + 规则行号 |
| **一致性** | 数据与引擎一致，无自创 | grep提取数字对比JSON |
| **完整性** | 5项必含内容全部存在 | 逐项过checklist |
| **可读性** | 语言通顺、无模板话术 | 眼扫一遍 |
| **格式** | 排盘格式正确、段落间距一致 | 移动端预览 |

## §3. Maker/Checker 执行流程

```
Maker:
  ① 加载所有技能（Phase 4.1）
  ② 逐§写分析（按Phase 4.3A映射）
  ③ 每写完一§打勾✅

Checker（Maker之后）:
  ① 从报告中提取所有数字/十神/五行数据
  ② 对比引擎JSON中的对应字段
  ③ 逐项确认一致
  ④ 不一致 → 标记并退回Maker改
  ⑤ 全部一致 → 标记✅

完成条件 → Phase 5发布前校验
```

## §4. 常见Checker发现的问题

| 问题 | 严重度 | 处理方法 |
|:-----|:------|:---------|
| 分数写错（记忆偏差） | 🔴 | 以JSON为准重写 |
| 格局命名错误 | 🔴 | 查fortune-analysis §6 7步法重判 |
| 缺少强制内容 | 🔴 | 补充后重审 |
| 模板话术 | 🟡 | 替换为具体数据描述 |
| 排版不一致 | 🟢 | 调整格式 |
