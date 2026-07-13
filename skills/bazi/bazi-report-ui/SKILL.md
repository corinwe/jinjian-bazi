---
name: bazi-report-ui
version: 1.3
description: 金鉴真人·报告页前端UI设计体系。涵盖布局结构、数据绑定模式、视觉风格、移动端适配原则、Vue 3静默崩溃调试法、API数据类型防御性编程、sessionStorage注入测试法。v1.3新增API数据类型不兼容防御模式+sessionStorage注入测试法+一页总览增强绑定表。
category: bazi
tags: [frontend, ui, vue, report, mobile-first, safety]
---

# 金鉴真人·报告页前端UI设计体系

## 设计原则（老板校准·不可违背）

### P1: 简洁清晰
老板原话：「你还可以设计得更好，更简单，更简洁，清晰明了」「符合互联网产品的设计」

- 不要复制ZYDX的复杂排版 — 简化再简化
- 每个区块只呈现核心信息，不要塞满数据
- 信息密度要适中，白空间充足
- 移动端优先，卡片式布局

### P2: 四层结构
所有报告页按以下四层顺序展示：

```
① 命局总览       ← 四柱表+核心数据+五行能量
② 大运流年       ← 大运时间线+最佳/最差运+关键事件
③ 深度命理分析   ← 21§可折叠详解（仅显式computed）
④ 人生建议       ← 结构化建议（事业/财富/健康/婚姻）
```

### P3: 数据驱动，零硬编码
- 所有展示数据必须从引擎JSON提取
- 前端不做计算，只做翻译和格式化
- 引擎缺少数据时，优先修改引擎注入，不在前端伪造

### P4: 可折叠分析区
- 21§分析默认折叠，只展开1-2个关键§（如身强弱）
- 用户点击展开/收起，不刷屏
- 每个§显示标题+编号，展开后只显示前端自定义的结构化内容（标签/卡片/数据grid）
- 永不显示引擎原始 detail_analysis / description / condition 等字段

### P5: 规则符号零泄漏（老板铁律·2026-07-09校准）
老板原话：「很多节，你还把符号规则透露出来，这个不能透露，要全部修掉」

**铁律：用户端报告绝不能包含以下内容：**
- 规则标记: 如「金鉴真人·xxx规则·」
- 计算逻辑: 如「月令本气定格局」「天干透出确认」
- 规则口诀: 如「冲则动」「刑则伤」
- 内部评分体系: 如「结婚四大信号」
- 计分细则: 如「月令本气印=40分」
- 专业术语: 如「实神」「虚神」「余气」
- condition 字段: 已从引擎删除

**安全措施（两层保险）：**
1. 引擎层: run_pipeline() 中 _strip_rule_markers() 自动剥离所有标记内容
2. 前端层: 永不 fallback 到 s.description / s.analysis / s.detail 等未知字段

**正确做法**：每个§只渲染template中显式写的computed属性，禁止用通用提取方法

---

## 数据绑定模式

### 四柱表数据路径

```
pillars = data.basic_data.pillars  // { year, month, day, hour }
// 每个pillar: { gan, zhi, shi_shen, cang_gan: [], na_yin, kong_wang }
// 展示为：十神 / 天干(+五行) / 地支(+五行) / 藏干 / 纳音 / 空亡
```

### 核心数据路径

| 字段 | 数据路径 | 类型兼容 |
|:-----|:---------|:---------|
| 日主 | basic_data.ri_zhu.gan | string |
| 身强弱 | result.sec_3_shen_qiang_ruo.{label, score, details} | string / number |
| 格局 | result.sec_2_ge_ju.detail | string |
| 财星 | result.sec_8_wealth.cai_xing_total | number |
| 起运 | result.sec_1_overview.qi_yun_age | number |
| 喜用神 | result.sec_4_xi_yong.xi | string[] |
| 忌神 | result.sec_4_xi_yong.ji | string[] |
| 调候 ⚠️ | result.sec_4_xi_yong.tiao_hou | **list→string**（引擎返回`['水']`，前端需要`'水'`） |

### 深度分析（21§）数据类型兼容表（2026-07-10新增）

以下字段因引擎输出类型与前端期望不一致，需要防御性处理：

| § | computed | 引擎实际类型 | 前端期望 | 修复 |
|:-:|:---------|:------------|:---------|:-----|
| §4 | tiaoHou | `['水']` (list) | `'水'` | `if Array.isArray(v) return v[0]` |
| §6 | riZhuBase | `{gan, base, desc}` (dict) | `'性格务实...'` | `if typeof v==='object' return v.desc` |
| §9 | propertyPotential | **缺失computed**（模板引用但未定义） | `'喜用水→宜选北方位'` | 新增computed: `result.sec_9_property.property_potential` |
| §9 | propertyLevel | **缺失computed**（模板引用但未定义） | `'偏弱，需大运配合'` | 新增computed: `result.sec_9_property.property_level` |
| §13 | childAch | `{时干, 时支, 藏干信息}` (dict) | `'孩子爱学习；孩子能当官'` | `typeof v==='object' ? extractText(v) : v` |
| §18 | verdicts | `{verdicts: [{...}]}` (dict) | `[{...}]` (array) | `v.verdicts \|\| []` |

