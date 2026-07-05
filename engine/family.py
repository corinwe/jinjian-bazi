"""
金鉴真人·原生家庭/六亲分析引擎 v1.0

规则框架:
  年柱: 祖上/早年家庭/遗传基因
  月柱: 父母/兄弟姐妹/出身环境
  日支: 配偶/婚姻（由婚姻模块处理）
  时柱: 子女/晚年（由子女模块处理）

  每柱分析维度:
  1. 天干十神 → 对人的性格影响
  2. 地支藏干 → 家庭能量底色
  3. 纳音 → 家运气质
  4. 神煞 → 特殊家世信息
  5. 刑冲合害 → 家庭关系互动（年柱被冲→离家/父母紧张，月柱被冲→兄弟/父母关系）
"""

from __future__ import annotations

from shi_shen import get_shi_shen_for_gan, get_shi_shen_for_cang_gan
from xing_chong_he_hua import check_all_relations, check_all_tian_gan_he, check_chong
from constants import DI_ZHI_CANG_GAN


def analyze_nian_yue(
    year_gan: str, year_zhi: str,
    month_gan: str, month_zhi: str,
    ri_zhu: str, shen_label: str,
    gender: str = "男",
    all_gans: list[str] | None = None,
    all_zhis: list[str] | None = None,
    xi_yong_wuxing: list[str] | None = None,
) -> dict:
    """
    原生家庭分析（年柱+月柱）

    参数:
        gender: "男" or "女" — 用于区分十神性别对应（男命正印=母亲，偏印=祖父；女命反之）
        all_gans: 四柱天干列表 [年, 月, 日, 时] — 用于检查天干五合（月干被合）
        all_zhis: 四柱地支列表 [年, 月, 日, 时] — 用于全面检查月支被冲
        xi_yong_wuxing: 喜用神五行列表，如 ["金","水"] — 用于喜用宫位分析
    """
    # ── 年柱十神 ──
    year_shi_shen = get_shi_shen_for_gan(year_gan, ri_zhu)

    # ── 月柱十神 ──
    month_shi_shen = get_shi_shen_for_gan(month_gan, ri_zhu)

    # ── 刑冲合害分析 — 家庭关系互动 ──
    rel = check_all_relations([year_zhi, month_zhi])

    family_notes = []

    # 年支被冲 → 早年离家/祖业不守
    if rel["冲"]:
        family_notes.append("年支与月支相冲→早年离家或父母关系紧张")

    # 年支月支相害 → 父母关系不睦
    if rel["害"]:
        family_notes.append("年支与月支相害→祖上/父母关系暗藏矛盾")

    # 年支月支相刑 → 家庭内部矛盾多
    if rel["刑"]:
        for x in rel["刑"]:
            family_notes.append(f"年支与月支{x['type']}→家庭内部矛盾多")

    # 年支月支六合 → 家庭和睦
    if rel["六合"]:
        family_notes.append("年支月支六合→家庭关系和睦")

    # ── P0-2: 月柱被合检测（天干五合） ──
    if all_gans and len(all_gans) >= 2:
        he_results = check_all_tian_gan_he(all_gans)
        # 检查月干是否参与天干五合
        month_he = [h for h in he_results if all_gans[1] in h["gans"]]
        for h in month_he:
            partner = h["gans"][0] if h["gans"][1] == all_gans[1] else h["gans"][1]
            family_notes.append(f"月干{month_gan}与{partner}五合（{h['wx']}）→父亲角色变化/父母离异信号")

    # ── P0-3: 月支被冲全面检查（四柱全检查） ──
    if all_zhis and len(all_zhis) >= 2:
        pillar_names = ["年柱", "日柱", "时柱"]
        month_chong = []
        for i, z in enumerate(all_zhis):
            if z != month_zhi and check_chong(month_zhi, z):
                # i=0→年柱, i=1→月柱(自身), i=2→日柱, i=3→时柱
                name_map = {0: "年柱", 2: "日柱", 3: "时柱"}
                month_chong.append(name_map.get(i, ""))
        if month_chong:
            family_notes.append(f"月支{month_zhi}被{'、'.join(month_chong)}相冲→母亲受冲击")

    # ── P1-1: 喜用神宫位分析 ──
    if xi_yong_wuxing:
        from constants import DI_ZHI_WU_XING, TIAN_GAN_WU_XING

        # 年柱检查：年干+年支五行是否在喜用神中
        year_gan_wx = TIAN_GAN_WU_XING.get(year_gan, "")
        year_zhi_wx = DI_ZHI_WU_XING.get(year_zhi, "")
        year_is_xi = year_gan_wx in xi_yong_wuxing or year_zhi_wx in xi_yong_wuxing

        # 月柱检查
        month_gan_wx = TIAN_GAN_WU_XING.get(month_gan, "")
        month_zhi_wx = DI_ZHI_WU_XING.get(month_zhi, "")
        month_is_xi = month_gan_wx in xi_yong_wuxing or month_zhi_wx in xi_yong_wuxing

        if year_is_xi:
            family_notes.append("年柱喜用宫位→祖上有德，家运得力")
        else:
            family_notes.append("年柱忌凶宫位→祖上拖累，早年资源不足")

        if month_is_xi:
            family_notes.append("月柱喜用宫位→父母得力，家庭支持佳")
        else:
            family_notes.append("月柱忌凶宫位→六亲拖累，家庭助力不足")

    # ── P1-2: 藏干分析（年支+月支） ──
    year_cang_gan_list = DI_ZHI_CANG_GAN.get(year_zhi, [])
    month_cang_gan_list = DI_ZHI_CANG_GAN.get(month_zhi, [])

    if year_cang_gan_list:
        cg_parts = []
        for cg, ratio in year_cang_gan_list:
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            cg_parts.append(f"{cg}({ss})")
        cg_desc = _cang_gan_year_desc(year_cang_gan_list, ri_zhu)
        family_notes.append(f"年支{year_zhi}藏干{'、'.join(cg_parts)}→{cg_desc}")

    if month_cang_gan_list:
        cg_parts = []
        for cg, ratio in month_cang_gan_list:
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            cg_parts.append(f"{cg}({ss})")
        cg_desc = _cang_gan_month_desc(month_cang_gan_list, ri_zhu)
        family_notes.append(f"月支{month_zhi}藏干{'、'.join(cg_parts)}→{cg_desc}")

    # ── P0-1: gender 区分男女命十神含义 ──
    if gender == "男":
        gender_note = _male_family_meaning(year_shi_shen, month_shi_shen)
    else:
        gender_note = _female_family_meaning(year_shi_shen, month_shi_shen)
    if gender_note:
        family_notes.append(gender_note)

    # ── 十神基础描述 ──
    year_desc_map = {
        "正印": "祖上有文化底蕴，家庭注重教育",
        "偏印": "祖上有特殊技艺或独门传承",
        "正财": "祖上经济条件较好，家庭物质充足",
        "偏财": "祖上经商或社交广泛",
        "正官": "祖上有公职或社会地位",
        "七杀": "祖上经历坎坷或有军警背景",
        "食神": "祖上擅长技艺，家庭氛围宽松",
        "伤官": "祖上怀才不遇或家庭有变动",
        "比肩": "祖上兄弟姐妹多，家庭负担重",
        "劫财": "祖上财产有纷争或过继",
    }
    month_desc_map = {
        "正印": "父母慈爱，重视教育",
        "偏印": "父母有特殊才能，亲子关系偏冷",
        "正财": "父母务实，经济稳定",
        "偏财": "父母社交广阔，收入来源多样",
        "正官": "父母管教严格，重视规矩",
        "七杀": "父母严厉或工作压力大",
        "食神": "家庭氛围宽松有爱",
        "伤官": "亲子间有代沟或冲突",
        "比肩": "兄弟姐妹关系紧密",
        "劫财": "兄弟姐妹间有竞争或资源争夺",
    }

    return {
        "year_pillar": {
            "gan": year_gan,
            "zhi": year_zhi,
            "shi_shen": year_shi_shen,
            "family_desc": year_desc_map.get(year_shi_shen, "普通家庭背景"),
            "cang_gan": [
                {"gan": cg, "ratio": ratio, "shi_shen": get_shi_shen_for_cang_gan(cg, ri_zhu)}
                for cg, ratio in year_cang_gan_list
            ],
        },
        "month_pillar": {
            "gan": month_gan,
            "zhi": month_zhi,
            "shi_shen": month_shi_shen,
            "family_desc": month_desc_map.get(month_shi_shen, "普通亲子关系"),
            "cang_gan": [
                {"gan": cg, "ratio": ratio, "shi_shen": get_shi_shen_for_cang_gan(cg, ri_zhu)}
                for cg, ratio in month_cang_gan_list
            ],
        },
        "family_interaction": {
            "刑冲合害关系": rel["summary"],
            "家庭互动解读": family_notes if family_notes else ["无明显冲刑害，家庭关系平稳"],
        },
        "shen_label": shen_label,
        "summary": f"年柱{year_shi_shen}+月柱{month_shi_shen}，{rel['summary']}",
    }


