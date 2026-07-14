# Python API 完整调用序列（2026-07-04固化 · 2026-07-14增补run_pipeline）

> **触发场景**：本会话中花费5次尝试才跑通 `paipan → BaZi → run_v5()` 序列。
> **根因**：`paipan` 参数顺序特殊（name第一非year）、输出字段名为英文、BaZi构造函数需 `gender` 字段。
> **目的**：抄走直接跑，不需要反复试错。

---

## 传统路径：paipan() → BaZi → run_v5()（扁平输出）

```python
import json, sys
sys.path.insert(0, 'projects/bazi-platform/engine')

from constants import BaZi, Pillar
from paipan import paipan
from pipeline_v5 import run_v5

# ① 排盘 — ⚠️ 第1个参数是name，不是year！
# paipan(name, gender, year, month, day, hour)
pp = paipan('姓名', '男', 1980, 5, 15, 12)

# ② 构造BaZi对象 — ⚠️ 字段名是 year_pillar / month_pillar / day_pillar / hour_pillar
#    ⚠️ 不是「年柱」/「月柱」/「日柱」/「时柱」
year = Pillar(gan=pp['year_pillar']['gan'], zhi=pp['year_pillar']['zhi'])
month = Pillar(gan=pp['month_pillar']['gan'], zhi=pp['month_pillar']['zhi'])
day = Pillar(gan=pp['day_pillar']['gan'], zhi=pp['day_pillar']['zhi'])
hour = Pillar(gan=pp['hour_pillar']['gan'], zhi=pp['hour_pillar']['zhi'])

# ③ BaZi构造 — ⚠️ gender是字段（不是ri_zhu）
#    ⚠️ ri_zhu是@property，由day.gan自动计算，不要传
bazi = BaZi(year=year, month=month, day=day, hour=hour, gender='男')

# ④ run_v5 — birth_year必须指定
result = run_v5(bazi, birth_year=1980)

# ⑤ 使用结果 — ⚠️ run_v5输出扁平的sec_*在顶层
print(result['sec_1_overview']['shen_qiang_ruo'])       # 身强弱
print(result['sec_8_wealth']['cai_xing_total'])          # 财星分数
print(result['sec_17_da_yun_detail']['list'])            # 大运序列
print(result['sec_19_overall']['curve'])                 # 运程评分曲线
```

---

## 🆕 简捷路径：get_full_paipan() → run_pipeline()（嵌套输出·一站式）

`run_pipeline()` 是 `pipeline_v5.py` 提供的高级封装，内部自动完成：
- 排盘验证
- BaZi 对象构造
- `run_v5()` 调用
- `attach_detail_analysis()` 附加分析文本
- `add_narratives()` 叙述段落
- 内部规则标记剥离

```python
import json, sys
sys.path.insert(0, 'projects/bazi-platform/engine')

from pipeline_v5 import run_pipeline
from paipan import get_full_paipan

# ① 先排盘获取四柱干支（get_full_paipan = paipan + 文昌检查）
p = get_full_paipan(2011, 5, 31, 9, '男', '子源')
# p['bazi'] = '辛卯 癸巳 丙戌 癸巳'
# p['year_pillar'] = {'gan': '辛', 'zhi': '卯'}
# p['wen_chang'] = {'has_wen_chang': False, 'wen_chang_zhi': '申', 'detail': '...'}

# ② 一站式调用 — 参数直接来自排盘dict，不用手动构造BaZi
result = run_pipeline(
    name='子源',
    gender='男',
    year_gan=p['year_pillar']['gan'],
    year_zhi=p['year_pillar']['zhi'],
    month_gan=p['month_pillar']['gan'],
    month_zhi=p['month_pillar']['zhi'],
    day_gan=p['day_pillar']['gan'],
    day_zhi=p['day_pillar']['zhi'],
    hour_gan=p['hour_pillar']['gan'],
    hour_zhi=p['hour_pillar']['zhi'],
    birth_year=2011,
    birth_month=5,
    birth_day=31,
)

# ③ 使用结果 — ⚠️ run_pipeline() 输出是嵌套结构！
paipan_section = result['paipan']        # 排盘数据（八字/四柱/文昌）
basic_data = result['basic_data']        # 基础数据（日主/藏干）
analysis = result['analysis']            # 结构化分析（身强弱/财星/格局/喜用/五行/大运）
sections = result['result']              # 21个§（sec_1_overview ~ sec_21_advice）
text_report = result['text']             # 格式化的文本报告（可直接展示）

print(sections['sec_1_overview']['bazi'])                    # 八字
print(sections['sec_3_shen_qiang_ruo']['score'])             # 身强弱分数
print(sections['sec_8_wealth']['wealth_level'])              # 财富等级
print(len(text_report), 'chars text report')                 # 文本报告
```

---

## ⚠️ run_v5() vs run_pipeline() 输出结构差异

这是最容易踩坑的地方。两个函数的输出结构**完全不同**：

| 函数 | 输出形状 | sec_* 位置 | 额外输出 |
|:-----|:---------|:-----------|:---------|
| `run_v5(bazi, birth_year=...)` | 扁平的 dict | **顶层**: `result['sec_3_shen_qiang_ruo']['score']` | 无 |
| `run_pipeline(...)` | 嵌套 dict | `result['result']['sec_3_shen_qiang_ruo']['score']` | `paipan`/`basic_data`/`analysis`/`text` |

