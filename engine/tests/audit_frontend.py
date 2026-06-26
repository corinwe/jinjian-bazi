#!/usr/bin/env python3
"""审查引擎完整输出，对比前端展示缺失"""
import sys, json, subprocess

# 调API获取数据
cmd = [
    "curl", "-s", "--max-time", "30",
    "http://localhost:8000/api/v1/engine/debug",
    "-X", "POST", "-H", "Content-Type: application/json",
    "-d", '{"name":"测试","gender":"男","birth_year":1979,"birth_month":7,"birth_day":15,"birth_hour":4}'
]
result = subprocess.run(cmd, capture_output=True, text=True)
d = json.loads(result.stdout)
r = d.get('result', {})
bd = d.get('basic_data', {})

print("=== 21§全部输出 ===")
for k in sorted(r.keys()):
    if k.startswith('sec_'):
        val = r[k]
        vtype = type(val).__name__
        if isinstance(val, dict):
            keys = list(val.keys())
            print(f"  ✅ {k} ({vtype}): {len(keys)}字段 → {keys[:8]}...")
        elif isinstance(val, list):
            print(f"  ✅ {k} ({vtype}): {len(val)}项")
        else:
            print(f"  ✅ {k}: {str(val)[:60]}")

print()
# 检查前端index.html显示哪些§
with open('/root/bazi-platform/frontend/index.html', 'r') as f:
    html = f.read()

keywords = {
    "一、一页总览": "sec_1",
    "二、财富": "sec_8",
    "三、事业": "sec_10", 
    "四、学业": "sec_11",
    "五、婚姻": "sec_12",
    "六、子女": "sec_13",
    "七、健康": "sec_14",
    "大运走势": "sec_17",
    "三决断": "sec_18",
    "八维评分": "dimensions",
    "五行开运": "sec_20",
}
for kw, sec in keywords.items():
    found = kw in html
    print(f"  {'✅' if found else '❌'} 前端展示 {kw} ({sec})")

print()
print("=== 前端未展示但有数据的§ ===")
for k in sorted(r.keys()):
    if k.startswith('sec_'):
        ref = k.replace('sec_', '').split('_')[0]
        shown_in_html = False
        for kw, sec in keywords.items():
            if ref in sec or sec in k:
                shown_in_html = True
                break
        # 检查sec_5, sec_6等
        sec_num = k.split('_')[1] if len(k.split('_')) > 1 else ''
        if sec_num in ['5','6','7','9','15','16','19','21']:
            print(f"  ❌ {k} — 引擎有数据但前端未渲染")

print()
print("=== 基础数据四柱字段 ===")
pi = bd.get('pillars', {})
for p in ['year', 'month', 'day', 'hour']:
    pdata = pi.get(p, {})
    print(f"  {p}: {list(pdata.keys())}")

print()
print("=== 农历转换验证 ===")
sys.path.insert(0, '/root/bazi-platform/engine')
from lunar import lunar_to_solar
tests = [(1980,5,15), (1979,7,15), (2011,4,25)]
for y,m,d in tests:
    sol = lunar_to_solar(y, m, d)
    print(f"  农历{y}年{m}月{d}日 → 公历{sol.year}年{sol.month}月{sol.day}日")

print()
# 验证: 农历转公历后调引擎是否一致
for y,m,d in [(1980,5,15)]:
    sol = lunar_to_solar(y, m, d)
    cmd1 = ["curl", "-s", "--max-time", "15",
        "http://localhost:8000/api/v1/engine/debug",
        "-X", "POST", "-H", "Content-Type: application/json",
        "-d", json.dumps({"name":"测试","gender":"男","birth_year":y,"birth_month":m,"birth_day":d,"birth_hour":10,"calendar_type":"lunar"})]
    cmd2 = ["curl", "-s", "--max-time", "15",
        "http://localhost:8000/api/v1/engine/debug",
        "-X", "POST", "-H", "Content-Type: application/json",
        "-d", json.dumps({"name":"测试","gender":"男","birth_year":sol.year,"birth_month":sol.month,"birth_day":sol.day,"birth_hour":10,"calendar_type":"solar"})]
    r1 = json.loads(subprocess.run(cmd1, capture_output=True, text=True).stdout)
    r2 = json.loads(subprocess.run(cmd2, capture_output=True, text=True).stdout)
    b1 = r1.get('paipan',{}).get('bazi','')
    b2 = r2.get('paipan',{}).get('bazi','')
    match = "✅ 一致" if b1 == b2 else "❌ 不一致"
    print(f"  农历{y}-{m}-{d}→公历{sol.year}-{sol.month}-{sol.day}: 八字{b1} == {b2} {match}")
