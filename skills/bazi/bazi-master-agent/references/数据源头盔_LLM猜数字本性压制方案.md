# 数据源头盔 — LLM猜数字本性压制方案

> **编制人：** 金鉴真人
> **编制时间：** 2026年06月24日
> **版本：** v1.0
> **来源：** 本会话中老板发现子源起运年龄随口说错（说约1岁，实际8.52岁）后，经网上调研发现这是LLM体系的结构性问题。

---

## 根因认知

**OpenAI 2025论文（Kalai et al.）核心结论：**
> "LLMs hallucinate because training and evaluation procedures reward guessing over acknowledging uncertainty."
>
>「LLM出现幻觉是因为训练和评估流程奖励猜测而不是奖励承认不确定性」

**结构性原因：** Next-token训练目标和排行榜奖励自信的猜测，而不是校准的不确定性。所以LLM学会了** bluff（虚张声势）**。

这不是我的个人毛病，是所有LLM的架构性问题。

## 实战案例

| 场景 | LLM随口说 | 数据源真实值 | 偏差 |
|:----|:----------|:------------|:----|
| 子源起运年龄 | 「约1岁」 | **8.52岁** | **7.5年** |
| 家主起运年龄 | 「9岁多」 | **0.38岁** | **9年** |

两个案例的共同模式：LLM被问到数字时，第一反应是**编一个看起来合理的数字**，而不是说「等一下我查一下」。

## 物理压制方案

### 方案一：pipeline数据源强制读取（已实现）
`bazi-pipeline.sh v1.1` 在生成context前强制读取数据源JSON，已验证的数字标注✅，未验证的标注⚠️。

### 方案二：心理口诀（固化到memory）
「先查再说」 — 任何八字数字说出来之前，必须先查数据源JSON。

### 方案三：拒绝输出未验证数字
当数字未经数据源验证时，必须说：
「等一下我查一下数据源」
而不是编一个数字。

## 后续研究引用

- OpenAI 2025 paper: "Hallucination" by Kalai et al.
- arXiv 2605.06445: "Constraint Decay" — 约束随对话衰减
- Lakera Guide: "6 failure modes of LLM hallucination (2026)"
- dev.to: "AI Agent Guardrails: Rules That LLMs Cannot Bypass" — 提示词只是建议，架构才是约束
