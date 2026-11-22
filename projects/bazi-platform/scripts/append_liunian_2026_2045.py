#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 21§ 双引擎报告追加「§24 未来20年流年详析（2026–2045）」。

用法：
    python3 scripts/append_liunian_2026_2045.py <姓名> <报告路径>

配置内置三人（家主/主母/少爷）的引擎参数；数据全部由 liu_nian_v2 实跑。
"""
import json
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, "engine"))
from liu_nian_v2 import analyze_liu_nian_v2  # noqa: E402
from shi_shen import get_shi_shen_for_gan  # noqa: E402
from lunar_python import Solar  # noqa: E402

CONFIG = {
    "魏启令": dict(rz="辛", rwx="金", nyz="申", nmz="未", gans=["庚", "癸", "辛", "辛"],
                 zhis=["申", "未", "亥", "卯"], score=64.0, label="身强",
                 xi=["木", "水", "火"], ji=["土", "金"], birth=1980,
                 dy=lambda y: ("戊", "子") if y <= 2030 else (("己", "丑") if y <= 2040 else (("庚", "寅") if y <= 2050 else ("辛", "卯")))),
    "主母": dict(rz="庚", rwx="金", nyz="卯", nmz="未", gans=["丁", "丁", "庚", "壬"],
                zhis=["卯", "未", "午", "午"], score=50.0, label="从弱",
                xi=["木", "水", "火"], ji=["土", "金"], birth=1987,
                dy=lambda y: ("辛", "亥") if y <= 2032 else (("壬", "子") if y <= 2042 else (("癸", "丑") if y <= 2052 else ("甲", "寅")))),
    "少爷": dict(rz="丙", rwx="火", nyz="卯", nmz="巳", gans=["辛", "癸", "丙", "癸"],
                zhis=["卯", "巳", "戌", "巳"], score=55.6, label="中和",
                xi=["金", "土", "水"], ji=["木", "火"], birth=2011,
                dy=lambda y: ("壬", "辰") if y <= 2028 else (("辛", "卯") if y <= 2038 else (("庚", "寅") if y <= 2048 else ("己", "丑")))),
}

SHISHEN_HINT = {
    "正官": "名分/平台/规则", "七杀": "压力/竞争/权力", "正印": "文书/背书/靠山",
    "偏印": "思考/技术/孤独", "正财": "稳定收入/务实", "偏财": "机会财/外部",
    "食神": "表达/产出/享受", "伤官": "创新/锋芒/不服", "比肩": "同辈/自立/竞争",
    "劫财": "争夺/分利/合伙",
}


def level(s: float) -> str:
    if s >= 8.5:
        return "🏆 大吉"
    if s >= 7.0:
        return "✅ 吉"
    if s >= 5.5:
        return "➖ 平"
    if s >= 4.5:
        return "⚠️ 弱"
    return "🔻 低"


def build_section(name: str) -> str:
    c = CONFIG[name]
    # 大运真实起止年（以引擎 JSON 为准，避免与门禁校验冲突）
    dy_range = {}
    try:
        eng = json.load(open(f"/tmp/{name}_engine.json", encoding="utf-8"))
        for d in eng["analysis"]["da_yun"]["list"]:
            dy_range[d["gan_zhi"]] = (d["start_year"], d["end_year"])
    except Exception:
        pass
    rows = []
    for y in range(2026, 2046):
        ec = Solar.fromYmd(y, 6, 1).getLunar().getEightChar()
        yg, yz = ec.getYear()[0], ec.getYear()[1]
        d = c["dy"](y)
        r = analyze_liu_nian_v2(yg, yz, y, c["rz"], c["rwx"], c["nyz"], c["nmz"], d[0], d[1],
                                c["gans"], c["zhis"], c["score"], c["label"], c["xi"], c["ji"],
                                c["birth"], y - c["birth"] + 1)
        km = r.get("key_months", "")
        km = km.replace("重点月份：", "").replace("重点月份:", "")
        rows.append((y, yg + yz, d[0] + d[1], r["shi_shen"], r["comprehensive_score"], km))

    L = ["\n\n---\n", "## §24 未来二十年流年详析（2026–2045）\n",
         "> **口径：** `liu_nian_v2.analyze_liu_nian_v2()` 逐年实跑；"
         "十神按日主取，评分 = 流年与原局/大运的合能净分（0–10）。\n",
         "> **读法：** ≥8.5 大吉｜7.0–8.4 吉｜5.5–6.9 平｜4.5–5.4 弱｜<4.5 低。"
         "分数是「能量匹配度」，不是「事件吉凶」——高分年也会有事，只是扛得住。\n"]

    # 大运分段
    L.append("### 24.1 大运分段总览\n")
    L.append("| 大运 | 起始年 | 十神 | 评分 | 一句话判读 |")
    L.append("|:---|:---:|:---|:---:|:---|")
    dygroups = {}
    for y in range(2026, 2046):
        dygroups.setdefault(c["dy"](y), []).append(y)
    for d, ys in dygroups.items():
        ss = get_shi_shen_for_gan(d[0], c["rz"])
        hint = SHISHEN_HINT.get(ss, "")
        avg = sum(x[4] for x in rows if x[2] == d[0] + d[1]) / max(1, len(ys))
        y0, y1 = dy_range.get(d[0] + d[1], (ys[0], ys[-1]))
        L.append(f"| **{d[0]}{d[1]}** | {y0}–{y1} | {ss}（{hint}） | "
                 f"均 {avg:.1f} | {'顺' if avg >= 7 else ('平' if avg >= 5.5 else '逆')} |")
    L.append("")

    # 逐年表
    L.append("### 24.2 逐年详表（2026–2045）\n")
    L.append("| 年份 | 干支 | 大运 | 十神 | 评分 | 等级 | 关键月 | 主要读法 |")
    L.append("|:---:|:---:|:---:|:---|:---:|:---:|:---|:---|")
    for y, gz, dy, ss, sc, km in rows:
        hint = SHISHEN_HINT.get(ss, "")
        L.append(f"| **{y}** | {gz} | {dy} | {ss}（{hint}） | **{sc:.1f}** | {level(sc)} | {km or '—'} | "
                 f"{'顺势推进' if sc >= 7 else ('守中求进' if sc >= 5.5 else '收敛蓄力')} |")
    L.append("")

    # 窗口小结
    high = [r for r in rows if r[4] >= 7.0]
    low = [r for r in rows if r[4] < 5.5]
    L.append("### 24.3 窗口小结\n")
    if high:
        L.append(f"- **优势年（≥7.0，共 {len(high)} 年）：** "
                 + "、".join(f"{r[0]}({r[4]:.1f})" for r in high))
    if low:
        L.append(f"- **弱势年（<5.5，共 {len(low)} 年）：** "
                 + "、".join(f"{r[0]}({r[4]:.1f})" for r in low))
    L.append("")

    # 行动建议
    L.append("### 24.4 行动建议（按窗口）\n")
    L.append("| 时段 | 策略 |")
    L.append("|:---|:---|")
    if high:
        y0 = high[0][0]
        L.append(f"| **{y0} 起的高分年** | 主动出击：谈条件、换平台、投项目、扩规模 |")
    if low:
        y1 = low[0][0]
        L.append(f"| **{y1} 起的低分年** | 收敛蓄力：不裸辞、不重投、不担保，守住现金流与技术资产 |")
    L.append("| 每年重点月 | 表中「关键月」为引擎给出的应期窗口，重要决策尽量落在这些月份 |")
    L.append("")
    return "\n".join(L)


def main():
    if len(sys.argv) < 3:
        print("用法: python3 scripts/append_liunian_2026_2045.py <姓名> <报告路径>")
        sys.exit(1)
    name, path = sys.argv[1], sys.argv[2]
    if name not in CONFIG:
        print(f"未配置：{name}（可选：{'/'.join(CONFIG)}）")
        sys.exit(1)
    with open(path, "a", encoding="utf-8") as f:
        f.write(build_section(name))
    print(f"✅ 已追加 §24 → {path}")


if __name__ == "__main__":
    main()
