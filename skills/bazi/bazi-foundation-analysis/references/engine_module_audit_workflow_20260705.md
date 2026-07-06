# 引擎模块审计工作流（2026-07-05全量版·28模块覆盖）

> 来源：2026-07-05 全链路深度审计（28个模块全量覆盖，P0/P1 Bug全部修复）

## 核心原则

1. **「审计」= 所有模块，不止你想到的那几个** — 老板说审计就要全部审完，不能只挑自己觉得重要的
2. **发现的问题全部修完再继续一步** — 修一个推一个，不积压
3. **批处理 + 并行** — 核心模块手动审，大模块派 Sub-Agent 并行，输出层快速过
4. **先审核心再审外围** — shen_qiang_ruo/ge_ju/shi_shen → v2分析模块 → 中间层 → 输出层 → 基础模块

## 三步审计法

### Step 1 — 加载skill对照原始理论
```python
skill_view('bazi-xxx-analysis')  # 加载对应的理论skill
```
逐条对比代码逻辑 vs 原始理论。检查：
- ✅ 已正确实现
- ❌ 未实现（在skill中有但代码无）
- ⚠️ 部分实现/有Bug
- 🚨 **特别注意**：判断逻辑本身是否与九龙道长一致，不只是功能对齐

### Step 1.5 — 数据契约验证（输出dict字段校验）
**代码正确但下游看不到 = 等于没做。** 审计输出dict的字段是否与所有下游消费者期望的保持一致。

强制流程：
```python
# 1. 收集所有下游消费者期望的字段
#    模块的 return { ... } 列出所有key
#    grep 搜索 .get("sec_xx_xxx", {}).get("field") 找出所有期望字段

# 2. 对比 — 期望字段 vs 实际输出字段

# 3. 标记不匹配
#    ✅ 期望字段在输出dict中 → 通过
#    ❌ 不在输出dict中 → 下游永远读不到 → P0 Bug
#    ❌ 字段名不一致 → P0 Bug
```

**致命教训**：family.py 缺 family_economy/family_pressure/wu_xing_analysis → 下游 report_generator.py 永远读到空。

### Step 2 — 引用链验证
```python
# 1. comprehensive_v2.py 调用了该模块？
# 2. pipeline_v5.py 调用了该模块？
# 3. 传入参数完整？（特别是 shen_label/xi_yong/da_yun_list）
# 4. 返回结果被正确使用？（数据契约验证）
```

### Step 3 — 测试验证
```bash
cd /root/bazi-platform/engine && python3 -m pytest tests/ -v --tb=short
# 必须 9/9 全部通过

python3 pipeline_v5.py --name 测试 --gender 男 --year 1990 --month 5 --day 15 --hour 10 --json
# 引擎完整运行正常
```

## Sub-Agent 并行审计模式

### 分批策略
```
第1批（核心三件套·手动审）: shen_qiang_ruo / ge_ju / shi_shen
第2批（并行派审）: xing_chong_he_hua + shen_sha + misfortune_analysis
第3批（并行派审）: liu_nian_v2 + marriage_v2 + wealth_v2
第4批（并行派审）: health_v2 + children_v2 + family
第5批（手动快速审）: comprehensive_v2 / paipan / lunar / constants
第6批（手动快速审）: report_generator / generate_deep_report / narratives
```

### Sub-Agent Context 四要素
1. **文件路径** — 要审计的模块路径
2. **Skill规则** — 需要对照的技能规则
3. **引用链** — 该模块被哪些文件调用
4. **验证命令** — 修改后如何验证

### 注意：delegation并发限制
当 `delegation.max_concurrent_children` 达到容量时，后续 delegation 会同步执行而非后台。需要确认容量配置足够支撑预期并行数。

## 审计优先级体系

| 级别 | 说明 | 处理方式 |
|:----:|:-----|:---------|
| **P0** | 致命Bug/计算结果错误 | 立即修，阻塞推库 |
| **P1** | 重要缺失/逻辑缺陷 | 本批次必修 |
| **P2** | 次要缺失/增强 | 有余力则修 |
| **P3** | 风格/文档/死代码 | 标注即可 |

## 常见 Bug 模式（28模块审计沉淀）

| 模式 | 检测方法 | 典型案例 | 修复 |
|:-----|:---------|:---------|:-----|
| **映射表口诀验证缺失** | grep "映射表\|MAP =\{" 并逐条用口诀验证 | liu_nian_v2 CAI_WUXING_MAP：「金日主→火」应为→木「我克者=财」 | 口诀验证 |
| **能量系数混淆** | grep "NENG_LIANG" 检查是否区分类型 | xing_chong_he_hua 丑未戌15/寅巳申10共用 | 分离为独立条目 |
| **自刑规则不完整** | check_xing 只检查相同字成对 | 辰午酉亥跨字组合不触发 | 任意2个即触发 |
| **字典条目错误** | 逐条对照标准口诀 | shen_sha TIAN_DE 仅4/12正确 | 按口诀重写 |
| **传参张冠李戴** | 检查调用处实参名 vs 函数形参名 | misfortune da_yun_gan=liu_nian_gan 永远误报 | 从 da_yun_list 取真实大运 |
| **分支覆盖缺失** | if-elif 是否覆盖所有排列组合 | wealth_v2 cai_total<=0+身强无分支 | 加 else |
| **刑冲范围过宽** | 是否限制仅日支参与 | marriage_v2 全局三刑扣100 | 仅日支参与才扣 |
| **喜忌不区分** | 扣分逻辑是否检查喜用神 | marriage_v2 刑冲破害一律扣 | 喜用时减半扣 |
| **下游字段缺失** | grep 期望字段 vs 输出dict | family 缺 family_economy | 在 family.py 补充 |

