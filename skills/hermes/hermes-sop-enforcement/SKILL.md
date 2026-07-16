---
name: hermes-sop-enforcement
category: hermes
description: Hermes Agent SOP自动执行与工程化保障体系。解决"规则写进SOUL.md/HERMES.md但Agent执行时跳过/遗忘"的根本矛盾。涵盖7层机制：/goal持久目标、Kanban多Agent看板、Cron定时任务标准化、Event Hooks自动守卫、Narrow Toolset窄工具集、Prompt工程化、Profile Distribution配置固化。
version: 1.1
created: 2026-07-16
updated: 2026-07-16
source: 官方文档逐字精读+生产部署实践
references:
  - references/hermes-hook-architecture-20260716.md — 实战hook脚本+配置示例+六六一键配置脚本+关键教训
---

# Hermes Agent SOP Enforcement — 让Agent按规则执行，不靠自觉

> **核心问题**：规则写进了 SOUL.md / HERMES.md / config.yaml，但 Agent 执行时仍然跳过、遗忘、凭感觉走。
> **根因**：文件规则是 LLM 需要"自觉遵守"的建议，不是系统强制的约束。
> **解法**：用 Hermes 内置的工程机制将规则变成「不执行就不能继续」的硬约束。

---

## 一、问题诊断

### 症状
- Agent 在多轮任务中跳过验证步骤
- 上下文压缩后遗忘之前设定好的目标
- 同一错误在不同会话中反复出现
- 多个 Agent（如金鉴真人 + 六六）各自遗忘不同步骤

### 根因
| 假因 | 真因 |
|:-----|:-----|
| "Agent 记忆力不够" | 规则在 system prompt 中，LLM 每轮都"看到"但可能忽略 |
| "prompt 不够详细" | 详细程度不改变 LLM 自主跳过规则的概率 |
| "需要更好的模型" | 更强模型一样会漏步骤——这是架构问题不是模型问题 |

---

## 二、三层架构模型（执行层/持久化层/治理层）

> **来源**：2026-07-16 精读 Hermes 官方 Hooks + Goals + Kanban + Cron 完整文档后重构。
> 原7层平铺模型已更新为三层架构，更清晰地反映工程化保障的层次关系。

### 执行层（Physical Enforcement）— 不依赖LLM自觉

> 核心原则：**物理拦截，不是AI自觉能替代的。** 这是本技能最核心的教训。

| 机制 | 能力 | 局限 |
|:-----|:-----|:------|
| `pre_tool_call` hook | **能阻断**工具调用（block） | 无法注入上下文，只能拦截 |
| `pre_verify` hook | **能追加**验证轮次（max_verify_nudges: 3） | 有次数上限，默认3次 |
| `pre_llm_call` hook | **能注入**上下文到用户消息层 | 约束力弱，非系统提示 |
| `transform_terminal_output` | **能过滤**敏感信息 | 只作用于终端输出 |
| `post_tool_call` hook | **observer-only**，返回值被忽略 | 不能阻断不能注入 |
| `on_session_start` hook | **observer-only**，返回值被忽略 | 不能注入上下文 |

**关键发现（2026-07-16精读修正）**：
- `post_tool_call` **不能**自动跑验证后阻断。它的返回值被忽略，脚本能跑但结果不影响流程
- `pre_llm_call` 注入的是**用户消息**不是系统提示。约束力低于SOUL.md
- `on_session_start` 不能注入上下文。别用它做"自动注入SOP"
- 真正能拦截的只有 `pre_tool_call`（阻断）和 `pre_verify`（追加轮次）

```yaml
# 执行层推荐配置
hooks:
  # 写文件前先验证 — 真正的物理拦截
  pre_tool_call:
    - matcher: "write_file|patch"
      command: "~/.hermes/agent-hooks/bazi-pre-write-verify.sh"
      timeout: 30
  
  # 每次回答前注入提醒（约束力弱，仅做提醒）
  pre_llm_call:
    - command: "~/.hermes/agent-hooks/bazi-pre-llm-hook.sh"
```

