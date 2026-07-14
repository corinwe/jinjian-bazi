---
name: bazi-paipan-sop
description: 金鉴真人·八字排盘标准作业程序（SOP）。封装排盘全流程：技能加载顺序（含盲派§3B-§3O+象法11章）→排盘源头校验→引擎评分→分析报告（默认九龙+备选盲派五步工作流）→发布前校验→归档推库。确保每次排盘物理化加载所有必需技能。
tags: [八字, 排盘, SOP, 金鉴真人, pipeline, 物理化]
related_skills: [bazi-engine-workflow, bazi-foundation-analysis, bazi-report-template, bazi-platform-harness, bazi-task-dispatch, maker-checker-workflow, bazi-auto-verify, bazi-calibration, bazi-report-engine-audit]
---

# 金鉴真人·八字排盘SOP v1.3

> 本SOP是排盘流程的**物理化约束**，执行排盘任务时必须按顺序走完所有Phase。
> 
> **加载方式**：已加入config.yaml → skills → auto_load，每次会话自动加载。
> **替代方案**：`skill_view('bazi-paipan-sop')` 手动加载。
> 
> **核心原则**：每一步必须先加载对应技能（skill_view），再从引擎取数据，最后做人工分析。
> 
> ⚠️ **双系统说明**（2026-07-13更新）：
>   本体系融合了九龙道长（传统+独家倍数法）和泉师兄（盲派实务）两套知识体系。
>   两套体系在**刑冲合害优先级（三会>三合 vs 三合>三会）、体用定义、地支特殊生克**等3个核心点上存在根本冲突（详见 foundation-analysis §3B/§3C/§3D 盲派专项）。
>   - **默认**：出报告时使用 **九龙道长体系**
>   - **双系统模式**：用户明确要求「两套都出」时，同时输出两套分析
>   - 所有冲突点均独立标注，不互相覆盖
> 
> **⚠️ CWD铁律**：所有 `cd projects/bazi-platform/...` 命令，必须从 `/root/.hermes/profiles/jinjian-zhenren/` 开始执行。Hermes默认 terminal CWD 为 `/root`——必须先 `cd /root/.hermes/profiles/jinjian-zhenren && cd projects/bazi-platform/...`。
> 
> **执行体系架构**：详见 `references/execution-enforcement-architecture.md`
> - SOUL.md = 身份+纪律（3条执行铁律）+ 「必须遵循HERMES.md」
> - HERMES.md = 所有项目级规则（8条铁律+铁律A~G）
> - SOP = 详细执行步骤（21§映射+验证清单）
> - config.yaml → `tool_use_enforcement: true`（强制工具返回值校验）

---

## 📋 Phase 0 — 系统就绪（自动·无需操作）

| 资源 | 来源 | 内容 |
|:-----|:-----|:------|
| SOUL.md | Hermes自动加载 | 身份+原则+3条执行铁律+Sub-Agent分工 |
| USER.md | Hermes自动注入 | 老板画像+原则+教训 |
| MEMORY.md | Hermes自动注入 | 持久记忆+路径 |
| HERMES.md | 项目级or链自动加载 | 8条铁律+铁律A~G+工作流+技能矩阵 |
| config.yaml | 系统配置 | `tool_use_enforcement: true`（阻断执行幻觉） |

**验证：** ⚠️ 每次排盘前先`date`确认服务器时间（时区Asia/Shanghai）

### 🔴 致命陷阱：Profile缓存目录存在旧版报告

> **踩坑记录（2026-07-07）**：本次会话中，前一个上下文压缩的会话留下了 `/root/.hermes/profiles/jinjian-zhenren/cache/主母_精要报告_v1.0_20260707.md`——八字写成了「丁卯 丁未 辛巳 甲午」（辛金日主·1987-07-31），与正确版本「丁卯 丁未 庚午 壬午」（庚金日主·1987-07-20）完全不符。老板看到的是缓存中的错版，而不是重建后的正确版。
>
> **根因**：Hermes上下文压缩后，会话状态被截断。前一个会话在cache目录写的文件不会自动清除，新的会话不知情。这是一个「死文件遗留」问题。
>
> **强制清理流程（每次Phase 0执行）：**
> ```bash
> # 清除目标人物的旧缓存文件，防止老板看到过期版本
> rm -f /root/.hermes/profiles/jinjian-zhenren/cache/{姓名}_*.md
> # 确认清理干净
> ls /root/.hermes/profiles/jinjian-zhenren/cache/ 2>/dev/null || echo "cache已空"
> ```
> 
> **注意**：只清理当前人物的缓存。完整清理用 `rm -rf /root/.hermes/profiles/jinjian-zhenren/cache/`（不推荐）。

