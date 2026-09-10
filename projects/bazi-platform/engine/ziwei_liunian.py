#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 紫微流年权重层 v1.0（2026-09-10 建立）
================================================
在「本命权重层(§22.9)」之上，加**流年**一层：某一年哪些宫被引动、要注意什么。

规则（全部有据，不自创）：
  ① 流年命宫（太岁宫）= 流年地支所处之本命宫位 → 该年为「流年主战场」
  ② 流年四化 = 依流年天干查标准四化表（禄权科忌）→ 飞入本命宫位断吉凶
  ③ 叠加大限：流年命宫 与本命大限宫同宫 → 「大限+流年双激活」= 关键年
  ④ 叠加生年四化：流年化忌 与 生年化忌 同落一宫 / 同星 → 「双忌叠加」重点警示
  ⑤ 冲合引动：流年支 六冲/六合 本命宫位支 → 该宫被「冲开/合动」

输出：§22.10 流年权重层（含当年+次年），白话 + 怎么办。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ziwei_weight import all_scores, key_combos, current_daxian, PALACE_HINT
from ziwei_rules import PALACE_SIHUA, SIHUA_BASE, STAR_PALACE, STAR_BASE
from jixiong import sihua_tag, weight_tag

ZHI = "子丑寅卯辰巳午未申酉戌亥"
GAN = "甲乙丙丁戊己庚辛壬癸"

# 标准四化表（紫微斗数全书）：年干 → 禄/权/科/忌
SIHUA_TABLE = {
    "甲": ("廉贞", "破军", "武曲", "太阳"), "乙": ("天机", "天梁", "紫微", "太阴"),
    "丙": ("天同", "天机", "文昌", "廉贞"), "丁": ("太阴", "天同", "天机", "巨门"),
    "戊": ("贪狼", "太阴", "右弼", "天机"), "己": ("武曲", "贪狼", "天梁", "文曲"),
    "庚": ("太阳", "武曲", "太阴", "天同"), "辛": ("巨门", "太阳", "文曲", "文昌"),
    "壬": ("天梁", "紫微", "左辅", "武曲"), "癸": ("破军", "巨门", "太阴", "贪狼"),
}
LIU_CHONG = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
             "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}
LIU_HE = {("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未")}

# 年干支（立春口径，走 engine/jieqi.py；失败回退算术）
def year_gan_zhi(year: int) -> tuple:
    try:
        import jieqi
        from datetime import datetime as _dt
        return jieqi.year_gan_zhi(_dt(year, 7, 1))
    except Exception:
        return GAN[(year - 4) % 10], ZHI[(year - 4) % 12]


def _zmap(zw):
    return {p["宫位"]: p for p in zw["紫微"]["十二宫"]}


def _palace_by_zhi(zmap, zhi):
    for p in zmap.values():
        if p["干支"][1] == zhi:
            return p
    return None


def _find_star_palaces(zmap, star):
    """某星落在哪个宫（含主星与辅星）"""
    out = []
    for p in zmap.values():
        for s in list(p.get("主星") or []) + list(p.get("辅星") or []):
            if s.get("名") == star:
                out.append((p["宫位"], s.get("庙旺"), s.get("四化")))
    return out


