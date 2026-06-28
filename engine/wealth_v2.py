"""
金鉴真人·财富分析引擎 v1.0 — 五层动态体系
基于bazi-wealth-analysis v3.4

五层动态：
  第1层：原局定调 — 六种八字状态
  第2层：辛苦度 — 身强弱+围克程度
  第3层：围克折扣 — 财星受克兑现率
  第4层：财库 — 日/时支有库/无库
  第5层：大运窗口 — 财富爆发时间窗口
"""

from __future__ import annotations

from constants import DI_ZHI_CANG_GAN, DI_ZHI_WU_XING, TIAN_GAN_WU_XING, WU_XING_KE
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan

# ── 五级定量 ──
WEALTH_LEVELS = [
    {"level": "👑 巨富", "range": "几十亿~上百亿", "score_range": (50, 100)},
    {"level": "💰 大富", "range": "几个亿", "score_range": (40, 50)},
    {"level": "🥈 中富", "range": "几千万", "score_range": (30, 40)},
    {"level": "🏠 小富/小康", "range": "上千万", "score_range": (15, 30)},
    {"level": "🥉 贫穷", "range": "千万以内", "score_range": (0, 15)},
]

# ── 六种状态断语 ──
STATUS_TEMPLATES = {
    "身强财旺": "本命局已满足发财条件，天生不缺钱",
    "身强财弱": "底子好但财星弱，等食伤/财星大运年份发中财",
    "身弱财旺": "有机会但抓不住，等印比帮身才能变现",
    "身弱财弱": "辛苦钱，遇印比发中财",
    "无财身弱": "和尚命，对钱看淡，难发财",
    "从弱格": "特殊格局，财为喜用，大运对方向就爆发",
}

# ── 五种墓库表 ──
WU_KU = {
    "木": {"比劫库": "未", "财库": "戌", "官杀库": "丑", "印库": "辰", "食伤库": "戌"},
    "火": {"比劫库": "戌", "财库": "丑", "官杀库": "辰", "印库": "未", "食伤库": "戌"},
    "土": {"比劫库": "戌", "财库": "辰", "官杀库": "未", "印库": "戌", "食伤库": "丑"},
    "金": {"比劫库": "丑", "财库": "未", "官杀库": "戌", "印库": "丑", "食伤库": "辰"},
    "水": {"比劫库": "辰", "财库": "戌", "官杀库": "未", "印库": "丑", "食伤库": "未"},
}


def _get_base_status(shen_label: str, shen_score: float, cai_total: float) -> str:
    """第1层：定基础状态"""
    if shen_label == "从弱":
        return "从弱格"
    if cai_total <= 0 and shen_label == "身弱":
        return "无财身弱"
    if shen_label == "身强" or shen_score >= 55:
        return "身强财旺" if cai_total >= 40 else "身强财弱"
    else:
        return "身弱财旺" if cai_total >= 40 else "身弱财弱"


