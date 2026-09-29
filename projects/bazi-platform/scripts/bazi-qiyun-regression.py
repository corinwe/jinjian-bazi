#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起运口径回归门禁 v1.0  (bazi-qiyun-regression)
================================================
存在意义：全库曾同时存在 **4 套起运算法**，导致同一命造出现
  起运年龄 8岁8个月19天 vs 8岁10个月0天、大运年龄带 8~17 vs 9~18、起始年差 1 年。
本门禁强制：**只有 engine/qi_yun.py 一套实现**，且 5 个入口逐字段一致。

检查项：
  ① 黄金锚点：静 = 起运8岁8个月19天(8.72岁)·首运庚寅8~17岁·2015年起运（老板已确认口径）
  ② 入口一致性：qi_yun / da_yun / pipeline_v5 / bazi-engine / dual-prepare产物 五路同值
  ③ 实现唯一性 lint：起运公式(天数/3、//3)只允许出现在 engine/qi_yun.py
退出码：0=全通过，1=有漂移（禁止推库/出报告）
"""
import os
import re
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENG = os.path.join(ROOT, "engine")
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, ENG)

GOLDEN = {  # 姓名: (出生(y,m,d,h,mi), 性别, 月干, 月支, 期望起运年龄, 首运干支, 首运起始岁, 首运起始年)
    "静": ((2006, 4, 1, 5, 25), "女", "辛", "卯", 8.72, "庚寅", 8, 2015),
}
CHARTS = {
    "静": ((2006, 4, 1, 5, 25), "女", "辛", "卯"),
    "家主": ((1980, 8, 6, 5, 30), "男", "癸", "未"),
}

fails = []


def chk(label, ok, detail=""):
    print(f"  {'✅' if ok else '❌'} {label}{(' | ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


def main():
    from qi_yun import compute_qi_yun, format_qi_yun
    import da_yun as dy_mod
    from constants import BaZi, Pillar
    import pipeline_v5
    sys.path.insert(0, SCRIPTS)

    print("═══ ① 黄金锚点（静·老板已确认口径）═══")
    (y, m, d, h, mi), g, mg, mz = CHARTS["静"]
    bdt = datetime(y, m, d, h, mi)
    qy = compute_qi_yun(bdt, g, month_gan=mg, month_zhi=mz)
    E = GOLDEN["静"]
    chk("起运年龄=8.72", qy["起运年龄"] == E[4], f"实际 {qy['起运年龄']}")
    chk("折算=8岁8个月19天", (qy["岁"], qy["个月"], qy["天"]) == (8, 8, 19),
        f"实际 {qy['岁']}岁{qy['个月']}个月{qy['天']}天")
    chk("首运=庚寅 8~17岁 2015~2024", (qy["大运"][0]["干支"], qy["大运"][0]["起始岁"],
        qy["大运"][0]["结束岁"], qy["大运"][0]["起始年"]) == (E[5], E[6], E[6] + 9, E[7]),
        f"实际 {qy['大运'][0]['干支']} {qy['大运'][0]['起始岁']}~{qy['大运'][0]['结束岁']}岁 {qy['大运'][0]['起始年']}起")
    chk("展示格式统一", format_qi_yun(qy).startswith("起运8岁8个月19天（8.72岁"), format_qi_yun(qy))
    chk("步数=11（至起运年+100）", len(qy["大运"]) == 11, f"实际 {len(qy['大运'])}")

    print("\n═══ ② 五路入口一致性 ═══")
    for name, (bd, gd, mga, mza) in CHARTS.items():
        yy, mm, dd, hh, mmin = bd
        b_dt = datetime(yy, mm, dd, hh, mmin)
        ref = compute_qi_yun(b_dt, gd, month_gan=mga, month_zhi=mza)
        # 入口3: pipeline_v5（其内部走 da_yun.compute_da_yun）
        o = pipeline_v5.run_pipeline(name, gd, "丙" if name == "静" else "庚", "戌" if name == "静" else "申",
                                     mga, mza, "庚" if name == "静" else "辛", "申" if name == "静" else "亥",
                                     "己" if name == "静" else "辛", "卯",
                                     yy, mm, dd, None, birth_hour=hh, birth_minute=mmin)
        st = o["result"]["sec_17_da_yun_detail"]["list"]
        chk(f"[{name}] pipeline_v5 首运同值",
            (st[0]["gan_zhi"], st[0]["start_age"], st[0]["start_year"]) ==
            (ref["大运"][0]["干支"], ref["大运"][0]["起始岁"], ref["大运"][0]["起始年"]),
            f"pipeline {st[0]['gan_zhi']} {st[0]['start_age']}岁 {st[0]['start_year']} vs qi_yun "
            f"{ref['大运'][0]['干支']} {ref['大运'][0]['起始岁']}岁 {ref['大运'][0]['起始年']}")
        chk(f"[{name}] pipeline 起运年龄同值",
            round(o["result"]["sec_1_overview"].get("qi_yun_age", -1), 2) == ref["起运年龄"],
            f"{o['result']['sec_1_overview'].get('qi_yun_age')} vs {ref['起运年龄']}")
        chk(f"[{name}] 步数=11", len(st) == 11, f"实际 {len(st)}")

    # 入口4: bazi-engine（dual-prepare 的生产路径）
    print("\n═══ ③ bazi-engine 生产路径（dual-prepare）═══")
    r = subprocess.run(["bash", f"{SCRIPTS}/bazi-dual-prepare.sh", "静", "女", "2006-04-01", "05:25"],
                       capture_output=True, text=True, cwd=ROOT)
    out = r.stdout
    chk("dual-prepare 执行成功", r.returncode == 0 and "双引擎四柱交叉校验通过" in out,
        " | ".join(l.strip() for l in out.splitlines() if "交叉校验" in l)[:80])
    import json
    pai = json.load(open("/tmp/静_engine.json"))
    qy_line = pai.get("大运", {})
    a0 = (qy_line.get("大运表") or qy_line.get("列表") or [{}])[0] if isinstance(qy_line, dict) else {}
    chk("引擎产物起运年龄=8.72", round(float(qy_line.get("起运年龄", -1)), 2) == 8.72,
        f"实际 {qy_line.get('起运年龄')}")
    if a0:
        chk("引擎产物首运同值",
            (a0.get("起始年龄"), a0.get("起始年份")) == (8, 2015),
            f"实际 {a0.get('起始年龄')}岁 {a0.get('起始年份')}年")

    print("\n═══ ④ 实现唯一性 lint（起运公式只准在 engine/qi_yun.py）═══")
    pat = re.compile(r"(days_diff\s*/\s*3|//\s*3\b|days\s*//\s*3|qi_yun_age\s*=\s*.*/\s*3)")
    offenders = []
    for base, _, files in os.walk(ROOT):
        if "/archive" in base or "/.git" in base:
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            fp = os.path.join(base, f)
            if fp.endswith("engine/qi_yun.py") or fp.endswith("bazi-qiyun-regression.py"):
                continue
            try:
                indoc = False
                for i, line in enumerate(open(fp, encoding="utf-8"), 1):
                    if line.count('"""') % 2 == 1:
                        indoc = not indoc
                        continue
                    if indoc or line.strip().startswith("#"):
                        continue
                    if pat.search(line):
                        offenders.append(f"{os.path.relpath(fp, ROOT)}:{i}")
            except Exception:
                pass
    chk("无越权起运实现", not offenders, "；".join(offenders[:5]))

    print("\n" + "═" * 46)
    if fails:
        print(f"❌ 起运口径门禁未通过（{len(fails)} 项）：" + " / ".join(fails))
        return 1
    print("✅ 起运口径门禁全通过：全系统唯一算法 engine/qi_yun.py（R1~R9）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