def liunian_analysis(zw: dict, year: int, birth_year: int) -> dict:
    zmap = _zmap(zw)
    g, z = year_gan_zhi(year)
    ln_ming = _palace_by_zhi(zmap, z)
    S = all_scores(zw)
    row = {"年": year, "干支": g + z, "虚岁": year - birth_year + 1,
           "流年命宫": ln_ming["宫位"] if ln_ming else "",
           "流年命宫主星": "、".join(s["名"] for s in (ln_ming or {}).get("主星", [])) or "空宫",
           "流年命宫分": S["单宫"].get(ln_ming["宫位"], {}).get("分") if ln_ming else None,
           "领域总评": S["领域总评"].get(ln_ming["宫位"]) if ln_ming else None,
           "四化飞入": [], "叠加": [], "冲合": []}

    # ② 流年四化飞入本命宫位
    for hua, star in zip(("禄", "权", "科", "忌"), SIHUA_TABLE.get(g, ("", "", "", ""))):
        for gong, miao, sheng_hua in _find_star_palaces(zmap, star):
            desc = PALACE_SIHUA.get(gong, {}).get(hua, "")
            note = f"{star}化{hua} → 本命{gong}"
            if miao:
                note += f"（{miao}）"
            row["四化飞入"].append({"化": hua, "星": star, "宫": gong, "庙旺": miao,
                                    "白话": desc, "生年同星同化": sheng_hua == hua})
            # ④ 叠加生年四化（同宫同化）
            if sheng_hua == hua:
                row["叠加"].append(f"流年{star}化{hua} 与 生年{star}化{hua} **同星同化** → "
                                   f"{gong}这块双倍发力（吉则更吉、忌则要更当心）")
            elif sheng_hua == "忌" and hua == "忌":
                row["叠加"].append(f"流年{star}化忌 叠加生年{gong}原有化忌 → 「**双忌叠宫**」重点警示")
            elif sheng_hua and hua == "忌":
                row["叠加"].append(f"流年{star}化忌 落宫正是生年{star}化{sheng_hua}之处 → 先得后失，宜守")

    # ③ 大限叠加
    dx = current_daxian(zw, birth_year)
    if dx.get("宫位") and ln_ming and dx["宫位"] == ln_ming["宫位"]:
        row["叠加"].append(f"流年命宫 = 当前大限宫（{dx['宫位']}）→ **大限+流年双激活**："
                           f"这一年是十年主线上的关键年，重大决定放在这一年")

    # ⑤ 冲合引动
    for p in zmap.values():
        pz = p["干支"][1]
        if LIU_CHONG.get(z) == pz:
            row["冲合"].append(f"流年{z}冲本命{p['宫位']}（{pz}）→ {PALACE_HINT.get(p['宫位'],'')}这块被冲动（变动/搬迁/调整）")
        for a, b in LIU_HE:
            if (z, pz) == (a, b) or (z, pz) == (b, a):
                row["冲合"].append(f"流年{z}合本命{p['宫位']}（{pz}）→ {PALACE_HINT.get(p['宫位'],'')}这块被合动（合作/姻缘/机会）")
    return row


def liunian_section(name, ds, zw, years=(2026, 2027)) -> str:
    by = 0
    try:
        by = int(str(zw.get("公历", ""))[:4])
    except Exception:
        by = (ds.get("出生年份") or 0)
    if not by:
        return ""
    rows = [liunian_analysis(zw, y, by) for y in years]

    L = ["\n\n---\n\n## §22.10 流年权重层（今年/明年 · 哪些宫被引动）\n"]
    L.append("> **怎么看**：① 流年命宫＝该年的主战场；② 流年四化飞入本命宫位＝该年具体吉凶落点；"
             "③ 与生年四化/大限的叠加＝重点警示；④ 冲合＝被动引动的事。\n"
             "> ⚠️ 流年四化依**年干**查标准四化表；流年命宫按**流年地支（太岁）**定位。\n")

    for r in rows:
        L.append(f"### {r['年']} 年（{r['干支']}·虚岁 {r['虚岁']}）\n")
        L.append(f"- **流年命宫（主战场）：{r['流年命宫']}** {weight_tag(r['流年命宫分'] or 50)} ｜ "
                 f"主星：{r['流年命宫主星']} ｜ 单宫分 **{r['流年命宫分']}** ｜ 领域总评 **{r['领域总评']}** → "
                 f"{PALACE_HINT.get(r['流年命宫'],'')}"
                 f"（{'强项年，可发力' if (r['领域总评'] or 0) >= 62 else '弱项年，宜守成' if (r['领域总评'] or 0) < 48 else '中平年，稳扎稳打'}）")
        if r["四化飞入"]:
            L.append("")
            L.append("| 流年四化 | 落本命宫 | 吉凶 | 庙旺 | **大白话** |")
            L.append("|:---|:---|:---|:---|:---|")
            for f in r["四化飞入"]:
                L.append(f"| {f['星']}化{f['化']} | {f['宫']} | "
                         f"{sihua_tag(f['化'], f['庙旺'], None, [f['化']], doubled=f.get('生年同星同化', False))} | "
                         f"{f['庙旺'] or '—'} | {f['白话']} |")
        if r["叠加"]:
            L.append("")
            for s in r["叠加"]:
                L.append(f"- ⚠️ {s}")
        if r["冲合"]:
            L.append("")
            for s in r["冲合"][:6]:
                L.append(f"- {s}")
        L.append("")
    L.append("**📌 用法**：流年命宫＝今年重心；化禄落宫＝使力方向；化忌落宫＝今年要防的地方（提前补，不硬碰）。")
    return "\n".join(L) + "\n"
