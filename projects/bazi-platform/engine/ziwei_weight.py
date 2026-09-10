#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 紫微叠加权重层 v1.0（2026-09-10 建立）
=================================================
把「单星断 → 双星断 → 三方组合断」再叠一层**量化**：
    主星性质分 × 庙旺系数 + 双星加成 + 辅星吉煞分 + 四化分  → 每宫强度分(0-100)
    再按 本宫55% + 三方各15% 加权 → 该领域「总评」
最后输出：① 十二宫强弱排行 ② 三大王牌 / 三大短板 ③ 四级叠加断语（白话+怎么办）

🚨 定位声明（老板原则④零自创断事逻辑）：
  · 断语**文本**来自规则库（ziwei_rules / ziwei_star_combo），本层不新造断语；
  · 本层只做**量化排序与重点识别**（哪些宫是强项、哪些是短板、哪年激活），
    系数为引擎模型参数（可调），不单独作为断命依据。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ziwei_star_combo import DOUBLE_STAR, _DS_LOOKUP

# ── 参数区（可调）──────────────────────────────────────────
MIAO_COEF = {"庙": 1.30, "旺": 1.20, "得": 1.10, "利": 1.00,
             "平": 0.85, "不": 0.80, "陷": 0.70}
MIAO_DEFAULT = 0.95

STAR_SCORE = {"紫微": 11, "天府": 11, "天相": 9, "天梁": 9, "太阴": 8, "太阳": 8,
              "武曲": 7, "天同": 7, "天机": 6, "廉贞": 6, "贪狼": 5, "巨门": 5,
              "七杀": 4, "破军": 3}
EMPTY_PENALTY = -5          # 空宫：力量靠借，略减

DOUBLE_SCORE = {"紫微天府": 8, "紫微贪狼": 2, "紫微天相": 7, "紫微七杀": 4, "紫微破军": 0,
                "天机太阴": 5, "天机巨门": 2, "天机天梁": 5,
                "太阳太阴": 4, "太阳巨门": 2, "太阳天梁": 6,
                "武曲天府": 9, "武曲贪狼": 3, "武曲天相": 7, "武曲七杀": 2, "武曲破军": -3,
                "天同太阴": 6, "天同巨门": 1, "天同天梁": 6,
                "廉贞天府": 7, "廉贞贪狼": -4, "廉贞天相": 6, "廉贞七杀": 0, "廉贞破军": -5}

AUX_SCORE = {"左辅": 8, "右弼": 8, "文昌": 6, "文曲": 6, "天魁": 7, "天钺": 7,
             "禄存": 10, "天马": 3,
             "擎羊": -7, "陀罗": -6, "火星": -5, "铃星": -5, "地空": -6, "地劫": -8}
SIHUA_SCORE = {"禄": 12, "权": 9, "科": 8, "忌": -16}

JI_AUX = {"左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存"}
SHA_AUX = {"擎羊", "陀罗", "火星", "铃星", "地空", "地劫"}
TAOHUA = {"贪狼", "廉贞", "文曲"}
WEAK_MIAO = {"陷", "平", "不", ""}
HARD_STARS = {"七杀", "破军", "武曲"}

PALACE_HINT = {
    "命宫": "你自己", "兄弟": "手足朋友", "夫妻": "婚姻配偶", "子女": "孩子",
    "财帛": "赚钱方式", "疾厄": "身体健康", "迁移": "外出发展", "仆役": "朋友下属",
    "官禄": "事业方向", "田宅": "房子家业", "福德": "精神享受", "父母": "长辈上级",
}


def _miao_coef(m):
    return MIAO_COEF.get(m or "", MIAO_DEFAULT)


