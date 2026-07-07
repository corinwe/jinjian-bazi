# 全链路数据流字段名校验 · 2026-07-05 实战记录

## 数据流四步

```
get_full_paipan(年,月,日,时,性别,姓名)
  ↓ 输出 paipan_result (dict)
  ↓ keys: name, gender, birth_date, birth_hour, shi_chen, bazi,
  │       year_pillar:{gan,zhi}, month_pillar:{gan,zhi},
  │       day_pillar:{gan,zhi}, hour_pillar:{gan,zhi}, wen_chang
  ├─ ❌ 没有 "pillars" 顶层key
  ├─ ❌ pillar里没有 tian_gan, di_zhi, cang_gan 字段
  └─ ❌ 没有 "ri_zhu" 顶层key
  
BaZi(year=Pillar(gan,zhi), month=..., day=..., hour=..., gender=...)
  ↓ 构造 engine 内部对象
  ↓ 属性: year.cang_gan (list[tuple[str,int]])
  │      month.zhi, year.zhi 等
  
run_v5(bazi, birth_year, birth_month, birth_day)
  ↓ 输出 result dict (21§)
  ↓ 关键路径:
  ├─ sec_1_overview: bazi, na_yin, ri_zhu:{gan,wx}, qi_yun_age, kong_wang
  ├─ sec_2_ge_ju: main, detail, shi_shen, condition
  ├─ sec_3_shen_qiang_ruo: score, label, details:{yue_yin,yue_bi,tg_bi,rz,nsz,total}
  ├─ sec_8_wealth: cai_xing_total, wealth_level, cai_ku, wealth_years
  └─ sec_17_da_yun_detail: list (dy start_year, start_age, end_age, score)

generate_deep_report({"paipan":paipan_r, "basic_data":paipan_r, "result":pipeline_r}, name, gender, version)
  ↓ 内部变量
  ├─ pp = engine_json["paipan"] → paipan_result
  ├─ bd = engine_json["basic_data"] → 同paipan_result（没有额外数据）
  ├─ r = engine_json["result"] → pipeline result dict
  ├─ s1~s21 = r.get("sec_N_xxx", {})
  └─ 五行能量: 用 from energy import compute_energy_profile 直接算 BaZi 对象
```

## 已修复的字段名不匹配

| 文件 | 原代码 | 实际字段 | 修复 |
|:----|:-------|:---------|:-----|
| generate_deep_report.py L286 | `bd['month_pillar'].get('di_zhi')` | `bd['month_pillar'].get('zhi')` | 显示月令从「?」→ 「未」 |
| generate_deep_report.py L98-99 | `bd.get('ri_zhu',{})` | `s1.get('ri_zhu',{})` | 日主从空 → 正确显示 |
| generate_deep_report.py L300-301 (已删除) | `bd['pillars']['year']['tian_gan']` | 不存在此结构 | 改用 `energy.compute_energy_profile(bazi_obj)` |
| generate_deep_report.py L300-301 (已删除) | `bd['pillars']['year']['cang_gan']` | 不存在此结构 | 改用引擎计算 |

## 2026-07-05 追加发现: `report_generator.py` 传空 paipan/basic_data

### 致命陷阱：空 paipan/basic_data

`report_generator.py` 第34行调用：
```python
deep = generate_deep_report({"paipan": {}, "basic_data": {}, "result": result}, ...)
```
**paipan和basic_data传的是空dict `{}`！** 这意味着 `generate_deep_report.py` 中任何从 `pp` 或 `bd` 读取数据的代码都会失败。

### 修复方案：从bazi字符串解析干支

新增 `_parse_bazi_str()` 函数直接解析 bazi 字符串（如 `"庚申 癸未 辛亥 辛卯"`）：
```python
def _parse_bazi_str(bazi_str: str):
    parts = bazi_str.strip().split()
    if len(parts) >= 4:
        yg, yz = parts[0][0], parts[0][1]
        mg, mz = parts[1][0], parts[1][1]
        dg, dz = parts[2][0], parts[2][1]
        hg, hz = parts[3][0], parts[3][1]
        return yg, yz, mg, mz, dg, dz, hg, hz
    return "", "", "", "", "", "", "", ""
```

bazi字符串在 `sec_1_overview.bazi` 中始终可用，不依赖外部 paipan 数据。

### 涉及修复点

| 原始代码 | 修复 | 效果 |
|:---------|:-----|:-----|
| `bd.get('month_pillar',{}).get('zhi','?')` | `_parse_bazi_str(bazi_str)[3]` | 月令从`?` → **正确地支** |
| BaZi从 `pp.get("year_pillar",{}).get("gan")` 构建 | BaZi从 `_parse_bazi_str()` 直接构建 | 五行能量从**暂不可用** → **正确分布** |

### 两种paipan数据结构的差异

| 来源 | 访问路径 | 示例 |
|:-----|:---------|:-----|
| `get_full_paipan(1980,8,6,6,'男','魏启令')` | `result["year_pillar"]["gan"]` | `"庚"` |
| `pipeline_v5.run_pipeline(...)` 的 `output["paipan"]` | `output["paipan"]["year"]["gan"]` | `"庚"` |

`pipeline_v5` 的 paipan 块使用 `year/month/day/hour` 作为 pillar key，而 `get_full_paipan` 使用 `year_pillar/month_pillar/day_pillar/hour_pillar`。`generate_deep_report.py` 在任何一种结构下都不能安全读取——bazi字符串解析是统一的鲁棒方案。

## 审计方法论（老板亲令）

1. **建立完整数据流映射**
   - 跑一次 `get_full_paipan()` → 打印所有key
   - 跑一次 `run_v5()` → 打印所有sec_* 的key
   - 有实际数据，不靠记忆

2. **逐级核对字段名**
   - generate_deep_report.py 中每个 `.get("xxx")` 
   - 对照实际数据结构的key名
   - 特别注意：bd(paipan) vs pp(paipan) vs r(pipeline) 是三个不同的数据源

3. **验证fallback链**
   - 当主路径读取不存在时，fallback是否真正生效？
   - 例：`bd.get('ri_zhu')` 不存在 → fallback到 `s1.get('ri_zhu')` → 需要实际运行确认

4. **致命陷阱**
   - paipan_result 的 pillar 结构只有 `gan` 和 `zhi`，没有 `tian_gan`/`di_zhi`/`cang_gan`
   - paipan_result 没有 `pillars` 顶层key
   - bd = basic_data = 同 paipan_result（没有额外数据！）
   - 五行能量不能用bd/pp数据独立算（字段名对不上）→ 必须用 engine/energy.py
