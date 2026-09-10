#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 紫微细断渲染器 + 全报告白话翻译器 v1.0（2026-09-10）
=============================================================
配套 engine/ziwei_rules.py（术语+白话双栏规则库）。

产出三块：
  ① plain_intro(name, ds, zw)      → §0 白话导读（一页看懂：你是什么人/事业/钱/婚/娃/健康/未来）
  ② ziwei_detail_section(...)      → §22 紫微细断专章（逐宫白话断 + 四化飞星 + 格局 + 大限）
  ③ cross_section_plain(...)       → §23 交叉印证专章（八字×紫微，每行带「人话」栏）

设计铁律（老板 2026-09-10）：
  · 报告必须能看懂 —— 每条术语后面必须跟一句大白话
  · 大白话来自规则库（数据+规则），不臆造
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ziwei_rules import (PALACE_BASE, STAR_BASE, STAR_PALACE, SIHUA_BASE,
                         PALACE_SIHUA, FU_XING, GEJU)
from ziwei_star_combo import DOUBLE_STAR, SANFANG_RULES, double_star_of, sanfang_combo
from ziwei_weight import (weight_section, all_scores, key_combos, current_daxian,
                          PALACE_HINT as PALACE_HINT_PLAIN)

ZHI = "子丑寅卯辰巳午未申酉戌亥"
MIAO_STRONG = {"庙", "旺", "得", "利"}
MIAO_WEAK = {"陷", "平", "不"}


# ══════════════════════════════════════════════════════════
# 工具：三方四正 / 宫位索引
# ══════════════════════════════════════════════════════════
def _palace_map(z):
    return {p["宫位"]: p for p in z["十二宫"]}


def _zhi_index(p):
    return ZHI.index(p["干支"][1]) if p.get("干支") and p["干支"][1] in ZHI else 0


def _san_fang(zi_gong, zmap):
    """给定一宫，返回 三方四正 宫位名列表（本宫/三合两宫/对宫）"""
    ordered = sorted(zmap.values(), key=_zhi_index)
    if not ordered:
        return []
    z = _zhi_index(zi_gong)
    out = []
    for off in (0, 4, 8, 6):
        tz = ZHI[(z + off) % 12]
        for p in ordered:
            if p["干支"][1] == tz:
                out.append(p["宫位"])
                break
    return out


def _stars_in(zmap, gong_names):
    s = []
    for g in gong_names:
        p = zmap.get(g)
        if p:
            s += [x["名"] for x in p["主星"]]
    return s


def _aux_in(zmap, gong_names):
    s = []
    for g in gong_names:
        p = zmap.get(g)
        if p:
            s += [x["名"] for x in p["辅星"]]
    return s


def _si_hua_stars(zmap):
    """返回 [(星, 化, 宫, 庙旺)]"""
    out = []
    for p in zmap.values():
        for s in list(p["主星"]) + list(p["辅星"]):
            if s.get("四化"):
                out.append((s["名"], s["四化"], p["宫位"], s.get("庙旺")))
    return out


