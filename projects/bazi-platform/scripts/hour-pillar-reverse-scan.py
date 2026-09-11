#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 时柱反推扫描器 v1.0（12 时辰横向评估 · 全确定性引擎）
=================================================================================
用途：出生时辰未知时，给定「年/月/日 + 出生地」→ 扫描 12 个候选时柱 →
      逐时辰跑 pipeline_v5（身强弱/格局/喜用/财星）+ xing_chong_he_hua（刑冲合害/空亡/自刑）
      → 按技能库规则打分排名 → 输出 最好 / 平均 / 最差 三个时辰 + 对比表。

规则出处（不引入自创断语）：
  A 四象限      bazi-four-pillars-analysis §1.2（天干×地支喜忌组合，±2/±2）
  B 刑冲合害    同技能 §七「关卡④ 全局冲刑校验」＋九龙能量优先序（三会20>六合/半合>冲10）
                自刑 = 九龙体系「辰午酉亥两两相见」（24号文档）；空亡 = 旬首公式
  C 格局成格    老板铁律③（成格条件+身强弱校验+辅助格局）
  D 身强弱      引擎 shen_qiang_ruo.total（身弱局取帮身分，除最高值归一到 0-2）
  E 调候        穷通宝鉴（丁生辰月用甲；其它日主/月令由引擎 tiaohou 给出）
分层判定：技能 §5.4 判定优先级（🥇双喜 > 🥈一喜一忌 > ❌双忌），层内按综合分排序；
         「平均时辰」= 一喜一忌层内综合分最接近 0 者（最中性）。

用法：
  python3 scripts/hour-pillar-reverse-scan.py --name 小静 --gender 女 \
      --date 2007-04-13 --place 东阳 --day-ganzhi 丁丑 [--out /tmp/小静_时柱扫描.md]
  说明：--day-ganzhi 可省略，脚本会用「1900-01-01=甲戌」基准自算（与 engine 同口径），
        但建议用 bazi-engine.py 的结果核对一次（脚本会自动打印自算值供比对）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, "engine"))

import jieqi  # noqa: E402
import xing_chong_he_hua as X  # noqa: E402
from pipeline_v5 import run_pipeline  # noqa: E402

TG = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DZ = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
SH = DZ
CLOCK = ['23:00–00:59', '01:00–02:59', '03:00–04:59', '05:00–06:59', '07:00–08:59', '09:00–10:59',
         '11:00–12:59', '13:00–14:59', '15:00–16:59', '17:00–18:59', '19:00–20:59', '21:00–22:59']
TG_WX = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
         '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
DZ_WX = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
         '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}
JIULONG_ZIXING = ['辰', '午', '酉', '亥']
# 地支藏干（100/60/30 标准·与 engine 口径一致；用于调候判定）
CANG = {'子': ['癸'], '丑': ['己', '癸', '辛'], '寅': ['甲', '丙', '戊'], '卯': ['乙'],
        '辰': ['戊', '乙', '癸'], '巳': ['丙', '庚', '戊'], '午': ['丁', '己'],
        '未': ['己', '丁', '乙'], '申': ['庚', '壬', '戊'], '酉': ['辛'],
        '戌': ['戊', '辛', '丁'], '亥': ['壬', '甲']}
# 调候用神五行：**以引擎 tiaohou 输出为准**（bazi-paipan-sop 铁律：调候用神以引擎为准，不得自行发明组合）
# 本命（丁生辰月）引擎给出 tiao_hou=['木'] → E 分 = 时柱是否含「木」（甲/乙天干 或 支中藏甲乙）


def day_ganzhi(d: date) -> tuple[str, str]:
    """与 engine/bazi-engine.py 同口径：1900-01-01 = 甲戌日"""
    base = date(1900, 1, 1)
    off = (d - base).days
    return TG[(0 + off) % 10], DZ[(10 + off) % 12]


def shichen_gan(day_gan: str, idx: int) -> str:
    """五鼠遁：时干 = TIAN_GAN[((日干序 % 5) * 2 + 时支序) % 10]"""
    return TG[((TG.index(day_gan) % 5) * 2 + idx) % 10]


