"""
金鉴真人·8大维度评分引擎 v2.1 — 确定性规则版
基于bazi-calibration体系

每个维度 = 原局基础(0-7) + 大运赋能(0-3) = 总分(0-10)

v2.1 修复大运赋能: 新增da_yun_list参数, 由调用方传入真实大运数据
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from constants import (
    BaZi, DimensionScore, TIAN_GAN_WU_XING, DI_ZHI_WU_XING,
    DI_ZHI_CANG_GAN, WU_XING_SHENG, WU_XING_KE, DaYun,
)
from shen_qiang_ruo import compute_shen_qiang_ruo
from cai_xing import compute_cai_xing
from shi_shen import get_shi_shen_for_gan, get_shi_shen_all_dry
from ge_ju import determine_xi_yong_shen, determine_ge_ju
from da_yun import compute_da_yun, compute_da_yun_scores


def _get_da_yun_bonus(bazi: BaZi, da_yun_list: list[DaYun]) -> float:
    """
    计算大运赋能加成 (0-3分)
    基于真实大运数据: 取最佳大运评分与基准分5的差距
    """
    if not da_yun_list:
        return 0.0
    dy_scores = compute_da_yun_scores(bazi, da_yun_list)
    if not dy_scores:
        return 0.0
    max_dy = max(s for _, s in dy_scores)
    bonus = min(3.0, max(0.0, (max_dy - 5.0) * 0.5))
    return round(bonus, 1)


def score_cai_fu(bazi: BaZi, xi_yong: list[str], da_yun_list: list[DaYun]) -> DimensionScore:
    """财富根基评分 — 校准版"""
    base = 3.5

    # 财星分数
    cai = compute_cai_xing(bazi)
    cai_score = cai.total

    if cai_score >= 50:
        base += 2.5
    elif cai_score >= 30:
        base += 1.5
    elif cai_score >= 15:
        base += 0.5
    elif cai_score >= 8:
        base += 0
    else:
        base -= 0.5

    # 身强弱
    shen_score, shen_label, _ = compute_shen_qiang_ruo(bazi)
    if shen_label == "身强" and cai_score >= 30:
        base += 1.0
    elif shen_label == "身弱" and cai_score >= 20:
        base -= 0.5

    # 财库加分
    yue_zhi = bazi.month.zhi
    if yue_zhi in ("辰", "戌", "丑", "未"):
        ri_wx = TIAN_GAN_WU_XING[bazi.ri_zhu]
        wo_ke = WU_XING_KE.get(ri_wx, "")
        wo_ke_ku_map = {"木": "未", "火": "戌", "金": "丑", "水": "辰"}
        cai_ku_zhi = wo_ke_ku_map.get(wo_ke, "")
        if yue_zhi == cai_ku_zhi:
            base += 1.5

    base = max(0, min(7, base))
    bonus = _get_da_yun_bonus(bazi, da_yun_list)

    return DimensionScore(base=round(base, 1), da_yun_bonus=bonus,
                          total=round(min(10, base + bonus), 1))


def score_shi_ye(bazi: BaZi, xi_yong: list[str], ge_ju_main: str,
                 da_yun_list: list[DaYun]) -> DimensionScore:
    """事业发展评分 — 校准版"""
    base = 3.5
    all_ss = [s["shi_shen"] for s in get_shi_shen_all_dry(bazi)]

    # 官杀→事业心
    if "七杀" in all_ss:
        base += 0.5
    if "正官" in all_ss:
        base += 0.5
    # 印星→学识助力
    if "正印" in all_ss or "偏印" in all_ss:
        base += 0.5
    # 格局加成
    if ge_ju_main in ("正官格", "七杀格"):
        base += 0.5

    shen_score, shen_label, _ = compute_shen_qiang_ruo(bazi)
    if shen_label == "身强":
        base += 0.5
    elif shen_label == "身弱":
        base -= 0.5

    base = max(0, min(7, base))
    bonus = _get_da_yun_bonus(bazi, da_yun_list)

    return DimensionScore(base=round(base, 1), da_yun_bonus=bonus,
                          total=round(min(10, base + bonus), 1))


def score_hun_yin(bazi: BaZi, xi_yong: list[str], da_yun_list: list[DaYun]) -> DimensionScore:
    """婚姻感情评分 — 校准版"""
    base = 3.5
    all_ss = [s["shi_shen"] for s in get_shi_shen_all_dry(bazi)]

    if bazi.gender == "男":
        if "正财" in all_ss:
            base += 1.0
        elif "偏财" in all_ss:
            base += 0.5
    else:
        if "正官" in all_ss:
            base += 1.0
        elif "七杀" in all_ss:
            base += 0.5

    base = max(0, min(7, base))
    bonus = _get_da_yun_bonus(bazi, da_yun_list) * 0.6  # 婚姻受大运影响约60%

    return DimensionScore(base=round(base, 1), da_yun_bonus=round(bonus, 1),
                          total=round(min(10, base + bonus), 1))


def score_xue_li(bazi: BaZi, xi_yong: list[str], da_yun_list: list[DaYun]) -> DimensionScore:
    """学业学历评分 — 校准版"""
    base = 3.5
    all_ss = [s["shi_shen"] for s in get_shi_shen_all_dry(bazi)]

    if "正印" in all_ss:
        base += 1.5
    elif "偏印" in all_ss:
        base += 1.0
    if "伤官" in all_ss:
        base += 0.5
    elif "食神" in all_ss:
        base += 0.5

    base = max(0, min(7, base))
    bonus = _get_da_yun_bonus(bazi, da_yun_list) * 0.4  # 学历受大运影响约40%

    return DimensionScore(base=round(base, 1), da_yun_bonus=round(bonus, 1),
                          total=round(min(10, base + bonus), 1))


def score_zi_nv(bazi: BaZi, da_yun_list: list[DaYun]) -> DimensionScore:
    """子女运势评分 — 校准版"""
    base = 3.5
    all_ss = [s["shi_shen"] for s in get_shi_shen_all_dry(bazi)]

    if bazi.gender == "男":
        if "食神" in all_ss or "伤官" in all_ss:
            base += 1.0
    else:
        if "正官" in all_ss or "七杀" in all_ss:
            base += 1.0

    base = max(0, min(7, base))
    bonus = _get_da_yun_bonus(bazi, da_yun_list) * 0.5  # 子女约50%

    return DimensionScore(base=round(base, 1), da_yun_bonus=round(bonus, 1),
                          total=round(min(10, base + bonus), 1))


def score_jian_kang(bazi: BaZi, da_yun_list: list[DaYun]) -> DimensionScore:
    """健康体质评分 — 校准版"""
    base = 4.0
    shen_score, shen_label, _ = compute_shen_qiang_ruo(bazi)

    if shen_label == "身强":
        base += 1.0
    elif shen_label == "身弱":
        base -= 0.5

    # 五行过三
    wx_count = {}
    for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
        wx = TIAN_GAN_WU_XING[p.gan]
        wx_count[wx] = wx_count.get(wx, 0) + 1
        for cg, _ in p.cang_gan:
            wx = TIAN_GAN_WU_XING[cg]
            wx_count[wx] = wx_count.get(wx, 0) + 1

    for wx, count in wx_count.items():
        if count >= 3:
            base -= 0.5

    base = max(0, min(7, base))
    bonus = _get_da_yun_bonus(bazi, da_yun_list) * 0.3  # 健康约30%

    return DimensionScore(base=round(base, 1), da_yun_bonus=round(bonus, 1),
                          total=round(min(10, base + bonus), 1))


def DEFAULT_DIMENSIONS(bazi: BaZi, da_yun_list: list[DaYun] = None) -> dict[str, DimensionScore]:
    """
    8大维度完整评分

    参数:
      bazi: 八字数据
      da_yun_list: 大运列表（用于计算赋能加成）。
                   为None或空列表时, 大运赋能=0。
    """
    if da_yun_list is None:
        da_yun_list = []

    xi_yong, _ = determine_xi_yong_shen(bazi)
    ge_ju_main, _ = determine_ge_ju(bazi)

    return {
        "财富根基": score_cai_fu(bazi, xi_yong, da_yun_list),
        "事业发展": score_shi_ye(bazi, xi_yong, ge_ju_main, da_yun_list),
        "婚姻感情": score_hun_yin(bazi, xi_yong, da_yun_list),
        "学业学历": score_xue_li(bazi, xi_yong, da_yun_list),
        "子女运势": score_zi_nv(bazi, da_yun_list),
        "健康体质": score_jian_kang(bazi, da_yun_list),
        "人际贵人": DimensionScore(base=4.0,
                                   da_yun_bonus=round(_get_da_yun_bonus(bazi, da_yun_list) * 0.3, 1),
                                   total=round(min(10, 4.0 + _get_da_yun_bonus(bazi, da_yun_list) * 0.3), 1)),
        "综合家运": DimensionScore(base=4.0,
                                   da_yun_bonus=round(_get_da_yun_bonus(bazi, da_yun_list) * 0.4, 1),
                                   total=round(min(10, 4.0 + _get_da_yun_bonus(bazi, da_yun_list) * 0.4), 1)),
    }
