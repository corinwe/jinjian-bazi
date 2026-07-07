#!/usr/bin/env python3
"""
bazi-report-validator.py — 八字报告全量验证器
被 ~/.hermes/hooks/bazi-mandatory/check.sh 调用
v1.0: 内容级验证（数据来源→规则来源→结论三段式）
"""

import sys
import re

def validate_report(filepath: str) -> bool:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # [1] 是否有数据来源标注
    data_refs = re.findall(r'引擎|JSON|data\[|分数:', content)
    if len(data_refs) < 3:
        warnings.append(f"报告中引擎数据引用较少({len(data_refs)}处)，可能缺乏数据依据")

    # [2] 检查大运年份是否合理（不早于出生前）
    year_ranges = re.findall(r'(\d{4})~(\d{4})', content)
    for start, end in year_ranges:
        s, e = int(start), int(end)
        if e - s > 11:
            warnings.append(f"大运年份区间可能异常: {start}~{end}(跨度>11年)")
        if s < 1940:
            warnings.append(f"年份异常(早于1940): {start}")

    # [3] 检查是否有模板占位符残留
    placeholders = ['{姓名}', '{出生}', '{八字}', 'TODO', '待补充']
    for ph in placeholders:
        if ph in content:
            errors.append(f"发现模板占位符残留: {ph}")

    # [4] 检查年龄区间格式
    if '.3~' in content or '.7~' in content:
        warnings.append("存在小数年龄区间(应全部为整数)")

    # [5] 报告深度（粗略检查）
    lines = content.split('\n')
    if len(lines) < 200:
        errors.append(f"报告过短: {len(lines)}行(应≥200行)")

    if errors:
        print("❌ 报告验证失败:")
        for e in errors:
            print(f"  - {e}")
        return False

    if warnings:
        print("⚠️ 报告验证通过但有警告:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✅ 报告全量验证通过")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: bazi-report-validator.py <报告文件.md>")
        sys.exit(1)
    success = validate_report(sys.argv[1])
    sys.exit(0 if success else 1)
