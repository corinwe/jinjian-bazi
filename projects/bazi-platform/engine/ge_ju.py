"""
格局判定+喜用神引擎 v2.0 — 金鉴真人原始规则（2026-07-05审计修复）

格局判定规则（bazi-foundation-analysis v2.17）：
  月令本气→中气→余气依次看何者透干：
    透干→该十神成格（正八格之一）
    比肩劫财即使透干也不入格局
  本中余气均未透干 → 杂气格

喜用神规则：
  身强：先克(官杀)→再泄(食伤)→后耗(财才)
  身弱：先扶(印)→后帮(比)
"""

from __future__ import annotations

from constants import TIAN_GAN_WU_XING, BaZi, Pillar
from shen_qiang_ruo import compute_shen_qiang_ruo
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan, is_tou_gan

# ── 月令定格局（只含正八格，比肩劫财不入格局）──
GE_JU_BY_YUE_LING = {
    "正印": "正印格",
    "偏印": "偏印格",
    "正官": "正官格",
    "七杀": "七杀格",
    "正财": "正财格",
    "偏财": "偏财格",
    "食神": "食神格",
    "伤官": "伤官格",
}


def _get_tou_gan_shi_shen(bazi: BaZi, ri_zhu: str) -> set[str]:
    """获取所有透干的十神（天干上的十神集合）"""
    return {get_shi_shen_for_gan(p.gan, ri_zhu) for p in [bazi.year, bazi.month, bazi.day, bazi.hour]}


