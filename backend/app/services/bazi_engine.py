#!/usr/bin/env python3
"""
金鉴真人·八字排盘引擎 v7.0
基于九龙道长原始规则体系重写
规则来源：weiwuji-knowledge-base 理论知识体系
v7.0更新：
  - 燥土规则：未/戌对金日主，被火引化不计分
  - 格局透干定：比劫不入格局，检查中气/余气透干
  - 财库计算：calc_cai_xing输出has_ku/cai_ku
"""
from __future__ import annotations
from datetime import datetime, date, timedelta
import math

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

# 燥土地支（未/戌）
ZAO_TU = {"未","戌"}

# ── 六害（六穿）：子未·丑午·寅巳·卯辰·申亥·酉戌 ──
LIU_HAI = {"子":"未","丑":"午","寅":"巳","卯":"辰","辰":"卯","巳":"寅",
            "午":"丑","未":"子","申":"亥","酉":"戌","戌":"酉","亥":"申"}

# ── 六破：子酉·寅亥·辰丑·午卯·申巳·戌未 ──
LIU_PO = {"子":"酉","丑":"辰","寅":"亥","卯":"午","辰":"丑","巳":"申",
           "午":"卯","未":"戌","申":"巳","酉":"子","戌":"未","亥":"寅"}

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

def shi_shen(ri_gan: str, gan: str) -> str:
    """十神"""
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
    燥土是否有效（有效才计分）v7.0
    规则：未/戌对庚辛金日主
      - 天干有丙/丁（火引化）→ 当火看 → 不计分
      - 天干有壬/癸（水灭火）→ 当土看 → 计分
      - 无火无水 → 计分
      - 非金日主 → 不计燥土规则
    """
    if zhi not in ZAO_TU:
        return True  # 非燥土地支，正常计分
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    if ri_wx != "金":
        return True  # 非金日主，燥土规则不适用
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
        drift = round((year - 2000) * 0.2422)
        leap_count = sum(1 for y in range(2001, year+1) 
                        if (y%4==0 and y%100!=0) or y%400==0) if year > 2000 else 0
        adj = -drift + leap_count
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
    """检查三刑，返回所有三刑组合及类型"""
    results = []
    zhi_set = list(zhi_list)
    # 寅巳申三刑
    if {"寅","巳","申"}.issubset(set(zhi_set)):
        results.append(("寅巳申三刑", "无恩之刑", ENERGY_MULTIPLIER["三刑"]))
    # 丑未戌三刑
    if {"丑","未","戌"}.issubset(set(zhi_set)):
        results.append(("丑未戌三刑", "恃势之刑", ENERGY_MULTIPLIER["三刑"]))
    # 子卯刑
    if {"子","卯"}.issubset(set(zhi_set)):
        results.append(("子卯刑", "无礼之刑", ENERGY_MULTIPLIER["三刑"]))
    # 自刑
    for z in zhi_set:
        if z in ZI_XING:
            count = zhi_set.count(z)
            if count >= 2:
                results.append((f"{z}自刑", "自刑", ENERGY_MULTIPLIER["自刑"]))
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
    返回完整的关系列表和能量汇总"""
    zhi_list = [nian_zhi, yue_zhi, ri_zhi, shi_zhi]
    positions = ["年支","月支","日支","时支"]
    results = []
    total_energy = 0

    # 两两检查
    for i in range(4):
        for j in range(i+1, 4):
            rel = calc_energy_relationship(zhi_list[i], zhi_list[j])
            if rel:
                rel["zhi_a_pos"] = positions[i]
                rel["zhi_b_pos"] = positions[j]
                rel["zhi_a"] = zhi_list[i]
                rel["zhi_b"] = zhi_list[j]
                results.append(rel)
                total_energy += rel["multiplier"]

    # 三合局检查(完整三合)
    sh_wx, sh_complete, sh_mult = check_san_he(zhi_list)
    if sh_complete:
        results.append({"type":"三合局", "name":f"{sh_wx}三合局", "multiplier":sh_mult,
                        "detail":f"地支构成{sh_wx}三合局 +{sh_mult}倍"})
        total_energy += sh_mult
    # 半三合
    elif sh_mult > 1:
        results.append({"type":"半三合", "name":f"{sh_wx}半三合", "multiplier":sh_mult,
                        "detail":f"地支构成{sh_wx}半三合 +{sh_mult}倍"})
        total_energy += sh_mult

    # 三会局检查
    hui_wx, hui_complete, hui_mult = check_san_hui(zhi_list)
    if hui_complete:
        results.append({"type":"三会局", "name":f"{hui_wx}三会局", "multiplier":hui_mult,
                        "detail":f"地支构成{hui_wx}三会局 +{hui_mult}倍"})
        total_energy += hui_mult

    # 三刑检查
    xing_results = check_san_xing(zhi_list)
    for xr in xing_results:
        results.append({"type":"三刑", "name":xr[0], "multiplier":xr[2],
                        "detail":f"{xr[0]}({xr[1]}) +{xr[2]}倍"})
        total_energy += xr[2]

    # 空亡减半
    # (空亡在排盘阶段已计算，此处标记)
    # 汇总
    if xi_shen:
        xi_set = set(xi_shen)
        for r in results:
            # 判断关系涉及的五行方向是否喜用
            r["xi_ji"] = "喜" if r.get("multiplier",0) < 0 else "冲"  # placeholder for direction

    return {"relationships": results, "total_multiplier": total_energy, "count": len(results)}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 身强弱评分（九龙道长原始规则 v7.0）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 位置基础分（满分100，日干不计）
