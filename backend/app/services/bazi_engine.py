#!/usr/bin/env python3
"""
|金鉴真人·八字排盘引擎 v7.0
基于金鉴真人原始规则体系重写
规则来源：weiwuji-knowledge-base 理论知识体系
v7.0更新：
  - 燥土规则：未/戌对金日主，被火引化不计分
  - 格局透干定：比劫不入格局，检查中气/余气透干
  - 财库计算：calc_cai_xing输出has_ku/cai_ku
"""
from __future__ import annotations
from datetime import datetime, date, timedelta
import math
import lunardate

from app.services.bazi_data import *

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 基础数据
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━



# 藏干权重：本气100% / 中气60% / 余气30%


# 五虎遁月
# 六合
# 三合
# P0-2: 辰戌丑未五行变性引擎
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 辰戌丑未变性映射：
#   辰(水库)：遇申+子 → 水（不以土论）
#   戌(火库)：遇寅+午 → 火（不以土论）
#   丑(金库)：遇巳+酉 → 金（不以土论）
#   未(木库)：遇亥+卯 → 木（不以土论）
BIAN_XING_RULES = {
    "辰": {"trigger": {"申", "子"}, "to_wx": "水", "title": "水库"},
    "戌": {"trigger": {"寅", "午"}, "to_wx": "火", "title": "火库"},
    "丑": {"trigger": {"巳", "酉"}, "to_wx": "金", "title": "金库"},
    "未": {"trigger": {"亥", "卯"}, "to_wx": "木", "title": "木库"},
}

def get_bian_xing_wu_xing(zhi: str, zhi_list: list = None, yue_zhi: str = "") -> str | None:
    """辰戌丑未五行变性检测
    返回变性后的五行，若无变性则返回None

    规则（双维度）：
    维度A — 三合触发（传统规则）：辰遇申+子→水，戌遇寅+午→火，丑遇巳+酉→金，未遇亥+卯→木
    维度B — 单字月令变性（P0补充）：辰戌丑未作为单字在不同月令下的五行变性
    """
    if zhi not in BIAN_XING_RULES:
        return None

    # 维度A：三合触发（至少两个trigger元素在zhi_list中才触发）
    if zhi_list:
        rule = BIAN_XING_RULES[zhi]
        zhi_set = set(zhi_list)
        if rule["trigger"].issubset(zhi_set):
            return rule["to_wx"]

    # 维度B：单字月令变性（月令为四季旺月时，辰戌丑未五行可变）
    if yue_zhi:
        bx = _get_single_bian_xing_by_month(zhi, yue_zhi)
        if bx:
            return bx

    return None


# 辰戌丑未单字月令变性映射
# 格式：{辰戌丑未字: {月令: 变性后五行}}
_SINGLE_BIAN_XING_BY_MONTH = {
    "辰": {
        "寅": "木", "卯": "木",  # 春木旺，辰从木势
        "巳": None, "午": None,  # 夏火生土，辰仍以土论
        "未": None,
        "申": "水", "酉": "水",  # 秋金生水，辰为水库从水势
        "亥": "水", "子": "水",  # 冬水旺，辰从水势
        "丑": None,
        "辰": None, "戌": None,  # 土旺季月，辰本气为土
    },
    "戌": {
        "寅": "火", "卯": "火",  # 春木生火，戌为火库
        "巳": "火", "午": "火",  # 夏火旺，戌为火库从火势
        "未": "火",
        "申": None, "酉": None,  # 秋金旺，火退气，戌仍以土论
        "亥": None, "子": None,  # 冬水克火，戌以土论
        "丑": None,
        "辰": None, "戌": None,  # 土旺季月，戌本气为土
    },
    "丑": {
        "寅": None, "卯": None,  # 春木旺克土，丑仍以土论
        "巳": None, "午": None,  # 夏火生土，丑以土论
        "未": None,
        "申": "金", "酉": "金",  # 秋金旺，丑为金库从金势
        "亥": "水", "子": "水",  # 冬水旺，丑为湿土蓄水
        "丑": None,
        "辰": None, "戌": None,  # 土旺季月，丑本气为土
    },
    "未": {
        "寅": "木", "卯": "木",  # 春木旺，未为木库从木势
        "巳": "火", "午": "火",  # 夏火旺，未为燥土带火性
        "未": None,
        "申": None, "酉": None,  # 秋金旺，土生金，未以土论
        "亥": "木", "子": "木",  # 冬水生木，未为木库得水
        "丑": None,
        "辰": None, "戌": None,  # 土旺季月，未本气为土
    },
}

# 季节组：春季、夏季、秋季、冬季
_SEASON_GROUPS = {
    "春": {"寅", "卯", "辰"},
    "夏": {"巳", "午", "未"},
    "秋": {"申", "酉", "戌"},
    "冬": {"亥", "子", "丑"},
}

# 辰戌丑未按季节的变性（后备规则，当月令精确匹配未命中时）
_SINGLE_BIAN_XING_BY_SEASON = {
    "辰": {"春": "木", "夏": None, "秋": "水", "冬": "水"},
    "戌": {"春": "火", "夏": "火", "秋": None, "冬": None},
    "丑": {"春": None, "夏": None, "秋": "金", "冬": "水"},
    "未": {"春": "木", "夏": "火", "秋": None, "冬": "木"},
}


def _get_single_bian_xing_by_month(zhi: str, yue_zhi: str) -> str | None:
    """按精确月令查出辰戌丑未单字变性结果"""
    monthly_map = _SINGLE_BIAN_XING_BY_MONTH.get(zhi, {})
    # 精确月令命中（含显式None表示不变性）
    if yue_zhi in monthly_map:
        return monthly_map[yue_zhi]

    # 按季节查后备（仅当精确月令未在映射表中时）
    season_map = _SINGLE_BIAN_XING_BY_SEASON.get(zhi, {})
    for season_name, season_zhi_set in _SEASON_GROUPS.items():
        if yue_zhi in season_zhi_set:
            return season_map.get(season_name)
    return None


def get_zhi_wu_xing_with_bian_xing(zhi: str, zhi_list: list, original_func=None) -> str:
    """带五行变性的地支五行查询
    优先检测辰戌丑未变性，无变性则返回原始五行
    """
    bx = get_bian_xing_wu_xing(zhi, zhi_list)
    if bx:
        return bx
    # 回退到原始查询
    if original_func:
        return original_func(zhi)
    return DI_ZHI_WU_XING.get(zhi, "土")


GAN_WU_HE = {
    "甲":"己","己":"甲","乙":"庚","庚":"乙",
    "丙":"辛","辛":"丙","丁":"壬","壬":"丁",
    "戊":"癸","癸":"戊",
}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 工具函数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def gan_idx(g): return TIAN_GAN.index(g)
def zhi_idx(z): return DI_ZHI.index(z)
def wx_of(g): return TIAN_GAN_WU_XING[g]
def ri_yin(g): return gan_idx(g) % 2  # 0阳1阴

def shi_shen(ri_gan: str, gan: str, mark_xiao: bool = False, tian_gan_list: list = None) -> str:
    """十神
    新增: mark_xiao=True 时，偏印在天干且食神/伤官也在天干 → 标记为"枭神"
    """
    ri = gan_idx(ri_gan); g = gan_idx(gan)
    rw = WX_ORDER.index(wx_of(ri_gan)); gw = WX_ORDER.index(wx_of(gan))
    ry = ri % 2; gy = g % 2
    if rw == gw: return "比肩" if ry==gy else "劫财"
    if gw == (rw+1)%5: return "食神" if ry==gy else "伤官"
    if gw == (rw+2)%5: return "正财" if ry!=gy else "偏财"
    if gw == (rw+3)%5: return "正官" if ry!=gy else "七杀"
    if gw == (rw+4)%5:
        # 正印/偏印：阴阳同→偏印，阴阳异→正印
        if ry != gy:
            return "正印"  # 异阴阳→正印（正）
        # 同阴阳→偏印：检查是否枭神夺食
        if mark_xiao and tian_gan_list:
            # 检查天干是否有食神或伤官
            for tg in tian_gan_list:
                if tg:
                    tg_ss = _raw_shi_shen(ri_gan, tg)
                    if tg_ss in ("食神", "伤官"):
                        return "枭神"  # 夺食状态
        return "偏印"
    return ""


def _raw_shi_shen(ri_gan: str, gan: str) -> str:
    """内部原始十神（无mark_xiao逻辑，避免递归）"""
    ri = gan_idx(ri_gan); g = gan_idx(gan)
    rw = WX_ORDER.index(wx_of(ri_gan)); gw = WX_ORDER.index(wx_of(gan))
    ry = ri % 2; gy = g % 2
    if rw == gw: return "比肩" if ry==gy else "劫财"
    if gw == (rw+1)%5: return "食神" if ry==gy else "伤官"
    if gw == (rw+2)%5: return "正财" if ry!=gy else "偏财"
    if gw == (rw+3)%5: return "正官" if ry!=gy else "七杀"
    if gw == (rw+4)%5: return "正印" if ry!=gy else "偏印"
    return ""

def na_yin(gan: str, zhi: str) -> str:
    """纳音：60甲子序数直接索引"""
    seq = (gan_idx(gan)*6 - zhi_idx(zhi)*5) % 60
    return NA_YIN[seq]

def kong_wang(gan: str, zhi: str) -> list:
    """空亡：60甲子序数→旬首→空亡"""
    seq = (gan_idx(gan)*6 - zhi_idx(zhi)*5) % 60
    xun = seq // 10
    xun_zhi = (12 - xun*2) % 12
    return [DI_ZHI[(xun_zhi-2)%12], DI_ZHI[(xun_zhi-1)%12]]

def is_zao_tu_effective(zhi: str, ri_gan: str, tian_gan_list: list) -> bool:
    """
    燥土是否有效（有效才计分）v7.1
    规则：未/戌对庚辛金日主
      - 天干有丙/丁（火引化）→ 当火看 → 不计分
      - 月干直接引化（月干丙/丁对月令未/戌）→ 优先不计分，不受时干水平干扰
      - 天干有壬/癸（水灭火）→ 当土看 → 计分
      - 无火无水 → 计分
      - 非金日主 → 不计燥土规则
    """
    if zhi not in ZAO_TU:
        return True  # 非燥土地支，正常计分
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    if ri_wx != "金":
        return True  # 非金日主，燥土规则不适用
    # 月干直接引化规则：月干丙/丁直接引化月令未/戌，时干水平无法灭火
    has_yue_gan_huo = tian_gan_list[1] in ("丙","丁")
    is_yue_ling = (zhi == "未" or zhi == "戌")  # 调用时传的是月令
    if has_yue_gan_huo and is_yue_ling:
        return False  # 月干透火直接引化月令→不计分
    has_huo = any(g in ("丙","丁") for g in tian_gan_list)
    has_shui = any(g in ("壬","癸") for g in tian_gan_list)
    if has_huo and not has_shui:
        return False  # 火引化→不计分
    return True  # 有水平火，或无水无火→计分

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 节气计算（精确查表法 1900-2100）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

JIE_QI_DATES_CENTURY = [
    # 2000年节气日期表 (月,日) — 12个节
    # 立春,惊蛰,清明,立夏,芒种,小暑,立秋,白露,寒露,立冬,大雪,小寒(次年)
    (2,4),(3,5),(4,5),(5,5),(6,5),(7,7),(8,7),(9,7),(10,8),(11,7),(12,7),(1,6)
]

def get_solar_term_date(year: int, term_index: int) -> date:
    """
    获取节气日期。
    使用天文经验公式，精度±1天。
    term_index: 0=立春,1=惊蛰,...,10=大雪,11=小寒(次年)
    """
    m, d = JIE_QI_DATES_CENTURY[term_index]
    if term_index < 11:
        # 今年节气
        y_offset = year - 2000
        drift = round(abs(y_offset) * 0.2422)
        leap_before = sum(1 for y in range(year+1, 2001)
                         if (y%4==0 and y%100!=0) or y%400==0) if year < 2000 else 0
        leap_after = sum(1 for y in range(2001, year+1)
                        if (y%4==0 and y%100!=0) or y%400==0) if year > 2000 else 0
        if year > 2000:
            adj = -drift + leap_after
        elif year < 2000:
            adj = drift - leap_before
        else:
            adj = 0
        return date(year, m, d) + timedelta(days=adj)
    else:
        # 小寒在次年1月
        return date(year+1, m, d) + timedelta(days=round(-(year-2000)*0.2422))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 四柱计算
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_nian_zhu(year: int, month: int, day: int) -> tuple:
    """年柱：立春分界"""
    lc = get_solar_term_date(year, 0)
    actual = year if (month > lc.month or (month==lc.month and day>=lc.day)) else year-1
    return TIAN_GAN[(actual-4)%10], DI_ZHI[(actual-4)%12]

def get_yue_zhu(year: int, month: int, day: int, nian_gan: str) -> tuple:
    """月柱：节气分界 + 五虎遁"""
    current = date(year, month, day)
    # 构建12个节气序列：立春(今年)~小寒(明年)
    terms = [get_solar_term_date(year, i) for i in range(12)]
    
    if current < terms[0]:  # 立春前→上一年
        prev_terms = [get_solar_term_date(year-1, 10), get_solar_term_date(year-1, 11)]
        if current >= prev_terms[1]:
            branch_idx = 1  # 丑(小寒后)
        elif current >= prev_terms[0]:
            branch_idx = 0  # 子(大雪后)
        else:
            branch_idx = 11  # 亥(大雪前)
    else:
        latest = -1
        for i in range(12):
            if current >= terms[i]:
                latest = i
        if latest >= 0:
            # 节气→月支映射
            term_branch = {0:2,1:3,2:4,3:5,4:6,5:7,6:8,7:9,8:10,9:11,10:0,11:1}
            branch_idx = term_branch[latest]
        else:
            branch_idx = 2  # fallback寅
    
    start_gan = WU_HU_DUN_YUE[nian_gan]
    gan_idx_val = (TIAN_GAN.index(start_gan) + (branch_idx-2)%12) % 10
    return TIAN_GAN[gan_idx_val], DI_ZHI[branch_idx]

def get_ri_zhu(year: int, month: int, day: int) -> tuple:
    """日柱：2000-01-01 戊午日 为基准"""
    delta = (date(year, month, day) - date(2000, 1, 1)).days
    return TIAN_GAN[(4+delta)%10], DI_ZHI[(6+delta)%12]

def get_shi_zhu(hour: int, minute: int, ri_gan: str) -> tuple:
    """时柱：五鼠遁"""
    if hour == 23 or hour < 1: z = 0
    elif hour < 3: z = 1
    elif hour < 5: z = 2
    elif hour < 7: z = 3
    elif hour < 9: z = 4
    elif hour < 11: z = 5
    elif hour < 13: z = 6
    elif hour < 15: z = 7
    elif hour < 17: z = 8
    elif hour < 19: z = 9
    elif hour < 21: z = 10
    else: z = 11
    sg = WU_SHU_DUN_SHI[ri_gan]
    gi = (TIAN_GAN.index(sg) + z) % 10
    return TIAN_GAN[gi], DI_ZHI[z]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 三合/六合检测
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_san_he(zhi_list: list, tian_gan_list: list = None) -> tuple:
    """
    检查三合局。返回 (局名, 是否完整, 能量倍数, 是否有引化)
    完整三合：有引化15倍，无引化7.5倍
    半三合：有引化10倍，无引化5倍
    """
    zhi_set = set(zhi_list)
    for he_set, wx in SAN_HE.items():
        present = zhi_set.intersection(he_set)
        if len(present) == 3:
            has_yh = _has_yin_hua(wx, tian_gan_list) if tian_gan_list else False
            mult = ENERGY_MULTIPLIER["三合有引化"] if has_yh else ENERGY_MULTIPLIER["三合无引化"]
            return (wx, True, mult, has_yh)
        elif len(present) >= 2:
            has_yh = _has_yin_hua(wx, tian_gan_list) if tian_gan_list else False
            mult = ENERGY_MULTIPLIER["半三合有引化"] if has_yh else ENERGY_MULTIPLIER["半三合无引化"]
            return (wx, False, mult, has_yh)
    return ("", False, 1, False)

def check_liu_he(zhi_list: list) -> list:
    """检查六合，返回所有六合对"""
    pairs = []
    for i, z1 in enumerate(zhi_list):
        for z2 in zhi_list[i+1:]:
            if LIU_HE.get(z1) == z2 or LIU_HE.get(z2) == z1:
                pairs.append((z1, z2))
    return pairs


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 能量倍数引擎（总纲v1.0核心公式）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 恶神×能量对应表（九龙道长体系）
# 用于根据能量倍数断灾祸/流年事件
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
E_SHEN_EVENT_MAP = {
    "七杀": [
        {"range": (1, 3), "event": "压力、小人口舌、罚单", "level": "轻微"},
        {"range": (3, 7), "event": "得病、手术", "level": "中等"},
        {"range": (10, 15), "event": "官非、牢狱", "level": "严重"},
        {"range": (20, 20), "event": "横死、大灾", "level": "极凶"},
    ],
    "伤官": [
        {"range": (1, 3), "event": "口舌是非", "level": "轻微"},
        {"range": (3, 7), "event": "官非", "level": "中等"},
        {"range": (10, 15), "event": "丢官罢职", "level": "严重"},
        {"range": (20, 20), "event": "牢狱", "level": "极凶"},
    ],
    "枭印": [
        {"range": (1, 3), "event": "不开心、郁闷", "level": "轻微"},
        {"range": (3, 7), "event": "抑郁症、情绪障碍", "level": "中等"},
        {"range": (10, 15), "event": "精神疾病", "level": "严重"},
    ],
    "劫财": [
        {"range": (1, 3), "event": "破小财、意外支出", "level": "轻微"},
        {"range": (3, 7), "event": "破大财、重大损失", "level": "中等"},
        {"range": (10, 15), "event": "破产", "level": "严重"},
    ],
    "灾煞": [
        {"range": (10, 10), "event": "车祸、意外事故", "level": "严重"},
        {"range": (15, 15), "event": "血光之灾", "level": "极凶"},
    ],
    "血刃": [
        {"range": (10, 10), "event": "手术", "level": "严重"},
        {"range": (15, 15), "event": "血光之灾", "level": "极凶"},
    ],
}

# 恶神事件等级阈值
E_SHEN_LEVEL_THRESHOLDS = {
    "七杀":  {"轻微": (1, 3), "中等": (3, 7), "严重": (10, 15), "极凶": (20, 20)},
    "伤官":  {"轻微": (1, 3), "中等": (3, 7), "严重": (10, 15), "极凶": (20, 20)},
    "枭印":  {"轻微": (1, 3), "中等": (3, 7), "严重": (10, 15)},
    "劫财":  {"轻微": (1, 3), "中等": (3, 7), "严重": (10, 15)},
    "灾煞":  {"严重": (10, 10), "极凶": (15, 15)},
    "血刃":  {"严重": (10, 10), "极凶": (15, 15)},
}


def e_shen_event_lookup(e_shen: str, energy_multiplier: float) -> str:
    """根据恶神名称和能量倍数查找对应事件描述

    Args:
        e_shen: 恶神名称（七杀/伤官/枭印/劫财/灾煞/血刃）
        energy_multiplier: 能量倍数

    Returns:
        事件描述字符串，如"压力、小人口舌、罚单"
    """
    if e_shen not in E_SHEN_EVENT_MAP:
        return ""
    best_event = ""
    best_level = -1
    level_order = {"轻微": 0, "中等": 1, "严重": 2, "极凶": 3}
    for entry in E_SHEN_EVENT_MAP[e_shen]:
        lo, hi = entry["range"]
        if lo <= energy_multiplier <= hi:
            lv = level_order.get(entry.get("level", ""), -1)
            if lv > best_level:
                best_level = lv
                best_event = entry["event"]
    # 高于最高区间的fallback：取最高级别的事件
    if not best_event:
        max_hi = max(e["range"][1] for e in E_SHEN_EVENT_MAP[e_shen])
        if energy_multiplier > max_hi:
            # 取最后一条（最高级）事件
            highest_entry = max(E_SHEN_EVENT_MAP[e_shen], key=lambda e: e["range"][1])
            best_event = highest_entry.get("event", "")
    return best_event


def e_shen_event_level(e_shen: str, energy_multiplier: float) -> str:
    """获取恶神事件等级（轻微/中等/严重/极凶）"""
    if e_shen not in E_SHEN_EVENT_MAP:
        return ""
    best_level_str = ""
    best_level = -1
    level_order = {"轻微": 0, "中等": 1, "严重": 2, "极凶": 3}
    for entry in E_SHEN_EVENT_MAP[e_shen]:
        lo, hi = entry["range"]
        if lo <= energy_multiplier <= hi:
            lv = level_order.get(entry.get("level", ""), -1)
            if lv > best_level:
                best_level = lv
                best_level_str = entry.get("level", "")
    # 高于最高区间的fallback
    if not best_level_str:
        max_hi = max(e["range"][1] for e in E_SHEN_EVENT_MAP[e_shen])
        if energy_multiplier > max_hi:
            best_level_str = "极凶"
    return best_level_str


def _has_yin_hua(he_wx: str, tian_gan_list: list) -> bool:
    """判断合局/刑冲是否有引化（化神在天干透出）

    规则：合局/刑冲所化五行在天干有透出 = 有引化
    如申子辰水局，天干有壬/癸水即为有引化

    Args:
        he_wx: 合局/刑冲的五行（木火土金水）
        tian_gan_list: 天干列表 [年干,月干,日干,时干]

    Returns:
        True=有引化, False=无引化
    """
    WX_TO_GAN = {
        "木": ["甲", "乙"],
        "火": ["丙", "丁"],
        "土": ["戊", "己"],
        "金": ["庚", "辛"],
        "水": ["壬", "癸"],
    }
    yin_hua_gans = WX_TO_GAN.get(he_wx, [])
    return any(g in tian_gan_list for g in yin_hua_gans)