def determine_ge_ju(bazi: BaZi) -> tuple[str, str]:
    """
    判定格局（v3.0 · 从弱/从旺优先级修正）

    规则：
      1. 特殊格局（从弱/从旺）优先级高于月令本气定的正八格
      2. 月令本气→中气→余气依次看何者透干
      3. 透干→该十神成格
      4. 比肩劫财不入格局
      5. 本中余气均未透干→杂气格

    返回: (主格局, 详细描述)
    """
    ri_zhu = bazi.ri_zhu
    yue_zhi = bazi.month.zhi
    yue_cangs = bazi.month.cang_gan

    # ⚠️ 特殊格局优先判断：从弱/从旺优先级高于月令本气定的正八格
    sqr_score, sqr_label, _ = compute_shen_qiang_ruo(bazi)
    if sqr_label == "从弱":
        # 从弱格细分：取克泄耗五行中能量最强的
        from energy import compute_energy_profile
        ep = compute_energy_profile(bazi)
        wx_energy = ep.get("wu_xing_energy", {})
        # 从弱喜克泄耗：官杀(土)>财(火)>食伤(木)
        energy_map = {"土": wx_energy.get("土", 0),
                      "火": wx_energy.get("火", 0),
                      "木": wx_energy.get("木", 0)}
        strongest = max(energy_map, key=lambda k: energy_map[k])
        sub_type = {"土": "从杀格", "火": "从财格", "木": "从儿格"}.get(strongest, "从杀格")
        return "从弱格", f"从弱格({sub_type})"
    if sqr_label == "从旺":
        return "从旺格", "从旺格(专旺)"

    tou_gan_ss = _get_tou_gan_shi_shen(bazi, ri_zhu)

    # 月令本气→中气→余气依次看何者透干
    main_ge_ju = "杂气格"  # 默认
    ge_ju_source = ""
    yong_shen_gan = None  # 取用之神的天干（用于用神变化检测）

    for cg, ratio in yue_cangs:
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if ss in GE_JU_BY_YUE_LING and ss in tou_gan_ss:
            main_ge_ju = GE_JU_BY_YUE_LING[ss]
            level = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
            ge_ju_source = f"月令{yue_zhi}{level}{cg}={ss}透干"
            # 找到透干用神的天干（在四柱天干中找该十神）
            for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
                if get_shi_shen_for_gan(p.gan, ri_zhu) == ss:
                    yong_shen_gan = p.gan
                    break
            break

    # ──《子平真诠》规则补充（2026-08-02 荀太虚讲解交叉验证沉淀）──
    # 规则① 会支取用：月令藏干不透，但月支与他支三合/三会成局 → 取会局十神为用神
    if main_ge_ju == "杂气格":
        hui_ge = _get_hui_zhi_ge_ju(bazi)
        if hui_ge:
            main_ge_ju, ge_ju_source = hui_ge

    # 规则② 本气兜底：不透不会，取月支本气为用神（比肩劫财不入格局→维持杂气格）
    if main_ge_ju == "杂气格" and yue_cangs:
        ben_qi_ss = get_shi_shen_for_cang_gan(yue_cangs[0][0], ri_zhu)
        if ben_qi_ss in GE_JU_BY_YUE_LING:
            main_ge_ju = GE_JU_BY_YUE_LING[ben_qi_ss]
            ge_ju_source = f"月令{yue_zhi}本气{yue_cangs[0][0]}={ben_qi_ss}(本气兜底)"

    # 规则③ 用神变化：取用天干被天干五合 → 标记格局变化（《论用神变化》）
    yong_shen_change = ""
    if yong_shen_gan:
        change = _check_yong_shen_he(bazi, yong_shen_gan, main_ge_ju)
        if change:
            yong_shen_change = change

    # 顺逆用标记（《论用神》善顺用/不善逆用）
    shun_ni = ""
    if main_ge_ju in ("正官格", "正印格", "偏印格", "正财格", "偏财格", "食神格"):
        shun_ni = "顺用"
    elif main_ge_ju in ("七杀格", "伤官格"):
        shun_ni = "逆用"

    # 若本中余气都未透干，则为杂气格（已默认）

    # 复合格局检测（基于透干十神 + 身强弱校验）
    all_shi_shen = list(tou_gan_ss)
    extra_info = []

    # 身强弱已在上方获取，直接使用
    is_shen_qiang = sqr_label in ("身强", "中和偏强")
    is_shen_ruo = sqr_label in ("身弱", "")
    is_zhong_he = sqr_label == "中和"

    # 官杀混杂
    has_guan = "正官" in all_shi_shen
    has_sha = "七杀" in all_shi_shen
    if has_guan and has_sha:
        extra_info.append("官杀混杂")

    # 伤官生财（需身强·成格条件§6.4.4）
    has_shang_guan = "伤官" in all_shi_shen
    has_zheng_cai = "正财" in all_shi_shen
    has_pian_cai = "偏财" in all_shi_shen
    if has_shang_guan and (has_zheng_cai or has_pian_cai):
        if is_shen_qiang:
            extra_info.append("伤官生财(成格)")
        else:
            extra_info.append("伤官生财(不成格-需身强)")

    # 伤官配印（需身弱·成格条件§6.4.3）
    if has_shang_guan and ("正印" in all_shi_shen or "偏印" in all_shi_shen):
        if is_shen_ruo:
            extra_info.append("伤官配印(成格)")
        else:
            extra_info.append("伤官配印(不成格-需身弱)")

    # 杀印相生（需身弱·成格条件§6.4.1·8条件中第1条）
    if has_sha and ("正印" in all_shi_shen or "偏印" in all_shi_shen):
        if is_shen_ruo:
            extra_info.append("杀印相生(成格)")
        else:
            extra_info.append("杀印相生(不成格-需身弱)")

    # 食神生财（需身强）
    has_shi_shen = "食神" in all_shi_shen
    if has_shi_shen and (has_zheng_cai or has_pian_cai):
        if is_shen_qiang:
            extra_info.append("食神生财(成格)")
        else:
            extra_info.append("食神生财(不成格-需身强)")

    # 食神制杀（需身强·成格条件§6.4.2）
    if has_shi_shen and has_sha:
        if is_shen_qiang:
            extra_info.append("食神制杀(成格)")
        else:
            extra_info.append("食神制杀(不成格-需身强)")

    detail_parts = [main_ge_ju]
    if ge_ju_source:
        detail_parts.append(ge_ju_source)
    if shun_ni:
        detail_parts.append(shun_ni)
    if yong_shen_change:
        detail_parts.append(yong_shen_change)
    if extra_info:
        detail_parts.extend(extra_info)

    detail = "+".join(detail_parts)

    return main_ge_ju, detail


# ──《子平真诠》规则辅助函数（2026-08-02 沉淀）──

def _get_shi_shen_by_wuxing(wx: str, ri_zhu: str) -> str:
    """合局五行 → 十神（正神取向·会支取用兜底）"""
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    sheng_mu = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke_mu = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    if wx == ri_wx:
        return "比肩"  # 比劫不入格局
    if sheng_mu[ri_wx] == wx:
        return "食神"  # 我生=食伤（取正神）
    if sheng_mu[wx] == ri_wx:
        return "正印"  # 生我=印
    if ke_mu[wx] == ri_wx:
        return "正官"  # 克我=官
    if ke_mu[ri_wx] == wx:
        return "正财"  # 我克=财
    return "比肩"


