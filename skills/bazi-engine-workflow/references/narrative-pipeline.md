# 叙事引擎管线 — 方案B：引擎层输出命理师口吻连贯文字

> 创设日期：2026-06-27  
> 触发：老板反馈报告中文字是"每段一句话"而非文章段落  
> 老板原话：*"我我做事的逻辑要解决根本问题"*  
> 方案A（被拒）：在PDF层拼凑字段成段落  
> 方案B（采用）：在引擎层直接输出命理师口吻的连贯分析文字

## 架构

```
确定性规则引擎 (comprehensive_v2.py + 各模块)
    ↓ 输出结构化数据 ({label, score, details, list, ...})
叙事生成器 (engine/narratives.py)
    ↓ 21个章节的 narrative_* 函数
    ↓ 输入结构化数据 → 输出150-500字段落
叙事集成层 (engine/narrative_integration.py)
    ↓ add_narratives(result)
    ↓ 遍历result，为每节附加 narrative 字段
pipeline_v5.py run_pipeline()
    ↓ 在 attach_detail_analysis() 之后、output构造之前
    ↓ from narrative_integration import add_narratives
    ↓ result = add_narratives(result)
API层 (/api/v1/engine/debug 等)
    ↓ 返回带 narrative 的JSON
PDF生成器 (api/services/pdf_report.py)
    ↓ 优先读取 sec_*.narrative 字段，直接输出
    ↓ 降级：无narrative时用PDF层的_narrative_*函数
```

## 关键文件

| 文件 | 用途 | 改内容风格改这里 |
|:-----|:------|:----------------|
| `engine/narratives.py` | **全部21个叙述函数** | ✅ **是的** |
| `engine/narrative_integration.py` | add_narratives(result) 适配层 | ❌ 不 |
| `engine/pipeline_v5.py` (run_pipeline) | 调用点（line 618后） | ❌ 不 |
| `api/services/pdf_report.py` | PDF生成器，消费narrative | ❌ 不 |

## 各章节叙述函数清单（21§全覆盖）

| 函数 | 章节 | 输入参数 |
|:-----|:-----|:---------|
| narrative_overview | §1 一页总览 | bazi, ri_zhu, ri_zhu_wx, gender, shen_label, shen_score, ge_ju_detail, xi_yong, ji_shen, cai_total, wealth_level, tiao_hou |
| narrative_ge_ju | §2 格局分析 | ge_ju_main, ge_ju_detail, bazi, ri_zhu, shen_label, shen_score |
| narrative_shen_qiang_ruo | §3 身强弱 | shen_label, shen_score, shen_detail |
| narrative_xi_yong | §4 喜用神 | xi_yong, ji_shen, tiao_hou |
| narrative_zai_huo | §5 灾祸 | misfortune_full, chong, xing, hai, remission_advice |
| narrative_character | §6 性格 | ri_zhu, ri_zhu_wx, shen_label, shen_score, ge_ju_main, xi_yong, ji_shen, character_data |
| narrative_appearance | §7 外貌 | ri_zhu, ge_ju_main, shen_label |
| narrative_wealth | §8 财富 | cai_total, wealth_level, cai_ku, xi_yong, ji_shen, shen_label |
| **narrative_property** | **§9 置业分析** | **property_data: dict（含property_potential/level/windows/risk）** |
| narrative_career | §10 事业 | career_data, ge_ju_main, ge_ju_detail, shen_label, shen_score, xi_yong |
| narrative_education | §11 学历 | education_result, shen_label |
| narrative_marriage | §12 婚姻 | marriage_result, ri_zhu, gender |
| narrative_children | §13 子女 | children_data, ri_zhu |
| narrative_health | §14 健康 | health_data, ri_zhu, shen_label |
| narrative_family | §15 六亲 | family_data, ri_zhu |
| narrative_events | §16 流年 | key_events |
| **narrative_da_yun_detail** | **§17 大运详批** | **dy_data: dict（含list/best_idx/worst_idx）** |
| **narrative_verdicts** | **§18 三决断** | **verdicts: list（含title/event/time/reason/degree）** |
| **narrative_da_yun_curve** | **§19 运程总评** | **dy_curve_data: dict（含curve数组）** |
| **narrative_wu_xing_advice** | **§20 五行补充** | **wx_data: dict（含xi_yong_wx/colors/directions/jewellery/diet/numbers）** |
| **narrative_life_advice** | **§21 人生建议** | **advice_data: dict（含career/wealth/health/marriage/social）** |

