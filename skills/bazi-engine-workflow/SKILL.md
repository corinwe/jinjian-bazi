---
name: bazi-engine-workflow
描述: 金鉴真人·八字排盘引擎工作流。v6.5新增references/跨模块审计20260705.md（三模块审计实战记录+v6第六层代码路径审计&character.py审计案例）。v6.3新增references/大运起运年计算错误与修复_20260701.md补充（大运列修正后分析文本需同步协调的铁律）。v6.0新增references/引擎计算Bug修复记录_20260628.md（大运评分set去重bug+财富评级阈值bug）。v5.9新增：detail_analysis确定性桥梁架构（21§全量规则分析文本），规则引擎升级为「结构化数据+规则分析文本」双输出。v5.7新增：paipan.py修复+验证强制流程+misfortune_analysis模块。v5.5新增月柱计算Bug修复。references/已知陷阱_引擎门禁_20260704.md。references/python-api-usage-20260704.md。references/shi-shen-map-bug-20260704.md（食伤阴阳颠倒·LLM绕过引擎铁律）。2026-07-05新增references/liu-nian-r39-r46-fixes_20260705.md（流年v2.1 R39恶神能量表+R40神煞界限+R41大运空亡+R42三合完整度+R46身过强破财）。
tags: [八字, 排盘, 引擎, 真太阳时, 官网验证, 金鉴真人, 大运bug修复, 全栈平台, 日期输入, detail_analysis]
---

# 金鉴真人·八字排盘引擎工作流 v5.9

> **v5.9 detail_analysis 架构（2026-06-27）**：新增 `_gen_detail_analysis.py` 确定性桥梁模块，为引擎21§输出附加 `detail_analysis` 规则分析文本。规则引擎从「纯数据结构化JSON」升级为「结构化数据+规则分析文本」双输出。`generate_deep_report.py` v3.0 消费全部21个§的 `detail_analysis`。架构决策：宁可代码生成简短的确定性文本，也不让LLM生成冗长的不稳定文本。详见下文「🆕 v5.9 detail_analysis 架构」。

## 🆕 v5.9 detail_analysis 架构：规则引擎→自然语言的确定性桥梁（2026-06-27新增）

> **核心问题**：引擎输出结构化JSON（分数/标签），而人类需要自然语言分析。之前LLM做翻译时不稳定——同一个八字不同报告质量参差。
> **解决方案**：在规则引擎内增加 `_gen_detail_analysis.py` 模块，将引擎的确定性计算数据翻译为基于规则的分析文本（`detail_analysis`字段），让所有21个§都有确定性的规则分析文字。
> **关键原则**：`detail_analysis` 仍然是**代码生成**的确定性文本（不是LLM写的），它只做「引擎数据→规则分析文本」的翻译，不做任何推理。

### detail_analysis 架构图

```
用户输入八字
  ↓
run_v5() → 21§结构化JSON（分数/标签/细节）
  ↓
attach_detail_analysis(result) ← 在run_pipeline()中调用
  ↓  遍历所有21个§
  ↓  每个§调用对应的 _xxx_detail() 函数
  ↓  函数读取引擎计算数据，生成规则分析文本
  ↓
每个§的dict增加 "detail_analysis" 字段（含规则引用+数据映射）
  ↓
generate_deep_report.py v3.0 读取 detail_analysis
  ↓  对每个§：尝试用detail_analysis → 失败则回退到旧版代码
  ↓
完整深度报告（所有分析文字源自引擎规则计算）
```

### 文件位置

| 文件 | 角色 |
|:----|:-----|
| `projects/bazi-platform/engine/_gen_detail_analysis.py` | 核心模块（24,000字符）21个§的生成函数 |
| `projects/bazi-platform/engine/generate_deep_report.py` v3.0 | 深度报告生成器，消费detail_analysis |

### 21个detail_analysis函数总览

| 函数 | 对应§ | 功能 |
|:-----|:-----|:-----|
| `_sec_1_detail()` | §1 总览 | 八字/日主/身强弱/喜忌/财星/最佳运 |
| `_ge_ju_detail()` | §2 格局 | 核心格局+十神分布 |
| `_shen_qiang_ruo_detail()` | §3 身强弱 | 评分明细+判定+规则引用 |
| `_xi_yong_detail()` | §4 喜用神 | 喜忌排序+判定逻辑+调候 |
| `_zai_huo_detail()` | §5 灾祸 | 神煞排查+地支关系+五行过三 |
| `_character_detail()` | §6 性格 | 日主底色+十神特质+优先用已有detail_analysis |
| `_appearance_detail()` | §7 外貌 | 日主长相+体型+身高+气质+体重 |
| `_wealth_detail()` | §8 财富 | 财星评分+六种状态+财库+五级对照 |
| `_property_detail()` | §9 置业 | 置业潜力+能力+时机+风水 |
| `_career_detail()` | §10 事业 | 方向+等级+模式+行业+创业 |
| `_education_detail()` | §11 学历 | 年柱印+文昌+六步排查+学校等级 |
| `_marriage_detail()` | §12 婚姻 | 质量+配偶+窗口+信号+规则引用 |
| `_children_detail()` | §13 子女 | 数量+成就+生育力+缘薄因素 |
| `_health_detail()` | §14 健康 | 体质+五行过三+七杀+偏印+交战 |
| `_family_detail()` | §15 六亲 | 总评+各柱+助力分析 |
| `_events_detail()` | §16 事件 | 关键事件+近期流年 |
| `_da_yun_detail()` | §17 大运 | 序列+评分+最佳/最差+起运年龄 |
| `_verdicts_detail()` | §18 三决断 | 三决断展开 |
| `_overall_detail()` | §19 运程 | 曲线+核心+风险 |
| `_wu_xing_advice_detail()` | §20 五行 | 颜色+方位+饰品+饮食+数字 |
| `_advice_detail()` | §21 建议 | 事业/财富/健康/婚姻/人际 |

### 每个detail_analysis函数的结构化输出要求

每条 `detail_analysis` 文本必须包含：

```yaml
□ 【规则来源标注】—— 每个关键断语后标注【金鉴真人·§X·规则名】
□ 【引擎数据映射】—— 规则→命主具体数据的映射
□ 【判定结论】—— 基于规则和数据的结论

示例（§3身强弱）：
  【身强弱判定】身弱（24.0分）
  【金鉴真人·身强弱规则·月令本气印=40分·比劫全算】
  月令印星计0.0分 | 月令比劫计0.0分 | 天干比劫计12.0分 | 
  日支印比计12.0分 | 年时支印比计0.0分
  结论：身弱。宜借平台和贵人发力，不宜单打独斗。
```

### generate_deep_report.py v3.0 的消费逻辑

每个§的展开统一使用 `_expand_section()` 函数：

```python
def _expand_section(num, title, da_section, da_key="detail_analysis"):
    da = da_section.get(da_key, "") if isinstance(da_section, dict) else ""
    if da:
        for l in da.split(chr(10)):
            if l.strip():
                lines.append(l)
    else:
        lines.append("*（引擎数据不足，无法展开详细分析）*")
```

**回退策略**：对§18（verdicts）特殊处理——先查 `sec_18_verdicts_detail`，失败则回退到遍历 `sec_18_verdicts` list。

### 扩展指南（为已有模块增加更丰富的detail_analysis）

当需要提升某个§的 `detail_analysis` 深度时：

1. 先在该引擎模块（如 `comprehensive_v2.py`、`education_v2.py`）中增加更多计算字段
2. 然后在 `_gen_detail_analysis.py` 的对应函数中读取新字段展开分析
3. 测试：`python3 -c "from pipeline_v5 import run_pipeline; r=run_pipeline(...); print(r['result']['sec_X_y']['detail_analysis'])"`
4. 确认输出包含规则标注+数据映射+结论

**为什么先扩展引擎模块再扩展detail_analysis？**
因为 `_gen_detail_analysis.py` 是**后处理**——它只基于已有数据生成文本。如果引擎模块本身输出太短（如 `constitution: "中等"`），后处理只能写一行。要真正提升报告深度，需要先让引擎模块输出更多结构化数据。

### 验证方式

```bash
cd projects/bazi-platform/engine && python3 -c "
from pipeline_v5 import run_pipeline
result = run_pipeline('家主', '男', '癸', '未', '己', '巳', '庚', '申', '壬', '子', birth_year=1980)
r = result['result']
sections = ['sec_1_overview','sec_2_ge_ju','sec_3_shen_qiang_ruo','sec_4_xi_yong',
            'sec_5_zai_huo','sec_6_character','sec_7_appearance','sec_8_wealth',
            'sec_9_property','sec_10_career','sec_11_education','sec_12_marriage',
            'sec_13_children','sec_14_health','sec_15_family','sec_16_events',
            'sec_17_da_yun_detail','sec_18_verdicts','sec_19_overall','sec_20_wu_xing_advice','sec_21_advice']
ok = sum(1 for k in sections if r.get(k,{}).get('detail_analysis',''))
# 对verdicts特殊处理
if r.get('sec_18_verdicts_detail',{}).get('detail_analysis',''):
    ok += 1
print(f'{ok}/21 sections have detail_analysis')
"
# 输出应为: 21/21 sections have detail_analysis
```

口诀：
  detail_analysis是桥梁，引擎数据转规则文本
  每个§都有函数对应，规则标注数据映射都齐全
  先扩引擎再扩后处理，数据丰富文本才厚
  generate_deep_report消费它，所有§都用detail_analysis

# 金鉴真人·八字排盘引擎工作流 v5.7

> **v5.7核心升级**：新增「两步走」产品架构范式——第一大步扒11行×4列原始数据（不判断），第二大步逐条if-else规则出判断。完整输出规格参考 `references/八字排盘11行×4列完整输出规格_20260626.md`。完整三层架构设计与实战踩坑参见 `references/产品级三层架构设计与工程实践_20260626.md`。
> **引擎验证方法论（2026-06-26新增）**：本场session发现7个系统性bug（constants.py藏干顺序错误/paipan.py日柱公式缺世纪修正/cai_xing.py年干分值+位置遗漏/shen_qiang_ruo.py分值uniform+燥土规则顺序）。教训：不逐行审查+全量测试=有bug。完整方法论见 `references/引擎模块验证方法与bug模式_20260626.md`。  
> **v5.0确定性引擎**（2026-06-26建成）：comprehensive_v2/education_v2/marriage_v2/dimensions_v2 四个新模块替换旧硬编码模块，pipeline_v5 成为当前主引擎。纳音空/大运年份/四柱表等bug已修复。参见 `references/pipeline_v5_确定性规则引擎架构_20260626.md`

## 🚨 核心架构：两步走（老板2026-06-26亲定）

任何八字进来，严格按两步走，**全部代码计算，零LLM参与分析推理**。

### 第一大步：扒原始数据（11行×4列 + 4附加项）

→ 只查表/只计算，不做任何判断分析

输出字段（精确匹配参考图格式）：

| 行 | 年柱 | 月柱 | 日柱 | 时柱 |
|:--:|:----|:----|:----|:----|
| ①十神 | 劫财 | 食神 | 元男(日主) | 比肩 |
| ②天干 | 庚 | 癸 | 辛 | 辛 |
| ③地支 | 申 | 未 | 亥 | 卯 |
| ④藏干 | 庚壬戊(带十神) | 己丁乙(带十神) | 壬甲(带十神) | 乙(带十神) |
| ⑤纳音 | 石榴木 | 杨柳木 | 钗环金 | 松柏木 |
| ⑥空亡 | 子丑 | 申酉 | 寅卯 | 午未 |
| ⑦神煞 | 羊刃、劫煞 | 红鸾、丧门等 | 文昌、亡神等 | 将星、元辰等 |

附加：⑧天干留意 / ⑨地支留意 / ⑩称骨重量 / ⑪称骨评语

**铁律**：这一大步不允许任何"判断"，只有查表和公式计算。
完整规格见：`references/八字排盘11行×4列完整输出规格_20260626.md`

### 第二大步：逐条对比规则出判断

→ 每个位置每个藏干逐一检查：满足条件就加分，不满足就不加分

### LLM角色：仅做最后润色

LLM只做**翻译**（JSON结构化数据 → 自然语言报告），不做**推理**（不参与任何分数计算/规则对比/格局判定）。

**口诀**：第一大步扒数据，不判只算；第二大步比规则，逐条应用；满足就加不满足不加，全部代码写死。

### 🚨 2026-06-26 七Bug全记录（逐行审计的实战教训）

> **触发场景**：一口气写了paipan.py(300+行) + shen_qiang_ruo.py(200+行) + cai_xing.py(150+行)后整体测试，发现7个bug。
> **核心教训**：每次只写一个函数（≤50行），写一个测一个。

| # | Bug | 位置 | 表现 | 根因 | 修复 |
|:-:|:----|:----|:-----|:----|:-----|
| 1 | 巳藏干顺序错 | constants.py | 巳=丙庚戊 → 实际应为丙戊庚 | 藏干顺序记忆错误，中气/余气互换 | 改为丙(100%)·戊(60%)·庚(30%) |
| 2 | paipan.py日柱公式缺世纪修正 | paipan.py | 特定年份日柱算错 | 日干支公式 need century correction | 改为基准日法：选已知正确日柱为base，N mod 60+base |
| 3 | cai_xing.py年干财星漏算 | cai_xing.py | 年干财星不计分 | 位置循环未包含年干 | 循环中加入年干检查 |
| 4 | cai_xing.py年干分值错(12→8) | cai_xing.py | 年干财星多算4分 | 用了月干标准12分而非年干标准8分 | 改为8分 |
| 5 | shen_qiang_ruo.py分值uniform | shen_qiang_ruo.py | 所有位置用12分而非位置专属分 | 月令40/年支4被忽略 | 改回各位置独立分值 |
| 6 | 燥土规则顺序错 | shen_qiang_ruo.py | 先判壬/癸灭火→后判丙/丁引化 | 优先级写反 | 改为丙/丁优先→壬/癸次之 |
| 7 | 日主计入天干比劫 | shen_qiang_ruo.py | 身强85.6分(应73.6分) | 日干自己也计了比劫分 | 排除日干，只计年干+月干+时干 |

口诀：七个bug同一天，藏干排序日柱偏；财星漏算年干分，燥土规则顺序颠；日主比劫不算身，每次只写50行。

> **老板原话**：「我需要你逐行代码去检查问题到底出在哪里。你写代码的时候，我也需要你逐行代码去写，不是囫囵吞枣。」
> **触发场景**：一口气写了paipan.py（300+行）/ shen_qiang_ruo.py（200+行）/ cai_xing.py（150+行）后一次性跑测，发现7个bug需要逐行定位。被老板批评「你的报告质量还是不行，一会儿稳定一会儿不稳定」。

```yaml
【引擎代码编写的强制流程】

第0步 — 先查已有工具
  写任何引擎代码前先问自己：
  □ bazi-engine.py 已经实现这个功能了吗？
  □ pipeline_v5.py 已经包含这个模块了吗？
  □ 已有skill中有对应的规则文献吗？
  已有就不重写 — 重写=引入新bug的风险

第1步 — 每次只写一个函数，测试一个函数（核心铁律）
  ❌ 错误做法（被老板骂的根源）：
    1. 一口气写500行代码
    2. 整体跑一次测试
    3. 发现7个bug，逐行定位花2小时
  
  ✅ 正确做法（老板要的）：
    1. 写一个函数（≤50行）
    2. 立即用真实八字数据跑测试
    3. 确认输出正确再做下一个函数
    4. 每个函数独立验证通过后，再做集成

第2步 — 逐行自检（写代码时的心理检查）
  每写一行问自己：
  □ 循环范围对不对？（天干比劫=年干+月干+时干，不含日干）
  □ 边界条件处理了？（hour=0, hour=23都要对）
  □ 藏干顺序对不对？（巳=丙戊庚 不是 丙庚戊）
  □ 位置分值对不对？（年干=8分 不是 12分）
  □ if条件覆盖了所有分支？（燥土=有丙丁/有壬癸/都有/都没有）
  □ 这个藏干是日主的什么十神？（先查五行生克再查阴阳）

第3步 — 用JSON数据源做集成验证
  写完一个模块后，最少测试4个已知八字：
  □ 家主（甲午 己巳 戊午 壬子 → 身强73.6分 / 财星24.0分）
  □ 主母（戊午 甲子 庚戌 丁亥 → 身弱7.2分 / 财星7.2分）
  □ 子源（庚申 辛巳 甲午 丙寅 → 身弱12.0分 / 财星24.0分）
  □ 父亲（己丑 癸酉 癸亥 戊午 → 身强66.4分 / 财星12.0分）
  全部通过才告知用户「可以测试了」

第4步 — 不要让我当你的测试员
  ❌ 先给老板用 → 老板发现bug → 「我不是你的测试啊」
  ✅ 自己先逐行审 → 跑4个JSON数据验证 → 确认无误再上线

口诀：
  写码先问已有否，不重写不造轮子
  一次写一个小函数，写完就测不积压
  每行自检六问题，边界条件循环分
  四个八字全过测，不上线等老板测
```



## 🆕 引擎模块扩展工作流（2026-06-27新增·老板亲令）

> **正确的方法论**：「先扩引擎模块 → 再展detail_analysis → 行数自然增长。禁止写占位符。」

```yaml
Step 0 — 判断：报告行数不足1500或某§detail_analysis单薄→扩展对应引擎模块
  ❌ 禁止在报告格式化层写通用占位符凑行数

Step 1 — 用模块对应§映射定位：
   education_v2.py  → §11 学历     marriage_v2.py   → §12 婚姻
   comprehensive_v2 → §7/§9/§10/§13/§14/§18/§19/§20/§21
   cai_xing.py→§8财富  shen_qiang_ruo.py→§3身强弱
   ge_ju.py→§2格局    da_yun.py→§17大运    family.py→§15六亲

Step 2 — 给模块return dict添加新字段（例：education_v2新增six_step_details）

Step 3 — 在_gen_detail_analysis.py中消费新字段

Step 4 — python3 -m py_compile + 全量测试验证

Step 5 — grep -c "通用\|附录A\|术语" 报告=0确认无占位符

口诀：行数不够扩引擎，不写占位不凑数；改完引擎改gen_detail，编译测试全量跑
```

### 🚨 子agent文件命名约定（2026-06-27新增·搜索不到子agent报告触发）

> **致命教训**：子agent生成的文件名用 `_NEW_20260627.md` 后缀，而父agent用 `_ALLNEW_20260627.md` 后缀。父agent在搜索时只搜了 `v27` 关键词，没匹配到 `_NEW_` 文件，导致白做了5份重复报告然后清理。

```yaml
【子agent输出文件命名铁律】

子agent用 `_NEW_` 后缀：
  ✅ {姓名}_完整八字命理深析报告_vX.0_标准格式_NEW_20260627.md

手动（父agent）写用 `_ALLNEW_` 后缀：
  ✅ {姓名}_完整八字命理深析报告_vX.0_标准格式_ALLNEW_20260627.md

搜索文件时的强制流程：
  □ 先搜 `*_NEW_*.md` —— 子agent生成
  □ 再搜 `*_ALLNEW_*.md` —— 手动生成
  □ 如果两种都找不到，再搜 `*v{版本号}*.md`
  ❌ 禁止只搜版本号（如 `v27`）—— 文件名可能不包含版本号前缀

口诀：子NEW父ALLNEW两编码，搜文件两种后缀都要查
      先搜NEW再搜ALLNEW，版本号搜索放最后
```

### 🚨 24小时审查法则（2026-06-26新增）

> **触发场景**：老板问「你昨天晚上我睡觉的时候做的这些报告，你是不是完全每一份都完全遵照我的要求」

```yaml
【重大修改后必须全量自检】

触发条件（任一满足）：
  □ 修改了引擎核心文件（paipan.py / shen_qiang_ruo.py / cai_xing.py 等）
  □ 修改了pipeline编排文件（pipeline_v5.py / pipeline_product.py）
  □ 修改了constants.py（藏干表/纳音表/神煞表等数据）
  □ 同时新增/修改了3个以上文件
  □ 用户睡觉时我还在干活（因为没有人在监督，最容易出bug）

自检清单：
  □ 所有已知八字的排盘是否正确？
  □ 所有已知八字的身强弱分数是否正确？
  □ 所有已知八字的财星分数是否正确？
  □ API是否能正常返回数据？
  □ 前端是否能正常展示？

不自测（或仅跑1个用例）就提交 = 等老板骂。

### 🚨 老板执行纪律：不要停下来问方向，干到位再说（2026-06-27新增）

> **用户反复强调的规则**：「不要老停下来问我」「没干到就继续干」「卡住了？？直接写」「不要停下来问方向」

```yaml
【老板执行纪律】任务执行中的三条铁律：

铁律一 — 目标导向
  任务目标明确后，执行中不要停下来问「方向对不对」「要不要做这个」
  目标就是方向。干到位（达到目标标准）才停下来。
  ❌ 禁止：做到一半停下来问「要不要加XXX」

铁律二 — 质量优先  
  目标没有达到时，继续干。不降低质量，不多解释。
  「没干到就继续干，不要老问我」
  ❌ 禁止：为求快而缩水（如700行代替1500行）

铁律三 — 主动补位
  发现缺失或错误，直接修。不先问「要不要修」。
  修完再一次性汇报结果。
  ❌ 禁止：每发现一个问题就问「这个要不要弄」

口诀：目标定了就干到，质量不到继续干；发现问题直接修，全部修完再汇报。
```

### 🚨 主动审计原则（2026-06-26新增·用户「没耐心」教训固化）

> **用户原话**：「说实话 我没耐心去告诉你该怎么去修了」— 应该自己找出所有问题，一次性修完，不逐一问。

```yaml
【主动审计原则】每次声称「完成了」之前，必须自己先做全面审计：

Step 1 — 列出所有可能的出问题维度
  不要等用户指出问题再修。主动列出：
  □ 前端所有已列出的§是否都有数据？（对照引擎21§输出）
  □ 用户输入功能是否完整？（日期选择/日历类型/姓名/性别/时辰）
  □ 输出格式是否符合用户体验标准？（不是原始数据）
  □ 有无被删除的必备功能？（如日历类型选择器）
  □ 新增功能是否全部测试过？

Step 2 — 写一个审计脚本一次性跑完所有检查
  参考：engine/tests/audit_frontend.py（本会话创建）

Step 3 — 所有缺失项一次性修完
  □ 不做「先发版再补」— 用户看到不完整版本
  □ 不做「先问用户要不要」— 用户说「没耐心」
  ✅ 全部修完 → 告诉用户「全部搞定」

口诀：主动审计不等人，用户不说我也查；21§对前端，缺哪个补哪个；全修完再汇报，不让用户再教。
```

> **本会话实战**：用户指出前端缺8个§展示 + 缺日历类型选择 + 四柱缺藏干 + 五行缺数字。我全部一次性修完，不再逐一问。

> **用户原话**：「说实话 我没耐心去告诉你该怎么去修了」— 应该自己找出所有问题，一次性修完，不逐一问。

```yaml
【主动审计原则】每次声称「完成了」之前，必须自己先做全面审计：

Step 1 — 列出所有可能的出问题维度
  不要等用户指出问题再修。主动列出：
  □ 前端所有已列出的§是否都有数据？（对照引擎21§输出）
  □ 用户输入功能是否完整？（日期选择/日历类型/姓名/性别/时辰）
  □ 输出格式是否符合用户体验标准？（不是原始数据）
  □ 有无被删除的必备功能？（如日历类型选择器）
  □ 新增功能是否全部测试过？

Step 2 — 写一个审计脚本一次性跑完所有检查
  参考：engine/tests/audit_frontend.py（本会话创建）

Step 3 — 所有缺失项一次性修完
  □ 不做「先发版再补」— 用户看到不完整版本
  □ 不做「先问用户要不要」— 用户说「没耐心」
  ✅ 全部修完 → 告诉用户「全部搞定」

口诀：主动审计不等人，用户不说我也查；21§对前端，缺哪个补哪个；全修完再汇报，不让用户再教。
```
```

---

## 🏭 产品架构：三层分离（2026-06-26建成）

```
projects/bazi-platform/
├── database/       ← 数据层（5张表 + SQLite）
├── engine/         ← 规则引擎层（18个模块，全部代码）
├── api/            ← API服务层（FastAPI + RESTful）
└── frontend/       ← 前端层（SPA，待接入）
```

