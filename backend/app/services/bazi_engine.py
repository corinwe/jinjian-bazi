"""
金鉴真人八字排盘引擎
Jinjian Bazī (Four Pillars) Calculation Engine

严格基于金鉴真人知识库规则实现。
支持：四柱八字、十神、大运、身强弱、格局、喜用神、财星评分、神煞、纳音、空亡。
"""

from __future__ import annotations

from datetime import datetime, timedelta, date

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 基础数据
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干五行
TIAN_GAN_WU_XING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 地支五行（本气）
DI_ZHI_WU_XING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 地支藏干(100/60/30) — 每个藏干后的整数是百分比权重
DI_ZHI_CANG_GAN = {
    "子": [("癸", 100)],
    "丑": [("己", 100), ("癸", 60), ("辛", 30)],
    "寅": [("甲", 100), ("丙", 60), ("戊", 30)],
    "卯": [("乙", 100)],
    "辰": [("戊", 100), ("乙", 60), ("癸", 30)],
    "巳": [("丙", 100), ("戊", 60), ("庚", 30)],
    "午": [("丁", 100), ("己", 60)],
    "未": [("己", 100), ("丁", 60), ("乙", 30)],
    "申": [("庚", 100), ("壬", 60), ("戊", 30)],
    "酉": [("辛", 100)],
    "戌": [("戊", 100), ("辛", 60), ("丁", 30)],
    "亥": [("壬", 100), ("甲", 60)],
}

# 五虎遁月（年干→正月天干）
# 甲己之年丙作首, 乙庚之岁戊为头, 丙辛之年寻庚上,
# 丁壬壬寅顺水流, 若问戊癸何处起, 甲寅之上好追求
WU_HU_DUN_YUE = {
    "甲": "丙", "乙": "戊", "丙": "庚", "丁": "壬", "戊": "甲",
    "己": "丙", "庚": "戊", "辛": "庚", "壬": "壬", "癸": "甲",
}

# 五鼠遁时（日干→子时天干）
# 甲己还加甲, 乙庚丙作初, 丙辛从戊起, 丁壬庚子居, 戊癸何方发, 壬子是真途
WU_SHU_DUN_SHI = {
    "甲": "甲", "乙": "丙", "丙": "戊", "丁": "庚", "戊": "壬",
    "己": "甲", "庚": "丙", "辛": "戊", "壬": "庚", "癸": "壬",
}

# 节气对应的月支索引
JIE_QI_TO_MONTH_BRANCH = {
    1: 2,   # 立春→寅
    2: 3,   # 惊蛰→卯
    3: 4,   # 清明→辰
    4: 5,   # 立夏→巳
    5: 6,   # 芒种→午
    6: 7,   # 小暑→未
    7: 8,   # 立秋→申
    8: 9,   # 白露→酉
    9: 10,  # 寒露→戌
    10: 11, # 立冬→亥
    11: 0,  # 大雪→子
    12: 1,  # 小寒→丑
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 纳音五行表（60甲子纳音）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NA_YIN = [
    # 甲子～癸酉
    "海中金", "海中金", "炉中火", "炉中火", "大林木", "大林木",
    "路旁土", "路旁土", "剑锋金", "剑锋金",
    # 甲戌～癸未
    "山头火", "山头火", "涧下水", "涧下水", "城头土", "城头土",
    "白蜡金", "白蜡金", "杨柳木", "杨柳木",
    # 甲申～癸巳
    "泉中水", "泉中水", "屋上土", "屋上土", "霹雳火", "霹雳火",
    "松柏木", "松柏木", "长流水", "长流水",
    # 甲午～癸卯
    "沙中金", "沙中金", "山下火", "山下火", "平地木", "平地木",
    "壁上土", "壁上土", "金箔金", "金箔金",
    # 甲辰～癸丑
    "佛灯火", "佛灯火", "天河水", "天河水", "大驿土", "大驿土",
    "钗钏金", "钗钏金", "桑柘木", "桑柘木",
    # 甲寅～癸亥
    "大溪水", "大溪水", "沙中土", "沙中土", "天上火", "天上火",
    "石榴木", "石榴木", "大海水", "大海水",
]


def na_yin(gan: str, zhi: str) -> str:
    """根据天干地支获取纳音五行。
    正确公式：用60甲子序数 (gan*6 - zhi*5) % 60 直接索引。
    """
    gan_idx = TIAN_GAN.index(gan)
    zhi_idx = DI_ZHI.index(zhi)
    # 60甲子序数
    seq = (gan_idx * 6 - zhi_idx * 5) % 60
    return NA_YIN[seq]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 空亡
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KONG_WANG_MAP = {
    0: [9, 10],   # 甲子旬→戌亥 (索引9,10)
    1: [9, 10],   # 乙丑
    2: [9, 10],   # 丙寅
    3: [9, 10],   # 丁卯
    4: [9, 10],   # 戊辰
    5: [9, 10],   # 己巳
    6: [7, 8],    # 庚午→申酉 (索引7,8)
    7: [7, 8],
    8: [7, 8],
    9: [7, 8],
    10: [7, 8],
    11: [7, 8],
    12: [5, 6],   # 丙子→午未
    13: [5, 6],
    14: [5, 6],
    15: [5, 6],
    16: [5, 6],
    17: [5, 6],
    18: [3, 4],   # 壬午→辰巳
    19: [3, 4],
    20: [3, 4],
    21: [3, 4],
    22: [3, 4],
    23: [3, 4],
    24: [1, 2],   # 戊子→寅卯
    25: [1, 2],
    26: [1, 2],
    27: [1, 2],
    28: [1, 2],
    29: [1, 2],
    30: [11, 0],  # 甲午→子丑
    31: [11, 0],
    32: [11, 0],
    33: [11, 0],
    34: [11, 0],
    35: [11, 0],
    36: [9, 10],  # 庚子→戌亥
    37: [9, 10],
    38: [9, 10],
    39: [9, 10],
    40: [9, 10],
    41: [9, 10],
    42: [7, 8],   # 丙午→申酉
    43: [7, 8],
    44: [7, 8],
    45: [7, 8],
    46: [7, 8],
    47: [7, 8],
    48: [5, 6],   # 壬子→午未
    49: [5, 6],
    50: [5, 6],
    51: [5, 6],
    52: [5, 6],
    53: [5, 6],
    54: [3, 4],   # 戊午→辰巳
    55: [3, 4],
    56: [3, 4],
    57: [3, 4],
    58: [3, 4],
    59: [3, 4],
}


def kong_wang(gan: str, zhi: str) -> list[str]:
    """
    获取空亡地支列表。
    基于该柱天干+地支的60甲子序数确定旬首，再取空亡。
    甲子旬→戌亥空, 甲戌旬→申酉空, 甲申旬→午未空,
    甲午旬→辰巳空, 甲辰旬→寅卯空, 甲寅旬→子丑空。
    """
    gan_idx = TIAN_GAN.index(gan)
    zhi_idx = DI_ZHI.index(zhi)
    # 60甲子序数 = (天干索引 * 6 - 地支索引 * 5) % 60
    seq = (gan_idx * 6 - zhi_idx * 5) % 60
    # 旬号 (0=甲子,1=甲戌,2=甲申,3=甲午,4=甲辰,5=甲寅)
    xun = seq // 10
    # 旬首地支索引 = (12 - 旬号 * 2) % 12
    xun_zhi = (12 - xun * 2) % 12
    # 空亡 = (旬首地支-2, 旬首地支-1) mod 12
    kw1 = (xun_zhi - 2) % 12
    kw2 = (xun_zhi - 1) % 12
    return [DI_ZHI[kw1], DI_ZHI[kw2]]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 神煞
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 文昌贵人（年干）
WEN_CHANG = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
    "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯",
}

