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
  5. 刑冲合害 → 家庭关系互动
"""

from __future__ import annotations
from constants import TIAN_GAN_WU_XING, DI_ZHI_WU_XING, NA_YIN
from shi_shen import get_shi_shen_for_gan, get_shi_shen_for_cang_gan


def analyze_nian_yue(
    year_gan: str, year_zhi: str,
    month_gan: str, month_zhi: str,
    ri_zhu: str,
    shen_label: str,
) -> dict:
    """
    原生家庭分析（年柱+月柱）
    """
    # ── 年柱分析 ──
    year_shi_shen = get_shi_shen_for_gan(year_gan, ri_zhu)
    
    year_fortune_map = {
        "正印": "祖上有文化传承",
        "偏印": "祖上有特殊技能/手艺",
        "正官": "祖上为公职人员或守规矩",
        "七杀": "祖上经历动荡或军武出身",
        "正财": "祖上家境殷实",
        "偏财": "祖上经商或人脉广",
        "比肩": "祖上兄弟多/家族大",
        "劫财": "祖上有竞争/争产",
        "食神": "祖上懂生活/有福气",
        "伤官": "祖上有才华但怀才不遇",
    }
    
    year_meaning = year_fortune_map.get(year_shi_shen, "祖上普通")
    
    # ── 月柱分析（父母/出身环境） ──
    month_shi_shen = get_shi_shen_for_gan(month_gan, ri_zhu)
    
    month_fortune_map = {
        "正印": "母亲慈爱/家庭文化氛围好",
        "偏印": "母亲独立或有特殊才能",
        "正官": "父亲正直/家教严格",
        "七杀": "父亲严厉/家庭竞争性强",
        "正财": "家境较好/父母会理财",
        "偏财": "父亲社交广/收入多元",
        "比肩": "兄弟姐妹多/家庭平等",
        "劫财": "兄弟姐妹有竞争/父母偏心力",
        "食神": "家庭氛围宽松/父母懂教育",
        "伤官": "父亲有才华/家庭叛逆氛围",
    }
    
    month_meaning = month_fortune_map.get(month_shi_shen, "出身普通")
    
    # ── 身强弱修正 ──
    family_pressure = ""
    if shen_label == "身弱":
        if month_shi_shen in ["七杀", "正官"]:
            family_pressure = "早期家庭/学业压力较大，需要印星大运化解"
        elif month_shi_shen in ["正财", "偏财"]:
            family_pressure = "家庭经济条件尚可但要求高"
    elif shen_label == "身强":
        if month_shi_shen in ["正印", "偏印"]:
            family_pressure = "家庭支持有力，成长环境好"
    
    # ── 家庭经济评估 ──
    economy_level = "中等"
    if month_shi_shen in ["正财", "偏财"]:
        economy_level = "中上"
    elif month_shi_shen in ["正印", "偏印"]:
        economy_level = "中等偏上"
    elif month_shi_shen in ["七杀", "劫财"]:
        economy_level = "一般偏紧"
    
    # ── 五行助力分析（源自bazi-foundation-analysis §30六亲助力规则）──
    wx_help = {}
    if shen_label == "身弱" and year_shi_shen in ["正印", "偏印"]:
        wx_help["parent_help"] = "身弱得印→得父母/祖上荫庇"
    elif shen_label == "身强" and year_shi_shen in ["正财", "偏财"]:
        wx_help["parent_help"] = "身旺财旺→家业丰厚"
    else:
        wx_help["parent_help"] = "父母助力一般，需结合大运分析"
    
    return {
        "nian_zhu": {
            "gan": year_gan,
            "zhi": year_zhi,
            "shi_shen": year_shi_shen,
            "meaning": year_meaning,
        },
        "yue_zhu": {
            "gan": month_gan,
            "zhi": month_zhi,
            "shi_shen": month_shi_shen,
            "meaning": month_meaning,
        },
        "family_economy": economy_level,
        "family_pressure": family_pressure or "无明显家庭压力",
        "summary": f"出身{economy_level}家庭，{year_meaning}。{month_meaning}。{family_pressure}",
        "year_pillar": {"detail": f"年干{year_gan}={year_shi_shen}，{year_meaning}"},
        "month_pillar": {"detail": f"月干{month_gan}={month_shi_shen}，{month_meaning}"},
        "day_pillar": {"detail": f"日支为配偶宫，由§12婚姻分析详细展开"},
        "hour_pillar": {"detail": f"时柱为子女宫，由§13子女分析详细展开"},
        "wu_xing_analysis": wx_help,
    }


if __name__ == "__main__":
    # 测试: 子源 庚申 辛巳 甲午 丙寅
    result = analyze_nian_yue("庚", "申", "辛", "巳", "甲", "身弱")
    print(f"原生家庭: {result['summary']}")
    print(f"经济: {result['family_economy']}")
