#!/usr/bin/env python3
"""金鉴真人·家族五人报告统一生成脚本（2026-08-26体系化修复后固化）

用法:
  python3 gen_family_reports.py [output_dir]
  默认输出 /tmp/{姓名}_engine.json / {姓名}_ds.json / {姓名}_report.md

流程: pipeline_v5引擎(确定性) → convert_v5_to_ds(ds数据源) → generate_deep_report(21§报告)
⚠️ 调用前必须: touch /tmp/.bazi_verified（pre_tool_call物理约束）
"""
import json
import os
import sys
import subprocess

ENGINE_DIR = "/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine"
SCRIPTS_DIR = "/root/.hermes/profiles/jinjian-zhenren/scripts"
ONLY = [a for a in sys.argv[1:] if not a.startswith("/") and not a.isdigit()] or None
OUT_DIR = "/tmp"

# 家族五人出生档案（四柱已由paipan模块确认，qi_yun_days为节气距离天数）
# 性别必须显式传入（旧bug：gender缺失→报告全默认"女"）
FAMILY = [
    {"name": "家主", "gender": "男", "birth_year": 1980, "birth_month": 8, "birth_day": 6, "hour": 6,
     "gz": ("庚", "申", "癸", "未", "辛", "亥", "辛", "卯"), "qi_yun_days": 1.0},
    {"name": "主母", "gender": "女", "birth_year": 1987, "birth_month": 7, "birth_day": 20, "hour": 12,
     "gz": ("丁", "卯", "丁", "未", "庚", "午", "壬", "午"), "qi_yun_days": 18},
    {"name": "少爷", "gender": "男", "birth_year": 2011, "birth_month": 5, "birth_day": 31, "hour": 10,
     "gz": ("辛", "卯", "癸", "巳", "丙", "戌", "癸", "巳"), "qi_yun_days": 25},
    {"name": "七七", "gender": "女", "birth_year": 2017, "birth_month": 7, "birth_day": 7, "hour": 8,
     "gz": ("丁", "酉", "丁", "未", "乙", "未", "庚", "辰"), "qi_yun_days": 31},
    {"name": "左左", "gender": "男", "birth_year": 2019, "birth_month": 4, "birth_day": 23, "hour": 14,
     "gz": ("己", "亥", "戊", "辰", "庚", "寅", "癸", "未"), "qi_yun_days": 18},
]


def run_pipeline_member(m):
    """跑 pipeline_v5 run_pipeline → engine.json"""
    sys.path.insert(0, ENGINE_DIR)
    from pipeline_v5 import run_pipeline
    yg, yz, mg, mz, dg, dz, hg, hz = m["gz"]
    output = run_pipeline(
        m["name"], m["gender"], yg, yz, mg, mz, dg, dz, hg, hz,
        m["birth_year"], m["birth_month"], m["birth_day"], m["qi_yun_days"],
    )
    output["success"] = True
    ep = os.path.join(OUT_DIR, f'{m["name"]}_engine.json')
    with open(ep, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return ep


def convert_to_ds(engine_path, m):
    """convert_v5_to_ds.py → ds.json"""
    ds_path = os.path.join(OUT_DIR, f'{m["name"]}_ds.json')
    subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "convert_v5_to_ds.py"), engine_path, ds_path],
                   check=True)
    return ds_path


def gen_report(engine_path, m):
    """generate_deep_report → report.md"""
    sys.path.insert(0, ENGINE_DIR)
    import generate_deep_report
    d = json.load(open(engine_path))
    rep = generate_deep_report.generate_deep_report(d, name=m["name"], version="1.1")
    rp = os.path.join(OUT_DIR, f'{m["name"]}_report.md')
    with open(rp, "w") as f:
        f.write(rep)
    return rp


if __name__ == "__main__":
    if not os.path.exists("/tmp/.bazi_verified"):
        print("❌ 缺少物理约束标记 /tmp/.bazi_verified，请先 touch /tmp/.bazi_verified")
        sys.exit(1)
    for m in FAMILY:
        if ONLY and m["name"] not in ONLY:
            continue
        ep = run_pipeline_member(m)
        dp = convert_to_ds(ep, m)
        rp = gen_report(ep, m)
        print(f"✅ {m['name']} | {m['gender']} | {rp}")
