"""
财星评分引擎 v1.0 — 金鉴真人·金鉴真人原始规则

核心规则:
  1. 月令本气须是财星才适用"在月看父母/平台"
  2. 余气财星不算引化点（不触发月令财星规则）
  3. 食神生财不分正偏
  4. 财星定正偏以日主为基准判断阴阳
  5. 藏干财星: 本气100% / 中气60% / 余气30%
  
  基础分:
  年支 = 4, 月令 = 40, 日支 = 12, 时干 = 12, 时支 = 12
"""

from __future__ import annotations
from constants import (
    TIAN_GAN, TIAN_GAN_YIN_YANG, TIAN_GAN_WU_XING,
    DI_ZHI_CANG_GAN, CANG_GAN_RATIO, BASE_SCORE,
    SHI_SHEN_MAP, WU_XING_SHENG, WU_XING_KE,
    BaZi, Pillar, CaiXingDetail,
)
from shi_shen import get_shi_shen_for_gan, get_shi_shen_for_cang_gan


def _is_cai_xing(gan_or_cg: str, ri_zhu: str) -> bool:
    """
    判断天干/藏干相对于日主是否为财星
    财星 = 日主所克之五行
    我克者为财（正财阴阳异，偏财同）
    """
    cg_wx = TIAN_GAN_WU_XING[gan_or_cg]
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    # 日主克该五行 = 财星
    return WU_XING_KE[ri_wx] == cg_wx


def compute_cai_xing(bazi: BaZi) -> CaiXingDetail:
    """
    财星评分精确计算
    返回 CaiXingDetail
    """
    ri_zhu = bazi.ri_zhu
    detail = CaiXingDetail()
    
    # 检查月令本气是否为财星
    yue_ben_qi = bazi.month.cang_gan[0][0] if bazi.month.cang_gan else ""
    detail.is_yue_ling_ben_qi_cai = _is_cai_xing(yue_ben_qi, ri_zhu) if yue_ben_qi else False
    
    # ── 年干（基础分=8分，非12分）──
    nian_gan_score = 8.0 if _is_cai_xing(bazi.year.gan, ri_zhu) else 0.0
    
    # ── 月干（基础分=12分）──
    month_gan_score = 12.0 if _is_cai_xing(bazi.month.gan, ri_zhu) else 0.0
    
    # ── 年支 ──
    nian_score = 0.0
    for cg, ratio in bazi.year.cang_gan:
        if _is_cai_xing(cg, ri_zhu):
            r = CANG_GAN_RATIO.get(ratio, 0)
            nian_score += 4.0 * r  # 年支基础分=4
    detail.nian_zhi_score = round(nian_score, 1)
    
    # ── 月令 ──
    yue_score = 0.0
    for cg, ratio in bazi.month.cang_gan:
        if _is_cai_xing(cg, ri_zhu):
            r = CANG_GAN_RATIO.get(ratio, 0)
            yue_score += 40.0 * r  # 月令基础分=40
    detail.yue_ling_score = round(yue_score, 1)
    
    # ── 日支 ──
    ri_score = 0.0
    for cg, ratio in bazi.day.cang_gan:
        if _is_cai_xing(cg, ri_zhu):
            r = CANG_GAN_RATIO.get(ratio, 0)
            ri_score += 12.0 * r  # 日支基础分=12
    detail.ri_zhi_score = round(ri_score, 1)
    
    # ── 时干 ──
    shi_gan_score = 0.0
    shi_gan = bazi.hour.gan
    if _is_cai_xing(shi_gan, ri_zhu):
        shi_gan_score += 12.0  # 时干基础分=12
    detail.shi_gan_score = round(shi_gan_score, 1)
    
    # ── 时支 ──
    shi_zhi_score = 0.0
    for cg, ratio in bazi.hour.cang_gan:
        if _is_cai_xing(cg, ri_zhu):
            r = CANG_GAN_RATIO.get(ratio, 0)
            shi_zhi_score += 12.0 * r  # 时支基础分=12
    detail.shi_zhi_score = round(shi_zhi_score, 1)
    
    # 总分
    yue_ling_cai = detail.yue_ling_score
    detail.total = round(nian_gan_score + month_gan_score + detail.nian_zhi_score +
                         yue_ling_cai + detail.ri_zhi_score +
                         detail.shi_gan_score + detail.shi_zhi_score, 1)
    
    return detail


def cai_xing_explain(detail: CaiXingDetail) -> str:
    """生成财星评分说明"""
    lines = [
        f"年支财星: {detail.nian_zhi_score}分",
        f"月令财星: {detail.yue_ling_score}分",
        f"日支财星: {detail.ri_zhi_score}分",
        f"时干财星: {detail.shi_gan_score}分",
        f"时支财星: {detail.shi_zhi_score}分",
        f"月令本气是否财星: {'是' if detail.is_yue_ling_ben_qi_cai else '否'}",
        f"财星总分: {detail.total}分",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    from constants import BaZi, Pillar
    
    test_cases = [
        ("家主", BaZi(year=Pillar("甲", "午"), month=Pillar("己", "巳"),
                      day=Pillar("戊", "午"), hour=Pillar("壬", "子"), gender="男")),
        ("子源", BaZi(year=Pillar("庚", "申"), month=Pillar("辛", "巳"),
                      day=Pillar("甲", "午"), hour=Pillar("丙", "寅"), gender="男")),
        ("主母", BaZi(year=Pillar("戊", "午"), month=Pillar("甲", "子"),
                      day=Pillar("庚", "戌"), hour=Pillar("丁", "亥"), gender="女")),
    ]
    
    for name, b in test_cases:
        detail = compute_cai_xing(b)
        print(f"【{name}】{b.summary()}")
        print(f"  {cai_xing_explain(detail)}")
        print()
