"""
金鉴真人·婚姻分析引擎 v2.0 — 确定性规则版
基于bazi-marriage-analysis v1.3

核心规则：
  - 男命：正财=妻，偏财=情人
  - 女命：正官=夫，七杀=情人
  - 夫妻宫十神断婚姻质量
  - 四大结婚信号（按强度排序）
  - 配偶特征从夫妻宫推导
  - 婚姻质量评分
"""

from __future__ import annotations

from constants import DI_ZHI_CANG_GAN, DI_ZHI_WU_XING, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan

# ── 夫妻宫十神断婚姻 ──
FUFU_GONG_MALE = {
    "正官": "配偶正直",
    "七杀": "配偶霸道⚠️",
    "正印": "配偶有爱心",
    "偏印": "配偶敏感",
    "正财": "夫妻恩爱✅",
    "偏财": "配偶豪爽",
    "比肩": "配偶独立",
    "劫财": "离婚几率大❌",
    "食神": "配偶温和",
    "伤官": "配偶挑剔",
}

FUFU_GONG_FEMALE = {
    "正官": "配偶正直✅",
    "七杀": "配偶凶悍⚠️",
    "正印": "配偶包容",
    "偏印": "冷战、怄气❌",
    "正财": "配偶务实",
    "偏财": "配偶大方",
    "比肩": "配偶独立",
    "劫财": "感情不好⚠️",
    "食神": "欲望强",
    "伤官": "吵架闹矛盾❌",
}

# 配偶宫日支断相貌
ZI_WU_MAO_YOU = {"子": "漂亮", "午": "漂亮", "卯": "漂亮", "酉": "漂亮"}
YIN_SHEN_SI_HAI = {"寅": "一般", "申": "一般", "巳": "一般", "亥": "一般"}
CHEN_XU_CHOU_WEI = {"辰": "敦厚", "戌": "敦厚", "丑": "敦厚", "未": "敦厚"}

# 配偶宫五行断性功能
GONG_WX_SEX = {"土": "配偶肾功能偏弱（土克水）", "水": "肾功能强", "火": "精力旺盛", "金": "适度", "木": "和谐"}

# 结婚四大信号优先级
HUN_YIN_SIGNAL = {
    "正财透干": 5,  # 男命财星透干
    "正官透干": 5,  # 女命官星透干
    "合夫妻宫": 4,
    "冲夫妻宫": 3,
    "桃花年": 2,
    "印星帮身": 1,
}


def _get_pei_ou_xing(ri_zhu: str, gender: str, bazi_gans: list[str], bazi_zhis: list[str]) -> dict:
    """
    配偶星定位

    男命：正财=妻（首选），无正财→偏财替代
    女命：正官=夫（首选），无正官→七杀替代
    """
    result = {"primary": "", "secondary": "", "has_primary": False, "detail": ""}

    if gender == "男":
        # 正财=妻星
        zheng_cai = _find_shi_shen_in_bazi("正财", ri_zhu, bazi_gans, bazi_zhis)
        pian_cai = _find_shi_shen_in_bazi("偏财", ri_zhu, bazi_gans, bazi_zhis)

        if zheng_cai["found"]:
            result["primary"] = f"正财={zheng_cai['positions']}"
            result["has_primary"] = True
            result["detail"] = f"正财为妻星·有根✅→{zheng_cai['positions']}"
        elif pian_cai["found"]:
            result["primary"] = f"偏财={pian_cai['positions']}(替代)"
            result["has_primary"] = True
            result["detail"] = "无正财→偏财替代为妻星"
        else:
            result["detail"] = "配偶星缺失❌"

    else:  # 女命
        zheng_guan = _find_shi_shen_in_bazi("正官", ri_zhu, bazi_gans, bazi_zhis)
        qi_sha = _find_shi_shen_in_bazi("七杀", ri_zhu, bazi_gans, bazi_zhis)

        if zheng_guan["found"]:
            result["primary"] = f"正官={zheng_guan['positions']}"
            result["has_primary"] = True
            result["detail"] = f"正官为夫星·有根✅→{zheng_guan['positions']}"
        elif qi_sha["found"]:
            result["primary"] = f"七杀={qi_sha['positions']}(替代)"
            result["has_primary"] = True
            result["detail"] = "无正官→七杀替代为夫星"
        else:
            result["detail"] = "配偶星缺失❌"

    return result


