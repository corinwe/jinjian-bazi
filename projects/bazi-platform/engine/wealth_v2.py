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
from shen_sha import get_wen_chang
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan

# ── 五级定量 (⚠️ 审计标记 2026-06-29: 以下阈值均为自创，九龙道长原始素材无此数值分段) ──
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
    "金": {"比劫库": "丑", "财库": "未", "官杀库": "戌", "印库": "戌", "食伤库": "辰"},
    "水": {"比劫库": "辰", "财库": "戌", "官杀库": "戌", "印库": "丑", "食伤库": "未"},
}


def _get_base_status(shen_label: str, shen_score: float, cai_total: float) -> str:
    """第1层：定基础状态"""
    if shen_label == "从弱":
        return "从弱格"
    if cai_total <= 0:
        return "无财身弱" if shen_label == "身弱" else "无财身强"
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

    # ⚠️ 审计标记: 折扣率0.3/0.6/1.0为自创数值，无九龙道长原始素材支撑
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
        dy_gan = dy.gan if hasattr(dy, "gan") and dy.gan else (dy.get("gan", "") if isinstance(dy, dict) else "")
        dy_zhi = dy.zhi if hasattr(dy, "zhi") and dy.zhi else (dy.get("zhi", "") if isinstance(dy, dict) else "")
        dy_ss = get_shi_shen_for_gan(dy_gan, ri_zhu) if dy_gan else ""

        score = dy.score if hasattr(dy, "score") else (dy.get("score", 5) if isinstance(dy, dict) else 5)
        is_wealth = dy_ss in ("正财", "偏财", "食神", "伤官")

        if is_wealth and score >= 5:
            gan_zhi = f"{dy_gan}{dy_zhi}" if dy_gan and dy_zhi else str(dy)
            wealth_windows.append({"da_yun": gan_zhi, "window": "补财/食伤大运，利于财富积累", "score": score})
        if shen_label == "身弱" and dy_ss in ("正印", "偏印", "比肩", "劫财") and score >= 5:
            gan_zhi = f"{dy_gan}{dy_zhi}" if dy_gan and dy_zhi else str(dy)
            wealth_windows.append({"da_yun": gan_zhi, "window": "印比帮身大运，身弱能担财", "score": score})

    # 综合评级 (⚠️ 审计标记 2026-06-29: effective_score阈值50/40/30/15均为自创，无九龙道长原始素材支撑)
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

    # 冲库检查（辰戌冲/丑未冲=开财库）
    cai_ku_open = False
    cai_ku_signals = []
    if len(bazi_zhis) >= 4:
        chong_pairs = [("辰", "戌"), ("戌", "辰"), ("丑", "未"), ("未", "丑")]
        for i in range(len(bazi_zhis)):
            for j in range(i + 1, len(bazi_zhis)):
                pair = (bazi_zhis[i], bazi_zhis[j])
                if pair in chong_pairs:
                    # 检查冲开的是否为财库
                    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
                    cai_ku_zhi = WU_KU.get(ri_wx, {}).get("财库", "")
                    if bazi_zhis[i] == cai_ku_zhi or bazi_zhis[j] == cai_ku_zhi:
                        cai_ku_open = True
                        cai_ku_signals.append(
                            f"{bazi_zhis[i]}{bazi_zhis[j]}冲→开财库({cai_ku_zhi})，财富爆发信号"
                        )
                    else:
                        cai_ku_signals.append(
                            f"{bazi_zhis[i]}{bazi_zhis[j]}冲→并非本命财库，需大运流年引动"
                        )

    return {
        "status": status,
        "status_template": template,
        "cai_total": cai_total,
        "discount_rate": round(discount, 2),
        "effective_score": round(effective_score, 1),
        "wealth_level": level,
        "level_index": level_idx,
        "cai_ku": ku,
        "cai_ku_open": cai_ku_open,
        "cai_ku_signals": cai_ku_signals,
        "has_shi_shang_root": has_shi_shang,
        "wealth_windows": wealth_windows[:3],
        "summary": f"理论{level}，财星{cai_total}分，围克折扣{round(discount * 100)}%，有效{round(effective_score, 1)}分",
    }


# ═══════════════════════════════════════════════════════════
# 文昌贵人检查 — 用于财富/事业分析中的文昌辅助判断
# ═══════════════════════════════════════════════════════════

# 十二地支对应位置索引
_ZHI_POSITION = {
    "年": 0,
    "月": 1,
    "日": 2,
    "时": 3,
}

# 反查位置名称
_ZHI_NAMES = {0: "年支", 1: "月支", 2: "日支", 3: "时支"}