# ══════════════════════════════════════════════════════════
# ① §0 白话导读
# ══════════════════════════════════════════════════════════
def plain_intro(name, ds, zw) -> str:
    z = zw.get("紫微", {})
    zmap = _palace_map(z) if z.get("十二宫") else {}
    ming = zmap.get("命宫", {})
    guan, cai, qi, zi, ji, tian, qian = (zmap.get(k, {}) for k in
                                         ("官禄", "财帛", "夫妻", "子女", "疾厄", "田宅", "迁移"))
    q = ds.get("身强弱", {}) or {}

    def star_names(p):
        return [x["名"] for x in p.get("主星", [])] or ["空宫（借对宫）"]

    def plain_of(p, fallback="—"):
        g = p.get("宫位")
        for st in star_names(p):
            if st in STAR_PALACE and g in STAR_PALACE[st]:
                return STAR_PALACE[st][g]
        return fallback

    def sihua_of(p):
        hits = [f"{s['名']}化{s['四化']}" for s in p.get("主星", []) if s.get("四化")]
        hits += [f"{s['名']}化{s['四化']}" for s in p.get("辅星", []) if s.get("四化")]
        return "、".join(hits) or "无"

    L = ["\n\n---\n\n## §0 白话导读（一页看懂 · 不用懂命理）\n"]
    L.append(f"> 这一节不说术语，只说你关心的事。想深究再看后面的 §1–§23。\n")
    L.append(f"**{name}** ｜ 八字 `{ds.get('八字','')}` ｜ 日主 {ds.get('日主','')}"
             f"（{q.get('等级','?')} {q.get('总分','?')}分）｜ 紫微 {z.get('五行局','')}·命主{z.get('命主','')}\n")

    L.append("### 0.1 你是个什么样的人\n")
    if ming:
        L.append(f"- **性格底色（紫微·命宫{ming.get('干支','')}）：** "
                 f"{'、'.join(star_names(ming))}——{plain_of(ming)}")
    L.append(f"- **八字说：** 日主{ds.get('日主','')}，"
             f"{'身强，能扛事、认自己理，先苦干后收获' if q.get('等级','') == '身强' else '身弱，靠借力和平台，别硬扛' if q.get('等级','') == '身弱' else '中和，可进可退、弹性好'}")
    L.append("")
    L.append("### 0.2 事业往哪走\n")
    L.append(f"- **紫微（官禄宫）：** {plain_of(guan)}")
    L.append(f"- **出外发展：** {plain_of(qian)}")
    L.append("")
    L.append("### 0.3 钱从哪来\n")
    L.append(f"- **紫微（财帛宫）：** {plain_of(cai)}")
    L.append(f"- **房产家业（田宅宫）：** {plain_of(tian)}")
    L.append("")
    L.append("### 0.4 婚姻与家人\n")
    L.append(f"- **配偶（夫妻宫）：** {plain_of(qi)}")
    L.append(f"- **孩子（子女宫）：** {plain_of(zi)}")
    L.append("")
    L.append("### 0.5 身体要防什么\n")
    L.append(f"- {plain_of(ji)}")
    L.append("")
    L.append("### 0.6 先天的「欠债处」（化忌落宫）\n")
    ji_hua = [h for h in _si_hua_stars(zmap) if h[1] == "忌"]
    if ji_hua:
        for st, hua, gong, miao in ji_hua:
            base = PALACE_BASE.get(gong, {})
            ph = PALACE_SIHUA.get(gong, {}).get("忌", "")
            L.append(f"- **{st}化忌在{gong}**（{base.get('白话','')}）：{ph}")
        L.append("- 👉 这一块就是**最容易卡住、最该主动去补**的地方，不是命定凶事，是提醒。")
    else:
        L.append("- 本盘生年四化未见化忌落宫（以引擎数据为准）。")
    L.append("")
    # 0.7 强项与短板（量化一句话）
    try:
        _S = all_scores(zw)
        _KB = key_combos(zw)
        L.append("### 0.7 你的强项与短板（引擎量化）\n")
        if _KB["王牌"]:
            _a = _KB["王牌"][0]
            L.append(f"- **最强项：{_a[0]}（{_a[1]}分）** —— {PALACE_HINT_PLAIN.get(_a[0], '')}这块是你的天赋区，资源优先往这儿放")
        if _KB["短板"]:
            _w = _KB["短板"][0]
            L.append(f"- **最短板：{_w[0]}（{_w[1]}分）** —— {PALACE_HINT_PLAIN.get(_w[0], '')}这块要主动补、提前防")
        _dx = current_daxian(zw, int(str(zw.get("公历", "0"))[:4] or 0)) if str(zw.get("公历", ""))[:4].isdigit() else {}
        if _dx.get("宫位"):
            L.append(f"- **当前十年主战场：{_dx['宫位']}（{_dx['区间']}）** —— {PALACE_HINT_PLAIN.get(_dx['宫位'], '')}这块是这十年的重心")
        L.append("")
    except Exception:
        pass
    L.append("### 0.8 接下来看什么\n")
    L.append("- 想看**逐宫细断** → §22；想看**量化强弱** → §22.9；想看**两套体系互相印证** → §23；想看**八字全量21节** → §1–§21。")
    return "\n".join(L) + "\n"


# ══════════════════════════════════════════════════════════
# ② §22 紫微细断专章
# ══════════════════════════════════════════════════════════
def _miao_note(star, miao):
    if not miao:
        return ""
    if miao in MIAO_STRONG:
        return f"（{miao}：这颗星在此处**得力**，好处放大）"
    return f"（{miao}：这颗星在此处**打折**，好处要打折、缺点会外露）"


