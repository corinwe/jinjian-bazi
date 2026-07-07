---
name: maker-checker-workflow
description: >-
  Maker/Checker分离工作流 — 写代码的Agent和检查的Agent永远分开。
  核心信条：同一个Agent不能既当球员又当裁判。实现者(Maker)产出的东西必须由独立的验证者(Checker)审查，
  审查不通过就循环修复，直到Checker APPROVED。
  这是 Loop Engineering 最重要的架构决策。
version: 1.0.0
author: 元宝
license: MIT
metadata:
  hermes:
    tags: [maker-checker, review, quality, loop-engineering, delegation]
    related_skills: [subagent-driven-development, writing-plans, test-driven-development, termination-condition, family-ai-assistant-architecture]
references:
  - references/大运修正Checker清单.md — 八字报告大运修正场景专用Checker验证清单（2026-07-01立报告3轮修复教训）
  - references/学习循环_Checkers检查清单.md — 学习循环（新知识→skill更新→报告更新）Checker验证清单（2026-07-02 09号视频学习循环实战教训）
---

# Maker/Checker 工作流

## 核心原则

> **写代码的Agent天然倾向于认为自己写的代码是对的。**
> 独立的Checker Agent用不同的视角、独立的指令来验证结果，才能真正发现问题。

**永远分离 Maker 和 Checker。** 这不是可选的——这是 Loop Engineering 最重要的架构决策。

## 何时使用

- **任何涉及代码/内容创建的delegate_task**
- 修复bug、添加功能、重构代码
- AI评估/分析报告的生成
- **不需要**使用：纯查询/只读操作（数据查询、状态检查）

## 工作流总览

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Maker Agent │────▶│ Checker Agent │────▶│   APPROVED?  │
│  (实现)      │     │  (验证)       │     │              │
└─────────────┘     └──────────────┘     └──────┬───────┘
       ▲                                        │
       │               ❌ REJECT                 │
       └─────────────────────────────────────────┘
                                                │ ✅ PASS
                                                ▼
                                        任务完成
```

## 第一步：定义终止条件（Termination Condition）

**在派发任何Agent之前**，先定义可测量的"完成"标准。

```python
# 好：可验证
"Success condition: run 'pnpm test test/auth/login.spec.ts' 5 times consecutively with zero failures"

