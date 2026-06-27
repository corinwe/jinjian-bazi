"""
金鉴真人·统一分析引擎 v3.0 — 全量模块集成

分析步骤（严格按序，每步规则基于身强弱→喜忌→刑冲合害→能量→断事）:
  Step 1:  排盘基础信息
  Step 2:  十神判定（天干+藏干）
  Step 3:  身强弱评分（金鉴真人原始规则）
  Step 4:  财星评分
  Step 5:  格局判定
  Step 6:  喜用神（含调候）
  Step 7:  五行能量分布
  Step 8:  地支关系（刑冲合害·三合六合）
  Step 9:  神煞系统（12种）
  Step 10: 大运评估+排序
  Step 11: 流年精准分析（30年·含事件断法）
  Step 12: 学历学业分析（六步排查+文昌）
  Step 13: 性格分析（十神+五行+身强弱）
  Step 14: 原生家庭分析（年柱+月柱）
  Step 15: 婚姻分析（四大信号+三个窗口）
  Step 16: 8大维度评分
  Step 17: 关键事件年表（发财·灾祸·结婚·职业·学业·健康）
  Step 18: 结构化JSON输出
"""

from __future__ import annotations

from datetime import datetime

from cai_xing import compute_cai_xing
from character import analyze_character
from constants import TIAN_GAN_WU_XING, BaZi, Pillar
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
from shi_shen import get_all_cang_gan_shi_shen, get_shi_shen_all_dry
from xing_chong_he_hua import check_all_relations


