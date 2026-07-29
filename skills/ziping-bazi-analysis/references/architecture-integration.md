# 商业化架构参考（2026-07-29）

整体架构文档见 `bazi-foundation-analysis/architecture/` 目录。
完整概要见 `bazi-foundation-analysis/references/architecture-summary.md`。

## 与本技能的关系

当本技能（ziping-bazi-analysis）被加载时，正确的调用流程是：
1. 先调 `paipan.py` 排盘（非LLM）→得到四柱+藏干
2. 再调 `shen_qiang_ruo.py` 算身强弱（非LLM）→得到分数+标签
3. 再调 `ge_ju.py` 定格局（非LLM）→得到主格+喜用+调候
4. 以上引擎数据→喂给LLM做叙事合成（LLM只做文字工作）

**禁止**：LLM自己算排盘、身强弱、格局。这是确定性的代码工作。
