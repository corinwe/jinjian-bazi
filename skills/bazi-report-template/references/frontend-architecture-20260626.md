# 前端架构设计模式（2026-06-26实战沉淀）

> 来源：金鉴真人平台1426会话 · 老板多次纠正前端展示

## 三组架构

```
用户浏览器 (index.html SPA)
  | 输入出生日期 + 选择阳历/农历
FastAPI (:8000)
  +-- / → 前端静态页面 (index.html)
  +-- /api/v1/engine/debug → 返回21§完整JSON（前端渲染）
  +-- /api/v1/report → 返回标准格式命理报告文字
  +-- /api/v1/analyze → 完整分析+存数据库
  +-- /ping → 健康检查
        |
  engine/ (12,437行确定性代码)
  +-- paipan.py → 排盘（基准日法：2000-01-01=戊午）
  +-- shen_qiang_ruo.py → 身强弱（印40/0/0规则）
  +-- cai_xing.py → 财星（年干8分/月干12分规则）
  +-- career_v2.py / wealth_v2.py / marriage_v2.py / education_v2.py
  +-- health_v2.py / children_v2.py / misfortune_analysis.py
  +-- pipeline_v5.py → 21§编排主入口
  +-- report_generator.py → 结构化数据→命理报告
  +-- lunar.py → 农历转公历（1900-2100年数据表）
  +-- tests/test_full_suite.py → 320个自动化测试
```

## 前端数据流

用户填表 → doAnalyze() → fetch(/api/v1/engine/debug) → 得到完整JSON → renderReport(data) → 从JSON提取各§数据 → 渲染HTML

## 前端架构设计要点

### 1. 页面结构

顶部报告头部卡（个人档案+八字）→ 四柱信息表（卡片）→ 核心数据（卡片）→ 命理分析（卡片·13段）→ 大运走势（4x2网格）→ 运程曲线 → 三决断 → 八维评分 → 五行开运 → 人生建议 → [PDF下载]

### 2. CSS设计系统

```css
:root{
  --g:#c9a84c;  /* 金色 */
  --d:#1a1a2e;  /* 深紫背景 */
  --c:#252542;  /* 中紫卡片 */
  --t:#e8e0d0;  /* 米白文字 */
  --m:#8a8070;  /* 灰 */
  --b:#0d0d1a;  /* 深黑 */
  --a:#c0392b;  /* 红警示 */
}
```

### 3. 数据来源对照

| 数据 | 来源 | 展示位置 |
|:----|:-----|:---------|
| 八字bazi | pp.bazi | 报告头部 |
| 姓名/性别/日期/时辰 | 用户输入 | 报告头部 |
| 四柱十神/天干/地支/藏干/纳音/空亡 | bd.pillars.* | 四柱信息表 |
| 身强弱/分数 | s3.label, s3.score | 核心数据卡 |
| 财星 | s8.cai_xing_total | 核心数据卡+§8 |
| 格局 | s2.detail | 核心数据卡+§2 |
| 喜用/忌 | s4.xi, s4.ji | 核心数据卡 |
| 大运列表 | s17.list | 大运走势卡+§17 |
| 维度评分 | a.dimensions{} | 八维评分卡 |
| 三决断 | s18[] | 三决断卡 |
| 五行开运 | s20.* | 五行开运卡 |
| 人生建议 | s21.* | 人生建议卡 |
| 各§分析 | s5~s16 | 命理分析正文 |

### 4. PDF打印

使用 window.print() + @media print 实现，不依赖第三方库。打印样式需覆盖：背景色变白、文字变黑、隐藏交互元素、卡片break-inside:avoid。

### 5. 踩坑记录

1. JS用//注释，不能用#（Python习惯带进来的）
2. 字段类型不固定：engine可能返回dict而非str，前端必须 typeof x=='object'?x.text||x.数量||'':x
3. 农历转换后八字会不同——这是正确行为
4. @media print中CSS变量不可用，需直接写颜色值
5. 四柱表需要藏干cang_gan字段，如果pipeline没返回需手动添加
