#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 紫微斗数回归门禁 v1.0
================================================
把「排盘不能错」固化成可执行断言。移植自开源项目 ziwei-doushu 的
`scripts/regression/*.test.ts`（MIT License, © 2026 紫微研究）的设计思路，
按本平台引擎（ziwei_engine + iztro bridge + dst_cn）重写。

跑: python3 engine/ziwei_gates.py            # 全部
    python3 engine/ziwei_gates.py dst        # 只跑某一条
失败 exit 1。

铁律清单：
  1. pan_integrity        12宫齐全/身宫唯一/十四主星齐全/五行局合法/大限齐全
  2. dst_cn               中国夏令时表边界（1986/1988/1991 起止日）
  3. clock_adjust         经度差＝(经度−120)×4 分钟；均时差 |EoT| ≤ 17 分钟
  4. lichun_boundary      立春时刻前后年柱必须切换
  5. hongluan_tianxi      红鸾/天喜必须在对宫（相隔 6 宫）
  6. dual_sihua_same_palace  生年四化必须 4 条（同宫也不得漏）
  7. time_index_boundary  23/00/01/22 点 → 时辰索引边界
  8. solar_date_exists    不存在的公历日期必须报错
  9. dual_engine_consistency  紫微桥接与八字引擎四柱必须一致
 10. neutral_naming       断语库不得出现「一定会/必然/肯定」等绝对断言
