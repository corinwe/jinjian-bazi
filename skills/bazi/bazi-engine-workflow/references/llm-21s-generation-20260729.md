# LLM 21§报告生成技术（2026-07-29 实战验证）

> 场景：workflow_engine_v3.py 让LLM直接生成21§完整报告，而不是用结构化模型截取字段。
> 触发：老板验收时发现报告只有5段（§1/§2/§18+自创两段），不是标准21§。根因是 Pydantic AnalysisReport 模型只有5个字段，LLM输出被模型约束截断了。

## 一、根因：结构化模型截断输出

```
旧方案（错误）:
  AnalysisReport(gegang, xiyong, san_jueduan, lines(5), knowledge_used)
  → Instructor 强制LLM输出这5个字段 → 报告只有5段，21§缺失

老板验收: "你所谓生成的21段报告，你验证过了吗？就一个格局，还有一个三决断"
```

**教训**：用Instructor/Pydantic结构化输出时，模型的字段集合就是LLM输出的天花板。要21§就必须让模型输出 raw_markdown，而不是穷举字段。

## 二、正确方案（workflow_engine_v3.py）

```python
class Report21(BaseModel):
    raw_markdown: str = Field(min_length=500)  # 只约束整体，不约束内容

# 生成后代码层校验§完整性
def count_sections(text: str) -> tuple:
    found = [s for s in STD_21 if re.search(re.escape(s[:6]), text)]
    missing = [s for s in STD_21 if s not in found]
    return found, missing

# 重试循环：缺失§ → 把缺失列表反馈给LLM重试（最多3次）
```

## 三、关键参数（每项都是踩坑换来的）

| 参数 | 值 | 原因 |
|:-----|:---|:-----|
| max_tokens | **6000** | 4000不够，LLM写到§6就截断 |
| 每§篇幅 | **2-3句话·简洁精炼** | 说"内容充实"→LLM每§写500字→token耗尽只出6§ |
| §分隔 | `---` | 明确分隔，校验正则好匹配 |
| §列表 | prompt内**完整列出21§** | 不列→LLM自由发挥只写8-10个§ |
| system | "每§2-3句。必须包含全部21个§。用---分隔§。" | 简洁约束进system比user更稳 |
| 校验 | 代码层 count_sections + 缺失反馈重试 | 命中率从~30%提升到~100%（1-2次尝试） |

## 四、prompt模板（验证可用）

```
输出21§标准八字分析报告。要求：
1. 必须包含全部21个§，一个不能少
2. 每§写2-3句话，简洁精炼
3. §之间用---分隔
4. §8财富分析的破财风险根据八字实际喜忌动态判定（不可写死"比劫"）
5. §1一页总览表必须列出三大核心分析【关键调和与关键做工路径】【强项与弱项】【关键链路不能断】
6. §21人生建议必须呼应以上三项
7. §17大运总表必须用Markdown表格：大运|起止年龄|起止年份|干支五行|对格局影响|定性描述（至80岁）
8. §16流年重点事件表必须用表格：流年干支|事件类型|事件描述|吉凶（近10-15年已发生+未来5-10年，事件具体如"2023癸卯年升任总监"）

完整§列表：
 1. §1 一页总览表 ... 21. §21 人生建议
```

## 五、架构决策：弃用LangGraph

v2用LangGraph StateGraph → 重试循环触发 `GraphRecursionError: Recursion limit of 15 reached`（retry_count没有正确递增，无限循环）。
v3改为**直接函数调用流水线**（engine→retrieve→LLM生成→while循环校验重试→输出），更稳定：
- 无图递归限制
- 重试逻辑用普通while循环，肉眼可追踪
- 单文件自包含（workflow_engine_v3.py ~180行）

## 六、校验清单（交付前必跑）

```
□ 引擎: bazi_str | shen_qiang_label(score) | gegang_main | 调候用神(穷通宝鉴)
□ 检索: refs数量（TOP_K=8）
□ LLM: count_sections 21/21
□ 校验: 缺失=0 或 重试≤3
□ 输出: raw_markdown 含全部21§
□ 端到端抽查: 报告含调候/体象/定格等经典框架痕迹
```

## 七、相关坑（同日Chroma向量化）

经典文档入库后检索0命中 → 两个原因：
1. `index_knowledge.py` section提取顺序错（先匹配§N再匹配经典名）→ 经典块全标成§37 → 改为文件名拼音→中文映射表优先
2. `pre_retrieval_hook.py` 的 section 白名单没有包含 `经典-*` 前缀 → 检索时被 where 过滤掉 → 必须在 get_required_sections 加入新section
3. 入库成功 ≠ 检索命中：必须跑真实查询验证 refs 含"经典-XX"
详见 bazi-foundation-analysis/references/chroma-vectorization-pitfalls_20260729.md
