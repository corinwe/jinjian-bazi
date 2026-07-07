---
name: bazi-paipan-sop
描述: 金鉴真人·八字排盘标准作业程序（SOP）。封装排盘全流程：技能加载顺序→排盘源头校验→引擎评分→分析报告→发布前校验→归档推库。确保每次排盘物理化加载所有必需技能。
tags: [八字, 排盘, SOP, 金鉴真人, pipeline, 物理化]
related_skills: [bazi-engine-workflow, bazi-foundation-analysis, bazi-report-template, bazi-platform-harness, bazi-task-dispatch, maker-checker-workflow, bazi-auto-verify, bazi-calibration]
---

# 金鉴真人·八字排盘SOP v1.0

> 本SOP是排盘流程的**物理化约束**，执行排盘任务时必须按顺序走完所有Phase。
> 
> **加载方式**：已加入config.yaml → skills → auto_load，每次会话自动加载。
> **替代方案**：`skill_view('bazi-paipan-sop')` 手动加载。
> 
> **核心原则**：每一步必须先加载对应技能（skill_view），再从引擎取数据，最后做人工分析。

---

## 📋 Phase 0 — 系统就绪（自动·无需操作）

| 资源 | 来源 | 内容 |
|:-----|:-----|:------|
| SOUL.md | Hermes自动加载 | 身份+原则+Sub-Agent分工 |
| USER.md | Hermes自动注入 | 老板画像+原则+教训 |
| MEMORY.md | Hermes自动注入 | 持久记忆+路径 |
| HERMES.md | 项目级or链自动加载 | 8条铁律+工作流+技能矩阵 |

**验证：** ⚠️ 每次排盘前先`date`确认服务器时间（时区Asia/Shanghai）

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
skill_view('bazi-foundation-analysis')   # 排盘基础+身强弱+喜用神规则
```
✅ 确认内容：排盘基础规则、身强弱判定标准、藏干十神表

### Step 1.2 — 引擎工作流
```bash
skill_view('bazi-engine-workflow')             # 大运规则+流年规则+引擎调用方式
# ⚠️ 已auto_load → 但仍需确认以下规则已加载：
#   - 大运年龄ceil向上取整
#   - Q4进位（浮点月份偏移）
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
skill_view('bazi-platform-harness', 'references/project-config.md')  # 项目配置+路径
```
✅ 确认内容：项目路径、知识库路径、推库命令

### Step 1.5 — 校验工具
```bash
skill_view('bazi-auto-verify')            # 自动验证规则
```
✅ 确认内容：验证流程、常见错误模式

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
# 检查是否有易混淆项
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

### Step 4.1 — 加载对应事象技能
```bash
skill_view('bazi-destiny-analysis')       # 性格/命运综合分析（§6五重人格）
skill_view('bazi-wealth-analysis')        # 财富（§8含补财库）
skill_view('bazi-marriage-analysis')      # 婚姻
skill_view('bazi-education-analysis')     # 学业（§11含文昌判断）
skill_view('bazi-children-analysis')      # 子女
skill_view('bazi-career-analysis')        # 事业
skill_view('bazi-health-psychology')      # 健康
skill_view('bazi-misfortune-analysis')    # 灾祸
skill_view('bazi-remission-methods')      # 化解（§8.5补财库方案）
skill_view('bazi-liunian-analysis')       # 流年
skill_view('bazi-birthtime-analysis')     # 时辰判断（如需）
```

### Step 4.2 — 格局判定规则（写§2前先过此规则）

> 🚨 **格局判定是报告最容易被质疑的环节。必须有清晰规则，不能凭感觉。**
>
> **格局命名规则（严格按以下步骤）：**
> ```
> Step 1 — 月令是什么 → 月支的本气/中气/余气是什么
> Step 2 — 月令有透干吗？→ 月支的藏干有没有在天干出现？
> Step 3 — 格局名 = 月支主气的十神 + 透出的十神（如适用）
>
> 例：辛金日主，月令未土（己偏印），月干癸水（食神）
>   → 月令主气偏印，月干透食神
>   → 正确定名：「偏印格」或「偏印配食神」
>   → ❌ 不可叫「食神配印格」（食神不是在月令的主气）
>
> ⚠️ 常见错误：
>   - 混用食神/伤官（癸水是辛金的食神，不是伤官）
>   - 以透干为主气命名（正确：月令主气优先，透干为配）
>   - 自创格局名（只能用标准格局名称）
> ```
>
> **写§2前必须先过以下流程：**
> ```
> □ 月令地支是什么？主气藏干是什么？→ 定月令十神
> □ 月干是什么？→ 看月令主气是否透干
> □ 综合命名：月令主气格局为主，透干格局为辅
> □ 格局名称写完后反问：这个名称对得上月令吗？
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
示例: 辛金日主·未月令(偏印)·癸水月干(食神) → 「偏印格」不是「食神配印格」
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
  - 有财库 → 蓄库策略（如何蓄满/保护财库不被冲）
  - 无财库 → 补财库方案：
    ① 开户补库：在对应五行方位银行开户
    ② 实物补库：摆放对应五行物品
    ③ 行业补库：深耕属财的行业
    ④ 形法补库：20%月收入强制储蓄
    ⑤ 合作补库：与带财库八字的人合作
  - 充库（在财星大运时主动充实）
  - 开库（遇到刑冲害的年份如何把握开库窗口）
