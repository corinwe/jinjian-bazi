#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 中国大陆夏令时判定（1935–1991）
================================================
移植自开源项目 ziwei-doushu 的 `lib/ziwei/dst-cn.ts`（MIT License, © 2026 紫微研究）。
来源：https://github.com/Renhuai123/ziwei-doushu

为什么必须处理：
  夏令时期间钟表拨快 1 小时，而时辰是 2 小时一档 ——
  出生时刻落在时辰边界的人，**命宫/身宫/大限/时柱会整个换掉**。
  影响量级远大于经度修正（最多十几分钟）。

口径铁律（照抄主流排盘口径，不按个人理解改）：
  1. 表 XLS_CN 与判定逻辑逐字对齐通行口径，起止日均含；
  2. 判定**纯按日期**，不看小时；
  3. `else if` 结构不可"顺手优化"（month==起月 且 day<起日 时不再比止月分支）；
  4. **只提示，绝不自动减 1 小时** —— 我们无法知道用户报的是夏令时读数还是
     已自行换算过的标准时。默默减既可能算错，又会把所有存量历史命盘悄悄改掉。

用法：
  python3 engine/dst_cn.py 1988-07-01 08:00
  from dst_cn import check, is_china_dst
"""
from __future__ import annotations

# 通行口径 XLS_CN：[年, 起月, 起日, 止月, 止日]，起止日均含
XLS_CN = [
    (1935, 5, 1, 9, 30), (1936, 5, 1, 9, 30), (1937, 5, 1, 9, 30), (1938, 5, 1, 9, 30),
    (1939, 5, 1, 9, 30), (1940, 5, 1, 9, 30), (1941, 5, 1, 9, 30), (1942, 5, 1, 9, 30),
    (1943, 5, 1, 9, 30), (1944, 5, 1, 9, 30), (1945, 5, 1, 9, 30), (1946, 5, 1, 9, 30),
    (1947, 5, 1, 9, 30), (1948, 5, 1, 9, 30), (1949, 5, 1, 9, 30), (1950, 5, 1, 9, 30),
    (1951, 5, 1, 9, 30), (1952, 3, 1, 10, 31), (1953, 4, 1, 10, 31), (1954, 4, 1, 10, 31),
    (1955, 5, 1, 9, 30), (1956, 5, 1, 9, 30), (1957, 4, 1, 9, 30), (1958, 4, 1, 9, 30),
    (1959, 4, 1, 9, 30), (1960, 6, 1, 9, 30), (1961, 6, 1, 9, 30), (1974, 4, 1, 10, 31),
    (1975, 4, 1, 10, 31), (1979, 7, 1, 9, 30), (1986, 5, 4, 9, 14), (1987, 4, 12, 9, 13),
    (1988, 4, 10, 9, 11), (1989, 4, 16, 9, 17), (1990, 4, 15, 9, 16), (1991, 4, 14, 9, 15),
]


def is_china_dst(year: int, month: int, day: int) -> bool:
    """该公历日期是否处于中国大陆夏令时期间（纯按日期，不看小时）。"""
    for y, m1, d1, m2, d2 in XLS_CN:
        if year != y:
            continue
        if m1 < month < m2:
            return True
        if month == m1:
            if day >= d1:
                return True
        elif month == m2:
            if day <= d2:
                return True
    return False


def is_china_dst_year(year: int) -> bool:
    return any(y == year for y, *_ in XLS_CN)


def china_dst_span(year: int):
    """返回 {'起':'M月D日','止':'M月D日'} 或 None。"""
    for y, m1, d1, m2, d2 in XLS_CN:
        if y == year:
            return {'起': f'{m1}月{d1}日', '止': f'{m2}月{d2}日'}
    return None


def check(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> dict:
    """排盘前置检查：**只判定并给出提示，不修改任何时间**。

    返回：
      {'是否夏令时': bool, '区间': dict|None, '提示': str|None}
    """
    span = china_dst_span(year)
    if not span:
        return {'是否夏令时': False, '区间': None, '提示': None}
    if not is_china_dst(year, month, day):
        return {'是否夏令时': False, '区间': span, '提示': None}
    notice = (
        f"⚠️ 夏令时提示：{year} 年 {span['起']}–{span['止']} 中国大陆实行夏令时，"
        f"出生日期 {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} 落在区间内。"
        f"若你提供的钟表读数已是夏令时时间，真实标准时应为 {hour:02d}:{minute:02d} 减 1 小时"
        f"（{((hour - 1) % 24):02d}:{minute:02d}）——是否减 1 小时由你确认，本引擎不自动调整。"
    )
    return {'是否夏令时': True, '区间': span, '提示': notice}


if __name__ == '__main__':
    import json
    import sys
    if len(sys.argv) < 2:
        print('用法: python3 engine/dst_cn.py YYYY-MM-DD [HH:MM]')
        sys.exit(1)
    ds = sys.argv[1]
    tm = sys.argv[2] if len(sys.argv) > 2 else '00:00'
    y, m, d = [int(x) for x in ds.replace('/', '-').split('-')]
    hh, mm = [int(x) for x in tm.split(':')]
    print(json.dumps(check(y, m, d, hh, mm), ensure_ascii=False, indent=1))
