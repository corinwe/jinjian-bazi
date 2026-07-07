# 文昌检查 + 流年财富分析引擎模块（2026-07-01新增）

> 本文件记录本次会话对引擎模块的文昌和流年财富分析功能扩展，供后续维护参考。

## 一、新增引擎函数

### wealth_v2.py

**check_wen_chang(ri_zhu, zhi_list)**
- 功能：检查某八字原局是否自带文昌贵人
- 参数：ri_zhu=日干, zhi_list=[年支,月支,日支,时支]
- 返回：{has_wenchang(bool), wenchang_zhi(str), need_supplement(bool), wenchang_position(str)}

内置WEN_CHANG字典：甲巳乙午丙申丁酉戊申己酉庚亥辛子壬寅癸卯

**analyze_liunian_wealth(bazi_data, liunian_gan, liunian_zhi)**
- 功能：分析某流年对八字财富的影响
- 参数：bazi_data含{ri_zhu, shen_label, xi_yong, bazi_zhis}, liunian_gan/liunian_zhi
- 返回：{liunian, liunian_shi_shen, is_wealth_year, score_impact(-10~10), impact, advice}
- 维度：财星流年、喜用神流年、比劫流年、官杀流年、文昌流年、刑冲伏吟

### paipan.py

新增常量 `WEN_CHANG_MAP`（10天干→文昌地支映射表）
新增函数 `check_wen_chang(ri_zhu, all_zhis)` — 文昌贵人检查
新增函数 `get_full_paipan(...)` — 封装paipan() + 追加文昌输出

### 继承的文昌规则
- 口诀：甲巳乙午丙申丁酉戊申己酉庚亥辛子壬寅癸卯
- 文昌属神煞系统，与身强弱完全无关
- 原局有文昌地支 → 无需补（标注✅）
- 原局无文昌地支 → 需要补（标注⚠️需补）
- 补文昌方法见 bazi-remission-methods §19

## 二、排盘门禁 + 文昌检查

### bazi-must-run-engine.sh
新增 -w 参数：排盘输出中集成文昌检查结果

### bazi-wenchang-check.sh（新建）
用法：bash bazi-wenchang-check.sh -n姓名 -r日主 [-z四地支逗号分隔]
输出：文昌口诀、文昌地支、原局有无、位置影响力、补文昌建议方位

## 三、验证体系

### test_full_suite.py
新增 §F test_wen_chang() — 10日主文昌全覆盖验证
新增 §G test_wealth_liunian() — 流年财富分析验证

### bazi-auto-verify
新增文昌贵人验证子检查（5步流程+口诀）

## 四、✅ 已验证通过的文昌检查（家族3人）

| 人物 | 日主 | 文昌 | 原局 | 需要补？ | 方案 |
|:----|:---:|:----:|:----:|:--------:|:-----|
| 家主 | 辛金 | 子 | 无子(仅申未亥卯) | ✅ 需要补 | 正北(子方)文昌塔+鼠形饰品 |
| 主母 | 庚金 | 亥 | 无亥(仅卯未午午) | ✅ 需要补 | 西北偏北(亥方)文昌塔+猪形饰品 |
| 子源 | 丙火 | 申 | 无申(仅卯巳戌巳) | ✅ 需要补 | 西南偏西(申方)文昌塔+猴形饰品 |

## 五、⚠️ 文昌查法易错点（2026-07-01实战教训）

**致命错误案例**：家主辛金文昌被误判为亥（日支亥以为自带文昌✅）
- 正确：辛金文昌在子（口诀「辛子」）
- 庚金文昌才是亥（口诀「庚亥」）
- 家主原局地支申/未/亥/卯 — 无子 → 需要补文昌

**口诀记忆法**：甲巳乙午丙申丁酉戊申己酉庚亥辛子壬寅癸卯
**断句**：甲巳 | 乙午 | 丙申 | 丁酉 | 戊申 | 己酉 | 庚亥 | 辛子 | 壬寅 | 癸卯

**每次写文昌前必做**：
1. 背口诀确定日主的文昌地支
2. 用 shen_sha.get_wen_chang(日主) 验证
3. 检查四地支是否包含该字
4. 三者一致 → 才能写入文档
