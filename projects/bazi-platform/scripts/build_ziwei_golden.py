#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成紫微斗数黄金用例（回归锚点）。

用法：
    python3 scripts/build_ziwei_golden.py

产物：
    engine/tests/golden/ziwei_cases.json

口径：
    · 用例值由当前引擎实跑产出，作为「行为冻结」锚点；
    · 家族四盘（家主/主母/少爷/云森）为已人工校验盘；
    · 边界用例覆盖：立春前后、闰月、晚子时。
"""
import json
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, "engine"))
import ziwei_engine  # noqa: E402

CASES = [
    # (id, 姓名, 性别, 日期, 时间, 地点, 备注)
    ("jia_zhu", "魏启令", "男", "1980-08-06", "06:00", "上海", "家主·卯时"),
    ("zhu_mu", "主母", "女", "1987-07-20", "12:00", "上海", "主母·午时（农历六月廿五）"),
    ("shao_ye", "少爷", "男", "2011-05-31", "09:30", "上海", "少爷·巳时（辛卯癸巳丙戌癸巳）"),
    ("yun_sen", "云森智达", "男", "2026-10-28", "10:31", "上海", "公司盘·巳时"),
    ("lichun_before", "立春前", "男", "2026-02-03", "23:30", "北京", "立春前·年柱应为乙巳"),
    ("lichun_after", "立春后", "男", "2026-02-04", "10:00", "北京", "立春后·年柱应为丙午"),
    ("leap_month", "闰月盘", "女", "2025-07-25", "12:00", "上海", "2025 闰六月"),
    ("late_zishi", "晚子时", "男", "2026-03-15", "23:30", "上海", "晚子时口径"),
]

OUT = os.path.join(PROJ, "engine", "tests", "golden", "ziwei_cases.json")


def snapshot(cid, name, gender, date, tm, loc, note):
    zw = ziwei_engine.build(name, gender, date, tm, loc)
    z = zw["紫微"]
    palaces = {}
    for p in z["十二宫"]:
        palaces[p["宫位"]] = {
            "干支": p["干支"],
            "主星": [s["名"] for s in p["主星"]],
            "辅星": [s["名"] for s in p["辅星"]],
        }
    b = zw.get("四柱") or zw.get("bazi") or zw.get("八字同源摘要", {}).get("四柱")
    if isinstance(b, dict):
        b = " ".join(b[k]["gan"] + b[k]["zhi"] for k in ("year", "month", "day", "time"))
    return {
        "id": cid,
        "note": note,
        "input": {"name": name, "gender": gender, "date": date, "time": tm, "location": loc},
        "expected": {
            "bazi": b,
            "五行局": z.get("五行局"),
            "命主": z.get("命主"),
            "身主": z.get("身主"),
            "生年四化": z.get("生年四化"),
            "时辰": z.get("时辰"),
            "命宫干支": palaces.get("命宫", {}).get("干支"),
            "命宫主星": palaces.get("命宫", {}).get("主星"),
            "十二宫主星": {k: v["主星"] for k, v in palaces.items()},
        },
    }


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cases = []
    for c in CASES:
        try:
            cases.append(snapshot(*c))
            print(f"✅ {c[0]} {c[1]} → {cases[-1]['expected']['bazi']}")
        except Exception as e:
            print(f"❌ {c[0]} 失败: {e}")
    payload = {
        "version": 1,
        "generated_by": "scripts/build_ziwei_golden.py",
        "engine": ziwei_engine.ENGINE_VERSION,
        "cases": cases,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"\n写入 {OUT}｜{len(cases)} 条")


if __name__ == "__main__":
    main()
