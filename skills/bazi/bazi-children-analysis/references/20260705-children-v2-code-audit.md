# 2026-07-05 children_v2.py 代码审计发现

> **前置上下文：** `bazi-platform-harness/references/20260705-children-marriage-audit-case-study.md` 已覆盖 skill § vs 代码 § 的**功能缺失**检查。
> 本文档覆盖的是上一层审计没发现的**代码实现Bug**——skill有的功能代码也实现了，但实现不完整或有Bug的项。

---

## 🟠 中等问题

### ① 评分函数缺失两项（`calc_children_star_score`）

`CHILDREN_STAR_SCORE_MAP`(L152-160) 定义了 7 项评分，但 `calc_children_star_score()`(L504-566) 只实现了 5 项：

| 评分项 | 常量定义 | 代码实现 | 状态 |
|:-------|:--------:|:--------:|:----:|
| tou_gan(天干透出) | +15 | L515-519 | ✅ |
| zhen_gen(地支真根) | +20 | L522-527 | ✅ |
| san_he_enhance(三合三会加强) | +20 | L530-538 | ✅ |
| **da_yun_trigger(大运流年引动)** | **+10** | **从未实现** | ❌ |
| **kong_wang(空亡)** | **-25** | **从未实现** | ❌ |
| be_he_off(被合化走) | -30 | L541-544 (用了-15) | ⚠️ 值不对 |
| chong_xing(被冲/刑) | -15 | L547-556 | ✅ |

**为什么没发现之前：** 之前的审计是对比 skill § 与代码 § 的"功能是否存在"（feature level），没有逐项核对评分常量表是否全量实现（value level）。

**影响：** 子女星评分不会超过 35 分（因为只剩 35 分满分），永远达不到"子女缘分深(≥40分)"的阈值。

**修复方案：**
```python
# 在 calc_children_star_score 中增加：
# 1. 大运流年引动 +10（需判断大运或当前流年是否透出子女星）
# 2. 空亡 -25（检查子女星所在地支是否逢空亡）
```

### ② 父母合参调用不完整（`analyze_children_full` L1953-1961）

```python
parent_joint = check_parent_joint_rules(
    father_ri_zhu=father_ri_zhu,
    mother_ri_zhu=mother_ri_zhu,
    father_bazi_gans=bazi_gans,      # ✅ 父数据正确传入
    father_bazi_zhis=bazi_zhis,       # ✅
    mother_bazi_gans=None,            # ❌ 硬编码None
    mother_bazi_zhis=None,            # ❌ 硬编码None
)
```

函数 `check_parent_joint_rules()` 接收完整参数（L1206-1262），但主函数调用方只传了父亲的数据。合参变成了"单参"。

**根因：** `analyze_children_full()` 的参数列表没有定义 `mother_bazi_gans/mother_bazi_zhis`，所以调用时只能传 None。

**修复方案：** 在 `analyze_children_full()` 增加可选参数 `mother_bazi_gans` 和 `mother_bazi_zhis`，通传下去。

### ③ 自刑检测逻辑不严谨（`check_twin_conditions` L1018）

```python
zi_xing_count = sum(1 for z in bazi_zhis 
    if z in ("辰","午","酉","亥") and bazi_zhis.count(z) >= 2)
```

**问题：** 只检查同一个地支出现≥2次（伏吟式自刑），不检查多个不同自刑地支同时出现的情况。

SKILL.md 原文「辰午酉亥自刑（至少两个自刑出现）」可能指 4 个自刑地支中**任选 2 个**出现，不限定同一地支重复。

**例：** 八字 `[辰, 酉, 亥, ...]` — 辰、酉、亥各出现一次，自刑条件已满足，但当前代码判为 False。

**修复：**
```python
# 正确逻辑：至少2个不同的自刑地支出现
zi_xing_branches = [z for z in bazi_zhis if z in ("辰","午","酉","亥")]
if len(set(zi_xing_branches)) >= 2:
    # 自刑条件满足
```

---

## 🟡 代码质量问题

### ④ 废弃注释代码（L96-98）

```python
WU_XING_CHANG_SHENG_START = {
    "木": 2,  # 寅(地支index 2)
    "火": 3,  # 卯 → 不对，火长生在寅，index=2... 等等
}
```

含错误（火长生写为卯）和草稿笔记。实际用 `YANG_GAN_CHANG_SHENG_START` / `YIN_GAN_CHANG_SHENG_START` 替代，此变量从未使用。直接删除。

### ⑤ 死代码函数（L237-243）

```python
def _get_shi_shen_wu_xing(shi_shen: str) -> str | None:
    """根据十神名称返回其五行..."""
    return None  # 始终返回None
```

未完成的辅助函数。删除或补全。

### ⑥ `check_easy_to_conceive` 规则③-⑥逻辑重复（L1799-1836）

规则②（`hour_zhi in 子午卯酉`）已覆盖规则③-⑥（分别检查卯/酉/子/午）。③-⑥只提供更细化的描述消息。可简化为遍历 `[("卯","生育力最强"), ("酉","强"), ...]` 生成。

### ⑦ 长篇叙事性注释（L99-109）

```python
# 实际上，标准做法：
# 对于男命：子女星=正官/七杀，其五行属性是确定的
# 比如甲日主男命，正官=辛(金)，看辛金在时支的长生位
# 需要建立: 天干在十二地支的长生位表
...
```

属于设计思路记录，放在文档而非代码中。建议移至模块 docstring 或删减至必要提示。

---

## 🟢 边缘问题

### ⑧ `死=0` 与 `墓=-1` 语义

| 长生位 | 代码值 | SKILL.md原文 | 
|:------:|:------:|:-------------|
| 死 | 0 | 死中晚景少儿郎（**极少**） |
| 墓 | -1 | 入墓之时多不良（**不良/抱养**） |

- `极少≠0`（极少意味着极小概率但不是零）
- `不良/抱养`不能用负数表示——基数乘法中负基数有意义（减少总分），但-1意味着"倒扣"，语义上不如用 0.5 或 1（乘法系数）

### ⑨ `infer_child_birth_years` 每大运限15年

```python
for year in range(start_year, min(end_year + 1, start_year + 15)):
```
大运本身10年，`start_year+15` 通常 > `end_year+1`，所以限制不会触发。逻辑没错，但`15`是硬编码魔数，应改为常量 `MAX_YEARS_PER_DAYUN`。

### ⑩ `validate_all.py` 无 children 测试

`grep children tests/validate_all.py` 返回空。`calc_children_star_score` 和 `check_hard_to_conceive` 等复杂函数无任何自动化回归测试。

---

## 根因分析

| 根因 | 举例 |
|:-----|:------|
| **评分常量定义与实现不同步** | CHILDREN_STAR_SCORE_MAP 定义 7 项，函数实现 5 项——"定义脱节" |
| **函数签名扩展但调用方不跟进** | check_parent_joint_rules 有 mother 参数但不传——"参数传递断层" |
| **边界逻辑只写了一种情况** | 自刑只检查重复不检查多自刑同时出现——"单路径思维" |
| **旧代码未清理** | WU_XING_CHANG_SHENG_START / _get_shi_shen_wu_xing — "代码保洁缺失" |

---

## 口诀

```
评分函数查常量，定义实现要一致
函数参数通调用，不要硬编None值
自刑检查双路径，伏吟多刑都要看
旧代码要常清理，死函数删不留坑
validate_all加测试，回归验证不靠猜
```
