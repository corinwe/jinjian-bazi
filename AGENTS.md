# 金鉴真人·八字排盘平台

## 🔥 物理铁律（每次进入项目自动加载）
- **SOUL.md**: `/root/bazi-platform/SOUL.md` — 我的身份定义+核心原则+铁律+行事风格
- **USER.md**: `/root/bazi-platform/USER.md` — 老板画像+原则+风格+核心教训
- 完整铁律列表保存于: `/root/bazi-platform/.hermes/config/credentials.md`
- 包含铁律①排盘跑引擎 ②知识库路径 ③不依赖记忆 ④报告格式 ⑤财富规则 ⑥学习协议
- 每次进入项目必须先加载: `skill_view('bazi-platform-harness','references/project-config.md')`
- 收到老板新知识（文档/音频/视频/链接/图片）时，先加载: `skill_view('learning-protocol')`

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

### 铁律⑦ — 任务启动强制加载顺序（2026-07-06）

**每次执行任务前，必须按 §1→§2→§3→§4→§5 顺序加载。**

- 文件: `/root/bazi-platform/BOOTSTRAP.md`
- 完整加载顺序表在该文件中
- 禁止跳过任意一节
- 必须在排盘/出报告/分析/修Bug/审计前执行

```
□ §1 身份设定    → cat SOUL.md
□ §2 老板画像    → cat USER.md
□ §3 项目配置    → skill_view('bazi-platform-harness','references/project-config.md')
□ §4 分析技能    → skill_view('bazi-{topic}') （见BOOTSTRAP.md任务→技能矩阵）
□ §5 运行时校验  → canggan-parse.py（自动集成到排盘门禁）
```

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

## 工作流程（新 · BOOTSTRAP标准顺序）
```
收到任务
  ↓
① §1 加载身份设定     → cat SOUL.md
② §2 加载老板画像     → cat USER.md
③ §3 加载项目配置     → skill_view('bazi-platform-harness','references/project-config.md')
④ §4 加载分析技能     → skill_view('bazi-{topic}') 查阅BOOTSTRAP.md任务→技能矩阵
⑤ §5 排盘源头校验     → bash scripts/bazi-must-run-engine.sh（已集成canggan-parse.py）
⑥ 执行分析/出报告
⑦ 放入人物档案目录
⑧ cd /root/weiwuji-knowledge-base && git push
```