```python
# ✅ run_v5 输出（扁平）
r = run_v5(bazi, birth_year=2011)
r['sec_3_shen_qiang_ruo']['score']       # 55.6 ✅

# ✅ run_pipeline 输出（嵌套）
r = run_pipeline(...)
r['result']['sec_3_shen_qiang_ruo']['score']  # 55.6 ✅
# 同时也提供:
r['analysis']['shen_qiang_ruo']['score']       # 55.6（相同数据，不同路径）
r['text']                                      # 完整文本报告

# ❌ 混淆两者的路径会导致 KeyError
r['sec_3_shen_qiang_ruo']                      # run_pipeline输出下不存在
r['result']['result']                           # run_v5输出下不存在
```

**选择建议**：
- 只需引擎JSON数据（21§结构化）→ 用 `run_v5()`（扁平，少一层嵌套）
- 需要引擎数据+文本报告+结构化分析 → 用 `run_pipeline()`（一站式）
- 初学/快速验证 → 用 `run_pipeline()`（参数更直观，不需要自己构造BaZi）

---

## 常见错误速查

| 错误 | 现象 | 修复 |
|:----|:-----|:-----|
| `paipan(1980, 5, 15, 12, '男', '姓名')` | TypeError: 参数位置错 | 第一参是name，不是year |
| `paipan('姓名', '男', 1980, 7, 20, 12)` ✔️ | 正确 | name→gender→year→month→day→hour |
| `pp['年柱']['天干']` | KeyError: '年柱' | 正确字段名是 `year_pillar`/`month_pillar`/`day_pillar`/`hour_pillar` |
| `BaZi(..., ri_zhu='庚')` | TypeError: unexpected keyword | ri_zhu是@property，由day.gan自动计算 |
| `run_v5(bazi)` | AttributeError: 'dict' no 'ri_zhu' | 必须传入BaZi对象（不是dict）+ 指定birth_year |
| 传入 `{'year':...}` 给run_v5 | AttributeError | run_v5需要BaZi dataclass，不是普通dict |
| `r['sec_3_shen_qiang_ruo']` 对run_pipeline结果 | KeyError | run_pipeline输出嵌套在 `r['result']` 下 |

---

## 快速验证（一行命令）

### run_v5 路径（扁平输出）
```bash
cd projects/bazi-platform/engine && python3 -c "
import json, sys; sys.path.insert(0, '.')
from constants import BaZi, Pillar; from paipan import paipan; from pipeline_v5 import run_v5
pp = paipan('测试', '男', 1980, 5, 15, 12)
bazi = BaZi(year=Pillar(gan=pp['year_pillar']['gan'],zhi=pp['year_pillar']['zhi']),
            month=Pillar(gan=pp['month_pillar']['gan'],zhi=pp['month_pillar']['zhi']),
            day=Pillar(gan=pp['day_pillar']['gan'],zhi=pp['day_pillar']['zhi']),
            hour=Pillar(gan=pp['hour_pillar']['gan'],zhi=pp['hour_pillar']['zhi']),
            gender='男')
r = run_v5(bazi, birth_year=1980)
print('身强弱:', r['sec_1_overview']['shen_qiang_ruo'], '| 财星:', r['sec_8_wealth']['cai_xing_total'], '| 大运步数:', len(r['sec_17_da_yun_detail']['list']))
"
```

### run_pipeline 路径（嵌套输出·一站式）
```bash
cd projects/bazi-platform/engine && python3 -c "
from pipeline_v5 import run_pipeline; from paipan import get_full_paipan
p = get_full_paipan(2011, 5, 31, 9, '男', '子源')
r = run_pipeline(name='子源', gender='男',
    year_gan=p['year_pillar']['gan'], year_zhi=p['year_pillar']['zhi'],
    month_gan=p['month_pillar']['gan'], month_zhi=p['month_pillar']['zhi'],
    day_gan=p['day_pillar']['gan'], day_zhi=p['day_pillar']['zhi'],
    hour_gan=p['hour_pillar']['gan'], hour_zhi=p['hour_pillar']['zhi'],
    birth_year=2011, birth_month=5, birth_day=31)
print('身强弱:', r['result']['sec_3_shen_qiang_ruo']['score'],
      '| 财星:', r['result']['sec_8_wealth']['cai_xing_total'],
      '| 文本报告:', len(r['text'][:80]))
"
```

---

## 输出结构参考（run_pipeline 完整键路径）

```
paipan:
  ├─ bazi: '辛卯 癸巳 丙戌 癸巳'
  ├─ year_gan/zhi, month_gan/zhi, day_gan/zhi, hour_gan/zhi
  ├─ ri_zhu, gender, shi_chen
  └─ wen_chang: {has_wen_chang, wen_chang_zhi, detail}

basic_data:
  ├─ ri_zhu, pillars
  ├─ tian_gan_notes, di_zhi_notes
  └─ cang_gan_map

analysis:
  ├─ shen_qiang_ruo: {score, label, details, detail_analysis, narrative}
  ├─ cai_xing: {total, wealth_level, cai_ku, detail_analysis}
  ├─ ge_ju: {main, detail, shi_shen[...]}
  ├─ xi_yong_shen: {xi[], ji[], tiao_hou, detail_analysis, narrative}
  ├─ energy: {wu_xing, wu_xing_energy, strongest_wx, weakest_wx}
  ├─ da_yun: {list[{gan_zhi, start_age, end_age, start_year, end_year, label, score}], ...}
  └─ dimensions: {}

result:
  ├─ meta: {version, engine, generated}
  ├─ sec_1_overview ~ sec_21_advice (21 sections)
  ├─ sec_17_da_yun_detail: {list[...], best_idx, worst_idx, ...}
  └─ sec_18_verdicts_detail: {detail_analysis}

text: '完整文本报告...'
```