### 🚀 Hermes /goal 机制：系统级硬约束替代文件软约束

> **来源**：2026-07-07老板纠正。原理写进了SOUL.md和SOP，但我不执行，因为文件规则是「自觉遵守」，不是「强制执行」。
>
> **Hermes内置机制**：`/goal <text>` — 设置一个持久目标，每轮结束后Judge模型自动检查是否达成。未达成则system强制继续。这比文件规则更可靠。
>
> **何时使用**：当需要确保「交付前必须过校验清单」时，由老板在Feishu中输入`/goal`设目标。Judge检查的优先级 > 我的自觉。
>
> **/goal vs Kanban**：
> - `/goal` = 单Agent跨轮次执行强制（Judge每轮检查）
> - Kanban = 多角色/长链路SOP编排（任务卡片+流转状态）
> - 两者互补不冲突

---

---

## 📋 Phase 1 — 加载排盘必需技能

> **⚠️ auto_load vs skill_view 的区别：**
> - **config.yaml auto_load** → 将技能的 content 注入系统提示词（LLM已经知道这些规则）
> - **skill_view()** → 手动读取技能的完整内容，用于**确认**规则已加载、**逐条对照**具体行号
> - **流程**：auto_load已做了 → 但排盘前仍需skill_view确认内容不为空，列出核心规则再对比数据
>
> **必须按此顺序加载，不可跳过。**

### Step 1.1 — 排盘基础
```bash
skill_view('bazi-foundation-analysis')   # 排盘基础+身强弱+喜用神规则 + 盲派§3B-§3O
```
✅ 确认内容：排盘基础规则、身强弱判定标准、藏干十神表、盲派体用/功神/正局反局/三垣/神煞/串宫

### Step 1.2 — 引擎工作流
```bash
skill_view('bazi-engine-workflow')             # 大运规则+流年规则+引擎调用方式
# ⚠️ 已auto_load → 但仍需确认以下规则已加载：
#   - 大运年龄ceil向上取整
#   - 大运年份 = qi_yun_year + step×10（2026-07-14修复：取消Q4进位导致的+1偏移）
#   - 大运天干地支分开判喜忌
#   - 大运前5年天干70%/后5年地支70%
#   - 流年上午天干/下午地支
#   - 大运+流年叠加判断
```

### Step 1.3 — 报告模板
```bash
skill_view('bazi-report-template')             # 21§标准模板+年龄向上取整规则
```
✅ 确认内容：21§模板完整、大运年龄向上取整、能量分阶段规则

### Step 1.4 — 平台架构
```bash
skill_view('bazi-platform-harness')             # 项目配置+路径+推库命令
```
✅ 确认内容：项目路径、知识库路径、推库命令

### Step 1.5 — 校验工具
```bash
skill_view('bazi-auto-verify')            # 自动验证规则
```
✅ 确认内容：验证流程、常见错误模式

### Step 1.6 — 盲派象法（⛩️盲派体系·象法篇）
```bash
skill_view('bazi-image-method')           # 象法11章：天干/地支象形+六大原则+七种思路+四象技法+七步工作流
```
✅ 确认内容：象形画图法、七维扫描法、带象/换象/共象/化象技法
⚠️ 象法仅用于用户明确要求「象法分析」时使用，默认不输出

### Step 1.7 — 盲派专项技能
```bash
skill_view('bazi-wealth-analysis')        # 盲派财富§19-§29（归属权/做功路线/枭神夺食/劫财制财）
skill_view('bazi-marriage-analysis')      # 盲派婚姻§14（鸳鸯门/定份额法/阴阳定位）
```
✅ 确认内容：盲派财富做功路线、鸳鸯门婚姻口诀、归属权2×2矩阵
⚠️ 仅在用户要求「盲派分析」或「双系统对比」时使用这些§

---

## 📋 Phase 2 — 排盘 + 源头校验

> **铁律：排盘必须跑引擎，禁止手算。**

### Step 2.1 — 排盘门禁脚本
```bash
bash projects/bazi-platform/scripts/bazi-must-run-engine.sh -n <姓名> -g <性别> -y <年> -m <月> -d <日> -h <时>
```
✅ 这个脚本自动完成：
   - 调用 `paipan.py` 排四柱八字
   - 调用 `canggan-parse.py` 源头校验（标出藏干十神易混淆项）
   - 输出结果到 `/tmp/bazi_output.json`

