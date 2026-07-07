# career_v2.py v3.1 引擎升级（2026-07-05）

> 本次升级基于三模块审计发现：丢官信号④未实现 + 开官库缺失 + 恶神制化级别不精细 + 循环自导入。

## 升级项

| 升级项 | 类型 | 函数/位置 | 改动 |
|:-------|:----|:---------|:-----|
| 丢官信号④ | 🔴 Bug修复 | `_analyze_diu_guan_signal()` | 官星被合化（负面）从注释占位符→完整实现 |
| 开官库分析 | 🆕 功能新增 | `_analyze_kai_guan_ku()` + `_GUAN_KU_MAP` | 91行新函数+映射表 |
| 恶神制化级别精细化 | 🔧 改进 | `analyze_career_full()` | 新增2个中级（身弱杀无制/身弱官无制）→ 7级全覆盖 |
| 循环自导入 | 🔴 P0修复 | `_analyze_diu_guan_signal()` | 删除 `from career_v2 import GUAN_HE_HUA` |

## 丢官信号④ 实现逻辑

```python
# 天干五合映射表
_WU_HE_WU_XING = {
    ("甲", "己"): "土", ("乙", "庚"): "金",
    ("丙", "辛"): "水", ("丁", "壬"): "木",
    ("戊", "癸"): "火",
}

# 遍历八字天干，找出官杀（正官/七杀）所在的字
# 检查该字是否与其他天干构成五合
# 如果合化后的五行 != 官杀原本的五行 → 官杀被合化走了 → 丢官信号
for i, g in enumerate(bazi_gans):
    ss = get_shi_shen_for_gan(g, ri_zhu)
    if ss not in ("正官", "七杀"):
        continue
    for j, other_g in enumerate(bazi_gans):
        if i == j:
            continue
        key = (g, other_g)
        if key in _WU_HE_WU_XING:
            he_wx = _WU_HE_WU_XING[key]
            guan_sha_wx = TIAN_GAN_WU_XING.get(g, "")
            if he_wx != guan_sha_wx:
                # 官杀五行被改变 → 丢官
```

## 开官库分析

### 官杀库映射（日主五行→官杀库地支→方位→颜色→生肖）

| 日主五行 | 官杀库 | 方位 | 颜色 | 生肖 |
|:--------|:------|:----|:----|:----|
| 木(甲乙) | 丑(金库) | 东北 | 白/金 | 牛 |
| 火(丙丁) | 辰(水库) | 东南 | 蓝/黑 | 龙 |
| 土(戊己) | 未(木库) | 西南 | 绿/青 | 羊 |
| 金(庚辛) | 戌(火库) | 西北 | 红/紫 | 狗 |
| 水(壬癸) | 戌(土库) | 西北 | 红/紫 | 狗 |

### 判定流程

```
官杀存在？
  ├─ ❌ 无官杀 → "开官库效果有限"
  └─ ✅ 有官杀 →
      1. 官星得令？（月令本气为官杀→天生≥40分）
      2. 天干透官杀？（显性官星）
      3. 原局有官杀库？（查 GUAN_KU_MAP + bazi_zhis）
      4. 综合结论：
         ├─ 得令或透干 + 有库 → ✅ 可开，给出方位/颜色/生肖建议
         ├─ 得令或透干 + 无库 → ⚠️ 人工布库
         └─ 未得令+不透干 → ❌ 先补能量
      5. 身强身弱区分：
         ├─ 身强 → 直接开库
         └─ 身弱 → 先补印比帮身再开库
```

## 恶神制化7级全表

| 级别 | 条件 | 代码判定 |
|:----:|:-----|:--------|
| 👑 一级·伟人格 | 杀印相生/食神制杀/杀身两停 | `is_wei` |
| 🌟 二级·上等·恶神有制 | 七杀+印或食神 + 身强/中和 | `has_sha and (has_yin or has_shi) and shen_label in ("身强","中和")` |
| 🥈 三级·中等偏上·官印相生 | 正官+印 + 身强 | `has_guan and has_yin and shen_label == "身强"` |
| 🏠 四级·中等·正官得用 | 正官 + 身强 | `has_guan and shen_label == "身强"` |
| 🏠 四级·中等·身弱得印 | 印 + 身弱 | `has_yin and shen_label == "身弱"` |
| 🥉 五级·中等偏下·身弱杀无制 | 七杀 + 身弱 + 无印 | 新增 |
| 🥉 五级·中等偏下·身弱官无制 | 正官 + 身弱 + 无印 | 新增 |
| 🪜 六级·下等 | 均不满足 | else |

## 调用链

```
comprehensive_v2.run_comprehensive_engine
    → analyze_career_advanced (career_v2.analyze_career_full)
        → _analyze_diu_guan_signal (含④方案)
        → _analyze_kai_guan_ku (新增)
        → _analyze_sheng_guan_yao_su
        → _analyze_cai_guan_lian_dong
        ...
```
