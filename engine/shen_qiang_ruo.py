"""
身强弱评分引擎 v1.0 — 金鉴真人·金鉴真人原始规则

核心规则（强制·不可违背）:
  1. 月令本气印=40分；月令中/余气印=0分
  2. 所有其他位置印=0分（不论任何位置、任何藏干比例）
  3. 月令比劫全计分
  4. 所有比劫全计分（天干比劫全计分，地支藏干按比例）
  5. 燥土规则: 未/戌 + 天干丙/丁引化 = 当火看（不计印分、不生金）
              未/戌 + 天干壬/癸灭火 = 当土看（生金）
  6. 从弱恒定50分（从弱格的判断标准）
  7. 身强≥50分，身弱<50分（含40~49分区间）
"""

from __future__ import annotations
from constants import (
    TIAN_GAN, TIAN_GAN_YIN_YANG, TIAN_GAN_WU_XING,
    DI_ZHI, DI_ZHI_WU_XING, DI_ZHI_CANG_GAN,
    CANG_GAN_RATIO, BASE_SCORE,
    SHI_SHEN_MAP, WU_XING_SHENG,
    BaZi, Pillar, ScoreDetails,
)
from shi_shen import get_shi_shen_for_gan, get_shi_shen_for_cang_gan


# ── 辅助函数 ──

def _is_yin(gan: str) -> bool:
    """是否为印星（正印/偏印）"""
    wx = TIAN_GAN_WU_XING[gan]
    return wx in ("金", "水")  # 金生水为印, 针对日主五行动态判断

def _is_bi_jie(gan_or_cg: str, ri_zhu: str) -> bool:
    """是否为比劫（比肩/劫财）"""
    # 比劫 = 与日主五行相同
    return TIAN_GAN_WU_XING[gan_or_cg] == TIAN_GAN_WU_XING[ri_zhu]

def _is_yin_for_ri_zhu(cg: str, ri_zhu: str) -> bool:
    """判断藏干相对于日主是否为印星"""
    cg_wx = TIAN_GAN_WU_XING[cg]
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    return WU_XING_SHENG[cg_wx] == ri_wx

def _is_dry_earth(zhi: str) -> bool:
    """是否为燥土（未/戌）"""
    return zhi in ("未", "戌")

def _check_zao_tu_rule(zhi: str, tian_gan_list: list[str], ri_zhu: str) -> str:
    """
    燥土规则检查
    返回: "fire" (当火看), "earth" (当土看), "normal" (不适用)
    
    未/戌 + 天干有丙/丁 → 当火看（不计印分、不生金）
    未/戌 + 天干无丙/丁 → 当土看（生金，计印分）
    壬/癸只有在无丙/丁时才有效（灭火变土）
    规则原文：「未/戌+天干丙/丁引化→当火看，不计印分」
    """
    if not _is_dry_earth(zhi):
        return "normal"
    
    has_fire = any(g in ("丙", "丁") for g in tian_gan_list)
    
    if has_fire:
        return "fire"    # 天干丙/丁引化 → 当火看（不计印分）
    return "earth"       # 无丙/丁引化 → 当土看


