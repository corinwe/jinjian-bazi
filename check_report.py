#!/usr/bin/env python3
"""检查API数据和报告生成器的问题"""
import json, urllib.request

API = "http://localhost:9000/api/v1/analyze"

data = json.dumps({
    "name": "少爷测试", "gender": "男",
    "birth_year": 2011, "birth_month": 5, "birth_day": 31,
    "birth_hour": 10, "birth_minute": 0, "calendar": "solar"
}).encode('utf-8')
req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req, timeout=30)
d = json.loads(resp.read())
a = d["analysis"]
rm = d.get("report_md", "")

print("=== 引擎数据（可用的）===")
print(f"大运吉凶（8步）:")
for dy in a["da_yun_ji_xiong"]:
    print(f"  {dy['gan_zhi']}: {dy['ji_xiong']} ({dy['gan_ss']}) score={dy['score']}")

cx = a["cai_xing"]
print(f"\n财星总分: {cx.get('score','?')} | 等级: {cx.get('wealth_level','?')} | 财库: {cx.get('has_ku','?')}")
if cx.get('cai_ku'):
    print(f"财库详情: {cx['cai_ku']}")

print(f"财富量级: {a['cai_fu_deng_ji']['level']} ({a['cai_fu_deng_ji']['score']}分)")
print(f"身强弱: {a['shen_qiang_ruo']['level']} ({a['shen_qiang_ruo']['score']}分)")
print(f"喜用神: {a['xi_yong_shen']['xi_shen']} | 忌神: {a['xi_yong_shen']['ji_shen']}")

print("\n=== 报告§8财富分析 ===")
# 找§8内容
s8_start = rm.find("§8")
s8_end = rm.find("§9") if rm.find("§9") > s8_start else len(rm)
s8 = rm[s8_start:s8_end]
print(s8[:2000])

print("\n\n=== 报告§6大运分析 ===")
s6_start = rm.find("§6")
s6_end = rm.find("§7") if rm.find("§7") > s6_start else len(rm)
s6 = rm[s6_start:s6_end]
print(s6[:2000])

print("\n\n=== 报告§5用神忌神 ===")
s5_start = rm.find("§5")
s5_end = rm.find("§6") if rm.find("§6") > s5_start else len(rm)
s5 = rm[s5_start:s5_end]
print(s5[:2000])