# 差：不可验证
"Fix the auth bug"
```

关于终止条件的完整指南，参见 `termination-condition` 技能。

## 第二步：派发 Maker Agent

Maker Agent 是"实现者"——负责写代码、创建内容、实现功能。

```python
delegate_task(
    goal="Implement: add password strength validation to User model",
    context="""
    TASK FROM PLAN:
    - Modify: src/models/user.py — add validate_password_strength() method
    - Create: tests/models/test_password.py — test cases
    - Requirements:
      1. Minimum 8 characters
      2. At least one uppercase letter
      3. At least one digit
      4. Return (is_valid: bool, message: str)

    TERMINATION CONDITION:
    Success = 'pnpm test tests/models/test_password.py' passes all tests with 0 failures.

    IMPLEMENTATION INSTRUCTIONS:
    1. Write tests FIRST (TDD)
    2. Verify tests fail before implementation
    3. Write minimal implementation
    4. Verify tests pass
    5. Run full test suite to check for regressions

    PROJECT CONTEXT:
    - Python 3.11, FastAPI app
    - Tests use pytest
    - Model files in src/models/
    """,
    toolsets=['terminal', 'file']
)
```

### Maker Agent 工作指南

| 步骤 | 动作 | 验证 |
|------|------|------|
| 1 | 写测试（先红） | 运行测试 → 预期 FAIL |
| 2 | 写最小实现 | 只做刚好够让测试通过的程度 |
| 3 | 运行测试（变绿） | 运行测试 → 预期 PASS |
| 4 | 回归检查 | 运行完整测试套件 → 无回归 |
| 5 | 提交 | `git add . && git commit -m "type: description"` |

## 第三步：派发 Checker Agent

Checker Agent 是"验证者"——对抗性审查 Maker 的输出。

**关键：** Checker 和 Maker 不能是同一个会话/上下文。必须用独立的 `delegate_task`，用独立的指令。

```python
delegate_task(
    goal="Adversarially review the password validation implementation against spec",
    context="""
    ORIGINAL TASK SPEC:
    - Modify: src/models/user.py — add validate_password_strength() method
    - Requirements:
      1. Minimum 8 characters
      2. At least one uppercase letter
      3. At least one digit
      4. Return (is_valid: bool, message: str)

    CHECKLIST:
    - [ ] All 4 requirements from spec are implemented?
    - [ ] Return type matches (bool, str)?
    - [ ] Edge cases handled (None input, empty string, unicode)?
    - [ ] Tests cover: valid cases, each failure case, edge cases?
    - [ ] No scope creep (nothing extra added)?
    - [ ] File paths match spec?
    - [ ] No obvious bugs or security issues?
    - [ ] Existing tests still pass? (run tests)

    OUTPUT FORMAT (strict):
    STATUS: PASS or REJECT
    
    If REJECT, provide:
    1. Failure: [specific issue]
       Evidence: [file:line or test output]
    
    If PASS:
    STATUS: PASS
    """,
    toolsets=['terminal', 'file']
)
```

### Checker Agent 审查维度

| 维度 | 检查内容 | 严重程度 |
|------|---------|---------|
| **规范符合** | 是否实现了所有需求？ | Critical |
| **范围蔓延** | 是否做了没要求的事？ | Critical |
| **测试覆盖** | 测试是否覆盖了正向+负向+边界？ | Important |
| **代码质量** | 是否有明显bug、安全问题？ | Important |
| **项目一致** | 是否遵循项目的命名/结构/风格？ | Minor |

## 第四步：循环修复

如果 Checker REJECT，循环：

```
┌─────────┐    ❌ REJECT     ┌──────────┐
│  Maker  │◀────────────────│  Checker  │
│  修复    │                 │  再验证    │
└─────────┘                 └──────────┘
      │                         │
      │     ✅ PASS             │
      ▼                         ▼
  任务完成                   记录存档
```

```python
# 如果 Checker 拒绝，派新的 Maker Agent 修复
delegate_task(
    goal="Fix: password validation — missing uppercase check",
    context="""
    CHECKER REJECTION:
    Failure: Missing requirement #2 (at least one uppercase letter)
    Evidence: src/models/user.py:42 — no regex check for [A-Z]
    Tests: tests/models/test_password.py — no test case for uppercase

    ORIGINAL TASK SPEC (same as before)
    Modified file: src/models/user.py
    """,
    toolsets=['terminal', 'file']
)

# 然后重新派发 Checker 验证修复
# （重复第三步，直到 PASS）
```

**循环规则：**
- 每一步必须验证（不能跳过Checker直接进入下一步）
- 最多循环 **3次**，超过后上报人工处理
- 每次循环记录拒绝原因到 STATE.md

## 可选：使用不同模型作为 Checker

当任务重要性高或风险大时，让 Checker 使用更强的模型：

```python
# Maker 用 fast/cheap 模型
delegate_task(goal="Implement feature X", ...)

# Checker 用更强的模型做对抗性审查
delegate_task(goal="Review implementation of feature X", context="""
    ...
    Note: You are a STRONGER model acting as adversarial reviewer.
    Be more strict than usual. Assume the implementer made subtle mistakes.
""", ...)
```

注意：当前配置下所有 Agent 使用同一模型（DeepSeek V4 Flash），
但可以通过 context 中的指令差异实现 Maker/Checker 角色分离：
- **Maker**: "Write clean, focused code. Be pragmatic."
- **Checker**: "Be adversarial. Assume there are bugs. Prove they exist or that the code is clean."

## 实际完整示例

```python
from hermes_tools import delegate_task

# Step 1: Maker
maker_result = delegate_task(
    goal="Add rate limiting to /api/login endpoint",
    context="""
    SPEC:
    - File: src/routes/auth.py
    - Add rate limiting: max 5 attempts per IP per 15 minutes
    - Use flask-limiter library (already in requirements)
    - Tests in tests/routes/test_auth.py
    
    TERMINATION: pytest tests/routes/test_auth.py -v — all pass
    """,
    toolsets=['terminal', 'file']
)

