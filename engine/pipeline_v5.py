"""
金鉴真人·全量报告引擎 v5.0 — 确定性规则引擎
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基于v2.0模块的完整pipeline：
  - comprehensive_v2 → 事业/子女/健康/外貌/置业/建议
  - education_v2 → 学历（年柱三档法+文昌双轨+印运时间线）
  - marriage_v2 → 婚姻（配偶星替代+四大信号+夫妻宫十神）
  - dimensions_v2 → 8大维度校准评分
  - 其余模块自v4.0继承

输出结构：21§完整映射
"""

from __future__ import annotations

import json
import sys
from datetime import datetime

from _gen_detail_analysis import attach_detail_analysis
from cai_xing import compute_cai_xing
from character import analyze_character
from comprehensive_v2 import run_comprehensive_engine
from constants import TIAN_GAN_WU_XING, BaZi, Pillar
from da_yun import compute_da_yun, compute_da_yun_scores

# dimensions_v2已删除（审计标记 2026-06-29: 自创评分体系），DEFAULT_DIMENSIONS不再使用
from education import analyze_education
from energy import compute_energy_profile
from family import analyze_nian_yue
from ge_ju import determine_ge_ju, determine_xi_yong_shen, get_tiao_hou_yong_shen
from liu_nian_v2 import analyze_liu_nian_range, extract_key_events
from marriage_v2 import analyze_marriage
from misfortune_analysis import analyze_misfortune, analyze_remission
from shen_qiang_ruo import compute_shen_qiang_ruo
from shen_sha import compute_all_shen_sha
from shi_shen import get_shi_shen_all_dry, get_shi_shen_for_gan
from xing_chong_he_hua import check_all_relations

# ── 地支藏干映射 ──
CANG_GAN_MAP = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

# ── 纳音查表（修复原引擎bug）──
NA_YIN_FULL = {
    "甲子": "海中金",
    "乙丑": "海中金",
    "丙寅": "炉中火",
    "丁卯": "炉中火",
    "戊辰": "大林木",
    "己巳": "大林木",
    "庚午": "路旁土",
    "辛未": "路旁土",
    "壬申": "剑锋金",
    "癸酉": "剑锋金",
    "甲戌": "山头火",
    "乙亥": "山头火",
    "丙子": "涧下水",
    "丁丑": "涧下水",
    "戊寅": "城头土",
    "己卯": "城头土",
    "庚辰": "白蜡金",
    "辛巳": "白蜡金",
    "壬午": "杨柳木",
    "癸未": "杨柳木",
    "甲申": "泉中水",
    "乙酉": "泉中水",
    "丙戌": "屋上土",
    "丁亥": "屋上土",
    "戊子": "霹雳火",
    "己丑": "霹雳火",
    "庚寅": "松柏木",
    "辛卯": "松柏木",
    "壬辰": "长流水",
    "癸巳": "长流水",
    "甲午": "沙中金",
    "乙未": "沙中金",
    "丙申": "山下火",
    "丁酉": "山下火",
    "戊戌": "平地木",
    "己亥": "平地木",
    "庚子": "壁上土",
    "辛丑": "壁上土",
    "壬寅": "金箔金",
    "癸卯": "金箔金",
    "甲辰": "覆灯火",
    "乙巳": "覆灯火",
    "丙午": "天河水",
    "丁未": "天河水",
    "戊申": "大驿土",
    "己酉": "大驿土",
    "庚戌": "钗钏金",
    "辛亥": "钗钏金",
    "壬子": "桑柘木",
    "癸丑": "桑柘木",
    "甲寅": "大溪水",
    "乙卯": "大溪水",
    "丙辰": "沙中土",
    "丁巳": "沙中土",
    "戊午": "天上火",
    "己未": "天上火",
    "庚申": "石榴木",
    "辛酉": "石榴木",
    "壬戌": "大海水",
    "癸亥": "大海水",
}


def _get_na_yin(gan: str, zhi: str) -> str:
    """正确的纳音查表"""
    return NA_YIN_FULL.get(f"{gan}{zhi}", "")


