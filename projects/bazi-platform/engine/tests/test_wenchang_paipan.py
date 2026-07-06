#!/usr/bin/env python3
"""Test paipan.py wenchang functionality"""

import sys

sys.path.insert(0, "/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine")

from paipan import get_full_paipan, check_wen_chang, WEN_CHANG_MAP

# Test 1: get_full_paipan with wenchang
result = get_full_paipan(1980, 8, 6, 3, "男", "家主")
print("=== get_full_paipan test ===")
print(f"八字: {result['bazi']}")
print(f"文昌: {result['wen_chang']}")
assert "wen_chang" in result, "get_full_paipan should return wen_chang"
assert "has_wen_chang" in result["wen_chang"], "wen_chang should have has_wen_chang"

# Test 2: 辛金日主文昌在子 - need to check
result2 = get_full_paipan(1979, 7, 27, 5, "女", "梦")
print(f"\n梦 八字: {result2['bazi']}")
print(f"文昌: {result2['wen_chang']}")

# Test 3: check_wen_chang direct
print("\n=== check_wen_chang tests ===")
wc1 = check_wen_chang("甲", ["子", "寅", "辰", "午"])
print(f"甲->巳, in [子,寅,辰,午]: {wc1}")
assert not wc1["has_wen_chang"], "甲->巳 should not be in [子,寅,辰,午]"
assert wc1["wen_chang_zhi"] == "巳", "甲->wen_chang_zhi should be 巳"

wc2 = check_wen_chang("庚", ["申", "未", "亥", "卯"])
print(f"庚->亥, in [申,未,亥,卯]: {wc2}")
assert wc2["has_wen_chang"], "庚->亥 should be in [申,未,亥,卯]"
assert wc2["wen_chang_zhi"] == "亥", "庚->wen_chang_zhi should be 亥"

# Test 4: All 10 day masters in WEN_CHANG_MAP
print("\n=== All 10 day masters ===")
assert len(WEN_CHANG_MAP) == 10, f"Should have 10 entries, got {len(WEN_CHANG_MAP)}"
expected = {
    "甲": "巳",
    "乙": "午",
    "丙": "申",
    "丁": "酉",
    "戊": "申",
    "己": "酉",
    "庚": "亥",
    "辛": "子",
    "壬": "寅",
    "癸": "卯",
}
for gan, expected_zhi in expected.items():
    actual = WEN_CHANG_MAP.get(gan)
    assert actual == expected_zhi, f"{gan}->{actual} != {expected_zhi}"
    print(f"  ✅ {gan} -> {actual}")

# Test 5: get_full_paipan with 立(甲木), 月支巳 → 文昌在巳 → 原局自带
print("\n=== 立 (甲木日主) ===")
for shi_idx in range(12):
    result = get_full_paipan(2011, 5, 19, shi_idx, "男")
    if shi_idx == 0:
        print(f"八字: {result['bazi']}")
        print(f"文昌: {result['wen_chang']}")

print("\n✅ All tests passed!")
