# 端到端链路验证方法论

> 归属技能：bazi-paipan-sop
> 编制时间：2026-07-07

## 用途

用已确认八字的两个人跑通全部6 Phase，验证物理自动化体系的稳定性、逻辑性、合理性和正确性。

## 前置铁律

- 取对八字：用已确认数据直接跑引擎，不从日期重新推导
- 首次即真理：第一次拿到的八字=ground truth，无对比对象
- 源头验证：排盘前先date确认服务器时间

## 验证流程

### Phase 0 — 系统就绪
确认SOUL/USER/MEMORY/HERMES全部自动加载，config.yaml auto_load 7个技能就绪

### Phase 1 — 技能加载
skill_view顺序：foundation-analysis → engine-workflow → report-template → platform-harness → auto-verify → wushidun-verify

### Phase 2 — 排盘+源头校验
bazi-must-run-engine.sh跑引擎(用已确认数据)→ 校验四柱一致 → 藏干十神核对 → 五鼠遁验证 → 文昌检查 → 门禁验证

### Phase 3 — 引擎21§评分
pipeline_v5.run_v5() → 验证21个§全输出 → 身强弱/喜忌/财星/大运与知识库一致 → 当前年份落在正确大运

### Phase 4 — 三项必含检查
① 性格分析(§6五重人格) — 所有人必含
② 补财库方案(§8.5) — 所有人必含，有库→蓄财，无库→5种补法
③ 文昌改进方案(§21.8) — 年龄≤25或引擎标需补→强制包含

### Phase 5 — 发布前校验
pillar-verify.py 5关 → validate_all.py 320门禁(API测试失败为预期) → verify_report.py 7项格式

### Phase 6 — 归档推库
知识库git双推(知识库+profile)，禁止写/root/

## 常见失败模式
- 日期推导错误：用新日期而非已确认八字 → 取对八字直接跑
- API测试FAIL：validate_all API测试依赖服务 → 引擎级测试独立验证
- 技能不存在：skill_view报错 → 检查skills_list找替代
- 推库冲突：远端有变更 → git pull --rebase再推