### Step 2.2 — 人工验证排盘结果
```bash
cd projects/bazi-platform/engine && python3 -c "
from paipan import get_full_paipan
p = get_full_paipan(年, 月, 日, 时, '性别', '姓名')
print(f'八字: {p[\"bazi\"]}')
print(f'年柱: {p[\"year_pillar\"][\"gan\"]}{p[\"year_pillar\"][\"zhi\"]}')
print(f'月柱: {p[\"month_pillar\"][\"gan\"]}{p[\"month_pillar\"][\"zhi\"]}')
print(f'日柱: {p[\"day_pillar\"][\"gan\"]}{p[\"day_pillar\"][\"zhi\"]}')
print(f'时柱: {p[\"hour_pillar\"][\"gan\"]}{p[\"hour_pillar\"][\"zhi\"]}')
"
```
✅ 检查要点：
   - 五鼠遁口诀验证时柱（`skill_view('bazi-wushidun-verify')`）
   - 月柱节气验证：对比节气表确认月支正确
   - 藏干十神逐一核对：确认每个藏干对应的十神名称正确（特别注意辛+午=七杀⚠️）
   - 从 `/tmp/bazi_output.json` 检查 `canggan-parse.py` 输出的易混淆标注

---

## 📋 Phase 3 — 完整引擎评分

> **数据来源：引擎计算，LLM不做计算只做翻译。**

### Step 3.1 — 调用pipeline_v5
```bash
cd projects/bazi-platform/engine && python3 -c "
from pipeline_v5 import run_v5
from paipan import get_full_paipan
from constants import BaZi, Pillar

# 排盘 → BaZi对象
p = get_full_paipan(年, 月, 日, 时, '性别', '姓名')
bazi = BaZi(
    year=Pillar(p['year_pillar']['gan'], p['year_pillar']['zhi']),
    month=Pillar(p['month_pillar']['gan'], p['month_pillar']['zhi']),
    day=Pillar(p['day_pillar']['gan'], p['day_pillar']['zhi']),
    hour=Pillar(p['hour_pillar']['gan'], p['hour_pillar']['zhi']),
    gender='性别'
)

# 完整引擎评分（qi_yun_days=None=引擎自动基于节气表计算）
result = run_v5(bazi, 年, 月, 日, qi_yun_days=None)

# 输出所有§的JSON
import json; print(json.dumps(result, ensure_ascii=False, indent=2))
"
```
✅ 输出保存到文件便于后续使用：
```bash
cd projects/bazi-platform/engine && python3 -c "..." > /tmp/{姓名}_engine.json
```
✅ `qi_yun_days=None` 说明：不传值或传None时，da_yun.py自动基于节气表计算起运天数。无需手动导入jie_qi模块。

### Step 3.2 — 提取关键数据
从引擎JSON提取（以pipeline_v5输出为准）：

> ⚠️ **引擎JSON数据结构陷阱（2026-07-07实战发现）**：
> pipeline_v5 输出的 JSON 是**扁平结构**——所有 sec_* 在顶层，不在 `result` 下。
> ```python
> # ✅ 正确：扁平结构（pipeline_v5 实际输出）
> engine["sec_3_shen_qiang_ruo"]["score"]
> # ❌ 错误：假设嵌套在 result 下（会导致读取失败被静默捕获）
> engine["result"]["sec_3_shen_qiang_ruo"]["score"]  # KeyError
> ```
> 同时 `sec_1_overview.ri_zhu` 可能是 dict `{"gan":"庚","wx":"金"}` 而非字符串。
> 提取方式：`ri_gan = ri_zhu.get("gan","") if isinstance(ri_zhu, dict) else ri_zhu[0]`

```python
result['sec_3_shen_qiang_ruo']['score']  → 身强弱分数
result['sec_3_shen_qiang_ruo']['label']  → 身强弱标签（身强/身弱/从格）
result['sec_4_xi_yong']['xi']            → 喜用神列表
result['sec_4_xi_yong']['ji']            → 忌神列表
result['sec_8_wealth']['cai_xing_total'] → 财星总分
result['sec_17_da_yun_detail']['list']   → 大运序列（唯一真值，禁止自行计算）
result['sec_1_overview']                 → 基础身份数据
```

---

## 📋 Phase 4 — 分析 + 出报告

### Step 4.1 — 🚨 强制加载对应事象技能（不可跳过，写报告前必须执行）

> ⚠️ **每次写报告前必须加载以下所有技能，缺一不可。加载后确认内容不为空才可开始写。**
> **铁律F要求：每§前先读JSON再写。技能规则用于补充JSON中没有的推理内容。**