def _get_kong_wang(gan: str, zhi: str) -> str:
    """计算每柱空亡（根据干支所属旬）"""
    g = "甲乙丙丁戊己庚辛壬癸".index(gan)
    z = "子丑寅卯辰巳午未申酉戌亥".index(zhi)
    n = (6 * g - 5 * z) % 60  # 60甲子序号
    xun = n // 10  # 旬索引 0~5
    return ["戌亥", "申酉", "午未", "辰巳", "寅卯", "子丑"][xun]


def run_v5(bazi: BaZi, birth_year=1980, birth_month=1, birth_day=1, qi_yun_days=None, current_year=None):
    """v5.0 确定性pipeline主入口"""
    if current_year is None:
        current_year = datetime.now().year

    ri_zhu = bazi.ri_zhu
    all_gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    all_zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]

    # ═══════════════════════════════
    # 核心计算（确定性）
    # ═══════════════════════════════

    # 身强弱
    sqr_score, sqr_label, sqr_detail = compute_shen_qiang_ruo(bazi)

    # 财星
    cai = compute_cai_xing(bazi)

    # 格局+喜用神
    main_ge, detail_ge = determine_ge_ju(bazi)
    xi, ji = determine_xi_yong_shen(bazi)

    # 调候
    th = get_tiao_hou_yong_shen(ri_zhu, birth_month)

    # 五行能量
    energy = compute_energy_profile(bazi)

    # 地支关系
    dz = check_all_relations(all_zhis)

    # 神煞
    ss = compute_all_shen_sha(all_gans, all_zhis, bazi.year.zhi, bazi.month.zhi, ri_zhu)

    # 大运
    dy_list, qy_age, qy_year = compute_da_yun(bazi, birth_year, birth_month, birth_day, qi_yun_days)
    dy_scores = compute_da_yun_scores(bazi, dy_list)

    # 最佳/最差大运
    best_idx = max(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1
    worst_idx = min(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1

    dy_gans = [dy.gan for dy in dy_list]
    dy_zhis = [dy.zhi for dy in dy_list]
    dy_years = [dy.start_year for dy in dy_list]
    dy_ages = [dy.start_age for dy in dy_list]

    # 流年
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

    # ═══════════════════════════════
    # v2.0 模块（确定性规则引擎）
    # ═══════════════════════════════

    # 学历（v2 — 年柱三档法+文昌双轨+印运时间线）
    edu = analyze_education(all_gans, all_zhis, ri_zhu, sqr_score, sqr_label, xi, dy_gans, dy_zhis, dy_ages)

    # 婚姻（v2 — 配偶星替代+四大信号+夫妻宫十神）
    mar = analyze_marriage(
        ri_zhu, bazi.day.zhi, bazi.gender, all_gans, all_zhis, sqr_label, sqr_score, xi, dy_gans, dy_zhis, dy_ages
    )

    # 性格（已有模块）
    char = analyze_character(ri_zhu, all_gans, sqr_label, sqr_score, dz["summary"], ss.summary)

    # 原生家庭（已有模块）
    fam = analyze_nian_yue(
        bazi.year.gan, bazi.year.zhi, bazi.month.gan, bazi.month.zhi, ri_zhu, sqr_label,
        gender=bazi.gender, all_gans=all_gans, all_zhis=all_zhis, xi_yong_wuxing=xi,
    )

    # 8大维度（dimensions_v2已删除，跳过维度评分）
    dims = {}

    # 综合引擎（v2 — 事业/子女/健康/外貌/置业/三决断/建议）
    comprehensive = run_comprehensive_engine(
        bazi,
        sqr_score,
        sqr_label,
        sqr_detail,
        cai,
        main_ge,
        detail_ge,
        xi,
        ji,
        dy_list,
        dy_scores,
        best_idx,
        worst_idx,
        mar,
        edu,
        birth_year,
        current_year,
    )

    # ═══════════════════════════════
    # 灾祸分析（单次调用，修复审计双调用问题）
    # ═══════════════════════════════
    _kw_zhis_str = _get_kong_wang(bazi.day.gan, bazi.day.zhi)
    _kw_list = [c for c in _kw_zhis_str]  # "戌亥" → ["戌", "亥"]
    _dy_dict_list = [{"gan": d.gan, "zhi": d.zhi, "start_age": d.start_age} for d in dy_list]
    _mf = analyze_misfortune(
        all_gans, all_zhis, ri_zhu, bazi.gender,
        sqr_label, sqr_score,
        bazi.year.zhi, _get_na_yin(bazi.year.gan, bazi.year.zhi),
        current_year - birth_year,
        da_yun_list=_dy_dict_list,
        kong_wang_zhis=_kw_list,
        wu_xing_energy=energy["wu_xing_energy"],
        month_zhi=bazi.month.zhi,
    )
    _misfortune_ctx = {
        "shen_sha_chong": dz["冲"],
        "shen_sha_xing": [x["type"] for x in dz["刑"]],
        "shen_sha_hai": dz["害"],
        "yuan_chen": getattr(ss, "yuan_chen", ""),
        "zai_sha": getattr(ss, "zai_sha", ""),
        "tian_luo": getattr(ss, "tian_luo_di_wang", ""),
        "wu_xing_over_three": [
            {"wx": k, "count": v} for k, v in energy["wu_xing_energy"].items() if v >= 3
        ],
        "misfortune_full": _mf,
        "remission_advice": analyze_remission(xi, ji, _mf["risk_level"], _mf),
    }

    # ═══════════════════════════════
    # 21§完整输出
    # ═══════════════════════════════

    return {
        "meta": {"version": "5.0", "engine": "金鉴真人·确定性规则引擎 v5.0", "generated": datetime.now().isoformat()},
        # §1 一页总览
        "sec_1_overview": {
            "bazi": bazi.summary(),
            "na_yin": [
                _get_na_yin(bazi.year.gan, bazi.year.zhi),
                _get_na_yin(bazi.month.gan, bazi.month.zhi),
                _get_na_yin(bazi.day.gan, bazi.day.zhi),
                _get_na_yin(bazi.hour.gan, bazi.hour.zhi),
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
            "education": edu.get("display", ""),
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
        "sec_5_zai_huo": _misfortune_ctx,
        # §6 性格
        "sec_6_character": char,
        # §7 身材外貌（v2引擎）
        "sec_7_appearance": comprehensive["sec_7_appearance"],
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
            "wealth_level": "小富" if cai.total < 30 else "中富" if cai.total < 50 else "大富",
        },
        # §9 置业（v2引擎）
        "sec_9_property": comprehensive["sec_9_property"],
        # §10 事业（v2引擎）
        "sec_10_career": comprehensive["sec_6_career"],
        # §11 学历（v2引擎）
        "sec_11_education": edu,
        # §12 婚姻（v2引擎）
        "sec_12_marriage": mar,
        # §13 子女（v2引擎）
        "sec_13_children": comprehensive["sec_13_children"],
        # §14 健康（v2引擎）
        "sec_14_health": comprehensive["sec_14_health"],
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
                    "end_year": d.start_year + 9,
                    "score": dy_scores[i][1],
                    "gan_ss": get_shi_shen_for_gan(d.gan, ri_zhu),
                }
                for i, d in enumerate(dy_list)
            ],
            "best_idx": best_idx,
            "worst_idx": worst_idx,
        },
        # §18 三决断（v2引擎）
        "sec_18_verdicts": comprehensive["sec_18_verdicts"],
        # §19 运程总评（v2引擎）
        "sec_19_overall": comprehensive["sec_19_overall"],
        # §20 五行补充（v2引擎）
        "sec_20_wu_xing_advice": comprehensive["sec_20_wu_xing_advice"],
        # §21 人生建议（v2引擎）
        "sec_21_advice": comprehensive["sec_21_advice"],
    }