def _male_family_meaning(year_shi_shen: str, month_shi_shen: str) -> str:
    """男命：正印=母亲，偏印=祖父"""
    parts = []
    if year_shi_shen == "正印":
        parts.append("年柱正印→祖上母系文化传承")
    elif year_shi_shen == "偏印":
        parts.append("年柱偏印→祖父有特殊才能/另类传承")
    if month_shi_shen == "正印":
        parts.append("月柱正印→母亲慈爱、教育有方")
    elif month_shi_shen == "偏印":
        parts.append("月柱偏印→祖父参与抚养/亲子关系偏冷")
    return "；".join(parts) if parts else ""


def _female_family_meaning(year_shi_shen: str, month_shi_shen: str) -> str:
    """女命：正印=祖父/女婿，偏印=母亲"""
    parts = []
    if year_shi_shen == "正印":
        parts.append("年柱正印→祖父有德/祖上文化之家")
    elif year_shi_shen == "偏印":
        parts.append("年柱偏印→母亲影响深/祖上母系传承强")
    if month_shi_shen == "正印":
        parts.append("月柱正印→祖父或长辈得力")
    elif month_shi_shen == "偏印":
        parts.append("月柱偏印→母亲影响大/亲子关系紧密偏冷")
    return "；".join(parts) if parts else ""