```bash
# 🚨 以下11个技能全部必须加载，不可选择性跳过
skill_view('bazi-destiny-analysis')       # §6性格/命运分析（五重人格）
skill_view('bazi-wealth-analysis')        # §8财富（含补财库方案）
skill_view('bazi-marriage-analysis')      # §12婚姻
skill_view('bazi-education-analysis')     # §11学业（含文昌判断·仅≤25岁）
skill_view('bazi-children-analysis')      # §13子女
skill_view('bazi-career-analysis')        # §10事业
skill_view('bazi-health-psychology')      # §14健康
skill_view('bazi-misfortune-analysis')    # §5灾祸
skill_view('bazi-remission-methods')      # §8.5补财库+§20五行补充
skill_view('bazi-liunian-analysis')       # §16流年+事件总表
skill_view('bazi-birthtime-analysis')     # 时辰判断（如需）
```

**验证：确认以下11个技能全部加载成功**
```
□ bazi-destiny-analysis    □ bazi-wealth-analysis      □ bazi-marriage-analysis
□ bazi-education-analysis  □ bazi-children-analysis    □ bazi-career-analysis
□ bazi-health-psychology   □ bazi-misfortune-analysis  □ bazi-remission-methods
□ bazi-liunian-analysis    □ bazi-birthtime-analysis
→ ❌ 缺一个都不能开始写报告
```

### Step 4.2 — 格局判定规则（写§2前先过此规则·完整体系·2026-07-07重构）

> 🚨 **格局判定是报告最容易被质疑的环节。必须严格按完整体系三步走：①主格判定 → ②成格条件校验 → ③辅格判定**
>
> **详细规则链**：bazi-fortune-analysis §6（格局判定·完整体系）
>
> **7步检查清单（每次写§2前逐项过）：**
> ```yaml
> □ 第1步：月令地支是什么？列出藏干（本气/中气/余气）
> □ 第2步：检查每个藏干是否透出天干？（逐干对比四柱）
>      ├─ 本气透出 → 以本气定正八格 ✅
>      ├─ 本气不透→中气/余气透出 → 以透出者定正八格 ✅
>      └─ 本气/中气/余气全不透 → 杂气格 ⚠️
> □ 第3步：定主格后，检查该格局的成格条件是否满足？
>      └─ 成格条件包括：身强弱校验 + 十神位置 + 比例 + 刑冲合害检查
> □ 第4步：定辅格（日支本气十神 + 月干十神）
>      └─ 主格反映人生追求，辅格反映性格/脾气/实际表现
□ 第5步：检查是否有特殊格局？（从格/从旺/化气格）
  └─ 特殊格局的判定优先级 > 正八格
  └─ **执行流程：先查身强弱，再定格局名**
      ├─ 从引擎取 sec_3_shen_qiang_ruo.label
      ├─ label == "从弱" → 格局名 = "从弱格(从杀格/从财格/从官格...)"
      │    ↳ 不再走月令循环定正八格！
      ├─ label == "从旺" → 格局名 = "从旺格(专旺)"
      │    ↳ 不再走月令循环定正八格！
      └─ 其他 → 走第1~4步月令循环定正八格
  └─ **引擎检查**：验证 ge_ju.py 的 determine_ge_ju() 在月令循环前先查从弱/从旺
> □ 第6步：格局分级（顶级/上等/中等/下等）
>      └─ 凶神制化 > 五行流通 > 正八格常规
> □ 第7步：最终格局命名 = 主格 + 辅格（如：杂气格·食神透干·自坐伤官）
> ```

### Step 4.3 — 五项必含专项内容

> 🚨 **以下五项是每份报告必含内容**，不可遗漏。判断逻辑逐条列出：

#### ① 格局定名（§2）— 所有报告必含
```
判断: 所有报告必含，不设条件
流程:
  1. 查引擎result['sec_1_overview']['ge_ju'] → 引擎给的格局名
  2. 手动验证：月支主气十神 × 月干十神 → 格局名
  3. 引擎名 ≠ 手动验证名 → 以手动验证为准（引擎可能用简称）
示例: 辛金日主·未月(己偏印/丁七杀/乙偏财全不透) → **杂气格**（不是偏印格，不是食神配印格）
  [参见 Phase 4.2 完整格局判定规则]
```

#### ② 性格分析（§6）— 所有报告必含
```
判断: 所有人都有性格分析，不设判断条件
内容: 五重人格特质（每重≥50字）+ 十神底色 + 白话解读
技能: bazi-destiny-analysis（写前先加载，列出核心规则再写）
```

#### ③ 补财库方案（§8.5含充库/蓄库/开库）— 所有报告必含
```
判断: 所有人都有财库检查，不设判断条件
内容:
  - 财库检查（日支/时支是否有辰戌丑未作为财库）
  - 有财库 → 蓄库策略
  - 无财库 → 补财库方案（5种方法）
  - 充库（在财星大运时主动充实）
  - 开库（遇到刑冲害的年份如何把握开库窗口）
技能: bazi-remission-methods
```

