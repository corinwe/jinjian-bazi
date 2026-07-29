---
name: bazi-paipan-sop
description: 金鉴真人·八字排盘标准作业程序（SOP）。封装排盘全流程：技能加载顺序→排盘源头校验→引擎评分→分析报告→发布前校验→归档推库。2026-07-14重写。2026-07-27新增商业化架构转型参考。
tags: [八字, 排盘, SOP, 金鉴真人, pipeline, 物理化]
related_skills: [bazi-engine-workflow, bazi-foundation-analysis, bazi-report-template, bazi-platform-harness, bazi-task-dispatch, maker-checker-workflow, bazi-auto-verify, bazi-calibration, bazi-report-engine-audit, bazi-data-source]
---

# 金鉴真人·八字排盘SOP v2.0

> **2026-07-29 架构转型完成**：从「Agent自主Loop」转型为「确定性引擎+代码层前置检索+LLM叙事合成+校验门禁」。
> 完整架构代码在 `skills/bazi/bazi-foundation-analysis/architecture/`

## 核心架构（三层四步）

```
[输入]
   │
   ▼
┌─────────────────────────────────────┐
│ Step 1: 引擎计算层（确定性Python代码）│ ← paipan.py / shen_qiang_ruo.py / ge_ju.py
│   排盘 → 身强弱 → 格局 → 喜用 → 十神  │   全部代码层直接调用，LLM不参与计算
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│ Step 2: 知识检索层（代码层强制）      │ ← pre_retrieval_hook.py → Chroma
│   根据任务类型自动检索相关知识块注入    │   220个知识块，Agent无选择权
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│ Step 3: LLM叙事合成层（仅合成不计算）  │ ← workflow_engine.py → DeepSeek API
│   基于引擎数据+知识库规则合成流动报告    │   温度0.1，结构化JSON输出
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│ Step 4: 校验门禁层（代码层拦截）       │ ← gatekeeper.py → Instructor+Pydantic
│   分线完整性/知识引用/三决断具体性      │   不通过则驳回重试（最多3次）
└────────────────┬────────────────────┘
                 ▼
              输出
```

## 执行顺序（先验过去→再看当下选择）

### Phase 0 — 三决断（免费）
任何分析的第一步：给3条可验证的过去判断。
参考：`products/flow.md`, `products/three-verifications-methodology.md`

### Phase 1 — 排盘校验
调用引擎 `paipan.py` 排盘，比对四柱是否正确。

### Phase 2 — 引擎计算
调用 `shen_qiang_ruo.py` → `ge_ju.py` → `da_yun.py` → 各领域模块。
所有计算由确定性Python代码完成，LLM不参与计算。

### Phase 3 — 前置检索
调用 `pre_retrieval_hook.retrieve()` 从Chroma检索相关知识。
检索结果强制注入上下文，标注【强制知识】。

### Phase 4 — LLM叙事合成
调用 `workflow_engine.node_reasoning()`，基于Phase 1-3的数据合成报告。
LLM只做翻译和叙述，不做计算和判断。

### Phase 5 — 校验门禁
调用 `gatekeeper.validate_full_analysis()` 校验输出。
必检项：分线完整性（5条缺一不可）、知识引用、三决断具体性。
不通过则驳回重试（最多3次），3次都不过则转人工。

### Phase 6 — 归档推库
见下「文件归档铁律」。

## 文件归档铁律（2026-07-27 老板校准·两次修正）

### 两仓库分工
仓库名            存放内容                          归属
──────            ──────                            ────
weiwuji-knowledge  知识库（报告/知识/人物档案/素材）   主库
jinjian-bazi       程序（SOP/代码/引擎/配置）          程序库

### 知识库目录规则
路径                                                               用途
────                                                                ────
`07-国学哲学/八字命格/00-原始素材/`                                 外部导入的原始材料
`07-国学哲学/八字命格/02-人物档案/编号-姓名/`                       人物分析报告
`07-国学哲学/八字命格/04-金鉴真人体系/`                             体系性文件（SOP/代码/架构）
`07-国学哲学/八字命格/04-金鉴真人体系/architecture/`                 架构代码（.py文件）
`07-国学哲学/八字命格/01-理论体系/`                                 理论体系
`07-国学哲学/八字命格/00-索引/`                                     索引文件

### 推送铁律（必做清单）
□ 文件写到磁盘后，必须立刻 git add + git commit + git push
□ 涉及人物报告/知识文档 → 推 weiwuji 仓库
□ 涉及程序代码/SOP/引擎 → 推 jinjian 仓库
□ 两者都涉及 → 两个仓库都推（这是常见情况）
□ 推完后告知老板具体文件路径
□ 避免硬编码API key到代码中（用环境变量注入）

