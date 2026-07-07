---
name: bazi-task-dispatch
description: 金鉴真人·Sub-Agent任务派发标准模板。涵盖7种Sub-Agent分工的delegate_task模板，context四要素（目标+标准+格式+流程），终止条件定义规则，post-task路径验证与全量审计流程。用于任何需要派sub-agent干活的场景。
category: software-development
---

# 🚀 金鉴真人 · Sub-Agent 任务派发标准模板

> **核心铁律：** 每次派任务，context必须带四要素——🎯目标 + 📏标准 + 📋格式 + 🔄流程。\\n> **没有终止条件不派活。**\\n> **Sub-Agent返回后必须验证结果（路径+内容），不可轻信自述报告。**\\n> **批量任务完成后自动执行全量审计，不等用户问。**\\n> **报告交付（.md→.docx→飞书推送）由 bazi-platform-harness §Phase 7 流程处理。**

---

## 📦 通用模板结构

```python
delegate_task(
    goal="🎯 [一句话：做什么]",
    context=f"""
    🎯 **目标：**
    [具体要完成什么工作]

    📏 **标准：**
    [质量要求 / 必须遵守的规则]
    - 来源：金鉴真人·九龙道长原始规则

    📋 **格式：**
    [输入数据格式 → 输出数据格式]

    🔄 **流程：**
    1. [第一步：做什么]
    2. [第二步：验证什么]
    3. [第三步：提交什么]

    🛑 **终止条件：**
    Success = [可脚本验证的命令/条件]
    
    🏗️ **项目上下文：**
    - 项目路径：projects/bazi-platform/
    - 引擎路径：projects/bazi-platform/engine/
    - 测试命令：cd engine && python3 tests/test_full_suite.py
    - Git：cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && git add -A && git commit -m "msg" && git push
    """,
    toolsets=['terminal', 'file']
)
```

---

## 🎯 模板1：派引擎开发员

```python
delegate_task(
    goal="🎯 实现[模块名]规则引擎模块",
    context=f"""
    🎯 **目标：**
    在 projects/bazi-platform/engine/ 下实现 [模块名] 模块

    📏 **标准：**
    - 所有逻辑必须源自九龙道长原始规则（零自创）
    - 每个断语必须有规则依据标注
    - TDD先行：先写测试，再写实现
    - 最小实现原则（YAGNI）

    📋 **格式：**
    - 输入：BaZi struct (from constants.py)
    - 输出：dict with scoring + analysis text
    - 测试：tests/test_[module].py 覆盖正向+负向+边界

    🔄 **流程：**
    1. 写测试（RED）→ 验证测试失败
    2. 写最小实现（GREEN）→ 验证测试通过
    3. 运行完整测试套件 → 无回归
    4. py_compile 通过

    🛑 **终止条件：**
    Success = cd projects/bazi-platform/engine && python3 tests/test_full_suite.py — 全部PASS
    
    🏗️ **项目上下文：**
    - 引擎路径：projects/bazi-platform/engine/
    - 运行测试：cd projects/bazi-platform/engine && python3 tests/test_full_suite.py
    - 模块导入验证：cd projects/bazi-platform/engine && python3 tests/test_imports.py
    """,
    toolsets=['terminal', 'file']
)
```

---

## 🎯 模板2：派前端开发员

```python
delegate_task(
    goal="🎯 [前端任务描述]",
    context=f"""
    🎯 **目标：**
    [具体前端改动]

    📏 **标准：**
    - 移动端优先设计
    - 暗金配色（深色背景#1a1a2e + 金色#c9a84c）
    - 永不展示原始JSON字段/分数
    - 21§展示顺序必须与bazi-report-template一致
    - 响应式设计，适配手机+平板+桌面

    📋 **格式：**
    - 前端文件：projects/bazi-platform/frontend/
    - API基础URL：http://43.162.90.39:8000

    🔄 **流程：**
    1. 修改前端文件
    2. 本地验证HTML/CSS/JS语法
    3. 部署到服务器验证

    🛑 **终止条件：**
    Success = python3 projects/bazi-platform/engine/tests/test_e2e.py --remote — 16/16通过
    """,
    toolsets=['terminal', 'file', 'browser']
)
```