#### ④ 婚姻/桃花分析（§12）— 所有报告必含
```
判断: 所有报告必含，不设条件
内容:
  - 夫妻宫（日支）十神分析 + 喜忌
  - 配偶星定位（男:正财/偏财 女:正官/七杀）
  - 配偶特征（只列局中实际地支，不列全组）
  - 结婚窗口（3个，精确到年份）
  - 感情走势
技能: bazi-marriage-analysis
```

#### ⑤ 子女分析（§13）— 所有报告必含
```
判断: 所有报告必含，不设条件
内容:
  - 子女星定位（男:官杀 女:食伤）
  - 子女宫（时柱）喜忌分析
  - 子女出息程度
  - 子女性别倾向
  - 添丁年份
技能: bazi-children-analysis
```

#### ⑥ 大运列表只列到80岁
```
规则:
  - 只列到第8步大运（约80岁）
  - 80岁以后不列
```

#### ⑦ 文昌改进方案（§21.8）— 仅限≤25岁
```
IF 当前年龄 ≤ 25岁 → 强制包含文昌改进方案
IF 当前年龄 > 25岁 → 完全不输出
技能: bazi-education-analysis
```

### Step 4.3A — 21§ 逐模块执行映射

> 🚨 **每写一个§前，先加载该§对应的理论技能，列出核心规则后逐一对比命主数据，再写分析。**

```yaml
§1 一页总览表:
  引擎数据: pipeline_v5 → sec_1_overview (25字段)
  技能规则: bazi-report-template §1
  验证: 字段完整性 → 25项不缺 ✅

§2 格局分析:
  引擎数据: ge_ju.py → sec_2_ge_ju
  技能规则: bazi-fortune-analysis §6
  执行流程: Phase 4.2 七步检查清单 ✅

§3 身强弱详解:
  引擎数据: shen_qiang_ruo.py → sec_3_shen_qiang_ruo
  技能规则: bazi-foundation-analysis §4 ✅

§4 喜用神详解:
  引擎数据: ge_ju.py → sec_4_xi_yong
  技能规则: bazi-fortune-analysis §5 ✅

§5 灾祸/疾病/搬迁:
  引擎数据: misfortune_analysis.py → sec_5_zai_huo
  技能规则: bazi-misfortune-analysis ✅

§6 性格分析:
  引擎数据: character.py → sec_6_character
  技能规则: bazi-destiny-analysis (五重人格)
  执行流程: Phase 4.2 七步检查清单 ✅

§7 身材外貌:
  引擎数据: comprehensive_v2.py → sec_7_appearance ✅

§8 财富分析（含补财库）:
  引擎数据: cai_xing.py → sec_8_wealth
  技能规则: bazi-wealth-analysis + bazi-remission-methods ✅

§9 置业/买房:
  引擎数据: comprehensive_v2.py → sec_9_property
  技能规则: bazi-house-buying ✅

§10 事业分析:
  引擎数据: career_v2.py → sec_10_career
  技能规则: bazi-career-analysis ✅

§11 学历分析:
  引擎数据: education.py → sec_11_education
  技能规则: bazi-education-analysis ✅

§12 婚姻分析:
  引擎数据: marriage_v2.py → sec_12_marriage
  技能规则: bazi-marriage-analysis ✅

§13 子女分析:
  引擎数据: children_v2.py → sec_13_children
  技能规则: bazi-children-analysis ✅

§14 健康分析:
  引擎数据: health_v2.py → sec_14_health
  技能规则: bazi-health-psychology ✅

§15 六亲分析:
  引擎数据: family.py → sec_15_family
  技能规则: bazi-foundation-analysis §1.5 ✅

§16 事件总表（含婚姻子女重点年份）:
  引擎数据: liu_nian_v2.py → sec_16_events
  技能规则: bazi-liunian-analysis
  强制内容: 婚姻/子女/事业/财富/健康/搬迁/觉醒事件 ✅

§17 大运精析:
  引擎数据: da_yun.py → sec_17_da_yun_detail
  验证: 只列8步至80岁 ✅

§18 三决断:
  引擎数据: comprehensive_v2.py → sec_18_verdicts ✅

§19 运程总评:
  引擎数据: pipeline_v5.py → sec_19_overall
  技能规则: bazi-calibration ✅

§20 五行补充:
  引擎数据: comprehensive_v2.py → sec_20_wu_xing_advice
  技能规则: bazi-remission-methods ✅

§21 人生建议:
  引擎数据: comprehensive_v2.py → sec_21_advice ✅
```