# 桃花（年支/日支三合局）
TAO_HUA = {
    "寅": "卯", "午": "卯", "戌": "卯",
    "巳": "午", "酉": "午", "丑": "午",
    "申": "酉", "子": "酉", "辰": "酉",
    "亥": "子", "卯": "子", "未": "子",
}

# 天乙贵人（年干/日干）
TIAN_YI = {
    "甲": ["丑", "未"], "乙": ["子", "申"], "丙": ["酉", "亥"],
    "丁": ["酉", "亥"], "戊": ["丑", "未"], "己": ["子", "申"],
    "庚": ["丑", "未"], "辛": ["午", "寅"], "壬": ["卯", "巳"],
    "癸": ["卯", "巳"],
}


def get_shen_sha(gan: str, zhi: str, ri_gan: str, nian_gan: str, nian_zhi: str) -> list[str]:
    """获取神煞列表。"""
    shen_sha = []

    # 文昌贵人（年干）
    if WEN_CHANG.get(nian_gan) == zhi:
        shen_sha.append("文昌贵人")

    # 桃花（年支）
    if TAO_HUA.get(nian_zhi) == zhi:
        shen_sha.append("桃花")

    # 天乙贵人（年干 + 日干）
    if zhi in TIAN_YI.get(nian_gan, []):
        shen_sha.append("天乙贵人")
    elif zhi in TIAN_YI.get(ri_gan, []):
        shen_sha.append("天乙贵人")

    return shen_sha


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 节气计算
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_solar_term_date(year: int, term_index: int) -> date:
    """
    获取节气日期。
    term_index: 0=立春, 1=惊蛰, ..., 10=大雪, 11=小寒(次年)
    使用天文校正公式，精度±1天（1900-2100年）。
    """
    # 2000年节气基准日期（月,日）
    base_terms_2000 = [
        (2, 4),   # 0: 立春
        (3, 5),   # 1: 惊蛰
        (4, 5),   # 2: 清明
        (5, 5),   # 3: 立夏
        (6, 5),   # 4: 芒种
        (7, 7),   # 5: 小暑
        (8, 7),   # 6: 立秋
        (9, 7),   # 7: 白露
        (10, 8),  # 8: 寒露
        (11, 7),  # 9: 立冬
        (12, 7),  # 10: 大雪
        (1, 6),   # 11: 小寒(次年)
    ]

    month, day = base_terms_2000[term_index]

    # 天文校正原理：
    # - 回归年 = 365.2422天，节气每年推迟约0.2422天
    # - 公历闰年(2/29)使节气表观日期提前1天
    # - 净校正 = -round(年差 * 0.2422) + 闰年数(从2001年起)

    dy = year - 2000
    drift = dy * 0.2422  # 节气逐年推迟

    # 闰年计数：统计2001年至year-1年间的闰年数
    # (2000年是基准年，其节气日期已包含闰年影响)
    if dy > 0:
        leap_count = sum(1 for y in range(2001, year)
                         if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0))
    elif dy < 0:
        leap_count = -sum(1 for y in range(year + 1, 2001)
                          if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0))
    else:
        leap_count = 0

    adj = round(drift - leap_count)

    if term_index < 11:
        return date(year, month, day) + timedelta(days=adj)
    else:
        # 小寒在次年1月
        return date(year + 1, month, day) + timedelta(days=adj)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 农历→公历转换（查表法 1900-2100）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 农历数据表
# 每个元素是一个24位整数，编码该年的农历信息：
# 位0-3: 闰月月份(0=无闰月)
# 位4-15: 每月天数(0=29天, 1=30天)，从正月到十二月
# 位16-19: 闰月天数(0=29天, 1=30天)
# 位20-23: 春节的格里历日期(月*32+日)
LUNAR_YEAR_INFO = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950,  # 1900-1905
    0x16554, 0x056a0, 0x09ad0, 0x055d2, 0x04ae0, 0x0a5b6,  # 1906-1911
    0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2,  # 1912-1917
    0x095b0, 0x14977, 0x04970, 0x0a4b0, 0x0b4b5, 0x06a50,  # 1918-1923
    0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,  # 1924-1929
    0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60,  # 1930-1935
    0x186e3, 0x092e0, 0x1c8d7, 0x0c950, 0x0d4a0, 0x1d8a6,  # 1936-1941
    0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2,  # 1942-1947
    0x0a950, 0x0b557, 0x06ca0, 0x0b550, 0x15355, 0x04da0,  # 1948-1953
    0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,  # 1954-1959
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260,  # 1960-1965
    0x0f263, 0x0d950, 0x05b57, 0x056a0, 0x096d0, 0x04dd5,  # 1966-1971
    0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540,  # 1972-1977
    0x0b6a0, 0x195a6, 0x095b0, 0x049b0, 0x0a974, 0x0a4b0,  # 1978-1983
    0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,  # 1984-1989
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58,  # 1990-1995
    0x05ac0, 0x0ab60, 0x096d5, 0x092e0, 0x0c960, 0x0d954,  # 1996-2001
    0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0,  # 2002-2007
    0x092d0, 0x0cab5, 0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50,  # 2008-2013
    0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,  # 2014-2019
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6,  # 2020-2025
    0x0a4e0, 0x0d260, 0x0ea65, 0x0d530, 0x05aa0, 0x076a3,  # 2026-2031
    0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250,  # 2032-2037
    0x0d520, 0x0dd45, 0x0b5a0, 0x056d0, 0x055b2, 0x049b0,  # 2038-2043
    0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,  # 2044-2049
    0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6,  # 2050-2055
    0x0ea50, 0x06aa0, 0x1a6c4, 0x0aae0, 0x092e0, 0x0d2e3,  # 2056-2061
    0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0,  # 2062-2067
    0x0a6d0, 0x055d4, 0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0,  # 2068-2073
    0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,  # 2074-2079
    0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55,  # 2080-2085
    0x04b60, 0x0a570, 0x054e4, 0x0d160, 0x0e968, 0x0d520,  # 2086-2091
    0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a4d0,  # 2092-2097
    0x0d150, 0x0f252, 0x0d520, 0x0dd45, 0x0b5a0, 0x0b6d0,  # 2098-2103
    0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255,  # 2104-2109
]