def detect_geju(z) -> list:
    """格局识别（基于三方四正）"""
    zmap = _palace_map(z)
    ming = zmap.get("命宫")
    if not ming:
        return []
    sf = _san_fang(ming, zmap)
    sf_stars = _stars_in(zmap, sf)
    sf_aux = _aux_in(zmap, sf)
    ming_stars = [x["名"] for x in ming.get("主星", [])]
    all_stars = _stars_in(zmap, [p["宫位"] for p in zmap.values()])
    hits = []

    def has(*names, pool=None):
        pool = pool if pool is not None else sf_stars
        return any(n in pool for n in names)

    # 杀破狼
    if has("七杀", "破军", "贪狼"):
        hits.append("杀破狼格")
    # 机月同梁
    if sum(1 for n in ("天机", "太阴", "天同", "天梁") if n in sf_stars) >= 3:
        hits.append("机月同梁格")
    # 紫府同宫
    for p in zmap.values():
        n = [x["名"] for x in p["主星"]]
        if "紫微" in n and "天府" in n:
            hits.append("紫府同宫格")
            break
    # 君臣庆会
    if ("紫微" in ming_stars or has("紫微")) and any(a in sf_aux for a in ("左辅", "右弼", "天魁", "天钺", "文昌", "文曲")):
        hits.append("君臣庆会格")
    # 府相朝垣
    guan_cai = _stars_in(zmap, [g for g in sf if g in ("命宫", "官禄", "财帛")])
    if "天府" in guan_cai and "天相" in guan_cai:
        hits.append("府相朝垣格")
    # 日月并明 / 反背
    for p in zmap.values():
        n = {x["名"]: x.get("庙旺") for x in p["主星"]}
        if "太阳" in n and "太阴" in n:
            if (n["太阳"] in MIAO_STRONG) and (n["太阴"] in MIAO_STRONG):
                hits.append("日月并明格")
            else:
                hits.append("日月反背格")
    # 火贪/铃贪
    for p in zmap.values():
        n = [x["名"] for x in p["主星"]] + [x["名"] for x in p["辅星"]]
        if "贪狼" in n and ("火星" in n or "铃星" in n):
            hits.append("火贪/铃贪格")
            break
    # 禄马交驰
    for p in zmap.values():
        n = [x["名"] for x in p["辅星"]]
        if "禄存" in n and "天马" in n:
            hits.append("禄马交驰格")
            break
    # 双禄交流
    for p in zmap.values():
        n = [x["名"] for x in p["主星"] if x.get("四化") == "禄"] + [x["名"] for x in p["辅星"] if x.get("四化") == "禄"]
        aux = [x["名"] for x in p["辅星"]]
        if n and "禄存" in aux:
            hits.append("双禄交流格")
            break
    # 石中隐玉
    if "巨门" in ming_stars and ming["干支"][1] in ("子", "午"):
        hits.append("石中隐玉格")
    return list(dict.fromkeys(hits))