技能: bazi-remission-methods（写前先加载，确认补库规则）
```

#### ④ 婚姻/桃花分析（§12）— 所有报告必含，深度展开
```
判断: 所有报告必含，不设条件
内容:
  - 夫妻宫（日支）十神分析 + 喜忌
  - 配偶星定位（男:正财/偏财 女:正官/七杀）
  - 配偶特征：长相类型（子午卯酉=好/寅申巳亥=一般/辰戌丑未=敦厚）
    五行属性、性格特点（禁止列全组地支，只写实际在局中的）
  - 结婚窗口（3个，精确到年份）
  - 桃花机会（配偶星出现的流年+合夫妻宫的流年）
  - 感情走势（早婚/晚婚倾向+质量评估）
技能: bazi-marriage-analysis（写前先加载，列出核心规则再写）
```

#### ⑤ 子女分析（§13）— 所有报告必含，深度展开
```
判断: 所有报告必含，不设条件
内容:
  - 子女星定位（男:官杀为子女 女:食伤为子女）
  - 子女宫（时柱）喜忌分析
  - 子女出息程度：时柱十神+大运配合 → 上等/中等/一般
  - 子女性别倾向：从子女星阴阳+时支类型判断
  - 添丁年份
  - 子女性格特征
技能: bazi-children-analysis（写前先加载，列出核心规则再写）
```

#### ⑥ 大运列表只列到80岁（不列超过80岁的大运）
```
规则:
  - 只列到第8步大运（即覆盖到约80岁）
  - 80岁以后的大运不列在报告中（参考价值有限）
  - 引擎会计算11步，但报告只取前8步
示例:
  ✅ 大运序列只列8步：甲申→乙酉→丙戌→丁亥→戊子→己丑→庚寅→辛卯
  ❌ 不要列壬辰·癸巳·甲午（81~110岁）
```

#### ⑦ 文昌改进方案（§21.8）— 仅限≤25岁未成年人
```
判断逻辑:
  当前年龄 = 当前年份 - 出生年份
  IF 当前年龄 ≤ 25岁 → 强制包含文昌改进方案 ⚠️
  IF 当前年龄 > 25岁 → 完全不输出（成年人不需要补文昌段）

内容（仅年龄≤25时）:
  - 年干文昌位查法
  - 本命文昌检查结果（引擎wen_chang数据）
  - 文昌布局方案（方位/摆件/颜色/时间/饮食）
  - 关键学业年份
