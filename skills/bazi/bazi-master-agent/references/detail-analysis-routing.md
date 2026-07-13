# detail_analysis 路由与消费说明

## 架构定位

`detail_analysis` 是规则引擎与自然语言报告之间的**确定性桥梁**。所有21个§的结构化JSON数据通过 `attach_detail_analysis()` 自动附加 `detail_analysis` 字段。

## 路由节点

```
pipeline_v5.py run_pipeline()
  └─ result = run_v5(...)                         # 21§结构化JSON
  └─ result = attach_detail_analysis(result)       # → 附加detail_analysis
  └─ report = generate_deep_report(result, ...)     # → 消费detail_analysis
```

## 关键文件

| 文件 | 路径 | 职责 |
|:-----|:-----|:------|
| `_gen_detail_analysis.py` | engine/ | 为每个§生成规则分析文本（~24K代码·21个生成函数） |
| `generate_deep_report.py` | engine/ | 消费detil_analysis并展开为1500+行完整报告 |
| `pipeline_v5.py` | engine/ | 调用链编排 `run_v5 → attach_detail_analysis` |

## 使用约束

1. 任何时候生成报告必须经过`attach_detail_analysis()`后处理
2. 不要跳过detail_analysis直接让LLM写分析（会导致不稳定）
3. 如需新增§的分析文本，在`_gen_detail_analysis.py`中加对应的函数