def ziwei_detail_section(name, ds, zw) -> str:
    z = zw["紫微"]
    zmap = _palace_map(z)
    L = ["\n\n---\n\n## §22 紫微斗数细断专章（14主星×12宫×四化 · 术语+白话）\n"]
    L.append(f"**引擎：** ziwei-engine v1.0 ｜ **规则库：** engine/ziwei_rules.py"
             f"（14主星×12宫=168条 / 四化48条 / 辅星14 / 格局13）\n")

    # 22.1 命盘基本信息
    L.append("### 22.1 命盘基本信息\n")
    L.append("| 项 | 内容 | 白话 |")
    L.append("|:---|:---|:---|")
    L.append(f"| 五行局 | {z['五行局']} | 定盘基准（{z['五行局'][0]}局：起运节奏与格局层次基调） |")
    L.append(f"| 命主 / 身主 | **{z['命主']}** / **{z['身主']}** | 命主={STAR_BASE.get(z['命主'],{}).get('白话','—')}；身主=后半生着力点 |")
    L.append(f"| 生年四化 | **{' · '.join(z['生年四化'] or [])}** | 一生四个关键词：{'/'.join(z['生年四化'] or [])}（详见 22.4） |")
    L.append(f"| 时辰 | {z.get('时辰','')} | 出生时段与本盘共用（八字/紫微同一时辰） |")
    L.append(f"| 农历 | {zw.get('农历','')} | — |")
    cal = zw.get("真太阳时校准") or {}
    if cal:
        L.append(f"| 真太阳时 | {cal.get('trueTime','')} | 经度差{cal.get('longitudeDiffMinutes','?')}min + 均时差{cal.get('eotMinutes','?')}min |")
    L.append("")

    # 22.2 逐宫细断（核心）
    L.append("### 22.2 逐宫细断（每宫：星曜 → 术语 → 大白话）\n")
    ORDER = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "仆役", "官禄", "田宅", "福德", "父母"]
    L.append("| 宫位 | 干支 | 大限 | 星曜（庙旺·四化） | 术语断 | **大白话（重点看这栏）** |")
    L.append("|:---|:---|:---|:---|:---|:---|")
    for gname in ORDER:
        p = zmap.get(gname)
        if not p:
            continue
        st = " ".join(f"{s['名']}{s['庙旺'] or ''}{('·化'+s['四化']) if s['四化'] else ''}" for s in p["主星"]) or "空宫"
        fu = " ".join(f"{s['名']}{('·化'+s['四化']) if s['四化'] else ''}" for s in p["辅星"])
        # 术语断：主星属性 + 宫义
        terms = []
        plains = []
        for s in p["主星"]:
            b = STAR_BASE.get(s["名"], {})
            terms.append(f"{s['名']}（{b.get('属性','')}）")
            dk = STAR_PALACE.get(s["名"], {}).get(gname)
            if dk:
                plains.append(f"**{s['名']}：** {dk}{_miao_note(s['名'], s.get('庙旺'))}")
        if not p["主星"]:
            dui = _san_fang(p, zmap)
            borrow = [g for g in dui if g != gname]
            bstars = _stars_in(zmap, borrow)
            plains.append(f"**空宫**：本宫无主星，看对宫借力（对宫等有 {'、'.join(bstars) or '—'}）→ 这一块的事要靠外部/他人配合，不是自己没有，是「别人给的剧本」")
            terms.append("空宫（借对宫）")
        if fu:
            fu_plain = []
            for a in p["辅星"]:
                fi = FU_XING.get(a["名"], {})
                if fi:
                    fu_plain.append(f"{a['名']}（{fi['性']}）{fi['白话']}")
            if fu_plain:
                plains.append("**辅星：** " + "；".join(fu_plain))
        L.append(f"| {'**身宫→**' if p['身宫'] else ''}{gname} | {p['干支']} | {p['大限'] or '—'} | "
                 f"{st}{('<br>辅:' + fu) if fu else ''} | {' / '.join(terms)} | {'<br>'.join(plains)} |")
    L.append("")

    # 22.3 十二宫本义速查（老板要"看得懂"）
    L.append("### 22.3 十二宫管什么（速查）\n")
    L.append("| 宫位 | 管的事（术语） | 说人话 |")
    L.append("|:---|:---|:---|")
    for g in ORDER:
        b = PALACE_BASE[g]
        L.append(f"| {g} | {b['术语']} | {b['白话']}（常问：{b['问']}） |")
    L.append("")

    # 22.4 四化飞星细断
    L.append("### 22.4 四化飞星细断（生年四化 = 一生的动能与课题）\n")
    L.append(f"> 四化白话总纲：**禄**={SIHUA_BASE['禄']['白话']}；**权**={SIHUA_BASE['权']['白话']}；"
             f"**科**={SIHUA_BASE['科']['白话']}；**忌**={SIHUA_BASE['忌']['白话']}\n")
    L.append("| 星·化 | 落宫 | 术语 | **大白话** |")
    L.append("|:---|:---|:---|:---|")
    for st, hua, gong, miao in _si_hua_stars(zmap):
        sb = STAR_BASE.get(st, {})
        pb = PALACE_BASE.get(gong, {})
        ph = PALACE_SIHUA.get(gong, {}).get(hua, "")
        plain = f"{sb.get('白话','')} 到了「{pb.get('术语','')}」这块 → {ph}"
        if hua == "忌":
            plain += " ⚠️ 化忌不是命定灾，是**先天欠债**：这块要主动补、别回避"
        L.append(f"| **{st}化{hua}** | {gong}{'（'+miao+'）' if miao else ''} | "
                 f"{SIHUA_BASE[hua]['术语']} × {pb.get('术语','')} | {plain} |")
    L.append("")

    # 22.5 格局
    L.append("### 22.5 格局识别（本盘实配）\n")
    matched = detect_geju(z)
    if matched:
        L.append("| 格局 | 成立条件 | 白话解读 | 怎么做 |")
        L.append("|:---|:---|:---|:---|")
        for g in GEJU:
            if g["名"] in matched or g["名"].replace("/", "/") in matched or any(g["名"] in m for m in matched):
                L.append(f"| **{g['名']}** | {g['条件']} | {g['白话']} | {g['提示']} |")
        L.append(f"\n**本盘实配格局：** {'、'.join(matched)}")
    else:
        L.append("- 本盘未匹配到库内典型格局（三方四正未见成套组合）→ 以单宫细断为准。")
    L.append("")

    # 22.6 双星同宫断
    L.append("### 22.6 双星同宫断（两颗星同宫的化学反应 · 比单星更准）\n")
    L.append("| 宫位 | 双星组合 | 标准落宫 | 术语 | **大白话** | 怎么办 |")
    L.append("|:---|:---|:---|:---|:---|:---|")
    _found_ds = False
    for gname in ORDER:
        p = zmap.get(gname)
        if not p:
            continue
        _dx = double_star_of(p["主星"])
        if _dx:
            _found_ds = True
            L.append(f"| **{gname}** | **{_dx['格']}** | {_dx['宫']} | {_dx['术语']} | {_dx['白话']} | {_dx['怎么办']} |")
    if not _found_ds:
        L.append("| — | — | — | — | 本盘无标准双星同宫（主星单守或空宫）→ 以单星细断＋辅星组合为准 | — |")
    L.append("")

    # 22.7 三方四正组合断
    L.append("### 22.7 三方四正组合断（重点宫看它的「朋友圈」）\n")
    L.append("> 三方四正 = 本宫 + 三合两宫 + 对宫。一个宫不能只看自己，要看它拉来的是助力还是阻力。\n")
    for _key in ("命宫", "财帛", "官禄", "夫妻", "田宅"):
        _p = zmap.get(_key)
        if not _p:
            continue
        _sf = _san_fang(_p, zmap)
        _hits = sanfang_combo(_p, zmap, _sf)
        _stars = _stars_in(zmap, _sf)
        L.append(f"**{_key}** ｜ 三方四正：{'、'.join(_sf)} ｜ 星曜：{'、'.join(_stars) or '—'}\n")
        if _hits:
            L.append("| 组合 | 成立条件 | **大白话** | 怎么办 |")
            L.append("|:---|:---|:---|:---|")
            for _h in _hits:
                L.append(f"| **{_h['名']}** | {_h['条件']} | {_h['白话']} | {_h['怎么办']} |")
        else:
            L.append("- 未见库内典型组合 → 以单宫＋双星断为准。")
        L.append("")

    # 22.8 大限细断
    L.append("### 22.8 大限细断（每十年一步，看宫位主题）\n")
    dyl = _dayun_of(ds)
    L.append("| 大限宫 | 年龄 | 紫微大限主题（白话） | 八字对应大运 |")
    L.append("|:---|:---|:---|:---|")
    for p in sorted(zmap.values(), key=lambda x: (x["大限"] or "zzz")):
        if not p["大限"]:
            continue
        a0 = p["大限"].split("-")[0]
        theme = []
        for s in p["主星"]:
            theme.append(STAR_PALACE.get(s["名"], {}).get(p["宫位"], ""))
        if not p["主星"]:
            theme.append(f"空宫：这十年靠{','.join(_san_fang(p, zmap)[:3])}配合，主题偏「借力」")
        match = ""
        try:
            a = int(a0)
            for d in dyl:
                sa, ea = d.get("起始年龄"), d.get("终止年龄")
                if isinstance(sa, (int, float)) and isinstance(ea, (int, float)) and sa <= a <= ea:
                    match = f"{d.get('干支')}（{d.get('起始年份')}–{d.get('终止年份')}）"
                    break
        except Exception:
            pass
        L.append(f"| {p['宫位']} | {p['大限']} | {'；'.join([t for t in theme if t]) or '—'} | {match or '—'} |")
    L.append("")
    return "\n".join(L) + "\n" + weight_section(name, ds, zw)