def _calc_energy_multiplier(zhi_list: list, tian_gan_list: list) -> dict:
    """完整能量倍数计算（九龙道长体系）

    计算每个地支的最终能量倍数及所有刑冲合害关系，
    含合化/刑冲的引化判定（有引化/无引化两档）。

    输入：
        zhi_list: 四柱地支列表 [年支, 月支, 日支, 时支]
        tian_gan_list: 天干列表 [年干, 月干, 日干, 时干]

    输出：
        {
            "relationships": [...],  # 所有关系及倍数
            "per_zhi": {             # 每个地支的倍数详情
                "子": {"base": 1.0, "boosts": [...], "total": 1.0},
                ...
            },
            "total_energy": 0,       # 总能量倍数
            "yin_hua_detail": {...},  # 引化详情
            "has_zi_mao_xing": False, # 子卯刑标记（不加强能量）
        }
    """
    from collections import defaultdict

    positions = ["年支", "月支", "日支", "时支"]
    # 每个地支的倍数累积
    per_zhi = {z: {"base": 1.0, "boosts": [], "total": 1.0} for z in zhi_list}
    relationships = []
    total_energy = 0.0
    has_zi_mao_xing = False
    yin_hua_detail = {}

    # ---- 1. 天干透出本气（3倍） ----
    for i, zhi in enumerate(zhi_list):
        cang_gan = DI_ZHI_CANG_GAN.get(zhi, [])
        if cang_gan:
            ben_qi_gan = cang_gan[0][0]  # 本气天干
            # 检查本气是否在天干透出
            for j, tg in enumerate(tian_gan_list):
                if tg and tg == ben_qi_gan:
                    boost = ENERGY_MULTIPLIER["透干"]
                    desc = f"{positions[i]}{zhi}本气{tg}在天干{['年干','月干','日干','时干'][j]}透出 +{boost}倍"
                    per_zhi[zhi]["boosts"].append(desc)
                    per_zhi[zhi]["total"] += boost
                    total_energy += boost
                    break

    # ---- 2. 天干通根于地支（3倍） ----
    for j, tg in enumerate(tian_gan_list):
        if not tg:
            continue
        tg_wx = TIAN_GAN_WU_XING.get(tg, "")
        if not tg_wx:
            continue
        # 检查天干五行是否在地支有根（地支藏干中有同五行）
        for i, zhi in enumerate(zhi_list):
            cang_gan = DI_ZHI_CANG_GAN.get(zhi, [])
            for cg_gan, _ in cang_gan:
                cg_wx = TIAN_GAN_WU_XING.get(cg_gan, "")
                if cg_wx == tg_wx and cg_gan != tg:
                    # 通根：天干在地支的藏干中找到同五行
                    boost = ENERGY_MULTIPLIER["透干"]
                    desc = f"{['年干','月干','日干','时干'][j]}{tg}通根于{positions[i]}{zhi}(藏{cg_gan}) +{boost}倍"
                    per_zhi[zhi]["boosts"].append(desc)
                    per_zhi[zhi]["total"] += boost
                    total_energy += boost
                    break

    # ---- 3. 三合局检查 ----
    zhi_set = set(zhi_list)
    for he_set, wx in SAN_HE.items():
        present = zhi_set.intersection(he_set)
        present_list = sorted(present, key=lambda z: zhi_list.index(z) if z in zhi_list else 0)
        if len(present) >= 2:
            has_yh = _has_yin_hua(wx, tian_gan_list)
            if len(present) == 3:
                mult = ENERGY_MULTIPLIER["三合有引化"] if has_yh else ENERGY_MULTIPLIER["三合无引化"]
                yin_hua_detail[f"{wx}三合局"] = "有引化" if has_yh else "无引化"
                rel = {
                    "type": "三合局", "name": f"{wx}三合局",
                    "multiplier": mult, "has_yin_hua": has_yh,
                    "detail": f"地支{'、'.join(present_list)}构成{wx}三合局 {mult}倍({'有引化' if has_yh else '无引化'})",
                    "zhi_a": present_list[0] if present_list else "",
                    "zhi_b": present_list[1] if len(present_list) > 1 else "",
                }
                relationships.append(rel)
                total_energy += mult
                for z in present:
                    per_zhi[z]["boosts"].append(f"{wx}三合局({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z]["total"] *= (1 + mult / 10)  # 合局对各参与者按比例增强
            elif len(present) == 2:
                mult = ENERGY_MULTIPLIER["半三合有引化"] if has_yh else ENERGY_MULTIPLIER["半三合无引化"]
                yin_hua_detail[f"{wx}半三合"] = "有引化" if has_yh else "无引化"
                rel = {
                    "type": "半三合", "name": f"{wx}半三合",
                    "multiplier": mult, "has_yin_hua": has_yh,
                    "detail": f"地支{'、'.join(present_list)}构成{wx}半三合 {mult}倍({'有引化' if has_yh else '无引化'})",
                    "zhi_a": present_list[0] if present_list else "",
                    "zhi_b": present_list[1] if len(present_list) > 1 else "",
                }
                relationships.append(rel)
                total_energy += mult
                for z in present:
                    per_zhi[z]["boosts"].append(f"{wx}半三合({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z]["total"] += mult

    # ---- 4. 三会局检查 ----
    for he_set, wx in SAN_HUI.items():
        present = zhi_set.intersection(he_set)
        present_list = sorted(present, key=lambda z: zhi_list.index(z) if z in zhi_list else 0)
        if len(present) >= 2:
            has_yh = _has_yin_hua(wx, tian_gan_list)
            if len(present) == 3:
                mult = ENERGY_MULTIPLIER["三会有引化"] if has_yh else ENERGY_MULTIPLIER["三会无引化"]
                yin_hua_detail[f"{wx}三会局"] = "有引化" if has_yh else "无引化"
                rel = {
                    "type": "三会局", "name": f"{wx}三会局",
                    "multiplier": mult, "has_yin_hua": has_yh,
                    "detail": f"地支{'、'.join(present_list)}构成{wx}三会局 {mult}倍({'有引化' if has_yh else '无引化'})",
                    "zhi_a": present_list[0] if present_list else "",
                    "zhi_b": present_list[1] if len(present_list) > 1 else "",
                }
                relationships.append(rel)
                total_energy += mult
                for z in present:
                    per_zhi[z]["boosts"].append(f"{wx}三会局({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z]["total"] *= (1 + mult / 10)
            elif len(present) == 2:
                mult = ENERGY_MULTIPLIER["半三合有引化"] if has_yh else ENERGY_MULTIPLIER["半三合无引化"]
                yin_hua_detail[f"{wx}半会局"] = "有引化" if has_yh else "无引化"
                rel = {
                    "type": "半会局", "name": f"{wx}半会局",
                    "multiplier": mult, "has_yin_hua": has_yh,
                    "detail": f"地支{'、'.join(present_list)}构成{wx}半会局 {mult}倍({'有引化' if has_yh else '无引化'})",
                    "zhi_a": present_list[0] if present_list else "",
                    "zhi_b": present_list[1] if len(present_list) > 1 else "",
                }
                relationships.append(rel)
                total_energy += mult
                for z in present:
                    per_zhi[z]["boosts"].append(f"{wx}半会局({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z]["total"] += mult

    # ---- 5. 六合/六害/六破/六冲/三刑/自刑检测（pairwise） ----
    for i in range(len(zhi_list)):
        for j in range(i + 1, len(zhi_list)):
            z1, z2 = zhi_list[i], zhi_list[j]

            # 六合
            if LIU_HE.get(z1) == z2:
                # 六合化什么五行？
                he_wx = _get_liu_he_wx(z1, z2)
                has_yh = _has_yin_hua(he_wx, tian_gan_list) if he_wx else False
                mult = ENERGY_MULTIPLIER["六合有引化"] if has_yh else ENERGY_MULTIPLIER["六合无引化"]
                yin_hua_detail[f"{z1}{z2}合"] = f"有引化({he_wx}透干)" if has_yh and he_wx else f"无引化"
                rel = {
                    "type": "六合", "name": f"{z1}{z2}六合",
                    "multiplier": mult, "has_yin_hua": has_yh,
                    "detail": f"{z1}与{z2}六合 {'有引化' if has_yh else '无引化'} ×{mult}倍",
                    "zhi_a": z1, "zhi_b": z2,
                }
                relationships.append(rel)
                total_energy += mult
                per_zhi[z1]["boosts"].append(f"{z1}{z2}六合({'有引化' if has_yh else '无引化'}) +{mult}倍")
                per_zhi[z2]["boosts"].append(f"{z1}{z2}六合({'有引化' if has_yh else '无引化'}) +{mult}倍")
                per_zhi[z1]["total"] += mult / 2
                per_zhi[z2]["total"] += mult / 2
                continue

            # 六冲 — 辰戌丑未冲特殊处理（有引化/无引化）
            if LIU_CHONG.get(z1) == z2:
                if z1 in ("辰", "戌", "丑", "未") and z2 in ("辰", "戌", "丑", "未"):
                    # 辰戌丑未冲：有引化=10倍，无引化=5倍
                    has_yh = _has_yin_hua("土", tian_gan_list)
                    mult = ENERGY_MULTIPLIER["辰戌丑未冲有引化"] if has_yh else ENERGY_MULTIPLIER["辰戌丑未冲无引化"]
                    yin_hua_detail[f"{z1}{z2}冲"] = "有引化" if has_yh else "无引化"
                    rel = {
                        "type": "辰戌丑未冲", "name": f"{z1}{z2}冲",
                        "multiplier": mult, "has_yin_hua": has_yh,
                        "detail": f"{z1}与{z2}辰戌丑未冲 {'有引化' if has_yh else '无引化'} ×{mult}倍",
                        "zhi_a": z1, "zhi_b": z2,
                    }
                    relationships.append(rel)
                    total_energy += mult
                    per_zhi[z1]["boosts"].append(f"{z1}{z2}辰戌丑未冲({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z2]["boosts"].append(f"{z1}{z2}辰戌丑未冲({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z1]["total"] += mult / 2
                    per_zhi[z2]["total"] += mult / 2
                else:
                    mult = ENERGY_MULTIPLIER["六冲"]
                    rel = {
                        "type": "六冲", "name": f"{z1}{z2}冲",
                        "multiplier": mult,
                        "detail": f"{z1}与{z2}相冲 ×{mult}倍",
                        "zhi_a": z1, "zhi_b": z2,
                    }
                    relationships.append(rel)
                    total_energy += mult
                    per_zhi[z1]["boosts"].append(f"{z1}{z2}六冲 +{mult}倍")
                    per_zhi[z2]["boosts"].append(f"{z1}{z2}六冲 +{mult}倍")
                    per_zhi[z1]["total"] += mult / 2
                    per_zhi[z2]["total"] += mult / 2
                continue

            # 三刑：子卯刑特殊处理（不加强能量）
            if {z1, z2} == {"子", "卯"}:
                has_zi_mao_xing = True
                rel = {
                    "type": "子卯刑", "name": f"{z1}{z2}子卯刑",
                    "multiplier": 0,  # 子卯刑不加强能量
                    "detail": f"{z1}与{z2}子卯刑（无礼之刑）— 特殊规则：不加强能量",
                    "zhi_a": z1, "zhi_b": z2,
                }
                relationships.append(rel)
                per_zhi[z1]["boosts"].append(f"{z1}{z2}子卯刑（不加强能量）")
                per_zhi[z2]["boosts"].append(f"{z1}{z2}子卯刑（不加强能量）")
                continue

            # 其他三刑（寅巳申、丑未戌中的pair）
            for pair_key, (pz1, pz2) in [("寅巳",("寅","巳")),("巳申",("巳","申")),
                                          ("丑未",("丑","未")),("未戌",("未","戌")),("丑戌",("丑","戌"))]:
                if {z1, z2} == {pz1, pz2}:
                    has_yh = _has_yin_hua("土" if "丑" in pair_key or "未" in pair_key or "戌" in pair_key else "木" if "寅" in pair_key else "水", tian_gan_list)
                    mult = ENERGY_MULTIPLIER["三刑有引化"] if has_yh else ENERGY_MULTIPLIER["三刑无引化"]
                    yin_hua_detail[f"{z1}{z2}刑"] = "有引化" if has_yh else "无引化"
                    rel = {
                        "type": "三刑", "name": f"{z1}{z2}三刑",
                        "multiplier": mult, "has_yin_hua": has_yh,
                        "detail": f"{z1}与{z2}相刑 {'有引化' if has_yh else '无引化'} ×{mult}倍",
                        "zhi_a": z1, "zhi_b": z2,
                    }
                    relationships.append(rel)
                    total_energy += mult
                    per_zhi[z1]["boosts"].append(f"{z1}{z2}三刑({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z2]["boosts"].append(f"{z1}{z2}三刑({'有引化' if has_yh else '无引化'}) +{mult}倍")
                    per_zhi[z1]["total"] += mult / 2
                    per_zhi[z2]["total"] += mult / 2
                    break
            else:
                # 不是三刑，继续检查其他关系
                # 六害
                if LIU_HAI.get(z1) == z2:
                    mult = ENERGY_MULTIPLIER["六害"]
                    rel = {
                        "type": "六害", "name": f"{z1}{z2}害",
                        "multiplier": mult,
                        "detail": f"{z1}与{z2}相害 ×{mult}倍",
                        "zhi_a": z1, "zhi_b": z2,
                    }
                    relationships.append(rel)
                    total_energy += mult
                    per_zhi[z1]["boosts"].append(f"{z1}{z2}六害 +{mult}倍")
                    per_zhi[z2]["boosts"].append(f"{z1}{z2}六害 +{mult}倍")
                    per_zhi[z1]["total"] += mult / 2
                    per_zhi[z2]["total"] += mult / 2
                    continue

                # 六破
                if LIU_PO.get(z1) == z2:
                    mult = ENERGY_MULTIPLIER["六破"]
                    rel = {
                        "type": "六破", "name": f"{z1}{z2}破",
                        "multiplier": mult,
                        "detail": f"{z1}与{z2}相破 ×{mult}倍",
                        "zhi_a": z1, "zhi_b": z2,
                    }
                    relationships.append(rel)
                    total_energy += mult
                    per_zhi[z1]["boosts"].append(f"{z1}{z2}六破 +{mult}倍")
                    per_zhi[z2]["boosts"].append(f"{z1}{z2}六破 +{mult}倍")
                    per_zhi[z1]["total"] += mult / 2
                    per_zhi[z2]["total"] += mult / 2
                    continue

    # ---- 6. 自刑检查 ----
    from collections import Counter
    zhi_counter = Counter(zhi_list)
    for z, count in zhi_counter.items():
        if count >= 2 and z in ZI_XING:
            has_yh = _has_yin_hua(DI_ZHI_WU_XING.get(z, "土"), tian_gan_list)
            mult = ENERGY_MULTIPLIER["自刑有引化"] if has_yh else ENERGY_MULTIPLIER["自刑无引化"]
            yin_hua_detail[f"{z}自刑"] = "有引化" if has_yh else "无引化"
            rel = {
                "type": "自刑", "name": f"{z}自刑",
                "multiplier": mult, "has_yin_hua": has_yh,
                "detail": f"{z}自刑（{'有引化' if has_yh else '无引化'}）×{mult}倍",
                "zhi_a": z, "zhi_b": z,
            }
            relationships.append(rel)
            total_energy += mult
            per_zhi[z]["boosts"].append(f"{z}自刑({'有引化' if has_yh else '无引化'}) +{mult}倍")
            per_zhi[z]["total"] += mult

    # ---- 汇总 ----
    return {
        "relationships": relationships,
        "per_zhi": dict(per_zhi),
        "total_energy": round(total_energy, 1),
        "yin_hua_detail": yin_hua_detail,
        "has_zi_mao_xing": has_zi_mao_xing,
        "count": len(relationships),
    }


def _get_liu_he_wx(z1: str, z2: str) -> str:
    """获取六合所化五行"""
    LIU_HE_WU_XING = {
        ("子", "丑"): "土", ("丑", "子"): "土",
        ("寅", "亥"): "木", ("亥", "寅"): "木",
        ("卯", "戌"): "火", ("戌", "卯"): "火",
        ("辰", "酉"): "金", ("酉", "辰"): "金",
        ("巳", "申"): "水", ("申", "巳"): "水",
        ("午", "未"): "土", ("未", "午"): "土",  # 午未合土
    }
    return LIU_HE_WU_XING.get((z1, z2), "")


_ZHONG_QI_MAP = {}  # placeholder for forward reference


def check_liu_hai(zhi_list: list) -> list:
    """检查六害，返回所有六害对"""
    pairs = []
    for i, z1 in enumerate(zhi_list):
        for z2 in zhi_list[i+1:]:
            if LIU_HAI.get(z1) == z2 or LIU_HAI.get(z2) == z1:
                pairs.append((z1, z2))
    return pairs


def check_liu_po(zhi_list: list) -> list:
    """检查六破，返回所有六破对"""
    pairs = []
    for i, z1 in enumerate(zhi_list):
        for z2 in zhi_list[i+1:]:
            if LIU_PO.get(z1) == z2 or LIU_PO.get(z2) == z1:
                pairs.append((z1, z2))
    return pairs


def check_san_hui(zhi_list: list, tian_gan_list: list = None) -> tuple:
    """检查三会局。返回 (五行, 是否完整, 能量倍数, 是否有引化)
    三会：有引化20倍，无引化10倍
    半会：有引化10倍，无引化5倍
    """
    zhi_set = set(zhi_list)
    for he_set, wx in SAN_HUI.items():
        present = zhi_set.intersection(he_set)
        if len(present) == 3:
            has_yh = _has_yin_hua(wx, tian_gan_list) if tian_gan_list else False
            mult = ENERGY_MULTIPLIER["三会有引化"] if has_yh else ENERGY_MULTIPLIER["三会无引化"]
            return (wx, True, mult, has_yh)
        elif len(present) >= 2:
            has_yh = _has_yin_hua(wx, tian_gan_list) if tian_gan_list else False
            mult = ENERGY_MULTIPLIER["半三合有引化"] if has_yh else ENERGY_MULTIPLIER["半三合无引化"]
            return (wx, False, mult, has_yh)
    return ("", False, 1, False)


def check_san_xing(zhi_list: list, tian_gan_list: list = None) -> list:
    """检查三刑（不含自刑），返回所有三刑组合及类型
    自刑由calc_energy_relationship的pairwise检测处理，避免重复计数
    子卯刑特殊：不加强能量（倍数为0）
    其他三刑：有引化15倍，无引化7.5倍
    """
    results = []
    zhi_set = set(zhi_list)
    # 寅巳申三刑
    if {"寅","巳","申"}.issubset(zhi_set):
        has_yh = _has_yin_hua("水", tian_gan_list) if tian_gan_list else False
        mult = ENERGY_MULTIPLIER["三刑有引化"] if has_yh else ENERGY_MULTIPLIER["三刑无引化"]
        results.append(("寅巳申三刑", "无恩之刑", mult, has_yh))
    # 丑未戌三刑
    if {"丑","未","戌"}.issubset(zhi_set):
        has_yh = _has_yin_hua("土", tian_gan_list) if tian_gan_list else False
        mult = ENERGY_MULTIPLIER["三刑有引化"] if has_yh else ENERGY_MULTIPLIER["三刑无引化"]
        results.append(("丑未戌三刑", "恃势之刑", mult, has_yh))
    # 子卯刑（特殊：不加强能量）
    if {"子","卯"}.issubset(zhi_set):
        results.append(("子卯刑", "无礼之刑", 0, False))  # 子卯刑不加强能量
    return results


def calc_energy_relationship(zhi_a: str, zhi_b: str, tian_gan_list: list = None) -> dict:
    """计算两个地支之间的能量关系
    返回 {"type":关系类型, "name":关系名称, "multiplier":能量倍数, "detail":描述, "has_yin_hua":是否引化}

    按九龙道长体系：
    - 六合：有引化10倍，无引化5倍
    - 辰戌丑未冲：有引化10倍，无引化5倍（普通六冲固定10倍）
    - 三刑：有引化15倍，无引化7.5倍（子卯刑特殊=0倍）
    - 自刑：有引化10倍，无引化5倍
    """
    # 六冲 — 辰戌丑未冲特殊处理
    if LIU_CHONG.get(zhi_a) == zhi_b:
        wx_a = DI_ZHI_WU_XING[zhi_a]
        wx_b = DI_ZHI_WU_XING[zhi_b]
        if zhi_a in ("辰","戌","丑","未") and zhi_b in ("辰","戌","丑","未"):
            has_yh = _has_yin_hua("土", tian_gan_list) if tian_gan_list else False
            mult = ENERGY_MULTIPLIER["辰戌丑未冲有引化"] if has_yh else ENERGY_MULTIPLIER["辰戌丑未冲无引化"]
            return {"type":"辰戌丑未冲", "name":f"{zhi_a}{zhi_b}冲", "multiplier":mult, "has_yin_hua":has_yh,
                    "detail":f"{zhi_a}与{zhi_b}辰戌丑未冲({'有引化' if has_yh else '无引化'}×{mult}倍)"}
        return {"type":"六冲", "name":f"{zhi_a}{zhi_b}冲", "multiplier":ENERGY_MULTIPLIER["六冲"], "has_yin_hua":False,
                "detail":f"{zhi_a}与{zhi_b}相冲({wx_a}冲{wx_b})"}
    # 六合
    if LIU_HE.get(zhi_a) == zhi_b:
        he_wx = _get_liu_he_wx(zhi_a, zhi_b)
        has_yh = _has_yin_hua(he_wx, tian_gan_list) if he_wx and tian_gan_list else False
        mult = ENERGY_MULTIPLIER["六合有引化"] if has_yh else ENERGY_MULTIPLIER["六合无引化"]
        return {"type":"六合", "name":f"{zhi_a}{zhi_b}合", "multiplier":mult, "has_yin_hua":has_yh,
                "detail":f"{zhi_a}与{zhi_b}六合({'有引化' if has_yh else '无引化'}×{mult}倍)"}
    # 六害
    if LIU_HAI.get(zhi_a) == zhi_b:
        return {"type":"六害", "name":f"{zhi_a}{zhi_b}害", "multiplier":ENERGY_MULTIPLIER["六害"], "has_yin_hua":False,
                "detail":f"{zhi_a}与{zhi_b}相害"}
    # 六破
    if LIU_PO.get(zhi_a) == zhi_b:
        return {"type":"六破", "name":f"{zhi_a}{zhi_b}破", "multiplier":ENERGY_MULTIPLIER["六破"], "has_yin_hua":False,
                "detail":f"{zhi_a}与{zhi_b}相破"}
    # 三刑（含子卯刑特殊处理）
    for pair_key, (z1, z2) in [("子卯",("子","卯")),("寅巳",("寅","巳")),("巳申",("巳","申")),
                                ("丑未",("丑","未")),("未戌",("未","戌")),("丑戌",("丑","戌"))]:
        if {zhi_a, zhi_b} == {z1, z2}:
            if pair_key == "子卯":
                # 子卯刑不加强能量
                return {"type":"子卯刑", "name":f"{zhi_a}{zhi_b}刑", "multiplier":0, "has_yin_hua":False,
                        "detail":f"{zhi_a}与{zhi_b}子卯刑（无礼之刑）— 不加强能量"}
            xing_name = "无恩之刑" if "寅" in pair_key or "巳" in pair_key or "申" in pair_key else "恃势之刑"
            yh_wx = "土" if "丑" in pair_key or "未" in pair_key or "戌" in pair_key else "水"
            has_yh = _has_yin_hua(yh_wx, tian_gan_list) if tian_gan_list else False
            mult = ENERGY_MULTIPLIER["三刑有引化"] if has_yh else ENERGY_MULTIPLIER["三刑无引化"]
            return {"type":"三刑", "name":f"{zhi_a}{zhi_b}刑", "multiplier":mult, "has_yin_hua":has_yh,
                    "detail":f"{zhi_a}与{zhi_b}相刑({xing_name}) {'有引化' if has_yh else '无引化'}×{mult}倍"}
    # 自刑
    if zhi_a == zhi_b and zhi_a in ZI_XING:
        has_yh = _has_yin_hua(DI_ZHI_WU_XING.get(zhi_a, "土"), tian_gan_list) if tian_gan_list else False
        mult = ENERGY_MULTIPLIER["自刑有引化"] if has_yh else ENERGY_MULTIPLIER["自刑无引化"]
        return {"type":"自刑", "name":f"{zhi_a}自刑", "multiplier":mult, "has_yin_hua":has_yh,
                "detail":f"{zhi_a}自刑({'有引化' if has_yh else '无引化'}×{mult}倍)"}
    return {}


def calc_bazi_energy_analysis(ri_gan: str, nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                               tian_gan_list: list = None, xi_shen: list = None) -> dict:
    """八字全局能量分析
    计算四柱地支之间的全部刑冲合害破关系及能量倍数
    返回完整的关系列表和能量汇总（九龙道长体系·有引化/无引化双档）

    伤害分体系（来自金鉴真人_八字命理终极总纲_v1.0）：
      冲=-70, 害=-60, 破=-20, 刑=-50
      三合局: 完整+15, 半合+7
    """
    # 关系类型 → 伤害分映射
    DAMAGE_SCORE = {
        "六冲": -70,
        "六害": -60,
        "六破": -20,
        "三刑": -50,
        "子卯刑": 0,      # 子卯刑无伤害加成
        "自刑": -50,
        "三合局": 15,      # 完整三合正加成
        "半三合": 7,       # 半三合正加成
        "三会局": 0,       # 三会局无额外伤害/加成
        "六合": 0,         # 六合无伤害
        "辰戌丑未冲": -50, # 辰戌丑未冲减半
    }
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    positions = ["年支","月支","日支","时支"]
    results = []
    total_energy = 0
    total_damage = 0

    # 使用新的完整能量倍数引擎计算所有关系
    energy_mult = _calc_energy_multiplier(zhi_list, tian_gan_list or [])
    for rel in energy_mult.get("relationships", []):
        rel_type = rel.get("type", "")
        rel["damage_score"] = DAMAGE_SCORE.get(rel_type, 0)
        # 给关系补充位置信息
        for z in [rel.get("zhi_a", ""), rel.get("zhi_b", "")]:
            if z and z in zhi_list:
                idx = zhi_list.index(z)
                rel_key = f"zhi_{'a' if z == rel.get('zhi_a','') else 'b'}_pos"
                rel[rel_key] = positions[idx]
        results.append(rel)
        total_energy += rel.get("multiplier", 0)
        total_damage += rel.get("damage_score", 0)
    if xi_shen:
        xi_set = set(xi_shen)
        for r in results:
            # 判断关系涉及的五行方向是否喜用
            r["xi_ji"] = "喜" if r.get("multiplier",0) < 0 else "冲"  # placeholder for direction

    return {
        "relationships": results,
        "total_multiplier": total_energy,
        "damage_score": total_damage,
        "count": len(results),
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 身强弱 v7.1
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def calc_shen_qiang_ruo(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                         nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str) -> dict:
    """
    身强弱评分（九龙道长原始规则·三段式）
    规则：
    - 印只在月令本气计分（40分）
    - 比劫在所有位置都计分
    - 燥土规则：未/戌对金日主，火引化时不记分
    - 从弱=0分→恒定50分，从强=>100分→恒定20分
    - 三档：<40身弱, 40-60中和, >60身强
    """
    tian_gan_list = [nian_gan, yue_gan, ri_gan, shi_gan]
    
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_idx = WX_ORDER.index(ri_wx)
    yin_wx = WX_ORDER[(ri_idx+4)%5]   # 生我=印
    bi_wx = WX_ORDER[ri_idx]           # 同我=比劫
    
    score = 0.0
    details = []
    
    # 月令空亡减半（九龙道长：空亡看日柱，月令空亡则40分→20分，藏干同比例减半）
    # File 18原文："空亡主要看日柱的空亡...这个申本来按40分计算的，现在只按20分计算"
    yue_zhi_kong = kong_wang(ri_gan, ri_zhi)
    yue_ling_empty = yue_zhi in yue_zhi_kong
    yue_ling_factor = 0.5 if yue_ling_empty else 1.0
    
    # 1. 月令本气（含燥土规则）
    yz_ben = DI_ZHI_CANG_GAN[yue_zhi][0][0]
    yz_ben_wx = TIAN_GAN_WU_XING[yz_ben]
    yz_effective = is_zao_tu_effective(yue_zhi, ri_gan, tian_gan_list)
    
    yue_ling_score = 0.0
    
    # 月令被克三次→能量衰减（File03 L106：九龙道长"被克三次顶多算弱根"）
    # 检查年/日/时支五行是否克月令五行
    YUE_KE_CYCLE = {"木":"土","土":"水","水":"火","火":"金","金":"木"}  # 克月令的五行
    yue_zhi_wx = DI_ZHI_WU_XING.get(yue_zhi, "")
    ke_wx = YUE_KE_CYCLE.get(yue_zhi_wx, "")  # 什么样的五行会克月令
    ke_count = 0
    for other_zhi in [nian_zhi, ri_zhi, shi_zhi]:
        if other_zhi and other_zhi != yue_zhi:
            if DI_ZHI_WU_XING.get(other_zhi, "") == ke_wx:
                ke_count += 1
    yue_ling_ke_factor = 1.0
    if ke_count >= 3:
        yue_ling_ke_factor = 0.4  # 被克三次→只剩40%能量（≈16分，与File24"仅剩16分"一致）
    elif ke_count == 2:
        yue_ling_ke_factor = 0.7  # 被克两次→受伤，剩70%
    
    yue_ben_score = 0.0
    if yz_ben_wx == yin_wx and yz_effective:
        base = 40
        if yue_ling_empty:
            base = 20
        base = int(round(base * yue_ling_ke_factor))
        yue_ben_score += base; score += base
        detail = f"月令本气印({yz_ben}) +{base}"
        if yue_ling_empty:
            detail += "（空亡减半）"
        if yue_ling_ke_factor < 1.0:
            detail += f"（被克{ke_count}次，能量衰减）"
        details.append(detail)
    elif yz_ben_wx == bi_wx and yz_effective:
        base = 40
        if yue_ling_empty:
            base = 20
        base = int(round(base * yue_ling_ke_factor))
        yue_ben_score += base; score += base
        detail = f"月令本气比劫({yz_ben}) +{base}"
        if yue_ling_empty:
            detail += "（空亡减半）"
        if yue_ling_ke_factor < 1.0:
            detail += f"（被克{ke_count}次，能量衰减）"
        details.append(detail)
    
    # 2. 月令中/余气（比劫才计分，印不计）
    for cg, wt in DI_ZHI_CANG_GAN[yue_zhi]:
        if TIAN_GAN_WU_XING[cg] == bi_wx and cg != yz_ben:
            p = 40 * wt / 100
            if yue_ling_empty:
                p = p / 2
            p = p * yue_ling_ke_factor
            yue_ling_score += p
            score += p
            detail = f"月令藏干比劫({cg}) +{p:.1f}"
            if yue_ling_empty:
                detail += "（空亡减半）"
            if yue_ling_ke_factor < 1.0:
                detail += "（被克衰减）"
            details.append(detail)
    
    yue_ling_score += yue_ben_score
    
    # 3. 天干比劫（日干不计）
    for pos, gan, pts in [('年干',nian_gan,8),('月干',yue_gan,12),('时干',shi_gan,12)]:
        if TIAN_GAN_WU_XING[gan] == bi_wx:
            score += pts; details.append(f"{pos}比劫({gan}) +{pts}")
    
    # 4. 年/日/时支藏干比劫（含燥土过滤）
    for pos, zhi, base in [('年支',nian_zhi,4),('日支',ri_zhi,12),('时支',shi_zhi,12)]:
        effective = is_zao_tu_effective(zhi, ri_gan, tian_gan_list)
        for cg, wt in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cg] == bi_wx and effective:
                p = round(base * wt / 100, 1)
                if p > 0:
                    score += p; details.append(f"{pos}藏干比劫({cg}) +{p:.1f}")
    
    # 从格 + 三段式（九龙道长：<40身弱, 40-60中和, >60身强）
    if score <= 0:
        return {"score": 50.0, "level": "从弱", "details": details}
    if score > 100:
        return {"score": 20.0, "level": "从强", "details": details}
    if score > 60:
        return {"score": round(score,1), "level": "身强", "details": details}
    if score >= 40:
        return {"score": round(score,1), "level": "中和", "details": details}
    return {"score": round(score,1), "level": "身弱", "details": details}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 格局 v7.0（透干定格局·比劫不入格局）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _detect_top10_ge_ju(ri_gan: str,
                        nian_gan: str, yue_gan: str, shi_gan: str,
                        nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                        sqr_level: str = "", zhuan_wang_flag: bool = False,
                        is_hua_qi: bool = False) -> dict:
    """
    检测十大格局（金鉴真人_八字最好的格局排名）
    返回 {"ge_ju": str, "rank": int|None, "rank_name": str|None, "details": list}
    """
    details = []
    ge_ju_base = None  # 基础格局名（正八格名称）
    rank = None
    rank_name = None

    # 构建 十神列表（四柱天干）
    tian_gan_list = [nian_gan, yue_gan, shi_gan]
    all_ss = set()
    # 天干十神
    for tg in tian_gan_list:
        if tg:
            all_ss.add(shi_shen(ri_gan, tg, mark_xiao=False))
    # 月支+日支+时支本气十神
    for zhi in [yue_zhi, ri_zhi, shi_zhi]:
        cg = DI_ZHI_CANG_GAN[zhi][0][0]
        all_ss.add(shi_shen(ri_gan, cg, mark_xiao=False))

    has_shi_shen = "食神" in all_ss
    has_shang_guan = "伤官" in all_ss
    has_zheng_yin = "正印" in all_ss
    has_pian_yin = "偏印" in all_ss
    has_zheng_guan = "正官" in all_ss
    has_qi_sha = "七杀" in all_ss
    has_zheng_cai = "正财" in all_ss
    has_pian_cai = "偏财" in all_ss
    has_yin = has_zheng_yin or has_pian_yin
    has_pian_yin_only = has_pian_yin and not has_zheng_yin
    has_guan_sha = has_zheng_guan or has_qi_sha
    has_cai = has_zheng_cai or has_pian_cai
    has_shi_shang = has_shi_shen or has_shang_guan

    # 天干五行计数（用于木火通明）
    gan_wx_count = {"木": 0, "火": 0, "水": 0, "金": 0, "土": 0}
    for tg in tian_gan_list:
        if tg:
            gan_wx_count[TIAN_GAN_WU_XING[tg]] += 1

    # 地支五行计数
    zhi_wx_count = {"木": 0, "火": 0, "水": 0, "金": 0, "土": 0}
    for zhi in [nian_zhi, yue_zhi, ri_zhi, shi_zhi]:
        zhi_wx_count[DI_ZHI_WU_XING[zhi]] += 1

    # 四柱地支列表
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    
    # 月令本气十神（用于判断格局是否与月令相关）
    yue_ben_qi = DI_ZHI_CANG_GAN[yue_zhi][0][0]
    yue_ben_ss = shi_shen(ri_gan, yue_ben_qi, mark_xiao=False)
    # 月令是否为明确独立主格（不覆盖此格）
    YUE_DU_LI_GE = ("正印", "偏印", "正官", "七杀", "正财", "偏财", "食神", "伤官")
    yue_is_du_li = yue_ben_ss in YUE_DU_LI_GE
    
    # ════════════════════════════════════════════
    # 检测逻辑（按九龙道长排名从高到低：高排名优先匹配）
    # 参考：九龙道长_八字最好的格局排名_20260627.md
    # ════════════════════════════════════════════

    # ── 第1名：食神制杀格/杀印相生 ──
    if has_shi_shen and has_qi_sha:
        rank = 1
        rank_name = "食神制杀格/杀印相生"
        details.append("食神+七杀同时出现，食神制杀格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}
    if has_yin and has_qi_sha:
        rank = 1
        rank_name = "食神制杀格/杀印相生"
        details.append("印星+七杀同时出现，杀印相生格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第2名：伤官配印格（v7.2：必须正印，偏印不算）──
    # 九龙道长原文：伤官配正印（非偏印），身弱伤官为忌、印为喜用
    if has_shang_guan and has_zheng_yin and not has_pian_yin_only:
        rank = 2
        rank_name = "伤官配印格"
        details.append("伤官+正印同时出现（非偏印），伤官配印格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第3名：财官双美格（v7.2：月令本气相关，且月令非独立主格）──
    if has_guan_sha and has_cai and not yue_is_du_li:
        yue_aligned = yue_ben_ss in ("正官", "七杀", "正财", "偏财", "正印")
        if yue_aligned:
            rank = 3
            rank_name = "财官双美格"
            details.append("官杀+财星同时出现且月令相关，财官双美格成立")
            return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第6名：官印相生格 ──
    if has_zheng_guan and has_zheng_yin:
        rank = 6
        rank_name = "官印相生格"
        details.append("正官+正印相生，官印相生格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第7名：食伤生财格（v7.2：月令本气相关，且月令非独立主格）──
    if has_shi_shang and has_cai and not yue_is_du_li:
        yue_aligned = yue_ben_ss in ("食神", "伤官", "正财", "偏财")
        if yue_aligned:
            rank = 7
            rank_name = "食伤生财格"
            details.append("食伤+财星同时出现且月令相关，食伤生财格成立")
            return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第8名：五行流通格（P2新增·九龙道长：无冲克+五行齐全+用神得生扶）──
    liu_tong_result = check_wu_xing_liu_tong(ri_gan, nian_zhi, yue_zhi, ri_zhi, shi_zhi)
    if liu_tong_result.get("is_liu_tong"):
        # 无冲无克+五行齐全+用神得生扶 → 五行流通格（九龙道长原文规则，无额外限制）
        rank = 8
        rank_name = "五行流通格"
        details.append(liu_tong_result["detail"])
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第9名：专旺格 ──
    if zhuan_wang_flag:
        rank = 9
        rank_name = "专旺格"
        details.append("全局五行专旺，构成专旺格")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第10名：木火通明格（P2新增·九龙道长：日主木火+地支汇火局+无水破局）──
    mu_huo_result = check_mu_huo_tong_ming(ri_gan, nian_zhi, yue_zhi, ri_zhi, shi_zhi,
                                           tian_gan_list=(tian_gan_list + [ri_gan]))
    if mu_huo_result.get("is_mu_huo_tong_ming"):
        rank = 10
        rank_name = "木火通明格"
        details.append(mu_huo_result["detail"])
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    return None


def get_ge_ju(ri_gan: str, yue_zhi: str,
              nian_gan: str = "", yue_gan: str = "", shi_gan: str = "",
              nian_zhi: str = "", ri_zhi: str = "", shi_zhi: str = "",
              sqr_level: str = "", zhuan_wang_flag: bool = False,
              is_hua_qi: bool = False) -> dict:
    """
    格局 v7.4：十大格局分级增强版
    ────────────────
    返回格式：
      {"ge_ju": "正官格", "rank": 3, "rank_name": "财官双美", "details": [...]}
      非十大格局时只返回 ge_ju 字段，无 rank
    ────────────────
    判定流程：
      ① 先检测十大格局（特殊组合）
      ② 若非十大格局，走正八格四维判定
    """
    details = []

    # ── 第0步：先检测十大格局 ──
    top10 = _detect_top10_ge_ju(
        ri_gan, nian_gan, yue_gan, shi_gan,
        nian_zhi, yue_zhi, ri_zhi, shi_zhi,
        sqr_level=sqr_level, zhuan_wang_flag=zhuan_wang_flag,
        is_hua_qi=is_hua_qi,
    )
    if top10 is not None:
        return top10

    # ── 非十大格局：走正八格四维判定 ──
    tian_gan = [nian_gan, yue_gan, shi_gan]
    cang_gan_list = DI_ZHI_CANG_GAN[yue_zhi]  # [本气, 中气, 余气]
    
    # ── 第1维：月令本气 ──
    ben_qi_gan = cang_gan_list[0][0]  # 本气对应的天干
    ben_qi_ss = shi_shen(ri_gan, ben_qi_gan)
    if ben_qi_ss in ZHENG_BA_GE:
        gj_name = GE_JU_NAME[ben_qi_ss]
        details.append(f"月令本气{ben_qi_gan}为{ben_qi_ss}，取{gj_name}")
        return {"ge_ju": gj_name, "details": details, "rank": None, "rank_name": None}
    
    # ── 第2维：月干透出 ──
    if yue_gan:
        yue_gan_ss = shi_shen(ri_gan, yue_gan)
        if yue_gan_ss in ZHENG_BA_GE:
            gj_name = GE_JU_NAME[yue_gan_ss]
            details.append(f"月干{yue_gan}为{yue_gan_ss}，取{gj_name}")
            rank_info = GE_JU_RANK_MAP.get(gj_name)
            if rank_info:
                return {"ge_ju": gj_name, "rank": rank_info[0], "rank_name": rank_info[1], "details": details}
            return {"ge_ju": gj_name, "details": details}
    
    # ── 第3维：月令中/余气透干（字符匹配）──
    for cg, wt in cang_gan_list[1:]:  # 跳过本气
        cg_ss = shi_shen(ri_gan, cg)
        if cg_ss not in ZHENG_BA_GE:
            continue
        for tg in tian_gan:
            if tg and tg == cg:  # 字符匹配
                gj_name = GE_JU_NAME[cg_ss]
                details.append(f"月令{cg}({cg_ss})透干{tg}，取{gj_name}")
                rank_info = GE_JU_RANK_MAP.get(gj_name)
                if rank_info:
                    return {"ge_ju": gj_name, "rank": rank_info[0], "rank_name": rank_info[1], "details": details}
                return {"ge_ju": gj_name, "details": details}
    
    # ── 第4维：月令中/余气取首个非比劫 ──
    for cg, wt in cang_gan_list:
        cg_ss = shi_shen(ri_gan, cg)
        if cg_ss in ZHENG_BA_GE:
            gj_name = GE_JU_NAME[cg_ss]
            details.append(f"月令{cg}({cg_ss})取首非比劫，得{gj_name}")
            rank_info = GE_JU_RANK_MAP.get(gj_name)
            if rank_info:
                return {"ge_ju": gj_name, "rank": rank_info[0], "rank_name": rank_info[1], "details": details}
            return {"ge_ju": gj_name, "details": details}
    
    return {"ge_ju": "无正格", "details": []}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 喜用神 / 忌神
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_xi_yong_shen(ri_gan: str, shen_qiang_level: str, shen_qiang_score: float = 50.0) -> dict:
    """喜用神/忌神 v8.0（输出具体五行）
    知识库来源：
    - 金鉴真人八字命理终极总纲
    - 素材17第329~333行·从弱格喜忌
    从弱格：喜克泄耗，但顺序为 官杀(克) > 食伤(泄) > 财星(耗)"""
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_idx = WX_ORDER.index(ri_wx)

    # 从弱格特殊顺序：官杀(克我) > 食伤(我生泄) > 财星(我克耗)
    if shen_qiang_level == "从弱":
        # 克我者 = 官杀
        ke_wo = WX_ORDER[(ri_idx+3)%5]
        # 我生者 = 食伤
        wo_sheng = WX_ORDER[(ri_idx+1)%5]
        # 我克者 = 财星
        wo_ke = WX_ORDER[(ri_idx+2)%5]
        # 生我者 = 印星(忌)
        sheng_wo = WX_ORDER[(ri_idx+4)%5]
        # 同我者 = 比劫(忌)
        tong_wo = WX_ORDER[ri_idx]
        
        xi = [ke_wo, wo_sheng, wo_ke]  # 官杀 > 食伤 > 财星
        ji = [sheng_wo, tong_wo]  # 印 > 比劫
    elif shen_qiang_level in ("身强", "偏强"):
        # 身强/偏强喜克泄耗：财 > 官 > 食伤
        ke_xi = [WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+1)%5]]
        ke_ji = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
        xi, ji = ke_xi, ke_ji
    elif shen_qiang_level == "从强":
        xi = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
        ji = [WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+1)%5]]
    elif shen_qiang_level == "中和":
        if shen_qiang_score >= 50:
            # 偏强喜克泄耗
            xi = [WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+1)%5]]
            ji = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
        else:
            xi = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
            ji = [WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+1)%5]]
    else:  # 身弱 / 偏弱
        xi = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
        ji = [WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+1)%5]]

    return {"xi_shen": xi, "yong_shen": [xi[0]], "ji_shen": ji}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 财星评分 v7.0（含财库）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 财库对应表：日主五行 → 对应的财库地支
# 木日主→丑(金库), 火日主→辰(水库), 土日主→辰(水库),
# 金日主→未(木库), 水日主→戌(火库)

def calc_cai_xing(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                  nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                  sq_level: str = "", sq_score: float = 0.0) -> dict:
    """
    财星评分 v7.0（金鉴真人规则 + 财库计算）
    规则：
    - 只含正偏财，不含劫财
    - 财库：仅日/时柱辰戌丑未才算自己的库
    - 从弱格特殊处理：财得令+40分
    """
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_idx = WX_ORDER.index(ri_wx)
    cai_wx = WX_ORDER[(ri_idx+2)%5]  # 我克者财
    
    score = 0.0
    details = []
    
    # 天干财星
    for pos, gan, pts in [('年干',nian_gan,8),('月干',yue_gan,12),('时干',shi_gan,12)]:
        if TIAN_GAN_WU_XING[gan] == cai_wx:
            score += pts; details.append(f"{pos}({gan})财星 +{pts}")
    
    # 地支财星（藏干按比例），含空亡减半
    gan_map = {'年支': nian_gan, '月令': yue_gan, '日支': ri_gan, '时支': shi_gan}
    for pos, zhi, base in [('年支',nian_zhi,4),('月令',yue_zhi,40),('日支',ri_zhi,12),('时支',shi_zhi,12)]:
        zhi_kong = kong_wang(gan_map[pos], zhi)
        zhi_empty = zhi in zhi_kong
        for cg, wt in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cg] == cai_wx:
                p = base * wt / 100
                if zhi_empty:
                    p = p / 2
                    score += p; details.append(f"{pos}藏干({cg})财星空亡减半 +{p:.1f}")
                else:
                    score += p; details.append(f"{pos}藏干({cg})财星 +{p:.1f}")
    
    # 财库检测（日/时/月柱）
    cai_ku_zhi = CAI_KU_MAP.get(ri_wx, "")
    has_ku = False
    ri_shi_list = [("日支", ri_zhi), ("时支", shi_zhi), ("月支", yue_zhi)]
    found_ku = ""
    for pos_name, zhi in ri_shi_list:
        if zhi == cai_ku_zhi:
            has_ku = True
            found_ku = f"{pos_name}{zhi}"
            break
        # 辰戌丑未也可能是其他库
        if zhi in KU_ZHI:
            # 检查藏干是否有财星
            for cg, wt in DI_ZHI_CANG_GAN[zhi]:
                if TIAN_GAN_WU_XING[cg] == cai_wx:
                    has_ku = True
                    found_ku = f"{pos_name}{zhi}(藏{cg})"
                    break
    
    # ── 从弱格特殊处理 ──
    # 规则（金鉴真人规则·总纲）：
    #   从弱格以克泄耗为喜，财星(我克者)为喜神之一
    #   "财得令+40分"：当从弱格月令生财（月令的五行能生财星五行）时，
    #   财星额外+40分，表示财星得令而旺
    #
    # 设计决策：
    #   calc_cai_xing 仅反映原局财星原始分数（不含从弱加成），
    #   确保原局财星强弱判断独立于身强弱状态
    #   从弱格的额外加分（+40分逻辑）在 calc_cai_fu_deng_ji 中处理，
    #   见该函数的"从弱格+财旺→亿万级"分支：
    #     - 财旺(cai_strong=True, score≥40)时直接映射大富(70-90分)
    #     - 财弱时按比例映射小富区间(12-36分)
    #   此处仅记录从弱标记，供调用方参考
    if sq_level == "从弱":
        details.append("从弱格：财星原局分数如实计算，额外加成由calc_cai_fu_deng_ji处理（财得令+40→大富基准70分）")
    
    # 财富五级（九龙道长原始规则：身强财旺/身强财弱/身弱财旺/身弱财弱四级）
    # 大富：身强+财旺(score≥40)
    # 中富：身强+财弱(score<40) 或 中和+财旺
    # 小富：身弱+财旺 或 身弱+财弱 或 中和+财弱
    # 贫穷：身弱+无财(score≈0)
    cai_strong = score >= 40
    if sq_level == "从弱":
        level = "大富" if cai_strong else "小富"
    elif sq_level == "身强":
        level = "大富" if cai_strong else "中富"
    elif sq_level == "中和":
        level = "中富" if cai_strong else "小富"
    else:  # 身弱
        level = "小富" if score >= 12 else "贫穷"
    
    return {
        "score": round(score,1),
        "wealth_level": level,
        "details": details,
        "has_ku": has_ku,
        "cai_ku": found_ku,
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 大运计算
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calc_da_yun(nian_gan: str, nian_zhi: str, gender: int,
                year: int, month: int, day: int, hour: int, minute: int) -> dict:
    """
    大运计算。
    阳男阴女顺排，阴男阳女逆排。
    起运岁数：3天=1岁，1天=4个月，1时辰=10天。
    顺排：找出生后的下一个节气
    逆排：找出生前的上一个节气
    """
    is_yang = gan_idx(nian_gan) % 2 == 0  # 阳年
    is_shun = (is_yang and gender==1) or (not is_yang and gender==0)
    
    birth = datetime(year, month, day, hour, minute)
    
    if is_shun:
        # 找下一个节气
        next_term = None
        for i in range(12):
            td = get_solar_term_date(year, i)
            td_dt = datetime(td.year, td.month, td.day, 0, 0)
            if td_dt > birth:
                if next_term is None or td_dt < next_term:
                    next_term = td_dt
        if next_term is None:
            next_term = datetime(year+1, 2, 4, 0, 0)  # 下年立春
        days_diff = (next_term - birth).total_seconds() / 86400
        step_sign = 1  # 顺排递增
    else:
        # 找上一个节气
        prev_term = None
        for i in range(11, -1, -1):
            td = get_solar_term_date(year, i)
            td_dt = datetime(td.year, td.month, td.day, 0, 0)
            if td_dt < birth:
                if prev_term is None or td_dt > prev_term:
                    prev_term = td_dt
        if prev_term is None:
            prev_term = datetime(year-1, 12, 7, 0, 0)  # 上年大雪
        days_diff = (birth - prev_term).total_seconds() / 86400
        step_sign = -1  # 逆排递减

    # 起运岁数
    qi_yun = round(days_diff / 3, 2)

    # 月柱干支为基础
    yue_gan, yue_zhi = get_yue_zhu(year, month, day, nian_gan)
    yg_idx = TIAN_GAN.index(yue_gan)
    yz_idx = DI_ZHI.index(yue_zhi)

    # 逆排：从月柱前一个干支开始（step从1开始）
    # 顺排：从月柱下一个干支开始（step从1开始）
    da_yun = []
    for step in range(1, 9):
        gi = (yg_idx + step_sign * step) % 10
        zi = (yz_idx + step_sign * step) % 12
        gz = TIAN_GAN[gi] + DI_ZHI[zi]
        sa = round(qi_yun + (step-1)*10, 1)
        ea = round(qi_yun + step*10, 1)
        da_yun.append({"index":step-1, "gan_zhi":gz, "start_age":sa, "end_age":ea})

    return {"is_shun_pai": is_shun, "qi_yun_age": qi_yun,
            "qi_yun_year": int(qi_yun), "da_yun": da_yun}


def calc_wu_xing_energy(nian_gan: str, yue_gan: str, ri_gan: str, shi_gan: str,
                         nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str) -> dict:
    """计算四柱五行能量分布
    算法：每个天干10分，每个地支本气10分+中气6分+余气3分
    月令权重加倍（总纲规则）
    统计比例并按五行分类，附带过旺过弱预警
    v8.0新增：辰戌丑未五行变性检测 + 生多为克检测 + 恶神能量映射"""
    wu_xing_score = {wx: 0.0 for wx in WX_ORDER}

    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    zhi_positions = ["年支", "月支", "日支", "时支"]

    # 天干4个，每个10分
    for gan_pos, gan in [("年干", nian_gan), ("月干", yue_gan), ("日干", ri_gan), ("时干", shi_gan)]:
        wu_xing_score[TIAN_GAN_WU_XING[gan]] += 10.0

    # ── P0-2: 辰戌丑未五行变性检测 ──
    bian_xing_list = []
    for zhi_pos, zhi in zip(zhi_positions, zhi_list):
        bx = get_bian_xing_wu_xing(zhi, zhi_list)
        if bx:
            rule = BIAN_XING_RULES[zhi]
            bian_xing_list.append({
                "zhi": zhi,
                "position": zhi_pos,
                "original_wx": DI_ZHI_WU_XING[zhi],
                "transformed_wx": bx,
                "title": rule["title"],
                "detail": f"{zhi}({zhi_pos})遇{'+'.join(sorted(rule['trigger']))}→{rule['title']}({bx})，不以{DI_ZHI_WU_XING[zhi]}论"
            })

    # 地支+藏干（月令权重加倍）
    for zhi_pos, zhi in zip(zhi_positions, zhi_list):
        cg_list = DI_ZHI_CANG_GAN[zhi]
        for cg, wt in cg_list:
            wx = TIAN_GAN_WU_XING[cg]
            weight = {100: 10.0, 60: 6.0, 30: 3.0}.get(wt, 0)
            # 月令权重加倍
            if zhi_pos == "月支":
                weight *= 2.0
            wu_xing_score[wx] += weight

    # 标准化到百分比
    total = sum(wu_xing_score.values())
    if total > 0:
        result = {wx: round(score / total * 100, 1) for wx, score in wu_xing_score.items()}
    else:
        result = {wx: 0.0 for wx in WX_ORDER}

    # 过旺过弱预警
    warnings = []
    for wx, pct in result.items():
        if pct > 45:
            warnings.append({"wx": wx, "pct": pct, "level": "过旺", "detail": f"{wx}占比{pct}%，超过45%阈值，五行过旺"})
        elif pct < 5:
            warnings.append({"wx": wx, "pct": pct, "level": "过弱", "detail": f"{wx}占比{pct}%，低于5%阈值，五行过弱"})

    # ── P0-1: 生多为克检测（当某五行能量超过平均值的5倍时，"生"变为"克"）──
    sheng_duo_wei_ke = None
    # 平均值 = 100% / 5 = 20%, 5倍 = 100% (百分比空间不可能)
    # 改用原始分数: 若任一元素原始分 > 5 * (总分/5) = 总分
    # 在百分比等价条件中: pct > 5 * (100-pct)/4  =>  pct > 55.56
    for wx, pct in result.items():
        # 条件: pct > 5 * (100 - pct) / 4
        if pct > 5 * (100 - pct) / 4:
            avg_pct = round(100.0 / 5, 1)
            five_x = round(5 * avg_pct, 1)
            sheng_duo_wei_ke = {
                "wx": wx,
                "detail": f"{wx}能量值{pct}%(平均{avg_pct}%的5倍={five_x}%)，生多为克"
            }
            break  # 只报告最严重的一个

    # ── P0-3: 恶神能量对应表 ──
    # 恶神：七杀、伤官、枭神、劫财
    # 根据不同能量倍数映射具体事件
    E_SHEN_EVENT_MAP = {
        "七杀": [
            (1, 3, "压力小人"),
            (3, 7, "官非手术"),
            (7, 10, "重大灾难"),
            (10, 15, "生死大灾"),
            (20, float('inf'), "牢狱之灾"),
        ],
        "伤官": [
            (1, 3, "口舌是非"),
            (3, 7, "官非失业"),
            (7, 10, "重大官非"),
            (10, 15, "刑狱巨灾"),
        ],
        "枭神": [
            (1, 3, "孤独抑郁"),
            (3, 7, "精神困扰"),
            (7, 10, "严重抑郁"),
            (10, 15, "精神崩溃"),
        ],
        "劫财": [
            (1, 3, "破财小人"),
            (3, 7, "重大破财"),
            (7, 10, "破产危机"),
            (10, 15, "倾家荡产"),
        ],
    }

    # 计算每个恶神的能量倍数
    # 基于天干中该十神的数量 + 地支藏干中该十神的数量 * 权重
    # 用 position score 体系加权
    POS_WEIGHT = {"年干": 8, "月干": 12, "日干": 0, "时干": 12,
                  "年支": 4, "月支": 40, "日支": 12, "时支": 12}

    e_shen_energy = {}
    for gan_pos, gan in [("年干", nian_gan), ("月干", yue_gan), ("日干", ri_gan), ("时干", shi_gan)]:
        ss = _raw_shi_shen(ri_gan, gan)
        if ss in E_SHEN_EVENT_MAP:
            e_shen_energy.setdefault(ss, 0)
            e_shen_energy[ss] += POS_WEIGHT.get(gan_pos, 10)

    for zhi_pos, zhi in zip(zhi_positions, zhi_list):
        for cg, wt in DI_ZHI_CANG_GAN[zhi]:
            ss = _raw_shi_shen(ri_gan, cg)
            if ss in E_SHEN_EVENT_MAP:
                e_shen_energy.setdefault(ss, 0)
                ratio = wt / 100.0
                base = POS_WEIGHT.get(zhi_pos, 12)
                e_shen_energy[ss] += base * ratio

    # 将原始能量值归一化为能量倍数（以10分为基准倍）
    e_shen_map = {}
    for ss_name, raw_energy in sorted(e_shen_energy.items(), key=lambda x: -x[1]):
        # 能量倍数 = 原始能量 / 10 (每10分算1倍)
        multiplier = round(raw_energy / 10.0, 1)
        # 查找事件映射
        events = []
        for lo, hi, event in E_SHEN_EVENT_MAP.get(ss_name, []):
            if lo <= multiplier < hi:
                events.append({"range": f"{lo}-{hi}倍", "event": event})
        if not events and multiplier > 0:
            # 不在定义范围内的，按最近的级别
            if multiplier < 1:
                events.append({"range": "<1倍", "event": "轻微影响"})
            else:
                # 找最后一个
                last_hi = max(h for _, h, _ in E_SHEN_EVENT_MAP.get(ss_name, [(0,1,"")]))
                if multiplier >= last_hi:
                    events.append({"range": f">={last_hi}倍", "event": "极凶"})
        e_shen_map[ss_name] = {
            "raw_energy": round(raw_energy, 1),
            "multiplier": multiplier,
            "events": events,
        }

    # 排序：从高到低
    sorted_result = dict(sorted(result.items(), key=lambda x: -x[1]))
    return {
        "percentages": sorted_result,
        "strongest_wx": list(sorted_result.keys())[0] if sorted_result else "",
        "weakest_wx": list(sorted_result.keys())[-1] if sorted_result else "",
        "warnings": warnings,
        "sheng_duo_wei_ke": sheng_duo_wei_ke,
        "bian_xing": bian_xing_list,  # P0-2: 辰戌丑未五行变性
        "e_shen_energy_map": e_shen_map,  # P0-3: 恶神能量对应表
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 神煞计算（v1.0 完整16种）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 天乙贵人查法表（以年干或日干查四支地支）
# 口诀: 甲戊庚牛羊, 乙己鼠猴乡, 丙丁猪鸡位, 壬癸蛇兔藏, 六辛逢马虎














def _find_san_he_set(zhi):
    """找到包含指定地支的三合局集合"""
    for he_set in SAN_HE:
        if zhi in he_set:
            return he_set
    return None


def calc_shensha(ri_gan, ri_zhi, nian_gan, nian_zhi, yue_gan, yue_zhi, shi_gan, shi_zhi, gender):
    """
    计算四柱神煞（完整16种）
    
    参数：
        ri_gan..shi_zhi: 四柱天干地支
        gender: 0=女, 1=男
    
    返回：
        {"nian": {神煞名: bool, ...}, "yue": {...}, "ri": {...}, "shi": {...}}
    """
    pillars_zhi = {"nian": nian_zhi, "yue": yue_zhi, "ri": ri_zhi, "shi": shi_zhi}
    pillars_gan = {"nian": nian_gan, "yue": yue_gan, "ri": ri_gan, "shi": shi_gan}
    
    result = {pos: {} for pos in ["nian", "yue", "ri", "shi"]}
    
    for pos_name in ["nian", "yue", "ri", "shi"]:
        zhi = pillars_zhi[pos_name]
        gan = pillars_gan[pos_name]
        ss = {}
        
        # ── 1. 天乙贵人（年干或日干查四支地之中） ──
        found = False
        for ref_gan in (nian_gan, ri_gan):
            if zhi in TIAN_YI_GUI_REN.get(ref_gan, set()):
                found = True
                break
        ss["天乙贵人"] = found
        
        # ── 2. 文昌贵人（年干或日干查四支地之中） ──
        found = False
        for ref_gan in (nian_gan, ri_gan):
            if WEN_CHANG.get(ref_gan) == zhi:
                found = True
                break
        ss["文昌贵人"] = found
        
        # ── 3. 天德贵人（月支查四柱天干） ──
        tian_de_gan = TIAN_DE.get(yue_zhi, "")
        ss["天德贵人"] = (gan == tian_de_gan) if tian_de_gan else False
        
        # ── 4. 月德贵人（月支三合局见阳干） ──
        yue_de_gan = ""
        for he_set, g in YUE_DE.items():
            if yue_zhi in he_set:
                yue_de_gan = g
                break
        ss["月德贵人"] = (gan == yue_de_gan) if yue_de_gan else False
        
        # ── 5. 太极贵人（年干或日干查四支地之中） ──
        found = False
        for ref_gan in (nian_gan, ri_gan):
            if zhi in TAI_JI.get(ref_gan, set()):
                found = True
                break
        ss["太极贵人"] = found
        
        # ── 6. 福星贵人（年干或日干查四支地之中） ──
        found = False
        for ref_gan in (nian_gan, ri_gan):
            if zhi in FU_XING.get(ref_gan, set()):
                found = True
                break
        ss["福星贵人"] = found
        
        # ── 7. 禄神（日干之临官位） ──
        ss["禄神"] = (zhi == LU_SHEN.get(ri_gan, ""))
        
        # ── 8. 华盖（年支或日支查四支地之中） ──
        found = False
        for ref_zhi in (nian_zhi, ri_zhi):
            he_set = _find_san_he_set(ref_zhi)
            if he_set and zhi == HUA_GAI.get(he_set, ""):
                found = True
                break
        ss["华盖"] = found
        
        # ── 9. 桃花/咸池（年支或日支查四支地之中） ──
        found = False
        for ref_zhi in (nian_zhi, ri_zhi):
            he_set = _find_san_he_set(ref_zhi)
            if he_set and zhi == TAO_HUA.get(he_set, ""):
                found = True
                break
        ss["桃花"] = found
        
        # ── 10. 驿马（年支或日支查四支地之中） ──
        found = False
        for ref_zhi in (nian_zhi, ri_zhi):
            he_set = _find_san_he_set(ref_zhi)
            if he_set and zhi == YI_MA.get(he_set, ""):
                found = True
                break
        ss["驿马"] = found
        
        # ── 11. 将星（年支或日支查四支地之中） ──
        found = False
        for ref_zhi in (nian_zhi, ri_zhi):
            he_set = _find_san_he_set(ref_zhi)
            if he_set and zhi == JIANG_XING.get(he_set, ""):
                found = True
                break
        ss["将星"] = found
        
        # ── 12. 灾煞（以年支查四支地支） ──
        he_set = _find_san_he_set(nian_zhi)
        ss["灾煞"] = (he_set and zhi == ZAI_SHA.get(he_set, "")) or False
        
        # ── 13. 血刃（以日干查四支地支） ──
        ss["血刃"] = (zhi == XUE_REN.get(ri_gan, ""))
        
        # ── 14. 孤辰寡宿（以年支查四支地支） ──
        found_gu = False
        found_gua = False
        for he_set, (gu, gua) in GU_CHEN_GUA_SU.items():
            if nian_zhi in he_set:
                found_gu = (zhi == gu)
                found_gua = (zhi == gua)
                break
        ss["孤辰"] = found_gu
        ss["寡宿"] = found_gua
        
        # ── 15. 红鸾（以年支查四支地支） ──
        ss["红鸾"] = (zhi == HONG_LUAN.get(nian_zhi, ""))
        
        # ── 16. 天喜（以年支查四支地支） ──
        ss["天喜"] = (zhi == TIAN_XI.get(nian_zhi, ""))
        
        result[pos_name] = ss
    
    return result


def calc_all_shensha_with_positions(ri_gan, ri_zhi, nian_gan, nian_zhi, yue_gan, yue_zhi, shi_gan, shi_zhi, gender):
    """
    返回所有神煞的扁平列表，带位置信息，供报告生成器使用。
    
    返回格式：
    [
        {"name": "天乙贵人", "position": "nian", "position_label": "年柱"},
        {"name": "桃花", "position": "ri", "position_label": "日柱"},
        ...
    ]
    """
    shensha_dict = calc_shensha(ri_gan, ri_zhi, nian_gan, nian_zhi, yue_gan, yue_zhi, shi_gan, shi_zhi, gender)
    pos_labels = {"nian": "年柱", "yue": "月柱", "ri": "日柱", "shi": "时柱"}
    result = []
    for pos in ["nian", "yue", "ri", "shi"]:
        for name, present in shensha_dict[pos].items():
            if present:
                result.append({
                    "name": name,
                    "position": pos,
                    "position_label": pos_labels[pos]
                })
    return result


def calc_shensha_summary(ri_gan, ri_zhi, nian_gan, nian_zhi, yue_gan, yue_zhi, shi_gan, shi_zhi, gender):
    """
    返回神煞摘要统计。
    
    返回格式：
    {
        "auspicious_count": N,        # 吉神数量
        "neutral_count": N,           # 中性神煞数量
        "inauspicious_count": N,      # 凶神数量
        "marriage_count": N,          # 婚姻类神煞数量
        "total": N,                   # 总计
        "auspicious_list": [...],     # 吉神列表(带位置)
        "inauspicious_list": [...],   # 凶神列表(带位置)
    }
    """
    shensha_dict = calc_shensha(ri_gan, ri_zhi, nian_gan, nian_zhi, yue_gan, yue_zhi, shi_gan, shi_zhi, gender)
    
    # 分类定义
    auspicious = {"天乙贵人","文昌贵人","天德贵人","月德贵人","太极贵人","福星贵人","禄神"}
    neutral = {"华盖","桃花","驿马","将星"}
    inauspicious = {"灾煞","血刃","孤辰","寡宿"}
    marriage = {"红鸾","天喜"}
    
    pos_labels = {"nian": "年柱", "yue": "月柱", "ri": "日柱", "shi": "时柱"}
    
    auspicious_list = []
    inauspicious_list = []
    total = 0
    
    for pos in ["nian", "yue", "ri", "shi"]:
        for name, present in shensha_dict[pos].items():
            if present:
                total += 1
                item = {"name": name, "position": pos, "position_label": pos_labels[pos]}
                if name in auspicious:
                    auspicious_list.append(item)
                elif name in inauspicious:
                    inauspicious_list.append(item)
    
    return {
        "auspicious_count": len(auspicious_list),
        "neutral_count": sum(1 for pos in shensha_dict for n, p in shensha_dict[pos].items() if p and n in neutral),
        "inauspicious_count": len(inauspicious_list),
        "marriage_count": sum(1 for pos in shensha_dict for n, p in shensha_dict[pos].items() if p and n in marriage),
        "total": total,
        "auspicious_list": auspicious_list,
        "inauspicious_list": inauspicious_list,
    }



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 调候用神
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 调候用神逻辑（知识库理论）：
# 夏天(巳午未月)生于火旺之时，需水调候润局
# 冬天(亥子丑月)生于水旺之时，需火调候暖局
# 春木秋金亦各有调候需求

def calc_tiao_hou(ri_gan: str, yue_zhi: str, tian_gan_list: list) -> dict:
    """计算调候用神
    返回: {"has_tiao_hou": bool, "need": str, "tiao_hou_wx": str, "detail": str}"""
    month_need = TIAO_HOU_MONTHS.get(yue_zhi)
    if not month_need:
        return {"has_tiao_hou": False, "need": "", "tiao_hou_wx": "", "detail": ""}
    
    need_wx = month_need["wx"]
    # 检查天干是否有调候五行
    has = any(TIAN_GAN_WU_XING[g] == need_wx for g in tian_gan_list if g)
    # 检查地支藏干
    tian_gan_list_clean = [g for g in tian_gan_list if g]
    
    return {
        "has_tiao_hou": has,
        "need": month_need["tiao_hou"],
        "tiao_hou_wx": need_wx,
        "detail": month_need["reason"] + (f"，天干有{need_wx}调候得力" if has else f"，天干无{need_wx}调候欠缺"),
    }


def calc_tong_guan(ri_gan: str, wx_scores: dict) -> list:
    """计算通关用神
    当两行相战时（两行得分接近且都>25%），需中间五行通关
    返回通关关系列表"""
    results = []
    sorted_wx = sorted(wx_scores.items(), key=lambda x: -x[1])
    if len(sorted_wx) < 2:
        return results
    
    top1_wx, top1_score = sorted_wx[0]
    top2_wx, top2_score = sorted_wx[1]
    
    # 两行相战：前两名得分>25%且差距<10%
    if top1_score > 25 and top2_score > 25 and abs(top1_score - top2_score) < 10:
        tong_guan_map = {
            ("木", "土"): "火", ("土", "木"): "火",
            ("火", "金"): "土", ("金", "火"): "土",
            ("土", "水"): "金", ("水", "土"): "金",
            ("金", "木"): "水", ("木", "金"): "水",
            ("水", "火"): "木", ("火", "水"): "木",
        }
        tg_wx = tong_guan_map.get((top1_wx, top2_wx))
        if tg_wx:
            ri_wx = TIAN_GAN_WU_XING[ri_gan]
            xi_shen_list = []
            # 日主五行若能通关则优先
            if ri_wx == tg_wx:
                xi_shen_list.append(ri_wx)
            else:
                xi_shen_list.append(tg_wx)
            results.append({
                "between": f"{top1_wx}与{top2_wx}相战",
                "tong_guan_wx": tg_wx,
                "xi_shen": xi_shen_list,
                "detail": f"{top1_wx}{top2_wx}两行相战，需{tg_wx}通关为用",
            })
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 假旺真弱排查
# 假旺真弱（check_jia_wang_zhen_ruo）已于 v9.0 删除
# 原因：该算法存在数据污染问题——假旺真弱的判断依赖身强弱评分，但身强弱评分
# 已通过三段式（月令/天干/地支）完整刻画强弱，假旺真弱修正造成了过度降级和
# 循环依赖，反而污染了最终的身强弱结论。引擎层只负责数据计算，不留存有争议的修正逻辑。


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 专旺格 & 化气格
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def check_zhuan_wang_ge(ri_gan: str, wx_scores: dict, sqr_score: float,
                        tian_gan_list: list = None, zhi_list: list = None) -> dict:
    """检查专旺格（严格版P2）
    要求：① 全局同一五行占比>85%
          ② 天干无官杀/财星透出（破格）
          ③ 地支无六冲
    返回 {"is_zhuan_wang": bool, "name": str, "wx": str, "detail": str}"""
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_pct = wx_scores.get(ri_wx, 0)
    
    # 硬门槛：占比>85%（比旧版70%更严格）
    if ri_pct < 85:
        return {"is_zhuan_wang": False, "name": "", "wx": "", "detail": ""}
    
    ri_idx = WX_ORDER.index(ri_wx)
    ke_wo_wx = WX_ORDER[(ri_idx + 3) % 5]  # 克我→官杀五行
    wo_ke_wx = WX_ORDER[(ri_idx + 2) % 5]  # 我克→财星五行
    
    # 检查天干无官杀/财星透出
    if tian_gan_list:
        for tg in tian_gan_list:
            if tg:
                tg_wx = TIAN_GAN_WU_XING[tg]
                if tg_wx == ke_wo_wx or tg_wx == wo_ke_wx:
                    return {
                        "is_zhuan_wang": False, "name": "", "wx": "",
                        "detail": f"天干{tg}为{'官杀' if tg_wx == ke_wo_wx else '财星'}透出，破格",
                    }
    
    # 检查地支无六冲
    if zhi_list and len(zhi_list) >= 2:
        for i, z1 in enumerate(zhi_list):
            for z2 in zhi_list[i + 1:]:
                if LIU_CHONG.get(z1) == z2 or LIU_CHONG.get(z2) == z1:
                    return {
                        "is_zhuan_wang": False, "name": "", "wx": "",
                        "detail": f"地支{z1}与{z2}六冲，破格",
                    }
    
    name = ZHUAN_WANG_NAMES.get(ri_wx, "")
    return {
        "is_zhuan_wang": True,
        "name": name,
        "wx": ri_wx,
        "detail": f"日主五行{ri_wx}占比{ri_pct}%，无破格，构成{name}，格局特殊",
    }


# 天干五合化气：甲己合土、乙庚合金、丙辛合水、丁壬合木、戊癸合火

def check_hua_qi_ge(ri_gan: str, tian_gan_list: list, yue_zhi: str,
                    zhi_list: list = None) -> dict:
    """检查化气格（P2增强版）
    天干五合成功化气 = 合化 + 月令生助 + 化气五行有根
    返回 {"is_hua_qi": bool, "hua_qi_wx": str, "detail": str}"""
    for i, g_a in enumerate(tian_gan_list):
        for g_b in tian_gan_list[i+1:]:
            if not g_a or not g_b:
                continue
            pair = (g_a, g_b)
            if pair in HUA_QI_MAP:
                hua_wx = HUA_QI_MAP[pair]
                # 月令生助化气五行
                yue_wx = DI_ZHI_WU_XING[yue_zhi]
                if WX_SHENG.get(yue_wx) == hua_wx or yue_wx == hua_wx:
                    # 有根检查：化气五行在地支有藏干支撑
                    if zhi_list:
                        has_root = False
                        for zhi in zhi_list:
                            if not zhi:
                                continue
                            for cg, _ in DI_ZHI_CANG_GAN[zhi]:
                                if TIAN_GAN_WU_XING.get(cg) == hua_wx:
                                    has_root = True
                                    break
                            if has_root:
                                break
                        if not has_root:
                            continue  # 无根，不视为化气格
                    return {
                        "is_hua_qi": True,
                        "hua_qi_wx": hua_wx,
                        "detail": f"{g_a}{g_b}合化{hua_wx}成功，月令{yue_zhi}生助化气，化气有根",
                    }
    return {"is_hua_qi": False, "hua_qi_wx": "", "detail": ""}


# ── 五行流通格（P2新增）──
def check_wu_xing_liu_tong(ri_gan: str,
                           nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                           wx_pcts: dict = None) -> dict:
    """检查五行流通格（九龙道长原始规则）
    理论：八字无冲无克，五行循环相生，用神得生扶
    来源：九龙道长_八字最好的格局排名_20260627.md
    返回 {"is_liu_tong": bool, "detail": str}"""
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]

    # 1. 检查无六冲
    for i, z1 in enumerate(zhi_list):
        for z2 in zhi_list[i + 1:]:
            if LIU_CHONG.get(z1) == z2 or LIU_CHONG.get(z2) == z1:
                return {
                    "is_liu_tong": False,
                    "detail": f"地支{z1}与{z2}六冲，不构成五行流通格",
                }

    # 2. 检查无三刑（寅巳申/丑未戌/子卯刑）
    san_xing_results = check_san_xing(zhi_list)
    if san_xing_results:
        xing_detail = "、".join([r[0] for r in san_xing_results])
        return {
            "is_liu_tong": False,
            "detail": f"地支存在{xing_detail}，不构成五行流通格",
        }

    # 3. 检查无六害
    liu_hai_pairs = check_liu_hai(zhi_list)
    if liu_hai_pairs:
        hai_detail = "、".join([f"{p[0]}{p[1]}害" for p in liu_hai_pairs])
        return {
            "is_liu_tong": False,
            "detail": f"地支存在{hai_detail}，不构成五行流通格",
        }

    # 4. 检查无六破
    liu_po_pairs = check_liu_po(zhi_list)
    if liu_po_pairs:
        po_detail = "、".join([f"{p[0]}{p[1]}破" for p in liu_po_pairs])
        return {
            "is_liu_tong": False,
            "detail": f"地支存在{po_detail}，不构成五行流通格",
        }

    # 5. 检查五行齐全（每种五行都有占比>0）
    if wx_pcts:
        zero_wxs = [wx for wx, pct in wx_pcts.items() if pct <= 0]
        if zero_wxs:
            return {
                "is_liu_tong": False,
                "detail": f"缺少{''.join(zero_wxs)}，不构成五行流通格",
            }

    return {
        "is_liu_tong": True,
        "detail": "八字无冲无克，五行齐全且循环流通，用神得生扶，五行流通格成立",
    }


# ── 木火通明格（P2新增）──
def check_mu_huo_tong_ming(ri_gan: str,
                           nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                           tian_gan_list: list = None) -> dict:
    """检查木火通明格
    理论：日主为木或火 + 地支汇火局 + 天干无水破局
    返回 {"is_mu_huo_tong_ming": bool, "detail": str}"""
    ri_wx = TIAN_GAN_WU_XING[ri_gan]

    # 1. 日主为木或火
    if ri_wx not in ("木", "火"):
        return {"is_mu_huo_tong_ming": False, "detail": f"日主为{ri_wx}，不属木火"}

    # 2. 天干无水破局
    if tian_gan_list:
        for tg in tian_gan_list:
            if tg and TIAN_GAN_WU_XING.get(tg) == "水":
                return {
                    "is_mu_huo_tong_ming": False,
                    "detail": f"天干{tg}为水透出破局，不构成木火通明格",
                }

    # 3. 地支汇火局（三合/三会火局或至少两个火地支）
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    zhi_set = frozenset(zhi_list)
    # 三合火局
    huo_ju = frozenset(["寅", "午", "戌"])
    # 三会火局
    huo_hui = frozenset(["巳", "午", "未"])
    if not (huo_ju.issubset(zhi_set) or huo_hui.issubset(zhi_set)):
        # 退一步：至少两个火地支
        fire_zhi_count = sum(1 for z in zhi_list if DI_ZHI_WU_XING.get(z) == "火")
        if fire_zhi_count < 2:
            return {
                "is_mu_huo_tong_ming": False,
                "detail": "地支无火局或火势不足，不构成木火通明格",
            }

    return {
        "is_mu_huo_tong_ming": True,
        "detail": f"日主为{ri_wx}，地支汇火局，天干无水破局，木火通明格成立",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 大运吉凶判定表
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 大运吉凶表（知识库理论：身强/身弱各十神的影响）
# 身强：喜克泄耗（官杀/财/食伤）→吉；忌生扶（印/比劫）→凶
# 身弱：喜生扶（印/比劫）→吉；忌克泄耗（官杀/财/食伤）→凶

def calc_da_yun_ji_xiong(da_yun_list: list, ri_gan: str, sqr_level: str,
                          xi_shen: list = None, ji_shen: list = None,
                          nian_zhi: str = "", ri_zhi: str = "",
                          yue_zhi: str = "", shi_zhi: str = "") -> list:
    """大运评分 v3.0 — 金鉴真人评分法（回归理论本源）
    公式：总分 = 人生阶段基础(0-7) + 大运赋能(0-3)，满分10分
    大运赋能 = 喜用神效应 + 十神交互效应 + 刑冲合害效应"""
    WX_MAP = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土",
              "庚":"金","辛":"金","壬":"水","癸":"水"}
    xi = xi_shen or []
    ji = ji_shen or []
    liu_chong = {"子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥",
                 "午":"子","未":"丑","申":"寅","酉":"卯","戌":"辰","亥":"巳"}
    
    def zhi_wx(z):
        return {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土",
                "巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}.get(z, "")
    
    result = []
    for yun in da_yun_list:
        gz = yun.get("gan_zhi", "")
        if len(gz) < 2:
            result.append({**yun, "ji_xiong": "平", "score": 5.0, "gan_ss": "", "detail": "未知"})
            continue
        gan, zhi = gz[0], gz[1]
        gan_wx = WX_MAP.get(gan, "")
        gan_ss = shi_shen(ri_gan, gan) if gan and ri_gan else ""
        zwx = zhi_wx(zhi)
        start_age = yun.get("start_age", 50)
        
        details = []
        
        # ═══════════════════════════════════════════════
        # 第一步：人生阶段基础分 (0-7)
        # 金鉴真人规则：每步大运有先天阶段基础值
        # ═══════════════════════════════════════════════
        age = (start_age + (start_age + 10)) / 2  # 运中年龄
        if age < 20:
            base = 4.5  # 少年期：学业打基础
        elif age < 30:
            base = 5.0  # 青年期：进入社会
        elif age < 40:
            base = 5.5  # 黄金期：职场上升
        elif age < 50:
            base = 4.5  # 中年早期：压力最大
        elif age < 60:
            base = 5.5  # 中年鼎盛：人生巅峰期
        elif age < 70:
            base = 3.5  # 晚年初期：退休过渡
        elif age < 80:
            base = 3.0  # 晚年中期
        else:
            base = 2.5  # 晚年后期
        
        # ═══════════════════════════════════════════════
        # 第二步：大运赋能 (0-3)
        # 九龙道长规则：前五年天干70%+地支30%，后五年地支70%+天干30%
        # ═══════════════════════════════════════════════
        bonus = 1.5  # 默认中性
        
        # 2a. 喜用神效应
        gan_is_xi = gan_wx in xi
        gan_is_ji = gan_wx in ji
        zhi_is_xi = zwx in xi
        zhi_is_ji = zwx in ji
        
        # 分别计算天干和地支的赋能
        gan_bonus = 0.0
        zhi_bonus = 0.0
        
        if gan_is_xi:
            gan_bonus += 0.5
            zhi_bonus += 0.3  # 天干喜用也给地支轻微正向
            details.append(f"天干{gan}=喜用→天干+0.5/地支+0.3")
        elif gan_is_ji:
            gan_bonus -= 0.3
            zhi_bonus -= 0.2
            details.append(f"天干{gan}=忌神→天干-0.3/地支-0.2")
        
        if zhi_is_xi:
            zhi_bonus += 0.3
            details.append(f"地支{zhi}=喜用→地支+0.3")
        elif zhi_is_ji:
            zhi_bonus -= 0.2
            details.append(f"地支{zhi}=忌神→地支-0.2")
        
        # 2b. 十神交互效应（金鉴真人核心规则）
        # 伤官见官 → 减分
        if gan_ss == "伤官":
            if shi_shen(ri_gan, "癸") == "正官" or shi_shen(ri_gan, "壬") == "七杀":
                gan_bonus -= 0.5; zhi_bonus -= 0.3
                details.append("伤官见官→前五年-0.5/后五年-0.3")
        
        # 食神制杀 → 加分
        if gan_ss == "七杀":
            zhi_cang = DI_ZHI_CANG_GAN.get(zhi, [])
            zhi_has_shi_shen = any(shi_shen(ri_gan, cg) in ("食神", "伤官") for cg, _ in zhi_cang)
            if zhi_has_shi_shen:
                zhi_bonus += 0.3
                details.append(f"食神制杀→后五年+0.3")
        
        # 财星生官 → 加分
        if gan_ss in ("正财", "偏财") and zhi_is_xi:
            gan_bonus += 0.2; zhi_bonus += 0.2
            details.append(f"财生官→前五年+0.2/后五年+0.2")
        
        # 2c. 刑冲合害效应
        if nian_zhi and liu_chong.get(zhi) == nian_zhi:
            gan_bonus -= 0.5; zhi_bonus -= 0.3
            details.append(f"冲年柱{nian_zhi}→天干-0.5/地支-0.3")
        
        if ri_zhi and liu_chong.get(zhi) == ri_zhi:
            gan_bonus -= 0.3; zhi_bonus -= 0.3
            details.append(f"冲日柱{ri_zhi}→各-0.3")
        
        # 刑
        liu_xing_pairs = [("丑","戌"),("戌","丑"),("寅","巳"),("巳","寅"),
                          ("巳","申"),("申","巳"),("子","卯"),("卯","子"),
                          ("丑","未"),("未","丑"),("戌","未"),("未","戌")]
        for z1, z2 in liu_xing_pairs:
            if zhi == z1 and (z2 in [nian_zhi, yue_zhi, ri_zhi, shi_zhi]):
                gan_bonus -= 0.2; zhi_bonus -= 0.2
                details.append(f"{z1}{z2}刑→各-0.2")
                break
        
        # 伏吟
        for pos_zhi in [nian_zhi, yue_zhi, ri_zhi, shi_zhi]:
            if zhi == pos_zhi and gan == ri_gan:
                gan_bonus -= 0.2; zhi_bonus -= 0.2
                details.append(f"伏吟日柱→各-0.2")
                break
        
        # cap赋能
        gan_bonus = max(-3.0, min(3.0, gan_bonus))
        zhi_bonus = max(-3.0, min(3.0, zhi_bonus))
        
        # ═══════════════════════════════════════════════
        # 第三步：九龙70/30分治评分
        # 前五年 = 天干70% + 地支30%；后五年 = 地支70% + 天干30%
        # 总分 = max(前五年分, 后五年分)（取运势最好的半段为准）
        # ═══════════════════════════════════════════════
        bonus_first5 = gan_bonus * 0.7 + zhi_bonus * 0.3
        bonus_last5  = zhi_bonus * 0.7 + gan_bonus * 0.3
        
        score_first5 = round(base + bonus_first5, 1)
        score_last5  = round(base + bonus_last5, 1)
        
        # 总分取两段最高（代表该十年运势上限），但也要反映两段差异
        score = round(max(score_first5, score_last5), 1)
        score = max(1.0, min(10.0, score))
        score_first5 = max(1.0, min(10.0, score_first5))
        score_last5  = max(1.0, min(10.0, score_last5))
        
        # 吉凶标签
        if score >= 7:
            ji_xiong_label = "吉"
        elif score >= 4.5:
            ji_xiong_label = "平"
        else:
            ji_xiong_label = "凶"
        
        # 双维度定性（能量层面 + 感受层面）
        # 能量层面：基于十神+喜忌的事件描述
        _ENERGY_DIM = {
            "正官": {"吉": "事业晋升·地位提升·贵气临门", "平": "官星平运·按部就班", "凶": "官星为忌·压力束缚"},
            "七杀": {"吉": "七杀化权·事业突破·掌权得势", "平": "杀运平过·压力可控", "凶": "七杀攻身·小人侵扰·冲突频发"},
            "正印": {"吉": "印星护身·学业精进·贵人相助", "平": "稳中求进·积累阶段", "凶": "印星为忌·依赖被动"},
            "偏印": {"吉": "偏印得力·技艺精进·特殊机缘", "平": "偏印平运·深度思考", "凶": "枭神夺食·计划受阻"},
            "正财": {"吉": "财运亨通·收入增长·资产增值", "平": "财运平稳·积累有方", "凶": "财星为忌·为财所累"},
            "偏财": {"吉": "偏财透出·意外之财·投资得利", "平": "偏财平运·小有进账", "凶": "偏财为忌·投机失利"},
            "比肩": {"吉": "比肩帮身·根基坚实·自主有成", "平": "比肩平运·独立担当", "凶": "比肩争夺·竞争激烈"},
            "劫财": {"吉": "劫财助身·人脉助力·合作共赢", "平": "劫财平运·社交活跃", "凶": "劫财夺财·破耗连连"},
            "食神": {"吉": "食神生财·才华变现·技艺有成", "平": "食神平运·享受成果", "凶": "食神为忌·放纵享乐"},
            "伤官": {"吉": "伤官生财·创新获利·才华展露", "平": "伤官平运·突破常规", "凶": "伤官见官·口舌是非"},
        }
        _FEELING_DIM = {
            "正官": {"吉": "心情安稳·做事有底气·受人尊重", "平": "中规中矩·按部就班", "凶": "感到压抑·被管太严·束手束脚"},
            "七杀": {"吉": "压力巨大但能驾驭·痛并成长着", "平": "压力适中·能应付", "凶": "身心俱疲·心力交瘁·四面楚歌"},
            "正印": {"吉": "内心充实·学习愉悦·有安全感", "平": "心态平和·缺乏动力", "凶": "消极被动·过度依赖·缺乏主见"},
            "偏印": {"吉": "精神富足·钻研有得·思维活跃", "平": "喜欢独处·思考人生", "凶": "孤僻多疑·思想极端·与社会脱节"},
            "正财": {"吉": "财务自由带来的安全感·踏实满足", "平": "收支平衡·生活稳定", "凶": "为钱发愁·经济压力大"},
            "偏财": {"吉": "赚钱轻松·花钱也痛快·社交愉悦", "平": "小有进账·生活滋润", "凶": "破财心疼·投资焦虑"},
            "比肩": {"吉": "独立自信·有主见·有掌控感", "平": "自给自足·不依赖人", "凶": "感到孤立·无人相助·固执己见"},
            "劫财": {"吉": "朋友帮助·合作愉快·有人撑腰", "平": "社交忙碌·应酬频繁", "凶": "被朋友所累·社交疲惫·经济纠纷"},
            "食神": {"吉": "心情愉悦·才华被认可·生活享受", "平": "轻松自在·不紧张", "凶": "放纵后的空虚·才华受阻"},
            "伤官": {"吉": "灵感迸发·创造满足·被欣赏", "平": "想法多·表达欲强", "凶": "被孤立·争执不断·心中有火"},
        }

        ji_xiong_key = ji_xiong_label  # "吉" / "平" / "凶"
        energy_dim = _ENERGY_DIM.get(gan_ss, {}).get(ji_xiong_key, f"{gan_ss}运·{ji_xiong_key}")
        feeling_dim = _FEELING_DIM.get(gan_ss, {}).get(ji_xiong_key, f"{gan_ss}运·感受{ji_xiong_key}")

        result.append({
            "gan_zhi": gz,
            "ji_xiong": f"{ji_xiong_label}（{gan_ss}）",
            "score": score,
            "score_first5": score_first5,  # 前五年：天干70%+地支30%
            "score_last5": score_last5,    # 后五年：地支70%+天干30%
            "gan_ss": gan_ss,
            "detail": f"前五年{score_first5}分(天干{gan_bonus:+.1f}×70%+地支{zhi_bonus:+.1f}×30%) → 后五年{score_last5}分(地支{zhi_bonus:+.1f}×70%+天干{gan_bonus:+.1f}×30%); " + "; ".join(details),
            "energy_dim": energy_dim,    # 能量层面
            "feeling_dim": feeling_dim,  # 感受层面
        })
    return result


def calc_cai_fu_deng_ji(cai_xing_total: float, sqr_score: float, sqr_level: str,
                         ri_gan: str, ge_ju: str,
                         nian_gan: str = "", yue_gan: str = "", shi_gan: str = "",
                         has_ku: bool = False) -> dict:
    """
    财富量级评估 v8.0
    基于金鉴真人·财富定级定量体系（素材11+17逐字精读版）
    使用六种八字状态矩阵法（素材17第161~193行）
    """
    # 1. 判断财星强弱（≥40分为财旺）
    cai_strong = cai_xing_total >= 40.0
    
    # 2. 从弱格特殊处理（知识库素材17第329~333行）
    if sqr_level == "从弱":
        if cai_strong:
            # 从弱格+财旺 → 亿万级（月令生财，财星得令）
            state = "从弱格+财旺"
            base_score = 70  # 大富基准
            score = min(base_score + 10, 90)
        else:
            # 从弱格+财弱 → 小富~中富（贵气生财），除非财星极弱
            if cai_xing_total < 1:
                state = "从弱格+无财"
                base_score = 0
            else:
                state = "从弱格+财弱"
                # 财星分数按比例映射到小富区间(12-36)
                base_score = 12 + (cai_xing_total / 40.0) * 24
                base_score = min(base_score, 36)
            score = base_score  # 不加额外加成，贵气>财气
        info = CAI_FU_STATES[state]
        # 按分数映射到具体财富五级
        actual_level = "贫穷"
        for lv_name, lv_low, lv_high, _ in CAI_FU_WU_JI:
            if lv_low <= score < lv_high:
                actual_level = lv_name
                break
        return {
            "level": actual_level,
            "score": round(score, 1),
            "detail": f"财富总评{round(score,1)}分，属于{actual_level}层次。{info['desc']}",
            "state": state,
            "cai_xing_score": round(cai_xing_total, 1),
            "sq_level": sqr_level,
        }
    
    # 3. 常规状态判断
    # 判断身强身弱（基于知识库：适配七段式评分映射）
    if sqr_level in ("身强", "偏强", "从强"):
        shen_state = "身强"
    elif sqr_level in ("中和",):
        shen_state = "中和"
    else:  # 身弱 / 偏弱 / 从弱
        shen_state = "身弱"
    
    # 四柱无财检查（cai_xing_total < 1分视为无财）
    wu_cai = cai_xing_total < 1.0
    
    if wu_cai and shen_state == "身弱":
        state = "无财+身弱"
    elif wu_cai and shen_state == "身强":
        state = "无财+身强"
    elif shen_state == "身强" and cai_strong:
        state = "身强财旺"
    elif shen_state == "身强" and not cai_strong:
        state = "身强财弱"
    elif shen_state == "身弱" and cai_strong:
        state = "身弱财旺"
    elif shen_state == "中和" and cai_strong:
        state = "中和财旺"
    elif shen_state == "中和" and not cai_strong:
        state = "中和财弱"
    else:
        state = "身弱财弱"
    
    info = CAI_FU_STATES.get(state, {"level":"小富", "desc":""})
    
    # 综合财富评分 = 财星原分（知识库不单独定义综合评分，直接用财星原分）
    score = cai_xing_total
    
    score = min(max(score, 0), 100)
    
    # 按分数映射到具体财富五级
    # 优先级：状态判断(CAI_FU_STATES) > 分数映射(CAI_FU_WU_JI)
    # 九龙道长规则：身强财弱=中富，不应被纯分数映射覆盖
    actual_level = info["level"]
    # CAI_FU_WU_JI仅作为补充参考（只在info不提供level时使用）
    if actual_level in ("大富~巨富", "小富~中富"):
        # 区间级别需按分数落入方向再分
        for lv_name, lv_low, lv_high, _ in CAI_FU_WU_JI:
            if lv_low <= score < lv_high:
                actual_level = lv_name
                break
    
    return {
        "level": actual_level,
        "score": round(score, 1),
        "detail": f"财富总评{round(score,1)}分，属于{actual_level}层次。{info['desc']}",
        "state": state,
        "cai_xing_score": round(cai_xing_total, 1),
        "sq_level": sqr_level,
    }
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# P0: 重大灾祸5指标检测（用于calc_liu_nian）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

XUE_REN_FOR_ZAI_HUO = {
    "甲":"卯","乙":"辰","丙":"午","丁":"未","戊":"午",
    "己":"未","庚":"酉","辛":"戌","壬":"子","癸":"丑"
}

def _calc_zai_huo_indicators(ri_gan: str, liu_nian_gan: str, liu_nian_zhi: str,
                              da_yun_gan_zhi: str = "",
                              yuan_gan_list: list = None,
                              yuan_zhi_list: list = None) -> dict:
    """
    流年重大灾祸5指标检测
    
    指标：
    1. 岁运并临 — 流年干支与大运干支完全相同
    2. 三刑+七杀 — 流年地支与原局/大运构成三刑，且流年天干为七杀
    3. 七杀无制 — 流年天干为七杀，原局无印星化杀且无食神制杀
    4. 血刃 — 流年地支为日干的血刃位
    5. 枭神夺食 — 流年天干为枭神，原局天干有食神/伤官
    
    返回：
    {
        "sui_yun_bing_lin": bool,
        "san_xing_qi_sha": bool,
        "qi_sha_wu_zhi": bool,
        "xue_ren": bool,
        "xiao_shen_duo_shi": bool,
        "count": int,            # 命中指标总数
        "details": [str],        # 详细说明
        "has_zai_huo": bool,     # count >= 1 即为有灾祸信号
    }
    """
    indicators = {
        "sui_yun_bing_lin": False,
        "san_xing_qi_sha": False,
        "qi_sha_wu_zhi": False,
        "xue_ren": False,
        "xiao_shen_duo_shi": False,
    }
    details = []
    
    # 辅助函数：获取十神
    def _get_ss(ri_g, g):
        ri = TIAN_GAN.index(ri_g)
        g_idx = TIAN_GAN.index(g)
        rw = WX_ORDER.index(TIAN_GAN_WU_XING[ri_g])
        gw = WX_ORDER.index(TIAN_GAN_WU_XING[g])
        ry = ri % 2
        gy = g_idx % 2
        if rw == gw:
            return "比肩" if ry == gy else "劫财"
        if gw == (rw + 1) % 5:
            return "食神" if ry == gy else "伤官"
        if gw == (rw + 2) % 5:
            return "正财" if ry != gy else "偏财"
        if gw == (rw + 3) % 5:
            return "正官" if ry != gy else "七杀"
        if gw == (rw + 4) % 5:
            if ry != gy:
                return "正印"
            return "偏印"
        return ""
    
    def _get_raw_ss(ri_g, g):
        """原始十神（不含枭神标记）"""
        ri = TIAN_GAN.index(ri_g)
        g_idx = TIAN_GAN.index(g)
        rw = WX_ORDER.index(TIAN_GAN_WU_XING[ri_g])
        gw = WX_ORDER.index(TIAN_GAN_WU_XING[g])
        ry = ri % 2
        gy = g_idx % 2
        if rw == gw:
            return "比肩" if ry == gy else "劫财"
        if gw == (rw + 1) % 5:
            return "食神" if ry == gy else "伤官"
        if gw == (rw + 2) % 5:
            return "正财" if ry != gy else "偏财"
        if gw == (rw + 3) % 5:
            return "正官" if ry != gy else "七杀"
        if gw == (rw + 4) % 5:
            return "正印" if ry != gy else "偏印"
        return ""
    
    liu_nian_ss = _get_ss(ri_gan, liu_nian_gan)
    
    # ── 1. 岁运并临 ──
    if da_yun_gan_zhi and len(da_yun_gan_zhi) >= 2:
        dy_gan = da_yun_gan_zhi[0]
        dy_zhi = da_yun_gan_zhi[1]
        if liu_nian_gan == dy_gan and liu_nian_zhi == dy_zhi:
            indicators["sui_yun_bing_lin"] = True
            details.append(f"岁运并临：流年{liu_nian_gan}{liu_nian_zhi}与大运{dy_gan}{dy_zhi}完全相同，主重大变动")
    
    # ── 2. 三刑+七杀 ──
    if liu_nian_ss == "七杀":
        # 检查流年地支与大运/原局构成三刑
        all_check_zhi = []
        if da_yun_gan_zhi and len(da_yun_gan_zhi) >= 2:
            all_check_zhi.append(da_yun_gan_zhi[1])
        if yuan_zhi_list:
            all_check_zhi.extend(yuan_zhi_list)
        
        for other_zhi in all_check_zhi:
            if not other_zhi or other_zhi == liu_nian_zhi:
                continue
            # 检查是否构成三刑
            xing_target = SAN_XING_MAP.get(liu_nian_zhi)
            if xing_target and xing_target == other_zhi and liu_nian_zhi not in ZI_XING:
                indicators["san_xing_qi_sha"] = True
                details.append(f"三刑+七杀：流年天干{liu_nian_gan}为七杀，地支{liu_nian_zhi}与{other_zhi}相刑，凶险叠加")
                break
    
    # ── 3. 七杀无制 ──
    if liu_nian_ss == "七杀":
        you_yin = False  # 有印星化杀
        you_shi_shen = False  # 有食神制杀
        if yuan_gan_list:
            for tg in yuan_gan_list:
                if not tg:
                    continue
                tg_raw_ss = _get_raw_ss(ri_gan, tg)
                if tg_raw_ss in ("正印", "偏印"):
                    you_yin = True
                if tg_raw_ss in ("食神", "伤官"):
                    you_shi_shen = True
        if not you_yin and not you_shi_shen:
            indicators["qi_sha_wu_zhi"] = True
            detail_parts = [f"七杀无制：流年天干{liu_nian_gan}为七杀"]
            if not you_yin:
                detail_parts.append("原局无印星化杀")
            if not you_shi_shen:
                detail_parts.append("无食神制杀")
            details.append("，".join(detail_parts))
    
    # ── 4. 血刃 ──
    xue_ren_zhi = XUE_REN_FOR_ZAI_HUO.get(ri_gan, "")
    if xue_ren_zhi and liu_nian_zhi == xue_ren_zhi:
        indicators["xue_ren"] = True
        details.append(f"血刃：流年地支{liu_nian_zhi}为日干{ri_gan}的血刃位，主血光意外")
    
    # ── 5. 枭神夺食 ──
    # 流年天干为偏印(枭神)，且原局天干有食神/伤官
    liu_nian_raw_ss = _get_raw_ss(ri_gan, liu_nian_gan)
    if liu_nian_raw_ss == "偏印":
        has_shi_shen = False
        if yuan_gan_list:
            for tg in yuan_gan_list:
                if not tg:
                    continue
                tg_raw_ss = _get_raw_ss(ri_gan, tg)
                if tg_raw_ss in ("食神", "伤官"):
                    has_shi_shen = True
                    break
        if has_shi_shen:
            indicators["xiao_shen_duo_shi"] = True
            details.append(f"枭神夺食：流年天干{liu_nian_gan}为枭神，原局天干有食神/伤官，该年运势不畅")
    
    count = sum(1 for v in indicators.values() if v)
    return {
        **indicators,
        "count": count,
        "details": details,
        "has_zai_huo": count >= 1,
    }

# ── 天干五合成功率检测 ──
# 规则：隔合减半、遥合无效、有根不减、无根全减
# 位置距离：年(0) 月(1) 日(2) 时(3)
#   相邻(d=1)：合有效  隔合(d=2)：减半  遥合(d≥3)：无效
_POSITION_ORDER = {"年": 0, "月": 1, "日": 2, "时": 3}

def _calc_tian_gan_wu_he_success_rate(gan_a: str, pos_a: str,
                                       gan_b: str, pos_b: str,
                                       zhi_list: list) -> dict:
    """计算天干五合成功率
    返回: {"success_rate": float, "reason": str}
    """
    # 检查是否构成五合
    if GAN_WU_HE.get(gan_a) != gan_b:
        return {"success_rate": 0.0, "reason": f"{gan_a}{gan_b}不构成五合"}

    # 位置距离
    idx_a = _POSITION_ORDER.get(pos_a, 0)
    idx_b = _POSITION_ORDER.get(pos_b, 3)
    dist = abs(idx_a - idx_b)

    if dist >= 3:
        return {"success_rate": 0.0, "reason": f"{pos_a}{pos_b}遥合，无效"}

    base_rate = 1.0 if dist == 1 else 0.5  # 相邻=1.0, 隔合=0.5

    # 检查是否有根：gan_b（原局组合中处于较远位置的天干）的五行
    # 是否在地支藏干中有支撑
    has_root = False
    wx_b = TIAN_GAN_WU_XING[gan_b]
    for zhi in zhi_list:
        for cg, wt in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cg] == wx_b:
                has_root = True
                break
        if has_root:
            break

    if not has_root:
        base_rate = 0.0  # 无根全减

    reason_parts = [f"{pos_a}{pos_b}"]
    if dist == 2:
        reason_parts.append("隔合")
    if has_root:
        reason_parts.append("有根")
    else:
        reason_parts.append("无根")
    reason_parts.append(f"成功率{int(base_rate*100)}%")

    return {"success_rate": base_rate, "reason": "，".join(reason_parts)}


def calc_liu_nian(year: int, ri_gan: str, da_yun_list: list,
                  nian_gan: str = "", nian_zhi: str = "",
                  yue_gan: str = "", yue_zhi: str = "",
                  ri_zhi: str = "",
                  shi_gan: str = "", shi_zhi: str = "") -> dict:
    """
    流年分析（含与原局四柱互动）。
    
    参数：
        year: 流年公历年份
        ri_gan: 日干
        da_yun_list: calc_da_yun 返回的 da_yun 列表，每项含 gan_zhi
        nian_gan/nian_zhi/yue_gan/yue_zhi/ri_zhi/shi_gan/shi_zhi: 原局四柱干支（可选，传入后计算与原局互动）
    
    返回：
        {
            "year": 2026,
            "tian_gan": "丙",
            "di_zhi": "午",
            "gan_zhi": "丙午",
            "shi_shen": "正印",
            "current_da_yun": {...},
            "chong_da_yun": bool,    # 与当前大运相冲
            "he_da_yun": bool,       # 与当前大运相合
            "xing_da_yun": bool,     # 与当前大运相刑
            "hai_da_yun": bool,      # 与当前大运相害
            "conflict_detail": "流年天干丙与大运天干壬相冲",
            "analysis": "...",
            # 以下为与原局四柱互动（有传入原局数据时才存在）
            "yuan_ju_gan_he": {"月": "丙辛合"},       # 天干五合
            "yuan_ju_gan_ke": {"年": "丙壬冲"},       # 天干相冲
            "yuan_ju_gan_fu_yin": {"日": "丙伏吟"},   # 天干伏吟
            "yuan_ju_zhi_chong": {"日": "子午冲"},     # 地支六冲（贪合忘冲）
            "yuan_ju_zhi_he": {"年": "寅亥合"},        # 地支六合
            "yuan_ju_zhi_xing": {"月": "巳申刑"},      # 地支三刑
            "yuan_ju_zhi_zi_xing": {"年": "辰自刑"},   # 地支自刑
            "yuan_ju_zhi_hai": {"时": "子未害"},       # 地支六害
            "yuan_ju_zhi_po": {"日": "子酉破"},        # 地支六破
            "yuan_ju_detail": "流年天干丙与年柱天干丙伏吟；流年地支午与日柱地支子六冲",
            "yuan_ju_analysis": "流年与原局冲克较多，运势多变动",
        }
    """
    # 流年干支
    # 保存原局年柱（后续会被流年覆盖）
    yuan_nian_gan = nian_gan
    yuan_nian_zhi = nian_zhi
    nian_gan = TIAN_GAN[(year - 4) % 10]
    nian_zhi = DI_ZHI[(year - 4) % 12]
    gan_zhi = nian_gan + nian_zhi

    # 十神
    ss = shi_shen(ri_gan, nian_gan)

    # 找出当前所行大运
    current_da_yun = None
    if da_yun_list:
        # 假设当前年龄=流年减去生年，简化处理
        # 实际调用时传已计算好的大运和当前年龄更准确
        current_da_yun = da_yun_list[0] if da_yun_list else None

    # ── 重大灾祸5指标检测 ──
    dy_gan_zhi = current_da_yun.get("gan_zhi", "") if current_da_yun else ""
    yuan_gan_list_for_zaihuo = [tg for tg in (yuan_nian_gan, yue_gan, ri_gan, shi_gan) if tg]
    yuan_zhi_list_for_zaihuo = [tz for tz in (yuan_nian_zhi, yue_zhi, ri_zhi, shi_zhi) if tz]
    zai_huo = _calc_zai_huo_indicators(
        ri_gan=ri_gan,
        liu_nian_gan=nian_gan,
        liu_nian_zhi=nian_zhi,
        da_yun_gan_zhi=dy_gan_zhi,
        yuan_gan_list=yuan_gan_list_for_zaihuo,
        yuan_zhi_list=yuan_zhi_list_for_zaihuo,
    )
    
    # 与当前大运的关系检测
    chong_da_yun = False
    he_da_yun = False
    xing_da_yun = False
    hai_da_yun = False
    conflict_detail = ""
    
    if current_da_yun and "gan_zhi" in current_da_yun:
        dy_gan = current_da_yun["gan_zhi"][0]
        dy_zhi = current_da_yun["gan_zhi"][1]
        
        # 天干相冲（甲庚冲、乙辛冲、丙壬冲、丁癸冲）
        gan_chong_pairs = {"甲":"庚","庚":"甲","乙":"辛","辛":"乙",
                           "丙":"壬","壬":"丙","丁":"癸","癸":"丁"}
        if gan_chong_pairs.get(nian_gan) == dy_gan:
            chong_da_yun = True
            conflict_detail += f"流年天干{nian_gan}与大运天干{dy_gan}相冲; "
        
        # 地支相冲
        if LIU_CHONG.get(nian_zhi) == dy_zhi:
            chong_da_yun = True
            conflict_detail += f"流年地支{nian_zhi}与大运地支{dy_zhi}相冲; "
        
        # 六合
        liu_he_check = LIU_HE.get(nian_zhi, "")
        if liu_he_check and liu_he_check == dy_zhi:
            he_da_yun = True
            conflict_detail += f"流年地支{nian_zhi}与大运地支{dy_zhi}六合; "
        
        # 三合（简化：只要两字在三合集合中就合）
        for he_set in SAN_HE:
            if nian_zhi in he_set and dy_zhi in he_set:
                he_da_yun = True
                conflict_detail += f"流年地支{nian_zhi}与大运地支{dy_zhi}三合; "
                break
        
        # 相刑
        xing_check = SAN_XING_MAP.get(nian_zhi, "")
        if xing_check and xing_check == dy_zhi:
            xing_da_yun = True
            conflict_detail += f"流年地支{nian_zhi}与大运地支{dy_zhi}相刑; "
        
        # 相害
        hai_check = LIU_HAI.get(nian_zhi, "")
        if hai_check and hai_check == dy_zhi:
            hai_da_yun = True
            conflict_detail += f"流年地支{nian_zhi}与大运地支{dy_zhi}相害; "
    
    if not conflict_detail:
        conflict_detail = "流年与大运无明显冲合刑害关系"
    
    # ── 流年与原局四柱的互动 ──
    yuan_ju_gan_he = {}
    yuan_ju_gan_ke = {}
    yuan_ju_gan_fu_yin = {}
    yuan_ju_zhi_chong = {}
    yuan_ju_zhi_he = {}
    yuan_ju_zhi_xing = {}
    yuan_ju_zhi_zi_xing = {}
    yuan_ju_zhi_hai = {}
    yuan_ju_zhi_po = {}
    yuan_ju_detail_parts = []
    
    # 四柱天干（含日干ri_gan）
    yuan_gan_list = [("年", nian_gan), ("月", yue_gan), ("日", ri_gan), ("时", shi_gan)]
    # 四柱地支
    yuan_zhi_list = [("年", nian_zhi), ("月", yue_zhi), ("日", ri_zhi), ("时", shi_zhi)]
    
    # 天干相冲映射
    gan_chong_pairs = {"甲":"庚","庚":"甲","乙":"辛","辛":"乙",
                       "丙":"壬","壬":"丙","丁":"癸","癸":"丁"}
    
    # 流年天干 vs 原局四天干
    for pos, pg in yuan_gan_list:
        if not pg:
            continue
        # 五合（甲己、乙庚、丙辛、丁壬、戊癸）带成功率检测
        if GAN_WU_HE.get(nian_gan) == pg:
            # 计算成功率（隔合减半、遥合无效、有根不减、无根全减）
            # 流年天干视作"年"位，与各柱构成对比
            wu_he_result = _calc_tian_gan_wu_he_success_rate(
                nian_gan, "年", pg, pos,
                [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
            )
            if wu_he_result["success_rate"] > 0:
                yuan_ju_gan_he[pos] = f"{nian_gan}{pg}合({wu_he_result['reason']})"
                yuan_ju_detail_parts.append(
                    f"流年天干{nian_gan}与{pos}柱天干{pg}五合，{wu_he_result['reason']}"
                )
            else:
                yuan_ju_detail_parts.append(
                    f"流年天干{nian_gan}与{pos}柱天干{pg}五合但{wu_he_result['reason']}"
                )
        # 相冲（甲庚冲、乙辛冲、丙壬冲、丁癸冲）
        if gan_chong_pairs.get(nian_gan) == pg:
            yuan_ju_gan_ke[pos] = f"{nian_gan}{pg}冲"
            yuan_ju_detail_parts.append(f"流年天干{nian_gan}与{pos}柱天干{pg}相冲")
        # 伏吟（天干相同）
        if nian_gan == pg:
            yuan_ju_gan_fu_yin[pos] = f"{nian_gan}伏吟"
            yuan_ju_detail_parts.append(f"流年天干{nian_gan}与{pos}柱天干{pg}伏吟")
    
    # 流年地支 vs 原局四地支
    for pos, pz in yuan_zhi_list:
        if not pz:
            continue
        
        # 判断流年地支与该柱地支是否六合（用于贪合忘冲）
        liu_he_with_pillar = (LIU_HE.get(nian_zhi) == pz)
        
        # 六合
        if liu_he_with_pillar:
            yuan_ju_zhi_he[pos] = f"{nian_zhi}{pz}合"
            yuan_ju_detail_parts.append(f"流年地支{nian_zhi}与{pos}柱地支{pz}六合")
        
        # 六冲（贪合忘冲原则：流年与某柱相合时，不对该柱相冲）
        if LIU_CHONG.get(nian_zhi) == pz and not liu_he_with_pillar:
            yuan_ju_zhi_chong[pos] = f"{nian_zhi}{pz}冲"
            yuan_ju_detail_parts.append(f"流年地支{nian_zhi}与{pos}柱地支{pz}六冲")
        
        # 三刑（不含自刑，自刑单独处理）
        xing_target = SAN_XING_MAP.get(nian_zhi)
        if xing_target == pz and nian_zhi not in ZI_XING:
            yuan_ju_zhi_xing[pos] = f"{nian_zhi}{pz}刑"
            yuan_ju_detail_parts.append(f"流年地支{nian_zhi}与{pos}柱地支{pz}相刑")
        
        # 自刑（辰辰、午午、酉酉、亥亥）
        if nian_zhi in ZI_XING and nian_zhi == pz:
            yuan_ju_zhi_zi_xing[pos] = f"{nian_zhi}自刑"
            yuan_ju_detail_parts.append(f"流年地支{nian_zhi}与{pos}柱地支{pz}自刑")
        
        # 六害（子未、丑午、寅巳、卯辰、申亥、酉戌）
        if LIU_HAI.get(nian_zhi) == pz:
            yuan_ju_zhi_hai[pos] = f"{nian_zhi}{pz}害"
            yuan_ju_detail_parts.append(f"流年地支{nian_zhi}与{pos}柱地支{pz}六害")
        
        # 六破（子酉、寅亥、辰丑、午卯、申巳、戌未）
        if LIU_PO.get(nian_zhi) == pz:
            yuan_ju_zhi_po[pos] = f"{nian_zhi}{pz}破"
            yuan_ju_detail_parts.append(f"流年地支{nian_zhi}与{pos}柱地支{pz}六破")
    
    yuan_ju_detail = "；".join(yuan_ju_detail_parts) if yuan_ju_detail_parts else "流年与原局无明显冲合刑害关系"
    
    # 大树理论分析：有根的天干受冲克影响小
    tree_theory_notes = []
    if yuan_ju_gan_ke or yuan_ju_gan_fu_yin:
        # 收集有冲克/伏吟的天干在原局中是否有根
        affected_positions = list(yuan_ju_gan_ke.keys()) + list(yuan_ju_gan_fu_yin.keys())
        for pos in set(affected_positions):
            # 找出该柱的原局天干
            pos_map = {"年": nian_gan, "月": yue_gan, "日": ri_gan, "时": shi_gan}
            pg = pos_map.get(pos, "")
            if pg:
                # 检查该天干在原局四地支中是否有根（同字出现在藏干中）
                has_root = False
                for zhi in [nz for _, nz in yuan_zhi_list if nz]:
                    for cg, _ in DI_ZHI_CANG_GAN.get(zhi, []):
                        if cg == pg:
                            has_root = True
                            break
                    if has_root:
                        break
                if has_root:
                    tree_theory_notes.append(f"{pos}柱{pg}有根（大树理论），受流年冲克影响较小")
    
    # 综合评价
    analysis_parts = []
    if chong_da_yun:
        analysis_parts.append("流年与大运相冲，运势波动较大，宜保守行事")
    if he_da_yun:
        analysis_parts.append("流年与大运相合，运势顺遂，贵人相助")
    if xing_da_yun:
        analysis_parts.append("流年与大运相刑，注意人际关系纠纷")
    if hai_da_yun:
        analysis_parts.append("流年与大运相害，谨防小人暗算")
    if not chong_da_yun and not he_da_yun and not xing_da_yun and not hai_da_yun:
        analysis_parts.append("流年与大运关系平和，按常规节奏行事即可")
    
    # 原局互动分析
    yuan_ju_analysis_parts = []
    has_yuan_hu_dong = bool(yuan_ju_detail_parts)
    
    if yuan_ju_gan_he:
        he_names = "、".join([v for v in yuan_ju_gan_he.values()])
        yuan_ju_analysis_parts.append(f"流年与原局天干五合（{he_names}），有化气可能")
    if yuan_ju_gan_ke:
        ke_names = "、".join([v for v in yuan_ju_gan_ke.values()])
        yuan_ju_analysis_parts.append(f"流年与原局天干相冲（{ke_names}），注意外应变动")
    if yuan_ju_gan_fu_yin:
        fy_pos = "、".join(yuan_ju_gan_fu_yin.keys())
        yuan_ju_analysis_parts.append(f"流年与原局{fy_pos}柱伏吟，该方面易有重复性事件")
    if yuan_ju_zhi_chong:
        zc_parts = "、".join([v for v in yuan_ju_zhi_chong.values()])
        yuan_ju_analysis_parts.append(f"流年与原局地支相冲（{zc_parts}），根基变动")
    if yuan_ju_zhi_he:
        zh_parts = "、".join([v for v in yuan_ju_zhi_he.values()])
        yuan_ju_analysis_parts.append(f"流年与原局地支六合（{zh_parts}），人缘关系加强")
    if yuan_ju_zhi_xing:
        zx_parts = "、".join([v for v in yuan_ju_zhi_xing.values()])
        yuan_ju_analysis_parts.append(f"流年与原局地支相刑（{zx_parts}），注意口舌官非")
    if yuan_ju_zhi_zi_xing:
        zzx_parts = "、".join([v for v in yuan_ju_zhi_zi_xing.values()])
        yuan_ju_analysis_parts.append(f"流年与原局地支自刑（{zzx_parts}），内心纠结")
    if yuan_ju_zhi_hai:
        zh_parts2 = "、".join([v for v in yuan_ju_zhi_hai.values()])
        yuan_ju_analysis_parts.append(f"流年与原局地支相害（{zh_parts2}），防小人暗伤")
    if yuan_ju_zhi_po:
        zp_parts = "、".join([v for v in yuan_ju_zhi_po.values()])
        yuan_ju_analysis_parts.append(f"流年与原局地支相破（{zp_parts}），小有损耗")
    if tree_theory_notes:
        yuan_ju_analysis_parts.append("；".join(tree_theory_notes))
    if not has_yuan_hu_dong:
        yuan_ju_analysis_parts.append("流年与原局无明显冲合刑害关系")
    
    result = {
        "year": year,
        "tian_gan": nian_gan,
        "di_zhi": nian_zhi,
        "gan_zhi": gan_zhi,
        "shi_shen": ss,
        "current_da_yun": current_da_yun,
        "chong_da_yun": chong_da_yun,
        "he_da_yun": he_da_yun,
        "xing_da_yun": xing_da_yun,
        "hai_da_yun": hai_da_yun,
        "conflict_detail": conflict_detail.strip("; "),
        "analysis": " ".join(analysis_parts),
        "zai_huo_indicators": zai_huo,
    }
    
    # 只有传入了原局数据时才添加原局互动字段
    if nian_gan or nian_zhi or yue_gan or yue_zhi or ri_zhi or shi_gan or shi_zhi:
        result.update({
            "yuan_ju_gan_he": yuan_ju_gan_he,
            "yuan_ju_gan_ke": yuan_ju_gan_ke,
            "yuan_ju_gan_fu_yin": yuan_ju_gan_fu_yin,
            "yuan_ju_zhi_chong": yuan_ju_zhi_chong,
            "yuan_ju_zhi_he": yuan_ju_zhi_he,
            "yuan_ju_zhi_xing": yuan_ju_zhi_xing,
            "yuan_ju_zhi_zi_xing": yuan_ju_zhi_zi_xing,
            "yuan_ju_zhi_hai": yuan_ju_zhi_hai,
            "yuan_ju_zhi_po": yuan_ju_zhi_po,
            "yuan_ju_detail": yuan_ju_detail,
            "yuan_ju_analysis": " ".join(yuan_ju_analysis_parts),
        })
    
    return result


def calc_xue_ye(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                ge_ju: str = "", shen_score: float = 50.0, da_yun_list: list = None,
                sqr_level: str = "") -> dict:
    """
    学历评分 v8.1 — 基于九龙道长原始理论
    核心原则：印星只在月令计分（非月令之印不计分）
    四维度综合判断法：
    ① 身强弱定承载 → ② 月令印能量 → ③ 文昌佐证 → ④ 大运窗口
    得分 = 原局基础(0-7分) + 大运赋能(0-3分) = 满分10分
    输出前×10转为0-100分制
    知识库来源：
    - 金鉴课程/金鉴真人_学历与报考分析知识点_20260604.md
    - jiulong_complete_theory.md (印星只在月令计分)
    """
    from collections import Counter
    
    is_cong_ruo = (sqr_level == "从弱")
    is_cong_qiang = (sqr_level == "从强")
    is_cong_ge = is_cong_ruo or is_cong_qiang
    
    raw_score = 0.5  # 基础保底：所有人都有基本学习能力
    details = ["基础保底 +0.5"]
    
    # ── 维度①：身强弱定承载 ──
    # 身强(≥60)：印大概率是忌神，但月令有印仍为客观事实
    # 身弱(<40)：印大概率是喜用
    # 中和(40-60)：印星中性
    shen_factor_desc = ""
    if is_cong_ruo:
        shen_factor_desc = "从弱格：印为忌神，不靠印星"
    elif is_cong_qiang:
        shen_factor_desc = "从强格：印为喜用"
    elif shen_score >= 60:
        shen_factor_desc = f"身强({shen_score:.0f}分)：印大概率是忌神"
    elif shen_score >= 40:
        shen_factor_desc = f"中和({shen_score:.0f}分)：印星中性"
    else:
        shen_factor_desc = f"身弱({shen_score:.0f}分)：印大概率是喜用"
    details.append(f"①身强弱定承载: {shen_factor_desc}")
    
    # ── 维度②：月令印能量（核心！原文：印星只在月令计分） ──
    yue_ben = DI_ZHI_CANG_GAN[yue_zhi][0][0] if DI_ZHI_CANG_GAN.get(yue_zhi) else ""
    yue_ben_ss = shi_shen(ri_gan, yue_ben) if yue_ben else ""
    
    yue_yin_score = 0.0
    yue_yin_detail = ""
    
    if yue_ben_ss in ("正印", "偏印"):
        # 月令有印 — 基础分
        yue_yin_score = 1.5
        yue_yin_detail = f"月令本气{yue_ben}={yue_ben_ss} ✅ +{yue_yin_score}"
        
        # 透干加分：月干透印
        yue_gan_ss = shi_shen(ri_gan, yue_gan)
        if yue_gan_ss in ("正印", "偏印"):
            yue_yin_score += 1.0
            yue_yin_detail += f"，月干透{yue_gan}({yue_gan_ss}) +1.0"
        
        # 印根完整度：看其它支的藏干印
        yin_zhi_count = 0
        for pos, zhi in [("年支", nian_zhi), ("日支", ri_zhi), ("时支", shi_zhi)]:
            for cg, wt in DI_ZHI_CANG_GAN.get(zhi, []):
                if shi_shen(ri_gan, cg) in ("正印", "偏印"):
                    yin_zhi_count += 1
                    if wt >= 60:
                        yue_yin_score += 0.3
                        yue_yin_detail += f"，{pos}藏{cg}({wt}%) +0.3"
                    break
        if yin_zhi_count >= 2:
            yue_yin_score += 0.3
            yue_yin_detail += "，印根充足 +0.3"
    else:
        # 月令非印 — 无印星基础分
        yue_yin_detail = f"月令本气{yue_ben}={yue_ben_ss or '无'} ❌ 无月令印"
        
        # 非月令印星有根补偿（年支/日支/时支藏干印星）
        # 月令无印时，年支有印为强学业基因
        for pos, zhi in [("年支", nian_zhi), ("日支", ri_zhi), ("时支", shi_zhi)]:
            for cg, wt in DI_ZHI_CANG_GAN.get(zhi, []):
                if shi_shen(ri_gan, cg) in ("正印", "偏印"):
                    if wt >= 60:
                        yue_yin_score += 1.0
                        yue_yin_detail += f"，{pos}藏{cg}{shi_shen(ri_gan, cg)}({wt}%) +1.0"
                    elif wt >= 30:
                        yue_yin_score += 0.5
                        yue_yin_detail += f"，{pos}藏{cg}{shi_shen(ri_gan, cg)}({wt}%) +0.5"
                    break  # 每支只取第一个印星
    
    # 从弱格特殊：月令印为假从真用
    if is_cong_ruo and yue_ben_ss in ("正印", "偏印"):
        yue_yin_score = 0.8
        yue_yin_detail = f"从弱格·月令{yue_ben}={yue_ben_ss}(假从真用) +0.8"
    
    # 从强格特殊：月令印增强
    if is_cong_qiang and yue_ben_ss in ("正印", "偏印"):
        yue_yin_score = 2.5
        yue_yin_detail = f"从强格·月令{yue_ben}={yue_ben_ss} +2.5"
    
    raw_score += yue_yin_score
    details.append(f"②月令印能量: {yue_yin_detail}")
    
    # ── 维度③：文昌贵人（日干查法为主） ──
    wen_chang_zhi = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申",
                     "己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
    wc_zhi = wen_chang_zhi.get(ri_gan, "")  # 以日干查文昌（理论首重）
    found_wc = False
    wc_detail_parts = []
    for pos, zhi in [("年支", nian_zhi), ("月支", yue_zhi), ("日支", ri_zhi), ("时支", shi_zhi)]:
        if zhi == wc_zhi:
            found_wc = True
            raw_score += 0.8
            wc_detail_parts.append(f"{pos}文昌({wc_zhi}) +0.8")
            break
    
    # 年干文昌作为备查
    wc_zhi_nian = wen_chang_zhi.get(nian_gan, "")
    if wc_zhi_nian and wc_zhi_nian != wc_zhi:
        for pos, zhi in [("年支", nian_zhi), ("月支", yue_zhi), ("日支", ri_zhi), ("时支", shi_zhi)]:
            if zhi == wc_zhi_nian and not found_wc:
                found_wc = True
                raw_score += 0.5
                wc_detail_parts.append(f"{pos}文昌(年干补查{wc_zhi_nian}) +0.5")
                break
    
    if not found_wc:
        wc_detail_parts.append("原局无文昌")
    
    details.append(f"③文昌贵人: {'、'.join(wc_detail_parts) if wc_detail_parts else '无'}")

    # ── 维度⑤：正官/七杀自律加分 ──
    # 天干透官杀为自律型，学业有毅力加成
    guan_score = 0.0
    guan_detail_parts = []
    for pos, gan in [("月干", yue_gan), ("时干", shi_gan), ("年干", nian_gan)]:
        g_ss = shi_shen(ri_gan, gan)
        if g_ss in ("正官", "七杀"):
            if guan_score < 1.0:
                add = min(0.5, 1.0 - guan_score)
                guan_score += add
                guan_detail_parts.append(f"{pos}透{gan}({g_ss}) +{add}")
    raw_score += guan_score
    if guan_detail_parts:
        details.append(f"⑤官星自律: {'、'.join(guan_detail_parts)} (合计+{guan_score:.1f})")

    # ── 维度④：大运窗口（前两大运有无印运/文昌运） ──
    dy_bonus = 0.0
    dy_detail_parts = []
    if da_yun_list and len(da_yun_list) > 0:
        # 检查前两个大运（首运+次运）
        check_count = min(2, len(da_yun_list))
        for i in range(check_count):
            dy = da_yun_list[i]
            dy_label = "首运" if i == 0 else "次运"
            dy_gan = dy["gan_zhi"][0]
            dy_zhi = dy["gan_zhi"][1]
            dy_gan_ss = shi_shen(ri_gan, dy_gan)

            # 大运天干为印
            if dy_gan_ss in ("正印", "偏印"):
                dy_bonus += 0.5
                dy_detail_parts.append(f"{dy_label}天干{dy_gan}={dy_gan_ss} +0.5")

            # 大运地支为印（新增：地支五行生助日干为印，或藏干有印≥60%）
            dy_zhi_wx = DI_ZHI_WU_XING.get(dy_zhi, "")
            ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
            dy_is_yin = False
            # 方式一：地支五行生我者为印（如卯=木生火=印）
            if dy_zhi_wx and ri_wx and WX_SHENG.get(ri_wx) == dy_zhi_wx:
                dy_is_yin = True
            # 方式二：地支藏干本气为印（如辰藏乙木60%正印）
            if not dy_is_yin:
                dy_zhi_cang = DI_ZHI_CANG_GAN.get(dy_zhi, [])
                for cg, wt in dy_zhi_cang:
                    if shi_shen(ri_gan, cg) in ("正印", "偏印") and wt >= 60:
                        dy_is_yin = True
                        break
            if dy_is_yin:
                dy_bonus += 0.5
                dy_detail_parts.append(f"{dy_label}地支{dy_zhi}为印 +0.5")

            # 大运地支为文昌
            if dy_zhi == wc_zhi or dy_zhi == wc_zhi_nian:
                dy_bonus += 0.5
                dy_detail_parts.append(f"{dy_label}地支文昌({dy_zhi}) +0.5")

            # 大运喜忌（仅对首运应用）
            if i == 0:
                if dy_gan_ss in ("正印", "偏印", "比肩", "劫财") and shen_score < 40:
                    dy_bonus += 0.5
                    dy_detail_parts.append(f"身弱遇印比运 +0.5")
                elif dy_gan_ss in ("食神", "伤官", "正财", "偏财") and shen_score >= 60:
                    dy_bonus += 0.5
                    dy_detail_parts.append(f"身强遇食财运 +0.5")
                elif shen_score >= 40 and shen_score < 60:
                    if dy_gan_ss in ("正印", "偏印", "比肩", "劫财"):
                        dy_bonus += 0.3
                        dy_detail_parts.append(f"中和遇印比运 +0.3")
    
    dy_bonus = min(dy_bonus, 3.0)  # cap at 3.0
    raw_score += dy_bonus
    details.append(f"④大运窗口: {'、'.join(dy_detail_parts) if dy_detail_parts else '无显著窗口'} (合计+{dy_bonus:.1f})")
    
    # ── 五维度调校 ──
    # 印星透干加成（月干/时干）
    for pos, gan in [("月干", yue_gan), ("时干", shi_gan)]:
        if shi_shen(ri_gan, gan) in ("正印", "偏印"):
            raw_score += 0.3
            details.append(f"印透{pos}({gan}) +0.3")
    
    # ── 从弱格特殊：靠食伤+官杀+文昌 ──
    if is_cong_ruo and not (yue_ben_ss in ("正印", "偏印")):
        # 从弱且月令无印：靠食伤悟性+官杀自律
        ss_bonus = 0.0
        for pos, gan, pts in [("月干", yue_gan, 0.8), ("年干", nian_gan, 0.5), ("时干", shi_gan, 0.5)]:
            g_ss = shi_shen(ri_gan, gan)
            if g_ss in ("食神", "伤官"):
                ss_bonus += pts
                details.append(f"从弱·{pos}({gan}){g_ss}(悟性) +{pts}")
            elif g_ss in ("正官", "七杀"):
                ss_bonus += pts * 0.7
                details.append(f"从弱·{pos}({gan}){g_ss}(自律) +{pts*0.7}")
        raw_score += ss_bonus
        cap_base = 5.5
    else:
        cap_base = 8.0
    
    # ── 最终分 ──
    raw_score = min(raw_score, cap_base)  # 原局基础 cap
    base_score = raw_score
    details.append(f"原局基础分: {base_score:.1f}/{cap_base}")
    
    # 大运赋能单独计算（0-3分）
    dy_bonus_final = min(dy_bonus, 3.0)
    total = base_score + dy_bonus_final
    total = min(max(total, 0.5), 10.0)
    details.append(f"大运赋能: +{dy_bonus_final:.1f}")
    details.append(f"总分: {total:.1f}/10")
    
    # 映射到0-100
    score_100 = round(total * 10, 1)
    
    # 等级判定
    if is_cong_ruo:
        if score_100 >= 50:
            level = "本科以上"
        elif score_100 >= 30:
            level = "中等学历"
        elif score_100 >= 15:
            level = "基础学历"
        else:
            level = "基础教育"
    else:
        if score_100 >= 70:
            level = "高学历"
        elif score_100 >= 45:
            level = "本科以上"
        elif score_100 >= 30:
            level = "中等学历"
        else:
            level = "基础教育"
    
    return {
        "score": score_100,
        "level": level,
        "details": details,
        "_raw": {
            "base_score": round(base_score, 2),
            "dy_bonus": round(dy_bonus_final, 2),
            "total": round(total, 2),
        }
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 事业评分
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calc_shi_ye(ge_ju: str, shen_qiang: dict, da_yun_scores: list,
                tian_gan_list: list = None, ri_gan: str = None, yue_zhi: str = None) -> dict:
    """事业评分 v8.1
    从弱格(从官杀/从财)：顶级大富大贵格局
    常规格局：基于格局+身强弱+最佳大运
    新增v8.1：恶神制化检测 + 三大伟人格加分"""
    # 格局基础分（含从格）
    gj_scores = {
        "正官格": 8, "从弱格": 8,  # 从官杀→顶级
        "七杀格": 7, "正印格": 7, "偏印格": 6,
        "正财格": 7, "偏财格": 6, "食神格": 6, "伤官格": 5,
        "从强格": 7, "专旺格": 8,
        "化气格": 7,
    }
    base = gj_scores.get(ge_ju, 5)
    
    # 身强弱修正
    sq_level = shen_qiang.get("level", "")
    sq = shen_qiang.get("score", 50)
    
    if sq_level == "从弱":
        shen_mod = 2  # 从弱反强，压力越大成就越高
    elif 40 <= sq <= 70:
        shen_mod = 2  # 中和最佳
    elif sq >= 30:
        shen_mod = 1
    else:
        shen_mod = 0  # 过弱
    
    # 最佳大运加成
    best_dy = max((d.get("score", 0) for d in da_yun_scores), default=0)
    dy_mod = 2 if best_dy >= 7.5 else 1 if best_dy >= 5 else 0
    
    # ── 恶神制化检测 v8.1 ──
    evil_mod = 0
    evil_details = []
    
    if tian_gan_list and ri_gan:
        # 检查天干七杀
        has_qi_sha = False
        for tg in tian_gan_list:
            if tg and shi_shen(ri_gan, tg) == "七杀":
                has_qi_sha = True
                break
        
        # 检查天干食神（食神制杀）/ 印星（杀印相生/偏印化杀）
        has_shi_shen_zhi = False
        has_yin_xing = False
        for tg in tian_gan_list:
            if tg:
                ss = shi_shen(ri_gan, tg)
                if ss in ("食神", "伤官"):
                    has_shi_shen_zhi = True
                elif ss in ("正印", "偏印"):
                    has_yin_xing = True
        
        if has_qi_sha:
            # 七杀有制（食神制杀或印星转化）→ 加2分顶级
            if has_shi_shen_zhi or has_yin_xing:
                evil_mod += 2
                evil_details.append("七杀有制+2")
            # 七杀无制但身强 → 杀身两停加分
            elif sq_level == "身强" or (40 <= sq <= 70):
                evil_mod += 1
                evil_details.append("杀身两停+1")
            
            # 三大伟人格检测
            if has_yin_xing and has_qi_sha:
                # 杀印相生 → 加1分
                evil_mod += 1
                evil_details.append("杀印相生+1")
            if has_shi_shen_zhi and has_qi_sha:
                # 食神制杀 → 加1分
                evil_mod += 1
                evil_details.append("食神制杀+1")
    
    # 身弱修正采用乘法（乘法替加法）：身强/从弱者基础分乘以更大系数
    shen_factor = 1.0 + shen_mod * 0.15  # shen_mod=0→1.0, =1→1.15, =2→1.30
    total = base * shen_factor + dy_mod + evil_mod
    
    # ── 年干伤官负信号（学业维度） ──
    nian_sg_penalty = 0
    nian_sg_detail = ""
    if tian_gan_list and ri_gan and len(tian_gan_list) >= 4:
        nian_gan = tian_gan_list[0]
        if nian_gan and shi_shen(ri_gan, nian_gan) == "伤官":
            nian_sg_penalty = -2
            nian_sg_detail = "年干伤官强负信号-2"
    
    # 等级判定（含恶神制化后的升级）
    if total >= 12:
        level = "顶级/统帅级"
    elif total >= 10:
        level = "高层管理/专家级"
    elif total >= 8:
        level = "中高层管理"
    elif total >= 6:
        level = "中层管理/专业人士"
    elif total >= 4:
        level = "基层/稳定工作"
    else:
        level = "普通工作"
    
    return {"score": round(total * 10, 1), "level": level,
            "base_score": base, "shen_mod": shen_mod, "shen_factor": round(shen_factor, 2),
            "dy_mod": dy_mod,
            "evil_mod": evil_mod, "evil_details": evil_details,
            "nian_sg_penalty": nian_sg_penalty, "nian_sg_detail": nian_sg_detail}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 婚姻分析引擎 v1.0
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calc_hunyin(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                gender: int = 1, xi_shen: list = None,
                ji_shen: list = None) -> dict:
    """
    婚姻分析引擎 v1.0
    基于金鉴真人·婚姻子女断事体系

    规则来源：
    - 婚姻子女知识点提取报告.md
    - 金鉴真人_婚姻子女重点事件断事体系大全_补遗v1.0_20260606.md
    - bazi-marriage-analysis/SKILL.md

    返回值：
      {"fuqi_xing": "正财/正官",
       "fuqi_gong": {"zhi": "酉", "status": "喜/忌/冲/刑/害/破", "score": 0-100},
       "guan_sha_hun_za": False,
       "shang_guan_jian_guan": False,
       "ru_mu": False,
       "score": 75,
       "level": "良好",
       "details": [...]}
    """
    if xi_shen is None:
        xi_shen = []
    if ji_shen is None:
        ji_shen = []

    details = []
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_idx = WX_ORDER.index(ri_wx)

    # ── 1. 夫妻星定位 ──
    is_male = (gender == 1)
    if is_male:
        # 男命：正财=妻星，偏财=偏缘
        fuqi_wx = WX_ORDER[(ri_idx + 2) % 5]  # 我克者财
        fuqi_xing = "正财"
        fuqi_alt = "偏财"
        fuqi_label = "妻星"
    else:
        # 女命：正官=夫星，七杀=偏缘
        fuqi_wx = WX_ORDER[(ri_idx + 3) % 5]  # 克我者官杀
        fuqi_xing = "正官"
        fuqi_alt = "七杀"
        fuqi_label = "夫星"

    # 检测天干是否有夫妻星
    tian_gan_list = [nian_gan, yue_gan, shi_gan]
    fuqi_tg_found = False
    for tg in tian_gan_list:
        if tg:
            tg_ss = shi_shen(ri_gan, tg)
            if tg_ss == fuqi_xing:
                fuqi_tg_found = True
                details.append(f"天干{tg}为{fuqi_xing}({fuqi_label})透出")
            elif tg_ss == fuqi_alt:
                details.append(f"天干{tg}为{fuqi_alt}(偏{fuqi_label})")

    # 检测地支是否有夫妻星（藏干）
    all_zhi = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    fuqi_score = 0
    for zhi in all_zhi:
        for cg, wt in DI_ZHI_CANG_GAN[zhi]:
            cg_ss = shi_shen(ri_gan, cg)
            if cg_ss == fuqi_xing:
                fuqi_score += wt / 100
                details.append(f"地支{zhi}藏{cg}为{fuqi_xing}({fuqi_label}) 权重{wt}%")
            elif cg_ss == fuqi_alt:
                fuqi_score += wt / 200  # 偏星权重减半
                details.append(f"地支{zhi}藏{cg}为{fuqi_alt}(偏{fuqi_label}) 权重{wt}%")

    fuqi_xing_actual = fuqi_xing
    if not fuqi_tg_found and fuqi_score < 0.5:
        # 无正夫妻星，看替代
        for tg in tian_gan_list:
            if tg:
                tg_ss = shi_shen(ri_gan, tg)
                if tg_ss == fuqi_alt:
                    fuqi_xing_actual = fuqi_alt
                    details.append(f"无{fuqi_xing}，以{fuqi_alt}为{fuqi_label}")
                    break
        else:
            # 官杀皆无→看夫妻宫
            ri_zhi_ss = shi_shen(ri_gan, DI_ZHI_CANG_GAN[ri_zhi][0][0])
            details.append(f"无{fuqi_xing}/{fuqi_alt}，看夫妻宫十神{ri_zhi_ss}")

    # ── 2. 夫妻宫（日支）喜忌判定 ──
    ri_zhi_wx = DI_ZHI_WU_XING[ri_zhi]
    ri_zhi_ss = shi_shen(ri_gan, DI_ZHI_CANG_GAN[ri_zhi][0][0])
    
    fuqi_gong_status = "中"
    if ri_zhi_wx in xi_shen:
        fuqi_gong_status = "喜"
        details.append(f"日支{ri_zhi}({ri_zhi_wx})为喜用神，夫妻宫吉利")
    elif ri_zhi_wx in ji_shen:
        fuqi_gong_status = "忌"
        details.append(f"日支{ri_zhi}({ri_zhi_wx})为忌神，夫妻宫不利")

    # ── 3. 夫妻宫刑冲害破检测 ──
    fuqi_gong_score = 100
    for zhi in all_zhi:
        if zhi == ri_zhi:
            continue
        rel = calc_energy_relationship(ri_zhi, zhi)
        if rel and rel.get("type"):
            rtype = rel["type"]
            if rtype == "六冲":
                fuqi_gong_status += "+冲"
                fuqi_gong_score -= 70
                details.append(f"日支{ri_zhi}与{zhi}相冲，婚姻不稳定")
            elif rtype == "三刑":
                fuqi_gong_status += "+刑"
                fuqi_gong_score -= 50
                details.append(f"日支{ri_zhi}与{zhi}相刑，婚姻多矛盾")
            elif rtype == "六害":
                fuqi_gong_status += "+害"
                fuqi_gong_score -= 30
                details.append(f"日支{ri_zhi}与{zhi}相害，有第三者/小人")
            elif rtype == "六破":
                fuqi_gong_status += "+破"
                fuqi_gong_score -= 20
                details.append(f"日支{ri_zhi}与{zhi}相破，婚姻轻微不顺")
            elif rtype == "自刑":
                fuqi_gong_status += "+自刑"
                fuqi_gong_score -= 20
                details.append(f"日支{ri_zhi}自刑，婚姻自我纠结")

    # 日支十神扣分
    if is_male:
        if ri_zhi_ss == "比肩":
            fuqi_gong_score -= 10
            details.append("男命日支比肩，婚姻有竞争")
        elif ri_zhi_ss == "劫财":
            fuqi_gong_score -= 20
            details.append("男命日支劫财，离婚率较高")
    else:
        if ri_zhi_ss == "食神":
            fuqi_gong_score -= 10
            details.append("女命日支食神，欲望较强")
        elif ri_zhi_ss == "伤官":
            fuqi_gong_score -= 20
            details.append("女命日支伤官，女坐伤官必克夫")

    fuqi_gong_score = max(0, min(100, fuqi_gong_score))

    # ── 4. 官杀混杂检测（女命） ──
    guan_sha_hun_za = False
    if not is_male:
        has_zheng_guan = False
        has_qi_sha = False
        for tg in tian_gan_list:
            if tg:
                tg_ss = shi_shen(ri_gan, tg)
                if tg_ss == "正官":
                    has_zheng_guan = True
                elif tg_ss == "七杀":
                    has_qi_sha = True
        # 藏干也检查
        for zhi in all_zhi:
            for cg, wt in DI_ZHI_CANG_GAN[zhi]:
                cg_ss = shi_shen(ri_gan, cg)
                if cg_ss == "正官":
                    has_zheng_guan = True
                elif cg_ss == "七杀":
                    has_qi_sha = True
        if has_zheng_guan and has_qi_sha:
            guan_sha_hun_za = True
            details.append("官杀混杂（正官+七杀同时存在），感情复杂")
            fuqi_gong_score -= 20

    # ── 5. 伤官见官检测（女命） ──
    shang_guan_jian_guan = False
    if not is_male:
        has_shang_guan = False
        has_zheng_guan = False
        for tg in tian_gan_list:
            if tg:
                tg_ss = shi_shen(ri_gan, tg)
                if tg_ss == "伤官":
                    has_shang_guan = True
                elif tg_ss == "正官":
                    has_zheng_guan = True
        if has_shang_guan and has_zheng_guan:
            shang_guan_jian_guan = True
            details.append("伤官见官（天干同时有伤官和正官），婚姻最大考验")
            fuqi_gong_score -= 25

    # ── 6. 入墓检测（夫妻星能量<40分） ──
    ru_mu = False
    if fuqi_score < 0.4:
        ru_mu = True
        details.append(f"{fuqi_xing_actual}能量{fuqi_score:.1f}<0.4，入墓状态，{fuqi_label}缘分浅")

    # ── 7. 日支与日主生克关系（谁爱谁更多） ──
    # 日支的五行生日干的五行 → 配偶爱自己更多
    # 日干的五行生日支的五行 → 自己爱配偶更多
    if WX_SHENG.get(ri_zhi_wx) == ri_wx:
        details.append(f"日支{ri_zhi}({ri_zhi_wx})生日干{ri_gan}({ri_wx})，配偶爱你更多")
        fuqi_gong_score += 5
    elif WX_SHENG.get(ri_wx) == ri_zhi_wx:
        details.append(f"日干{ri_gan}({ri_wx})生日支{ri_zhi}({ri_zhi_wx})，你爱配偶更多")
        fuqi_gong_score += 2

    # ── 8. 整体评分和等级 ──
    score = min(100, max(0, fuqi_gong_score))
    if score >= 80:
        level = "优秀"
    elif score >= 65:
        level = "良好"
    elif score >= 50:
        level = "中平"
    else:
        level = "较差"

    fuqi_gong = {
        "zhi": ri_zhi,
        "shi_shen": ri_zhi_ss,
        "status": fuqi_gong_status,
        "score": fuqi_gong_score,
    }

    return {
        "fuqi_xing": fuqi_xing_actual,
        "fuqi_gong": fuqi_gong,
        "guan_sha_hun_za": guan_sha_hun_za,
        "shang_guan_jian_guan": shang_guan_jian_guan,
        "ru_mu": ru_mu,
        "score": score,
        "level": level,
        "details": details,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 主入口 v7.2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_bazi(year: int, month: int, day: int,
                   hour: int = 12, minute: int = 0,
                   is_lunar: bool = False, gender: int = 1) -> dict:
    """八字排盘主入口 v7.2"""
    # 农历转阳历（如适用）
    if is_lunar:
        try:
            lunar_d = lunardate.LunarDate(year, month, day)
            solar_d = lunar_d.toSolarDate()
            year, month, day = solar_d.year, solar_d.month, solar_d.day
        except Exception:
            pass  # 如果转换失败，继续使用原日期
    # 四柱
    ng, nz = get_nian_zhu(year, month, day)
    yg, yz = get_yue_zhu(year, month, day, ng)
    rg, rz = get_ri_zhu(year, month, day)
    sg, sz = get_shi_zhu(hour, minute, rg)
    
    ba_zi = f"{ng}{nz} {yg}{yz} {rg}{rz} {sg}{sz}"
    
    # 各柱详情
    def build_pillar(g, z, pos):
        cg_data = [{"gan":c,"weight":w,"shi_shen":shi_shen(rg,c),"wu_xing":TIAN_GAN_WU_XING[c]} for c,w in DI_ZHI_CANG_GAN[z]]
        return {"gan":g,"zhi":z,"gan_shi_shen":shi_shen(rg,g),
                "gan_wu_xing":TIAN_GAN_WU_XING[g],"zhi_wu_xing":DI_ZHI_WU_XING[z],
                "cang_gan":cg_data,"na_yin":na_yin(g,z),
                "kong_wang":kong_wang(g,z)}
    
    pillars = {"nian":build_pillar(ng,nz,"年"),"yue":build_pillar(yg,yz,"月"),
               "ri":build_pillar(rg,rz,"日"),"shi":build_pillar(sg,sz,"时")}
    
    # 分析
    sqr = calc_shen_qiang_ruo(rg, ng, yg, sg, nz, yz, rz, sz)

    # 先调用能量分析/专旺格检测（格局增强需要）
    wx_energy = calc_wu_xing_energy(ng, yg, rg, sg, nz, yz, rz, sz)
    wx_pcts = wx_energy.get("percentages", wx_energy) if isinstance(wx_energy, dict) else {}
    tian_gan_list = [ng, yg, rg, sg]
    zhi_list = [nz, yz, rz, sz]
    zhuan_wang = check_zhuan_wang_ge(rg, wx_pcts, sqr["score"],
                                      tian_gan_list=tian_gan_list, zhi_list=zhi_list)

    # 格局判定（v7.4：十大格局分级增强版）
    gj_dict = get_ge_ju(rg, yz, ng, yg, sg,
                         nian_zhi=nz, ri_zhi=rz, shi_zhi=sz,
                         sqr_level=sqr["level"],
                         zhuan_wang_flag=zhuan_wang.get("is_zhuan_wang", False))
    gj_str = gj_dict["ge_ju"]
    # 从弱格/从强格覆盖普通格局判定（P2修复：不覆盖已由top10判定的从官杀/从财）
    if sqr["level"] == "从弱":
        # 如果top10已判定（从官杀/从财有rank），保留原结果
        if gj_dict.get("rank") is None:
            gj_str = "从弱格"
            gj_dict["rank_name"] = "从弱格"
    elif sqr["level"] == "从强":
        gj_str = "从强格"
    # 专旺格覆盖
    if zhuan_wang.get("is_zhuan_wang") and gj_dict.get("rank") is None:
        gj_str = zhuan_wang.get("name", "专旺格")
        gj_dict["rank"] = 9
        gj_dict["rank_name"] = "专旺格"

    xys = get_xi_yong_shen(rg, sqr["level"], sqr["score"])
    dy = calc_da_yun(ng, nz, gender, year, month, day, hour, minute)
    cx = calc_cai_xing(rg, ng, yg, sg, nz, yz, rz, sz, sq_level=sqr["level"], sq_score=sqr["score"])
    ss_sha = calc_shensha(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    ss_flat = calc_all_shensha_with_positions(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    ss_summary = calc_shensha_summary(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    energy_analysis = calc_bazi_energy_analysis(rg, nz, yz, rz, sz, xys.get("xi_shen", []))
    
    # 新增功能 v8.3
    # 调候用神
    tiao_hou = calc_tiao_hou(rg, yz, tian_gan_list)
    # 通关用神
    tong_guan = calc_tong_guan(rg, wx_pcts)
    # 假旺真弱已删除（v9.0）——避免对身强弱评分造成数据污染
    # 化气格（P2：增加有根检查）
    hua_qi = check_hua_qi_ge(rg, tian_gan_list, yz, zhi_list=zhi_list)
    # P2新增：五行流通格检测
    wu_xing_liu_tong = check_wu_xing_liu_tong(rg, nz, yz, rz, sz, wx_pcts=wx_pcts)
    # P2新增：木火通明格检测
    mu_huo_tong_ming = check_mu_huo_tong_ming(rg, nz, yz, rz, sz, tian_gan_list=tian_gan_list)
    # 大运吉凶 v2.0（喜用神驱动评分）
    dy_list = dy.get("da_yun", [])
    da_yun_jx = calc_da_yun_ji_xiong(dy_list, rg, sqr["level"],
                                       xi_shen=xys.get("xi_shen", []),
                                       ji_shen=xys.get("ji_shen", []),
                                       nian_zhi=nz, ri_zhi=rz,
                                       yue_zhi=yz, shi_zhi=sz)
    # 合并大运评分到 dy.da_yun（供前端 progress bar 使用）
    if da_yun_jx and len(da_yun_jx) == len(dy_list):
        for i, d in enumerate(dy_list):
            if i < len(da_yun_jx):
                jx = da_yun_jx[i]
                d["score"] = jx.get("score", d.get("score", 5.0))
                d["score_first5"] = jx.get("score_first5", d.get("score_first5"))
                d["score_last5"] = jx.get("score_last5", d.get("score_last5"))
                d["ji_xiong_label"] = jx.get("ji_xiong", "平")
                d["gan_ss"] = jx.get("gan_ss", d.get("gan_ss", ""))
    # 财富量级（知识库六态矩阵法v8.0）
    cai_fu = calc_cai_fu_deng_ji(
        cx.get("score", 0), sqr["score"], sqr["level"],
        rg, gj_str,
        nian_gan=ng, yue_gan=yg, shi_gan=sg,
        has_ku=cx.get("has_ku", False)
    )
    # 财富等级以calc_cai_xing的九龙道长规则为准（身强财弱→中富等）
    # calc_cai_fu_deng_ji仅用于综合评分，不覆盖等级
    # 流年分析（当前年份及附近5年）
    current_year = datetime.now().year
    liu_nian_list = []
    for yn in range(current_year - 2, current_year + 4):
        ln = calc_liu_nian(yn, rg, dy_list,
                               nian_gan=ng, nian_zhi=nz,
                               yue_gan=yg, yue_zhi=yz,
                               ri_zhi=rz,
                               shi_gan=sg, shi_zhi=sz)
        if ln:
            ln["year"] = yn
            liu_nian_list.append(ln)

    # 学历评分 v8.0（第0层年柱有印三档法+六步排查+从弱格特殊处理）
    dy_list = dy.get("da_yun", []) if isinstance(dy, dict) else []
    xy = calc_xue_ye(rg, ng, yg, sg, nz, yz, rz, sz,
                     ge_ju=gj_str, shen_score=sqr["score"], da_yun_list=dy_list,
                     sqr_level=sqr["level"])

    # 婚姻分析引擎 v1.0
    hunyin = calc_hunyin(rg, ng, yg, sg, nz, yz, rz, sz,
                          gender=gender,
                          xi_shen=xys.get("xi_shen", []),
                          ji_shen=xys.get("ji_shen", []))

    basic = {"ba_zi":ba_zi,"ri_zhu":rg+rz,"ri_gan":rg,"ri_zhi":rz,
             "nian_gan":ng,"nian_zhi":nz,"yue_gan":yg,"yue_zhi":yz,
             "shi_gan":sg,"shi_zhi":sz,
             "gender":"男" if gender==1 else "女",
             "solar_date":f"{year}年{month}月{day}日",
             "pillars":pillars,
             "shensha":ss_sha,
             "shensha_flat":ss_flat}

    analysis = {"shen_qiang_ruo":sqr,"ge_ju":gj_str,"ge_ju_detail":gj_dict,
                "xi_yong_shen":xys,
                "cai_xing":cx,"da_yun":dy,"wu_xing_energy":wx_energy,
                "shensha_summary":ss_summary,"energy_analysis":energy_analysis,
                "tiao_hou":tiao_hou,"tong_guan":tong_guan,
                "zhuan_wang_ge":zhuan_wang,
                "hua_qi_ge":hua_qi,"da_yun_ji_xiong":da_yun_jx,
                "wu_xing_liu_tong_ge":wu_xing_liu_tong,
                "mu_huo_tong_ming_ge":mu_huo_tong_ming,
                "cai_fu_deng_ji":cai_fu,"cai_yun":cai_fu,
                "liu_nian":liu_nian_list,
                "xue_ye":xy,"shi_ye":calc_shi_ye(gj_str, sqr, da_yun_jx),
                "hun_yin":hunyin}
    
    return {"basic":basic,"analysis":analysis}
