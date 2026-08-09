#!/usr/bin/env python3
"""农历转公历回归验证脚本（2026-08-01 闰月bug修复后建立）

用途：任何农历→公历转换修改后，运行本脚本验证与权威库 lunar-python 一致。
铁律：28个年份用例（含全部闰月年型）全部一致才算通过，任一 FAIL 阻断推送。

依赖：pip install lunar-python
用法：python3 verify_lunar_conversion.py
"""
import sys
sys.path.insert(0, '/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine')
from lunar import lunar_to_solar
from lunar_python import Lunar

# 覆盖1949-2025所有闰月年型 + 无闰月对照
TEST_CASES = [
    (1949, 7, 15),   # 闰7月
    (1952, 7, 6),    # 闰5月（2026-08-01老板抓错案例：曾错算成9-22，正确8-25）
    (1957, 8, 3),    # 闰8月
    (1960, 6, 15),   # 闰6月
    (1963, 4, 20),   # 闰4月
    (1966, 3, 10),   # 闰3月
    (1968, 7, 25),   # 闰7月
    (1971, 5, 18),   # 闰5月
    (1974, 10, 2),   # 闰10月
    (1976, 8, 14),   # 闰8月
    (1980, 5, 21),   # 无闰月对照
    (1982, 4, 9),    # 闰4月
    (1984, 10, 1),   # 闰10月
    (1987, 6, 26),   # 闰6月
    (1990, 5, 12),   # 闰5月
    (1993, 3, 15),   # 闰3月
    (1995, 8, 28),   # 闰8月
    (1998, 5, 15),   # 闰5月
    (2001, 4, 12),   # 闰4月
    (2004, 2, 15),   # 闰2月
    (2006, 7, 10),   # 闰7月
    (2009, 5, 8),    # 闰5月
    (2012, 4, 18),   # 闰4月
    (2014, 9, 15),   # 闰9月
    (2017, 6, 22),   # 闰6月
    (2020, 4, 20),   # 闰4月
    (2023, 2, 20),   # 闰2月
    (2025, 6, 15),   # 闰6月
]


def main() -> int:
    ok = fail = 0
    for y, m, d in TEST_CASES:
        try:
            s = lunar_to_solar(y, m, d)
            lp = Lunar.fromYmd(y, m, d).getSolar()
            lp_date = (lp.getYear(), lp.getMonth(), lp.getDay())
            engine_date = (s.year, s.month, s.day)
            if engine_date == lp_date:
                ok += 1
            else:
                fail += 1
                print(f"❌ {y}年{m}月{d}日: 引擎{engine_date} vs 权威{lp_date}")
        except Exception as e:
            fail += 1
            print(f"❌ {y}年{m}月{d}日: {e}")

    print(f"\n回归结果: {ok}通过 / {fail}失败 / 共{len(TEST_CASES)}")
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
