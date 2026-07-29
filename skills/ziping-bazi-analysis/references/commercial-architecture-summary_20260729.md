# 商业化架构总结（2026-07-29）
与 `bazi-paipan-sop` 配合使用

## 架构核心原则
LLM专用作叙事引擎，不做计算、不做检索、不做判断。
引擎(代码) + 向量库(知识) + LLM(叙事) + 校验门禁(代码)。

## 分层
1. 引擎计算层：paipan.py, shen_qiang_ruo.py, ge_ju.py
2. 检索层：pre_retrieval_hook.py → Chroma (220知识块)
3. 叙事层：workflow_engine.py → DeepSeek LLM (仅合成)
4. 校验层：gatekeeper.py → Instructor/Pydantic (全量拦截)

## 三决断(免费) + 深度报告(付费)
免费：三决断+基本盘
付费：六体系+条件喜忌+分线断法+大运流年+风险日历