def format_21_section_report(result: dict) -> str:
    """将JSON输出格式化为可读文本 - 完整21§输出"""
    lines = []
    lines.append(f"# 金鉴真人·八字命理分析报告 v{result['meta']['version']}")
    lines.append("")

    s1 = result["sec_1_overview"]
    lines.append("## §1 一页总览")
    lines.append(f"八字: {s1['bazi']} | 日主: {s1['ri_zhu']['gan']}({s1['ri_zhu']['wx']}) | {s1['gender']}")
    lines.append(f"纳音: {' '.join(s1['na_yin'])}")
    lines.append(f"身强弱: {s1['shen_qiang_ruo']} | {s1['cong_ruo_check']}")
    lines.append(f"喜用: {s1['xi_yong']} | 忌: {s1['ji_shen']}")
    lines.append(f"财星: {s1['cai_xing_score']}分 | 学历: {s1.get('education', '')}")
    lines.append(f"最佳运: {s1['best_da_yun']}({s1['best_da_yun_score']}/10)")
    lines.append("")

    s2 = result["sec_2_ge_ju"]
    lines.append(f"## §2 格局: {s2['detail']}")
    lines.append("")

    s3 = result["sec_3_shen_qiang_ruo"]
    lines.append(f"## §3 身强弱: {s3['label']}{s3['score']}分")
    det = s3.get("details", {})
    lines.append(
        f"  月令印: {det.get('yue_yin', 0)} | 月令比劫: {det.get('yue_bi', 0)} | 天干比劫: {det.get('tg_bi', 0)} | 日支: {det.get('rz', 0)} | 年时: {det.get('nsz', 0)} | 总分: {det.get('total', 0)}"
    )
    lines.append("")

    s4 = result["sec_4_xi_yong"]
    lines.append(f"## §4 喜用神: {s4['xi']} | 忌神: {s4['ji']} | 调候: {s4.get('tiao_hou', '')}")
    lines.append("")

    s5 = result["sec_5_zai_huo"]
    lines.append("## §5 灾祸/化解")
    lines.append(f"  冲: {s5.get('shen_sha_chong', '无')}")
    lines.append(f"  刑: {s5.get('shen_sha_xing', '无')}")
    lines.append(f"  害: {s5.get('shen_sha_hai', '无')}")
    mf = s5.get("misfortune_full", {})
    if isinstance(mf, dict):
        lines.append(f"  风险等级: {mf.get('risk_level', '')}")
    rm = s5.get("remission_advice", {})
    if isinstance(rm, dict):
        lines.append(f"  化解: {rm.get('advice', '')}")
    lines.append("")

    s6 = result["sec_6_character"]
    if isinstance(s6, dict):
        lines.append(f"## §6 性格: {s6.get('main_trait', '')}")
        tags = s6.get("tags", [])
        if isinstance(tags, list):
            lines.append(f"  标签: {', '.join(tags)}")
    else:
        lines.append(f"## §6 性格: {s6}")
    lines.append("")

    s7 = result["sec_7_appearance"]
    if isinstance(s7, dict):
        lines.append(f"## §7 身材外貌: {s7.get('ri_zhu_appearance', '')}")
        lines.append(f"  体型: {s7.get('build', '')} | 身高: {s7.get('height_estimate', '')}")
        lines.append(f"  气质: {s7.get('style', '')}")
    lines.append("")

    s8 = result["sec_8_wealth"]
    lines.append(
        f"## §8 财富: {s8['cai_xing_total']}分 | 等级: {s8['wealth_level']} | 财库: {'有' if s8['cai_ku']['has'] else '无'}"
    )
    lines.append("")

    s9 = result["sec_9_property"]
    if isinstance(s9, dict):
        lines.append(f"## §9 置业: {s9.get('property_potential', '')} | 能力: {s9.get('property_level', '')}")
    lines.append("")

    s10 = result["sec_10_career"]
    if isinstance(s10, dict):
        lines.append(f"## §10 事业: {s10.get('career_direction', '')}")
        lines.append(f"  等级: {s10.get('career_grade', '')} | 模式: {s10.get('work_mode', '')}")
        lines.append(f"  行业: {s10.get('recommended_industries', '')}")
        lines.append(f"  创业: {s10.get('entrepreneurship', '')}")
    lines.append("")

    s11 = result["sec_11_education"]
    lines.append(f"## §11 学历: {s11.get('display', s11.get('school_level', ''))}")
    if isinstance(s11, dict):
        ypc = s11.get("year_pillar_check", {})
        if isinstance(ypc, dict):
            lines.append(f"  年柱印: {ypc.get('detail', '')}")
        nc = s11.get("nian_gan_check", {})
        if isinstance(nc, dict):
            lines.append(f"  年干十神: {nc.get('shi_shen', '')}")
        sc = s11.get("wen_chang_ming_li", {})
        if isinstance(sc, dict):
            lines.append(f"  文昌: {sc.get('detail', '')}")
    lines.append("")

    s12 = result["sec_12_marriage"]
    if isinstance(s12, dict):
        lines.append(
            f"## §12 婚姻: {s12.get('quality_display', s12.get('quality', ''))} | 最佳{s12.get('best_window_age', '')}"
        )
        lines.append(f"  配偶特征: {s12.get('spouse_trait', '')}")
    lines.append("")

    s13 = result["sec_13_children"]
    if isinstance(s13, dict):
        lines.append(f"## §13 子女: {s13.get('child_count_estimate', '')} | 成就: {s13.get('child_achievement', '')}")
        lines.append(f"  生育力: {s13.get('sheng_yu_potential', '')}")
        thin = s13.get("thin_factors", [])
        if thin and isinstance(thin, list):
            lines.append(f"  缘薄因素: {' | '.join(thin[:2])}")
    lines.append("")

    s14 = result["sec_14_health"]
    if isinstance(s14, dict):
        lines.append(f"## §14 健康: {s14.get('constitution', '')}")
        wxot = s14.get("wu_xing_over_three", [])
        if wxot and isinstance(wxot, list):
            for item in wxot[:2]:
                if isinstance(item, dict):
                    lines.append(f"  五行过三->{item.get('wx', '')}({item.get('count', '')}): {item.get('organ', '')}")
    lines.append("")

    s15 = result["sec_15_family"]
    if isinstance(s15, dict):
        lines.append(f"## §15 家庭六亲: {s15.get('summary', '')}")
    lines.append("")

    lines.append("## §16 关键事件")
    for etype, evts in result["sec_16_events"]["key_events"].items():
        if evts:
            for e in evts[:2]:
                lines.append(f"  {e['year']}年 | {e.get('description', '')}")
    lines.append("")

    s17 = result["sec_17_da_yun_detail"]
    lines.append("## §17 大运")
    for dy in s17["list"]:
        star = "🏆" if dy["score"] >= 8 else "✅" if dy["score"] >= 6 else "⚠️"
        lines.append(f"  {star} {dy['gan_zhi']}({dy['start_age']}~{dy['end_age']}岁) {dy['score']}/10")
    lines.append("")

    s18 = result["sec_18_verdicts"]
    if isinstance(s18, list):
        lines.append("## §18 三决断")
        for v in s18:
            if isinstance(v, dict):
                lines.append(f"  {v.get('title', '')}: {v.get('event', '')} | {v.get('time', '')}")
    lines.append("")

    s19 = result["sec_19_overall"]
    lines.append("## §19 运程曲线")
    for c in s19["curve"]:
        lines.append(f"  {c['da_yun']}({c['age']}): {c['bar']} {c['score']}/10")
    lines.append("")

    s20 = result["sec_20_wu_xing_advice"]
    if isinstance(s20, dict):
        lines.append("## §20 五行补充")
        lines.append(f"  颜色: {s20.get('colors', '')}")
        lines.append(f"  方向: {s20.get('directions', '')}")
        lines.append(f"  饰品: {s20.get('jewellery', '')}")
        lines.append(f"  饮食: {s20.get('diet', '')}")
    lines.append("")

    s21 = result["sec_21_advice"]
    if isinstance(s21, dict):
        lines.append("## §21 人生建议")
        ca = s21.get("career", {})
        if isinstance(ca, dict):
            lines.append(f"  事业: {ca.get('advice', '')}")
        wa = s21.get("wealth", {})
        if isinstance(wa, dict):
            lines.append(f"  财富: {wa.get('advice', '')}")
        ha = s21.get("health", {})
        if isinstance(ha, dict):
            lines.append(f"  健康: {ha.get('advice', '')}")
        ma = s21.get("marriage", {})
        if isinstance(ma, dict):
            lines.append(f"  婚姻: {ma.get('advice', '')}")
    lines.append("")

    lines.append("---")
    lines.append("金鉴真人·确定性规则引擎 v5.0 | 21§完整输出")

    return "\n".join(lines)


