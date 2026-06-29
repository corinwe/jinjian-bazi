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

TIAN_GAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DI_ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

TIAN_GAN_WU_XING = {g:w for g,w in zip(TIAN_GAN, ["木","木","火","火","土","土","金","金","水","水"])}
DI_ZHI_WU_XING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}

# 藏干权重：本气100% / 中气60% / 余气30%
DI_ZHI_CANG_GAN = {
    "子":[("癸",100)],"丑":[("己",100),("癸",60),("辛",30)],
    "寅":[("甲",100),("丙",60),("戊",30)],"卯":[("乙",100)],
    "辰":[("戊",100),("乙",60),("癸",30)],"巳":[("丙",100),("戊",60),("庚",30)],
    "午":[("丁",100),("己",60)],"未":[("己",100),("丁",60),("乙",30)],
    "申":[("庚",100),("壬",60),("戊",30)],"酉":[("辛",100)],
    "戌":[("戊",100),("辛",60),("丁",30)],"亥":[("壬",100),("甲",60)],
}

WX_ORDER = ["木","火","土","金","水"]
# 五行生克关系（从日主视角：生我者/克我者/我生者）
WX_SHENG = {"木":"水","火":"木","土":"火","金":"土","水":"金"}  # 谁生日主：水生木，木生火...
WX_KE = {"木":"金","火":"水","土":"木","金":"火","水":"土"}    # 谁克日主：金克木，水克火...

# 五虎遁月
WU_HU_DUN_YUE = {"甲":"丙","乙":"戊","丙":"庚","丁":"壬","戊":"甲",
                  "己":"丙","庚":"戊","辛":"庚","壬":"壬","癸":"甲"}
# 五鼠遁时
WU_SHU_DUN_SHI = {"甲":"甲","乙":"丙","丙":"戊","丁":"庚","戊":"壬",
                   "己":"甲","庚":"丙","辛":"戊","壬":"庚","癸":"壬"}

# 六合
LIU_HE = {"子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯",
           "辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"}

# 三合
SAN_HE = {frozenset(["申","子","辰"]):"水", frozenset(["亥","卯","未"]):"木",
           frozenset(["寅","午","戌"]):"火", frozenset(["巳","酉","丑"]):"金"}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

def get_bian_xing_wu_xing(zhi: str, zhi_list: list) -> str | None:
    """辰戌丑未五行变性检测
    返回变性后的五行，若无变性则返回None
    """
    if zhi not in BIAN_XING_RULES:
        return None
    rule = BIAN_XING_RULES[zhi]
    zhi_set = set(zhi_list)
    if rule["trigger"].issubset(zhi_set):
        return rule["to_wx"]
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


# 燥土地支（未/戌）
ZAO_TU = {"未","戌"}

# ── 六害（六穿）：子未·丑午·寅巳·卯辰·申亥·酉戌 ──
LIU_HAI = {"子":"未","丑":"午","寅":"巳","卯":"辰","辰":"卯","巳":"寅",
            "午":"丑","未":"子","申":"亥","酉":"戌","戌":"酉","亥":"申"}

# ── 六破：子酉·寅亥·辰丑·午卯·申巳·戌未 ──
LIU_PO = {"子":"酉","丑":"辰","寅":"亥","卯":"午","辰":"丑","巳":"申",
           "午":"卯","未":"戌","申":"巳","酉":"子","戌":"未","亥":"寅"}

# ── 天干五合：甲己·乙庚·丙辛·丁壬·戊癸 ──
GAN_WU_HE = {
    "甲":"己","己":"甲","乙":"庚","庚":"乙",
    "丙":"辛","辛":"丙","丁":"壬","壬":"丁",
    "戊":"癸","癸":"戊",
}

# ── 三会局 ──
SAN_HUI = {frozenset(["寅","卯","辰"]):"木", frozenset(["巳","午","未"]):"火",
           frozenset(["申","酉","戌"]):"金", frozenset(["亥","子","丑"]):"水"}

# ── 自刑地支 ──
ZI_XING = {"辰","午","酉","亥"}

