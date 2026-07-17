# Harness Engine 架构
> 2026-07-16 搭建。基于 Harness Engineering 论文（Agent=Model+Harness）。
> 目标：规则独立化、模板标准化、验证自动化、飞轮自进化。

## 目录结构

```
skills/bazi/harness-engine/
├── workflow/
│   └── workflow_v2.yaml      # Phase 0-6 流程定义
├── rules/                    # 规则独立YAML文件
│   ├── cai_fu.yaml           # 财富分析(含开财库)
│   ├── shi_ye.yaml           # 事业分析
│   ├── overview.yaml         # 一页总览
│   ├── geju.yaml             # 格局分析
│   └── ... (共24个§)
├── templates/                # 输出模板(.md)
│   ├── cai_fu.md
│   ├── shi_ye.md
│   └── ... (对应24个§)
├── engine/
│   ├── workflow_v2.py        # Python工作流定义
│   └── step_runner.py        # 通用步骤执行器
└── test_suite/               # 评估集(L3飞轮用)
    └── (待添加测试用例)
```

## 工作流定义(workflow_v2.py)

每个Phase有明确的steps或sections：
- Phase 0: 系统预检查（检查BAZI_DATASOURCE+数据源字段）
- Phase 4: 模块生成（24个§逐步执行）
- Phase 5: 发布前校验（check_ds_alignment+check_arithmetic）

每步=输入schema+规则文件+模板+输出schema。

## 规则应用方式

```python
# 旧模式(已弃用) — 规则硬编码在Python if-else中
def apply_cai_fu_rules(ds):
    if '身强' in ds['身强弱']['等级']:
        result['shen_analysis'] = '身强喜财...'  # 改规则=改代码
    ...

# 新模式 — 规则从YAML加载
rule = yaml.load('rules/cai_fu.yaml')
for r in rule['rule']['shen_rules']:
    if condition.match(ds, r):
        result['shen_analysis'] = r['text']  # 改规则=改YAML
```

## 数据源引用规范

| 旧(不安全) | 新(安全) |
|:-----------|:---------|
| `DS['8字段'][0]` | `DS['年干']` |
| `DS['8字段'][1]` | `DS['月干']` |
| `DS['8字段'][5]` | `DS['月支']` |
| `B8[2]` | `DS['日干']` |

## 传感器(验证)

- check_ds_alignment: 完整报告检查八字和身强弱分数
- check_min_lines: 完整报告检查行数>=800
- check_cai_fu: 财富分析检查含财星/财富关键词
- check_shi_ye: 事业分析检查含事业/行业关键词

## 与旧体系的衔接

Harness Engine 不是替代现有体系，而是增加一个「规则驱动」的报告生成模式。
现有gen_report_v4.py仍可用作快速原型，但正式报告使用Harness Engine模式。