### 持久化层（Task Persistence）— 跨session/跨Agent任务不丢

| 机制 | 能力 | 局限 |
|:-----|:-----|:------|
| `/goal` | Judge每轮检查目标是否达成，未达成自动续跑 | ❌ **必须用户手动输入**，不能自动化 |
| Kanban | 任务看板持久化到SQLite，跨session/跨Agent可见 | 需要配置worker lanes |
| Cron | 定时执行标准SOP，workdir隔离不同项目上下文 | 一次性任务/非定时任务不适用 |

**/goal 关键特性**：
- 目标状态持久化在 `SessionDB.state_meta`，`/resume` 后恢复
- 自动检测后台进程是否卡住（park on background process）
- `protect_first_n: 3` 确保首轮目标不被上下文压缩裁剪
- Judge 可用独立低成本模型（`goal_judge` auxiliary task）
- 支持 completion contract（结构化验收标准）：`/goal draft <text>`
- 支持 `/subgoal` 追加验收条件
- ⚠️ Judge 非100%可靠：false positive（判定完成但实际没完成）和 false negative（判定继续但已完成）都可能发生

**Cron key参数**：
- `workdir` → 指定工作目录（自动加载该目录的 HERMES.md/SOUL.md）
- `enabled_toolsets` → 限制工具集（`terminal,file` 即可）
- `no_agent=True` → 纯脚本模式，零LLM干扰
- `attach_to_session: true` → 可回复

### 治理层（Governance）— 配置固化与规则落地

| 机制 | 能力 |
|:-----|:------|
| Narrow Toolset | 为不同任务定义不同工具集，减少决策分支 |
| Prompt工程化 | 将软规则转为可脚本验证的硬终止条件 |
| Profile Distribution | 将所有配置/技能/脚本打包为可分发包 |
| SOUL.md/.hermes.md分离 | SOUL.md只留身份+铁律，操作规则移到.hermes.md按项目加载 |

**提示工程化示例**：
```yaml
❌ 软规则：  "检查八字是否正确"
✅ 硬条件：  "Step 1: cat /tmp/bazi_output.json → 提取year_pillar
             Step 2: 对照五鼠遁口诀表 验证时柱
             Step 3: 不一致 → 停！不要继续"
```

---

## 🚨 研究方法论铁律（2026-07-16 老板训诫）

> **致命教训**：研究任何文档/资料时，扫关键字+组装方案 = 错误答案。
> 金鉴真人被老板当场指出「扫了几个关键字然后就组装成了这个方案」。
>
> 正确做法：**必须逐字逐句精读完整文档**，不跳行、不扫读、不凭记忆补全遗漏。

### 精读三步法

```
拿到文档 → 从头到尾逐字读一遍 → 不跳行不扫读
  如果被截断/太长 → 分部分读完整
读完后 → 列出核心发现 + 关键限制条件 + 遗漏细节
组装方案前 → 对照文档逐条核查自己的理解是否正确
```

### 常见违规行为

| ❌ 违规 | ✅ 正确 |
|:--------|:--------|
| 搜索到关键字就写方案 | 读完文档整个章节再写 |
| 看到"block"就以为可以阻断 | 仔细看是哪个hook、什么条件下、怎么返回 |
| 凭经验补充遗漏的细节 | 承认不知道，回文档找 |
| 觉得"大概就这个意思" | 承认不确定，读完确认 |

### 本技能就是由这种教训积累的

本技能从「官方文档扫读+组装」变为「官方文档逐字精读」后才发现了：
- `post_tool_call` 返回值被忽略（不能阻断）
- `pre_llm_call` 注入的是用户消息不是system prompt
- `on_session_start` 返回值被忽略
- 真正能拦截的只有 `pre_tool_call` 和 `pre_verify`

如果不是老板发现并纠正，现在还在用错误的方案。

---

## 三、Event Hooks 完整参考（18个事件逐字精读）

> **来源**：https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks 全文逐字精读

### 三种Hook系统对比

