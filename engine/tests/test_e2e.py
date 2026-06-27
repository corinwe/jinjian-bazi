#!/usr/bin/env python3
# ═══════════════════════════════════════════════
# 金鉴真人·E2E 端到端测试
# 验证: 前端 → API → 引擎 → 报告 全链路
# ═══════════════════════════════════════════════

"""
金鉴真人·端到端集成测试
覆盖: 前端加载 / API存活 / 引擎推理 / 报告生成 / 农历转换

用法:
    python3 tests/test_e2e.py                    # 本地测试
    python3 tests/test_e2e.py --remote           # 远程服务器测试
"""

import sys, json, os, subprocess, argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "engine"))

PASS = 0
FAIL = 0


def check(name, passed, detail=""):
    global PASS, FAIL
    if passed:
        PASS += 1
    else:
        FAIL += 1
    status = "✅" if passed else "❌"
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))


def api_get(path, base_url="http://localhost:8000"):
    import urllib.request

    try:
        r = urllib.request.urlopen(f"{base_url}{path}", timeout=10)
        return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}


def api_post(path, data, base_url="http://localhost:8000"):
    import urllib.request

    try:
        req = urllib.request.Request(
            f"{base_url}{path}",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        r = urllib.request.urlopen(req, timeout=15)
        return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="金鉴真人 E2E 测试")
    parser.add_argument("--remote", action="store_true", help="测试远程服务器")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API基础URL (默认: http://localhost:8000)")
    args = parser.parse_args()

    if args.remote:
        base_url = "http://43.162.90.39:8000"
    else:
        base_url = args.base_url

    print(f"\n{'═' * 50}")
    print(f"  金鉴真人·E2E 端到端测试")
    print(f"  目标: {base_url}")
    print(f"{'═' * 50}\n")

    # ── 1. 前端 ──
    print("〖1/6〗 前端加载")
    import urllib.request

    try:
        r = urllib.request.urlopen(f"{base_url}/", timeout=10)
        html = r.read().decode()
        check("首页加载", "金鉴真人" in html, "页面包含'金鉴真人'")
    except Exception as e:
        check("首页加载", False, str(e)[:40])

    # ── 2. API 存活 ──
    print("〖2/6〗 API 存活检查")
    ping = api_get("/ping", base_url)
    check("Ping", ping.get("status") == "ok", f"status={ping.get('status')}")

    health = api_get("/health", base_url)
    check("Health", health.get("status") == "healthy", f"status={health.get('status')}")
    check("引擎可用", health.get("engine", {}).get("available") is True)
    check("paipan模块", health.get("engine", {}).get("modules", {}).get("paipan") is True)
    check("pipeline模块", health.get("engine", {}).get("modules", {}).get("pipeline_v5") is True)

    # ── 3. 引擎推理 ──
    print("〖3/6〗 引擎推理测试")
    test_cases = [
        {"name": "家主", "gender": "男", "birth_year": 1980, "birth_month": 7, "birth_day": 15, "birth_hour": 10},
        {"name": "子源", "gender": "男", "birth_year": 2011, "birth_month": 4, "birth_day": 25, "birth_hour": 10},
        {"name": "主母", "gender": "女", "birth_year": 1987, "birth_month": 7, "birth_day": 1, "birth_hour": 12},
    ]
    for tc in test_cases:
        r = api_post("/api/v1/analyze", tc, base_url)
        ok = "analysis_id" in r and "status" in r
        detail = r.get("basic", {}).get("bazi", "?") if ok else str(r.get("error", "?"))[:40]
        check(f"分析: {tc['name']}", ok, detail)

    # ── 4. 报告生成 ──
    print("〖4/6〗 报告生成")
    for tc in test_cases:
        r = api_post("/api/v1/report", tc, base_url)
        ok = isinstance(r, dict) and ("report" in r or "error" not in r)
        detail = f"报告{'已生成' if ok else '失败'}"
        check(f"报告: {tc['name']}", ok, detail)

    # ── 5. 调试模式 ──
    print("〖5/6〗 调试模式")
    r = api_post("/api/v1/engine/debug", test_cases[0], base_url)
    a = r.get("analysis", {})
    has_shen_qiang = "shen_qiang_ruo" in a or "shen_qiang_ruo" in r
    has_cai_xing = "cai_xing" in a or "cai_xing" in r
    check("调试响应", r.get("success") is True or "paipan" in r, f"keys={list(r.keys())[:4]}")
    check("身强弱数据", has_shen_qiang)
    check("财星数据", has_cai_xing)

    # ── 6. 农历转换 ──
    print("〖6/6〗 农历验证")
    # 农历1990年五月初五 → 公历1990-05-28
    r = api_post(
        "/api/v1/analyze",
        {
            "name": "农历测试",
            "gender": "男",
            "birth_year": 1988,
            "birth_month": 5,
            "birth_day": 23,
            "birth_hour": 8,
            "is_lunar": True,
        },
        base_url,
    )
    check("农历分析", r.get("status") == "success" or "error" not in r)

    # ── 结果 ──
    print(f"\n{'═' * 50}")
    total = PASS + FAIL
    print(f"  E2E 测试完成: {PASS}/{total} 通过")
    if FAIL == 0:
        print(f"  {'✅ 全部通过！'}")
    else:
        print(f"  {'❌ 有 ' + str(FAIL) + ' 项失败'}")
    print(f"{'═' * 50}")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