"""
from __future__ import annotations

import itertools
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PROJ = os.path.dirname(os.path.abspath(__file__))

PASS, FAIL = [], []


def check(name, fn):
    try:
        n = fn()
        PASS.append((name, n))
        print(f'  ✓ {name}' + (f'（{n} 项断言）' if n else ''))
    except Exception as e:
        FAIL.append((name, str(e)))
        print(f'  ✗ {name}: {e}')
        traceback.print_exc(limit=2)


# ── 采样命盘（跨年代/月/时辰/性别）─────────────────────────────
def _samples(limit=12):
    if '--fast' in sys.argv:
        limit = min(limit, 4)
    out = []
    for y in (1965, 1988, 2003, 2020):
        for m, d in ((1, 15), (5, 28), (6, 10), (10, 8)):
            out.append((y, m, d, 4 if (y + m) % 2 else 9, 'male' if m % 2 else 'female'))
    return out[:limit]


def _chart(y, m, d, hh, gender):
    from ziwei_engine import build
    return build('门禁', gender, f'{y}-{m:02d}-{d:02d}', f'{hh:02d}:30',
                 leap_policy='split')


# ── 1. 排盘完整性 ─────────────────────────────────────────────
def test_pan_integrity():
    PALACES = {'命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄',
               '迁移', '仆役', '官禄', '田宅', '福德', '父母'}
    JU = {'水二局', '木三局', '金四局', '土五局', '火六局'}
    n = 0
    for (y, m, d, hh, g) in _samples():
        ch = _chart(y, m, d, hh, g)['紫微']
        pals = ch['十二宫']
        assert len(pals) == 12, f'{y}-{m}-{d}: 宫数 {len(pals)}≠12'
        assert {p['宫位'] for p in pals} == PALACES, f'{y}-{m}-{d}: 宫名缺失'
        assert sum(1 for p in pals if p['身宫']) == 1, f'{y}-{m}-{d}: 身宫不唯一'
        majors = [s['名'] for p in pals for s in p['主星']]
        assert len(majors) == 14, f'{y}-{m}-{d}: 十四主星数={len(majors)}'
        assert len({p['大限'] for p in pals if p['大限']}) == 12, f'{y}-{m}-{d}: 大限不全'
        assert ch['五行局'] in JU, f'{y}-{m}-{d}: 五行局={ch["五行局"]}'
        assert ch['命主'] and ch['身主'], f'{y}-{m}-{d}: 命主/身主为空'
        assert len(ch['生年四化']) == 4, f'{y}-{m}-{d}: 生年四化={ch["生年四化"]}'
        for p in pals:
            assert len(p['干支']) == 2, f'{y}-{m}-{d}: 宫干支异常 {p["干支"]}'
            for s in p['主星'] + p['辅星']:
                assert s['庙旺'] in ('庙', '旺', '得', '利', '平', '不', '陷', None), \
                    f'{y}-{m}-{d}: 亮度档位异常 {s}'
        n += 9
    return n


# ── 2. 夏令时表边界 ───────────────────────────────────────────
def test_dst_cn():
    from dst_cn import is_china_dst
    cases = [
        ((1986, 5, 3), False), ((1986, 5, 4), True), ((1986, 9, 14), True), ((1986, 9, 15), False),
        ((1988, 4, 9), False), ((1988, 4, 10), True), ((1988, 9, 11), True), ((1988, 9, 12), False),
        ((1991, 4, 13), False), ((1991, 4, 14), True), ((1991, 9, 15), True), ((1991, 9, 16), False),
        ((1992, 7, 1), False), ((2020, 7, 1), False), ((1979, 7, 1), True),
    ]
    for (y, m, d), want in cases:
        got = is_china_dst(y, m, d)
        assert got == want, f'{y}-{m}-{d}: 期望 {want} 实得 {got}'
    return len(cases)


# ── 3. 真太阳时：经度差公式 + 均时差量级 ──────────────────────
def test_clock_adjust():
    from ziwei_engine import _run_cli
    cases = [(121.5, '上海'), (120.0, '东经120'), (113.3, '广州'), (87.6, '乌鲁木齐')]
    n = 0
    for lon, nm in cases:
        raw = _run_cli('门禁', 'male', '2000-06-15', '12:00', longitude=lon)
        cal = raw.get('meta', {}).get('calibration', {})
        diff = cal.get('longitudeDiffMinutes')
        if diff is None:
            continue
        assert abs(diff - (lon - 120.0) * 4) < 0.6, f'{nm}: 经度差 {diff} ≠ {(lon-120)*4}'
        eot = cal.get('eotMinutes', 0) or 0
        assert abs(eot) <= 17, f'{nm}: 均时差 {eot} 超出 ±17min'
        n += 2
    assert n >= 4, '真太阳时校准字段缺失'
    return n


# ── 4. 立春边界 ───────────────────────────────────────────────
def test_lichun_boundary():
    from paipan import paipan
    before = paipan('门禁', 'male', 2024, 2, 4, 15, 0)['bazi'].split()[0]
    after = paipan('门禁', 'male', 2024, 2, 4, 17, 30)['bazi'].split()[0]
    assert before == '癸卯', f'立春前年柱应为癸卯，实得 {before}'
    assert after == '甲辰', f'立春后年柱应为甲辰，实得 {after}'
    return 2


# ── 5. 红鸾/天喜对宫 ──────────────────────────────────────────
def test_hongluan_tianxi():
    BR = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    n = 0
    for (y, m, d, hh, g) in _samples(6):
        pals = _chart(y, m, d, hh, g)['紫微']['十二宫']
        pos = {}
        for i, p in enumerate(pals):
            for s in p['杂曜']:
                if s in ('红鸾', '天喜'):
                    pos[s] = i
        if '红鸾' in pos and '天喜' in pos:
            gap = abs(pos['红鸾'] - pos['天喜'])
            assert gap == 6, f'{y}-{m}-{d}: 红鸾/天喜相隔 {gap} 宫（应 6）'
            n += 1
    return n


# ── 6. 生年四化完整性（同宫不漏）──────────────────────────────
def test_dual_sihua_same_palace():
    n = 0
    for (y, m, d, hh, g) in _samples(8):
        ch = _chart(y, m, d, hh, g)['紫微']
        hua = ch['生年四化']
        assert len(hua) == 4, f'{y}-{m}-{d}: 四化 {hua}'
        kinds = sorted(x[-1] for x in hua)
        assert kinds == ['忌', '权', '禄', '科'], f'{y}-{m}-{d}: 四化种类异常 {hua}'
        n += 1
    return n


# ── 7. 时辰索引边界 ───────────────────────────────────────────
def test_time_index_boundary():
    from ziwei_engine import _shichen_idx
    cases = {23: 12, 0: 0, 1: 1, 2: 1, 3: 2, 11: 6, 12: 6, 22: 11}
    for h, want in cases.items():
        got = _shichen_idx(h)
        assert got == want, f'{h}点 → {got}，应 {want}'
    return len(cases)


# ── 8. 不存在的公历日期 ───────────────────────────────────────
def test_solar_date_exists():
    from paipan import paipan
    for (m, d) in ((2, 30), (4, 31), (13, 1)):
        try:
            paipan('门禁', 'male', 2023, m, d, 8, 0)
        except Exception:
            continue
        raise AssertionError(f'2023-{m}-{d} 应报错但未报')
    return 3


# ── 9. 双引擎四柱一致 ─────────────────────────────────────────
def test_dual_engine_consistency():
    n = 0
    for (y, m, d, hh, g) in _samples(6):
        cv = _chart(y, m, d, hh, g)['四柱交叉校验']
        assert cv['一致'], f'{y}-{m}-{d}: {cv["说明"]}'
        n += 1
    return n


# ── 10. 断语中性（不许绝对断言）───────────────────────────────
def test_neutral_naming():
    BAN = ('一定会', '必然', '肯定', '绝对', '注定')
    hits = []
    p = os.path.join(PROJ, 'ziwei_rules.py')
    txt = open(p, encoding='utf-8').read()
    for w in BAN:
        if w in txt:
            hits.append(w)
    assert not hits, f'断语库出现绝对词：{hits}'
    return len(BAN)



# ── 11. 闰月口径（split 月中分界）──────────────────────────────
def test_leap_policy():
    from ziwei_engine import build, _lunar_leap_info
    is_leap, lday = _lunar_leap_info(2020, 6, 10)
    assert is_leap and lday > 15, f'2020-06-10 应为闰四月十九，实得 闰={is_leap} 日={lday}'
    a = build('门禁', 'male', '2020-06-10', '08:30', leap_policy='split')['闰月口径']
    b = build('门禁', 'male', '2020-06-10', '08:30', leap_policy='prev')['闰月口径']
    c = build('门禁', 'male', '2020-05-28', '08:30', leap_policy='split')['闰月口径']
    assert a['fixLeap'] is True and b['fixLeap'] is False, '闰月后半月 split 应归下月(True)'
    assert c['fixLeap'] is False, '闰月前半月 split 应按本月(False)'
    return 3


# ── 12. 神煞锚点（将星/岁建）──────────────────────────────────
def test_shensha_anchor():
    """将星：寅午戌→午、申子辰→子、巳酉丑→酉、亥卯未→卯；岁建＝年支。"""
    BR = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    GROUP = {'寅': '午', '午': '午', '戌': '午', '申': '子', '子': '子', '辰': '子',
             '巳': '酉', '酉': '酉', '丑': '酉', '亥': '卯', '卯': '卯', '未': '卯'}
    n = 0
    for (y, m, d, hh, g) in _samples(4):
        ch = _chart(y, m, d, hh, g)['紫微']
        pals = ch['十二宫']
        year_br = None
        for p in pals:
            if p['岁前12神'] == '岁建':
                year_br = p['干支'][1]
        assert year_br is not None, f'{y}-{m}-{d}: 找不到岁建'
        jiang_br = None
        for p in pals:
            if p['将前12神'] == '将星':
                jiang_br = p['干支'][1]
        assert jiang_br == GROUP[year_br], f'{y}-{m}-{d}: 年支{year_br} 将星应在{GROUP[year_br]}，实得{jiang_br}'
        n += 2
    return n


TESTS = [
    ('pan_integrity', test_pan_integrity),
    ('dst_cn', test_dst_cn),
    ('clock_adjust', test_clock_adjust),
    ('lichun_boundary', test_lichun_boundary),
    ('hongluan_tianxi', test_hongluan_tianxi),
    ('dual_sihua_same_palace', test_dual_sihua_same_palace),
    ('time_index_boundary', test_time_index_boundary),
    ('solar_date_exists', test_solar_date_exists),
    ('dual_engine_consistency', test_dual_engine_consistency),
    ('neutral_naming', test_neutral_naming),
    ('leap_policy', test_leap_policy),
    ('shensha_anchor', test_shensha_anchor),
]


def main():
    only = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
    print('\n═══ 紫微斗数回归门禁 v1.0 ═══\n')
    for name, fn in TESTS:
        if only and only != name:
            continue
        check(name, fn)
    print(f'\n通过 {len(PASS)} / {len(PASS) + len(FAIL)}')
    if FAIL:
        print('⛔ 存在失败项，禁止出报告')
        sys.exit(1)
    print('✅ 全部门禁通过')


if __name__ == '__main__':
    main()
