#!/usr/bin/env python3
"""
金鉴真人·引擎深度报告全面审计脚本
用法: python3 audit_report.py <报告文件路径>
"""

import re
import sys


def audit_report(fp: str) -> dict:
    with open(fp) as f:
        content = f.read()
    lines = content.split("\n")
    results = {}

    # 基础
    results["总行数"] = len(lines)
    results["§数量"] = sum(1 for l in lines if l.startswith("## §"))
    results["PIPELINE-SIG"] = "#PIPELINE-SIG" in content
    results["编制人"] = "金鉴真人" in content
    results["品牌统一"] = "九龙道长" not in content
    results["后略残留"] = "后略" not in content and "因篇幅" not in content

    # §1字段数
    in_s1 = False
    field_count = 0
    for l in lines:
        if l.startswith("## §1"):
            in_s1 = True
        elif l.startswith("## §2"):
            break
        if in_s1 and re.match(r"^\|\s*\d+\s*\|", l.strip()):
            field_count += 1
    results["§1字段"] = field_count

    # §16事件数
    s16_start = next((i for i, l in enumerate(lines) if l.startswith("## §16")), None)
    s17_start = next((i for i, l in enumerate(lines) if l.startswith("## §17")), None)
    if s16_start and s17_start:
        s16_events = sum(
            1 for l in lines[s16_start:s17_start] if re.match(r"^\|\s*\d+\s*\|", l.strip())
        )
    else:
        s16_events = 0
    results["§16事件"] = s16_events

    # 各§深度
    sec_ranges = {}
    cur = None
    for i, l in enumerate(lines):
        m = re.match(r"^## §(\d+)", l)
        if m:
            n = int(m.group(1))
            if cur:
                sec_ranges[cur] = (sec_ranges[cur][0], i)
            cur = n
            if cur not in sec_ranges:
                sec_ranges[cur] = (i, len(lines))
    if cur:
        sec_ranges[cur] = (sec_ranges[cur][0], len(lines))

    req = {6: 120, 8: 80, 11: 60, 12: 56, 14: 50, 16: 70, 17: 300, 21: 80}
    depth_results = {}
    for sn, r in sorted(req.items()):
        if sn in sec_ranges:
            depth_results[f"§{sn}"] = (sec_ranges[sn][1] - sec_ranges[sn][0], r)

    # JSON暴露
    json_leak = bool(re.search(r"\{'[^}]+'\}", content))
    results["JSON暴露"] = json_leak

    results["§深度明细"] = depth_results
    return results


def print_report(results: dict):
    print(f"总行数: {results['总行数']} {'✅' if results['总行数'] >= 1500 else '❌'}")
    print(f"§数量: {results['§数量']} {'✅' if results['§数量'] == 21 else '❌'}")
    print(f"§1字段: {results['§1字段']} {'✅' if results['§1字段'] == 25 else '❌'}")
    print(f"§16事件: {results['§16事件']} {'✅' if results['§16事件'] >= 70 else '❌'}")
    print(f"PIPELINE-SIG: {'✅' if results['PIPELINE-SIG'] else '❌'}")
    print(f"编制人: {'✅' if results['编制人'] else '❌'}")
    print(f"品牌统一: {'✅' if results['品牌统一'] else '❌'}")
    print(f"后略残留: {'✅' if results['后略残留'] else '❌'}")
    print(f"JSON暴露: {'❌ 发现JSON泄漏' if results['JSON暴露'] else '✅ 干净'}")
    print()
    for sec, (lc, r) in sorted(results['§深度明细'].items()):
        ok = lc >= r
        print(f"{sec}: {lc}行 (需≥{r}) {'✅' if ok else '⚠️'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 audit_report.py <报告路径>")
        sys.exit(1)
    results = audit_report(sys.argv[1])
    print(f"\n=== 审计报告: {sys.argv[1]} ===\n")
    print_report(results)
