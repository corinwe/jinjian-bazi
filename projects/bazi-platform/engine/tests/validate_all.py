#!/usr/bin/env python3
"""
金鉴真人·全量验证流水线 v1.0
每次更新后自动运行，验证所有模块的正确性

验证项:
1. 引擎测试（320条）
2. 排盘正确性（用已知八字对照）
3. API 端点可用性
4. 报告21§完整性
5. 报告格式对齐标准模板
6. 农历转换正确性
7. 前端可访问性
"""

import subprocess, json, sys, os, re, datetime
from pathlib import Path

ENGINE_DIR = "/root/bazi-platform/engine"
sys.path.insert(0, ENGINE_DIR)

PASS = 0
FAIL = 0
RESULTS = []


def check(name, passed, detail=""):
    global PASS, FAIL
    if passed:
        PASS += 1
    else:
        FAIL += 1
    status = "✅" if passed else "❌"
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))


def api_post(path, data):
    cmd = [
        "curl",
        "-s",
        "--max-time",
        "30",
        f"http://localhost:8000{path}",
        "-X",
        "POST",
        "-H",
        "Content-Type: application/json",
        "-d",
        json.dumps(data),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except:
        return {"error": f"JSON parse failed: {r.stdout[:200]}"}


def api_get(path):
    cmd = ["curl", "-s", "--max-time", "10", f"http://localhost:8000{path}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout


print("=" * 60)
print(f"金鉴真人·全量验证流水线")
print(f"时间: {datetime.datetime.now().isoformat()}")
print("=" * 60)

# ──── 1. 引擎测试 ────
print("\n# 1/7 引擎测试（320条）")
r = subprocess.run(["python3", f"{ENGINE_DIR}/tests/test_full_suite.py"], capture_output=True, text=True, timeout=120)
passed = r.returncode == 0
check("引擎320条测试", passed, r.stdout.split("\n")[-3:-1][0] if passed else r.stderr[:100])

# ──── 2. 排盘正确性 ────
print("\n# 2/7 排盘正确性验证")
from constants import BaZi, Pillar
from paipan import paipan
from shen_qiang_ruo import compute_shen_qiang_ruo
from cai_xing import compute_cai_xing
from ge_ju import determine_ge_ju

family_tests = [
    (
        "子源",
        BaZi(
            year=Pillar("辛", "卯"),
            month=Pillar("壬", "辰"),
            day=Pillar("庚", "戌"),
            hour=Pillar("辛", "巳"),
            gender="男",
        ),
        {"sqr": (70.8, "身强"), "cai": 28.0},
    )
]
for name, bazi, exp in family_tests:
    s, l, _ = compute_shen_qiang_ruo(bazi)
    c = compute_cai_xing(bazi)
    check(f"排盘{name}身强弱", abs(s - exp["sqr"][0]) <= 0.5 and l == exp["sqr"][1], f"{l}{s}分")
    check(f"排盘{name}财星", abs(c.total - exp["cai"]) <= 0.5, f"{c.total}分")

paipan_tests = [("2011-04-25-10", 2011, 4, 25, 10, "辛卯 壬辰 庚戌 辛巳")]
for label, y, m, d, h, expected in paipan_tests:
    r = paipan("测试", "男", y, m, d, h)
    actual = r.get("bazi", "")
    check(f"paipan{label}", actual == expected, f"{actual}")

# ──── 3. API 端点 ────
print("\n# 3/7 API端点可用性")
r = api_get("/ping")
check("GET /ping", '"ok"' in r)
r = api_get("/version")
check("GET /version", '"version"' in r)
r = api_post(
    "/api/v1/engine/debug",
    {"name": "测试", "gender": "男", "birth_year": 2011, "birth_month": 4, "birth_day": 25, "birth_hour": 10},
)
check("POST engine/debug", r.get("success") == True, r.get("paipan", {}).get("bazi", ""))
r = api_post(
    "/api/v1/report",
    {"name": "子源", "gender": "男", "birth_year": 2011, "birth_month": 4, "birth_day": 25, "birth_hour": 10},
)
check("POST report", r.get("success") == True, f"报告{len(r.get('report', ''))}字")

# ──── 4. 报告21§完整性 ────
print("\n# 4/7 报告21§完整性")
r = api_post(
    "/api/v1/report",
    {"name": "子源", "gender": "男", "birth_year": 2011, "birth_month": 4, "birth_day": 25, "birth_hour": 10},
)
report = r.get("report", "")
lines = report.split("\n")
sections = sorted(set(int(re.search(r"§(\d+)", l).group(1)) for l in lines if re.match(r"^## §\d+", l)))
check("21§全覆盖", len(sections) == 21, f"{len(sections)}/21")
check("报告总行数", len(lines) >= 200, f"{len(lines)}行")

# ──── 5. 格式对齐 ────
print("\n# 5/7 报告格式对齐")
fmt_checks = [
    ("版本说明8条", "> ⑧" in report),
    ("25字段四段式", "第四段：大运综合" in report),
    ("白话解读", "🗣️" in report),
    ("五行颜色", "颜色调运" in report),
    ("财富五级对照", "👑 **巨富**" in report),
    ("人生建议", "人生建议" in report),
    ("金鉴真人署名", "金鉴真人" in report),
]
for n, p in fmt_checks:
    check(f"格式{n}", p)

# ──── 6. 农历转换 ────
print("\n# 6/7 农历转换")
from lunar import lunar_to_solar

for y, m, d in [(1980, 5, 15), (2011, 4, 25)]:
    sol = lunar_to_solar(y, m, d)
    check(f"农历{y}-{m}-{d}→{sol.year}-{sol.month}-{sol.day}", sol.year > 0)
    r1 = api_post(
        "/api/v1/engine/debug",
        {
            "name": "测试",
            "gender": "男",
            "birth_year": y,
            "birth_month": m,
            "birth_day": d,
            "birth_hour": 10,
            "calendar_type": "lunar",
        },
    )
    r2 = api_post(
        "/api/v1/engine/debug",
        {
            "name": "测试",
            "gender": "男",
            "birth_year": sol.year,
            "birth_month": sol.month,
            "birth_day": sol.day,
            "birth_hour": 10,
            "calendar_type": "solar",
        },
    )
    b1 = r1.get("paipan", {}).get("bazi", "")
    b2 = r2.get("paipan", {}).get("bazi", "")
    check(f"农历{y}-{m}-{d}一致", b1 == b2 and b1 != "", f"{b1}")

# ──── 7. 前端 ────
print("\n# 7/7 前端可访问")
f = api_get("/")
check("前端加载", "金鉴真人" in f and "input" in f)
check("四柱表", "四柱信息" in f)
check("命理分析", "命理分析" in f)
check("阳历/农历", "阳历" in f and "农历" in f)
check("PDF下载", "下载PDF" in f or "print" in f)

print("\n" + "=" * 60)
print("验证总结")
print("=" * 60)
total = PASS + FAIL
print(f"总用例: {total}")
print(f"PASS: {PASS}")
print(f"FAIL: {FAIL}")
print(f"通过率: {PASS / total * 100:.1f}%" if total else "N/A")

if FAIL > 0:
    print("\n❌ 失败的用例:")
    for name, status, detail in RESULTS:
        if status == "❌ FAIL":
            print(f"  {name}: {detail}")
    sys.exit(1)
else:
    print("\n✅ 全部通过！")
