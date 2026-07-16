# 2026-07-16 会话学习记录：数据源架构固化

## 关键教训

### 教训①：数据层必须先于业务层
之前每次建报告模块先写分析逻辑再想数据来源。正确顺序：先数据层(DA)→再业务层(模块从DS取数)。
老板原话：「这种简单的架构思维你都想不到吗？」

### 教训②：子代理出错根因是缺数据源
所有子代理错误（藏干财不算用/巳中庚不算/大运真假误判）都是同一根因：无统一数据源→各代理重新推导→推导不一致→出错。
解决方案：BAZI_DATASOURCE强制+pre_tool_call拦截。

### 教训③：物理机制不是可选项
写进SOP文档→老板说「文件规则靠自觉，不行」。正确做法：precheck.py在write_file前检查BAZI_DATASOURCE→不满足则BLOCK。

### 教训④：报告≠数据堆砌
老板批评「你跑出来的是基础数据不是命理分析」。报告=DS数据+规则应用=分析结论。

## 本次创建的物理机制

| 机制 | 文件 | 作用 |
|:-----|:-----|:------|
| 数据源验证+锁定 | scripts/bazi-data-source.py | engine→datasource(23字段) |
| 模块报告生成器 | scripts/report-generator.py | 所有模块从DS取数 |
| 质量门禁 | scripts/verify-report-quality.py | 检查21§/800行/DS引用 |
| pre_tool_call拦截 | hooks/bazi-mandatory/precheck.py | 检查BAZI_DATASOURCE |
| 自动设置env | hooks/bazi-mandatory/inject-context.sh | 自动检测并设置BAZI_DATASOURCE |
