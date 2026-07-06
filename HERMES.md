# ═══════════════════════════════════════════════
# 金鉴真人 · 八字排盘平台 HERMES.md
# bazi项目级：约束 · 原则要求 · SOP
# HERMES.md 优先级高于 AGENTS.md（or链第1位）
# ═══════════════════════════════════════════════

## 🔥 项目铁律

### 铁律① — 排盘必须跑引擎（禁止手算）
- 来源: 2026-06-29 梦的日柱算错教训（壬戌→癸亥）
- 强制命令: `bash projects/bazi-platform/scripts/bazi-must-run-engine.sh -n <姓名> -g <性别> -y <年> -m <月> -d <日> -h <时>`
- 验证: 排盘输出必须与 engine/paipan.py 计算结果一致，禁止自行计算公式
- 执行时机: **任何八字分析前**，先跑这个脚本获取引擎数据

### 铁律② — 知识库路径不依赖记忆
- 人物报告存放: `/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{序号}-{姓名}/`
- 编码规则: 序号为当前目录最大号+1
- GitHub: `git@github.com:corinwe/weiwuji-knowledge-base.git`
- 推库命令: `cd /root/weiwuji-knowledge-base && git add -A && git commit -m "消息" && git push`
- 技能引用版配置: `skill_view('bazi-platform-harness','references/project-config.md')`

### 铁律③ — 报告必须按标准格式输出（21§）
- 来源: `skill_view('bazi-report-template')` → bazi-report-template v5.2
- 强制: 每次出报告前先 `skill_view('bazi-report-template')`
- 格式: 21§板块齐全，§1 25字段四段式，深度≥1,500行
- 禁止自创格式、禁止跳过模板直接输出

### 铁律④ — 排盘源头校验（2026-07-06）
- 排盘脚本 `bazi-must-run-engine.sh` 自动调 `canggan-parse.py`
- 排盘时就标出「藏干十神易混淆项」（如辛+午=七杀⚠️）
- 源头防错，不等分析结束

### 铁律⑤ — 分析结论发布前校验（2026-07-06）
- 跑 `python3 projects/bazi-platform/scripts/pillar-verify.py`
- 5关: 五鼠遁 → 藏干十神 → 结构优先级 → 全局冲刑 → 最优性

### 铁律⑥ — 车库测试门禁（任何修改后必跑）
- 全量验证: `cd projects/bazi-platform/engine/tests && python3 validate_all.py`
- 排盘验证: `bash projects/bazi-platform/scripts/bazi-must-run-engine.sh`

### 铁律⑦ — 原始理论验证原则（2026-07-05 · 学业模块走弯路教训）
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

### 铁律⑧ — 模块审计/修复标准流程（2026-07-05）
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

---

## 📍 核心路径

| 资源 | 路径 |
|:-----|:------|
| 引擎目录 | `projects/bazi-platform/engine/` |
| 排盘门禁脚本 | `projects/bazi-platform/scripts/bazi-must-run-engine.sh` |
| 排盘源头校验 | `projects/bazi-platform/scripts/canggan-parse.py`（自动集成） |
| 四柱5关校验 | `projects/bazi-platform/scripts/pillar-verify.py` |
| 测试验证 | `cd projects/bazi-platform/engine/tests && python3 validate_all.py` |
| 项目配置 | `skill_view('bazi-platform-harness','references/project-config.md')` |
| 知识库 | `/root/weiwuji-knowledge-base` |
| 人物档案 | `/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{序号}-{姓名}/` |
| skills | `projects/bazi-platform/skills/`（26个技能） |

---

## 🔄 工作流程

```
收到任务
  ↓
① 系统级已就绪：SOUL.md + USER.md + MEMORY.md（Hermes自动加载）
② 按需加载技能：skill_view('bazi-{topic}-analysis')（看任务→技能矩阵）
③ 加载项目配置：skill_view('bazi-platform-harness','references/project-config.md')
④ 排盘源头校验：bash projects/bazi-platform/scripts/bazi-must-run-engine.sh（已集成canggan-parse.py）
⑤ 执行分析/出报告（报告前加载 skill_view('bazi-report-template')）
⑥ 发布前校验：python3 projects/bazi-platform/scripts/pillar-verify.py
⑦ 放入人物档案目录
⑧ cd /root/weiwuji-knowledge-base && git push
```

---

## 📋 任务→技能矩阵

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

---

**本文件版本：v1.0 · 2026-07-06 · 取代AGENTS.md**
**加载机制：HERMES.md 是 or 链最高优先级，当前无.hermes.md挡路 → 本文件成功加载。**