**验证口诀**：
```
每写一§先读JSON，引擎数据取出来
藏干十神分数表，全部来自引擎算
不凭记忆不跳步，只有JSON没有的才用技能补
写完过后grep扫，数据一致再推库
```

### Step 4.3C — ⛩️ 盲派分析五步工作流（物理化路径·2026-07-14新增）

> **触发条件**：用户指令包含「盲派分析」「盲派怎么看」「用泉师兄体系」「双系统对比」时，强制执行此路径。
> **与九龙体系关系**：独立并存。默认出九龙体系报告，盲派分析作为备选/对比。

```yaml
第1步 — 理法篇：做功分析
  goal: 确定八字的核心做功模式
  skill: bazi-foundation-analysis §3B-§3K
  执行清单（逐条不跳）：
    □ 判体用 ─ 体=日主+印+比劫，用=财官
    □ 判宾主 ─ 主=日柱+时柱(家里)，宾=年柱+月柱(家外)
    □ 判功神废神 ─ 参与做功=功神，不参与=废神
    □ 判做功结构 ─ 制用/化用/生用/合用/墓用五种
    □ 判做功效率 ─ 合制>冲制>克制
    □ 判正局反局 ─ 原局/大运/流年三种
    □ 判家里家外 ─ 财官归属权（主位/宾位）

第2步 — 技法篇：根基+三垣+暗象
  goal: 确定八字的根基虚实和隐藏信息
  skill: bazi-foundation-analysis §3G + §3L + §3M
  执行清单：
    □ 寻根基 ─ 天干找地支/地支找库/混血儿逻辑
    □ 定份额 ─ 多根力量叠加+刑冲破坏打折
    □ 算三垣 ─ 胎元(体质)/命宫(事业)/身宫(财运)
    □ 查暗象 ─ 暗合/暗拱/暗带/暗邀

第3步 — 象法篇：取象读图
  goal: 把八字画成一幅画，看和谐度
  skill: bazi-image-method（11章完整体系）
  执行清单：
    □ 七维扫描 ─ 五行→天干→地支→十神→宫位→神煞→状态
    □ 画图四步法 ─ 每个字是什么物体→大小匹配→相互作用→整幅画
    □ 叠加分析 ─ 事业/婚恋/性格/健康各维度

第4步 — 流年断事
  skill: bazi-foundation-analysis §3E-§3F + §3N-§3O
  执行清单：
    □ 大运真假 ─ 三法验证（寻根基/鸠占鹊巢/生也微妙）
    □ 流年力量 ─ 原局有则等同/无则大于原局每个字
    □ 神煞信号 ─ 孤辰寡宿/元辰/灾煞/血刃查法
    □ 串宫压运 ─ 十二神排盘+口诀断

第5步 — 汇总输出（Maker→Checker循环）
  格式：
  ⛩️ 盲派分析结果
  ├─ 📐 理法：[做功结构]·[功神]·[正局/反局]·[家里家外]
  ├─ 🛠 技法：[根基强度]·[三垣]·[暗象]
  ├─ 🎨 象法：[七维扫描要点]·[画图解读]
  └─ 📅 流年：[大运真假]·[神煞]·[串宫]
  ⚠️ 九龙与盲派冲突点标注（如身强弱vs做功、合化vs合不讲化）
```

> 🚨 **防止漏强制项的铁律**——先搭骨架后填肉，不靠记忆靠清单。

```yaml
第1步：复制模板，建立所有§标题
  □ §1 排盘表+总览
  □ §2 格局分析
  □ §3 身强弱
  □ §4 喜用神
  □ §5 灾祸/疾病
  □ §6 性格分析
  □ §7 身材外貌
  □ §8 财富分析（含补财库方案）
  □ §9 置业/买房
  □ §10 事业分析
  □ §11 学历分析（注意：仅≤25岁含文昌）
  □ §12 婚姻/感情
  □ §13 子女分析
  □ §14 健康分析
  □ §15 六亲分析
  □ §16 事件总表（🚨强制含婚姻子女重点年份）
  □ §17 大运精析
  □ §18 三决断
  □ §19 运程总评
  □ §20 五行补充
  □ §21 人生建议

第2步：每个§填入[占位符]标记强制项
  例：§16 → 「[婚姻子女重点事件年份表:待填]」

第3步：逐§填入内容，每填完一个打勾✅

第4步：输出前扫描占位符 — 应全部被替换，零残留
```

### Step 4.3C — 每§写完后强制JSON校验

> 🚨 **铁律F的物理执行闸门**——每写完一个§，标记✅之前必须反向验证数据来自JSON而非记忆。