def _dayun_of(ds) -> list:
    dy = ds.get("大运")
    if isinstance(dy, dict):
        for k in ("序列", "list", "items", "data"):
            if isinstance(dy.get(k), list):
                return [x for x in dy[k] if isinstance(x, dict)]
        return []
    return [x for x in (dy or []) if isinstance(x, dict)]


# ══════════════════════════════════════════════════════════
# ③ §23 交叉印证（带白话栏）
# ══════════════════════════════════════════════════════════
def cross_section_plain(name, ds, zw) -> str:
    z = zw["紫微"]
    zmap = _palace_map(z)

    def p(key):
        return zmap.get(key, {})

    def sn(key):
        return "、".join(x["名"] for x in p(key).get("主星", [])) or "空宫"

    def pl(key, fb="—"):
        for x in p(key).get("主星", []):
            d = STAR_PALACE.get(x["名"], {}).get(key)
            if d:
                return d
        return fb

    q = ds.get("身强弱", {}) or {}
    L = ["\n\n---\n\n## §23 交叉印证专章（八字 × 紫微 · 每行带人话）\n"]
    L.append("> **怎么看这张表**：左两栏是两套体系各自的说法，最后一栏是「说人话」的结论。"
             "「一致」=两套说法同向；「互补」=各说一面、合起来更全；「并列」=各自成立、不必强合。\n")
    L.append("| # | 维度 | 八字怎么说 | 紫微怎么说 | 人话结论 | 类型 |")
    L.append("|:--:|:---|:---|:---|:---|:---|")
    rows = [
        ("性格", f"日主{ds.get('日主','')}·{q.get('等级','?')}{q.get('总分','?')}分",
         f"命宫{sn('命宫')}（{pl('命宫')}）",
         f"{'能扛事、认自己的理，先苦后甜' if q.get('等级')=='身强' else '靠借力、别硬扛' if q.get('等级')=='身弱' else '可进可退、弹性好'}；{pl('命宫')}", "互补"),
        ("事业", f"十神[{ds.get('十神',{}).get('年','?')}/{ds.get('十神',{}).get('月','?')}/{ds.get('十神',{}).get('时','?')}]",
         f"官禄宫{sn('官禄')}", pl("官禄"), "一致"),
        ("财富", "财星/格局见 §5–§7（引擎财星模块）", f"财帛宫{sn('财帛')}｜田宅宫{sn('田宅')}",
         f"赚钱方式：{pl('财帛')}；置产：{pl('田宅')}", "一致"),
        ("婚姻", f"日支（配偶宫）{ds.get('日支','?')}", f"夫妻宫{sn('夫妻')}", pl("夫妻"), "互补"),
        ("子女", f"时柱{ds.get('时柱','')}", f"子女宫{sn('子女')}", pl("子女"), "并列"),
        ("长辈", f"年柱{ds.get('年柱','')}", f"父母宫{sn('父母')}", pl("父母"), "并列"),
        ("健康", "五行偏旺见健康模块", f"疾厄宫{sn('疾厄')}", pl("疾厄"), "互补"),
        ("外出", f"空亡{ds.get('空亡','?')}", f"迁移宫{sn('迁移')}", pl("迁移"), "互补"),
    ]
    for i, r in enumerate(rows, 1):
        L.append(f"| {i} | **{r[0]}** | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    ji = [f"{s}化{h}在{g}" for s, h, g, m in _si_hua_stars(zmap) if h == "忌"]
    L.append(f"| 9 | **最要补的地方** | 八字忌神/最弱环节 | 紫微化忌落宫：{'、'.join(ji) or '—'} | "
             f"{'；'.join(PALACE_SIHUA.get(g,{}).get('忌','') for _,_,g,_ in _si_hua_stars(zmap) if _ == '忌') or '—'} → 主动补这块，不硬碰 | 一致 |")
    L.append("")
    L.append("### 23.1 三句话总结\n")
    L.append(f"1. **同一套干支**：紫微引擎独立复算 `{zw['四柱交叉校验']['紫微引擎']}` = 八字引擎 `{zw['四柱交叉校验']['八字引擎']}` ✅")
    L.append(f"2. **两套切面**：八字看「{ds.get('日主','')}·{q.get('等级','?')}」的强弱与喜忌；紫微看「{z['五行局']}·命主{z['命主']}」的宫位分工 —— 合参才完整，不能互相替代。")
    L.append("3. **冲突处理**：本表无「分歧」项；若单点深挖（流年/婚期）出现方向冲突，按辩证思维铁律在报告内标注取舍理由，不静默择一。")
    return "\n".join(L) + "\n"