> **粗体 = 2026-06-27新增**。原是PDF层降级处理，现已全部升级为引擎层narrative，总计1,500+字。

## 与 detail_analysis 的关系

两者都是引擎生成的确定性文本，但面向不同受众：

| 维度 | detail_analysis | narrative |
|:-----|:---------------|:----------|
| 生成方式 | `_gen_detail_analysis.py` | `narratives.py` |
| 受众 | 内部审计（含规则标记） | 最终用户 |
| 标记 | 含【金鉴真人·规则名】 | 无标记 |
| 风格 | 推导过程+结论 | 命理师口吻连贯段落 |
| PDF导出 | 不显示（debug模式可见） | 直接展示 |

## 扩展方法（三文件模式）

每新增一个叙事章节需要改动3个文件：

### Step 1: 在 `engine/narratives.py` 写函数

```python
def narrative_xxx(sec_data, ...) -> str:
    """§N 章节名"""
    if not sec_data:
        return '暂无数据。'
    parts = []
    # ... 从结构化数据中提取字段，组装为连贯段落 ...
    # 使用工具函数 _c() 清理Python语法字符
    # 使用 _l() 合并列表为字符串
    # 用 f-string 构建自然语言
    return ''.join(parts)
```

### Step 2: 在 `engine/narrative_integration.py` 的 `add_narratives()` 中接入

```python
# 导入新函数
from narratives import narrative_xxx

# 在add_narratives函数体中加入：
sN = result.get("sec_N_xxx", {})
if sN:
    sN["narrative"] = narrative_xxx(sN)
```

**⚠️ §18 特例（list类型）：**
```python
s18 = result.get("sec_18_verdicts", [])
if isinstance(s18, list):
    # list→包装为dict，不能直接在list上挂字段
    result["sec_18_verdicts"] = {"verdicts": s18, "narrative": narrative_verdicts(s18)}
elif isinstance(s18, dict):
    s18["narrative"] = narrative_verdicts(s18.get("verdicts", []))
```

### Step 3: 在 `api/services/pdf_report.py` 中增加支持

PDF的 `sections` 列表只包含 §1-16。§17-21 在单独渲染块中，需要分别加narrative支持：

```python
# 大运走势块
dy_detail = r.get("sec_17_da_yun_detail", {})
if dy_detail.get("narrative"):
    for line in dy_detail["narrative"].split('\n'):
        pdf.body_text(line)

# 三决断块
verdicts = r.get("sec_18_verdicts", [])
if isinstance(verdicts, dict) and verdicts.get("narrative"):
    for line in verdicts["narrative"].split('\n'):
        pdf.body_text(line)

# 运程总评块
s19 = r.get("sec_19_overall", {})
if s19.get("narrative"):
    for line in s19["narrative"].split('\n'):
        pdf.body_text(line)

# 五行开运块
wx = r.get("sec_20_wu_xing_advice", {})
if wx.get("narrative"):
    for line in wx["narrative"].split('\n'):
        pdf.body_text(line)

# 人生建议块
s21 = r.get("sec_21_advice", {})
if s21.get("narrative"):
    for line in s21["narrative"].split('\n'):
        pdf.body_text(line)
```

每个PDF渲染块还应保留降级fallback（无narrative时的旧逻辑）。

### 验证方法

```python
# 直接测试narrative函数
from engine.narratives import narrative_xxx
text = narrative_xxx(test_data)
assert len(text) >= 150

# 通过engine/debug端点验证
curl -s -X POST http://localhost:8000/api/v1/engine/debug \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","gender":"男","birth_year":1980,"birth_month":6,"birth_day":25,"birth_hour":2}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['result']; s=r['sec_N_xxx']; print(len(s.get('narrative','')))"
```

## 列表型章节叙事模式（2026-06-27经验沉淀）

部分章节的数据结构是**列表/数组**而非简单键值对，叙事函数需要「遍历+聚合」模式：

| 章节 | 数据源 | 叙事策略 |
|:-----|:-------|:---------|
| §16 流年 | `key_events: dict[str, list[dict]]` | 遍历所有事件，按年份排序，取前10条输出 |
| §17 大运 | `list: [gan_zhi, score, gan_ss, ...]` | ①挑最佳/最差大运 ②聚合十神出现频率 |
| §18 决断 | `verdicts: list[dict]` | ①逐条提取title/event/time/reason ②跨条聚合degree字段做综合判断 |
| §19 运程 | `curve: [da_yun, age, score, bar]` | ①分段(青壮年/中年/晚年) ②每段计算平均分 ③总体趋势(前后半段对比) |