# ── 能量倍数（总纲v1.0）──
ENERGY_MULTIPLIER = {
    "三会": 20, "三合": 15, "三刑": 15, "六冲": 10,
    "六合": 10, "半三合": 10, "六害": 5, "六破": 3,
    "自刑": 10, "透干": 3, "空亡": 0.5,
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 60甲子纳音表（完整60柱）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NA_YIN = [
    "海中金","海中金","炉中火","炉中火","大林木","大林木",
    "路旁土","路旁土","剑锋金","剑锋金",
    "山头火","山头火","涧下水","涧下水","城头土","城头土",
    "白蜡金","白蜡金","杨柳木","杨柳木",
    "泉中水","泉中水","屋上土","屋上土","霹雳火","霹雳火",
    "松柏木","松柏木","长流水","长流水",
    "沙中金","沙中金","山下火","山下火","平地木","平地木",
    "壁上土","壁上土","金箔金","金箔金",
    "佛灯火","佛灯火","天河水","天河水","大驿土","大驿土",
    "钗钏金","钗钏金","桑柘木","桑柘木",
    "大溪水","大溪水","沙中土","沙中土","天上火","天上火",
    "石榴木","石榴木","大海水","大海水",
]

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

def check_san_he(zhi_list: list) -> tuple:
    """
    检查三合局。返回 (局名, 是否完整, 能量倍数)
    完整三合15倍，半三合7倍
    """
    zhi_set = set(zhi_list)
    for he_set, wx in SAN_HE.items():
        present = zhi_set.intersection(he_set)
        if len(present) == 3:
            return (wx, True, 15)
        elif len(present) >= 2:
            return (wx, False, 7)
    return ("", False, 1)

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


def check_san_hui(zhi_list: list) -> tuple:
    """检查三会局。返回 (五行, 是否完整, 能量倍数)"""
    zhi_set = set(zhi_list)
    for he_set, wx in SAN_HUI.items():
        present = zhi_set.intersection(he_set)
        if len(present) == 3:
            return (wx, True, ENERGY_MULTIPLIER["三会"])
        elif len(present) >= 2:
            return (wx, False, ENERGY_MULTIPLIER["半三合"] if len(present)==2 else 1)
    return ("", False, 1)


def check_san_xing(zhi_list: list) -> list:
    """检查三刑（不含自刑），返回所有三刑组合及类型
    自刑由calc_energy_relationship的pairwise检测处理，避免重复计数"""
    results = []
    zhi_set = set(zhi_list)
    # 寅巳申三刑
    if {"寅","巳","申"}.issubset(zhi_set):
        results.append(("寅巳申三刑", "无恩之刑", ENERGY_MULTIPLIER["三刑"]))
    # 丑未戌三刑
    if {"丑","未","戌"}.issubset(zhi_set):
        results.append(("丑未戌三刑", "恃势之刑", ENERGY_MULTIPLIER["三刑"]))
    # 子卯刑
    if {"子","卯"}.issubset(zhi_set):
        results.append(("子卯刑", "无礼之刑", ENERGY_MULTIPLIER["三刑"]))
    return results


def calc_energy_relationship(zhi_a: str, zhi_b: str) -> dict:
    """计算两个地支之间的能量关系
    返回 {"type":关系类型, "name":关系名称, "multiplier":能量倍数, "detail":描述}"""
    # 六冲
    if LIU_CHONG.get(zhi_a) == zhi_b:
        wx_a = DI_ZHI_WU_XING[zhi_a]
        wx_b = DI_ZHI_WU_XING[zhi_b]
        return {"type":"六冲", "name":f"{zhi_a}{zhi_b}冲", "multiplier":ENERGY_MULTIPLIER["六冲"],
                "detail":f"{zhi_a}与{zhi_b}相冲({wx_a}冲{wx_b})"}
    # 六合
    if LIU_HE.get(zhi_a) == zhi_b:
        return {"type":"六合", "name":f"{zhi_a}{zhi_b}合", "multiplier":ENERGY_MULTIPLIER["六合"],
                "detail":f"{zhi_a}与{zhi_b}六合"}
    # 六害
    if LIU_HAI.get(zhi_a) == zhi_b:
        return {"type":"六害", "name":f"{zhi_a}{zhi_b}害", "multiplier":ENERGY_MULTIPLIER["六害"],
                "detail":f"{zhi_a}与{zhi_b}相害"}
    # 六破
    if LIU_PO.get(zhi_a) == zhi_b:
        return {"type":"六破", "name":f"{zhi_a}{zhi_b}破", "multiplier":ENERGY_MULTIPLIER["六破"],
                "detail":f"{zhi_a}与{zhi_b}相破"}
    # 三刑
    for pair_key, (z1, z2) in [("子卯",("子","卯")),("寅巳",("寅","巳")),("巳申",("巳","申")),
                                ("丑未",("丑","未")),("未戌",("未","戌")),("丑戌",("丑","戌"))]:
        if {zhi_a, zhi_b} == {z1, z2}:
            xing_name = "无礼之刑" if "子" in pair_key else "无恩之刑" if "寅" in pair_key or "巳" in pair_key or "申" in pair_key else "恃势之刑"
            return {"type":"三刑", "name":f"{zhi_a}{zhi_b}刑", "multiplier":ENERGY_MULTIPLIER["三刑"],
                    "detail":f"{zhi_a}与{zhi_b}相刑({xing_name})"}
    # 自刑
    if zhi_a == zhi_b and zhi_a in ZI_XING:
        return {"type":"自刑", "name":f"{zhi_a}自刑", "multiplier":ENERGY_MULTIPLIER["自刑"],
                "detail":f"{zhi_a}自刑"}
    return {}


def calc_bazi_energy_analysis(ri_gan: str, nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                               xi_shen: list = None) -> dict:
    """八字全局能量分析
    计算四柱地支之间的全部刑冲合害破关系及能量倍数
    返回完整的关系列表和能量汇总
    
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
        "自刑": -50,
        "三合局": 15,    # 完整三合正加成
        "半三合": 7,     # 半三合正加成
        "三会局": 0,     # 三会局无额外伤害/加成
        "六合": 0,       # 六合无伤害
    }
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    positions = ["年支","月支","日支","时支"]
    results = []
    total_energy = 0
    total_damage = 0

    # 两两检查
    for i in range(4):
        for j in range(i+1, 4):
            rel = calc_energy_relationship(zhi_list[i], zhi_list[j])
            if rel:
                rel["zhi_a_pos"] = positions[i]
                rel["zhi_b_pos"] = positions[j]
                rel["zhi_a"] = zhi_list[i]
                rel["zhi_b"] = zhi_list[j]
                # 计算伤害分
                rel_type = rel.get("type", "")
                rel["damage_score"] = DAMAGE_SCORE.get(rel_type, 0)
                results.append(rel)
                total_energy += rel["multiplier"]
                total_damage += rel["damage_score"]

    # 三合局检查(完整三合)
    sh_wx, sh_complete, sh_mult = check_san_he(zhi_list)
    if sh_complete:
        results.append({"type":"三合局", "name":f"{sh_wx}三合局", "multiplier":sh_mult,
                        "detail":f"地支构成{sh_wx}三合局 +{sh_mult}倍",
                        "damage_score": DAMAGE_SCORE["三合局"]})
        total_energy += sh_mult
        total_damage += DAMAGE_SCORE["三合局"]
    # 半三合
    elif sh_mult > 1:
        results.append({"type":"半三合", "name":f"{sh_wx}半三合", "multiplier":sh_mult,
                        "detail":f"地支构成{sh_wx}半三合 +{sh_mult}倍",
                        "damage_score": DAMAGE_SCORE["半三合"]})
        total_energy += sh_mult
        total_damage += DAMAGE_SCORE["半三合"]

    # 三会局检查
    hui_wx, hui_complete, hui_mult = check_san_hui(zhi_list)
    if hui_complete:
        results.append({"type":"三会局", "name":f"{hui_wx}三会局", "multiplier":hui_mult,
                        "detail":f"地支构成{hui_wx}三会局 +{hui_mult}倍",
                        "damage_score": DAMAGE_SCORE.get("三会局", 0)})
        total_energy += hui_mult

    # 三刑检查
    xing_results = check_san_xing(zhi_list)
    for xr in xing_results:
        results.append({"type":"三刑", "name":xr[0], "multiplier":xr[2],
                        "detail":f"{xr[0]}({xr[1]}) +{xr[2]}倍",
                        "damage_score": DAMAGE_SCORE["三刑"]})
        total_energy += xr[2]
        total_damage += DAMAGE_SCORE["三刑"]

    # 空亡减半
    # (空亡在排盘阶段已计算，此处标记)
    # 汇总
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
# 身强弱评分（金鉴真人原始规则 v7.0）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 位置基础分（满分100，日干不计）
POS_SCORE = {'nian_gan':8,'nian_zhi':4,'yue_gan':12,'yue_zhi':40,'ri_zhi':12,'shi_gan':12,'shi_zhi':12}

def calc_shen_qiang_ruo(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                         nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str) -> dict:
    """
    身强弱评分 v7.0
    规则（金鉴真人原始规则）：
    - 印只在月令本气计分（40分）
    - 比劫在所有位置都计分
    - 燥土规则：未/戌对金日主，火引化时不记分（v7.0新增）
    - 从弱=0分→恒定50分，从强=>100分→恒定20分
    - 自坐比劫永不从弱（v7.0新增）
    - 三段式：<40身弱, 40-60中和, >60身强
    """
    tian_gan_list = [nian_gan, yue_gan, ri_gan, shi_gan]
    
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_idx = WX_ORDER.index(ri_wx)
    yin_wx = WX_ORDER[(ri_idx+4)%5]   # 生我=印
    bi_wx = WX_ORDER[ri_idx]           # 同我=比劫
    
    score = 0.0
    details = []
    
    # 1. 月令本气（含燥土规则）
    yz_ben = DI_ZHI_CANG_GAN[yue_zhi][0][0]
    yz_ben_wx = TIAN_GAN_WU_XING[yz_ben]
    yz_effective = is_zao_tu_effective(yue_zhi, ri_gan, tian_gan_list)
    
    yue_ling_score = 0.0
    
    if yz_ben_wx == yin_wx and yz_effective:
        yue_ling_score += 40; score += 40; details.append(f"月令本气印({yz_ben}) +40")
    elif yz_ben_wx == bi_wx and yz_effective:
        yue_ling_score += 40; score += 40; details.append(f"月令本气比劫({yz_ben}) +40")
    
    # 2. 月令中/余气（比劫才计分，印不计）
    for cg, wt in DI_ZHI_CANG_GAN[yue_zhi]:
        if TIAN_GAN_WU_XING[cg] == bi_wx and cg != yz_ben:
            p = 40 * wt / 100
            yue_ling_score += p
            score += p; details.append(f"月令藏干比劫({cg}) +{p:.1f}")
    
    # 月令空亡检查：月令逢空亡，月令分数减半
    yz_kong = kong_wang(yue_gan, yue_zhi)
    if yue_zhi in yz_kong and yue_ling_score > 0:
        score -= yue_ling_score / 2
        details.append(f"月令({yue_zhi})逢空亡({','.join(yz_kong)})，月令分数减半 -{yue_ling_score/2:.1f}")
    
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
    
    # 5. 日支自坐比劫永不从弱
    ri_zi_zuo_bi_jie = False
    for cg, wt in DI_ZHI_CANG_GAN[ri_zhi]:
        if TIAN_GAN_WU_XING[cg] == bi_wx:
            ri_zi_zuo_bi_jie = True
            break

    # 5b. 三合局能量加成（v7.0版）
    # 完整三合局(3个)与日主同五行 → +15分
    # 半三合局(2个)与日主同五行 → +7分
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    he_name, he_complete, he_mult = check_san_he(zhi_list)
    if he_name and he_complete and he_name == ri_wx:
        score += 15
        details.append(f"三合局({he_name})与日主同五行 +15")
    elif he_name and not he_complete and he_name == ri_wx:
        score += 7
        details.append(f"半三合局({he_name})与日主同五行 +7")

    # 6. 从格 + 三段式（v7.0：自坐比劫永不从弱）
    if score <= 0 and not ri_zi_zuo_bi_jie:
        return {"score": 50.0, "level": "从弱", "details": details}
    if score <= 0 and ri_zi_zuo_bi_jie:
        score = 20.0  # 自坐比劫给最低身弱分
    if score > 100:
        return {"score": 20.0, "level": "从强", "details": details}
    if score < 40:
        return {"score": round(score,1), "level": "身弱", "details": details}
    if score <= 60:
        return {"score": round(score,1), "level": "中和", "details": details}
    return {"score": round(score,1), "level": "身强", "details": details}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 格局 v7.0（透干定格局·比劫不入格局）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 正八格（比肩/劫财不入格局，遇之降级查中气/余气）
ZHENG_BA_GE = {"食神","伤官","正财","偏财","正官","七杀","正印","偏印"}

GE_JU_NAME = {"食神":"食神格","伤官":"伤官格",
              "正财":"正财格","偏财":"偏财格",
              "正官":"正官格","七杀":"七杀格",
              "正印":"正印格","偏印":"偏印格"}

# ── 十大格局排名表 ──
TOP_10_GE_JU = [
    (1, "食神制杀格/杀印相生",
     "食神+七杀同时出现（食神制杀）或印星+七杀（杀印相生）"),
    (2, "伤官配印格",
     "伤官+印星同时出现"),
    (3, "财官双美格",
     "正官/七杀+财星同时出现且相生"),
    (4, "从官杀格",
     "从弱格+官杀为主要克泄"),
    (5, "从财格",
     "从弱格+财星为主要克泄"),
    (6, "官印相生格",
     "正官+正印相生"),
    (7, "食伤生财格",
     "食伤+财星同时出现"),
    (8, "五行流通格",
     "五行无冲无克，用神得生扶"),
    (9, "专旺格",
     "全局五行专旺"),
    (10, "木火通明格",
     "木火两旺+无水破局"),
]

# 格局名 → (rank, rank_name) 映射（仅对正八格）
GE_JU_RANK_MAP = {
    "食神格": (1, "食神制杀格/杀印相生"),
    "伤官格": (2, "伤官配印格"),
    "正官格": (3, "财官双美格"),
    "七杀格": (3, "财官双美格"),
    "正财格": (3, "财官双美格"),
    "偏财格": (3, "财官双美格"),
    "正印格": (6, "官印相生格"),
    "偏印格": (6, "官印相生格"),
}


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

    # ════════════════════════════════════════════
    # 检测逻辑（按优先级从高到低）
    # ════════════════════════════════════════════

    # ── 第9名：专旺格 ──
    if zhuan_wang_flag:
        rank = 9
        rank_name = "专旺格"
        details.append("全局五行专旺，构成专旺格")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 从弱格细化（P2修复）：按最强者判定 ──
    if sqr_level == "从弱":
        # 官杀最强 → 从官杀（第4名）
        if has_guan_sha:
            rank = 4
            rank_name = "从官杀格"
            details.append("从弱格，官杀旺相，从官杀格成立")
            return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}
        # 财星最强 → 从财（第5名）
        if has_cai and has_shi_shang:
            rank = 5
            rank_name = "从财格"
            details.append("从弱格，财星旺相，从财格成立")
            return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}
        # 食伤最强 → 从弱（普通，无rank）
        if has_shi_shang:
            details.append("从弱格，食伤为主，属普通从弱")
            # 不设rank，由calculate_bazi处理

    # ── 第10名：木火通明格（P2：使用专用函数） ──
    mu_huo_result = check_mu_huo_tong_ming(ri_gan, nian_zhi, yue_zhi, ri_zhi, shi_zhi,
                                           tian_gan_list=(tian_gan_list + [ri_gan]))
    if mu_huo_result.get("is_mu_huo_tong_ming"):
        rank = 10
        rank_name = "木火通明格"
        details.append(mu_huo_result["detail"])
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

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

    # ── 第2名：伤官配印格 ──
    if has_shang_guan and has_yin:
        rank = 2
        rank_name = "伤官配印格"
        details.append("伤官+印星同时出现，伤官配印格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第3名：财官双美格 ──
    if has_guan_sha and has_cai:
        rank = 3
        rank_name = "财官双美格"
        details.append("官杀+财星同时出现且相生，财官双美格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第6名：官印相生格 ──
    if has_zheng_guan and has_zheng_yin:
        rank = 6
        rank_name = "官印相生格"
        details.append("正官+正印相生，官印相生格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第7名：食伤生财格 ──
    if has_shi_shang and has_cai:
        rank = 7
        rank_name = "食伤生财格"
        details.append("食伤+财星同时出现，食伤生财格成立")
        return {"ge_ju": rank_name, "rank": rank, "rank_name": rank_name, "details": details}

    # ── 第8名：五行流通格（P2：使用专用函数） ──
    liu_tong_result = check_wu_xing_liu_tong(ri_gan, nian_zhi, yue_zhi, ri_zhi, shi_zhi)
    if liu_tong_result.get("is_liu_tong") and has_yin and has_shi_shang:
        # 无冲+无缺+有印+有食伤 → 五行流通格
        rank = 8
        rank_name = "五行流通格"
        details.append(liu_tong_result["detail"])
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
    elif shen_qiang_level in ("身强",):
        # 身强喜克泄耗：财 > 官 > 食伤
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
    else:  # 身弱
        xi = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
        ji = [WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+1)%5]]

    return {"xi_shen": xi, "yong_shen": [xi[0]], "ji_shen": ji}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 财星评分 v7.0（含财库）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 财库对应表：日主五行 → 对应的财库地支
# 木日主→丑(金库), 火日主→辰(水库), 土日主→辰(水库),
# 金日主→未(木库), 水日主→戌(火库)
CAI_KU_MAP = {"木":"丑","火":"辰","土":"辰","金":"未","水":"戌"}
KU_ZHI = {"辰","戌","丑","未"}

def calc_cai_xing(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                  nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                  sq_level: str = "") -> dict:
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
    
    # 从弱格：财星分数如实返回，不加额外加分
    # 从弱格的财星加分已在calc_cai_fu_deng_ji中处理
    # 知识库：从弱格"财得令+40分"指月令生财的情况
    # 但财星分数应该只反映原局，不预加从弱加成
    if sq_level == "从弱":
        pass  # 不加分，由财富等级评估函数处理
    
    # 财富五级（基于实际验证校准）
    if score >= 60: level = "大富"
    elif score >= 36: level = "中富"
    elif score >= 12: level = "小富"
    else: level = "贫穷"
    
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
TIAN_YI_GUI_REN = {
    "甲": {"丑","未"}, "戊": {"丑","未"}, "庚": {"丑","未"},
    "乙": {"申","子","辰"}, "己": {"申","子","辰"},
    "丙": {"亥","酉"}, "丁": {"亥","酉"},
    "壬": {"巳","卯"}, "癸": {"巳","卯"},
    "辛": {"寅","午"},
}

# 文昌贵人（以年干或日干查四支地支）
WEN_CHANG = {
    "甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申",
    "己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"
}

# 天德贵人（以月支查四柱天干）
TIAN_DE = {
    "寅":"丁","卯":"申","辰":"壬","巳":"辛","午":"亥","未":"甲",
    "申":"癸","酉":"寅","戌":"丙","亥":"乙","子":"巳","丑":"庚"
}

# 月德贵人（月支三合局见阳干）
YUE_DE = {
    frozenset(["寅","午","戌"]): "丙",
    frozenset(["申","子","辰"]): "壬",
    frozenset(["巳","酉","丑"]): "庚",
    frozenset(["亥","卯","未"]): "甲"
}

# 太极贵人（以年干或日干查四支地支）
TAI_JI = {
    "甲":{"子","午"}, "乙":{"子","午"},
    "丙":{"卯","酉"}, "丁":{"卯","酉"},
    "戊":{"辰","戌","丑","未"}, "己":{"辰","戌","丑","未"},
    "庚":{"寅","亥"}, "辛":{"寅","亥"},
    "壬":{"巳","申"}, "癸":{"巳","申"}
}

# 福星贵人（以年干或日干查四支地支）
FU_XING = {
    "甲":{"寅","子"}, "丙":{"寅","子"},
    "乙":{"卯","丑"}, "癸":{"卯","丑"},
    "戊":{"午","申"}, "庚":{"午","申"},
    "丁":{"巳","酉"}, "己":{"巳","酉"},
    "辛":{"未"}, "壬":{"辰"}
}

# 禄神（日干之临官位，查四支）
LU_SHEN = {
    "甲":"寅","乙":"卯","丙":"巳","丁":"午",
    "戊":"巳","己":"午","庚":"申","辛":"酉","壬":"亥","癸":"子"
}

# 华盖（三合局墓库）
HUA_GAI = {
    frozenset(["寅","午","戌"]): "戌",
    frozenset(["巳","酉","丑"]): "丑",
    frozenset(["申","子","辰"]): "辰",
    frozenset(["亥","卯","未"]): "未"
}

# 桃花/咸池（三合局咸池位）
TAO_HUA = {
    frozenset(["寅","午","戌"]): "卯",
    frozenset(["巳","酉","丑"]): "午",
    frozenset(["申","子","辰"]): "酉",
    frozenset(["亥","卯","未"]): "子"
}

# 驿马（三合局对冲之位）
YI_MA = {
    frozenset(["寅","午","戌"]): "申",
    frozenset(["巳","酉","丑"]): "亥",
    frozenset(["申","子","辰"]): "寅",
    frozenset(["亥","卯","未"]): "巳"
}

# 将星（三合局之中神）
JIANG_XING = {
    frozenset(["寅","午","戌"]): "午",
    frozenset(["巳","酉","丑"]): "酉",
    frozenset(["申","子","辰"]): "子",
    frozenset(["亥","卯","未"]): "卯"
}

# 灾煞（三合局中神对冲之字）
ZAI_SHA = {
    frozenset(["申","子","辰"]): "午",
    frozenset(["寅","午","戌"]): "子",
    frozenset(["巳","酉","丑"]): "卯",
    frozenset(["亥","卯","未"]): "酉"
}

# 血刃（以日干查四支地支）
# 阳干血刃=羊刃位(same as 帝旺), 阴干血刃=羊刃后一位
XUE_REN = {
    "甲":"卯","乙":"辰","丙":"午","丁":"未","戊":"午",
    "己":"未","庚":"酉","辛":"戌","壬":"子","癸":"丑"
}

# 孤辰寡宿（以年支查四支地支）
GU_CHEN_GUA_SU = {
    frozenset(["亥","子","丑"]): ("寅","戌"),  # 孤寅寡戌
    frozenset(["寅","卯","辰"]): ("巳","丑"),  # 孤巳寡丑
    frozenset(["巳","午","未"]): ("申","辰"),  # 孤申寡辰
    frozenset(["申","酉","戌"]): ("亥","未"),  # 孤亥寡未
}

# 红鸾（以年支查四支地支）
HONG_LUAN = {
    "子":"卯","丑":"寅","寅":"丑","卯":"子","辰":"亥","巳":"戌",
    "午":"酉","未":"申","申":"未","酉":"午","戌":"巳","亥":"辰"
}

# 天喜（红鸾对冲）
TIAN_XI = {
    "子":"酉","丑":"申","寅":"未","卯":"午","辰":"巳","巳":"辰",
    "午":"卯","未":"寅","申":"丑","酉":"子","戌":"亥","亥":"戌"
}


# 六冲表（用于流年分析）
LIU_CHONG = {
    "子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥",
    "午":"子","未":"丑","申":"寅","酉":"卯","戌":"辰","亥":"巳"
}

# 六害表
LIU_HAI = {
    "子":"未","丑":"午","寅":"巳","卯":"辰","辰":"卯","巳":"寅",
    "午":"丑","未":"子","申":"亥","酉":"戌","戌":"酉","亥":"申"
}

# 三刑表
SAN_XING_MAP = {
    "寅":"巳","巳":"申","申":"寅",  # 无恩之刑
    "丑":"未","未":"戌","戌":"丑",  # 恃势之刑
    "子":"卯","卯":"子",            # 无礼之刑
    "辰":"辰","午":"午","酉":"酉","亥":"亥"  # 自刑
}


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
TIAO_HOU_MONTHS = {
    "寅": {"tiao_hou": "丙火暖局", "wx": "火", "reason": "春寒木发，需火暖局"},
    "卯": {"tiao_hou": "丙火暖局", "wx": "火", "reason": "春寒木盛，需火暖局"},
    "辰": {"tiao_hou": "癸水润局", "wx": "水", "reason": "辰为湿土，需癸水润木"},
    "巳": {"tiao_hou": "壬水调候", "wx": "水", "reason": "巳月火旺，需壬水调候"},
    "午": {"tiao_hou": "癸水调候", "wx": "水", "reason": "午月火炎，需癸水调候"},
    "未": {"tiao_hou": "癸水润局", "wx": "水", "reason": "未月燥热，需癸水润局"},
    "申": {"tiao_hou": "壬水泄金", "wx": "水", "reason": "申月金旺，需壬水泄金"},
    "酉": {"tiao_hou": "癸水泄金", "wx": "水", "reason": "酉月金锐，需癸水泄金"},
    "戌": {"tiao_hou": "甲木疏土", "wx": "木", "reason": "戌月土燥，需甲木疏土"},
    "亥": {"tiao_hou": "丙火暖局", "wx": "火", "reason": "亥月水寒，需丙火暖局"},
    "子": {"tiao_hou": "丁火暖局", "wx": "火", "reason": "子月水冰，需丁火暖局"},
    "丑": {"tiao_hou": "丙火暖局", "wx": "火", "reason": "丑月寒湿，需丙火暖局"},
}

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
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_jia_wang_zhen_ruo(ri_gan: str, sqr_score: float, sqr_level: str,
                             nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str,
                             tian_gan_list: list, da_yun_gan: str = "") -> dict:
    """假旺真弱强制排查
    日主看似身强(印比多)，但地支被合冲耗泄，实际身弱
    返回 {"is_jia_wang": bool, "corrected_level": str, "corrected_score": float, "reason": str}"""
    reasons = []
    penalty = 0
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    
    # 1. 三合/三会耗身：地支组成消耗日主五行的三合局
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ke_wx = WX_KE[ri_wx]        # 克日主的五行
    
    # 检查三合局是否消耗日主
    wx_scores_raw = {wx: 0 for wx in WX_ORDER}
    for z in zhi_list:
        for cg, wt in DI_ZHI_CANG_GAN[z]:
            wx_scores_raw[TIAN_GAN_WU_XING[cg]] += wt
    
    # 2. 藏干攻击：月令/日支的藏干克日主
    for zhi_pos, zhi in [("月令", yue_zhi), ("日支", ri_zhi)]:
        for cg, _ in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cg] == ke_wx:
                penalty += 5
                reasons.append(f"{zhi_pos}藏干{cg}({ke_wx})攻身-5")
                break
    
    # 3. 月令遭克：月令被年干/月干/日支克制
    yue_gan = tian_gan_list[1] if len(tian_gan_list) > 1 else ""
    nian_gan = tian_gan_list[0] if tian_gan_list else ""
    ri_gan_tg = ri_gan  # ri_gan itself is in tian_gan_list
    for g in [nian_gan, yue_gan]:
        if g and TIAN_GAN_WU_XING.get(g) == ke_wx:
            penalty += 3
            reasons.append(f"月令被{g}({ke_wx})克制-3")
    
    # 4. 日主在地支的根被冲/害
    ri_zhi_wx = DI_ZHI_WU_XING[ri_zhi]
    for other_z in zhi_list:
        if other_z != ri_zhi:
            if LIU_CHONG.get(ri_zhi) == other_z:
                penalty += 8
                reasons.append(f"日支{ri_zhi}被{other_z}冲-8")
            if LIU_HAI.get(ri_zhi) == other_z:
                penalty += 5
                reasons.append(f"日支{ri_zhi}被{other_z}害-5")
    
    # 判断
    actual_score = sqr_score - penalty
    if penalty >= 10 and sqr_level in ("身强", "中和"):
        if actual_score < 40:
            return {
                "is_jia_wang": True,
                "corrected_level": "身弱",
                "corrected_score": max(0, actual_score),
                "reason": "假旺真弱：" + "；".join(reasons),
            }
    
    return {
        "is_jia_wang": False,
        "corrected_level": sqr_level,
        "corrected_score": sqr_score,
        "reason": "",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 专旺格 & 化气格
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ZHUAN_WANG_NAMES = {
    "木": "曲直格", "火": "炎上格",
    "土": "稼穑格", "金": "从革格", "水": "润下格",
}

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
HUA_QI_MAP = {
    ("甲", "己"): "土", ("己", "甲"): "土",
    ("乙", "庚"): "金", ("庚", "乙"): "金",
    ("丙", "辛"): "水", ("辛", "丙"): "水",
    ("丁", "壬"): "木", ("壬", "丁"): "木",
    ("戊", "癸"): "火", ("癸", "戊"): "火",
}

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
    """检查五行流通格
    理论：八字无冲克，五行循环相生，用神得生扶
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

    # 2. 检查五行齐全（每种五行都有占比>0）
    if wx_pcts:
        zero_wxs = [wx for wx, pct in wx_pcts.items() if pct <= 0]
        if zero_wxs:
            return {
                "is_liu_tong": False,
                "detail": f"缺少{''.join(zero_wxs)}，不构成五行流通格",
            }

    return {
        "is_liu_tong": True,
        "detail": "八字无冲克，五行齐全且循环流通，用神得生扶，五行流通格成立",
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
DA_YUN_JI_XIONG_TABLE = {
    "身强": {
        "正印": "凶（再生扶过旺）", "偏印": "凶",
        "比肩": "凶（身更强易刚愎）", "劫财": "凶",
        "食神": "平（消耗有度）", "伤官": "平~吉（泄秀显才）",
        "正财": "吉（财来就身）", "偏财": "吉",
        "正官": "吉（官星约身）", "七杀": "吉~平（有力为权）",
    },
    "身弱": {
        "正印": "吉（印来生身）", "偏印": "吉",
        "比肩": "吉（比助身旺）", "劫财": "吉",
        "食神": "凶（再泄身更弱）", "伤官": "凶",
        "正财": "凶（财耗身难担）", "偏财": "凶",
        "正官": "凶（官克身承压）", "七杀": "凶（杀攻身危）",
    },
    "中和": {
        "正印": "平", "偏印": "平",
        "比肩": "平", "劫财": "平",
        "食神": "吉（泄秀生财）", "伤官": "吉",
        "正财": "吉（财来相迎）", "偏财": "吉",
        "正官": "吉（官来相助）", "七杀": "平~吉",
    },
}

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
        # ═══════════════════════════════════════════════
        bonus = 1.5  # 默认中性
        
        # 2a. 喜用神效应
        gan_is_xi = gan_wx in xi
        gan_is_ji = gan_wx in ji
        zhi_is_xi = zwx in xi
        zhi_is_ji = zwx in ji
        
        if gan_is_xi:
            bonus += 0.5
            details.append(f"天干{gan}=喜用+0.5")
        elif gan_is_ji:
            bonus -= 0.3
            details.append(f"天干{gan}=忌神-0.3")
        
        if zhi_is_xi:
            bonus += 0.3
            details.append(f"地支{zhi}=喜用+0.3")
        elif zhi_is_ji:
            bonus -= 0.2
            details.append(f"地支{zhi}=忌神-0.2")
        
        # 2b. 十神交互效应（金鉴真人核心规则）
        # 伤官见官 → 减分
        if gan_ss == "伤官":
            if shi_shen(ri_gan, "癸") == "正官" or shi_shen(ri_gan, "壬") == "七杀":
                bonus -= 0.5
                details.append("伤官见官-0.5")
        
        # 食神制杀 → 加分（七杀大运+食神地支）
        if gan_ss == "七杀" and zhi_is_xi:
            # 地支为食神或伤官星 = 食神制杀
            zhi_cang = DI_ZHI_CANG_GAN.get(zhi, [])
            zhi_has_shi_shen = any(shi_shen(ri_gan, cg) in ("食神", "伤官") for cg, _ in zhi_cang)
            if zhi_has_shi_shen:
                bonus += 0.3
                details.append(f"食神制杀+0.3")
        
        # 财星生官 → 加分（财生官，事业提升）
        if gan_ss in ("正财", "偏财") and zhi_is_xi:
            bonus += 0.2
            details.append(f"财生官+0.2")
        
        # 2c. 刑冲合害效应
        # 冲年柱 → 根基动摇
        if nian_zhi and liu_chong.get(zhi) == nian_zhi:
            bonus -= 0.5
            details.append(f"冲年柱{nian_zhi}-0.5")
        
        # 冲日柱 → 婚姻宫/自身受冲
        if ri_zhi and liu_chong.get(zhi) == ri_zhi:
            bonus -= 0.3
            details.append(f"冲日柱{ri_zhi}-0.3")
        
        # 刑（丑戌刑、寅巳刑、巳亥刑复杂组合）
        liu_xing_pairs = [("丑","戌"),("戌","丑"),("寅","巳"),("巳","寅"),
                          ("巳","申"),("申","巳"),("子","卯"),("卯","子"),
                          ("丑","未"),("未","丑"),("戌","未"),("未","戌")]
        for z1, z2 in liu_xing_pairs:
            if zhi == z1 and (z2 in [nian_zhi, yue_zhi, ri_zhi, shi_zhi]):
                bonus -= 0.2
                details.append(f"{z1}{z2}刑-0.2")
                break
        
        # 伏吟（大运干支与四柱相同）
        for pos_zhi in [nian_zhi, yue_zhi, ri_zhi, shi_zhi]:
            if zhi == pos_zhi and gan == ri_gan:
                bonus -= 0.2
                details.append(f"伏吟日柱-0.2")
                break
        
        # cap赋能
        bonus = max(0.0, min(3.0, bonus))
        
        # ═══════════════════════════════════════════════
        # 第三步：总分 = 基础 + 赋能 (cap 1-10)
        # ═══════════════════════════════════════════════
        score = round(base + bonus, 1)
        score = max(1.0, min(10.0, score))
        
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
            "gan_ss": gan_ss,
            "detail": f"基础{base}+赋能{bonus:.1f}=" + "; ".join(details),
            "energy_dim": energy_dim,    # 能量层面
            "feeling_dim": feeling_dim,  # 感受层面
        })
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 财富量级评估模型
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 财富五级（素材11第349~433行·金鉴真人原始定级）
# 等级 | 身价范围 | 核心条件 | 来源
CAI_FU_WU_JI = [
    ("贫穷",   0,   12, "八字无财（一丁点财星都没有）+身弱，俗称和尚命"),
    ("小富",   12,  36, "身弱财也弱，遇印比则发小财，一生上千万"),
    ("中富",   36,  60, "身强财弱（财星<40分）或身弱财旺，几千万"),
    ("大富",   60,  85, "身强财旺（财≥40分），财星能量强，几个亿"),
    ("巨富",   85,  100,"身强财旺+日/时柱有财库或比劫库+财无刑冲+大运配合"),
]