def _cang_gan_year_desc(cang_gan_list: list[tuple[str, int]], ri_zhu: str) -> str:
    """年支藏干解读：祖上能量底色"""
    descs = []
    for cg, _ in cang_gan_list:
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if ss in ("正印", "偏印"):
            descs.append("祖上文墨传承")
        elif ss in ("正财", "偏财"):
            descs.append("祖上财富根基")
        elif ss in ("正官", "七杀"):
            descs.append("祖上官威或压力")
        elif ss in ("食神", "伤官"):
            descs.append("祖上技艺/才艺")
        elif ss in ("比肩", "劫财"):
            descs.append("祖上同辈缘重")
    return "、".join(descs) if descs else "祖上能量中性"


def _cang_gan_month_desc(cang_gan_list: list[tuple[str, int]], ri_zhu: str) -> str:
    """月支藏干解读：母系/母亲特征补充"""
    descs = []
    for cg, _ in cang_gan_list:
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if ss in ("正印", "偏印"):
            descs.append("母系印记深")
        elif ss in ("正财", "偏财"):
            descs.append("母亲务实持家")
        elif ss in ("正官", "七杀"):
            descs.append("母亲要求严格")
        elif ss in ("食神", "伤官"):
            descs.append("母亲有才艺开明")
        elif ss in ("比肩", "劫财"):
            descs.append("母亲兄弟姐妹缘重")
    return "、".join(descs) if descs else "母亲能量中性"