def _eval_wei_ke(all_zhis: list[str], ri_zhu: str, bazi_gans: list[str]) -> float:
    """第3层：围克折扣 — 财星受克折扣率"""
    # 找所有财星位置
    cai_positions = []
    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ("正财", "偏财"):
            cai_positions.append(("天干", i))

    for i, z in enumerate(all_zhis):
        for cg, ratio in DI_ZHI_CANG_GAN.get(z, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss in ("正财", "偏财"):
                cai_positions.append((f"地支{i}", z, cg, ratio))

    if not cai_positions:
        return 1.0  # 无财星

    # 简化：统计财星五行的被克情况
    cai_wx = WU_XING_KE.get(TIAN_GAN_WU_XING[ri_zhu], "")
    if not cai_wx:
        return 1.0

    # 统计克财星五行的字
    ke_count = 0
    all_wx = [TIAN_GAN_WU_XING[g] for g in bazi_gans]
    for z in all_zhis:
        all_wx.append(DI_ZHI_WU_XING[z])
        for cg, _ in DI_ZHI_CANG_GAN.get(z, []):
            all_wx.append(TIAN_GAN_WU_XING[cg])

    for wx in all_wx:
        if WU_XING_KE.get(wx) == cai_wx:  # 这个五行克财星五行
            ke_count += 1

    if ke_count >= 4:
        return 0.3  # 30%兑现
    elif ke_count >= 2:
        return 0.6  # 60%兑现
    return 1.0  # 全额兑现


def _eval_cai_ku(ri_zhu: str, day_zhi: str, hour_zhi: str) -> dict:
    """第4层：财库分析"""
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    ku_info = WU_KU.get(ri_wx, {})
    cai_ku_zhi = ku_info.get("财库", "")
    bi_ku_zhi = ku_info.get("比劫库", "")

    result = {"has_cai_ku": False, "has_bi_ku": False, "position": ""}
    for z in [day_zhi, hour_zhi]:
        if z == cai_ku_zhi:
            result["has_cai_ku"] = True
            pos = "日支" if z == day_zhi else "时支"
            result["position"] = pos
        if z == bi_ku_zhi:
            result["has_bi_ku"] = True

    return result


def analyze_wealth_full(
    ri_zhu: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    shen_label: str,
    shen_score: float,
    cai_total: float,
    xi_yong: list[str],
    da_yun_list: list[dict],
) -> dict:
    """
    财富完整分析 — 五层动态体系
    """
    # 第1层：基础状态
    status = _get_base_status(shen_label, shen_score, cai_total)
    template = STATUS_TEMPLATES.get(status, "")

    # 第2-3层：围克折扣
    discount = _eval_wei_ke(bazi_zhis, ri_zhu, bazi_gans)

    # 第4层：财库
    ku = _eval_cai_ku(ri_zhu, bazi_zhis[2], bazi_zhis[3])

    # 第5层：大运窗口
    wealth_windows = []
    for dy in da_yun_list:
        dy_gan = dy.get("gan", "") if hasattr(dy, "gan") else ""
        dy_zhi = dy.get("zhi", "") if hasattr(dy, "zhi") else ""
        dy_ss = get_shi_shen_for_gan(dy_gan, ri_zhu) if dy_gan else ""

        score = dy.get("score", 5) if isinstance(dy, dict) else 5
        is_wealth = dy_ss in ("正财", "偏财", "食神", "伤官")

        if is_wealth and score >= 5:
            wealth_windows.append(
                {"da_yun": dy.get("gan_zhi", str(dy)), "window": "补财/食伤大运，利于财富积累", "score": score}
            )
        if shen_label == "身弱" and dy_ss in ("正印", "偏印", "比肩", "劫财") and score >= 5:
            wealth_windows.append(
                {"da_yun": dy.get("gan_zhi", str(dy)), "window": "印比帮身大运，身弱能担财", "score": score}
            )

    # 综合评级
    effective_score = cai_total * discount
    if status == "从弱格":
        level = "💰 大富~巨富（特殊格局）"
        level_idx = 1
    elif effective_score >= 50:
        level = "👑 巨富"
        level_idx = 0
    elif effective_score >= 40:
        level = "💰 大富"
        level_idx = 1
    elif effective_score >= 30:
        level = "🥈 中富"
        level_idx = 2
    elif effective_score >= 15:
        level = "🏠 小富/小康"
        level_idx = 3
    else:
        level = "🥉 贫穷"
        level_idx = 4

    # 食伤=财根检查
    all_ss = [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]
    has_shi_shang = "食神" in all_ss or "伤官" in all_ss

    return {
        "status": status,
        "status_template": template,
        "cai_total": cai_total,
        "discount_rate": round(discount, 2),
        "effective_score": round(effective_score, 1),
        "wealth_level": level,
        "level_index": level_idx,
        "cai_ku": ku,
        "has_shi_shang_root": has_shi_shang,
        "wealth_windows": wealth_windows[:3],
        "summary": f"理论{level}，财星{cai_total}分，围克折扣{round(discount * 100)}%，有效{round(effective_score, 1)}分",
    }
