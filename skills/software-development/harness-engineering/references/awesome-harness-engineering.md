# Awesome Harness Engineering — 精选资源索引

> 来源：github.com/ai-boost/awesome-harness-engineering
> 完整学科：Agent = Model + Harness

## 📐 基础文献（Foundations）

| 文章 | 来源 | 核心观点 |
|------|------|---------|
| [Harness Engineering](https://openai.com/index/harness-engineering/) | OpenAI | 将Harness Engineering定义为学科 |
| [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) | Anthropic | 何时使用workflows vs agents |
| [Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) | Martin Fowler | 三大系统：上下文工程/架构约束/熵管理 |
| [The Anatomy of an Agent Harness](https://blog.langchain.com/the-anatomy-of-an-agent-harness/) | LangChain | 五大原语：文件系统/代码执行/沙箱/记忆/上下文 |
| [How We Build Azure SRE Agent](https://techcommunity.microsoft.com/blog/appsonazureblog/how-we-build-azure-sre-agent-with-agentic-workflows/4508753) | Microsoft | 35,000+生产事故自治处理案例 |

## 🔄 Agent Loop（代理循环）

- [ReAct论文](https://arxiv.org/abs/2210.03629) — Thought/Action/Observation循环
- [Unrolling Codex Agent Loop](https://openai.com/index/unrolling-the-codex-agent-loop/) — 每个循环内部的分解
- [Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) — 仅Harness变化使Agent从30名升到前5

## 🧩 上下文工程（Context Engineering）

- 上下文腐烂（Context Rot）是最大敌人
- 文件系统是最可靠的上下文载体
- Skills = 渐进式能力暴露（先摘要→再细节）
- 上下文压缩策略

## 🛡️ 验证与CI集成

- 计算型验证 >> 推理型验证（速度快、可靠性高）
- 前馈（规则/指南）+ 反馈（测试/审查）= 自我纠正循环
- 红线规则：30分钟无进展则停止重新评估

## 🔒 零信任设计（L0）

- 始终假设LLM会走捷径、跳过步骤
- 执行者和评估者始终分离
- 人类在环（HITL）：关键决策点需要人类介入

## 金鉴真人Harness架构映射

| Harness概念 | 金鉴真人实现 |
|-------------|------------|
| 前馈指南 | 18个八字技能、九龙道长原始规则、AGENTS.md |
| 确定性计算 | paipan引擎、身强弱评分、财星分数 |
| 反馈传感器 | bazi-auto-verify、validate_all.py、26项验证 |
| 三层架构 | 规则引擎→数据层→输出层 |
| 可审计性 | pipeline签名、版本控制、校准案例库 |
| HITL | 老板审查报告、校准验证 |

## 🔗 更多资源

- [awesome-harness-engineering (GitHub)](https://github.com/ai-boost/awesome-harness-engineering) — 883个实体，1590个关系
- [harness-engineering.ai](https://harness-engineering.ai/) — 交互式知识图谱
- [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/en/) — 项目基础课程
