"""
叙述引擎集成 — 在pipeline_v5.py的run_pipeline中调用
"""


def add_narratives(result):
    """为result中所有21个章节附加narrative字段"""
    from narratives import (
        narrative_appearance,
        narrative_career,
        narrative_character,
        narrative_children,
        narrative_da_yun_curve,
        narrative_da_yun_detail,
        narrative_education,
        narrative_events,
        narrative_family,
        narrative_ge_ju,
        narrative_health,
        narrative_life_advice,
        narrative_marriage,
        narrative_overview,
        narrative_property,
        narrative_shen_qiang_ruo,
        narrative_verdicts,
        narrative_wealth,
        narrative_wu_xing_advice,
        narrative_xi_yong,
        narrative_zai_huo,
    )

    # §1 一页总览
    s1 = result.get("sec_1_overview", {})
    if s1:
        s1["narrative"] = narrative_overview(
            s1.get("bazi", ""),
            s1.get("ri_zhu", {}).get("gan", ""),
            s1.get("ri_zhu", {}).get("wx", ""),
            s1.get("gender", ""),
            result.get("sec_3_shen_qiang_ruo", {}).get("label", ""),
            result.get("sec_3_shen_qiang_ruo", {}).get("score", 0),
            result.get("sec_2_ge_ju", {}).get("detail", ""),
            result.get("sec_4_xi_yong", {}).get("xi", []),
            result.get("sec_4_xi_yong", {}).get("ji", []),
            s1.get("cai_xing_score", 0),
            result.get("sec_8_wealth", {}).get("wealth_level", ""),
            result.get("sec_4_xi_yong", {}).get("tiao_hou", ""),
        )

    # §2 格局
    s2 = result.get("sec_2_ge_ju", {})
    if s2:
        s2["narrative"] = narrative_ge_ju(
            s2.get("main", ""),
            s2.get("detail", ""),
            s1.get("bazi", "") if s1 else "",
            s1.get("ri_zhu", {}).get("gan", "") if s1 else "",
            result.get("sec_3_shen_qiang_ruo", {}).get("label", ""),
            result.get("sec_3_shen_qiang_ruo", {}).get("score", 0),
        )

    # §3 身强弱
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    if s3:
        s3["narrative"] = narrative_shen_qiang_ruo(s3.get("label", ""), s3.get("score", 0), s3.get("details", {}))

    # §4 喜用神
    s4 = result.get("sec_4_xi_yong", {})
    if s4:
        s4["narrative"] = narrative_xi_yong(s4.get("xi", []), s4.get("ji", []), s4.get("tiao_hou", ""))

    # §5 灾祸
    s5 = result.get("sec_5_zai_huo", {})
    if s5:
        s5["narrative"] = narrative_zai_huo(
            s5.get("misfortune_full", {}),
            s5.get("shen_sha_chong", []),
            s5.get("shen_sha_xing", []),
            s5.get("shen_sha_hai", []),
            s5.get("remission_advice", {}),
        )

    # §6 性格
    s6 = result.get("sec_6_character", {})
    if s6:
        s6["narrative"] = narrative_character(
            s1.get("ri_zhu", {}).get("gan", "") if s1 else "",
            s1.get("ri_zhu", {}).get("wx", "") if s1 else "",
            s3.get("label", "") if s3 else "",
            s3.get("score", 0) if s3 else 0,
            s2.get("main", "") if s2 else "",
            s4.get("xi", []) if s4 else [],
            s4.get("ji", []) if s4 else [],
            s6,
        )

    # §7 外貌
    s7 = result.get("sec_7_appearance", {})
    if s7:
        s7["narrative"] = narrative_appearance(
            s1.get("ri_zhu", {}).get("gan", "") if s1 else "",
            s2.get("main", "") if s2 else "",
            s3.get("label", "") if s3 else "",
        )

    # §8 财富
    s8 = result.get("sec_8_wealth", {})
    if s8:
        s8["narrative"] = narrative_wealth(
            s8.get("cai_xing_total", 0),
            s8.get("wealth_level", ""),
            s8.get("cai_ku", {}),
            s4.get("xi", []) if s4 else [],
            s4.get("ji", []) if s4 else [],
            s3.get("label", "") if s3 else "",
        )

    # §9 置业分析
    s9 = result.get("sec_9_property", {})
    if s9:
        s9["narrative"] = narrative_property(s9)

    # §10 事业
    s10 = result.get("sec_10_career", {})
    if s10:
        s10["narrative"] = narrative_career(
            s10,
            s2.get("main", "") if s2 else "",
            s2.get("detail", "") if s2 else "",
            s3.get("label", "") if s3 else "",
            s3.get("score", 0) if s3 else 0,
            s4.get("xi", []) if s4 else [],
        )

    # §11 学历
    s11 = result.get("sec_11_education", {})
    if s11:
        s11["narrative"] = narrative_education(s11, s3.get("label", "") if s3 else "")

    # §12 婚姻
    s12 = result.get("sec_12_marriage", {})
    if s12:
        s12["narrative"] = narrative_marriage(
            s12,
            s1.get("ri_zhu", {}).get("gan", "") if s1 else "",
            s1.get("gender", "") if s1 else "",
        )

    # §13 子女
    s13 = result.get("sec_13_children", {})
    if s13:
        s13["narrative"] = narrative_children(
            s13,
            s1.get("ri_zhu", {}).get("gan", "") if s1 else "",
        )

    # §14 健康
    s14 = result.get("sec_14_health", {})
    if s14:
        s14["narrative"] = narrative_health(
            s14,
            s1.get("ri_zhu", {}).get("gan", "") if s1 else "",
            s3.get("label", "") if s3 else "",
        )

    # §15 六亲
    s15 = result.get("sec_15_family", {})
    if s15:
        s15["narrative"] = narrative_family(
            s15,
            s1.get("ri_zhu", {}).get("gan", "") if s1 else "",
        )

    # §16 流年
    s16 = result.get("sec_16_events", {})
    if s16:
        s16["narrative"] = narrative_events(s16.get("key_events", {}))

    # §17 大运详批
    s17 = result.get("sec_17_da_yun_detail", {})
    if s17:
        s17["narrative"] = narrative_da_yun_detail(s17)

    # §18 三决断
    s18 = result.get("sec_18_verdicts", [])
    if s18:
        # 如果s18是列表，包装成dict传给narrative
        if isinstance(s18, list):
            result["sec_18_verdicts"] = {"verdicts": s18, "narrative": narrative_verdicts(s18)}
        else:
            s18["narrative"] = narrative_verdicts(s18.get("verdicts", []))

    # §19 运程总评
    s19 = result.get("sec_19_overall", {})
    if s19:
        s19["narrative"] = narrative_da_yun_curve(s19)

    # §20 五行补充
    s20 = result.get("sec_20_wu_xing_advice", {})
    if s20:
        s20["narrative"] = narrative_wu_xing_advice(s20)

    # §21 人生建议
    s21 = result.get("sec_21_advice", {})
    if s21:
        s21["narrative"] = narrative_life_advice(s21)

    return result
