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
ENGINE_VERSION = 'ziwei-v1.1'
# v1.1 (2026-09-11): 四柱交叉校验口径归一化 —— 紫微侧 iztro 月柱按【农历月】口径、
#   八字侧 jieqi.py 按【节气】口径，两者在「农历月≠节气月」时必然不等（旧版误判不一致→阻断出报告）。
#   新规则：年/日/时柱严格比对；月柱不等时用农历月口径反算归一化，能解释=放行并标注，不能解释=仍拦截。

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


# ─────────────────────────────────────────────────────────────
# 四柱交叉校验（口径归一化版 · 2026-09-11）
# ─────────────────────────────────────────────────────────────
_TG = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
_ZHI_FROM_YIN = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']


def _expected_lunar_month_pillar(year_gan: str, lunar_month: int) -> str:
    """按【农历月】口径期望月柱：五虎遁(年干) + 正月起寅（紫微斗数传统口径）"""
    lm = abs(lunar_month)
    zhi = _ZHI_FROM_YIN[(lm - 1) % 12]
    gan = _TG[((_TG.index(year_gan) % 5) * 2 + 2 + (lm - 1)) % 10]
    return gan + zhi


def _cross_check(zi_pillars: str, ours: str, y, m, d, hh, mm):
    """四柱交叉校验 —— 区分【真错误】与【口径差异】

    🚨 2026-09-11 修复（小静 2007-04-13 案暴露）：
      紫微侧 iztro 的 chineseDate 月柱按【农历月】定（紫微斗数传统：正月=寅、二月=卯…），
      八字侧 engine/jieqi.py 月柱按【节气】定（立春换年·节换月）。
      两者在「农历月 ≠ 节气月」的日子必然不等（例：2007-04-13 农历二月廿六、节气已入辰月
      → 紫微癸卯 / 八字甲辰），旧版直接判「不一致」并阻断出报告 = **假阳性**。
    校验规则（不放宽对真错误的拦截）：
      ① 年/日/时柱必须严格一致；
      ② 月柱先严格比对；不等时用农历月口径反算期望值，
         能对上 → 通过（标注「月柱口径差异·已归一化」），对不上 → 不一致（真错误）。
    返回 (ok, 说明, 紫微侧展示串)
    """
    if len(zi_pillars) != 8 or len(ours) != 8:
        return False, f'四柱串长度异常：紫微={zi_pillars} 八字={ours}', zi_pillars
    zs = [zi_pillars[i:i + 2] for i in range(0, 8, 2)]
    os_ = [ours[i:i + 2] for i in range(0, 8, 2)]
    bad = [nm for i, nm in enumerate(['年', '月', '日', '时']) if i != 1 and zs[i] != os_[i]]
    if bad:
        return False, f"{'、'.join(bad)}柱不一致（真错误）｜紫微={zi_pillars} 八字={ours}", zi_pillars
    if zs[1] == os_[1]:
        return True, '✅ 双引擎四柱一致（月柱同为节气口径）', zi_pillars
    try:
        from lunar_python import Solar
        lm = Solar.fromYmdHms(y, m, d, hh, mm, 0).getLunar().getMonth()
    except Exception as e:  # lunar-python 不可用时退回严格判定
        return False, f'月柱不一致且农历月推算失败（{e}）：紫微={zs[1]} 八字={os_[1]}', zi_pillars
    exp = _expected_lunar_month_pillar(zs[0][0], lm)
    if zs[1] == exp:
        return True, (f"✅ 双引擎一致（口径差异已归一化）：紫微月柱{zs[1]}=农历"
                      f"{'闰' if lm < 0 else ''}{abs(lm)}月口径·八字月柱{os_[1]}=节气口径"
                      f"（同一命造·年/日/时柱严格相符）"), zi_pillars + '(农历月口径)'
    return False, (f"月柱不一致且不能用农历月口径解释：紫微={zs[1]} 期望农历月口径={exp} "
                   f"八字={os_[1]}"), zi_pillars


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
    cv_ok, cv_note, zi_label = _cross_check(zi_pillars, ours, y, m, d, hh, mm)

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
            '紫微引擎': zi_label,
            '八字引擎': ours,
            '一致': cv_ok,
            '说明': cv_note,
        },
        '紫微': {
            '五行局': zw.get('fiveElementsClass'),
            '命主': zw.get('soul'),
            '身主': zw.get('body'),
            '生肖': zw.get('zodiac'),
            '星座': zw.get('sign'),
            '时辰': f"{zw.get('time')}（{zw.get('timeRange')}）",
            '生年四化': _merge_sihua(cli_raw.get('ziwei', {}).get('shengnianSihua'), _si_hua(zw)),
            '十二宫': palaces,
        },
        '八字同源摘要': {
            '四柱': b.get('pillars'),
            '五行': b.get('wuxing'),
        },
    }
    return out


def _merge_sihua(cli_list, bridge_list) -> list:
    """合并两个来源的生年四化（去重，取并集，按 禄权科忌 排序）→ 防止任一来源漏字段"""
    ORDER = {'禄': 0, '权': 1, '科': 2, '忌': 3}
    s = set()
    for lst in (cli_list or [], bridge_list or []):
        for x in lst or []:
            if x:
                s.add(str(x))
    return sorted(s, key=lambda t: ORDER.get(t[-1] if t else '', 9))


def _si_hua(zw: dict) -> list:
    """
    从12宫星曜mutagen汇总生年四化（桥接层/三方CLI缺该字段时兜底）。
    🚨 2026-09-10 修正：必须同时扫描 **主星 + 辅星** —— 文昌/文曲属辅星，
    只扫主星会漏（例：辛年「巨门化禄/太阳化权/文曲化科/文昌化忌」只出2条）。
    顺序按 禄→权→科→忌 排列。
    """
    ORDER = {'禄': 0, '权': 1, '科': 2, '忌': 3}
    found = {}
    for pal in zw.get('palaces', []):
        for group in ('majorStars', 'minorStars'):
            for s in pal.get(group) or []:
                if isinstance(s, dict) and s.get('mutagen') and s.get('name'):
                    found[s['name']] = s['mutagen']
    return [f"{k}化{v}" for k, v in sorted(found.items(), key=lambda kv: ORDER.get(kv[1], 9))]


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
