# 21§报告流水线·技术陷阱（2026-07-29 实战验证）

> 场景：workflow_engine 从引擎数据+Chroma检索+LLM生成完整21§报告。
> 老板核心要求：确定性交给代码+前置注入，LLM只做叙事合成，**跑完必须验证**。

## 陷阱1：LangGraph条件循环死循环（GraphRecursionError）

- 现象：`Recursion limit of 15 reached without hitting a stop condition`
- 根因：`decide()` 判断 `retry_count < 3`，但节点返回时 `retry_count` 没有递增 → 永远满足重试条件 → 无限循环
- 修复：弃用LangGraph条件边循环，改为显式 `for attempt in range(MAX_RETRIES+1)` 手动重试循环
- 教训：条件边的判断状态必须由节点**实际更新**；简单线性+重试流程用显式循环比状态图更稳

## 陷阱2：LLM长报告输出截断（21§只生成6/21）

- 现象：max_tokens=4000 时，LLM只输出6个§（§1/§2/§3/§4/§8/§18）就截断
- 修复：`max_tokens=6000` + prompt显式要求「每§写2-3句话，简洁精炼」+「§之间用---分隔」
- 结果：21/21§齐全
- 教训：21§报告必须给足token预算；同时必须告诉LLM简洁——两者缺一不可

## 陷阱3：Instructor字段模型截断导致「假通过」

- 现象：把报告拆成有限字段的Pydantic模型（gegang/xiyong/san_jueduan/lines/knowledge_used）
  → LLM输出被模型截断为5个字段的内容
  → 校验门禁只检查「字段存在」，全字段都有 → 校验通过
  → 但报告根本不是21§！老板质疑「你验证过了吗？当前报告是啥样的」
- 根因：**字段数量=输出上限；校验范围=模型字段范围**。模型限制了什么，校验就只查什么。
- 修复：
  - `response_model = Report21 { raw_markdown: str }` 承载全文（只约束整体结构，不限制内容）
  - 校验用正则逐§计数：`for sec in STD_21: if re.search(re.escape(sec[:6]), raw)` 缺失即驳回重试
  - STD_21 列表必须与报告模板章节完全一致

## 陷阱4：验证必须亲自看实际输出，不能只看流水线日志

- 老板原话：「你所谓的生成21段报告，你验证过了吗？……你就跟我说那是21段标准的，你看看当前这报告是啥样的」
- 教训：`wc -l` + 检查每个§标题行是否存在。流水线打印「21/21§」不代表格式正确。
- 正确验证：读文件 → 逐§标题确认 → 确认§16/§17是表格 → 确认§1含三大核心分析

## 引擎API签名速查（接入时容易踩）

```python
# BaZi/Pillar 是dataclass，位置参数（不是year_pillar关键字！）
bazi = BaZi(
    Pillar(gan=p['year_pillar']['gan'], zhi=p['year_pillar']['zhi']),  # cang_gan留空自动从DI_ZHI_CANG_GAN填充
    Pillar(gan=p['month_pillar']['gan'], zhi=p['month_pillar']['zhi']),
    Pillar(gan=p['day_pillar']['gan'], zhi=p['day_pillar']['zhi']),
    Pillar(gan=p['hour_pillar']['gan'], zhi=p['hour_pillar']['zhi']),
    '男'
)
score, label, _ = compute_shen_qiang_ruo(bazi)      # 返回(分数, 标签, 明细)
geju_main, geju_desc = determine_ge_ju(bazi)        # 返回元组(主格局, 描述) — 只收1个值会TypeError
xiyong_tup = determine_xi_yong_shen(bazi)           # 返回([喜],[忌]) 元组
```
