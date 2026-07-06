---
name: bazi-platform-harness
description: 🚨 八字排盘平台·工程化落地总调度Harness。v7.5新增HERMES.md取代AGENTS.md（or链最高优先级），SOUL.md只保留系统级铁律，bazi项目级全进HERMES.md。
category: software-development
tags: [八字, 排盘, 工程化, 校验, 流水线]
---

# 🏗️ 八字排盘平台 · 工程化落地总调度 Harness v7.5

> 金鉴真人的工程化身份：Orchestrator（拆任务+验结果）
> Sub-Agent分工、身份定义 → **SOUL.md（profile根目录·自动加载，不要手动读）**
> 老板画像、原则 → **USER.md（memories/USER.md·自动注入，不要手动读）**
> **本文件(HERMES.md)** = 项目级约束+SOP（or链最高优先级）
> **references/SOUL.md和references/USER.md** = skill内参考副本，非主要加载源

---

## ⚠️ 核心教训：Hermes加载机制是or链，不是叠加载

> 2026-07-06 我造了BOOTSTRAP.md + preflight.sh手动加载流程 → 被老板连续纠正4次
> 根源：我在设计机制前没先理解现有机制。

### 正确加载链（源码验证·prompt_builder.py L1955）

**两条独立线：**

**线A：系统级（独立加载，无条件）**
```
SOUL.md    ← profile根目录 · 自动加载 → 角色/原则/系统铁律
USER.md    ← memories/USER.md · 自动注入 → 老板画像/风格/教训
MEMORY.md  ← memories/ · 自动注入 → 持久记忆
```

**线B：项目级（or链——只加载1个，找到就停）**
```python
project_context = (
    _load_hermes_md(cwd_path, ...)   # .hermes.md / HERMES.md, 递归往上到git root
    or _load_agents_md(cwd_path, ...) # AGENTS.md, 只在CWD（不往上走！）
    or _load_claude_md(cwd_path, ...)  # CLAUDE.md
    or _load_cursorrules(cwd_path, ...) # .cursorrules
)
```

### ⚠️ 常见错误（禁止）

| 错误 | 为什么错 | 正确做法 |
|:-----|:---------|:---------|
| 造手动加载流程(BOOTSTRAP.md/preflight.sh) | Hermes已自动加载，重复造轮子 | **信任Hermes**，不手动读已自动加载的文件 |
| SOUL.md放项目目录 | 不会自动加载，放profile根目录才生效 | SOUL.md在`~/.hermes/profiles/jinjian-zhenren/` |
| AGENTS.md放项目根目录 | or链第2优先级，被.hermes.md挡路 | **用HERMES.md**（第1优先级） |
| bazi铁律放SOUL.md | SOUL.md是系统级，跨项目通用 | SOUL.md=系统身份+framing；HERMES.md=项目级约束+SOP |
| 叠加载想象 | 以为所有文件一起上 | 系统级独立 + 项目级or链，**不叠** |

---

## 🔥 物理铁律速查

| 铁律 | 内容 | 来源 |
|:----|:-----|:------|
| ① 排盘门禁 | `bash /root/bazi-platform/scripts/bazi-must-run-engine.sh` | 2026-06-29 |
| ② 知识库路径 | `/root/weiwuji-knowledge-base/...` | 固化 |
| ③ 不依赖记忆 | 所有路径/规则从文件读取 | 固化 |
| ④ 报告格式 | 21§标准，§1 25字段四段式 | bazi-report-template |
| ⑤ 大运校验 | 结束年-开始年+1=10 | 2026-07-01 |
| ⑥ 节气自动计算 | 禁用硬编码qi_yun_days | 2026-07-05 |
| ⑦ int截断检查 | 起运年龄全程浮点数 | 2026-07-05 |
| ⑧ 全量审计流程 | 引擎→脚本→测试→大运→报告 | 2026-07-05 |
| ⑨ generate_deep_report | 用bazi_str解析代替空paipan | 2026-07-05 |
| ⑩ 全链路字段名校验 | generate_deep_report字段名一致性 | 2026-07-05 |
| ⑪ 版本对齐 | engine/backend/api版本号一致 | 2026-07-05 |
| ⑫ 旧版归档 | 归档后须运行引擎抓ImportError | 2026-07-05 |
| **⑲ 排盘源头校验** | **bazi-must-run-engine.sh自动调canggan-parse.py标易混淆⚠️** | **2026-07-06** |
| **⑳ 四柱分析校验** | **pillar-verify.py 5关校验，结论发布前强制跑** | **2026-07-06** |
| **㉑ 加载机制** | **SOUL.md(系统级)+HERMES.md(项目级)已分离。HERMES.md取代AGENTS.md（or链最高优先级）** | **2026-07-06** |

---

## 📐 验证流水线

| 命令 | 说明 | 时机 |
|:-----|:------|:------|
| `python3 /root/bazi-platform/scripts/canggan-parse.py /tmp/bazi_last_result.json` | 排盘后自动调：藏干十神解析 + 易混淆标注 | 每次排盘后 |
| `python3 /root/bazi-platform/scripts/pillar-verify.py` | 四柱分析前跑：5关校验（五鼠遁/十神/结构/冲刑/最优性） | 分析发布前 |
| `python3 /root/bazi-platform/scripts/verify_report.py` | 报告发布前跑：7项格式校验 | 报告发布前 |
| `cd /root/bazi-platform/engine/tests && python3 validate_all.py` | 引擎全量验证 | 代码修改后 |

---

## 📂 本技能包含的文件

| 文件 | 说明 |
|:-----|:------|
| `references/SOUL.md` | 🔥 金鉴真人身份参考副本（实际自动加载版在profile根目录） |
| `references/USER.md` | 🔥 老板用户画像参考副本（实际自动注入版在memories/USER.md） |
| `references/engineering-checklists.md` | 工程检查清单 |
| `references/project-config.md` | 项目配置（含验证命令、铁律、测试速查） |
| `references/physical-pipeline-20260706.md` | 物理化流水线 |
| `references/full-chain-verification.md` | 全链路验证 |
| ...（另含19个参考文件） |

---

## ⚠️ 加载本技能时必须做的

1. `skill_view('bazi-platform-harness', 'references/project-config.md')` → 加载完整配置
2. **不要手动加载SOUL.md/USER.md** —— Hermes已在系统级自动加载
3. 排盘前: 确认`/tmp/bazi_last_result.json`已更新（由bazi-must-run-engine.sh生成）
4. 发布报告前: 跑`verify_report.py`确认格式通过
5. 四柱分析结论发布前: 跑`pillar-verify.py`确认5关全过
