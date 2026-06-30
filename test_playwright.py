#!/usr/bin/env python3
"""Playwright验证脚本：输入八字→验证报告身强弱评分"""
from playwright.sync_api import sync_playwright
import json, time, re

BASE = "http://127.0.0.1:3001"

test_cases = [
    {
        "name": "老板·魏启令",
        "fields": {"姓名":"魏启令","性别":"男","出生年":"1980","出生月":"8","出生日":"6","时辰":"卯时"},
        "expect": {"八字":"庚申 癸未 辛亥 辛卯","得分":"64","等级":"偏强"}
    },
    {
        "name": "太太·成",
        "fields": {"姓名":"成","性别":"女","出生年":"1987","出生月":"6","出生日":"25","时辰":"午时"},
        "expect": {"八字":"丁卯 丁未 庚午 壬午","得分":"50","等级":"从弱"}
    },
    {
        "name": "少爷·源",
        "fields": {"姓名":"源","性别":"男","出生年":"2011","出生月":"5","出生日":"31","时辰":"巳时"},
        "expect": {"八字":"辛卯 癸巳 丙戌 癸巳","得分":"55","等级":"中和"}
    },
]

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="zh-CN"
        )
        page = context.new_page()

        for case in test_cases:
            print(f"\n{'='*60}")
            print(f"测试: {case['name']}")
            print(f"{'='*60}")
            
            try:
                page.goto(BASE, timeout=15000)
                page.wait_for_load_state("networkidle")
                
                # 点击"开始测算"
                btn = page.locator("button:has-text('开始测算')")
                if btn.is_visible():
                    btn.click()
                    page.wait_for_timeout(1000)
                
                # 填表单
                for label, value in case["fields"].items():
                    input_el = page.locator(f"input[placeholder*='{label}'], input[name*='{label}'], input[aria-label*='{label}']").first
                    if input_el.is_visible():
                        input_el.fill(value)
                        page.wait_for_timeout(200)
                    else:
                        # try by label text
                        lbl = page.locator(f"label:has-text('{label}')").first
                        if lbl.is_visible():
                            nearby = lbl.locator("xpath=following-sibling::input").first
                            if nearby.is_visible():
                                nearby.fill(value)
                
                # 选性别
                gender_sel = case["fields"]["性别"]
                gender_radio = page.locator(f"input[type='radio'][value='{gender_sel}'], input[value='{gender_sel}']").first
                if gender_radio.is_visible():
                    gender_radio.click()
                
                # 提交/排盘
                submit = page.locator("button:has-text('排盘'), button:has-text('分析'), button:has-text('提交')").first
                if submit.is_visible():
                    submit.click()
                
                # 等待报告加载
                page.wait_for_timeout(5000)
                
                # 截取报告内容
                content = page.text_content("body") or ""
                
                # 验证
                ba_zi_found = case["expect"]["八字"] in content
                score_found = case["expect"]["得分"] in content
                level_found = case["expect"]["等级"] in content
                
                print(f"八字 {'✅' if ba_zi_found else '❌'}: {'期望 ' + case['expect']['八字']}")
                print(f"得分 {'✅' if score_found else '❌'}: {'期望 含' + case['expect']['得分'] + '分'}")
                print(f"等级 {'✅' if level_found else '❌'}: {'期望 ' + case['expect']['等级']}")
                
                if not all([ba_zi_found, score_found, level_found]):
                    # 截屏
                    page.screenshot(path=f"/tmp/test_{case['name'][:2]}.png")
                    print(f"截图保存: /tmp/test_{case['name'][:2]}.png")
                    # 打印页面文本
                    print(f"页面内容(前500字): {content[:500]}")
                    
            except Exception as e:
                print(f"❌ 错误: {e}")
                try:
                    page.screenshot(path=f"/tmp/test_error_{case['name'][:2]}.png")
                except:
                    pass
        
        browser.close()

if __name__ == "__main__":
    run()