**排查方法**：当某个§展开后空白，先检查：
1. computed属性是否已定义？还是模板引用了不存在的属性？
2. 引擎返回的类型是否符合computed的预期？
3. computed返回的默认空值（`\|\| ''`）是否掩盖了「类型不匹配」的问题？

### 一页总览（§1）增强数据绑定

除基础字段外，一页总览还展示以下增强信息（2026-07-10新增）：

| 字段 | computed | 数据路径 | 说明 |
|:-----|:---------|:---------|:-----|
| 纳音 | s1NaYin | result.sec_1_overview.na_yin | Array→join('、') |
| 起运年龄 | s1QiYun | result.sec_1_overview.qi_yun_age | 原始数值 |
| 学历 | s1Edu | result.sec_1_overview.education | 去emoji前缀 |
| 详细描述 | s1Narrative | result.sec_1_overview.narrative | 完整段落文本 |

### 五行能量路径
```
energy = data.analysis.energy.wu_xing_energy  // {木: 24, 火: 4, ...}
// 渲染为横向条形图，以最大值归一化
```

### 大运数据路径
```
dyList = data.result.sec_17_da_yun_detail.list
// 每项: { gan_zhi, start_age, end_age, start_year, end_year, label, score }
// score 从 sec_19_overall.curve 映射注入（详见陷阱#1）
```

### 深度分析（21§）【安全警告：仅用显式computed，禁止secText】
每个§的数据通过独立的 computed 属性从引擎读取，只展示手动编写的结构化内容。

```
// 正确：显式绑定
<p v-if="riZhuBase"><strong>日主特质：</strong>{{ riZhuBase }}</p>
<p v-if="personalityType"><strong>性格类型：</strong>{{ personalityType }}</p>

// 禁止：从引擎回退读取未知字段
// secText('sec_6_character', 'detail') ← 危险！可能泄漏规则文本
```

---

## 视觉规范

### 主题色
- 背景: #0d0d1a (深蓝黑)
- 卡片: #252542
- 金色主色: #c9a84c
- 金色亮: #e8d48b
- 辅助文字: #8a8070
- 主文字: #e8e0d0
- 警示红: #c0392b
- 成功绿: #4caf50
- 警告黄: #ff9800

### 五行能量色
```
木: #4caf50   火: #ff5722   土: #ff9800
金: #c9a84c   水: #2196f3
```

### 组件样式
- 卡片: 圆角10px，半透明背景，1px边框
- 按钮: 圆角20px，金色渐变主按钮/透明描边次要按钮
- 四柱表: 紧凑表格，天干/地支用大字号(18px)，十神带颜色标记
- 核心数据: 3列grid，深色背景圆角块
- 大运: 左侧4px指示器色条，右内容区，color-coded
- 可折叠块: 左侧编号圆形徽标，点击展开

---

## Silent Component Crash 调试法（v1.2新增，v1.3扩展）

**问题描述**: ReportPage.vue 加载后只显示页头和页脚，内容区完全空白（不是空状态提示）。浏览器控制台无 JS 报错 — Vue 静默吞噬了渲染异常。

**诊断流程（三步渐进消除法）**：

### 步骤 1：确认组件是否加载成功
创建 MinimalTestReport.vue（仅包含纯静态模板 + data 空状态），替换 route 中的 ReportPage 引用：
```javascript
// router/index.js — 临时替换
{ path: '/report', component: () => import('../views/TestReport.vue') },
```
- ✅ 显示 → 组件加载机制正常，问题在 ReportPage 内部
- ❌ 不显示 → 路由/懒加载/构建问题

### 步骤 2：归零法验证缓存
```javascript
// 浏览器 navigation — 加 querystring 避免缓存
browser_navigate(url='http://127.0.0.1:8000/?t=TIMESTAMP#/report')
// 重建后验证 dist/index.html 中 JS bundle hash 已更新
```
- 经常需要硬清除浏览器缓存才能使新构建生效

### 步骤 3：用三个元素数量区分渲染状态
使用 browser_snapshot 的 `element_count` 快速诊断：