---

## 🎯 模板3：派API开发员

```python
delegate_task(
    goal="🎯 [API任务描述]",
    context=f"""
    🎯 **目标：**
    [具体API改动]

    📏 **标准：**
    - 契约优先：先定义请求/响应模型
    - 错误语义明确：400/404/422/500 使用标准HTTP状态码
    - 向后兼容：不破坏现有客户端
    - 所有端点必须有健康检查覆盖

    📋 **格式：**
    - API路径：projects/bazi-platform/api/
    - 端点参考：GET /ping | GET /health | POST /analyze | POST /report

    🔄 **流程：**
    1. 定义schema
    2. 实现路由
    3. 写测试
    4. 启动服务验证

    🛑 **终止条件：**
    Success = curl -s http://localhost:8000/health | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='healthy'"
    """,
    toolsets=['terminal', 'file']
)
```

---

## 🎯 模板4：派测试验证员

```python
delegate_task(
    goal="🎯 编写[模块]测试用例",
    context=f"""
    🎯 **目标：**
    为 [模块] 编写完整测试覆盖

    📏 **标准：**
    - 覆盖正向+负向+边界三种场景
    - 每个核心函数至少3个测试用例
    - 使用 pytest + pytest-cov
    - 测试数据用真实八字（家主/子源/主母等）

    📋 **格式：**
    - 测试文件：projects/bazi-platform/engine/tests/test_[module].py
    - 继承现有测试风格（test_full_suite.py）

    🔄 **流程：**
    1. 阅读现有测试 + 理解模块功能
    2. 编写测试
    3. 运行全部测试 → 无回归
    4. 运行覆盖率 → 不降低基线

    🛑 **终止条件：**
    Success = cd projects/bazi-platform/engine && python3 tests/test_full_suite.py — 全部PASS
    AND coverage >= 45%
    """,
    toolsets=['terminal', 'file']
)
```

---

## 🎯 模板5：派审核员（Checker）

```python
delegate_task(
    goal="🎯 对抗性审查 [具体实现]",
    context=f"""
    🎯 **目标：**
    你是一个对抗性审查员。审查以下实现是否满足规格要求。

    📏 **标准（五轴审查）：**
    - [ ] **正确性**：所有需求是否实现？
    - [ ] **可读性**：变量命名/函数结构是否清晰？
    - [ ] **架构**：是否遵循了项目的分层和约定？
    - [ ] **安全**：有无SQL注入/XSS/权限漏洞？
    - [ ] **性能**：有无明显的性能问题？

    📋 **格式：**
    输出格式（严格）：
    STATUS: PASS 或 REJECT
    
    如REJECT，提供：
    1. Failure: [具体问题]
       Evidence: [文件:行号]
    
    如PASS:
    STATUS: PASS

    🔄 **流程：**
    1. 逐条核对原始Spec
    2. 检查是否做了不该做的事（范围蔓延）
    3. 运行测试验证

    🛑 **终止条件：**
    Success = STATUS: PASS + 所有测试通过
    """,
    toolsets=['terminal', 'file']
)
```

---

## 🎯 模板6：派命理分析师

```python
delegate_task(
    goal="🎯 分析[姓名]的八字命格",
    context=f"""
    🎯 **目标：**
    对 [姓名（性别，出生日期）] 进行完整八字命理分析

    📏 **标准：**
    - 零自创断事逻辑（必须有原始素材行号）
    - 身强弱：用九龙道长原始规则（印只月令本气/比劫全算）
    - 先查规则→再对比八字数据→再出结论
    - 禁止通用占位符/模板话术

    📋 **格式：**
    输出21§完整报告，格式参考 projects/bazi-platform/engine/tests/test_full_suite.py 中的§结构

    🔄 **流程：**
    1. 排盘（用 bazi-pipeline.sh）
    2. 身强弱评分 → 取用神忌神
    3. 格局判定 → 十神分析
    4. 8维度评分
    5. 大运分析 → 流年窗口
    6. 生成21§报告

    🛑 **终止条件：**
    Success = cd projects/bazi-platform/engine && python3 tests/validate_all.py — 全部PASS
    """,
    toolsets=['terminal', 'file']
)
```

---

## 🎯 模板7：派报告生成员

