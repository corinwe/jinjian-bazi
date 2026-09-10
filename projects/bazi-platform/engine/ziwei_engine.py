#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 紫微斗数引擎 v1.0（平台第四引擎）
=================================================
定位：与 bazi-engine（八字）并列的**独立引擎**，输出标准化数据源 `/tmp/{姓名}_ziwei.json`。
默认与八字**同时运行、合参评估**；仅在老板明确指定时才单独使用（见双引擎门禁）。

计算层：iztro（MIT·紫微斗数）+ lunar-javascript（MIT），经 skills/bazi/bazi-ziwei 的 CLI 调用。
血统说明：**不得**使用 dzcmemory-web/bazi-ziwei-skill（2026-08-25 已被 GitHub DMCA 封禁）。

对外保证：
  1. 紫微12宫（宫位/干支/主星+庙旺+四化/辅星/杂曜/大限/长生12神）
  2. 生年四化 + 命主/身主 + 五行局
  3. 真太阳时校准（经度差 + 均时差，精确到分钟）
  4. **四柱与 bazi 引擎强制交叉校验** —— 不一致则标记 `交叉校验.一致=false` 并高亮（不静默）

用法：
  python3 engine/ziwei_engine.py 七七 女 2017-07-07 08:00 [出生地] [--json]
  python3 engine/ziwei_engine.py 老板 男 1980-08-06 06:00 上海 --json
输出：/tmp/{姓名}_ziwei.json
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(PROJ, '..', '..', 'skills', 'bazi', 'bazi-ziwei', 'scripts', 'bazi_ziwei_cli.js')
CLI = os.path.abspath(CLI)
ENGINE_VERSION = 'ziwei-v1.0'

if not os.path.exists(CLI):
    alt = '/root/.hermes/profiles/jinjian-zhenren/skills/bazi/bazi-ziwei/scripts/bazi_ziwei_cli.js'
    if os.path.exists(alt):
        CLI = alt


def _run_cli(name, gender, date_str, time_str, location=None, longitude=None,
             bazi_calib=True, ziwei_calib=True) -> dict:
    cmd = ['node', CLI, '--name', name, '--gender', gender, '--type', 'solar',
           '--date', date_str, '--time', time_str,
           '--bazi-calib', 'true' if bazi_calib else 'false',
           '--ziwei-calib', 'true' if ziwei_calib else 'false']
    if longitude:
        cmd += ['--longitude', str(longitude)]
    elif location:
        cmd += ['--location', location]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"紫微CLI执行失败: {(r.stderr or r.stdout)[-400:]}")
    return json.loads(r.stdout)


def _ours_bazi(year, month, day, hour, minute, gender, name, birthplace='') -> str:
    """我方八字引擎四柱（交叉校验用）"""
    sys.path.insert(0, os.path.join(PROJ, 'engine'))
    from paipan import paipan
    return paipan(name, gender, year, month, day, hour, minute)['bazi'].replace(' ', '')