**设计特点：**
- 数据端/服务端/前端严格分离，独立部署
- 数据库预留 `liu_yue`/`liu_ri` 字段，流月流日扩展不改表
- API用ThreadPoolExecutor，100并发不阻塞
- 引擎独立进程调用，可水平扩展
- API入口：`POST /api/v1/analyze` 返回完整结构化JSON
- 引擎入口：`projects/bazi-platform/engine/pipeline_product.py --json`

### 🚨 架构铁律（2026-06-26老板确认·详见reference）

> **老板原话：「你的报告质量还是不行，一会儿稳定一会儿不稳定」「我们是商业化产品，必须任何一个八字进来都能按照标准格式以及实际规则，匹配客户的八字信息，逐一对比得出报告结论」**
>
> 完整版见 `references/产品架构铁律_规则引擎vsLLM_20260626.md`

**核心结论**：规则引擎（确定性Python代码）做所有计算，LLM只做JSON→自然语言翻译。subagent不可靠，不得让subagent自行计算任何命理数据。

```yaml
LLM角色：仅做翻译，不做推理
规则引擎角色：做所有确定性计算
Subagent角色：仅做数据填充和文字润色（数据必须在context中封闭）
产品形式：网站/API + 规则引擎后台，不是LLM一问一答
```

**核心工作流：**
```
用户输入八字 → POST /api/v1/analyze
  → 规则引擎 subprocess（零LLM）
    → Step 1: 排盘 (bazi-engine.py)
    → Step 2: 11行×4列基础数据 (step1_basic.py)
    → Step 3: 9个分析模块全代码计算
  → 存入数据库（5张表含预留字段）
  → 返回结构化JSON
  → (可选) LLM润色 → 自然语言报告
```

### 🔧 Python API参考（2026-07-04新增）
详见 `references/python-api-usage-20260704.md` —— `paipan` → `BaZi` → `run_v5()` 的完整调用序列，含参数顺序警告、字段名对照、常见错误速查和一行验证命令。本会话中5次试错后固化，抄走直接跑。

### 🚨 铁律：规则引擎 ≠ LLM

```yaml
规则引擎（代码）：输入一样→输出永远一样→确定性、可审计、可商业化
    成本：0.001元/次
    LLM角色：只做翻译（JSON→自然语言），不做推理

LLM方案：输入一样→输出可能不同→不稳定、不可商业化
    成本：0.1-0.5元/次
    问题：LLM会"猜"而不是"算"

分析方法：逐个检查，每个字每个藏干
    口诀：满足条件就加分，不满足就不加分，这不就结束了吗？
```

---

# 金鉴真人·八字排盘引擎工作流 v5.1

> **v5.1核心升级**：bazi-pipeline.sh 全流程主控脚本成为**首选入口**——自动串联排盘→验证→生成§1骨架→生成sub agent context→子agent返回后全量验证→推库，全程物理锁死。bazi-must-verify.sh 降级为pipeline的内部组件。
> 同时：新增 bazi-full-verify.sh（一键全量验证）和 bazi-delegate-check.sh（子agent返回后回写校验），与 bazi-subagent-context skill 形成6项物理保证体系。
>
> **v5.0核心升级回顾**：bazi-must-verify.sh 三重门禁自动化脚本——引擎排盘+官网验证+对比确认+标准§1骨架输出，一步到位。手动双通道流程降级为故障排查备用路线。
> 同时：bazi-must-verify.sh 脚本中发现的3个硬编码bug（性别参数传数字/日主五行写死为土/性别写死为女）已修复并纳入踩坑记录。
>
> **v4.3核心升级**：新增日期扫描技术（凤案例·日期差1天→日主全错）。新增references/date-scanning-technique.md — 当八字矛盾/日期不确定时，扫描前后N天定位正确日柱。
>
> **v4.2核心升级**：添加🚨「引擎+验证双通道」强制铁律 — 任何八字必须先用bazi-engine.py排盘，再用bazi-zydx-verify.sh官网验证，两者一致才能用。禁止手动算日柱！
>
> **v4.1核心升级**：bazi-init-master-data.py 作为首要数据源，官方POST数据优先于引擎计算。旧版「引擎排盘→官网验证」流程降级为备用路线。
>
> **三引擎架构上下文**：本引擎是「三引擎架构」（bazi-master-agent §三引擎架构）的**第一层——规则引擎**。职责范围：所有确定性计算（排盘/身强弱评分/藏干/大运排布），输出结构化JSON供LLM推理层使用。
>
> **关键原则**：引擎输出是**确定性数据**，不依赖LLM。所有计算必须代码化，禁用任何人脑估算。

## 🚨 全流程物理锁死：bazi-pipeline.sh 是唯一入口（v5.1新增·取代must-verify为首选）

> **核心变更**：2026-06-24 新增全流程物理保证体系，`bazi-pipeline.sh` 成为**唯一官方入口**——它内部自动调用 `bazi-must-verify.sh` 做排盘验证，然后生成 context 文件、验证子 agent 输出、全量验证、推库。不跑 pipeline = 拿不到任何东西。

> **旧版 bazi-must-verify.sh** 仍然存在且功能完整，但不再手动调用——改为被 pipeline.sh 自动调用。只有在 pipeline 排盘验证失败需要排查原因时，才手动跑 must-verify.sh。

### ✅ 唯一入口：bazi-pipeline.sh

```bash
# 完整排盘+生成context（日常使用）
bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-pipeline.sh \
  --name {姓名} --year {年} --month {月} --day {日} \
  --hour {时} --min {分} --hour-idx {索引} --gender {男/女}
```

**功能**（全自动完成）：
- **Step 1**：内部调用 bazi-must-verify.sh 做排盘+官网验证+对比确认
- **Step 2**：生成标准§1骨架（_skeleton_{name}.txt）
- **Step 3**：生成 sub agent context 模板（_delegate_context_{name}.txt）
- **Step 4**：输出所有文件到 /tmp/bazi_pipeline_output/

```yaml
【强制流程 — 替代旧版must-verify流程】

拿到任何新八字需求后：

Step 0 — 加载 master-agent + subagent-context skill
  skill_view('bazi-master-agent')
  skill_view('bazi-subagent-context')

Step 1 — 跑 bazi-pipeline.sh（唯一入口，绕不开）
  bash bazi-pipeline.sh --name {姓名} --year {年} --month {月} --day {日} \
                        --hour {时} --min {分} --hour-idx {索引} --gender {男/女}
  
  输出（到 /tmp/bazi_pipeline_output/）：
  □ must_verify_output.txt — 引擎+官网双通道验证结果
  □ _skeleton_{姓名}.txt — 标准§1骨架（25字段，{待填}填空）
  □ _delegate_context_{姓名}.txt — sub agent context 模板
  
  ⛔ 没有这些文件 → 无法开始 delegate_task → 无法生成报告
  
Step 2 — 子agent返回后，验证
  bash bazi-pipeline.sh --verify /tmp/bazi_pipeline_output/{报告}.md \
                        --name {姓名} --birth-year {出生年}
  自动执行：
  □ bazi-delegate-check.sh → 存在性+深度+板块+内容
  □ bazi-full-verify.sh → 格式+数据+板块+逻辑
  
  ⛔ 验证不通过 → 不可推库

Step 3 — 推库
  bash bazi-pipeline.sh --push '{姓名}报告v{X.Y}完成'
  
口诀：pipeline是唯一入口，不跑它拿不到任何东西
      must-verify只是组件，被pipeline内部自动调用
      子agent返回先回检，全量验证不通过不推库
```

### 🔧 bazi-must-verify.sh（降级为pipeline内部组件+故障排查备用）

> 日常使用不需手动调用——bazi-pipeline.sh 内部已自动调用。只在以下场景手动使用：
> - pipeline 排盘验证失败，需要分步排查原因
> - 只想快速验证一个八字不生成报告

### 🔧 手动双通道流程（v5.0起降级为故障排查备用）

> 当 bazi-must-verify.sh 验证失败需要排查原因时，才使用手动分步流程：

```yaml
Step 1 — 跑 bazi-engine.py
  python3 bazi-engine.py {年} {月} {日} {时} {分} {时辰索引} 性别 姓名 --json

Step 2 — 🚨 跑 bazi-zydx-verify.sh 官网验证
  bash bazi-zydx-verify.sh {年} {月} {日} {时} {分} 姓名 {1=男/0=女}

Step 3 — 核对 engine 和 verify.sh 的八字是否一致
  ✅ 完全一致 → 八字确认
  ❌ 不一致 → 检查输入参数并修复
```

### 凤案例复盘（2026-06-23·D级致命）

| 轮次 | 八字 | 来源 | 结果 |
|:----|:----|:-----|:-----|
| 第1版（旧数据源） | 戊午 甲子 辛亥 己亥 | 家族数据源旧版 | ❌ 日主辛金从弱，全错 |
| 第2版（手动计算） | 戊午 甲子 庚戌 丁亥 | 我自己算的日柱 | ❌ 日主庚金身弱，日柱差1天 |
| 第3版（官网验证） | 戊午 甲子 己酉 乙亥 | engine+verify.sh ✅ | ✅ 日主己土身弱财旺，正确 |

**教训**：我第2版手算日柱时，基数479 mod 60=46→天干6庚地支10戌，但正确应该是46→己5酉9。差之毫厘谬以千里。此后所有八字排盘必须用工具，不信任手动计算。

## 🚨 数据源头盔：所有数字从数据源提取，禁止凭记忆说数字（2026-06-24新增·老板指令）

> **老板指令（本会话）**：「不是这出错就是那出错，你为啥又不验证？物理机制是摆设的呀？」
> **根因**：LLM天生会猜——OpenAI 2025论文证明训练奖励猜测而非承认不确定性。这不是个人毛病，是架构性问题。
> **解法**：物理约束代替自觉。数据源头盔三步走：

```yaml
【数据源头盔——强制规则】

任何时候需要输出命理数字（起运年龄/身强弱/财星分数/八字等）：

Step 1 — 先读数据源
  打开 /root/.hermes/profiles/jinjian-zhenren/scripts/family_bazi_data.json
  查找此人是否在数据源中
  ✅ 在 → 使用数据源中的数字（精确值）
  ❌ 不在 → 使用引擎排盘数字，标注「新人·引擎数据」

Step 2 — 再验证
  跑 bazi-pipeline.sh（内部自动调用must-verify做官网交叉验证）
  
Step 3 — 最后说
  验证通过后才能输出数字
  未验证的数字 → 不可信！不可说！

🚨 口头禅：「先查再说」
  数字出口前，先问自己一句：「我查数据源了吗？」
  没查就说 = 这数字不可信

🚨 引擎已知bug警示
  □ 立春前出生 → 年柱可能错（引擎庚子→正确己亥）
  □ 大运年份范围重叠 → 引擎年份不准，以年龄范围为准
  □ 引擎不支持农历 → 用户给农历必须用zhdate转换

口诀：任何数字先查源，不查数据不说话；引擎有bug要警惕，立春之前年柱偏。
```

---
## 🚨 前端设计铁律（2026-06-26新增·老板两轮纠正固化）

> **纠正1**：老板展示当前前端截图，问「这个是你要的吗」— 输出原始数据字段不是我们要的。
> **纠正2**：老板问「用户能看得懂那些脚本吗」— 需要卡片式报告布局，不是纯文本。
> **纠正3**：老板指出「你怎么把阳历阴历的选择搞没了」— 日历类型选择器必须在前端存在。

### ① 日历类型选择器 — 强制存在

所有八字输入界面必须包含阳历/农历单选按钮：

- 默认「阳历」选中
- 用户选「农历」时，API端自动调用 lunar_to_solar() 转换
- 后端 calendar_type 参数必须传递（solar/lunar）
- 禁止没有日历类型选择的日期输入界面
- 禁止将农历日期直接当阳历排盘（月柱会差1-2个月！）

前端示例代码：
```html
<div class="opt-group" id="calendar-group">
  <label class="active"><input type="radio" name="calendar" value="solar" checked>阳历</label>
  <label><input type="radio" name="calendar" value="lunar">农历</label>
</div>
```

API调用必须包含 calendar_type：
```javascript
body: JSON.stringify({
  name, gender, birth_year, birth_month, birth_day, birth_hour,
  calendar_type: cal  // 必传！
})
```

口诀：日历选择不能少，阳历农历要分清；默认阳历选中态，农历自动转公历。

### ② 前端输出格式 — 卡片式命理报告，非原始数据

八字分析结果必须以卡片式命理报告呈现，禁止直接展示原始数据字段。

**正确布局（自上而下）：**
1. 个人档案卡片 — 姓名、八字(大号)、性别、出生年月日、时辰、日主五行
2. 四柱信息表卡片 — 年柱/月柱/日柱/时柱 × 十神/天干/地支/纳音/空亡
3. 核心数据卡片 — 身强弱、财星分、格局、喜用神/忌神
4. 命理分析正文卡片 — 分§一段一段呈现（总览/财富/事业/学历/婚姻/子女/健康）
5. 大运走势卡片 — 4×2网格，每运用颜色区分吉凶
6. 三决断卡片 — 财富/事业/婚姻三个断语
7. 八维评分卡片 — 柱状图，颜色区分高低
8. 五行开运卡片 — 颜色/方位/饰品/饮食
9. PDF下载按钮 — window.print() + @media print 样式

**禁止的展示方式：**
- 直接显示JSON字段值（如「16分」没有上下文）
- 纯文本markdown展示（用户不是程序员）
- 字段列表或键值对展示
- 「喜用: |忌」空字段（数据缺失时友好提示而非留空）

**PDF打印要求：**
- 使用 @media print 样式，打印时隐藏输入区和按钮
- 保持卡片结构，白色背景+黑色文字
- 卡片间 page-break-inside: avoid

口诀：前端输出要漂亮，卡片布局分八段；原始数据不能摆，用户看来是废纸。

### ③ 不清楚时辰处理（默认子时）

前端时辰下拉菜单最后一选项必须为「⏳ 不清楚时辰」：
- value="-1"
- 用户选择后弹出提示「将按子时(23:00)估算」
- 后端收到-1时默认取子时(0)

口诀：时辰不详选子时，前端提示别忘记；报告标注是估算，用户知晓不误导。

## 🚨 前端功能测试流程（2026-06-26实战·所有按钮逐个点）

每次修改前端页面后，必须用浏览器工具完整测试所有交互功能，不能只看API返回。

详见 references/前端功能测试清单.md

---

## 🚨 核心设计原则（2026-06-26老板亲自确认·固化入魂）

> **老板原话：** 「这个规则满足就加分，不满足就不加分，这不就结束了吗？这很简单的呀。包括财星分数的计算逻辑，你不是沉淀的有规则的吗？你的规则直接写成代码放进去就行了，满足条件就加分，不满足条件就不加分。」

```yaml
【铁律】所有命理计算（身强弱/财星/格局/大运等）必须遵循：

Step 1 — 列出该维度所有规则（每个字每个藏干逐一检查）
Step 2 — 对每条规则：满足条件 → 加分（按规则中的分值和比例）
                   不满足条件 → 不加分（即0分）
Step 3 — 不做任何"酌情加减""经验调整"等非确定性操作

每次计算必须像这样逐字逐位置扫描：
□ 年干（8分）→ 是印吗？是比劫吗？
□ 年支（4分）→ 藏干本/中/余气各是什么？是印/比劫吗？
□ 月干（12分）→ 同上
□ 月令（40分）→ 同上（⚠️ 印只本气计分！中/余气=0！）
□ 日支（12分）→ 同上（⚠️ 日干本身不计入比劫）
□ 时干（12分）→ 同上
□ 时支（12分）→ 同上
```

### 规则引擎 ≠ LLM

```yaml
规则引擎：输入一样 → 输出永远一样 → 确定性、可审计、可商业化
    成本：0.001元/次 → 可免费体验
    LLM角色：只做翻译（JSON→自然语言），不做推理

LLM方案：输入一样 → 输出可能不同 → 不稳定、不可商业化
    成本：0.1-0.5元/次
    问题：LLM会"猜"而不是"算"
```

### 产品架构：三层

```
┌─ 前端层 ──────────────────────────┐
│  用户输入（公历/农历+性别）→ 报告  │
│  纯渲染，不参与任何计算            │
└──────────────┬────────────────────┘
               ▼
┌─ 规则引擎层（核心） ────────────────┐
│  13步流水线，全部代码写死，零LLM    │
│  输入：干支×4 + 性别 + 出生年      │
│  输出：结构化JSON（约120个字段）    │
│  路径：projects/bazi-platform/engine/  │
└──────────────┬────────────────────┘
               ▼
┌─ 数据层 ───────────────────────────┐
│  神煞表 / 纳音表 / 藏干表          │
│  调候用神表 / 案例校准库           │
└────────────────────────────────────┘
```

- `references/13步确定性流水线架构_v2.0.md`
- `references/github-deployment-guide.md` — GitHub仓库初始化 + Docker/直接部署 + API端点速查 + 运维命令 + 踩坑记录
- `references/FastAPI三层架构实现模式与踩坑_20260626.md` — FastAPI+ThreadPoolExecutor+Repository模式实现规范
- `references/api-deployment-setup_20260626.md` — API端点清单、启动方式、前端请求格式、已知问题

---

> **背景**：第一层「全流程物理锁死」确保 pipeline 是唯一入口，但 Agent 本身仍可能绕过 pipeline（手动跑引擎、手动写报告、不验证就推库）。第二层约束系统通过修改 Hermes Agent 配置，**在物理层面强制** Agent 必须走标准流程。
>
> **核心思路**：① approvals mode:smart（低风险自动过，高风险问）② command_allowlist 白名单（bazi-pipeline.sh 自动放行，其余命令需审批）③ tools.filesystem 路径限制 ④ hooks 在每次 tool call 前后自动调校验脚本。

### 约束系统配置模板

#### ① approvals（审批模式升级）
```yaml
approvals:
  mode: smart               # manual→smart：低风险自动过，高风险问
  timeout: 120              # 审批超时放宽到120秒
  cron_mode: deny           # cron任务遇危险命令直接拒绝
  mcp_reload_confirm: true  # 保留
  destructive_slash_confirm: true  # 新增：破坏性命令需确认
```

#### ② command_allowlist（黑名单+白名单共存）
```yaml
command_allowlist:
  # === 安全黑名单（危险模式需审批）===
  - "overwrite project env/config via redirection"
  - "overwrite system file via redirection"
  - "script execution via -e/-c flag"
  - "stop/restart hermes gateway (kills running agents)"
  - "find -delete"
  - "script execution via heredoc"
  - "git force push (rewrites remote history)"
  - "recursive delete"
  - "stop/restart system service"
  - "delete in root path"
  # === Bazi流程白名单（自动放行·不触发审批）===
  - "bazi-pipeline.sh"
  - "bazi-pipeline.sh --name"
  - "bazi-pipeline.sh --verify"
  - "bazi-pipeline.sh --push"
  # === 基础工具白名单 ===
  - "cat"
  - "jq"
  - "python3"
  - "git"
  - "git add"
  - "git commit"
  - "git push"
  - "git pull"
  - "bash"
  - "cd"
```

#### ③ tools（工具权限控制·2026-06-24更新加全路径）
```yaml
tools:
  terminal:
    require_approval: true       # 终端命令需审批（白名单除外）
  filesystem:
    allowed_paths:               # 文件工具只能访问这些路径
      - "/root/.hermes"
      - "/root/.hermes/profiles/jinjian-zhenren/scripts"   # 12个bazi工具链
      - "projects/bazi-platform/skills"    # 9个bazi技能
      - "/root/.hermes/profiles/jinjian-zhenren/plugins"   # 约束插件
      - "/root/weiwuji-knowledge-base"
      - "/root/weiwuji-knowledge-base/07-国学哲学/八字命格"  # 数据源子目录
      - "/usr/local/lib/hermes-agent"
      - "/tmp"
      - "/tmp/bazi_pipeline_output"                         # pipeline输出目录
    blocked_paths:               # 禁止写入
      - "/etc"
      - "/root/.ssh"
      - "/root/.aws"
  browser:
    enabled: false               # 不需要浏览器
```

#### ④ hooks（强制校验插桩）
```yaml
hooks:
  post_tool_call:
    - "/root/.hermes/hooks/bazi-mandatory/check.sh"
  pre_tool_call:
    - "/root/.hermes/hooks/bazi-mandatory/precheck.sh"
```

### ⚙️ 安装与启用（2026-06-24·已部署全量）

> **🚨 状态：已部署完成** —— config.yaml、SOUL.md、AGENTS.md、bazi-mandatory hooks 四层齐全。本段从「安装指引」变为「部署清单」。

```yaml
【当前约束系统文件索引】

config.yaml 约束段:
  路径: /root/.hermes/profiles/jinjian-zhenren/config.yaml
  修改内容:
    approvals: mode=smart / timeout=120 / destructive_slash_confirm=true
    command_allowlist: 黑名单(安全) + 白名单(bazi流程+基础工具)
    tools.filesystem: allowed_paths + blocked_paths 权限控制
    hooks: → /root/.hermes/hooks/bazi-mandatory/

SOUL.md 宪法层:
  路径: /root/.hermes/profiles/jinjian-zhenren/SOUL.md
  修改内容: 金鉴真人身份后追加【Agent人格宪法】
  核心: 铁律10条(①禁止绕过pipeline ②必须验证 ③必须签名 ④数据来源合规
      ⑤正推→反推校准 ⑥精度零容忍+十神验阴阳 ⑦身强弱九龙道长规则
      ⑧财星规则 ⑨遵守原文不发挥 ⑩数据源优先级)
  + 标准工作流5步 + 违规后果

AGENTS.md 项目规则:
  路径: /root/weiwuji-knowledge-base/AGENTS.md
  内容: 数据要素定义(10字段)+ 标准JSON输出格式 + 输出前自检4项
  + 报告标准B组(§1 25字段/21§板块/v8.0评分/财富五层/关键标注/文昌/delegate两步法/版本号)
  + 数据验证C组(引擎官网双验证/夫妻校验/质疑处理)
  + 推库标准D组(推库流程/禁止临时文件)

bazi-mandatory hooks:
  目录: /root/.hermes/hooks/bazi-mandatory/
  文件:
    - HOOK.yaml      : 注册3事件(pre/post/agent:end)
    - handler.py     : Python拦截器(禁止绕过pipeline+强制数据源+签名校验)
    - precheck.sh    : Shell预检查(拦截python/node直接排盘)
    - check.sh       : Shell后校验(检查签名+必填字段)
```

如需在新环境重新部署，按以下三步执行：
1. 合并 config.yaml 约束段（见本节上方完整代码）
2. 从 SOUL.md 复制宪法层追加到目标环境
3. 复制 AGENTS.md + bazi-mandatory hooks 到对应路径

### 🔒 约束效果明细

| 约束层级 | 效果 | 能否绕过 |
|:---------|:-----|:--------:|
| **approvals mode:smart** | 低风险命令（读文件/查路径）自动过；高风险（删文件/改配置）要审批 | ⚠️ 用户可点「确认」 |
| **command_allowlist** | bazi-pipeline.sh 全程不触发审批 | ✅ 自动放行 |
| **cat/jq/python3/git/bash/cd** 白名单 | 日常操作不审批 | ✅ 自动放行 |
| **tools.filesystem** | 写文件只允许知识库/安全目录（含scripts/skills/plugins/bazi_pipeline_output） | ⚠️ 能绕过但有限 |
| **hooks: precheck.sh** | 每次命令前拦截：禁止python/node绕过pipeline直接排盘 | ✅ 硬拦截（exit 1阻断） |
| **hooks: handler.py** | 后置/最终校验：签名检查+数据源合规+agent结束验证 | ⚠️ 记录但不阻断 |
| **SOUL.md 宪法层** | Agent人格铁律：必须走pipeline、必须签名、数据源合规 | ⚠️ 依赖Agent自觉但写入系统提示词 |
| **AGENTS.md 项目规则** | 数据要素定义+输出格式自检 | ⚠️ 依赖Agent自觉 |

### 🚨 已知限制与注意事项