# Step 2: Checker
checker_result = delegate_task(
    goal="Review rate limiting implementation",
    context="""
    CHECK:
    - [ ] Rate limit: 5/15min per IP implemented?
    - [ ] Error response returned on limit exceeded?
    - [ ] Tests cover: normal case, limit exceeded, reset after time?
    - [ ] No side effects on other endpoints?
    - [ ] Existing tests still pass?
    
    OUTPUT: PASS or REJECT with specific failures
    """,
    toolsets=['terminal', 'file']
)

# Step 3: Loop if needed
if "REJECT" in checker_result:
    # Fix and re-review
    pass
```

## Combine with Parallel Tasks

当多个独立任务可以并行时，使用 batch mode：

```python
# 并行派发3个Maker
delegate_task(tasks=[
    {"goal": "Implement feature A", "context": "...", "toolsets": ['terminal', 'file']},
    {"goal": "Implement feature B", "context": "...", "toolsets": ['terminal', 'file']},
    {"goal": "Implement feature C", "context": "...", "toolsets": ['terminal', 'file']},
])

# 全部Maker完成后，逐项做Checker
for result in results:
    delegate_task(goal=f"Review {result.task}", context="...", toolsets=['terminal', 'file'])
```

## Checker 通用模板

```markdown
你是一个对抗性审查员。你的工作不是认可，而是质疑。

收到一个 diff/实现后，执行以下检查：

1. **规范检查**：逐条核对原始需求，是否全部实现？有没有做不需要的事？
2. **测试验证**：运行测试套件，确认全部通过且有足够覆盖。
3. **质量审查**：检查错误处理、边界条件、安全性。
4. **一致性**：实现是否符合项目的现有风格和约定。

所有检查通过 → 输出 `STATUS: PASS`
任何检查失败 → 输出 `STATUS: REJECT` + 具体的失败证据
```

## Maker 通用模板

```markdown
你是一个实干家。你的工作是精确实现需求，不多不少。

工作方式：
1. 先写测试，验证失败
2. 写最小实现，验证通过
3. 运行完整测试，确保无回归
4. 提交

约束：
- 只做需求要求的事（YAGNI）
- 遵循项目现有风格（不引入新抽象除非必要）
- 写清晰的代码（不是聪明的代码）
- 所有变更必须有测试覆盖
```

## 应用场景：八字报告大运修正（GOLDEN-CLIENT版）

当修正八字报告的大运/起运数据时，Maker/Checker流程有特殊的陷阱。

### 关键发现

Maker修正大运表后，**流年分析文本中的大运引用会深层嵌入**，常见遗漏模式：

| 遗漏模式 | 示例 | 根因 |
|---------|------|------|
| 流年表大运列改但文本没改 | 2035年表写"庚寅"但文本写"辛卯大运" | Maker只改了表 |
| 合冲组合名不变 | "三卯"仍用旧大运地支 | 大运变了，组合名要更新 |
| 时间表述不改 | "X运将尽"、"交运年" | 还在用旧大运名 |
| 补库步骤年龄不改 | "约30岁时辛卯大运末期" | 起运年龄变了 |
| 发财窗口引用不改 | "48-57岁戊子"未改年份 | 窗口年份随起运偏移 |

### Checker 验证清单（5层级）

详见 `references/大运修正Checker清单.md`，涵盖：

1. **大运表验证** — 起运年龄÷干支÷年份÷年龄连贯性
2. **关键发财窗口验证** — 窗口年龄/年份与大运表一致
3. **流年分析文本验证** — 逐行扫描"大运"关键词（最易遗漏）
4. **破财预警表验证** — 大运列+分析文本双重检查
5. **补财库步骤验证** — "某岁某大运"表述同步更新

### 循环轮次上限

- 立报告曾需要 **3轮Maker/Checker循环** 才全部清除
- 每轮发现的问题类型不同：第1轮→表级，第2轮→文本级，第3轮→深层分析级
- 超过3轮上报人工

## 第五步（特殊）：学习循环 — 新知识的自动化 Maker/Checker

> **这不是代码循环，而是知识循环。** 当输入是「新规则/新知识」而非「代码变更」时，同样的 Maker/Checker 分离原则依然适用。

### 适用场景

| 场景 | Maker | Checker |
|:----|:------|:--------|
| 收到新规则（截图/视频/素材） | Loop Engineering 脚本自动检测变更 | 人工（或脚本）验证完整性 |
| 需要更新多个报告 | 脚本自动扫描受影响报告 | 确认所有受影响的报告都已覆盖 |
| skill修正 | 脚本生成patch指令 | 运行验证确认无遗漏 |

### 金鉴真人·财富体系学习循环（实战案例）

```
输入: 09号视频9张截图 + 素材11行349~433
  |
  v