def palace_score(palace: dict) -> dict:
    """单宫强度分（0-100）+ 明细"""
    bd = {"主星": 0.0, "双星加成": 0.0, "辅星": 0.0, "四化": 0.0, "空宫": 0.0}
    mains = palace.get("主星") or []
    if not mains:
        bd["空宫"] = EMPTY_PENALTY
    names = []
    for s in mains:
        nm = s.get("名", "")
        names.append(nm)
        bd["主星"] += STAR_SCORE.get(nm, 5) * _miao_coef(s.get("庙旺"))
    if len(names) >= 2:
        key = _DS_LOOKUP.get("".join(names[:2]))
        if key:
            bd["双星加成"] = DOUBLE_SCORE.get(key, 0)
    for a in palace.get("辅星") or []:
        nm = a.get("名", "")
        bd["辅星"] += AUX_SCORE.get(nm, 0)
        if a.get("四化"):
            bd["四化"] += SIHUA_SCORE.get(a["四化"], 0)
    for s in mains:
        if s.get("四化"):
            bd["四化"] += SIHUA_SCORE.get(s["四化"], 0)
    score = max(0.0, min(100.0, 50 + sum(bd.values())))
    grade = ("强" if score >= 75 else "偏强" if score >= 62 else "中" if score >= 48
             else "偏弱" if score >= 35 else "弱")
    return {"分": round(score, 1), "等级": grade, "明细": {k: round(v, 1) for k, v in bd.items()},
            "主星": names}


def _san_fang_names(palace, zmap):
    ZHI = "子丑寅卯辰巳午未申酉戌亥"
    try:
        z = ZHI.index(palace["干支"][1])
    except Exception:
        return []
    out = []
    for off in (0, 4, 8, 6):
        tz = ZHI[(z + off) % 12]
        for p in zmap.values():
            if p["干支"][1] == tz:
                out.append(p["宫位"])
                break
    return out


def all_scores(zw: dict) -> dict:
    """十二宫评分 + 领域总评（本宫55% + 三方各15%）"""
    zmap = {p["宫位"]: p for p in zw["紫微"]["十二宫"]}
    per = {g: palace_score(p) for g, p in zmap.items()}
    weighted = {}
    for g, p in zmap.items():
        sf = _san_fang_names(p, zmap)
        others = [x for x in sf if x != g]
        s = per[g]["分"] * 0.55 + sum(per.get(o, {}).get("分", 50) for o in others) * 0.15
        weighted[g] = round(min(100.0, s), 1)
    return {"单宫": per, "领域总评": weighted, "zmap": zmap}


def current_daxian(zw: dict, birth_year: int) -> dict:
    """当前大限（虚岁口径）"""
    age = 2026 - birth_year + 1
    for p in zw["紫微"]["十二宫"]:
        rng = p.get("大限")
        if not rng:
            continue
        try:
            a, b = rng.replace("岁", "").split("-")
            if int(a) <= age <= int(b):
                return {"宫位": p["宫位"], "区间": rng, "虚岁": age,
                        "主星": [s["名"] for s in p.get("主星", [])]}
        except Exception:
            continue
    return {"宫位": "", "区间": "", "虚岁": age, "主星": []}


