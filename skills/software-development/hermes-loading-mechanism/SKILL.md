---
name: hermes-loading-mechanism
description: 🔥 Hermes加载链源码确认版（prompt_builder.py L1955）。系统级(SOUL.md自动加载)+项目级(or链找HERMES.md→AGENTS.md→CLAUDE.md→.cursorrules)。bazi项目迁入profile/projects/bazi-platform/。skills在profile根目录(无symlink)。HERMES.md在profile根目录。
category: software-development
tags: [hermes, loading, or-chain, hermes-md, soul-md]
---

# Hermes 加载机制 · 源码确认版

> 2026-07-06 被老板连续纠正4轮后现固。

## 两条独立线

### 线A：系统级（无条件自动加载）

| 文件 | 位置 | 内容 |
|:-----|:-----|:------|
| **SOUL.md** | `~/.hermes/profiles/jinjian-zhenren/SOUL.md` | 角色/原则/系统铁律（不依赖记忆/零自创/加载链） |
| **USER.md** | `~/.hermes/profiles/jinjian-zhenren/memories/USER.md` | 老板画像/原则/风格/6大教训 |
| **MEMORY.md** | `~/.hermes/profiles/jinjian-zhenren/memories/` | 持久记忆（自动注入） |

### 线B：项目级（or链——只加载1个）

```python
project_context = (
    _load_hermes_md(cwd_path, ...)   # .hermes.md / HERMES.md, 递归向上到git root
    or _load_agents_md(cwd_path, ...) # AGENTS.md, 只在CWD
    or _load_claude_md(cwd_path, ...)  # CLAUDE.md
    or _load_cursorrules(cwd_path, ...) # .cursorrules
)
```

**找到第一个就停，后面的根本不进。不叠加载。**

## HERMES.md 分布（2026-07-06最终版）

| 位置 | 谁维护 | 在什么上下文中加载 |
|:-----|:-------|:-----------------|
| `~/.hermes/profiles/jinjian-zhenren/HERMES.md` | 金鉴真人 | bazi项目编码/分析时（profile根目录or链命中） |
| `weiwuji-knowledge-base/07-国学哲学/八字命格/HERMES.md` | 金鉴真人 | 知识库写报告时（or链递归向上找到git root命中） |
| `weiwuji-knowledge-base/HERMES.md` | **金久（别碰）** | 知识库全局规则（结构/分工/沉淀流程/格式规范） |

## 最终物理结构（2026-07-06）

```
~/.hermes/profiles/jinjian-zhenren/     ← 金鉴真人工作环境
├── SOUL.md                               ← 系统级：身份/原则/分工/反模式/3条系统铁律
├── HERMES.md                             ← 项目级SOP（or链第1优先级）
├── config.yaml                           ← Hermes配置（含API密钥，gitignore排除）
├── projects/bazi-platform/               ← bazi代码（engine/api/frontend/scripts/）
│   └── .git/                             ← GitHub: corinwe/jinjian-bazi
├── skills/                               ← 实际技能文件（无symlink！）
├── memories/USER.md                      ← 老板画像
└── .gitignore                            ← 只追踪bazi项目文件
```

## 历史错误一览（禁止重犯）

1. **造BOOTSTRAP.md** — Hermes已自动加载，重复造轮子
2. **造preflight.sh** — 手动检查已自动的文件
3. **SOUL.md放bazi-platform/** — 放profile根目录才生效
4. **bazi铁律放SOUL.md** — SOUL.md=系统级，HERMES.md=项目级
5. **删知识库AGENTS.md** — 越界了，只动bazi-platform/ + 07-国学哲学/八字命格/
6. **恢复旧AGENTS.md** — 覆盖了老板已有的HERMES.md
7. **bazi代码直接dump进profile根目录** — rsync后engine/api/frontend/等散在profile根目录，git无法区分bazi文件和Hermes系统文件。正确做法：放projects/bazi-platform/下的子目录。
8. **skills/作为symlink** — skill_manage无法写入。正确做法：skills/直接放在profile根目录（实际文件）。
