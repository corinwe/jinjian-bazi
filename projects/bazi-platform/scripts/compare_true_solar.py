#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真太阳时口径比对：NOAA（新） vs 旧简化式（CLI 在用）。

输出：
    ① 均时差全年极值/均值差
    ② 三个城市逐日逐 10 分钟的「时辰翻转」次数
    ③ JSON 结果到 /tmp/true_solar_compare.json

用法：
    python3 scripts/compare_true_solar.py [年份]
"""
import json
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, "engine"))

from true_solar import (  # noqa: E402
    equation_of_time_minutes, legacy_eot_minutes, branch_from_minutes,
)

CITIES = {"上海": 121.47, "北京": 116.40, "乌鲁木齐": 87.62}


def compare(year: int):
    # ① 均时差全年（每日 12:00）
    import datetime
    diffs = []
    d = datetime.date(year, 1, 1)
    while d.year == year:
        new = equation_of_time_minutes(d.year, d.month, d.day, 12, 0)
        old = legacy_eot_minutes(d.year, d.month, d.day)
        diffs.append(new - old)
        d += datetime.timedelta(days=1)

    abs_d = [abs(x) for x in diffs]
    eot_stats = {
        "days": len(diffs),
        "max_abs_min": round(max(abs_d), 2),
        "mean_abs_min": round(sum(abs_d) / len(abs_d), 2),
        "max_signed_min": round(max(diffs), 2),
        "min_signed_min": round(min(diffs), 2),
        "days_over_1min": sum(1 for x in abs_d if x > 1.0),
        "days_over_2min": sum(1 for x in abs_d if x > 2.0),
    }

    # ② 时辰翻转：逐日 × 每 10 分钟
    flips = {}
    for city, lon in CITIES.items():
        cnt, total = 0, 0
        d = datetime.date(year, 1, 1)
        while d.year == year:
            for mins in range(0, 1440, 10):
                hh, mm = divmod(mins, 60)
                corr = (lon - 120.0) * 4
                new = equation_of_time_minutes(d.year, d.month, d.day, hh, mm)
                old = legacy_eot_minutes(d.year, d.month, d.day)
                b_new = branch_from_minutes((mins + corr + new) % 1440)
                b_old = branch_from_minutes((mins + corr + old) % 1440)
                total += 1
                if b_new != b_old:
                    cnt += 1
            d += datetime.timedelta(days=1)
        flips[city] = {"checked": total, "branch_flips": cnt,
                       "flip_rate_pct": round(cnt / total * 100, 3)}

    return {"year": year, "eot": eot_stats, "branch_flips": flips}


def main():
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    r = compare(year)
    print(f"═══ 真太阳时口径比对 · {year} 年 ═══")
    e = r["eot"]
    print(f"均时差：最大差 {e['max_abs_min']} 分｜平均差 {e['mean_abs_min']} 分"
          f"｜>1分 {e['days_over_1min']} 天｜>2分 {e['days_over_2min']} 天")
    for city, v in r["branch_flips"].items():
        print(f"时辰翻转 · {city}：{v['branch_flips']}/{v['checked']}"
              f"（{v['flip_rate_pct']}%）")
    out = "/tmp/true_solar_compare.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    print(f"\n结果 → {out}")


if __name__ == "__main__":
    main()
