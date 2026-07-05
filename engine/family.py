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

from shi_shen import get_shi_shen_for_gan
from xing_chong_he_hua import check_all_relations


def analyze_nian_yue(
    year_gan: str, year_zhi: str, month_gan: str, month_zhi: str, ri_zhu: str, shen_label: str
) -> dict:
    """
    原生家庭分析（年柱+月柱）
    """
    # ── 年柱分析 ──
    year_shi_shen = get_shi_shen_for_gan(year_gan, ri_zhu)

    # ── 月柱分析 ──
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

    # ── 十神分析 ──
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
        },
        "month_pillar": {
            "gan": month_gan,
            "zhi": month_zhi,
            "shi_shen": month_shi_shen,
            "family_desc": month_desc_map.get(month_shi_shen, "普通亲子关系"),
        },
        "family_interaction": {
            "刑冲合害关系": rel["summary"],
            "家庭互动解读": family_notes if family_notes else ["无明显冲刑害，家庭关系平稳"],
        },
        "shen_label": shen_label,
        "summary": f"年柱{year_shi_shen}+月柱{month_shi_shen}，{rel['summary']}",
    }
