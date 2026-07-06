# 升官模块深审发现 · 2026-07-05

## 审计对照：career_v2.py vs bazi-career-analysis skill

### ✅ 已正确实现
| 规则 | 文件·行号 | 说明 |
|:-----|:-----------|:-----|
| 正官→管理/体制内 | GUAN_SHA_CAREER字典 | 军官/法官/地方官等 |
| 七杀→军警/压力 | GUAN_SHA_CAREER字典 | 军警/运动员/法官 |
| 杀印相生伟人格 | WEI_REN_GE + _evaluate_wei_ren_ge() | 身弱用印化杀 |
| 食神制杀伟人格 | WEI_REN_GE + _evaluate_wei_ren_ge() | 身强以智谋制伏 |
| 官星合化5组 | GUAN_HE_HUA + _analyze_guan_he_hua() | 丁壬合/丙辛合/戊癸合/甲己合/乙庚合 |
| 伤官三格 | SHANG_GUAN_SAN_GE + _evaluate_shang_guan_ge() | 伤官伤尽/配印/生财/见官 |
| 财官联动 | _analyze_cai_guan_lian_dong() | 身强+财旺+官杀旺 |
| 官杀混杂 | _analyze_guan_sha() | 身弱/身强两种判定 |
| 丢官信号(部分) | _analyze_diu_guan_signal() | 伤官见官→丢官/etc |

### ❌ 缺失规则
| 规则 | 影响 | 建议加到 |
|:-----|:-----|:---------|
| **财星破印→丢官** | skill明确规则：伤官配印最怕见财星 | _analyze_diu_guan_signal() |
| **官星受冲→丢官** | docstring明文标了但未实现 | _analyze_diu_guan_signal() |
| **官星被合化负面** | 只作为正面信号实现，缺合化出忌凶判断 | _analyze_diu_guan_signal() |
| **比劫夺官** | 比劫克财→财不生官链条未实现 | _analyze_diu_guan_signal() |
| **将星→领导才能** | step1_basic.py有计算但career_v2不接收神煞 | analyze_career()加神煞参数 |

### ⚠️ 部分实现
| 规则 | 现状 |
|:-----|:------|
| 比劫帮身→身强能担官 | 间接通过身强弱实现，无显式规则 |
| 印星护身→升官基础 | 隐式存在于职业级别判定，无独立规则名 |
| 伤官伤尽忌见正官 | 缺"有七杀没问题"的判断分支 |

### 将星速查表（用于补充career_v2）
```
年支查将星：
  寅午戌 → 午
  申子辰 → 子
  巳酉丑 → 酉
  亥卯未 → 卯
```
