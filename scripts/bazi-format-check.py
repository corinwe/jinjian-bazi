#!/usr/bin/env python3
"""
bazi-format-check.py — 八字报告格式校验器
被 ~/.hermes/hooks/bazi-mandatory/check.sh 调用
v1.0: 检查21§完整性 + 大运年龄向上取整规则 + PIPELINE-SIG签名
"""

import sys
import re

def check_report(filepath: str) -> bool:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # [1] 签名检查
    if 'PIPELINE-SIG' not in content:
        errors.append("缺少PIPELINE-SIG签名")

    # [2] 21§完整性检查
    required_sections = [
        '八字排盘', '格局', '身强弱', '喜用神',
        '财星', '文昌', '婚姻', '时柱', '性格',
        '子女', '大运喜忌|大运.*排序', '大运流年|关键事件',
        '补开财库|补财库', '补文昌|文昌方案',
        '五行补充', '关键数据'
    ]
    for section in required_sections:
        if not re.search(section, content):
            errors.append(f"缺少§板块: {section}")

    # [3] 大运年龄格式检查（禁止出现0.3~10.3岁这类小数）
    age_pattern = re.findall(r'\d+\.\d+~\d+\.\d+岁', content)
    if age_pattern:
        errors.append(f"大运年龄使用了小数格式(应为整数): {age_pattern[:3]}")

    # [4] 大运喜忌检查（禁止"双忌神"误判）
    if '双忌神' in content and '正官' in content:
        if '一喜一忌' not in content:
            errors.append("大运喜忌可能误判: 包含'双忌神'但未说明干支分开判定")

    # [5] 配偶特征检查（禁止"寅申巳亥"这种全组列举）
    if '寅申巳亥' in content:
        errors.append("配偶特征使用了'寅申巳亥'全组列举(应只提实际地支)")

    if errors:
        print("❌ 格式校验失败:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("✅ 格式校验通过")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: bazi-format-check.py <报告文件.md>")
        sys.exit(1)
    success = check_report(sys.argv[1])
    sys.exit(0 if success else 1)
