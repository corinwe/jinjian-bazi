# 金鉴真人·八字排盘平台

## 🔥 项目铁律（本文件在工作目录下自动加载）

### Hermes自动加载机制（不需要手动读）
```
SOUL.md  ← profile根目录 · 自动加载     → 系统级身份+铁律
USER.md  ← memories/USER.md · 自动注入  → 老板画像+原则+教训
MEMORY.md ← memories/ · 自动注入         → 持久记忆
本文件    ← 当前工作目录 · 自动触发       → 项目级SOP ↓
Skills   ← skill_view()按需加载          → 任务对应技能
```

### 铁律① — 排盘必须跑引擎（禁止手算）
- 来源: 2026-06-29 梦的日柱算错教训（壬戌→癸亥）
- 强制命令: `bash /root/bazi-platform/scripts/bazi-must-run-engine.sh -n <姓名> -g <性别> -y <年> -m <月> -d <日> -h <时>`
- 验证: 排盘输出必须与 engine/paipan.py 计算结果一致，禁止自行计算公式
- 执行时机: **任何八字分析前**，先跑这个脚本获取引擎数据

### 铁律② — 知识库路径不依赖记忆
- 人物报告存放: `/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{序号}-{姓名}/`
- 编码规则: 序号为当前目录最大号+1
- GitHub: `git@github.com:corinwe/weiwuji-knowledge-base.git`
- 命令: `cd /root/weiwuji-knowledge-base && git add -A && git commit -m "消息" && git push`

### 铁律③ — 所有规则不能依赖LLM记忆
- 本文件是所有物理规则的来源之一
- 项目配置完整版: `/root/bazi-platform/.hermes/config/credentials.md`
- 技能引用版: `skill_view('bazi-platform-harness','references/project-config.md')`
- 每次分析前必须加载上述config文件，不靠回忆

### 铁律④ — 报告必须按标准格式输出（21§）
- 来源: `bazi-report-template v5.2` 标准模板
- 强制: 每次出报告前先 `skill_view('bazi-report-template')`
- 格式: 21§板块齐全，§1 25字段四段式，深度≥1,500行
- 禁止自创格式、禁止跳过模板直接输出

### 铁律⑤ — 原始理论验证原则（2026-07-05 · 学业模块走弯路教训）
- **老板提点 → 先查原始理论验证，不能照单全收**
  - 老板语音输入可能有错字/口水话，需要自行识别
  - 老板提点一个"点"，必须延伸到"面"和"体系"（正反面全看）
- **由点→面→体系**
  - 例：身强遇正财跑引擎认为"喜用"→ 但原始理论说「正财=搞钱」→ 实际是搞钱无心向学，不是学得好
  - 例：身强遇食伤跑引擎认为"喜用"→ 但素材02行129说「食伤追求吃喝玩乐」→ 贪玩
- **每次改规则前加载对应技能文件**确认原始理论
  - `skill_view('bazi-education-analysis')`
  - `skill_view('bazi-marriage-analysis')`
- **每次修改后拿真实案例跑验证**
- **无原始依据不杜撰** — 所有规则必须有素材行号或公众号原文支撑

### 铁律⑥ — 模块审计/修复标准流程（2026-07-05）
**每次审计/修复一个模块，必须按以下标准流程执行：**

**Step 1 — 规则审计（对照原始理论逐条验证）**
  □ 加载对应skill（`skill_view('bazi-xxx-analysis')`）
  □ 逐条对比代码逻辑 vs 原始理论
  □ 无杜撰（原始理论没有的不能写）
  □ 无遗漏（原始理论有的不能少）
  □ 无错误（与原始理论完全一致）
  □ 特别检查：模块的判断逻辑本身是否与九龙道长一致

**Step 2 — 全量更新（修哪改哪的全都要改）**
  □ 代码/引擎逻辑更新
  □ 相关函数签名/返回值更新
  □ 引用该模块的所有文件更新
  □ 页面/报告/脚本/配置同步更新

**Step 3 — 引用链验证（排盘时正确调用）**
  □ 所有pipeline确认调用新版（v3/v4/v5各查一遍）
  □ 调用参数完整（特别是shen_label/喜用神是否传递）
  □ comprehensive_v2中间层参数传递正确
  □ 测试通过（test_full_suite.py）

**Step 4 — 点面体系验证**
  □ 修一个点→延伸到整个面→延伸到整个体系
  □ 正反面逻辑都考虑
  □ 拿真实案例验证输出合理
  □ 确认排盘脚本(bazi-must-run-engine.sh)能正确引用新版

## 核心路径
- 引擎目录: `/root/bazi-platform/engine/`
- 排盘门禁: `/root/bazi-platform/scripts/bazi-must-run-engine.sh`
- 测试验证: `cd /root/bazi-platform/engine/tests && python3 validate_all.py`
- 知识库: `/root/weiwuji-knowledge-base`

## 工作流程

```
收到任务
  ↓
① 信任Hermes已自动加载：SOUL.md + USER.md + MEMORY.md + 本文件
② 按需加载技能：skill_view('bazi-{topic}-analysis')（任务→技能矩阵见§1）
③ 加载项目配置：skill_view('bazi-platform-harness','references/project-config.md')
④ 排盘源头校验：bash /root/bazi-platform/scripts/bazi-must-run-engine.sh（已集成canggan-parse.py）
⑤ 执行分析/出报告（报告前加载 skill_view('bazi-report-template')）
⑥ 发布前校验：python3 /root/bazi-platform/scripts/pillar-verify.py
⑦ 放入人物档案目录
⑧ cd /root/weiwuji-knowledge-base && git push
```

## §1 — 任务→技能矩阵（技能加载参考）

| 任务 | 必须加载 | 可选加载 |
|:-----|:---------|:---------|
| **排盘/基础分析** | `bazi-foundation-analysis` | `bazi-auto-verify` |
| **财富分析** | `bazi-wealth-analysis` | `bazi-foundation-analysis` |
| **事业分析** | `bazi-career-analysis` | `bazi-wealth-analysis` |
| **婚姻分析** | `bazi-marriage-analysis` | `bazi-foundation-analysis` |
| **学业分析** | `bazi-education-analysis` | `bazi-foundation-analysis` |
| **健康/疾病** | `bazi-health-psychology` | `bazi-misfortune-analysis` |
| **子女分析** | `bazi-children-analysis` | `bazi-foundation-analysis` |
| **灾祸分析** | `bazi-misfortune-analysis` | `bazi-liunian-analysis` |
| **化解方法** | `bazi-remission-methods` | `bazi-foundation-analysis` |
| **流年分析** | `bazi-liunian-analysis` | `bazi-foundation-analysis` |
| **买房置业** | `bazi-house-buying` | `bazi-wealth-analysis` |
| **四柱反推** | `bazi-four-pillars-analysis` | — |
| **出报告** | `bazi-report-template` | 对应事象技能 |
| **校准/审计** | `bazi-calibration` | 对应模块技能 |
| **全量验证** | `bazi-validate-all` | `bazi-auto-verify` |
