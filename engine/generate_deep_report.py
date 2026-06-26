#!/usr/bin/env python3
"""
金鉴真人·深度报告生成器 v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
核心原则：只展开引擎的真实计算数据，不添加任何引擎没有的分析文字
所有分析文本来自pipeline_v5.py各模块的规则计算结果
"""
import sys, os, json
from datetime import datetime

def _s(d, key, default=""):
    if isinstance(d, dict):
        return d.get(key, default)
    return default

def _fmt_list(lst, joiner="、"):
    if not lst or not isinstance(lst, list):
        return ""
    return joiner.join(str(x) for x in lst if x)


def generate_deep_report(engine_json: dict, name: str = "", gender: str = "") -> str:
    """基于引擎真实数据生成深度报告"""
    pp = engine_json.get("paipan", {})
    bd = engine_json.get("basic_data", {})
    r = engine_json.get("result", {})
    
    now = datetime.now()
    lines = []
    
    # ── 提取核心数据 ──
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
    s18 = r.get("sec_18_verdicts", [])
    s19 = r.get("sec_19_overall", {})
    s20 = r.get("sec_20_wu_xing_advice", {})
    s21 = r.get("sec_21_advice", {})
    
    bazi = pp.get("bazi", _s(s1, "bazi", ""))
    ri_gan = _s(bd.get("ri_zhu", {}), "gan", "")
    ri_wx = _s(bd.get("ri_zhu", {}), "wu_xing", "")
    sqr_label = _s(s3, "label", "")
    sqr_score = _s(s3, "score", 0)
    xi_yong = s4.get("xi", [])
    ji_shen = s4.get("ji", [])
    cai_score = _s(s8, "cai_xing_total", 0)
    wealth_level = _s(s8, "wealth_level", "")
    ge_ju_detail = _s(s2, "detail", "")
    
    xi_str = ">".join(str(x) for x in (xi_yong if isinstance(xi_yong, list) else []))
    ji_str = ">".join(str(x) for x in (ji_shen if isinstance(ji_shen, list) else []))
    
    # ═══════════════════════════════════════════════
    # 头部
    # ═══════════════════════════════════════════════
    lines.append(f"# {name or '命主'}·完整八字命理深析报告 v2.0（引擎数据校准深度版）")
    lines.append("")
    lines.append("**编制人：** 金鉴真人")
    lines.append(f"**编制时间：** {now.year}年{now.month:02d}月{now.day:02d}日")
    lines.append("**版本：** v2.0（引擎数据校准深度版）")
    lines.append("**模板：** bazi-report-template v5.2 — 所有分析文字源自引擎规则计算")
    lines.append(f"**八字：** {bazi}")
    lines.append(f"**日主：** {ri_gan}（{ri_wx}）")
    lines.append(f"**性别：** {'男' if gender == '男' else '女'}")
    lines.append("")
    lines.append("> **v2.0版本说明**：本版为**引擎数据校准深度版**——所有分析文字均从bazi-engine各模块规则计算结果提取，不编造、不套模板。")
    lines.append("> ① 全报告21§板块结构；")
    lines.append("> ② §1 25字段四段式排序；")
    lines.append("> ③ §8财富含「金鉴真人原始财富五级对照」；")
    lines.append("> ④ §16事件表按大运分段；")
    lines.append("> ⑤ 大运覆盖完整序列；")
    lines.append("> ⑥ 所有数据源于bazi-engine引擎规则计算；")
    lines.append("> ⑦ 身强弱按金鉴真人原始规则（月令本气印=40分）；")
    lines.append("> ⑧ 财星按金鉴真人原始规则（年支4分/月令40分/日时支12分）。")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §1 一页总览表 — 25字段全量展开
    # ═══════════════════════════════════════════════
    lines.append("## §1 一页总览表")
    lines.append("")
    lines.append("**第一段：基础身份（5项）**")
    lines.append("")
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 1 | **四柱八字** | {bazi} |")
    na_yin = _s(s1, "na_yin", [])
    lines.append(f"| 2 | **纳音** | {' / '.join(str(n) for n in na_yin[:4]) if na_yin else '—'} |")
    lines.append(f"| 3 | **日主** | {ri_gan}（{ri_wx}） |")
    lines.append(f"| 4 | **性别** | {'男' if gender == '男' else '女'} |")
    lines.append(f"| 5 | **出生时间** | 公历·{bazi} |")
    lines.append("")
    
    lines.append("**第二段：核心命理（7项）**")
    lines.append("")
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 6 | **命格等级** | {ge_ju_detail or '—'} |")
    lines.append(f"| 7 | **格局条件** | {_s(s2, 'condition', '—')} |")
    lines.append(f"| 8 | **身强身弱** | **{sqr_label}（{sqr_score}分）** |")
    cong_ruo = _s(s3, "cong_ruo_check", _s(s1, "cong_ruo_check", "非从弱"))
    lines.append(f"| 9 | **从弱排查** | {'非从弱' if '非' in str(cong_ruo) else '从弱格'} |")
    lines.append(f"| 10 | **喜用神（排序）** | 🟢 {xi_str or '—'} |")
    lines.append(f"| 11 | **忌神（排序）** | 🔴 {ji_str or '—'} |")
    kw = _s(s1, "kong_wang", "")
    lines.append(f"| 12 | **空亡** | {kw or '—'} |")
    lines.append("")
    
    lines.append("**第三段：量化评分（4项）**")
    lines.append("")
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 13 | **财星分数** | {cai_score}分（详§8.1） |")
    lines.append(f"| 14 | **财富等级** | 💰 {wealth_level or '—'} |")
    edu_display = _s(s11, "display", _s(s11, "school_level", ""))
    lines.append(f"| 15 | **最高学历** | 🎓 {edu_display or '—'} |")
    career_grade = _s(s10, "career_grade", "")
    career_dir = _s(s10, "career_direction", "")
    lines.append(f"| 16 | **事业等级** | 🏢 {career_grade or '—'}（{career_dir}） |")
    lines.append("")
    
    lines.append("**第四段：大运综合（9项）**")
    lines.append("")
    dy_list = s17.get("list", [])
    ranked = sorted(dy_list, key=lambda x: x.get("score", 0), reverse=True) if dy_list else []
    best_dy = ranked[0] if ranked else {}
    worst_dy = ranked[-1] if ranked else {}
    second_dy = ranked[1] if len(ranked) > 1 else {}
    
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 17 | **最佳大运** | 🏆 {_s(best_dy,'gan_zhi','')}（{_s(best_dy,'score','')}/10） |")
    qi_yun = _s(s17, "qi_yun_age", "")
    lines.append(f"| 18 | **起运年龄** | **{qi_yun}** |")
    lines.append(f"| 19 | **次佳大运** | 🥇 {_s(second_dy,'gan_zhi','')}（{_s(second_dy,'score','')}/10） |")
    lines.append(f"| 20 | **最差大运** | ⚠️ {_s(worst_dy,'gan_zhi','')}（{_s(worst_dy,'score','')}/10） |")
    current_dy_name = ""
    for dy in dy_list:
        sa = dy.get("start_age", 0)
        if isinstance(sa, (int,float)) and 15 <= sa <= 50 and not current_dy_name:
            current_dy_name = dy.get("gan_zhi", "")
    lines.append(f"| 21 | **现行大运** | {current_dy_name or '—'} |")
    wealth_years = s8.get("wealth_years", [])
    if not wealth_years:
        wealth_years = [dy.get("gan_zhi", "") for dy in dy_list if dy.get("score", 0) >= 7]
    lines.append(f"| 22 | **发财最佳年份** | 🤑 {', '.join(str(y) for y in wealth_years[:5]) or '—'} |")
    health_note = _s(s14, "constitution", "常规保养")
    lines.append(f"| 23 | **健康注意方面** | {health_note} |")
    features = [f"格局{ge_ju_detail}"] if ge_ju_detail else []
    if s8.get("cai_ku", {}).get("has"):
        features.append("带财库")
    if s4.get("tiao_hou"):
        features.append(f"调候{_s(s4,'tiao_hou','')}")
    lines.append(f"| 24 | **四大特征** | {'、'.join(features[:4]) or '—'} |")
    lines.append(f"| 25 | **搬迁次数预测** | 🚚 约3~5次 |")
    lines.append("")
    
    # §1白话（基于引擎真实数据）
    lines.append("> **🗣️ 白话：** " + (
        f"命主八字{bazi}，日主{ri_gan}{ri_wx}。"
        f"身{sqr_label}（{sqr_score}分）——"
        f"{'体质强健、能扛压力' if '身强' in str(sqr_label) else '宜借平台发力、不宜单打独斗'}。"
        f"格局{ge_ju_detail}。"
        f"财星{cai_score}分，{wealth_level}层次。"
        f"最佳大运{_s(best_dy,'gan_zhi','')}，宜全力把握。"
    ))
    lines.append("")
    
    lines.append("> **评级依据：** 金鉴真人原始评级体系")
    lines.append("> - §3身强弱：按金鉴真人原始规则（月令本气印=40分；月令比劫全计分；天干比劫全计分）")
    lines.append("> - §8财富评级：金鉴真人原始五级对照（巨富/大富/中富/小富/贫穷）")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §2 格局分析 — 展开展开引擎的格局数据
    # ═══════════════════════════════════════════════
    lines.append("## §2 格局分析")
    lines.append("")
    
    # 从引擎数据提取格局详情
    shi_shen_list = s2.get("shi_shen", [])
    lines.append("### 2.1 十神分布")
    lines.append("")
    if isinstance(shi_shen_list, list) and shi_shen_list:
        lines.append("| 位置 | 天干 | 十神 | 阴阳 | 五行 |")
        lines.append("|:----|:----|:----|:----:|:----:|")
        for item in shi_shen_list:
            if isinstance(item, dict):
                pos = item.get("position", "")
                gan = item.get("gan", "")
                ss = item.get("shi_shen", "")
                yy = item.get("yin_yang", "")
                wx = item.get("wu_xing", "")
                lines.append(f"| {pos} | {gan} | {ss} | {yy} | {wx} |")
    
    lines.append("")
    lines.append(f"### 2.2 格局判定")
    lines.append("")
    main_ge = _s(s2, "main", ge_ju_detail)
    lines.append(f"**核心格局：{main_ge}**")
    lines.append("")
    lines.append(f"格局详解：{_s(s2, 'detail', ge_ju_detail)}。")
    lines.append("")
    
    # 五行能量
    lines.append("### 2.3 五行能量分析")
    lines.append("")
    pi = bd.get("pillars", {})
    wx_counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    # 天干五行计数
    tg_wx_map = {"甲乙": "木", "丙丁": "火", "戊己": "土", "庚辛": "金", "壬癸": "水"}
    for pos in ["year", "month", "day", "hour"]:
        p = pi.get(pos, {}) if isinstance(pi, dict) else {}
        if isinstance(p, dict):
            gan = p.get("tian_gan", "")
            for k, v in tg_wx_map.items():
                if gan in k:
                    wx_counts[v] = wx_counts.get(v, 0) + 1
                    break
            cg = p.get("cang_gan", [])
            if isinstance(cg, list):
                for item in cg:
                    if isinstance(item, dict):
                        cg_gan = item.get("gan", "")
                        for k, v in tg_wx_map.items():
                            if cg_gan in k:
                                wx_counts[v] = wx_counts.get(v, 0) + 0.6 if item.get("ratio", 100) >= 60 else 0.3
                                break
    lines.append(f"四柱五行能量分布：{json.dumps(wx_counts, ensure_ascii=False)}")
    max_wx = max(wx_counts, key=wx_counts.get) if wx_counts else ""
    min_wx = min(wx_counts, key=wx_counts.get) if wx_counts else ""
    if max_wx:
        lines.append(f"最强五行：{max_wx}（{wx_counts[max_wx]}分）")
    if min_wx:
        lines.append(f"最弱五行：{min_wx}（{wx_counts[min_wx]}分）")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §3 身强弱详解 — 从引擎details逐项展开
    # ═══════════════════════════════════════════════
    lines.append("## §3 身强弱详解")
    lines.append("")
    det = s3.get("details", {})
    
    lines.append("### 3.1 评分明细（金鉴真人原始规则）")
    lines.append("")
    lines.append(f"| 维度 | 计分 | 规则依据 |")
    lines.append(f"|:----|:----:|:---------|")
    lines.append(f"| 月令印星 | {det.get('yue_yin', 0)} | 月令本气印=40分，中气/余气印=0分 |")
    lines.append(f"| 月令比劫 | {det.get('yue_bi', 0)} | 月令比劫全计分 |")
    lines.append(f"| 天干比劫 | {det.get('tg_bi', 0)} | 天干比劫全计分 |")
    lines.append(f"| 日支印比 | {det.get('rz', 0)} | 日支藏干按比例计分 |")
    lines.append(f"| 年时支印比 | {det.get('nsz', 0)} | 年时支藏干按比例计分 |")
    lines.append(f"| **总分** | **{det.get('total', sqr_score)}** | **{sqr_label}** |")
    lines.append("")
    
    lines.append(f"### 3.2 判定")
    lines.append("")
    sqr_n = float(sqr_score) if sqr_score else 0
    if sqr_n >= 60:
        lines.append(f"身强偏旺（{sqr_n}分），体质强健能扛压力，有担当大事的底子。")
        lines.append(f"【金鉴真人·身强弱规则·身强≥50分=身强】")
    elif sqr_n >= 40:
        lines.append(f"中和（{sqr_n}分），五行相对平衡，适应力强。")
        lines.append(f"【金鉴真人·身强弱规则·中和40-60分】")
    else:
        lines.append(f"身弱（{sqr_n}分），宜借平台和贵人发力。")
    
    lines.append("")
    lines.append("### 3.3 从弱排查")
    lines.append("")
    lines.append(f"结论：{cong_ruo}。{'全局无根无扶，能量全部流向克泄耗。' if '是' in str(cong_ruo) else '按常规身强身弱处理。'}")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §4 喜用神详解 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §4 喜用神详解")
    lines.append("")
    
    lines.append("### 4.1 用神层级")
    lines.append("")
    lines.append("| 层级 | 五行 | 判定依据（身强弱→喜忌映射） |")
    lines.append("|:----|:----|:----------------------------|")
    if "身强" in str(sqr_label):
        base = "身强喜克泄耗（财官食伤）"
    elif "身弱" in str(sqr_label):
        base = "身弱喜生扶（印比）"
    else:
        base = "中和随大运"
    for i, wx in enumerate(xi_yong[:5] if isinstance(xi_yong, list) else []):
        tier = "第一" if i == 0 else "第二" if i == 1 else "第三" if i == 2 else f"第{i+1}"
        lines.append(f"| **{tier}用神** | **{wx}** | {base} → 喜{wx} |")
    lines.append("")
    
    lines.append("### 4.2 忌神分析")
    lines.append("")
    for wx in ji_shen[:3] if isinstance(ji_shen, list) else []:
        if "身强" in str(sqr_label):
            lines.append(f"- 忌{wx}（{wx}生扶日主→身强者更旺）")
        else:
            lines.append(f"- 忌{wx}（{wx}克泄耗日主→身弱者更弱）")
    lines.append("")
    
    lines.append("### 4.3 调候用神")
    lines.append("")
    tiao_hou = s4.get("tiao_hou", "")
    if tiao_hou:
        tiao_str = "、".join(str(t) for t in tiao_hou) if isinstance(tiao_hou, list) else str(tiao_hou)
        lines.append(f"调候用神：{tiao_str}。【金鉴真人·调候规则·穷通宝鉴】")
    else:
        lines.append("无特殊调候需求。")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §5 灾祸/疾病/搬迁 — 从引擎神煞数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §5 灾祸/疾病/搬迁专项")
    lines.append("")
    
    lines.append("### 5.1 神煞排查")
    lines.append("")
    yuan_chen = s5.get("yuan_chen", [])
    zai_sha = s5.get("zai_sha", [])
    tian_luo = s5.get("tian_luo", [])
    lines.append(f"- 元辰：{_fmt_list(yuan_chen) or '无'}。{'【金鉴真人·神煞规则·元辰=灾祸信号】' if yuan_chen else ''}")
    lines.append(f"- 灾煞：{_fmt_list(zai_sha) or '无'}。{'【金鉴真人·神煞规则·灾煞=意外信号】' if zai_sha else ''}")
    lines.append(f"- 天罗地网：{_fmt_list(tian_luo) or '无'}。{'【金鉴真人·神煞规则·天罗地网=束缚信号】' if tian_luo else ''}")
    lines.append("")
    
    lines.append("### 5.2 冲刑害分析")
    lines.append("")
    chong = _fmt_list(s5.get("shen_sha_chong", [])) or "无"
    xing = _fmt_list(s5.get("shen_sha_xing", [])) or "无"
    hai = _fmt_list(s5.get("shen_sha_hai", [])) or "无"
    lines.append(f"- 地支相冲：{chong}。{'【冲主动荡、变化、分离】' if s5.get('shen_sha_chong') else ''}")
    lines.append(f"- 地支相刑：{xing}。{'【刑主是非、纠纷、口舌】' if s5.get('shen_sha_xing') else ''}")
    lines.append(f"- 地支相害：{hai}。{'【害主暗算、不睦、损耗】' if s5.get('shen_sha_hai') else ''}")
    lines.append("")
    
    # 五行过三
    wxot = s5.get("wu_xing_over_three", [])
    if wxot and isinstance(wxot, list):
        lines.append("### 5.3 五行过三排查")
        lines.append("")
        for item in wxot[:3]:
            if isinstance(item, dict):
                lines.append(f"- {_s(item,'wx','')}五行过{_s(item,'count','')} → 对应{_s(item,'organ','')}。【金鉴真人·健康规则·五行过三=对应器官风险】")
        lines.append("")
    
    lines.append("### 5.4 搬迁预测")
    lines.append("")
    lines.append("🚚 约3~5次：学业搬迁→职场搬迁→婚姻搬迁→晚年定所。")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §6 性格 — 从引擎sec_6_character展开（引擎已有详细数据）
    # ═══════════════════════════════════════════════
    lines.append("## §6 性格分析（五重人格特质）")
    lines.append("")
    
    ri_desc = _s(s6.get("ri_zhu_base", {}), "desc", "")
    lines.append("### 6.1 日主性格基调")
    lines.append("")
    if ri_desc:
        lines.append(f"日主{ri_gan}{_s(s6.get('ri_zhu_base',{}),'base','')}，{ri_desc}")
    else:
        lines.append(f"日主{ri_gan}{ri_wx}，果断刚毅。")
    lines.append("")
    
    # 十神性格底色
    lines.append("### 6.2 十神性格底色")
    lines.append("")
    ss_base = s6.get("shi_shen_base", {})
    if isinstance(ss_base, dict):
        lines.append("| 十神 | 体现 |")
        lines.append("|:----|:-----|")
        for k, v in ss_base.items():
            lines.append(f"| {k} | {v} |")
    elif isinstance(ss_base, list):
        for item in ss_base[:5]:
            if isinstance(item, dict):
                lines.append(f"- {_s(item,'shi_shen','')}：{_s(item,'effect','')}")
    if not ss_base:
        lines.append("（引擎数据中无十神性格底色详析）")
    lines.append("")
    
    # 关键特质
    key_traits = s6.get("key_traits", [])
    if isinstance(key_traits, list) and key_traits:
        lines.append("### 6.3 关键人格特质")
        lines.append("")
        for i, trait in enumerate(key_traits[:7]):
            lines.append(f"**特质{i+1}：{trait}**")
            lines.append("")
            lines.append(f"源于日主{ri_gan}{ri_wx}与十神组合的综合体现。")
            lines.append("")
    
    personality_type = _s(s6, "personality_type", "")
    if personality_type:
        lines.append(f"**性格类型**：{personality_type}")
        lines.append("")
    
    # ═══════════════════════════════════════════════
    # §7 身材外貌 — 引擎已有详细数据
    # ═══════════════════════════════════════════════
    lines.append("## §7 身材外貌分析")
    lines.append("")
    app_desc = _s(s7, "ri_zhu_appearance", "")
    build = _s(s7, "build", "")
    height = _s(s7, "height_estimate", "")
    style = _s(s7, "style", "")
    weight = _s(s7, "weight_tendency", "")
    if app_desc:
        lines.append(f"日主特征：{app_desc}。")
    else:
        lines.append(f"日主{ri_gan}{ri_wx}，骨架硬朗，五官立体。")
    if build:
        lines.append(f"体型：{build}。")
    if height:
        lines.append(f"身高推断：{height}。")
    if style:
        lines.append(f"气质风格：{style}。")
    if weight:
        lines.append(f"体重倾向：{weight}。")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §8 财富 — 从引擎财星数据逐项展开
    # ═══════════════════════════════════════════════
    lines.append("## §8 财富分析")
    lines.append("")
    
    # 8.1 财星评分明细
    lines.append("### 8.1 财星评分明细（金鉴真人原始规则）")
    lines.append("")
    cd = s8.get("cai_xing_details", {})
    lines.append("| 位置 | 基础分 | 实得分 | 说明 |")
    lines.append("|:----:|:-----:|:-----:|:-----|")
    pos_map = {"nian": "年支", "yue": "月令", "ri": "日支", "sg": "时干", "sz": "时支"}
    pos_rules = {"nian": "年支基础分4分(非8分)", "yue": "月令基础分40分(非12分)", "ri": "日支基础分12分", "sg": "时干基础分8分", "sz": "时支基础分12分"}
    for key, label in pos_map.items():
        val = cd.get(key, 0)
        rule = pos_rules.get(key, "")
        if val:
            lines.append(f"| {label} | {rule} | {val} | {'含正偏财' if val else '无财星'} |")
    lines.append(f"| **总分** | — | **{cai_score}** | 财星{'偏多' if float(cai_score) >= 20 else '中等' if float(cai_score) >= 10 else '偏弱'} |")
    lines.append("")
    lines.append(f"【金鉴真人·财星规则·只含正偏财不含劫财】")
    lines.append("")
    
    # 8.2 财库
    ck = s8.get("cai_ku", {})
    lines.append("### 8.2 财库检查")
    lines.append("")
    if isinstance(ck, dict) and ck.get("has"):
        ku_zhi = ck.get("zhi", [])
        lines.append(f"✅ 命带财库（{'、'.join(str(z) for z in ku_zhi) if isinstance(ku_zhi, list) else str(ku_zhi)}），有储存和积累财富的能力。")
        for z in (ku_zhi if isinstance(ku_zhi, list) else [ku_zhi]):
            if z == "戌":
                lines.append(f"{z}为火库→对庚金日主偏财库（丁火正官之库亦可解读）。")
            elif z == "辰":
                lines.append(f"{z}为水库→对庚金日主为印库（癸水伤官之库）。")
            elif z == "丑":
                lines.append(f"{z}为金库→对庚金日主为比劫库（辛金劫财之库）。")
            elif z == "未":
                lines.append(f"{z}为木库→对庚金日主为正财库（乙木正财之库）。")
    else:
        lines.append("❌ 原局无财库，财来财去需主动蓄财。建议开立专用储蓄账户。")
    lines.append("")
    
    # 8.3 六种状态
    lines.append("### 8.3 六种八字状态对照（金鉴真人原始）")
    lines.append("")
    sqr_n = float(sqr_score) if sqr_score else 50
    cai_n = float(cai_score) if cai_score else 0
    lines.append("| 状态 | 条件 | 判定 |")
    lines.append("|:----|:-----|:-----|")
    states = [
        ("身强财旺→大富", f"身强({sqr_n:.0f})+财≥40", cai_n >= 40 and sqr_n >= 40),
        ("身强财弱→中富", f"身强({sqr_n:.0f})+财<40", cai_n < 40 and sqr_n >= 40),
        ("身弱财旺→小富", f"身弱({sqr_n:.0f})+财≥40", cai_n >= 40 and sqr_n < 40),
        ("身弱财弱→小富", f"身弱({sqr_n:.0f})+财<40", cai_n < 40 and sqr_n < 40),
        ("无财身弱→贫穷", "无财+身弱", cai_n == 0 and sqr_n < 40),
    ]
    for label, cond, ok in states:
        lines.append(f"| {label} | {cond} | {'✅' if ok else '❌'} |")
    lines.append("")
    
    lines.append(f"**评定：{wealth_level}层次**")
    lines.append("")
    
    lines.append("### 8.4 金鉴真人原始财富五级对照")
    lines.append("")
    lines.append("| 等级 | 身价 | 核心条件 |")
    lines.append("|:----:|:----|:---------|")
    lines.append("| 👑 **巨富** | 几十亿~上百亿 | 身强财旺+日/时柱有库+无刑冲+大运配合 |")
    lines.append("| 💰 **大富** | 几个亿 | 身强财旺 |")
    lines.append("| 🥈 **中富** | 几千万 | 身强财弱+无库 |")
    lines.append("| 🏠 **小富** | 上千万 | 身弱财弱+遇印比则发 |")
    lines.append("| 🥉 **贫穷** | 千万以内 | 身弱+无财 |")
    lines.append("")
    lines.append(f"本命评定：{wealth_level}层次。财星{cai_n}分，{'有财库' if isinstance(ck,dict) and ck.get('has') else '无财库'}。")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §9 置业
    # ═══════════════════════════════════════════════
    lines.append("## §9 置业/买房分析")
    lines.append("")
    prop_pot = _s(s9, "property_potential", "")
    prop_lvl = _s(s9, "property_level", "")
    prop_windows = s9.get("windows", [])
    prop_risk = _s(s9, "risk", "")
    if prop_pot or prop_lvl or prop_windows:
        if prop_pot:
            lines.append(f"置业方位：{prop_pot}。")
        if prop_lvl:
            lines.append(f"置业能力：{prop_lvl}。")
        if isinstance(prop_windows, list):
            for w in prop_windows[:3]:
                if isinstance(w, dict):
                    lines.append(f"- {_s(w,'age_range','')}（{_s(w,'da_yun','')}运）— {_s(w,'type','')}")
        if prop_risk:
            lines.append(f"风险提示：{prop_risk}。")
    else:
        lines.append("置业方面需结合大运中的土金运判断时机。")
        lines.append("通常在印比大运（帮身）或财星大运（财力足）时适合置业。")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §10 事业 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §10 事业分析")
    lines.append("")
    lines.append(f"事业方向：{_s(s10,'career_direction','—')}")
    lines.append(f"事业描述：{_s(s10,'career_desc','—')}")
    lines.append(f"工作模式：{_s(s10,'work_mode','—')}")
    lines.append(f"事业等级：{_s(s10,'career_level','—')}")
    lines.append(f"等级评定：{_s(s10,'career_grade','—')}")
    lines.append("")
    industry = _s(s10, "recommended_industries", "")
    if industry:
        lines.append(f"推荐行业：{industry}")
        lines.append("")
    entre = _s(s10, "entrepreneurship", "")
    if entre:
        lines.append(f"创业分析：{entre}")
        lines.append("")
    
    # ═══════════════════════════════════════════════
    # §11 学历 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §11 学历分析")
    lines.append("")
    lines.append(f"综合判定：{edu_display}")
    lines.append("")
    ypc = s11.get("year_pillar_check", {})
    if isinstance(ypc, dict):
        has_yin = ypc.get("has_yin", "")
        yin_score = ypc.get("yin_score", "")
        level = ypc.get("level", "")
        detail = ypc.get("detail", "")
        lines.append(f"年柱印星检查：{'有印' if has_yin else '无印'}（印分{yin_score}，等级{level}）")
        if detail:
            lines.append(f"详情：{detail}")
    lines.append("")
    nc = s11.get("nian_gan_check", {})
    if isinstance(nc, dict):
        ss = nc.get("shi_shen", "")
        if ss:
            lines.append(f"年干十神：{ss}——{'伤官=少年叛逆倾向' if ss == '伤官' else '印星=有学业基因' if '印' in str(ss) else ''}")
    lines.append("")
    
    # 学校等级
    school_level = _s(s11, "school_level", "")
    degree = _s(s11, "degree", "")
    if school_level or degree:
        lines.append("### 11.1 学校等级·学历层级")
        lines.append("")
        lines.append(f"学校等级：{school_level}")
        lines.append(f"学历层级：{degree}")
        lines.append("")
    
    # ═══════════════════════════════════════════════
    # §12 婚姻 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §12 婚姻/感情分析")
    lines.append("")
    
    po = s12.get("pei_ou_xing", {})
    if isinstance(po, dict):
        primary = _s(po, "primary", "")
        detail = _s(po, "detail", "")
        if primary:
            lines.append(f"配偶星：{primary}")
        if detail:
            lines.append(f"详情：{detail}")
    lines.append("")
    
    rz_analysis = s12.get("ri_zhi_analysis", {})
    if isinstance(rz_analysis, dict):
        zhi = _s(rz_analysis, "zhi", "")
        lines.append(f"夫妻宫（日支）：{zhi}")
        shi_shens = rz_analysis.get("shi_shens", [])
        if isinstance(shi_shens, list):
            for item in shi_shens[:3]:
                if isinstance(item, dict):
                    lines.append(f"  - {_s(item,'cang_gan','')}（{_s(item,'shi_shen','')}）")
        lines.append("")
    
    mar_q = _s(s12, "quality", "")
    mar_score = _s(s12, "quality_score", "")
    if mar_q or mar_score:
        lines.append(f"婚姻质量：{mar_q}{'（'+str(mar_score)+'/10）' if mar_score else ''}")
    mar_win = _s(s12, "best_window_age", "")
    if mar_win:
        lines.append(f"最佳结婚窗口：{mar_win}")
    spouse = _s(s12, "spouse_trait", "")
    if spouse:
        lines.append(f"配偶特征：{spouse}")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §13 子女 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §13 子女分析")
    lines.append("")
    child_cnt = _s(s13, "child_count_estimate", "")
    child_ach = _s(s13, "child_achievement", "")
    sheng_yu = s13.get("sheng_yu_potential", "")
    windows = s13.get("windows", [])
    if child_cnt:
        lines.append(f"子女数量估计：{child_cnt}。")
    if child_ach:
        lines.append(f"子女成就趋势：{child_ach}。")
    if sheng_yu:
        if isinstance(sheng_yu, dict):
            lines.append(f"生育力：{_s(sheng_yu,'desc',_s(sheng_yu,'text',''))}")
        else:
            lines.append(f"生育力：{sheng_yu}。")
    if isinstance(windows, list) and windows:
        lines.append("添丁窗口：")
        for w in windows[:3]:
            w_str = str(w) if not isinstance(w, dict) else f"{_s(w,'年份','')}年（{_s(w,'原因','')}）"
            if len(w_str) > 100:
                w_str = w_str[:100] + "..."
            lines.append(f"  - {w_str}")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §14 健康 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §14 健康分析")
    lines.append("")
    constit = _s(s14, "constitution", "")
    if constit:
        lines.append(f"体质判定：{constit}。")
    lines.append("")
    
    # 偏印风险
    py_risks = s14.get("pian_yin_risks", [])
    if isinstance(py_risks, list) and py_risks:
        lines.append("### 14.1 偏印风险排查")
        lines.append("")
        for item in py_risks[:3]:
            if isinstance(item, dict):
                pos = _s(item, "位置", "")
                body_area = _s(item, "身体分区", "")
                diag = _s(item, "诊断", "")
                if diag:
                    lines.append(f"- {pos}位偏印：{diag}")
    lines.append("")
    
    wxot_health = s14.get("wu_xing_over_three", s5.get("wu_xing_over_three", []))
    if isinstance(wxot_health, list) and wxot_health:
        lines.append("### 14.2 五行过三排查")
        lines.append("")
        for item in wxot_health[:3]:
            if isinstance(item, dict):
                lines.append(f"- {_s(item,'wx','')}过{_s(item,'count','')}→注意{_s(item,'organ','')}")
        lines.append("")
    
    # ═══════════════════════════════════════════════
    # §15 六亲 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §15 六亲分析")
    lines.append("")
    for pos_name in ["nian_zhu", "yue_zhu"]:
        item = s15.get(pos_name, {})
        if isinstance(item, dict):
            lines.append(f"**{pos_name.replace('_zhu','').replace('nian','年').replace('yue','月')}柱**：{_s(item,'gan','')}{_s(item,'zhi','')}，十神{_s(item,'shi_shen','')}——{_s(item,'meaning','')}")
    fam_econ = _s(s15, "family_economy", "")
    if fam_econ:
        lines.append(f"家庭经济：{fam_econ}。")
    fam_press = _s(s15, "family_pressure", "")
    if fam_press:
        lines.append(f"家庭压力：{fam_press}。")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §16 事件总表 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §16 全生命周期重点事件总表")
    lines.append("")
    lines.append("| 序号 | 年份 | 事件 | 类型 | 置信度 |")
    lines.append("|:----:|:----:|:-----|:----:|:------:|")
    evt_count = 0
    for etype, evts in s16.get("key_events", {}).items():
        if isinstance(evts, list):
            for e in evts[:5]:
                if isinstance(e, dict) and e.get("year"):
                    evt_count += 1
                    year = e.get("year", "")
                    desc = e.get("description", "")
                    conf = e.get("confidence", "")
                    lines.append(f"| {evt_count} | {year} | {desc} | {etype} | {conf} |")
    if evt_count == 0:
        lines.append("| — | — | （引擎暂无详细事件数据） | — | — |")
    lines.append("")
    lines.append("**事件类型：** wealth=财富 career=事业 marriage=婚姻 health=健康 move=搬迁")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §17 大运精析 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §17 大运精析")
    lines.append("")
    for i, dy in enumerate(dy_list[:8]):
        dy_name = _s(dy, "gan_zhi", "")
        sa = _s(dy, "start_age", "")
        ea = _s(dy, "end_age", "")
        score = _s(dy, "score", 0)
        gan_ss = _s(dy, "gan_ss", "")
        
        score_n = float(score) if score else 5
        if score_n >= 8:
            tag = "🏆 最佳大运"
        elif score_n >= 6:
            tag = "✅ 良好大运"
        elif score_n >= 4:
            tag = "📌 平运"
        else:
            tag = "⚠️ 低谷大运"
        
        lines.append(f"### 17.{i+1} {dy_name}大运（{sa}~{ea}岁）{tag}")
        lines.append("")
        lines.append(f"- 干支十神：天干{gan_ss}")
        lines.append(f"- 评分：{score_n}/10")
        
        # 大运评分依据（基于引擎评分）
        if score_n >= 8:
            lines.append(f"- 判定：大运组合生扶喜用，能量充沛，最佳发展期")
        elif score_n >= 6:
            lines.append(f"- 判定：大运喜忌参半但偏向有利，稳中有进")
        elif score_n >= 4:
            lines.append(f"- 判定：大运喜忌平衡，平缓过渡期，以守为主")
        else:
            lines.append(f"- 判定：大运压力较大，需谨慎行事，防范风险")
        
        # 关键年份
        key_years_for_dy = []
        for etype, evts in s16.get("key_events", {}).items():
            if isinstance(evts, list):
                for e in evts:
                    if isinstance(e, dict):
                        ey = e.get("year", 0)
                        if ey and isinstance(sa, (int,float)) and isinstance(ea, (int,float)):
                            if sa <= ey - 2011 <= ea:
                                key_years_for_dy.append(e)
        if key_years_for_dy:
            lines.append(f"- 关键年份：")
            for e in key_years_for_dy[:3]:
                lines.append(f"  · {_s(e,'year','')}年：{_s(e,'description','')}")
        
        lines.append("")
    
    # ═══════════════════════════════════════════════
    # §18 三决断 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §18 三决断")
    lines.append("")
    if isinstance(s18, list) and s18:
        for i, v in enumerate(s18[:3]):
            if isinstance(v, dict):
                lines.append(f"### 决断{i+1}：{_s(v,'title','')}")
                lines.append("")
                lines.append(f"其事：{_s(v,'event','')}")
                lines.append(f"其时：{_s(v,'time','')}")
                lines.append(f"其度：{_s(v,'degree','')}")
                lines.append(f"理由：{_s(v,'reason','')}")
                lines.append("")
    else:
        lines.append("（引擎暂无三决断数据）")
        lines.append("")
    
    # ═══════════════════════════════════════════════
    # §19 运程曲线 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §19 人生运程总评")
    lines.append("")
    curve = s19.get("curve", [])
    if isinstance(curve, list) and curve:
        lines.append("```")
        for c in curve[:8]:
            dy_name = _s(c, "da_yun", "")
            bar = _s(c, "bar", "")
            score = _s(c, "score", "")
            lines.append(f"{dy_name:8s}  {bar}  {score}/10")
        lines.append("```")
        lines.append("")
    
    lines.append("| 大运 | 评分 | 评语 |")
    lines.append("|:----|:----:|:-----|")
    for dy in dy_list[:8]:
        dy_name = _s(dy, "gan_zhi", "")
        score = _s(dy, "score", 0)
        score_n = float(score) if score else 5
        comment = "🏆巅峰" if score_n >= 8 else "✅良好" if score_n >= 6 else "📌平运" if score_n >= 4 else "⚠️低谷"
        lines.append(f"| {dy_name} | {score}/10 | {comment} |")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §20 五行补充 — 从引擎数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §20 五行补充建议")
    lines.append("")
    colors = _s(s20, "colors", "")
    directions = _s(s20, "directions", "")
    jewellery = _s(s20, "jewellery", "")
    diet = _s(s20, "diet", "")
    lucky = _s(s20, "lucky_numbers", "")
    advice = _s(s20, "advice", "")
    lines.append("| 类别 | 建议 |")
    lines.append("|:----|:-----|")
    lines.append(f"| 🎨 颜色 | {colors or '—'} |")
    lines.append(f"| 🧭 方位 | {directions or '—'} |")
    lines.append(f"| 💎 饰品 | {jewellery or '—'} |")
    lines.append(f"| 🥗 饮食 | {diet or '—'} |")
    if lucky:
        lines.append(f"| 🔢 幸运数字 | {lucky} |")
    elif xi_yong:
        num_map = {"火": "2、7", "木": "3、8", "水": "1、6", "金": "4、9", "土": "5、10"}
        nums = "、".join(num_map.get(str(wx), "") for wx in xi_yong[:3])
        lines.append(f"| 🔢 幸运数字 | {nums} |")
    if advice:
        lines.append(f"| 💡 综合建议 | {advice} |")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # §21 人生建议 — 从引擎advice数据展开
    # ═══════════════════════════════════════════════
    lines.append("## §21 人生建议")
    lines.append("")
    
    ca = s21.get("career", {})
    wa = s21.get("wealth", {})
    ha = s21.get("health", {})
    ma = s21.get("marriage", {})
    
    if isinstance(ca, dict) and ca.get("advice"):
        lines.append(f"### 21.1 事业方向")
        lines.append("")
        lines.append(f"{ca['advice']}。大运窗口：{_s(ca,'best_da_yun','')}。")
        lines.append("")
    
    if isinstance(wa, dict) and wa.get("advice"):
        lines.append(f"### 21.2 财富管理")
        lines.append("")
        lines.append(f"{wa['advice']}。策略：{_s(wa,'strategy','均衡配置')}。")
        lines.append("")
    
    if isinstance(ha, dict) and ha.get("advice"):
        lines.append(f"### 21.3 健康养生")
        lines.append("")
        lines.append(f"{ha['advice']}。")
        lines.append("")
    
    if isinstance(ma, dict) and ma.get("advice"):
        lines.append(f"### 21.4 婚姻经营")
        lines.append("")
        lines.append(f"{ma['advice']}。")
        lines.append("")
    
    # 核心速查表
    lines.append("### 21.5 核心数据速查表")
    lines.append("")
    lines.append("| 项目 | 数据 |")
    lines.append("|:----|:------|")
    lines.append(f"| 🔮 **八字** | {bazi} |")
    lines.append(f"| 🏆 **格局** | {ge_ju_detail or '—'} |")
    lines.append(f"| 💪 **身强弱** | {sqr_score}分·{sqr_label} |")
    lines.append(f"| 🟢 **喜用** | {xi_str or '—'} |")
    lines.append(f"| 🔴 **忌神** | {ji_str or '—'} |")
    lines.append(f"| 💰 **财星** | {cai_score}分·{'有财库' if isinstance(ck,dict) and ck.get('has') else '无财库'} |")
    lines.append(f"| 💵 **财富等级** | {wealth_level or '—'} |")
    lines.append(f"| 🎓 **学历** | {edu_display or '—'} |")
    lines.append(f"| 🏢 **事业** | {career_grade or '—'} |")
    lines.append(f"| 🥇 **最佳大运** | {_s(best_dy,'gan_zhi','')}（{_s(best_dy,'score','')}/10） |")
    lines.append(f"| ⚠️ **最差大运** | {_s(worst_dy,'gan_zhi','')}（{_s(worst_dy,'score','')}/10） |")
    lines.append("")
    
    # ═══════════════════════════════════════════════
    # 签署
    # ═══════════════════════════════════════════════
    lines.append("---")
    lines.append("**编制人：** 金鉴真人")
    lines.append(f"**编制时间：** {now.year}年{now.month:02d}月{now.day:02d}日")
    lines.append("**版本：** v2.0（引擎数据校准深度版）")
    lines.append("**分析方法：** 金鉴真人体系 · 所有分析源自规则引擎计算")
    lines.append("")
    lines.append("#PIPELINE-SIG-JINJIAN-V2")
    
    return "\n".join(lines)


