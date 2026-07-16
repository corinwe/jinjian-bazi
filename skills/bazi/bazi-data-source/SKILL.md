---
name: bazi-data-source
description: 金鉴真人·八字数据源验证+锁定体系。engine.json → bazi-data-source.py → datasource.json(23字段:8字段/藏干/藏干十神/纳音/空亡/神煞/起运年龄/8大运)。所有报告模块从datasource.json取数，物理禁止凭记忆重算。
tags: [八字, 数据源, 引擎, 排盘, 物理化, 约束]
related_skills:
  - bazi-paipan-sop
  - bazi-engine-workflow
  - bazi-foundation-analysis
references:
  - scripts/bazi-data-source.py — 验证+锁定脚本(engine→datasource)
  - scripts/report-generator.py — 数据源驱动的报告生成器
---

# 八字数据源体系 · 金鉴真人

> **🚨 铁律：数据源是唯一源泉。所有报告模块只能从 datasource.json 取数，禁止凭记忆/重算。**
>
> **老板指定架构**：
> ```
> Engine CLI → engine.json → bazi-data-source.py → datasource.json → 各模块取数+规则匹配
>               (16字段)       (验证+锁定+补全)      (23字段·唯一源)   (事业规则/财富规则/大运规则)
> ```

## 数据源字段清单

| # | 字段名 | 来源 | 类型 | 用途 |
|:-:|:-------|:-----|:-----|:-----|
| 1 | 年干 | ENGINE['四柱'] | str | 8字段·天干 |
| 2 | 年支 | ENGINE['四柱'] | str | 8字段·地支 |
| 3 | 月干 | ENGINE['四柱'] | str | 8字段·天干 |
| 4 | 月支 | ENGINE['四柱'] | str | 8字段·地支 |
| 5 | 日干 | ENGINE['四柱'] | str | 8字段·天干 |
| 6 | 日支 | ENGINE['四柱'] | str | 8字段·地支 |
| 7 | 时干 | ENGINE['四柱'] | str | 8字段·天干 |
| 8 | 时支 | ENGINE['四柱'] | str | 8字段·地支 |
| 9 | 藏干 | ENGINE['藏干'] | dict | 4个地支的藏干列表 |
| 10 | 藏干十神 | calc(藏干,日主) | dict | 每个藏干成分的十神标记 |
| 11 | 十神(天干) | ENGINE['十神'] | dict | 年干/月干/日干/时干的十神 |
| 12 | 纳音 | ENGINE['纳音'] | dict | 年柱/月柱/日柱/时柱 |
| 13 | 空亡 | calc(日柱干支) | str | 日柱对应旬空 |
| 14 | 日主 | ENGINE['日主'] | str | 日干 |
| 15 | 日主五行 | ENGINE['日主五行'] | str | 金木水火土 |
| 16 | 性别 | ENGINE['性别'] | str | 男/女 |
| 17 | 八字 | ENGINE['八字'] | str | 4柱用空格分隔 |
| 18 | 身强弱总分 | ENGINE['身强弱']['总分'] | float | 身强弱评分 |
| 19 | 身强弱等级 | ENGINE['身强弱']['等级'] | str | 身强/身弱/从弱/中和 |
| 20 | 起运年龄 | ENGINE['大运']['起运'] | str | 文字描述 |
| 21 | 起运年龄(岁) | ENGINE['大运']['起运年龄'] | float | 数值 |
| 22 | 神煞 | calc(日干,年支) | dict | 8种主要神煞 |
| 23 | 大运 | ENGINE['大运']['序列'] | list | 8步大运(到80岁) |

## 物理约束机制

### 约束① — BAZI_DATASOURCE 环境变量

```bash
export BAZI_DATASOURCE=/tmp/{姓名}_datasource.json
# 不设置 → pre_tool_call_hook阻止写报告
```

### 约束② — pre_tool_call_hook

每次写文件前检查：
- BAZI_DATASOURCE 是否设置
- 数据源文件是否存在
- 报告内容中的关键数字是否与数据源一致

### 约束③ — report-generator.py

所有模块函数的唯一参数是DS（数据源dict）：
```python
def module_wealth(DS):    # 财富模块
    cai = DS['藏干十神']  # 读的是文件数据，不是记忆
def module_career(DS):    # 事业模块
    guan = DS['藏干十神']
```

### 约束④ — Phase 5.1 内容对齐校验

| 检查项 | 比对 | 
|:-------|:-----|
| 身强弱得分 | 报告中 → ENGINE['身强弱']['总分'] |
| 身强弱等级 | 报告中 → ENGINE['身强弱']['等级'] |
| 大运年龄 | 报告中 → ENGINE['大运']['序列'][i]['起始年龄'] |
| 日主 | 报告中 → ENGINE['日主'] |
| 藏干 | 报告中引用 → ENGINE['藏干']存在 |

## 使用流程

```bash
# 1. 跑引擎 → engine.json
python3 bazi-engine.py <出生参数> --json > /tmp/{姓名}_engine.json

# 2. 数据源验证+锁定 → datasource.json
python3 bazi-data-source.py /tmp/{姓名}_engine.json /tmp/{姓名}_ds.json

# 3. 设置环境变量（物理约束）
export BAZI_DATASOURCE=/tmp/{姓名}_ds.json

# 4. 各模块从数据源取数
python3 report-generator.py {姓名} 所有模块
```

## 各模块取数对照

| 模块 | 从数据源取 | 对应的规则技能 |
|:-----|:-----------|:---------------|
| 体用分析 | DS['身强弱']+DS['藏干十神'] | bazi-foundation-analysis §3B/§3A.9 |
| 大运分析 | DS['大运']+DS['藏干']+DS['年干'] | bazi-engine-workflow |
| 财富分析 | DS['藏干十神'](财+库) | bazi-wealth-analysis |
| 事业分析 | DS['藏干十神'](官杀) | bazi-career-analysis |
| 婚姻分析 | DS['日支']+DS['藏干十神'] | bazi-marriage-analysis |
| 神煞分析 | DS['神煞'] | bazi-foundation-analysis §13 |
| 纳音分析 | DS['纳音'] | bazi-foundation-analysis §11 |
| 空亡分析 | DS['空亡'] | bazi-foundation-analysis §空亡 |