POS_SCORE = {'nian_gan':8,'nian_zhi':4,'yue_gan':12,'yue_zhi':40,'ri_zhi':12,'shi_gan':12,'shi_zhi':12}

def calc_shen_qiang_ruo(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                         nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str) -> dict:
    """
    身强弱评分 v7.0
    规则（九龙道长原始规则）：
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
    
    if yz_ben_wx == yin_wx and yz_effective:
        score += 40; details.append(f"月令本气印({yz_ben}) +40")
    elif yz_ben_wx == bi_wx and yz_effective:
        score += 40; details.append(f"月令本气比劫({yz_ben}) +40")
    
    # 2. 月令中/余气（比劫才计分，印不计）
    for cg, wt in DI_ZHI_CANG_GAN[yue_zhi]:
        if TIAN_GAN_WU_XING[cg] == bi_wx and cg != yz_ben:
            p = 40 * wt / 100
            score += p; details.append(f"月令藏干比劫({cg}) +{p:.1f}")
    
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

def get_ge_ju(ri_gan: str, yue_zhi: str,
              nian_gan: str = "", yue_gan: str = "", shi_gan: str = "") -> str:
    """
    格局 v7.3：严格遵循知识库正格判定规则
    ────────────────
    核心规则（每格）：「月令本气为日主X，或月干透出X」
    ────────────────
    判定流程（四维）：
      第1维：月令本气 → 取月支主气藏干的十神
        如为正八格之一 → 直接取格
        如为比劫 → 不入格，进入下一维
      
      第2维：月干透出 → 月柱天干的十神
        如为正八格之一 → 取该格
      
      第3维：月令中/余气透干
        月支中气/余气的十神如在正八格中
        且该藏干字符在年/月/时天干中出现(字符匹配) → 取该格
      
      第4维：月令中/余气取首个非比劫
        无人透干时，取月令中/余气中首个在正八格的
      
      均不匹配 → 返回"无正格"
    """
    tian_gan = [nian_gan, yue_gan, shi_gan]
    cang_gan_list = DI_ZHI_CANG_GAN[yue_zhi]  # [本气, 中气, 余气]
    
    # ── 第1维：月令本气 ──
    ben_qi_gan = cang_gan_list[0][0]  # 本气对应的天干
    ben_qi_ss = shi_shen(ri_gan, ben_qi_gan)
    if ben_qi_ss in ZHENG_BA_GE:
        return GE_JU_NAME[ben_qi_ss]
    
    # ── 第2维：月干透出 ──
    if yue_gan:
        yue_gan_ss = shi_shen(ri_gan, yue_gan)
        if yue_gan_ss in ZHENG_BA_GE:
            return GE_JU_NAME[yue_gan_ss]
    
    # ── 第3维：月令中/余气透干（字符匹配）──
    for cg, wt in cang_gan_list[1:]:  # 跳过本气
        cg_ss = shi_shen(ri_gan, cg)
        if cg_ss not in ZHENG_BA_GE:
            continue
        for tg in tian_gan:
            if tg and tg == cg:  # 字符匹配
                return GE_JU_NAME[cg_ss]
    
    # ── 第4维：月令中/余气取首个非比劫 ──
    for cg, wt in cang_gan_list:
        cg_ss = shi_shen(ri_gan, cg)
        if cg_ss in ZHENG_BA_GE:
            return GE_JU_NAME[cg_ss]
    
    return "无正格"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 喜用神 / 忌神
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_xi_yong_shen(ri_gan: str, shen_qiang_level: str, shen_qiang_score: float = 50.0) -> dict:
    """喜用神/忌神（输出具体五行，非十神类别）"""
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_idx = WX_ORDER.index(ri_wx)

    ke_xi = [WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+1)%5]]
    ke_ji = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
    sheng_xi = [WX_ORDER[(ri_idx+4)%5], WX_ORDER[ri_idx]]
    sheng_ji = [WX_ORDER[(ri_idx+3)%5], WX_ORDER[(ri_idx+2)%5], WX_ORDER[(ri_idx+1)%5]]

    if shen_qiang_level in ("身强", "从弱"):
        xi, ji = ke_xi, ke_ji
    elif shen_qiang_level == "从强":
        xi, ji = sheng_xi, sheng_ji
    elif shen_qiang_level == "中和":
        if shen_qiang_score >= 50:
            xi, ji = ke_xi, ke_ji  # 偏强喜克泄耗
        else:
            xi, ji = sheng_xi, sheng_ji  # 偏弱喜生扶
    else:  # 身弱
        xi, ji = sheng_xi, sheng_ji

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
                  nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str) -> dict:
    """
    财星评分 v7.0（九龙道长规则 + 财库计算）
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
    
    # 地支财星（藏干按比例）
    for pos, zhi, base in [('年支',nian_zhi,4),('月令',yue_zhi,40),('日支',ri_zhi,12),('时支',shi_zhi,12)]:
        for cg, wt in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cg] == cai_wx:
                p = base * wt / 100
                score += p; details.append(f"{pos}藏干({cg})财星 +{p:.1f}")
    
    # 财库检测（仅日/时柱）
    cai_ku_zhi = CAI_KU_MAP.get(ri_wx, "")
    has_ku = False
    ri_shi_list = [("日支", ri_zhi), ("时支", shi_zhi)]
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
    
    # 从弱格特殊处理
    sq_level = ""  # 调用者会传，但这里暂不处理
    # calc_cai_xing 被 calculate_bazi 调用，从弱格由调用者决定
    
    # 财富五级（基于实际验证校准）
    if score >= 60: level = "大富"
    elif score >= 26: level = "中富"
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
    统计比例并按五行分类"""
    wu_xing_score = {wx: 0.0 for wx in WX_ORDER}

    # 天干4个，每个10分
    for gan_pos, gan in [("年干", nian_gan), ("月干", yue_gan), ("日干", ri_gan), ("时干", shi_gan)]:
        wu_xing_score[TIAN_GAN_WU_XING[gan]] += 10.0

    # 地支+藏干
    for zhi_pos, zhi in [("年支", nian_zhi), ("月支", yue_zhi), ("日支", ri_zhi), ("时支", shi_zhi)]:
        cg_list = DI_ZHI_CANG_GAN[zhi]
        for cg, wt in cg_list:
            wx = TIAN_GAN_WU_XING[cg]
            weight = {100: 10.0, 60: 6.0, 30: 3.0}.get(wt, 0)
            wu_xing_score[wx] += weight

    # 标准化到百分比
    total = sum(wu_xing_score.values())
    if total > 0:
        result = {wx: round(score / total * 100, 1) for wx, score in wu_xing_score.items()}
    else:
        result = {wx: 0.0 for wx in WX_ORDER}

    # 排序：从高到低
    sorted_result = dict(sorted(result.items(), key=lambda x: -x[1]))
    return sorted_result

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
XUE_REN = {
    "甲":"卯","乙":"寅","丙":"午","丁":"巳","戊":"午",
    "己":"巳","庚":"酉","辛":"申","壬":"子","癸":"亥"
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
# 流年分析
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calc_liu_nian(year: int, ri_gan: str, da_yun_list: list) -> dict:
    """
    流年分析。
    
    参数：
        year: 流年公历年份
        ri_gan: 日干
        da_yun_list: calc_da_yun 返回的 da_yun 列表，每项含 gan_zhi
    
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
    
    return {
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 主入口 v7.0
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_bazi(year: int, month: int, day: int,
                   hour: int = 12, minute: int = 0,
                   is_lunar: bool = False, gender: int = 1) -> dict:
    """八字排盘主入口 v7.0"""
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
    gj = get_ge_ju(rg, yz, ng, yg, sg)
    xys = get_xi_yong_shen(rg, sqr["level"], sqr["score"])
    dy = calc_da_yun(ng, nz, gender, year, month, day, hour, minute)
    cx = calc_cai_xing(rg, ng, yg, sg, nz, yz, rz, sz)
    wx_energy = calc_wu_xing_energy(ng, yg, rg, sg, nz, yz, rz, sz)
    ss_sha = calc_shensha(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    ss_flat = calc_all_shensha_with_positions(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    ss_summary = calc_shensha_summary(rg, rz, ng, nz, yg, yz, sg, sz, gender)
    energy_analysis = calc_bazi_energy_analysis(rg, nz, yz, rz, sz, xys.get("xi_shen", []))

    basic = {"ba_zi":ba_zi,"ri_zhu":rg+rz,"ri_gan":rg,"ri_zhi":rz,
             "nian_gan":ng,"nian_zhi":nz,"yue_gan":yg,"yue_zhi":yz,
             "shi_gan":sg,"shi_zhi":sz,
             "gender":"男" if gender==1 else "女",
             "solar_date":f"{year}年{month}月{day}日",
             "pillars":pillars,
             "shensha":ss_sha,
             "shensha_flat":ss_flat}

    analysis = {"shen_qiang_ruo":sqr,"ge_ju":gj,"xi_yong_shen":xys,
                "cai_xing":cx,"da_yun":dy,"wu_xing_energy":wx_energy,
                "shensha_summary":ss_summary,"energy_analysis":energy_analysis}
    
    return {"basic":basic,"analysis":analysis}
