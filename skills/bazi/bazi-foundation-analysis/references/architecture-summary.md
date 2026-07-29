# 商业化架构概要（2026-07-29 构建完成）
参考架构代码：`architecture/` 目录下的6个Python文件

## 核心原则
确定性的东西交给代码，前置注入，不靠大模型。
大模型仅在节点上做叙事合成（基于引擎数据+知识库规则）。

## 架构全景

```
[输入] → TaskDispatcher(路由+session隔离)
       → node_input_validate(Pre-hook校验)
       → node_engine(引擎排盘+身强弱+格局+喜用)
       → node_retrieve(Chroma强制检索)
       → node_llm_reason(Instructor强制结构化输出)
       → node_gatekeeper(校验门禁)
          ├─ 通过 → node_output(输出)
          ├─ 不通过 → retry(最多3次,错误反馈注入)
          └─ 3次不过 → human_intervention(转人工)
```

## 各层文件映射

| 层次 | 文件 | 职责 |
|:-----|:-----|:------|
| 触发层 | `trigger_layer.py` | 路由/场景隔离/工具白名单/上下文隔离 |
| 引擎层 | `projects/bazi-platform/engine/paipan.py` | 排盘计算 |
| | `engine/shen_qiang_ruo.py` | 身强弱评分 |
| | `engine/ge_ju.py` | 格局+喜用判定 |
| 知识层 | `architecture/pre_retrieval_hook.py` | Chroma前置检索 |
| 合成层 | `architecture/workflow_engine_v2.py` | LangGraph状态图+LLM叙事 |
| 校验层 | `architecture/gatekeeper.py` | Instructor+Pydantic校验 |
| 观测层 | `architecture/langfuse_client.py` | LangFuse+Golden Dataset |

## 运行时环境变量

| 变量 | 用途 | 来源 |
|:-----|:-----|:------|
| `DEEPSEEK_API_KEY` | DeepSeek LLM调用 | config.yaml |
| `LLM_MODEL` | 模型名 | config.yaml (默认 deepseek-chat) |

## 调用方式
```python
from workflow_engine_v2 import run_analysis_pipeline
result = run_analysis_pipeline(
    user_query='...',
    task_type='事业',
    birth_year=1980, birth_month=8, birth_day=6,
    birth_hour=6, gender='男'
)
print(result['final_output'])
```
