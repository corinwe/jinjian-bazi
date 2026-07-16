# ═══════════════════════════════════════════════
# HERMES.md — 金鉴真人·项目级操作规则
# ═══════════════════════════════════════════════

> **本文件版本：v3.0 · 2026-07-16**
> **职责：存放SOUL.md迁出的SOP/规则/流程 + 项目级铁律**
> **加载方式**：Hermes or链自动加载（CWD递归搜索HERMES.md）
> **生效范围**：金鉴真人profile + bazi-platform项目目录

---

## 一、铁律A~G（执行标准）

### 铁律A — 每次会话先跑 date
```bash
date  # 确认服务器时间，时区CST/UTC+8
```

### 铁律B — 排盘必须跑引擎，禁止手算
大运/身强弱/财星分数等所有量化数据，必须从引擎JSON提取。禁止凭经验手算。

### 铁律C — 写§前先skill_view加载对应技能
每写一个§前，先加载该§对应的理论技能，列出核心规则后逐一对比命主数据。

### 铁律D — 每§写完反向校验JSON
写过的内容中的数字/十神/分数，回到引擎JSON逐项确认一致。

### 铁律E — 交付前过五关
pillar-verify + 320门禁 + 内容校验，全绿才能交付。

### 铁律F — 大运数据逐行映射
大运表的每一行必须对应引擎da_yun_list中的一条记录，禁止合并一行写20年。

### 铁律G — 不引入原局不存在的字
报告中每个天干/地支必须能在原局/大运/流年中找到。

---

## 二、Sub-Agent 分工体系

| 角色 | 负责 | 守则 |
|:----|:-----|:-----|
| **引擎开发员** | Python规则引擎（36模块） | TDD先行，零幻觉 |
| **前端开发员** | HTML/CSS/JS前端 | 移动端优先，永不展示JSON |
| **API开发员** | FastAPI后端 | 契约优先，错误语义明确 |
| **测试验证员** | 单元/集成/E2E测试 | 320条门禁全覆盖 |
| **审核员** | Maker输出的对抗性审查 | 假设有bug |
| **命理分析师** | 八字推理分析 | 零自创断事逻辑 |
| **报告生成员** | 21§报告格式化输出 | 禁止通用占位符 |

## 三、任务派发流程

```
老板指令 → 拆任务 → 定终止条件 → 组四要素(目标+标准+格式+流程)
→ delegate_task派发 → 审核结果 → 不通过重派 → 通过合并推库
```

## 四、端到端八字排盘流程

```
Phase 0: 系统就绪（SOUL+USER+MEMORY+HERMES）
Phase 1: 加载技能（foundation→engine→report→harness）
Phase 2: 排盘+源头校验（bazi-must-run-engine.sh）
Phase 3: 引擎评分（pipeline_v5→21§JSON）
Phase 4: 分析+出报告（Maker/Checker循环）
Phase 5: 发布前校验（5关pillar-verify+320门禁）
Phase 6: 归档推库（知识库+profile双推）
```

## 五、物理拦截系统（pre_tool_call hooks）

> 以下规则由 `/root/.hermes/hooks/bazi-mandatory/precheck.py` 物理强制，不是靠自觉。

### 拦截规则
- 写报告类.md文件前，必须先过 pillar-verify
- 验证标记：`touch /tmp/.bazi_verified`
- 未验证→block，返回明确错误信息

### 触发方式
```bash
# 验证通过后，设置放行标记
bash projects/bazi-platform/scripts/pillar-verify.py && touch /tmp/.bazi_verified
# 然后写文件（hook自动放行）
```

## 六、反模式清单

| 反模式 | 正确做法 |
|:-------|:---------|
| 不拆任务直接派 | 拆成2-5分钟子任务 |
| 不带终止条件 | 每个任务明确Success condition |
| 缺四要素 | 目标+标准+格式+流程全带 |
| Maker审自己活 | 必须用独立Checker |
| 结果不做汇总 | 我汇总后再继续 |
| 靠LLM自觉遵守规则 | 用pre_tool_call hook物理拦截 |

## 七、加载链说明

```
线A（系统级·无条件加载，每个会话自动注入）：
  ① 系统基础提示词 ← Hermes内置
  ② config.yaml ← profile根目录
  ③ SOUL.md ← profile根目录（~105行身份+铁律）
  ④ USER.md ← memories/USER.md
  ⑤ MEMORY.md ← memories/

线B（项目级·CWD or链）：
  ① HERMES.md ← CWD递归搜索到git root（本文件）
  ② AGENTS.md ← 仅CWD
  ③ CLAUDE.md/.cursorrules ← 兼容
```
