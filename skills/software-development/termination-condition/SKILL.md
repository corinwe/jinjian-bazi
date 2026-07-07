---
name: termination-condition
description: >-
  形式化终止条件定义 — 每个任务必须有可测量的"完成"标准。
  核心信条：没有终止条件的Loop要么永远循环，要么过早停止。
  定义方式：用可脚本验证的条件表达"done"，让实现者(Agent)和验证者(Agent)都能判断什么时候该停下。
version: 1.0.0
author: 元宝
license: MIT
metadata:
  hermes:
    tags: [termination, condition, done, quality, loop-engineering]
    related_skills: [maker-checker-workflow, subagent-driven-development, writing-plans, test-driven-development]
---

# 终止条件（Termination Condition）

## 核心原则

> **没有终止条件的Loop不是Loop，是黑洞。**
> 它要么永远跑下去消耗Token，要么过早停止然后骗你说"做完了"。

一个任务如果没有清晰的终止条件，就不应该被派发。

## 终止条件的六种模式

### 1. 测试驱动模式

```python
# 所有测试通过
"Success condition: pytest tests/test_auth.py -v — all tests pass, 0 failures"
```

**适用于：** Bug修复、功能实现、重构

### 2. 编译器驱动模式

```python
# 类型检查零错误
"Success condition: pnpm typecheck — exit code 0, no errors"
```

**适用于：** TypeScript迁移、依赖升级

### 3. 运行时验证模式

```python
# API 返回预期结果
"Success condition: curl -s http://localhost:8000/api/v1/health | jq '.status == \"ok\"'"
```

**适用于：** 后端开发、API实现

### 4. 重复性验证模式

```python
# 消除flaky test — 连续运行N次全部通过
"Success condition: run 'pnpm test test/auth/login.spec.ts' 5 times consecutively with zero failures"
```

**适用于：** 修复flaky测试、竞态条件

### 5. 端到端验收模式

```python
# 浏览器验证
"Success condition: browser loads http://localhost:3000/login, fill form with valid credentials, click Submit, redirects to /dashboard with 200 status"
```

**适用于：** UI功能、前端实现

### 6. 数据验证模式

```python
# 数据库记录验证
"Success condition: SELECT COUNT(*) FROM admissions WHERE year=2026 returns >0 — 新数据已入库"
```

**适用于：** 数据采集、ETL

## 如何写出好的终止条件

### 模板

```
Success condition: [可脚本验证的命令/检查] — [预期结果的文字描述]
```

### 好坏对比

| ❌ 差 | ✅ 好 |
|-------|-------|
| "修复auth bug" | "Success: pytest tests/test_auth/login.py passes with 0 failures" |
| "优化性能" | "Success: curl /api/dashboard returns < 200ms for 10 consecutive requests" |
| "完善数据" | "Success: SELECT COUNT(*) FROM admissions WHERE year=2026 > 0 — 至少1条新记录入库" |
| "添加登录功能" | "Success: POST /api/login with valid creds returns 200 + JWT token. Invalid creds returns 401." |

### 好的终止条件要素

1. **可测量** — 用数字/布尔值表达，不用主观描述
2. **可脚本化** — 可以写成一行命令/查询来验证
3. **原子性** — 一个条件，不包含"并且/或者/然后"的多重条件
4. **可复现** — 任何人/机器执行相同的验证步骤得到相同结果

## 嵌入到任务中的写法

### 在delegate_task中使用

```python
delegate_task(
    goal="Fix session leak in test/auth/login.spec.ts",
    context="""
    ...
    TERMINATION CONDITION:
    Success = run 'pnpm test test/auth/login.spec.ts' 5 times consecutively
             with ZERO failures across all 5 runs.
    
    The task is NOT done until this condition is met.
    If you cannot achieve it after 3 attempts, report why.
    """,
    toolsets=['terminal', 'file']
)
```

### 在plan中使用

```markdown
### Task 1: Add rate limiting

**Objective:** Add rate limiting to /api/login endpoint

**Termination Condition:** 
```
Success = pytest tests/routes/test_auth.py -v — all tests pass
AND curl -X POST http://localhost:8000/api/login (5 times in 60s)
  → 6th call returns 429 Too Many Requests
```

**Files:**
- Modify: src/routes/auth.py
- Create: tests/routes/test_auth.py
```

## 嵌套条件（高级）

当任务包含多个子条件时，按优先级排序：

```python
"TERMINATION CONDITIONS (all must pass):
 [P0] 1. pytest tests/auth/ -v — all tests pass
 [P0] 2. curl /api/login returns 200 for valid credentials
 [P1] 3. curl /api/login returns 401 for invalid credentials
 [P2] 4. lint is clean (pnpm lint)
 
 P0 failure → TASK BLOCKED (report immediately)
 P1/P2 failure → REPORT but can proceed"
```

## 超时处理

每个终止条件都应配套超时策略：

```python
"TIMEOUT策略:
 - 最多尝试 3 次
 - 每次尝试间休息 10 秒
 - 3次后仍未达成 → 记录失败原因到 STATE.md → 上报人工"
```

## 与 Maker/Checker 的关系

终止条件是 Maker 和 Checker 判断"是否完成"的共同基准：

```
Maker: 完成任务后，对照终止条件自检
        ↓
Checker: 收到Maker输出后，对照终止条件验证
        ↓
        条件满足 → PASS ✨
        条件不满足 → REJECT 🔄 → Maker修复
```

**始终在 context 中显式传递终止条件**，不要假设Agent能推断出来。

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 用模糊描述代替可验证命令 | Agent不知道什么时候算"完成" | 写出具体的验证命令 |
| 忘记添加超时策略 | 卡住的任务无限消耗token | 设置"3次尝试后上报" |
| 终止条件和任务目标脱节 | 测试过了但功能是错的 | 终端条件必须直接验证用户需求 |
| 条件过于复杂 | Agent无法判断是否满足 | 拆成多个简单条件，按优先级排列 |
| 只检查正向不检查负向 | 功能正常工作但错误处理缺失 | 验证正向+负向+边界三种场景 |
