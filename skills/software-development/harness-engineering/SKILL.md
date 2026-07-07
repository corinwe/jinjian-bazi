---
name: harness-engineering
description: Harness Engineering完整学科——Agent=Model+Harness。前馈指南+反馈传感器、计算型vs推理型控制、红线规则、三层架构。来自Martin Fowler/OpenAI/Anthropic/LangChain等权威来源
category: software-development
---

# Harness Engineering 完整知识体系

> **Agent = Model + Harness**
> 如果你不是模型，你就是Harness。

## 核心理念

### 什么是Harness Engineering？
Harness Engineering 是设计和维护围绕AI Agent的控制系统的学科——约束、反馈回路、验证机制，使Agent在生产环境中可靠运行。

- 模型包含智能（intelligence）
- **Harness让智能变得可用（useful）**

一个Harness包括：
- System Prompts
- Tools / Skills / MCPs
- 基础设施（文件系统、沙箱、浏览器）
- 编排逻辑（子Agent孵化、任务切换、模型路由）
- 确定性执行的Hooks/中间件

### 前馈与反馈（Feedforward & Feedback）

```
前馈指南（Feedforward）        反馈传感器（Feedback）
  ┌──────────────┐            ┌──────────────┐
  │  AGENTS.md   │            │   Linter     │
  │  Rules文件   │            │   测试       │
  │  参考文档    │────┐   ┌───│  类型检查    │
  │  How-to指南  │    │   │   │  审查Agent   │
  │  Skills      │    │   │   │  浏览器检查  │
  └──────────────┘    │   │   └──────────────┘
                      ▼   ▼
                ┌──────────────┐
                │  Coding Agent │──── 输出
                └──────────────┘
```

- **前馈**：在Agent行动之前引导它（规则、文档、提示）
- **反馈**：在Agent行动之后自我纠正（测试、lint、审查）

单独只有反馈→Agent不断重复同样的错误
单独只有前馈→Agent编码规则但永远不知道是否有效

### 计算型 vs 推理型控制

| 类型 | 速度 | 确定性 | 示例 |
|------|------|--------|------|
| **计算型（Computational）** | 毫秒-秒 | ✅ 可靠 | Lint、测试、类型检查、结构化分析 |
| **推理型（Inferential）** | 秒-分钟 | ⚠️ 概率性 | LLM作为评审者、审查Agent、质量评估 |

**最佳实践：先使用计算型检查，再用推理型检查。**

## 三层Harness架构

```
┌──────────────────────────────────────────────────┐
│   Layer 3: 用户Harness（最外层）                  │
│   项目规则、测试策略、CI/CD门禁                    │
├──────────────────────────────────────────────────┤
│   Layer 2: 构建者Harness（中间层）                 │
│   Skills、MCP工具、系统提示、记忆系统               │
├──────────────────────────────────────────────────┤
│   Layer 1: 模型Harness（核心层）                   │
│   Agent Loop、工具接口、上下文管理                  │
│   文件系统→沙箱→代码执行→验证                      │
└──────────────────────────────────────────────────┘
```

### L0: 零信任原则
> 始终假设LLM会走捷径、编造、跳过步骤。
> **做工作的Agent永远不能评价自己的工作。** 执行者和评估者始终是分离的。

## Harness核心组件

### 1. Agent Loop（代理循环）
ReAct模式：思考→行动→观察→重复
```
Observe → Plan → Act → Verify → (repeat)
```
关键：状态持久化、checkpoint/resume、circuit breaker

### 2. 工具设计（Tool Design）
- 命名清晰、schema精确、错误表面处理
- 工具设计即是Agent UX
- 最小暴露原则：太多MCP服务器会膨胀上下文
- 通用工具优先（bash+代码执行 > 专用工具）

### 3. 上下文管理（Context Engineering）
- 上下文腐烂（Context Rot）是最大敌人
- 渐进式暴露：先摘要→再细节→按需加载
- 文件系统是最基础的上下文管理原语
- Skills用于渐进式能力暴露（先加载SKILL.md摘要，再按需加载详细内容）

### 4. 验证与CI集成（Verification）
- 计算型验证优先（linter、类型检查、测试）
- 推理型验证补充（LLM-as-judge）
- **先正推再反推校准**（金鉴真人铁律）
- 验证门禁：每一步都必须通过才能继续

