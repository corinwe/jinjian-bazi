#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成黄金盘回归基线（P0-1）

用途：把 12 个已核验命例的引擎输出固化为基线，供 regression-golden.py 比对。
注意：本脚本会**覆盖** cases.json 的 expected 字段。
     运行前必须确认引擎是正确的（改引擎后应先跑回归，失败则不得更新基线）。

用法：
    python3 scripts/build_golden_cases.py --write
    python3 scripts/build_golden_cases.py --write --only 主母
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
os.environ.setdefault("BAZI_TRACE", "0")

from lunar_python import Solar  # noqa: E402
from pipeline_v5 import run_pipeline  # noqa: E402

GOLDEN = ROOT / "engine" / "tests" / "golden" / "cases.json"

# 12 个已核验命例（四柱均已与 KB 报告 / lunar_python 双向核对）
CASES = [
    {"id": "01", "name": "家主·魏启令", "gender": "男", "y": 1980, "m": 8, "d": 6, "hh": 5, "mm": 30, "sizhu": "庚申 癸未 辛亥 辛卯", "note": "身强64.0·偏财格·财31.2（报告已核）"},
    {"id": "02", "name": "主母·成", "gender": "女", "y": 1987, "m": 7, "d": 20, "hh": 12, "mm": 0, "sizhu": "丁卯 丁未 庚午 壬午", "note": "从弱50.0·从官杀·财16.0（2026-10-30 生日确认）"},
    {"id": "03", "name": "少爷·子源", "gender": "男", "y": 2011, "m": 5, "d": 31, "hh": 10, "mm": 0, "sizhu": "辛卯 癸巳 丙戌 癸巳", "note": "中和55.6·建禄格·财30.8（报告已核）"},
    {"id": "04", "name": "潘永禛", "gender": "男", "y": 2026, "m": 9, "d": 24, "hh": 9, "mm": 5, "sizhu": "丙午 丁酉 辛丑 癸巳", "note": "身弱27.2·建禄格（人物档案61）"},
    {"id": "05", "name": "凤", "gender": "女", "y": 1978, "m": 12, "d": 13, "hh": 21, "mm": 0, "sizhu": "戊午 甲子 己酉 乙亥", "note": "三引擎一致案例"},
    {"id": "06", "name": "七七", "gender": "女", "y": 2017, "m": 7, "d": 7, "hh": 7, "mm": 7, "sizhu": "丁酉 丁未 乙未 庚辰", "note": "紫微门禁金标准盘之一"},
    {"id": "07", "name": "杨昌玉", "gender": "女", "y": 2003, "m": 1, "d": 8, "hh": 14, "mm": 0, "sizhu": "壬午 癸丑 辛巳 乙未", "note": "岁首口径修正案例"},
    {"id": "08", "name": "左左", "gender": "男", "y": 2019, "m": 4, "d": 23, "hh": 14, "mm": 30, "sizhu": "己亥 戊辰 庚寅 癸未", "note": "v3.0报告性别=男·大运丁卯2025起（乾造报告内文误写『女』，以乾造/男为准）"},
    {"id": "09", "name": "梦", "gender": "女", "y": 2007, "m": 7, "d": 27, "hh": 6, "mm": 0, "sizhu": "丁亥 丁未 壬戌 癸卯", "note": "卯时"},
    {"id": "10", "name": "仔仔", "gender": "男", "y": 2019, "m": 10, "d": 23, "hh": 2, "mm": 0, "sizhu": "己亥 甲戌 癸巳 癸丑", "note": "丑时（档案19）"},
    {"id": "11", "name": "小静", "gender": "女", "y": 2007, "m": 4, "d": 13, "hh": 8, "mm": 0, "sizhu": "丁亥 甲辰 丁丑 甲辰", "note": "农历月≠节气月口径归一化案例"},
    {"id": "12", "name": "刘静", "gender": "女", "y": 2006, "m": 4, "d": 1, "hh": 5, "mm": 25, "sizhu": "丙戌 辛卯 庚申 己卯", "note": "人物档案60·卯时"},
]


def sizhu_from_birth(y, m, d, hh, mm) -> str:
    ec = Solar.fromYmdHms(y, m, d, hh, mm, 0).getLunar().getEightChar()
    return f"{ec.getYear()} {ec.getMonth()} {ec.getDay()} {ec.getTime()}"


def analyze(c: dict) -> dict:
    y, m, d, hh, mm = c["y"], c["m"], c["d"], c["hh"], c["mm"]
    g = [*c["sizhu"].replace(" ", "")]
    out = run_pipeline(
        c["name"], c["gender"],
        g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7],
        birth_year=y, birth_month=m, birth_day=d, birth_hour=hh, birth_minute=mm,
    )
    a = out["analysis"]
    return {
        "shen_qiang_ruo": {"score": a["shen_qiang_ruo"]["score"], "label": a["shen_qiang_ruo"]["label"]},
        "ge_ju": a["ge_ju"]["main"],
        "ge_ju_detail": a["ge_ju"].get("detail", ""),
        "xi": a["xi_yong_shen"]["xi"],
        "ji": a["xi_yong_shen"]["ji"],
        "tiao_hou": a["xi_yong_shen"].get("tiao_hou", []),
        "cai_xing": {"total": a["cai_xing"]["total"], "level": a["cai_xing"].get("wealth_level", "")},
        "da_yun": [{"gz": d0.get("gan_zhi"), "start": d0.get("start_year"), "score": d0.get("score")}
                   for d0 in a["da_yun"].get("list", [])[:6]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="写入 cases.json")
    ap.add_argument("--only", default=None, help="只处理名字包含该关键字的案例")
    args = ap.parse_args()

    cases = []
    mismatched = []
    for c in CASES:
        if args.only and args.only not in c["name"]:
            continue
        computed = sizhu_from_birth(c["y"], c["m"], c["d"], c["hh"], c["mm"])
        if computed != c["sizhu"]:
            mismatched.append((c["name"], computed, c["sizhu"]))
            print(f"❌ {c['name']} 四柱不一致: 计算={computed} KB={c['sizhu']}")
            continue
        exp = analyze(c)
        cases.append({
            "id": c["id"], "name": c["name"], "gender": c["gender"],
            "birth": {"y": c["y"], "m": c["m"], "d": c["d"], "hh": c["hh"], "mm": c["mm"]},
            "sizhu": c["sizhu"], "note": c["note"], "expected": exp,
        })
        print(f"✅ {c['id']} {c['name']:<8} {c['sizhu']} | 身强弱 {exp['shen_qiang_ruo']['score']:>5} {exp['shen_qiang_ruo']['label']:<4} | {exp['ge_ju']:<6} | 财 {exp['cai_xing']['total']:>5} {exp['cai_xing']['level']}")

    if mismatched:
        print(f"\n⛔ {len(mismatched)} 个案例四柱不一致，拒绝写基线")
        return 1

    if args.write:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "meta": {
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "engine": "pipeline_v5.run_pipeline",
                "count": len(cases),
                "note": "四柱均由 lunar_python 双向核验；expected 为引擎基线，改引擎后回归失败不得直接覆盖",
            },
            "cases": cases,
        }
        GOLDEN.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n✅ 已写入 {GOLDEN}（{len(cases)} 例）")
    else:
        print(f"\n（未写入；加 --write 落盘，当前 {len(cases)} 例）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
