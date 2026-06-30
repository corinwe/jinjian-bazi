#!/usr/bin/env python3
"""Playwright验证：输入八字→查看报告→验证关键数据"""
from playwright.sync_api import sync_playwright
import time

BASE = "http://127.0.0.1:3001"

# 时辰映射：小时 → select value
HOUR_MAP = {
    0:'zi',1:'chou',2:'chou',3:'yin',4:'yin',5:'mao',6:'mao',
    7:'chen',8:'chen',9:'si',10:'si',11:'wu',12:'wu',
    13:'wei',14:'wei',15:'shen',16:'shen',17:'you',18:'you',
    19:'xu',20:'xu',21:'hai',22:'hai',23:'zi'
}

def fill_form_and_verify(page, name, gender, calendar, year, month, day, hour, expect_strs, label):
    page.goto(BASE, timeout=15000)
    page.wait_for_load_state("networkidle")
    time.sleep(0.5)
    page.get_by_text("开始测算").first.click()
    time.sleep(1)
    
    page.locator("input[type='text']").first.fill(name)
    time.sleep(0.2)
    page.locator(f"text='{gender}'").first.click()
    time.sleep(0.2)
    page.locator(f"button:has-text('{calendar}')").first.click()
    time.sleep(0.2)
    
    selects = page.locator("select").all()
    selects[0].select_option(str(year))
    selects[1].select_option(str(month))
    selects[2].select_option(str(day))
    selects[3].select_option(HOUR_MAP[hour])
    time.sleep(0.3)
    
    page.get_by_text("开始排盘").first.click()
    time.sleep(5)
    
    # 等待报告加载
    for _ in range(30):
        time.sleep(1)
        body = page.text_content("body") or ""
        if "§1" in body or "§3" in body or "身强弱" in body:
            break
    
    body_text = page.text_content("body") or ""
    
    print(f"\n{'='*60}")
    print(f"验证: {label}")
    print(f"{'='*60}")
    
    all_pass = True
    for exp in expect_strs:
        found = exp in body_text
        s = "✅" if found else "❌"
        if not found: all_pass = False
        print(f"  {s} {exp}")
    
    if not all_pass:
        # 打印关键区域
        for line in body_text.split('\n'):
            if any(k in line for k in ['64','55','50','偏强','身强','从弱','中和','身强弱']):
                print(f"  >> {line.strip()[:120]}")
    
    return all_pass

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width":1280,"height":900}, locale="zh-CN")
        
        results = []
        
        # 老板：庚申 癸未 辛亥 辛卯 → 64.0分·偏强
        ok = fill_form_and_verify(page,
            name="元宝", gender="男", calendar="公历",
            year=1980, month=8, day=6, hour=5,
            expect_strs=["庚申 癸未 辛亥 辛卯","64.0","偏强"],
            label="老板")
        results.append(("老板", ok))
        
        # 太太：丁卯 丁未 庚午 壬午 → 50.0分·从弱
        ok = fill_form_and_verify(page,
            name="成", gender="女", calendar="农历",
            year=1987, month=6, day=25, hour=12,
            expect_strs=["丁卯","丁未","庚午","壬午","50.0","从弱"],
            label="太太")
        results.append(("太太", ok))
        
        # 少爷：辛卯 癸巳 丙戌 癸巳 → 55.6分·中和
        ok = fill_form_and_verify(page,
            name="源", gender="男", calendar="公历",
            year=2011, month=5, day=31, hour=9,
            expect_strs=["辛卯 癸巳 丙戌 癸巳","55.6","中和"],
            label="少爷")
        results.append(("少爷", ok))
        
        browser.close()
        
        print(f"\n{'='*60}")
        print("最终结果:")
        for label, ok in results:
            print(f"  {'✅' if ok else '❌'} {label}")

if __name__ == "__main__":
    run()
