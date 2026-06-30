#!/usr/bin/env python3
"""Playwright验证：输入八字→查看报告→验证身强弱"""
from playwright.sync_api import sync_playwright
import json, time

BASE = "http://127.0.0.1:3001"

test_cases = [
    {
        "name": "老板",
        "form": {"name":"元宝","gender":"男","calendar":"公历","year":"1980","month":"8","day":"6","hour":"5"},
        "expect_str": ["庚申 癸未 辛亥 辛卯","64.0","偏强","身强", "64分"]
    },
    {
        "name": "太太",
        "form": {"name":"成","gender":"女","calendar":"农历","year":"1987","month":"6","day":"25","hour":"11"},
        "expect_str": ["庚午","壬午","50.0","从弱"]
    },
    {
        "name": "少爷",
        "form": {"name":"源","gender":"男","calendar":"公历","year":"2011","month":"5","day":"31","hour":"9"},
        "expect_str": ["辛卯 癸巳 丙戌 癸巳","55.6","中和"]
    },
]

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":1280,"height":900}, locale="zh-CN")
        
        for case in test_cases:
            print(f"\n{'='*60}")
            print(f"测试: {case['name']}")
            print(f"{'='*60}")
            
            try:
                # 加载页面
                page.goto(BASE, timeout=15000)
                page.wait_for_load_state("networkidle")
                time.sleep(1)
                
                # 点击"开始测算"
                btn = page.get_by_text("开始测算")
                if btn.count() > 0:
                    btn.first.click()
                    time.sleep(2)
                
                # 填写姓名
                name_input = page.locator("input").first
                if name_input.is_visible():
                    name_input.fill(case["form"]["name"])
                    time.sleep(0.3)
                
                # 性别
                gender = case["form"]["gender"]
                gender_el = page.locator(f"text='{gender}'").first
                if gender_el.is_visible():
                    gender_el.click()
                    time.sleep(0.3)
                
                # 公历/农历
                cal = case["form"]["calendar"]
                cal_el = page.locator(f"text='{cal}'").first
                if cal_el.count() > 0:
                    cal_el.click()
                    time.sleep(0.3)
                
                # 年/月/日下拉框
                for field in ["year","month","day"]:
                    val = case["form"][field]
                    sel = page.locator(f"select").nth(["year","month","day"].index(field))
                    if sel.is_visible():
                        sel.select_option(val)
                        time.sleep(0.2)
                
                # 时辰
                hour = int(case["form"]["hour"])
                hour_labels = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
                hour_label = hour_labels[(hour + 1) // 2 % 12]
                hour_el = page.locator(f"text='{hour_label}时'").first
                if hour_el.is_visible():
                    hour_el.click()
                    time.sleep(0.3)
                
                # 提交按钮
                submit = page.get_by_text("排盘", exact=True).first
                if submit.count() == 0:
                    submit = page.get_by_text("分析", exact=True).first
                if submit.count() == 0:
                    submit = page.locator("button[type='submit']").first
                if submit.count() > 0:
                    submit.click()
                    time.sleep(3)
                
                # 等待报告
                time.sleep(5)
                
                full_text = page.text_content("body") or ""
                full_text_lower = full_text.lower()
                
                all_match = True
                for exp in case["expect_str"]:
                    found = exp.lower() in full_text_lower
                    status = "✅" if found else "❌"
                    if not found:
                        all_match = False
                    print(f"  {status} 检查: {exp}")
                
                if all_match:
                    print(f"  ✅ 全部通过!")
                else:
                    page.screenshot(path=f"/tmp/verify_{case['name']}.png")
                    print(f"  ⚠️ 截图: /tmp/verify_{case['name']}.png")
                    # 打印分数附近上下文
                    for line in full_text.split('\n'):
                        if '分' in line or '偏强' in line or '身强' in line or '中和' in line or '从弱' in line:
                            print(f"  >> {line.strip()[:100]}")
                            if line.count('分') > 2:
                                break
                    
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        browser.close()

if __name__ == "__main__":
    run()
