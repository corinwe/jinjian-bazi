# 金鉴真人·八字报告自动验证使用指南

> 关联 skill: bazi-calibration (三引擎架构)
> 脚本路径: `/root/.hermes/profiles/jinjian-zhenren/scripts/bazi-report-validator.py`

## 用途

在每次八字报告生成后、推库前，自动检查报告的格式完整性和逻辑一致性。

## 检查项

1. **§1 一页总览表** — 24个必填字段是否全部存在
2. **§1-§20 全部20个板块** — 标题格式是否正确（`## §N`）
3. **§16 全生命周期事件总表** — 数据行数是否≥40
4. **事件表时序** — 年份从小到大排列
5. **基础逻辑** — 称谓矛盾、同年结婚离婚等
6. **头部元数据** — 编制人/时间/版本号

## 命令

```bash
# 验证单个报告
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-report-validator.py --report <报告路径> --verbose

# 批量验证目录
python3 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-report-validator.py --dir <目录>

# Git pre-commit门禁
# 已安装到知识库 .git/hooks/pre-commit，自动触发
```

## 验证通过标准

- §1 字段 24/24 ✅
- §16 事件行数 ≥40 ✅
- §1-§20 全部存在 ✅
- 基础逻辑无矛盾 ✅

## 常见失败原因

| 失败原因 | 表现 | 修复方法 |
|:---------|:-----|:---------|
| §1字段不全 | 显示「❌ §1缺少字段: …」 | 补全§1表格到24字段 |
| 板块标题格式不对 | 显示「❌ 缺失板块 ## §N」 | 改为`## §N 标题`格式 |
| §16行数不足 | 显示「❌ §16仅X行，要求≥40」 | 扩展事件表 |
| 年份顺序异常 | 显示「⚠️ 事件表年份顺序异常」 | 检查是否有汇总表混入 |
