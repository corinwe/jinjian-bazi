---
name: harness-creator
description: 构建轻量级Agent Harness——AGENTS.md、功能状态、验证工作流、范围边界、生命周期交接、记忆持久化、上下文控制、工具安全。来自walkinglabs/learn-harness-engineering
category: software-development
---

# Harness Creator — 构建轻量级Agent Harness

> 让代码仓库更易于AI Agent启动、保持在范围、验证工作、跨会话恢复
> 来源：github.com/walkinglabs/learn-harness-engineering

## 核心模型

每个有用的编码Agent Harness都有五个子系统：

| 子系统 | 最小制品 | 目的 |
|--------|---------|------|
| **指令** | `AGENTS.md` 或 `CLAUDE.md` | 启动路径、工作规则、完成标准 |
| **状态** | `feature_list.json`、`progress.md` | 当前功能、状态、证据、下一步 |
| **验证** | `init.sh` 或文档化命令 | Agent在声称完成前必须运行的测试/检查 |
| **范围** | 功能依赖关系和完成标准 | 防止过度扩展和半成品 |
| **生命周期** | `session-handoff.md`、会话结束例程 | 使下一个会话可重新启动 |

## 创建流程

### 第一步：检查现有内容
- 指令文件：AGENTS.md / CLAUDE.md 是否存在？
- 状态文件：特性列表、进度跟踪？
- 验证命令：测试、构建、lint？
- 文档：README、架构决策记录？

### 第二步：构建最小Harness
创建五个最小制品（每个子系统一个）。

### 第三步：验证
- Agent能读取启动说明吗？
- Agent知道它应该做什么吗？
- Agent完成工作后如何知道完成了？
- 下一个Agent（或人类的下一轮）能从停止的地方继续吗？

## 保持Harness轻量

| 要做 | 不要做 |
|------|--------|
| 保持AGENTS.md < 50行 | 把整个代码库的规则都写进去 |
| 只会说"做什么"和"怎么做" | 会说"不做什么" |
| 为Agent提供验证命令 | 依赖Agent自己发明验证步骤 |
| 结束时写状态（进度/证据/下一步） | 结束时只写"完成了" |
| 每次扩展Harness时只加最小规则 | 一次性写大量规则 |

## 验证工作流

```
每次修改后：
1. 运行验证命令
2. 记录结果（通过/失败 + 证据）
3. 如果通过 → 更新状态文件
4. 如果失败 → 修复或回滚

每次会话结束：
1. 更新session-handoff.md
2. 更新progress.md
3. 提交到git
```

## 常见陷阱

- ❌ Harness过大（Agent不读）
- ❌ 过度指定实现方式（Agent应自由选择方法）
- ❌ 没有定义"完成"
- ❌ 没有验证命令
- ❌ 会话间没有延续性
- ❌ 忘记更新Harness本身（Harness应与系统共同进化）