def _get_hui_zhi_ge_ju(bazi: BaZi) -> tuple[str, str] | None:
    """会支取用（《子平真诠·论用神》）：月令藏干不透，但月支与他支三合/三会成局 → 取会局十神为用神

    优先级：三合（完整15倍/虚邀7倍）> 三会（20倍）> 半合（5倍）
    返回: (格局名, 来源描述) 或 None
    """
    try:
        from xing_chong_he_hua import check_san_he, check_san_hui, check_ban_he
    except ImportError:
        return None

    zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]
    yue_zhi = bazi.month.zhi
    ri_zhu = bazi.ri_zhu

    # 1. 完整三合（含虚邀）：能量15/7
    try:
        sanhe_results = check_san_he(zhis)
        for item in sanhe_results:
            he_type, wx, energy = item  # ("申子辰三合水局", "水", 15.0)
            if yue_zhi in he_type and energy >= 7:
                ss = _get_shi_shen_by_wuxing(wx, ri_zhu)
                if ss in GE_JU_BY_YUE_LING:
                    return GE_JU_BY_YUE_LING[ss], f"月令{yue_zhi}会支{he_type}→{ss}格"
    except Exception:
        pass

    # 2. 三会局
    try:
        sanhui_results = check_san_hui(zhis)
        for item in sanhui_results:
            he_type = item.get("type", "")
            wx = item.get("wx", "")
            if yue_zhi in he_type:
                ss = _get_shi_shen_by_wuxing(wx, ri_zhu)
                if ss in GE_JU_BY_YUE_LING:
                    return GE_JU_BY_YUE_LING[ss], f"月令{yue_zhi}会支{he_type}→{ss}格"
    except Exception:
        pass

    # 注：半合（能量5）不作取格依据——月令本气兜底优先（避免酉月伤官被半合误判）

    return None


def _check_yong_shen_he(bazi: BaZi, yong_shen_gan: str, ge_ju: str) -> str:
    """用神变化（《子平真诠·论用神变化》）：取用天干被邻干天干五合 → 用神被合去/合绊

    返回: 变化描述 或 ""
    """
    try:
        from xing_chong_he_hua import check_tian_gan_he
    except ImportError:
        return ""

    gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    pos_names = ["年", "月", "日", "时"]
    for i, g in enumerate(gans):
        if g != yong_shen_gan:
            try:
                ok, he_wx = check_tian_gan_he(g, yong_shen_gan)
                if ok:
                    return f"用神{yong_shen_gan}被{pos_names[i]}干{g}合绊({g}{yong_shen_gan}合)"
            except Exception:
                continue
    return ""


