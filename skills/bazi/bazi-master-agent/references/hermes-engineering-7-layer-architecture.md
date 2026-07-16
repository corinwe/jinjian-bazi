# Hermes Agent 商业化工程架构 — 7层保障体系

> 来源：2026-07-16 全网调研（Hermes官方文档 + 知乎深度解析 + 海外生产实践 + 社区经验）
> 核心痛因：规则写进文件，Agent执行时还是忘。靠LLM自觉遵守≠工程强制执行。

---

## 层1：/goal 持久目标（Hermes内置·Judge强制执行）

### 原理
每次交互后，Judge模型自动检查目标是否达成。未达成则system强制继续。

### 用法
```
在聊天平台输入：/goal <你的目标>
效果：Judge每轮检查，未达成不可进入下一轮
```

### 适用场景
- "必须过5关pillar-verify+320门禁才能交付"
- "写报告前必须先加载所有11个技能"
- "所有数据必须从引擎JSON提取，禁止手算"

### 关键限制
- 只能由用户在聊天平台输入，Agent无法自行设置
- 每次会话需重新设置（不跨session持久化）
- 适合单次任务的硬约束

---

## 层2：Kanban 多Agent看板（任务持续性保障）

### 原理
任务持久化到 ~/.hermes/kanban.db，跨session可见。上下文压缩不丢任务。

### 核心工具集
kanban_create / kanban_list / kanban_show / kanban_complete / kanban_block（熔断器）/ kanban_heartbeat（保活）/ kanban_comment / kanban_link / kanban_unblock

### 工作流
```
dispatcher 派任务 → kanban_create
worker 接任务 → kanban_list + kanban_heartbeat
中断/压缩 → kanban_show → 从断点继续
完成 → kanban_complete
```

---

## 层3：Cron 定时任务（标准化SOP自动化）

### 生产级配置关键参数
```
cronjob action=create
  schedule="0 9 * * *"
  workdir=/root/...
  enabled_toolsets=[file,terminal,delegation]  # 窄工具集
  skills=[skill1,skill2]                       # 固定技能
  attach_to_session=true                       # 可回复
  no_agent=true                                # 纯脚本模式
```

### 适用场景：每日报告生成 / 定时推库 / 批量处理 / 周期性校验

---

## 层4：Event Hooks + Plugin（执行拦截与安全网）

### Hook点
| Hook类型 | 触发时机 | 用途 |
|:---------|:---------|:-----|
| gateway hooks | 消息收发时 | 日志、告警 |
| tool hook (pre) | 工具调用前 | 安全检查 |
| tool hook (post) | 工具调用后 | 结果验证 |
| lifecycle hooks | 启动/关闭/压缩 | 状态持久化 |

### 适用场景：file_write前强制checklist / terminal执行前白名单检查

---

## 层5：Narrow Toolset 窄工具集（减少幻觉）

### 原理
每任务只暴露最小必要工具集，减少LLM决策分支，降低出错概率。

### 生产建议
| 任务类型 | 推荐工具集 | 排除 |
|:---------|:-----------|:-----|
| 八字报告生成 | file, terminal | web, browser, vision |
| PDF种子处理 | terminal, file | web, browser |
| 全网搜索研究 | web_search | file（只读） |

---

## 层6：Prompt as Engineering Specification（提示词工程化）

### 生产案例（来源：Field Notes）
"将提示视为严格的工程规范而非随意请求后，自主任务成功率从40%提升到90%+"

### 硬规则四要素
1. **可执行的命令**（不是描述，是命令）
2. **可验证的结果**（grep/test/wc，不是"看起来对"）
3. **硬终止条件**（不满足就停，不说OK）
4. **失败路径**（失败了怎么办，不是"那就修一下"）

### 示例对照
```
❌ "检查八字是否正确"
✅ "cat /tmp/bazi_output.json → 提取year_pillar → 对照五鼠遁表验证 → 不一致则停"

❌ "确认内容完整"
✅ "grep -c '§21' report.md → 必须是1才能继续"
```

---

## 层7：Profile Distribution（配置固化·即用即走）

### 命令
```
hermes profile import <name> --from-github <org/repo>
```

### 生产建议
- 所有技能/脚本/配置放在git仓库
- 重要更新打tag（如v2026-07-16）
- 配置中锁定 tool_use_enforcement: true

---

## 当前状态评估（2026-07-16）

| 层级 | 机制 | 状态 | 优先级 |
|:----|:-----|:-----|:-------|
| L1 | /goal持久目标 | ❌ 从未用过 | P0 |
| L2 | Kanban看板 | ❌ 从未用过 | P1 |
| L3 | Cron定时任务 | ⚠️ 部分在用 | P1 |
| L4 | Event Hooks | ❌ 从未用过 | P2 |
| L5 | Narrow Toolset | ❌ 从未用过 | P2 |
| L6 | 提示工程化 | ⚠️ 有但不硬 | P0 |
| L7 | Profile固化 | ✅ git追踪 | P3 |

### P0行动建议
1. L1（/goal）：每次跑报告前老板在Feishu输入 /goal 设置交付强制门禁
2. L6（硬约束）：逐条检查SOP中的规则，把"检查XX"改为"cat/grep → 不通过则停"
