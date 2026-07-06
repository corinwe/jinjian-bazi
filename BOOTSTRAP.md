# ═══════════════════════════════════════════════
# 金鉴真人 · 任务启动引导（BOOTSTRAP.md）
# 每次执行任务前，必须按此顺序加载文件
# 不可跳过、不可颠倒顺序
# ═══════════════════════════════════════════════

## 🚨 铁则

**每次新任务开始前，第一步必须先跑：**
```bash
bash /root/bazi-platform/scripts/preflight.sh
```

如果任何一项显示 **缺失** → 必须先补读，再干活。

补读完后，按 §1 → §2 → §3 → §4 → §5 的顺序主动加载对应文件。
**禁止跳过任意一节。** 每节完成后才能进入下一节。

不跑 preflight = 直接跳过最关键的上下文加载 = 我不算合格工具。

---

## §1 — 加载身份设定（我是什么人）

### 命令
```bash
cat /root/bazi-platform/SOUL.md
# 或: skill_view('bazi-platform-harness', 'references/SOUL.md')
```

### 内容
| 板块 | 说明 |
|:-----|:------|
| 我的身份 | 金鉴真人：顶级八字命理实战派大师 |
| 核心原则 | 双层分离、Maker/Checker、计算型优先 |
| Sub-Agent分工 | 7种角色+派发流程 |
| 反模式 | 5种禁止行为 |
| 物理铁律 | ①排盘跑引擎 ②知识库路径 ③不依赖记忆 ④21§报告 ⑤⑥源头+分析双校验 |

### 检查点
```
□ 我知道我是谁
□ 我知道我的铁律
□ 我知道我的分工体系
```

---

## §2 — 加载老板画像（为谁做事）

### 命令
```bash
cat /root/bazi-platform/USER.md
# 或: skill_view('bazi-platform-harness', 'references/USER.md')
```

### 内容
| 板块 | 说明 |
|:-----|:------|
| 老板是谁 | 魏启令·金鉴真人创始人 |
| 核心原则 | 引擎定量>LLM定性、点面体系、内容级验证 |
| 沟通风格 | 直接简短、要数据不要客气 |
| 核心教训 | 6个重大错误历史 |

### 检查点
```
□ 我知道老板是谁
□ 我知道他的原则和风格
□ 我知道过去犯过的教训
```

---

## §3 — 加载项目配置（在哪干活）

### 命令
```bash
skill_view('bazi-platform-harness', 'references/project-config.md')
# 或: cat /root/bazi-platform/.hermes/config/credentials.md
```

### 内容
| 板块 | 说明 |
|:-----|:------|
| GitHub仓库 | 路径、PAT、远程 |
| 部署信息 | API地址、启动命令 |
| 核心路径 | 引擎、脚本、知识库、人物档案 |
| 物理铁律 | ①排盘 ②路径 ③不依赖记忆 ④21§ ⑤~⑨ |
| 测试命令速查 | validate_all.py、pillar-verify.py等 |
| 项目结构 | engine/api/frontend/scripts布局 |

### 检查点
```
□ 我知道bazi-platform路径
□ 我知道知识库路径
□ 我知道测试命令
□ 我知道排盘门禁命令
```

---

## §4 — 加载具体分析技能（用什么工具）

根据任务类型，至少加载对应的技能文件：

### 任务类型 → 技能矩阵

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
| **四柱反推** | `bazi-four-pillars-analysis` | `—` |
| **出报告** | `bazi-report-template` | 对应事象技能 |
| **校准/审计** | `bazi-calibration` | 对应模块技能 |
| **全量验证** | `bazi-validate-all` | `bazi-auto-verify` |

### 命令
```bash
skill_view('bazi-{topic}-analysis')
```

### 检查点
```
□ 我知道任务类型对应的技能
□ 我已经加载了对应技能文件
□ 双喜忌判断已查藏干表（canggan-parse.py已集成）
```

---

## §5 — 运行时校验（事后查错）

### 分析过程中，遇到以下情况必须执行对应校验：

| 场景 | 校验命令 | 说明 |
|:-----|:---------|:------|
| **排盘时** | 已自动集成到`bazi-must-run-engine.sh` | 自动输出藏干十神+易混淆标记 |
| **做四柱反推后** | `python3 /root/bazi-platform/scripts/pillar-verify.py` | 5关校验：五鼠遁→藏干→结构→冲刑→最优 |
| **修改引擎后** | `cd /root/bazi-platform/engine/tests && python3 validate_all.py` | 全量验证（320条） |
| **推库前** | pre-commit hook自动触发 | 身强弱/财星/十神名称/大运/喜忌/空亡7项 |

---

## 📋 快速检查清单

```
每次任务开始前，跑一遍这个清单：

§1 身份设定    □ SOUL.md 已加载
§2 老板画像    □ USER.md 已加载
§3 项目配置    □ project-config.md 已加载
§4 分析技能    □ 对应技能已加载（见任务→技能矩阵）
§5 运行时      □ 排盘源头已校验（canggan-parse.py自动）
                □ 分析结论已校验（pillar-verify.py）
```

---

**本文件版本：v1.0 · 2026-07-06**
**每次执行任务前必须加载本文件并逐条对照。**
