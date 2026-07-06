# 2026-07-05 marriage_v2 + children_v2 审计实战记录

## 审计清单

| 模块 | 审计结果 | 修复项 |
|:-----|:---------|:-------|
| marriage_v2.py (518行) | ✅ 95%对齐，无严重bug | 无（通过） |
| children_v2.py (v2.0 vs skill v3.0) | ⚠️ 10项✅ + 5项⚠️ + 7项❌ | 见下方 |

## children_v2.py 修复清单

### 已实现的 (10项)
1. 子女星定位（流派A+流派B）✅
2. 十二长生基数法 ✅
3. 时支生育力排名 ✅
4. 子女缘分三层合参法 ✅
5. 子女出生年份推理 ✅
6. 缘薄因素排查 ✅
7. 生育窗口排查 ✅
8. 子女成就判断 ✅
9. 时柱七杀有制生子规则 ✅
10. 双胞胎特征 ✅

### 已修复的 (5项引擎层修正)
1. **养中留一** — `SHI_ER_CHANG_SHENG_BASE["养"]`: 3→1
2. **第3层用真喜用神** — `calc_three_layer_fate` 参数从 `ri_zhu_wx_xi_ji` 改为 `xi_yong: list[str] | None`，通传至 `analyze_children_full` 再到 `comprehensive_v2`
3. **空亡减半** — 在 `analyze_children_full` 中fertility计算后加空亡检测
4. **子女星空亡/被冲刑** — 替换 `check_thin_fate_factors` 中简化检测为精确旬空+六冲+三刑检查
5. **子女星被解合的生育窗口** — `check_fertility_windows` 中加原局子女星被合化→流年冲开解合检测

### 新增的 (2个功能块)
6. **不好生孩子11条特征** — `check_hard_to_conceive()` 新函数，覆盖skill §第九步全部11条
7. **容易生孩子6条特征** — `check_easy_to_conceive()` 新函数，覆盖skill §第十步全部6条

### 较小的修正 (3项)
8. **子女宫映射** — 报告dict中 `基础信息` 加 `子女宫: {时干→长子/长女, 时支→次子及后续}`
9. **逻辑一致性称谓检查** — `consistency_check` 中 `pass` 占位替换为实际警告逻辑
10. **命局无子女星检查** — `check_thin_fate_factors` 中加回被遗漏的「命局无子女星」因素

### 跳过report层实现的风水/玄学类 (在report层而非engine层实现)
- 催子八卦阵布置法
- 补充子女星能量8法
- 功德求子法
- 私生子信息（日支时支合）
- 石榴树禁忌

## 核心教训总结

1. **education被算了两次** — pipeline_v5外层调 + comprehensive_v2内部调 → 去重
2. **版本差 = 缺失根因** — children_v2 v2.0 vs skill v3.0 → 差了12天+1个大版本 → 按skill §顺序批量补
3. **引擎修完后必须检查caller + 返回值消费** — 参数传进来了不等于被使用
4. **占位符代码容易被忽视** — `# ...简化` / `pass` → grep 全项目扫描