```python
delegate_task(
    goal="🎯 格式化输出[姓名]的21§报告",
    context=f"""
    🎯 **目标：**
    将引擎结构化数据 → 格式化为可读的21§报告文本

    📏 **标准：**
    - 每行内容都必须基于原始理论规则逐条对比八字数据
    - §1 25字段四段式排序
    - §§2-21 完整覆盖
    - 附录必须有具体八字数据支持
    - 学历精确到985/211+本科/硕士/博士
    - 大运排序按喜用神逻辑

    📋 **格式：**
    输出markdown格式报告，符合 projects/bazi-platform/skills/bazi-report-template/SKILL.md

    🔄 **流程：**
    1. 读取引擎JSON数据
    2. 按模板填充各§
    3. 验证21§完整性
    4. 添加#PIPELINE-SIG签名

    🛑 **终止条件：**
    Success = #PIPELINE-SIG in report AND 21§完整
    """,
    toolsets=['file']
)
```

---

## 🚨 任务派发检查清单

每次delegate_task前，自检：

- [ ] **🎯 目标** — 一句话说清做什么？
- [ ] **📏 标准** — 质量/规则约束是否明确？
- [ ] **📋 格式** — 输入输出格式是否定义？
- [ ] **🔄 流程** — 执行步骤是否清晰？
- [ ] **🛑 终止条件** — 可脚本验证的完成标准？
- [ ] **工具集** — terminal/file/browser/vision 是否匹配任务？
- [ ] **依赖关系** — 是否需要等另一个Sub-Agent先完成？
- [ ] **Maker/Checker分离** — 如果任务重要，是否需要独立Checker？

## 🚨 常见陷阱与事后验证

### 陷阱①：Sub-Agent 写错路径

**现象：** Sub-Agent 写文件时写了错误的路径（如知识库路径而不是技能包路径），返回的 summary 声称"写入成功"，但实际文件不在正确位置。

**案例：** 2026-06-30，career-analysis 被写入 `/root/weiwuji-knowledge-base/.../skills/bazi/` 而非 `projects/bazi-platform/skills/bazi/`。

**根因：** Sub-Agent 用自己的工作目录判断路径，或从旧 session 中复用了错误的 base path。

**验证流程（每次Sub-Agent回来后必做）：**
```
Step 1 — 查看 summary 中声称写入的文件路径
Step 2 — 用 ls/stat 确认该路径是否存在
Step 3 — 如果路径是知识库路径（weiwuji-knowledge-base）但预期是技能包路径（profiles/.../skills/）:
   → 确认文件存在后，cp 到正确的技能包路径
   → 检查知识库的 git status 确认未造成脏提交
Step 4 — 如果路径不正确，记录问题并修正
```

### 陷阱②：并行任务写同一文件（write-write 冲突）

**现象：** 两个 Sub-Agent 同时修改同一个 SKILL.md，后写的覆盖了先写的。

**解法：** 不同子任务分配不同的技能包。如需修改同一技能包的各种子§，让 Sub-Agent 分别输出片段，由父 Agent 统一合并。

### 陷阱③：Sub-Agent 返回的"成功"不可信

**现象：** Sub-Agent 声称"文件已写入"或"上传成功"，但实际没有。

**规则：** Sub-Agent summary 是自述报告，不是验证结果。对于有外部副作用的操作（写文件/HTTP请求/远程部署），必须要求 Sub-Agent 返回可验证的句柄（文件路径/URL/ID），父 Agent 亲自验证。

**验证命令示例：**
```bash
# 验证文件写入
ls -la /预期路径/SKILL.md      # 确认存在
wc -l /预期路径/SKILL.md       # 确认行数合理
grep "新增内容" /预期路径/SKILL.md  # 确认内容已写入

# 验证 git 提交
cd /repo_path && git log --oneline -3  # 确认最近的commit
cd /repo_path && git status --short    # 确认无未提交更改
```

### 陷阱⑤：合集文档生成时不能只留摘要

**现象：** 生成多份报告合集时，只提取了核心摘要和汇总表，把各篇报告的具体补财库流程、前提条件、操作细节全删了。用户看到合集后指出「补财库开财库的前提条件全没了」。