## 28模块全量审计覆盖

### 第1批（已审计+修复·本次会话前）
| 模块 | 状态 | 修复项 |
|:-----|:----:|:-------|
| education.py | ✅ 修完 | 博士等级+年柱三档 |
| career_v2.py | ✅ 修完 | 丢官信号+将星 |
| shi_shang.py | ✅ 引用链通 | 算法正确，comprehensive_v2已调用 |
| character.py | ✅ 修完 | 死代码冲突+日主重复 |
| energy.py | ✅ 修完 | BASE_SCORE位置权重 |
| cai_xing.py | ✅ 通过 | 无需修 |
| da_yun.py | ✅ 修完 | 逆排跨年Bug |

### 第2批（手动审计·本次会话）
| 模块 | 状态 | 结论 |
|:-----|:----:|:-----|
| shen_qiang_ruo.py | ✅ 通过 | 逻辑正确（月令印40/比劫全计分/燥土/被克递减） |
| ge_ju.py | ✅ 通过 | 逻辑正确（1行死代码） |
| shi_shen.py | ✅ 通过 | 十神映射逻辑正确 |

### 第3批（并行派审·本次会话）
| 模块 | 状态 | 发现 |
|:-----|:----:|:-----|
| **xing_chong_he_hua.py** | ❌→✅ **已修** | 🔴三刑能量系数混淆 🟡自刑跨字漏报 |
| **shen_sha.py** | ❌→✅ **已修** | 🔴天德贵人字典8/12错误 |
| **misfortune_analysis.py** | ❌→✅ **已修** | 🔴岁运并临永远误报(da_yun=liu_nian传参) |
| **wealth_v2.py** | ❌→✅ **已修** | 🟡缺少无财身强状态 |
| **marriage_v2.py** | ❌→✅ **已修** | 🟡三刑范围过宽 🟡刑冲破害不按喜忌 |
| **health_v2.py** | ⚠️ 通过 | 🟡大运分析未接入（预存） 🟡流年预测空（预存） |
| **children_v2.py** | ✅ 通过 | 轻微代码残留 |
| **family.py** | ❌→✅ **已修** | 🟡下游字段family_economy/pressure缺失 |

### 第4批（手动审计·通过）
| 模块 | 结论 |
|:-----|:----:|
| comprehensive_v2.py | ✅ 无Bug |
| paipan.py | ✅ 排盘正常 |
| lunar.py | ✅ 农历转换正常 |
| constants.py | ✅ 常量正确 |

### 第5批（输出层·快速过）
| 模块 | 结论 |
|:-----|:----:|
| report_generator.py | ✅ 格式层（只做数据翻译） |
| generate_deep_report.py | ✅ 格式层（只做数据翻译） |
| narratives.py | ✅ 格式层（只做数据翻译） |
| narrative_integration.py | ✅ 格式层（只做数据翻译） |
| _gen_detail_analysis.py | ✅ 格式层（只做数据翻译） |

## 2026-07-05 新增Bug修复清单

| Bug | 模块 | 修复 |
|:----|:-----|:-----|
| CAI_WUXING_MAP金日主财星→火应为木 | liu_nian_v2.py | 改为木 |
| 寅巳申三刑能量15应10倍 | xing_chong_he_hua.py | 分离NENG_LIANG条目 |
| 自刑仅检测同字成对（漏跨字组合） | xing_chong_he_hua.py | 任意2个辰午酉亥即触发 |
| 天德贵人8/12错误 | shen_sha.py | 按口诀全部修正 |
| 岁运并临da_yun=liu_nian永远真 | misfortune_analysis.py | 从da_yun_list取真实大运 |
| cai_total<=0+身强无状态分支 | wealth_v2.py | 新增"无财身强" |
| 全局三刑扣分（未限日支参与） | marriage_v2.py | 仅日支参与才扣 |
| 刑冲破害不按喜忌一律扣分 | marriage_v2.py | 喜用减半扣 |
| family_economy/pressure字段缺失 | family.py | 在family.py补充 |

## 审计完成标准

- [ ] 全部模块代码审完（以 pipeline_v5.py imports 为准，跟踪到 every 叶子模块）
- [ ] 每个模块的引用链验证（谁调用它、传什么参数、结果怎么用）
- [ ] 每个模块的数据契约验证（输出dict字段 vs 下游期望字段）
- [ ] 所有 P0/P1 Bug 修复完成
- [ ] pytest 9/9 通过
- [ ] 引擎 pipeline_v5 完整运行正常
- [ ] 推库
