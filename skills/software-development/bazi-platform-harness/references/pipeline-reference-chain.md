# 引擎模块引用链路图（2026-07-05审计校准）

> **用途：** 每次审计/修Bug/加模块时，必须按此图确认调用链完整+无重复。
> **核心原则：** 每个模块在整个调用链中**只算一次**（要么 pipeline 算→传 orchestrator，要么 orchestrator 统一算）。

## 当前主入口链路

```
bazi-must-run-engine.sh
  → pipeline_v5.run_v5()
    │
    ├─ Step 1: 核心计算（确定性）
    │   ├─ compute_shen_qiang_ruo(bazi)         → sqr_score, sqr_label, sqr_detail
    │   ├─ compute_cai_xing(bazi)               → cai (含 cai.total)
    │   ├─ determine_ge_ju(bazi)                → main_ge, detail_ge
    │   ├─ determine_xi_yong_shen(bazi)         → xi, ji
    │   ├─ get_tiao_hou_yong_shen(...)          → th
    │   ├─ compute_energy_profile(bazi)         → energy
    │   ├─ check_all_relations(all_zhis)        → dz
    │   ├─ compute_all_shen_sha(...)             → ss
    │   ├─ compute_da_yun(bazi, ...)            → dy_list, qy_age, qy_year
    │   └─ compute_da_yun_scores(bazi, dy_list) → dy_scores
    │
    ├─ Step 2: 流年分析
    │   └─ analyze_liu_nian_range(...)          → ln_results
    │
    ├─ Step 3: v2.0 模块（各自独立计算，结果传给comprehensive）
    │   ├─ analyze_education(...)               → edu    ← 这里算一次
    │   ├─ analyze_marriage(...)                 → mar
    │   ├─ analyze_character(...)                → char
    │   └─ analyze_nian_yue(...)                 → fam
    │
    ├─ Step 4: 综合引擎（收拢 Step 3 的结果，不再自己重算）
    │   └─ run_comprehensive_engine(
    │         bazi, sqr_score, sqr_label, sqr_detail,
    │         cai, main_ge, detail_ge, xi, ji,
    │         dy_list, dy_scores, best_idx, worst_idx,
    │         mar,     ← marriage_result（接收pipeline算好的）
    │         edu,     ← education_result（接收pipeline算好的，不再自己重算！）
    │         birth_year, current_year
    │       )
    │       ├─ career_v2.analyze_career_full()      ← 内部算
    │       ├─ wealth_v2.analyze_wealth_full()      ← 内部算
    │       ├─ children_v2.analyze_children_full()   ← 内部算
    │       ├─ health_v2.analyze_health_full()       ← 内部算
    │       ├─ analyze_appearance()                 ← 自身函数
    │       ├─ analyze_property()                    ← 自身函数
    │       ├─ generate_three_verdicts()             ← 自身函数
    │       ├─ generate_da_yun_curve()               ← 自身函数
    │       ├─ generate_wu_xing_advice()             ← 自身函数
    │       ├─ generate_life_advice()                ← 自身函数
    │       └─ 返回 dict 含：
    │           sec_6_career, sec_8_wealth_full, sec_7_appearance,
    │           sec_5_education, sec_9_property,
    │           sec_13_children, sec_14_health,
    │           sec_18_verdicts, sec_19_overall,
    │           sec_20_wu_xing_advice, sec_21_advice
    │
    └─ Step 5: 21§ 输出汇总
        └─ comprehensive 的各个 sec_* 字段 + pipeline 自身算的 char/fam/liunian
```

## 谁调谁（完整映射）

| 被调模块 | 在 pipeline_v5 中 | 在 comprehensive_v2 中 | 审计状态 |
|:---------|:------------------|:-----------------------|:---------|
| wealth_v2 | ❌ 不直接调 | ✅ `analyze_wealth_advanced()` | ✅ 已审计 |
| career_v2 | ❌ 不直接调 | ✅ `analyze_career_advanced()` | ✅ 已审计+修复 |
| education | ✅ 外调→传结果给comprehensive | ✅ 接收参数，不再自己算 | ✅ 引用链已修 |
| marriage_v2 | ✅ 外调→传结果给comprehensive | ✅ 接收参数 | ✅ 审计通过(95%) |
| children_v2 | ❌ 不直接调 | ✅ `analyze_children_advanced()` | ✅ 已审计+修复 |
| health_v2 | ❌ 不直接调 | ✅ `analyze_health_advanced()` | ✅ 已审计+修复P0 |
| liu_nian_v2 | ✅ `analyze_liu_nian_range()` | ❌ 不涉及 | ✅ 已审计(修复中) |

## 版本差警示（2026-07-05 children_v2 案例）

**问题：** children_v2.py 代码标注 v2.0（2026-06-15），而 skill 已更新到 v3.0（2026-06-27）。

**后果：** 代码缺失了 skill 中 §第九步至§第十六步的 6 个新功能块（不好生孩子11条/容易生孩子6条/催子阵/能量8法/功德求子/私生子/石榴树），共 7 个缺失项。

**教训：** 审计前必须先核对代码头部的版本日期与 skill 版本日期。版本差=一定有未实现规则。

```yaml
检查流程：
  Step 1: 读代码头部 docstring（"vX.Y"/"更新日期"）
  Step 2: 读 skill 头部 description（"vX.Y"/"编制时间"）
  Step 3: 对比两个日期
    ├─ 代码日期 ≥ skill 日期 → 理论上全部实现（仍需逐条验证）
    └─ 代码日期 < skill 日期 → 一定有未实现规则！按 § 号逐一检查
```

## 并行 Sub-Agent 审计模式（2026-07-05 实战）

使用 `delegate_task` 同时审计多个模块，每个 sub-agent 独立加载 skill + 读代码 + 出报告。

```yaml
工作流：
  1. 确定待审计模块清单（按优先级排序）
  2. 为每个模块构造 delegate_task context
     ├─ goal: "深度审计 {模块}.py vs {对应-skill} 逐条对照"
     ├─ context: skill关键规则列表 + 引用链信息 + 审计标准
     └─ role: "leaf"
  3. 同时派发（batch模式）→ 并行审计
  4. 每个结果返回后检查审计报告
  5. 按顺序修问题 → 测试 → 推库

优点：
  ├─ 独立上下文 → 互不干扰
  ├─ 并行加速 → 2-3个模块同时审
  └─ 每份报告独立可存档
```

## 审计引用链时的检查清单

每次审完一个模块后：
```
□ 该模块在 pipeline_v5 中被调用了几次？
   — 只调一次 ✅
   — 既在 pipeline 外层调，又在 comprehensive 内部调 = 重复 ❌
□ 如果 pipeline 外层调了 → comprehensive 是否用参数接收而不是重调？
□ 如果 comprehensive 内部调了 → pipeline 外层是否不再调？
□ 模块返回的结果是否出现在 pipeline_v5 最终的返回 dict 中？
□ 返回的 key 名与 pipeline 中读取的 key 名一致吗？
   — 例：comprehensive 返回 "sec_5_education" → pipeline 用 comprehensive["sec_5_education"]
```

## 旧版 pipeline 仍存在的问题

| Pipeline | 问题 | 严重度 |
|:---------|:-----|:------:|
| pipeline_v4 | 用的 `from comprehensive import *`（旧版），不是 `comprehensive_v2`；用的 `marriage`（旧版）不是 `marriage_v2`；用的 `dimensions`（已废弃） | P3 |
| pipeline_v3 | 全部直接调旧版模块，无 comprehensive_v2 | P3 |

***本文件首次创建于 2026-07-05 会话，education 去重教训后固化。***
