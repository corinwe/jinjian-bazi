# 金鉴真人·八字平台 Harness Engineering 应用案例

> 将Harness Engineering理论落地到实际产品中的完整记录

## 项目背景

八字排盘分析平台（projects/bazi-platform/）
- 引擎：Python 12,437行，36模块（确定性规则引擎）
- API：FastAPI，8个端点
- 前端：单页SPA，21§报告渲染
- GitHub: corinwe/jinjian-bazi

## 应用的Harness Engineering原则

### 1. Agent = Model + Harness
- **Model**: 我（金鉴真人AI Agent）= 推理层，判断规则应用
- **Harness**: bazi-platform-harness总调度技能 = 控制系统
  - 前馈指南：18个八字技能 + 20个工程技能 + AGENTS.md
  - 反馈传感器：test_imports.py(模块验证) + test_full_suite.py(320条测试) + validate_all.py(26项全量验证)

### 2. 计算型验证 > 推理型验证
- 计算型（确定性）：paipan引擎、身强弱评分、财星分数、320条测试、validate_all.py
- 推理型（LLM判断）：老板审查报告、校准验证
- 流程：先计算型验证通过 → 再提交给人审查

### 3. 前馈 + 反馈双模式
- **前馈**（在行动前引导）：bazi-platform-harness 6 Phase流程、强制技能加载表
- **反馈**（在行动后纠正）：validate_all 26项、Prove-It模式写测试再修Bug

### 4. L0 零信任
- 每次修改都假设会引入Bug
- Prove-It模式：先写复现测试（RED）→ 再修复（GREEN）→ 再验证
- 执行者（开发）和评估者（验证脚本）始终分离

### 5. 三层架构
```
Layer 3: 用户Harness（老板审批）
Layer 2: 构建者Harness（bazi-platform-harness总调度）
Layer 1: 模型Harness（18八字技能 + 20工程技能）
```

## 实际工作流（经过本案例验证）

### Bug修复流程（Prove-It）
```
1. RED: 写复现Bug的测试（test_imports.py）
2. 确认测试失败（证明Bug存在）
3. 定位根因（函数名不一致：calculate→compute）
4. GREEN: 修函数调用
5. 测试通过
6. 运行完整套件（validate_all 26/26）
7. 提交
```

### 全方位重整流程（5 Sprint）
```
Sprint 1: 引擎修复+验证强化 → validate_all PASS
Sprint 2: API完善 → 8端点正常 + OpenAPI文档
Sprint 3: 前端改造 → 21§完整渲染
Sprint 4: CI/CD → GitHub Actions三阶段
Sprint 5: 用户系统 → 暂未完成
```

## 关键教训

### 教训1: 导入检查必须先做
- 问题：引擎模块有函数名不一致（calculate→compute），但test_full_suite.py没暴露
- 修复：新增test_imports.py验证所有模块函数签名
- 防护：validate_all.py中加入导入验证步骤

### 教训2: API重启前后验证
- API修改后需重启 → 验证端点 → 再提交
- Uvicorn background进程管理方式：
  - 旧进程要pkill再启动
  - 启动后sleep 2秒等ready
  - 用curl验证所有端点

### 教训3: Git PAT权限
- GitHub PAT推送需要repo scope
- 含workflow文件的推送需要workflow scope
- 如果PAT权限不足：排除workflow文件先推代码

### 教训4: 前端单文件架构
- 当前515行index.html = 全部前端
- 优点：零构建、零依赖
- 缺点：难以模块化、测试困难
- 后续：如需要复杂交互，拆分Vue/React组件

## 验证指标

| 检查项 | 通过标准 | 本案例结果 |
|--------|---------|-----------|
| test_imports.py | 19模块全部可导入 | ✅ |
| test_full_suite.py | 320条全部通过 | ✅ |
| validate_all.py | 26项全部PASS | ✅ |
| API端点 | 8端点正常响应 | ✅ |
| 前端 | 21§渲染 + 农历/阳历 | ✅ |
| 报告格式 | 版本说明/25字段/白话/五级对照/署名 | ✅ |