Phase 1 — LEARN (Maker = loop-engineering-wealth.py)
  ① 自动加载现有skill
  ② 精读新素材，提取规则
  ③ 对比现有skill，标记新增/修正/删除
  ④ 生成结构化变更清单
  -> 输出: 哪些规则已存在 / 哪些是新规则

Phase 2 — VERIFY (Checker = agent review)
  ① 检查变更清单完整性（无占位符）
  ② 检查规则内容非空
  ③ 扫描所有受影响报告
  -> 输出: PASS / REJECT

Phase 3 — APPLY (修复循环)
  ① 更新skill (Patch)
  ② 批量更新受影响报告
  ③ 推库
  -> 输出: 变更已应用 + git push
```

### 学习循环的 Checker 清单

```markdown
检查清单：
□ 变更清单中所有规则都已填充内容（无"待填充"占位符）
□ 每条规则标注了来源（素材行号/视频时间戳/实战校准）
□ 所有受影响的报告已被列出
□ 每个受影响报告都确认已更新
□ 更新后运行验证确认无数据不一致
□ 推库完成（git push已执行）
```

### 代码循环 vs 学习循环

| 维度 | 代码循环 | 学习循环 |
|:----|:--------|:--------|
| 输入 | Bug报告/Feature需求 | 新知识（截图/素材/视频/口述） |
| Maker | 实现Agent（写代码） | 循环引擎脚本（自动检测变更） |
| Checker | 审核Agent（跑测试+审查） | 整合Agent（验证完整性+交叉检查） |
| 循环内容 | 代码变更+测试 | skill更新+报告更新 |
| 失败模式 | 测试不过 | 遗漏规则 / 受影响的报告没更新 |

### 陷阱（本session实战教训）

| 陷阱 | 后果 | 解决方法 |
|:----|:-----|:---------|
| 手动执行学习六步而非自动循环 | 易漏步骤、不可重复 | 先跑循环引擎再动手 |
| 只更新了skill没更新所有报告 | 报告数据不一致 | 脚本自动扫描 affected_reports |
| 认为"已存在"就跳过 | 可能忽略了需修正的部分 | 先跑 cycle 再做最终判断 |

## 反模式（禁止）

| 反模式 | 为什么 | 正确做法 |
|--------|--------|---------|
| 让Maker自我审查 | 写代码的人天然看不到自己的bug | 永远用独立Checker |
| Maker和Checker用相同指令 | Checker会重复Maker的逻辑 | 给Checker对抗性指令 |
| 跳过Checker循环 | "看起来没问题"是最危险的 | 必须验证通过才继续 |
| 同一个Agent做Maker+Checker | 认知偏差不可消除 | 用delegate_task分离角色 |
| Checker只检查而不运行测试 | 静态分析不够 | 必须运行测试验证 |
| **文档流程无强制机制** | **写了BOOTSTRAP.md但没实际加载=纸上谈兵。文档只是陈述，不是约束。** | **每个流程必须有自动执行脚本或iron rule确保执行；没有强制机制的流程等于没写** |
| 超过3次循环不升级 | 无限循环浪费token | 3次后上报人工 |
