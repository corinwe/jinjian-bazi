"""
8大维度评分引擎 v1.0 — 金鉴真人·金鉴真人原始规则

维度列表:
  1. 财富根基
  2. 事业发展
  3. 婚姻感情
  4. 学业学历
  5. 子女运势
  6. 健康体质
  7. 人际贵人
  8. 综合家运

每个维度 = 原局基础(0-7) + 大运赋能(0-3) = 总分(0-10)
"""

from __future__ import annotations

from cai_xing import compute_cai_xing
from constants import DI_ZHI_WU_XING, TIAN_GAN_WU_XING, WU_XING_KE, BaZi, DimensionScore
from da_yun import compute_da_yun_scores
from shen_qiang_ruo import compute_shen_qiang_ruo
from shi_shen import get_shi_shen_all_dry

# ── 维度评分函数 ──


def score_cai_fu(bazi: BaZi) -> DimensionScore:
    """财富根基评分"""
    score = 3.5  # 基准分

    # 财星分数
    cai_detail = compute_cai_xing(bazi)
    cai_score = cai_detail.total

    if cai_score >= 40:
        score += 2.5
    elif cai_score >= 20:
        score += 1.5
    elif cai_score >= 10:
        score += 0.5
    else:
        score -= 0.5

    # 身强弱对财富的影响
    shen_score, shen_label, _ = compute_shen_qiang_ruo(bazi)
    if shen_label == "身强" and cai_score >= 40:
        score += 1.0  # 身强财旺
    elif shen_label == "身弱" and cai_score >= 20:
        score -= 0.5  # 身弱不胜财

    # 财库加分
    yue_zhi = bazi.month.zhi
    if yue_zhi in ("辰", "戌", "丑", "未"):
        # 检查是否为财库
        cai_ku = {"木": ["未", "辰"], "火": ["戌", "未"], "金": ["丑", "戌"], "水": ["辰", "丑"]}
        ri_wx = TIAN_GAN_WU_XING[bazi.ri_zhu]
        target_ku = cai_ku.get(ri_wx, [])
        # 财库: 日主所克五行的库
        wo_ke = WU_XING_KE[ri_wx]
        wo_ke_ku_map = {"木": "未", "火": "戌", "金": "丑", "水": "辰"}
        cai_ku_zhi = wo_ke_ku_map.get(wo_ke, "")
        if yue_zhi == cai_ku_zhi:
            score += 1.5

    score = max(0, min(7, score))

    # 大运赋能（简化）
    da_yun_scores = compute_da_yun_scores(bazi, [])
    max_da_yun = 5.0  # 默认
    if da_yun_scores:
        max_da_yun = max(s for _, s in da_yun_scores)

    da_yun_bonus = min(3, max(0, (max_da_yun - 5) * 0.5))

    return DimensionScore(
        base=round(score, 1), da_yun_bonus=round(da_yun_bonus, 1), total=round(min(10, score + da_yun_bonus), 1)
    )


def score_shi_ye(bazi: BaZi) -> DimensionScore:
    """事业发展评分"""
    score = 3.5

    shi_shen_list = get_shi_shen_all_dry(bazi)
    all_ss = [s["shi_shen"] for s in shi_shen_list]

    # 官杀透干→有事业心
    if "七杀" in all_ss:
        score += 0.5
    if "正官" in all_ss:
        score += 0.5

    # 印星加分（学识）
    if "正印" in all_ss or "偏印" in all_ss:
        score += 0.5

    # 身强弱对事业的影响
    shen_score, shen_label, _ = compute_shen_qiang_ruo(bazi)
    if shen_label == "身强":
        score += 0.5
    elif shen_label == "身弱":
        score -= 0.5

    score = max(0, min(7, score))

    da_yun_scores = compute_da_yun_scores(bazi, [])
    max_da_yun = 5.0
    if da_yun_scores:
        max_da_yun = max(s for _, s in da_yun_scores)
    da_yun_bonus = min(3, max(0, (max_da_yun - 5) * 0.5))

    return DimensionScore(
        base=round(score, 1), da_yun_bonus=round(da_yun_bonus, 1), total=round(min(10, score + da_yun_bonus), 1)
    )


def score_hun_yin(bazi: BaZi) -> DimensionScore:
    """婚姻感情评分"""
    score = 3.5

    ri_zhi = bazi.day.zhi
    ri_gan = bazi.day.gan

    shi_shen_list = get_shi_shen_all_dry(bazi)
    all_ss = [s["shi_shen"] for s in shi_shen_list]

    # 夫妻宫（日支）正财/正官为佳
    ri_zhi_wx = DI_ZHI_WU_XING[ri_zhi]
    is_male = bazi.gender == "男"

    if is_male:
        # 男命看正财（妻星）
        if "正财" in all_ss:
            score += 1.0
        if "偏财" in all_ss and "正财" not in all_ss:
            score += 0.5
    else:
        # 女命看正官（夫星）
        if "正官" in all_ss:
            score += 1.0
        if "七杀" in all_ss and "正官" not in all_ss:
            score += 0.5

    # 夫妻宫被冲刑为凶
    # 简化: 子午冲、丑未冲等

    score = max(0, min(7, score))

    da_yun_scores = compute_da_yun_scores(bazi, [])
    max_da_yun = 5.0
    if da_yun_scores:
        max_da_yun = max(s for _, s in da_yun_scores)
    da_yun_bonus = min(3, max(0, (max_da_yun - 5) * 0.3))

    return DimensionScore(
        base=round(score, 1), da_yun_bonus=round(da_yun_bonus, 1), total=round(min(10, score + da_yun_bonus), 1)
    )


