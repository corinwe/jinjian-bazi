#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单命造全流水线：双引擎数据源 → pipeline_v5 → 21§报告 → 机制链 → 双引擎后处理
用法: python3 build_report.py <姓名> <性别> <YYYY-MM-DD> <HH:MM> [出生地]
产出: /tmp/{姓名}_engine.json / _ds.json / _ziwei.json / _report.md / _chain.txt / _报告_双引擎.md

🚨 2026-09-29 口径：起运一律用【真太阳时】（含均时差 EoT）。
   1分钟真太阳时差 = 2小时命理时间，钟表时会算错"时"位。
"""
import json, os, subprocess, sys
from datetime import datetime

PROJ = "/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform"
SCRIPTS = "/root/.hermes/profiles/jinjian-zhenren/scripts"
ENG = f"{PROJ}/engine"
sys.path.insert(0, ENG)

name, gender, date, hhmm = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
loc = sys.argv[5] if len(sys.argv) > 5 else ""

print(f"═══ {name} {gender} {date} {hhmm} {loc or '(未指定出生地→经度按120E)'} ═══")
r = subprocess.run(["bash", f"{PROJ}/scripts/bazi-dual-prepare.sh", name, gender, date, hhmm] + ([loc] if loc else []),
                   capture_output=True, text=True)
print("\n".join(l for l in r.stdout.splitlines() if any(k in l for k in ("✅", "紫微:", "🚨", "八字:")))[-600:])
if r.returncode != 0:
    print("❌ dual-prepare 失败:", r.stderr[-600:]); sys.exit(1)

pai = json.load(open(f"/tmp/{name}_engine.json"))
gz, qy = pai["四柱"], pai["大运"]["起运年龄"]
y, m, d = [int(x) for x in date.split("-")]

# ── 真太阳时（含均时差）：起运唯一口径 ──
from jieqi import true_solar_time
clk = datetime(y, m, d, int(hhmm.split(":")[0]), int(hhmm.split(":")[1]))
true_dt = None
raw = pai.get("solar_dt")
if raw:
    try:
        true_dt = datetime.fromisoformat(str(raw)[:19])
    except Exception:
        true_dt = None
if true_dt is None:
    true_dt, _, _ = true_solar_time(clk, None)
print(f"   [真太阳时] 钟表 {hhmm} → {true_dt.strftime('%H:%M')}（含均时差 EoT）")

from pipeline_v5 import run_pipeline
out = run_pipeline(name, gender, gz["年柱"][0], gz["年柱"][1], gz["月柱"][0], gz["月柱"][1],
                   gz["日柱"][0], gz["日柱"][1], gz["时柱"][0], gz["时柱"][1], y, m, d, qy * 3,
                   birth_hour=true_dt.hour, birth_minute=true_dt.minute)
out["success"] = True
json.dump(out, open(f"/tmp/{name}_engine.json", "w"), ensure_ascii=False, indent=2)

subprocess.run([sys.executable, f"{SCRIPTS}/convert_v5_to_ds.py",
                f"/tmp/{name}_engine.json", f"/tmp/{name}_ds.json"], check=True)
import generate_deep_report
rep = generate_deep_report.generate_deep_report(json.load(open(f"/tmp/{name}_engine.json")), name=name, version="1.1")
open(f"/tmp/{name}_report.md", "w").write(rep)
# 🚨 顺序铁律（2026-09-29）：postprocess 会重写 /tmp/{name}_engine.json，
#   因此「机制链+SIG」必须在 postprocess 之后生成/对齐，否则报告内嵌SIG与最终JSON不一致→门禁拒推。
subprocess.run([sys.executable, f"{PROJ}/scripts/postprocess_dual_reports.py", name], check=True)
subprocess.run([sys.executable, f"{SCRIPTS}/mechanism-chain-generator.py",
                f"/tmp/{name}_engine.json", "--out", f"/tmp/{name}_chain.txt"], check=True)
# SIG 对齐：用最终 JSON 重算并写回报告头
import hashlib, re as _re, importlib.util as _ilu
_spec = _ilu.spec_from_file_location("vps", f"{SCRIPTS}/verify-pipeline-sig.py")
_vps = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_vps)
_sig = _vps.compute_sig(json.load(open(f"/tmp/{name}_engine.json")))
_rp = f"/tmp/{name}_报告_双引擎.md"
_at = open(_rp, encoding="utf-8").read()
_at = _re.sub(r"# PIPELINE-SIG: [0-9a-f]+", f"# PIPELINE-SIG: {_sig}", _at, count=1)
open(_rp, "w", encoding="utf-8").write(_at)
print(f"   [SIG对齐] {_sig[:16]}（在最终JSON上计算）")
print(f"排盘={pai['八字']} | 起运{qy}岁 | 报告{len(rep.splitlines())}行")
