#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 精确节气定界模块（引擎唯一权威口径）
==================================================
用途：年柱 / 月柱 的干支定界。**所有排盘模块必须调用本模块，禁止各自实现。**

铁律（子平法）：
  1. 年柱以「立春」为界，非公历1月1日、非农历春节。立春精确到分钟。
  2. 月柱以「节」（立春/惊蛰/清明/立夏/芒种/小暑/立秋/白露/寒露/立冬/大雪/小寒）为界，精确到分钟。
  3. 月干由真实年干起五虎遁 —— 年干错则月干必错（级联）。

历史教训（血案）：
  2026-06-24 杨昌玉案例：引擎年柱用公历年 → 立春前出生者年柱错 → 月干随五虎遁错。
  2026-09-10 复测：14例边界样本中 bazi-engine.py 错10例、paipan.py 错5例。
  本模块即为根治。

参考实现：lunar-python（精确天文节气，MIT）；无该库时回退 ephem 天文计算。
"""
from __future__ import annotations

from datetime import datetime, timedelta

# ── 节（换月节气）与月支对应 ──
JIE_NAMES = ["立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
             "立秋", "白露", "寒露", "立冬", "大雪", "小寒"]
JIE_TO_ZHI = {"立春": "寅", "惊蛰": "卯", "清明": "辰", "立夏": "巳", "芒种": "午", "小暑": "未",
              "立秋": "申", "白露": "酉", "寒露": "戌", "立冬": "亥", "大雪": "子", "小寒": "丑"}

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

WU_HU_DUN = {"甲": "丙", "乙": "戊", "丙": "庚", "丁": "壬", "戊": "甲",
             "己": "丙", "庚": "戊", "辛": "庚", "壬": "壬", "癸": "甲"}
MONTH_ORDER = {"寅": 0, "卯": 1, "辰": 2, "巳": 3, "午": 4, "未": 5,
               "申": 6, "酉": 7, "戌": 8, "亥": 9, "子": 10, "丑": 11}

# ── 后端探测 ──
try:
    from lunar_python import Solar as _LunarSolar
    BACKEND = "lunar-python"
except Exception:  # pragma: no cover
    _LunarSolar = None
    BACKEND = "ephem"

try:
    import ephem as _ephem
except Exception:  # pragma: no cover
    _ephem = None


def _as_dt(dt) -> datetime:
    if isinstance(dt, datetime):
        return dt
    raise TypeError(f"需要 datetime，收到 {type(dt)}")


# ══════════════════════════════════════════════════
# 后端1：lunar-python（精确天文节气 + 立春换年）
# ══════════════════════════════════════════════════
def _lunar_pillars(dt: datetime):
    s = _LunarSolar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)
    lunar = s.getLunar()
    ec = lunar.getEightChar()
    return ec.getYear(), ec.getMonth()


def _lunar_prev_jieqi(dt: datetime):
    s = _LunarSolar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)
    jq = s.getLunar().getPrevJieQi(True)
    si = jq.getSolar()
    return jq.getName(), datetime(si.getYear(), si.getMonth(), si.getDay(), si.getHour(), si.getMinute())


# ══════════════════════════════════════════════════
# 后端2：ephem 天文回退（UTC→北京时+8，禁止直接用UTC当本地时）
# ══════════════════════════════════════════════════
def _sun_longitude_utc(dt_utc: datetime) -> float:
    import math
    obs = _ephem.Observer()
    obs.date = dt_utc.strftime("%Y/%m/%d %H:%M:%S")
    return (math.degrees(_ephem.Sun(obs).hlong) + 180.0) % 360.0


_JIE_LON = {"立春": 315, "惊蛰": 345, "清明": 15, "立夏": 45, "芒种": 75, "小暑": 105,
            "立秋": 135, "白露": 165, "寒露": 195, "立冬": 225, "大雪": 255, "小寒": 285}
_JIE_APPROX = {"立春": (2, 4), "惊蛰": (3, 6), "清明": (4, 5), "立夏": (5, 6), "芒种": (6, 6),
               "小暑": (7, 7), "立秋": (8, 8), "白露": (9, 8), "寒露": (10, 8), "立冬": (11, 7),
               "大雪": (12, 7), "小寒": (1, 6)}


def _jieqi_datetime_ephem(year: int, name: str) -> datetime:
    """求某年某节的精确时刻（北京时间）。二分法收敛到 <1分钟。"""
    lon = _JIE_LON[name]
    mm, dd = _JIE_APPROX[name]
    base = datetime(year, mm, dd, 12, 0)
    lo = base - timedelta(days=8)
    hi = base + timedelta(days=8)
    lo = lo - timedelta(hours=8)   # 本地→UTC
    hi = hi - timedelta(hours=8)

    def unwrapped(dt_utc):
        v = _sun_longitude_utc(dt_utc)
        # 把目标黄经附近展开成连续值（处理跨0度）
        d = (v - lon + 180) % 360 - 180
        return d

    for _ in range(60):
        mid = lo + (hi - lo) / 2
        if unwrapped(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + (hi - lo) / 2) + timedelta(hours=8)   # UTC→北京时


def _ephem_pillars(dt: datetime):
    # 立春换年
    lichun = _jieqi_datetime_ephem(dt.year, "立春")
    eff_year = dt.year if dt >= lichun else dt.year - 1
    y_gan = TIAN_GAN[(eff_year - 4) % 10]
    y_zhi = DI_ZHI[(eff_year - 4) % 12]
    # 节气换月
    name, _ = _ephem_prev_jieqi(dt)
    m_zhi = JIE_TO_ZHI[name]
    start = TIAN_GAN.index(WU_HU_DUN[y_gan])
    m_gan = TIAN_GAN[(start + MONTH_ORDER[m_zhi]) % 10]
    return y_gan + y_zhi, m_gan + m_zhi


def _ephem_prev_jieqi(dt: datetime):
    cands = []
    for y in (dt.year - 1, dt.year, dt.year + 1):
        for name in JIE_NAMES:
            try:
                t = _jieqi_datetime_ephem(y, name)
            except Exception:
                continue
            if t <= dt:
                cands.append((t, name))
    if not cands:
        return "小寒", dt
    t, name = max(cands)
    return name, t


# ══════════════════════════════════════════════════
# 对外唯一接口
# ══════════════════════════════════════════════════
def year_gan_zhi(dt) -> tuple[str, str]:
    """年柱干支。以立春为界（精确到分钟）。"""
    dt = _as_dt(dt)
    if _LunarSolar is not None:
        y = _lunar_pillars(dt)[0]
    else:
        y = _ephem_pillars(dt)[0]
    return y[0], y[1]


def month_gan_zhi(dt) -> tuple[str, str]:
    """月柱干支。以「节」为界（精确到分钟），月干由真实年干起五虎遁。"""
    dt = _as_dt(dt)
    if _LunarSolar is not None:
        m = _lunar_pillars(dt)[1]
    else:
        m = _ephem_pillars(dt)[1]
    return m[0], m[1]


def year_gan_zhi_int(year: int, month: int = 7, day: int = 1, hour: int = 12, minute: int = 0):
    """兼容旧接口：无时刻信息时按给定年月日+时刻定界。"""
    return year_gan_zhi(datetime(year, month, day, hour, minute))


def li_chun(year: int) -> datetime:
    """某年立春精确时刻（北京时间）。"""
    if _LunarSolar is not None:
        return _lunar_jieqi(year, "立春")
    return _jieqi_datetime_ephem(year, "立春")


def _lunar_jieqi(year: int, name: str) -> datetime:
    """用 lunar-python 取某年某节时刻（通过节气表）。"""
    s = _LunarSolar.fromYmdHms(year, 6, 1, 12, 0, 0)
    table = s.getLunar().getJieQiTable()
    for k, v in table.items():
        if name in k:
            si = v
            if si.getYear() == year:
                return datetime(si.getYear(), si.getMonth(), si.getDay(), si.getHour(), si.getMinute())
    # 兜底
    return _jieqi_datetime_ephem(year, name)


def prev_jieqi(dt) -> tuple[str, datetime]:
    """
    dt 之前最近的「节」名称与时刻（12换月节气，**不含**中气如大寒/谷雨）。

    🚨 2026-09-10 修复：曾误用 lunar-python 的 getPrevJieQi()，它在24节气里取，
    会把「气」（大寒/谷雨…）当成「节」→ 逆排大运起运岁数严重偏小。
    起运规则只认 12 个「节」。
    """
    dt = _as_dt(dt)
    cands = []
    for y in (dt.year - 1, dt.year, dt.year + 1):
        for name in JIE_NAMES:
            try:
                t = _jieqi_at(y, name)
            except Exception:
                continue
            if t <= dt:
                cands.append((t, name))
    if not cands:
        return "小寒", dt
    t, name = max(cands)
    return name, t


def next_jieqi(dt) -> tuple[str, datetime]:
    """dt 之后最近的「节」名称与时刻（用于顺排大运起运计算）。"""
    dt = _as_dt(dt)
    cands = []
    for y in (dt.year - 1, dt.year, dt.year + 1):
        for name in JIE_NAMES:
            try:
                t = _jieqi_at(y, name)
            except Exception:
                continue
            if t > dt:
                cands.append((t, name))
    if not cands:
        return "立春", dt
    t, name = min(cands)
    return name, t


def _jieqi_at(year: int, name: str) -> datetime:
    """某年某「节」的精确时刻（北京时间）。"""
    if _LunarSolar is not None:
        return _lunar_jieqi(year, name)
    return _jieqi_datetime_ephem(year, name)


if __name__ == "__main__":
    print(f"backend = {BACKEND}")
    for d in [(2024, 2, 4, 10, 0), (2024, 2, 4, 17, 0), (2026, 1, 20, 10, 0),
              (1980, 8, 6, 6, 0), (2017, 7, 7, 8, 0), (2025, 1, 5, 9, 0), (2025, 1, 5, 12, 0)]:
        dt = datetime(*d)
        y, m = year_gan_zhi(dt), month_gan_zhi(dt)
        print(f"{dt}  年柱={y[0]}{y[1]}  月柱={m[0]}{m[1]}  节={prev_jieqi(dt)[0]}@{prev_jieqi(dt)[1]}")
    print("2024立春:", li_chun(2024), "| 2021立春:", li_chun(2021), "| 2026立春:", li_chun(2026))