```yaml
① 从报告中提取该§的所有数字/十神/五行数据
② 对比引擎JSON中的对应字段
③ 逐项确认一致：
   □ 藏干十神名 = JSON shi_shen 字段
   □ 身强弱分数 = JSON score 数值
   □ 财星分数 = JSON cai_xing_total 数值
   □ 大运干支/年份 = JSON da_yun_list
   □ 喜用/忌神列表 = JSON xi/ji
④ 不一致 → 以JSON为准改报告
⑤ 一致 → 标记 ✅
```

### Step 4.4 — 选择报告模式 → 逐§写分析

> 🚨 **2026-07-07老板校准**：报告深度不强制1500行。**说清楚即可。**
>
> **双版本选择**（2026-07-10新增）:
> ```yaml
> IF 用户类型 == "免费" 或 "默认":
>   → skill_view('bazi-report-template')  # 精简版（1,500-2,500字）
>   → 模板文件: bazi/bazi-report-template/SKILL.md
>   
> IF 用户类型 == "付费" 或 "VIP":
>   → skill_view('bazi-report-template-detailed')  # 详尽版（4,000-8,000字）
>     或 skill_view('bazi-report-template', 'references/detailed-template.md')
>   → 模板文件: bazi/bazi-report-template/references/detailed-template.md
> 
> IF 用户类型 == "内部使用" 或 "老板查看":
>   → 使用详尽版（含完整推理过程和数据引用）
> ```

```bash
skill_view('bazi-report-template')  # 或 references/detailed-template.md
```

### Step 4.5 — Maker/Checker循环
```bash
skill_view('maker-checker-workflow')
```

### 🆕 Step 4.6 — 双系统报告生成工作流（2026-07-13新增·家族对比报告实战验证）

> ⚠️ **双系统逻辑**（老板指令）：
>   - **默认**：只出九龙道长体系报告
>   - **用户明确要求「两套都出」**：同时输出两套体系的对比分析
>   - 冲突点必须独立标注，不强行统一

```yaml
IF 用户要求 == "单系统" 或 未指定:
  → 只出九龙道长体系报告（默认）
  → 完全不需要提及泉师兄体系
  → 报告结构和内容与之前完全一致

IF 用户要求 == "双系统":
  → 每人都出一份对比报告（格式如下）

双系统报告结构（对照家族三人对比报告实战验证）:

§0 声明 → 开篇说明双系统结构
  ├─ 两套体系来源（九龙道长·传统+倍数法 / 泉师兄·盲派实务）
  ├─ 3个根本冲突点（刑冲合害优先级/体用定义/地支特殊生克）
  └─ 默认体系：九龙道长

§1 核心引擎数据（共享）→ 两套体系共用
  ├─ 八字排盘（共享）
  ├─ 身强弱评分（引擎计算，共享）
  ├─ 喜用神列表（引擎从九龙体系输出）
  └─ 财星总分（引擎计算，共享）

§2～§20 逐§双栏对比
  ├─ 每个§先出九龙体系的分析（默认）
  ├─ 再出泉师兄体系的分析（备选）
  └─ 冲突点用 🆚 标记突出显示

§21 冲突点汇总
  ├─ 仅列出两套体系给出不同结论的关键维度
  ├─ 如：己丑大运（老板）→ 九龙=守成期 vs 泉师兄=墓开破财⚠️
  ├─ 不强行统一，让用户自己验证
  └─ 标注建议优先采信哪一套（倾向九龙体系）

双系统报告的输出格式建议:
  ┌─ 每个章节先用🏆标注九龙体系结论
  └─ 再用⛩️标注泉师兄体系结论
  例:
  🏆 九龙：偏印格·身强64分·喜木水火
  ⛩️ 泉师兄：体强用弱·体（比劫）>>用（财官）→等大运补财

双系统报告适用场景:
  □ 用户明确要求两套都出
  □ 家族成员对比分析（同时覆盖多人的统一视角）
  □ 内部使用（老板自己查看）
  □ 研究/校准用途
  ❌ 不适用于付费客户的标准报告输出
```

---

## 📋 Phase 5 — 发布前校验

### Step 5.1 — 五关校验
```bash
python3 projects/bazi-platform/scripts/pillar-verify.py
```

### Step 5.2 — 全量测试
```bash
cd projects/bazi-platform/engine/tests && python3 validate_all.py
```

### Step 5.3 — 内容级校验
```bash
skill_view('bazi-calibration')
```

### 🚨 Step 5.4 — 交付物理门禁（新增·2026-07-07）
> **每次交付给老板前必须先跑，exit 0才可交付。不通过→修复→重跑→通过后再说OK。**