def determine_xi_yong_shen(bazi: BaZi) -> tuple[list[str], list[str]]:
    """
    判定喜用神和忌神（v2.0 · 九龙道长原始规则顺序修正）

    身强：先克(官杀)→再泄(食伤)→后耗(财才) （skill line 1601）
    身弱：先扶(印)→后帮(比)
    """
    score, label, _ = compute_shen_qiang_ruo(bazi)
    ri_wx = TIAN_GAN_WU_XING[bazi.ri_zhu]

    # 五行相生克
    sheng_mu = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke_mu = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    # 生我的五行（印）
    sheng_wo = {v: k for k, v in sheng_mu.items()}[ri_wx]
    # 我生的五行（食伤）
    wo_sheng = sheng_mu[ri_wx]
    # 克我的五行（官杀）
    ke_wo = ke_mu[ri_wx]
    # 我克的五行（财）
    wo_ke = ke_mu[ke_mu[ri_wx]]  # 金克木->木克土->土是财
    # 正确逻辑：金克木=财，所以 my_ke = {v: k for k, v in ke_mu.items()}[ri_wx]
    # 即 ke_mu的逆映射

    # 纠正：我克=日主五行所克
    my_ke = {v: k for k, v in ke_mu.items()}[ri_wx]  # 财

    if label == "身弱":
        # 喜印比（生我+同我）
        xi_yong = [sheng_wo, ri_wx]  # 先印后比
        ji_shen = [my_ke, ke_wo, wo_sheng]  # 财>官>食伤
    elif label == "身强":
        # 喜克泄耗：先官杀→再食伤→后财才（skill line 1601）
        xi_yong = [ke_wo, wo_sheng, my_ke]
        ji_shen = [sheng_wo, ri_wx]
    elif label == "中和":
        # 中和分三段处理（2026-07-07审计修复）
        # 规则来源：bazi-fortune-analysis §4.2 + 老板2026-06-20校准（子源案）
        if score >= 55:
            # 55-60分 → 中和偏强 → 喜克泄耗（同身强）
            xi_yong = [ke_wo, wo_sheng, my_ke]
            ji_shen = [sheng_wo, ri_wx]
        elif score >= 45:
            # 45-55分 → 真正中和 → 无固定喜忌，随大运灵活变化
            # 暂设喜克泄耗（安全默认）
            xi_yong = [ke_wo, wo_sheng, my_ke]
            ji_shen = [sheng_wo, ri_wx]
        else:
            # 40-44分 → 中和偏弱 → 适度用印比
            xi_yong = [sheng_wo, ri_wx]
            ji_shen = [my_ke, ke_wo, wo_sheng]
    elif label == "从弱":
        # 从弱喜克泄耗
        xi_yong = [ke_wo, wo_sheng, my_ke]
        ji_shen = [sheng_wo, ri_wx]
    else:  # 从旺
        xi_yong = [sheng_wo, ri_wx]
        ji_shen = [ke_wo, wo_sheng, my_ke]

    return xi_yong, ji_shen


# ── 调候用神表（按出生月份）──
TIAO_HOU_YONG_SHEN = {
    "甲": {1: "丙", 2: "丙", 3: "庚", 4: "庚", 5: "壬", 6: "壬", 7: "壬", 8: "癸", 9: "庚", 10: "庚", 11: "丙", 12: "丙"},
    "乙": {1: "丙", 2: "丙", 3: "丙", 4: "癸", 5: "壬", 6: "壬", 7: "癸", 8: "癸", 9: "癸", 10: "癸", 11: "丙", 12: "丙"},
    "丙": {1: "壬", 2: "壬", 3: "壬", 4: "壬", 5: "壬", 6: "壬", 7: "壬", 8: "壬", 9: "甲", 10: "甲", 11: "壬", 12: "壬"},
    "丁": {1: "甲", 2: "甲", 3: "甲", 4: "甲", 5: "壬", 6: "壬", 7: "甲", 8: "甲", 9: "甲", 10: "甲", 11: "甲", 12: "甲"},
    "戊": {1: "丙", 2: "丙", 3: "丙", 4: "丙", 5: "壬", 6: "壬", 7: "庚", 8: "庚", 9: "丙", 10: "甲", 11: "丙", 12: "丙"},
    "己": {1: "丙", 2: "丙", 3: "甲", 4: "癸", 5: "壬", 6: "壬", 7: "癸", 8: "癸", 9: "癸", 10: "丙", 11: "丙", 12: "丙"},
    "庚": {1: "丁", 2: "甲", 3: "甲", 4: "壬", 5: "癸", 6: "壬", 7: "壬", 8: "癸", 9: "甲", 10: "甲", 11: "丁", 12: "丙"},
    "辛": {1: "丙", 2: "丙", 3: "甲", 4: "壬", 5: "壬", 6: "壬", 7: "壬", 8: "壬", 9: "壬", 10: "壬", 11: "丙", 12: "丙"},
    "壬": {1: "戊", 2: "戊", 3: "甲", 4: "壬", 5: "庚", 6: "庚", 7: "戊", 8: "甲", 9: "甲", 10: "甲", 11: "戊", 12: "戊"},
    "癸": {1: "丙", 2: "丙", 3: "丙", 4: "庚", 5: "庚", 6: "庚", 7: "壬", 8: "壬", 9: "甲", 10: "壬", 11: "丙", 12: "丙"},
}


def get_tiao_hou_yong_shen(ri_zhu: str, birth_month: int) -> list[str]:
    """获取调候用神（按出生月份）"""
    yong_shen_gan = TIAO_HOU_YONG_SHEN.get(ri_zhu, {}).get(birth_month, "")
    if not yong_shen_gan:
        return []
    wx = TIAN_GAN_WU_XING.get(yong_shen_gan, "")
    return [wx] if wx else []
