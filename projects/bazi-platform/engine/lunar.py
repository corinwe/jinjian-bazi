"""
金鉴真人·农历转阳历引擎 v1.0
支持 1900-2100 年农历日期转公历
"""

from datetime import date, timedelta

# ── 农历数据表（1900-2100年）──
# 每个元素 = 当年农历信息
# 编码: 前12位=每月大小月(1=30天/0=29天), 后4位=闰月月份(0=无闰月), 闰月大小
LUNAR_INFO = [
    0x04BD8,
    0x04AE0,
    0x0A570,
    0x054D5,
    0x0D260,
    0x0D950,
    0x16554,
    0x056A0,
    0x09AD0,
    0x055D2,  # 1900-1909
    0x04AE0,
    0x0A5B6,
    0x0A4D0,
    0x0D250,
    0x1D255,
    0x0B540,
    0x0D6A0,
    0x0ADA2,
    0x095B0,
    0x14977,  # 1910-1919
    0x04970,
    0x0A4B0,
    0x0B4B5,
    0x06A50,
    0x06D40,
    0x1AB54,
    0x02B60,
    0x09570,
    0x052F2,
    0x04970,  # 1920-1929
    0x06566,
    0x0D4A0,
    0x0EA50,
    0x06E95,
    0x05AD0,
    0x02B60,
    0x186E3,
    0x092E0,
    0x1C8D7,
    0x0C950,  # 1930-1939
    0x0D4A0,
    0x1D8A6,
    0x0B550,
    0x056A0,
    0x1A5B4,
    0x025D0,
    0x092D0,
    0x0D2B2,
    0x0A950,
    0x0B557,  # 1940-1949
    0x06CA0,
    0x0B550,
    0x15355,
    0x04DA0,
    0x0A5B0,
    0x14573,
    0x052B0,
    0x0A9A8,
    0x0E950,
    0x06AA0,  # 1950-1959
    0x0AEA6,
    0x0AB50,
    0x04B60,
    0x0AAE4,
    0x0A570,
    0x05260,
    0x0F263,
    0x0D950,
    0x05B57,
    0x056A0,  # 1960-1969
    0x096D0,
    0x04DD5,
    0x04AD0,
    0x0A4D0,
    0x0D4D4,
    0x0D250,
    0x0D558,
    0x0B540,
    0x0B6A0,
    0x195A6,  # 1970-1979
    0x095B0,
    0x049B0,
    0x0A974,
    0x0A4B0,
    0x0B27A,
    0x06A50,
    0x06D40,
    0x0AF46,
    0x0AB60,
    0x09570,  # 1980-1989
    0x04AF5,
    0x04970,
    0x064B0,
    0x074A3,
    0x0EA50,
    0x06B58,
    0x05AC0,
    0x0AB60,
    0x096D5,
    0x092E0,  # 1990-1999
    0x0C960,
    0x0D954,
    0x0D4A0,
    0x0DA50,
    0x07552,
    0x056A0,
    0x0ABB7,
    0x025D0,
    0x092D0,
    0x0CAB5,  # 2000-2009
    0x0A950,
    0x0B4A0,
    0x0BAA4,
    0x0AD50,
    0x055D9,
    0x04BA0,
    0x0A5B0,
    0x15176,
    0x052B0,
    0x0A930,  # 2010-2019
    0x07954,
    0x06AA0,
    0x0AD50,
    0x05B52,
    0x04B60,
    0x0A6E6,
    0x0A4E0,
    0x0D260,
    0x0EA65,
    0x0D530,  # 2020-2029
    0x05AA0,
    0x076A3,
    0x096D0,
    0x04AFB,
    0x04AD0,
    0x0A4D0,
    0x1D0B6,
    0x0D250,
    0x0D520,
    0x0DD45,  # 2030-2039
    0x0B5A0,
    0x056D0,
    0x055B2,
    0x049B0,
    0x0A577,
    0x0A4B0,
    0x0AA50,
    0x1B255,
    0x06D20,
    0x0ADA0,  # 2040-2049
    0x14B63,
    0x09370,
    0x049F8,
    0x04970,
    0x064B0,
    0x168A6,
    0x0EA50,
    0x06AA0,
    0x1A6C4,
    0x0AAE0,  # 2050-2059
    0x092E0,
    0x0D2E3,
    0x0C960,
    0x0D557,
    0x0D4A0,
    0x0DA50,
    0x05D55,
    0x056A0,
    0x0A6D0,
    0x055D4,  # 2060-2069
    0x052D0,
    0x0A9B8,
    0x0A950,
    0x0B4A0,
    0x0B6A6,
    0x0AD50,
    0x055A0,
    0x0ABA4,
    0x0A5B0,
    0x052B0,  # 2070-2079
    0x0B273,
    0x06930,
    0x07337,
    0x06AA0,
    0x0AD50,
    0x14B55,
    0x04B60,
    0x0A570,
    0x054E4,
    0x0D160,  # 2080-2089
    0x0E968,
    0x0D520,
    0x0DAA0,
    0x16AA6,
    0x056D0,
    0x04AE0,
    0x0A9D4,
    0x0A4D0,
    0x0D150,
    0x0F252,  # 2090-2099
    0x0D520,  # 2100
]

