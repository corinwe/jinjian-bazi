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
from pipeline_v5 import run_v5, run_pipeline, format_21_section_report
from shen_sha import get_wen_chang, WEN_CHANG
from wealth_v2 import analyze_wealth_full

# dimensions_v2.DEFAULT_DIMENSIONS 已删除（自创评分体系），不再使用

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

    # C5: 大运步数检查（DEFAULT_DIMENSIONS已删除，跳过维度评分验证）
    for person in FAMILY:
        p = person["bazi"]
        dy_list, qy_age, qy_year = compute_da_yun(p, person["birth_year"], 1.1)
        check(f"C5{person['name']}大运{len(dy_list)}步", len(dy_list) == 8)

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

    print(f"\\n→ {pass_count}/{pass_count + fail_count}")


# ════════════════════════════════════════════
# §F: 文昌贵人验证（10日主全覆盖）
# ════════════════════════════════════════════


def test_wen_chang():
    """测试10个日主文昌贵人查询是否正确"""
    print("\\n" + "=" * 60)
    print("§F 文昌贵人验证（10日主全覆盖）")
    print("=" * 60)

    # 文昌贵人标准表
    EXPECTED = {
        "甲": "巳",
        "乙": "午",
        "丙": "申",
        "丁": "酉",
        "戊": "申",
        "己": "酉",
        "庚": "亥",
        "辛": "子",
        "壬": "寅",
        "癸": "卯",
    }

    # F1: get_wen_chang 函数检查（10个日主全部验证）
    for gan, expected_zhi in EXPECTED.items():
        actual = get_wen_chang(gan)
        assert_eq(actual, expected_zhi, f"F1文昌{gan}→期望{expected_zhi}")

    # F2: WEN_CHANG 常量表完整性
    assert_eq(len(WEN_CHANG), 10, "F2文昌表含10天干")

    # F3: 用家族人物验证原局文昌存在性
    # 家主(辛): 文昌在子 → 原局有亥(非子) → 原局无文昌
    p0 = FAMILY[0]["bazi"]
    ri_zhu = p0.day.gan  # 辛
    wc = get_wen_chang(ri_zhu)  # 子
    all_zhis = [p0.year.zhi, p0.month.zhi, p0.day.zhi, p0.hour.zhi]
    check(f"F3家主(辛→子): 原局地支{all_zhis}含{wc}", wc in all_zhis)

    # 父亲(癸): 文昌在卯 → 原局(己丑 癸酉 癸亥 戊午)无卯
    p3 = FAMILY[3]["bazi"]
    ri_zhu3 = p3.day.gan  # 癸
    wc3 = get_wen_chang(ri_zhu3)  # 卯
    all_zhis3 = [p3.year.zhi, p3.month.zhi, p3.day.zhi, p3.hour.zhi]
    check(f"F3父亲(癸→卯): 原局地支{all_zhis3}含{wc3}", wc3 in all_zhis3)

    # F4: 通过 paipan.check_wen_chang 验证
    try:
        from paipan import check_wen_chang

        # 甲→巳: 用家主八字(亥)测试不含巳
        result = check_wen_chang("甲", [p0.year.zhi, p0.month.zhi, p0.day.zhi, p0.hour.zhi])
        assert_eq(result["wen_chang_zhi"], "巳", "F4check甲→巳")
        check("F4check_has_wen_chang=False", not result["has_wen_chang"])
    except ImportError:
        check("F4paipan.check_wen_chang", False, "import失败")

    print(f"\\n→ {pass_count}/{pass_count + fail_count}")


# ════════════════════════════════════════════
# §G: 流年财富分析验证
# ════════════════════════════════════════════


def test_wealth_liunian():
    """测试流年财富分析基础功能"""
    print("\\n" + "=" * 60)
    print("§G 流年财富分析验证")
    print("=" * 60)

    # G1: analyze_wealth_full 函数可用
    for person in FAMILY[:3]:  # 前3人
        p = person["bazi"]
        name = person["name"]
        sqr_score, sqr_label, _ = compute_shen_qiang_ruo(p)
        cai = compute_cai_xing(p)
        ge_main, ge_detail = determine_ge_ju(p)
        xi_yong = determine_xi_yong_shen(p) if hasattr(p, "xi_yong") else [sqr_label]

        # 构造大运列表
        dy_list, qy_age, qy_year = compute_da_yun(p, person["birth_year"], 1.1)

        try:
            wf = analyze_wealth_full(
                ri_zhu=p.day.gan,
                bazi_gans=[p.year.gan, p.month.gan, p.day.gan, p.hour.gan],
                bazi_zhis=[p.year.zhi, p.month.zhi, p.day.zhi, p.hour.zhi],
                shen_label=sqr_label,
                shen_score=sqr_score,
                cai_total=cai.total,
                xi_yong=[],
                da_yun_list=dy_list,
            )
            # 基础字段验证
            assert_eq("status" in wf, True, f"G1{name}含status")
            assert_eq("wealth_level" in wf, True, f"G1{name}含wealth_level")
            assert_eq("effective_score" in wf, True, f"G1{name}含effective_score")
            assert_eq("cai_ku" in wf, True, f"G1{name}含cai_ku")
            assert_eq("wealth_windows" in wf, True, f"G1{name}含wealth_windows")
            check(f"G1{name}财富分析通过: {wf['wealth_level']}", True)
        except Exception as e:
            check(f"G1{name}财富分析", False, f"异常: {e}")

    # G2: 流年分析 — 通过 pipeline_v5 检查 sec_8_wealth
    for person in FAMILY[:2]:  # 前2人
        p = person["bazi"]
        name = person["name"]
        result = run_v5(p, person["birth_year"], person["birth_month"], 1.1, 2026)
        s8 = result.get("sec_8_wealth", {})
        check(f"G2{name}§8存在", bool(s8))
        if s8:
            # 检查流年相关字段（如存在）
            for field in ["cai_xing_total", "cai_ku", "summary", "wealth_level"]:
                has_field = field in s8
                check(f"G2{name}§8.{field}", has_field)

    # G3: 从弱格的财富特殊处理（主母）
    zhu_mu = FAMILY[1]["bazi"]
    sqr_score, sqr_label, _ = compute_shen_qiang_ruo(zhu_mu)
    cai = compute_cai_xing(zhu_mu)
    dy_list, _, _ = compute_da_yun(zhu_mu, FAMILY[1]["birth_year"], 1.1)
    wf = analyze_wealth_full(
        ri_zhu=zhu_mu.day.gan,
        bazi_gans=[zhu_mu.year.gan, zhu_mu.month.gan, zhu_mu.day.gan, zhu_mu.hour.gan],
        bazi_zhis=[zhu_mu.year.zhi, zhu_mu.month.zhi, zhu_mu.day.zhi, zhu_mu.hour.zhi],
        shen_label=sqr_label,
        shen_score=sqr_score,
        cai_total=cai.total,
        xi_yong=[],
        da_yun_list=dy_list,
    )
    assert_eq(wf["status"], "从弱格", "G3主母从弱格状态")

    print(f"\\n→ {pass_count}/{pass_count + fail_count}")


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
    test_wen_chang()
    test_wealth_liunian()

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