def _find_shi_shen_in_bazi(target_ss: str, ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str]) -> dict:
    """在八字中找到指定十神的位置"""
    found = {"found": False, "positions": []}

    # 天干
    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == target_ss:
            found["found"] = True
            found["positions"].append(f"天干{['年', '月', '日', '时'][i]}")

    # 地支藏干
    for i, z in enumerate(bazi_zhis):
        for cg, ratio in DI_ZHI_CANG_GAN.get(z, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss == target_ss:
                level = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
                found["found"] = True
                found["positions"].append(f"{['年支', '月支', '日支', '时支'][i]}({cg}{level})")

    return found


def _analyze_fufu_gong(ri_zhi: str, ri_zhu: str, gender: str) -> dict:
    """夫妻宫（日支）十神分析"""
    result = {"zhi": ri_zhi, "shi_shens": [], "master": "", "quality_note": ""}

    # 日支藏干十神
    for cg, ratio in DI_ZHI_CANG_GAN.get(ri_zhi, []):
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        level = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
        result["shi_shens"].append({"cang_gan": cg, "shi_shen": ss, "level": level})

    # 本气十神
    if result["shi_shens"]:
        master_ss = result["shi_shens"][0]["shi_shen"]
        result["master"] = master_ss

        # 婚姻质量判定
        if gender == "男":
            note = FUFU_GONG_MALE.get(master_ss, "温和")
        else:
            note = FUFU_GONG_FEMALE.get(master_ss, "温和")
        result["quality_note"] = note

    # 外貌
    if ri_zhi in ZI_WU_MAO_YOU:
        result["appearance"] = "漂亮/帅气"
    elif ri_zhi in YIN_SHEN_SI_HAI:
        result["appearance"] = "长相一般"
    else:
        result["appearance"] = "敦厚老实"

    # 配偶宫五行
    wx = DI_ZHI_WU_XING.get(ri_zhi, "")
    result["spouse_wx"] = wx
    result["sex_note"] = GONG_WX_SEX.get(wx, "正常")

    return result


def _calculate_marriage_windows(
    ri_zhi: str,
    ri_zhu: str,
    gender: str,
    bazi_gans: list[str],
    shen_label: str,
    xi_yong: list[str],
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_ages: list[float],
) -> list:
    """结婚窗口分析 — 四大信号强度排序"""
    windows = []

    for dg, dz, sa in zip(da_yun_gans, da_yun_zhis, da_yun_start_ages, strict=False):
        if sa < 20 or sa > 55:
            continue

        score = 0
        reasons = []

        # 信号1: 正财/正官透干（最强）
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if gender == "男" and dg_ss == "正财":
            score += 5
            reasons.append("⭐⭐⭐⭐⭐正财透干")
        elif gender == "女" and dg_ss == "正官":
            score += 5
            reasons.append("⭐⭐⭐⭐⭐正官透干")

        # 信号2: 合夫妻宫
        chong_he_map = {
            "子": ["丑"],
            "丑": ["子"],
            "寅": ["亥"],
            "亥": ["寅"],
            "卯": ["戌"],
            "戌": ["卯"],
            "辰": ["酉"],
            "酉": ["辰"],
            "巳": ["申"],
            "申": ["巳"],
            "午": ["未"],
            "未": ["午"],
        }
        if dz in chong_he_map.get(ri_zhi, []):
            score += 4
            reasons.append("⭐⭐⭐⭐流年合夫妻宫")

        # 信号3: 冲夫妻宫
        chong_map = {
            "子": "午",
            "午": "子",
            "丑": "未",
            "未": "丑",
            "寅": "申",
            "申": "寅",
            "卯": "酉",
            "酉": "卯",
            "辰": "戌",
            "戌": "辰",
            "巳": "亥",
            "亥": "巳",
        }
        if chong_map.get(dz) == ri_zhi:
            score += 3
            reasons.append("⭐⭐⭐流年冲夫妻宫")

        # 大运为喜用
        dg_wx = TIAN_GAN_WU_XING.get(dg, "")
        if dg_wx in xi_yong:
            score += 1
            reasons.append("⭐喜用大运")

        if score >= 4:
            label = "🏆最佳窗口" if score >= 7 else "✅次佳窗口" if score >= 5 else "⚠️一般窗口"
            windows.append(
                {
                    "da_yun": f"{dg}{dz}",
                    "age_range": f"{sa}~{sa + 9}岁",
                    "score": score,
                    "label": label,
                    "reasons": reasons,
                }
            )

    windows.sort(key=lambda w: w["score"], reverse=True)
    return windows


def _calculate_marriage_quality(
    ri_zhi: str, ri_zhu: str, gender: str, shen_label: str, shen_score: float, pei_ou: dict, xi_yong: list[str]
) -> dict:
    """婚姻质量综合评分"""
    score = 5.0  # 基准分

    # 夫妻宫本气十神
    master_cg = DI_ZHI_CANG_GAN.get(ri_zhi, [])
    master_ss = get_shi_shen_for_cang_gan(master_cg[0][0], ri_zhu) if master_cg else ""

    # 加分项
    if gender == "男":
        if master_ss == "正财":
            score += 1.5  # 妻星入本位
        elif master_ss in ("正官", "正印"):
            score += 0.5
        if master_ss == "劫财":
            score -= 1.5  # 劫财克妻
    else:
        if master_ss == "正官":
            score += 1.5  # 夫星入本位
        elif master_ss in ("正印", "食神"):
            score += 0.5
        if master_ss == "伤官":
            score -= 1.5  # 伤官克夫
        if master_ss == "七杀":
            score -= 0.5

    # 配偶星存在加分
    if pei_ou.get("has_primary"):
        score += 1.0

    # 身强弱影响
    if shen_label == "身强":
        score += 0.5
    elif shen_label == "身弱":
        score -= 0.5

    score = max(1, min(10, score))

    if score >= 8:
        quality = "优秀"
    elif score >= 6.5:
        quality = "良好"
    elif score >= 5:
        quality = "中等"
    elif score >= 3:
        quality = "偏差"
    else:
        quality = "差"

    return {"score": round(score, 1), "quality": quality, "master_ss": master_ss}


def analyze_marriage(
    ri_zhu: str,
    ri_zhi: str,
    gender: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    shen_label: str,
    shen_score: float,
    xi_yong: list[str],
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_ages: list[float],
) -> dict:
    """
    婚姻完整分析 v2.0

    返回: 配偶星+夫妻宫+结婚窗口+质量评分
    """
    # ① 配偶星定位
    pei_ou = _get_pei_ou_xing(ri_zhu, gender, bazi_gans, bazi_zhis)

    # ② 夫妻宫分析
    fufu = _analyze_fufu_gong(ri_zhi, ri_zhu, gender)

    # ③ 结婚窗口
    windows = _calculate_marriage_windows(
        ri_zhi, ri_zhu, gender, bazi_gans, shen_label, xi_yong, da_yun_gans, da_yun_zhis, da_yun_start_ages
    )

    # ④ 婚姻质量评分
    quality = _calculate_marriage_quality(ri_zhi, ri_zhu, gender, shen_label, shen_score, pei_ou, xi_yong)

    # 最佳年龄
    best_window_age = "暂无明显窗口"
    if windows:
        best_window_age = windows[0]["age_range"].split("~")[0]

    # 配偶特征总结
    traits = []
    if fufu.get("appearance"):
        traits.append(f"相貌{fufu['appearance']}")
    if fufu.get("quality_note"):
        traits.append(f"性格{fufu['quality_note']}")
    if fufu.get("spouse_wx"):
        traits.append(f"五行偏{fufu['spouse_wx']}")

    return {
        "pei_ou_xing": pei_ou,
        "ri_zhi_analysis": fufu,
        "spouse_traits": traits,
        "spouse_description": "·".join(traits) if traits else "性格温和",
        "marriage_windows": windows[:3],
        "best_window_age": f"{best_window_age}岁",
        "quality": quality["quality"],
        "quality_score": quality["score"],
        "pei_ou_detail": f"配偶星{'存在' if pei_ou.get('has_primary') else '缺失'}",
        "fuqi_gong_shi_shen": fufu.get("master_ss", ""),
        "signal_detail": f"窗口{'、'.join([w['reason'][:15] for w in windows[:3] if 'reason' in w])}"
        if windows
        else "无显著结婚信号",
    }