def check_wen_chang(rizhu: str, zhi_list: list[str]) -> dict:
    """
    文昌贵人检查

    口诀: 甲巳乙午丙戊申, 丁己酉位庚亥辛, 壬寅癸卯顺推轮

    参数:
      rizhu: 日主天干 (甲~癸)
      zhi_list: [年支, 月支, 日支, 时支] 四个地支

    返回:
      {
        'has_wenchang': bool,       # 原局是否有文昌
        'wenchang_zhi': str,        # 文昌对应的地支 (如"巳")
        'need_supplement': bool,    # 是否需要补文昌 (原局无文昌)
        'wenchang_position': str,   # 文昌所在位置 ("年支"/"月支"/"日支"/"时支"/"无")
      }
    """
    # 查文昌对应的地支
    wc_zhi = get_wen_chang(rizhu)  # 从 shen_sha 查表
    if not wc_zhi:
        return {
            "has_wenchang": False,
            "wenchang_zhi": "",
            "need_supplement": True,
            "wenchang_position": "无",
        }

    # 检查四个地支中是否有文昌
    position = "无"
    for idx, zhi in enumerate(zhi_list):
        if zhi == wc_zhi:
            position = _ZHI_NAMES.get(idx, f"第{idx}柱")
            break

    has = position != "无"

    # 文昌位置对财富的影响力判断
    # 年支文昌 → 祖上文风, 月支文昌 → 少年学业加持, 日支文昌 → 自身智慧,
    # 时支文昌 → 晚年文昌, 子女聪慧
    wenchang_positions_influence = {
        "年支": "祖上书香门第",
        "月支": "少年学业有成",
        "日支": "自身智慧通达",
        "时支": "晚年文昌照拂",
    }

    return {
        "has_wenchang": has,
        "wenchang_zhi": wc_zhi,
        "need_supplement": not has,
        "wenchang_position": position,
        "position_influence": wenchang_positions_influence.get(position, ""),
    }