**根因：** 以为用户只需要汇总数据，实际用户需要每篇报告的全部内容拼在一起。

**铁律：合集文档 = 各篇报告全文拼接（不删任何内容）**
```
每次生成合集文档：
Step 1 — 确认合集用途：用户要的是"合集"（所有内容放一起），不是"摘要"
Step 2 — 使用 sed 跳过每篇报告的第1行标题（#），其余全部保留
Step 3 — 每篇之间用 --- 分隔
Step 4 — 首部加版本说明和汇总速查表（方便概览）
Step 5 — 生成 .md + .docx 双格式
Step 6 — 推库 + 飞书推送

验证命令：
  wc -l 合集文件        # 合集行数 ≈ 各篇行数之和（略少几行标题）
  diff <(sed '1{/^#/d}' 原报告) <(grep -A999 '---' 合集 | tail -n+2)
  # 合集内容应与原报告一致
```

### 陷阱⑦：合集文档遗漏「跨领域」板块（2026-07-02校准）

**现象：** 合成多篇技能文档的合集时，只把每个Skill的内容拼在一起，但漏掉了需要「跨越多个Skill」的综合性板块——这些板块不在任何一个Skill的目录里，但确实是合集用户期望覆盖的内容。

**案例：** 2026-07-02，从bazi-career-analysis + bazi-foundation-analysis + bazi-liunian-analysis合成事业名望文档时，缺了「天干合化/冲/克与官运」这个完整板块。因为天干规则在liunian-analysis里讲「字间互动」，而官运规则在career-analysis里讲「提升官运」——没有一个Skill单独讲「天干×官运」这个交叉领域。

**根因：** 只按Skill的边界拼接内容，没有做「交集分析」——两个Skill的交集处往往是用户最关心的综合性知识。

**验证流程（每次合集文档生成后）：**
```
Step 1 — 列出所有涉及的Skill的主题域
Step 2 — 找两两Skill的交集，看是否有遗漏的「跨领域板块」：
  例：career（官运）∩ liunian（天干合化）= 天干合化×官运（漏了）
  例：wealth（财星）∩ liunian（合化）= 合化财×发财窗口（需检查）
Step 3 — 检查合集文档是否有独立的交叉板块覆盖这些交集
Step 4 — 如有遗漏，新增交叉板块再推库
```

**口诀：**
```
合集文档不只看单个Skill的边界
两个Skill的交集处
就是用户最关心的综合知识
丢了交叉板块等于丢了精华
```

### 陷阱⑥：多§报告中的大运序列必须跨节一致

**现象：** Sub-Agent 生成的多§报告中，§1总览表、§16事件表、§17大运精析中的大运干支名不一致——有的节用了顺排干支名，有的节用了逆排干支名，甚至有的节用错了大运序号。

**案例：** 2026-07-05，少爷子源v2.0报告——§1/§4/§17用正确的逆排大运（壬辰→辛卯→庚寅→己丑…），但§16事件表错用了顺排大运（癸巳→甲午→乙未…），§19大运评分表的最后2步也用了错误的干支（庚子→辛丑，正确为甲申→癸未）。

**根因：** Sub-Agent 生成大运时在不同节用了不同的算法，或同一个Sub-Agent在不同段落中复用了不同的参考数据。

**铁律：多§报告的大运一致性检查：**

```python
# 报告生成后的强制检查脚本
def check_da_yun_consistency(report_path):
    """验证报告中所有节的大运序列一致"""
    
    # 正确大运序列（从引擎获取）
    correct_sequence = [
        ("壬辰", "8.5~18.5", "2019~2029"),
        ("辛卯", "18.5~28.5", "2029~2039"),
        # ... 全部10步
    ]
    
    # 检查位置（根据实际报告结构调整）
    check_points = [
        {"section": "§1 总览", "pattern": "最佳大运.*(..)运"},
        {"section": "§16 事件表", "pattern": "(..)运（.*岁）"},
        {"section": "§17 大运精析", "pattern": "### .* (..)大运"},
        {"section": "§19 评分表", "pattern": r"\|\\s*\\d+\\s+\|\\s*(..)"},
    ]
    
    # 如果任一检查点的大运名与正确序列不符 → 必须修复
```

