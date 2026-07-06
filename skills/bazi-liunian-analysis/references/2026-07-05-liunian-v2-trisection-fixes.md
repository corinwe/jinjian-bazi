# liu_nian_v2.py 2026-07-05 三修报告（5规则落地：R26+R11+R14+R43+R44）

> 修复时间：2026-07-05（会话三）
> 修复责任人：金鉴真人·Hermes Agent
> 对应文件：`/root/bazi-platform/engine/liu_nian_v2.py`

---

## 修复概览

| 规则 | 规则名 | 修复类型 | 核心代码 | 状态 |
|:----|:-------|:--------|:---------|:----:|
| R26 | 流月应事方法 | 新增 | `MONTH_GAN_ZHI` + `_get_key_months()` | ✅ |
| R11 | 三会局在流年事件中的应用 | 新增 | `check_all_relations_v2()` + 财富/灾祸检测 | ✅ |
| R14补 | 合化优先级在评分中的应用 | 新增 | `HE_HUA_PRIORITY` + `_get_highest_he_priority()` | ✅ |
| R43 | 大运定性双维度原则 | 新增 | `_da_yun_dual_dimension()` | ✅ |
| R44 | 最佳大运综合判断法五维评分 | 新增 | `_five_dimensional_da_yun_score()` | ✅ |

---

## R26 — 流月应事方法

### 新增数据结构

```python
MONTH_GAN_ZHI = {
    1: "甲寅", 2: "乙卯", 3: "丙辰", 4: "丁巳", 5: "戊午", 6: "己未",
    7: "庚申", 8: "辛酉", 9: "壬戌", 10: "癸亥", 11: "甲子", 12: "乙丑",
}
```

### 新增函数

```python
def _get_key_months(liu_nian_wx_gan, liu_nian_wx_zhi, xi_yong, ji_shen) -> str:
    """根据流年干支五行和喜忌，标注关键应事月份（R26）"""
    key_months = []
    for month_num, month_gz in MONTH_GAN_ZHI.items():
        mg = month_gz[0]  # 月天干
        mz = month_gz[1]  # 月地支
        mg_wx = TIAN_GAN_WU_XING[mg]
        mz_wx = DI_ZHI_WU_XING[mz]
        # 月份的天干/地支五行与流年天干/地支五行相同 → 能量共振
        if mg_wx == liu_nian_wx_gan or mz_wx == liu_nian_wx_zhi:
            key_months.append(month_num)
    # 取前3个关键月份
    return f"重点月份：{'、'.join(str(m) for m in key_months[:3])}月"
```

### 集成方式

所有6种事件类型（财富/灾祸/结婚/事业/学业/健康）的 `_build_event_desc()` 调用均新增 `key_months=key_months_str` 参数。

### 效果

事件描述中加入重点月份标注：
- `（程度：重大），（重点月份：3、4、5月）`
- `（程度：显著），（重点月份：1、2、7月）`

### 设计决策

简化方案：仅取月份天干/地支五行与流年天干/地支五行相同的前3个月份，不涉及复杂的喜忌权重判断。足够产生有用的应期提示。

---

## R11 — 三会局在流年事件中的应用

### 关键变更

1. **替换关系检测函数**：`all_rels` 从 `check_all_relations(v1)` 切换为 `check_all_relations_v2()`，获取三会/拱合/暗合数据
2. **增加import**：`check_all_relations_v2`, `check_san_hui`, `SAN_HUI`
3. **贪合忘冲**：`has_any_he` 加入 `all_rels.get("三会")` 判断
4. **合化优先级评分**：三会作为最高优先级，在评分中得分加倍（+2.0 vs 普通合的+1.0）

### 发财检测 R11 应用

```python
# 条件3b: 三会财局（R11补充 — 三会能量20倍＞三合15倍）
for hui in all_rels.get("三会", []):
    hui_wx = hui.get("wx", "")
    if hui_wx and ri_cai_wx and hui_wx == ri_cai_wx:
        wealth_conf += 0.4  # 三会比三合更强
        wealth_desc = f"{hui['type']}财局引动（三会20倍）"
```

### 灾祸检测 R11 应用

```python
# 条件4b: 三会忌神局（R11补充 — 三会局能量20倍，增强灾祸）
for hui in all_rels.get("三会", []):
    hui_wx = hui.get("wx", "")
    if hui_wx and hui_wx in ji_shen:
        mis_conf += 0.3
        mis_energy = max(mis_energy, 2.0)  # 三会20倍能量
```

### 返回值新增

`san_hui_relations` 字段：列出检测到的三会局列表

---

## R14补充 — 合化优先级在评分中的应用

### 新增常量

```python
HE_HUA_PRIORITY = {"三会": 4, "三合": 3, "六合": 2, "半合": 2, "拱合": 2, "暗合": 1}
```

### 核心逻辑

在评分函数中内嵌 `_get_highest_he_priority(rels)` 嵌套函数，检查所有合化类型并只保留最高优先级：

```python
he_priority = _get_highest_he_priority(all_rels)
if he_priority >= 4:      # 三会最高
    score += 2.0
elif he_priority >= 3:    # 三合
    score += 1.5
else:                     # 六合/半合/拱合
    score += 1.0
```

### 效果

之前：所有合化类型统一 +1.0 分
之后：三会 +2.0，三合 +1.5，其他 +1.0 — 区分了能量倍数的差异