# 农历年份对应的正月初一的公历日期
LUNAR_NEW_YEAR = {
    1900: date(1900, 1, 31),
    1901: date(1901, 2, 19),
    1902: date(1902, 2, 8),
    1903: date(1903, 1, 29),
    1904: date(1904, 2, 16),
    1905: date(1905, 2, 4),
    1906: date(1906, 1, 25),
    1907: date(1907, 2, 13),
    1908: date(1908, 2, 2),
    1909: date(1909, 1, 22),
    1910: date(1910, 2, 10),
    1911: date(1911, 1, 30),
    1912: date(1912, 2, 18),
    1913: date(1913, 2, 6),
    1914: date(1914, 1, 26),
    1915: date(1915, 2, 14),
    1916: date(1916, 2, 3),
    1917: date(1917, 1, 23),
    1918: date(1918, 2, 11),
    1919: date(1919, 2, 1),
    1920: date(1920, 2, 20),
    1921: date(1921, 2, 8),
    1922: date(1922, 1, 28),
    1923: date(1923, 2, 16),
    1924: date(1924, 2, 5),
    1925: date(1925, 1, 24),
    1926: date(1926, 2, 13),
    1927: date(1927, 2, 2),
    1928: date(1928, 1, 23),
    1929: date(1929, 2, 10),
    1930: date(1930, 1, 30),
    1931: date(1931, 2, 17),
    1932: date(1932, 2, 6),
    1933: date(1933, 1, 26),
    1934: date(1934, 2, 14),
    1935: date(1935, 2, 4),
    1936: date(1936, 1, 24),
    1937: date(1937, 2, 11),
    1938: date(1938, 1, 31),
    1939: date(1939, 2, 19),
    1940: date(1940, 2, 8),
    1941: date(1941, 1, 27),
    1942: date(1942, 2, 15),
    1943: date(1943, 2, 5),
    1944: date(1944, 1, 25),
    1945: date(1945, 2, 13),
    1946: date(1946, 2, 2),
    1947: date(1947, 1, 22),
    1948: date(1948, 2, 10),
    1949: date(1949, 1, 29),
    1950: date(1950, 2, 17),
    1951: date(1951, 2, 6),
    1952: date(1952, 1, 27),
    1953: date(1953, 2, 14),
    1954: date(1954, 2, 3),
    1955: date(1955, 1, 24),
    1956: date(1956, 2, 12),
    1957: date(1957, 1, 31),
    1958: date(1958, 2, 18),
    1959: date(1959, 2, 8),
    1960: date(1960, 1, 28),
    1961: date(1961, 2, 15),
    1962: date(1962, 2, 5),
    1963: date(1963, 1, 25),
    1964: date(1964, 2, 13),
    1965: date(1965, 2, 2),
    1966: date(1966, 1, 21),
    1967: date(1967, 2, 9),
    1968: date(1968, 1, 30),
    1969: date(1969, 2, 17),
    1970: date(1970, 2, 6),
    1971: date(1971, 1, 27),
    1972: date(1972, 2, 15),
    1973: date(1973, 2, 3),
    1974: date(1974, 1, 23),
    1975: date(1975, 2, 11),
    1976: date(1976, 1, 31),
    1977: date(1977, 2, 18),
    1978: date(1978, 2, 7),
    1979: date(1979, 1, 28),
    1980: date(1980, 2, 16),
    1981: date(1981, 2, 5),
    1982: date(1982, 1, 25),
    1983: date(1983, 2, 13),
    1984: date(1984, 2, 2),
    1985: date(1985, 2, 20),
    1986: date(1986, 2, 9),
    1987: date(1987, 1, 29),
    1988: date(1988, 2, 17),
    1989: date(1989, 2, 6),
    1990: date(1990, 1, 27),
    1991: date(1991, 2, 15),
    1992: date(1992, 2, 4),
    1993: date(1993, 1, 23),
    1994: date(1994, 2, 10),
    1995: date(1995, 1, 31),
    1996: date(1996, 2, 19),
    1997: date(1997, 2, 7),
    1998: date(1998, 1, 28),
    1999: date(1999, 2, 16),
    2000: date(2000, 2, 5),
    2001: date(2001, 1, 24),
    2002: date(2002, 2, 12),
    2003: date(2003, 2, 1),
    2004: date(2004, 1, 22),
    2005: date(2005, 2, 9),
    2006: date(2006, 1, 29),
    2007: date(2007, 2, 18),
    2008: date(2008, 2, 7),
    2009: date(2009, 1, 26),
    2010: date(2010, 2, 14),
    2011: date(2011, 2, 3),
    2012: date(2012, 1, 23),
    2013: date(2013, 2, 10),
    2014: date(2014, 1, 31),
    2015: date(2015, 2, 19),
    2016: date(2016, 2, 8),
    2017: date(2017, 1, 28),
    2018: date(2018, 2, 16),
    2019: date(2019, 2, 5),
    2020: date(2020, 1, 25),
    2021: date(2021, 2, 12),
    2022: date(2022, 2, 1),
    2023: date(2023, 1, 22),
    2024: date(2024, 2, 10),
    2025: date(2025, 1, 29),
    2026: date(2026, 2, 17),
    2027: date(2027, 2, 6),
    2028: date(2028, 1, 26),
    2029: date(2029, 2, 13),
    2030: date(2030, 2, 3),
    2031: date(2031, 1, 23),
    2032: date(2032, 2, 11),
    2033: date(2033, 1, 31),
    2034: date(2034, 2, 19),
    2035: date(2035, 2, 8),
    2036: date(2036, 1, 28),
    2037: date(2037, 2, 15),
    2038: date(2038, 2, 4),
    2039: date(2039, 1, 24),
    2040: date(2040, 2, 12),
    2041: date(2041, 2, 1),
    2042: date(2042, 1, 22),
    2043: date(2043, 2, 10),
    2044: date(2044, 1, 30),
    2045: date(2045, 2, 17),
    2046: date(2046, 2, 6),
    2047: date(2047, 1, 26),
    2048: date(2048, 2, 14),
    2049: date(2049, 2, 2),
    2050: date(2050, 1, 23),
}


