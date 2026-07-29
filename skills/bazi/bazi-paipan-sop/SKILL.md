---
name: bazi-paipan-sop
description: 金鉴真人·八字排盘标准作业程序（SOP）。封装排盘全流程：技能加载顺序→排盘源头校验→引擎评分→分析报告→发布前校验→归档推库。2026-07-14重写。2026-07-27新增商业化架构转型参考。
tags: [八字, 排盘, SOP, 金鉴真人, pipeline, 物理化]
related_skills: [bazi-engine-workflow, bazi-foundation-analysis, bazi-report-template, bazi-platform-harness, bazi-task-dispatch, maker-checker-workflow, bazi-auto-verify, bazi-calibration, bazi-report-engine-audit, bazi-data-source]
---

# 金鉴真人·八字排盘SOP

> **核心变化（2026-07-27）**：从「Agent自主决定检索」改为「代码层前置强检索+校验门禁」。
> 完整架构文件在 `skills/bazi/bazi-foundation-analysis/architecture/` 目录下。
> - pre_retrieval_hook.py — 强制检索知识库注入上下文
> - structured_output.py — Instructor/Pydantic强制JSON输出
> - gatekeeper.py — 每步后硬性校验（不通过则驳回重做）
> - workflow_engine.py — 确定性状态图
> - pipeline.py — Prefect编排
> - langfuse_client.py — LangFuse观测+GoldenDataset

## Phase 0 — 系统就绪
（原有Phase 0-7内容保持不变，详见skills库旧版）

## Phase 1-7 通用流程
所有原有Phase（排盘/校验/报告/验证/归档）不变。
仅在Phase 4中增加一步：调用pre_retrieval_hook.retrieve()强制注入知识。
仅在Phase 5中增加栅栏：gatekeeper结构化输出校验。

## Phase 0.5 — 三决断（新增·2026-07-27）
所有分析的第一步不是全面报告，而是"先验过去，再看当下选择"。
1. 根据八字给出3条可验证的过去判断（覆盖三个不同阶段/领域）
2. 标注"条1/条2/条3，您可以对照看看"
3. 等用户确认后再进入详细分析
参考：products/three-verifications-methodology.md

## 多流派分析模式（新增·2026-07-27）
可选：同时输出子平/盲派/九龙三个流派的简版三决断。
用户反馈哪个流派的判断最准 → 以该流派为主体做深度分析。
参考：products/multi-school-flow.md

## 文件归档铁律（2026-07-27 老板校准·两次修正）
- 人物报告 → `02-人物档案/编号-姓名/`
- 外部素材 → `00-原始素材/`
- 体系化文件（SOP/代码/配置）→ `04-金鉴真人体系/`
- 架构代码 → `04-金鉴真人体系/architecture/`
- 两仓库分工：weiwuji = 知识库（报告/知识/人物档案），jinjian = 程序（SOP/代码/引擎）
- 禁止混放·两次犯错后已固化此规则
