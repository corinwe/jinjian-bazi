# report_generator.py — 确定性命理报告生成器 v2

## 定位

`engine/report_generator.py` 将21§结构化数据 → 流畅的八字命理报告。
与手动写报告互补：手动=深度定制版，自动=快速标准版。

## 使用方式

### API调用
```
POST /api/v1/report
Body: {name, gender, birth_year, birth_month, birth_day, birth_hour, calendar_type}
返回: {success, report(文本), bazi, analysis_id}
```

### 前端集成
前端调用 `/api/v1/report` 获取报告文本，也可以用 `/api/v1/engine/debug` 获取完整JSON后自行渲染卡片式布局。

## 前端选择建议

| 场景 | 推荐方式 |
|:----|:---------|
| 快速出报告 | /api/v1/report → 直接显示文本 |
| 需要卡片布局 | /api/v1/engine/debug → 前端从JSON渲染 |
| 高定制UI | debug + 前端自定义渲染 |
| API集成 | /api/v1/report → 返回markdown文本 |

## 2026-06-26关键更新

前端改为调用 engine/debug 获取完整JSON后自行渲染卡片布局，
而不是直接显示 report_generator 的文本输出。
同时API层新增 calendar_type 参数处理农历→公历转换。