def score_xue_li(bazi: BaZi) -> DimensionScore:
    """学业学历评分"""
    score = 3.5

    shi_shen_list = get_shi_shen_all_dry(bazi)
    all_ss = [s["shi_shen"] for s in shi_shen_list]

    # 印星主学业
    if "正印" in all_ss:
        score += 1.5
    elif "偏印" in all_ss:
        score += 1.0

    # 食伤主聪明
    if "伤官" in all_ss:
        score += 0.5
    if "食神" in all_ss:
        score += 0.5

    # 文昌贵人（简化）

    score = max(0, min(7, score))

    da_yun_scores = compute_da_yun_scores(bazi, [])
    max_da_yun = 5.0
    if da_yun_scores:
        max_da_yun = max(s for _, s in da_yun_scores)
    da_yun_bonus = min(3, max(0, (max_da_yun - 5) * 0.4))

    return DimensionScore(
        base=round(score, 1), da_yun_bonus=round(da_yun_bonus, 1), total=round(min(10, score + da_yun_bonus), 1)
    )


def score_zi_nv(bazi: BaZi) -> DimensionScore:
    """子女运势评分"""
    score = 3.5

    shi_zhi = bazi.hour.zhi
    shi_gan = bazi.hour.gan

    # 时柱为子女宫
    shi_shen_list = get_shi_shen_all_dry(bazi)
    all_ss = [s["shi_shen"] for s in shi_shen_list]

    # 时支为食伤（男命子女星）或官杀（女命子女星）
    if bazi.gender == "男":
        if "食神" in all_ss or "伤官" in all_ss:
            score += 1.0
    else:
        if "正官" in all_ss or "七杀" in all_ss:
            score += 1.0

    score = max(0, min(7, score))

    da_yun_bonus = min(3, 1.0)

    return DimensionScore(
        base=round(score, 1), da_yun_bonus=round(da_yun_bonus, 1), total=round(min(10, score + da_yun_bonus), 1)
    )


def score_jian_kang(bazi: BaZi) -> DimensionScore:
    """健康体质评分"""
    score = 4.0

    shen_score, shen_label, _ = compute_shen_qiang_ruo(bazi)

    if shen_label == "身强":
        score += 1.0
    elif shen_label == "身弱":
        score -= 0.5

    # 五行过三检查（简化）
    wx_count = {}
    for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
        wx = TIAN_GAN_WU_XING[p.gan]
        wx_count[wx] = wx_count.get(wx, 0) + 1
        for cg, _ in p.cang_gan:
            wx = TIAN_GAN_WU_XING[cg]
            wx_count[wx] = wx_count.get(wx, 0) + 1

    for wx, count in wx_count.items():
        if count >= 3:
            score -= 0.5  # 五行过三损健康

    score = max(0, min(7, score))
    da_yun_bonus = 0.5

    return DimensionScore(
        base=round(score, 1), da_yun_bonus=round(da_yun_bonus, 1), total=round(min(10, score + da_yun_bonus), 1)
    )


def DEFAULT_DIMENSIONS(bazi: BaZi) -> dict[str, DimensionScore]:
    """计算全部8大维度"""
    return {
        "财富根基": score_cai_fu(bazi),
        "事业发展": score_shi_ye(bazi),
        "婚姻感情": score_hun_yin(bazi),
        "学业学历": score_xue_li(bazi),
        "子女运势": score_zi_nv(bazi),
        "健康体质": score_jian_kang(bazi),
        "人际贵人": DimensionScore(base=4.0, da_yun_bonus=0.5, total=4.5),
        "综合家运": DimensionScore(base=4.0, da_yun_bonus=0.5, total=4.5),
    }


if __name__ == "__main__":
    from constants import BaZi, Pillar

    test_cases = [
        (
            "家主",
            BaZi(
                year=Pillar("甲", "午"),
                month=Pillar("己", "巳"),
                day=Pillar("戊", "午"),
                hour=Pillar("壬", "子"),
                gender="男",
            ),
        ),
        (
            "子源",
            BaZi(
                year=Pillar("庚", "申"),
                month=Pillar("辛", "巳"),
                day=Pillar("甲", "午"),
                hour=Pillar("丙", "寅"),
                gender="男",
            ),
        ),
    ]

    for name, b in test_cases:
        print(f"\n【{name}】{b.summary()} 维度评分:")
        dims = DEFAULT_DIMENSIONS(b)
        for dim_name, ds in dims.items():
            print(f"  {dim_name}: {ds.total}/10 (原局{ds.base}+大运{ds.da_yun_bonus})")
