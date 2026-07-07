---
name: hermes-context-loading
description: 🏗️ Hermes Agent 上下文加载链——SOUL.md(系统级独立)+项目级or链(.hermes.md→AGENTS.md→CLAUDE.md→.cursorrules)。每session自动注入，不要手动补读。含源码验证的关键逻辑。
category: autonomous-ai-agents
tags: [hermes, loading, context, SOUL, AGENTS, profile, prompt-builder, or-chain]
---

# Hermes Context Loading · 上下文加载链

> **来源**：`prompt_builder.py` 逐行验证（含L1955 `or`链）
> **问题驱动**：本Agent误以为需要「手动加载」SOUL.md/USER.md/AGENTS.md，造了一套冗余的BOOTSTRAP.md+preflight.sh流程。用户指出后纠正。

---

## 🧠 核心认知

Hermes的上下文加载分为**两条独立线**，不是一条叠加载管道：

```
线A — 系统级（独立加载，无条件）：
  ① 系统基础提示词 ← Hermes内置
  ② config.yaml ← profile根目录
  ③ SOUL.md ← profile根目录（自动加载 ✅）
  ④ USER.md ← memories/USER.md（自动注入）
  ⑤ MEMORY.md ← memories/（自动注入）

线B — 项目级上下文（or链——只加载1个）：
  优先① .hermes.md / HERMES.md  ← 递归向上到git root
  优先② AGENTS.md                ← 只在CWD（不往上走！）
  兜底③ CLAUDE.md / .cursorrules ← Claude兼容
```

**关键区别**：
- 线A是**无条件、独立、全部加载**的
- 线B是**互斥`or`链**——找到第一个就停，后面的根本不进
- 不要手动去`cat`或`skill_view`自动已经加载的文件

---

## 🔬 源码验证

`prompt_builder.py` L1955 实际逻辑：

```python
project_context = (
    _load_hermes_md(cwd_path, context_length)   # .hermes.md / HERMES.md, 递归向上
    or _load_agents_md(cwd_path, context_length) # AGENTS.md, 只在CWD
    or _load_claude_md(cwd_path, context_length) # CLAUDE.md
    or _load_cursorrules(cwd_path, context_length) # .cursorrules
)
```

`or`链含义：
- 若`_load_hermes_md`返回非None → 直接赋值，**跳过后续所有**
- 若返回None → 尝试`_load_agents_md`
- 以此类推

---

## ⚠️ 关键坑

| 坑 | 后果 | 解决方案 |
|:---|:-----|:---------|
| ❌ 手动cat/read SOUL.md/USER.md | 重复工作，Hermes已自动注入 | **信任自动加载** |
| ❌ 认为AGENTS.md「一定加载」 | 如果.hermes.md存在，AGENTS.md永不被碰 | 检查项目根有无.hermes.md |
| ❌ 把SOUL.md放在工作目录下 | 系统级不加载（只在profile根目录读） | SOUL.md放profile根目录 |
| ❌ 复制BOOTSTRAP.md手动流程 | 造Hermes自动做的轮子 | 不需要 |
| ❌ AGENTS.md放在子目录 | 只在CWD找，不递归向上 | AGENTS.md放项目根目录 |

---

## ✅ 正确做法

### 每次session开始

1. **信任系统级已自动加载**：SOUL.md + USER.md + MEMORY.md 已经在上下文中
2. **信任项目级已自动加载**：如果在工作目录下，AGENTS.md（或.hermes.md）已在上下文中
3. **按需加载Skills**：`skill_view('bazi-{topic}-analysis')` 按任务选择
4. **按需加载配置**：`skill_view('bazi-platform-harness','references/project-config.md')`

### 不要做的事

- ❌ 不要`cat SOUL.md`「确认加载」
- ❌ 不要造preflight检查脚本
- ❌ 不要写BOOTSTRAP.md指导手动加载
- ❌ 不要以为AGENTS.md叠加载在SOUL.md之上
- ❌ 不要在多处副本中同步SOUL.md/USER.md（它们有唯一的自动加载位置）

---

## 🗺 文件位置速查

| 文件 | 自动加载位置 | 说明 |
|:-----|:------------|:------|
| SOUL.md | `~/.hermes/profiles/<name>/SOUL.md` | 系统级，自动 |
| USER.md | `~/.hermes/profiles/<name>/memories/USER.md` | 自动注入 |
| MEMORY.md | `~/.hermes/profiles/<name>/memories/MEMORY.md` | 自动注入 |
| .hermes.md | 任意git根目录 | 递归向上搜索 |
| HERMES.md | 任意git根目录 | 递归向上搜索 |
| AGENTS.md | 当前工作目录 | 只在CWD |

---

## 📝 版本

v1.0 · 2026-07-06 · 基于`prompt_builder.py` L1955源码验证
