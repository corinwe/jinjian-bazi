# 2026-07-27 新增文件索引
当加载此skill时，以下新文件可用：

## 产品设计
- `products/pricing.md` — 产品定价分层（免费三决断+付费深度报告）
- `products/flow.md` — 分析流程设计（先验过去→再看选择）
- `products/multi-school.md` — 多流派分析模式（子平/盲派/九龙）
- `products/three-verifications-methodology.md` — 三决断分析方法

## 商业化架构
- `architecture/pre_retrieval_hook.py` — 前置强制检索（Chroma知识库）
- `architecture/structured_output.py` — Instructor/Pydantic结构化输出模型
- `architecture/gatekeeper.py` — 校验门禁（全量硬性校验）
- `architecture/workflow_engine.py` — LangGraph确定性工作流（集成真实LLM API）
- `architecture/pipeline.py` — Prefect任务编排
- `architecture/langfuse_client.py` — LangFuse观测+GoldenDataset评估
- `architecture/run_test.py` — 全链路端到端测试脚本
- `architecture/金鉴真人_商业化架构改进方案_20260727.md` — 完整架构方案文档

## 墓库理论
- `references/mu-ku-theory.md` — 墓库理论完整：五行定库性/日主定十神/旺衰定喜忌/喜忌定吉凶
- `references/section37_8-to-section40-crossref.md` — §37.8→§40交叉引用

## 档案归档铁规
- `bazi-paipan-sop/SKILL.md` 末尾新增「文件归档铁律」段落
- `bazi-paipan-sop/references/file-organization-rules.md` — 完整文件归档规则

## 仓库分工
- **weiwuji-knowledge-base** = 知识库（报告/人物档案/命理知识）
- **jinjian-zhenren** = 程序代码（SOP/引擎/架构代码）
- 人物报告放 `02-人物档案/编号-姓名/`
- 外部素材放 `00-原始素材/`
