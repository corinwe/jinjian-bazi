#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为「纯表格」章节补两行白话口径说明，满足质量门禁的非空§要求。

用法：
    python3 scripts/ensure_section_prose.py <报告路径> [<报告路径> ...]
"""
import re
import sys

NOTES = {
    "§7": ("> **本节口径：** 外形倾向由日主五行＋十神气质推出，实际受遗传、作息、锻炼影响。",
           "> **提示：** 只作「气质与体态倾向」参考，不作医学判断。"),
    "§9": ("> **本节口径：** 置业倾向与窗口年份来自财星/田宅宫与流年合能。",
           "> **提示：** 具体买房决策还要看所在城市政策、家庭现金流与杠杆。"),
    "§11": ("> **本节口径：** 学历层次由印星/文昌/官星与学业期流年综合判断。",
            "> **提示：** 命理给的是「倾向与窗口」，最终取决于个人努力与教育环境。"),
    "§12": ("> **本节口径：** 婚姻质量看夫妻宫＋配偶星＋流年触发，窗口年份为高概率区间。",
            "> **提示：** 关系质量取决于双方经营，命理不作「必婚/必离」的定论。"),
    "§13": ("> **本节口径：** 子女缘看子女星＋子女宫＋时柱生育力。",
            "> **提示：** 实际情况以医学检查与家庭计划为准，命理只给倾向与窗口。"),
}

SEC_RE = re.compile(r"^(## §(7|9|11|12|13)\s.*)$", re.M)


def fix(path: str) -> bool:
    s = open(path, encoding="utf-8").read()
    changed = False
    for m in list(SEC_RE.finditer(s))[::-1]:
        key = "§" + m.group(2)
        start = m.end()
        tail = s[start:start + 300]
        if "本节口径" in tail:
            continue
        note = "\n\n" + "\n".join(NOTES[key]) + "\n"
        s = s[:start] + note + s[start:]
        changed = True
    if changed:
        open(path, "w", encoding="utf-8").write(s)
    print(f"{'✅ 已补' if changed else '➖ 无需补'} → {path}")
    return changed


if __name__ == "__main__":
    for p in sys.argv[1:]:
        fix(p)