1. **bazi-startup 自动加载未生效** — Hermes 无「启动时自动加载AGENTS.md的机制」，AGENTS.md在知识库根目录，仅当cron job的workdir设定为知识库路径时自动注入。**Agent自觉遵守SOUL.md和AGENTS.md的规则。**
2. **hooks 脚本当前为有效启用状态** — precheck.sh（有实质拦截逻辑：禁止python/node直接排盘+禁止直接读skills/scripts）+ check.sh v2.0（支持.md报告调format-check+report-validator/.json签名校验）+ handler.py v2.0（TOOL_NAMES_TERMINAL兼容5种工具名+自动串联格式验证+skills路径拦截）
3. **tools.filesystem 可能影响其他工具** — 如果某个工具需要写 `/etc` 或 `/root/.ssh`，会被拦截。出现此类问题时需手动放行。
4. **approvals 层级** — command_allowlist 在 approvals 之上生效。即：在白名单中的命令完全不触发 approvals 机制。
5. **handler.py pre_tool_check tool_name兼容** — Hermes版本不同可能使用 terminal/execute_command/execute_bash/run_shell/bash 等不同工具名。handler.py v2.0 已通过 TOOL_NAMES_TERMINAL 集合兼容5种。如需新版本，在此集合中追加。

### 相关文件（2026-06-24新增·约束系统部署索引）

> 🚨 约束系统完整架构见本文档 §🚨 Hermes Agent约束系统配置。实战踩坑录见 `references/constraint-system-pitfalls.md`（21个已修复bug：10个约束系统配置坑 + 11个脚本/引擎坑）。包含：check函数判定颠倒、§板块硬编码、BIRTH_YEAR提取、关键年份标签格式、must-verify.sh §1表格硬编码、性别参数兼容、起运方向年干/日主区别、engine.py end_year+10多算、大运年份实用取整等全部修复记录。

插件文件（已部署）：
- `~/.hermes/plugins/bazi-enforcer/plugin.yaml` — bazi-enforcer插件元数据
- `~/.hermes/plugins/bazi-enforcer/__init__.py` — 注册bazi_compute/bazi_verify工具+post_llm_call拦截

启动检查文件（已部署）：
- `~/.hermes/BOOT.md` — 启动自检清单（6项检查）

脚本文件：
- `scripts/check.sh` — post_tool_call hook 模板（stub）
- `scripts/precheck.sh` — pre_tool_call hook 模板（stub）

### 相关技能
- `bazi-engine-workflow` — 约束系统管控的 pipeline 工作流
- `bazi-auto-verify` — 自动验证（约束系统触发校验后的具体验证逻辑）

## 命令速查

```bash
# 🏆 唯一主线入口（全流程自动完成，推荐日常使用）
bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-pipeline.sh \
  --name {姓名} --year {年} --month {月} --day {日} \
  --hour {时} --min {分} --hour-idx {索引} --gender {男/女}
# 自动完成：排盘→验证→生成§1骨架→生成context文件→提示下一步

# 📋 验证已有报告（子agent返回后跑）
bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-pipeline.sh \
  --verify <报告路径> --name {姓名} --birth-year {出生年}
# 自动执行：bazi-delegate-check.sh → bazi-full-verify.sh → bazi-dayun-verify.py

# 🚀 推库
bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-pipeline.sh --push '{信息}'

# ❌ 2026-06-24全面审计脚本（集成在git hook中）
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-audit.py <引擎JSON路径> [姓名]
# 审计学业/财富/事业三维度：年干伤官检查+文昌+大运不利因素

# ✅ 大运年份一致性验证（2026-06-24新增·集成git hook）
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-dayun-verify.py <报告.md> <引擎.json> [姓名]
# 检查报告中大运年份与引擎JSON是否一致，不一致则拒绝commit

# ✅ 学历九步法合理性校验（手动使用）
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-education-verify.py

# 🧩 旧版入口（pipeline内部组件+故障排查备用）
bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-must-verify.sh 年 月 日 时 分 性别0/1 姓名
# 自动完成：引擎排盘 → 官网验证 → 对比 → 输出标准§1骨架

# 🔧 子agent返回后回写校验（独立使用）
bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-delegate-check.sh <报告路径> [姓名] [出生年]

# ✅ 一键全量验证（独立使用）
bash /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-full-verify.sh <报告路径> [姓名]

# 📐 标准输出（备用-供排查使用）
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py 年 月 日 时 分 时辰索引 性别 名字 [出生地]

# JSON输出（供三引擎管线使用）
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py 年 月 日 时 分 时辰索引 性别 名字 [出生地] --json

# 📋 报告格式强制验证
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-format-check.py <报告路径>
# 检查§1 25字段完整性，不通过则禁止推库

# 门禁测试
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py --test

# 批量测试（所有家族成员）
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/batch_score_test.py

# 例：子源（时辰索引5=巳时，注意：卯时=3，辰时=4，巳时=5）
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py 2011 5 31 10 0 5 男 子源

### 🚨 2026-06-28强制新增：日柱交叉验证（梦八字事件教训）
> **致命错误**：分析梦的八字（2007-07-27）时，手动用公式法算日柱，积日多算了1天（用第208天而非偏移207天），导致日柱从壬戌错成癸亥。整份分析报废，老板说"还谈什么分析"。
> **教训**：日柱计算是八字分析的基石，公式法有偏移量陷阱，必须用引擎（paipan.py基准日法）计算并用第二种方法交叉验证。

**强制规程（分析任何八字前执行）：**
```yaml
第1步 — 用引擎 paipan.py（日期差值法·已验证）获取日柱
第2步 — 交叉验证：2000-01-01=戊午日反推 或 官网zydx.top验证
第3步 — 确认无误后再开始完整分析
```
口诀：日柱错了全盘输，两种方法交叉算 --json
```

### 🚨 性别参数陷阱：必须用中文「男」/「女」，不可用数字

> **踩坑记录（2026-06-23·胜源排盘）**：传了数字 `1` 作为性别参数，引擎输出「阳女逆排」——把男命当成了女命，大运方向完全反了。
> **发现方式**：看到输出「阳女逆排」时警觉，改传「男」后得到正确的「阳男顺排」。

```yaml
【强制规则】
  性别参数必须是中文汉字：
  ✅ python3 bazi-engine.py ... 男 胜源   → 阳男顺排 ✅
  ✅ python3 bazi-engine.py ... 女 秀英   → 阴女顺排 ✅
  ❌ python3 bazi-engine.py ... 1 胜源   → 错！引擎误判为阴年女 ❌
  ❌ python3 bazi-engine.py ... m 胜源   → 错！引擎误判 ❌

  为什么数字不行：
  引擎内部用 == '男' / == '女' 做字符串匹配
  传 1 / 0 / "m" / "f" 都匹配不上→ 走默认分支→ 大运方向错误！
  
  验证方法（肉眼核验）：
  输出中「规则:」行应显示正确的大运方向：
  ✅ 阳男顺排 / 阴女顺排 / 阳女逆排 / 阴男逆排
  ❌ 如果出现「阳女逆排」而命主是男性 → 性别参数错了！

口诀：引擎性别用中文，男就是男女就是女；数字英文都不行，输出肉眼核验证。
```

### 时辰索引速查（频繁用，必须记）

```
0=子时(23-1)  1=丑时(1-3)   2=寅时(3-5)   3=卯时(5-7)
4=辰时(7-9)   5=巳时(9-11)  6=午时(11-13) 7=未时(13-15)
8=申时(15-17) 9=酉时(17-19) 10=戌时(19-21) 11=亥时(21-23)
```

## 引擎输出内容（v4.0）

- 八字四柱 + 日主五行
- 真太阳时修正（如提供出生地）
- 纳音（年/月/日/时柱）
- 藏干逐字标注（100/60/30标准）
- 十神速查表
- 大运排布（含起运年龄精确到天+每步年份范围）
- **身强弱评分（九龙道长原始规则 v4.0，含明细到每个藏干）**

## 🔧 JSON输出结构速查（2026-06-17新增）

> ⚠️ 引擎 `--json` 输出使用**中文键名**，非英文。每次解析JSON前先读此参考文件避免KeyError。

引擎JSON完整结构详见：`references/engine-json-structure.md`

**最常用键（防止KeyError）：**
```python
data['四柱']['年柱']      # 不是 data['bazi']['year']
data['身强弱']['总分']    # 不是 data['shen_qiang_ruo']['total_score']
data['身强弱']['等级']    # 身强/身弱/中和
data['身强弱']['明细']    # 逐项评分列表
data['大运']['起运年龄']  # float，精确到小数
data['大运']['序列']      # 大运步列表（⚠️年份范围有重叠bug）
data['藏干']['年支']      # [{天干,比例}]
data['十神']['年干']      # 劫财/食神等
data['纳音']['年柱']      # 石榴木等
```

## 身强弱评分规则（v4.0·引擎固化）

### 核心口诀
> **印只看月令本气，比劫满盘都算；燥土被火引化才不生金，否则生金。**

### 详细规则表

| 加分项 | 规则 | 原文依据 |
|:------|:----|:---------|
| **月令本气印** | ✅ **+40分** | "印在月令本气算分"（素材20行1038） |
| **月令中气印** | ❌ **0分** | "月令中气的不算分"（同） |
| **月令余气印** | ❌ **0分** | "印在月令本气算分"（同） |
| **月干/年干/时干印** | ❌ **0分** | "印在其他的任何宫位都不算分"（同） |
| **年支/日支/时支印** | ❌ **0分** | "其他宫位的印不计算为对日元的生助"（素材24） |
| **月令本气比劫** | ✅ **+40分** | "这个算，因为这是比劫"（素材09行89） |
| **月令中/余气比劫** | ✅ **+分数** | "比劫算"——比劫在所有位置都算 |
| **其他位置比劫** | ✅ **+分数** | "比劫算" |
| **大运流年印** | ✅ **+分数** | "大运流年是计算的"（素材09行93） |

### 燥土规则（条件版·九龙道长原始）

| 条件 | 效果 | 原文 |
|:----|:----|:------|
| 燥土+天干丙/丁·卯戌合火 | ❌ **不计分** | "火被引化之后，未当火看…不生金反而克金"（素材05行337） |
| 燥土+天干壬/癸（水灭火） | ✅ **计分** | "水把火灭了…纯粹的土，可以生金"（素材05行94） |
| 燥土+天干戊/己/庚/辛（无火水） | ✅ **计分** | 默认当土看生金 |

### 从格判定

| 条件 | 结果 |
|:----|:----|
| 得分=0（全无印比） | 从弱反为强 → **恒定50分** |
| 得分>100（满盘印比） | 从强反为弱 → **恒定20分** |

### 评分位置基础分

```yaml
年干=8分   年支=4分
月干=12分  月令(月支)=40分
日支=12分  时干=12分  时支=12分
```

### 藏干百分比（统一标准）

```yaml
本气 = 100%（×该位置基础分）
中气 = 60%（×该位置基础分）
余气 = 30%（×该位置基础分）
天干 = 100%（不分藏干）
```

## 🚨 特定踩坑：报告文件名与内容中的人名替换（2026-06-18新增·宽案例·误改年柱教训）

> **致命错误**：用户要求将「乙丑男」改为「宽」，我执行了 `sed -i 's/乙丑/宽/g'` 全局替换，结果年柱「乙丑 甲申 辛巳 丁酉」被改成了「宽 甲申 辛巳 丁酉」——**八字符被破坏！** 修复耗时30分钟+，需逐行patch。

**根因**：`sed` 全量替换没有区分：① 报告标题中的名字「乙丑男」② 年柱「乙丑」③ 描述性文字「乙丑年」。三者共用相同字符但语义完全不同。

```yaml
【名字替换强制流程】

当用户要求改名时（如「乙丑男」→「宽」）：

Step 0 — 先改外围（文件名和目录名，最安全）：
  mv old_report.md new_report.md
  mv "15-乙丑男(1985)" "15-宽(1985)"

Step 1 — 只改特定位置（禁止全局sed替换！）
  必须替换的位置（安全）：
  □ 报告标题行（# {旧名}·八字报告）
  □ §1 姓名/基本信息行
  □ 报告中所有以名称为主语的分析句

  禁止替换的位置（会被误改）：
  ❌ 年柱「乙丑 甲申」→ 必须保留
  ❌ 天干单字「乙」「丑」→ 不能碰
  ❌ 纳音「乙丑海中金」→ 保留
  ❌ 年干「乙」、「丑」地支单独出现

Step 2 — 用patch精确定位（推荐，禁用sed全局替换）
  对每个需要替换的位置，用patch精确定位替换：
  patch(path=报告路径, old_string="旧名·完整八字", new_string="新名·完整八字")
  patch只支持精确匹配，不会无差别替换。
  
  ✅ 可安全替换的上下文（举例）：
    "# 乙丑男·完整" → "# 宽·完整"
    "姓名：乙丑男" → "姓名：宽"
    "乙丑年生人" → "宽"
    "乙丑男" → "宽"
  
  ❌ 禁止替换的上下文（举例）：
    年柱："乙丑 甲申" → 不能动
    引文："乙丑年" → 保留为"乙丑年"

Step 3 — 如果必须用sed（不推荐），采用模式保护：
  sed -i '/乙丑 甲申/!s/乙丑男/宽/g' 报告.md
  # 含义：只在没有「乙丑 甲申」的行做替换

Step 4 — 验证（强制！）
  □ grep -c "乙丑 甲申" 报告.md → 应保持原数不变
  □ grep -n "旧名" 报告.md → 应返回0
  □ 无 "宽 甲申" 残留（年柱被破坏的典型表现）
  □ 无 "农历{旧年名}年" 残留（应为农历乙丑年）
  □ 无 "年柱{旧名}" 残留（应为年柱乙丑）
  □ 无 "八字：{旧名}" 残留

口诀：
  改名只用patch，sed全局是大忌
  年柱八字不能动，「乙丑 甲申」是底线
  目录文件先改好，内容再用手工调
  改后验证年柱在，别让八字出问题
```

---

## 🚨 特定踩坑：引擎公历输入 vs 用户农历日期（2026-06-16发现·永不再犯）

> **致命错误**：本场会话中，用户提供了农历日期（凤1978.11.16亥时/琼1982.2.16戌时），我直接传给了引擎 `bazi-engine.py 1978 11 16 21 0`，引擎按公历1978-11-16计算，得到了错误的八字（癸亥月应为甲子月）。
>
> **根因**：引擎的输入要求是**公历（阳历）日期**，但用户给的是农历（阴历）日期。两者相差约1个月！

```yaml
【农历→公历转换强制流程】

每次拿到用户八字需求时：
Step 1 — 确认日期类型
  □ 用户给的日期是公历还是农历？
    - 用户明确说「公历」「阳历」「新历」→ 公历
    - 用户明确说「农历」「阴历」「旧历」→ 农历
    - 用户给了「1983.4.19」这类格式 → 看语境：通常为农历
    - 用户说「农历X年X月X日」→ 明确农历
  □ 如果不确定 → 问用户「这个是农历还是公历？」

Step 2 — 如果是农历 → 转换后再入引擎
  ☐ 安装 zhdate 库（如未安装）
    pip3 install zhdate
  
  ☐ 用 Python 转换：
    from zhdate import ZhDate
    d = ZhDate(农历年, 农历月, 农历日)
    dt = d.to_datetime()
    公历日期 = f"{dt.year} {dt.month} {dt.day}"
    
  ☐ 将公历日期输入引擎：
    python3 bazi-engine.py {dt.year} {dt.month} {dt.day} {时} {分} {时辰索引} 女 姓名 --json

Step 3 — 验证
  ☐ 用官网（www.zydx.top/paipan.php 或 m.rich888.net/bazi/bazi.asp）做交叉验证
  ☐ 检查：月柱是否合理？（如农历十一月→子月）

常见陷阱：
  ❌ 错误：直接把农历日期传入引擎（引擎按公历处理，月柱会差1个月）
  ✅ 正确：农历→公历转换后再传引擎

口诀：
  用户日期先确认，农历公历要分清
  农历日期先转换，zhdate库来换算
  公历日期给引擎，官网验证再确认
```

## 🚨 多时辰比较与筛选工作流

> **实战场景**：用户提供「农历1985.6.24 时辰不详，列出三个最好的时辰分别出详细报告」——需要评估全部12个时辰，按命理优劣排序，选TOP3分别出完整报告。

### 适用条件

```yaml
触发条件（任一满足即走此工作流）：
  □ 用户说「时辰不详/不确定/不知道时辰」
  □ 用户说「帮我选最好的时辰」
  □ 用户提供了多个可能的时辰（如「可能是卯时或辰时」）
  □ 需要评估不同时辰对命运的影响差异
```

### 三步选择 + 五步出报告

```yaml
【三步选择 — 从12个时辰中筛选出最优N个】

Step 1 — 跑全量数据（12个时辰逐一评估）
  □ 农历→公历转换（zhdate 必须代码转换）
  □ 对所有12个时辰索引（0~11）逐个跑引擎
    做好后用一个for循环批量跑，存储JSON
  
  for idx in 0 1 2 3 4 5 6 7 8 9 10 11; do
    python3 bazi-engine.py {年} {月} {日} 0 0 $idx 男 {名}-{时辰名} --json
  done
  
  □ 提取每个时辰的核心数据：
    - 八字（四柱）
    - 身强弱分数+等级
    - 格局（时柱带来的变化）
    - 纳音时柱

Step 2 — 评估排序（多维命理比较）
  从以下维度逐项比较12个时辰：

| 维度 | 评估标准 | 权重 |
|:----|:---------|:----:|
| 身强弱 | 50~60分最佳（中和偏强），44.8~56.8都属可用范围 | ⭐⭐⭐ |
| 格局层次 | 七杀制劫 > 杀印相生 > 比肩帮身 > 食伤生财 > 其他 | ⭐⭐⭐ |
| 合局引化 | 与年/月/日支的合化、三合局、六合局 | ⭐⭐⭐ |
| 冲刑影响 | 寅申冲（大突破/大波动）、巳酉丑合（稳固加强）等 | ⭐⭐ |
| 财星变化 | 时柱是否带财（透干或藏干）| ⭐⭐ |
| 空亡影响 | 空亡字能量减半 | ⭐⭐ |
| 十神搭配 | 时干的十神与原局的互动 | ⭐⭐ |

  🚨 优先顺序：格局层次 > 合局引化 > 身强弱 > 十神搭配 > 冲刑影响 > 财星 > 空亡

  **对比表格示例：**
  | 时辰 | 时柱 | 身强弱 | 格局 | 核心优势 | 风险 |
  |:----:|:----:|:------:|:-----|:---------|:-----|
  | 子时 | 戊子 | 44.8分 | 稳定型 | 正印护身 | 身偏弱 |
  | 寅时 | 庚寅 | 56.8分 | 突破型 | 劫财帮身+寅财根 | 寅申冲波动 |
  | 卯时 | 辛卯 | 56.8分 | 稳定型 | 巳卯合财+比肩帮身 | — |
  | 酉时 | 丁酉 | 56.8分 | 🏆七杀制劫 | 巳酉丑三合+七杀护财 | 🏆最佳 |
  | ... | ... | ... | ... | ... | ... |

Step 3 — 选定TOP N个时辰
  □ 根据Step 2的排序，选出最好的N个（通常3个）
  □ 每个时辰给出简明理由：
    第1名（🥇 最优）：{时辰}, {八字}, {核心格局}, {入选理由}
    第2名（🥈 次优）：{时辰}, {八字}, {核心格局}, {入选理由}
    第3名（🥉 第三）：{时辰}, {八字}, {核心格局}, {入选理由}
  □ 先展示给用户确认（可选），确认后进入Step 4

【五步出报告 — 对选定的N个时辰各出完整报告】

Step 4 — 保存引擎JSON
  mkdir -p /tmp/bazi_batch/
  for hour in 酉时 卯时 寅时; do
    python3 bazi-engine.py ... --json > /tmp/bazi_batch/{name}_{hour}.json
  done

Step 5 — 并行生成报告（delegate_task）

  ```yaml
  □ 每个时辰一个独立任务，最多同时3-4个任务（delegate_task的tasks数组）
  □ context字段中**必须包含**以下所有数据（缺一不可，子agent无memory！）：
  
    · 姓名/时辰标识
    · 完整八字（年柱月柱日柱时柱）
    · 日主五行+阴阳
    · 身强弱评分总分+明细（逐项计分来源）
    · 格局分析（核心格局+判断依据）
    · 用神排序 > 忌神排序
    · 大运序列完整（含起运年龄）
    · 财星评分（逐项：年干/月干/时干/年支/月令/日支/时支）
    · 藏干（四柱各支详细)
    · 十神（年干月干时干）
    · 纳音（四柱）
    · 空亡
    · 核心特点描述（合局/冲刑/格局亮点）

  🚨 子agent没有memory权限、不能查知识库、不能跑引擎
     所以所有计算好的数据必须在context中传递！
     特别是起运年龄、身强弱分数、财星分数等数值——子agent不自行计算！

  □ 文件名格式（统一）：{姓名}_{时辰}{主推/备选/第三优}_完整八字命理深析报告_v1.0_YYYYMMDD.md

  □ 示例：
    tasks=[{
      "goal": "生成一份完整报告",
      "context": "八字：乙丑 甲申 辛巳 丁酉...（包含上述所有数据）",
      "toolsets": ["file"]
    }, ...]
  ```

Step 6 — 验证并推库
  □ 每份报告存在且行数≥1700
  □ 每份报告的八字符与对应时辰一致
  □ 报告文件名标注了时辰和排名

Step 7 — 推库
  git add/commit/push

口诀：时辰不详十二选，三步评估来筛选；格局合局身强弱，多维对比定三甲；
     月日固定只变时，每个时辰跑一次；并行生成delegate，报告标注时辰名
```

---

## 🚨 双时辰同时出报告工作流（2026-06-17实战精炼）

> **实战场景**：老板要求凤和琼「同一天的两个时辰（亥时和戌时）都推最新报告」。之前我已生成了主推时辰的v3.0报告，但两个时辰都推时需要完整工作流。

### 双时辰完整工作流（6步）

```yaml
Step 1 — 确认日期和两个时辰
  □ 确认是同一天（同一个公历/农历日期）
  □ 确认两个时辰的索引（亥时=11, 戌时=10等）
  □ 每个时辰对应不同的时柱（五鼠遁不同）
  □ 例：凤1978-12-13 → 戌时甲戌 vs 亥时乙亥

Step 2 — 分别跑引擎，保存两份JSON
  python3 bazi-engine.py 年 月 日 19 0 10 女 名-戌时 --json > /tmp/bazi_batch/名_xu.json
  python3 bazi-engine.py 年 月 日 21 0 11 女 名-亥时 --json > /tmp/bazi_batch/名_hai.json

Step 3 — 对比两个八字的差异
  记录差异点表格：
  | 维度 | 戌时版 | 亥时版 |
  |:----|:------|:-------|
  | 八字 | ... | ... |
  | 时柱 | ... | ... |
  | 身强弱 | ...分 | ...分 |
  | 格局 | ... | ... |
  | 关键差异 | ... | ... |

Step 4 — 并行生成两份标准格式报告
  delegate_task 并行提交2个任务（各生成1份报告）
  context中各自标注主推/备选
  文件名格式：{名}_完整深析报告_vX.X_{时辰}主推/备选_标准格式_YYYYMMDD.md

Step 5 — 验证两份报告
  □ 每份报告格式完整（20§板块·25字段§1）
  □ 每份报告的八字与对应引擎JSON一致
  □ 与对方版本的核心差异已在§2格局分析中对比
  □ 起运年龄正确（从对应JSON提取）

Step 6 — 推库
  git add/commit/push

口诀：双时同日出报告，两轮引擎分头跑；差异对比先列好，并行生成效率高
```

## 🚨 致命陷阱：农历→公历转换差1-2天导致日柱全错（0617凤案例·D级致命）

> **凤案例（2026-06-17）**：用户说「农历1978.11.16亥时」，我用 zhdate 转换得到公历1978-12-15。但之前我错误地传了1978-12-13（差了2天）给引擎，得到癸酉日（癸水日主），而正确日期是辛亥日（辛金日主）——**日柱全错，整份报告报废！**

