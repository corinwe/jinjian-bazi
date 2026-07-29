# 商业化架构参考

## 架构文件
本技能目录下 `architecture/` 目录包含完整的六层商业化架构：

| 文件 | 用途 | 技术栈 |
|:-----|:-----|:-------|
| pre_retrieval_hook.py | 前置强制检索→Chroma知识库 | chromadb |
| structured_output.py | Instructor+Pydantic模型定义 | instructor, pydantic |
| gatekeeper.py | 输出校验门禁（全量） | pydantic |
| workflow_engine.py | LangGraph确定性状态图 | langgraph |
| pipeline.py | Prefect任务编排 | prefect |
| langfuse_client.py | LangFuse观测+Golden Dataset | langfuse |

## 架构原则
1. **知识向量化** — SKILL.md §35-§40拆分为220个知识块存入Chroma
2. **前置检索** — Agent无法跳过，代码层无条件执行
3. **结构化输出** — 用Instructor强制LLM输出固定JSON结构
4. **校验门禁** — 不通过则驳回（最多3次重试）
5. **上下文隔离** — 每任务销毁，不被前任务污染
6. **观测评估** — LangFuse全量追踪+每日自动评估

详见 `architecture/` 目录和 `architecture/金鉴真人_商业化架构改进方案_20260727.md`
