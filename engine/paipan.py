"""
金鉴真人·八字排盘引擎 v1.0
从公历日期+时辰 → 四柱八字
"""

from __future__ import annotations
from datetime import datetime, date

# ── 天干地支 ──
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# ── 月支映射 ──
YUE_ZHI = {1: "寅", 2: "卯", 3: "辰", 4: "巳", 5: "午", 6: "未",
           7: "申", 8: "酉", 9: "戌", 10: "亥", 11: "子", 12: "丑"}

# ── 五虎遁（年干→月干起始）──
WU_HU_DUN = {
    "甲": "丙", "乙": "戊", "丙": "庚", "丁": "壬", "戊": "甲",
    "己": "丙", "庚": "戊", "辛": "庚", "壬": "壬", "癸": "甲",
}

# ── 五鼠遁（日干→时干起始）──
WU_SHU_DUN = {
    "甲": "甲", "乙": "丙", "丙": "戊", "丁": "庚", "戊": "壬",
    "己": "甲", "庚": "丙", "辛": "戊", "壬": "庚", "癸": "壬",
}

# ── 时辰地支映射 ──
SHI_CHEN = {
    0: "子", 1: "丑", 2: "寅", 3: "卯", 4: "辰", 5: "巳",
    6: "午", 7: "未", 8: "申", 9: "酉", 10: "戌", 11: "亥",
}

# ── 节气日期表（简化：每月大概的分界日）──
# 用于判断年柱/月柱的立春分界
# 立春大约在2月4日
LI_CHUN = {}


def get_year_gan_zhi(year: int, month: int, day: int) -> tuple[str, str]:
    """
    获取年柱天干地支
    年柱以立春（约2月4日）为分界
    """
    # 立春前算上一年
    if month < 2 or (month == 2 and day < 4):
        year -= 1
    
    gan_idx = (year - 4) % 10
    zhi_idx = (year - 4) % 12
    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


def get_month_gan_zhi(year_gan: str, month: int, day: int) -> tuple[str, str]:
    """
    获取月柱天干地支（五虎遁）
    月柱以节气为分界（简化：以每月大概的节气日）
    """
    # 节气大约日期（简化版）
    jie_qi_day = {
        1: 6,   # 小寒
        2: 4,   # 立春
        3: 6,   # 惊蛰
        4: 5,   # 清明
        5: 6,   # 立夏
        6: 6,   # 芒种
        7: 7,   # 小暑
        8: 7,   # 立秋
        9: 8,   # 白露
        10: 8,  # 寒露
        11: 7,  # 立冬
        12: 7,  # 大雪
    }
    
    # 判断实际月支（节气分界）
    if day < jie_qi_day.get(month, 1):
        # 在本月节气之前 → 属于上个月的节气月
        real_month = month - 2
    else:
        # 在本月节气之后 → 属于本月的节气月
        real_month = month - 1
    
    # 边界回绕（1月→12月）
    if real_month <= 0:
        real_month += 12
    elif real_month > 12:
        real_month -= 12
    
    # 月支
    month_zhi = YUE_ZHI.get(real_month, "子")
    
    # 五虎遁：月干 = f(年干, 月支)
    start_gan = WU_HU_DUN.get(year_gan, "丙")
    start_idx = TIAN_GAN.index(start_gan)
    
    # 月支对应序号（寅=0, 卯=1, ...）
    zhi_order = {"寅": 0, "卯": 1, "辰": 2, "巳": 3, "午": 4, "未": 5,
                 "申": 6, "酉": 7, "戌": 8, "亥": 9, "子": 10, "丑": 11}
    offset = zhi_order.get(month_zhi, 0)
    gan_idx = (start_idx + offset) % 10
    
    return TIAN_GAN[gan_idx], month_zhi


