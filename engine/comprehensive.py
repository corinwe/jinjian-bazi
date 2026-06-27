"""
金鉴真人·全局补充模块 v1.0 — 补齐模板缺失的8个§
"""

from __future__ import annotations

from constants import DI_ZHI_CANG_GAN, TIAN_GAN_WU_XING


# ── §7 身材外貌 ──
def analyze_appearance(ri_zhu: str, shen_label: str, shen_score: float, bazi_gans: list, bazi_zhis: list) -> dict:
    wx = TIAN_GAN_WU_XING[ri_zhu]
    desc_map = {
        "木": "身形修长挺拔，气质清秀，四肢协调。",
        "火": "面色红润，仪态大方，精力充沛，气场较强。",
        "土": "敦厚稳重，骨骼坚实，给人可靠感。",
        "金": "五官分明，骨架匀称，气质干练。",
        "水": "体态柔美，气质灵动，眼神清澈。",
    }
    height = "中等偏上(175-185cm)" if shen_label == "身强" else "中等(168-178cm)"
    return {
        "ri_zhu_appearance": desc_map.get(wx, "气质温和"),
        "height_estimate": height,
        "build": "骨架偏大/肌肉型" if shen_label == "身强" else "骨架偏小/纤细型",
        "style": "气质大方" if shen_label == "身强" else "气质斯文",
    }


# ── §9 置业/买房 ──
def analyze_property(ri_zhu: str, ri_zhi: str, xi_yong: list, da_yun_list: list, best_idx: int) -> dict:
    xi_wx = xi_yong[0] if xi_yong else "土"
    direction_map = {"金": "西/西北", "水": "北", "木": "东/东南", "火": "南", "土": "中"}

    windows = []
    if best_idx >= 0 and best_idx < len(da_yun_list):
        dy = da_yun_list[best_idx]
        windows.append({"age_range": f"{dy['start_age']}~{dy['end_age']}岁", "type": "最佳置业期"})

    return {
        "property_potential": f"喜用{xi_wx}→宜选{direction_map.get(xi_wx, '吉')}方位",
        "windows": windows,
        "risk": "忌在忌神大运购置大额不动产",
    }


# ── §10 事业详析 ──
def analyze_career_detail(ri_zhu: str, bazi_gans: list, shen_label: str, xi_yong: list, ge_ju_detail: str) -> dict:
    wx = TIAN_GAN_WU_XING[ri_zhu]
    career_map = {
        "木": "教育/文化/创意/环保/医疗",
        "火": "互联网/传媒/能源/娱乐/销售",
        "土": "房地产/建筑/农业/管理/咨询",
        "金": "金融/法律/科技/制造/审计",
        "水": "物流/贸易/旅游/传媒/人力资源",
    }
    level = "高管/管理型" if shen_label == "身强" else "专家/技术型"
    return {
        "career_level": level,
        "recommended_industries": career_map.get(wx, "多元化"),
        "management_potential": f"格局{ge_ju_detail}→{'适合管理' if '官' in ge_ju_detail else '适合技术'}",
        "entrepreneurship": "适合创业" if shen_label == "身强" and "财" in ge_ju_detail else "谨慎创业",
    }


# ── §13 子女 ──
def analyze_children(ri_zhu: str, gender: str, hour_gan: str, hour_zhi: str, da_yun_list: list) -> dict:
    if gender == "男":
        child_star_ss = ["七杀", "正官"]
    else:
        child_star_ss = ["伤官", "食神"]

    from shi_shen import get_shi_shen_for_gan

    hour_ss = get_shi_shen_for_gan(hour_gan, ri_zhu)

    windows = []
    for dy in da_yun_list:
        if 25 <= dy["start_age"] <= 45 and dy["score"] >= 5:
            windows.append(f"{dy['start_age']}~{dy['end_age']}岁")
            if len(windows) >= 2:
                break

    return {"child_star": hour_ss, "child_count_estimate": "1-2个", "windows": windows if windows else ["35~45岁"]}


# ── §14 健康 ──
def analyze_health_detail(bazi_gans: list, bazi_zhis: list, shen_label: str, liu_nian_events: list) -> dict:
    # 五行过三
    wx_count = {}
    for g in bazi_gans:
        wx = TIAN_GAN_WU_XING[g]
        wx_count[wx] = wx_count.get(wx, 0) + 1
    for z in bazi_zhis:
        for cg, _ in DI_ZHI_CANG_GAN.get(z, []):
            wx = TIAN_GAN_WU_XING[cg]
            wx_count[wx] = wx_count.get(wx, 0) + 1

    organ_map = {
        "金": "肺/大肠/呼吸",
        "木": "肝/胆/神经",
        "水": "肾/膀胱/内分泌",
        "火": "心/小肠/眼",
        "土": "脾/胃/消化",
    }

    risks = []
    for wx, cnt in wx_count.items():
        if cnt >= 3:
            risks.append({"wx": wx, "organ": organ_map.get(wx, ""), "risk": f"过三→注意{organ_map.get(wx, '')}"})

    return {
        "wu_xing_over_three": risks,
        "constitution": "体质偏强" if shen_label == "身强" else "体质偏弱",
        "focus_years": [e["year"] for e in liu_nian_events if e.get("event_type") == "health"][:5],
    }


