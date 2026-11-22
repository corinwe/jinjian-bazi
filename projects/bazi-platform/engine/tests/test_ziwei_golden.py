#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""紫微斗数黄金用例回归测试。

运行：
    pytest engine/tests/test_ziwei_golden.py -q
    python3 engine/tests/test_ziwei_golden.py        # 直接跑

数据：
    engine/tests/golden/ziwei_cases.json
    （由 scripts/build_ziwei_golden.py 生成，行为冻结锚点）

覆盖：
    · 家族四盘（家主/主母/少爷/云森）
    · 立春前后年柱切换
    · 闰月口径
    · 晚子时口径
"""
import json
import os
import sys

import pytest

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJ, "engine"))

import ziwei_engine  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden", "ziwei_cases.json")


def load_cases():
    with open(GOLDEN, encoding="utf-8") as f:
        return json.load(f)["cases"]


CASES = load_cases()


def _bazi(zw) -> str | None:
    b = zw.get("四柱") or zw.get("bazi") or zw.get("八字同源摘要", {}).get("四柱")
    if isinstance(b, dict):
        b = " ".join(b[k]["gan"] + b[k]["zhi"] for k in ("year", "month", "day", "time"))
    return b


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_golden(case):
    inp, exp = case["input"], case["expected"]
    zw = ziwei_engine.build(inp["name"], inp["gender"], inp["date"], inp["time"], inp["location"])
    z = zw["紫微"]

    assert _bazi(zw) == exp["bazi"], f"四柱不符：{_bazi(zw)} != {exp['bazi']}"
    assert z.get("五行局") == exp["五行局"], f"五行局不符：{z.get('五行局')} != {exp['五行局']}"
    assert z.get("命主") == exp["命主"], f"命主不符：{z.get('命主')} != {exp['命主']}"
    assert z.get("身主") == exp["身主"], f"身主不符：{z.get('身主')} != {exp['身主']}"
    assert z.get("生年四化") == exp["生年四化"], f"四化不符：{z.get('生年四化')} != {exp['生年四化']}"

    pmap = {p["宫位"]: p for p in z["十二宫"]}
    assert pmap["命宫"]["干支"] == exp["命宫干支"], f"命宫干支不符：{pmap['命宫']['干支']}"
    assert [s["名"] for s in pmap["命宫"]["主星"]] == exp["命宫主星"], "命宫主星不符"

    for gong, stars in exp["十二宫主星"].items():
        got = [s["名"] for s in pmap[gong]["主星"]]
        assert got == stars, f"{gong}主星不符：{got} != {stars}"


def main():
    failed = 0
    for c in CASES:
        try:
            test_golden(c)
            print(f"✅ {c['id']:<14} {c['expected']['bazi']}")
        except AssertionError as e:
            failed += 1
            print(f"❌ {c['id']:<14} {e}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} 通过")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