def compute_shen_qiang_ruo(bazi: BaZi) -> tuple[float, str, ScoreDetails]:
    """
    计算身强弱评分（金鉴真人原始规则）
    
    返回: (total_score, label, details)
    """
    ri_zhu = bazi.ri_zhu
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    details = ScoreDetails()
    
    # 收集四柱天干列表（用于燥土规则检查）
    all_tian_gan = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    
    # ═══════════════════════════════════════
    # ① 月令印星评分
    # ═══════════════════════════════════════
    yue_zhi = bazi.month.zhi
    yue_cang_gan = bazi.month.cang_gan
    
    # 检查燥土规则
    zao_tu_mode = _check_zao_tu_rule(yue_zhi, all_tian_gan, ri_zhu)
    
    # 月令本气（第一个藏干 = 本气 = 100%）
    ben_qi = yue_cang_gan[0][0] if yue_cang_gan else ""
    ben_qi_ratio = yue_cang_gan[0][1] if yue_cang_gan else 0
    
    # ⚠️ 月令本气印=40分（仅本气）
    if ben_qi and _is_yin_for_ri_zhu(ben_qi, ri_zhu):
        if zao_tu_mode == "fire":
            # 燥土被火引化→当火看→不计印分
            details.yue_ling_yin = 0.0
        elif zao_tu_mode == "earth":
            # 燥土被水灭火→当土看→印星仍然计分
            details.yue_ling_yin = 40.0
        else:
            details.yue_ling_yin = 40.0
    else:
        details.yue_ling_yin = 0.0
    
    # ⚠️ 月令中/余气印=0分（明确规则）
    # 只检查中气(60%)和余气(30%)
    for cg, ratio in yue_cang_gan[1:]:
        if _is_yin_for_ri_zhu(cg, ri_zhu):
            # 中/余气印 = 0分（明确规则）
            pass  # 保持0分
    
    # ═══════════════════════════════════════
    # ② 月令比劫评分（全计分）
    # ═══════════════════════════════════════
    yue_bi_jie_score = 0.0
    for cg, ratio in yue_cang_gan:
        if _is_bi_jie(cg, ri_zhu):
            # 月令比劫全计分
            r = CANG_GAN_RATIO.get(ratio, 0)
            # 月令比劫基础分=40×藏干比例
            yue_bi_jie_score += 40.0 * r
    
    # 燥土规则对月令比劫的影响
    if zao_tu_mode == "fire":
        # 燥土当火看—土类比劫不计
        for cg, ratio in yue_cang_gan:
            if cg in ("戊", "己") and _is_bi_jie(cg, ri_zhu):
                # 燥土当火→土性消失
                yue_bi_jie_score = 0.0
    
    details.yue_ling_bi_jie = round(yue_bi_jie_score, 1)
    
    # ═══════════════════════════════════════
    # ③ 天干印星评分 
    # ═══════════════════════════════════════
    # 所有位置天干印 = 0分（明确规则：月令本气印才是唯一印分来源）
    details.tian_gan_yin = 0.0
    
    # ═══════════════════════════════════════
    # ④ 天干比劫评分（全计分）
    # ═══════════════════════════════════════
    tian_gan_bi_jie = 0.0
    # ⚠️ 日主本身不计入比劫——日主是"我"，不是"比"不是"劫"
    for pillar, pos_score in [(bazi.year, 8.0), (bazi.month, 12.0), (bazi.hour, 12.0)]:
        if _is_bi_jie(pillar.gan, ri_zhu):
            tian_gan_bi_jie += pos_score
    details.tian_gan_bi_jie = round(tian_gan_bi_jie, 1)
    
    # ═══════════════════════════════════════
    # ⑤ 日支印比评分
    # ═══════════════════════════════════════
    # 日支印 = 0分（非月令位置的印全部=0）
    ri_zhi_score = 0.0
    for cg, ratio in bazi.day.cang_gan:
        if _is_bi_jie(cg, ri_zhu):
            # 比劫按比例计分
            r = CANG_GAN_RATIO.get(ratio, 0)
            ri_zhi_score += 12.0 * r
    # 日支印=0（规则强制）
    details.ri_zhi_yin_bi = round(ri_zhi_score, 1)
    
    # ═══════════════════════════════════════
    # ⑥ 年时支印比评分
    # ═══════════════════════════════════════
    nian_shi_score = 0.0
    
    # 年支
    for cg, ratio in bazi.year.cang_gan:
        if _is_bi_jie(cg, ri_zhu):
            r = CANG_GAN_RATIO.get(ratio, 0)
            nian_shi_score += 4.0 * r  # 年支基础分4
    # 年支印=0
    
    # 时支
    for cg, ratio in bazi.hour.cang_gan:
        if _is_bi_jie(cg, ri_zhu):
            r = CANG_GAN_RATIO.get(ratio, 0)
            nian_shi_score += 12.0 * r  # 时支基础分12
    # 时支印=0
    
    details.nian_shi_zhi_yin_bi = round(nian_shi_score, 1)
    
    # ═══════════════════════════════════════
    # 总分计算
    # ═══════════════════════════════════════
    total = (details.yue_ling_yin + details.yue_ling_bi_jie +
             details.tian_gan_yin + details.tian_gan_bi_jie +
             details.ri_zhi_yin_bi + details.nian_shi_zhi_yin_bi)
    total = round(total, 1)
    details.total = total
    
    # 从弱格恒定50分
    # 从弱格判定：原局几乎无助（无印无比劫），但这里我们直接用分数判断
    if total <= 0:
        total = 50.0
        details.total = 50.0
        label = "从弱"
    elif total >= 50:
        label = "身强"
    else:
        label = "身弱"
    
    return total, label, details