```bash
bash projects/bazi-platform/scripts/run-with-gate.sh {姓名} /tmp/{姓名}_报告.md [/tmp/{姓名}_engine.json]
```

**15项门禁清单**:

```
线A（引擎数据·7项）: A1身强弱 A2财星 A3五行生克 A4十神 A5大运 A6喜忌 A7空亡
线B（/goal交付·8项）: G1品牌名 G2性格分析 G3≥800行 G4婚姻子女 G5补财库
                         G5b财库方位 G6数据来源 G7工作变动分析
```

**执行顺序**: 先跑5.1(~5.3)，再跑5.4门禁。全部通过才进入Phase 6推库。

---

## 📋 Phase 6 — 归档 + 推库

### Step 6.1 — 放入人物档案（禁止写入/root/）
```bash
cp <报告文件> /root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/<序号>-<姓名>/
```

### Step 6.2 — 推库
```bash
cd /root/weiwuji-knowledge-base && git add -A && git commit -m "📖 <消息>" && git push
cd /root/.hermes/profiles/jinjian-zhenren && git add -A && git commit -m "🧮 <消息>" && git push
```

---

## 📋 Phase 7 — 纠错修正工作流

### Step 7.0 — 铁律⑨+铁律0：先查原始理论，再写入→审计→说OK

> **来源**: HERMES.md 铁律⑨（有疑先查九龙）+ SOUL.md 铁律0（写入→审计→说OK）
> **口诀**: 有疑先查九龙，不猜不赌不蒙；写下→审计→说OK，三步少一不算完

```yaml
每次老板交代任何规则/要求/修改/补充，必须执行以下三步，缺一不可：

第1步 — 先查原始理论再动手
  → 有疑先查九龙，不猜不赌不蒙
  → 查理论5步：①基础技能②事象技能③§索引④行号对比⑤以原始为准
  → 禁止：凭感觉说"I think" / "应该是" / "大概率"

第2步 — 写入必加载文件
  → 规则写入 SOUL.md 或 HERMES.md
  → grep 确认写入成功

第3步 — 全盘物理审计
  → 用真实数据/报告验证规则是否真的被执行了
  → 检查链：引擎代码 → 技能SKILL.md → SOP → 报告输出 → 验证脚本

第4步 — 审计通过才说OK
  → 四步全过 → 报告"已完成，已审计"
  → 任一步没过 → 继续修，不说OK
```

### Step 7.1 — 确认问题范围
```
当老板指出问题时：
  ├─ 不要辩解！
  └─ 立即确认：「明白，我查原始理论然后全面修复」
然后区分问题类型：
  □ 单点问题 → 直接修复+验证
  □ 体系性问题 → 执行全流程修正 Step 7.2~7.6
```

🚨 **双验必读**：当老板指出理论规则错误时，必须同时检查**技能文件（理论层）+ 引擎代码（实践层）**，两层可能有不一致。
详见 `references/dual-layer-correction-workflow.md`

### Step 7.2 — 回原始理论全量验证
```
第1步：找到所有相关的原始理论素材
第2步：全量提取，非抽样
第3步：标记已有 vs 缺失 vs 冲突
```

### Step 7.3 — 补漏所有相关技能模块
```
列出完整链路 → 逐文件检查修复
```

### ⚠️ Step 7.3A — 技能文件存在性检查（2026-07-10新增·全量审计触发）

> **教训**: 2026-07-10审计发现SOP引用的5个技能文件在磁盘上不存在。
> **铁律**: SOP中引用的每个技能文件必须先确认磁盘存在，才能执行skill_view。

```yaml
① 提取SOP中所有 skill_view('xxx') 引用
② 逐个检查 /root/.hermes/profiles/jinjian-zhenren/skills/bazi/xxx/SKILL.md 是否存在
③ 存在 → ✅ 继续
④ 不存在 → 创建后继续（或调整SOP引用到已存在技能）
⑤ 全量审计时（至少月一次），执行此检查
```

### Step 7.4 — 焊死物理化链（7个焊接点）
```
① SOUL.md → ② HERMES.md → ③ SOP → ④ 技能SKILL.md
→ ⑤ 引擎代码 → ⑥ 参考文件 → ⑦ 验证脚本
```

### Step 7.5 — 端到端验证
```
用真实八字跑通全流程
```

### Step 7.6 — 推库 + 汇报
```
git add/commit/push 双库
```

---

## 🚨 终止条件

| Phase | 终止条件 |
|:------|:---------|
| 1 | 所有必需技能已skill_view |
| 2 | 排盘JSON输出到/tmp |
| 3 | 引擎21§全量输出 |
| 4 | 报告完整21§ |
| 5 | 5关+320门禁全绿 |
| 6 | git push成功 |
