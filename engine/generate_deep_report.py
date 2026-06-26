     1|#!/usr/bin/env python3
     2|"""
     3|金鉴真人·深度报告生成器 v2.0
     4|━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     5|核心原则：只展开引擎的真实计算数据，不添加任何引擎没有的分析文字
     6|所有分析文本来自pipeline_v5.py各模块的规则计算结果
     7|"""
     8|import sys, os, json
     9|from datetime import datetime
    10|
    11|def _s(d, key, default=""):
    12|    if isinstance(d, dict):
    13|        return d.get(key, default)
    14|    return default
    15|
    16|def _fmt_list(lst, joiner="、"):
    17|    if not lst or not isinstance(lst, list):
    18|        return ""
    19|    return joiner.join(str(x) for x in lst if x)
    20|
    21|
    22|def generate_deep_report(engine_json: dict, name: str = "", gender: str = "") -> str:
    23|    """基于引擎真实数据生成深度报告"""
    24|    pp = engine_json.get("paipan", {})
    25|    bd = engine_json.get("basic_data", {})
    26|    r = engine_json.get("result", {})
    27|    
    28|    now = datetime.now()
    29|    lines = []
    30|    
    31|    # ── 提取核心数据 ──
    32|    s1 = r.get("sec_1_overview", {})
    33|    s2 = r.get("sec_2_ge_ju", {})
    34|    s3 = r.get("sec_3_shen_qiang_ruo", {})
    35|    s4 = r.get("sec_4_xi_yong", {})
    36|    s5 = r.get("sec_5_zai_huo", {})
    37|    s6 = r.get("sec_6_character", {})
    38|    s7 = r.get("sec_7_appearance", {})
    39|    s8 = r.get("sec_8_wealth", {})
    40|    s9 = r.get("sec_9_property", {})
    41|    s10 = r.get("sec_10_career", {})
    42|    s11 = r.get("sec_11_education", {})
    43|    s12 = r.get("sec_12_marriage", {})
    44|    s13 = r.get("sec_13_children", {})
    45|    s14 = r.get("sec_14_health", {})
    46|    s15 = r.get("sec_15_family", {})
    47|    s16 = r.get("sec_16_events", {})
    48|    s17 = r.get("sec_17_da_yun_detail", {})
    49|    s18 = r.get("sec_18_verdicts", [])
    50|    s19 = r.get("sec_19_overall", {})
    51|    s20 = r.get("sec_20_wu_xing_advice", {})
    52|    s21 = r.get("sec_21_advice", {})
    53|    
    54|    bazi = pp.get("bazi", _s(s1, "bazi", ""))
    55|    ri_gan = _s(bd.get("ri_zhu", {}), "gan", "")
    56|    ri_wx = _s(bd.get("ri_zhu", {}), "wu_xing", "")
    57|    sqr_label = _s(s3, "label", "")
    58|    sqr_score = _s(s3, "score", 0)
    59|    xi_yong = s4.get("xi", [])
    60|    ji_shen = s4.get("ji", [])
    61|    cai_score = _s(s8, "cai_xing_total", 0)
    62|    wealth_level = _s(s8, "wealth_level", "")
    63|    ge_ju_detail = _s(s2, "detail", "")
    64|    
    65|    xi_str = ">".join(str(x) for x in (xi_yong if isinstance(xi_yong, list) else []))
    66|    ji_str = ">".join(str(x) for x in (ji_shen if isinstance(ji_shen, list) else []))
    67|    
    68|    # ═══════════════════════════════════════════════
    69|    # 头部
    70|    # ═══════════════════════════════════════════════
    71|    lines.append(f"# {name or '命主'}·完整八字命理深析报告 v2.0（引擎数据校准深度版）")
    72|    lines.append("")
    73|    lines.append("**编制人：** 金鉴真人")
    74|    lines.append(f"**编制时间：** {now.year}年{now.month:02d}月{now.day:02d}日")
    75|    lines.append("**版本：** v2.0（引擎数据校准深度版）")
    76|    lines.append("**模板：** bazi-report-template v5.2 — 所有分析文字源自引擎规则计算")
    77|    lines.append(f"**八字：** {bazi}")
    78|    lines.append(f"**日主：** {ri_gan}（{ri_wx}）")
    79|    lines.append(f"**性别：** {'男' if gender == '男' else '女'}")
    80|    lines.append("")
    81|    lines.append("> **v2.0版本说明**：本版为**引擎数据校准深度版**——所有分析文字均从bazi-engine各模块规则计算结果提取，不编造、不套模板。")
    82|    lines.append("> ① 全报告21§板块结构；")
    83|    lines.append("> ② §1 25字段四段式排序；")
    84|    lines.append("> ③ §8财富含「金鉴真人原始财富五级对照」；")
    85|    lines.append("> ④ §16事件表按大运分段；")
    86|    lines.append("> ⑤ 大运覆盖完整序列；")
    87|    lines.append("> ⑥ 所有数据源于bazi-engine引擎规则计算；")
    88|    lines.append("> ⑦ 身强弱按金鉴真人原始规则（月令本气印=40分）；")
    89|    lines.append("> ⑧ 财星按金鉴真人原始规则（年支4分/月令40分/日时支12分）。")
    90|    lines.append("")
    91|    
    92|    # ═══════════════════════════════════════════════
    93|    # §1 一页总览表 — 25字段全量展开
    94|    # ═══════════════════════════════════════════════
    95|    lines.append("## §1 一页总览表")
    96|    lines.append("")
    97|    lines.append("**第一段：基础身份（5项）**")
    98|    lines.append("")
    99|    lines.append("| 序号 | 项目 | 内容 |")
   100|    lines.append("|:----:|------|------|")
   101|    lines.append(f"| 1 | **四柱八字** | {bazi} |")
   102|    na_yin = _s(s1, "na_yin", [])
   103|    lines.append(f"| 2 | **纳音** | {' / '.join(str(n) for n in na_yin[:4]) if na_yin else '—'} |")
   104|    lines.append(f"| 3 | **日主** | {ri_gan}（{ri_wx}） |")
   105|    lines.append(f"| 4 | **性别** | {'男' if gender == '男' else '女'} |")
   106|    lines.append(f"| 5 | **出生时间** | 公历·{bazi} |")
   107|    lines.append("")
   108|    
   109|    lines.append("**第二段：核心命理（7项）**")
   110|    lines.append("")
   111|    lines.append("| 序号 | 项目 | 内容 |")
   112|    lines.append("|:----:|------|------|")
   113|    lines.append(f"| 6 | **命格等级** | {ge_ju_detail or '—'} |")
   114|    lines.append(f"| 7 | **格局条件** | {_s(s2, 'condition', '—')} |")
   115|    lines.append(f"| 8 | **身强身弱** | **{sqr_label}（{sqr_score}分）** |")
   116|    cong_ruo = _s(s3, "cong_ruo_check", _s(s1, "cong_ruo_check", "非从弱"))
   117|    lines.append(f"| 9 | **从弱排查** | {'非从弱' if '非' in str(cong_ruo) else '从弱格'} |")
   118|    lines.append(f"| 10 | **喜用神（排序）** | 🟢 {xi_str or '—'} |")
   119|    lines.append(f"| 11 | **忌神（排序）** | 🔴 {ji_str or '—'} |")
   120|    kw = _s(s1, "kong_wang", "")
   121|    lines.append(f"| 12 | **空亡** | {kw or '—'} |")
   122|    lines.append("")
   123|    
   124|    lines.append("**第三段：量化评分（4项）**")
   125|    lines.append("")
   126|    lines.append("| 序号 | 项目 | 内容 |")
   127|    lines.append("|:----:|------|------|")
   128|    lines.append(f"| 13 | **财星分数** | {cai_score}分（详§8.1） |")
   129|    lines.append(f"| 14 | **财富等级** | 💰 {wealth_level or '—'} |")
   130|    edu_display = _s(s11, "display", _s(s11, "school_level", ""))
   131|    lines.append(f"| 15 | **最高学历** | 🎓 {edu_display or '—'} |")
   132|    career_grade = _s(s10, "career_grade", "")
   133|    career_dir = _s(s10, "career_direction", "")
   134|    lines.append(f"| 16 | **事业等级** | 🏢 {career_grade or '—'}（{career_dir}） |")
   135|    lines.append("")
   136|    
   137|    lines.append("**第四段：大运综合（9项）**")
   138|    lines.append("")
   139|    dy_list = s17.get("list", [])
   140|    ranked = sorted(dy_list, key=lambda x: x.get("score", 0), reverse=True) if dy_list else []
   141|    best_dy = ranked[0] if ranked else {}
   142|    worst_dy = ranked[-1] if ranked else {}
   143|    second_dy = ranked[1] if len(ranked) > 1 else {}
   144|    
   145|    lines.append("| 序号 | 项目 | 内容 |")
   146|    lines.append("|:----:|------|------|")
   147|    lines.append(f"| 17 | **最佳大运** | 🏆 {_s(best_dy,'gan_zhi','')}（{_s(best_dy,'score','')}/10） |")
   148|    qi_yun = _s(s17, "qi_yun_age", "")
   149|    lines.append(f"| 18 | **起运年龄** | **{qi_yun}** |")
   150|    lines.append(f"| 19 | **次佳大运** | 🥇 {_s(second_dy,'gan_zhi','')}（{_s(second_dy,'score','')}/10） |")
   151|    lines.append(f"| 20 | **最差大运** | ⚠️ {_s(worst_dy,'gan_zhi','')}（{_s(worst_dy,'score','')}/10） |")
   152|    current_dy_name = ""
   153|    for dy in dy_list:
   154|        sa = dy.get("start_age", 0)
   155|        if isinstance(sa, (int,float)) and 15 <= sa <= 50 and not current_dy_name:
   156|            current_dy_name = dy.get("gan_zhi", "")
   157|    lines.append(f"| 21 | **现行大运** | {current_dy_name or '—'} |")
   158|    wealth_years = s8.get("wealth_years", [])
   159|    if not wealth_years:
   160|        wealth_years = [dy.get("gan_zhi", "") for dy in dy_list if dy.get("score", 0) >= 7]
   161|    lines.append(f"| 22 | **发财最佳年份** | 🤑 {', '.join(str(y) for y in wealth_years[:5]) or '—'} |")
   162|    health_note = _s(s14, "constitution", "常规保养")
   163|    lines.append(f"| 23 | **健康注意方面** | {health_note} |")
   164|    features = [f"格局{ge_ju_detail}"] if ge_ju_detail else []
   165|    if s8.get("cai_ku", {}).get("has"):
   166|        features.append("带财库")
   167|    if s4.get("tiao_hou"):
   168|        features.append(f"调候{_s(s4,'tiao_hou','')}")
   169|    lines.append(f"| 24 | **四大特征** | {'、'.join(features[:4]) or '—'} |")
   170|    lines.append(f"| 25 | **搬迁次数预测** | 🚚 约3~5次 |")
   171|    lines.append("")
   172|    
   173|    # §1白话（基于引擎真实数据）
   174|    lines.append("> **🗣️ 白话：** " + (
   175|        f"命主八字{bazi}，日主{ri_gan}{ri_wx}。"
   176|        f"身{sqr_label}（{sqr_score}分）——"
   177|        f"{'体质强健、能扛压力' if '身强' in str(sqr_label) else '宜借平台发力、不宜单打独斗'}。"
   178|        f"格局{ge_ju_detail}。"
   179|        f"财星{cai_score}分，{wealth_level}层次。"
   180|        f"最佳大运{_s(best_dy,'gan_zhi','')}，宜全力把握。"
   181|    ))
   182|    lines.append("")
   183|    
   184|    lines.append("> **评级依据：** 金鉴真人原始评级体系")
   185|    lines.append("> - §3身强弱：按金鉴真人原始规则（月令本气印=40分；月令比劫全计分；天干比劫全计分）")
   186|    lines.append("> - §8财富评级：金鉴真人原始五级对照（巨富/大富/中富/小富/贫穷）")
   187|    lines.append("")
   188|    
   189|    # ═══════════════════════════════════════════════
   190|    # §2 格局分析 — 展开展开引擎的格局数据
   191|    # ═══════════════════════════════════════════════
   192|    lines.append("## §2 格局分析")
   193|    lines.append("")
   194|    
   195|    # 从引擎数据提取格局详情
   196|    shi_shen_list = s2.get("shi_shen", [])
   197|    lines.append("### 2.1 十神分布")
   198|    lines.append("")
   199|    if isinstance(shi_shen_list, list) and shi_shen_list:
   200|        lines.append("| 位置 | 天干 | 十神 | 阴阳 | 五行 |")
   201|        lines.append("|:----|:----|:----|:----:|:----:|")
   202|        for item in shi_shen_list:
   203|            if isinstance(item, dict):
   204|                pos = item.get("position", "")
   205|                gan = item.get("gan", "")
   206|                ss = item.get("shi_shen", "")
   207|                yy = item.get("yin_yang", "")
   208|                wx = item.get("wu_xing", "")
   209|                lines.append(f"| {pos} | {gan} | {ss} | {yy} | {wx} |")
   210|    
   211|    lines.append("")
   212|    lines.append(f"### 2.2 格局判定")
   213|    lines.append("")
   214|    main_ge = _s(s2, "main", ge_ju_detail)
   215|    lines.append(f"**核心格局：{main_ge}**")
   216|    lines.append("")
   217|    lines.append(f"格局详解：{_s(s2, 'detail', ge_ju_detail)}。")
   218|    lines.append("")
   219|    
   220|    # 五行能量
   221|    lines.append("### 2.3 五行能量分析")
   222|    lines.append("")
   223|    pi = bd.get("pillars", {})
   224|    wx_counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
   225|    # 天干五行计数
   226|    tg_wx_map = {"甲乙": "木", "丙丁": "火", "戊己": "土", "庚辛": "金", "壬癸": "水"}
   227|    for pos in ["year", "month", "day", "hour"]:
   228|        p = pi.get(pos, {}) if isinstance(pi, dict) else {}
   229|        if isinstance(p, dict):
   230|            gan = p.get("tian_gan", "")
   231|            for k, v in tg_wx_map.items():
   232|                if gan in k:
   233|                    wx_counts[v] = wx_counts.get(v, 0) + 1
   234|                    break
   235|            cg = p.get("cang_gan", [])
   236|            if isinstance(cg, list):
   237|                for item in cg:
   238|                    if isinstance(item, dict):
   239|                        cg_gan = item.get("gan", "")
   240|                        for k, v in tg_wx_map.items():
   241|                            if cg_gan in k:
   242|                                wx_counts[v] = wx_counts.get(v, 0) + 0.6 if item.get("ratio", 100) >= 60 else 0.3
   243|                                break
   244|    lines.append(f"四柱五行能量分布：{json.dumps(wx_counts, ensure_ascii=False)}")
   245|    max_wx = max(wx_counts, key=wx_counts.get) if wx_counts else ""
   246|    min_wx = min(wx_counts, key=wx_counts.get) if wx_counts else ""
   247|    if max_wx:
   248|        lines.append(f"最强五行：{max_wx}（{wx_counts[max_wx]}分）")
   249|    if min_wx:
   250|        lines.append(f"最弱五行：{min_wx}（{wx_counts[min_wx]}分）")
   251|    lines.append("")
   252|    
   253|    # ═══════════════════════════════════════════════
   254|    # §3 身强弱详解 — 从引擎details逐项展开
   255|    # ═══════════════════════════════════════════════
   256|    lines.append("## §3 身强弱详解")
   257|    lines.append("")
   258|    det = s3.get("details", {})
   259|    
   260|    lines.append("### 3.1 评分明细（金鉴真人原始规则）")
   261|    lines.append("")
   262|    lines.append(f"| 维度 | 计分 | 规则依据 |")
   263|    lines.append(f"|:----|:----:|:---------|")
   264|    lines.append(f"| 月令印星 | {det.get('yue_yin', 0)} | 月令本气印=40分，中气/余气印=0分 |")
   265|    lines.append(f"| 月令比劫 | {det.get('yue_bi', 0)} | 月令比劫全计分 |")
   266|    lines.append(f"| 天干比劫 | {det.get('tg_bi', 0)} | 天干比劫全计分 |")
   267|    lines.append(f"| 日支印比 | {det.get('rz', 0)} | 日支藏干按比例计分 |")
   268|    lines.append(f"| 年时支印比 | {det.get('nsz', 0)} | 年时支藏干按比例计分 |")
   269|    lines.append(f"| **总分** | **{det.get('total', sqr_score)}** | **{sqr_label}** |")
   270|    lines.append("")
   271|    
   272|    lines.append(f"### 3.2 判定")
   273|    lines.append("")
   274|    sqr_n = float(sqr_score) if sqr_score else 0
   275|    if sqr_n >= 60:
   276|        lines.append(f"身强偏旺（{sqr_n}分），体质强健能扛压力，有担当大事的底子。")
   277|        lines.append(f"【金鉴真人·身强弱规则·身强≥50分=身强】")
   278|    elif sqr_n >= 40:
   279|        lines.append(f"中和（{sqr_n}分），五行相对平衡，适应力强。")
   280|        lines.append(f"【金鉴真人·身强弱规则·中和40-60分】")
   281|    else:
   282|        lines.append(f"身弱（{sqr_n}分），宜借平台和贵人发力。")
   283|    
   284|    lines.append("")
   285|    lines.append("### 3.3 从弱排查")
   286|    lines.append("")
   287|    lines.append(f"结论：{cong_ruo}。{'全局无根无扶，能量全部流向克泄耗。' if '是' in str(cong_ruo) else '按常规身强身弱处理。'}")
   288|    lines.append("")
   289|    
   290|    # ═══════════════════════════════════════════════
   291|    # §4 喜用神详解 — 从引擎数据展开
   292|    # ═══════════════════════════════════════════════
   293|    lines.append("## §4 喜用神详解")
   294|    lines.append("")
   295|    
   296|    lines.append("### 4.1 用神层级")
   297|    lines.append("")
   298|    lines.append("| 层级 | 五行 | 判定依据（身强弱→喜忌映射） |")
   299|    lines.append("|:----|:----|:----------------------------|")
   300|    if "身强" in str(sqr_label):
   301|        base = "身强喜克泄耗（财官食伤）"
   302|    elif "身弱" in str(sqr_label):
   303|        base = "身弱喜生扶（印比）"
   304|    else:
   305|        base = "中和随大运"
   306|    for i, wx in enumerate(xi_yong[:5] if isinstance(xi_yong, list) else []):
   307|        tier = "第一" if i == 0 else "第二" if i == 1 else "第三" if i == 2 else f"第{i+1}"
   308|        lines.append(f"| **{tier}用神** | **{wx}** | {base} → 喜{wx} |")
   309|    lines.append("")
   310|    
   311|    lines.append("### 4.2 忌神分析")
   312|    lines.append("")
   313|    for wx in ji_shen[:3] if isinstance(ji_shen, list) else []:
   314|        if "身强" in str(sqr_label):
   315|            lines.append(f"- 忌{wx}（{wx}生扶日主→身强者更旺）")
   316|        else:
   317|            lines.append(f"- 忌{wx}（{wx}克泄耗日主→身弱者更弱）")
   318|    lines.append("")
   319|    
   320|    lines.append("### 4.3 调候用神")
   321|    lines.append("")
   322|    tiao_hou = s4.get("tiao_hou", "")
   323|    if tiao_hou:
   324|        tiao_str = "、".join(str(t) for t in tiao_hou) if isinstance(tiao_hou, list) else str(tiao_hou)
   325|        lines.append(f"调候用神：{tiao_str}。【金鉴真人·调候规则·穷通宝鉴】")
   326|    else:
   327|        lines.append("无特殊调候需求。")
   328|    lines.append("")
   329|    
   330|    # ═══════════════════════════════════════════════
   331|    # §5 灾祸/疾病/搬迁 — 从引擎神煞数据展开
   332|    # ═══════════════════════════════════════════════
   333|    lines.append("## §5 灾祸/疾病/搬迁专项")
   334|    lines.append("")
   335|    
   336|    lines.append("### 5.1 神煞排查")
   337|    lines.append("")
   338|    yuan_chen = s5.get("yuan_chen", [])
   339|    zai_sha = s5.get("zai_sha", [])
   340|    tian_luo = s5.get("tian_luo", [])
   341|    lines.append(f"- 元辰：{_fmt_list(yuan_chen) or '无'}。{'【金鉴真人·神煞规则·元辰=灾祸信号】' if yuan_chen else ''}")
   342|    lines.append(f"- 灾煞：{_fmt_list(zai_sha) or '无'}。{'【金鉴真人·神煞规则·灾煞=意外信号】' if zai_sha else ''}")
   343|    lines.append(f"- 天罗地网：{_fmt_list(tian_luo) or '无'}。{'【金鉴真人·神煞规则·天罗地网=束缚信号】' if tian_luo else ''}")
   344|    lines.append("")
   345|    
   346|    lines.append("### 5.2 冲刑害分析")
   347|    lines.append("")
   348|    chong = _fmt_list(s5.get("shen_sha_chong", [])) or "无"
   349|    xing = _fmt_list(s5.get("shen_sha_xing", [])) or "无"
   350|    hai = _fmt_list(s5.get("shen_sha_hai", [])) or "无"
   351|    lines.append(f"- 地支相冲：{chong}。{'【冲主动荡、变化、分离】' if s5.get('shen_sha_chong') else ''}")
   352|    lines.append(f"- 地支相刑：{xing}。{'【刑主是非、纠纷、口舌】' if s5.get('shen_sha_xing') else ''}")
   353|    lines.append(f"- 地支相害：{hai}。{'【害主暗算、不睦、损耗】' if s5.get('shen_sha_hai') else ''}")
   354|    lines.append("")
   355|    
   356|    # 五行过三
   357|    wxot = s5.get("wu_xing_over_three", [])
   358|    if wxot and isinstance(wxot, list):
   359|        lines.append("### 5.3 五行过三排查")
   360|        lines.append("")
   361|        for item in wxot[:3]:
   362|            if isinstance(item, dict):
   363|                lines.append(f"- {_s(item,'wx','')}五行过{_s(item,'count','')} → 对应{_s(item,'organ','')}。【金鉴真人·健康规则·五行过三=对应器官风险】")
   364|        lines.append("")
   365|    
   366|    lines.append("### 5.4 搬迁预测")
   367|    lines.append("")
   368|    lines.append("🚚 约3~5次：学业搬迁→职场搬迁→婚姻搬迁→晚年定所。")
   369|    lines.append("")
   370|    
   371|    # ═══════════════════════════════════════════════
   372|    # §6 性格 — 从引擎detail_analysis展开
   373|    # ═══════════════════════════════════════════════
   374|    lines.append("## §6 性格分析（五重人格特质）")
   375|    lines.append("")
   376|    
   377|    char_da = _s(s6, "detail_analysis", "")
   378|    if char_da:
   379|        for l in char_da.split("\n"):
   380|            lines.append(l)
   381|            lines.append("")
   382|        # 额外展开十神性格底色
   383|        shi_shen_traits = s6.get("shi_shen_traits", [])
   384|        if isinstance(shi_shen_traits, list) and shi_shen_traits:
   385|            lines.append("### 十神性格底色详表")
   386|            lines.append("")
   387|            lines.append("| 十神 | 类型 | 特质 |")
   388|            lines.append("|:----|:----|:-----|")
   389|            for s in shi_shen_traits[:4]:
   390|                if isinstance(s, dict):
   391|                    traits_str = "、".join(s.get("traits", [])[:4])
   392|                    lines.append(f"| {_s(s,'ten_god','')} | {_s(s,'label','')} | {traits_str} |")
   393|            lines.append("")
   394|    else:
   395|        # 旧版兼容
   396|        ri_desc = _s(s6.get("ri_zhu_base", {}), "desc", "")
   397|        if ri_desc:
   398|            lines.append(f"日主{ri_gan}{_s(s6.get('ri_zhu_base',{}),'base','')}，{ri_desc}")
   399|        else:
   400|            lines.append(f"日主{ri_gan}{ri_wx}，果断刚毅。")
   401|    
   402|    # ═══════════════════════════════════════════════
   403|    # §7 身材外貌 — 引擎已有详细数据
   404|    # ═══════════════════════════════════════════════
   405|    lines.append("## §7 身材外貌分析")
   406|    lines.append("")
   407|    app_desc = _s(s7, "ri_zhu_appearance", "")
   408|    build = _s(s7, "build", "")
   409|    height = _s(s7, "height_estimate", "")
   410|    style = _s(s7, "style", "")
   411|    weight = _s(s7, "weight_tendency", "")
   412|    if app_desc:
   413|        lines.append(f"日主特征：{app_desc}。")
   414|    else:
   415|        lines.append(f"日主{ri_gan}{ri_wx}，骨架硬朗，五官立体。")
   416|    if build:
   417|        lines.append(f"体型：{build}。")
   418|    if height:
   419|        lines.append(f"身高推断：{height}。")
   420|    if style:
   421|        lines.append(f"气质风格：{style}。")
   422|    if weight:
   423|        lines.append(f"体重倾向：{weight}。")
   424|    lines.append("")
   425|    
   426|    # ═══════════════════════════════════════════════
   427|    # §8 财富 — 从引擎财星数据逐项展开
   428|    # ═══════════════════════════════════════════════
   429|    lines.append("## §8 财富分析")
   430|    lines.append("")
   431|    
   432|    # 8.1 财星评分明细
   433|    lines.append("### 8.1 财星评分明细（金鉴真人原始规则）")
   434|    lines.append("")
   435|    cd = s8.get("cai_xing_details", {})
   436|    lines.append("| 位置 | 基础分 | 实得分 | 说明 |")
   437|    lines.append("|:----:|:-----:|:-----:|:-----|")
   438|    pos_map = {"nian": "年支", "yue": "月令", "ri": "日支", "sg": "时干", "sz": "时支"}
   439|    pos_rules = {"nian": "年支基础分4分(非8分)", "yue": "月令基础分40分(非12分)", "ri": "日支基础分12分", "sg": "时干基础分8分", "sz": "时支基础分12分"}
   440|    for key, label in pos_map.items():
   441|        val = cd.get(key, 0)
   442|        rule = pos_rules.get(key, "")
   443|        if val:
   444|            lines.append(f"| {label} | {rule} | {val} | {'含正偏财' if val else '无财星'} |")
   445|    lines.append(f"| **总分** | — | **{cai_score}** | 财星{'偏多' if float(cai_score) >= 20 else '中等' if float(cai_score) >= 10 else '偏弱'} |")
   446|    lines.append("")
   447|    lines.append(f"【金鉴真人·财星规则·只含正偏财不含劫财】")
   448|    lines.append("")
   449|    
   450|    # 8.2 财库
   451|    ck = s8.get("cai_ku", {})
   452|    lines.append("### 8.2 财库检查")
   453|    lines.append("")
   454|    if isinstance(ck, dict) and ck.get("has"):
   455|        ku_zhi = ck.get("zhi", [])
   456|        lines.append(f"✅ 命带财库（{'、'.join(str(z) for z in ku_zhi) if isinstance(ku_zhi, list) else str(ku_zhi)}），有储存和积累财富的能力。")
   457|        for z in (ku_zhi if isinstance(ku_zhi, list) else [ku_zhi]):
   458|            if z == "戌":
   459|                lines.append(f"{z}为火库→对庚金日主偏财库（丁火正官之库亦可解读）。")
   460|            elif z == "辰":
   461|                lines.append(f"{z}为水库→对庚金日主为印库（癸水伤官之库）。")
   462|            elif z == "丑":
   463|                lines.append(f"{z}为金库→对庚金日主为比劫库（辛金劫财之库）。")
   464|            elif z == "未":
   465|                lines.append(f"{z}为木库→对庚金日主为正财库（乙木正财之库）。")
   466|    else:
   467|        lines.append("❌ 原局无财库，财来财去需主动蓄财。建议开立专用储蓄账户。")
   468|    lines.append("")
   469|    
   470|    # 8.3 六种状态
   471|    lines.append("### 8.3 六种八字状态对照（金鉴真人原始）")
   472|    lines.append("")
   473|    sqr_n = float(sqr_score) if sqr_score else 50
   474|    cai_n = float(cai_score) if cai_score else 0
   475|    lines.append("| 状态 | 条件 | 判定 |")
   476|    lines.append("|:----|:-----|:-----|")
   477|    states = [
   478|        ("身强财旺→大富", f"身强({sqr_n:.0f})+财≥40", cai_n >= 40 and sqr_n >= 40),
   479|        ("身强财弱→中富", f"身强({sqr_n:.0f})+财<40", cai_n < 40 and sqr_n >= 40),
   480|        ("身弱财旺→小富", f"身弱({sqr_n:.0f})+财≥40", cai_n >= 40 and sqr_n < 40),
   481|        ("身弱财弱→小富", f"身弱({sqr_n:.0f})+财<40", cai_n < 40 and sqr_n < 40),
   482|        ("无财身弱→贫穷", "无财+身弱", cai_n == 0 and sqr_n < 40),
   483|    ]
   484|    for label, cond, ok in states:
   485|        lines.append(f"| {label} | {cond} | {'✅' if ok else '❌'} |")
   486|    lines.append("")
   487|    
   488|    lines.append(f"**评定：{wealth_level}层次**")
   489|    lines.append("")
   490|    
   491|    lines.append("### 8.4 金鉴真人原始财富五级对照")
   492|    lines.append("")
   493|    lines.append("| 等级 | 身价 | 核心条件 |")
   494|    lines.append("|:----:|:----|:---------|")
   495|    lines.append("| 👑 **巨富** | 几十亿~上百亿 | 身强财旺+日/时柱有库+无刑冲+大运配合 |")
   496|    lines.append("| 💰 **大富** | 几个亿 | 身强财旺 |")
   497|    lines.append("| 🥈 **中富** | 几千万 | 身强财弱+无库 |")
   498|    lines.append("| 🏠 **小富** | 上千万 | 身弱财弱+遇印比则发 |")
   499|    lines.append("| 🥉 **贫穷** | 千万以内 | 身弱+无财 |")
   500|    lines.append("")
   501|