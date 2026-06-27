#!/usr/bin/env python3
"""Check report quality - §8.6财星 and §17大运 details"""
import json, urllib.request
data = json.dumps({"name":"少爷","gender":"男","birth_year":2011,"birth_month":5,"birth_day":31,"birth_hour":10,"birth_minute":0,"calendar":"solar"}).encode()
req = urllib.request.Request("http://localhost:9000/api/v1/analyze", data=data, headers={"Content-Type":"application/json"})
d = json.loads(urllib.request.urlopen(req,timeout=30).read())
rm = d["report_md"]
a = d["analysis"]

print("=== §8 财富分析（完整）===")
i=rm.find("## §8 财富"); j=rm.find("## §9")
if i>=0: print(rm[i:j][:3000])

print("\n\n=== §17 大运精析（前3步）===")
i=rm.find("## §17 大运"); 
if i>=0:
    s17=rm[i:]

print("\n\n=== 引擎da_yun_ji_xiong数据 ===")
for dy in a.get("da_yun_ji_xiong",[]):
    print(f"  {dy['gan_zhi']}: {dy['ji_xiong']} score={dy['score']} ({dy['gan_ss']})")

print("\n\n=== 报告中各步大运评分 ===")
import re
scores = re.findall(r'评分(\d+\.?\d*)/10', s17 if i>=0 else rm)
print(f"找到{len(scores)}个评分: {scores}")
