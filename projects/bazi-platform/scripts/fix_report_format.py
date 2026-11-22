#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""报告格式补齐：头部元数据 + §16.9 九类事件索引。

用于通过 pre-commit 的 21§ 报告校验（bazi-report-validator.py）。

用法：
    python3 scripts/fix_report_format.py <姓名> <报告路径>
"""
import os
import re
import sys

CATS = [
    ("学业", ["学业", "文昌"]),
    ("事业/晋升", ["事业", "晋升", "[B]"]),
    ("发财/财务", ["财", "[C]", "[wealth]"]),
    ("置业/买房", ["置业", "买房", "田宅", "房"]),
    ("结婚/桃花", ["婚", "桃花", "[F]"]),
    ("子女添丁", ["子女", "添丁", "[G]"]),
    ("灾祸/疾病", ["健康", "疾病", "灾", "[misfortune]", "[health]"]),
    ("搬迁/变动", ["搬迁", "驿马", "调动", "[I]", "变动"]),
    ("觉醒/转折", ["转折", "觉醒", "[A]"]),
]

HEADER_TMPL = """# {name} · 八字 × 紫微 双引擎全量报告

> **编制人：** 金鉴真人 ｜ **编制时间：** 2026-11-22 ｜ **版本：** v5.0（21§＋§22 紫微细断＋§23 交叉印证＋§24 流年详析）
> **数据源：** `/tmp/{name}_ds.json` ／ `/tmp/{name}_ziwei.json` ｜ **引擎：** `pipeline_v5` ＋ `ziwei_engine v1.3` ＋ `liu_nian_v2`
> **起运口径：** 真太阳时（含均时差 EoT）

---

"""


def build_index(s16: str) -> str:
    lines = [l for l in s16.splitlines() if l.strip().startswith("|") and "---" not in l]
    rows = []
    for cat, kws in CATS:
        years = []
        for l in lines:
            if any(k in l for k in kws):
                m = re.search(r"(?:19|20)\d{2}", l)
                if m:
                    years.append(m.group(0))
        years = sorted(set(years))
        if years:
            shown = "、".join(years[:6]) + ("…" if len(years) > 6 else "")
            rows.append(f"| {len(rows)+1} | {cat} | {shown} | 见上方明细 |")
        else:
            rows.append(f"| {len(rows)+1} | {cat} | — | 本盘未明确触发该类应期 |")
    out = ["### §16.9 九类事件索引（按类型归集）\n",
           "| 序号 | 类型 | 年份 | 说明 |",
           "|:---:|:---|:---|:---|"]
    out += rows
    out.append("")
    return "\n".join(out)


def _section(s: str, num: str) -> str:
    m = re.search(rf"##\s*§{num}\s.*?(?=##\s*§{int(num)+1}\s|\Z)", s, re.DOTALL)
    return m.group(0) if m else ""


def _grab(text: str, kws, maxlen: int = 70) -> str:
    for line in text.splitlines():
        t = line.strip().lstrip("|").strip()
        if len(t) < 10 or "---" in t or t.startswith("#") or t.startswith(">") or "§" in t:
            continue
        if any(k in t for k in kws):
            return re.sub(r"\s+", " ", t)[:maxlen]
    return "详见对应章节"


def build_s1_extra(s: str) -> str:
    mapping = [
        ("从事行业", "10", ["适合", "行业", "职业"]),
        ("婚姻质量", "12", ["婚姻", "感情"]),
        ("子女情况", "13", ["子女", "个数", "数量"]),
        ("身材/体型", "7", ["身材", "体型", "身高"]),
        ("结婚最佳窗口", "12", ["最佳", "结婚", "窗口"]),
        ("置业/买房年份", "9", ["买房", "置业", "年份"]),
        ("学习力", "11", ["学习", "学历", "读书"]),
    ]
    rows = []
    for i, (field, sec, kws) in enumerate(mapping, start=26):
        val = _grab(_section(s, sec), kws)
        rows.append(f"| {i} | **{field}** | {val} |")
    out = ["", "**第五段：专项速览（7项）**", "", "| 序号 | 项目 | 内容 |", "|:----:|------|------|"]
    out += rows
    out.append("")
    return "\n".join(out)


def main():
    name, path = sys.argv[1], sys.argv[2]
    s = open(path, encoding="utf-8").read()

    if "编制人" not in s[:600]:
        s = HEADER_TMPL.format(name=name) + s

    if "§16.9" not in s:
        m = re.search(r"##\s*§16.*?(?=##\s*§17)", s, re.DOTALL)
        if not m:
            print("❌ 未找到 §16")
            sys.exit(1)
        s16 = m.group(0)
        idx = build_index(s16)
        s = s[:m.end()] + idx + "\n" + s[m.end():]

    if "第五段：专项速览" not in s:
        m2 = re.search(r"##\s*§2\s", s)
        if not m2:
            print("❌ 未找到 §2")
            sys.exit(1)
        s = s[:m2.start()] + build_s1_extra(s) + "\n" + s[m2.start():]

    open(path, "w", encoding="utf-8").write(s)
    print(f"✅ 格式补齐 → {path}（{len(s.splitlines())} 行）")


if __name__ == "__main__":
    main()