| 系统 | 注册方式 | 运行环境 | 用途 |
|:-----|:---------|:---------|:-----|
| **Gateway hooks** | `~/.hermes/hooks/<name>/HOOK.yaml + handler.py` | 仅网关 | 日志、告警、webhook |
| **Plugin hooks** | `ctx.register_hook()` in plugin | CLI + 网关 | 工具拦截、指标、guardrails |
| **Shell hooks** | `hooks:` in `config.yaml` → shell脚本 | CLI + 网关 | 即插即用的阻断/格式化/注入 |

### 完整事件表（18个事件，来自官方文档逐行提取）

| Hook | 触发时机 | 返回值/作用 |
|:-----|:---------|:-----------|
| `pre_tool_call` | 任何工具执行前 | `{"action": "block", "message": "..."}` 可阻断 |
| `post_tool_call` | 任何工具返回后 | observer-only，返回值被忽略 |
| `pre_llm_call` | 每轮开始，工具循环前 | `{"context": "..."}` 注入到**用户消息** |
| `post_llm_call` | 每轮结束，工具循环后 | observer-only |
| `pre_verify` | Agent编辑代码后，验证/完成前 | `{"action": "continue", "message": "..."}` 可追加轮次（上限3次） |
| `pre_api_request` | API请求前 | observer-only |
| `post_api_request` | API请求后 | observer-only |
| `on_session_start` | 新会话创建（首轮） | observer-only，不能注入上下文 |
| `on_session_end` | 会话结束 | observer-only |
| `on_session_finalize` | CLI/网关拆除活跃会话 | observer-only（flush/save/stats） |
| `on_session_reset` | `/new`或`/reset` | observer-only |
| `subagent_start` | delegate_task子Agent构建后 | observer-only |
| `subagent_stop` | delegate_task子Agent退出 | observer-only |
| `pre_gateway_dispatch` | 网关收到用户消息，认证+分发前 | `{"action": "skip"|"rewrite"|"allow", ...}` 影响路由 |
| `pre_approval_request` | 审批决策请求时 | observer-only |
| `post_approval_response` | 审批决策完成（或超时） | observer-only |
| `transform_terminal_output` | terminal工具内，截断/ANSI清洗/脱敏前 | `str` 替换原始输出，None保留 |
| `transform_tool_result` | 任何工具返回后，交给模型前 | `str` 替换结果，None保留 |
| `transform_llm_output` | 工具循环完成，最终响应交付前 | `str` 替换响应文本，None/空保留 |

---

## 四、推荐实施路径

### P0（今晚能做）
1. 创建 `~/.hermes/agent-hooks/` 目录
2. 写 `pre_tool_call` hook：匹配 `write_file|patch` → 写文件前验证，不通过就block
3. 写 `pre_llm_call` hook：每次回答前注入提醒（约束力弱但聊胜于无）
4. 配置 `hooks_auto_accept: true`

### P1（本周做）
5. 将重复性 SOP 转为 Cron Job（workdir + narrow toolsets）
6. 为不同任务类型定义工具集

### P2（本月做）
7. 将 Profile 导出为可分发包
8. 为多Agent协作配置 Kanban lanes

---

## 五、常见陷阱

| 陷阱 | 后果 | 正确做法 |
|:-----|:-----|:---------|
| 只在 SOUL.md 写规则 | 规则存在但 Agent 可能跳过 | 用 `pre_tool_call` hook 物理阻断 |
| 依赖 `/goal` 做所有事 | 每次要手动输入 | 用 `pre_tool_call` hook 自动拦截 |
| 以为 `post_tool_call` 能阻断 | hook脚本跑了但交付还是过了 | 应改用 `pre_tool_call` |
| 以为 `on_session_start` 能注入上下文 | 写入了配置但没生效 | 该hook是observer-only |
| hook 脚本不测试就上线 | 脚本出错时Agent继续（hook非阻塞） | 先在CLI测试脚本再配hook |
| 给所有任务全量工具集 | LLM有太多选择→易走错分支 | 按任务类型限制工具集 |
| 扫描文档关键字就组装方案 | 答案看似合理但关键细节全错 | 必须逐字逐句精读完整文档 |