技能: bazi-education-analysis（写前先加载文昌规则）
```

### Step 4.3 — 选择报告模式 → 逐§写分析

> 🚨 **2026-07-07老板校准**：报告深度不强制1500行。**说清楚即可。**
> 
> **模式选择**（二选一，取决于需求）：
> | 模式 | 行数 | 场景 | 格式 |
> |:----|:----:|:-----|:-----|
> | **精简版（推荐）** | 800~1000行 | 快速分析/家族多人/客户初稿 | 7大板块，不加§标注 |
> | **深度版** | 按需 | 付费深度报告/学术研究 | 21§详尽展开，标注【金鉴真人·§X】 |

```bash
skill_view('bazi-report-template')        # 确认模板最新版（内置精简版+深度版双模板）
```
🚨 **铁律**：
   - 分析文本**亲自写**，不靠自动生成
   - 每行内容必须有**引擎数据 + 技能规则 双支撑**
   - 禁止模板话术/通用占位符
   - 大运年龄按**向上取整(ceil)**显示
   - 大运喜忌按**干支分别判定**

### Step 4.3 — Maker/Checker循环
```bash
skill_view('maker-checker-workflow')
```
1. Maker写分析 → Checker审查
2. Checker发现问题 → Maker修改
3. 循环直到Checkers通过

---

## 📋 Phase 5 — 发布前校验

### Step 5.1 — 五关校验
```bash
python3 projects/bazi-platform/scripts/pillar-verify.py
```
✅ 5关：五鼠遁 → 藏干十神 → 结构优先级 → 全局冲刑 → 最优性

### Step 5.2 — 全量测试
```bash
cd projects/bazi-platform/engine/tests && python3 validate_all.py
```
✅ 320条门禁全部通过

### Step 5.3 — 内容级校验
```bash
skill_view('bazi-calibration')            # 校准体系
```
✅ 对每个输出数值展示三段式证据链：
   - 数据来源（引擎哪个字段）
   - 规则来源（技能哪个规则+行号）
   - 结论

---

## 📋 Phase 6 — 归档 + 推库

### Step 6.1 — 放入人物档案（禁止写入/root/）
```bash
cp <报告文件> /root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/<序号>-<姓名>/
```
🚨 **铁律**：所有人物八字分析报告只放知识库人物档案，**禁止写入 `/root/`**。

### Step 6.2 — 推库
```bash
cd /root/weiwuji-knowledge-base
git add -A && git commit -m "📖 <消息>" && git push
cd /root/.hermes/profiles/jinjian-zhenren
git add -A && git commit -m "🧮 <消息>" && git push
```

---

## 🚨 终止条件

每个Phase完成后必须确认下一Phase可以开始：

| Phase | 终止条件 | 验证方式 |
|:------|:---------|:---------|
| 1 | 所有必需技能已skill_view | 检查技能内容不为空 |
| 2 | 排盘JSON输出到/tmp | `test -f /tmp/bazi_output.json` |
| 3 | 引擎21§全量输出 | `jq '. \| keys' /tmp/bazi_output.json` |
| 4 | 报告完整21§ | 目视检查每§存在 |
| 5 | 5关+320门禁全绿 | 查看exit code |
| 6 | git push成功 | 查看commit hash |

---

## 📌 参考文献

| 文件 | 路径 |
|:-----|:------|
| 项目铁律+技能矩阵 | `skill_view('bazi-platform-harness', 'references/project-config.md')` |
| 验证模式选择 | `references/verification-mode-selection-20260707.md` |
| 排盘门禁脚本 | `projects/bazi-platform/scripts/bazi-must-run-engine.sh` |
| 引擎代码 | `projects/bazi-platform/engine/` |
| 知识库 | `/root/weiwuji-knowledge-base` |
| 端到端验证方法论 | `references/end-to-end-verification-methodology.md` |
