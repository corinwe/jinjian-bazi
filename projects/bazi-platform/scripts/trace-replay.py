#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轨迹回放（P0-2）

用法：
    python3 scripts/trace-replay.py                # 最近一次
    python3 scripts/trace-replay.py 主母_20261030_120000
    python3 scripts/trace-replay.py --list         # 列出所有轨迹
"""
import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RUNS = PROJECT / "runs"


def summaries(rec: dict) -> str:
    step = rec.get("step", "")
    r = rec.get("result")
    if step == "paipan" and isinstance(r, dict):
        return f"四柱 {r.get('四柱')}"
    if step == "shen_qiang_ruo" and isinstance(r, dict):
        return f"{r.get('score')} 分 · {r.get('label')}"
    if step == "ge_ju" and isinstance(r, dict):
        return f"{r.get('main')} / {r.get('detail')}"
    if step == "xi_yong_shen" and isinstance(r, dict):
        return f"喜 {r.get('xi')} 忌 {r.get('ji')} 调候 {r.get('tiao_hou')}"
    if step == "cai_xing" and isinstance(r, dict):
        return f"{r.get('total')} 分 · {r.get('level')}"
    if step == "da_yun" and isinstance(r, list):
        return " → ".join(f"{d.get('gz')}({d.get('start')},{d.get('score')})" for d in r[:4])
    if step == "report_text" and isinstance(r, dict):
        return f"{r.get('chars')} 字符"
    return json.dumps(r, ensure_ascii=False)[:70] if r is not None else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id", nargs="?", default=None)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list or not RUNS.exists():
        if not RUNS.exists():
            print("（暂无轨迹目录）")
            return 0
        for p in sorted(RUNS.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
            if (p / "trace.jsonl").exists():
                n = sum(1 for _ in open(p / "trace.jsonl", encoding="utf-8"))
                print(f"{p.name:<40} {n} 条")
        return 0

    run_id = args.run_id
    if not run_id:
        cands = [p for p in RUNS.iterdir() if (p / "trace.jsonl").exists()] if RUNS.exists() else []
        if not cands:
            print("⛔ 没有可用轨迹，先跑一次排盘/报告生成")
            return 1
        run_id = max(cands, key=lambda p: p.stat().st_mtime).name

    path = RUNS / run_id / "trace.jsonl"
    if not path.exists():
        print(f"⛔ 轨迹不存在: {path}")
        return 1

    recs = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    start = next((r for r in recs if r.get("event") == "start"), {})
    print(f"═══ 轨迹回放: {run_id} ═══")
    print(f"开始: {start.get('ts')} | 元数据: {start.get('meta')}")
    print("─" * 88)
    steps = 0
    for r in recs:
        if r.get("event") == "step":
            steps += 1
            print(f"{r['seq']:>2} {r.get('ts','')[11:]} +{r.get('elapsed_ms',0):>6}ms  {r.get('step'):<15} {summaries(r)}")
        elif r.get("event") == "end":
            print("─" * 88)
            print(f"结束: {r.get('ts')} | 总耗时 {r.get('elapsed_ms')}ms | 决策点 {steps} 个 | 摘要 {r.get('summary')}")
    if steps < 5:
        print(f"⚠️ 决策点仅 {steps} 个（要求 ≥5）")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