### 人物报告命名规范
`{日柱天干地支}_{内容}_{日期}.md`（如 `乾造辛亥_完整多流派报告_20260727.md`）

## 多流派分析模式
支持同时输出子平/盲派/九龙三个流派的简版分析。
用户反馈哪个流派准→以该流派为主体深度分析。
参考：`products/multi-school.md`

## 商业化收费标准
- 免费：基础排盘+旺衰+格局+三决断+后续方向选择
- 付费：六体系完整分析+条件喜忌+分线断法+大运流年总表+风险日历
参考：`products/pricing.md`

## 标准报告格式铁律
输出报告必须按21§标准（详见 `skills/bazi/bazi-foundation-analysis/architecture/report_template_21s.md`）：
§1总览→§2格局→§3身强弱→§4喜用→§5灾祸→§6性格→§7外貌→§8财富→§9置业→§10事业→§11学历→§12婚姻→§13子女→§14健康→§15六亲→§16大事表→§17大运→§18三决断→§19总评→§20补益→§21建议
**铁律**：不可只输出§2+§18就结束。必须覆盖全部21§。

## 动态威胁规则
§8财富分析的破财风险必须根据八字喜忌动态判定（不可写死为"比劫"）：
- 身强→防比劫夺财
- 从弱→防印比逆势
- 身弱→防财星损身
- 火旺→防水克火
- 从强→防官杀破局
判断依据：引擎输出的身强弱标签+喜用忌组合。

## 流派声明铁律（2026-07-29 老板校准）
报告开头**不**加流派声明段落。综合给出分析结论即可。
流派信息仅在报告中通过用词和判断方式自然体现（子平体系用术语、九龙用比例法）。

## 输出格式铁律（2026-07-29 老板校准·两次修正）
- 报告必须使用标准21§格式输出，不可只输出§2+§18就结束
- 格式必须包含正确换行（`\\n`）、Markdown表格（`| 序号 | 项目 | 内容 |`）、清晰的分段标题
- **不可揉在一起无换行无格式**（老板多次纠正此问题）
- **报告开头不加流派声明段落**，直接进入§1总览表
- 参考：`architecture/report_template_21s.md`（21§标准SOP）
- 报告末尾注明：*基于传统子平命理框架，仅供文化娱乐参考。*

## 架构代码路径
所有架构代码在 `skills/bazi/bazi-foundation-analysis/architecture/` 下：
- `report_template_21s.md` — 21§标准报告模板SOP
- `workflow_engine_v2.py` — **主流程**（LangGraph状态图+Instructor强制结构化+引擎集成+校验）
- `pre_retrieval_hook.py` — Chroma前置检索（强制注入知识）
- `structured_output.py` — Pydantic输出模型（Instructor）
- `gatekeeper.py` — 校验门禁（全量硬性拦截）
- `workflow_engine.py` — 旧版v1工作流引擎（线性函数，已弃用，保留参考）
- `pipeline.py` — Prefect编排（定时任务调度）
- `langfuse_client.py` — LangFuse观测+Golden Dataset评估
- `run_test.py` — 端到端测试入口
- `trigger_layer.py` — 触发层（场景路由+上下文隔离+工具白名单）

**v2.0关键升级（2026-07-29）**：
- Instructor `response_model=AnalysisReport` 强制LLM输出固定JSON结构，非软约束
- LangGraph有向图+条件边（校验通过→输出 / 不通过→重试 / 3次不过→转人工）
- Pre-hook：`node_validate_input`为首节点，输入合法性校验
- Post-hook：3次重试不过→`human_intervention`节点，输出转人工标记
- 重试时错误反馈注入下一轮LLM prompt
- 场景路由：`SCENE_CONFIGS`按场景（事业/婚姻/财富/健康/通用）隔离System Prompt
- 上下文隔离：`TaskSession`每任务reset，杜绝Memory污染
- 工具白名单：`SCENE_TOOLS`按场景限制LLM节点可用工具
- 触发层：`TaskDispatcher`路由请求到对应场景+session分配
- LangFuse集成：dispatch时自动log各阶段
- Golden Dataset：含6个测试用例，自动评估检索覆盖率

## 引擎路径
`/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine/`
- `paipan.py` — 排盘（年柱/月柱/日柱/时柱计算+五虎遁+五鼠遁）
- `shen_qiang_ruo.py` — 身强弱（月令+天干+地支综合评分）
- `ge_ju.py` — 格局判定+喜用神+调候
- `shi_shen.py` — 十神转换
- `da_yun.py` — 大运排盘
- `liu_nian_v2.py` — 流年分析
- `xing_chong_he_hua.py` — 刑冲合害
- `generate_deep_report.py` — 21§深度报告生成器
- `pipeline_v5.py` — 引擎全量管线
