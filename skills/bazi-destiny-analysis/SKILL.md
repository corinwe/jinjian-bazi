---
name: bazi-destiny-analysis
description: >
  八字命理深度分析 Skill。基于《渊海子平》《三命通会》《滴天髓》《子平真诠》四书经典，
  提供四柱八字排盘、五行十神分析、大运流年推演、事件验证校准、事业方向评估、财富名望预测、
  家庭合婚协同等全方位命理解读。当用户请求八字分析、命理咨询、运势预测、事业财富评估、
  命盘合婚、大运流年解读时触发此 Skill。
---

# 八字命理深度分析 Skill

## 核心能力

1. **八字排盘与格局判定**：根据出生年月日时排出四柱，分析日主强弱、五行喜忌、十神格局
2. **大运流年推演**：推算十年大运和年度流年，标注吉凶时间节点
3. **事件验证校准**：用户提供已发生事件，反向验证命理准确性并校准预测
4. **事业方向评估**：基于命格推荐最适合的行业、岗位、创业/打工决策
5. **财富名望预测**：预测一生财富量级、社会名望层级、身家过亿路径
6. **家庭合婚协同**：夫妻合婚分析、子女命格评估、家庭财富合力路径

## 分析流程（严格执行）

### Phase 1：排盘与基础分析
1. 接收用户出生信息（年月日时，注明农历/公历、性别、出生地）
2. 排出四柱八字（年柱、月柱、日柱、时柱）
3. **⚠️ 关键验证步骤：日柱计算后必须使用已知参考点验证**
   - 加载 `bazi-fortune-analysis/references/calendar-anchor-points.md`
   - 使用 2008-08-08 = 庚辰 或其他已确认八字（如魏启令 1980-08-06 = 辛亥）做交叉验证
   - 若验证不通过 → 日柱计算有误，不可继续分析
4. 标注天干地支、藏干、纳音、神煞
5. 读取 [references/bazi-theory.md](references/bazi-theory.md) 获取核心理论

### Phase 2：五行十神深度分析
1. 计算五行力量分布（金木水火土各占比例）
2. 判定日主强弱（得令、得地、得势）
3. 确定十神格局（正官、七杀、正印、偏印、比肩、劫财、食神、伤官、正财、偏财）
4. 找出用神、忌神、喜神、仇神
5. 读取 [references/wuxing-analysis.md](references/wuxing-analysis.md) 获取分析方法

### Phase 3：大运流年推演
1. 排大运（顺排/逆排，根据年干阴阳和性别）
2. 标注每个大运的天干地支、十神、吉凶属性
3. 标注关键流年（用神到位、忌神到位、冲合刑害年份）
4. 读取 [references/dayun-liunian.md](references/dayun-liunian.md) 获取推演方法

### Phase 4：事件验证校准（用户提供事件后执行）
1. 接收用户提供的已发生真实事件（带年份）
2. 将事件映射到对应的大运/流年
3. 验证命理预测与真实事件的吻合度
4. 根据偏差校准后续预测
5. 读取 [references/event-calibration.md](references/event-calibration.md) 获取校准方法

### Phase 5：事业财富名望预测
1. 基于校准后的命格评估事业方向
2. 预测财富量级（使用财富预测模型）
3. 预测社会名望层级
4. 若用户有明确目标（如身家过亿），制定最优路径
5. 读取 [references/wealth-prediction.md](references/wealth-prediction.md) 获取预测模型

### Phase 6：输出报告
1. 按规范格式生成完整报告
2. 包含图表（五行力量图、大运走势图、财富路径图等）
3. 读取 [references/output-format.md](references/output-format.md) 获取输出规范

## 核心原则

### 四书经典为准绳
- 《渊海子平》：格局判定、用神取用
- 《三命通会》：神煞、纳音、各类命格详解
- 《滴天髓》：五行生克、旺衰强弱、命理哲学
- 《子平真诠》：格局成败、用神层次、命理精微

### 验证校准循环
每次用户补充真实信息后，必须执行校准：
1. 对比预测 vs 实际 → 找出偏差原因
2. 重新审视用神/格局 → 微调判定
3. 更新后续预测 → 提高准确度
4. 记录校准日志 → 追踪预测准确率

### 量化表达
- 五行力量用百分比表示
- 命格等级用 1-10 级表示
- 财富量级用具体数字区间（万/亿）
- 名望层级用标准等级（无名→圈内→行业→公众→名流）
- 时间节点尽量精确到年份

## 参考文件速查

| 分析阶段 | 需要读取的文件 | 内容 |
|---------|-------------|------|
| 排盘基础 | [references/bazi-theory.md](references/bazi-theory.md) | 四柱理论、天干地支、藏干、纳音、神煞表、**四柱与人生四阶段（年0-20/月20-35/日35-60/时60+）** |
| 日柱校准 | [bazi-fortune-analysis/references/calendar-anchor-points.md](bazi-fortune-analysis/references/calendar-anchor-points.md) | **⚠️ 日柱计算参考点验证（必备）** — 1900-01-01=甲戌，2008-08-08=庚辰 |
| 五行十神 | [references/wuxing-analysis.md](references/wuxing-analysis.md) | 五行生克、十神定义、格局判定、用神取用、**实用格局速查表（食神+七杀→抗风险行业等）** |
| 大运流年 | [references/dayun-liunian.md](references/dayun-liunian.md) | 大运排法、流年吉凶、冲合刑害 |
| 事件校准 | [references/event-calibration.md](references/event-calibration.md) | 验证方法、偏差分析、校准流程 |
| 财富名望 | [references/wealth-prediction.md](references/wealth-prediction.md) | 财富模型、名望层级、身家过亿路径 |
| 报告输出 | [references/output-format.md](references/output-format.md) | 报告结构、图表规范、校准标记 |
| **身强身弱精密判断** | **[references/shen-qiang-ruo-precision.md](references/shen-qiang-ruo-precision.md)** | **假旺真弱识别、各日主误判场景、三合局量化、强制排查清单** |