**验证清单（每个多§报告生成后）：**
- [ ] §1总览的「最佳大运」「次佳大运」「最差大运」与§17大运序列的第N步一致？
- [ ] §16事件表的每个大运段标题与§17的同年龄大运名称一致？
- [ ] §19评分表的每行大运名与§17的同序号一致？
- [ ] 大运序列总步数正确（阳男阴女/阴男阳女→顺排/逆排？）
- [ ] 大运最后2步未出现"跳跃式"错误（从逆排序列突然跳到顺排序列）

**验证命令（报告§19评分表大运名检查）：**
```bash
grep "^| [0-9]" §19部分  # 提取所有大运行
# 检查序号连续性 + 干支排列规律（逆排应逐次减，顺排应逐次加）
```

### 陷阱⑦：多§报告中的空亡数据必须跨节一致

**现象：** Sub-Agent 生成的报告中，§1的空亡字段写对了，但正文§§5-16中仍使用了错误的空亡数据（如旧版的空亡干支）。

**案例：** 2026-07-05，少爷子源v1.0→v2.0迁移——§1已修正为"午未·四柱无空亡"，但§5灾祸分析、§12婚姻分析、§8财富分析中仍有13处"戌为空亡"错误。

**根因：** Sub-Agent 修了§1但没同步修改正文中的空亡引用。

**铁律：空亡验证三步走：**

```
Step 1 — 排盘跑引擎获取正确空亡
    bash projects/bazi-platform/scripts/bazi-must-run-engine.sh -n 姓名 -g 性别 -y 年 -m 月 -d 日 -h 时
    → 从输出中提取空亡信息

Step 2 — 检查§1的空亡字段
    grep -n "空亡" 报告.md | head -1
    → 确认与引擎输出一致

Step 3 — 搜索正文中所有"空亡"、"为空"引用
    grep -n "空亡\|为空" 报告.md
    → 逐一确认每个引用都使用正确的空亡数据
    → 特别检查：财库空亡、夫妻宫空亡、健康空亡
```

**> 核心原则：先跑引擎获取空亡 → 再写入§1 → 最后遍历全文替换旧空亡引用**

### 陷阱⑧：报告中的十神标注必须与引擎同步验证

**现象：** Sub-Agent 生成报告时，自行推断十神（食神/伤官/正官/七杀等），但引擎数据可能已被修正。或者 Sub-Agent 记住了错误的十神规则写出错误内容。

**案例：** 2026-07-04，引擎 SHI_SHEN_MAP 中食神/伤官映射颠倒——辛金×癸水本应=食神，引擎错误输出=伤官。Sub-Agent 用引擎错误数据生成报告，97处月干癸水被标为伤官。用户指出后才发现。

**根因：** Sub-Agent 默认信任引擎数据，但引擎本身可能有 bug。且 Sub-Agent 不会主动验证引擎输出是否符合十神阴阳规则。

**铁律：十神验证铁三角**

```
每份报告中的月干十神，必须经过三重验证：
① 引擎数据：shi_shen.py 输出的是什么？
② 阴阳规则：日主五行的阴阳 × 月干五行的阴阳 → 正确十神是什么？
③ 报告文本：报告的§1-§12等章节中，十神名称是否与②一致？

流程：
  引擎输出 → 人工/LLM校验阴阳规则 → 报告写入
  不可跳过第②步直接写入
```

**十神阴阳速查口诀：**
- 正异偏同：正印/正官/正财=异阴阳，偏印/七杀/偏财=同阴阳
- **食伤例外**：食神=同阴阳，伤官=异阴阳（最容易错！）

**Sub-Agent 报告中十神的自检方法：**

```python
# 每月干/时干十神验证
十神规则表 = {
    ("我生", "同"): "食神",  # ✅ 阴生阴/阳生阳
    ("我生", "异"): "伤官",  # ✅ 阴生阳/阳生阴
    ("克我", "异"): "正官",  # ✅ 阴克阳/阳克阴
    ("克我", "同"): "七杀",  # ✅ 阴克阴/阳克阳
}

def verify_shi_shen(gan, ri_zhu, expected):
    # 检查五行生克关系和阴阳
    pass  # 调用 shi_shen.get_shi_shen_for_gan()
    if actual != expected:
        raise ValueError(f"十神错误: {ri_zhu}×{gan}={actual}, 应为{expected}")

# 关键检查点
verify_shi_shen(月干, 日主, 报告中的十神名)
```

