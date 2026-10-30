#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刑冲合害回归测试 — 自刑判定（2026-10-30 修复）

背景：旧 check_xing() 把「辰午酉亥中任意两字」当作自刑，导致
      - 误报：午亥、辰酉、辰午 等跨字组合被判自刑；
      - 漏报：午午、亥亥 等真正的同支自刑（旧逻辑按"去重后的字"计数，len 恒为 1）。
规范：自刑只存在于**同一地支重复出现**（辰辰/午午/酉酉/亥亥）。

运行：python3 engine/tests/test_xing_chong_he_hua.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from xing_chong_he_hua import check_xing  # noqa: E402


def zixing_names(zhi_list):
    return [n for n, _ in check_xing(zhi_list) if n.endswith("自刑")]


CASES = [
    # (输入, 期望的自刑结果, 说明)
    (["午", "亥"], [], "跨字（午+亥）不得判自刑"),
    (["辰", "酉"], [], "跨字（辰+酉）不得判自刑"),
    (["辰", "午"], [], "跨字（辰+午）不得判自刑"),
    (["酉", "亥"], [], "跨字（酉+亥）不得判自刑"),
    (["午", "午"], ["午午自刑"], "同支双午 → 自刑"),
    (["亥", "亥"], ["亥亥自刑"], "同支双亥 → 自刑"),
    (["辰", "辰"], ["辰辰自刑"], "同支双辰 → 自刑"),
    (["酉", "酉"], ["酉酉自刑"], "同支双酉 → 自刑"),
    (["辰", "辰", "午", "午"], ["辰辰自刑", "午午自刑"], "两组自刑同时命中"),
    (["申", "未", "亥", "卯"], [], "家主原局：无自刑"),
    (["丁", "卯", "丁", "未", "庚", "午", "壬", "午"], None, "含天干时不应崩溃（仅地支参与）"),
    (["卯", "未", "午", "午"], ["午午自刑"], "主母原局：双午自刑"),
]


def main():
    failed = 0
    for zhis, expect, note in CASES:
        # 只把地支传入（过滤天干字符）
        only_zhi = [z for z in zhis if z in "子丑寅卯辰巳午未申酉戌亥"]
        got = zixing_names(only_zhi)
        if expect is None:
            ok = True
        else:
            ok = got == expect
        print(("✅" if ok else "❌"), only_zhi, "→", got, "|", note)
        if not ok:
            failed += 1
            print("     期望:", expect)
    print()
    if failed:
        print(f"❌ 失败 {failed} / {len(CASES)}")
        return 1
    print(f"✅ 全部通过 {len(CASES)} / {len(CASES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