def _get_lunar_info(year: int) -> dict:
    """解析农历年份信息"""
    if year < 1900 or year > 2100:
        raise ValueError(f"不支持{year}年，仅支持1900-2100年")

    idx = year - 1900
    if idx >= len(LUNAR_INFO):
        raise ValueError(f"缺少{year}年数据")

    info = LUNAR_INFO[idx]

    # 解析月份天数
    months = []
    for i in range(12):
        months.append(30 if (info >> (20 - i)) & 1 else 29)

    # 解析闰月
    leap_month = (info >> 4) & 0x0F
    leap_days = 30 if (info & 0xF) == 1 else 29 if leap_month > 0 else 0

    return {"months": months, "leap_month": leap_month, "leap_days": leap_days}


def lunar_to_solar(year: int, month: int, day: int, is_leap: bool = False) -> date:
    """
    农历转公历
    year: 农历年
    month: 农历月
    day: 农历日
    is_leap: 是否闰月
    """
    if year not in LUNAR_NEW_YEAR:
        raise ValueError(f"不支持{year}年转换")

    info = _get_lunar_info(year)
    spring = LUNAR_NEW_YEAR[year]

    # 计算从正月初一到目标日期的天数
    days = 0
    leap_encountered = False

    for m in range(1, month):
        if m == info["leap_month"]:
            # 闰月在小月之前
            days += info["months"][m - 1]
            if is_leap and month == info["leap_month"]:
                days += info["leap_days"]
                leap_encountered = True
        elif not leap_encountered and info["leap_month"] > 0 and m > info["leap_month"]:
            # 过了闰月，但目标月不是闰月
            pass  # 正常月份
        days += info["months"][m - 1]

    # 处理闰月特殊
    if is_leap:
        if month != info["leap_month"]:
            raise ValueError(f"{year}年{month}月不是闰月")
        # 加完正常月份后再加闰月天数
        days = 0
        for m in range(1, info["leap_month"]):
            days += info["months"][m - 1]
        days += info["leap_days"]  # 闰月本身
        days += day - 1
    else:
        # 如果目标月在闰月之后，需要加上闰月
        if info["leap_month"] > 0 and month > info["leap_month"]:
            days += info["leap_days"]
        days += day - 1

    return spring + timedelta(days=days)


def validate_date(year: int, month: int, day: int, calendar: str) -> str:
    """
    校验日期有效性
    返回: None=合法, str=错误信息
    """
    import datetime

    if year < 1900 or year > 2100:
        return "年份仅支持1900-2100"
    if month < 1 or month > 12:
        return "月份必须在1-12之间"
    if day < 1 or day > 31:
        return "日期必须在1-31之间"

    if calendar == "solar":
        try:
            datetime.date(year, month, day)
        except ValueError:
            return f"无效的公历日期: {year}年{month}月{day}日"

    return ""


if __name__ == "__main__":
    # 测试转换
    print("农历1980年5月15日 →", lunar_to_solar(1980, 5, 15))
    print("农历1968年5月15日 →", lunar_to_solar(1968, 5, 15))
    print("农历1976年12月25日 →", lunar_to_solar(1976, 12, 25))