### 5. 记忆与状态（Memory & State）
- 跨会话持久化
- 上下文压缩（compaction）
- 文件系统作为最可靠的记忆载体
- git提供版本控制
- **🚨 重要配置必须存文件，不靠记忆。记忆会被截断（~2200字符限制），截断后信息丢失。** 存配置的方式：`原生文件（完整版）→ skill reference（引用版）→ 记忆（仅存指针）`

### 6. 沙箱与安全（Sandbox）
- 安全隔离执行环境
- 三层边界：外部→内部→数据
- 权限控制（allowedTools、permission gates）
- 密钥管理

### 7. 可观测性（Observability）
- 结构化日志（JSON格式）
- RED指标（Rate/Errors/Duration）
- OpenTelemetry追踪
- 症状告警（不是原因告警）

### 8. 人类在环（Human-in-the-Loop）
- 关键决策点暂停执行
- 审批/修改/拒绝模式
- 逐步扩大信任（canary→25%→50%→100%）

## 三个Harness类别（Martin Fowler分类）

### 维护性Harness（Maintainability）
- 代码风格一致性
- 架构规则
- 命名约定

### 架构适应性Harness（Architecture Fitness）
- 模块边界验证
- 依赖方向检查
- 架构约束测试（ArchUnit等）

### 行为Harness（Behaviour）
- 功能测试
- 回归测试
- 性能测试

## 金鉴真人 Harness 架构实践

我们的八字排盘平台本身就是Harness Engineering的最佳应用：

```
┌────────────────────────────────────────────────────────┐
│  用户输入层                                            │
│  出生日期/姓名/性别                                    │
└──────────────────────┬─────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────┐
│  前馈指南（Feedforward Guides）                        │
│  ├─ 金鉴真人18个技能（规则固化）                       │
│  ├─ AGENTS.md / SKILL.md                               │
│  ├─ 九龙道长原始方法论                                  │
│  └─ 校准案例库                                         │
└──────────────────────┬─────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────┐
│  规则引擎（确定性计算型）                               │
│  ├─ bazi-pipeline.sh（排盘）                          │
│  ├─ paipan.py（身强弱评分）                            │
│  ├─ 财星/格局/用神/维度评分                            │
│  └─ 21§结构化输出                                      │
│  特点：确定性、可审计、零幻觉                            │
└──────────────────────┬─────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────┐
│  反馈传感器（Feedback Sensors）                        │
│  ├─ bazi-auto-verify（审计验证）                      │
│  ├─ bazi-wushidun-verify（五鼠遁验证）                │
│  ├─ validate_all.py（全量26项验证）                    │
│  ├─ §1 vs §8财星数一致性检查                           │
│  └─ 官网验证（bazi-zydx-verify.sh）                   │
└──────────────────────┬─────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────┐
│  API输出层                                              │
│  FastAPI → 结构化JSON → 前端渲染 → 用户                │
└────────────────────────────────────────────────────────┘
```

## Harness工程核心原则总结

| 原则 | 说明 |
|------|------|
| **零信任** | 假设Agent会犯错，做工作的不评价自己的工作 |
| **计算型优先** | 先用确定性的检查，再用推理型的判断 |
| **前馈+反馈** | 同时有引导和验证，缺一不可 |
| **渐进暴露** | 先给摘要，按需加载详情（Skill的SKILL.md模式） |
| **最小工具** | 只暴露需要的工具，太多MCP会膨胀上下文 |
| **可审计** | 每一步都可追溯、可重现、可验证 |
| **人类在环** | 关键决策点需要人类介入 |

## 参考资源

| 来源 | 内容 |
|------|------|
| Martin Fowler: Harness Engineering | 前馈/反馈框架、三层Harness |
| OpenAI: Harness Engineering | Codex Harness设计哲学 |
| Anthropic: Building Effective Agents | Agent架构基础 |
| LangChain: Anatomy of an Agent Harness | 五大原语（文件系统/代码执行/沙箱/记忆/上下文） |
| awesome-harness-engineering | 883个实体、1590个关系 |

### 内置参考文件

本技能包含以下参考文件，通过 skill_view(name='harness-engineering', file_path='references/xxx') 加载：

| 文件 | 内容 |
|------|------|
| `references/awesome-harness-engineering.md` | 精选外部资源索引（基础文献/Agent循环/上下文/验证/零信任） |
| `references/bazi-platform-case-study.md` | 八字平台实战案例（5 Sprint重整/Prove-It教训/PAT权限坑/验证指标） |
| `references/bazi-platform-rebuild-case-study.md` | 2026-06-26全方位重整案例（引擎修复/Sprint交付/26项验证） |