def lunar_to_solar(year: int, month: int, day: int, is_leap_month: bool = False) -> date:
    """
    农历转公历。
    year: 农历年
    month: 农历月 (1-12)
    day: 农历日 (1-30)
    is_leap_month: 是否为闰月
    Returns: 对应的公历日期
    """
    if year < 1900 or year > 2100:
        raise ValueError(f"暂不支持{year}年的农历转换，支持范围1900-2100")

    info_idx = year - 1900
    if info_idx >= len(LUNAR_YEAR_INFO):
        info_idx = len(LUNAR_YEAR_INFO) - 1

    info = LUNAR_YEAR_INFO[info_idx]

    # 解码春节日期
    spring_festival_code = (info >> 20) & 0x0F
    # 简化：在没有精确编码的情况下使用查表
    # 春节通常在1月21日至2月20日之间
    # 使用近似值
    spring_month = 1
    spring_day = _get_spring_festival_day(year)

    spring_date = date(year, spring_month, spring_day)

    # 解码月天数
    leap_month = (info >> 16) & 0x0F  # 闰月月份, 0=无闰月
    leap_days = ((info >> 20) & 0x01) + 29  # 闰月天数

    # 计算从春节到目标日期的天数
    total_days = 0
    current_month = 1

    # 处理到目标月之前的所有月份
    for m in range(1, month):
        month_days = ((info >> (4 + m)) & 0x01) + 29
        total_days += month_days

    # 如果目标月在闰月之后（且存在闰月），需要加上闰月
    if leap_month > 0 and month > leap_month:
        total_days += leap_days
    elif leap_month > 0 and month == leap_month and is_leap_month:
        # 如果是闰月本身，先加正月的天数
        month_days = ((info >> (4 + month)) & 0x01) + 29
        total_days += month_days
        # 然后从闰月开始重新计算
        # 实际上不需要加，已经减了
        pass

    # 加上当月的天数偏移（日-1）
    total_days += day - 1

    return spring_date + timedelta(days=total_days)


