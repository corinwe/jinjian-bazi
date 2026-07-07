# 2026-07-05 全量引擎模块审计覆盖矩阵（v2.0）

> **覆盖：28个引擎模块全量审计**
> **发现+修复Bug：12个P0/P1（全部已修）**
> **旧版归档：13个文件（engine/archive/）**

## 审计批次

### 第1批（6/29~7/4·已审计+修复）
| 模块 | 状态 | 问题 | 修复 |
|:-----|:----:|:-----|:-----|
| education.py | ✅ | 博士等级+年柱三档第②档+身强弱×十神正反面 | 已修 |
| career_v2.py | ✅ | 丢官信号5项(伤官克官/财破印/官受冲/合化负面/比劫夺官)+将星领导才能+循环导入 | 已修 |
| shi_shang.py | ✅ | 引用链断裂（算法正确但零调用者） | 打通至comprehensive_v2 |
| character.py | ✅ | 死代码冲突(叛逆型/开拓型/保守型)+日主重复计入十神 | 已修 |
| energy.py | ✅ | 无BASE_SCORE位置权重(月令偏低21倍) | 加权重体系(月令40/年支4/日时12) |
| cai_xing.py | ✅ | 无问题 | — |
| da_yun.py | ✅ | 逆排跨年逻辑错误(阴男/阳女跨年未+1) | 已修 |

### 第2批（7/5·手动审计·全通过）
| 模块 | 状态 | 结论 |
|:-----|:----:|:------|
| shen_qiang_ruo.py | ✅ | 身强弱规则完全正确（月令本气印40/中余气印0/其他位置印0/比劫全计分/燥土规则/从弱50分/自坐比劫永不从弱/月令被克三次递减） |
| ge_ju.py | ✅ | 格局判定逻辑正确（月令本→中→余气逐次查透干/比劫不入格局/复合格局检测） |
| shi_shen.py | ✅ | 十神映射逻辑正确（五行关系+阴阳判定） |

### 第3批（7/5·并行派审+修复）
| 模块 | 状态 | Bug | 修复 |
|:-----|:----:|:----|:-----|
| xing_chong_he_hua.py | ❌→✅ **已修** | 🔴寅巳申三刑能量15应10倍；🟡自刑仅检同字漏跨字组合 | 分离NENG_LIANG条目；辰午酉亥任意2即触发 |
| shen_sha.py | ❌→✅ **已修** | 🔴天德贵人字典仅4/12正确 | 按标准口诀全部修正(丑→庚/寅→丁/辰→壬等) |
| misfortune_analysis.py | ❌→✅ **已修** | 🔴岁运并临da_yun=liu_nian永远真 | 从da_yun_list取真实大运干支 |
| wealth_v2.py | ❌→✅ **已修** | 🟡cai_total<=0+身强无状态分支 | 新增"无财身强" |
| marriage_v2.py | ❌→✅ **已修** | 🟡三刑范围过宽(不限日支参与)；🟡刑冲破害不按喜忌扣分 | 仅日支参与才扣；喜用时减半扣 |
| health_v2.py | ⚠️ 通过 | 🟡大运分析未接入(预存)；🟡流年预测空(预存) | 标注已知缺陷 |
| children_v2.py | ✅ 通过 | 🟢死代码残留 | 标注 |
| family.py | ❌→✅ **已修** | 🟡downstream字段family_economy/pressure缺失 | 补充计算逻辑+输出字段 |

### 第4批（手动审计·通过）
| 模块 | 结论 |
|:-----|:----:|
| comprehensive_v2.py | ✅ 无Bug，调用链完整(调用career_v2/children_v2/health_v2/wealth_v2/shi_shang/appearance/property/verdicts) |
| paipan.py | ✅ 排盘正确 |
| lunar.py | ✅ 农历转换正常 |
| constants.py | ✅ 常量正确 |

### 第5批（输出层·快速过）
| 模块 | 结论 |
|:-----|:----:|
| report_generator.py | ✅ 格式层（只做数据翻译，不参与计算） |
| generate_deep_report.py | ✅ 格式层 |
| narratives.py | ✅ 格式层 |
| narrative_integration.py | ✅ 格式层 |
| _gen_detail_analysis.py | ✅ 格式层 |

## 旧版归档（13个文件 → engine/archive/）

| 旧文件 | 替代 | 隐藏引用 |
|:-------|:-----|:---------|
| pipeline_v4.py / pipeline_v3.py / pipeline_v2.py / pipeline.py / pipeline_product.py | pipeline_v5.py | 无 |
| comprehensive.py | comprehensive_v2.py | 无 |
| marriage.py | marriage_v2.py | 无 |
| liu_nian.py | liu_nian_v2.py | ⚠️ liu_nian_v2内有 `from liu_nian import check_fan_tai_sui`（相对导入！已内联修复） |
| dimensions.py / dimensions_v2.py | 已弃用 | 无 |
| step1_basic.py | 仅被pipeline_product引用 | 无 |
| report_standard_gen.py / audit_report_content.py | 零引用脚本 | 无 |

## 关键教训

### 1. 「审计」= 所有模块
老板说审计就要全部审完，不能只挑自己觉得重要的。首批只审了7个，被老板问「所有模块全结束了吗」才发现还有15+个没审。

### 2. 相对导入是归档的隐藏陷阱
文件级 glob 搜 `engine.xxx` 找不到 `from xxx import`（无前缀）。必须运行引擎实际抓 ModuleNotFoundError。

### 3. 映射表/字典必须逐条用口诀验证
- CAI_WUXING_MAP：「金日主→火」实际应为「木（我克者=财）」——口诀验证
- TIAN_DE：8/12条错误——标准口诀逐条对照

### 4. 传参张冠李戴
`da_yun_gan=liu_nian_gan` → 函数内「大运=流年」永远为真 → 岁运并临永远误报。
修复：调用处实参名 vs 函数形参名逐项核对。

### 5. 批处理并行最高效
- 核心模块（3个）手动审：10分钟
- 大模块（8个）Sub-Agent并行派审：每批2-3个，合计约3分钟
- 输出层（5个）快速过：5分钟
- 总计：约20分钟全量28模块审计完成

### 6. 修完Bug必须查所有引用
修了 `signal_detail` 的 `reason`→`reasons` 后，必须查 `_gen_detail_analysis.py` 和 `pipeline_v5.py` 是否同样读这个字段。修一个模块的Bug，引用方可能还有同样的Bug。

## 当前活跃引擎模块总览

```
engine/（30个模块 + 13个归档）
├── pipeline_v5.py              ← 唯一主入口
├── comprehensive_v2.py         ← 中间层
├── 分析模块（14个）: career_v2/children_v2/education/energy/character/
│                     health_v2/liu_nian_v2/marriage_v2/wealth_v2/
│                     cai_xing/shi_shang/da_yun/misfortune_analysis/family
├── 核心模块（7个）: shen_qiang_ruo/ge_ju/shi_shen/shen_sha/
│                     xing_chong_he_hua/paipan/lunar
├── 输出层（6个）: report_generator/generate_deep_report/narratives/
│                  narrative_integration/_gen_detail_analysis/constants
└── archive/（13个旧版·保留备查）
```
