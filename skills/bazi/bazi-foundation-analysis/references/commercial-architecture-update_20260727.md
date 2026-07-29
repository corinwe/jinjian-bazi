# 商业化架构转型（2026-07-27）
> 从"Agent自主决定检索"改为"代码层前置强检索+校验门禁"
> 文档：architecture/目录下6个Python文件

## 核心变化
之前：Agent自己决定查不查 → 经常"忘记"
现在：代码层强制先查Chroma → 知识硬注入 → LLM仅推理 → 校验门禁拦截

## 六层架构
| 层 | 实现 | 文件 |
|:---|:-----|:-----|
| 知识层 | Chroma向量库(220块) | data/chroma_db/ |
| 前置检索 | 代码层无条件先查 | pre_retrieval_hook.py |
| 结构化输出 | Instructor+Pydantic强制JSON | structured_output.py |
| 校验门禁 | 每步全量校验+重试 | gatekeeper.py |
| 工作流引擎 | 确定性状态图 | workflow_engine.py |
| 观测评估 | LangFuse追踪+Golden Dataset | langfuse_client.py |

## 三决断流程（所有分析起点）
先验过去→3条可验证判断→用户确认→再深度分析
参考：products/flow.md, products/three-verifications-methodology.md

## 多流派分析
子平/盲派/九龙三流派同步输出简版→用户选准的→该流派深度分析
参考：products/multi-school.md

## 文件归档铁律
- 人物报告 → weiwuji/02-人物档案/编号-姓名/
- 体系文件(SOP/代码) → weiwuji/04-金鉴真人体系/
- 架构代码 → 04-金鉴真人体系/architecture/
- 两仓库: weiwuji=知识库, jinjian=程序