def analyze_liunian_wealth(bazi_data: dict, liunian_gan: str, liunian_zhi: str) -> dict:
    """
    流年财富分析 — 判断流年对命主财富的影响

    参数:
      bazi_data: 包含以下键的字典:
        - ri_zhu (str): 日主天干
        - bazi_gans (list[str]): [年干, 月干, 日干, 时干]
        - bazi_zhis (list[str]): [年支, 月支, 日支, 时支]
        - shen_label (str): 身强弱标签 ("身强"/"身弱"/"从弱")
        - shen_score (float): 身强弱分数
        - cai_total (float): 财星总分
        - xi_yong (list[str]): 喜用神列表
      liunian_gan: 流年天干
      liunian_zhi: 流年地支

    返回:
      {
        'liunian': str,                       # 流年干支组合
        'liunian_shi_shen': str,              # 流年天干对应的十神
        'is_wealth_year': bool,                # 是否为财星流年
        'is_xi_yong_year': bool,               # 是否为喜用神流年
        'impact': str,                         # 影响描述
        'advice': str,                         # 建议
        'score_impact': float,                 # 对财富分的影响（-10~+10）
      }
    """
    ri_zhu = bazi_data.get("ri_zhu", "")
    bazi_gans = bazi_data.get("bazi_gans", [])
    bazi_zhis = bazi_data.get("bazi_zhis", [])
    shen_label = bazi_data.get("shen_label", "身弱")
    shen_score = bazi_data.get("shen_score", 50.0)
    cai_total = bazi_data.get("cai_total", 0.0)
    xi_yong = bazi_data.get("xi_yong", [])

    if not ri_zhu:
        return {"liunian": f"{liunian_gan}{liunian_zhi}", "error": "缺少日主信息"}

    # 流年天干的十神
    ln_ss = get_shi_shen_for_gan(liunian_gan, ri_zhu)
    is_wealth = ln_ss in ("正财", "偏财")
    is_xi_yong = liunian_gan in xi_yong

    # 流年地支的藏干十神
    ln_zhi_ss_list = []
    for cg, _ in DI_ZHI_CANG_GAN.get(liunian_zhi, []):
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if ss:
            ln_zhi_ss_list.append(ss)
    zhi_has_wealth = "正财" in ln_zhi_ss_list or "偏财" in ln_zhi_ss_list
    zhi_has_xi_yong = any(cg in xi_yong for cg, _ in DI_ZHI_CANG_GAN.get(liunian_zhi, []))

    # ── 综合判断 ──
    impact_parts = []
    score_impact = 0.0
    advice_parts = []

    # 1) 财星流年
    if is_wealth:
        score_impact += 4.0
        impact_parts.append("流年天干为财星")
        if shen_label == "身强":
            score_impact += 3.0
            impact_parts.append("身强能担财，利于求财")
            advice_parts.append("积极主动把握机会")
        elif shen_label == "身弱":
            score_impact -= 2.0
            impact_parts.append("身弱财旺需谨慎，防财多压身")
            advice_parts.append("宜借印比帮身，不宜冒进投资")
        elif shen_label == "从弱":
            score_impact += 5.0
            impact_parts.append("从弱格逢财星，爆发之年")
            advice_parts.append("顺势而为，果断行动")
    elif zhi_has_wealth:
        score_impact += 2.0
        impact_parts.append("流年地支藏财星")

    # 2) 喜用神流年
    if is_xi_yong:
        score_impact += 3.0
        impact_parts.append("天干为喜用神")
        advice_parts.append("各方面运势有利，宜积极进取")
    if zhi_has_xi_yong:
        score_impact += 1.5
        impact_parts.append("地支藏喜用神")

    # 3) 忌神流年
    if not is_xi_yong and ln_ss and ln_ss not in ("正财", "偏财", "正印", "偏印"):
        # 非喜用的比劫/官杀/食伤
        if ln_ss in ("比肩", "劫财"):
            if shen_label == "身强":
                score_impact -= 3.0
                impact_parts.append("身强遇比劫流年→比劫夺财，防破财")
                advice_parts.append("身强比劫年，忌投资合作，防朋友借钱")
            elif shen_label == "身弱":
                score_impact += 2.0
                impact_parts.append("身弱遇比劫流年→比劫帮身，可得合作之财")
                advice_parts.append("身弱喜比劫帮身，可与人合作求财")
            else:
                score_impact -= 2.0
                impact_parts.append("比劫流年，防破财竞争")
                advice_parts.append("谨慎投资，注意人际关系")
        elif ln_ss in ("正官", "七杀"):
            if shen_label == "身强":
                score_impact += 1.0
                impact_parts.append("官杀流年，身强能任官，事业带财")
            else:
                score_impact -= 2.0
                impact_parts.append("官杀流年，压力大妨财")
                advice_parts.append("宜稳守，勿与人争执")

    # 4) 流年与原局特殊关系
    # 流年地支与原局地支的关系
    for idx, zhi in enumerate(bazi_zhis):
        if liunian_zhi == zhi:
            score_impact += 1.0
            impact_parts.append(f"流年伏吟{_ZHI_NAMES.get(idx, '')}，能量加倍")
            break

    # 流年地支冲原局（六冲映射）
    _LIU_CHONG_MAP = {
        "子": "午",
        "丑": "未",
        "寅": "申",
        "卯": "酉",
        "辰": "戌",
        "巳": "亥",
        "午": "子",
        "未": "丑",
        "申": "寅",
        "酉": "卯",
        "戌": "辰",
        "亥": "巳",
    }
    for idx, zhi in enumerate(bazi_zhis):
        if _LIU_CHONG_MAP.get(liunian_zhi) == zhi:
            score_impact -= 1.5
            pos_name = _ZHI_NAMES.get(idx, "")
            impact_parts.append(f"流年冲动{pos_name}，财运动荡")
            advice_parts.append(f"{pos_name}受冲之年，注意财务波动")

    # 5) 文昌流年
    wc_zhi = get_wen_chang(ri_zhu)
    if wc_zhi and liunian_zhi == wc_zhi:
        score_impact += 2.0
        impact_parts.append("流年逢文昌贵人，智慧开运")
        advice_parts.append("利学习、决策、签合同")

    # 财星流年又逢冲 → 大起大落
    if is_wealth and any(_LIU_CHONG_MAP.get(liunian_zhi) == z for z in bazi_zhis):
        score_impact -= 1.0
        impact_parts.append("财星流年逢冲，有财但波动大")

    # 构建输出
    impact_str = "；".join(impact_parts) if impact_parts else "流年对财富无明显影响"
    advice_str = "；".join(advice_parts) if advice_parts else "按兵不动，静观其变"

    # 限制影响分数范围
    score_impact = max(-10.0, min(10.0, score_impact))

    return {
        "liunian": f"{liunian_gan}{liunian_zhi}",
        "liunian_shi_shen": ln_ss or "",
        "is_wealth_year": is_wealth or zhi_has_wealth,
        "is_xi_yong_year": is_xi_yong or zhi_has_xi_yong,
        "impact": impact_str,
        "advice": advice_str,
        "score_impact": round(score_impact, 1),
    }
