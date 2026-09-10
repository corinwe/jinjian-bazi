#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金鉴真人 · 紫微权重层系数标定器 v1.0（2026-09-10）
=================================================
标定思路（可复核、不臆造）：
  观测标签 = **八字引擎**同一命主、同一维度的分级（sec_8_wealth / sec_9_property /
  sec_10_career / sec_12_marriage / sec_13_children / sec_14_health）。
  → 这是**双引擎一致性标定**：让紫微量化层对同一命主同一维度的打分，
    与八字引擎的定性分级**对齐**（老板双引擎合参铁律的量化落地）。

拟合参数（紫微宫分模型）：
    分 = BASE + a·主星分 + b·双星加成 + c·辅星吉煞分 + d·四化分
  其中「主星分」已含庙旺系数（参数区见 ziwei_weight.MIAO_COEF）。
  目标：最小化 18 个标签（3人×6维）的 RMSE。

输出：
  engine/ziwei_weight_calib.json   标定参数（ziwei_weight.py 自动加载）
  /tmp/紫微权重层标定报告.md        标定前后对比 + 逐标签对照（供老板复核）

用法: python3 scripts/calibrate_ziwei_weight.py
"""
import itertools
import json
import os
import sys

ENG = "/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/engine"
sys.path.insert(0, ENG)
from ziwei_weight import (STAR_SCORE, MIAO_COEF, MIAO_DEFAULT, DOUBLE_SCORE,
                          AUX_SCORE, SIHUA_SCORE, EMPTY_PENALTY)

ZHI = "子丑寅卯辰巳午未申酉戌亥"

# ── 观测标签：八字引擎分级 → 0-100 目标分（映射规则见「依据」列）──────────
#   等级映射（统一口径）：大富/顶尖=90 · 中富/高管=75 · 小富/985/中高层=65 ·
#                        中等/普通本科=55 · 偏弱=42 · 弱=32
LABELS = [
    # (姓名, 维度, 紫微宫位, 目标分, 八字依据(引擎字段))
    ("家主", "财富", "财帛", 75, "sec_8_wealth.wealth_level=中富 (31.2分)"),
    ("家主", "房产", "田宅", 60, "sec_9_property.property_level=中，有能力购房自住"),
    ("家主", "事业", "官禄", 75, "sec_10_career.career_level=高管/管理型"),
    ("家主", "婚姻", "夫妻", 50, "sec_12_marriage.spouse_traits=配偶挑剔·相貌一般"),
    ("家主", "子女", "子女", 85, "sec_13_children.sheng_yu_potential=最强(6-10个基础)"),
    ("家主", "健康", "疾厄", 55, "sec_14_health.constitution=中等"),

    ("主母", "财富", "财帛", 65, "sec_8_wealth.wealth_level=小富 (16.0分)"),
    ("主母", "房产", "田宅", 42, "sec_9_property.property_level=偏弱，需大运配合"),
    ("主母", "事业", "官禄", 65, "sec_10_career.career_level=中高层/专业型"),
    ("主母", "婚姻", "夫妻", 70, "sec_12_marriage.spouse_traits=配偶正直✅"),
    ("主母", "子女", "子女", 70, "sec_13_children.sheng_yu_potential=中强(3-6个基础)"),
    ("主母", "健康", "疾厄", 55, "sec_14_health.constitution=中等"),

    ("少爷", "财富", "财帛", 75, "sec_8_wealth.wealth_level=中富 (30.8分)"),
    ("少爷", "房产", "田宅", 60, "sec_9_property.property_level=中，有能力购房自住"),
    ("少爷", "事业", "官禄", 65, "sec_10_career.career_level=中高层/专业型"),
    ("少爷", "婚姻", "夫妻", 68, "sec_12_marriage.spouse_traits=配偶温和·相貌敦厚"),
    ("少爷", "子女", "子女", 50, "sec_13_children.sheng_yu_potential=偏弱(1-3个基础)"),
    ("少爷", "健康", "疾厄", 55, "sec_14_health.constitution=中等"),
]

# 默认参数（现行版）
DEFAULT_P = {"BASE": 50.0, "a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0}


def _coef(m):
    return MIAO_COEF.get(m or "", MIAO_DEFAULT)


def components(palace: dict) -> dict:
    """返回未加 BASE 的四个分量（主星/双星/辅星/四化）——与 ziwei_weight.palace_score 同源"""
    mains = palace.get("主星") or []
    # 主星部分保留 (性质分, 庙旺系数) 明细 → 便于把「庙旺幅度 k」也纳入标定
    stars = [(STAR_SCORE.get(s.get("名", ""), 5), MIAO_COEF.get(s.get("庙旺") or "", MIAO_DEFAULT))
             for s in mains]
    ds = 0.0
    if len(mains) >= 2:
        k = "".join([x.get("名", "") for x in mains[:2]])
        ds = DOUBLE_SCORE.get(k, DOUBLE_SCORE.get(k[2:] + k[:2], 0))
    aux_s, sh_s = 0.0, 0.0
    for a in palace.get("辅星") or []:
        aux_s += AUX_SCORE.get(a.get("名", ""), 0)
        if a.get("四化"):
            sh_s += SIHUA_SCORE.get(a["四化"], 0)
    for s in mains:
        if s.get("四化"):
            sh_s += SIHUA_SCORE.get(s["四化"], 0)
    if not mains:
        aux_s += EMPTY_PENALTY
    return {"stars": stars, "双星": ds, "辅星": aux_s, "四化": sh_s}


def build_samples():
    out = []
    for name in ("家主", "主母", "少爷"):
        zw = json.load(open(f"/tmp/{name}_ziwei.json", encoding="utf-8"))
        zmap = {p["宫位"]: p for p in zw["紫微"]["十二宫"]}
        for nm, dim, gong, target, src in LABELS:
            if nm != name or gong not in zmap:
                continue
            out.append({"人": name, "维度": dim, "宫": gong, "目标": target,
                        "依据": src, "c": components(zmap[gong])})
    return out


def predict(c, p):
    k = float(p.get("k", 1.0))
    main_s = sum(sc * (1.0 + k * (coef - 1.0)) for sc, coef in c["stars"])
    return max(0.0, min(100.0, p["BASE"] + p["a"] * main_s + p["b"] * c["双星"]
                        + p["c"] * c["辅星"] + p["d"] * c["四化"]))


def rmse(samples, p):
    errs = [(predict(s["c"], p) - s["目标"]) ** 2 for s in samples]
    return (sum(errs) / len(errs)) ** 0.5


def grade_chinese(x, cuts=None):
    hi, lo = (cuts if cuts else (62.0, 48.0))
    return "强" if x >= hi else "弱" if x < lo else "中"


def grade3(target):
    """观测标签 → 强/中/弱（目标分口径：≥68强 / <50弱 / 其余中）"""
    return "强" if target >= 68 else "弱" if target < 50 else "中"


def agree(samples, p, cuts=None):
    ok = sum(1 for s in samples
             if grade_chinese(predict(s["c"], p), cuts) == grade3(s["目标"]))
    return ok, len(samples)


def main():
    samples = build_samples()
    print(f"样本标签数: {len(samples)}（3人×6维）")
    base_r = rmse(samples, DEFAULT_P)
    base_ok, base_n = agree(samples, DEFAULT_P)
    print(f"默认参数: RMSE={base_r:.2f}  方向一致 {base_ok}/{base_n}")

    # 两级网格搜索：先粗后细（目标＝最大化方向一致数，其次最小化 RMSE）
    def search(grids):
        best = None
        for BASE in grids["BASE"]:
            for a in grids["a"]:
                for b in grids["b"]:
                    for c in grids["c"]:
                        for d in grids["d"]:
                            for k in grids["k"]:
                                for thi in grids["th"]:
                                    for tlo in grids["tl"]:
                                        if tlo >= thi:
                                            continue
                                        p = {"BASE": float(BASE), "a": a, "b": b, "c": c,
                                             "d": d, "k": k}
                                        r = rmse(samples, p)
                                        ok, n = agree(samples, p, (thi, tlo))
                                        # 目标：一致数↑ → RMSE↓ → 参数偏移小（正则化，避免过拟合）
                                        reg = abs(a - 1) + abs(c - 1) + abs(d - 1) + abs(k - 1)
                                        key = (-ok, round(r, 3), round(reg, 3))
                                        if best is None or key < best[0]:
                                            best = (key, dict(p, T_hi=thi, T_lo=tlo), r, ok, n)
        return best

    coarse = {"BASE": [46, 48, 50, 52, 54], "a": [0.9, 1.0, 1.1, 1.2, 1.3],
              "b": [0.0, 0.3, 0.6, 1.0], "c": [0.4, 0.6, 0.8, 1.0, 1.2],
              "d": [0.6, 0.8, 1.0, 1.2], "k": [0.6, 0.8, 1.0, 1.2, 1.4],
              "th": [50, 56, 62, 68], "tl": [40, 44, 48, 52]}
    b1 = search(coarse)
    print(f"粗搜: {b1[1]} → 一致 {b1[3]}/{b1[4]}, RMSE={b1[2]:.2f}")

    # 细搜：在粗搜最优邻域加密
    p0 = b1[1]
    fine = {"BASE": [p0["BASE"] - 2, p0["BASE"], p0["BASE"] + 2],
            "a": [round(p0["a"] - 0.1, 2), p0["a"], round(p0["a"] + 0.1, 2)],
            "b": [round(max(0, p0["b"] - 0.2), 2), p0["b"], round(p0["b"] + 0.2, 2)],
            "c": [round(max(0, p0["c"] - 0.1), 2), p0["c"], round(p0["c"] + 0.1, 2)],
            "d": [round(max(0, p0["d"] - 0.1), 2), p0["d"], round(p0["d"] + 0.1, 2)],
            "k": [round(max(0.2, p0["k"] - 0.2), 2), p0["k"], round(p0["k"] + 0.2, 2)],
            "th": [p0["T_hi"] - 3, p0["T_hi"], p0["T_hi"] + 3],
            "tl": [p0["T_lo"] - 3, p0["T_lo"], p0["T_lo"] + 3]}
    fr = search(fine)
    # 细搜若不如粗搜则回退（防止邻域未覆盖最优解时退化）
    best = b1 if (b1[3], -b1[2]) >= (fr[3], -fr[2]) else fr
    _, bp, br, bok, bn = best
    print(f"标定参数: {bp}")
    print(f"标定后: RMSE={br:.2f}  方向一致 {bok}/{bn}")

    # 写参数文件（ziwei_weight.py 自动加载）
    cp = os.path.join(ENG, "ziwei_weight_calib.json")
    with open(cp, "w", encoding="utf-8") as f:
        json.dump({"参数": bp, "标定前RMSE": round(base_r, 3), "标定后RMSE": round(br, 3),
                   "标定前一致": f"{base_ok}/{base_n}", "标定后一致": f"{bok}/{bn}",
                   "样本数": len(samples), "方法": "八字引擎同级维度分级为观测标签·两级网格搜索(先最大化方向一致数再最小RMSE, 含正则项防过拟合)",
                   "分级阈值": {"T_hi": bp.get("T_hi"), "T_lo": bp.get("T_lo")},
                   "注意": "样本仅3人×6维, 属试点标定; 新增可核实事实后需重跑"}, f,
                  ensure_ascii=False, indent=2)
    print(f"✅ 参数已写入 {cp}")

    cuts = (bp.get("T_hi", 62), bp.get("T_lo", 48))
    L = ["# 紫微权重层系数标定报告（2026-09-10）\n",
         "## 一、方法\n",
         "把**八字引擎**在六个维度上的分级，当作紫微量化层的**观测标签**（双引擎一致性标定）：\n",
         "| 维度 | 观测来源（八字引擎字段） | 等级→目标分映射 |",
         "|:---|:---|:---|",
         "| 财富 | sec_8_wealth.wealth_level | 大富90 / 中富75 / 小富65 / 平55 |",
         "| 房产 | sec_9_property.property_level | 强90 / 中60 / 偏弱42 |",
         "| 事业 | sec_10_career.career_level | 高管75 / 中高层65 |",
         "| 婚姻 | sec_12_marriage.spouse_traits | 配偶正直/温和≈68-70 / 挑剔50 |",
         "| 子女 | sec_13_children.sheng_yu_potential | 最强85 / 中强70 / 偏弱50 |",
         "| 健康 | sec_14_health.constitution | 中等55 |",
         "",
         "模型：`分 = BASE + a·主星分(含庙旺幅度k) + b·双星加成 + c·辅星吉煞分 + d·四化分`；",
         "目标：**最大化强/中/弱方向一致数**（同级维度两引擎应同向），并列时最小化 RMSE，另加正则项防过拟合。\n",
         "## 二、结果\n",
         f"- 样本：**{len(samples)} 个标签**（3人×6维）",
         f"- 标定前：RMSE **{base_r:.2f}**，方向一致 **{base_ok}/{base_n}**",
         f"- 标定后：RMSE **{br:.2f}**，方向一致 **{bok}/{bn}**",
         f"- 标定参数：`{json.dumps(bp, ensure_ascii=False)}`",
         f"- 分级阈值：强 ≥ {cuts[0]} ｜ 弱 < {cuts[1]}\n",
         "## 三、逐标签对照（标定前 → 标定后 vs 八字观测）\n",
         "| 人 | 维度 | 宫位 | 八字观测(依据) | 目标 | 观测档 | 标定前 | 标定后 | 一致? |",
         "|:---|:---|:---|:---|:--:|:--:|:--:|:--:|:--:|"]
    for s in sorted(samples, key=lambda x: (x["人"], x["维度"])):
        b1_ = predict(s["c"], DEFAULT_P)
        b2_ = predict(s["c"], bp)
        same = "✅" if grade_chinese(b2_, cuts) == grade3(s["目标"]) else "❌"
        L.append(f"| {s['人']} | {s['维度']} | {s['宫']} | {s['依据']} | {s['目标']} | {grade3(s['目标'])} | "
                 f"{b1_:.1f}({grade_chinese(b1_, cuts)}) | {b2_:.1f}({grade_chinese(b2_, cuts)}) | {same} |")
    L += ["", "## 四、局限（必须说清）\n",
          f"1. 样本仅 **{len(samples)} 个标签**（3人×6维），属**试点标定**；新增可核实事实后必须重跑。",
          "2. 观测标签来自**八字引擎**（不是独立现实数据）→ 本标定保证的是**双引擎口径一致**，",
          "   不等于「已与真实人生校准」。要贴真实，需老板提供可核实的现实标签（职业/房产/婚姻/健康实况）。",
          f"3. 仍有 {(bn-bok)}/{bn} 个标签方向不一致 → 说明某些维度两套体系本来就不同源（如紫微宫位强 vs 八字维度等级），",
          "   这类分歧**不应硬凑**，按老板辩证思维铁律在报告里标注、不静默择一。",
          "4. 学业维度未纳入（紫微侧对应宫位不唯一：命宫/官禄/父母/昌曲皆有关）→ 映射存在歧义，暂不标定。",
          "", f"**参数文件：** `engine/ziwei_weight_calib.json`（ziwei_weight.py 启动自动加载，缺省回落默认值）"]
    open("/tmp/紫微权重层标定报告.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("✅ 标定报告 → /tmp/紫微权重层标定报告.md")
    return bp


if __name__ == "__main__":
    main()
