---
name: bazi-validate-all
description: 金鉴真人·全量验证流水线。每次修改后运行此skill，验证引擎/排盘/API/报告/农历/前端全部模块。任何FAIL阻断推送。
---

# 金鉴真人·全量验证流水线

## 模块代码审计方法（铁律⑥⑦ → skill化）

### 铁律⑥：单模块审计（7步）— 2026-07-05升级版

每次修改/新建引擎模块后，在跑 `validate_all.py` 之前，先按以下流程审计：

```yaml
Step 1 — 规则审计
  □ load对应skill（skill_view('bazi-xxx-analysis')）
  □ 逐条对比代码逻辑 vs 原始理论规则
  □ 检查：无杜撰、无遗漏、无错误
  □ 特别：模块判断逻辑本身是否与九龙道长一致

Step 2 — 死代码检查
  □ 搜所有def → 检查每个函数是否被调用
  □ 搜所有常量 → 检查是否在分析逻辑中使用（不仅是output dict中存放）
  ⚠️ 2026-07-05教训：health_v2.py的shen_label传入但仅在dict存储，从不用于分析

Step 3 — 引用链验证（⚠️ 最容易被忽略！2026-07-05 education/shi_shang双重教训）\n  □ 入口函数需要哪些参数？调用方comprehensive_v2.py真的传了这些参数吗？\n  □ comprehensive_v2的返回dict真的包含了该模块的结果吗？\n  □ pipeline_v5是否在comprehensive_v2之外又单独调了同一模块？（重复计算）\n  □ 引用链：pipeline_v5 → comprehensive_v2 → module → sub_function\n  □ 额外检查：搜索 `from module_name` 和 `import module_name`，确认有真正的import\n  ⚠️ 致命教训：education审计了两次但都没发现comprehensive_v2根本没调用它！\n  ⚠️ 2026-07-05新发现：shi_shang.py算法完全正确(4/4案例匹配)，但全项目零import——\"孤岛模块\"。\n    算法正确 ≠ 功能可用。必须全链跑通：src → import → call → pipeline → report_output。

Step 4 — 参数是否被至少1个分析函数使用（不仅是放在return dict中）
  □ 特别检查：shen_label/shen_score/xi_yong在每个模块中是否真的用于分析逻辑
  □ 不只是"参数传进来了"，而是"参数在if/for/条件判断中被使用了"

Step 5 — 自测/干跑
  □ python the_module.py（如果有__main__测试）
  □ 检查输出是否与预期一致

Step 6 — 全量测试
  □ cd engine/tests && python test_full_suite.py
  □ 确认FAIL数量不变（或减少）

Step 7 — 发现的问题全部修完再继续下一个模块
  □ 不要审完一个模块就跳下一个——修完所有发现问题再审计下一个
  □ 对大量缺失(30+项)，用sub-agent分5批并行修复最有效
  □ 每批sub-agent修完后跑test_full_suite.py确认回归通过
```

### 铁律⑦：跨模块刑冲合害全链路审计（2026-07-05新增）

每次修复/新增规则类Bug后，额外执行以下检查：

```yaml
第1步：加载覆盖矩阵
  □ skill_view('bazi-auto-verify','references/刑冲合害跨模块覆盖矩阵_20260705.md')
  □ 确认修改的规则涉及哪些事象模块

第2步：逐模块检查规则一致性
  □ 同一规则在3个以上模块有独立定义时，全部检查
  □ 特别注意：六破在xing_chong_he_hua.py中缺失！step1_basic和marriage_v2各自定义

第3步：docstring vs code 一致性检查
  □ 模块头部docstring声称实现的规则，代码是否真的实现了？
  ⚠️ 2026-07-05发现：family.py/misfortune_analysis.py docstring写刑冲合害但代码无

第4步：特殊规则检查
  □ 辰戌丑未冲=越冲越强（不同于普通冲）
  □ 天干四冲仅4组（戊己土居中不冲）
  □ 自刑（辰辰/午午/酉酉/亥亥）容易被忽略
```

### 审计清单（逐模块验讫打勾）— 2026-07-05全量更新

```python
# 2026-07-05 全链路审计结果（全部模块逐行对照skill）：
# 
# ✅ career_v2.py        → 审计+修复(丢官信号④/开官库/恶神级别/循环导入)
# ✅ education.py        → 审计+引用链修复(comprehensive_v2从未调用)
# ✅ marriage_v2.py      → 审计通过(95%对齐skill，无需修)
# ✅ children_v2.py      → 审计+10项修复(养中留一/喜用神/空亡/冲刑/解合/
#                             映射/称谓/不好生特征/容易生特征)
# ✅ health_v2.py        → 审计+4项修复(干支疾病表/妇科/自杀/色欲)
# ✅ liu_nian_v2.py      → 审计+34项修复(评分Bug/岁运并临/贪合忘冲/
#                             能量倍数/天干五合/三会局/拱合/暗合/
#                             宫位断事/断语四要素/分时段/恶神能量表/
#                             大运空亡/三合完整度/合冲害应事/过三关/
#                             流月/大运五维)
# ✅ xing_chong_he_hua.py→ 新增天干五合/三会局/拱合/暗合/合化优先级/
#                             check_all_relations_v2()
# ✅ family.py           → 审计+5项修复(gender参数/月柱被合/月支被冲/
#                             藏干分析/shen_label使用)
# ✅ misfortune_analysis.py→ 审计+12项修复(印星被冲/五行过三/七杀断病/
#                             偏印断病/灾煞能量/元辰填实/血刃/枭神夺食/
#                             岁运并临/六十甲子/天乙化解/宫位定位)
#
# ✅ shi_shang.py        → 2026-07-05审计：算法正确(4/4案例匹配参考值)，但**从未被任何pipeline导入/调用**(孤岛模块)
#
# 待审计:
#   □ character.py / energy.py / cai_xing.py / da_yun.py
#   □ pipeline_v4/v3 同步更新到 comprehensive_v2
```

---

## 使用方式

```bash
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && python3 engine/tests/validate_all.py
```

## 验证项（26条）

| # | 验证项 | 覆盖内容 |
|:-:|:------|:---------|
| 1 | 引擎320条测试 | 5人×身强弱/财星/格局+21§结构+特殊规则 |
| 2 | 排盘正确性 | 子源八字对照+paipan模块日期→八字 |
| 3 | API端点 | ping/version/engine/debug/report |
| 4 | 21§完整性 | 全套21个§是否存在+报告行数 |
| 5 | 格式对齐 | 版本说明/25字段/白话/五级/署名 |
| 6 | 农历转换 | lunar_to_solar正确性+API农历/阳历一致 |
| 7 | 前端可访问 | 首页加载/四柱/命理/日历/PDF |

## 铁律

```yaml
每次修改以下内容后，必须跑validate_all.py：
  □ 引擎代码（engine/*.py）
  □ 排盘逻辑（paipan.py）
  □ API路由（api/routers/*.py）
  □ 报告生成器（report_generator.py）
  □ 前端（frontend/index.html）
  
阻断规则：
  ❌ 有任何FAIL → 禁止push到GitHub
  ✅ 全部PASS → 允许push

发现问题的处理原则（2026-07-05校准）：
  □ 审完一个模块后，发现的全部问题修完再审计下一个
  □ 不跳过、不"以后再修"
  □ 对大量缺失用sub-agent分批并行修复（每批5项左右）
```

## 验证脚本路径

`projects/bazi-platform/engine/tests/validate_all.py`