# ── §18 三决断 ──
def generate_three_verdicts(
    shen_label: str, cai_score: float, ge_ju_detail: str, best_da_yun: dict, marriage_info: dict
) -> list:
    verdicts = []
    # 决断一: 财富
    verdicts.append(
        {
            "title": "财富格局",
            "person": "格局+财星",
            "event": f"财星{cai_score}分+{shen_label}",
            "time": f"最佳{best_da_yun.get('gan_zhi', '')}运({best_da_yun.get('start_age', '')}~{best_da_yun.get('end_age', '')}岁)",
            "degree": "小富~中富" if cai_score < 40 else "中富以上",
            "reason": f"格局{ge_ju_detail}+财星{cai_score}分+{shen_label}",
        }
    )
    # 决断二: 婚姻
    verdicts.append(
        {
            "title": "婚姻缘分",
            "person": "夫妻宫",
            "event": marriage_info.get("quality", "中等"),
            "time": marriage_info.get("best_window_age", "35岁前"),
            "degree": marriage_info.get("quality", "中等"),
            "reason": f"配偶特征{','.join(marriage_info.get('spouse_traits', ['温和']))}",
        }
    )
    # 决断三: 人生定位
    verdicts.append(
        {
            "title": "人生定位",
            "person": f"{shen_label}·{ge_ju_detail}",
            "event": "行业深耕+专业路线",
            "time": f"最佳{best_da_yun.get('gan_zhi', '')}运发力",
            "degree": "行业专家/中高层",
            "reason": f"{shen_label}+{ge_ju_detail}→选择正确赛道持续深耕",
        }
    )
    return verdicts


# ── §19 运程总评 ──
def generate_da_yun_curve(da_yun_list: list) -> dict:
    curve = []
    for dy in da_yun_list:
        score = dy.get("score", 5)
        bar = "█" * int(score) + "░" * (10 - int(score))
        curve.append(
            {"da_yun": dy["gan_zhi"], "age": f"{dy['start_age']}~{dy['end_age']}岁", "score": score, "bar": bar}
        )
    return {"curve": curve}


# ── §20 五行补充 ──
def generate_wu_xing_advice(xi_yong: list) -> dict:
    color_map = {"金": "白/金/银", "水": "蓝/黑/灰", "木": "绿/青", "火": "红/紫/橙", "土": "黄/棕/米"}
    direction_map = {"金": "西/西北", "水": "北", "木": "东/东南", "火": "南", "土": "中/西南/东北"}
    stone_map = {
        "金": "白金/银饰",
        "水": "黑曜石/海蓝宝",
        "木": "绿松石/翡翠",
        "火": "红玛瑙/石榴石",
        "土": "黄水晶/蜜蜡",
    }

    xi = xi_yong[0] if xi_yong else "土"
    return {
        "colors": color_map.get(xi, "白/蓝"),
        "numbers": {
            "lucky": "1,6(水) 4,9(金)" if xi in "金水" else "3,8(木) 2,7(火)",
            "avoid": "5,0(土)" if xi in "金水" else "1,6(水)",
        },
        "directions": direction_map.get(xi, "北"),
        "jewellery": stone_map.get(xi, "白水晶"),
        "diet": f"补{xi}性食物",
    }


# ── §21 人生建议（结构化） ──
def generate_life_advice(
    shen_label: str, cai_score: float, xi_yong: list, ge_ju_detail: str, da_yun_list: list, marriage_info: dict
) -> dict:
    return {
        "career": f"深耕专业领域，{ge_ju_detail}格局，选择{xi_yong[0] if xi_yong else '适合'}行业",
        "wealth": f"财星{cai_score}分，{shen_label}，大运窗口期全力积累",
        "health": f"体质{'偏强注意劳逸结合' if shen_label == '身强' else '偏弱注意调养'}",
        "marriage": f"婚姻质量{marriage_info.get('quality', '中等')}，注意沟通经营",
        "social": f"喜用{xi_yong[0] if xi_yong else '土'}→多与相关五行属性的人合作",
    }
