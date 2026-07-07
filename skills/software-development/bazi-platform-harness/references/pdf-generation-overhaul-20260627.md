# PDF生成全面改造（2026-06-27）

## 问题

老板用产品后导出的PDF有严重问题：
1. PDF是把HTML页面**截图**后嵌入图片的——文字不可选中、不可搜索
2. 文件大小48MB（5页PDF，每页9.6MB截图）
3. 第1页和第2页内容重复（截图时的渲染bug）
4. 老板反馈："PDF全是截屏，文字不能选"

## 解决方案

### 架构变更
```
之前：前端 html2canvas 截图 → jsPDF 嵌入图片 → 48MB
现在：后端 fpdf2 逐字写文字 → 真正的文本PDF → 210KB
```

### 新增文件
- `api/services/pdf_report.py` — PDF生成核心（JinjianPDF类 + generate_pdf_report函数 + 16个_narrative_*叙事函数）
- `api/routers/pdf_download.py` — PDF下载API路由（POST /api/v1/report/pdf）

### 修改文件
- `api/main.py` — 注册pdf_download路由
- `frontend/src/views/ReportPage.vue` — PDF下载按钮从html2canvas改为调用后端API

### 对比

| 项目 | 截图PDF（旧） | 文本PDF（新） |
|:-----|:------------|:------------|
| 文件大小 | 48MB | 210KB |
| 文字可选 | ❌ | ✅ |
| 页数 | 5页（含重复） | 24页 |
| 生成位置 | 前端浏览器 | 后端服务器 |
| 核心库 | html2canvas + jspdf | fpdf2 |
| NotoSansCJK字体 | 无 | 系统字体(210KB完整) |

## 关键教训（两个层面）

### 第一层：格式（截图→文本）【已修复】

1. **PDF必须是文本不是截图** — 老板明确说「既然是PDF就文字写上去」。
2. **Response直接返回bytes** — `StarletteResponse(content=pdf_bytes, media_type="application/pdf")` 最可靠。`StreamingResponse(io.BytesIO(...))` 会导致latin-1编码错误。
3. **fpdf2的TTC字体支持** — 用 `add_font('CJK', '', '/path/to/NotoSansCJK-Regular.ttc')` 即可，不需要额外配置。
4. **前端不需要截图依赖** — html2canvas和jspdf可以移除（保留在package.json里不影响）。
5. **中文文件名** — Content-Disposition包含中文时用RFC 5987编码，简单做法用ASCII文件名如 `report.pdf`。

### 第二层：内容组织（字段列表→连贯段落）【本会话新增·已修复】

**问题发现**：即使改成了文本PDF，老板看后说"每一段就是一句话，你觉得有1500字吗？可能就是两三百字"。
**根因**：PDF生成器把引擎的字段值一条条陈列出来，像数据库导出（403行碎片短句），没有组织成文章段落。

**解决方案：叙事函数（Narrative Function）模式**

```
❌ 错误做法（字段列表）：
  【身强弱判定】身强（64.0分）
  月令印星计40.0分
  天干比劫计20.0分
  结论：身强偏旺

✅ 正确做法（叙事段落）：
  命局身强（64.0分）。根基扎实，有一定的抗压能力和事业基础。
  适合在压力环境中成长，不宜过于安逸。
```

**实现方式**：定义16个 `_narrative_*` 函数（每个§一个），将引擎的结构化数据合并为2-3个连贯段落：

```python
def _narrative_overview(sec, r, a):
    """把散落的字段合并为一段话"""
    paras = []
    paras.append(f'命局为{status}格（{score}分）。')
    paras.append(f'格局为{geju}，为命局之纲领，主宰人生大方向。')
    paras.append(f'喜用神为{xi}，此乃命局平衡之关键，补之则运势顺遂。')
    return paras
```

**核心原则**：
- 每节输出2-3个连贯段落（不是10+个单句）
- 合并相关字段到同一段话中
- 移除【金鉴真人·规则】标注（用户不需要看）
- 移除Python dict/JSON格式泄漏
- 移除emoji（fpdf2 CJK字体不支持）
- 每节第一段必须是一句完整的概括句

**注意事项**：
- 叙事函数优先从 `detail_analysis` 字段提取长文本（这些字段内容更丰富）
- 回退策略：字段值不够时再用key_value方式展示
- 每节最多5个段落（太多会显得零碎）
- 调候用神从 `['水']` → 清洗为 `水`
- 页眉不要显示"金鉴真人·八字命理分析报告"（pdftotext提取时会污染正文统计）

## 字数审计方法

| 工具 | 命令 |
|:-----|:-----|
| 引擎内容字数 | `python3 engine/audit_report_content.py` |
| PDF实际字数 | `curl -s -o /tmp/test.pdf -X POST ... && pdftotext /tmp/test.pdf - | python3 -c "统计中文字数"` |
| 要求 | >=1,500字（实测：引擎约4,900字 / PDF约1,900～2,000字） |

**注意**：pdftotext从文本PDF提取的字数（约1,900字）少于引擎原始数据（约4,900字），因为PDF是经过筛选和组织的用户可见内容。只要>=1,500字即达标。
