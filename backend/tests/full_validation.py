"""金鉴真人引擎完整验证套件"""
import sys
sys.path.insert(0, '/root/jinjian/backend')
from app.services.bazi_engine import calculate_bazi

CASES = [
    {
        "name": "老板", "y":1980, "m":8, "d":6, "h":5, "min":0, "g":1,
        "golden": {
            "ba_zi": "庚申 癸未 辛亥 辛卯",
            "na_yin": ["石榴木","杨柳木","钗钏金","松柏木"],
            "sq": ("身强", 64.0), "gj": "偏印格",
            "xs": ["火","木","水"], "js": ["土","金"],
            "cx": (31.2, "小富"), "dy": "甲申",
        }
    },
    {
        "name": "少爷", "y":2011, "m":5, "d":31, "h":9, "min":9, "g":1,
        "golden": {
            "ba_zi": "辛卯 癸巳 丙戌 癸巳",
            "na_yin": ["松柏木","长流水","屋上土","长流水"],
            "sq": ("中和", 55.6), "gj": "正官格",
            "xs": ["水","金","土"], "js": ["木","火"],
            "cx": (30.8, "小富"), "dy": "壬辰",
        }
    },
    {
        "name": "主母", "y":1987, "m":7, "d":20, "h":12, "min":0, "g":0,
        "golden": {
            "ba_zi": "丁卯 丁未 庚午 壬午",
            "na_yin": ["炉中火","天河水","路旁土","杨柳木"],
            "sq": ("从弱", 50.0), "gj": "正印格",
            "xs": ["火","木","水"], "js": ["土","金"],
            "cx": (16.0, "小富"), "dy": "戊申",
        }
    },
]

passed = 0
failed = 0
total = 0

for c in CASES:
    r = calculate_bazi(c["y"], c["m"], c["d"], c["h"], c["min"], False, c["g"])
    b = r["basic"]
    a = r["analysis"]
    g = c["golden"]
    p = b["pillars"]
    
    total += 1
    ba_zi = b["ba_zi"]
    if ba_zi == g["ba_zi"]:
        passed += 1; s = "✅"
    else:
        failed += 1; s = "❌"
    print(f"{s} {c['name']} 八字: {ba_zi} (期望: {g['ba_zi']})")
    
    total += 1
    ny = [p[k]["na_yin"] for k in ["nian","yue","ri","shi"]]
    if ny == g["na_yin"]:
        passed += 1; s = "✅"
    else:
        failed += 1; s = "❌"
    print(f"  {s} 纳音: {ny} (期望: {g['na_yin']})")
    
    total += 1
    sq = a["shen_qiang_ruo"]
    sq_actual = (sq["level"], round(sq["score"], 1))
    if sq_actual == g["sq"]:
        passed += 1; s = "✅"
    else:
        failed += 1; s = "❌"
    print(f"  {s} 身强弱: {sq_actual} (期望: {g['sq']})")
    
    total += 1
    gj = a["ge_ju"]
    if gj == g["gj"]:
        passed += 1; s = "✅"
    else:
        failed += 1; s = "❌"
    print(f"  {s} 格局: {gj} (期望: {g['gj']})")
    
    total += 1
    xs = a["xi_yong_shen"]["xi_shen"]
    js = a["xi_yong_shen"]["ji_shen"]
    xs_ok = xs == g["xs"]
    js_ok = js == g["js"]
    if xs_ok and js_ok:
        passed += 1; s = "✅"
    else:
        failed += 1; s = "❌"
    print(f"  {s} 喜用: {xs} (期望: {g['xs']}) 忌: {js} (期望: {g['js']})")
    
    total += 1
    cx_score = round(a["cai_xing"]["score"], 1)
    cx_level = a["cai_xing"]["wealth_level"]
    cx_actual = (cx_score, cx_level)
    if cx_score == g["cx"][0] or abs(cx_score - g["cx"][0]) <= 2:
        # 允许2分误差（少爷的30分是近似值）
        level_ok = cx_level == g["cx"][1]
        if level_ok:
            passed += 1; s = "✅"
        else:
            failed += 1; s = "❌"
    else:
        failed += 1; s = "❌"
    print(f"  {s} 财星: {cx_actual} (期望: {g['cx']})")
    
    total += 1
    dy = a["da_yun"]["da_yun"][0]["gan_zhi"]
    if dy == g["dy"]:
        passed += 1; s = "✅"
    else:
        failed += 1; s = "❌"
    print(f"  {s} 大运起点: {dy} (期望: {g['dy']})")
    print()

print(f"="*50)
print(f"总计: {passed}/{total} 通过  |  {failed} 失败")
if failed == 0:
    print("🎉 全部通过！引擎修复完成！")
else:
    print(f"❌ {failed} 项需要继续修复")