# 六种八字状态×发财条件（素材17第161~193行）
CAI_FU_STATES = {
    "从弱格+财旺":    {"level":"大富~巨富","desc":"从弱格（0→50分），财星得令，财为喜用，财务全通→亿万级"},
    "从弱格+财弱":    {"level":"小富~中富","desc":"从弱格但财星偏弱，靠事业贵气生财，财富是事业副产品"},
    "身强财旺":       {"level":"大富~巨富","desc":"身强（40~60分）+财旺（≥40分），本命局已满足发财条件，天生不缺钱"},
    "身强财弱":       {"level":"中富",     "desc":"身强（40~60分）+财弱（<40分），底子好但财星弱，遇食伤/财星大运发中财"},
    "身弱财旺":       {"level":"中富",     "desc":"身弱（<40分）+财旺（≥40分），有机会但抓不住，等印比帮身才能变现"},
    "身弱财弱":       {"level":"小富",     "desc":"身弱（<40分）+财弱（<40分），辛苦钱，遇印比则发中财"},
    "无财+身弱":      {"level":"贫穷",     "desc":"四柱无财+身弱(或从弱格+财星极弱)，和尚命，一辈子难发财"},
    "无财+身强":      {"level":"小富",     "desc":"四柱无财+身强，遇财星年份有钱进账但不长久，短暂小财"},
    "从弱格+无财":    {"level":"贫穷",     "desc":"从弱格+财星极弱（<1分），穷命，靠贵气也难生财"},
    "中和财旺":       {"level":"大富",     "desc":"中和（40~60分）+财旺（≥40分），财能为我用，发大财格局"},
    "中和财弱":       {"level":"中富",     "desc":"中和（40~60分）+财弱（<40分），财星不足但自身运势平稳，逢食伤大运可发中财"},
}

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
    # 判断身强身弱（基于知识库三段式：<40身弱，40-60中和，>60身强）
    if sqr_score >= 60:
        shen_state = "身强"
    elif sqr_score >= 40:
        shen_state = "中和"  # 中和不属于身强也不属于身弱
    else:
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
    
    # 计算分数（映射到等级区间）
    if state == "身强财旺":
        score = 60 + (cai_xing_total - 40) * 0.8  # 60-92分
        if has_ku:
            score = min(score + 10, 100)  # 有库→巨富可能
    elif state == "身强财弱":
        score = 36 + (cai_xing_total / 40.0) * 24  # 36-60分
    elif state == "身弱财旺":
        score = 36 + (sqr_score / 40.0) * 24  # 越接近身强越好
    elif state == "身弱财弱":
        score = 12 + (cai_xing_total / 40.0) * 24  # 12-36分
    elif state == "无财+身弱":
        score = 0 + min(sqr_score, 12)  # 0-12分
    elif state == "无财+身强":
        score = 12 + min(sqr_score - 40, 24)  # 12-36分
    elif state == "中和财旺":
        score = 48 + (cai_xing_total - 40) * 0.6
    elif state == "中和财弱":
        score = 24 + (cai_xing_total / 40.0) * 24
    else:
        score = 25.0
    
    score = min(max(score, 0), 100)
    
    # 按分数映射到具体财富五级
    actual_level = info["level"]
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
        # 五合（甲己、乙庚、丙辛、丁壬、戊癸）
        if GAN_WU_HE.get(nian_gan) == pg:
            yuan_ju_gan_he[pos] = f"{nian_gan}{pg}合"
            yuan_ju_detail_parts.append(f"流年天干{nian_gan}与{pos}柱天干{pg}五合")
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
    学历评分 v8.0 — 基于金鉴真人·学历文昌体系
    使用第0层年柱有印三档法 + 六步精细排查法
    得分 = 原局基础(0-7分) + 大运赋能(0-3分) = 满分10分
    输出前×10转为0-100分制
    知识库来源：
    - 金鉴真人_学历文昌体系_20260604.md (卷二·印枭学历判断法)
    - bazi-education-analysis/SKILL.md (第0层年柱有印三档法+六步排查)
    """
    from collections import Counter
    
    is_cong_ruo = (sqr_level == "从弱")
    is_cong_qiang = (sqr_level == "从强")
    is_cong_ge = is_cong_ruo or is_cong_qiang
    
    raw_score = 0.0
    details = []
    
    # ── 第0层：年柱有印三档法[SKILL.md §第一步] ──
    nian_gan_ss = shi_shen(ri_gan, nian_gan)
    nian_gan_is_yin = nian_gan_ss in ("正印", "偏印")
    
    # 年支藏干是否有印
    nian_zhi_yin = False
    nian_zhi_yin_score = 0.0
    for cg, wt in DI_ZHI_CANG_GAN[nian_zhi]:
        cg_ss = shi_shen(ri_gan, cg)
        if cg_ss in ("正印", "偏印"):
            nian_zhi_yin = True
            nian_zhi_yin_score = 4 * wt / 100  # 年支4分×藏干比例
            break
    
    layer0_has_yin = nian_gan_is_yin or nian_zhi_yin
    
    # 12岁前有无文昌大运/流年
    layer0_wen_chang_12 = False
    if da_yun_list and len(da_yun_list) > 0:
        first_dy_gan = da_yun_list[0]["gan_zhi"][0]
        first_dy_zhi = da_yun_list[0]["gan_zhi"][1]
        wen_chang_zhi = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申",
                         "己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
        # 双轨制：年干/日干任一查得文昌即有效
        wc_zhi_nian = wen_chang_zhi.get(nian_gan, "")  # 年干文昌
        wc_zhi_ri = wen_chang_zhi.get(ri_gan, "")      # 日干文昌
        if first_dy_zhi in (wc_zhi_nian, wc_zhi_ri):
            layer0_wen_chang_12 = True
    
    if layer0_has_yin:
        layer0_verdict = "有学业基因"
        layer0_detail = f"年柱有印（透干={nian_gan_is_yin}，藏印={nian_zhi_yin}）→有学业基因"
    elif layer0_wen_chang_12:
        layer0_verdict = "学业中等（文昌补救）"
        layer0_detail = "年柱无印但12岁前大运文昌→学业中等"
    else:
        layer0_verdict = "无学业基因"
        layer0_detail = "年柱无印且12岁前无文昌→学业一般"
    details.append(f"第0层:{layer0_detail}")
    
    # ── 从弱格特殊处理[学历文昌体系卷2.1.2] ──
    if is_cong_ruo:
        # 从弱格：印为忌神，不靠印星
        # 靠食伤(悟性)+官杀(自律)+文昌
        # 基础分 = 食伤/官杀天干加分
        details.append("从弱格:不靠印星，食伤/官杀/文昌主学业")
        
        # 天干食伤悟性
        for pos, gan, pts in [("年干", nian_gan, 1.5), ("月干", yue_gan, 1.5), ("时干", shi_gan, 1.5)]:
            ss = shi_shen(ri_gan, gan)
            if ss in ("食神", "伤官"):
                raw_score += pts
                details.append(f"{pos}({gan}){ss}(从弱喜泄) +{pts}")
        # 天干官杀自律
        for pos, gan, pts in [("月干", yue_gan, 1.0), ("年干", nian_gan, 0.5)]:
            ss = shi_shen(ri_gan, gan)
            if ss in ("正官", "七杀"):
                raw_score += pts
                details.append(f"{pos}({gan}){ss}(从弱喜克) +{pts}")
        
        # 从弱格印在月令本气：假从真用
        yue_ben = DI_ZHI_CANG_GAN[yue_zhi][0][0] if DI_ZHI_CANG_GAN[yue_zhi] else ""
        if yue_ben:
            yue_ben_ss = shi_shen(ri_gan, yue_ben)
            if yue_ben_ss in ("正印", "偏印"):
                raw_score += 0.5
                details.append(f"月令本气{yue_ben}:{yue_ben_ss}(从弱假从真用) +0.5")
        
        cap_base = 5.0
    
    # ── 从强格特殊处理 ──
    elif is_cong_qiang:
        # 从强格：全盘皆喜，印星愈旺愈吉
        for pos, gan, full_pts in [("年干", nian_gan, 1.5), ("月干", yue_gan, 1.5), ("时干", shi_gan, 1.0)]:
            ss = shi_shen(ri_gan, gan)
            if ss in ("正印", "偏印"):
                raw_score += full_pts
                details.append(f"{pos}({gan}){ss}(从强喜印) +{full_pts}")
        cap_base = 5.0
    
    # ── 常规身强/身弱/中和 ──
    else:
        # ---- 六步排查[SKILL.md §第二步] ----
        checks_passed = 0
        checks_total = 6
        
        # 第1步：印在月令本气？（40分）
        yue_ben = DI_ZHI_CANG_GAN[yue_zhi][0][0] if DI_ZHI_CANG_GAN[yue_zhi] else ""
        yue_ben_ss = shi_shen(ri_gan, yue_ben) if yue_ben else ""
        if yue_ben_ss in ("正印", "偏印"):
            raw_score += 1.5
            details.append(f"第1步·月令本气印({yue_ben}) +1.5")
            checks_passed += 1
        else:
            details.append(f"第1步·月令本气非印 ❌")
        
        # 第2步：印根是否被合化消耗
        yin_gen_ok = True
        # 检查年支印星是否被合化
        for cg, wt in DI_ZHI_CANG_GAN[nian_zhi]:
            if shi_shen(ri_gan, cg) in ("正印", "偏印"):
                # 检查这个位置是否被合化
                san_he_results = check_san_he([nian_zhi, yue_zhi, ri_zhi, shi_zhi])
                if san_he_results and san_he_results[0]:
                    yin_gen_ok = False
                    break
        if yin_gen_ok:
            details.append("第2步·印根完整 ✅")
        else:
            details.append("第2步·印根被合化消耗 ❌")
        if yin_gen_ok:
            checks_passed += 1
        
        # 第3步：文昌存在（四柱有文昌地支）
        wen_chang_zhi = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申",
                         "己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
        wc_zhi = wen_chang_zhi.get(nian_gan, "")  # 命理文昌用年干查（SKILL.md §3.1.1）
        found_wc = False
        for pos, zhi in [("年支", nian_zhi), ("月支", yue_zhi), ("日支", ri_zhi), ("时支", shi_zhi)]:
            if zhi == wc_zhi:
                raw_score += 1.0
                details.append(f"第3步·{pos}文昌({wc_zhi}) ✅ +1.0")
                found_wc = True
                break
        if found_wc:
            checks_passed += 1
        else:
            details.append("第3步·原局无文昌 ❌")
        
        # 第4步：18岁前大运走喜用还是忌神
        # 学历主要看印比运（喜用），财官运（忌神）
        if da_yun_list and len(da_yun_list) > 1:
            first_dy = da_yun_list[0]
            first_dy_gan = first_dy["gan_zhi"][0]
            first_dy_ss = shi_shen(ri_gan, first_dy_gan)
            # 知识库：印比运为喜用学习运，财官食伤为忌神
            if shen_score < 40:  # 身弱喜印比
                if first_dy_ss in ("正印", "偏印", "比肩", "劫财"):
                    raw_score += 1.0
                    details.append(f"第4步·{first_dy_gan}大运(身弱喜印比) ✅ +1.0")
                    checks_passed += 1
                else:
                    details.append(f"第4步·{first_dy_gan}大运(身弱忌神) ❌")
            elif shen_score >= 60:  # 身强忌印比
                if first_dy_ss not in ("正印", "偏印", "比肩", "劫财"):
                    raw_score += 0.8
                    details.append(f"第4步·{first_dy_gan}大运(身强不忌) ✅ +0.8")
                    checks_passed += 1
                else:
                    details.append(f"第4步·{first_dy_gan}大运(身强遇印比) ❌")
            else:  # 中和
                checks_passed += 1
                details.append(f"第4步·身中和,大运无忧 ✅")
        else:
            details.append("第4步·无大运数据 ❌")
        
        # 第5步：第0层+文昌在原局 = 第0层已判有学业基因
        if layer0_has_yin or found_wc:
            checks_passed += 1
            details.append(f"第5步·学业基因存在 ✅")
        else:
            details.append(f"第5步·无学业基因 ❌")
        
        # 第6步：全局综合 — 印星在天干透出
        yin_tou_gan = 0
        for pos, gan in [("年干", nian_gan), ("月干", yue_gan), ("时干", shi_gan)]:
            if shi_shen(ri_gan, gan) in ("正印", "偏印"):
                yin_tou_gan += 1
                if yin_tou_gan >= 2:
                    raw_score += 0.8
                    details.append(f"第6步·印星双透 +0.8")
                    checks_passed += 1
                    break
        if yin_tou_gan < 2:
            details.append(f"第6步·印星透干不足 ❌")
        
        # 六步结论
        details.append(f"六步排查: {checks_passed}/{checks_total}项通过")
        if checks_passed >= 4:
            raw_score += 0.5
            details.append(f"≥4项✅→高学历倾向 +0.5")
        elif checks_passed <= 1:
            raw_score -= 0.5
            details.append(f"≤1项✅→低学历倾向 -0.5")
        
        cap_base = 4.5
    
    # ── 年柱十神辅助（知识库·年干定性） ──
    nian_ss = shi_shen(ri_gan, nian_gan)
    if nian_ss in ("正官",):
        raw_score += 0.3
        details.append(f"年干正官:稳定不叛逆 +0.3")
    elif nian_ss == "食神":
        raw_score += 0.3
        details.append(f"年干食神:聪明 +0.3")
    elif nian_ss in ("正印", "偏印"):
        if is_cong_ruo:
            details.append(f"年干{nian_ss}:从弱格忌印 +0")
        else:
            raw_score += 0.5
            details.append(f"年干{nian_ss}:学习基因 +0.5")
    
    # ── 年支藏印基础分（知识库第0层量化） ──
    if nian_zhi_yin:
        pts = round(nian_zhi_yin_score * 0.3, 2)
        if not is_cong_ruo:
            raw_score = round(raw_score + pts, 2)
            details.append(f"年支藏印基础分 +{pts}")
    
    # cap原局基础
    raw_score = min(raw_score, cap_base)
    
    # ── 大运赋能 (0-3分) ──────────────────────────
    dy_bonus = 0.0
    dy_details = []
    
    if da_yun_list:
        # 前4步大运看学习
        for dy in da_yun_list[:4]:
            dg = dy["gan_zhi"][0]
            dz = dy["gan_zhi"][1]
            dg_ss = shi_shen(ri_gan, dg)
            
            if is_cong_ruo:
                # 从弱格:食伤(悟性)/官杀(自律)运加分
                if dg_ss in ("食神", "伤官"):
                    dy_bonus += 0.5
                    dy_details.append(f"大运{dg}:{dg_ss}(从弱喜泄) +0.5")
                elif dg_ss in ("正官", "七杀"):
                    dy_bonus += 0.3
                    dy_details.append(f"大运{dg}:{dg_ss}(从弱喜克) +0.3")
                # 从弱格文昌：文昌独立神煞，不受运喜忌约束（双轨制：年干/日干）
                wen_chang_zhi = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申",
                                 "己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
                wc_zhi_nian = wen_chang_zhi.get(nian_gan, "")  # 年干文昌
                wc_zhi_ri = wen_chang_zhi.get(ri_gan, "")      # 日干文昌
                if dz in (wc_zhi_nian, wc_zhi_ri):
                    dy_bonus += 0.8
                    dy_details.append(f"大运文昌({dz}) +0.8")
            else:
                if dg_ss in ("正印", "偏印"):
                    dy_bonus += 0.5
                    dy_details.append(f"大运{dg}:{dg_ss} +0.5")
                # 非从弱格文昌（双轨制：年干/日干）
                wen_chang_zhi = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申",
                                 "己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
                wc_zhi_nian = wen_chang_zhi.get(nian_gan, "")  # 年干文昌
                wc_zhi_ri = wen_chang_zhi.get(ri_gan, "")      # 日干文昌
                if dz in (wc_zhi_nian, wc_zhi_ri) and not found_wc:
                    dy_bonus += 1.0
                    dy_details.append(f"大运文昌({dz}) +1.0")
                    found_wc = True
    
    dy_bonus = min(dy_bonus, 3.0)
    raw_score = round(raw_score + dy_bonus, 1)
    for dd in dy_details:
        details.append(dd)
    
    raw_score = min(raw_score, 10.0)
    
    # ── 等级划定（知识库标准） ──
    if is_cong_ruo:
        # 从弱格：印为忌神，学历上限一般较低
        if raw_score >= 5.0:
            level = "本科以上"
        elif raw_score >= 3.0:
            level = "中等学历"
        elif raw_score >= 1.0:
            level = "基础学历"
        else:
            level = "基础教育"
    elif raw_score >= 8.0:
        level = "高学历"
    elif raw_score >= 4.5:
        level = "本科以上"
    elif raw_score >= 3.5:
        level = "中等学历"
    elif raw_score >= 1.5:
        level = "基础学历"
    else:
        level = "基础教育"
    
    out_score = round(raw_score * 10, 1)
    return {"score": out_score, "level": level, "details": details,
            "_raw": raw_score}


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
    
    total = base + shen_mod + dy_mod + evil_mod
    
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
            "base_score": base, "shen_mod": shen_mod, "dy_mod": dy_mod,
            "evil_mod": evil_mod, "evil_details": evil_details}


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
    cx = calc_cai_xing(rg, ng, yg, sg, nz, yz, rz, sz, sq_level=sqr["level"])
    ss_sha = calc_shensha(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    ss_flat = calc_all_shensha_with_positions(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    ss_summary = calc_shensha_summary(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    energy_analysis = calc_bazi_energy_analysis(rg, nz, yz, rz, sz, xys.get("xi_shen", []))
    
    # 新增功能 v8.3
    # 调候用神
    tiao_hou = calc_tiao_hou(rg, yz, tian_gan_list)
    # 通关用神
    tong_guan = calc_tong_guan(rg, wx_pcts)
    # 假旺真弱
    jwzr = check_jia_wang_zhen_ruo(rg, sqr["score"], sqr["level"], nz, yz, rz, sz, tian_gan_list)
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
    # 财富量级（知识库六态矩阵法v8.0）
    cai_fu = calc_cai_fu_deng_ji(
        cx.get("score", 0), sqr["score"], sqr["level"],
        rg, gj_str,
        nian_gan=ng, yue_gan=yg, shi_gan=sg,
        has_ku=cx.get("has_ku", False)
    )
    # 统一财富等级：以calc_cai_fu_deng_ji的level为权威来源
    cx["wealth_level"] = cai_fu["level"]
    # 流年分析（当前年份及附近5年）
    current_year = 2026
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
                "jia_wang_zhen_ruo":jwzr,"zhuan_wang_ge":zhuan_wang,
                "hua_qi_ge":hua_qi,"da_yun_ji_xiong":da_yun_jx,
                "wu_xing_liu_tong_ge":wu_xing_liu_tong,
                "mu_huo_tong_ming_ge":mu_huo_tong_ming,
                "cai_fu_deng_ji":cai_fu,"cai_yun":cai_fu,
                "liu_nian":liu_nian_list,
                "xue_ye":xy,"shi_ye":calc_shi_ye(gj_str, sqr, da_yun_jx),
                "hun_yin":hunyin}
    
    return {"basic":basic,"analysis":analysis}