def score_hour(r: dict, xwx: list, xji: list, ri_gan: str, yue_zhi: str) -> dict:
    xi, ji = xwx, xji
    tg, dz = r['时柱']
    gok, zok = TG_WX[tg] in xi, DZ_WX[dz] in xi
    detail = []
    A = (2 if gok else -2) + (2 if zok else -2)
    detail.append(("A 四象限", A, f"时干{tg}({TG_WX[tg]}){'喜' if gok else '忌'} + 时支{dz}({DZ_WX[dz]}){'喜' if zok else '忌'}"))

    rel = r['rel']
    B, note = 0.0, []
    for h in rel.get('三会', []):
        B += 3 if h['wx'] in xi else -3
        note.append(f"三会{h['type']}({'喜' if h['wx'] in xi else '忌'})")
    for h in rel.get('冲', []):
        if h in ('辰戌冲',):
            B -= 3; note.append(f"冲月支({h})致命")
        elif h in ('丑未冲',):
            B -= 3; note.append(f"冲日支({h})致命")
        else:
            B -= 1.5; note.append(f"冲年支({h})")
    for h in rel.get('刑', []):
        if '丑未戌' in h['type']:
            B -= 1.5; note.append(f"刑({h['type']})")
        else:
            B -= 0.5; note.append(f"自刑({h['type']})")
    for h in rel.get('害', []):
        hard = any(t in h for t in ('丑', '辰'))   # 涉日支/月支
        B -= 2 if hard else 1
        note.append(f"害({'月/日支' if hard else '年支'}({h}))")
    for h in rel.get('六合', []):
        wx = h[-1] if h and h[-1] in '木火土金水' else ''
        B += 1 if wx in xi else -1; note.append(f"六合{h}")
    for h in rel.get('半合', []):
        B += 1 if h['wx'] in xi else -1; note.append(f"半合{h['type']}")
    for h in rel.get('拱合', []):
        B += 0.5 if h['wx'] in xi else -0.5; note.append(f"拱合{h['type']}")
    for h in rel.get('暗合', []):
        B += 0.5 if h['wx'] in xi else -0.5; note.append(f"暗合{h['type']}")
    for h in rel.get('天干五合', []):
        B += 1 if h['wx'] in xi else -1; note.append(f"干合{h['gans'][0]}{h['gans'][1]}化{h['wx']}")
    if r['空亡']:
        B -= 1.5; note.append("时支空亡")
    if dz in (r['四支'][0], r['四支'][1]):
        B -= 1; note.append("时支伏吟年/月支")
    if dz == r['四支'][2]:
        B -= 1; note.append("时支伏吟日支")
    detail.append(("B 刑冲合害", round(B, 2), '；'.join(note) or '无'))

    C = 2 if r['成格'] else 0
    detail.append(("C 格局成格", C, r['格局详解']))
    detail.append(("D 身强弱", round(r['身强弱'] / 32.0 * 2, 2), f"{r['身强弱']}分(身弱)"))
    th = r.get('调候', [])          # 引擎调候用神五行（如 ['木']）
    E = 1 if (TG_WX[tg] in th or any(TG_WX.get(c['天干'], '') in th for c in r['时支藏干'])) else 0
    detail.append(("E 调候", E, f"引擎调候用神 {'/'.join(th) or '—'}；时柱{'含' if E else '不含'}该五行"))
    total = round(A + B + C + detail[3][1] + E, 2)
    return dict(A=A, B=round(B, 2), C=C, D=detail[3][1], E=E, total=total, detail=detail,
                quad=('双喜' if A == 4 else ('双忌' if A == -4 else '一喜一忌')), tg=tg, dz=dz,
                g_ok=gok, z_ok=zok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--gender', required=True, choices=['男', '女'])
    ap.add_argument('--date', required=True, help='公历 YYYY-MM-DD')
    ap.add_argument('--place', default='')
    ap.add_argument('--day-ganzhi', default=None, help='日柱（如 丁丑）；省略则自算')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    y, m, d = [int(x) for x in a.date.split('-')]
    dg_auto, dz_auto = day_ganzhi(date(y, m, d))
    if a.day_ganzhi:
        assert a.day_ganzhi == dg_auto + dz_auto, \
            f"日柱不一致：传入 {a.day_ganzhi} vs 自算 {dg_auto}{dz_auto}（请用 bazi-engine.py 核对）"
    dg, dz = dg_auto, dz_auto
    yg, yz = jieqi.year_gan_zhi(datetime(y, m, d, 12, 0))
    mg, mz = jieqi.month_gan_zhi(datetime(y, m, d, 12, 0))
    print(f"三柱（引擎口径）：{yg}{yz} {mg}{mz} {dg}{dz}｜日主 {dg}｜出生地 {a.place or '未指定'}")

    rows = []
    for idx in range(12):
        dt = datetime(y, m, d, (0 if idx == 0 else idx * 2), 30 if idx == 0 else 0)
        hg = shichen_gan(dg, idx)
        hz = DZ[idx]
        jn, jdt = jieqi.next_jieqi(dt)
        qy_days = (jdt - dt).total_seconds() / 86400.0
        out = run_pipeline(a.name, a.gender, yg, yz, mg, mz, dg, dz, hg, hz, y, m, d, qy_days)
        an = out['analysis']
        xy = an['xi_yong_shen']
        kw = X._get_kong_wang(dg, dz)
        zhis = [yz, mz, dz, hz]
        rel = X.check_all_relations_v2(zhis, [yg, mg, dg, hg], kw)
        ss = [s for s in an['ge_ju']['shi_shen'] if s['position'] == '时柱'][0]['shi_shen']
        rec = dict(idx=idx, sh=SH[idx], 时柱=(hg, hz), 时柱串=hg + hz, 十神=ss,
                   身强弱=an['shen_qiang_ruo']['score'], 格局=an['ge_ju']['main'],
                   格局详解=an['ge_ju']['detail'], 成格='成格' in an['ge_ju']['detail'],
                   财星=an['cai_xing']['total'], 财级=an['cai_xing']['wealth_level'],
                   空亡=(hz in kw), 四支=zhis,
                   时支藏干=[{'天干': g} for g in CANG.get(hz, [])],
                   调候=(an['xi_yong_shen'].get('tiao_hou') or []),
                   rel=rel, v5=out)
        sc = score_hour(rec, xy['xi'], xy['ji'], dg, mz)
        rec.update(sc)
        rows.append(rec)
        json.dump(out, open(f"/tmp/{a.name}_h{idx}_v5.json", "w"), ensure_ascii=False)

    rank = sorted(rows, key=lambda x: -x['total'])
    print(f"\n{'排名':<4}{'时辰':<5}{'时柱':<6}{'十神':<6}{'身强弱':<8}{'格局':<8}{'层级':<10}{'综合分':>8}")
    for n, r in enumerate(rank, 1):
        print(f"{n:<4}{SH[r['idx']]:<5}{r['时柱串']:<6}{r['十神']:<6}{r['身强弱']:<8}{r['格局']:<8}{r['quad']:<10}{r['total']:>+8.2f}")

    # 分层优先（技能 §5.4 判定优先级）：🥇双喜 > 🥈一喜一忌 > ❌双忌；层内按综合分排序
    t1 = sorted([r for r in rank if r['quad'] == '双喜'], key=lambda x: -x['total'])
    t2 = sorted([r for r in rank if r['quad'] == '一喜一忌'], key=lambda x: -x['total'])
    t3 = sorted([r for r in rank if r['quad'] == '双忌'], key=lambda x: -x['total'])
    best = t1[0] if t1 else rank[0]
    avg = sorted(t2, key=lambda x: abs(x['total']))[0] if t2 else rank[len(rank) // 2]
    worst = t3[-1] if t3 else rank[-1]
    print(f"  分层：🥇双喜 {[SH[x['idx']] for x in t1]} ｜ 🥈一喜一忌 {[SH[x['idx']] for x in t2]} ｜ ❌双忌 {[SH[x['idx']] for x in t3]}")
    print(f"\n🥇 最好：{SH[best['idx']]}时 {best['时柱串']}（{best['total']:+.2f}）"
          f"\n🥈 平均：{SH[avg['idx']]}时 {avg['时柱串']}（{avg['total']:+.2f}·一喜一忌层内最中性）"
          f"\n❌ 最差：{SH[worst['idx']]}时 {worst['时柱串']}（{worst['total']:+.2f}）")

    if a.out:
        L = [f"# {a.name} · 时柱反推扫描（{a.date} · {a.place}）\n",
             f"三柱：{yg}{yz} {mg}{mz} {dg}{dz}｜日主 {dg}\n",
             "| 排名 | 时辰 | 时柱 | 时干十神 | 身强弱 | 格局 | 成格 | 层级 | 财星 | 空亡 | A | B | C | D | E | 综合分 |",
             "|:--:|:---|:---|:---|:--:|:---|:--:|:---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|"]
        for n, r in enumerate(rank, 1):
            L.append(f"| {n} | {SH[r['idx']]} | {r['时柱串']} | {r['十神']} | {r['身强弱']} | {r['格局']} | "
                     f"{'✅' if r['成格'] else '—'} | {r['quad']} | {r['财星']} | {'空' if r['空亡'] else '—'} | "
                     f"{r['A']:+d} | {r['B']:+.2f} | {r['C']:+d} | {r['D']:.2f} | {r['E']:+d} | **{r['total']:+.2f}** |")
        L += ["", f"**🥇 最好**：{SH[best['idx']]}时 {best['时柱串']}",
              f"**🥈 平均**：{SH[avg['idx']]}时 {avg['时柱串']}（一喜一忌层内最中性）",
              f"**❌ 最差**：{SH[worst['idx']]}时 {worst['时柱串']}", ""]
        open(a.out, 'w', encoding='utf-8').write('\n'.join(L))
        print(f"💾 扫描表 → {a.out}")


if __name__ == '__main__':
    main()
