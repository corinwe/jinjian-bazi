"""
金鉴真人引擎工程验证套件
===============
使用九龙道长官网(https://www.zydx.top/)做金标准比对。
"""
import sys, re
sys.path.insert(0, '/root/jinjian/backend')
from app.services.bazi_engine import calculate_bazi

# ──────────────────────────────────────────
# 测试用例 (来源：九龙道长官网手动验证通过)
# ──────────────────────────────────────────
GOLDEN_CASES = [
    # (name, Y, M, D, h, m, gender, expected_八字, expected_空亡四柱)
    
    # === 全家福 ===
    ("老板", 1980, 8, 6, 5, 0, 1, 
     "庚申 癸未 辛亥 辛卯", [["子","丑"],["申","酉"],["寅","卯"],["午","未"]]),
    
    ("少爷", 2011, 5, 31, 10, 0, 1,
     "辛卯 癸巳 丙戌 癸巳", [["午","未"],["午","未"],["午","未"],["午","未"]]),
    
    ("主母", 1987, 7, 20, 12, 0, 0,
     "丁卯 丁未 庚午 壬午", [["戌","亥"],["寅","卯"],["戌","亥"],["申","酉"]]),
]

def test_bazi():
    """测试四柱八字"""
    passed = 0
    failed = 0
    for name, y, m, d, h, min_, g, expected_bazi, expected_kw in GOLDEN_CASES:
        result = calculate_bazi(y, m, d, h, min_, is_lunar=False, gender=g)
        basic = result['basic']
        ba_zi = basic.get('ba_zi', '')
        
        if ba_zi == expected_bazi:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"{status} {name}: {ba_zi} (期望: {expected_bazi})")
    
    print(f"\n四柱验证: {passed}/{passed+failed} 通过")
    return failed == 0

def test_kong_wang():
    """测试空亡"""
    passed = 0
    failed = 0
    pillars_key = ['nian', 'yue', 'ri', 'shi']
    pname = ['年柱','月柱','日柱','时柱']
    
    for name, y, m, d, h, min_, g, expected_bazi, expected_kw in GOLDEN_CASES:
        result = calculate_bazi(y, m, d, h, min_, is_lunar=False, gender=g)
        pillars = result['basic'].get('pillars', {})
        
        for i, pk in enumerate(pillars_key):
            p = pillars.get(pk, {})
            kw = p.get('kong_wang', [])
            expected = expected_kw[i]
            if kw == expected:
                passed += 1
            else:
                failed += 1
                print(f"❌ {name} {pname[i]}: 引擎{kw} ≠ 期望{expected}")
    
    print(f"\n空亡验证: {passed}/{passed+failed} 通过")
    return failed == 0

def test_na_yin():
    """测试纳音（与官网比对）"""
    # 纳音金标准（从官网提取）
    expected = {
        # 老板: 庚申 癸未 辛亥 辛卯
        "庚申": "屋上土", "癸未": "杨柳木", "辛亥": "钗钏金", "辛卯": "松柏木",
        # 等待官网校对后补充...
    }
    return True

# ──────────────────────────────────────────
# 运行全部测试
# ──────────────────────────────────────────
all_pass = True
all_pass &= test_bazi()
all_pass &= test_kong_wang()
# all_pass &= test_na_yin()
# all_pass &= test_via_api()

print(f"\n{'='*50}")
print(f"总体结果: {'✅ 全部通过' if all_pass else '❌ 有不通过项'}")
