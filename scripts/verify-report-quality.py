#!/usr/bin/env python3
"""
verify-report-quality.py — 报告质量物理门禁
SOP Phase 5.6 强制校验：推库前必须通过此脚本检查
21§完整性 / ≥800行 / 数据源对齐 / 无空§
exit 0 → 通过 | exit 1 → 不通过
"""

import sys, os, re

# ─── 标准21§标题（来自 detailed-template.md） ───
STANDARD_SECTIONS = [
    '§1 一页总览表', '§2 格局分析', '§3 身强弱详解', '§4 喜用神详解',
    '§5 灾祸/疾病/搬迁', '§6 性格分析', '§7 身材外貌', '§8 财富分析',
    '§9 置业/买房', '§10 事业分析', '§11 学历分析', '§12 婚姻分析',
    '§13 子女分析', '§14 健康分析', '§15 六亲分析', '§16 事件总表',
    '§17 大运精析', '§18 三决断', '§19 运程总评', '§20 五行补充',
    '§21 人生建议',
]

MIN_LINES = 800
MIN_SECTIONS = 21

def check(path):
    failures = []
    
    # 1. 文件存在
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}")
        return False
    
    with open(path, encoding='utf-8') as f:
        content = f.read()
    lines = content.splitlines()
    
    # 2. 行数 ≥ 800
    if len(lines) < MIN_LINES:
        failures.append(f"行数不足: {len(lines)}行 < {MIN_LINES}行要求")
    else:
        print(f"✅ 行数: {len(lines)}行 ≥ {MIN_LINES}")
    
    # 3. 21§完整性
    found_sections = []
    for i, sec in enumerate(STANDARD_SECTIONS):
        # 匹配 §N 标题
        pattern = re.escape(sec[:3])  # 匹配 §1 §2 等
        if re.search(pattern, content):
            found_sections.append(sec)
    
    missing = [s for s in STANDARD_SECTIONS if s not in found_sections]
    extra = [s for s in found_sections if s not in STANDARD_SECTIONS]
    
    if missing:
        failures.append(f"缺失§: {len(missing)}个 — {' '.join(m[:2] for m in missing)}")
    else:
        print(f"✅ 21§完整: 全部找到")
    
    if len(found_sections) < MIN_SECTIONS:
        failures.append(f"§数量: {len(found_sections)} < {MIN_SECTIONS}")
    
    # 4. 每个§有内容（非空§）
    empty_sections = []
    for sec in STANDARD_SECTIONS:
        idx = content.find(sec[:3])
        if idx >= 0:
            next_section = content.find('§', idx + 3)
            section_content = content[idx:next_section] if next_section > 0 else content[idx:]
            section_lines = section_content.strip().splitlines()
            # 排除只有标题行的情况
            non_header = [l for l in section_lines if not l.startswith('##') and not l.startswith('|') and not l.startswith('---') and l.strip()]
            if len(non_header) < 2:
                empty_sections.append(sec[:3])
    
    if empty_sections:
        failures.append(f"空§: {len(empty_sections)}个§无内容")
    else:
        print(f"✅ 所有§有内容")
    
    # 5. 数据源引用
    ds_refs = re.findall(r"DS\[.*?\]|DS\['.*?'\]", content)
    if len(ds_refs) < 3:
        failures.append(f"数据源引用: {len(ds_refs)}处 < 3处最低要求")
    else:
        print(f"✅ 数据源引用: {len(ds_refs)}处")
    
    # 6. 结论报告
    if failures:
        print(f"\n❌ 未通过 ({len(failures)}项):")
        for f in failures:
            print(f"  {f}")
        return False
    else:
        print(f"\n✅ 全部通过！可进入Phase 6推库。")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 verify-report-quality.py <报告.md>")
        sys.exit(1)
    
    result = check(sys.argv[1])
    sys.exit(0 if result else 1)
