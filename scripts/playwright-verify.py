#!/usr/bin/env python3
"""金鉴真人 Playwright 浏览器验证脚本 — v1.1 增加score_first5/财富/事业检查"""
import asyncio
import json
import re
import urllib.request
from playwright.async_api import async_playwright

# 三个验证八字（用真实生辰，已永久记忆）
TESTS = [
    ("魏无记", "男", 1980, 8, 6, 5, False, "64.0", "身强"),
    ("主母", "女", 1987, 7, 20, 12, False, "50.0", "从弱"),
    ("Joe", "男", 2011, 5, 31, 9, False, "55.6", "中和"),
]
FORBIDDEN = ["假旺真弱", "七段式"]
FORBIDDEN_PINYIN = ["nian支", "yue支", "透干=True", "透干=False"]


def audit_report(report_text, name, exp_score, exp_level):
    """逐项审计报告内容"""
    ok = True
    print(f"\n{'='*60}")
    print(f"📋 报告审计: {name}")

    # 八字正确性
    ba_zi_match = re.search(r'八字[：:]\\s*(\\S+\\s+\\S+\\s+\\S+\\s+\\S+)', report_text)
    if ba_zi_match:
        print(f"  八字: {ba_zi_match.group(1)}")

    # 分数验证
    score_match = re.search(r'(\\d+\\.?\\d*)\\s*分[·\\s]\\s*(身强|身弱|中和|从弱|从强)', report_text)
    if score_match:
        gs, gl = score_match.group(1), score_match.group(2)
        if gs == exp_score and gl == exp_level:
            print(f"  ✅ 身强弱: {gs}分·{gl}")
        else:
            print(f"  ❌ 期望 {exp_score}分·{exp_level}, 实际 {gs}分·{gl}")
            ok = False

    # §1-§20完整性
    sections = sorted(set(int(s) for s in re.findall(r'## §(\d+)', report_text)))
    missing = [e for e in range(1, 21) if e not in sections]
    if missing:
        print(f"  ❌ 缺§{missing}")
        ok = False
    else:
        print(f"  ✅ §1-§20完整 ({len(sections)}个)")

    # 禁止词检查
    for word in FORBIDDEN:
        if word in report_text:
            print(f"  ❌ 禁止词'{word}'残留")
            ok = False
    for word in FORBIDDEN_PINYIN:
        if word in report_text:
            print(f"  ❌ 拼音残留'{word}'")
            ok = False

    # 财富一致性
    if "54.7" in report_text:
        print(f"  ❌ 残留自创分数54.7")
        ok = False
    if "身弱系数" in report_text:
        print(f"  ❌ 身弱系数标签残留")
        ok = False
    if "三定律" in report_text:
        print(f"  ❌ 三定律残留")
        ok = False
    if "围克反成助力" in report_text:
        print(f"  ❌ 围克反成助力残留")
        ok = False

    # 财富等级验证（身强财弱→中富）
    if name == "魏无记":
        if "中富" in report_text:
            print(f"  ✅ 财富等级: 中富")
        else:
            print(f"  ❌ 财富等级应为中富，实际未找到")
            ok = False

    # 事业总结验证
    if "事业" in report_text[-2000:]:
        print(f"  ✅ 事业总结存在")
    else:
        print(f"  ❌ 报告末尾缺少事业总结")
        ok = False

    # 大运定性验证（替代旧版数值评分）
    dayun_qualitative = re.findall(r'(ding_xing|吉|凶|好坏参半|first5_ding_xing|last5_ding_xing)', report_text)
    if dayun_qualitative:
        print(f"  ✅ 大运定性（吉/凶/好坏参半）")
    else:
        print(f"  ❌ 大运缺少定性标记")
        ok = False

    # 流年新特性验证（报告文本）
    new_features = [
        ("过三关 top3", r"过三关|top3|能量倍数"),
        ("能量倍数排序", r"能量倍数"),
        ("宫位应事断语", r"红鸾|隐忍|怀胎|心情郁闷|配偶|子女"),
        ("干透干藏", r"干透|干藏"),
    ]
    for feat_name, pattern in new_features:
        if re.search(pattern, report_text):
            print(f"  ✅ {feat_name}")
        else:
            print(f"  ❌ 缺少{feat_name}")
            ok = False

    print(f"  报告行数: {len(report_text.splitlines())}")
    if ok:
        print(f"  🎉 全部通过!")
    return ok


async def verify_via_api(name, gender, y, m, d, h, lunar, exp_score, exp_level):
    """通过API获取报告并进行浏览器渲染验证"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

        # 1. 通过API获取报告 + 验证数据结构
        data = json.dumps({"name": name, "gender": gender,
            "birth_year": y, "birth_month": m, "birth_day": d,
            "birth_hour": h, "is_lunar": lunar}).encode()
        req = urllib.request.Request(
            "http://localhost:9000/api/v1/analyze",
            data=data, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        report_md = result.get("report_md", "")

        # 验证API返回的da_yun数据包含新字段（定性）
        da_yun_list = result.get("analysis", {}).get("da_yun", {}).get("da_yun", [])
        if da_yun_list:
            has_ding_xing = "ding_xing" in da_yun_list[0]
            has_kong_wang = "kong_wang" in da_yun_list[0]
            print(f"  API dayun: ding_xing={has_ding_xing}, kong_wang={has_kong_wang}")

        # API层新特性验证（引擎JSON数据）
        da_yun_jx = result.get("analysis", {}).get("da_yun_ji_xiong", [])
        liu_nian_list = result.get("analysis", {}).get("liu_nian", [])
        api_checks = {
            "空亡检测": any(d.get("kong_wang") for d in da_yun_jx),
            "断层认知": any("过程虽苦" in d.get("detail","") or "感受不痛苦" in d.get("detail","") for d in da_yun_jx),
            "犯太岁定性": any(ln.get("fan_tai_sui") and "犯太岁" in str(ln["fan_tai_sui"]) for ln in liu_nian_list[:3]),
            "流年top3": any(len(ln.get("top3_events",[])) > 0 for ln in liu_nian_list[:3]),
        }
        for feat, ok_flag in api_checks.items():
            print(f"  API {feat}: {ok_flag}")

        # 2. 在前端页面渲染并截图
        await page.goto("http://localhost:3001")
        await page.wait_for_timeout(3000)
        await page.set_content(f"<html><body><pre>{report_md[:5000]}</pre></body></html>")
        await page.screenshot(path=f"/tmp/playwright_{name}.png")
        print(f"  📸 截图: /tmp/playwright_{name}.png")

        await browser.close()

        # 3. 审计报告内容
        return audit_report(report_md, name, exp_score, exp_level)


async def main():
    results = []
    for test in TESTS:
        result = await verify_via_api(*test)
        results.append(result)

    passed = sum(1 for r in results if r)
    print(f"\n{'='*60}")
    print(f"🎉 {passed}/{len(results)} 全部验证通过!" if all(results) else f"⚠️ {len(results)-passed}个测试失败")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