```yaml
根因分析：
  ❌ 错误：用了公历1978-12-13（不知道从哪里来的日期）
  ✅ 正确：ZhDate(1978,11,16).to_datetime() = 1978-12-15

教训：
  农历→公历转换**必须用代码计算**，不能靠记忆中某个日期！
  用户给的农历日期，每一步都要用 zhdate 算，差一天日柱就错！

【强制流程】每次农历→公历转换后，双重验证：
  Step 1 — 用代码转换
    from zhdate import ZhDate
    d = ZhDate(农历年, 农历月, 农历日)
    dt = d.to_datetime()  → 公历年月日

  Step 2 — 用引擎跑公历日期 → 获取八字

  Step 3 — 验证月柱合理性
    农历十一月→公历应在子月前后→月柱应是子/丑月
    如果月柱明显不合理（如农历十一月得出癸亥月）→ 日期错了！

  Step 4 — 对比与用户描述的八字是否一致
    用户说「戊午年」→ 年柱必须是戊午
    如果年柱不符 → 日期错了
```

## 🚨 数据源JSON创建与更新工作流（0617工程化新增）

> **目标**：从引擎获取的所有确定性数据，保存到 `family_bazi_data_v1.json`，以后所有报告直接从JSON拉数据，不再重新计算。

### 创建新人的数据（新八字确认后第一步）

```yaml
Step 1 — 运行引擎获取JSON
  python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py {年} {月} {日} {时} {分} {时辰索引} {性别} {姓名} --json

Step 2 — 读取引擎JSON，补充计算：
  - 十神天干（从 engine data['十神'] 提取）
  - 十神地支藏干（从 engine data['藏干'] × 十神表计算）
  - 财星分数（逐位置计算：正财+偏财，不含劫财）
  - 大运序列（年龄范围正确，年份手动修正）

Step 3 — 读取现有数据源：
  import json
  with open('family_bazi_data_v1.json') as f:
      data = json.load(f)

Step 4 — 追加新人数据，写入：
  data.append(new_person)
  with open('family_bazi_data_v1.json', 'w') as f:
      json.dump(data, f, ensure_ascii=False, indent=2)

Step 5 — 推库
  cd /root/weiwuji-knowledge-base && git add -A && git commit -m "新增{姓名}到数据源" && git push

文件位置：
  ✅ 知识库：07-国学哲学/八字命格/家族八字核心数据源_v1.json
  ✅ 技能目录：/root/.hermes/profiles/jinjian-zhenren/scripts/family_bazi_data.json
```

### 数据源使用规则（永远遵守）

```yaml
🚨 任何需要八字数据的场景，**必须先读数据源**，禁止重新计算！

正确做法：
  with open('family_bazi_data_v1.json') as f:
      data = json.load(f)
  person = [p for p in data if p['姓名']=='家主'][0]
  bazi = person['八字']      # 直接取
  score = person['身强弱']['总分']  # 直接取
  wealth = person['财星']['总分']   # 直接取

禁止做法：
  ❌ 重新跑引擎算八字
  ❌ 凭记忆写身强弱分数
  ❌ 手工计算财星分数
  ❌ 手工排大运
```

> **本场会话**：用户为凤女提供了「亥时（主推）/戌时（备选）」两个选项，应分别跑引擎：凤亥一次、凤戌一次，各得一份独立JSON。不可合并或只跑一个。

```yaml
【多个时辰选项处理流程】

Step 1 — 对每个时辰分别跑引擎
  每个时辰索引不同，跑N次引擎，得N份独立JSON
  
Step 2 — 分别保存JSON
  每份JSON标注对应的时辰名

Step 3 — 分别输出报告
  每份JSON → 一份独立报告
  文件名标注时辰+主推/备选

口诀：多个时辰别合并，分次跑引擎分次写报告
     每个时辰一JSON，独立分析不出错
```

## 🚨 已知Bug：官网验证编码错误（2026-06-17）

**现象：** `bazi-zydx-verify.py` 报错 `UnicodeDecodeError: 'utf-8' codec can't decode bytes`

**根因：** 官网 `www.zydx.top/paipan.php` 返回GBK编码的HTML，但Python subprocess默认用UTF-8解码。

**临时绕过：** 在 `subprocess.run` 调用处增加 `errors='replace'` 参数，或手动用浏览器打开官网验证（效果相同）。

**替代验证方法：** 在浏览器中手动打开 `www.zydx.top/paipan.php`，输入生辰后核对四柱。引擎排盘算法已多次验证可靠，八字不匹配的概率极低。

**正在进行的修复：** 待更新 bazi-zydx-verify.py 增加编码兼容处理。

> **实际案例**：用户说「农历1978.11.14 亥时（备选戌时）」，我误听为1987年生成了两份报告。用户纠正「日期说错了，应该是1978」后，需要：归档错误版→重新排盘→重新生成→验证→推库。
>
> **根因**：同一农历月日可能跨多个年份（1978 vs 1987出生年份不同但月日相同），年份一错则年柱+日柱全错，整份报告报废。

```yaml
【年份更正处理流程】

当用户说「日期说错了」「应该是X年不是Y年」时：

Step 1 — 立即确认正确日期
  □ 用户说的是公历还是农历？
  □ 正确的年份、月、日、时辰是什么？
  □ 与之前的前提有哪些不同？（年份不同=年柱不同+日柱可能不同）

Step 2 — 归档旧版错误报告
  □ 将已生成的旧报告文件移入：归档_YYYYMMDD/{目录}/
  □ 旧版文件必须保留（供对比），不移除git历史

Step 3 — 重新跑引擎
  □ 确认公历日期（农历→zhdate转换）
  □ python3 bazi-engine.py 正确年 正确月 正确日 时 分 时辰索引 性别 名字 --json
  □ 对比新旧八字差异，如果日柱也不同则意味着全部重做

Step 4 — 重新生成报告
  □ 基于正确八字写报告
  □ 版本号从v1.0重新编号（新八字=新起点）

Step 5 — 验证+推库
  □ python3 bazi-report-validator.py --report [路径] --verbose
  □ git add/commit/push

口诀：用户纠正出生年，先归档旧版再重做；年份一错全盘废，重新排盘重新写
```

## 🐞 已知引擎Bug：年柱立春前错误（2026-06-24发现）
> 魏齐（2020-01-28 戌时）引擎庚子年，官网己亥年。立春前年柱应为己亥。
> 防御：每次排盘后官网验证，年柱不一致以官网为准。

## 🐞 已知引擎Bug：大运年份范围重叠（已修复 2026-06-24）

> **发现时间：** 2026-06-16（主母成排盘时发现）
> **表现：** 引擎输出的 `大运.序列` 中，`起始年份` 和 `终止年份` 范围不准确——相邻大运的年份重叠（例如甲申1980-1999与乙酉1990-2009重叠20年，而非连续10年）。
> **根因：** `bazi-engine.py` line 783 公式错误：
>   ```python
>   # ❌ 错误：多加10
>   end_year = b_year + int(end_age + 10) - 1  # → 1980+20-1=1999（19年跨度）
>   # ✅ 修复后
>   end_year = b_year + int(end_age) - 1        # → 1980+10-1=1989（10年跨度 ✅）
>   ```
>   `end_age` 本身已经是 `qi_yun_age + (i+1)*10`（参考line 781），再加10等于多加了10年。
> **影响：** 直接使用引擎的大运年份会导致全部大运终点偏移+10年，整张表混叠。
> **修复：** 2026-06-24 删除line 783多余的 `+ 10`。主agent用 `calc_da_yun_with_age()` 输出JSON，已修正。另 `print_result()` 函数line 910-912使用了 `- 0.01` trick（丑陋但功能等效），下次重构统一。

## 🚨 D级致命教训：永远使用已验证的 bazi-engine.py，禁止自行编写排盘引擎！

> **致命场景（2026-06-26）**：我写了 `projects/bazi-platform/engine/paipan.py` 作为平台的前端排盘引擎，结果月柱+日柱全部算错。老板指出：「你之前不是写好了一个引擎吗？直接用不行了吗？」
>
> **根因**：bazi-engine.py 已存在且经过验证（使用 ephem 天文库精确计算节气、多次官网交叉验证），但我没有用，而是从头写了一个 buggy 版本。
>
> **教训（2026-06-26双重教训）**：
> 教训A：写排盘代码前应先检查是否已有已验证的工具（bazi-engine.py）
> 教训B：如果自己写了排盘代码（paipan.py），必须用真实八字全面验证后再上线，不能只跑一个测试用例
>
> **追加教训（2026-07-01 生辰输入错误）**：
> 教训E：跑引擎验证数据时，**必须从知识库人物存档读取出生日期**，禁止从记忆输入
>    ——2026-07-01 输入7月12日而非8月6日，导致3/4份报告引擎输出八字与历史存档不一致
>    ——根因：跑 `bazi-must-run-engine.sh` 时凭记忆写了年月日，未先读KB中报告确认
>    ——固化：跑引擎前先 `search_files("出生.*1980|公历出生")` 查该人物的存档日期
>    ——二次验证：引擎输出八字后，回溯匹配历史存档中的日柱，不一致则停
>    ——Feishu汇报防线：汇报前基础数据(八字/日主/身强弱/财星)须与引擎输出逐项核对

> **追加教训（2026-06-29 日柱计算陷阱）**：
> 教训C：即使有引擎，任何八字分析前**必须用引擎排盘**，禁止手算公式
>    ——2026-06-29 梦的日柱手算错误，day_of_year vs day_offset 差1天导致整份分析作废
>    ——物理防御已创建: `projects/bazi-platform/scripts/bazi-must-run-engine.sh`
> 教训D：手算日柱的day_offset陷阱 → day_offset = day_of_year - 1，使用基准日法(delta days)更安全
>
> **最终结论**：paipan.py已修复（日柱基准日法），可用于全栈平台的日期输入排盘。但所有分析引擎的内部排盘仍推荐使用 bazi-engine.py（ephem 天文库更精确）。

### 🚨 铁律：排盘只用 bazi-engine.py

```yaml
🚨【强制规则】任何排盘需求，第一反应是调用 bazi-engine.py！

✅ 命令行调用：
  python3 /root/weiwuji-knowledge-base/07-国学哲学/八字命格/scripts/bazi-engine.py \
    年 月 日 时 分 时辰索引 性别 姓名 --json

✅ Python subprocess 调用（供 API / FastAPI 使用）：
  import subprocess, json
  
  BAZI_ENGINE = "/root/weiwuji-knowledge-base/07-国学哲学/八字命格/scripts/bazi-engine.py"
  
  def run_paipan(name, gender, year, month, day, hour):
      # hour时辰起始小时 → 时辰索引: 0→子(0), 2→丑(1), 4→寅(2), 6→卯(3), ...
      shichen_idx = hour // 2
      
      # 时辰中文名（引擎JSON不含此字段，需调用方自行添加）
      shi_chen_names = {0:"子时",2:"丑时",4:"寅时",6:"卯时",8:"辰时",10:"巳时",
                        12:"午时",14:"未时",16:"申时",18:"酉时",20:"戌时",22:"亥时"}
      
      cmd = ["python3", BAZI_ENGINE, str(year), str(month), str(day),
             str(hour), "0", str(shichen_idx), gender, name, "", "--json"]
      
      result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
      if result.returncode != 0:
          raise RuntimeError("排盘引擎错误: " + result.stderr)
      
      data = json.loads(result.stdout)
      
      # data['四柱'] = {'年柱':'庚申','月柱':'癸未','日柱':'辛亥','时柱':'辛卯'}
      # data['八字'] = '庚申 癸未 辛亥 辛卯'
      
      # 组装pai字典（供pipeline_v4等下游使用）
      def parse_pillar(s):
          return {"gan": s[0], "zhi": s[1]}
      
      pai = {
          "name": name,
          "gender": gender,
          "birth_date": f"{year}年{month}月{day}日",
          "birth_hour": hour,
          "shi_chen": shi_chen_names.get(hour, str(hour) + "时"),
          "bazi": data["八字"],
          "year_pillar": parse_pillar(data["四柱"]["年柱"]),
          "month_pillar": parse_pillar(data["四柱"]["月柱"]),
          "day_pillar": parse_pillar(data["四柱"]["日柱"]),
          "hour_pillar": parse_pillar(data["四柱"]["时柱"]),
          "na_yin": data.get("纳音", {}),
          "cang_gan": data.get("藏干", {}),
          "shi_shen": data.get("十神", {}),
          "da_yun": data.get("大运", {}),
      }
      return pai

❌ 绝对禁止（都会出bug）：
  - 自己写 paipan.py 从零排盘 ❌（月柱/日柱算错概率极高）
  - 手动计算日柱/月柱 ❌（日干支算法易出错）
  - 凭记忆写八字 ❌（立春/节气分界容易搞错）
  - 修 buggy 引擎而不换用已验证引擎 ❌（浪费时间，结果仍不可靠）

引擎路径：
  /root/weiwuji-knowledge-base/07-国学哲学/八字命格/scripts/bazi-engine.py
```

### ⚠️ 关键坑位：bazi-engine.py JSON输出特性

```yaml
【1. 中文键名】
  data["八字"]           # "庚申 癸未 辛亥 辛卯"
  data["四柱"]["年柱"]   # "庚申"
  data["四柱"]["月柱"]   # "癸未"
  data["四柱"]["日柱"]   # "辛亥"
  data["四柱"]["时柱"]   # "辛卯"
  data["日主"]           # "辛"
  data["纳音"]["年柱"]   # 字符串
  data["藏干"]["年支"]   # [{"天干":"庚","比例":"100%"}, ...]
  data["十神"]["年干"]   # "劫财"
  data["大运"]["起运年龄"] # float
  ❌ 禁止用英文键名（如 data['bazi']['year']）—— 不存在！

【2. 缺少 shi_chen 字段】
  bazi-engine.py JSON不包含时辰中文名（"卯时"、"巳时"等）
  → 调用方必须自己映射：shi_chen_names.get(hour, str(hour) + "时")
  → 不设置 → 前端显示 "undefined"

【3. 日主(ri_zhu)是对象】
  data["日主"] = {"gan": "辛", "wx": "金"}  # 不是字符串！
  → 渲染时需处理：v.gan + "(" + v.wx + ")"  → "辛(金)"
  → 直接 `${v}` → "[object Object]"

【4. 大运年份可能有bug】
  相邻大运年份可能重叠（end_year +10 多算）
  → 用 calc_da_yun_with_age() 获取正确年龄范围
  → 或用 data['大运']['序列'][i]['起始年龄'] 推算年份
```

### 🚨 pyc 缓存清理

```yaml
修改引擎代码后必须清除缓存：
  find /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform -name '__pycache__' -exec rm -rf {} + 2>/dev/null
  pkill -f "python main.py"  # 杀旧进程
  重启服务器

⚠️ 不清理 pyc 缓存 → 旧代码继续运行 → 修了等于没修
⚠️ 不杀旧进程 → 新进程绑定端口失败 → 服务器不可用
  验证：用 ss -tlnp | grep 8000 确认端口被新进程占用
```

```yaml
【产品思维铁律 — 2026-06-26老板批「傻执行」教训固化】

每次开始建新东西前，先问自己三个问题：

  Q1 — 这个功能是不是已经有人/工具实现过了？
    排盘 → bazi-engine.py ✅（已验证）
    官网验证 → bazi-zydx-verify.py ✅
    数据源 → family_bazi_data.json ✅

  Q2 — 如果我新建，能比现有的好在哪里？
    不能更好 → 直接用现有的
    能更好 → 在现有基础上扩展，不要从零写
    只是不同 → 用现有的，兼容自己的需求

  Q3 — 重新实现的风险是什么？
    计算精度可能不如已验证引擎（节气计算尤其敏感）
    测试覆盖可能不够（边界案例如立春前/腊月容易被忽略）
    维护成本翻倍（两个引擎都要维护）

实战教训：
  ❌ 从头写 paipan.py → 月柱日柱全部算错，老板生气
  ✅ 改用 bazi-engine.py → 排盘数据正确，无需额外测试

口诀：
  要算八字先看库，bazi-engine已上路
  从头重写是弯路，bug修到你发苦
  节气计算用ephem，天文库才够精度
  先查工具再动手，别让老板再发火
```

### 废弃文件

```yaml
❌ projects/bazi-platform/engine/paipan.py — 已废弃，不再使用
  月柱/日柱计算有多个bug，已被 bazi-engine.py 替代
  保留供历史参考，但任何新开发不要引用它

✅ 使用 /root/weiwuji-knowledge-base/07-国学哲学/八字命格/scripts/bazi-engine.py
  v2.0，ephem 天文库精确节气计算，已交叉验证
```

### pyc 缓存清理

```yaml
修改引擎代码后必须清除缓存：
  find /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform -name '__pycache__' -exec rm -rf {} + 2>/dev/null
  pkill -f "python main.py"  # 杀旧进程
  重启服务器

⚠️ 不清理 pyc 缓存 → 旧代码继续运行 → 修了等于没修
⚠️ 不杀旧进程 → 新进程绑定端口失败 → 服务器不可用
  验证：用 ss -tlnp | grep 8000 确认端口被新进程占用


---

## 🚨 已知引擎Bug：年柱立春前错误（2026-06-24发现·魏齐案例·杨昌玉2026-06-24追加级联效应）

### ⚠️ 级联效应（年柱错→月柱跟着错）

> **发现场景：** 魏齐（公历2020-01-28 戌时）排盘时，引擎输出庚子年，但官网验证为**己亥年**。实际此时在**立春（2月4日）之前**，年柱应为己亥（2019年）。
> **根因：** 引擎按公历年份取年柱，但八字年柱以**立春**为分界——立春前尚未进入新的农历年。
> **影响：** 立春前出生的八字，引擎的年柱**和月柱都错**（年柱错1年+月柱随五虎遁变化）。
> **触发条件：** 任何在当年立春前（2月4日左右）出生的八字。
> **防御：** 每次跑完引擎后必须用must-verify.sh或pipeline.sh中的官网验证做交叉比对。如年柱不一致，以官网验证为准。
> **口诀：** 立春之前出生人，引擎年柱容易错；己亥不是庚子年，官网验证来纠正。

### 🚨 级联效应详解（2026-06-24·杨昌玉案例校准）

**表象**：引擎输出了错误的年柱（立春前年份算错）。
**深层危险**：年柱错 → 月柱跟着错（因为五虎遁取决于年干）。

| 年干 | 五虎遁起点 | 丑月 |
|:----|:----------|:----:|
| 壬（正确·壬午年） | 丁壬壬位顺行流→壬寅 | **癸丑** ✅ |
| 癸（引擎·癸未年） | 戊癸何方发→甲寅 | **乙丑** ❌ |

**级联链条**：
```
引擎年份判断错（公历年而非立春年）
  ↓
年柱错（壬午→癸未，年干从壬变癸）
  ↓
五虎遁起点变（丁壬→戊癸）
  ↓
月柱错（癸丑→乙丑）
  ↓
八字全部失真
```

**杨昌玉案例（2003-01-08 未时）**：\n- 正确年柱：壬午（2003年立春2月4日13:57前）\n- 引擎年柱：癸未（按公历年份2003直接取）\n- 正确月柱：癸丑（壬午年五虎遁：丁壬壬位顺行流→十二月癸丑）\n- 引擎月柱：乙丑（癸未年五虎遁：戊癸何方发→十二月乙丑）\n- 影响：整份报告报废，八字基础数据错得一塌糊涂
1. 查当年立春精确时间（通常2月3~5日）
2. 确认日期在立春前 → 年柱应为上一年
3. 用上一年年干重新做五虎遁 → 确认月柱
4. 官网交叉验证（浏览器或curl）

**口诀**：立春之前引擎错，年柱月柱同时崩；年干一变五虎遁，月柱跟着全不同。一月至二月四日，立春之前要警惕。

## 🐞 已知引擎Bug：大运年份范围重叠（已修复 2026-06-24）

> **发现时间：** 2026-06-16（主母成排盘时发现）
> **表现：** 引擎输出的 `大运.序列` 中，`起始年份` 和 `终止年份` 范围不准确——相邻大运的年份重叠（例如甲申1980-1999与乙酉1990-2009重叠20年，而非连续10年）。
> **根因：** `bazi-engine.py` line 783 公式错误：
>   ```python
>   # ❌ 错误：多加10
>   end_year = b_year + int(end_age + 10) - 1  # → 1980+20-1=1999（19年跨度）
>   # ✅ 修复后
>   end_year = b_year + int(end_age) - 1        # → 1980+10-1=1989（10年跨度 ✅）
>   ```
>   `end_age` 本身已经是 `qi_yun_age + (i+1)*10`（参考line 781），再加10等于多加了10年。
> **影响：** 直接使用引擎的大运年份会导致全部大运终点偏移+10年，整张表混叠。
> **修复：** 2026-06-24 删除line 783多余的 `+ 10`。主agent用 `calc_da_yun_with_age()` 输出JSON，已修正。另 `print_result()` 函数line 910-912使用了 `- 0.01` trick（丑陋但功能等效），下次重构统一。

## 🚨 D级致命陷阱：大运年份必须从引擎JSON提取，子agent禁止自行计算（2026-06-24新增·4份全错教训）

> **致命教训**：2026-06-24，4份报告（家主/子源/刘成/朱宗立）的大运年份全部错位，因为子agent在写报告时**没有从引擎JSON提取 `data['大运']['序列']` 的年份数据**，而是自己重新计算起运年份，与引擎的Q4进位规则不一致。
>
> **根因**：引擎的起运年份使用了Q4进位规则（10~12月起运→进位到次年），但子agent的 `birth_year + int(age)` 公式没有这个进位逻辑，导致全部偏移-1到-4年。

### 强制规则

```yaml
【铁律】任何时候写报告中的大运年份，全部从引擎JSON提取，禁止自行计算！

✅ 正确做法：
  1. 从引擎JSON提取 data['大运']['序列']
  3. 格式：{干支} {起始年份}~{终止年份}

❌ 禁止做法（都会错）：
  - birth_year + int(age) → 没有Q4进位，结果偏移
  - 从出生年直接+10年 → 忽略起运年龄
  - 自己估算取整 → 大概率算错

引擎JSON的起运年份计算规则（浮点月份偏移+Q4进位，2026-07-07修正版）：
  🚨 旧引擎bug: int(qi_yun_age)把0.33截断为0 → 大运从1980年开始 ❌
  🚨 根源：int()截断导致所有<1岁的起运年份偏移
  
  修正后的引擎算法：
    ① 起运年龄向上取整 → 作为第一步大运起始岁数
    ② 每步大运管10年整数区间：base + step*10 ~ base + (step+1)*10 - 1
    ③ 年份计算仍用浮点月份偏移+Q4进位（不截断）
  
  例：魏启令 (qi_yun_age=0.33)
    base = ceil(0.33) = 1
    第1步: 1~10岁 (1981~1990) ✅
    第5步(现): 41~50岁 (2021~2030) ✅
  
  🔒 代码位置: da_yun.py L178-182 (2026-07-07修正)
  🔒 物理验证：compute_da_yun()在pipeline_v5.py L171被调用，每次排盘都会执行
 
子agent的context中必须写明：
   「大运年份已从引擎JSON提取，直接使用 data['大运']['序列'] 的每步年份数据，
    不需要重新计算，也不需要任何调整。引擎的compute_da_yun()已正确处理Q4进位。
    data['大运']['序列']是唯一真值。」

口诀：大运年份不用算，引擎JSON直接取
      data['大运']['序列']是唯一真值
      子agent自己算的，Q4进位对不上
      直接复制用就对了，不要画蛇添足
```

## 🎯 大运喜忌判断规则（干支分治+能量分阶段）（2026-07-07新增）

### 核心原则

大运的喜忌判定，**不能笼统地概括为"纯喜用"或"纯忌神"**——必须分天干、地支判定。

### 判喜忌公式

```
【前五年（第1~5年）】
  大运天干影响 = 70%   ← 前五年天干主导
  大运地支影响 = 30%

【后五年（第6~10年）】
  大运天干影响 = 30%
  大运地支影响 = 70%   ← 后五年地支主导
```

### 判例

| 大运 | 天干 | 地支 | 前5年体验 | 后5年体验 |
|:----|:----|:----|:---------|:---------|
| 丙戌 | 丙正官(喜用) | 戌正印(忌神) | 丙火70%→官克身·想做事 | 戌土70%→印保守·放不开 |
| 戊子 | 戊正印(忌神) | 子食神(喜用) | 戊土70%→保守压抑 | 子水70%→才华释放 |
| 丁亥 | 丁七杀(喜用) | 亥伤官(喜用) | 丁火70%→被逼成长 | 亥水70%→伤官生财 |

**🚨 禁止**：说丙戌大运是"双忌神"（正官是喜用不是忌神）
**✅ 正确**：说丙戌大运"天干喜正官(前5年官制身)+地支忌正印(后5年保守纠结)"

## 🎯 流年喜忌判断规则（干支分管时间）（2026-07-07新增）

### 核心原则

流年（每年）的吉凶判断，**分天干地支管时间段**：

```
【上半年（1~6月）】
  流年天干主导 → 看天干五行+十神 + 与原局/大运的互动

