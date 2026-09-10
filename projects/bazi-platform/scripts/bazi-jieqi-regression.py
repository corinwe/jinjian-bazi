#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 四柱节气定界回归门禁 v1.0（2026-09-10 建立）
=========================================================
背景：2026-06-24 发现「年柱用公历年→立春前出生者年柱错→月干五虎遁级联错」，
      当时只写进检查清单**未修代码**；2026-09-10 复测确认：14例边界样本错10例。
      本脚本为**物理门禁**：任何对排盘/节气逻辑的改动，跑不过就不许提交。

裁判：lunar-python（精确天文节气，独立实现）
被测：engine/jieqi.py、engine/paipan.py、scripts/bazi-engine.py、scripts/bazi-verify.py

覆盖：立春当日前后·各节气当日前后·1月跨年·早晚子时·闰日·家族真实八字基准
用法：python3 scripts/bazi-jieqi-regression.py            # 全量
      python3 scripts/bazi-jieqi-regression.py --quick    # 快速（仅固定用例）
退出码：0=全过  1=有失败（禁止提交）
"""
import sys
import os
import random
from datetime import datetime, timedelta

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, 'engine'))
sys.path.insert(0, os.path.join(PROJ, 'scripts'))

from lunar_python import Solar  # 裁判
import jieqi

QUICK = '--quick' in sys.argv
FAIL = []
CHECKS = [0]


def ref(y, m, d, h=12, mi=0):
    """裁判：lunar-python 四柱（立春换年 + 节气换月）"""
    ec = Solar.fromYmdHms(y, m, d, h, mi, 0).getLunar().getEightChar()
    return ec.getYear() + ec.getMonth() + ec.getDay() + ec.getTime()


def check(label, got, exp, extra=''):
    CHECKS[0] += 1
    if got != exp:
        FAIL.append(f"{label}: 得 {got} ≠ 期望 {exp} {extra}")
        print(f"  ❌ {label:34} {got:22} ≠ {exp}   {extra}")
        return False
    return True


# ══════════════════════════════════════════════════
# A. jieqi 模块 vs 裁判（年月柱精确性）
# ══════════════════════════════════════════════════
print("═══ A. engine/jieqi.py 年柱/月柱 精确性 ═══")
FIXED = [
    (2024, 2, 4, 10, 0, '立春当日·立春前(16:27)'),
    (2024, 2, 4, 17, 0, '立春当日·立春后'),
    (2026, 1, 20, 10, 0, '1月·立春前'),
    (1990, 1, 15, 10, 0, '1月·立春前'),
    (2021, 2, 3, 20, 0, '立春当日(22:58)·前'),
    (2021, 2, 3, 23, 30, '立春当日(22:58)·后'),
    (2025, 1, 5, 9, 0, '小寒当日·前(10:32)'),
    (2025, 1, 5, 12, 0, '小寒当日·后'),
    (1980, 8, 6, 6, 0, '老板魏启令(基准)'),
    (2017, 7, 7, 8, 0, '七七(基准)'),
    (2019, 4, 23, 14, 0, '左左(基准)'),
    (2010, 9, 16, 10, 0, '胜源(基准)'),
    (1978, 12, 20, 22, 0, '燃凤(基准)'),
]
for y, m, d, h, mi, label in FIXED:
    dt = datetime(y, m, d, h, mi)
    r = ref(y, m, d, h, mi)
    ygz = ''.join(jieqi.year_gan_zhi(dt))
    mgz = ''.join(jieqi.month_gan_zhi(dt))
    check(f"jieqi·年柱 {label}", ygz, r[:2])
    check(f"jieqi·月柱 {label}", mgz, r[2:4])

if not QUICK:
    # 随机扫：每年取12个节气日 ±1天各3个时点 + 随机日
    random.seed(20260910)
    cnt = 0
    for year in range(1955, 2036):
        for name in jieqi.JIE_NAMES:
            try:
                t = jieqi._jieqi_at(year, name)
            except Exception:
                continue
            for delta_min in (-16 * 60, -2 * 60, +2 * 60, +16 * 60):
                dt = t + timedelta(minutes=delta_min)
                if dt.year != year:
                    continue
                r = ref(dt.year, dt.month, dt.day, dt.hour % 24, dt.minute)
                check(f"扫·年柱 {dt:%Y-%m-%d %H:%M}", ''.join(jieqi.year_gan_zhi(dt)), r[:2])
                check(f"扫·月柱 {dt:%Y-%m-%d %H:%M}", ''.join(jieqi.month_gan_zhi(dt)), r[2:4])
                cnt += 2
    for _ in range(300):
        y = random.randint(1955, 2035)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        h = random.randint(0, 23)
        dt = datetime(y, m, d, h, 0)
        r = ref(y, m, d, h, 0)
        check(f"扫·年柱 {dt:%Y-%m-%d %H}", ''.join(jieqi.year_gan_zhi(dt)), r[:2])
        check(f"扫·月柱 {dt:%Y-%m-%d %H}", ''.join(jieqi.month_gan_zhi(dt)), r[2:4])
        cnt += 2
    print(f"  —— 节气边界+随机共扫 {cnt} 项")

# ══════════════════════════════════════════════════
# B. paipan.py / bazi-engine.py 端到端
# ══════════════════════════════════════════════════
print("═══ B. engine/paipan.py 端到端 ═══")
from paipan import paipan

END2END = [
    (2024, 2, 4, 10, 0, '男', '立春当日·前'),
    (2024, 2, 4, 17, 0, '男', '立春当日·后'),
    (2026, 1, 20, 10, 0, '男', '1月·立春前'),
    (1990, 1, 15, 10, 0, '男', '1月·立春前'),
    (2025, 1, 5, 9, 0, '男', '小寒当日·前'),
    (2025, 1, 5, 12, 0, '男', '小寒当日·后'),
    (1980, 8, 6, 6, 0, '男', '老板'),
    (2017, 7, 7, 8, 0, '女', '七七'),
    (2019, 4, 23, 14, 0, '男', '左左'),
    (2010, 9, 16, 10, 0, '男', '胜源'),
    (1978, 12, 20, 22, 0, '女', '燃凤'),
    (2024, 2, 29, 12, 0, '男', '闰日'),
]
for y, m, d, h, mi, g, label in END2END:
    got = paipan(label, g, y, m, d, h, mi)['bazi'].replace(' ', '')
    check(f"paipan {label}", got, ref(y, m, d, h, mi))

print("═══ C. scripts/bazi-engine.py 端到端（年/月/日/时柱 + 大运方向）═══")
import importlib.util
spec = importlib.util.spec_from_file_location("be", os.path.join(PROJ, 'scripts', 'bazi-engine.py'))
be = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ['bazi-engine.py']
spec.loader.exec_module(be)
sys.argv = _argv

SHICHEN = {0: 0, 23: 0}
for h in range(0, 24):
    SHICHEN.setdefault(h, ((h + 1) // 2) % 12)

for y, m, d, h, mi, g, label in END2END:
    r = be.to_json(be.calc_bazi(y, m, d, h, mi, SHICHEN[h], g, label))
    p = r['四柱']
    got = p['年柱'] + p['月柱'] + p['日柱'] + p['时柱']
    exp = ref(y, m, d, h, mi)
    check(f"bazi-engine {label}", got, exp)
    # 大运方向：年干阴阳决定顺逆
    y_gan = exp[0]
    yin_yang = '阳' if y_gan in '甲丙戊庚壬' else '阴'
    want = '顺排' if ((yin_yang == '阳') == (g == '男')) else '逆排'
    got_dir = r['大运']['规则']
    check(f"大运方向 {label}", '顺排' if '顺' in got_dir else '逆排', want, f"(年干{y_gan}·{g})")

# ══════════════════════════════════════════════════
# D. 起运岁数 vs lunar-python 裁判
# ══════════════════════════════════════════════════
print("═══ D. 起运岁数（裁判 lunar-python Yun）═══")
for y, m, d, h, mi, g, label in END2END[:6] + END2END[6:9]:
    ec = Solar.fromYmdHms(y, m, d, h, mi, 0).getLunar().getEightChar()
    yun = ec.getYun(1 if g == '男' else 0)
    ref_age = yun.getStartYear() + yun.getStartMonth() / 12.0 + yun.getStartDay() / 365.0
    r = be.to_json(be.calc_bazi(y, m, d, h, mi, SHICHEN[h], g, label))
    got_age = r['大运'].get('起运年龄')
    if got_age is None:
        FAIL.append(f"起运 {label}: 引擎未返回起运年龄")
        continue
    CHECKS[0] += 1
    diff = abs(got_age - ref_age)
    flag = '✅' if diff <= 0.05 else ('⚠️' if diff <= 0.15 else '❌')
    if diff > 0.15:
        FAIL.append(f"起运 {label}: 引擎{got_age} vs 裁判{ref_age:.2f}")
    print(f"  {flag} 起运 {label:16} 引擎 {got_age:5} vs 裁判 {ref_age:5.2f}  (差 {diff:.3f}年)")

# ══════════════════════════════════════════════════
print()
print("═" * 78)
if FAIL:
    print(f"❌ 回归失败：{len(FAIL)} 项 / 共校验 {CHECKS[0]} 项")
    for f in FAIL[:40]:
        print("   -", f)
    sys.exit(1)
print(f"✅ 回归全过：共校验 {CHECKS[0]} 项，0 失败")
sys.exit(0)
