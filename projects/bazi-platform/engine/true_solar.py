#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真太阳时计算（NOAA 均时差口径）。

移植自开源项目 ziwei-doushu 的 `lib/ziwei/true-solar-time.ts`
（MIT License, © 2026 紫微研究）。
来源：https://github.com/Renhuai123/ziwei-doushu  commit 39c0abd

口径：
    真太阳时 = 钟表时间 + 经度修正 + 均时差
    经度修正 = (出生地经度 − 时区中央经线) × 4 分钟
    中央经线 = utcOffsetMinutes / 4（东八区 480 → 120°）

与旧口径的区别：
    旧（CLI）：9.87·sin(2B) − 7.53·cos(B) − 1.5·sin(B)，B = 2π(d−81)/365.24
    新（NOAA）：229.18 × (0.000075 + 0.001868cosγ − 0.032077sinγ
                          − 0.014615cos2γ − 0.040849sin2γ)
    γ 采用 fractional-year（含时刻），精度更高；两者差异见
    `scripts/compare_true_solar.py`。

用法：
    from true_solar import true_solar_time
    r = true_solar_time(1988, 7, 1, 8, 30, longitude=121.47)
"""
from __future__ import annotations

import math

MINUTES_PER_DAY = 1440
SECONDS_PER_DAY = 86400


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _day_of_year(year: int, month: int, day: int) -> int:
    cum = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    d = cum[month - 1] + day
    if month > 2 and _is_leap(year):
        d += 1
    return d


def equation_of_time_minutes(year: int, month: int, day: int,
                             hour: int = 12, minute: int = 0) -> float:
    """NOAA 均时差（分钟）。正值＝真太阳时快于平太阳时。"""
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return 0.0
    days_in_year = 366 if _is_leap(year) else 365
    fractional_hour = hour + minute / 60
    gamma = (2 * math.pi / days_in_year) * (
        _day_of_year(year, month, day) - 1 + (fractional_hour - 12) / 24
    )
    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )


def legacy_eot_minutes(year: int, month: int, day: int) -> float:
    """旧口径（CLI 在用）：9.87sin2B − 7.53cosB − 1.5sinB。仅用于比对。"""
    d = _day_of_year(year, month, day)
    b = 2 * math.pi * (d - 81) / 365.24
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def branch_from_minutes(normalized_minutes: float) -> int:
    """时辰索引：0=子（含晚子 23:00–01:00），1=丑 … 11=亥。"""
    if normalized_minutes >= 1380 or normalized_minutes < 60:
        return 0
    return int((normalized_minutes - 60) // 120) + 1


def true_solar_time(year: int, month: int, day: int, clock_hour: int, clock_minute: int,
                    longitude: float, utc_offset_minutes: int = 480) -> dict:
    """返回真太阳时结果字典（字段与 TS 版对齐）。"""
    meridian = utc_offset_minutes / 4
    longitude_correction = (longitude - meridian) * 4
    eot = equation_of_time_minutes(year, month, day, clock_hour, clock_minute)
    total = longitude_correction + eot
    raw = clock_hour * 60 + clock_minute + total

    rounded_seconds = round(raw * 60)
    day_offset = rounded_seconds // SECONDS_PER_DAY
    second_of_day = rounded_seconds % SECONDS_PER_DAY
    hour = second_of_day // 3600
    minute = (second_of_day % 3600) // 60
    second = second_of_day % 60
    normalized = second_of_day / 60

    return {
        "longitudeCorrectionMinutes": round(longitude_correction, 4),
        "equationOfTimeMinutes": round(eot, 4),
        "totalCorrectionMinutes": round(total, 4),
        "rawMinutes": round(raw, 4),
        "dayOffset": day_offset,
        "hour": hour,
        "minute": minute,
        "second": second,
        "normalizedMinutes": normalized,
        "branch": branch_from_minutes(normalized),
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 6:
        print("用法: python3 engine/true_solar.py YYYY MM DD HH MM [经度]")
        sys.exit(1)
    y, mo, d, hh, mm = (int(x) for x in sys.argv[1:6])
    lon = float(sys.argv[6]) if len(sys.argv) > 6 else 121.47
    print(json.dumps(true_solar_time(y, mo, d, hh, mm, lon), ensure_ascii=False, indent=1))
