"""
金鉴真人·婚姻分析引擎 v2.1 — 确定性规则版（九龙道长原始理论修正）
基于bazi-marriage-analysis v1.4

核心规则：
  - 男命：正财=妻，偏财=情人
  - 女命：正官=夫，七杀=情人
  - 夫妻宫十神断婚姻质量
  - 四大结婚信号（按强度排序）
  - 配偶特征从夫妻宫推导
  - 婚姻质量评分（基于原始100分体系：刑冲破害扣分）
  - 婆媳关系（财克印原理）
"""

from __future__ import annotations

from constants import DI_ZHI_CANG_GAN, DI_ZHI_WU_XING, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan
from xing_chong_he_hua import check_chong, check_hai, check_xing

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

# 配偶宫日支断相貌（九龙道长原始理论）
ZI_WU_MAO_YOU = {"子": "漂亮", "午": "漂亮", "卯": "漂亮", "酉": "漂亮"}
YIN_SHEN_SI_HAI = {"寅": "一般", "申": "一般", "巳": "一般", "亥": "一般"}
CHEN_XU_CHOU_WEI = {"辰": "敦厚", "戌": "敦厚", "丑": "敦厚", "未": "敦厚"}

# ── 六破表（九龙道长原始理论）──
# 子酉破、寅亥破、卯午破、辰丑破、巳申破、未戌破
LIU_PO = {"子": "酉", "酉": "子", "寅": "亥", "亥": "寅",
           "卯": "午", "午": "卯", "辰": "丑", "丑": "辰",
           "巳": "申", "申": "巳", "未": "戌", "戌": "未"}

# ── 桃花查法（以年支查）──
# 申子辰→酉 | 亥卯未→子 | 寅午戌→卯 | 巳酉丑→午
TAO_HUA = {
    "申": "酉", "子": "酉", "辰": "酉",
    "亥": "子", "卯": "子", "未": "子",
    "寅": "卯", "午": "卯", "戌": "卯",
    "巳": "午", "酉": "午", "丑": "午",
}


