# Python API 完整调用序列（2026-07-04固化）

> **触发场景**：本会话中花费5次尝试才跑通 `paipan → BaZi → run_v5()` 序列。
> **根因**：`paipan` 参数顺序特殊（name第一非year）、输出字段名为英文、BaZi构造函数需 `gender` 字段。
> **目的**：抄走直接跑，不需要反复试错。

---

## 完整调用代码（直接从这里复制）

```python
import json, sys
sys.path.insert(0, '/root/bazi-platform/engine')

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

# ⑤ 使用结果
print(result['sec_1_overview']['shen_qiang_ruo'])       # 身强弱
print(result['sec_8_wealth']['cai_xing_total'])          # 财星分数
print(result['sec_17_da_yun_detail']['list'])            # 大运序列
print(result['sec_19_overall']['curve'])                 # 运程评分曲线
```

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

---

## 快速验证（一行命令）

```bash
cd /root/bazi-platform/engine && python3 -c "
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