def get_day_gan_zhi(target_date: date) -> tuple[str, str]:
    """
    获取日柱天干地支（使用标准算法-基准日法）
    基准：2000年1月1日 = 甲午日（干支序号30，0-based）
    """
    from datetime import date as dt_date
    base_date = dt_date(2000, 1, 1)
    delta = (target_date - base_date).days
    
    # 2000年1月1日是戊午日 → 干支序号54(0-based)
    base_seq = 54  # 戊午日对应的0-based干支序号
    seq = (base_seq + delta) % 60
    if seq < 0:
        seq += 60
    
    gan_idx = seq % 10
    zhi_idx = seq % 12
    
    return TIAN_GAN[gan_idx], DI_ZHI[zhi_idx]


def get_hour_gan_zhi(day_gan: str, hour: int) -> tuple[str, str]:
    """
    获取时柱天干地支（五鼠遁）
    """
    shi_chen_zhi = SHI_CHEN.get(((hour + 1) // 2) % 12, "子")
    
    # 五鼠遁
    start_gan = WU_SHU_DUN.get(day_gan, "甲")
    start_idx = TIAN_GAN.index(start_gan)
    
    zhi_order = {"子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
                 "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11}
    offset = zhi_order.get(shi_chen_zhi, 0)
    gan_idx = (start_idx + offset) % 10
    
    return TIAN_GAN[gan_idx], shi_chen_zhi


def paipan(name: str, gender: str, birth_year: int, birth_month: int,
           birth_day: int, birth_hour: int) -> dict:
    """
    完整排盘：从出生日期 → 四柱八字
    name: 姓名
    gender: 男/女
    birth_year/month/day/hour: 公历出生日期
    """
    target_date = date(birth_year, birth_month, birth_day)
    
    # 年柱
    year_gan, year_zhi = get_year_gan_zhi(birth_year, birth_month, birth_day)
    
    # 月柱
    month_gan, month_zhi = get_month_gan_zhi(year_gan, birth_month, birth_day)
    
    # 日柱
    day_gan, day_zhi = get_day_gan_zhi(target_date)
    
    # 时柱
    hour_gan, hour_zhi = get_hour_gan_zhi(day_gan, birth_hour)
    
    # 时辰中文名
    shi_chen_names = {
        "子": "子时(23:00-00:59)", "丑": "丑时(01:00-02:59)",
        "寅": "寅时(03:00-04:59)", "卯": "卯时(05:00-06:59)",
        "辰": "辰时(07:00-08:59)", "巳": "巳时(09:00-10:59)",
        "午": "午时(11:00-12:59)", "未": "未时(13:00-14:59)",
        "申": "申时(15:00-16:59)", "酉": "酉时(17:00-18:59)",
        "戌": "戌时(19:00-20:59)", "亥": "亥时(21:00-22:59)",
    }
    
    bazi_str = f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}"
    
    return {
        "name": name,
        "gender": gender,
        "birth_date": f"{birth_year}年{birth_month}月{birth_day}日",
        "birth_hour": birth_hour,
        "shi_chen": shi_chen_names.get(hour_zhi, f"{hour_zhi}时"),
        "bazi": bazi_str,
        "year_pillar": {"gan": year_gan, "zhi": year_zhi},
        "month_pillar": {"gan": month_gan, "zhi": month_zhi},
        "day_pillar": {"gan": day_gan, "zhi": day_zhi},
        "hour_pillar": {"gan": hour_gan, "zhi": hour_zhi},
    }


if __name__ == "__main__":
    # 测试：1980年5月15日 中午12点 男
    result = paipan("测试", "男", 1980, 5, 15, 12)
    print(f"姓名: {result['name']}")
    print(f"出生: {result['birth_date']} {result['shi_chen']}")
    print(f"八字: {result['bazi']}")
    print(f"年柱: {result['year_pillar']['gan']}{result['year_pillar']['zhi']}")
    print(f"月柱: {result['month_pillar']['gan']}{result['month_pillar']['zhi']}")
    print(f"日柱: {result['day_pillar']['gan']}{result['day_pillar']['zhi']}")
    print(f"时柱: {result['hour_pillar']['gan']}{result['hour_pillar']['zhi']}")
    
    # 测试2：家主 1968年5月15日
    result2 = paipan("家主", "男", 1968, 5, 15, 0)
    print(f"\n家主: {result2['bazi']} (期望: 甲午 己巳 戊午 ???)")
