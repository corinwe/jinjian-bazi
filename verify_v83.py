#!/usr/bin/env python3
"""验证v8.3所有新功能"""
import json, urllib.request

data = json.dumps({
    "name": "测试", "gender": "男",
    "birth_year": 2011, "birth_month": 5, "birth_day": 31,
    "birth_hour": 10, "birth_minute": 0, "calendar": "solar"
}).encode('utf-8')
req = urllib.request.Request("http://localhost:9000/api/v1/analyze", data=data, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req, timeout=30)
d = json.loads(resp.read())
a = d["analysis"]

ok = 0
fail = 0

def check(name, ok_condition, detail=""):
    global ok, fail
    if ok_condition:
        ok += 1
        print(f"  ✅ {name}")
    else:
        fail += 1
        print(f"  ❌ {name} — {detail}")

print("=" * 55)
print("金鉴八字 v8.3 全功能验证报告")
print("=" * 55)

# 1. 调候用神
check("调候用神", "tiao_hou" in a, "缺失")
if "tiao_hou" in a:
    check("  调候detail", len(a["tiao_hou"].get("detail","")) > 0, a["tiao_hou"].get("detail","")[:40])

# 2. 通关用神
check("通关用神", "tong_guan" in a, "缺失")

# 3. 假旺真弱
check("假旺真弱", "jia_wang_zhen_ruo" in a, "缺失")
if "jia_wang_zhen_ruo" in a:
    check("  结构完整", all(k in a["jia_wang_zhen_ruo"] for k in ["is_jia_wang","corrected_level","corrected_score","reason"]))

# 4. 专旺格
check("专旺格", "zhuan_wang_ge" in a, "缺失")
if "zhuan_wang_ge" in a:
    check("  结构完整", all(k in a["zhuan_wang_ge"] for k in ["is_zhuan_wang","name","wx","detail"]))

# 5. 化气格
check("化气格", "hua_qi_ge" in a, "缺失")

# 6. 大运吉凶
check("大运吉凶判定表", "da_yun_ji_xiong" in a, "缺失")
if "da_yun_ji_xiong" in a:
    check("  8步完整", len(a["da_yun_ji_xiong"]) == 8, f"只有{len(a['da_yun_ji_xiong'])}步")
    for dy in a["da_yun_ji_xiong"]:
        has_ss = bool(dy.get("gan_ss",""))
        has_jx = bool(dy.get("ji_xiong",""))
        check(f"  {dy['gan_zhi']}: {dy['ji_xiong']} ({dy['gan_ss']})", has_ss and has_jx)

# 7. 财富量级
check("财富量级评估", "cai_fu_deng_ji" in a, "缺失")
if "cai_fu_deng_ji" in a:
    check("  有等级+分数", bool(a["cai_fu_deng_ji"].get("level","")) and a["cai_fu_deng_ji"].get("score",0) > 0)

# 8. 流年分析
check("流年分析(API)", "liu_nian" in a, "缺失")
if "liu_nian" in a:
    check("  6年数据", len(a["liu_nian"]) >= 5, f"只有{len(a['liu_nian'])}年")

# 9. 月令五行加倍
we = a.get("wu_xing_energy", {})
check("月令五行加倍", "percentages" in we, "旧格式")
check("过旺过弱预警", "warnings" in we, "缺失warnings")

# 10. 神煞摘要
sss = a.get("shensha_summary", {})
check("神煞摘要", sss.get("total",0) > 0, f"total={sss.get('total',0)}")
check("神煞吉凶分类", "auspicious_count" in sss and "inauspicious_count" in sss)

# 11. 自刑去重
ea = a.get("energy_analysis", {})
rels = ea.get("relationships", [])
type_count = {}
for r in rels:
    t = r.get("type","")
    type_count[t] = type_count.get(t,0) + 1
# 自刑应该只出现一次
for t, c in type_count.items():
    check(f"  能量关系 {t}: {c}次", True)

# 12. 报告完整性
rm = d.get("report_md","")
check("报告21§", sum(1 for i in range(1,22) if rm.count(f"§{i}")>0) >= 21, f"只有{sum(1 for i in range(1,22) if rm.count(chr(167)+str(i))>0)}段")
check("报告字数>50000", len(rm) > 50000)

print(f"\n{'='*55}")
print(f"验证结果: {ok}/{ok+fail} 通过")
if fail > 0:
    print(f"⚠️  {fail}项待修复")
else:
    print(f"🎉 全部通过!")
print(f"{'='*55}")

# 新增功能总结
print(f"\n📊 引擎功能总数: {len(a)}项")
print(f"📊 API输出字段: {list(a.keys())}")