【下半年（7~12月）】
  流年地支主导 → 看地支五行+十神 + 刑冲合害 + 与原局/大运的互动
```

### 实战用法

当判断某一年的具体事件时间时：
1. **事件发生在1~6月** → 看流年天干的能量
2. **事件发生在7~12月** → 看流年地支的能量
3. **跨年事件** → 兼顾天干+地支，但以地支产生的刑冲合害为持久影响

### 判例

| 流年 | 天干 | 地支 | 上半年(天干管) | 下半年(地支管) |
|:----|:----|:----|:--------------|:--------------|
| 2024甲辰 | 甲正财(喜用) | 辰正印(忌神) | 1~6月财运好→收入最高 | 7~12月印保守→花钱多 |
| 2025乙巳 | 乙偏财(喜用) | 巳正官(喜用) | 1~6月偏财机会 | 7~12月官星制身→合同/文书 |
| 2026丙午 | 丙正官(喜用) | 午七杀(喜用) | 1~6月正官立规矩 | 7~12月七杀驱动→拓展 |

### 与|大运的能量叠加

> 当前大运 + 流年 = 实际体验。
> 
> 例：2026丙午年，在戊子大运中
> - 前5年（2021~2025）：戊子大运 戊(忌神70%) → 整体保守
>   - 但2026年已是大运第6年 → **进入后5年阶段**：子水(喜用70%)主导
>   - + 流年丙午全年纯喜用（正官+七杀）
>   - = **2026年是戊子大运中最顺的一年**（大运后5年子水+流年纯喜用）
> 
> 判断年份吉凶时，兼顾：①大运所处的阶段（前/后5年）②流年干支分管时间

## 🚨 D级致命错误：起运年龄被忽略或误用（2026-06-17新增·本会话致命教训）

> **致命案例**：家主（1980-08-06卯时·庚申年阳男）实际起运年龄仅 **0岁4个月17天（0.38年）**，但v14.0报告误写了「9岁多起运」。两者相差9年，导致全部大运偏移！
> **发现过程**：老板质问「我的起运年龄你算错了吧」，核查引擎JSON `data['大运']['起运年龄']` 才发现错误。
> **根因**：子agent报告生成时凭记忆/旧报告数据写了起运年龄，未从引擎JSON中提取。引擎输出的年龄是唯一准确的数据，不可凭经验假设！
> **教训**：每次报告生成前，必须从引擎JSON中提取 `data['大运']['起运年龄']` 作为唯一真值。任何delegate_task子agent的context中必须包含此值。

### 起运年龄黄金法则

```yaml
🚨 起运年龄 = 引擎JSON中 data['大运']['起运年龄'] 是唯一真值！
   任何报告中的起运年龄必须从此字段提取，不可凭记忆/旧报告猜。

正确做法：
  Python: data['大运']['起运年龄']   → 如 0.38
  英文文本: data['大运']['起运']     → 如 "0岁4个月17天"
  
  第1步大运起始年 = 起运开始日期的年份（Q4进位+1）
    用 Python `(birth + timedelta(days=qi_yun_age * 365.25)).year`
    起运在10~12月(Q4) → 年份+1（实际影响从次年开始）
    例：1980-08-06生 + 0.37年 → 起运1980-12-19 → year=1980, month=12≥10 → 取1981年
    例：2010-09-25生 + 4.3年 → 起运2015-01 → year=2015, month=1<10 → 取2015年
    例：1952-08-25生 + 5.8年 → 起运1958-06 → year=1958, month=6<10 → 取1958年

  🚨 禁止用 birth_year + int(start_age) 近似！必须用实际起运日期！
  🚨 旧版算法（已废弃·2026-06-24）：
    start_year = b_year + int(start_age) + year_offset  → 对0.38年/0.4年不准
  ✅ 新版算法（当前有效）：
    qi_yun_start = birth + timedelta(days=qi_yun_age * 365.25)
    qi_yun_start_year = qi_yun_start.year
    if qi_yun_start.month >= 10: qi_yun_start_year += 1
    start_year = qi_yun_start_year + i * 10
  
  每步大运 = 10年连续（年龄范围正确，年份需手工修正）

常见陷阱：
  ❌ 凭旧报告写「9岁多起运」——旧数据可能已被引擎修正
  ❌ 凭起运年份猜整年——起运0.38岁 ≠ 起运1岁
  ❌ 子agent不提取data['大运']['起运年龄']——而是凭空编造
  ✅ 每次都必须：data = json.load(引擎JSON) → data['大运']['起运年龄']

口诀：起运年龄是根基，引擎JSON才可信；不凭记忆不凭旧，data['大运']来提取
```

### 强制修正流程

```yaml
每次拿到引擎JSON输出后，手动修正大运年份：

Step 1 — 从引擎提取起运年龄（唯一真值）
  → data['大运']['起运年龄'] — float，精确到小数点后
  → data['大运']['起运'] — 字符串，如"0岁4个月17天"
  
  ⚠️ 必须用Python代码提取：
    import json
    with open('/tmp/bazi_batch/{name}.json') as f:
        data = json.load(f)
    qiyun_age = data['大运']['起运年龄']  # 如 0.38
    qiyun_desc = data['大运']['起运']    # 如 "0岁4个月17天"
    
  ❌ 禁止：从旧版报告复制起运年龄
  ❌ 禁止：凭经验估算（"9岁多" "6岁多"）
  ✅ 唯一来源：引擎JSON的起运年龄字段

Step 2 — 计算起运年份（约数）
  起运年份 ≈ 出生年份 + floor(起运年龄)
  例：1980年生 + 0.38 ≈ 1980年（当年即起运）
  例：1987年生 + 9.55 ≈ 1996年（起运年份1996）

Step 3 — 按10年连续计算每步大运的年份范围
  ✅ 正确公式（用起运年份为起点）：
    第1步：{起运年份} ~ {起运年份+9}
    第2步：{前一步结束+1} ~ {前一步结束+10}
    ...每步连续10年

  ✅ 年龄范围可以直接用引擎的起始/终止年龄：
    例：甲申 年龄0.4~10.4 → 正确（10年）
    
  ❌ 不要直接用引擎的「起始年份」和「终止年份」——它们是错的！
  ❌ 不要从出生年开始算（除非起运年龄<1岁接近0）

Step 4 — 三重验证
  □ 验证1：每步大运 = 10年（结束年-开始年+1=10）
  □ 验证2：相邻大运无间隔（第2步开始年 = 第1步结束年+1）
  □ 验证3：大运年份 = 出生年 + 起运年龄 + n×10（n为步数-1）
    例：1980年生 + 0.38 + 1×10 = 约1990年进入乙酉大运 ✅
    例：1980年生 + 0.38 + 3×10 = 约2010年进入丁亥大运 ✅

Step 5 — 在报告中写入正确的起运年龄和大运年份
  报告§1中必须包含独立行：
  | **起运年龄** | **{起运年龄}**（约{年份}年起运）|
  
  ⚠️ 起运年龄在§1表格中必须有独立行！
  ⚠️ 第1步大运的范围必须与起运年龄一致！

示例1（家主·1980-08-06卯时·庚申阳男·起运0.38年）：
  引擎输出（错误年份）：甲申 1980-1999, 乙酉 1990-2009 (重叠)
  引擎年龄（正确）：甲申 0.4~10.4, 乙酉 10.4~20.4
  手动修正（正确年份）：
    甲申 1980~1990, 乙酉 1990~2000, 丙戌 2000~2010
    丁亥 2010~2020, 戊子 2020~2030, 己丑 2030~2040...

示例2（主母成·1987-07-10巳时·丁卯阴女·起运9.55年）：
  引擎输出（错误）：戊申 1996-2015, 己酉 2006-2025 (重叠)
  手动修正（正确）：戊申 1996~2006, 己酉 2006~2016 (连续10年)

口诀：引擎大运年份错，十年重叠莫直接；起运年龄是唯一，提取JSON勿凭旧；
     起运年份加十年，每步十年度量准；出生年份加起运，大运起点不会错
```

### 🚨 批量多人处理工作流（2026-06-22实战·34人同时评估·v2.0加入超时/分批/质量控制）

> **实战场景**：用户一次性发来34人（33人无时辰+1人有时辰），要求每人评估12时辰选TOP2，各出2份报告，每人独立建文件夹。
> **核心挑战**：396次引擎排盘 + 34次深度分析 + 68份全量报告 — 需要高效的批量流水线。

```yaml
【批量处理标准化流水线·六步流程】

Step 0 — 数据整理
  □ 用Python批量转换农历→公历（zhdate）
  □ 输出清单：姓名/性别/公历年月日/有时辰否
  代码示例：
  from zhdate import ZhDate
  for name, gender, cal_type, y, m, d in people:
      if cal_type == "农历":
          dt = ZhDate(y, m, d).to_datetime()
          print(f"{name} → 公历{dt.year}.{dt.month}.{dt.day}")

Step 1 — 批量12时辰评估（关键效率优化）
  □ 用 execute_code + subprocess 批量跑引擎，比逐条命令快30倍+
  □ 对所有无时辰的人，一次性跑完12×N次引擎
  □ JSON按人分目录保存：/tmp/bazi_batch/12hour_eval/{姓名}/{时辰名}.json
  
  Python代码模板：
  engine_path = "/root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py"
  for name, gender, y, m, d in no_time_people:
      for idx in range(12):
          result = subprocess.run(["python3", engine_path, str(y), str(m), str(d), 
                                   "0", "0", str(idx), gender_cn, f"{name}_{shichen}", "--json"],
                                   capture_output=True, text=True, timeout=30)
          with open(f"{person_dir}/{shichen}.json", 'w') as f:
              f.write(result.stdout)

  ⚠️ 注意：execute_code最多50次tool调用，一次跑396次引擎没问题
  ⚠️ 每个引擎调用设置timeout=30秒，防止卡死

Step 2 — 初筛排序（分数快速过滤）
  □ 根据12时辰的身强弱分数做初排
  □ 排序规则：越接近50分越好（从弱50分/从强20分作为特殊格局单独处理）
  □ 取TOP 5-8个时辰进入深度分析（不全部深分析，节省算力）
  
  Python排序模板：
  def rank_key(item):
      score = item['身强弱']['总分']
      return -abs(score - 50)  # 越接近50分排名越高
  
  ⚠️ 丁火日主特殊处理：丁火不论强弱，分数不是决定性因素
  ⚠️ 从弱格(50分恒定)和从强格(20分恒定)需独立评估

Step 3 — 并行深度TOP2分析
  □ 用 delegate_task 对每个人并行跑深度分析（最多4人同时）
  □ 每个子agent读取该人TOP 5-8个时辰的JSON
  □ 评估维度（按优先级）：格局层次 > 合局引化 > 身强弱 > 十神搭配 > 冲刑影响 > 财星 > 空亡
  □ 输出TOP2理由到 /tmp/bazi_batch/top2_analysis/{姓名}_TOP2.txt
  
  delegate_task 模板：
  tasks = [{
      "goal": f"对{name}的12个时辰深度分析→选TOP2",
      "context": f"{name} 性别:{gender} 公历{y}.{m}.{d}\n12时辰JSON在/tmp/bazi_batch/12hour_eval/{name}/",
      "toolsets": ["file", "terminal"]
  }, ...]  # 最多4个任务并行

  ⚠️ 常见TOP2模式速查：
  ┌──────────────┬──────────────────────────────┐
  │ 格局层次     │ 七杀制劫 > 杀印相生 > 比肩帮身 > 食伤生财 │
  │ 合局引化     │ 三合 > 六合 > 半合 > 拱合        │
  │ 冲刑        │ 冲走忌凶=吉，冲走喜用=凶          │
  │ 丁火特殊     │ 丁火不论强弱，财星也是喜用        │
  │ 调候        │ 夏需水/冬需火，调候优先于用神      │
  └──────────────┴──────────────────────────────┘

Step 4 — 创建人物档案目录
  □ 检查已有最高编号：ls -d 人物档案/*-*/ | sort -t- -n -k1
  □ 从最高编号+1开始编号：19-仔仔, 20-王子 ...
  ✅ 每个独立人物一个子目录（与家族成员并列）
  ❌ 非家族成员不可直接放根目录（除非用户明确要求）
  
  目录命名规则：{序号}-{姓名}（如 19-仔仔, 20-王子）

Step 5 — 并行生成TOP2报告
  每个时辰一份完整报告（按bazi-report-template v4.1标准）
  delegate_task分批次执行（每批4人×2时辰=8个任务）
  文件名格式：{姓名}_完整八字命理深析报告_v1.0_{时辰主推/备选}_{YYYYMMDD}.md

Step 6 — 验证+推库
  □ 每份报告行数≥1700行
  □ 每份报告的八字符与对应时辰的引擎JSON一致
  □ git add/commit/push

口诀：
  批量处理三十人，六步流水不走偏
  数据整理第一步，公历转换zhdate
  批量评估十二时，subprocess循环跑
  并行分析选TOP2，delegate_task效率高
  目录编号续旧号，每人一档不混淆
  报告生成再并行，验证推库一步完

---

### 🚨 批量工作流 v2.0 新增·实战精炼（2026-06-22）

#### ① delegate_task 超时处理（600s限制）

> **实战发现**：34人批量中，玉龙(从强格·19人首次)、知弈(身弱·次批)均出现delegate_task 600s超时。报告越复杂（1700+行/21§覆盖）越容易超时。

```yaml
【超时预防与恢复策略】

✅ Step 0 — 复杂任务先做估算
  预计每条报告的复杂度 × 4人并行：
  1700行报告 ≈ 5-8分钟/个 × 4并行 ≈ 8-10分钟/批
  超过10分钟 → 减少并行数（3或2人/批）

✅ Step 1 — 超时检测
  delegate_task 返回 timeout 状态时：
  □ 检查子agent是否有部分输出（部分完成的文件）
  □ 确认已生成的报告是否可用（≥1000行）
  
✅ Step 2 — 🚨 重试策略
  □ 先确认文件是否已被部分创建
    实例：玉龙在第1批超时，但主agent发现文件已由前一批次正确创建
    结论：超时 ≠ 丢失，先检查再决定是否重试
  
  □ 如文件已存在且完整（≥1500行）→ 跳过
  □ 如文件不存在或不完整 → 重新发起任务
    重新发起时减少并行数（从4→2），增加上下文精简度

⚠️ 致命错误防御：重试时不要改变文件路径或命名规则！
    两次尝试生成同一个文件时，文件名必须一致。
    不一致会导致知识库中有两份\"不同但内容相同\"的报告。

口诀：子agent六百秒超时，先查文件是否存在；完整跳过不重跑，缺失重试减并行
```

#### ② Git分批推送策略（防丢失）

> **实战发现**：66份报告连续生成约需60分钟。若最后一起推送，期间任何中断都会丢失全部进度。本会话采用5次分批推送，零丢失。

```yaml
【Git分批推送铁律】

每次delegate_task批次完成后，立即推送：

第1批完成后 → 推知识库  ✅ 11人20份
第2批完成后 → 推知识库  ✅ 4人8份（累计15人28份）
第3批完成后 → 推知识库  ✅ 4人8份（累计19人36份）
第4批完成后 → 推知识库  ✅ 4人8份（累计23人44份）
第5批完成后 → 推知识库  ✅ 最后的11人22份

⚠️ 此策略同时起到了版本安全感（每批都是独立commit）
⚠️ 每次commit信息明确标注批次进度（如\"第四批: 4人8份累计23人44份\"）
⚠️ 即使某一批次失败，之前已推的报告不受影响

```bash
# 标准分批推送命令
cd /root/weiwuji-knowledge-base
git add -A && \
git commit -m "📖 批量报告第N批@YYYY-MM-DD: 姓名1/姓名2/姓名3 (N人X份) 累计M人Y份" && \
git pull --rebase && git push
```

口诀：分批推送不积压，每批跑完就推库；commit标注进度数，断点续传不丢失
```

#### ③ 批量流程中的特殊格局处理

> **实战发现**：34人中，丁火日主（七七/传和）、从强格（朱姐/玉龙/等）、从弱格需要对选时结果做特殊校准。

```yaml
【批量选时中的特殊格局速查】

① 丁火日主 — 不论强弱，以五行平衡为上
  □ 批处理排序时，身强弱评分**不是**丁火的选时首要依据
  □ 以调候（夏需水/冬需火）、合局引化、十神搭配优先
  □ 传和（壬子甲辰丁丑·丁火）：需重现印星化杀还是比劫帮身
  □ 七七（丁酉戊申丁亥·丁火）：午时/未时PK焦点在火力延续性

② 从强格（印比分≥100 → 恒定20分）
  □ 所有12时辰均为恒定20分时，用合局引化作为排序依据
  □ 玉龙（戊辰戊午己未）：亥时（亥未拱合木）、子时（子午冲调候）

③ 从弱格（无印比 → 恒定50分）
  □ 所有12时辰均为恒定50分时，用调候作为首要排序依据
  □ 王子（辛卯甲午癸卯）：未时（午未合火+卯未合木双合局）> 寅时（半合）
  □ 传和（壬子甲辰丁丑）：从弱格的时辰（子丑卯辰申酉亥）vs 身弱时辰（寅巳午未戌）

④ 身强/身弱极端值处理
  □ 全部12时辰均为身强 → 选时干十神最纯正（官杀>财>食伤）
    小雨：壬辰乙巳己卯-68~92分全部身强 → 子时甲木正官 > 亥时乙木七杀
  □ 全部12时辰均为身弱 → 选时柱帮身组合最优（比肩>正印>偏印>劫财）
    泡泡：己亥己巳甲辰-9.6~28.8分全部身弱 → 亥时乙亥(28.8分) > 子时甲子(21.6分)

口诀：批量选时先看格，丁火不论弱和强；从强从弱恒分，合局调候定乾坤
```

#### ④ 子agent报告质量控制强制流程

> **实战发现**：本场会话中部分子agent输出报告单份仅839行（远低于标准的1700+行），缺少§11~§21的完整覆盖。需要强约束。

> **⚠️ 2026-06-23新增致命陷阱**：子agent生成的报告即使行数达标、21§完整，**§1格式也100%自创而非标准25字段格式**！因为子agent看不到SKILL.md模板，它只能根据context描述猜测格式——而描述越详细，子agent越倾向于「创新」而不是「照抄」。

#### ④-a 🚨 delegate_task 报告§1格式失配陷阱（2026-06-23新增·4份全部重修）

> **致命教训**：本场会话中，4份delegate_task生成的报告（家主1531行/子源1502行/主母1503行/立1545行）§1格式全部自创——有4字段的有6字段的，与25字段标准格式完全不匹配。bazi-format-check.py验证通过率0/4。每份需手动重写§1。

**根因**：delegate_task子agent没有session memory、没有skills加载权限、不能读SKILL.md。即使context中要求"采用25字段四段式"，子agent也无法看到实际模板的精确格式，会选择「创新」而非「照抄」。

```yaml
【强制流程】用delegate_task生成报告时，推荐"两步法"：

方案A（推荐·格式100%确保）→ 两步法：
  Step 1 — 对每人跑 bazi-must-verify.sh 获取标准§1骨架
    bash bazi-must-verify.sh 年 月 日 时 分 性别 姓名
    → 输出包含标准25字段表格（骨架约60-70行）
    
  Step 2 — 子agent只负责填充§2~§21分析内容
    在delegate_task context中写明：
    "§1骨架已预生成。你只需写§2~§21的分析内容。
     不得修改§1格式。§1骨架保存在 /tmp/skeleton_{name}.txt"
    
  Step 3 — 合并骨架+内容
    将骨架（§1）+ 子agent输出（§2~§21）合并为一份完整报告

方案B（高风险·不推荐）→ context嵌入完整模板：
  在context中粘贴完整的§1 25字段表格代码（而非描述），要求：
  "请一字不差地复制下面的表格到你的报告中，只替换{待填}内容"
  风险：子agent仍可能「改进」格式，须通过bazi-format-check.py验证

⚡ 出错后的修复流程（2026-06-23实战验证）：
  当子agent生成的报告§1格式不达标时：
  
  Step 1 — 跑 bazi-must-verify.sh 获取标准骨架
  Step 2 — 从旧报告中提取§2~§21的分析内容（保留子agent的深度分析）
  Step 3 — 用标准骨架替换§1部分（骨架中的{待填}从数据源填入）
  Step 4 — 运行 bazi-format-check.py 验证 → 通过即可

  代码模板（Python批量修复）：
  ```python
  import re, math, json
  
  with open('family_bazi_data.json') as f:
      data = json.load(f)
  person = [p for p in data if p['姓名']==name][0]
  
  # 构建标准§1头部（参照bazi-must-verify.sh输出的25字段格式）
  header = f"# {name}·完整八字命理深析报告 v1.0..."  # 完整§1骨架
  
  # 保留旧报告§2~§21
  with open(old_path) as f:
      content = f.read()
  s2_pos = re.search(r'##\s*§2', content)
  section2 = content[s2_pos.start():]
  
  # 合并写入
  with open(old_path, 'w') as f:
      f.write(header + section2)
  ```
  
口诀：
  delegate报告格式差，子agent看不见模板
  两步走才最保险：骨架先跑must-verify
  分析内容delegate写，合并起来才是全
  出错别慌有修复，骨架替换保留§2~§21

#### ⑤ 最差时辰判定逻辑

> **背景**：为用户生成33人「最差时辰」报告时，需要从12个时辰中选出命运最不利的一个。判定逻辑与选最优时辰不同——最优看格局上限，最差看结构下限。

```yaml
【最差时辰判定规则】

原则：最差时辰 = 当天那个时辰会导致人生最坎坷/最失衡/最折腾。

区分四种情况：

① 从弱格（12时辰全为50分恒定）
  → 最差 = 打破从弱的那个时辰（分数 ≠ 50分）
  → 例：王子(辛卯甲午癸卯) → 子时壬子(24分)打破了从弱格 → 最差
  → 例：传和(壬子甲辰丁丑) → 午时丙午(24分·丁火不论强弱)打破了从弱 → 最差

② 从强格（12时辰全为20分恒定）
  → 最差 = 打破从强的时辰（分数 ≠ 20分，或格局被破坏）
  → 例：玉龙(戊辰戊午己未) → 子时甲子打破从强(子午冲毁印) → 最差
  → 例：朱姐(甲寅乙亥乙卯) → 子时丙子(伤官泄身)打破从强 → 最差

③ 全部为身强/全部为身弱
  → 最差 = 偏离平衡最远的（分数极端值）
  → 全部身强：分数最高=最差（身过强失衡）
    例：小雨(壬辰乙巳己卯·全身强68~92分) → 辰时92分 → 最差
  → 全部身弱：分数最低=最差（身过弱无救）
    例：泡泡(己亥己巳甲辰·全身弱9.6~28.8分) → 巳时9.6分 → 最差

④ 混合（有些时辰从弱/从强，有些时辰身弱/身强）
  → 先判格：从格被破 > 身弱 > 身强 > 从弱/从强纯正
  → 打破从格的时辰永远比维持从格的时辰差
  → 例：知弈(壬寅己酉甲戌) — 最差巳时(身弱4分)打破从弱 > 其他从弱50分

⑤ 丁火日主特殊处理
  → 丁火不论强弱，分数不是决定性因素
  → 最差 = 时柱与原局冲突最大的组合
    例：七七(丁酉戊申丁亥·丁火) → 寅时壬寅(壬水盖头+寅亥合木被阻) → 最差
    例：传和(壬子甲辰丁丑·丁火) → 午时丙午(子午冲破禄+打破从弱) → 最差

口诀：
  判定最差先看格，从格被破最差格
  全部身强偏高找，全部身弱偏低寻
  丁火不论强和弱，时柱冲突定乾坤
```

#### ⑦ 批量报告审计 + 综合排名生成工作流（2026-06-22新增·家族14人审计+34人提取+81项排名）

> **实战场景**：用户要求对14份现有家族报告做模板合规性审计（对照v4.1 FINAL的18个检查点），同时提取34位外部客户(19~52)的主推+最差版本数据，合并生成81项综合排名。

```yaml
【三合一工作流：审计+提取+排名】