| element_count | 含义 | 可信度 |
|:-------------|:-----|:-------|
| **恰好 3** | 页头（logo + 2 nav links）仅渲染，组件静默崩溃 | ⭐⭐⭐ |
| 5-8 | 简化版组件（TestReport）可见，但原始组件内容区未渲染 | ⭐⭐⭐ |
| 7-10 | 空状态渲染（工具栏 + "暂无报告数据" + "返回输入"链接） | ⭐⭐⭐ |
| 30+ | 完整报告内容渲染（40-60 元素为典型值） | ⭐⭐⭐ |

再配合 browser_vision（截图 + "What does the report page look like?"）交叉确认。
注意：browser_vision 有时因 `/tmp/agent-browser-*/_stdout_screenshot` 路径问题在 local 模式下失败，此时依赖 browser_snapshot 的 element_count 做判断。

### 可能的 Vue 3 静默崩溃原因

| 原因 | 现象 | 检查方法 |
|:-----|:-----|:---------|
| **v-if + v-for 同元素** ⚠️最常见 | Vue 3 中 `v-if` 优先级高于 `v-for`，当 `v-if` 引用 `v-for` 迭代变量时组件崩溃。页头可见但内容区空白，element_count=3 | grep -n 'v-if.*v-for\\|v-for.*v-if' *.vue 排查同元素共存情况（注意：`v-if`在父元素、`v-for`在子元素是安全的，无需修改） |
| **setup() + Options API 混用** | `setup()` 返回闭包函数，`methods` 中用 `this.xxx()` 调用。Vue 3 暴露到 `this` 但某些构建优化可能破坏引用 | 将 `setup()` 函数统一移到 `methods` |
| **sessionStorage 数据过大** | >5MB 或含循环引用，`JSON.stringify` 自动失败 | 检查数据大小 < 100KB |
| **sessionStorage 跨域丢失** | 使用 `http://127.0.0.1` 和 `http://localhost` 是不同域 | 保持域名一致 |

**修复模板中 v-if + v-for 共生（标准写法）**：
```html
<!-- ❌ 错误：v-if 和 v-for 在同一元素 -->
<div v-for="wx in wxOverThree" v-if="wx.wx" :key="wx.wx">
  ⚠️ 五行<strong>{{ wx.wx }}</strong>过旺
</div>

<!-- ✅ 正确：用 <template> 包装分离 -->
<template v-for="wx in wxOverThree" :key="wx.wx">
  <div v-if="wx.wx" class="health-warn">
    ⚠️ 五行<strong>{{ wx.wx }}</strong>过旺
  </div>
</template>

<!-- ✅ 也正确：computed 预过滤 -->
<div v-for="wx in filteredOverThree" :key="wx.wx">
  ⚠️ 五行<strong>{{ wx.wx }}</strong>过旺
</div>
```

---

## sessionStorage注入测试法（v1.3新增）

**适用场景**：需要测试报告页渲染效果，但不想每次都手动填表单提交API。直接往 sessionStorage 注入 API 数据后导航到 `#/report`。

### 通过测试HTML注入（推荐）

1. 用API获取真实数据，加 `_meta` 字段
2. 生成独立的 `test-load.html` 放在 `frontend/dist/`
3. 在 `<script>` 中直接赋值 `sessionStorage.setItem('lastReport', JSON.stringify(data))`
4. 导航到 `http://host/test-load.html#/report` 查看渲染效果

```python
# 生成脚本示例
import json, requests
from hermes_tools import write_file, terminal

# 获取API数据
r = requests.post('http://localhost:8000/api/v1/engine/debug', json={...})
data = r.json()
data['_meta'] = {'name': '印', ...}

# 获取dist最新的JS hash
assets = os.listdir('frontend/dist/assets/')
index_js = [f for f in assets if f.startswith('index-') and f.endswith('.js')][0]
index_css = [f for f in assets if f.startswith('index-') and f.endswith('.css')][0]

# 生成测试HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8">
<link rel="stylesheet" crossorigin href="/assets/{index_css}">
</head>
<body><div id="app"></div>
<script>
var d = {json.dumps(data, ensure_ascii=False)};
sessionStorage.setItem('lastReport', JSON.stringify(d));
window.location.hash = '/report';
</script>
<script type="module" src="/assets/{index_js}"></script>
</body></html>'''

write_file('frontend/dist/test-load.html', html)
```

### 直接在浏览器中注入

通过 `browser_console(expression=...)` 在页面上下文中执行（需要 `browser.allow_unsafe_evaluate: true` 配置）：

```javascript
sessionStorage.setItem('lastReport', JSON.stringify(data));
window.location.hash = '/report';
```

### 注意事项
- 测试HTML中的JS hash必须与 `vite build` 最新产出的hash一致，否则模块加载失败
- 重建（`npx vite build`）会清空 `dist/` 目录（`emptyOutDir: true`），测试HTML需重新生成
- `browser_navigate` 不能直接设置 sessionStorage，所以必须通过独立HTML注入

---

## 常见陷阱