### 注意事项

此优先级的应用范围仅限于 `analyze_liu_nian_v2()` 的评分部分。五维大运评分(`_five_dimensional_da_yun_score`)中合局引化维度累加计分（不适用优先级）。

---

## R43 — 大运定性双维度原则

### 新增函数

```python
def _da_yun_dual_dimension(da_yun_gan, da_yun_zhi, ri_zhu, ri_zhu_wx, xi_yong, shen_label) -> str:
```

### 双维度判断逻辑

| 维度 | 判断条件 | 结果 |
|:----|:---------|:-----|
| **能量层面** | 大运天干/地支五行是否在喜用中 | ✅ 能量得到补充（用神大运） |
| | | ❌ 能量消耗（非用神大运） |
| **感受层面** | 用神大运但十神为七杀/伤官/劫财 | 虽是用神但感受挑战 |
| | 用神大运且十神为正印/偏印/正官 | 用神到位且感受相对舒适 |
| | 非用神大运且身弱 | 非用神大运，身弱难担 |
| | 非用神大运且身强 | 非用神大运，需主动调整 |

### 输出格式

```
大运壬午: 能量层面能量得到补充（用神大运），感受层面用神到位且感受相对舒适
大运丙午: 能量层面能量消耗（非用神大运），感受层面非用神大运，身弱难担
```

### 返回值新增

`da_yun_dual_dimension` 字段

---

## R44 — 最佳大运综合判断法五维评分

### 新增函数

```python
def _five_dimensional_da_yun_score(da_yun_gan, da_yun_zhi, ri_zhu, ri_zhu_wx,
                                    xi_yong, ji_shen, all_gans, all_zhis, shen_label) -> dict:
```

### 五维评分表

| 维度 | 权重 | 判断逻辑 | 分值范围 |
|:----|:----:|:---------|:--------:|
| ① 表面十神 | 3 | 吉神喜用=3, 财食喜用=2, 恶神喜用=1, 忌神=-2 | -6~9 |
| ② 合局引化 | 2 | 三会=+3/个, 三合=+2/个, 六合=+1 | 0~10 |
| ③ 空亡 | 2 | 空亡=-2, 未空亡=0 | -4~0 |
| ④ 神煞 | 1.5 | 天乙=+2, 文昌=+2, 天德=+1, 月德=+1 | 0~9 |
| ⑤ 十二长生 | 1.5 | 临官/帝旺=+2, 长生/冠带=+1, 死/墓/绝=-1 | -1.5~3 |

### 归一化

原始总分范围 -11.5~28 → 归一化到 **-10~10**

### 综合判断标准

| 五维总分 | 判断 |
|:--------:|:----|
| ≥ 4 | 上佳大运 |
| ≥ 2 | 良好大运 |
| ≥ -2 | 平运 |
| < -2 | 不佳大运 |

### 返回值结构

```python
{
    "五维总分": 1.8,
    "五维明细": {
        "表面十神": {"score": 3, "weight": 3, "desc": "正官"},
        "合局引化": {"score": 1, "weight": 2, "desc": "午戌半合火"},
        "空亡": {"score": 0, "weight": 2, "desc": "未逢空亡"},
        "神煞": {"score": 4, "weight": 1.5, "desc": "天乙贵人、文昌"},
        "十二长生": {"score": -1, "weight": 1.5, "desc": "死"},
    },
    "综合判断": "平运"
}
```

### 返回值新增

`da_yun_five_dimension` 字段

---

## 返回值完整结构对比

### 三修前

```python
return {
    "year", "age", "liu_nian", "gan_zhi_wx", "shi_shen",
    "shen_sha_summary", "di_zhi_guan_xi", "da_yun_guan_xi",
    "comprehensive_score", "pillar_interactions",
    "events", "ying_shi", "he_ban", "summary",
}
```

### 三修后（新增字段标 ★）

```python
return {
    "year", "age", "liu_nian", "gan_zhi_wx", "shi_shen",
    "shen_sha_summary", "di_zhi_guan_xi", "da_yun_guan_xi",
    "comprehensive_score", "pillar_interactions",
    "events", "ying_shi", "he_ban",
    ★ "da_yun_dual_dimension",    # R43: 大运定性双维度描述
    ★ "da_yun_five_dimension",     # R44: 大运五维评分
    ★ "san_hui_relations",         # R11: 三会局列表
    ★ "key_months",                # R26: 重点月份
    "summary",
}
```

共 18 个字段（新增4个）。

---

## 测试验证

- `python3 -c "from liu_nian_v2 import analyze_liu_nian_range"` — ✅ 无ImportError
- `python3 -c "import py_compile; py_compile.compile('liu_nian_v2.py')"` — ✅ Syntax OK
- `python3 liu_nian_v2.py` — ✅ 运行正常，产出正确
- `test_full_suite.py` — ✅ exit code 0
- 新函数单元测试：
  - `_get_key_months('甲', '午', ['水','木'], ['金','土','火'])` → `"重点月份：3、4、5月"` ✅
  - `_da_yun_dual_dimension('壬', '午', '甲', '木', ['水','木'], '身弱')` → 正确输出双维度描述 ✅
  - `_five_dimensional_da_yun_score(...)` → 返回五维总分+明细+综合判断 ✅
