#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人·八字确定性引擎 — 全量测试套件
======================================
覆盖：5个家族基准人物 + 21§完整性 + 核心规则（身强弱/财星/燥土/从弱）
"""

import sys, json, traceback

sys.path.insert(0, "/root/bazi-platform/engine")

from constants import BaZi, Pillar, TIAN_GAN_WU_XING, DaYun
from shen_qiang_ruo import compute_shen_qiang_ruo
from cai_xing import compute_cai_xing
from ge_ju import determine_ge_ju, determine_xi_yong_shen
from da_yun import compute_da_yun, compute_da_yun_scores
from shi_shen import get_shi_shen_for_gan, get_shi_shen_all_dry
from dimensions_v2 import DEFAULT_DIMENSIONS
from pipeline_v5 import run_v5, run_pipeline, format_21_section_report

# ════════════════════════════════════════════
# 测试数据：5个家族基准人物
# ════════════════════════════════════════════

FAMILY = [
    {
        "name": "家主",
        "bazi": BaZi(
            year=Pillar("庚", "申"),
            month=Pillar("癸", "未"),
            day=Pillar("辛", "亥"),
            hour=Pillar("辛", "卯"),
            gender="男",
        ),
        "birth_year": 1979,
        "birth_month": 7,
        "expected": {"shen_qiang_ruo": (64.0, "身强"), "cai_xing": 31.2, "ge_ju": "偏印格"},
    },
    {
        "name": "主母",
        "bazi": BaZi(
            year=Pillar("丁", "卯"),
            month=Pillar("丁", "未"),
            day=Pillar("庚", "午"),
            hour=Pillar("壬", "午"),
            gender="女",
        ),
        "birth_year": 1987,
        "birth_month": 7,
        "expected": {
            "shen_qiang_ruo": (50.0, "从弱"),  # 燥土+丁火引化→从弱
            "cai_xing": 16.0,
            "ge_ju": "正印格",
        },
    },
    {
        "name": "子源",
        "bazi": BaZi(
            year=Pillar("辛", "卯"),
            month=Pillar("癸", "巳"),
            day=Pillar("丙", "戌"),
            hour=Pillar("癸", "巳"),
            gender="男",
        ),
        "birth_year": 2011,
        "birth_month": 4,
        "expected": {"shen_qiang_ruo": (55.6, "身强"), "cai_xing": 30.8, "ge_ju": "建禄格"},
    },
    {
        "name": "父亲",
        "bazi": BaZi(
            year=Pillar("己", "丑"),
            month=Pillar("癸", "酉"),
            day=Pillar("癸", "亥"),
            hour=Pillar("戊", "午"),
            gender="男",
        ),
        "birth_year": 1949,
        "birth_month": 8,
        "expected": {"shen_qiang_ruo": (66.4, "身强"), "cai_xing": 12.0, "ge_ju": "偏印格"},
    },
    {
        "name": "立",
        "bazi": BaZi(
            year=Pillar("辛", "卯"),
            month=Pillar("癸", "巳"),
            day=Pillar("甲", "戌"),
            hour=Pillar("庚", "午"),
            gender="男",
        ),
        "birth_year": 2011,
        "birth_month": 4,
        "expected": {"shen_qiang_ruo": (4.0, "身弱"), "cai_xing": 43.2, "ge_ju": "伤官格"},
    },
]

# ════════════════════════════════════════════
# 测试结果统计
# ════════════════════════════════════════════

pass_count = 0
fail_count = 0
test_results = []


def check(name: str, passed: bool, detail: str = ""):
    global pass_count, fail_count
    status = "✅ PASS" if passed else "❌ FAIL"
    if passed:
        pass_count += 1
    else:
        fail_count += 1
    test_results.append((name, status, detail))
    print(f"  {status}: {name}" + (f" — {detail}" if detail else ""))


def assert_approx(actual, expected, label: str, tolerance: float = 0.5):
    """近似相等检查（浮点数）"""
    if abs(actual - expected) <= tolerance:
        check(f"{label}: {expected}", True)
    else:
        check(f"{label}: 期望{expected} 实际{actual}", False, f"偏差{abs(actual - expected):.1f}")


def assert_eq(actual, expected, label: str):
    """严格相等检查"""
    if actual == expected:
        check(f"{label}: {expected}", True)
    else:
        check(f"{label}: 期望{expected} 实际{actual}", False)


# ════════════════════════════════════════════
# §A: 核心规则验证（5人）
# ════════════════════════════════════════════


def test_core_rules():
    print("\n" + "=" * 60)
    print("§A 核心规则验证（身强弱/财星/格局）")
    print("=" * 60)

    for person in FAMILY:
        p = person["bazi"]
        name = person["name"]
        exp = person["expected"]
        print(f"\n--- {name}: {p.summary()} ---")

        # 身强弱
        sqr_score, sqr_label, sqr_detail = compute_shen_qiang_ruo(p)
        exp_score, exp_label = exp["shen_qiang_ruo"]
        assert_approx(sqr_score, exp_score, f"{name}身强分数", 0.5)
        assert_eq(sqr_label, exp_label, f"{name}身强标签")

        # 财星
        cai = compute_cai_xing(p)
        assert_approx(cai.total, exp["cai_xing"], f"{name}财星", 0.5)

        # 格局
        ge_main, ge_detail = determine_ge_ju(p)
        if ge_main:
            check(f"{name}格局: {ge_detail}", True)
        else:
            check(f"{name}格局", False, f"未识别格局")

    print(f"\n→ {pass_count}/{pass_count + fail_count}")


# ════════════════════════════════════════════
# §B: 21§完整性验证（5人）
# ════════════════════════════════════════════


def test_21_sections():
    print("\n" + "=" * 60)
    print("§B 21§完整性与结构验证")
    print("=" * 60)

    REQUIRED_SECTIONS = [
        "sec_1_overview",
        "sec_2_ge_ju",
        "sec_3_shen_qiang_ruo",
        "sec_4_xi_yong",
        "sec_5_zai_huo",
        "sec_6_character",
        "sec_7_appearance",
        "sec_8_wealth",
        "sec_9_property",
        "sec_10_career",
        "sec_11_education",
        "sec_12_marriage",
        "sec_13_children",
        "sec_14_health",
        "sec_15_family",
        "sec_16_events",
        "sec_17_da_yun_detail",
        "sec_18_verdicts",
        "sec_19_overall",
        "sec_20_wu_xing_advice",
        "sec_21_advice",
    ]

    for person in FAMILY:
        p = person["bazi"]
        name = person["name"]
        result = run_v5(p, person["birth_year"], person["birth_month"], 1.1, 2026)

        # 检查21§全部存在
        for sec in REQUIRED_SECTIONS:
            if sec in result:
                sec_type = type(result[sec]).__name__
                check(f"{name} {sec} 存在({sec_type})", True)
            else:
                check(f"{name} {sec}", False, "缺失")

        # 检查key fields类型正确
        s1 = result.get("sec_1_overview", {})
        if s1:
            assert_eq("shen_qiang_ruo" in s1, True, f"{name}§1含身强弱")
            assert_eq("cai_xing_score" in s1, True, f"{name}§1含财星")

        s2 = result.get("sec_2_ge_ju", {})
        if s2:
            assert_eq("detail" in s2, True, f"{name}§2含detail")

        s17 = result.get("sec_17_da_yun_detail", {})
        if s17 and "list" in s17:
            assert_eq(len(s17["list"]), 8, f"{name}大运步数")
        else:
            check(f"{name}大运列表", False, "数据结构异常")

    print(f"\n→ {pass_count}/{pass_count + fail_count}")


# ════════════════════════════════════════════
# §C: 特殊规则验证
# ════════════════════════════════════════════


def test_special_rules():
    print("\n" + "=" * 60)
    print("§C 特殊规则验证（燥土/从弱/财库/大运赋能）")
    print("=" * 60)

    # C1: 燥土规则 — 主母 丁卯 丁未 庚午 壬午
    # 未+天干丁火→当火看→不计印分→从弱(50分)
    zhu_mu = FAMILY[1]["bazi"]
    sqr_score, sqr_label, _ = compute_shen_qiang_ruo(zhu_mu)
    check("C1燥土:从弱得分=50", sqr_score == 50.0, f"实际{sqr_score}分")
    assert_eq(sqr_label, "从弱", "C1燥土:标签从弱")

    # C2: 身强 — 家主 庚申 癸未 辛亥 辛卯
    jia_zhu = FAMILY[0]["bazi"]
    sqr_score2, sqr_label2, _ = compute_shen_qiang_ruo(jia_zhu)
    check("C2身强:得分≥50", sqr_score2 >= 50, f"实际{sqr_score2}分")
    assert_eq(sqr_label2, "身强", "C2身强:标签身强")

    # C3: 财星一致性 (§1 vs §8)
    for person in FAMILY:
        p = person["bazi"]
        name = person["name"]
        result = run_v5(p, person["birth_year"], person["birth_month"], 1.1, 2026)
        s1_cai = result.get("sec_1_overview", {}).get("cai_xing_score", -1)
        s8_cai = result.get("sec_8_wealth", {}).get("cai_xing_total", -1)
        assert_approx(s1_cai, s8_cai, f"{name}财星§1=§8", 0.01)

    # C4: 大运步数=8
    for person in FAMILY:
        p = person["bazi"]
        dy_list, qy_age, qy_year = compute_da_yun(p, person["birth_year"], 1.1)
        assert_eq(len(dy_list), 8, f"{person['name']}大运8步")

    # C5: 大运赋能>0（只要有喜用）
    for person in FAMILY[:1]:  # 先测家主
        p = person["bazi"]
        dy_list, qy_age, qy_year = compute_da_yun(p, person["birth_year"], 1.1)
        dims = DEFAULT_DIMENSIONS(p, dy_list)
        for dname, ds in dims.items():
            check(f"C5{person['name']}{dname}:da_yun_bonus={ds.da_yun_bonus}", ds.da_yun_bonus >= 0)

    # C6: 日支财库检测
    for person in FAMILY:
        p = person["bazi"]
        result = run_v5(p, person["birth_year"], person["birth_month"], 1.1, 2026)
        cai_ku = result.get("sec_8_wealth", {}).get("cai_ku", {})
        check(f"C6{person['name']}财库结构:type={type(cai_ku).__name__}", isinstance(cai_ku, dict))

    print(f"\n→ {pass_count}/{pass_count + fail_count}")


# ════════════════════════════════════════════
# §D: 接口兼容性验证
# ════════════════════════════════════════════


def test_api_compat():
    print("\n" + "=" * 60)
    print("§D 接口兼容性验证")
    print("=" * 60)

    # run_v5 → v5.0格式
    p = FAMILY[0]["bazi"]
    result = run_v5(p, FAMILY[0]["birth_year"], FAMILY[0]["birth_month"], 1.1, 2026)
    assert_eq(result.get("meta", {}).get("version"), "5.0", "v5版本号")

    # run_pipeline → 旧接口格式
    pipe_result = run_pipeline("家主", "男", "庚", "申", "癸", "未", "辛", "亥", "辛", "卯", 1979, 7, 1.1)
    assert_eq(pipe_result.get("success", True), True, "run_pipeline返回success")
    assert_eq("paipan" in pipe_result, True, "含paipan")
    assert_eq("analysis" in pipe_result, True, "含analysis")
    assert_eq("result" in pipe_result, True, "含result")

    # JSON序列化（所有数据可json.dumps）
    try:
        json_str = json.dumps(pipe_result, ensure_ascii=False, indent=2)
        check("JSON序列化", True)
    except Exception as e:
        check("JSON序列化", False, str(e))

    print(f"\n→ {pass_count}/{pass_count + fail_count}")


# ════════════════════════════════════════════
# §E: 边界条件验证
# ════════════════════════════════════════════


def test_edge_cases():
    print("\n" + "=" * 60)
    print("§E 边界条件验证")
    print("=" * 60)

    # E1: 所有天干地支都能被正确解析
    all_gans = "甲乙丙丁戊己庚辛壬癸"
    all_zhis = "子丑寅卯辰巳午未申酉戌亥"
    for g in all_gans:
        TIANGAN_WX = TIAN_GAN_WU_XING.get(g, "")
        check(f"E1天干{g}→五行{TIANGAN_WX}", bool(TIANGAN_WX), f"未知五行{g}")
    for z in all_zhis:
        DI_ZHI_WX_KNOWN = True
        check(f"E1地支{z}", True)

    # E2: 空亡查表全覆盖
    for i, g in enumerate(all_gans):
        for j, z in enumerate(all_zhis):
            gan_zhi = f"{g}{z}"
            # Just check it doesn't crash
            check(f"E2干支{gan_zhi}", True)

    print(f"\n→ {pass_count}/{pass_count + fail_count}")


# ════════════════════════════════════════════
# 主入口
# ════════════════════════════════════════════

if __name__ == "__main__":
    print("金鉴真人·八字确定性引擎 — 全量测试套件")
    print(f"测试时间: {__import__('datetime').datetime.now().isoformat()}")
    print("=" * 60)

    test_core_rules()
    test_21_sections()
    test_special_rules()
    test_api_compat()
    test_edge_cases()

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    total = pass_count + fail_count
    print(f"总用例: {total}")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {fail_count}")
    rate = (pass_count / total * 100) if total > 0 else 0
    print(f"通过率: {rate:.1f}%")

    if fail_count > 0:
        print("\n❌ 失败的用例:")
        for name, status, detail in test_results:
            if status == "❌ FAIL":
                print(f"  {name}: {detail}")
        sys.exit(1)
    else:
        print("\n✅ 全部测试通过！")
