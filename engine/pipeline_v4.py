"""
金鉴真人·全量报告引擎 v4.0 — 21§完整映射

输出结构直接对应标准模板21个§
每§字段完整，无遗漏
"""

from __future__ import annotations

from datetime import datetime

from cai_xing import compute_cai_xing
from character import analyze_character
from comprehensive import *
from constants import NA_YIN, TIAN_GAN_WU_XING, BaZi, Pillar
from da_yun import compute_da_yun, compute_da_yun_scores
from dimensions import DEFAULT_DIMENSIONS
from education import analyze_education
from energy import compute_energy_profile
from family import analyze_nian_yue
from ge_ju import determine_ge_ju, determine_xi_yong_shen, get_tiao_hou_yong_shen
from liu_nian_v2 import analyze_liu_nian_range, extract_key_events
from marriage import analyze_marriage
from shen_qiang_ruo import compute_shen_qiang_ruo
from shen_sha import compute_all_shen_sha
from shi_shen import get_shi_shen_all_dry, get_shi_shen_for_gan
from xing_chong_he_hua import check_all_relations


def run_v4(bazi: BaZi, birth_year=1980, birth_month_lunar=1, qi_yun_days=1.1, current_year=None):
    if current_year is None:
        current_year = datetime.now().year

    ri_zhu = bazi.ri_zhu
    all_gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    all_zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]

    # 核心计算（复用v3）
    sqr_score, sqr_label, sqr_detail = compute_shen_qiang_ruo(bazi)
    cai = compute_cai_xing(bazi)
    main_ge, detail_ge = determine_ge_ju(bazi)
    xi, ji = determine_xi_yong_shen(bazi)
    th = get_tiao_hou_yong_shen(ri_zhu, birth_month_lunar)
    energy = compute_energy_profile(bazi)
    dz = check_all_relations(all_zhis)
    ss = compute_all_shen_sha(all_gans, all_zhis, bazi.year.zhi, bazi.month.zhi, ri_zhu)
    dy_list, qy_age, qy_year = compute_da_yun(bazi, birth_year, qi_yun_days)
    dy_scores = compute_da_yun_scores(bazi, dy_list)
    best_idx = max(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1
    worst_idx = min(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1
    dy_gans = [dy.gan for dy in dy_list]
    dy_zhis = [dy.zhi for dy in dy_list]
    dy_years = [dy.start_year for dy in dy_list]
    dy_ages = [dy.start_age for dy in dy_list]

    ln_results = analyze_liu_nian_range(
        all_gans,
        all_zhis,
        ri_zhu,
        TIAN_GAN_WU_XING[ri_zhu],
        bazi.year.zhi,
        bazi.month.zhi,
        dy_gans,
        dy_zhis,
        dy_years,
        sqr_score,
        sqr_label,
        xi,
        ji,
        birth_year,
        current_year,
        30,
    )
    key_evts = extract_key_events(ln_results)

    edu = analyze_education(all_gans, all_zhis, ri_zhu, sqr_score, sqr_label, xi, dy_gans, dy_zhis, dy_ages)
    char = analyze_character(ri_zhu, all_gans, sqr_label, sqr_score, dz["summary"], ss.summary)
    fam = analyze_nian_yue(bazi.year.gan, bazi.year.zhi, bazi.month.gan, bazi.month.zhi, ri_zhu, sqr_label)
    mar = analyze_marriage(
        ri_zhu, bazi.day.zhi, bazi.gender, all_gans, sqr_label, sqr_score, xi, dy_gans, dy_zhis, dy_ages
    )
    dims = {
        n: {"base": ds.base, "da_yun_bonus": ds.da_yun_bonus, "total": ds.total}
        for n, ds in DEFAULT_DIMENSIONS(bazi).items()
    }

    # 新增模块
    app = analyze_appearance(ri_zhu, sqr_label, sqr_score, all_gans, all_zhis)
    prop = analyze_property(
        ri_zhu,
        bazi.day.zhi,
        xi,
        [
            {"gan_zhi": d.gan_zhi, "score": dy_scores[i][1], "start_age": d.start_age, "end_age": d.end_age}
            for i, d in enumerate(dy_list)
        ],
        best_idx,
    )
    car = analyze_career_detail(ri_zhu, all_gans, sqr_label, xi, detail_ge)
    child = analyze_children(
        ri_zhu,
        bazi.gender,
        bazi.hour.gan,
        bazi.hour.zhi,
        [{"start_age": d.start_age, "end_age": d.end_age, "score": dy_scores[i][1]} for i, d in enumerate(dy_list)],
    )
    health = analyze_health_detail(all_gans, all_zhis, sqr_label, [e for evts in key_evts.values() for e in evts])
    best_dy = (
        {
            "gan_zhi": dy_list[best_idx].gan_zhi,
            "start_age": dy_list[best_idx].start_age,
            "end_age": dy_list[best_idx].end_age,
        }
        if best_idx >= 0
        else {}
    )
    verdicts = generate_three_verdicts(sqr_label, cai.total, detail_ge, best_dy, mar)
    dy_curve = generate_da_yun_curve(
        [
            {"gan_zhi": d.gan_zhi, "start_age": d.start_age, "end_age": d.end_age, "score": dy_scores[i][1]}
            for i, d in enumerate(dy_list)
        ]
    )
    wx_advice = generate_wu_xing_advice(xi)
    advice = generate_life_advice(
        sqr_label, cai.total, xi, detail_ge, [{"gan_zhi": d.gan_zhi, "start_age": d.start_age} for d in dy_list], mar
    )

    # ── 21§完整输出 ──
    return {
        "meta": {"version": "4.0", "engine": "金鉴真人·全量报告引擎 v4.0", "generated": datetime.now().isoformat()},
        # §1 总览
        "sec_1_overview": {
            "bazi": bazi.summary(),
            "na_yin": [
                NA_YIN.get(f"{bazi.year.gan}{bazi.year.zhi}", ""),
                NA_YIN.get(f"{bazi.month.gan}{bazi.month.zhi}", ""),
                NA_YIN.get(f"{bazi.day.gan}{bazi.day.zhi}", ""),
                NA_YIN.get(f"{bazi.hour.gan}{bazi.hour.zhi}", ""),
            ],
            "ri_zhu": {"gan": ri_zhu, "wx": TIAN_GAN_WU_XING[ri_zhu]},
            "gender": bazi.gender,
            "shen_qiang_ruo": f"{sqr_label}{sqr_score}分",
            "cong_ruo_check": "非从弱" if sqr_label != "从弱" else "从弱",
            "xi_yong": xi,
            "ji_shen": ji,
            "cai_xing_score": cai.total,
            "cai_xing_detail": {
                "yue": cai.yue_ling_score,
                "ri": cai.ri_zhi_score,
                "shi_gan": cai.shi_gan_score,
                "shi_zhi": cai.shi_zhi_score,
                "nian": cai.nian_zhi_score,
            },
            "best_da_yun": f"{dy_list[best_idx].gan_zhi}" if best_idx >= 0 else "",
            "best_da_yun_score": dy_scores[best_idx][1] if best_idx >= 0 else 0,
            "worst_da_yun": f"{dy_list[worst_idx].gan_zhi}" if worst_idx >= 0 else "",
            "worst_da_yun_score": dy_scores[worst_idx][1] if worst_idx >= 0 else 0,
            "qi_yun_age": round(qy_age, 1),
        },
        # §2 格局
        "sec_2_ge_ju": {"main": main_ge, "detail": detail_ge, "shi_shen": get_shi_shen_all_dry(bazi)},
        # §3 身强弱
        "sec_3_shen_qiang_ruo": {
            "score": sqr_score,
            "label": sqr_label,
            "details": {
                "yue_yin": sqr_detail.yue_ling_yin,
                "yue_bi": sqr_detail.yue_ling_bi_jie,
                "tg_bi": sqr_detail.tian_gan_bi_jie,
                "rz": sqr_detail.ri_zhi_yin_bi,
                "nsz": sqr_detail.nian_shi_zhi_yin_bi,
                "total": sqr_detail.total,
            },
        },
        # §4 喜用神
        "sec_4_xi_yong": {"xi": xi, "ji": ji, "tiao_hou": th},
        # §5 灾祸/搬迁
        "sec_5_za_i_hui": {
            "shen_sha_chong": dz["冲"],
            "shen_sha_xing": [x["type"] for x in dz["刑"]],
            "shen_sha_hai": dz["害"],
            "yuan_chen": ss.yuan_chen,
            "zai_sha": ss.zai_sha,
            "tian_luo": ss.tian_luo_di_wang,
            "wu_xing_over_three": [
                {"wx": k, "count": v} for k, v in compute_energy_profile(bazi)["wu_xing_energy"].items() if v >= 3
            ],
        },
        # §6 性格
        "sec_6_character": char,
        # §7 身材外貌
        "sec_7_appearance": app,
        # §8 财富
        "sec_8_wealth": {
            "cai_xing_total": cai.total,
            "cai_xing_details": {
                "nian": cai.nian_zhi_score,
                "yue": cai.yue_ling_score,
                "ri": cai.ri_zhi_score,
                "sg": cai.shi_gan_score,
                "sz": cai.shi_zhi_score,
            },
            "cai_ku": {
                "has": any(z in "辰戌丑未" for z in [bazi.day.zhi, bazi.hour.zhi]),
                "zhi": [z for z in [bazi.day.zhi, bazi.hour.zhi] if z in "辰戌丑未"],
            },
            "wealth_level": "小富" if cai.total < 40 else "中富" if cai.total < 60 else "大富",
        },
        # §9 置业
        "sec_9_property": prop,
        # §10 事业
        "sec_10_career": car,
        # §11 学历
        "sec_11_education": edu,
        # §12 婚姻
        "sec_12_marriage": mar,
        # §13 子女
        "sec_13_children": child,
        # §14 健康
        "sec_14_health": health,
        # §15 六亲
        "sec_15_family": fam,
        # §16 事件表
        "sec_16_events": {"key_events": key_evts, "recent_5": ln_results[:5]},
        # §17 大运精析
        "sec_17_da_yun_detail": {
            "list": [
                {
                    "gan_zhi": d.gan_zhi,
                    "start_age": d.start_age,
                    "end_age": d.end_age,
                    "start_year": d.start_year,
                    "score": dy_scores[i][1],
                    "gan_ss": get_shi_shen_for_gan(d.gan, ri_zhu),
                }
                for i, d in enumerate(dy_list)
            ],
            "best_idx": best_idx,
            "worst_idx": worst_idx,
        },
        # §18 三决断
        "sec_18_verdicts": verdicts,
        # §19 运程总评
        "sec_19_overall": dy_curve,
        # §20 五行补充
        "sec_20_wu_xing_advice": wx_advice,
        # §21 人生建议
        "sec_21_advice": advice,
    }


def format_21_section_report(result: dict) -> str:
    """将JSON输出格式化为可读文本"""
    lines = []
    lines.append(f"# 金鉴真人·八字命理分析报告 v{result['meta']['version']}")
    lines.append("")
    s1 = result["sec_1_overview"]
    lines.append("## §1 一页总览")
    lines.append(f"八字: {s1['bazi']} | 日主: {s1['ri_zhu']['gan']}({s1['ri_zhu']['wx']}) | {s1['gender']}")
    lines.append(f"身强弱: {s1['shen_qiang_ruo']} | {s1['cong_ruo_check']}")
    lines.append(f"喜用: {s1['xi_yong']} | 忌: {s1['ji_shen']}")
    lines.append(f"财星: {s1['cai_xing_score']}分 | 最佳运: {s1['best_da_yun']}({s1['best_da_yun_score']}/10)")
    lines.append("")

    s2 = result["sec_2_ge_ju"]
    lines.append(f"## §2 格局: {s2['detail']}")
    lines.append("")

    s8 = result["sec_8_wealth"]
    lines.append(
        f"## §8 财富: {s8['cai_xing_total']}分 | 等级: {s8['wealth_level']} | 财库: {'有' if s8['cai_ku']['has'] else '无'}"
    )
    lines.append("")

    s11 = result["sec_11_education"]
    lines.append(f"## §11 学历: {s11['school_level']}({s11['degree']})")
    lines.append("")

    s12 = result["sec_12_marriage"]
    lines.append(f"## §12 婚姻: {s12['quality']} | 最佳{s12['best_window_age']}岁")
    lines.append("")

    lines.append("## §16 关键事件")
    for etype, evts in result["sec_16_events"]["key_events"].items():
        if evts:
            for e in evts[:2]:
                lines.append(f"  {e['year']}年 | {e['description']}")
    lines.append("")

    s17 = result["sec_17_da_yun_detail"]
    lines.append("## §17 大运")
    for dy in s17["list"]:
        star = "🏆" if dy["score"] >= 8 else "✅" if dy["score"] >= 6 else "⚠️"
        lines.append(f"  {star} {dy['gan_zhi']}({dy['start_age']}~{dy['end_age']}岁) {dy['score']}/10")
    lines.append("")

    s19 = result["sec_19_overall"]
    lines.append("## §19 运程曲线")
    for c in s19["curve"]:
        lines.append(f"  {c['da_yun']}({c['age']}): {c['bar']} {c['score']}/10")
    lines.append("")

    lines.append("---")
    lines.append("金鉴真人·全量报告引擎 v4.0 | 21§完整输出")

    return "\n".join(lines)


if __name__ == "__main__":
    test_cases = [
        ("子源", "庚", "申", "辛", "巳", "甲", "午", "丙", "寅", "男", 1980, 4),
        ("家主", "甲", "午", "己", "巳", "戊", "午", "壬", "子", "男", 1968, 4),
    ]
    for name, yg, yz, mg, mz, dg, dz, hg, hz, gn, by, bm in test_cases:
        b = BaZi(year=Pillar(yg, yz), month=Pillar(mg, mz), day=Pillar(dg, dz), hour=Pillar(hg, hz), gender=gn)
        r = run_v4(b, by, bm)
        print(f"\n{'=' * 60}")
        print(f"【{name}】21§完整输出")
        print(f"{'=' * 60}")
        secs = [k for k in r if k.startswith("sec_")]
        print(f"覆盖§数量: {len(secs)}个")
        for s in sorted(secs):
            print(f"  {s}")
        print(f"\n{format_21_section_report(r)}")
