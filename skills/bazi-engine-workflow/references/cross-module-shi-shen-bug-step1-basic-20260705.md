# step1_basic.py 十神判定Bug + 跨模块一致性教训 (2026-07-05)

## 错误现象

`projects/bazi-platform/engine/step1_basic.py` 的 `_get_shi_shen()` 和 `_get_cang_gan_shi_shen()` 函数中，
十神判定逻辑有 **3处反了**，与正确的 `shi_shen.py` 和 `constants.py` 不一致：

### Bug 1: 我生→食伤 天干版 (L177)
```python
# ❌ 修复前:
return "伤官" if same_yy else "食神"
# ✅ 修复后:
return "食神" if same_yy else "伤官"
```

### Bug 2: 我生→食伤 藏干版 (L203)
```python
# ❌ 同上错误
return "伤官" if same_yy else "食神"
# ✅ 修复后:
return "食神" if same_yy else "伤官"
```

### Bug 3: 同我→比劫 藏干版 (L209)
```python
# ❌ 修复前:
return "劫财" if same_yy else "比肩"
# ✅ 修复后:
return "比肩" if same_yy else "劫财"
```

## 根因

这是 **2026-07-04 constants.py SHI_SHEN_MAP 食神/伤官反转Bug 的同类错误**，但出现在不同模块：
- constants.py 的 SHI_SHEN_MAP 字典映射反了 → 2026-07-04 已修复
- step1_basic.py 的条件判断反了 → 2026-07-05 本会话修复
- shi_shen.py 在2026-07-04已经过修复且正确 ✅

**模式总结**：十神判定逻辑被**独立实现了至少3次**（constants.py 的 SHI_SHEN_MAP、shi_shen.py 的 get_shi_shen_for_gan、step1_basic.py 的 _get_shi_shen），但只修复了前两个。

## 天干四冲Bug (L414-421)

step1_basic.py 的 `TIAN_GAN_CHONG` 表包含了**8个非标准的天干冲组合**：

```python
# ❌ 非标准（已删除）：
("戊", "甲"): "戊甲冲",
("己", "乙"): "己乙冲",
("丙", "庚"): "丙庚冲",
("丁", "辛"): "丁辛冲",
# 以及它们的反向
```

标准天干四冲 **仅4组**：甲庚冲、乙辛冲、丙壬冲、丁癸冲。戊己土居中，不参与相冲。

## 影响范围

step1_basic.py 仅被 `pipeline_product.py` 使用，用于生成**排盘显示表（11行×4列）**。
实际分析模块（ge_ju.py、cai_xing.py 等）使用 `shi_shen.py`，不受影响。
**影响仅限于前端排盘表的十神/天干冲显示错误，不改变分析结果。**

## 🚨 跨模块一致性铁律

当修复一个**规则类Bug**（如十神判定规则）时，必须检查**所有实现了同样规则的模块**：

```yaml
检查清单：
  □ constants.py — SHI_SHEN_MAP 字典
  □ shi_shen.py — get_shi_shen_for_gan / get_shi_shen_for_cang_gan
  □ step1_basic.py — _get_shi_shen / _get_cang_gan_shi_shen
  □ 其他任何实现了十神判定的模块
  □ 前端/API层是否有独立的十神判定逻辑

验证方法：
  for 日主 in 十天干:
    for 其他干 in 十天干:
      手动计算十神 → 与每个模块的输出对照
      不一致 = Bug

口诀：
  十神规则三处写，一处修了另两处查
  五行生克需一致，阴阳关系不能反
  食伤最容易搞混，同阳同阴是食神
```

## 修复

commit `04e3212` in jinjian-bazi repo (2026-07-05)
变更文件：`projects/bazi-platform/engine/step1_basic.py`
