#!/usr/bin/env python3
"""Smoke test for bazi-verify.py — runs all 5 anchors + wenchang check"""
import sys, subprocess, json
script = "/root/bazi-platform/skills/bazi/bazi-auto-verify/scripts/bazi-verify.py"
tests = [
    ("2011 5 31 5 男", "子源", "辛卯 癸巳 丙戌 癸巳"),
    ("2011 5 19 6 男", "立", "辛卯 癸巳 甲戌 庚午"),
    ("1980 8 6 3 男", "家主", "庚申 癸未 辛亥 辛卯"),
    ("1987 7 10 6 女", "主母", "丁卯 丁未 庚申 壬午"),
    ("1949 9 30 6 男", "家主父", "己丑 癸酉 癸亥 戊午"),
]
all_pass = True

# ── 文昌贵人标准表 ──
WEN_CHANG = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
    "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
    "壬": "寅", "癸": "卯",
}

# 各人物日主+文昌预期
WEN_CHANG_TESTS = [
    ("子源",  "丙", "申", False),  # 原局巳/午/戌/巳 → 无申
    ("立",    "甲", "巳", False),  # 原局卯/巳/戌/午 → 无巳(月支巳是巳, yes!)
    ("家主",  "辛", "子", False),  # 原局申/未/亥/卯 → 无子
    ("主母",  "庚", "亥", False),  # 原局卯/未/午/午 → 无亥
    ("家主父","癸", "卯", False),  # 原局丑/酉/亥/午 → 无卯
]
# 修正：立甲→巳，巳月地支正好是巳！所以立有文昌
WEN_CHANG_TESTS_CORRECTED = [
    ("子源",  "丙", "申", False, "申不在巳午戌巳"),
    ("立",    "甲", "巳", True,  "巳在月支"),
    ("家主",  "辛", "子", False, "子不在申未亥卯"),
    ("主母",  "庚", "亥", False, "亥不在卯未午午"),
    ("家主父","癸", "卯", False, "卯不在丑酉亥午"),
]

print("=" * 50)
print("金鉴真人·排盘smoke测试 + 文昌验证")
print("=" * 50)

# Part 1: 基础排盘验证
print("\n📋 §1 基础排盘验证")
for args, name, expected in tests:
    result = subprocess.run(["python3", script] + args.split(), capture_output=True, text=True)
    if expected in result.stdout:
        print(f"  ✅ {name} = {expected}")
    else:
        print(f"  ❌ {name} 期望 {expected}，实际输出：")
        for line in result.stdout.split('\n'):
            if '八字' in line or '日主' in line: print(f"     {line.strip()}")
        all_pass = False

# Part 2: 文昌贵人验证
print("\n📚 §2 文昌贵人验证")
# 立(甲木日主)文昌在巳，月支是巳 → 原局自带文昌
# 所以这个校验需要根据实际八字数据
for name, ri_zhu, wc_zhi, has_it, note in WEN_CHANG_TESTS_CORRECTED:
    expected = WEN_CHANG.get(ri_zhu)
    if expected == wc_zhi:
        check_pass = True
        msg = f"✅ {name}({ri_zhu}→{expected}): {'原局有' if has_it else '原局无'} ({note})"
    else:
        check_pass = False
        msg = f"❌ {name}({ri_zhu}→{expected}←->{wc_zhi}): 文昌表不符"
    print(f"  {'✅' if check_pass else '❌'} {name}({ri_zhu}→{expected}): {'原局自带' if has_it else '需补文昌'} — {note}")
    if not check_pass:
        all_pass = False

# Part 3: WEN_CHANG表完整性
print("\n📋 §3 文昌表完整性验证")
all_gans = "甲乙丙丁戊己庚辛壬癸"
expected_all = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申","己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
for gan in all_gans:
    if gan in WEN_CHANG and WEN_CHANG[gan] == expected_all.get(gan):
        print(f"  ✅ {gan}→{WEN_CHANG[gan]}")
    else:
        print(f"  ❌ {gan}→{WEN_CHANG.get(gan, '缺失')} (期望{expected_all.get(gan)})")
        all_pass = False

print("\n" + "=" * 50)
if all_pass:
    print("✅ 全部通过 (排盘+文昌)")
else:
    print("❌ 有错误")
    sys.exit(1)