### 1. 引擎缺少前端需要的数据
问题: sec_17_da_yun_detail 原本没有 score 字段
解决: 修改 pipeline_v5.py 添加 _calc_dy_score() 从 sec_19_overall.curve 映射注入
教训: 前端需求 → 优先改引擎输出层，不在前端伪造计算

### 2. 四柱数据来源不一致
问题: 不同API端点(/analyze vs /engine/debug)返回数据路径不同
解决: 前端使用 basic_data.pillars 路径（engine/debug返回），兼容 result.sec_1_overview 降级

### 3. 规则符号泄漏（2026-07-09致命教训）
问题: 前端secText()降级读取会泄漏引擎内部detail_analysis文本，包含规则标记
后果: 用户端看到底层计算规则「月令本气定格局」「金鉴真人·身强弱规则」等
解决:
  - 引擎层: run_pipeline() 增加 _strip_rule_markers() 自动剥离标记
  - 前端层: 删除全部 secText() 调用，删除全部 sec-detail-text div
  - 前端层: 删除 condition / description / analysis 等回退读取
  - 前端层: 每个§只写显式 computed + template 绑定
验证: grep -r 'secText|sec-detail-text' 应该零命中

### 4. 浏览器原生date input自动化困难
问题: Headless Chrome 原生 input type=date 不易通过browser_*工具操作
解决: 测试验证主要通过 curl/API 完成；前端效果建议用户实地操作验证

### 5. API数据类型不兼容 — 前端防御性编程（2026-07-10新增）

**问题描述**: 引擎输出层的某些字段返回的数据类型与前端 computed 属性期望的类型不一致，导致 `{{ }}` 显示为 `[object Object]`、`[水]`、或空白。

**根因**: 引擎在逐步重构过程中，同字段的输出格式在不同模块间有差异。前端 computed 属性用 `|| ''` 兜底，但未处理「值存在但类型不对」的情况。

**通用修复模式（`bazi-safe-str`）**：

```javascript
// 字符串安全提取 — 兼容 string / list / dict
function baziSafeStr(v) {
  if (!v) return ''
  if (Array.isArray(v)) return v[0] || ''
  if (typeof v === 'object') return v.desc || v.base || v.text || ''
  return String(v)
}
```

**排查方法（三步）**：
1. 用 `/api/v1/engine/debug` 获取该八字完整JSON
2. 检查 `result.sec_N_xxx` 对应字段的实际 `type()` 和 `repr()`
3. 如果前端 `v-if` 不显示 → 查 computed 返回值是否为 falsy（空字符串/空数组/undefined），即使引擎数据不为空

**预防**：每次新增 computed 属性时，先用 API 实际数据验证类型，不要在模板中写 `v-if="xxx"` 而不验证 xxx 的返回值类型。

### 6. 缺失computed属性（2026-07-10新增）

**问题描述**: 模板中引用了 `v-if="propertyPotential"` 和 `{{ propertyPotential }}`，但 computed 中根本没有定义 `propertyPotential()`。`v-if` 永为 false → 内容空白。

**根因**: 开发过程中，模板先写好了数据展示逻辑（`v-if="xxx"`），但对应的 computed 属性忘记添加。

**排查方法**: 搜索模板中所有 `{{ xxx }}` 和 `v-if="xxx"` / `v-for="x in xxx"` 中的变量名，逐一确认 `computed: {}` 中都有定义。

**快速验证命令**:
```bash
# 提取模板中所有引用的变量名
grep -oP '\{\{\s*\K[^}\s.]+(?=\s*\|?\s*}})' ReportPage.vue | sort -u
grep -oP 'v-if="\K[^"\s.]+' ReportPage.vue | sort -u
grep -oP 'v-for="\s*\w+\s+in\s+\K[^"\s]+' ReportPage.vue | sort -u

# 提取computed中定义的属性名
grep -oP '^\s{4}\K\w+(?=\(\))' ReportPage.vue | sort -u

# 对比两组名称 — 差异即缺失的computed
```

---

## 工作流

1. 确认前端需要的所有数据字段在引擎输出中是否存在
2. 缺失则修改 pipeline_v5.py 的 run_v5() 输出层注入
3. 设计布局：四层结构（总览→大运→分析→建议）
4. 实现组件：表格→数据grid→条形图→时间线→折叠块
5. （2026-07-09新增）删除所有 secText() 调用，每个§只做显式computed绑定
6. 验证零规则泄漏：检查无 sec-detail-text div、无 secText()、无 condition 引用
7. 验证所有模板引用的 computed 均已定义（无缺失computed）
8. 验证 API 数据类型兼容性（list vs string, dict vs string, dict vs array）
9. 移动端适配：grid改列、字号微调、间距压缩
10. 构建发布：npm run build → 重启uvicorn → 验证API
