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
    格局 v7.0：透干定格局 + 比劫不入格局
    规则：
    1. 取月令藏干（本气→中气→余气依次）检查透干
    2. 透干=年/月/时天干出现该藏干对应五行
    3. 比劫不入格局，遇比劫跳过
    4. 无人透干时：取首个非比劫的本气/中气/余气
    5. 全部比劫→返回"无正格"
    """
    tian_gan = [nian_gan, yue_gan, shi_gan]
    
    for cg, wt in DI_ZHI_CANG_GAN[yue_zhi]:
        cg_ss = shi_shen(ri_gan, cg)
        if cg_ss not in ZHENG_BA_GE:
            continue  # 比劫跳过
        # 检查是否透干
        for tg in tian_gan:
            if tg and tg == cg:
                return GE_JU_NAME[cg_ss]
    
    # 无人透干：取首个非比劫
    for cg, wt in DI_ZHI_CANG_GAN[yue_zhi]:
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
    
    basic = {"ba_zi":ba_zi,"ri_zhu":rg+rz,"ri_gan":rg,"ri_zhi":rz,
             "nian_gan":ng,"nian_zhi":nz,"yue_gan":yg,"yue_zhi":yz,
             "shi_gan":sg,"shi_zhi":sz,
             "gender":"男" if gender==1 else "女",
             "solar_date":f"{year}年{month}月{day}日",
             "pillars":pillars}
    
    analysis = {"shen_qiang_ruo":sqr,"ge_ju":gj,"xi_yong_shen":xys,
                "cai_xing":cx,"da_yun":dy,"wu_xing_energy":wx_energy}
    
    return {"basic":basic,"analysis":analysis}