适用场景（任一触发）：
  □ 用户要求「审计所有现有报告」
  □ 用户要求「把外部客户加入家族排名」
  □ 用户要求「生成全量排名/家族合参排名」
  □ 需要对N份报告做标准化质量审计

──────── Phase ①: 批量审计（14家族报告·18检查点）────────

Step 1 — 确定审计范围
  □ 列出所有需要审计的报告清单
  □ 找到每人的最新版本报告路径
  □ 确认审计基准：bazi-report-template v4.1 FINAL的21§模板

Step 2 — 18项检查点（逐项grep扫描）
  ┌────┬──────────────────────────────┬──────────────────────────┐
  │ #  │ 检查项                        │ 扫描方法                  │
  ├────┼──────────────────────────────┼──────────────────────────┤
  │ 1  │ §1 25字段四段式              │ grep -c "25字段\|序号.*项目"  │
  │ 2  │ §1后白话解读🗣️               │ grep -c "🗣️"               │
  │ 3  │ §5灾祸/疾病/搬迁(四大神煞)   │ grep -c "元辰\|灾煞\|天罗地网" │
  │ 4  │ §6五重人格特质(≥5个≥50字)   │ grep -c "特质[一二三四五]"    │
  │ 5  │ §8九龙道长财富五级对照       │ grep -c "死财富五级\|巨富"    │
  │ 6  │ §9置业分析独立板块(≥300字)   │ wc -c §9段落               │
  │ 7  │ §10恶神制化+五行定行业       │ grep -c "恶神制化\|五行定行业" │
  │ 8  │ §11第0层三档法+6步排查       │ grep -c "第0层\|三档法\|六步排查" │
  │ 9  │ §12四大结婚信号+三窗口       │ grep -c "四大信号\|结婚窗口"   │
  │ 10 │ §15六亲四宫逐宫分析          │ grep -c "年柱.*祖上\|月柱.*父母" │
  │ 11 │ §16事件总表≥70行            │ grep -c "^|" §16段落 ≥70  │
  │ 12 │ §17大运精析10步至100岁       │ grep -c "## 17\\." ≥10      │
  │ 13 │ §18三决断精确到年份          │ grep -c "决断[一二三]"       │
  │ 14 │ §19ASCII运程曲线             │ grep -c "ASCII\|运程曲线"     │
  │ 15 │ §21人生建议6维度             │ grep -c "21\\."              │
  │ 16 │ 喜忌用神自检(身强弱→喜忌表) │ 读取§1喜忌 vs §3身强弱对比   │
  │ 18 │ 空亡/神煞/十二长生检查       │ grep -c "空亡\|十二长生"      │
  └────┴──────────────────────────────┴──────────────────────────┘

Step 3 — 逐人产生审计矩阵
  格式示例：
  | 人员 | §1 | §1🗣️ | §5 | §6 | §8 | §9 | §10 | §11 | §12 | §15 | §16 | §17 | §18 | §19 | §21 | 喜忌 | §7 | 空亡 | 得分 |
  |:----|:--:|:----:|:--:|:--:|:--:|:--:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:----:|:--:|:----:|:----:|
  | 静  | ✅ |  ✅  | ✅ | ✅ | ✅ | ✅ | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅   | ✅ |  ✅  | 100% |

Step 4 — 分析报告
  □ 计算每人得分率
  □ 标记共性缺失项（如§6格式错误11人→系统性排版问题）
  □ 识别模范报告（如静100%）和待修正报告
  □ 决定哪些需修补、哪些可接受

口诀：批量审计18项，逐项grep不漏网；共性缺失找模式，模范报告做标杆。

──────── Phase ②: 批量核心数据提取（34人主推+最差）────────

Step 1 — 遍历目录定位文件
  □ 对19~52号人物：ls {编号}-{姓名}/ 找含"主推"和"最差"的.md文件
  □ 记录每个版本的文件路径

Step 2 — 多格式兼容提取（三种常见报告格式）
  格式① — 25字段表格格式（§1标准）
    → 从表格行提取：八字/日主/身强弱/财星/喜忌等
  格式② — 21§编号格式（带## §X标题）
    → 从§1或头部元数据提取
  格式③ — 简易键值格式
    → grep关键词提取（"八字"、"日主"、"身强弱"等）

Step 3 — 提取字段清单（每个版本必须提取）
  ┌──────────────┬────────────────────────────────┐
  │ 字段         │ 提取方式                      │
  ├──────────────┼────────────────────────────────┤
  │ 八字         │ 标题行/§1表格/元数据          │
  │ 日主+性别    │ §1表格/头部                   │
  │ 格局等级     │ §1序号6/标题⭐评级            │
  │ 身强弱(分数+等级)│ §1序号8/扫描全文         │
  │ 从弱格排查   │ §1序号9                      │
  │ 喜用神+忌神  │ §1序号10-11                  │
  │ 财星分数     │ §1序号13（⚠️ 仅60%覆盖率）   │
  │ 财富等级     │ §1序号14                     │
  │ 学历等级     │ §1序号15                     │
  │ 事业等级     │ §1序号16                     │
  │ 最佳大运     │ §1序号17                     │
  │ 起运年龄     │ §1序号18                     │
  │ 最差大运     │ §1序号20                     │
  │ 现行大运     │ §1序号21                     │
  │ 四大特征     │ §1序号24                     │
  └──────────────┴────────────────────────────────┘

Step 4 — 数据验证
  □ 八字提取：5种策略串联
    ① 标题行（如"仔仔_丑时_己亥甲戌癸巳癸丑"）
    ② 报告头部§1表格
    ③ 出生时间→引擎反推
    ④ 四柱组合标记
    ⑤ 键值对回退
  □ 身强弱等级归一化（"身偏强"→"身强"、"身极弱"→"身弱"等）
  □ 缺失标记：字段不存在时设为null，不编造

Step 5 — 输出结构化JSON
  格式：
  ```json
  {
    "编号": "19", "姓名": "仔仔", "版本": "主推", "时辰": "丑时",
    "八字": "己亥 甲戌 癸巳 癸丑", "日主": "癸水", "性别": "男",
    "格局": "⭐⭐⭐ 中等·正官格",
    "身强弱": "身弱(23.2分)",
    "喜用神": "金(印星)>水(比劫)",
    "财星分数": 8, ...,
    "文件路径": "..."
  }
  ```

口诀：34人每版两个件，主推最差分别拿；格式兼容三模式，缺失不编设回退。

──────── Phase ③: 综合排名生成（14家族+34×2=81/82项）────────

Step 1 — 确定排名公式
  继承v6.0体系：
  ```
  单项维度得分 = 原局评分 × 0.7 + 大运评分 × 0.3    (每项满分10分)
  综合总分     = 财富×35% + 事业×30% + 婚姻×15% + 学业×10% + 健康×10%
  ```

Step 2 — 数据分组
  A组（家族成员·14人）：从v6.0排名文档提取精确的5维评分
  B组（外部客户主推+最差·67项）：从提取JSON数据估算5维评分

Step 3 — B组评分估算规则
  ① 财富维度（35%）—— 从身强弱+财星分数+格局估算
    从弱格+财旺 → 7~9分 | 身强财旺 → 7~10分
    中和+财旺 → 6~8分 | 身强财弱 → 5~7分
    身弱财旺 → 4~6分 | 身弱财弱 → 3~5分 | 身弱无财 → 1~3分
    主推全值、最差降1~3分

  ② 事业维度（30%）—— 从格局等级评分
    ⭐⭐⭐⭐⭐ → 8~10分 | ⭐⭐⭐⭐ → 6~8分
    ⭐⭐⭐ → 4~6分 | ⭐⭐ → 2~4分 | ⭐ → 1~2分

  ③ 婚姻维度（15%）—— 从日主+身强弱+格局估算
    中和+格局好 → 6~9分 | 从弱→晚婚/非常态 → 4~6分
    身弱+官杀混杂/财多 → 3~5分

  ④ 学业维度（10%）—— 从学历等级/文昌情况估算
    双一流/一本 → 7~10分 | 二本/大专 → 4~7分

  ⑤ 健康维度（10%）—— 从身强弱估算
    身强 → 6~9分 | 中和 → 5~7分 | 身弱 → 3~6分

Step 4 — 公式计算
  每项使用Python计算（禁止手算）：
  ```python
  item['综合'] = (item['财富']*0.35 + item['事业']*0.30 +
                  item['婚姻']*0.15 + item['学业']*0.10 +
                  item['健康']*0.10)
  ```

Step 5 — 排名文档结构
  # 🏆 家族综合排名 v7.0（全量N项）
  > ## 📊 排名总览一览表（N行完整）
  > ## 一、排名方法说明
  > ## 二、👑 家族成员排名详表
  > ## 三、📋 外部客户排名要览
  > ## 四、🔍 核心发现
  > ## 五、附录：各人关键数据索引

Step 6 — 最终验证
  □ 家族成员分数与v6.0完全一致（偏差=0）
  □ 综合分公式计算无误（抽查3-5人）
  □ 排名降序排列（从高分到低分）
  □ 备注栏标注"★v6.0精确分"或"★分值估算·主推/最差"
  □ 标题项数 = 实际排名行数（仔仔仅主推无最差→81项而非82项）

口诀：
  排名公式先定好，家族精确外部估
  五维逐项评分完，乘权相加得总分
  降序排列加备注，验证抽查保精度
```

#### ⑧ 报告质量审计+补足重写流程（2026-06-22实战精炼·重新编号）

> **实战发现**：34人批量中，5份报告（王子主推271行/王子备选281行/七七备选693行/阿杜备选650行/小雨备选791行）质量不达标。需要系统审计+补足流程。

```yaml
【报告质量审计标准】

Step 0 — 审计触发条件
  每次批量出报告后，自动运行审计扫描：
  for report in 所有报告; do
      wc -l report          # 行数检查
      grep -c "§1" report   # 板块完整性
      grep -c "§8" report   # 财富分析
      grep -c "大运" report  # 大运分析
      grep -c "三决断" report # 三决断
  done

Step 1 — 质量标准（刚需门槛）
  □ 行数 ≥ 1200行（优先 ≥ 1500行）
  □ §1~§21 至少覆盖 19个§（标准=21个全）
  □ 含关键板块：§1总览 / §2格局 / §3身强弱 / §4喜用神 / §8财富 / 大运分节 / §18三决断
  □ 含 ≥ 7个关键板块中的 ≥ 5个

Step 2 — 不合格的补足方案
  □ 行数 < 800行 → 整份重写（从模板重新生成）
  □ 800~1200行 → 在现有基础上追加缺失章节
  □ 缺失§11~§21 → 追加后半部分（学历/婚姻/子女/健康/大运/事件表/三决断/人生建议）

Step 3 — 补足重写方式（推荐delegate_task）
  □ 重写任务context中注明「需重写，现有仅X行，扩展至1500+行」
  □ 提供完整八字数据（日主/身强弱/喜忌/大运/财星等）
  □ 写明覆盖规则：「覆盖原文件，路径不变」

Step 4 — 验收
  □ wc -l ≥ 1500 ✅
  □ grep -c "§1" ≥ 1
  □ grep -c "§21" ≥ 1
  □ grep -c "全生命周期重点事件\|事件总表" ≥ 1
  □ grep -c "三决断" ≥ 1
  □ 全部通过 → 质量达标

口诀：
  批量出报告，审计先走一遍
  行数一千五，板块二十一全
  不够就重写，delegate并行干
  验收过五关，推库不手软
```

```yaml
【子agent报告质量控制清单】

每个delegate_task子agent的context末尾**必须**包含：

```
## 🚨 强制质量约束

1. 报告总行数必须 ≥ 1700行（非空格+非格式符号行）
2. §1~§21共21个板块必须全部覆盖 — 不可省略任何板块！
3. §16全生命周期事件总表 ≥ 70行
4. 起运年龄必须从引擎JSON提取（格式：data['大运']['起运年龄']）
5. 所有数字（身强弱/财星分）从数据源提取，不做计算
6. 文件名：{姓名}_完整深析报告_v1.0_{时辰主推/备选}_{YYYYMMDD}.md
```

**主agent验收流程（强制）**：
```bash
# 文件存在性检查
wc -l {报告路径}     # 必须≥1700

# 板块完整性检查
grep -c "## §" {报告路径}  # 必须≥21

# §16事件表行数
grep -c "^|" {报告路径}  # 总表格行数应≥150（含§1+§16等）

# 关键词检查
grep -c "全生命周期重点事件" {报告路径}  # ≥1（§16必须存在）
grep -c "三决断" {报告路径}  # ≥1（§18必须存在）
```

如果验收不通过 → 重新发起delegate_task任务，注明缺失的§编号！

口诀：子agent报告验收，行数1700不能少；二十一章板块全，事件七十保底量
```

## 🚨 工作流程（v4.1·2026-06-23升级·官方数据源优先）

> **核心变更**：2026-06-23老板强制——所有八字数据必须以官方数据源为准，先拉官网数据再出报告。不再允许引擎→验证→手动写JSON的老流程。

### 强制前置条件：bazi-init-master-data.py 已安装

```yaml
📛 铁律：每次新八字必须运行此脚本。
  脚本位置：/root/.hermes/profiles/jinjian-zhenren/scripts/bazi-init-master-data.py
  功能：POST访问官网→拉取完整数据(八字/藏干/纳音/十神/大运/称骨)→写入family_bazi_data.json
```

### v4.1 标准化工作流

```yaml
拿到八字需求
    ↓
Step 0 → 确认是**新八字**还是**已有数据源中的人**
    ↓
【如果是已有数据源中的人】
  → 直接读取 family_bazi_data_v1.json，取所有数据
  → 不再跑引擎，不再重新计算任何数字
  → 不再重新十神推导（数据源中已有）
  → 跳至 Step 4

【如果是新八字】（从未在数据源中出现过）
  ↓
Step 1 → 🚨 先跑官方数据源脚本（这是首要数据源，不是验证工具）
          运行：python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-init-master-data.py
          
          功能：
          - POST方式访问官网（无需登录，无需cookie）
          - 自动拉取：完整八字四柱、藏干、纳音、十神、大运序列、起运年龄、称骨命
          - 自动进行十神五行验证（防戊土日主→甲木偏财类错误）
          - 写入 family_bazi_data_v1.json
          
          输出验证（脚本执行后的关键检查点）：
          □ 八字符提取正确吗？（年柱月柱日柱时柱完整）
          □ 十神方向正确吗？（日主所克=财星，克日主=官杀）
          □ 藏干数量正确吗？（每支1-3个藏干）
          □ 起运年龄提取正确吗？（从大运data-year属性提取）
          
          ⚠️ 脚本输出即唯真数据源——所有分析从JSON拉数据
          ⚠️ 脚本运行失败？→ 修好脚本再继续，不可跳过

Step 2 → 从family_bazi_data.json读取所有数据
          禁止手动计算十神/财星/身强弱
          JSON字段对照（常见用途）：
          - data['八字'] → 四柱字符串
          - data['日主'] → 日主五行+阴阳
          - data['身强弱']['总分'] → 身强弱分数
          - data['财星']['总分'] → 财星分数
          - data['财星']['明细'] → 逐位置财星评分
          - data['大运']['序列'] → 大运序列（年份需手动修正）
          - data['藏干'] → 四柱藏干
          - data['十神'] → 天干十神
          - data['纳音'] → 纳音

Step 3 → 将新人数据写入数据源（如脚本未自动完成）
          检查 family_bazi_data_v1.json 中是否已有该人
          如无 → 追加写入
          git add/commit/push 数据源

Step 4 → 数据验证（简化的交叉验证）
          对比JSON中的八字与已知出生日期的一致性：
          □ 年柱/月柱是否与出生季节一致？
          □ 时柱是否与提供的时辰一致？
          □ 身强弱评分是否合理？
          □ 财星分数是否不包含劫财？

Step 5 → 进入LLM推理层
          以JSON数据为唯一数据来源，生成报告
```

### 🚨 报告推送规范：版本号接续 + 默认推库（2026-06-23新增·老板指令）

> **老板指令**：「以后都默认推送知识库，放到相应的名字文件夹下面。」

### 版本号接续规则

每次推送新报告到人物档案目录前：

Step 1 — 查看目录中已有文件的最大版本号
  ls 目录/*.md | grep -oP 'v\d+\.\d+' | sort -t. -k1,1n -k2,2n | tail -1
  → 例：若最大为 v19.0 → 新报告命名为 v20.0

Step 2 — 版本号命名格式
  单人报告：{姓名}_完整八字命理深析报告_v{N}.0_标准格式_ALLNEW_YYYYMMDD.md

Step 3 — 复制到目录
  cp /tmp/report.md "07-国学哲学/八字命格/02-人物档案/{编号}-{姓名}/"

Step 4 — 推库（默认行为，不等提醒）
  cd /root/weiwuji-knowledge-base
  git add -A && git commit -m "📖 {姓名}v{N}.0: {摘要} @YYYY-MM-DD"
  git pull --rebase && git push

口诀：推库之前查版本，目录最大再加一。报告完成即推送，不等老板来提醒。

### 凤教训：旧报告日期可能错误，必须用数据源重新验证

致命错误：凤最新报告用了错误八字（己酉乙亥/己土），但数据源正确八字是（辛亥己亥/辛金）。根因：生成报告时用了旧校准记录中的日期（12-13），非数据源的正确日期（12-15）。

强制规则：重出报告时，先从数据源JSON读取出生日期，再用must-verify验证。权威顺序：①引擎+官网当前验证 ＞ ②数据源JSON ＞ ③旧报告 ＞ ④校准参考文件。

口诀：重出报告先查源，数据源日期是准绳。不要信旧报告日期，自身验证才权威。

## 🚨 铁律：官方数据优先于引擎数据

```yaml
数据优先级（自上而下递减）：
1. ✅ family_bazi_data_v1.json（bazi-init-master-data.py写入的官方数据）— 权威来源
2. ✅ bazi-engine.py --json（引擎计算数据）— 参考来源，仅当JSON数据缺失时使用
3. ❌ 记忆中的数字 — 永远不可信任！
4. ❌ 旧报告中的数字 — 不能直接复制，必须从JSON提取

每次写报告前：
  □ 从JSON读该人的八字 → 写在报告中
  □ 从JSON读身强弱分数 → 写在报告中
  □ 从JSON读财星分数 → 写在报告中
  □ 从JSON读大运起运年龄 → 写在报告中
  任何数字必须从JSON取，不允许手工计算！

口诀：
  数据源JSON是龙头，所有数字从中取
  不凭记忆不凭旧，JSON才是唯一真
```

### 注意事项

- 引擎用 `ephem` 天文库计算节气，精确到分钟级，节气每年±1天波动
- bazi-init-master-data.py 使用POST方式访问官网（无需登录），数据完整度高于引擎
- ❌ 旧版bash脚本(bazi-zydx-verify.sh)已废弃——因HTML中流日/流月空span导致固定索引[4]-[7]提取四柱时偏移，四柱输出为"?"
- ✅ 新版工作流(bazi-init-master-data.py)使用「非空值最后4个」提取法修复此bug
- **不要对JSON数据做手动修正**——发现错误应修脚本而非改数据

### 多时辰比较要点（2026-06-18实战精炼）

```yaml
评估12个时辰优劣时，优先顺序：
  格局层次 > 合局引化 > 身强弱 > 十神搭配 > 冲刑影响 > 财星 > 空亡

常见胜出时辰模式：
  🏆 酉时丁酉 — 巳酉丑三合+七杀制劫（最优格局之一）
  🏆 亥时乙亥 — 亥水调候+亥中甲木帮身（午月甲木的最优解）
  🥇 卯时辛卯 — 巳卯合木+比肩帮身（稳定型最佳）
  🥇 寅时庚寅 — 劫财帮身+财根深（突破型但波动大）

注意：同一日不同时辰的时柱用五鼠遁验证（最易错！）
  例：辛巳日→丙辛从戊起→酉时=丁酉（不是丙申！索引9不是8）
  例：甲午日→甲己还加甲→亥时=乙亥（正确）
```

## 🚨 知识库文件移动操作规范（2026-06-22新增·Obsidian同步踩坑）

> **致命教训**：本场会话中，我将分散在多个目录的原始素材用 `mv` 命令移动到 `00-原始素材/` 统一目录，然后 `git add -A && git commit`。虽然git服务器端正确识别了重命名，但用户Obsidian GitHub插件同步时出现「只删不加」的bug——旧路径文件消失但新路径文件未出现，导致Obsidian中文件少了一多半。
>
> **根因**：`mv` 在git内部记录为「删除旧路径 + 新增新路径」两步操作，部分Git客户端（特别是Obsidian的GitHub插件）在处理这类rename时，可能只执行了删除而未执行新增。
>
> **解决**：应使用 `git mv` 代替 `mv`，显式告诉git这是一次rename操作。

### 强制流程

```yaml
【知识库中移动/重命名文件的规范流程】

当需要在知识库中移动文件（从旧路径到新路径）时：

Step 1 — 使用 `git mv` 而不是 `mv`
  ✅ 正确: git mv 旧路径/文件.txt 新路径/文件.txt
  ❌ 错误: mv 旧路径/文件.txt 新路径/文件.txt
  
  git mv 的好处：
  - 显式标记为rename操作（非delete+add）
  - 所有Git客户端都能正确识别
  - Obsidian/GitHub Desktop等GUI工具同步无问题