def run_v3(
    bazi: BaZi,
    birth_year: int = 1980,
    birth_month_lunar: int = 1,
    qi_yun_days: float = 1.1,
    current_year: int | None = None,
) -> dict:
    """
    完整分析流水线 v3 — 全量模块·全量规则
    """
    if current_year is None:
        current_year = datetime.now().year

    ri_zhu = bazi.ri_zhu
    all_gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    all_zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]

    # ═══════════════════════════════════════
    # Step 1-2: 基础信息+十神
    # ═══════════════════════════════════════
    basic = {
        "bazi": bazi.summary(),
        "gender": bazi.gender,
        "ri_zhu": {"gan": ri_zhu, "wu_xing": TIAN_GAN_WU_XING[ri_zhu]},
    }
    shi_shen = {"tian_gan": get_shi_shen_all_dry(bazi), "cang_gan": get_all_cang_gan_shi_shen(bazi)}

    # ═══════════════════════════════════════
    # Step 3: 身强弱
    # ═══════════════════════════════════════
    sqr_score, sqr_label, sqr_detail = compute_shen_qiang_ruo(bazi)
    shen_qiang_ruo = {
        "score": sqr_score,
        "label": sqr_label,
        "details": {
            "yue_ling_yin": sqr_detail.yue_ling_yin,
            "yue_ling_bi_jie": sqr_detail.yue_ling_bi_jie,
            "tian_gan_bi_jie": sqr_detail.tian_gan_bi_jie,
            "ri_zhi_yin_bi": sqr_detail.ri_zhi_yin_bi,
            "nian_shi_zhi_yin_bi": sqr_detail.nian_shi_zhi_yin_bi,
            "total": sqr_detail.total,
        },
    }

    # ═══════════════════════════════════════
    # Step 4: 财星
    # ═══════════════════════════════════════
    cai = compute_cai_xing(bazi)
    cai_xing = {
        "total": cai.total,
        "details": {
            "nian_zhi": cai.nian_zhi_score,
            "yue_ling": cai.yue_ling_score,
            "ri_zhi": cai.ri_zhi_score,
            "shi_gan": cai.shi_gan_score,
            "shi_zhi": cai.shi_zhi_score,
        },
    }

    # ═══════════════════════════════════════
    # Step 5-6: 格局+喜用神
    # ═══════════════════════════════════════
    main_ge, detail_ge = determine_ge_ju(bazi)
    xi, ji = determine_xi_yong_shen(bazi)
    th = get_tiao_hou_yong_shen(ri_zhu, birth_month_lunar)
    ge_ju = {"main": main_ge, "detail": detail_ge}
    xi_yong_shen = {"xi": xi, "ji": ji, "tiao_hou": th}

    # ═══════════════════════════════════════
    # Step 7-9: 能量+地支+神煞
    # ═══════════════════════════════════════
    energy = compute_energy_profile(bazi)
    di_zhi_guan_xi = check_all_relations(all_zhis)
    shen_sha = compute_all_shen_sha(all_gans, all_zhis, bazi.year.zhi, bazi.month.zhi, ri_zhu)

    # ═══════════════════════════════════════
    # Step 10: 大运
    # ═══════════════════════════════════════
    dy_list, qy_age, qy_year = compute_da_yun(bazi, birth_year, qi_yun_days)
    dy_scores = compute_da_yun_scores(bazi, dy_list)
    best_idx = max(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1
    worst_idx = min(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1

    da_yun = {
        "qi_yun_age": round(qy_age, 1),
        "qi_yun_year": qy_year,
        "list": [
            {
                "gan_zhi": dy.gan_zhi,
                "start_age": dy.start_age,
                "end_age": dy.end_age,
                "start_year": dy.start_year,
                "score": dy_scores[i][1],
            }
            for i, dy in enumerate(dy_list)
        ],
        "best_index": best_idx,
        "worst_index": worst_idx,
    }

    # 大运甘旨列表（用于流年分析）
    dy_gans = [dy.gan for dy in dy_list]
    dy_zhis = [dy.zhi for dy in dy_list]
    dy_start_years = [dy.start_year for dy in dy_list]
    dy_start_ages = [dy.start_age for dy in dy_list]

    # ═══════════════════════════════════════
    # Step 11: 流年分析（30年·含事件断法）
    # ═══════════════════════════════════════
    liu_nian_results = analyze_liu_nian_range(
        all_gans,
        all_zhis,
        ri_zhu,
        TIAN_GAN_WU_XING[ri_zhu],
        bazi.year.zhi,
        bazi.month.zhi,
        dy_gans,
        dy_zhis,
        dy_start_years,
        sqr_score,
        sqr_label,
        xi,
        ji,
        birth_year,
        current_year,
        30,
    )
    key_events = extract_key_events(liu_nian_results)

    # ═══════════════════════════════════════
    # Step 12: 学历分析
    # ═══════════════════════════════════════
    education = analyze_education(all_gans, all_zhis, ri_zhu, sqr_score, sqr_label, xi, dy_gans, dy_zhis, dy_start_ages)

    # ═══════════════════════════════════════
    # Step 13: 性格分析
    # ═══════════════════════════════════════
    character = analyze_character(ri_zhu, all_gans, sqr_label, sqr_score, di_zhi_guan_xi["summary"], shen_sha.summary)

    # ═══════════════════════════════════════
    # Step 14: 原生家庭
    # ═══════════════════════════════════════
    family = analyze_nian_yue(bazi.year.gan, bazi.year.zhi, bazi.month.gan, bazi.month.zhi, ri_zhu, sqr_label)

    # ═══════════════════════════════════════
    # Step 15: 婚姻分析
    # ═══════════════════════════════════════
    marriage = analyze_marriage(
        ri_zhu, bazi.day.zhi, bazi.gender, all_gans, sqr_label, sqr_score, xi, dy_gans, dy_zhis, dy_start_ages
    )

    # ═══════════════════════════════════════
    # Step 16: 维度评分
    # ═══════════════════════════════════════
    dimensions = {
        name: {"base": ds.base, "da_yun_bonus": ds.da_yun_bonus, "total": ds.total}
        for name, ds in DEFAULT_DIMENSIONS(bazi).items()
    }

    # ═══════════════════════════════════════
    # Step 17-18: 聚合输出
    # ═══════════════════════════════════════
    return {
        "version": "3.0",
        "engine": "金鉴真人·统一分析引擎 v3.0",
        "generated_at": datetime.now().isoformat(),
        # 基础
        "basic": basic,
        "shi_shen": shi_shen,
        # 核心
        "shen_qiang_ruo": shen_qiang_ruo,
        "cai_xing": cai_xing,
        "ge_ju": ge_ju,
        "xi_yong_shen": xi_yong_shen,
        # 能量与关系
        "energy": {
            "wu_xing": energy["wu_xing_energy"],
            "strongest": energy["strongest_wx"],
            "weakest": energy["weakest_wx"],
        },
        "di_zhi_guan_xi": {
            "summary": di_zhi_guan_xi["summary"],
            "chong": di_zhi_guan_xi["冲"],
            "xing": [x["type"] for x in di_zhi_guan_xi["刑"]],
            "hai": di_zhi_guan_xi["害"],
            "liu_he": di_zhi_guan_xi["六合"],
            "san_he": [s["type"] for s in di_zhi_guan_xi["三合"]],
            "ban_he": [s["type"] for s in di_zhi_guan_xi["半合"]],
        },
        "shen_sha": shen_sha.to_dict(),
        # 大运
        "da_yun": da_yun,
        # 基本面分析
        "education": education,
        "character": character,
        "family": family,
        "marriage": marriage,
        # 流年
        "liu_nian": {"recent_5": liu_nian_results[:5], "key_events": {k: v for k, v in key_events.items() if v}},
        # 维度
        "dimensions": dimensions,
    }


if __name__ == "__main__":
    test_cases = [
        ("家主", "甲", "午", "己", "巳", "戊", "午", "壬", "子", "男", 1968, 4),
        ("子源", "庚", "申", "辛", "巳", "甲", "午", "丙", "寅", "男", 1980, 4),
        ("主母", "戊", "午", "甲", "子", "庚", "戌", "丁", "亥", "女", 1976, 11),
    ]

    for name, yg, yz, mg, mz, dg, dz, hg, hz, gn, by, bm in test_cases:
        bazi = BaZi(year=Pillar(yg, yz), month=Pillar(mg, mz), day=Pillar(dg, dz), hour=Pillar(hg, hz), gender=gn)
        result = run_v3(bazi, by, bm)

        print(f"\n{'=' * 50}")
        print(f"【{name}】{bazi.summary()}")
        print(f"{'=' * 50}")
        print(f"身: {result['shen_qiang_ruo']['score']}分 → {result['shen_qiang_ruo']['label']}")
        print(f"财: {result['cai_xing']['total']}分 | 格局: {result['ge_ju']['detail']}")
        print(f"喜: {result['xi_yong_shen']['xi']} 忌: {result['xi_yong_shen']['ji']}")
        print(f"地支: {result['di_zhi_guan_xi']['summary']}")
        print(f"神煞: {result['shen_sha']['summary'][:50]}...")
        print(f"学历: {result['education']['school_level']} ({result['education']['degree']})")
        print(f"性格: {result['character']['personality_type'][:30]}...")
        print(f"家庭: {result['family']['summary'][:40]}...")
        print(f"婚姻: {result['marriage']['quality']} 最佳{result['marriage']['best_window_age']}岁")
        print("关键事件:")
        for etype, events in result["liu_nian"]["key_events"].items():
            if events:
                top = events[0]
                print(f"  {etype}: {top['year']}年 {top['description'][:30]}...")