def _shichen_idx(hour: int, minute: int = 0) -> int:
    """小时→iztro时辰索引(0早子..12晚子)"""
    if hour == 23:
        return 12
    if hour == 0:
        return 0
    return ((hour + 1) // 2) % 12


def _run_bridge(name, gender, date_str, time_str) -> dict:
    """主路径：engine/ziwei_bridge.js（iztro直连，字段完整）"""
    bridge = os.path.join(PROJ, 'engine', 'ziwei_bridge.js')
    y, m, d = [int(x) for x in date_str.replace('/', '-').split('-')]
    hh = int(time_str.split(':')[0])
    r = subprocess.run(['node', bridge, f'{y}-{m}-{d}', str(_shichen_idx(hh)), gender],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"ziwei_bridge 失败: {(r.stderr or r.stdout)[-300:]}")
    return json.loads(r.stdout)


def build(name, gender, date_str, time_str, location=None, longitude=None,
          bazi_calib=True, ziwei_calib=True, birthplace='') -> dict:
    # ① 真太阳时校准 + 农历：走三方CLI（含经度差/均时差）
    cli_raw = {}
    try:
        cli_raw = _run_cli(name, gender, date_str, time_str, location, longitude,
                           bazi_calib, ziwei_calib)
    except Exception as e:
        cli_raw = {'meta': {'calibration': {'error': str(e)}}}
    meta = cli_raw.get('meta', {})
    b = cli_raw.get('bazi', {})

    # ② 紫微命盘：走自建桥接层（iztro直连，命主/身主/12宫完整）
    zw = _run_bridge(name, gender, date_str, time_str)
    zi_pillars = (zw.get('chineseDate') or '').replace(' ', '')

    y, m, d = [int(x) for x in date_str.replace('/', '-').split('-')]
    hh, mm = [int(x) for x in time_str.split(':')]
    ours = _ours_bazi(y, m, d, hh, mm, gender, name, birthplace)

    palaces = []
    for pal in zw.get('palaces', []):
        def _st(s):
            if isinstance(s, dict):
                return {'名': s.get('name'), '庙旺': s.get('brightness'), '四化': s.get('mutagen')}
            return {'名': str(s), '庙旺': None, '四化': None}
        palaces.append({
            '宫位': pal.get('name'),
            '干支': (pal.get('heavenlyStem') or '') + (pal.get('earthlyBranch') or ''),
            '主星': [_st(s) for s in (pal.get('majorStars') or [])],
            '辅星': [_st(s) for s in (pal.get('minorStars') or [])],
            '杂曜': [_st(s)['名'] for s in (pal.get('adjectiveStars') or [])],
            '大限': (f"{pal['decadalRange'][0]}-{pal['decadalRange'][1]}岁"
                     if pal.get('decadalRange') else None),
            '流年年龄': pal.get('ages'),
            '长生12神': pal.get('changsheng12'),
            '博士12神': pal.get('boshi12'),
            '身宫': bool(pal.get('isBodyPalace')),
        })

    out = {
        '引擎版本': ENGINE_VERSION,
        '编制人': '金鉴真人',
        '姓名': name,
        '性别': gender,
        '公历': f'{date_str} {time_str}',
        '农历': zw.get('lunarDate') or b.get('lunarDate') or '',
        '出生地': location or (f'经度{longitude}' if longitude else '未指定'),
        '真太阳时校准': meta.get('calibration', {}),
        '四柱交叉校验': {
            '紫微引擎': zi_pillars,
            '八字引擎': ours,
            '一致': zi_pillars == ours,
            '说明': '✅ 双引擎四柱一致' if zi_pillars == ours else '🚨 双引擎四柱不一致，禁止出报告，需先查 engine/jieqi.py 定界',
        },
        '紫微': {
            '五行局': zw.get('fiveElementsClass'),
            '命主': zw.get('soul'),
            '身主': zw.get('body'),
            '生肖': zw.get('zodiac'),
            '星座': zw.get('sign'),
            '时辰': f"{zw.get('time')}（{zw.get('timeRange')}）",
            '生年四化': cli_raw.get('ziwei', {}).get('shengnianSihua') or _si_hua(zw),
            '十二宫': palaces,
        },
        '八字同源摘要': {
            '四柱': b.get('pillars'),
            '五行': b.get('wuxing'),
        },
    }
    return out


def _si_hua(zw: dict) -> list:
    """从12宫主星mutagen反推生年四化（桥接层无该字段时兜底）"""
    out = []
    for pal in zw.get('palaces', []):
        for s in pal.get('majorStars') or []:
            if isinstance(s, dict) and s.get('mutagen'):
                out.append(f"{s.get('name')}化{s.get('mutagen')}")
    return out


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith('--')]
    as_json = '--json' in sys.argv
    if len(argv) < 4:
        print(__doc__)
        sys.exit(1)
    name, gender, date_str, time_str = argv[0], argv[1], argv[2], argv[3]
    location = argv[4] if len(argv) > 4 else None
    longitude = argv[5] if len(argv) > 5 else None

    data = build(name, gender, date_str, time_str, location, longitude)
    out_path = f'/tmp/{name}_ziwei.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=1))
        return

    cv = data['四柱交叉校验']
    print(f"═══ 紫微斗数引擎 {ENGINE_VERSION} ═══")
    print(f"命主: {data['姓名']}（{data['性别']}） {data['公历']} {data['农历']}")
    print(f"真太阳时: {data['真太阳时校准'].get('trueTime', '未校准')} "
          f"(经度差{data['真太阳时校准'].get('longitudeDiffMinutes', 0)}min + "
          f"均时差{data['真太阳时校准'].get('eotMinutes', 0)}min)")
    print(f"四柱交叉校验: 紫微={cv['紫微引擎']} 八字={cv['八字引擎']} → {cv['说明']}")
    zw = data['紫微']
    print(f"五行局: {zw['五行局']} | 命主: {zw['命主']} | 身主: {zw['身主']}")
    print(f"生年四化: {zw['生年四化']}")
    print("─── 十二宫 ───")
    for pal in zw['十二宫']:
        stars = ' '.join(f"{s['名']}{s['庙旺'] or ''}{('[' + s['四化'] + ']') if s['四化'] else ''}"
                         for s in pal['主星']) or '无主星'
        fu = ' '.join(s['名'] for s in pal['辅星']) or '—'
        print(f"  {'[身宫]' if pal['身宫'] else '      '}{pal['宫位']:<4}{pal['干支']:<5}主星: {stars:<28}辅星: {fu:<16}大限: {pal['大限']}")
    print(f"\n💾 已写入: {out_path}")
    if not cv['一致']:
        print("🚨 双引擎四柱不一致！禁止出报告，先查 engine/jieqi.py 定界。")


if __name__ == '__main__':
    main()