**检查清单：**
- [ ] 月干的十神是否与阴阳规则一致？
- [ ] 时干的十神是否与阴阳规则一致？
- [ ] 年干的十神是否与阴阳规则一致？
- [ ] 格局描述中的十神名（如"伤官配印"）是否与实际十神匹配？
- [ ] 如果月干是食神但格局写的是"伤官配印"→ 格局名称全错 → 必须修正

### 陷阱⑩：Sub-Agent 内容分析必须明确要求「逐字逐句精读」

**现象：** 派Sub-Agent进行知识提取时，仅说"读取完整转写确定主题"或"提取知识点"，Sub-Agent理解为"扫描关键点即可"，跳过大量行造成遗漏。用户发现后纠正"逐字逐句精读啊"。

**根因：** Sub-Agent的默认行为是"提取要点"而非"逐行阅读"。没有明确指令时，它们会跳过中间行、只读开头结尾。

**铁律：内容分析类Sub-Agent任务，goal中必须包含"逐字逐句精读"或"读完全部N行"的明确要求：**

> **关联铁律：** `skill_view('learning-protocol')` 的「物理铁律：逐字逐句精读」章节覆盖亲自读和派子Agent读两种场景，本陷阱是子Agent场景的具体代码示例。

```python
# ✅ 正确写法（明确要求逐字逐句）：
delegate_task(
    goal="【逐字逐句精读】音频X（228k字·九龙道长核心课）\n\n"
         "必须：\n"
         "✅ 读完全部7510行！不要跳！\n"
         "✅ 逐段分析每个知识点\n"
         "✅ 对比已有体系标记【已掌握】/【新发现】/【补充细节】\n"
         "✅ 输出完整知识点提取报告到指定路径",
    context="...四要素..."
)

# ❌ 错误写法（容易被理解为扫描）：
delegate_task(
    goal="提取音频X的知识点，对比已有体系，输出报告",
    context="..."
)
```

**验证方法（Sub-Agent返回后）：**
```python
# 检查报告是否覆盖了全文
grep -c "行\|全部\|完整" 输出报告.md
# 如果报告明显偏短（如84k字原文只产出30行摘要）→ 未逐字逐句 → 重新派发
```

**Sub-Agent内容分析任务检查清单：**
- [ ] goal中是否明确写了"逐字逐句精读"或"读完全部N行"？
- [ ] 原文行数（如7510行）是否在goal中明确标出？
- [ ] 是否使用了"不要跳"、"不要跳过任何行"等强调措辞？
- [ ] 返回后是否验证了报告深度（行数/章节数与原文对比）？

### 陷阱⑨：大段内容插入Markdown文档不能用patch（2026-07-02校准）

**现象：** 需要向已有Markdown文档中插入数百行新内容时，用 `patch(old_string=..., new_string=...)` 导致失败——要么old_string不唯一（匹配到多处），要么new_string中混入了shell命令语法（如`$(cat file)`不被展开）。

**正确做法：**
```python
# ✅ 用 execute_code + write_file 做三大段操作：

from hermes_tools import read_file, write_file

# Step 1 — 读入原文件
original = read_file(path="/path/to/file.md")["content"]

# Step 2 — 找到插入点（精确匹配一个唯一标记）
marker = "## 需要插入的位置标题"
if marker in original:
    pos = original.find(marker)
    before = original[:pos]
    after = original[pos:]
    new_content = before + NEW_SECTION_CONTENT + "\n\n" + after
    
    # Step 3 — 写回
    write_file(path="/path/to/file.md", content=new_content)
else:
    print("ERROR: marker not found")
```

**关键区别（patch vs execute_code+write_file）：**
| 维度 | patch | execute_code + write_file |
|:----|:------|:-------------------------|
| 适合场景 | 小改动（几行内） | 大段插入（数百行） |
| 匹配策略 | 模糊匹配 | 精确字符串定位 |
| 文件大小 | 适合10KB以下 | 适合任意大小 |
| 回滚 | 不支持 | 通过git checkout恢复 |

