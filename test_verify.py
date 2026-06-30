#!/usr/bin/env python3
"""Playwright验证: 4个八字的身强弱评分是否正确"""

import json
import sys
import requests

API = "http://localhost:9000/api/v1/analyze"

test_cases = [
    {
        "name": "老板·魏启令",
        "input": {"name":"魏启令","gender":"男","birth_year":1980,"birth_month":8,"birth_day":6,"birth_hour":5,"birth_minute":0,"is_lunar":False},
        "expect_ba_zi": "庚申 癸未 辛亥 辛卯",
        "expect_score": 64.0,
        "expect_level": "偏强"
    },
    {
        "name": "太太·成",
        "input": {"name":"成","gender":"女","birth_year":1987,"birth_month":6,"birth_day":25,"birth_hour":12,"birth_minute":0,"is_lunar":True},
        "expect_ba_zi": "丁卯 丁未 庚午 壬午",
        "expect_score": 50.0,
        "expect_level": "从弱"
    },
    {
        "name": "少爷·源",
        "input": {"name":"源","gender":"男","birth_year":2011,"birth_month":5,"birth_day":31,"birth_hour":9,"birth_minute":9,"is_lunar":False},
        "expect_ba_zi": "辛卯 癸巳 丙戌 癸巳",
        "expect_score": 55.6,
        "expect_level": "中和"
    },
]

print("=" * 70)
print(f"{'姓名':<12} {'八字':<24} {'得分':<8} {'等级':<8} {'状态'}")
print("=" * 70)

all_pass = True
for case in test_cases:
    try:
        r = requests.post(API, json=case["input"], timeout=10)
        data = r.json()
        basic = data.get("basic", {})
        analysis = data.get("analysis", {})
        sq = analysis.get("shen_qiang_ruo", {})
        ba_zi = basic.get("ba_zi", "")
        score = sq.get("score", 0)
        level = sq.get("level", "")
        details = sq.get("details", [])

        score_ok = abs(score - case["expect_score"]) < 0.1
        level_ok = level == case["expect_level"]
        ba_zi_ok = ba_zi == case["expect_ba_zi"]
        status = "✅" if (score_ok and level_ok and ba_zi_ok) else "❌"

        print(f"{case['name']:<12} {ba_zi:<24} {score:<8} {level:<8} {status}")
        if not all([score_ok, level_ok, ba_zi_ok]):
            print(f"  → 期望: {case['expect_ba_zi']} / {case['expect_score']}分·{case['expect_level']}")
            print(f"  → 明细: {details}")
            all_pass = False
    except Exception as e:
        print(f"{case['name']:<12} {'ERROR':<24} {'':<8} {'':<8} ❌")
        print(f"  → {e}")
        all_pass = False

print("=" * 70)
print(f"总结果: {'全部通过 ✅' if all_pass else '有失败 ❌'}")

# 祖母八字需要找一下
# 先用一个占位
print()
print("【祖母八字需要确认】目前跳过")