def _get_pei_ou_xing(ri_zhu: str, gender: str, bazi_gans: list[str], bazi_zhis: list[str]) -> dict:
    """
    配偶星定位（九龙道长原始理论）

    男命：正财=妻（首选），无正财→偏财替代
    女命：正官=夫（首选），无正官→七杀替代
    """
    result = {"primary": "", "secondary": "", "has_primary": False, "detail": ""}

    if gender == "男":
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

    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == target_ss:
            found["found"] = True
            found["positions"].append(f"天干{['年', '月', '日', '时'][i]}")

    for i, z in enumerate(bazi_zhis):
        for cg, ratio in DI_ZHI_CANG_GAN.get(z, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss == target_ss:
                level = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
                found["found"] = True
                found["positions"].append(f"{['年支', '月支', '日支', '时支'][i]}({cg}{level})")

    return found


def _analyze_fufu_gong(ri_zhi: str, ri_zhu: str, gender: str) -> dict:
    """夫妻宫（日支）分析"""
    result = {"zhi": ri_zhi, "shi_shens": [], "master": "", "quality_note": ""}

    for cg, ratio in DI_ZHI_CANG_GAN.get(ri_zhi, []):
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        level = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
        result["shi_shens"].append({"cang_gan": cg, "shi_shen": ss, "level": level})

    if result["shi_shens"]:
        master_ss = result["shi_shens"][0]["shi_shen"]
        result["master"] = master_ss
        if gender == "男":
            note = FUFU_GONG_MALE.get(master_ss, "温和")
        else:
            note = FUFU_GONG_FEMALE.get(master_ss, "温和")
        result["quality_note"] = note

    # 配偶相貌（日支断相貌，九龙道长原始理论）
    if ri_zhi in ZI_WU_MAO_YOU:
        result["appearance"] = "漂亮/帅气"
    elif ri_zhi in YIN_SHEN_SI_HAI:
        result["appearance"] = "长相一般"
    else:
        result["appearance"] = "敦厚老实"

    # 配偶宫五行
    wx = DI_ZHI_WU_XING.get(ri_zhi, "")
    result["spouse_wx"] = wx

    return result


def _check_guan_sha_hun_za(ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str], gender: str) -> dict:
    """
    官杀混杂检查（女命专项·九龙道长原始理论）
    正官≥3且不透干 → 官多为杀 → 家暴风险
    """
    result = {"has_mixed": False, "detail": "", "risk_level": "正常"}
    if gender != "女":
        return result

    zheng_guan_count = 0
    guan_sha_tou_gan = False

    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == "正官":
            zheng_guan_count += 1
            guan_sha_tou_gan = True

    for z in bazi_zhis:
        for cg, ratio in DI_ZHI_CANG_GAN.get(z, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss == "正官":
                zheng_guan_count += 1

    if zheng_guan_count >= 3 and not guan_sha_tou_gan:
        result["has_mixed"] = True
        result["risk_level"] = "高风险"
        result["detail"] = f"正官{zheng_guan_count}个且不透干→官多为杀，家暴风险高⚠️"
    elif zheng_guan_count >= 2:
        result["detail"] = f"正官{zheng_guan_count}个，感情较复杂"

    return result


def _check_shi_zhi_chong_ri_zhi(all_zhis: list[str]) -> dict:
    """
    时支冲日支检查（九龙道长原始理论）
    时柱子女宫冲克日支夫妻宫 → 婚姻结构性矛盾
    """
    result = {"has_chong": False, "detail": ""}
    if len(all_zhis) < 4:
        return result

    ri_zhi = all_zhis[2]  # 日支
    shi_zhi = all_zhis[3]  # 时支

    if check_chong(shi_zhi, ri_zhi):
        result["has_chong"] = True
        result["detail"] = f"时支{shi_zhi}冲日支{ri_zhi}→夫妻宫被子女宫冲克，婚姻有结构性矛盾"
    return result


def _check_wan_nian_zai_hun(ri_zhu: str, gender: str, bazi_zhis: list[str]) -> dict:
    """
    时支藏正财/官杀→晚年再婚信号（九龙道长原始理论）
    素材12行277：时支正财可能是老年再婚之象
    """
    result = {"has_signal": False, "detail": ""}
    if len(bazi_zhis) < 4:
        return result

    shi_zhi = bazi_zhis[3]

    for cg, ratio in DI_ZHI_CANG_GAN.get(shi_zhi, []):
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if gender == "男" and ss == "正财":
            result["has_signal"] = True
            level = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
            result["detail"] = f"时支{shi_zhi}藏正财({cg}{level})→晚年再婚信号"
        elif gender == "女" and ss in ("正官", "七杀"):
            result["has_signal"] = True
            level = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
            result["detail"] = f"时支{shi_zhi}藏{ss}({cg}{level})→晚年再婚/偏缘信号"

    return result


def _calculate_marriage_quality(
    ri_zhi: str, ri_zhu: str, gender: str, shen_label: str, shen_score: float,
    pei_ou: dict, xi_yong: list[str], bazi_gans: list[str], bazi_zhis: list[str]
) -> dict:
    """
    婚姻质量评分——基于九龙道长原始100分体系

    夫妻宫(日支)原始100分：
      三刑 → -100（归零离婚）
      六冲邻位 → -70
      六害邻位 → -30
      六破邻位 → -20
      男命日支比肩-10/劫财-20
      女命日支食神-10/伤官-20

    得分<50 → 会离婚
    """
    # ── 基础分 ──
    score = 100.0

    # ── 夫妻宫与其他三柱的刑冲破害检查 ──

    # 三刑检查 — 仅日支参与的三刑才扣分（未参与的不影响婚姻）
    xing_results = check_xing(bazi_zhis)
    has_three_xing = False
    has_two_xing = False
    has_zi_xing = False
    for xing_type, energy in xing_results:
        # 检查日支是否参与该刑
        ri_zhi_in_xing = ri_zhi in xing_type
        if not ri_zhi_in_xing:
            continue
        if "三刑" in xing_type:
            has_three_xing = True
        elif "二刑" in xing_type:
            has_two_xing = True
        elif "自刑" in xing_type:
            has_zi_xing = True

    # 喜用神保护：刑的五行若为喜用，少扣或不扣
    def _xing_wx_in_xi(xing_type: str) -> bool:
        """判断刑中涉及的地支五行是否属于喜用神"""
        from constants import DI_ZHI_WU_XING
        involved_zhis = [z for z in xing_type if z in "子丑寅卯辰巳午未申酉戌亥"]
        for z in involved_zhis:
            if DI_ZHI_WU_XING.get(z, "") in xi_yong:
                return True
        return False

    if has_three_xing:
        score -= 50 if _xing_wx_in_xi("三刑") else 100  # 喜用减半扣
    elif has_two_xing:
        score -= 35 if _xing_wx_in_xi("二刑") else 70
    elif has_zi_xing:
        score -= 15 if _xing_wx_in_xi("自刑") else 30

    # 六冲检查（日支与其它三柱的冲）— 冲为喜用不扣分
    chong_count = 0
    chong_xi_count = 0
    for other_zhi in bazi_zhis:
        if other_zhi != ri_zhi:
            if check_chong(ri_zhi, other_zhi):
                from constants import DI_ZHI_WU_XING
                chong_wx = DI_ZHI_WU_XING.get(other_zhi, "")
                if chong_wx in xi_yong:
                    chong_xi_count += 1
                else:
                    chong_count += 1
    score -= chong_count * 70
    score -= chong_xi_count * 35  # 喜用冲减半扣

    # 六害检查 — 害为喜用不扣分
    hai_count = 0
    hai_xi_count = 0
    for other_zhi in bazi_zhis:
        if other_zhi != ri_zhi:
            if check_hai(ri_zhi, other_zhi):
                from constants import DI_ZHI_WU_XING
                hai_wx = DI_ZHI_WU_XING.get(other_zhi, "")
                if hai_wx in xi_yong:
                    hai_xi_count += 1
                else:
                    hai_count += 1
    score -= hai_count * 30
    score -= hai_xi_count * 15  # 喜用害减半扣

    # 六破检查 — 破为喜用不扣分
    po_count = 0
    po_xi_count = 0
    for other_zhi in bazi_zhis:
        if other_zhi != ri_zhi:
            if LIU_PO.get(ri_zhi) == other_zhi:
                from constants import DI_ZHI_WU_XING
                po_wx = DI_ZHI_WU_XING.get(other_zhi, "")
                if po_wx in xi_yong:
                    po_xi_count += 1
                else:
                    po_count += 1
    score -= po_count * 20
    score -= po_xi_count * 10  # 喜用破减半扣

    # ── 夫妻宫十神扣分（九龙道长原始理论）──
    master_cg = DI_ZHI_CANG_GAN.get(ri_zhi, [])
    master_ss = get_shi_shen_for_cang_gan(master_cg[0][0], ri_zhu) if master_cg else ""

    if gender == "男":
        if master_ss == "比肩":
            score -= 10
        elif master_ss == "劫财":
            score -= 20
    else:
        if master_ss == "食神":
            score -= 10
        elif master_ss == "伤官":
            score -= 20

    # ── 配偶星入本位加分（正财/正官在本位→加分）──
    if master_ss in ("正财", "正官"):
        score += 30  # 配偶星入本位，大幅加分

    # ── 配偶星存在加分（有配偶星→加分）──
    if pei_ou.get("has_primary"):
        score += 15

    # 限制范围
    score = max(0, min(100, score))

    # 映射到等级
    if score >= 80:
        quality = "优秀"
    elif score >= 65:
        quality = "良好"
    elif score >= 50:
        quality = "中等"
    elif score >= 30:
        quality = "偏差"
    else:
        quality = "差"

    return {"score": round(score, 1), "quality": quality, "master_ss": master_ss}


def _calculate_marriage_windows(
    ri_zhi: str,
    ri_zhu: str,
    gender: str,
    bazi_gans: list[str],
    nian_zhi: str,
    shen_label: str,
    xi_yong: list[str],
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_ages: list[float],
) -> list:
    """结婚窗口分析（九龙道长原始理论：四大信号排序 + 桃花年检测）"""
    windows = []

    for dg, dz, sa in zip(da_yun_gans, da_yun_zhis, da_yun_start_ages, strict=False):
        if sa < 20 or sa > 55:
            continue

        score = 0
        reasons = []

        # 信号1: 正财/正官透干（最强信号 ⭐⭐⭐⭐⭐）
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if gender == "男" and dg_ss == "正财":
            score += 5
            reasons.append("⭐⭐⭐⭐⭐正财透干")
        elif gender == "女" and dg_ss == "正官":
            score += 5
            reasons.append("⭐⭐⭐⭐⭐正官透干")

        # 信号2: 流年合夫妻宫（⭐⭐⭐⭐）
        he_map = {"子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
                  "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
                  "巳": "申", "申": "巳", "午": "未", "未": "午"}
        if he_map.get(dz) == ri_zhi:
            score += 4
            reasons.append("⭐⭐⭐⭐流年合夫妻宫")

        # 信号3: 流年冲夫妻宫（⭐⭐⭐）
        chong_map = {"子": "午", "午": "子", "丑": "未", "未": "丑",
                     "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
                     "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}
        if chong_map.get(dz) == ri_zhi:
            score += 3
            reasons.append("⭐⭐⭐流年冲夫妻宫")

        # 信号4: 桃花年（⭐⭐ · 九龙道长原始理论）
        # 以年支查：申子辰→酉 | 亥卯未→子 | 寅午戌→卯 | 巳酉丑→午
        tao_hua_zhi = TAO_HUA.get(nian_zhi, "")
        if tao_hua_zhi and dz == tao_hua_zhi:
            score += 2
            reasons.append("⭐⭐桃花年引动")

        # 辅助: 喜用大运
        dg_wx = TIAN_GAN_WU_XING.get(dg, "")
        if dg_wx in xi_yong:
            score += 1
            reasons.append("⭐喜用大运")

        if score >= 4:
            label = "🏆最佳窗口" if score >= 7 else "✅次佳窗口" if score >= 5 else "⚠️一般窗口"
            windows.append({
                "da_yun": f"{dg}{dz}",
                "age_range": f"{sa}~{sa + 9}岁",
                "score": score,
                "label": label,
                "reasons": reasons,
            })

    windows.sort(key=lambda w: w["score"], reverse=True)
    return windows


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
    婚姻完整分析 v2.1 — 九龙道长原始理论修正版

    返回: 配偶星+夫妻宫+结婚窗口+质量评分(原始100分体系)+专项核验
    """
    # ① 配偶星定位
    pei_ou = _get_pei_ou_xing(ri_zhu, gender, bazi_gans, bazi_zhis)

    # ② 夫妻宫分析
    fufu = _analyze_fufu_gong(ri_zhi, ri_zhu, gender)

    # ③ 结婚窗口
    nian_zhi = bazi_zhis[0] if bazi_zhis else ""
    windows = _calculate_marriage_windows(
        ri_zhi, ri_zhu, gender, bazi_gans, nian_zhi, shen_label, xi_yong,
        da_yun_gans, da_yun_zhis, da_yun_start_ages
    )

    # ④ 婚姻质量评分（原始100分体系）
    quality = _calculate_marriage_quality(
        ri_zhi, ri_zhu, gender, shen_label, shen_score, pei_ou, xi_yong, bazi_gans, bazi_zhis
    )

    # ⑤ 特殊核验
    guan_sha = _check_guan_sha_hun_za(ri_zhu, bazi_gans, bazi_zhis, gender)
    shi_zhi_chong = _check_shi_zhi_chong_ri_zhi(bazi_zhis)
    wan_nian = _check_wan_nian_zai_hun(ri_zhu, gender, bazi_zhis)

    # ⑥ 婆媳关系（财克印）
    po_xi = ""
    if gender == "男":
        # 男命：正财=妻，正印=母，财克印→婆媳矛盾
        cai_count = sum(1 for g in bazi_gans if get_shi_shen_for_gan(g, ri_zhu) == "正财")
        yin_count = sum(1 for g in bazi_gans if get_shi_shen_for_gan(g, ri_zhu) in ("正印", "偏印"))
        if cai_count >= 1 and yin_count >= 1:
            if cai_count > yin_count:
                po_xi = "妻强势>母弱势→婆媳关系紧张（财强印弱）"
            elif yin_count > cai_count:
                po_xi = "母强势>妻弱势→婆婆主导（印强财弱）"
            else:
                po_xi = "婆媳能量相当→需注意平衡"

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

    # signal_detail（取前3窗口的头条理由）
    signal_items = []
    for w in windows[:3]:
        if w.get("reasons"):
            signal_items.append(w["reasons"][0][:15])
    signal_str = "、".join(signal_items)

    # 质量分的展示格式（原始100分体系）
    quality_display = f"{quality['quality']}({int(quality['score'])}/100)"
    # 向后兼容：原始100分→10分映射
    quality_score_legacy = round(quality['score'] / 10, 1)

    return {
        "pei_ou_xing": pei_ou,
        "ri_zhi_analysis": fufu,
        "spouse_traits": traits,
        "spouse_description": "·".join(traits) if traits else "性格温和",
        "marriage_windows": windows[:3],
        "best_window_age": f"{best_window_age}岁",
        "quality": quality["quality"],
        "quality_score": quality_score_legacy,  # 向后兼容
        "quality_score_100": quality["score"],  # 原始100分
        "quality_display": quality_display,      # 展示用
        "pei_ou_detail": f"配偶星{'存在' if pei_ou.get('has_primary') else '缺失'}",
        "fuqi_gong_shi_shen": fufu.get("master_ss", ""),
        "signal_detail": f"窗口{signal_str}" if signal_str else "无显著结婚信号",
        # 专项核验
        "guan_sha_hun_za": guan_sha,
        "shi_zhi_chong_ri_zhi": shi_zhi_chong,
        "wan_nian_zai_hun": wan_nian,
        "po_xi_guan_xi": po_xi,
    }
