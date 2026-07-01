# 金鉴真人·八字排盘平台

## 🔥 物理铁律（每次进入项目自动加载）
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

## 核心路径
- 引擎目录: `/root/bazi-platform/engine/`
- 排盘门禁: `/root/bazi-platform/scripts/bazi-must-run-engine.sh`
- 测试验证: `cd /root/bazi-platform/engine/tests && python3 validate_all.py`
- 知识库: `/root/weiwuji-knowledge-base`

## 工作流程
```
收到八字分析需求
  ↓
① skill_view('bazi-platform-harness','references/project-config.md') 加载配置
② bash /root/bazi-platform/scripts/bazi-must-run-engine.sh 跑引擎排盘
③ skill_view('bazi-report-template') 加载报告模板
④ 按21§标准格式写报告（≥1,500行）
⑤ 报告放入人物档案目录
⑥ cd /root/weiwuji-knowledge-base && git push
```
