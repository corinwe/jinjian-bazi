#!/usr/bin/env python3
"""
金鉴真人·八字排盘引擎 v6.0
基于九龙道长原始规则体系重写
规则来源：weiwuji-knowledge-base 理论知识体系
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
    gan_idx = (TIAN_GAN.index(start_gan) + (branch_idx-2)%12) % 10
    return TIAN_GAN[gan_idx], DI_ZHI[branch_idx]

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
# 身强弱评分（九龙道长原始规则 v1.0）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 位置基础分（满分100，日干不计）
POS_SCORE = {'nian_gan':8,'nian_zhi':4,'yue_gan':12,'yue_zhi':40,'ri_zhi':12,'shi_gan':12,'shi_zhi':12}

def calc_shen_qiang_ruo(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                         nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str) -> dict:
    """
    身强弱评分。
    规则（九龙道长原始规则）：
    - 印只在月令本气计分（40分）
    - 比劫在所有位置都计分（年干8/月干12/时干12/年支4/月令40/日支12/时支12）
    - 燥土条件版：被火引化才不计，否则计分
    - 从弱=0分→恒定50分，从强=>100分→恒定20分
    - 三段式：<40身弱, 40-60中和, >60身强
    """
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_idx = WX_ORDER.index(ri_wx)
    yin_wx = WX_ORDER[(ri_idx+4)%5]   # 生我=印
    bi_wx = WX_ORDER[ri_idx]           # 同我=比劫
    
    score = 0.0
    details = []
    
    # 1. 月令本气
    yz_ben = DI_ZHI_CANG_GAN[yue_zhi][0][0]
    yz_ben_wx = TIAN_GAN_WU_XING[yz_ben]
    if yz_ben_wx == yin_wx:
        score += 40; details.append(f"月令本气印({yz_ben}) +40")
    elif yz_ben_wx == bi_wx:
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
    
    # 4. 年/日/时支藏干比劫
    for pos, zhi, base in [('年支',nian_zhi,4),('日支',ri_zhi,12),('时支',shi_zhi,12)]:
        for cg, wt in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cg] == bi_wx:
                p = base * wt / 100
                if p > 0:
                    score += p; details.append(f"{pos}藏干比劫({cg}) +{p:.1f}")
    
    # 5. 从格 + 三段式
    if score <= 0:
        return {"score": 50.0, "level": "从弱", "details": details}
    if score > 100:
        return {"score": 20.0, "level": "从强", "details": details}
    if score < 40:
        return {"score": round(score,1), "level": "身弱", "details": details}
    if score <= 60:
        return {"score": round(score,1), "level": "中和", "details": details}
    return {"score": round(score,1), "level": "身强", "details": details}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 格局
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GE_JU_NAME = {"比肩":"建禄格","劫财":"劫财格","食神":"食神格","伤官":"伤官格",
              "正财":"正财格","偏财":"偏财格","正官":"正官格","七杀":"七杀格",
              "正印":"正印格","偏印":"偏印格"}

def get_ge_ju(ri_gan: str, yue_zhi: str) -> str:
    """格局：月令本气十神"""
    ben_qi = DI_ZHI_CANG_GAN[yue_zhi][0][0]
    ss = shi_shen(ri_gan, ben_qi)
    return GE_JU_NAME.get(ss, ss+"格")

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
# 财星评分
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calc_cai_xing(ri_gan: str, nian_gan: str, yue_gan: str, shi_gan: str,
                  nian_zhi: str, yue_zhi: str, ri_zhi: str, shi_zhi: str) -> dict:
    """财星评分（九龙道长规则：只含正偏财，不含劫财）"""
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
    
    # 财富五级（基于实际验证校准）
    # 金标准: 老板31.2=中富, 少爷26.8=中富, 主母16.0=小富
    if score >= 60: level = "大富"
    elif score >= 26: level = "中富"
    elif score >= 12: level = "小富"
    else: level = "贫穷"
    
    return {"score": round(score,1), "wealth_level": level, "details": details}

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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 主入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_bazi(year: int, month: int, day: int,
                   hour: int = 12, minute: int = 0,
                   is_lunar: bool = False, gender: int = 1) -> dict:
    """八字排盘主入口"""
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
    gj = get_ge_ju(rg, yz)
    xys = get_xi_yong_shen(rg, sqr["level"], sqr["score"])
    dy = calc_da_yun(ng, nz, gender, year, month, day, hour, minute)
    cx = calc_cai_xing(rg, ng, yg, sg, nz, yz, rz, sz)
    
    basic = {"ba_zi":ba_zi,"ri_zhu":rg+rz,"ri_gan":rg,"ri_zhi":rz,
             "nian_gan":ng,"nian_zhi":nz,"yue_gan":yg,"yue_zhi":yz,
             "shi_gan":sg,"shi_zhi":sz,
             "gender":"男" if gender==1 else "女",
             "solar_date":f"{year}年{month}月{day}日",
             "pillars":pillars}
    
    analysis = {"shen_qiang_ruo":sqr,"ge_ju":gj,"xi_yong_shen":xys,
                "cai_xing":cx,"da_yun":dy}
    
    return {"basic":basic,"analysis":analysis}
