#!/usr/bin/env python3
"""九龙道长官网八字验证脚本 v2.0
POST提交排盘，解析返回HTML，输出四柱八字、大运、称骨命
用法: python3 bazi-zydx-verify.py <year> <month> <day> <hour> <minute> <name> [sex]
"""

import sys, re, subprocess, os, json

def verify(year, month, day, hour, minute, name, sex=1):
    gender = "男" if sex == 1 else "女"
    
    print("══════════════════════════════════════════")
    print(f"  九龙道长官网排盘验证 v2.0")
    print(f"  命主: {name} | {year}年{month}月{day}日 {hour}:{minute} | {gender}")
    print("══════════════════════════════════════════")
    
    # POST方式提交排盘（无需登录）
    curl_cmd = [
        "curl", "-s", "-L", "https://www.zydx.top/paipan.php",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-H", "Accept: text/html,application/xhtml+xml",
        "-H", "Accept-Language: zh-CN,zh;q=0.9",
        "-H", "Referer: https://www.zydx.top/paipan.php",
        "-H", "Origin: https://www.zydx.top",
        "-c", "/tmp/zydx_cookies.txt",
        "--data", f"act=ok&name={name}&DateType=0&year={year}&month={month}&date={day}&hour={hour}&minute={minute}&sex={sex}",
    ]
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=15)
    html = result.stdout
    
    if not html or len(html) < 1000:
        print("  ❌ 下载失败，请检查网络连接")
        return False
    
    # 四柱八字 - 从tgline/dzline提取最后4个非空span.big
    tg_match = re.search(r'<tr id="tgline">(.*?)</tr>', html, re.DOTALL)
    dz_match = re.search(r'<tr id="dzline">(.*?)</tr>', html, re.DOTALL)
    
    if not tg_match or not dz_match:
        print("  ❌ 无法解析四柱数据")
        return False
    
    tg_spans = [s for s in re.findall(r'<span class="big"[^>]*>([^<]*)</span>', tg_match.group(1)) if s.strip()]
    dz_spans = [s for s in re.findall(r'<span class="big"[^>]*>([^<]*)</span>', dz_match.group(1)) if s.strip()]
    
    tg_pillars = tg_spans[-4:] if len(tg_spans) >= 4 else ['?']*4
    dz_pillars = dz_spans[-4:] if len(dz_spans) >= 4 else ['?']*4
    pillars = [f'{t}{d}' for t, d in zip(tg_pillars, dz_pillars)]
    
    print(f"  完整八字: {pillars[0]} {pillars[1]} {pillars[2]} {pillars[3]}")
    print(f"  年柱: {pillars[0]}  月柱: {pillars[1]}  日柱: {pillars[2]}  时柱: {pillars[3]}")
    
    # 地支藏干
    print()
    print("【地支藏干】")
    cg_spans = re.findall(r'<span class="small">([^<]+)</span>', html)
    relevant_cg = [s for s in cg_spans if re.search(r'[劫伤印枭杀才食官比]', s)]
    cg_pillars = relevant_cg[-4:] if len(relevant_cg) >= 4 else relevant_cg
    for i, pn in enumerate(['年支:', '月支:', '日支:', '时支:']):
        if i < len(cg_pillars):
            print(f"  {pn} {cg_pillars[i]}")
    
    # 大运序列
    print()
    print("【大运序列】")
    dayun = re.findall(r"data-year=['\"](\d+)['\"][^>]*>([^<]+)", html)
    for age, gan in dayun:
        print(f"  {gan}: data-year={age} (约{int(age)}~{int(age)+10}岁)")
    
    # 称骨命
    print()
    print("【称骨命】")
    weight_m = re.search(r'称骨重量.*?<td[^>]*>([^<]+)</td>', html, re.DOTALL)
    comment_m = re.search(r'称骨评语.*?<td[^>]*>([^<]+)</td>', html, re.DOTALL)
    if weight_m:
        print(f"  重量: {weight_m.group(1).strip()}")
    if comment_m:
        print(f"  评语: {comment_m.group(1).strip()}")
    
    print()
    print("══════════════════════════════════════════")
    print("  ✅ 验证完成（POST方式·无需登录）")
    print("══════════════════════════════════════════")
    
    # 清理cookie
    try:
        os.remove("/tmp/zydx_cookies.txt")
    except:
        pass
    
    # 返回结构化数据
    return {
        "八字": f"{pillars[0]} {pillars[1]} {pillars[2]} {pillars[3]}",
        "年柱": pillars[0], "月柱": pillars[1], "日柱": pillars[2], "时柱": pillars[3],
        "大运": [(gan, int(age)) for age, gan in dayun],
    }

if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 1980
    month = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    day = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    hour = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    minute = int(sys.argv[5]) if len(sys.argv) > 5 else 30
    name = sys.argv[6] if len(sys.argv) > 6 else "测试"
    sex = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    verify(year, month, day, hour, minute, name, sex)
