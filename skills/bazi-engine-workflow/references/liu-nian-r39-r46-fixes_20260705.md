# 🚨 流年 v2.1 · R39-R46 修复记录（2026-07-05）

## 背景
对 `liu_nian_v2.py` 和 `xing_chong_he_hua.py` 的多项规则修复。期间遇到 sibling subagent 覆写问题。

---

## Fix 1：R39 — 恶神×能量级别对应表

### 位置
`/root/bazi-platform/engine/liu_nian_v2.py` → `E_SHEN_LEVEL` 常量 + 灾祸事件检测

### 变更
新增 `E_SHEN_LEVEL` 字典，七杀/伤官各能量级对应具体灾祸描述：
```python
E_SHEN_LEVEL = {
    "七杀": {
        1: "压力/罚单/小人口舌",
        3: "纠纷/病痛/破财",
        10: "官非/重伤/大破财",
        15: "横死/猝死/重大灾祸",
    },
    "伤官": {
        1: "口舌/误解",
        3: "官非/失业",
        10: "官司/名声扫地",
    },
}
```

在灾祸检测中，统计原局七杀/伤官数量，匹配对应的能量级别描述，同步计算 `mis_energy` 系数。

### 排查信号
灾祸描述太笼统（只有"七杀攻身"没有具体程度）→ 检查 `E_SHEN_LEVEL` 是否被加载

---

## Fix 2：R40 — 神煞 vs 十神 系统界限

### 位置
`liu_nian_v2.py` → `SHEN_SHA_BOUNDARY_NOTE` 常量 + 灾祸检测中的标注

### 变更
**核心规则：天乙/天德贵人只能化解神煞类灾祸（灾煞/血刃/劫煞），不能化解十神系统灾祸（七杀/枭神夺食/伤官见官）。**

代码中：当带天乙/天德 + 七杀能量≥3时，追加界限标注到描述中，不因神煞而减免灾祸分数。

### 排查信号
用户问"我有天乙贵人为什么还是七杀年倒霉？" → 检查 `SHEN_SHA_BOUNDARY_NOTE` 是否被正确引用，神煞救不了十神

---

## Fix 3：R41 — 大运空亡检测

### 位置
`xing_chong_he_hua.py` → 新增 `_get_kong_wang()` 函数
`liu_nian_v2.py` → 新增 `_check_da_yun_kong_wang()` 函数 + `da_yun_energy_factor`

### 变更
1. `_get_kong_wang(day_gan, day_zhi)` 从 `children_v2.py` 提取到 `xing_chong_he_hua.py` 作通用函数
2. `_check_da_yun_kong_wang(da_yun_zhi, day_gan, day_zhi)` 检查大运地支是否在日柱空亡中
3. 在 `analyze_liu_nian_v2` 中早计算 `da_yun_energy_factor`（空亡=0.5，否则=1.0）
4. 所有事件的 `energy` 字段乘以 `da_yun_energy_factor`

### 旬空规则
甲子旬→戌亥空, 甲戌旬→申酉空, 甲申旬→午未空,
甲午旬→辰巳空, 甲辰旬→寅卯空, 甲寅旬→子丑空

### 排查信号
流年事件强度与预期不符 → 检查大运是否逢空亡

---

## Fix 4：R42 — 三合局完整度检查

### 位置
`xing_chong_he_hua.py` → `check_san_he()` 函数签名升级

### 变更
`check_san_he` 新增可选参数 `kong_wang_zhis`。返回的完整度等级：
| 等级 | 条件 | energy |
|------|------|--------|
| 完整三合 | 三字齐全 + 中神无破 | 15.0 |
| 虚邀三合 | 三字齐全 + 中神空亡 | 7.0 |

中神映射：申子辰→子, 亥卯未→卯, 寅午戌→午, 巳酉丑→酉

### 调用链
`check_san_he(zhi_list, kong_wang_zhis)` ← `check_all_relations(zhi_list, kong_wang_zhis)` ← `check_all_relations_v2(zhi_list, gan_list, kong_wang_zhis)`

### 排查信号
三合局能量始终是15从不变 → 检查 `kong_wang_zhis` 是否被传递到 `check_san_he`

---

## Fix 5：R46 — 身过强>60分破财

### 位置
`liu_nian_v2.py` → `analyze_liu_nian_v2()` 评分段

### 变更
在综合评分中新增：如果 `shen_score > 60`，比劫年为忌神→破财扣分：
```python
if shen_score > 60 and liu_nian_shi_shen in ["比肩", "劫财"]:
    bijie_wx = TIAN_GAN_WU_XING[liu_nian_gan]
    if bijie_wx in ji_shen or bijie_wx not in xi_yong:
        score -= 1.0  # 比劫为忌→破财
```

**原理**：身过强时，比劫不再扶身，反而争财 → 为忌神

### 排查信号
身强>60的人遇到比劫年反而说"好" → 检查是否是身过强（shen_score > 60）

---

## ⚠️ 踩坑记录：Sibling Subagent 覆写问题

### 场景
当两个 Hermes agent（或 sibling subagents）同时/先后修改同一文件时，后一个 agent 的写入可能**覆盖**前一个 agent 的所有变更。

### 本次教训
`liu_nian_v2.py` 在会话中被 sibling subagent 升级为 v2.1（新增 R25/R30/R31/R35/R36），同时我的 R39/R40/R41/R46 变更也被该 subagent 写入同一文件。从该 agent 角度，我的修改被视为"旧的"版本被整体替换。

### 应对策略
1. **每次 `patch` 后立即验证**：使用 `read_file` 确认修改生效
2. **发现被覆写后不要慌张**：读取完整文件的新状态，重新执行缺失的 `patch`
3. **考虑锁定**：对将被批量修改的关键文件，考虑临时隔离或先完成全部修改后再让其他 agent 处理

---

## 测试验证

```
总用例: 361 | PASS: 347 | FAIL: 14 | 通过率: 96.1%
```

14项失败的均为既有问题（大运步数不匹配、原局地支检测、summary格式），与本批次修复无关。
