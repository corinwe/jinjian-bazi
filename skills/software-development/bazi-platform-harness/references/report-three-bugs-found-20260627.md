# 报告前端渲染 Bug 修复记录（2026-06-27）

> **发现来源**：老板发送两份实际生成的PDF报告（令_八字命理报告.pdf、魏源_八字命理报告.pdf），经OCR分析发现3处Bug。

---

## Bug 1: PDF导出第1页和第2页重复

**现象**：生成的PDF报告中，第1页（四柱八字+一页总览+格局分析）和第2页内容完全重复。

**根因**：`frontend/src/views/ReportPage.vue` 中 `doDownloadPDF` 方法的多页循环逻辑有bug。`html2canvas` 截图了当前视口内容，但在计算多页分页时，第一页被包含了两次。

**复现步骤**：
1. 输入生辰 → 点击「开始排盘」
2. 进入报告页 → 点击「下载PDF」
3. 查看PDF → 第1页和第2页内容相同

**修复方案**：
```javascript
// ReportPage.vue - doDownloadPDF 方法修正

// ❌ Bug版：position计算错误导致第一帧被重复
const pageH = 297
pdf.addImage(imgData, 'PNG', 0, position, pdfW, pdfH)
heightLeft -= pageH
while (heightLeft > 0) {
  position = heightLeft - pdfH + pageH  // ← 这里错了，第一帧被重复
  pdf.addPage()
  pdf.addImage(imgData, 'PNG', 0, position, pdfW, pdfH)
  heightLeft -= pageH
}

// ✅ 修正版：从第二页开始正确偏移
const pdfH = (canvas.height * pdfW) / canvas.width
let pos = 0
const pageHeight = 297  // A4高度mm
pdf.addImage(imgData, 'PNG', 0, pos, pdfW, pdfH)
pos -= pageHeight  // 向上偏移一页高度

while (pos + pdfH > 0) {
  pdf.addPage()
  pdf.addImage(imgData, 'PNG', 0, pos, pdfW, pdfH)
  pos -= pageHeight
}
```

**验证方式**：导出PDF后检查第1页和第2页内容是否不同。

---

## Bug 2: "暂无置业分析数据"与真实数据同时显示

**现象**：§9置业分析中同时出现「暂无置业分析数据」和「置业方位：喜用火→宜选南方位」。两条矛盾的文案。

**根因**：ReportPage.vue 的条件渲染逻辑有bug——引擎返回的数据中有`propertyPotential`字段，但前端在显示数据的同时也渲染了fallback文本「暂无置业分析数据」。

**修复方案**：
```html
<!-- ❌ Bug版：两个条件独立判断，fallback和data同时渲染 -->
<div v-html="secText('sec_9_property', 'detail') || '暂无置业分析数据。'" class="sec-text"></div>
<p v-if="propertyPotential">置业方位：{{ propertyPotential }}。</p>

<!-- ✅ 修正版：统一条件，有数据就不显示fallback -->
<div v-if="hasPropertyData">
  <p>置业方位：{{ propertyPotential }}。</p>
  <p>置业能力：{{ propertyLevel }}。</p>
</div>
<p v-else>暂无置业分析数据。</p>
```

---

## Bug 3: "暂无明显窗口岁"文案不通顺

**现象**：婚姻分析中显示「最佳婚恋窗口：暂无明显窗口岁。」——"窗口岁"不是标准中文表达。

**根因**：引擎返回的 `best_window_age` 字段值为「暂无」，前端直接渲染为「暂无明显窗口岁」。没有做文案包装。

**修复方案**：
```javascript
// 在computed或method中处理
formattedMarriageWindow() {
  const raw = this.marWindow
  if (!raw || raw === '暂无' || raw.includes('无明显')) {
    return '当前大运未触发明显婚姻信号'
  }
  return raw
}
```

---

## 预防措施

1. **PDF导出质量检查** — 每次修改 `doDownloadPDF` 后，必须导出至少1份PDF人工验证
2. **占位符/数据一致性检查** — 避免同时出现 fallback 文本和真实数据
3. **中文文案审查** — 所有用户可见文本需自然流畅，避免「窗口岁」类生造词
4. **自动化测试** — 用 `puppeteer` 或 `playwright` 截取报告页截图，OCR检测上述问题
