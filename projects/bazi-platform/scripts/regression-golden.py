#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""黄金盘回归（P0-1）— 改引擎/改规则后必跑

比对项（12 个已核验命例）：
  1. 四柱（lunar_python 由出生时间反推，验排盘层）
  2. 身强弱 分数 + 等级
  3. 格局（main + detail）
  4. 喜用 / 忌神 / 调候
  5. 财星 分数 + 等级
  6. 大运 前 6 步（干支 + 起始年 + 评分）

退出码：0=全过；1=有失败（禁止提交引擎改动）

用法：
    python3 scripts/regression-golden.py
    python3 scripts/regression-golden.py --verbose
    python3 scripts/regression-golden.py --only 主母
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
os.environ.setdefault("BAZI_TRACE", "0")  # 回归不写轨迹，保持 runs/ 干净

from lunar_python import Solar  # noqa: E402
from pipeline_v5 import run_pipeline  # noqa: E402

CASES_PATH = ROOT / "engine" / "tests" / "golden" / "cases.json"
EPS = 0.011


def sizhu_from_birth(b: dict) -> str:
    ec = Solar.fromYmdHms(b["y"], b["m"], b["d"], b["hh"], b["mm"], 0).getLunar().getEightChar()
    return f"{ec.getYear()} {ec.getMonth()} {ec.getDay()} {ec.getTime()}"


def analyze(c: dict) -> dict:
    b = c["birth"]
    g = list(c["sizhu"].replace(" ", ""))
    out = run_pipeline(
        c["name"], c["gender"],
        g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7],
        birth_year=b["y"], birth_month=b["m"], birth_day=b["d"],
        birth_hour=b["hh"], birth_minute=b["mm"],
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
        "da_yun": [{"gz": d.get("gan_zhi"), "start": d.get("start_year"), "score": d.get("score")}
                   for d in a["da_yun"].get("list", [])[:6]],
    }


def diff(exp: dict, got: dict) -> list[str]:
    errs = []

    def num(path, e, g):
        try:
            if abs(float(e) - float(g)) > EPS:
                errs.append(f"{path}: 期望 {e} 实际 {g}")
        except (TypeError, ValueError):
            if e != g:
                errs.append(f"{path}: 期望 {e} 实际 {g}")

    num("身强弱.score", exp["shen_qiang_ruo"]["score"], got["shen_qiang_ruo"]["score"])
    for k in ("label",):
        if exp["shen_qiang_ruo"][k] != got["shen_qiang_ruo"][k]:
            errs.append(f"身强弱.{k}: 期望 {exp['shen_qiang_ruo'][k]} 实际 {got['shen_qiang_ruo'][k]}")

    for k in ("ge_ju", "ge_ju_detail"):
        if exp[k] != got[k]:
            errs.append(f"{k}: 期望 {exp[k]} 实际 {got[k]}")

    for k in ("xi", "ji", "tiao_hou"):
        if list(exp[k]) != list(got[k]):
            errs.append(f"{k}: 期望 {exp[k]} 实际 {got[k]}")

    num("财星.total", exp["cai_xing"]["total"], got["cai_xing"]["total"])
    if exp["cai_xing"]["level"] != got["cai_xing"]["level"]:
        errs.append(f"财星.level: 期望 {exp['cai_xing']['level']} 实际 {got['cai_xing']['level']}")

    ed, gd = exp["da_yun"], got["da_yun"]
    if len(ed) != len(gd):
        errs.append(f"大运步数: 期望 {len(ed)} 实际 {len(gd)}")
    for i, (e, g) in enumerate(zip(ed, gd), 1):
        if e["gz"] != g["gz"]:
            errs.append(f"大运{i}.干支: 期望 {e['gz']} 实际 {g['gz']}")
        if e["start"] != g["start"]:
            errs.append(f"大运{i}.起始年: 期望 {e['start']} 实际 {g['start']}")
        num(f"大运{i}.评分", e["score"], g["score"])
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--json", action="store_true", help="输出机器可读结果")
    args = ap.parse_args()

    if not CASES_PATH.exists():
        print(f"⛔ 缺少黄金基线: {CASES_PATH}\n   先运行: python3 scripts/build_golden_cases.py --write")
        return 1

    payload = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = payload["cases"]
    if args.only:
        cases = [c for c in cases if args.only in c["name"]]

    results, failed = [], 0
    for c in cases:
        computed = sizhu_from_birth(c["birth"])
        sizhu_ok = computed == c["sizhu"]
        try:
            got = analyze(c)
            errs = [] if not sizhu_ok else diff(c["expected"], got)
            if not sizhu_ok:
                errs = [f"四柱: 期望 {c['sizhu']} 实际 {computed}"]
        except Exception as e:  # noqa: BLE001
            got, errs = None, [f"异常: {type(e).__name__}: {e}"]

        ok = not errs
        failed += 0 if ok else 1
        results.append({"id": c["id"], "name": c["name"], "ok": ok, "errors": errs})
        mark = "✅" if ok else "❌"
        print(f"{mark} {c['id']} {c['name']:<8} {c['sizhu']}")
        if not ok:
            for e in errs:
                print(f"     • {e}")
        elif args.verbose:
            print(f"     身强弱 {c['expected']['shen_qiang_ruo']['score']} {c['expected']['shen_qiang_ruo']['label']} | {c['expected']['ge_ju']} | 财 {c['expected']['cai_xing']['total']} {c['expected']['cai_xing']['level']}")

    print()
    print(f"通过 {len(cases) - failed} / {len(cases)}")
    if args.json:
        print(json.dumps({"total": len(cases), "failed": failed, "results": results}, ensure_ascii=False))
    if failed:
        print("⛔ 黄金盘回归失败：禁止提交引擎改动")
        return 1
    print("✅ 黄金盘回归全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