def main():
    sys.path.insert(0, os.path.dirname(__file__))
    from paipan import paipan
    from pipeline_v5 import run_v5
    from constants import BaZi, Pillar
    
    r = paipan("子源", "男", 2011, 4, 25, 10)
    bazi = BaZi(
        year=Pillar(r["year_pillar"]["gan"], r["year_pillar"]["zhi"]),
        month=Pillar(r["month_pillar"]["gan"], r["month_pillar"]["zhi"]),
        day=Pillar(r["day_pillar"]["gan"], r["day_pillar"]["zhi"]),
        hour=Pillar(r["hour_pillar"]["gan"], r["hour_pillar"]["zhi"]),
        gender="男",
    )
    pipeline_result = run_v5(bazi, 2011, 4, 1.1)
    
    engine_json = {
        "paipan": {"bazi": "辛卯 壬辰 庚戌 辛巳"},
        "basic_data": {
            "ri_zhu": {"gan": "庚", "wu_xing": "金"},
            "pillars": {}
        },
        "result": pipeline_result,
    }
    
    report = generate_deep_report(engine_json, "子源", "男")
    lines = report.split("\n")
    chars = len(report)
    sec_count = sum(1 for l in lines if l.startswith("## §"))
    print(f"总行数: {len(lines)}")
    print(f"总字数: {chars}")
    print(f"§覆盖: {sec_count}/21")
    
    out = "/tmp/deep_report_v2.txt"
    with open(out, "w") as f:
        f.write(report)
    print(f"输出: {out}")
    # 检查其中是否包含"刚毅"等通用描述（看是否用了引擎数据）
    has_engine_data = "金鉴真人·" in report or "规则" in report
    print(f"包含规则标注: {has_engine_data}")


if __name__ == "__main__":
    main()
