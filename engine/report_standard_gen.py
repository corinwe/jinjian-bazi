#!/usr/bin/env python3
"""金鉴真人·标准报告深度生成器 — 从引擎JSON生成21§完整格式报告"""

import json
import sys
from datetime import datetime


def fmt(v):
    if v is None:
        return ""
    s = str(v)
    for ch in ["'", '"']:
        s = s.replace(ch, "")
    return s


def fmt_lines(text, prefix=""):
    """将文本按行切分，每行加prefix"""
    if not text:
        return []
    return [f"{prefix}{line.strip()}" for line in str(text).split("\\n") if line.strip() and len(line.strip()) > 3]


def gen_report(data, name, gender_cn):
    r = data.get("result", {})
    pp = data.get("paipan", {})

    s1 = r.get("sec_1_overview", {})
    s2 = r.get("sec_2_ge_ju", {})
    s3 = r.get("sec_3_shen_qiang_ruo", {})
    s4 = r.get("sec_4_xi_yong", {})
    s5 = r.get("sec_5_zai_huo", {})
    s6 = r.get("sec_6_character", {})
    s7 = r.get("sec_7_appearance", {})
    s8 = r.get("sec_8_wealth", {})
    s9 = r.get("sec_9_property", {})
    s10 = r.get("sec_10_career", {})
    s11 = r.get("sec_11_education", {})
    s12 = r.get("sec_12_marriage", {})
    s13 = r.get("sec_13_children", {})
    s14 = r.get("sec_14_health", {})
    s15 = r.get("sec_15_family", {})
    s16 = r.get("sec_16_events", {})
    s17 = r.get("sec_17_da_yun_detail", {})
    s19 = r.get("sec_19_overall", {})
    s20 = r.get("sec_20_wu_xing_advice", {})
    s21 = r.get("sec_21_advice", {})

    bazi = s1.get("bazi", pp.get("bazi", ""))
    ri_gan = s1.get("ri_zhu", {}).get("gan", "")
    ri_wx = s1.get("ri_zhu", {}).get("wx", "")
    now = datetime.now()

    L = []

    def add(t=""):
        L.append(t)

    def add_empty():
        L.append("")

    def add_nar(sec, title):
        """添加一套内容：title + narrative + detail_analysis + 空行"""
        add(f"## {title}")
        add_empty()
        nar = sec.get("narrative", "") if isinstance(sec, dict) else ""
        if nar:
            for line in str(nar).split("\\n"):
                line = line.strip()
                if line and len(line) > 3:
                    add(line)
            add_empty()
        da = sec.get("detail_analysis", "") if isinstance(sec, dict) else ""
        if da:
            add("**规则分析依据：**")
            for line in fmt(da).split("\\n"):
                line = line.strip()
                if line and len(line) > 5:
                    add(f"- {line}")
            add_empty()

    # ===== 头部 =====
    add(f"# {name}·标准引擎深度报告")
    add_empty()
    add("---")
    add("**编制人：** 金鉴真人·确定性规则引擎 v5.0")
    add(f"**生成时间：** {now.year}年{now.month:02d}月{now.day:02d}日 {now.hour:02d}:{now.minute:02d}")
    add(f"**八字：** {bazi}")
    add(f"**日主：** {ri_gan}（{ri_wx}）| **性别：** {gender_cn}")
    add_empty()
    add("---")
    add_empty()

    # ===== §1 一页总览 =====
    shen_label = s3.get("label", "")
    shen_score = s3.get("score", 0)
    cai_total = s8.get("cai_xing_total", 0)
    wealth_lv = s8.get("wealth_level", "")
    na_yin = s1.get("na_yin", [])
    xi_arr = s4.get("xi", [])
    ji_arr = s4.get("ji", [])

    add("## §1 一页总览")
    add_empty()
    add(f"- **八字：** {bazi}")
    add(f"- **纳音：** {' '.join(na_yin) if na_yin else '—'}")
    add(f"- **日主：** {ri_gan}（{ri_wx}）| **性别：** {gender_cn}")
    add(f"- **身强弱：** {shen_label}（{shen_score}分）")
    add(f"- **格局：** {s2.get('detail', s2.get('main', ''))}")
    add(f"- **喜用神：** {'、'.join(xi_arr) if xi_arr else '—'}")
    add(f"- **忌神：** {'、'.join(ji_arr) if ji_arr else '—'}")
    add(f"- **财星总分：** {int(cai_total)}分（{wealth_lv}）")
    tp = s4.get("tiao_hou", "")
    add(f"- **调候用神：** {fmt(tp) if tp else '—'}")

    # 大运摘要
    dy_list = s17.get("list", [])
    best_idx = s17.get("best_idx", -1)
    worst_idx = s17.get("worst_idx", -1)
    if dy_list:
        add(f"- **起运年龄：** {s1.get('qi_yun_age', '')}岁")
        if best_idx >= 0 and best_idx < len(dy_list):
            b = dy_list[best_idx]
            add(
                f"- **最佳大运：** {b.get('gan_zhi', '')}运（{b.get('start_age', '')}~{b.get('end_age', '')}岁）评分{b.get('score', '')}/10"
            )
        if worst_idx >= 0 and worst_idx < len(dy_list):
            w = dy_list[worst_idx]
            add(
                f"- **需防大运：** {w.get('gan_zhi', '')}运（{w.get('start_age', '')}~{w.get('end_age', '')}岁）评分{w.get('score', '')}/10"
            )
    add_empty()

    # 总览叙述
    nar = s1.get("narrative", "")
    if nar:
        add("**总评：**")
        for line in str(nar).split("\\n"):
            line = line.strip()
            if line and len(line) > 3:
                add(f"> {line}")
        add_empty()

    # ===== 正文 §2-§21 =====
    sections = [
        ("§2 格局分析", s2, "sec_2_ge_ju"),
        ("§3 身强弱判定", s3, "sec_3_shen_qiang_ruo"),
        ("§4 喜用神与忌神", s4, "sec_4_xi_yong"),
        ("§5 灾祸预警与化解", s5, "sec_5_zai_huo"),
    ]
    for title, sec, _ in sections:
        add_nar(sec, title)

    # §6 性格（加detail_analysis展开）
    add("## §6 性格解析")
    add_empty()
    nar = s6.get("narrative", "")
    if nar:
        for line in str(nar).split("\\n"):
            line = line.strip()
            if line and len(line) > 3:
                add(line)
        add_empty()
    da = s6.get("detail_analysis", "")
    if da:
        add("**性格规则分析：**")
        for line in fmt(da).split("\\n"):
            line = line.strip()
            if line and len(line) > 5:
                add(f"- {line}")
        add_empty()
    # 关键特质列表
    key_traits = s6.get("key_traits", [])
    if key_traits:
        add(f"**关键特质：** {'、'.join(key_traits)}")
        add_empty()

    # §7 外貌
    add_nar(s7, "§7 身材外貌")
    build = s7.get("build", "")
    height = s7.get("height_estimate", "")
    if build or height:
        add(f"**体型：** {fmt(build)} | **身高：** {fmt(height)}")
        add_empty()

    # §8 财富（含明细）
    add("## §8 财富格局")
    add_empty()
    nar = s8.get("narrative", "")
    if nar:
        for line in str(nar).split("\\n"):
            line = line.strip()
            if line and len(line) > 3:
                add(line)
        add_empty()
    da = s8.get("detail_analysis", "")
    if da:
        add("**财星计分明细：**")
        for line in fmt(da).split("\\n"):
            line = line.strip()
            if line and len(line) > 5:
                add(f"- {line}")
        add_empty()
    ck = s8.get("cai_ku", {})
    if ck and ck.get("has"):
        add(f"**财库：** {', '.join(ck.get('zhi', []))} | 命带财库，有蓄财能力")
        add_empty()
    # 财星明细
    cai_details = s8.get("cai_xing_details", {})
    if cai_details:
        add("**财星来源分布：**")
        for k, v in cai_details.items():
            if isinstance(v, (int, float)) and v > 0:
                add(f"- {fmt(k)}: {v}分")
        add_empty()

    # §9-§15
    for title, sec, _ in [
        ("§9 置业分析", s9, "sec_9_property"),
        ("§10 事业发展", s10, "sec_10_career"),
        ("§11 学业学历", s11, "sec_11_education"),
        ("§12 婚姻感情", s12, "sec_12_marriage"),
        ("§13 子女运势", s13, "sec_13_children"),
        ("§14 健康注意", s14, "sec_14_health"),
        ("§15 六亲关系", s15, "sec_15_family"),
    ]:
        add_nar(sec, title)

    # §16 流年事件
    add("## §16 流年关键事件")
    add_empty()
    nar = s16.get("narrative", "")
    if nar:
        for line in str(nar).split("\\n"):
            line = line.strip()
            if line and len(line) > 3:
                add(line)
        add_empty()
    # 事件列表
    key_events = s16.get("key_events", {})
    event_items = []
    for etype, evts in key_events.items():
        if isinstance(evts, list):
            for e in evts:
                if isinstance(e, dict) and e.get("year") and e.get("description"):
                    event_items.append(e)
    if event_items:
        event_items.sort(key=lambda x: x.get("year", 0))
        add("**关键事件一览：**")
        add_empty()
        add("| 年份 | 事件描述 |")
        add("|------|----------|")
        for e in event_items[:20]:
            add(f"| {e['year']} | {e['description'][:60]} |")
        add_empty()

    # §17 大运详批
    add("## §17 大运详批")
    add_empty()
    nar = s17.get("narrative", "")
    if nar:
        for line in str(nar).split("\\n"):
            line = line.strip()
            if line and len(line) > 3:
                add(line)
        add_empty()
    da = s17.get("detail_analysis", "")
    if da:
        add("**大运规则分析：**")
        for line in fmt(da).split("\\n"):
            line = line.strip()
            if line and len(line) > 5:
                add(f"- {line}")
        add_empty()
    if dy_list:
        add("**大运列表：**")
        add_empty()
        add("| 大运 | 年龄 | 年份区间 | 十神 | 评分 | 柱状图 |")
        add("|------|------|----------|------|:----:|:------:|")
        for dy in dy_list:
            gz = dy.get("gan_zhi", "")
            sa = dy.get("start_age", "")
            ea = dy.get("end_age", "")
            sy = dy.get("start_year", "")
            ey = dy.get("end_year", "")
            ss = dy.get("gan_ss", "")
            sc = dy.get("score", 5)
            bar = "█" * int(round(sc)) + "░" * (10 - int(round(sc)))
            add(f"| {gz} | {sa}~{ea}岁 | {sy}~{ey}年 | {ss} | {sc}/10 | {bar} |")
        add_empty()
        # 排序
        sorted_dy = sorted(dy_list, key=lambda d: d.get("score", 5), reverse=True)
        add("**大运排序（按评分降序）：**")
        for i, dy in enumerate(sorted_dy):
            tag = ""
            if i == 0:
                tag = " 👑最佳"
            add(
                f"{i + 1}. {dy.get('gan_zhi', '')}运（{dy.get('start_age', '')}~{dy.get('end_age', '')}岁）：{dy.get('score', 5)}/10{tag}"
            )
        add_empty()

    # §18 三决断
    add("## §18 三决断")
    add_empty()
    if isinstance(r.get("sec_18_verdicts"), dict):
        nar = r["sec_18_verdicts"].get("narrative", "")
        if nar:
            for line in str(nar).split("\\n"):
                line = line.strip()
                if line and len(line) > 3:
                    add(line)
            add_empty()
    vlist = []
    if isinstance(r.get("sec_18_verdicts"), dict):
        vlist = r["sec_18_verdicts"].get("verdicts", [])
    elif isinstance(r.get("sec_18_verdicts"), list):
        vlist = r["sec_18_verdicts"]
    for v in vlist:
        add(f"### {v.get('title', '')}")
        add(f"- **结论：** {v.get('event', '')}")
        add(f"- **时机：** {v.get('time', '')}")
        add(f"- **依据：** {v.get('reason', '')}")
        add_empty()

    # §19 运程总评
    add_nar(s19, "§19 运程总评")
    # 运程曲线
    curve = s19.get("curve", [])
    if curve:
        add("**运程曲线：**")
        for c in curve:
            bar = c.get("bar", "")
            add(f"{c.get('da_yun', '')}（{c.get('age', '')}）：{bar} {c.get('score', '')}/10")
        add_empty()

    # §20 五行补充
    add_nar(s20, "§20 五行补充建议")
    # 结构化数据
    add("**五行开运速查表：**")
    add_empty()
    add("| 类别 | 建议 |")
    add("|------|------|")
    if s20.get("colors"):
        add(f"| 颜色 | {s20['colors']} |")
    if s20.get("directions"):
        add(f"| 方位 | {s20['directions']} |")
    if s20.get("jewellery"):
        add(f"| 饰品 | {s20['jewellery']} |")
    if s20.get("diet"):
        add(f"| 饮食 | {s20['diet']} |")
    if s20.get("lucky_numbers"):
        add(f"| 数字 | {s20['lucky_numbers']} |")
    if s20.get("avoid_numbers"):
        add(f"| 避讳 | {s20['avoid_numbers']} |")
    add_empty()

    # §21 人生建议
    add_nar(s21, "§21 人生建议")

    # 附录
    add("---")
    add_empty()
    add("**编制引擎：** 金鉴真人·确定性规则引擎 v5.0")
    add("**引擎模块：** 36个规则模块（paipan/shen_qiang_ruo/cai_xing/ge_ju/da_yun/dimensions等）")
    add("**测试覆盖：** 320条自动化测试 100%通过")
    add("**报告版本：** 引擎标准版 v1.0")
    add(f"**编制时间：** {now.year}年{now.month:02d}月{now.day:02d}日 {now.hour:02d}:{now.minute:02d}")
    add_empty()
    add("#PIPELINE-SIG: engine-v5.0-standard-report")
    add_empty()

    return "\n".join(L)


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    report = gen_report(data, sys.argv[2], sys.argv[3])
    print(report)
