#!/usr/bin/env python3
"""提取报告关键段落分析问题"""
import json, urllib.request, re

data = json.dumps({
    "name": "少爷测试", "gender": "男",
    "birth_year": 2011, "birth_month": 5, "birth_day": 31,
    "birth_hour": 10, "birth_minute": 0, "calendar": "solar"
}).encode()
req = urllib.request.Request("http://localhost:9000/api/v1/analyze", data=data, headers={"Content-Type":"application/json"})
d = json.loads(urllib.request.urlopen(req, timeout=30).read())
rm = d["report_md"]

# 提取§8 财富分析
s8 = rm[rm.find("## §8 财富分析"):]
s8 = s8[:s8.find("## §") if s8.find("## §", 40) > 0 else len(s8)]
print("=" * 50)
print("§8 财富分析")
print("=" * 50)
print(s8[:3000])

print("\n\n" + "=" * 50)
print("§8.6 大运财星窗口（关键问题）")
print("=" * 50)
idx = s8.find("8.6")
if idx > 0:
    s86 = s8[idx:idx+2000]
    print(s86)
else:
    print("§8.6不存在!")

print("\n\n" + "=" * 50)
print("§17 大运精析（关键问题）")
print("=" * 50)
s17 = rm[rm.find("## §17 大运精析"):]
s17 = s17[:s17.find("## §") if s17.find("## §", 40) > 0 else len(s17)]
print(s17[:4000])

print("\n\n" + "=" * 50)
print("§4 喜用神详解（关键问题）")
print("=" * 50)
s4 = rm[rm.find("## §4 喜用神详解"):]
s4 = s4[:s4.find("## §") if s4.find("## §", 40) > 0 else len(s4)]
print(s4[:3000])