def key_combos(zw: dict) -> dict:
    """王牌 / 短板 / 特殊叠加断语"""
    zmap = {p["宫位"]: p for p in zw["紫微"]["十二宫"]}
    scores = {g: palace_score(p) for g, p in zmap.items()}
    ace, weak = [], []
    special = []
    for g, p in zmap.items():
        s = scores[g]
        hint = PALACE_HINT.get(g, g)
        mains = [x.get("名") for x in (p.get("主星") or [])]
        auxs = [x.get("名") for x in (p.get("辅星") or [])]
        sh = [x.get("四化") for x in (p.get("主星") or []) + (p.get("辅星") or []) if x.get("四化")]
        miao = [(x.get("名"), x.get("庙旺")) for x in (p.get("主星") or [])]
        n_ji = sum(1 for a in auxs if a in JI_AUX)
        n_sha = sum(1 for a in auxs if a in SHA_AUX)
        n_th = sum(1 for a in mains + auxs if a in TAOHUA)

        if s["分"] >= 75:
            _mt = "/".join((m[0] + (m[1] or "")) for m in miao)
            _jt = "".join(a for a in auxs if a in JI_AUX)
            ace.append((g, s["分"], ("、".join(mains) or "空宫") + ("（" + _mt + "）" if _mt else "")
                        + ("+吉星" + _jt if n_ji else "")))
        if s["分"] <= 35:
            _st = "".join(a for a in auxs if a in SHA_AUX)
            weak.append((g, s["分"], ("、".join(mains) or "空宫") + ("+煞" + _st if n_sha else "")))

        # 四级叠加特殊断
        _ms = "/".join((x[1] or "—") for x in miao)
        _sn = "".join(a for a in auxs if a in SHA_AUX)
        if "忌" in sh and n_sha >= 1:
            special.append((g, "煞忌交加",
                            ("、".join(mains) + "（" + _ms + "）＋化忌＋" + _sn) if mains else ("空宫＋化忌＋" + _sn),
                            "→ " + hint + "这块是卡点叠加冲撞：低调守成、别硬碰，过了这步再动"))
        if mains and all((m[1] or "") in WEAK_MIAO for m in miao) and any(a in ("地空", "地劫") for a in auxs):
            special.append((g, "空转组合", f"{'、'.join(mains)}落陷＋{''.join(a for a in auxs if a in ('地空','地劫'))} → "
                            f"{hint}这块想法大、落地难：先小步验证再投入"))
        if n_ji >= 3 and mains and all((m[1] or "") in WEAK_MIAO for m in miao):
            special.append((g, "虚旺组合", f"吉星{n_ji}颗但主星{'、'.join(mains)}落陷 → "
                            f"{hint}看着热闹、实际要自己扛：别指望外力，靠流程和计划"))
        _HARD_SHA = {"擎羊", "陀罗", "火星", "铃星"}   # 空劫属破耗，不算硬拼
        _hard_sha = "".join(a for a in auxs if a in _HARD_SHA)
        if _hard_sha and any(m in HARD_STARS for m in mains) and g in ("命宫", "官禄", "财帛", "迁移", "仆役"):
            _hs = "、".join(m for m in mains if m in HARD_STARS)
            special.append((g, "硬拼可用",
                            _hs + "＋" + _hard_sha,
                            "这块是硬碰硬的场（" + _hs + "+" + _hard_sha + "）："
                            "适合工程/军警/医疗/竞技/销售这类硬行业，越硬越出成绩；软岗位反而憋屈（" + hint + "）"))
        if n_th >= 3:
            special.append((g, "桃花过旺", f"桃花星{n_th}颗（{'、'.join(x for x in mains + auxs if x in TAOHUA)}） → "
                            f"{hint}这块人缘旺、机会多：把关系做成资源，别做成消耗"))
        if ("天府" in mains or "禄存" in auxs) and g in ("财帛", "田宅"):
            special.append((g, "库星入库", f"{'、'.join(mains)}＋禄存/库星 → {hint}这块存得住，适合做长期资产"))
    ace.sort(key=lambda x: -x[1])
    weak.sort(key=lambda x: x[1])
    return {"王牌": ace, "短板": weak, "特殊": special}