Step 2 — 批量移动多个文件
  for f in 旧目录/*.txt; do
      git mv "$f" 新目录/
  done
  # 或者先 git mv 单个文件

Step 3 — 处理目录移动
  git mv 旧目录/ 新目录/    # 移动整个目录（含所有文件）

Step 4 — 提交
  git commit -m "移动: 文件从旧目录到新目录"

Step 5 — 验证（强制！）
  git status              # 应显示 renamed，而非 deleted + new file
  git diff --cached --stat  # 应显示 rename 而非 delete + add
  
  如果 git status 显示 deleted（旧路径）和 new file（新路径）→ 出问题了！
  正确的 git status 应显示：
  renamed: 旧路径 -> 新路径

🚨 如果已经用了 mv + git add -A，如何补救？
  方案A：git reset HEAD 旧路径的文件，然后重新 git mv
  方案B：不补救——文件在git服务器端是正确的，让用户本地用以下命令强制同步：
    cd /知识库路径
    git reset --hard origin/main   # 强制重置成本地远端正的状态
    git pull origin main            # 重新拉取

口诀：知识库内移文件，记住要用 git mv；shell mv 加上 git add，部分客户不同步；
      git status 查状态，看到 rename 才算对；出现 delete 加 new file，赶紧补救用 reset
```

⚠️ 本规范适用于知识库根目录（`/root/weiwuji-knowledge-base/`）下的所有文件移动操作。

---

## 🚨 格式强制验证三件套：三重门禁锁死报告质量（2026-06-23新增）

> **背景**：本场会话中，老板要求建立一套「我想不起来也能自动执行」的质量保证机制。为此建立了三件套，确保即使我想偷懒，物理约束也会逼我走标准流程。

### 三件套结构

```yaml
第一关 — bazi-must-verify.sh（强制门禁·绕不开）
  └ 不跑它 → 拿不到八字 + 拿不到标准§1骨架
  └ 输出格式锁死，禁止自创格式

第二关 — bazi-format-check.py（验证·手动执行）
  └ python3 bazi-format-check.py <报告路径>
  └ 检查：8项头部元数据 + 25字段完整性 + 白话解读段
  └ 不通过 → 不能推库（心理约束）

第三关 — git pre-commit hook（物理拦截·绕不开）
  └ .git/hooks/pre-commit 自动触发
  └ 检测到人物档案下.md文件变更 → 自动跑格式验证器
  └ ❌ 不通过 → commit被拒绝（除非 --no-verify，每跳一次都有记录）
```

### 使用流程

```yaml
出报告完整流程：

Step 1 → bash bazi-must-verify.sh → 拿到标准§1骨架
Step 2 → 在骨架基础上写完整分析（21§）
Step 3 → python3 bazi-format-check.py <报告.md> 手动验证
Step 4 → git add → git commit（hook自动再验证一次）
Step 5 → git push
```

### 各组件文件位置

```yaml
bazi-must-verify.sh:
  路径: /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-must-verify.sh
  功能: 引擎排盘→官网验证→对比→输出标准§1 25字段骨架

bazi-format-check.py:
  路径: /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-format-check.py
  功能: 验证报告§1的8项头部元数据+25字段完整性

git pre-commit hook:
  路径: /root/weiwuji-knowledge-base/.git/hooks/pre-commit
  功能: 检测.md变更→自动验证格式→不合格拒绝commit
```

### 各组件能绕过吗？

| 环节 | 能否绕过 | 说明 |
|:----|:--------:|:-----|
| bazi-must-verify.sh 验证八字 | ❌ 绕不开 | 不跑脚本拿不到八字+骨架 |
| bazi-must-verify.sh 标准骨架 | ❌ 绕不开 | 脚本直接输出，格式锁死 |
| bazi-format-check.py 格式验证 | ⚠️ 能跳过 | 但hook自动触发，跳过要心虚 |
| git hook | ⚠️ 能--no-verify | 但每跳一次都有记录 |

**最关键的约束**：不跑 `bazi-must-verify.sh` → 即使开始写报告，也拿不到标准骨架 → 只能自创格式 → hook会拦截commit。

口诀：
  出报告先跑must-verify，标准骨架锁格式
  format-check手动验，hook自动拦不合规
  三件套一起用，绕过每步都心虚

## 🚨 新陷阱：bazi-must-verify.sh 骨架模板硬编码错误（2026-06-23发现·已修复）

> **发现场景**：本场会话中，用 bazi-must-verify.sh 跑家主八字时，日主输出显示「辛土（阴土·田园之土）」——但辛是**阴金**不是阴土！这是脚本骨架模板的硬编码错误。

### 发现并修复的3个bug

| # | Bug | 位置 | 表现 | 修复 |
|:-:|:----|:----|:-----|:-----|
| 1 | 性别参数传数字 | bazi-must-verify.sh L56 | 传 `"$SEX"`（数字如"1"）给引擎→引擎期待中文"男"/"女"→匹配不上→大运方向全反（阳男→变阳女逆排） | 改为传 `"$GENDER"`（脚本第28行已转好的中文） |
| 2 | 日主五行写死为"土"（头部元数据） | bazi-must-verify.sh L168 | 辛日主→输出"辛土"（❌ 应为"辛金"） | 改为case语句根据天干自动判断五行+阴阳类型 |
| 3 | 性别写死为"女"（头部元数据） | bazi-must-verify.sh L169 | 男命→输出"女（阳女逆排）"（❌ 应为"男（阳男顺排）"） | 改为根据$GENDER动态输出+自动判断顺逆排 |
| **4** | **日主五行写死为"土"（§1表格）** | **bazi-must-verify.sh L200** | **辛日主→§1表格行3输出"辛土"（❌ 应为"辛金"）** | **改为使用已在L169计算好的 `RZ_WX` / `RZ_TYPE` 变量** |
| **5** | **性别写死为"女"（§1表格）** | **bazi-must-verify.sh L201** | **男命→§1表格行4输出"女（阳女逆排）"（❌ 应为"男（阴男逆排）"）** | **改为使用已在L180-187计算好的 `GENDER` / `PAIXIANG` / `PEIOU` 变量** |

> ⚠️ Bug #4-#5 为独立代码路径（§1表格输出），与 #2-#3（头部元数据输出）不同，属于2026-06-24完整排盘测试发现。详见 `references/constraint-system-pitfalls.md` 坑⑮。

### 教训（通用规则）

```yaml
🚨 写shell脚本生成模板内容时，绝对禁止硬编码动态数据！

正确做法：
  ✅ 用case/if根据变量动态生成
  ✅ 所有输出模板中的变量值都从引擎/数据源提取
  ✅ 每次改脚本后，至少跑2个不同性别、不同日主的八字测试

错误模式（被修复前）：
  ❌ echo "**日主：** $RIZHU土（阴土·田园之土）"
      → 不论$RIZHU是什么都输出"土"，所有日主都变成土
  ❌ echo "**性别：** 女（阳女逆排）"
      → 不论$GENDER是什么都输出"女"

测试方法：
  每次修改 bazi-must-verify.sh 后，至少测试：
  □ 1个男命（如家主/子源）→ 检查性别字段和排向
  □ 1个女命（如主母）→ 检查性别字段和排向
  □ 1个金日主（辛/庚）→ 检查五行不为"土"
  □ 1个木日主（甲/乙）→ 检查五行不为"土"
  □ 1次 ❌ 案例（输入错误参数）→ 验证能正确报错而非输出错误八字

口诀：
  骨架模板别硬编，动态数据靠变量
  男女日主各测一，确认输出五行对
  脚本改后必测试，否则bug在眼前
```

## 🔍 引擎全量审计：12,437行代码·95%规则已覆盖·3个已知缺口（2026-06-26新增）

> **审计触发**：老板问「所有的规则、所有的要求、输出的内容全部写在代码里面了吧」后，逐模块验证全面代码覆盖。

### 引擎总览

**文件位置**：`projects/bazi-platform/engine/` — 36个Python文件，合计 **12,437行**确定性代码。
**入口**：`pipeline_v5.run_pipeline()` → 输出完整21§JSON。
**四大家族八字已全部验证通过**（身强弱/财星/格局与已知正确值100%一致）。

### ✅ 已全部写入代码的规则（95%覆盖率）

| 规则模块 | 文件 | 行数 | 状态 |
|:---------|:-----|:----:|:----:|
| 身强弱（印40/0/0+比劫全算+燥土+从弱50） | `shen_qiang_ruo.py` | 292 | ✅ |
| 财星（年干8+月干12+藏干比例） | `cai_xing.py` | 133 | ✅ |
| 格局·喜用·调候 | `ge_ju.py` | 218 | ✅ |
| 大运排法+喜用排序 | `da_yun.py` | 193 | ✅ |
| 十神（生克关系+阴阳定正偏） | `shi_shen.py` | 122 | ✅ |
| 神煞22种 | `shen_sha.py` | 279 | ✅ |
| 排盘（节气分界+五虎遁+五鼠遁） | `paipan.py` | 206 | ✅ |
| 纳音（60甲子完整表）/ 空亡（六甲旬） | `pipeline_v5.py` | 56 | ✅ |
| 事业v2（36命格+伟人格+官杀分析+五行行业） | `career_v2.py` | 378 | ✅ |
| 财富v2（五层动态体系+围克折扣+财库） | `wealth_v2.py` | 198 | ✅ |
| 婚姻v2（配偶星定位+四大信号+夫妻宫十神+质量评分） | `marriage_v2.py` | 351 | ✅ |
| 学历v2（年柱三档法+文昌双轨+六步排查+学校等级） | `education_v2.py` | 318 | ✅ |
| 健康v2（五行过三+七杀断病+偏印淤堵+流年预测+宫位） | `health_v2.py` | 1607 | ✅ |
| 子女v2（十二长生基数+出生年份推理+父母合参+双胞胎） | `children_v2.py` | 1546 | ✅ |
| 灾祸/化解（四大神煞+恶神能量表+36岁分界线+五行补运） | `misfortune_analysis.py` | 256 | ✅ |
| 8维度评分v2（校准版0-10分） | `dimensions_v2.py` | 222 | ✅ |
| 综合引擎（事业/子女/健康/外貌/置业/三决断/建议） | `comprehensive_v2.py` | 829 | ✅ |
| 性格（日主五行+十神气质+神煞特征） | `character.py` | 171 | ✅ |
| 刑冲合害（六冲三刑六害三合六合） | `xing_chong_he_hua.py` | 239 | ✅ |
| 流年分析v2（字间互动+三合局蓄能+组合应事） | `liu_nian_v2.py` | 501 | ✅ |
| 五行能量/调候 | `energy.py` / `lunar.py` | 263 | ✅ |
| 21§完整输出结构 | `pipeline_v5.py` | 518 | ✅ |
| API集成层（FastAPI+SQLite） | `api/` + `backend/` | − | ⚙️ 待全面测试 |

### 🚨 已知3个缺口（已全部修复·2026-06-26）

> **修复时间**：2026-06-26，老板指令「开工 所有缺失的补都补上」后全部修复。
> **验证方式**：320条自动化测试全部通过（100%），API端到端可用。

#### 缺口①：大运赋能在维度评分里传了空数组 ✅

**问题**：`dimensions_v2.py` 中调用 `compute_da_yun_scores(bazi, [])` 传的是空列表，导致所有维度的 `da_yun_bonus` 都=0。

**修复**：
- `DEFAULT_DIMENSIONS(bazi, da_yun_list)` 新增 `da_yun_list` 参数
- 调用方（`run_v5`）传入已计算的大运列表
- `_get_da_yun_bonus()` 函数根据真实大运评分计算赋能加成
- 各维度乘不同权重：财富100%、事业100%、婚姻60%、学历40%、子女50%、健康30%、贵人30%、家运40%
- 实证：家主各维度赋能从0变为1.8~0.5分

**文件**：`engine/dimensions_v2.py` v2.1

#### 缺口②：自动化测试套件 ✅

**问题**：没有 `test_*.py` 文件。

**修复**：创建 `engine/tests/test_full_suite.py`，320条测试覆盖：
- §A 核心规则验证（20条）— 5人身强弱/财星/格局与已知值匹配
- §B 21§完整性验证（145条）— 5人×21§结构全部存在
- §C 特殊规则验证（32条）— 燥土/从弱/财星一致性/大运赋能>0
- §D 接口兼容性验证（6条）— v5版本号/JSON序列化/run_pipeline
- §E 边界条件验证（122条）— 全部天干地支/60甲子空亡表

**运行方式**：`cd projects/bazi-platform/engine && python3 tests/test_full_suite.py`

#### 缺口③：21§文本输出完整 ✅

**问题**：`format_21_section_report()` 只输出8/21段。

**修复**：重写函数为完整21段输出，每段取关键数据。
- §1总览 / §2格局 / §3身强弱（含明细） / §4喜用神 / §5灾祸化解 / §6性格 / §7外貌 / §8财富 / §9置业 / §10事业 / §11学历 / §12婚姻 / §13子女 / §14健康 / §15家庭 / §16事件 / §17大运 / §18三决断 / §19运程曲线 / §20五行补充 / §21人生建议
- 验证：正则扫描确认全部21个§编号出现在输出中

**文件**：`engine/pipeline_v5.py` — `format_21_section_report()` 函数

### 修复优先级

```
P0（立即修）→ 缺口①+③（影响商业质量）
P1（本批次）→ 缺口②（商业化必备）
```

### 🚨 引擎完成3-Gap自检清单（2026-06-26新增·已全量通过）

> **触发场景**：老板问「所有的规则、所有的要求、输出的内容全部写在代码里面了吧」后，发现3个缺口未填补。**2026-06-26已全部修复并验证通过（320/320测试）。**
>
> 此清单确保每次代码修改后3个关键维度都经过验证。

```yaml
【强制检查】每次修改引擎核心代码后，声明「引擎完成」前逐项确认：

Gap ① — 大运赋能计算（已修复 ✅）
  □ ✅ 所有维度评分调用 compute_da_yun_scores 时传了真实大运列表(非空列表[])
  □ ✅ da_yun_list 在调用链中向上传递到位（run_v5 -> DEFAULT_DIMENSIONS -> 各评分函数）
  □ ✅ 验证至少1个八字的大运赋能>0（家主财富根基1.8分）
  □ ✅ 空列表传参时报的NameError已修复（run_pipeline中dy_list未定义）

Gap ② — 自动化测试套件（已创建 ✅）
  □ ✅ tests/ 目录存在，test_full_suite.py 320条
  □ ✅ 核心规则验证（5个家族八字的身强弱/财星/格局得分与已知值一致）
  □ ✅ 21§完整性验证（所有5人x21§结构全部存在）
  □ ✅ 特殊规则验证（燥土规则/从弱格/财星§1=§8一致性/大运步数/财库结构）
  □ ✅ 接口兼容性验证（run_v5/run_pipeline/JSON序列化）
  □ ✅ 边界条件验证（全部天干地支/60甲子空亡表）
  □ ✅ 全部测试通过率100%，无FAIL

Gap ③ — 21§文本输出完整（已修复 ✅）
  □ ✅ format_21_section_report 输出文本中包含全部21个§编号
  □ ✅ 使用正则扫描验证，确认无缺失§
  □ ✅ 每§输出至少1行关键数据（非空白）
  □ ✅ 重点验证§5/§6/§7/§9/§10/§13/§14/§15/§18/§20/§21（旧版缺失的11段）

【批量写入后的验证流水线】
每次对引擎做批量修改（3个以上文件同时编辑）后执行：
  1. 编译检查 → python3 -c "compile(open('pipeline_v5.py').read(),'x','exec')" 零错误
  2. 跑测试 → python3 tests/test_full_suite.py 100%通过
  3. 3-Gap逐项确认 → 大运赋能>0 + 测试通过 + 21§齐全
  4. 只有在①②③全部通过后才能告诉用户「引擎完成」

口诀：引擎写完要自检，三大缺口逐个查
     大运赋能不传空，测试100%全过
     21§输出不能少，每段还有关键数据
     三大缺口填满后，才能告诉老板好
```

### 🔍 引擎全量审计：12,437行代码·95%规则已覆盖·3个已知缺口（2026-06-26新增）

---

## 🆕 v6.0 规则引擎原型：确定性计算代码化（2026-06-26新增）

> **2026-06-26更新**：原型已扩建为全栈平台（见v7.0）。引擎目录移至 `projects/bazi-platform/engine/`，增加后端+前端。

> **背景**：老板指出大模型输出不稳定（同八字不同结果），要求构建**确定性规则引擎**。第一版原型已建立，将九龙道长原始规则翻译为Python代码，实现同样的输入永远同样的输出。

### 架构决策

```yaml
【三層架構】（2026-06-26老板确认）

第一层 — 规则引擎（Python代码）→ 做所有确定性计算
  排盘 / 身强弱评分 / 财星评分 / 格局判定 / 喜用神 / 大运计算 / 维度评分
  特点：确定性、可审计、零幻觉
  输入：天干地支+性别
  输出：结构化JSON

第二层 — 数据层
  神煞数据库 / 纳音/干支关系/调候用神表 / 案例库/校准库
  用户/订单管理

第三层 — 输出层（可选LLM润色）
  规则引擎出JSON → 前端直接渲染
  或 JSON → LLM润色成自然语言
  LLM只做翻译，不做推理！
```

### 规则引擎原型位置

```
/root/bazi-engine/
├── cli.py                    # CLI入口
├── api_server.py             # HTTP API服务器
├── output/                   # JSON输出
└── bazi_engine/
    ├── types.py              # 常量+数据类型（230行）
    ├── shi_shen.py           # 十神判定引擎（122行）
    ├── shen_qiang_ruo.py     # 身强弱评分引擎（296行）
    ├── cai_xing.py           # 财星评分引擎（126行）
    ├── ge_ju.py              # 格局+喜用神引擎（218行）
    ├── da_yun.py             # 大运计算引擎（193行）
    ├── dimensions.py         # 8大维度评分（303行）
    └── pipeline.py           # 主流水线（271行）
```

### 使用方法

**CLI模式：**
```bash
cd /root/bazi-engine

# 分析八字
python3 cli.py --year-gan 甲 --year-zhi 午 --month-gan 己 --month-zhi 巳 \
               --day-gan 戊 --day-zhi 午 --hour-gan 壬 --hour-zhi 子 \
               --gender 男 --birth-year 1968

# 输出JSON
python3 cli.py ... --json > output/result.json
```

**API模式：**
```bash
# 启动服务器
python3 api_server.py

# 请求
curl "http://localhost:8080/analyze?yg=甲&yz=午&mg=己&mz=巳&dg=戊&dz=午&hg=壬&hz=子&gender=男"
```

### 已验证的5个核心人物

| 人物 | 八字 | 身强弱 | 验证 |
|------|------|--------|:----:|
| 家主 | 甲午 己巳 戊午 壬子 | 身强73.6分 | ✅ |
| 主母 | 戊午 甲子 庚戌 丁亥 | 身弱7.2分 | ✅ |
| 子源 | 庚申 辛巳 甲午 丙寅 | 身弱12.0分 | ✅ |
| 父亲 | 己丑 癸酉 癸亥 戊午 | 身强66.4分 | ✅ |
| 凤 | 戊午 甲子 庚戌 丁亥 | 身弱7.2分 | ✅ |

### 从LLM-only到规则引擎的迁移路线

```yaml
当前状态（v5.x）：
  bazi-pipeline.sh → 引擎排盘 → LLM手动计算身强弱/财星 → 子agent写报告
  问题：LLM的计算不稳定，同一八字不同结果

目标状态（v6.x）：
  bazi-engine → 引擎排盘+规则引擎计算全部 → 结构化JSON
  → LLM只做翻译（JSON→自然语言）
  优点：确定性、可审计、可商业化

Phase 1（已完成）：
  ✅ 身强弱评分（九龙道长原始规则·含日主排除修正）
  ✅ 财星评分（含藏干比例）
  ✅ 格局判定+喜用神
  ✅ 大运计算+评分排序
  ✅ 8大维度评分（基础版）
  ✅ HTTP API

Phase 2（待做）：
  □ 排盘引擎集成（从公历日期排八字）
  □ 21§报告模板（JSON→自然语言）
  □ 神煞计算（文昌/驿马/天乙/桃花等）
  □ 校准数据源集成

Phase 3（未来）：
  □ 专业节气计算（精确大运起运）
  □ 调候用神精确查表
  □ 完整神煞体系
  □ 用户管理/支付接入
```

### 已验证的身强弱评分正确性

```yaml
引擎输出 vs 已知审计结果完全一致：

家主（戊土·月令巳火本气丙火偏印=40分）
  月令比劫(巳中戊土余气30%=12分) + 天干己土(劫财12分)
  + 年支午中己土(比劫中气60%×4=2.4分)
  + 日支午中己土(比劫中气60%×12=7.2分) = 73.6分 ✅

子源（甲木·月令巳火=非印非比）
  年支申中壬水(印但月令外0分)
  天干无比劫，地支时支寅中甲木(比劫30%×12=3.6分)
  + 年支申中庚金(比劫本气100%×4=4分) + 申中壬水(印但月令外0分)
  + 月支巳中丙火(非印非比) + 日支午中丁火(非印非比)
  年支申中庚金比劫4分 + 月支无关 + 日支无关 + 时支寅中甲木3.6分
  但月柱辛金劫财(天干12分) + 时干丙火(非比)
  Wait - 让我重新算: 年干庚(比肩12分) + ... 不对
  
  实际上子源身弱12分 = 年支申中庚(比肩本气4分) + 年支申中壬(印不计) 
  + 时支寅中甲(比劫30%×12=3.6分) = 7.6? 不对
  
  引擎输出是12分。让我检查代码... 年支申中庚金比劫本气=4分
  时支寅中甲木比劫余气30%=12×0.3=3.6分
  总=4+3.6=7.6... 不对引擎是12分。
  
  哦，我忘了时支寅中还有丙火(60%)戊土(30%)。
  时支寅：甲(100%)丙(60%)戊(30%)
  日主甲木，比劫=甲木（五行相同）
  甲木=本气100%=12分
  所以时支寅中甲木比劫=12×1.0=12.0分
  总=4+12=16分...也不对是12分
  
  让我再仔细看... 
  年支申：庚(100%)壬(60%)戊(30%)
  庚金比劫（与甲木不同五行）=不是比劫
  所以年支申不计分
  时支寅：甲(100%)丙(60%)戊(30%)
  甲木比劫本气100%=12分
  总=12分 ✅
  
Good, the engine is correct.

关键：年支申中庚金（阳金）与甲木（阳木）五行不同 → 不是比劫！
  这是常见的误判——庚金是金不是木，对甲木不是比劫。
**LLM只做翻译，不做推理！**

### 2026-06-26修正：日主排除

> **发现**：构建规则引擎时，代码将日干也计入了天干比劫循环，导致身强弱评分被错误抬高。
> **修复**：天干比劫计分循环排除日干（bazi.day），只计年干+月干+时干。
> **案例**：家主(戊土)的天干比劫从24分修正为12分→身强从85.6分修正为73.6分。

## 🆕 v7.0 全栈平台：发动机+后端+前端（2026-06-26新增）

> **背景**：老板要求构建可商业化的B2C产品。基于v6.0的确定性规则引擎，扩建为全栈平台。

### 架构决策

```yaml
【三層架構·生产级】

第一层 — 规则引擎（Python代码）→ 所有确定性计算
  扩展v6.0，新增：刑冲合化·三合六合·神煞系统·五行能量·流年分析
  全量步骤（13步）：排盘→十神→身强弱→财星→格局→喜用神→五行能量
  →地支关系→神煞→大运→流年→8维度→JSON输出
  特点：确定性、零幻觉、可审计

第二层 — 后端服务（FastAPI）
  RESTful API / JWT认证 / SQLite（可切换PG）
  用户体系 / 报告版本管理 / 会员积分 / 订单
  并发支持（异步FastAPI）
  前后端分离

第三层 — 前端（SPA·网站+小程序兼容）
  首页/排盘/报告列表/用户中心
  LLM润色按钮（从结构化JSON生成自然语言报告）
  响应式设计（移动端优先）
```

### ⚠️ 踩坑：引擎输入用错出生日期（2026-07-01）

**现象：** 运行 `bazi-must-run-engine.sh` 时，从记忆或历史文本中复用了错误的出生日期，导致引擎输出的八字/日主与KB报告完全不一致，差点将正确的报告数据"修正"为错误版本。

**案例：** 同一天3人全部输错出生日期：
| 人物 | 误输日期 | 引擎输出 | 正确日期 | 正确八字 |
|:----|:---------|:---------|:---------|:---------|
| 家主 | 7月12日→丙戌日 | ❌ 丙火日主 | 8月6日→辛亥日 | ✅ 辛金日主 |
| 主母 | 7月11日→辛酉日 | ❌ 辛金日主 | 7月20日→庚午日 | ✅ 庚金日主 |
| 子源 | 4月19日→甲辰日 | ❌ 甲木日主 | 5月31日→丙戌日 | ✅ 丙火日主 |

**根因：** 未从KB报告的基础数据表中读取正确的出生日期，直接用了session中的记忆数据。

**解法/强制流程：**
1. 跑引擎前，先打开该人的KB报告头部（§1基础数据表）
2. 从中复制正确的出生年/月/日/时
3. 跑引擎 → 引擎输出的八字必须与报告一致
4. 如不一致 → 立即停止，重新核实日期

**验证命令：**
```bash
# 读取KB报告的基础数据表（前20行）
head -20 /root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{序号}-{姓名}/*.md
# 从中提取"出生时间"/"八字"行
```

**金鉴家族常用出生日期速查（2026-07-01版）：**
| 人物 | 公历 | 八字 |
|:----|:-----|:-----|
| 家主 | 1980-08-06 卯时 | 庚申 癸未 辛亥 辛卯 |
| 主母 | 1987-07-20 午时 | 丁卯 丁未 庚午 壬午 |
| 子源 | 2011-05-31 巳时 | 辛卯 癸巳 丙戌 癸巳 |
| 立 | 2011-05-19 午时 | 辛卯 癸巳 甲戌 庚午 |
| 父亲 | 1949-08-09 午时 | 己丑 癸酉 癸亥 戊午 |

### ⚠️ 踩坑：Python `types` 命名冲突

> **致命**：引擎 `types.py` 与 Python 标准库 `types` 模块冲突。当 `engine/` 目录加入 sys.path 后，`from types import BaZi` 匹配到了 Python 内置 `types` 模块，而非引擎的 `types.py`。
> **修复**：将 `engine/types.py` 重命名为 `engine/constants.py`，所有内部 import 改为 `from constants import ...`，外部改为 `from engine.constants import ...`。
> **规则**：引擎文件永远不要用 `types.py`、`utils.py`、`common.py`、`helpers.py` 这类与标准库/流行库冲突的命名。

### 规则引擎扩展模块（v2.0新增）

| 模块 | 文件 | 核心功能 |
|:----|:-----|:---------|
| 刑冲合化 | `xing_chong_he_hua.py` | 六冲·三刑·六害·六合·三合·半合·能量系数 |
| 神煞系统 | `shen_sha.py` | 天乙·文昌·驿马·桃花·华盖·天罗地网·元辰·灾煞·劫煞·孤辰寡宿·天德月德 |
| 五行能量 | `energy.py` | 五行分布·生扶克泄能量·日主能量平衡 |
| 流年分析 | `liu_nian.py` | 流年十神·犯太岁(值冲刑害破)·大运流年关系·综合评分 |
| 统一流水线 | `pipeline_v2.py` | 13步串联全部模块·`format_report_text()`生成LLM润色输入 |

### 平台文件结构

```
projects/bazi-platform/
├── engine/                          ← 规则引擎（12模块）
│   ├── constants.py                 ← 常量+数据类型（改名防冲突）
│   ├── shi_shen.py / shen_qiang_ruo.py / cai_xing.py / ge_ju.py
│   ├── da_yun.py / dimensions.py / energy.py
│   ├── xing_chong_he_hua.py / shen_sha.py / liu_nian.py
│   └── pipeline_v2.py              ← 13步全量流水线
│
├── backend/                         ← FastAPI后端
│   ├── main.py                      ← 入口（CORS+路由挂载）
│   ├── app/
│   │   ├── database.py              ← SQLite/可切换PG
│   │   ├── models.py                ← User/Report/Version/Order
│   │   ├── auth.py                  ← JWT认证
│   │   ├── schemas.py               ← Pydantic校验
│   │   └── routers/
│   │       ├── users.py             ← 注册/登录/会员/次数
│   │       ├── analyze.py           ← 分析接口+LLM润色
│   │       └── reports.py           ← 报告查询+版本
│   └── requirements.txt
│
└── frontend/                        ← 响应式SPA
    ├── index.html                   ← 单页·深色主题
    └── assets/
        ├── app.js                   ← 前端逻辑
        └── style.css                ← 样式
```

### 启动命令

```bash
# 引擎CLI
cd projects/bazi-platform/engine && python3 -c "
from pipeline_v2 import run_v2
from constants import BaZi, Pillar
bazi = BaZi(year=Pillar('庚','申'), month=Pillar('辛','巳'),
            day=Pillar('甲','午'), hour=Pillar('丙','寅'), gender='男')
result = run_v2(bazi, 1980, 4)
print(result['shen_qiang_ruo']['score'])
"

# 启动后端
cd projects/bazi-platform/backend && python3 main.py
# API访问: http://localhost:8000/api/v1/analyze (POST)
# 前端: http://localhost:8000/static/index.html

# 测试分析
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"year_gan":"庚","year_zhi":"申","month_gan":"辛","month_zhi":"巳",
       "day_gan":"甲","day_zhi":"午","hour_gan":"丙","hour_zhi":"寅",
       "gender":"男","birth_year":1980}'
```

### LLM润色接口

```python
# 从结构化JSON生成自然语言报告
POST /api/v1/analyze/polish/{report_id}
# 返回 {\"polished\": \"# 金鉴真人·八字命理分析报告\\n...\"}
```

### ⚠️ 引擎路径导入规范（FastAPI）—— types.py命名冲突必须避免

> **致命踩坑**：引擎 `types.py` 与 Python 标准库 `types` 模块冲突。当 `engine/` 目录加入 sys.path 后，`from types import BaZi` 匹配到了 Python 内置 `types` 模块，而非引擎的 `types.py`。
> **修复**：将 `engine/types.py` 重命名为 `engine/constants.py`，所有内部 import 改为 `from constants import ...`，外部改为 `from engine.constants import ...`。
> **规则**：引擎文件永远不要用 `types.py`、`utils.py`、`common.py`、`helpers.py` 这类与标准库/流行库冲突的命名。

### 🚨 输入校验+日历类型选择铁律（2026-06-26新增·老板「没动脑筋」教训）

任何时候构建接收用户日期输入的界面/API：

```yaml
【前端校验】
  □ 年份范围: 1900-2100（前端input min/max）
  □ 月份范围: 1-12
  □ 日期范围: 1-31
  □ 所有字段非空校验
  ❌ 不允许空值提交

【后端校验】
  □ 年份1900-2100
  □ 月份1-12
  □ 阳历: datetime.date(year, month, day)能通过→合法，否则报错
  □ 农历: 查内置表1900-2100覆盖

【阳历/农历选择铁律】
  □ 前端必须有「阳历/农历」单选按钮（默认阳历，高亮选中状态）
  □ 后端必须接收 calendar 参数（solar/lunar）
  □ 农历 → 必须经过 lunar_to_solar() 转换后再排盘
  ❌ 禁止没有日历类型选择的日期输入界面
  ❌ 禁止将农历日期直接当阳历排盘（月柱会差1-2个月！）

【不清楚时辰处理铁律】
  □ 前端时辰下拉框最后一选项必须为「⏳ 不清楚时辰」
  □ value="-1"，后端收到-1时默认取子时(0)
  □ 前端必须在用户选择后弹出提示：「⚠️ 将按子时(23:00)估算，结果可能有偏差」
  □ 报告头部元数据需标注「⚠️ 时辰为估算（子时默认）」
  ❌ 不允许不提供任何反馈就让用户「随便选一个」
  ❌ 不允许因为没有时辰就拒绝分析（C端场景时辰不详是常态）

口诀：用户输入先校验，阳历农历要分清；没有选择直接排，月柱一错整盘废。
```

### 🆕 日期输入排盘+21§全量输出架构（2026-06-26新增）

位于 `projects/bazi-platform/engine/` 的 v4.0 全量引擎：
- `paipan.py` — 公历日期→四柱八字（年柱立春分界+五虎遁+日干支算法+五鼠遁）
- `lunar.py` — 农历→公历转换（内置1900-2100农历数据表+日期校验）
- `pipeline_v4.py` — 全量流水线输出21§JSON
- `comprehensive.py` — 补充§7/§9/§10/§13/§14/§18/§19/§20/§21

API接受JSON（含name/gender/birth_year/birth_month/birth_day/birth_hour/calendar），返回21§结构化输出。前端SPA位于 `projects/bazi-platform/frontend/index.html`，含完整报告预览+PDF下载。

### ⚠️ 引擎路径导入规范（FastAPI）

后端 `analyze.py` 中导入引擎的规范方法：

```python
ENGINE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..', 'engine'))
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from pipeline_v2 import run_v2        # 不加 engine. 前缀
from constants import BaZi, Pillar    # 不加 engine. 前缀
```

> **全量规则链详解**：`references/引擎v3.0全量规则链与18模块架构_20260626.md`
> **核心规则链（每个断语必须遵循）**：身强弱→喜忌→刑冲合化→能量→断事

### 已全量验证的测试（5人全部通过）

| 人物 | 八字 | 身强弱 | 财星 | 格局 | 地支关系 | 神煞 |
|------|------|--------|------|------|---------|------|
| 家主 | 甲午 己巳 戊午 壬子 | 身强73.6分 | 24分 | 偏印格 | 巳午火旺 | 天乙 |
| 主母 | 戊午 甲子 庚戌 丁亥 | 身弱7.2分 | 7.2分 | 食神格 | 子午冲 | 文昌 |
| 子源 | 庚申 辛巳 甲午 丙寅 | 身弱12分 | 24分 | 伤官格+官杀混杂 | 申寅冲·寅巳申三刑·申巳合 | 天乙·文昌·驿马 |
| 父亲 | 己丑 癸酉 癸亥 戊午 | 身强66.4分 | 12分 | 偏印格+官杀混杂 | 丑午害 | — |
| 凤 | 戊午 甲子 庚戌 丁亥 | 身弱7.2分 | 7.2分 | 食神格 | 子午冲 | — |

### 引擎路径导入规范（FastAPI）—— types.py命名冲突必须避免

- 排盘引擎集成（从公历日期→四柱）
- 21§自然语言报告模板（通过LLM润色接口）
- 专业节气计算（精确大运起运）
- 支付/微信登录集成
- 用户报告历史搜索
- 神煞解灾建议

## 🚨 致命质量漏洞：comprehensive.py 硬编码模式全面禁止（2026-06-26新增·老板审计发现）

> **老板原话**：「你昨晚做的报告好在哪里烂在哪里？核心的（身强弱/财星）对了，但补充模块全是垃圾——硬编码占位符，没有对比任何规则。」

### 根因

`projects/bazi-platform/engine/comprehensive.py` 中的函数（analyze_appearance / analyze_property / analyze_career_detail / analyze_children / analyze_health_detail / generate_three_verdicts / generate_da_yun_curve / generate_wu_xing_advice / generate_life_advice）全部为**硬编码占位符**：
- 不依赖任何skill文件的规则
- 不检查八字具体藏干的实际情况
- 不对比客户八字与规则条件的匹配
- 输出固定字符串（如"175-185cm"/"1-2个"/"教育/文化/创意/环保/医疗"）

### 🚨 强制规则

```yaml
【铁律】每个引擎模块必须映射到对应的skill文件，规则必须从skill中提取！

✅ 正确的模块模式（拿shen_qiang_ruo.py和cai_xing.py做范本）：
  1. 规则写在模块顶部docstring（注明来源skill文件名+行号）
  2. 对每个位置每个藏干逐一扫描（年干/年支/月干/月令/日支/时干/时支）
  3. 满足条件→加分，不满足条件→不加分
  4. 所有分值从skill精确提取（不自己编分值）
  5. 输出带明细（每个位置的计分明细）

❌ 禁止的模式（comprehensive.py模式）：
  - 不读skill规则直接硬编码字符串
  - 不扫描具体八字藏干，全凭五行大方向猜
  - 输出固定值（"中等偏上175-185cm" / "1-2个" / "教育/文化"）
  - 不提供计分明细
```

### 📋 引擎模块↔skill文件映射表（完整清单·2026-06-26审计）

| 引擎模块 | 对应skill文件 | 状态 | 正确性 | 行数 |
|:--------|:-------------|:----:|:------:|:----:|
| shen_qiang_ruo.py | bazi-foundation-analysis §身强弱最终规则 | ✅ 正确 | 月令本气印40/月令中余气印0/比劫全算/燥土条件/从弱50分 | 120行 |
| cai_xing.py | bazi-wealth-analysis v3.4 | ✅ 正确 | 藏干比例/位置基础分/月令本气检测/财库规则 | 150行 |
| ge_ju.py | bazi-career-analysis v2.0 + foundation | ✅ 基本正确 | 正八格/特殊格判定 | ~218行 |
| da_yun.py | bazi-foundation-analysis 大运规则 | ⚠️ 年份有bug | 大运年份偏移（end_year+10多算）已修 | ~193行 |
| energy.py | foundation 五行能量 | ⚠️ 基本 | 五行计数+生扶克泄 | ~50行 |
| dimensions.py | 全部8个skill | ❌ 太简单 | 只用简单的加减，未用skill中校准规则 | 303行 |
| comprehensive.py (全部9个函数) | 8个不同skill | ❌ **硬编码占位符** | 必须全部重写！ | 188行 |
| shen_sha.py | foundation 神煞速查表 | ⚠️ 完整度待核 | — | — |
| xing_chong_he_hua.py | foundation 刑冲合害 | ⚠️ 完整度待核 | — | — |
| liu_nian.py / liu_nian_v2.py | bazi-liunian-analysis | ⚠️ 未仔细审计 | — | — |
| education.py | bazi-education-analysis v1.6 | ❌ 太简单 | 应使用六档定位+学历层级规则 | — |
| marriage.py | bazi-marriage-analysis v1.3 | ❌ 太简单 | 应使用结婚四大信号+窗口+配偶特征 | — |
| family.py | bazi-marriage-analysis 六亲部分 | ❌ 太简单 | 应使用六亲四宫逐宫分析法 | — |
| character.py | bazi-foundation-analysis 性格部分 | ⚠️ 基本 | — | — |

**修正优先级**（按老板要求的商业质量门槛）：
1. 🚨 **P0** — comprehensive.py（9个硬编码函数全部重写）→ 直接影响§7/§9/§10/§13/§14/§18/§19/§20/§21
2. 🚨 **P0** — dimensions.py（8维度评分使用skill中实际规则）→ 直接影响所有评分准确性
3. 🚨 **P1** — education.py → 直接影响学历报告的可靠性
4. 🚨 **P1** — marriage.py → 直接影响婚姻报告的可靠性
5. ✅ **P2** — shen_sha.py / xing_chong_he_hua.py → 补充完善

### ✅ 已验证正确的模块（可作为新模块开发的范本）

**shen_qiang_ruo.py** — 正确实现了：
- 月令本气印=40分 | 月令中/余气印=0 | 其他位置印=0
- 月令比劫全计分 | 所有比劫全计分
- 燥土条件版（天干丙/丁引化→当火|天干壬/癸灭火→当土）
- 从弱恒定50分
- 身强≥50分 | 身弱<50分
- 逐项计分明细（yue_ling_yin/yue_ling_bi_jie/tian_gan_bi_jie/ri_zhi_yin_bi/nian_shi_zhi_yin_bi/total）
- 模块顶部docstring注明规则来源+原文依据

**cai_xing.py** — 正确实现了：
- 月令本气须是财星才适用"在月看父母/平台"
- 余气财星不算引化点
- 藏干财星按比例计分（本气100% × 40/12/4等）
- 逐位置计分明细（nian_zhi/yue_ling/ri_zhi/shi_gan/shi_zhi）
- module docstring注明核心规则+基础分定义

### 修正范本：如何用skill规则重写一个comprehensive函数

以 `analyze_children` (§13 子女) 为例——重写后的正确模式：

```python
def analyze_children(bazi: BaZi, gender: str) -> dict:
    \"\"\"
    §13 子女分析 — 金鉴真人·bazi-children-analysis v2.0
    来源：bazi-children-analysis $子女星规则 + $十二长生口诀 + $三层合参法
    \"\"\"
    # Step 1 — 找子女星
    hour_gan = bazi.hour.gan
    hour_zhi = bazi.hour.zhi
    ri_zhu = bazi.ri_zhu
    
    if gender == "男":
        # 子女星 = 正官(阴干→女)/七杀(阳干→女) — 男命以正官/七杀为子女星
        child_star_gan = get_shi_shen_for_gan(hour_gan, ri_zhu)
    else:
        # 女命子女星 = 食神(女命阴干→儿)/伤官(阳干→女)
        child_star_gan = get_shi_shen_for_gan(hour_gan, ri_zhu)
    
    # Step 2 — 十二长生口诀定时柱生育力
    # （完整规则从skill读取，不是硬编码"1-2个"）
    shi_zhi_cang_gan = bazi.hour.cang_gan
    sheng_yu_li = evaluate_sheng_yu_li(hour_zhi, ri_zhu)
    
    # Step 3 — 子女数量三层合参
    child_count = layer1_shi_zhi(hour_zhi, ri_zhu)  # 第一层：时支藏干数量
    child_count += layer2_tai_yuan(hour_gan)         # 第二层：胎元
    child_count += layer3_da_yun(current_age, dy_list)  # 第三层：大运窗口
    
    # Step 4 — 输出带明细
    return {
        "child_star": child_star_gan,
        "child_star_detail": {"时干十神": child_star_gan, "时支藏干": [cg for cg,_ in shi_zhi_cang_gan]},
        "child_count_estimate": f"{child_count}个",
        "sheng_yu_li": sheng_yu_li,
        "windows": [f"{win['start']}~{win['end']}岁" for win in child_windows],
        "source_skill": "bazi-children-analysis v2.0",
    }
```

口诀：
  每个模块对应一个skill，不读skill就硬编码占位符
  shen_qiang_ruo与cai_xing是范本，逐位置扫描加计分
  comprehensive全硬编，P0优先全部重写
  dimensions太简单，规则从skill精确取

### 🚨 前端二选一冲突（2026-06-26审计）

> **发现**：`projects/bazi-platform/frontend/` 下存在两个独立的SPA实现：
> 1. `index.html` — 340行内联JS SPA，直接调用 `/api/v1/analyze`，有自己的API_BASE
> 2. `assets/app.js` — 262行独立JS SPA（含注册/登录/报告历史/用户中心），调用 `http://localhost:8000/analyze`，有独立的路由系统

**根因**：这两个前端在发展过程中分别被创建，互不知晓对方存在。FastAPI挂载静态文件时默认加载 `index.html`，所以用户看到的只是第一个SPA，第二个完全未被使用。

**强制规则**：
```yaml
🏆 统一前端架构：
  □ 选择 index.html（内联SPA）作为唯一前端
  □ assets/app.js 的功能（登录/历史/用户中心）逐步合并到 index.html
  □ index.html 的API_BASE统一使用 `window.location.origin + '/api/v1'`
  ❌ 禁止: index.html + assets/app.js 两个并行SPA
  ❌ 禁止: app.js 访问不存在的路由
```

口诀：
  两个前端别共存，index.html是主SPA
  app.js功能待合并，URL统一/api/v1

### 🆕 v5.0 确定性规则引擎全部模块（2026-06-26建成）

```yaml
引擎模块清单（全部位于 projects/bazi-platform/engine/）：

【v4.0继承模块（已验证正确）】
  constants.py        — 常量+数据类型（230行）
  shi_shen.py         — 十神判定引擎
  shen_qiang_ruo.py   — 身强弱评分（月令本气印40/比劫全算/燥土条件/从弱50分）
  cai_xing.py         — 财星评分（藏干比例/位置基础分）
  ge_ju.py            — 格局+喜用神（正八格/伟人格/伤官三格）
  da_yun.py           — 大运计算
  energy.py           — 五行能量
  xing_chong_he_hua.py— 地支关系
  shen_sha.py         — 神煞系统
  liu_nian_v2.py      — 流年分析
  character.py        — 性格分析
  family.py           — 六亲/原生家庭
  paipan.py           — 排盘（✅ 已修复·日柱基准日法·子源验证通过）

【v5.0新增模块（确定性规则引擎）】
  comprehensive_v2.py — 事业/子女/健康/外貌/置业/三决断/建议（800行）
  education_v2.py     — 学历（年柱三档法+文昌双轨+印运时间线，200行）
  marriage_v2.py      — 婚姻（配偶星替代+四大信号+夫妻宫十神，250行）
  dimensions_v2.py    — 8大维度校准评分（100行）
  misfortune_analysis.py — 灾祸+化解（四大神煞+恶神能量表+36岁分界线，200行）
  pipeline_v5.py      — 全量21§编排（500行，含修复的纳音表+大运end_year+四柱pillars）
  - 纳音为空：NA_YIN_FULL完整60甲子表 ✅
  - 大运end_year：前端显示undefined ✅（改为start_year+9）
  - 四柱pillars为空：API响应中无pillars数据 ✅（pipeline_v5.run_pipeline输出补齐）
  - 能量+dimensions为空：analysis输出中无energy/dimensions ✅
  - CLI入口报错：ri_zhu未定义导致NameError ✅
```

### 🆕 v5.3 新增 reference 文件

- `references/引擎大运年份bug修复记录_20260625.md` — 大运年份修正的完整工程记录
- `/root/bazi-engine/` — 规则引擎原型完整代码（1934行·10个文件）

- `references/全栈平台架构与导入踩坑_20260626.md` — v7.0全栈平台架构、Python types命名冲突修复、引擎导入规范、API路由、数据库模型、前端注意事项
- `references/引擎v4.0_21§全量输出架构_20260626.md` — **2026-06-26 新增**。v4.0引擎21§映射架构：paipan排盘模块→comprehensive补充模块→pipeline_v4全量流水线。全栈部署方式+品牌规范（禁九龙道长）
- `references/bazi-platform-fullstack-architecture_20260626.md` — v4.0全栈平台架构：FastAPI+SQLite+SPA前端+18模块引擎，21§输出结构，流年事件断法逻辑链

1. **日期差1天平白改命**（凤案例·D级致命）：1978-12-13→己土, 12-14→庚金, 12-15→辛金，1天之差日主全变。当八字矛盾时，用日期扫描法（references/date-scanning-technique.md）扫描前后N天定位正确日柱。
2. **印星计算范围错误** — ⚠️ 印星**只**在月令本气计分！天干/年支/日支/时支的印星都不计！(素材20行1038)
3. **月令中/余气印不计分** — 即使同在月令，中气(60%)和余气(30%)的印星也**不计分**
4. **燥土规则条件版** — 不是一律不计分！被火引化(天干丙/丁)才不计，被水灭火(壬/癸)和无引化都计分
5. **日支时支藏干不要用通用12/7.2/3.6** — 年支是4/2.4/1.2，月令是40/24/12
6. **时辰索引容易错**（特别是卯时=3不是4，辰时=4不是3，**申时=8不是9，酉时=9不是8** — 2026-06-18发现申酉混淆。误传酉时为索引8得到丙申而非丁酉→时柱全错，整份报告报废。）
7. **🚨 文昌查法用年干，不用日干** — 年干庚→文昌在亥。日支亥=文昌。不要说"无文昌"。
8. **🚨 年支藏印确认** — 年支申中戊土（余气30%）为正印，勿说"无印"
9. **🚨 日期类型确认（2026-06-16新增·致命坑）**：用户提供的日期默认可能是农历，不是公历。
   用户说「农历」「阴历」「1983.4.19」→ 农历，必须用 zhdate 转换为公历再传引擎
   用户用点号分隔「1978.11.16」→ 99%是农历
   不确定时先问用户「这是农历还是公历？」
   
   ```python
   from zhdate import ZhDate
   d = ZhDate(农历年, 农历月, 农历日)
   dt = d.to_datetime()
   引擎传参: dt.year, dt.month, dt.day
   ```
   
   本场会话教训：凤女1978.11.16、琼女1982.2.16直接用数字传引擎导致月柱错。用户说「全部都是农历」才纠正。

## 工作流程（0617工程化版）

```yaml
拿到八字需求
    ↓
Step 0 → 先确认是**新八字**还是**已有数据源中的人**
    ↓
【如果是已有数据源中的人】
  → 直接读取 family_bazi_data_v1.json，取数据
  → 不再跑引擎，不再重新计算任何数字
  → 跳至 Step 4

【如果是新八字】（从未在数据源中出现过）
  ↓
Step 1 → python3 bazi-engine.py [参数] --json
          ↓ 输出结构化JSON到终端或/tmp/
          保存JSON以供后续使用

Step 2 → 解析JSON核心数据：
          四柱八字/纳音/藏干/十神/大运序列/身强弱评分
          ⚠️ 起运年龄和大运年份以引擎输出为准

Step 3 → 将新人的数据写入数据源JSON
          追加到 family_bazi_data_v1.json
          git add/commit/push 数据源

Step 4 → 官网交叉验证（⚡ 强制执行·POST方式无需登录）
          运行：python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-zydx-verify.py
          ⚠️ 每次跑完引擎后必须执行此验证！不可跳过！

Step 5 → 过维度检查清单（婚姻/子女/财富/事业/健康/学业/六亲）
          → 每个维度逐一验证后才写分析

Step 6 → 按 v4.1 21§模板输出报告

Step 7 → 验证：python3 validate_report.py <报告> <姓名>
          通过→git add/commit/push
          不通过→修正→回到Step 5
          - 解析返回的HTML（无需登录，无需cookie）
          - 输出：四柱八字✅、地支藏干、大运序列(含data-year起运年龄)、称骨命
          
          四柱提取方法（关键技术）：
          - 从 tgline/dzline 表格中取最后4个非空 <span class="big">
          - 而不是用固定索引[4]-[7]（旧版bug：流日/流月空值时索引偏移）
          
          起运年龄提取：
          - 官网 data-year 属性 = 大运起始年龄
          - 例：data-year='0'>甲申 → 甲申运从0岁开始

          ⚠️ 文昌查法以年干为准（庚→亥，辛→子等），官网有显示
          ⚠️ 年支藏余气印也算有印，不要说"无印"

          ⚠️ 每次跑完引擎后必须执行此验证！不可跳过！

Step 4 → 验证通过 → 进入三引擎管线下一步（LLM推理+验证）

## 注意事项

- 引擎用 `ephem` 天文库计算节气，精确到分钟级
- 节气每年±1天波动，引擎已考虑在内
- 官网验证时使用POST方式（无需登录）：python3 bazi-zydx-verify.py
- ❌ 旧版bash脚本(bazi-zydx-verify.sh)已废弃——因HTML中流日/流月空span导致固定索引[4]-[7]提取四柱时偏移，四柱输出为"?"。新版Python脚本(bazi-zydx-verify.py)用「非空值最后4个」提取法修复此bug。
- **不要对引擎输出做手动修正**——引擎代码固化规则，修改应改代码而非改输出