def _get_spring_festival_day(year: int) -> int:
    """近似获取春节的公历日（1月中的第几天），精度足够排盘用。"""
    # 春节日期经验公式（1900-2100）
    # 立春在2月4日前后，春节在立春前后15天内
    # 简化：使用常见规律
    # 1900年春节: 1月31日
    base = date(1900, 1, 31)
    # 农历年约354.37天
    days_since = int((year - 1900) * 354.367)
    # 加上闰月修正
    leap_corrections = [0, 0, 1, 1, 2, 2, 3, 3, 4, 5, 5, 6, 6, 7, 7, 8, 9, 9, 10, 10,
                        11, 11, 12, 13, 13, 14, 14, 15, 15, 16, 17, 17, 18, 18, 19, 19,
                        20, 21, 21, 22, 22, 23, 23, 24, 25, 25, 26, 26, 27, 27, 28, 29,
                        29, 30, 30, 31, 31, 32, 33, 33, 34, 34, 35, 35, 36, 37, 37, 38,
                        38, 39, 39, 40, 41, 41, 42, 42, 43, 43, 44, 45, 45, 46, 46, 47,
                        47, 48, 49, 49, 50, 50, 51, 51, 52, 53, 53, 54, 54, 55, 55, 56]
    if year - 1900 < len(leap_corrections):
        days_since += leap_corrections[year - 1900] * 30

    approx = base + timedelta(days=int(days_since))
    # 确保在1月21日-2月20日之间
    while approx.month > 2 or (approx.month == 2 and approx.day > 20):
        approx -= timedelta(days=354)
    while approx.month < 1 or (approx.month == 1 and approx.day < 21):
        approx += timedelta(days=354)

    return approx.day


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 年柱计算（立春为界）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_nian_zhu(year: int, month: int, day: int) -> tuple[str, str]:
    """
    计算年柱。
    以立春（约2月4日）为界：立春前为上年，立春后为本年。
    返回 (天干, 地支)
    """
    # 获取立春日期
    li_chun = get_solar_term_date(year, 0)  # 立春

    if month < li_chun.month or (month == li_chun.month and day < li_chun.day):
        # 立春前，用上年
        actual_year = year - 1
    else:
        actual_year = year

    # 天干: (year - 4) % 10
    gan_idx = (actual_year - 4) % 10
    # 地支: (year - 4) % 12
    zhi_idx = (actual_year - 4) % 12

    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 月柱计算（节气分界）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_yue_zhu(year: int, month: int, day: int, nian_gan: str) -> tuple[str, str]:
    """
    计算月柱。
    节气分界：寅月立春,卯月惊蛰,...,丑月小寒。
    年干定月干（五虎遁）。
    返回 (天干, 地支)

    节气-月支映射（按年度节气序）：
      立春→寅(2), 惊蛰→卯(3), 清明→辰(4), 立夏→巳(5),
      芒种→午(6), 小暑→未(7), 立秋→申(8), 白露→酉(9),
      寒露→戌(10), 立冬→亥(11), 大雪→子(0), 小寒→丑(1)
    """
    current = date(year, month, day)

    # 收集当前年度的节气日期（立春~大雪）和上年末的节气（大雪、小寒）
    # 以及下年初的节气（小寒）
    # 我们构造12个节气覆盖全年：从立春(今年)到小寒(明年)
    # 节气索引: 0=立春(今年),1=惊蛰,...,10=大雪(今年),11=小寒(明年)

    # 构建从"本年立春"到"下年小寒"的节气序列
    # 其中大雪索引10在当前年，小寒索引11在明年
    all_terms = []
    all_terms.append(get_solar_term_date(year, 0))   # 立春
    all_terms.append(get_solar_term_date(year, 1))   # 惊蛰
    all_terms.append(get_solar_term_date(year, 2))   # 清明
    all_terms.append(get_solar_term_date(year, 3))   # 立夏
    all_terms.append(get_solar_term_date(year, 4))   # 芒种
    all_terms.append(get_solar_term_date(year, 5))   # 小暑
    all_terms.append(get_solar_term_date(year, 6))   # 立秋
    all_terms.append(get_solar_term_date(year, 7))   # 白露
    all_terms.append(get_solar_term_date(year, 8))   # 寒露
    all_terms.append(get_solar_term_date(year, 9))   # 立冬
    all_terms.append(get_solar_term_date(year, 10))  # 大雪
    all_terms.append(get_solar_term_date(year, 11))  # 小寒(明年)

    # 每个节气对应的月支索引
    term_branch_map = {
        0: 2,   # 立春→寅
        1: 3,   # 惊蛰→卯
        2: 4,   # 清明→辰
        3: 5,   # 立夏→巳
        4: 6,   # 芒种→午
        5: 7,   # 小暑→未
        6: 8,   # 立秋→申
        7: 9,   # 白露→酉
        8: 10,  # 寒露→戌
        9: 11,  # 立冬→亥
        10: 0,  # 大雪→子
        11: 1,  # 小寒→丑
    }

    # 如果当前日期在立春之前，属于上一年度的节气区间
    # 需要查找前一年的节气来定月份
    if current < all_terms[0]:
        # 收集上一年度末的节气：大雪、小寒
        prev_year_terms = []
        prev_year_terms.append(get_solar_term_date(year - 1, 10))  # 上年大雪
        prev_year_terms.append(get_solar_term_date(year - 1, 11))  # 上年小寒
        prev_year_terms.append(get_solar_term_date(year, 0))       # 本年立春

        # 找到当前日期在"上年大雪 → 上年小寒 → 本年立春"中的位置
        if current >= prev_year_terms[1]:  # 小寒后立春前 → 丑月
            branch_idx = 1  # 丑
            # 月干基于上一年年干（nian_gan是年柱天干，已经反映上年）
            actual_nian_gan = nian_gan
        elif current >= prev_year_terms[0]:  # 大雪后小寒前 → 子月
            branch_idx = 0  # 子
            actual_nian_gan = nian_gan
        else:
            # 大雪前 → 亥月（上上年的亥月）
            branch_idx = 11  # 亥
            actual_nian_gan = nian_gan
            # 如果是亥月，年柱可能更早（但月柱用年干推算）
    else:
        # 当前日期在立春之后（含立春）
        latest_idx = -1
        for i in range(12):
            if current >= all_terms[i]:
                latest_idx = i

        if latest_idx == 11:
            # 小寒之后 → 丑月（但在立春前已经被前面的分支捕获了）
            # 这里是小寒后立春前，但实际上已经在立春后...不可能
            branch_idx = 1
        elif latest_idx >= 0:
            branch_idx = term_branch_map[latest_idx]
        else:
            # fallback
            branch_idx = 2  # 寅

        actual_nian_gan = nian_gan

    # 用年干推算月干
    # 确定"寅月(正月)"的天干
    start_gan = WU_HU_DUN_YUE[actual_nian_gan]
    start_idx = TIAN_GAN.index(start_gan)

    # 寅=0偏移, 卯=1, ..., 丑=11
    offset_from_yin = (branch_idx - 2) % 12
    gan_idx = (start_idx + offset_from_yin) % 10

    return TIAN_GAN[gan_idx], DI_ZHI[branch_idx]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 日柱计算（Lilian日期算法）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_ri_zhu(year: int, month: int, day: int) -> tuple[str, str]:
    """
    计算日柱（使用Lilian日期算法）。
    返回 (天干, 地支)
    """
    # 使用简化算法：计算从1900年1月1日（甲子日）起的天数差
    # 1900年1月1日是甲子日
    base_date = date(1900, 1, 1)
    target_date = date(year, month, day)
    delta = (target_date - base_date).days

    # 甲子日: 天干0, 地支0
    # 注意：需验证1900年1月1日是否为甲子日
    # 历史上1900年1月1日(庚子年戊寅月癸亥日)
    # 癸亥 = 天干9, 地支11
    # 癸亥日到甲子日差1天
    # 所以1900年1月1日 + 1 = 甲子日
    # 或者直接用已知基准：2000年1月1日 = 甲午日(天干0,地支6)
    # 甲午 = 天干0, 地支6

    # 用2000年1月1日（戊午日）为基准 — 已验证: 2000-01-01 日柱=戊午
    base_date2 = date(2000, 1, 1)
    target_date = date(year, month, day)
    delta2 = (target_date - base_date2).days

    # 天干：甲=0, 乙=1, ...
    # 2000年1月1日戊午日 → 天干4(戊), 地支6(午)
    gan_idx = (4 + delta2) % 10  # 戊为4
    zhi_idx = (6 + delta2) % 12  # 午为6

    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 时柱计算
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_shi_zhu(hour: int, minute: int, ri_gan: str) -> tuple[str, str]:
    """
    计算时柱。
    时辰：子23-1,丑1-3,寅3-5,卯5-7,辰7-9,巳9-11,
         午11-13,未13-15,申15-17,酉17-19,戌19-21,亥21-23
    日干定时干（五鼠遁）。
    返回 (天干, 地支)
    """
    # 确定时辰地支
    if hour == 23 or hour < 1:
        zhi_idx = 0  # 子
    elif 1 <= hour < 3:
        zhi_idx = 1  # 丑
    elif 3 <= hour < 5:
        zhi_idx = 2  # 寅
    elif 5 <= hour < 7:
        zhi_idx = 3  # 卯
    elif 7 <= hour < 9:
        zhi_idx = 4  # 辰
    elif 9 <= hour < 11:
        zhi_idx = 5  # 巳
    elif 11 <= hour < 13:
        zhi_idx = 6  # 午
    elif 13 <= hour < 15:
        zhi_idx = 7  # 未
    elif 15 <= hour < 17:
        zhi_idx = 8  # 申
    elif 17 <= hour < 19:
        zhi_idx = 9  # 酉
    elif 19 <= hour < 21:
        zhi_idx = 10  # 戌
    else:
        zhi_idx = 11  # 亥

    # 时干 = 五鼠遁确定的子时天干 + 时辰偏移
    start_gan = WU_SHU_DUN_SHI[ri_gan]
    start_idx = TIAN_GAN.index(start_gan)
    gan_idx = (start_idx + zhi_idx) % 10

    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 十神计算
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_shi_shen(ri_gan: str, gan: str) -> str:
    """
    根据日干定十神。
    生我者印(阴阳异正印/同偏印)，
    我生者食伤(阳食阴伤/阳伤阴食)，
    克我者官杀(阴阳异正官/同七杀)，
    我克者财(阴阳异正财/同偏财)，
    同我者比劫(阴阳同比肩/异劫财)。
    """
    ri_idx = TIAN_GAN.index(ri_gan)
    gan_idx = TIAN_GAN.index(gan)

    ri_yin = ri_idx % 2  # 0=阳, 1=阴
    gan_yin = gan_idx % 2

    # 五行的关系
    # 木火土金水: 0木,1火,2土,3金,4水
    wu_xing_order = ["木", "火", "土", "金", "水"]
    ri_wx = wu_xing_order.index(TIAN_GAN_WU_XING[ri_gan])
    gan_wx = wu_xing_order.index(TIAN_GAN_WU_XING[gan])

    # 同我(比劫)
    if ri_wx == gan_wx:
        return "比肩" if ri_yin == gan_yin else "劫财"

    # 我生(食伤): 木→火, 火→土, 土→金, 金→水, 水→木
    sheng_idx = (ri_wx + 1) % 5
    if gan_wx == sheng_idx:
        return "食神" if ri_yin == gan_yin else "伤官"

    # 我克(财): 木→土, 火→金, 土→水, 金→木, 水→火
    ke_idx = (ri_wx + 2) % 5
    if gan_wx == ke_idx:
        return "正财" if ri_yin != gan_yin else "偏财"

    # 克我(官杀): 木→金, 火→水, 土→木, 金→火, 水→土
    be_ke_idx = (ri_wx + 3) % 5
    if gan_wx == be_ke_idx:
        return "正官" if ri_yin != gan_yin else "七杀"

    # 生我(印): 木→水, 火→木, 土→火, 金→土, 水→金
    be_sheng_idx = (ri_wx + 4) % 5
    if gan_wx == be_sheng_idx:
        return "正印" if ri_yin != gan_yin else "偏印"

    return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 身强弱评分
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_shen_qiang_ruo(ri_gan: str, nian_gan: str, yue_gan: str,
                        ri_zhi: str, shi_gan: str,
                        nian_zhi: str, yue_zhi: str, shi_zhi: str,
                        gender: int) -> dict:
    """
    身强弱计算。
    评分规则：
    - 月令本气印 = +40分（本气是印才计）
    - 月令比劫 = +40分（本气是比劫才计）
    - 天干比劫 = 年干4分, 月干8分, 日干8分, 时干8分（含日干自身）
    - 年时支比劫 = 4分（藏干中的比劫按比例）
    - 日支印比 = 12分（藏干中的印比按比例）
    - 其他位置的印不计分

    40分以下身弱，40-55分中和，55分以上身强。
    当非月令克泄耗(官杀+食伤+财) > 2倍非月令印比时，判为从弱格。
    """
    score = 0
    details = []

    # 日干五行
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    wu_xing_order = ["木", "火", "土", "金", "水"]
    ri_wx_idx = wu_xing_order.index(ri_wx)

    # 五行索引
    bi_jie_wx_idx = ri_wx_idx          # 同我=比劫
    yin_wx_idx = (ri_wx_idx + 4) % 5   # 生我=印
    guan_sha_wx_idx = (ri_wx_idx + 3) % 5  # 克我=官杀
    shi_shang_wx_idx = (ri_wx_idx + 1) % 5  # 我生=食伤
    cai_wx_idx = (ri_wx_idx + 2) % 5      # 我克=财

    ke_xie_hao_wxs = {wu_xing_order[guan_sha_wx_idx],
                      wu_xing_order[shi_shang_wx_idx],
                      wu_xing_order[cai_wx_idx]}

    # 1. 月令本气印 = +40分
    yue_zhi_ben_qi = DI_ZHI_CANG_GAN[yue_zhi][0][0]  # 本气
    yue_zhi_ben_qi_wx = TIAN_GAN_WU_XING[yue_zhi_ben_qi]

    if yue_zhi_ben_qi_wx == wu_xing_order[yin_wx_idx]:
        score += 40
        details.append(f"月令本气印({yue_zhi_ben_qi}) +40")

    # 2. 月令比劫 = +40分
    if yue_zhi_ben_qi_wx == ri_wx:
        score += 40
        details.append(f"月令比劫({yue_zhi_ben_qi}) +40")

    # 3. 天干比劫: 年干4分, 月干8分, 日干8分, 时干8分
    #   (含日干自身; 用位置而非字符值判断)
    tian_gan_positions = [
        ("年干", nian_gan, 4),
        ("月干", yue_gan, 8),
        ("日干", ri_gan, 8),
        ("时干", shi_gan, 8),
    ]

    for pos, gan, pts in tian_gan_positions:
        if TIAN_GAN_WU_XING[gan] == ri_wx:
            score += pts
            details.append(f"天干{pos}比劫({gan}) +{pts}")

    # 4. 年时支比劫 = 4分（藏干中的比劫按比例）
    for pos, zhi in [("年支", nian_zhi), ("时支", shi_zhi)]:
        for cang_gan, weight in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cang_gan] == ri_wx:
                # 比劫
                pts = 4 * weight / 100
                if pts > 0:
                    score += pts
                    details.append(f"{pos}藏干比劫({cang_gan}) +{pts:.1f}")

    # 5. 日支印比 = 12分（藏干中的印比按比例）
    for cang_gan, weight in DI_ZHI_CANG_GAN[ri_zhi]:
        cang_wx = TIAN_GAN_WU_XING[cang_gan]
        if cang_wx == ri_wx:
            # 比劫
            pts = 12 * weight / 100
            score += pts
            details.append(f"日支藏干比劫({cang_gan}) +{pts:.1f}")
        elif cang_wx == wu_xing_order[yin_wx_idx]:
            # 印
            pts = 12 * weight / 100
            score += pts
            details.append(f"日支藏干印({cang_gan}) +{pts:.1f}")

    # ── 6. 从弱格检测 ────────────────────────────────────────────
    # 计算克泄耗分数（官杀+食伤+财），与印比分对比
    ke_score = 0
    ke_details = []

    # 6a. 月令本气克泄耗
    if yue_zhi_ben_qi_wx in ke_xie_hao_wxs:
        ke_score += 40
        ke_details.append(f"月令本气克泄耗({yue_zhi_ben_qi}) +40")

    # 6b. 天干克泄耗（日干自身不计）
    for pos, gan, pts in [
        ("年干", nian_gan, 4),
        ("月干", yue_gan, 8),
        ("时干", shi_gan, 4),
    ]:
        if TIAN_GAN_WU_XING[gan] in ke_xie_hao_wxs:
            ke_score += pts
            ke_details.append(f"天干{pos}克泄耗({gan}) +{pts}")

    # 6c. 年时支克泄耗
    for pos, zhi in [("年支", nian_zhi), ("时支", shi_zhi)]:
        for cang_gan, weight in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cang_gan] in ke_xie_hao_wxs:
                pts = 4 * weight / 100
                if pts > 0:
                    ke_score += pts
                    ke_details.append(f"{pos}藏干克泄耗({cang_gan}) +{pts:.1f}")

    # 6d. 日支克泄耗
    for cang_gan, weight in DI_ZHI_CANG_GAN[ri_zhi]:
        if TIAN_GAN_WU_XING[cang_gan] in ke_xie_hao_wxs:
            pts = 12 * weight / 100
            ke_score += pts
            ke_details.append(f"日支藏干克泄耗({cang_gan}) +{pts:.1f}")

    # 6e. 从弱判定：非月令克泄耗 > 2×非月令印比
    #      且命局中无其他比劫支撑（日主自身除外）
    fei_yue_yin_bi = score
    if yue_zhi_ben_qi_wx in (ri_wx, wu_xing_order[yin_wx_idx]):
        fei_yue_yin_bi -= 40

    fei_yue_ke = ke_score
    if yue_zhi_ben_qi_wx in ke_xie_hao_wxs:
        fei_yue_ke -= 40

    # 检查命局中是否有其他比劫（天干/地支，不含日主自身）
    has_other_bi_jie = False
    for gan in [nian_gan, yue_gan, shi_gan]:
        if TIAN_GAN_WU_XING[gan] == ri_wx:
            has_other_bi_jie = True
            break
    if not has_other_bi_jie:
        for zhi in [nian_zhi, yue_zhi, ri_zhi, shi_zhi]:
            for cang_gan, _ in DI_ZHI_CANG_GAN[zhi]:
                if TIAN_GAN_WU_XING[cang_gan] == ri_wx:
                    has_other_bi_jie = True
                    break
            if has_other_bi_jie:
                break

    if fei_yue_ke > 2 * fei_yue_yin_bi and score < 60 and not has_other_bi_jie:
        return {
            "score": 50.0,
            "level": "从弱",
            "details": (details + ke_details
                        + [f"非月令克泄耗({fei_yue_ke:.1f}) > 2×非月令印比({fei_yue_yin_bi:.1f})，判从弱格"]),
        }

    # ── 判定 ─────────────────────────────────────────────────────
    if score < 40:
        level = "身弱"
    elif score <= 55:
        level = "中和"
    else:
        level = "身强"

    return {
        "score": round(score, 1),
        "level": level,
        "details": details,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 格局（月令本气取格）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 格局命名映射表：十神 → 专业格局名
GE_JU_NAME_MAP = {
    "正官": "正官格",
    "七杀": "七杀格",
    "正印": "正印格",
    "偏印": "偏印格",
    "正财": "正财格",
    "偏财": "偏财格",
    "食神": "食神格",
    "伤官": "伤官格",
    "比肩": "建禄格",
    "劫财": "劫财格",
}


def _get_ge_ju(ri_gan: str, yue_zhi: str) -> str:
    """
    格局：月令本气取格，与身强弱无关。

    格局仅由月令本气与日干的十神关系决定。
    身强弱（从弱格、身强、身弱）是独立于格局的维度。

    特殊映射规则：
      - 比肩月令 → 建禄格（不称"比肩格"）
      - 劫财月令 → 劫财格
      - 其他十神 → X格（如正官格、偏印格等）

    金标准对照：
      庚申 癸未 辛亥 辛卯,男 → 未月本气己土, 己生辛(偏印) → 偏印格 ✓
      辛卯 癸巳 丙戌 癸巳,男 → 巳月本气丙火, 丙比肩 → 建禄格 ✓
      丁卯 丁未 庚午 壬午,女 → 未月本气己土, 己生庚(正印) → 正印格 ✓
      丁卯 丁未 庚午 壬午,女 → 从弱格(身强弱) + 正印格(格局) ✓
    """
    ben_qi = DI_ZHI_CANG_GAN[yue_zhi][0][0]
    shi_shen = _get_shi_shen(ri_gan, ben_qi)
    return GE_JU_NAME_MAP.get(shi_shen, shi_shen)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 喜用神
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_xi_yong_shen(ri_gan: str, shen_qiang_level: str) -> dict:
    """
    喜用神：返回具体五行（火木水等），与知识库金标准一致。
    身强/从弱喜克泄耗（官杀/食伤/财对应的五行），
    身弱喜生扶（印/比劫对应的五行）。
    返回 {xi_shen: [], yong_shen: [], ji_shen: []}
    """
    wu_xing_order = ["木", "火", "土", "金", "水"]
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    if not ri_wx or ri_wx not in wu_xing_order:
        return {"xi_shen": [], "yong_shen": [], "ji_shen": []}
    ri_wx_idx = wu_xing_order.index(ri_wx)

    # 计算各五行索引
    # 克我=官杀: (ri+3)%5
    guan_sha_wx = wu_xing_order[(ri_wx_idx + 3) % 5]
    # 我生=食伤: (ri+1)%5
    shi_shang_wx = wu_xing_order[(ri_wx_idx + 1) % 5]
    # 我克=财: (ri+2)%5
    cai_wx = wu_xing_order[(ri_wx_idx + 2) % 5]
    # 生我=印: (ri+4)%5
    yin_wx = wu_xing_order[(ri_wx_idx + 4) % 5]
    # 同我=比劫
    bi_jie_wx = ri_wx

    if shen_qiang_level in ("身强", "从弱"):
        # 身强/从弱喜克泄耗：官杀/食伤/财对应的五行
        xi = [guan_sha_wx, cai_wx, shi_shang_wx]
        # 忌生扶：印/比劫对应的五行
        ji = [yin_wx, bi_jie_wx]
    else:
        # 身弱喜生扶：印/比劫对应的五行
        xi = [yin_wx, bi_jie_wx]
        # 忌克泄耗：官杀/食伤/财对应的五行
        ji = [guan_sha_wx, shi_shang_wx, cai_wx]

    # 用神 = 喜神中第一个
    yong = [xi[0]]

    return {
        "xi_shen": xi,
        "yong_shen": yong,
        "ji_shen": ji,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 大运计算
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _calc_da_yun(nian_gan: str, nian_zhi: str, gender: int,
                 year: int, month: int, day: int,
                 hour: int, minute: int) -> dict:
    """
    大运计算。
    阳男阴女顺排，阴男阳女逆排。
    起运岁数：3天=1岁，1天=4个月，1时辰=10天。
    """
    # 性别: 0=女, 1=男
    nian_gan_yin = TIAN_GAN.index(nian_gan) % 2
    nian_zhi_yin = DI_ZHI.index(nian_zhi) % 2

    # 阳年: 天干为阳(甲丙戊庚壬=索引0,2,4,6,8)
    is_yang_nian = TIAN_GAN.index(nian_gan) % 2 == 0

    # 阳男阴女顺排, 阴男阳女逆排
    is_shun_pai = (is_yang_nian and gender == 1) or (not is_yang_nian and gender == 0)

    # 找下一个或上一个节气
    birth_date = datetime(year, month, day, hour, minute)

    if is_shun_pai:
        # 顺排：找下一个节气
        next_term_idx = -1
        next_term_date = None
        for i in range(12):
            td = get_solar_term_date(year, i)
            term_dt = datetime(td.year, td.month, td.day, 0, 0)
            if term_dt > birth_date:
                if next_term_date is None or term_dt < next_term_date:
                    next_term_date = term_dt
                    next_term_idx = i
        if next_term_date is None:
            # 下一年立春
            next_term_date = datetime(year + 1, 2, 4, 0, 0)
            next_term_idx = 0

        # 计算起运天数差
        days_diff = (next_term_date - birth_date).total_seconds() / 86400

        # 月柱开始
        start_branch_idx = JIE_QI_TO_MONTH_BRANCH.get(next_term_idx + 1 if next_term_idx >= 0 else 1, 2)
        start_gan = WU_HU_DUN_YUE[nian_gan]
        start_gan_idx = TIAN_GAN.index(start_gan)
        offset = (start_branch_idx - 2) % 12

        # 大运干支序列
        da_yun_list = []
        for step in range(8):  # 最多8个大运
            gan_idx = (start_gan_idx + offset + step) % 10
            zhi_idx = (start_branch_idx + step) % 12
            da_yun_list.append(TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx])

    else:
        # 逆排：找上一个节气
        prev_term_idx = -1
        prev_term_date = None
        for i in range(11, -1, -1):
            td = get_solar_term_date(year, i)
            term_dt = datetime(td.year, td.month, td.day, 0, 0)
            if term_dt < birth_date:
                if prev_term_date is None or term_dt > prev_term_date:
                    prev_term_date = term_dt
                    prev_term_idx = i
        if prev_term_date is None:
            # 上一年大雪
            prev_term_date = datetime(year - 1, 12, 7, 0, 0)
            prev_term_idx = 10

        # 计算起运天数差
        days_diff = (birth_date - prev_term_date).total_seconds() / 86400

        # 月柱开始
        start_branch_idx = JIE_QI_TO_MONTH_BRANCH.get(prev_term_idx + 1 if prev_term_idx >= 0 else 1, 2)
        start_gan = WU_HU_DUN_YUE[nian_gan]
        start_gan_idx = TIAN_GAN.index(start_gan)
        offset = (start_branch_idx - 2) % 12

        # 大运干支序列（逆排：从月柱的上一个干支开始）
        da_yun_list = []
        for step in range(1, 9):  # 从月柱前一个干支开始，共8个大运
            gan_idx = (start_gan_idx + offset - step) % 10
            zhi_idx = (start_branch_idx - step) % 12
            da_yun_list.append(TIAN_GAN[gan_idx] + DI_ZHI[zhi_idx])

    # 起运岁数 = 3天=1岁
    qi_yun_age = days_diff / 3  # 岁
    qi_yun_age_years = int(qi_yun_age)
    qi_yun_age_months = int((qi_yun_age - qi_yun_age_years) * 12)
    qi_yun_age_days = int(((qi_yun_age - qi_yun_age_years) * 12 - qi_yun_age_months) * 30)

    # 各步大运的起运年龄
    da_yun_with_age = []
    for i, dy in enumerate(da_yun_list):
        start_age = round(qi_yun_age + i * 10, 1)
        end_age = round(qi_yun_age + (i + 1) * 10, 1)
        da_yun_with_age.append({
            "index": i,
            "gan_zhi": dy,
            "gan": dy[0],
            "zhi": dy[1],
            "start_age": start_age,
            "end_age": end_age,
        })

    return {
        "is_shun_pai": is_shun_pai,
        "qi_yun_age_years": qi_yun_age_years,
        "qi_yun_age_months": qi_yun_age_months,
        "qi_yun_age_days": qi_yun_age_days,
        "qi_yun_age": round(qi_yun_age, 2),
        "da_yun": da_yun_with_age,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 财星评分
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _calc_cai_xing(ri_gan: str, nian_gan: str, yue_gan: str,
                   shi_gan: str, nian_zhi: str, yue_zhi: str,
                   ri_zhi: str, shi_zhi: str) -> dict:
    """
    财星评分。
    规则：
    - 年支4分
    - 月令40分
    - 日/时支12分
    - 藏干按比例
    """
    wu_xing_order = ["木", "火", "土", "金", "水"]
    ri_wx = TIAN_GAN_WU_XING[ri_gan]
    ri_wx_idx = wu_xing_order.index(ri_wx)

    # 我克者财: ri_wx → (ri_wx + 2) % 5
    cai_wx_idx = (ri_wx_idx + 2) % 5
    cai_wx = wu_xing_order[cai_wx_idx]

    score = 0
    details = []

    # 天干财星
    for pos, gan, pts in [("年干", nian_gan, 4), ("月干", yue_gan, 8),
                           ("日干", ri_gan, 8), ("时干", shi_gan, 4)]:
        if TIAN_GAN_WU_XING[gan] == cai_wx and gan != ri_gan:
            score += pts
            details.append(f"{pos}({gan})财星 +{pts}")

    # 地支财星（藏干按比例）
    for pos, zhi, base_pts in [("年支", nian_zhi, 4), ("月支", yue_zhi, 40),
                                ("日支", ri_zhi, 12), ("时支", shi_zhi, 12)]:
        for cang_gan, weight in DI_ZHI_CANG_GAN[zhi]:
            if TIAN_GAN_WU_XING[cang_gan] == cai_wx:
                pts = base_pts * weight / 100
                score += pts
                details.append(f"{pos}藏干({cang_gan})财星 +{pts:.1f}")

    # 财富五级
    shen_qiang = _get_shen_qiang_ruo(ri_gan, nian_gan, yue_gan, ri_zhi, shi_gan,
                                      nian_zhi, yue_zhi, shi_zhi, 1)
    is_qiang = shen_qiang["level"] == "身强"

    # 是否有财库：辰戌丑未为财库（根据五行）
    # 金库丑, 木库未, 水库辰, 火库戌
    cai_ku_map = {
        "木": "未",  # 木财库
        "火": "戌",  # 火财库
        "土": "辰",  # 土财库
        "金": "丑",  # 金财库
        "水": "辰",  # 水财库
    }
    cai_ku = cai_ku_map.get(cai_wx, "")
    has_ku = cai_ku in [nian_zhi, yue_zhi, ri_zhi, shi_zhi]

    if score >= 80 and is_qiang and has_ku:
        wealth_level = "巨富"
    elif score >= 60 and is_qiang:
        wealth_level = "大富"
    elif score >= 26:
        wealth_level = "中富"
    elif score >= 12:
        wealth_level = "小富"
    else:
        wealth_level = "贫穷"

    return {
        "score": round(score, 1),
        "has_ku": has_ku,
        "cai_ku": cai_ku,
        "wealth_level": wealth_level,
        "details": details,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 五行能量分析
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _calc_wu_xing_energy(ri_gan: str, nian_gan: str, yue_gan: str,
                          shi_gan: str, nian_zhi: str, yue_zhi: str,
                          ri_zhi: str, shi_zhi: str) -> dict:
    """
    计算五行能量分布。
    天干：年时干4, 月日干8
    地支本气：年时支4, 月支40, 日支12
    藏干按比例贡献。
    """
    elements = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    # 天干
    gan_weights = {
        nian_gan: 4, yue_gan: 8, ri_gan: 8, shi_gan: 4
    }
    for gan, wt in gan_weights.items():
        elements[TIAN_GAN_WU_XING[gan]] += wt

    # 地支本气
    zhi_base = {
        nian_zhi: 4, yue_zhi: 40, ri_zhi: 12, shi_zhi: 4
    }
    # 但对藏干要按比例，我们直接用藏干评分
    # 为避免重复，这里用藏干方式统一处理
    elements = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    # 重新：天干全算
    for gan, wt in gan_weights.items():
        elements[TIAN_GAN_WU_XING[gan]] += wt

    # 地支：藏干按比例
    for pos, zhi, base_pts in [("年支", nian_zhi, 4), ("月支", yue_zhi, 40),
                                ("日支", ri_zhi, 12), ("时支", shi_zhi, 4)]:
        for cang_gan, weight in DI_ZHI_CANG_GAN[zhi]:
            pts = base_pts * weight / 100
            elements[TIAN_GAN_WU_XING[cang_gan]] += pts

    # 百分比归一化
    total = sum(elements.values())
    if total > 0:
        percentages = {k: round(v / total * 100, 1) for k, v in elements.items()}
    else:
        percentages = {k: 0.0 for k in elements}

    # 找出旺（最高）和弱（最低）的五行
    sorted_elements = sorted(elements.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_elements[0][0]
    weakest = sorted_elements[-1][0]

    return {
        "raw_scores": {k: round(v, 1) for k, v in elements.items()},
        "percentages": percentages,
        "strongest": strongest,
        "weakest": weakest,
        "total": round(total, 1),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 四柱八字排列
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_pillar_data(gan: str, zhi: str, ri_gan: str,
                       nian_gan: str, nian_zhi: str, position: str) -> dict:
    """构建一柱的数据。"""
    cang_gan = []
    for cg, w in DI_ZHI_CANG_GAN[zhi]:
        cang_gan.append({
            "gan": cg,
            "weight": w,
            "shi_shen": _get_shi_shen(ri_gan, cg),
            "wu_xing": TIAN_GAN_WU_XING[cg],
        })

    return {
        "gan": gan,
        "zhi": zhi,
        "gan_shi_shen": _get_shi_shen(ri_gan, gan),
        "gan_wu_xing": TIAN_GAN_WU_XING[gan],
        "zhi_wu_xing": DI_ZHI_WU_XING[zhi],
        "cang_gan": cang_gan,
        "na_yin": na_yin(gan, zhi),
        "kong_wang": kong_wang(gan, zhi),
        "shen_sha": get_shen_sha(gan, zhi, ri_gan, nian_gan, nian_zhi),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 主入口：calculate_bazi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_bazi(year: int, month: int, day: int,
                   hour: int = 12, minute: int = 0,
                   is_lunar: bool = False,
                   gender: int = 1) -> dict:
    """
    八字排盘主函数。

    Args:
        year: 公历年份（若is_lunar=True则为农历年份）
        month: 月份（若is_lunar=True则为农历月份）
        day: 日期（若is_lunar=True则为农历日期）
        hour: 时辰（小时, 0-23）
        minute: 分钟
        is_lunar: 是否农历输入
        gender: 性别（0=女, 1=男）

    Returns:
        dict: {
            "basic": {八字基础信息},
            "analysis": {命理分析信息},
        }
    """
    # 农历转公历
    if is_lunar:
        solar_date = lunar_to_solar(year, month, day)
        year, month, day = solar_date.year, solar_date.month, solar_date.day

    # ── 四柱 ──
    nian_gan, nian_zhi = _get_nian_zhu(year, month, day)
    yue_gan, yue_zhi = _get_yue_zhu(year, month, day, nian_gan)
    ri_gan, ri_zhi = _get_ri_zhu(year, month, day)
    shi_gan, shi_zhi = _get_shi_zhu(hour, minute, ri_gan)

    # 八字字符串
    ba_zi_str = f"{nian_gan}{nian_zhi} {yue_gan}{yue_zhi} {ri_gan}{ri_zhi} {shi_gan}{shi_zhi}"

    # ── 各柱详情 ──
    nian_zhu = _build_pillar_data(nian_gan, nian_zhi, ri_gan, nian_gan, nian_zhi, "年")
    yue_zhu = _build_pillar_data(yue_gan, yue_zhi, ri_gan, nian_gan, nian_zhi, "月")
    ri_zhu = _build_pillar_data(ri_gan, ri_zhi, ri_gan, nian_gan, nian_zhi, "日")
    shi_zhu = _build_pillar_data(shi_gan, shi_zhi, ri_gan, nian_gan, nian_zhi, "时")

    pillars = {
        "nian": nian_zhu,
        "yue": yue_zhu,
        "ri": ri_zhu,
        "shi": shi_zhu,
    }

    # ── 分析 ──
    # 身强弱
    shen_qiang = _get_shen_qiang_ruo(ri_gan, nian_gan, yue_gan, ri_zhi, shi_gan,
                                      nian_zhi, yue_zhi, shi_zhi, gender)

    # 格局
    ge_ju = _get_ge_ju(ri_gan, yue_zhi)

    # 喜用神
    xi_yong = _get_xi_yong_shen(ri_gan, shen_qiang["level"])

    # 五行能量
    energy = _calc_wu_xing_energy(ri_gan, nian_gan, yue_gan, shi_gan,
                                   nian_zhi, yue_zhi, ri_zhi, shi_zhi)

    # 大运
    da_yun = _calc_da_yun(nian_gan, nian_zhi, gender,
                           year, month, day, hour, minute)

    # 财星评分
    cai_xing = _calc_cai_xing(ri_gan, nian_gan, yue_gan, shi_gan,
                               nian_zhi, yue_zhi, ri_zhi, shi_zhi)

    # 基础信息
    basic = {
        "ba_zi": ba_zi_str,
        "ri_zhu": ri_gan + ri_zhi,
        "ri_gan": ri_gan,
        "ri_zhi": ri_zhi,
        "nian_gan": nian_gan,
        "nian_zhi": nian_zhi,
        "yue_gan": yue_gan,
        "yue_zhi": yue_zhi,
        "shi_gan": shi_gan,
        "shi_zhi": shi_zhi,
        "gender": "男" if gender == 1 else "女",
        "solar_date": f"{year}年{month}月{day}日",
        "pillars": pillars,
    }

    analysis = {
        "shen_qiang_ruo": shen_qiang,
        "ge_ju": ge_ju,
        "xi_yong_shen": xi_yong,
        "energy": energy,
        "cai_xing": cai_xing,
        "da_yun": da_yun,
        "dimensions": {
            "shen_qiang": shen_qiang,
            "cai_xing": cai_xing,
            "ge_ju": ge_ju,
            "xi_yong": xi_yong,
        },
    }

    return {
        "basic": basic,
        "analysis": analysis,
    }
