# detail_analysis 架构文档（2026-06-27）

## 为什么需要detail_analysis

引擎 `pipeline_v5.py` 的 `run_v5()` 输出21§结构化JSON——每个§包含分数、标签、明细等确定性计算数据。但：

- 人类看不懂 `constitution: "中等"` 是什么意思
- 之前的 `generate_deep_report.py` v1.0-v2.0 用硬编码代码展开数据，但每个§的展开逻辑分散且容易遗忘
- LLM润色方案不稳定（同八字不同文本，不可商业化）

**solution**：在规则引擎内加一个后处理模块 `_gen_detail_analysis.py`，把引擎数据翻译为基于规则的分析文本。

## 架构

```
run_pipeline() 中调用 flow:
  result = run_v5(...)           # 21§结构化JSON
  result = attach_detail_analysis(result)  # 为每个§加detail_analysis字段
  # result现在包含: sec_1_overview["detail_analysis"] = "..." 等21个
  report = generate_deep_report(pipeline_output, name, gender)  # 消费所有detail_analysis
```

## 关键设计决策

### 为什么在pipeline_v5.py里而不是单独模块？
`attach_detail_analysis()` 作为 `run_pipeline()` 的后处理步骤，与引擎计算在同一进程完成。这样保证：
- 零额外依赖和网络调用
- 与引擎数据完全一致（没有版本漂移）
- 可以被下游统一消费（API JSON和深度报告都包含 detail_analysis）

### 为什么不用LLM生成？
LLM的稳定性不足以支撑商业化。代码生成的 `detail_analysis` 即使文本较短，也保证：
- 同八字→同文本（确定性）
- 规则标注精确到行号
- 数据映射100%匹配引擎计算

### 为什么有些detail_analysis很短？
因为 `_gen_detail_analysis.py` 是**后处理**——它只能基于引擎模块已有的数据展开。如果引擎模块输出只有 `constitution: "中等"`，后处理只能写一行。要提升文本厚度，需要：
1. 先让引擎模块（如 `comprehensive_v2.py`）输出更多结构化字段
2. 然后在 `_gen_detail_analysis.py` 对应函数中展开

## 所有21个函数的规范

每个 `_xxx_detail(result) -> str` 函数：
- 输入：完整的 `result` dict（包含全部21§）
- 输出：多行字符串（每行一条规则分析）
- 必须包含：【规则来源标注】+【引擎数据映射】+【判定结论】

## 验证方法

```python
from pipeline_v5 import run_pipeline
result = run_pipeline('家主', '男', '癸', '未', '己', '巳', '庚', '申', '壬', '子', birth_year=1980)
r = result['result']

# 检查21个§的detail_analysis
sections = ['sec_1_overview','sec_2_ge_ju','sec_3_shen_qiang_ruo','sec_4_xi_yong',
            'sec_5_zai_huo','sec_6_character','sec_7_appearance','sec_8_wealth',
            'sec_9_property','sec_10_career','sec_11_education','sec_12_marriage',
            'sec_13_children','sec_14_health','sec_15_family','sec_16_events',
            'sec_17_da_yun_detail','sec_18_verdicts','sec_19_overall','sec_20_wu_xing_advice','sec_21_advice']
ok = sum(1 for k in sections if r.get(k,{}).get('detail_analysis',''))
# verdicts特殊处理
if r.get('sec_18_verdicts_detail',{}).get('detail_analysis',''):
    ok += 1
print(f'{ok}/21')
assert ok == 21, f"Expected 21/21, got {ok}/21"
```

## 输出示例（家主）

取自2026-06-27验证输出：

```
§1: 【八字】癸未 己巳 庚申 壬子 ...
§3: 【身强弱判定】身弱（24.0分）【金鉴真人·身强弱规则·月令本气印=40分·比劫全算】...
§8: 【财星评分】总分1.2分 | 等级：小富 【金鉴真人·财星规则·只含正偏财·不含劫财】...
§14: 【先天体质】中等 五行过三排查：无 ...
§17: 【大运序列（8步至100岁）】✅ 戊辰 0~9岁 7.0/10分 ...
```

## 扩展建议

当前 `_gen_detail_analysis.py` 的每个函数只有10-30行。要提升到50-100行/§（使报告达到1500+行），需要：

1. **引擎模块加厚**：在 `comprehensive_v2.py`、`education_v2.py`、`marriage_v2.py` 等模块的函数中增加更多计算结果字段
2. **detail_analysis对应扩展**：在 `_gen_detail_analysis.py` 对应函数中读取新字段展开
3. **循环迭代**：每轮加厚2-3个模块→验证→再下轮

优先加厚模块：`comprehensive_v2.py`（影响§7/§9/§10/§13/§14/§18/§19/§20/§21共9个§）