**大文档操作通用流程：**
```
Step 1 — git commit 当前状态（确保可回滚）
Step 2 — 用 execute_code 做读→改→写三步
Step 3 — grep验证结构（grep -n "^## " 检查章节标题）
Step 4 — wc -l 检查行数是否合理
Step 5 — 如出错 → git checkout 恢复
```

**现象：** Sub-Agent 返回正确结果后，我在汇总给用户的飞书消息中写错了关键数据——把31.2分说成"十几分"，把"从弱50分"说成"身弱十几分"。用户看到错误数据直接质疑全盘。

**根因：** 汇总时凭记忆写数字，未逐条核对Sub-Agent返回的原始数据。

**解法/强制流程：**
```
Step 1 — 收到Sub-Agent结果后，提取所有关键数字（八字/分数/标签）写入临时checklist
Step 2 — 在发送给用户前，逐条比对 checklist 与 Sub-Agent 返回的原始数据
Step 3 — 特别检查：身强弱分数 ≠ 财星分数（容易混淆）
Step 4 — 特别检查：从弱格 ≠ 身弱（是完全不同的框架）
Step 5 — 确认无误后再发出消息

核验命令（发消息前必做）：
  grep -E "身强弱|财星|从弱|八字" /path/to/subagent/output
  # 逐字核对数字和标签
```

**验证清单（发消息前自检）：**
- [ ] 每人的八字与引擎输出一致？
- [ ] 身强弱分数/标签与引擎输出一致？
- [ ] 财星分数与引擎输出一致？
- [ ] 文昌结论与引擎/老板决定一致？
- [ ] 从弱格未写成"身弱"？
- [ ] 数字单位正确（分/岁/年）？

**每次批量子任务完成后，在合并结果前执行以下检查：**

```
□ 每个 Sub-Agent 写入了哪些文件？路径是否正确？
□ 所有涉及的文件是否都已 git add？
□ 多个 Sub-Agent 是否修改了同一个文件？有无冲突？
□ 是否有知识库也需要同步更新？
□ git status 是否干净？有无未预期的脏文件？
```

## ⛓️ Sub-Agent 依赖与链接

当多个Sub-Agent需要协作时，用 `parents` 参数控制执行顺序：

### 并行模式（独立任务同时派发）

```python
from hermes_tools import delegate_task

# 3个独立任务并行跑
results = delegate_task(tasks=[
    {
        "goal": "🎯 任务A",
        "context": "四要素...",
        "toolsets": ['terminal', 'file']
    },
    {
        "goal": "🎯 任务B", 
        "context": "四要素...",
        "toolsets": ['terminal', 'file']
    },
    {
        "goal": "🎯 任务C",
        "context": "四要素...",
        "toolsets": ['terminal', 'file']
    },
])
```

### 串行模式（有依赖关系）

先派依赖任务，用返回结果做后续任务的context：

```python
# Step 1: 先做依赖任务
r1 = delegate_task(goal="🎯 基础任务", context="...", toolsets=['terminal','file'])

# Step 2: 基于结果做后续任务
r2 = delegate_task(goal="🎯 后续任务", 
    context=f"""
    前置任务结果：{r1}
    
    🎯 目标：基于上述结果继续...
    ...
    """,
    toolsets=['terminal','file'])
```

### Maker/Checker 分离模式

```python
# Step 1: Maker干活
maker = delegate_task(goal="🎯 实现功能X", context="...", toolsets=['terminal','file'])

# Step 2: Checker审核（独立Agent，对抗性审查）
checker = delegate_task(
    goal="🎯 对抗性审查功能X的代码质量",
    context=f"""
    你是一个对抗性审查员。审查以下实现的代码质量。
    
    Maker输出摘要：{maker}
    
    五轴审查：正确性/可读性/架构/安全/性能
    
    STATUS: PASS 或 REJECT（附具体证据）
    """,
    toolsets=['terminal', 'file']
)

# Step 3: 如REJECT，循环修复（最多3次）
if 'REJECT' in str(checker):
    # 派新的Maker修复
    delegate_task(goal="🎯 修复Checker指出的问题", context=f"Checker拒绝原因：{checker}", ...)
```