def run_pipeline(
    name: str,
    gender: str,
    year_gan: str,
    year_zhi: str,
    month_gan: str,
    month_zhi: str,
    day_gan: str,
    day_zhi: str,
    hour_gan: str,
    hour_zhi: str,
    birth_year: int = 1980,
    birth_month: int = 1,
    birth_day: int = 1,
    qi_yun_days: float | None = None,
) -> dict:
    """外部调用入口"""
    ri_zhu = day_gan
    bazi = BaZi(
        year=Pillar(year_gan, year_zhi),
        month=Pillar(month_gan, month_zhi),
        day=Pillar(day_gan, day_zhi),
        hour=Pillar(hour_gan, hour_zhi),
        gender=gender,
    )

    result = run_v5(bazi, birth_year, birth_month, birth_day, qi_yun_days)

    # 🆕 为所有21个§附加详细规则分析文本
    result = attach_detail_analysis(result)

    # 🆕 方案B: 为所有21个§附加命理师口吻的连贯叙述段落
    from narrative_integration import add_narratives

    result = add_narratives(result)

    # 构造兼容旧接口的输出
    energy_profile = compute_energy_profile(bazi)
    strongest_wx = (
        max(energy_profile.get("wu_xing_energy", {}).items(), key=lambda x: x[1])[0]
        if energy_profile.get("wu_xing_energy")
        else ""
    )
    weakest_wx = (
        min(energy_profile.get("wu_xing_energy", {}).items(), key=lambda x: x[1])[0]
        if energy_profile.get("wu_xing_energy")
        else ""
    )

    dims_raw = {}

    output = {
        "paipan": {
            "bazi": bazi.summary(),
            "year_gan": year_gan,
            "year_zhi": year_zhi,
            "month_gan": month_gan,
            "month_zhi": month_zhi,
            "day_gan": day_gan,
            "day_zhi": day_zhi,
            "hour_gan": hour_gan,
            "hour_zhi": hour_zhi,
            "ri_zhu": day_gan,
        },
        "basic_data": {
            "ri_zhu": {"gan": day_gan, "wu_xing": TIAN_GAN_WU_XING[day_gan]},
            "pillars": {
                "year": {
                    "gan": year_gan,
                    "zhi": year_zhi,
                    "shi_shen": get_shi_shen_for_gan(year_gan, ri_zhu),
                    "tian_gan": year_gan,
                    "di_zhi": year_zhi,
                    "cang_gan": CANG_GAN_MAP.get(year_zhi, []),
                    "na_yin": _get_na_yin(year_gan, year_zhi),
                    "kong_wang": _get_kong_wang(year_gan, year_zhi),
                },
                "month": {
                    "gan": month_gan,
                    "zhi": month_zhi,
                    "shi_shen": get_shi_shen_for_gan(month_gan, ri_zhu),
                    "tian_gan": month_gan,
                    "di_zhi": month_zhi,
                    "cang_gan": CANG_GAN_MAP.get(month_zhi, []),
                    "na_yin": _get_na_yin(month_gan, month_zhi),
                    "kong_wang": _get_kong_wang(month_gan, month_zhi),
                },
                "day": {
                    "gan": day_gan,
                    "zhi": day_zhi,
                    "shi_shen": "元男" if gender == "男" else "元女",
                    "tian_gan": day_gan,
                    "di_zhi": day_zhi,
                    "cang_gan": CANG_GAN_MAP.get(day_zhi, []),
                    "na_yin": _get_na_yin(day_gan, day_zhi),
                    "kong_wang": _get_kong_wang(day_gan, day_zhi),
                },
                "hour": {
                    "gan": hour_gan,
                    "zhi": hour_zhi,
                    "shi_shen": get_shi_shen_for_gan(hour_gan, ri_zhu),
                    "tian_gan": hour_gan,
                    "di_zhi": hour_zhi,
                    "cang_gan": CANG_GAN_MAP.get(hour_zhi, []),
                    "na_yin": _get_na_yin(hour_gan, hour_zhi),
                    "kong_wang": _get_kong_wang(hour_gan, hour_zhi),
                },
            },
            "tian_gan_notes": [],
            "di_zhi_notes": [],
        },
        "analysis": {
            "shen_qiang_ruo": result["sec_3_shen_qiang_ruo"],
            "cai_xing": {"total": result["sec_8_wealth"]["cai_xing_total"], **result["sec_8_wealth"]},
            "ge_ju": result["sec_2_ge_ju"],
            "xi_yong_shen": result["sec_4_xi_yong"],
            "energy": {
                "wu_xing": {k: f"{v}%" for k, v in energy_profile.get("wu_xing_energy", {}).items()},
                "wu_xing_energy": energy_profile.get("wu_xing_energy", {}),
                "strongest_wx": strongest_wx,
                "weakest_wx": weakest_wx,
            },
            "da_yun": {**result["sec_17_da_yun_detail"], "qi_yun_age": result["sec_1_overview"]["qi_yun_age"]},
            "dimensions": {
                n: {"base": ds.base, "da_yun_bonus": ds.da_yun_bonus, "total": ds.total} for n, ds in dims_raw.items()
            },
        },
        "result": result,
        "text": format_21_section_report(result),
    }

    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="金鉴真人·八字确定性分析引擎 v5.0")
    parser.add_argument("--name", required=True, help="姓名")
    parser.add_argument("--gender", required=True, choices=["男", "女"], help="性别")
    parser.add_argument("--year", type=int, required=True, help="出生年")
    parser.add_argument("--month", type=int, required=True, help="出生月")
    parser.add_argument("--day", type=int, required=True, help="出生日")
    parser.add_argument("--hour", type=int, required=True, help="出生时辰(0-23)")
    parser.add_argument("--minute", type=int, default=0, help="出生分")
    parser.add_argument("--lunar-month", type=int, default=None)
    parser.add_argument("--lunar-day", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="输出JSON")
    parser.add_argument("--pretty", action="store_true", help="美化输出")

    args = parser.parse_args()

    # 用paipan模块排盘
    from paipan import paipan as paipan_func

    calc_year, calc_month, calc_day = args.year, args.month, args.day

    paipan_result = paipan_func(args.name, args.gender, calc_year, calc_month, calc_day, args.hour)

    if not paipan_result or "error" in paipan_result:
        output = {"success": False, "error": str(paipan_result)}
        print(json.dumps(output, ensure_ascii=False))
        sys.exit(1)

    # 提取干支
    yg = paipan_result.get("year_pillar", {}).get("gan", "")
    yz = paipan_result.get("year_pillar", {}).get("zhi", "")
    mg = paipan_result.get("month_pillar", {}).get("gan", "")
    mz = paipan_result.get("month_pillar", {}).get("zhi", "")
    dg = paipan_result.get("day_pillar", {}).get("gan", "")
    dz = paipan_result.get("day_pillar", {}).get("zhi", "")
    hg = paipan_result.get("hour_pillar", {}).get("gan", "")
    hz = paipan_result.get("hour_pillar", {}).get("zhi", "")

    qi_yun_days = 1.1
    birth_month_val = args.lunar_month or calc_month

    output = run_pipeline(
        args.name, args.gender, yg, yz, mg, mz, dg, dz, hg, hz, calc_year, birth_month_val, args.day, qi_yun_days
    )
    output["success"] = True

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
    else:
        print(output.get("text", ""))