def explain_score(details: ScoreDetails) -> str:
    """生成评分说明文本"""
    lines = [
        f"月令本气印: {details.yue_ling_yin}分",
        f"月令比劫: {details.yue_ling_bi_jie}分",
        f"天干印: {details.tian_gan_yin}分",
        f"天干比劫: {details.tian_gan_bi_jie}分",
        f"日支印比: {details.ri_zhi_yin_bi}分",
        f"年时支印比: {details.nian_shi_zhi_yin_bi}分",
        f"总分: {details.total}分",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    from constants import BaZi, Pillar
    
    # 测试1: 家主 甲午 己巳 戊午 壬子
    bazi1 = BaZi(
        year=Pillar("甲", "午"),
        month=Pillar("己", "巳"),
        day=Pillar("戊", "午"),
        hour=Pillar("壬", "子"),
        gender="男"
    )
    score, label, det = compute_shen_qiang_ruo(bazi1)
    print(f"【家主】{bazi1.summary()}")
    print(f"  身强弱: {score}分 → {label}")
    print(f"  {explain_score(det)}")
    print()
    
    # 测试2: 子源 庚申 辛巳 甲午 丙寅
    bazi2 = BaZi(
        year=Pillar("庚", "申"),
        month=Pillar("辛", "巳"),
        day=Pillar("甲", "午"),
        hour=Pillar("丙", "寅"),
        gender="男"
    )
    score, label, det = compute_shen_qiang_ruo(bazi2)
    print(f"【子源】{bazi2.summary()}")
    print(f"  身强弱: {score}分 → {label}")
    print(f"  {explain_score(det)}")
    print()
    
    # 测试3: 主母 戊午 甲子 庚戌 丁亥
    bazi3 = BaZi(
        year=Pillar("戊", "午"),
        month=Pillar("甲", "子"),
        day=Pillar("庚", "戌"),
        hour=Pillar("丁", "亥"),
        gender="女"
    )
    score, label, det = compute_shen_qiang_ruo(bazi3)
    print(f"【主母】{bazi3.summary()}")
    print(f"  身强弱: {score}分 → {label}")
    print(f"  {explain_score(det)}")
    print()
    
    # 测试4: 父亲 己丑 癸酉 癸亥 戊午
    bazi4 = BaZi(
        year=Pillar("己", "丑"),
        month=Pillar("癸", "酉"),
        day=Pillar("癸", "亥"),
        hour=Pillar("戊", "午"),
        gender="男"
    )
    score, label, det = compute_shen_qiang_ruo(bazi4)
    print(f"【父亲】{bazi4.summary()}")
    print(f"  身强弱: {score}分 → {label}")
    print(f"  {explain_score(det)}")
    print()
    
    # 测试5: 凤 戊午 甲子 庚戌 丁亥
    bazi5 = BaZi(
        year=Pillar("戊", "午"),
        month=Pillar("甲", "子"),
        day=Pillar("庚", "戌"),
        hour=Pillar("丁", "亥"),
        gender="女"
    )
    score, label, det = compute_shen_qiang_ruo(bazi5)
    print(f"【凤】{bazi5.summary()}")
    print(f"  身强弱: {score}分 → {label}")
    print(f"  {explain_score(det)}")
