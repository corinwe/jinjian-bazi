# 报告生成器模块 — 结构化数据→命理报告

> **创建时间：** 2026-06-26
> **用途：** 将engine 21§结构化JSON转化为流畅的命理报告文字（像真人写的，不是数据展示）

## 模块位置

```
engine/report_generator.py — 16215字节
api/routers/analyze.py — POST /api/v1/report 端点
frontend/index.html — 前端渲染逻辑
```

## 核心思想

**不展示分数和字段，展示命理师口吻的分析。**

用户要的不是：
```
财星: 31.2分 | 身强: 64分
```
用户要的是：
```
命主辛金生于未月得令，身强64分，根基扎实。
财星31.2分属中富层次，财富需靠专业技能变现。
```

## report_generator.py 结构

每个§对应一个私有函数：

| 函数 | 对应§ | 行数 | 逻辑 |
|:----|:------|:----:|:-----|
| `_shen_qiang_ruo_to_text()` | §3 身强弱 | 25 | 从弱/身强≥70/身强/身弱<20各一种口吻 |
| `_xi_yong_to_text()` | §4 喜用神 | 10 | 喜用+忌五行拼接 |
| `_wealth_to_text()` | §8 财富 | 25 | 财库有无+等级描述+量级 |
| `_career_to_text()` | §10 事业 | 20 | 方向+等级+行业+创业建议 |
| `_education_to_text()` | §11 学历 | 20 | 印刷分析+年干伤官检查+文昌 |
| `_marriage_to_text()` | §12 婚姻 | 20 | 质量+窗口+配偶特征+夫妻宫 |
| `_children_to_text()` | §13 子女 | 30 | 数量+成就+生育力+缘薄因素 |
| `_health_to_text()` | §14 健康 | 25 | 体质+五行过三+冲克 |
| `_da_yun_to_text()` | §17 大运 | 30 | 列表+最佳运标注 |
| `_verdicts_to_text()` | §18 三决断 | 15 | 标题+事件拼接 |
| `_wu_xing_advice_to_text()` | §20 五行 | 20 | 颜色/方位/饰品/饮食 |
| `generate_report()` | 全部 | 80 | 主入口，按§顺序组装 |

## API端点

```
POST /api/v1/report
Body: {name, gender, birth_year, birth_month, birth_day, birth_hour}
Returns: {success, report, bazi}
```

## 字段类型安全（踩坑记录）

从engine返回的结构化数据中，部分字段可能为dict而非str：

| 字段 | 可能的类型 | 处理方式 |
|:----|:----------|:---------|
| `s13.child_count_estimate` | str或dict | dict→取`text`/`数量`/第一个值 |
| `s13.sheng_yu_potential` | str或dict | dict→取`desc`/`text` |
| `s13.thin_factors[]` | str或dict[] | 每项dict→取`text`/`desc` |
| `s11.wen_chang_ming_li` | dict | `.get("has")`判断 |

**铁律：任何从engine dict取值的字段，写`isinstance()`类型检查后再用。** 不要假设engine返回的字段类型是固定的。

## 前端渲染

前端 `/api/v1/report` 返回的 `report` 字段是Markdown格式文本，前端渲染为HTML：

- `# 标题` → 报告头部（八字+日主）
- `## 章节` → 带边框的卡片section
- `### 子节` → section内的标签
- `  · 大运` → 列表行，按评分加颜色标签
- `---` → 分隔线（页脚）

前端不解析JSON字段，不显示任何原始分数。全部由后端报告生成器处理成文字。

## 新增报告时的流程

1. engine跑出21§ JSON（通过 `/engine/debug`）
2. `report_generator.generate_report(result, name, gender)` → 得到markdown文本
3. 前端渲染markdown → 用户看到流畅的命理报告
4. 如果发现某个字段显示异常，大概率是engine返回了dict而非str → 在`report_generator.py`对应函数加类型检查

## 各§的文案风格要求

| § | 风格 | 示例开头 |
|:--|:-----|:---------|
| §1 总览 | 正式简洁 | "八字：庚申 癸未 辛亥 辛卯。日主辛金，性格精致优雅，注重品质" |
| §2 财富 | 客观分析 | "财星40.8分，属中富层次。中富之命，财富可达千万级别" |
| §3 事业 | 方向建议 | "事业方向宜走执法/军警/管理路线" |
| §4 婚姻 | 中性叙述 | "婚姻质量中等（6/10分）。最佳婚恋窗口在..." |
| §5 大运 | 列表+推荐 | "命主共8步大运：· 壬申运——❌低谷" |
| §6 五行开运 | 直接建议 | "【颜色】宜多用黄/棕/米色系" |

## 已知问题

1. **dict/str类型不一致** — engine的children模块返回部分字段为dict，report_generator需要做isinstance检查
2. **ge_ju_detail太长** — 格局字符串如"七杀格+杀印相生+食神制杀"太长时，需只取主格
3. **大运评分颜色** — 大运列表用🏆/✅/⚠️/❌评分时，配合score值（≥8/≥6/≥4/<4）
4. **空数据保护** — 任何section可能返回空，需要用`if not sXX:`检查跳过
