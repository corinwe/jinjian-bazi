#!/usr/bin/env python3
"""
workflow_v2.py — Harness Engine 工作流定义
Workflow优先于自由Agent。每步 = 输入 + 规则 + 传感器 + 输出
"""
import json, os, yaml

# ─── Workflow定义 ───
WORKFLOW = {
    "name": "九龙道长标准报告v2",
    "version": "2.0",
    "phases": [
        {
            "id": 0,
            "name": "系统预检查",
            "type": "computational",
            "steps": [
                {"name": "检查BAZI_DATASOURCE", "action": "check_env", "param": "BAZI_DATASOURCE", "fail": "BLOCK"},
                {"name": "检查数据源字段完整性", "action": "verify_ds_fields", "fail": "BLOCK"},
            ]
        },
        {
            "id": 4,
            "name": "模块生成",
            "type": "orchestrated",
            "sections": [
                {"id": "s8", "name": "财富分析", "rule": "rules/cai_fu.yaml", "template": "templates/cai_fu.md"},
                {"id": "s10", "name": "事业分析", "rule": "rules/shi_ye.yaml", "template": "templates/shi_ye.md"},
            ]
        },
        {
            "id": 5,
            "name": "发布前校验",
            "type": "computational",
            "steps": [
                {"name": "数据源对齐", "action": "check_ds_alignment", "fail": "BLOCK"},
                {"name": "数字算术自检", "action": "check_arithmetic", "fail": "BLOCK"},
            ]
        },
    ]
}


def load_rule(path):
    """加载规则YAML文件"""
    with open(path) as f:
        return yaml.safe_load(f)


def get_ds_field(ds, path):
    """从DS按路径取值，如 '藏干十神.年支.0.十神'"""
    parts = path.split('.')
    val = ds
    for p in parts:
        if p.isdigit():
            val = val[int(p)]
        elif isinstance(val, dict) and p in val:
            val = val[p]
        else:
            return None
    return val
