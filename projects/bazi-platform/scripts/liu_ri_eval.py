#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""流日择日评估器 v1.0（确定性规则，非LLM臆断）

用途：给定命主四柱/喜忌，评估指定日期区间的每一天（默认周六），输出可解释评分。
规则（全部显式，可复核）：
  基础分 5.0
  1) 十神：日干/日支本气十神，喜神 +1，忌神 -1
  2) 关系（只计「流年/流月/流日」参与的组合）：
       六冲 -1.5/对；相刑 -1/对；相害 -0.5/对；伏吟 -0.5/对；自刑 -1
       六合/半合/三合/三会：合成五行属喜 +1，属忌 -1
  3) 神煞：文昌日 +1.5；天乙贵人日 +0.5
输出 0-10 分 + 明细，供报告引用。

用法：
  python3 scripts/liu_ri_eval.py --sizhu "辛卯 癸巳 丙戌 癸巳" --gender 男 \
         --start 2026-11-01 --end 2026-12-31 --weekday sat --xi 金,土,水 --ji 木,火
"""
import argparse
import datetime as dt
import sys

GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
          "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
ZHI_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
          "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}
# 地支本气（用于十神）
ZHI_BENQI = {"子": "癸", "丑": "己", "寅": "甲", "卯": "乙", "辰": "戊", "巳": "丙",
             "午": "丁", "未": "己", "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬"}

SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

LIU_HE = {frozenset("子丑"), frozenset("寅亥"), frozenset("卯戌"),
          frozenset("辰酉"), frozenset("巳申"), frozenset("午未")}
LIU_HE_WX = {frozenset("子丑"): "土", frozenset("寅亥"): "木", frozenset("卯戌"): "火",
             frozenset("辰酉"): "金", frozenset("巳申"): "水", frozenset("午未"): "土"}
LIU_CHONG = {frozenset("子午"), frozenset("丑未"), frozenset("寅申"),
             frozenset("卯酉"), frozenset("辰戌"), frozenset("巳亥")}
LIU_HAI = {frozenset("子未"), frozenset("丑午"), frozenset("寅巳"),
           frozenset("卯辰"), frozenset("申亥"), frozenset("酉戌")}
SAN_HE = {"申子辰": "水", "亥卯未": "木", "寅午戌": "火", "巳酉丑": "金"}
SAN_HUI = {"寅卯辰": "木", "巳午未": "火", "申酉戌": "金", "亥子丑": "水"}
ZI_XING = set("辰午酉亥")


def shi_shen(ri_gan: str, target_gan: str) -> str:
    """以日干为我，返回目标天干的十神（简化：只分五行+阴阳）。"""
    me, other = GAN_WX[ri_gan], GAN_WX[target_gan]
    same_yin_yang = (GAN_YANG[ri_gan] == GAN_YANG[target_gan])
    if me == other:
        return "比肩" if same_yin_yang else "劫财"
    if SHENG[me] == other:
        return "食神" if same_yin_yang else "伤官"
    if SHENG[other] == me:
        return "偏印" if same_yin_yang else "正印"
    if KE[me] == other:
        return "偏财" if same_yin_yang else "正财"
    if KE[other] == me:
        return "七杀" if same_yin_yang else "正官"
    return "?"


GAN_YANG = {"甲": True, "乙": False, "丙": True, "丁": False, "戊": True,
            "己": False, "庚": True, "辛": False, "壬": True, "癸": False}

SS_WX = {"比肩": "同我", "劫财": "同我", "食神": "我生", "伤官": "我生",
         "正印": "生我", "偏印": "生我", "正财": "我克", "偏财": "我克",
         "正官": "克我", "七杀": "克我"}


def ss_to_wx(ri_gan: str, ss: str) -> str:
    me = GAN_WX[ri_gan]
    rel = SS_WX.get(ss, "")
    if rel == "同我":
        return me
    if rel == "我生":
        return SHENG[me]
    if rel == "生我":
        return [k for k, v in SHENG.items() if v == me][0]
    if rel == "我克":
        return KE[me]
    if rel == "克我":
        return [k for k, v in KE.items() if v == me][0]
    return "?"


def xing_pairs(branches: list[str]) -> list[tuple[str, str]]:
    """返回相刑组合（三刑缺一按二刑算，自刑需同支）。"""
    out = []
    s = set(branches)
    # 三刑
    if {"寅", "巳", "申"} <= s:
        out += [("寅", "巳"), ("巳", "申"), ("申", "寅")]
    if {"丑", "未", "戌"} <= s:
        out += [("丑", "未"), ("未", "戌"), ("戌", "丑")]
    # 二刑（缺一也算）
    for a, b in [("寅", "巳"), ("巳", "申"), ("申", "寅"), ("丑", "未"), ("未", "戌"), ("戌", "丑")]:
        if a in s and b in s and (a, b) not in out and (b, a) not in out:
            out.append((a, b))
    # 子卯刑
    if "子" in s and "卯" in s:
        out.append(("子", "卯"))
    return out


def evaluate_day(ri_gan: str, natal: list[str], year_zhi: str, month_zhi: str,
                 day_gan: str, day_zhi: str, xi: list[str], ji: list[str]) -> dict:
    score = 5.0
    notes = []
    # 1) 十神
    ss_g = shi_shen(ri_gan, day_gan)
    wx_g = GAN_WX[day_gan]
    ss_z = shi_shen(ri_gan, ZHI_BENQI[day_zhi])
    wx_z = ZHI_WX[day_zhi]
    for label, ss, wx in [("日干", ss_g, wx_g), ("日支", ss_z, wx_z)]:
        if wx in xi:
            score += 1
            notes.append(f"{label}{ss}({wx}·喜)+1")
        elif wx in ji:
            score -= 1
            notes.append(f"{label}{ss}({wx}·忌)-1")

    # 2) 关系：只计 流年/流月/流日 参与的组合
    flow = [(n, z) for n, z in [("流年", year_zhi), ("流月", month_zhi), ("流日", day_zhi)] if z]
    all_b = natal + [z for _, z in flow]
    for name, z in flow:
        for nz in natal:
            pair = frozenset({z, nz})
            if pair in LIU_CHONG:
                score -= 1.5
                notes.append(f"{name}{z}冲{nz}-1.5")
            elif pair in LIU_HE:
                wx = LIU_HE_WX.get(pair, "")
                if wx in xi:
                    score += 1
                    notes.append(f"{name}{z}合{nz}→{wx}(喜)+1")
                elif wx in ji:
                    score -= 1
                    notes.append(f"{name}{z}合{nz}→{wx}(忌)-1")
            elif pair in LIU_HAI:
                score -= 0.5
                notes.append(f"{name}{z}害{nz}-0.5")
            if z == nz:
                score -= 0.5
                notes.append(f"{name}{z}伏吟{nz}-0.5")
    # 流年/流月/流日 之间
    fz = [z for _, z in flow]
    for i in range(len(fz)):
        for j in range(i + 1, len(fz)):
            a, b = fz[i], fz[j]
            if frozenset({a, b}) in LIU_CHONG:
                score -= 1.5
                notes.append(f"{a}冲{b}-1.5")
            if a == b and a in ZI_XING:
                score -= 1
                notes.append(f"{a}{a}自刑-1")
            elif a == b:
                score -= 0.5
                notes.append(f"{a}{b}伏吟-0.5")
    # 相刑
    for a, b in xing_pairs(all_b):
        involved = any(a == z or b == z for _, z in flow)
        if involved and frozenset({a, b}) not in LIU_HE:  # 合能解刑
            score -= 1
            notes.append(f"{a}{b}刑-1")
    # 三合/半合/三会（含流日）
    for group, wx in SAN_HE.items():
        present = [g for g in group if g in all_b]
        if day_zhi in group and len(present) >= 3:
            if wx in xi:
                score += 1
                notes.append(f"三合{wx}局(喜)+1")
            elif wx in ji:
                score -= 1
                notes.append(f"三合{wx}局(忌)-1")

    # 3) 神煞
    wenchang = {"甲": "巳", "乙": "午", "丙": "申", "戊": "申", "丁": "酉",
                "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"}[ri_gan]
    if day_zhi == wenchang:
        score += 1.5
        notes.append(f"文昌日({day_zhi})+1.5")
    tianyi = {"甲": "丑未", "戊": "丑未", "庚": "丑未", "乙": "子申", "己": "子申",
              "丙": "亥酉", "丁": "亥酉", "壬": "卯巳", "癸": "卯巳", "辛": "寅午"}[ri_gan]
    if day_zhi in tianyi:
        score += 0.5
        notes.append(f"天乙贵人({day_zhi})+0.5")

    return {"score": round(max(0, min(10, score)), 1), "gan": day_gan, "zhi": day_zhi,
            "shi_shen": f"{ss_g}/{ss_z}", "notes": notes}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizhu", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--weekday", default="sat", help="sat / sun / sat,sun / all")
    ap.add_argument("--xi", required=True)
    ap.add_argument("--ji", required=True)
    a = ap.parse_args()

    from lunar_python import Solar
    pillars = a.sizhu.split()
    ri_gan = pillars[2][0]
    natal = [p[1] for p in pillars]
    xi, ji = a.xi.split(","), a.ji.split(",")

    d0 = dt.date.fromisoformat(a.start)
    d1 = dt.date.fromisoformat(a.end)
    rows = []
    d = d0
    while d <= d1:
        _want = {"sat": 5, "sun": 6}
        _sel = a.weekday.split(",")
        if a.weekday == "all" or d.weekday() in ({_want[k] for k in _sel if k in _want} or {5, 6}):
            ec = Solar.fromYmd(d.year, d.month, d.day).getLunar().getEightChar()
            r = evaluate_day(ri_gan, natal, ec.getYear()[1], ec.getMonth()[1], ec.getDay()[0], ec.getDay()[1], xi, ji)
            rows.append((d, ec.getMonth(), r))
        d += dt.timedelta(days=1)

    print(f"命主: {a.sizhu} | 日主 {ri_gan} | 喜 {xi} 忌 {ji}")
    print(f"{'日期':<12}{'星期':<4}{'月柱':<5}{'日柱':<4}{'评分':<5}{'十神':<12}明细")
    print("─" * 110)
    for d, mz, r in sorted(rows, key=lambda x: -x[2]["score"]):
        print(f"{d}{'  周六' if d.weekday()==5 else '':<4}{mz:<5}{r['gan']}{r['zhi']:<3}{r['score']:<5}{r['shi_shen']:<12}{'; '.join(r['notes'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