**聚合模式代码模板：**

```python
def narrative_xxx(data: list[dict]) -> str:
    parts = []
    
    # ① 通用概述
    parts.append(f'该章节涉及{len(data)}项数据...')
    
    # ② 提取极值
    if len(data) >= 2:
        best = max(data, key=lambda x: x.get("score", 0))
        worst = min(data, key=lambda x: x.get("score", 0))
        parts.append(f'最佳为{best.get("name","")}（评分{best.get("score","")}），最差为{worst.get("name","")}（{worst.get("score","")}）。')
    
    # ③ 分段/分组聚合
    segments = {"高分段": [], "低分段": []}
    for item in data:
        if item.get("score", 0) >= 7:
            segments["高分段"].append(item)
        else:
            segments["低分段"].append(item)
    if segments["高分段"]:
        parts.append(f'高分段共{len(segments["高分段"])}项，表现突出。')
    
    # ④ 跨项统计
    categories = {}
    for item in data:
        cat = item.get("category", "")
        categories[cat] = categories.get(cat, 0) + 1
    if categories:
        top_cat = max(categories, key=categories.get)
        parts.append(f'以{top_cat}类型最多（共{categories[top_cat]}项）。')
    
    return ''.join(parts)
```

**与键值对章节的对比：**

| 维度 | 键值对章节（§1-§8, §10-§15） | 列表章节（§16-§19） |
|:-----|:----------------------------|:------------------|
| 数据结构 | `{label, score, detail, ...}` | `[item1, item2, ...]` 或 `{curve: [...]}` |
| 叙事手法 | 直接提取字段转为自然语言 | 遍历→极值→分组→统计→趋势 |
| 风险 | 字段内容重复（如level原文含汉字） | 数据太少时无意义、需降级处理 |
| 字数保障 | 300-500字/节 | 数据量少时可能仅100-150字，需补充一般性分析 |

## API端点与narrative可达性（2026-06-27）

**重要：并非所有API端点都返回narrative文本。**

| 端点 | 返回narrative？ | 说明 |
|:-----|:---------------|:-----|
| `POST /api/v1/engine/debug` | ✅ **完整返回** | `result`字段含全部21§的narrative |
| `POST /api/v1/report` | ✅ **间接可用** | 通过PDF生成器消费narrative |
| `POST /api/v1/analyze` | ❌ **不返回** | 只返回`analysis`中的特定字段（shen_qiang_ruo/cai_xing/ge_ju等），不含`result` |

**根因：** `AnalysisService.analyze()` 从引擎输出中只提取了 `engine_result['analysis']` 中的7个字段存入数据库，`engine_result['result']`（含21§+narrative）被丢弃。

**影响：** 标准分析流程（前端→/analyze→展示）看不到narrative文本。只有调试端点或报告端点能获取。

**修复方向（如需要）：** 在 `AnalysisService.analyze()` 中将 `engine_result['result']` 存入数据库的 `analysis.results_json` 字段，并在 `AnalyzeResponse` 中返回。

## 常见陷阱

- ⚠️ **叙述函数不能抛出异常** → 用空字符串降级，函数体内部try/except保护
- ⚠️ **叙述文字不应含Python dict/json格式** → 用 `_c()` 工具函数清理 `[` `]` `'` `"` 等字符
- ⚠️ **叙述文字不应含规则标记**（【金鉴真人·规则名】）→ 那些在detail_analysis里
- ⚠️ **字数控制**：每节150-500字为宜，超过500字应考虑分段（用 `\n` 分隔）
- ⚠️ **§18 是list类型**（其他章节都是dict）→ narrative_integration需要特殊处理，PDF渲染也要优先检查narrative字段而非直接遍历list
- ⚠️ **PDF的§17-21不在sections循环中** → 它们有独立的渲染块（大运/三决断/八维/五行/建议），每个块都需要单独加narrative支持
- ⚠️ **避免level字段内容重复** → 当 `property_level` = "中，有能力购房自住" 时，不要输出"置业能力中等，中，有能力购房自住"，用描述替换原文
- ⚠️ **PDF渲染的indentation陷阱** → 在 `if/else` 分支中嵌入 `for` 循环时，else分支的正确缩进容易被破坏，每次修改后必须运行 `python3 -c "import py_compile; py_compile.compile('api/services/pdf_report.py')"`
