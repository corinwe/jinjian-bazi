# 自动化前端输出格式 v5.0

> 本文件描述由 engine/pipeline_v5.py + report_generator.py + 前端index.html 组成的自动化报告输出体系。
> 与 SKILL.md 中的手动写报告模板互补，适用于商业化产品场景。

---

## 整体架构

```
用户输入 (出生日期+性别+时辰)
  → /api/v1/engine/debug (引擎JSON)
  → 前端 renderReport() 
  → 13§卡片式页面 + [PDF下载]
```

## 前端输出的13个§

与手动模板的21§不同，前端将数据分成了13个展示区块：

| 卡片/区块 | 数据源 | 展示方式 |
|:---------|:-------|:---------|
| 个人档案 | profile-header | 姓名·八字·性别·出生信息·日主 |
| 四柱信息表 | pillar-table | 十神/天干/地支/**藏干**/纳音/空亡 |
| 核心数据 | metrics | 身强弱·财星·格局·喜用忌神 |
| 命理分析(13段) | report-body | 一~十三分标题展示 |
| 大运走势 | dy-grid | 4×2网格卡片·颜色区分 |
| 运程曲线 | bar chart | ASCII条形图+评分 |
| 三决断 | verdicts | 标题+事件卡片 |
| 八维评分 | dim-list | 柱状进度条 |
| 五行开运 | wx-grid | 2×2网格+数字+建议 |
| 人生建议 | wx-grid | 事业/财富/健康/婚姻 |

### 命理分析13段正文

| # | 标题 | 数据源(engine) |
|:-:|:----|:---------------|
| 一 | 一页总览 | sec_1 + sec_2 + sec_3 + sec_4 |
| 二 | 财富格局 | sec_8 |
| 三 | 事业发展 | sec_10 |
| 四 | 学业学历 | sec_11 |
| 五 | 性格解析 | sec_6 (新增) |
| 六 | 身材外貌 | sec_7 (新增) |
| 七 | 婚姻感情 | sec_12 |
| 八 | 子女运势 | sec_13 |
| 九 | 健康注意 | sec_14 |
| 十 | 灾祸与化解 | sec_5 (新增) |
| 十一 | 置业分析 | sec_9 (新增) |
| 十二 | 六亲关系 | sec_15 (新增) |
| 十三 | 流年事件 | sec_16 (新增) |

## 四柱表字段（含藏干）

```
年柱     月柱     日柱     时柱
十神    十神     元男     十神
天干    天干     天干     天干
地支    地支     地支     地支
藏干1   藏干1   藏干1   藏干1   ← 新增
藏干2   藏干2   藏干2   藏干2
藏干3   藏干3   藏干3   藏干3
纳音    纳音    纳音    纳音
空亡    空亡    空亡    空亡
```

藏干数据来源：engine/pipeline_v5.py 中的 CANG_GAN_MAP 字典。

## 农历/阳历切换

- 前端提供阳历/农历选择器
- API层调用 engine/lunar.py 的 lunar_to_solar() 自动转换
- 转换后的公历日期传入 paipan.py 排盘
- 验证：农历1980年5月15日 → 公历1980年6月25日 → 八字庚申壬午己巳己巳 ✅

## PDF下载

使用 `window.print()` + `@media print` CSS 样式：
- 隐藏输入区、工具栏
- 卡片背景变白、保留金色边框
- 分页控制 (break-inside: avoid)

## 关键文件

```
engine/pipeline_v5.py       — 21§结构化输出 (含CANG_GAN_MAP)
engine/report_generator.py  — 命理报告文本生成器
engine/lunar.py             — 农历转公历 (1900-2100)
api/routers/analyze.py      — API端点: /engine/debug, /report
frontend/index.html         — 前端展示 (含全部JS渲染)
```

## 前端渲染注意事项

1. **数据格式兼容**: 部分字段(如 child_count_estimate)可能是 dict 而非 str，渲染时需用 typeof 判断
2. **四柱藏干**: pipeline_v5.py 的 run_pipeline() 输出中 pillars 已包含 cang_gan 字段
3. **运程曲线**: sec_19_overall.curve 中的 bar 是 ASCII 条形图(█░)
4. **三决断**: sec_18_verdicts 是 list of dict，不在 report-body 内展示(已独立卡片)