def weight_section(name, ds, zw, birth_year=None) -> str:
    """§22.9 叠加权重层（量化强弱 + 王牌/短板 + 四级叠加断）"""
    S = all_scores(zw)
    KB = key_combos(zw)
    by = birth_year or (ds.get("出生年份") or 0)
    if not by:
        try:
            by = int(str(zw.get("公历", ""))[:4])
        except Exception:
            by = 0
    dx = current_daxian(zw, int(by)) if by else {"宫位": "", "区间": "", "虚岁": "", "主星": []}

    L = ["\n\n---\n\n## §22.9 叠加权重层（星×庙旺×辅星×四化 → 量化强弱）\n"]
    L.append("> **怎么算的**：主星性质分 × 庙旺系数 + 双星加成 + 辅星吉煞分 + 四化分 → 每宫强度分；"
             "再按「本宫55% + 三方各15%」算领域总评。\n"
             "> **怎么用**：分高的地方是你的强项（重仓），分低的是短板（要补/要防）。\n"
             "> ⚠️ 本层是**引擎量化模型**（系数可调），只做排序与重点识别；断语文本来自规则库，不单独作为断命依据。\n")

    L.append("### 22.9.1 十二宫强弱排行（总分＝单宫分｜领域总评）\n")
    L.append("| 排名 | 宫位 | 管的事 | 单宫分 | 等级 | 领域总评 | 主星（庙旺） | 加减分明细 |")
    L.append("|:--:|:---|:---|:--:|:---|:--:|:---|:---|")
    rank = sorted(S["单宫"].items(), key=lambda kv: -kv[1]["分"])
    for i, (g, v) in enumerate(rank, 1):
        p = S["zmap"][g]
        miao = "、".join(f"{x['名']}{x['庙旺'] or ''}{('·化' + x['四化']) if x['四化'] else ''}"
                        for x in p.get("主星", [])) or "空宫"
        bd = " ".join(f"{k}{v2:+.1f}" for k, v2 in v["明细"].items() if abs(v2) > 0.05)
        L.append(f"| {i} | **{g}** | {PALACE_HINT.get(g,'')} | **{v['分']}** | {v['等级']} | "
                 f"{S['领域总评'][g]} | {miao} | {bd or '—'} |")
    L.append("")

    L.append("### 22.9.2 三大王牌（重仓区）\n")
    if KB["王牌"]:
        for g, sc, desc in KB["王牌"][:3]:
            L.append(f"- **{g}（{sc}分）** {desc} → 这块是你的强项，**资源优先往这儿放**")
    else:
        L.append("- 本盘无 ≥75 分的宫位：整体偏均衡/偏保守，靠稳扎稳打而非单点爆破。")
    L.append("")

    L.append("### 22.9.3 三大短板（要补要防）\n")
    if KB["短板"]:
        for g, sc, desc in KB["短板"][:3]:
            L.append(f"- **{g}（{sc}分）** {desc} → 这块要主动补、提前防，**别在这儿硬押重注**")
    else:
        L.append("- 本盘无 ≤35 分的宫位：没有致命短板，属「底盘稳」型。")
    L.append("")

    if KB["特殊"]:
        L.append("### 22.9.4 四级叠加特殊组合（星×庙旺×辅星×四化 叠加识别）\n")
        L.append("| 宫位 | 组合类型 | 叠加实况 | **大白话 + 怎么办** |")
        L.append("|:---|:---|:---|:---|")
        seen = set()
        for _item in KB["特殊"]:
            g, t = _item[0], _item[1]
            _rest = list(_item[2:])
            if len(_rest) >= 2:
                _sitch, _advice = _rest[0], _rest[1]
            else:
                _parts = str(_rest[0]).split(" → ", 1)
                _sitch = _parts[0]
                _advice = _parts[1] if len(_parts) > 1 else ""
            _advice = str(_advice).replace("→ ", "").strip()
            k = (g, t)
            if k in seen:
                continue
            seen.add(k)
            L.append(f"| **{g}**（{PALACE_HINT.get(g,'')}） | {t} | {_sitch} | {_advice} |")
        L.append("")

    if dx.get("宫位"):
        L.append("### 22.9.5 当前大限激活（2026 年 · 虚岁 " + str(dx["虚岁"]) + "）\n")
        L.append(f"- 当前大限宫：**{dx['宫位']}**（{dx['区间']}）｜主星：{'、'.join(dx['主星']) or '空宫'}")
        g = dx["宫位"]
        L.append(f"- 这十年的主战场是「{PALACE_HINT.get(g,'')}」，单宫分 **{S['单宫'][g]['分']}**、"
                 f"领域总评 **{S['领域总评'][g]}** → "
                 f"{'这十年正是你的强项区，适合发力扩张' if S['领域总评'][g] >= 62 else '这十年是弱项区，宜守成、先补短板再图进' if S['领域总评'][g] < 48 else '这十年中平，靠稳扎稳打积累'}")
        L.append("")
    return "\n".join(L) + "\n"
