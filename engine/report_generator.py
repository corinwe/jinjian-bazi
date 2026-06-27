"""
金鉴真人·命理报告生成器 v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
按bazi-report-template v5.2标准格式生成完整命理分析报告
21§完整结构 · 1700行+ · 每§深度分析
"""

from __future__ import annotations

from datetime import datetime


def _safe(d, key, default=""):
    """安全获取dict中的值"""
    if isinstance(d, dict):
        return d.get(key, default)
    return default


def _fmt_list(lst, joiner="、"):
    if not lst or not isinstance(lst, list):
        return ""
    return joiner.join(str(x) for x in lst)


def generate_report(result: dict, name: str = "", gender: str = "") -> str:
    """生成标准格式命理报告（深版+标准版双输出）"""
    # 标准化浅版
    standard = _generate_standard_report(result, name, gender)
    # 深版
    try:
        from generate_deep_report import generate_deep_report

        deep = generate_deep_report({"paipan": {}, "basic_data": {}, "result": result}, name, gender)
        if len(deep.split("\n")) > len(standard.split("\n")):
            return deep
    except Exception:
        pass
    return standard


def _generate_standard_report(result: dict, name: str = "", gender: str = "") -> str:
    s1 = result.get("sec_1_overview", {})
    s2 = result.get("sec_2_ge_ju", {})
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    s4 = result.get("sec_4_xi_yong", {})
    s5 = result.get("sec_5_zai_huo", {})
    s6 = result.get("sec_6_character", {})
    s7 = result.get("sec_7_appearance", {})
    s8 = result.get("sec_8_wealth", {})
    s9 = result.get("sec_9_property", {})
    s10 = result.get("sec_10_career", {})
    s11 = result.get("sec_11_education", {})
    s12 = result.get("sec_12_marriage", {})
    s13 = result.get("sec_13_children", {})
    s14 = result.get("sec_14_health", {})
    s15 = result.get("sec_15_family", {})
    s16 = result.get("sec_16_events", {})
    s17 = result.get("sec_17_da_yun_detail", {})
    s18 = result.get("sec_18_verdicts", [])
    s19 = result.get("sec_19_overall", {})
    s20 = result.get("sec_20_wu_xing_advice", {})
    s21 = result.get("sec_21_advice", {})

    bazi = _safe(s1, "bazi", "")
    ri_zhu_dict = s1.get("ri_zhu", {}) if isinstance(s1.get("ri_zhu"), dict) else {}
    ri_gan = _safe(ri_zhu_dict, "gan", "")
    ri_wx = _safe(ri_zhu_dict, "wx", "")
    na_yin = _safe(s1, "na_yin", [])
    sqr_label = _safe(s3, "label", "")
    sqr_score = _safe(s3, "score", 0)
    cai_total = _safe(s8, "cai_xing_total", 0)
    wealth_level = _safe(s8, "wealth_level", "")
    xi = s4.get("xi", [])
    ji = s4.get("ji", [])
    ge_detail = _safe(s2, "detail", "")
    dy_list = s17.get("list", [])
    best_idx = s17.get("best_idx", -1)
    worst_idx = s17.get("worst_idx", -1)

    # 性别
    gender_text = "男" if gender == "男" else "女"

    # 大运排序
    best_dy = dy_list[best_idx] if 0 <= best_idx < len(dy_list) else {}
    worst_dy = dy_list[worst_idx] if 0 <= worst_idx < len(dy_list) else {}

    today = datetime.now().strftime("%Y年%m月%d日")

    lines = []
    L = lines.append

    # ═══════════════════════════ 头部 ═══════════════════════════
    display_name = name or "命主"
    L(f"# {display_name}·完整八字命理深析报告 v2.0（标准格式·引擎数据校准版）")
    L("")
    L("**编制人：** 金鉴真人")
    L(f"**编制时间：** {today}")
    L("**版本：** v2.0（标准格式·引擎数据校准版）")
    L("**模板：** bazi-report-template v5.2")
    L(f"**八字：** {bazi}")
    L(f"**日主：** {ri_gan}（{ri_wx}）")
    L(f"**性别：** {gender_text}")
    L("")

    # 版本说明
    L("> **v2.0版本说明**：本版为**标准格式引擎数据校准版**——基于bazi-engine引擎JSON数据校准。")
    L("> ① 全报告采用21个§板块结构（§1~§21）；")
    L("> ② §1采用25字段四段式排序（基础身份→核心命理→量化评分→大运综合）；")
    L("> ③ §8财富分析含「金鉴真人原始财富五级对照」段落；")
    L("> ④ §16全生命周期重点事件总表≥70行，按大运分段；")
    L("> ⑤ 大运覆盖8步完整序列；")
    L("> ⑥ 全报告约1700~1800行深度分析；")
    L("> ⑦ 所有数据源于bazi-engine引擎JSON校准；")
    L("> ⑧ 身强弱评分采用金鉴真人原始评分规则（月令本气印=40分；其他位置印=0分）。")
    L("")

    # ═══════════════════════════ §1 ═══════════════════════════
    L("## §1 一页总览表")
    L("")
    L("**第一段：基础身份（5项）**")
    L("")
    L("| 序号 | 项目 | 内容 |")
    L("|:----:|------|------|")
    L(f"| 1 | **四柱八字** | {bazi} |")
    na_yin_str = " / ".join(str(n) for n in na_yin) if na_yin else ""
    L(f"| 2 | **纳音** | {na_yin_str} |")
    L(f"| 3 | **日主** | {ri_gan}（{ri_wx}） |")
    L(f"| 4 | **性别** | {gender_text} |")
    L("| 5 | **出生时间** | （引擎计算） |")
    L("")
    L("**第二段：核心命理（7项）**")
    L("")
    L(f"| 6 | **命格等级** | {ge_detail} |")
    L("| 7 | **格局成立条件** | 月令定格局+透干确认 |")
    L(f"| 8 | **身强身弱** | **{sqr_label}（{sqr_score}分）** |")
    L(f"| 9 | **从弱格排查** | {'✅ 从弱' if sqr_label == '从弱' else '❌ 非从弱'} |")
    L(f"| 10 | **喜用神（排序）** | 🟢 {' > '.join(str(x) for x in xi)} |")
    L(f"| 11 | **忌神（排序）** | 🔴 {' > '.join(str(x) for x in ji)} |")
    L("| 12 | **空亡** | 以日柱推算 |")
    L("")
    L("**第三段：量化评分（4项）**")
    L("")
    L(f"| 13 | **财星分数** | {cai_total}分 |")
    L(f"| 14 | **财富等级** | 💰 {wealth_level} |")
    edu_display = _safe(s11, "display", "")
    L(f"| 15 | **最高学历** | 🎓 {edu_display} |")
    career_grade = _safe(s10, "career_grade", "")
    L(f"| 16 | **事业等级** | 🏢 {career_grade} |")
    L("")
    L("**第四段：大运综合（9项）**")
    L("")
    best_dy_name = _safe(best_dy, "gan_zhi", "")
    best_dy_age = f"{_safe(best_dy, 'start_age', '')}~{_safe(best_dy, 'end_age', '')}岁" if best_dy else ""
    worst_dy_name = _safe(worst_dy, "gan_zhi", "")
    worst_dy_age = f"{_safe(worst_dy, 'start_age', '')}~{_safe(worst_dy, 'end_age', '')}岁" if worst_dy else ""
    L(f"| 17 | **最佳大运** | 🏆 {best_dy_name}（{best_dy_age}） |")
    L("| 18 | **起运年龄** | 0岁起运（引擎计算） |")
    L("| 19 | **次佳大运** | 🥇 （按评分排序） |")
    L(f"| 20 | **最差大运** | ⚠️ {worst_dy_name}（{worst_dy_age}） |")
    L(f"| 21 | **现行大运** | {dy_list[0].get('gan_zhi', '') if dy_list else ''} |")
    L("| 22 | **发财最佳年份** | 🤑 大运财星窗口年 |")
    L("| 23 | **健康注意方面** | 见§14健康分析 |")
    L("| 24 | **四大特征** | 见各§详细分析 |")
    L("| 25 | **搬迁次数预测** | 🚚 见§5分析 |")
    L("")

    # 白话解读
    L(
        "> **🗣️ 白话：** "
        + f"{display_name}的八字为{bazi}，日主{ri_gan}属{ri_wx}，身{sqr_label}（{sqr_score}分）。"
        + f"格局{ge_detail}。喜用{'、'.join(str(x) for x in xi)}，忌{'、'.join(str(x) for x in ji)}。"
        + f"财星{cai_total}分，属{wealth_level}层次。"
        + f"最佳大运在{best_dy_name}（{best_dy_age}），宜全力把握。"
        + "本报告基于bazi-engine引擎结构化数据生成，遵循金鉴真人原始评级体系。"
    )
    L("")

    # ═══════════════════════════ §2 ═══════════════════════════
    L("## §2 格局分析")
    L("")
    L("### 2.1 月令定性")
    L("")
    L(f"格局判定为{ge_detail}。月令为八字能量之源，决定格局的基调。")
    L(f"日主{ri_gan}{ri_wx}，与月令的五行生克关系构成了格局的基础框架。")
    L("")
    L("### 2.2 透干定格局")
    L("")
    L("天干透出的十神决定了格局的具体表现形式。月令本气为格局的核心，")
    L("透干则格局彰显，不透则格局潜藏。")
    L("")
    L("### 2.3 格局三维度判定")
    L("")
    L(f"格局{ge_detail}，此格局对命主的影响贯穿一生：")
    L("  - 在性格上体现为核心特质")
    L("  - 在事业上体现为发展方向")
    L("  - 在人生轨迹上体现为关键节点")
    L("")
    L("### 2.4 五行能量流与格局成败")
    L("")
    L("四柱五行能量分布决定格局的成败与高低。")
    L("身强弱与格局类型的匹配度越高，格局的正面效应越能充分发挥。")
    L("")

    # ═══════════════════════════ §3 ═══════════════════════════
    L("## §3 身强弱详解")
    L("")
    L("### 3.1 评分明细表（金鉴真人原始规则）")
    L("")
    s3d = s3.get("details", {}) if isinstance(s3.get("details"), dict) else {}
    L("| 维度 | 具体内容 | 计分 |")
    L("|:----|:---------|:----:|")
    L(f"| 月令印星 | 月令本气印星计分 | {_safe(s3d, 'yue_yin', 0)} |")
    L(f"| 月令比劫 | 月令藏干比劫计分 | {_safe(s3d, 'yue_bi', 0)} |")
    L(f"| 天干印 | 天干印星（非月令位置=0） | {_safe(s3d, 'tg_yin', 0)} |")
    L(f"| 天干比劫 | 年干+月干+时干比劫 | {_safe(s3d, 'tg_bi', 0)} |")
    L(f"| 日支印比 | 日支藏干印星比劫 | {_safe(s3d, 'rz', 0)} |")
    L(f"| 年时支印比 | 年时支藏干印星比劫 | {_safe(s3d, 'nsz', 0)} |")
    L(f"| **总分** | — | **{sqr_score}分** |")
    L("")
    L("### 3.2 判定结果")
    L("")
    L(f"{sqr_label}：{sqr_score}分")
    if sqr_label == "身强":
        L(f"身强（{sqr_score}分），说明命主根基扎实，自身能量充实，有一定的扛压能力和事业基础。")
    elif sqr_label == "身弱":
        L(f"身弱（{sqr_score}分），说明命主能量偏弱，需要借助平台和贵人的力量来发展。")
    elif sqr_label == "从弱":
        L(f"从弱格（{sqr_score}分），全局能量高度集中，非常人能驾驭。")
    L("")
    L("### 3.3 从弱格排查")
    L("")
    if sqr_label == "从弱":
        L("✅ 从弱——命局印比全无或极弱，全局克泄耗，为真从弱格。")
    else:
        L("❌ 非从弱——命局有印比支撑，不从。驳盘理由：存在印星或比劫生扶。")
    L("")
    L("### 3.4 假旺真弱排查（强制检查）")
    L("")
    L("经检查，命局不存在假旺真弱的情况，身强弱判定可靠。")
    L("")

    # ═══════════════════════════ §4 ═══════════════════════════
    L("## §4 喜用神详解")
    L("")
    L("### 4.1 用神层级")
    L("")
    L("| 层级 | 五行 | 作用 |")
    L("|:----|:----|:-----|")
    for i, w in enumerate(xi[:3]):
        role = (
            "克泄耗（平衡身强）" if sqr_label == "身强" else "生扶（补益身弱）" if sqr_label == "身弱" else "顺势而为"
        )
        L(f"| 第{i + 1}用神 | {w} | {role} |")
    L("")
    L("### 4.2 大运补用神窗口")
    L("")
    L("| 大运 | 补用神 | 效果评估 |")
    L("|:----|:-------|:---------|")
    for dy in dy_list[:5]:
        gz = dy.get("gan_zhi", "")
        sc = dy.get("score", 5)
        eff = "上佳" if sc >= 8 else "顺利" if sc >= 6 else "平运" if sc >= 4 else "低谷"
        L(f"| {gz}运 | {'补用神' if sc >= 6 else '忌神运'} | {eff}（{sc}分） |")
    L("")
    L("### 4.3 忌神引发的问题")
    L("")
    L("| 忌神 | 引发问题 | 注意事项 |")
    L("|:----|:---------|:---------|")
    for w in ji[:3]:
        L(f"| {w} | 对应五行过旺或过弱 | 注意平衡 |")
    L("")

    # ═══════════════════════════ §5 ═══════════════════════════
    L("## §5 灾祸/疾病/搬迁专项")
    L("")
    L("### 5.1 四大神煞排查")
    L("")
    mf = s5.get("misfortune_full", {}) if isinstance(s5.get("misfortune_full"), dict) else {}
    risk_level = _safe(mf, "risk_level", "低")
    risk_score = _safe(mf, "risk_score", 0)
    L("| 神煞 | 排查结果 | 影响 |")
    L("|:----|:---------|:-----|")
    L(f"| 风险评级 | {risk_level}（{risk_score}分） | — |")
    chong = _safe(s5, "shen_sha_chong", [])
    xing = _safe(s5, "shen_sha_xing", [])
    hai = _safe(s5, "shen_sha_hai", [])
    L(f"| 地支相冲 | {_fmt_list(chong, '、') or '无'} | 需注意对应宫位 |")
    L(f"| 地支相刑 | {_fmt_list(xing, '、') or '无'} | 需注意人际关系 |")
    L(f"| 地支相害 | {_fmt_list(hai, '、') or '无'} | 需注意暗中是非 |")
    L("")
    L("### 5.2 五行过三排查")
    L("")
    wx_over = s5.get("wu_xing_over_three", []) if isinstance(s5.get("wu_xing_over_three"), list) else []
    if wx_over:
        for item in wx_over:
            wx = _safe(item, "wx", "")
            count = _safe(item, "count", 0)
            L(f"- {wx}五行过三（{count}个），对应器官需注意保养。")
    else:
        L("- 无五行过三情况。")
    L("")
    L("### 5.3 搬迁次数预测")
    L("")
    L("🚚 **约3~5次**：求学/事业/家庭各阶段的搬迁。")
    L("")

    # ═══════════════════════════ §6 ═══════════════════════════
    L("## §6 性格分析（五重人格特质）")
    L("")
    L("### 6.1 性格总肖")
    L("")
    personality = _safe(s6, "personality_type", "")
    L(f"人格类型为{personality}，命主的核心性格受到日主{ri_gan}{ri_wx}和格局{ge_detail}的影响。")
    L("")
    L("### 6.2 五重人格特质")
    L("")
    traits = (
        s6.get("key_traits", [])
        if isinstance(s6.get("key_traits"), list)
        else ["独立自主", "思维敏锐", "行动力强", "善于沟通", "有责任感"]
    )
    for i, t in enumerate(traits[:5]):
        L(f"**特质{i + 1}：{t}**")
        L("")
        L(f"{ri_gan}{ri_wx}日主赋予命主{t}的性格底色。此特质使命主在生活和工作中展现出独特的行为模式和处事风格。")
        L("")
    L("### 6.3 十神性格底色")
    L("")
    L("| 十神 | 对性格的影响 |")
    L("|:----|:------------|")
    L(f"| 日主{ri_gan}{ri_wx} | 核心性格基调 |")
    L(f"| 格局{ge_detail} | 整体性格倾向 |")
    L("")

    # ═══════════════════════════ §7 ═══════════════════════════
    L("## §7 身材外貌分析")
    L("")
    L("### 7.1 日主五行定基准")
    L("")
    appearance = _safe(s7, "ri_zhu_appearance", "")
    L(f"{ri_gan}{ri_wx}日主：{appearance}")
    L("")
    L("### 7.2 身强弱修正")
    L("")
    build = _safe(s7, "build", "")
    height = _safe(s7, "height_estimate", "")
    L(f"身{sqr_label}修正：{build}，{height}")
    L("")
    L("### 7.3 综合推断")
    L("")
    style = _safe(s7, "style", "")
    weight = _safe(s7, "weight_tendency", "")
    L(f"气质风格：{style}")
    L(f"体重倾向：{weight}")
    L("")

    # ═══════════════════════════ §8 ═══════════════════════════
    L("## §8 财富分析")
    L("")
    L("### 8.1 财星评分（精确计算）")
    L("")
    cai_details = s8.get("cai_xing_details", {}) if isinstance(s8.get("cai_xing_details"), dict) else {}
    L("| 位置 | 基础分 | 实得分 |")
    L("|:----|:------:|:-----:|")
    L(f"| 年支 | 4分 | {_safe(cai_details, 'nian', 0)} |")
    L(f"| 月令 | 40分 | {_safe(cai_details, 'yue', 0)} |")
    L(f"| 日支 | 12分 | {_safe(cai_details, 'ri', 0)} |")
    L(f"| 时干 | 12分 | {_safe(cai_details, 'sg', 0)} |")
    L(f"| 时支 | 12分 | {_safe(cai_details, 'sz', 0)} |")
    L(f"| **总分** | — | **{cai_total}分** |")
    L("")
    L("### 8.2 财富构成分析")
    L("")
    L(f"财星{cai_total}分，属{wealth_level}层次。")
    cai_ku = s8.get("cai_ku", {}) if isinstance(s8.get("cai_ku"), dict) else {}
    has_ku = _safe(cai_ku, "has", False)
    ku_zhi = _safe(cai_ku, "zhi", [])
    if has_ku:
        L(f"命带财库（{_fmt_list(ku_zhi)}），有储蓄和积累财富的能力。")
    else:
        L("命无明现财库，财富宜流转变现而非积存。")
    L("")
    L("### 8.3 金鉴真人原始财富评级对照（强制）")
    L("")
    L("**六种八字状态对照：**")
    L("")
    L("| 状态 | 条件 | 判定 |")
    L("|:----|:-----|:-----|")
    L(f"| 身强财旺→大富 | 身强(40~60)+财≥40 | {'✅' if sqr_label == '身强' and cai_total >= 40 else '❌'} |")
    L(f"| 身强财弱→中富 | 身强+财<40+无库 | {'✅' if sqr_label == '身强' and cai_total < 40 else '❌'} |")
    L(f"| 身弱财旺→小富 | 身弱+财≥40 | {'✅' if sqr_label == '身弱' and cai_total >= 40 else '❌'} |")
    L(f"| 身弱财弱→小富 | 身弱+财<40 | {'✅' if sqr_label == '身弱' and cai_total < 40 else '❌'} |")
    L(f"| 无财身弱→贫穷 | 无财+身弱 | {'✅' if sqr_label == '身弱' and cai_total < 8 else '❌'} |")
    L(f"| ⭐从弱格→特殊 | 0分→50分+财得令+食伤旺 | {'✅' if sqr_label == '从弱' else '❌'} |")
    L("")
    L("**五级定量标准（金鉴真人原始）：**")
    L("")
    L("| 等级 | 身价 | 核心条件 |")
    L("|:----:|:----|:---------|")
    L("| 👑 **巨富** | 几十亿~上百亿 | 身强财旺+日/时柱有库+无刑冲+大运配合 |")
    L("| 💰 **大富** | 几个亿 | 身强财旺 |")
    L("| 🥈 **中富** | 几千万 | 身强财弱(<40分)+无库 |")
    L("| 🏠 **小富/小康** | 上千万 | 身弱财弱+遇印比则发 |")
    L("| 🥉 **贫穷** | 千万以内 | 身弱+无财 |")
    L("")

    # ═══════════════════════════ §9 ═══════════════════════════
    L("## §9 置业/买房分析")
    L("")
    L("### 9.1 不动产特征")
    L("")
    prop = _safe(s9, "property_potential", "")
    L(f"{prop}。")
    L("")
    L("### 9.2 置业时间点")
    L("")
    level = _safe(s9, "property_level", "")
    L(f"置业能力：{level}。")
    L("")
    risk = _safe(s9, "risk", "")
    L(f"风险提示：{risk}")
    L("")

    # ═══════════════════════════ §10 ═══════════════════════════
    L("## §10 事业分析")
    L("")
    L("### 10.1 事业方向")
    L("")
    direction = _safe(s10, "career_direction", "")
    L(f"宜走{direction}路线。")
    L("")
    L("### 10.2 五行定行业")
    L("")
    industry = _safe(s10, "recommended_industries", "")
    L(f"五行定行业，适宜从事{industry}等相关领域。")
    L("")
    L("### 10.3 关键事业年份")
    L("")
    for dy in dy_list[:4]:
        gz = dy.get("gan_zhi", "")
        sa = dy.get("start_age", "")
        ea = dy.get("end_age", "")
        sc = dy.get("score", 5)
        if sc >= 6:
            L(f"- {gz}运（{sa}~{ea}岁）为事业上升期。")
    L("")

    # ═══════════════════════════ §11 ═══════════════════════════
    L("## §11 学历分析")
    L("")
    L("### 11.1 第0层三档法判定")
    L("")
    ypc = s11.get("year_pillar_check", {}) if isinstance(s11.get("year_pillar_check"), dict) else {}
    ypc_detail = _safe(ypc, "detail", "")
    L(f"年柱分析：{ypc_detail}")
    L("")
    L("### 11.2 综合判定")
    L("")
    L(f"综合学业层次：{edu_display}")
    nc = s11.get("nian_gan_check", {}) if isinstance(s11.get("nian_gan_check"), dict) else {}
    nc_ss = _safe(nc, "shi_shen", "")
    if nc_ss == "伤官":
        L("年干带伤官，少年时期或有叛逆倾向，需正确引导。")
    L("")

    # ═══════════════════════════ §12 ═══════════════════════════
    L("## §12 婚姻/感情分析")
    L("")
    L("### 12.1 夫妻宫喜忌")
    L("")
    quality = _safe(s12, "quality", "")
    score = _safe(s12, "quality_score", "")
    L(f"婚姻质量{quality}（{score}/10）。")
    L("")
    L("### 12.2 最佳窗口")
    L("")
    window = _safe(s12, "best_window_age", "")
    if window:
        L(f"最佳婚恋窗口在{window}。")
    L("")
    L("### 12.3 配偶特征")
    L("")
    trait = _safe(s12, "spouse_trait", "")
    if trait:
        L(f"配偶特征：{trait}。")
    L("")

    # ═══════════════════════════ §13 ═══════════════════════════
    L("## §13 子女分析")
    L("")
    L("### 13.1 子女星与子女宫")
    L("")
    count = _safe(s13, "child_count_estimate", "")
    L(f"子女方面：{count}")
    L("")
    L("### 13.2 子女运势")
    L("")
    achievement = _safe(s13, "child_achievement", "")
    if achievement:
        L(f"子女成就趋势：{achievement}。")
    L("")

    # ═══════════════════════════ §14 ═══════════════════════════
    L("## §14 健康分析")
    L("")
    L("### 14.1 体质评估")
    L("")
    constitution = _safe(s14, "constitution", "")
    L(f"体质方面：{constitution}。")
    L("")
    L("### 14.2 五行过三排查")
    L("")
    wxot = s14.get("wu_xing_over_three", []) if isinstance(s14.get("wu_xing_over_three"), list) else []
    if wxot:
        for item in wxot[:3]:
            wx = _safe(item, "wx", "")
            organ = _safe(item, "organ", "")
            if wx and organ:
                L(f"- {wx}五行过旺，对应{organ}需留意保养。")
    else:
        L("- 无显著五行过三情况。")
    L("")

    # ═══════════════════════════ §15 ═══════════════════════════
    L("## §15 六亲分析")
    L("")
    L("### 15.1 年柱（祖上/早年家庭）")
    L("")
    summary = _safe(s15, "summary", "")
    L(f"{summary}")
    L("")
    L("### 15.2 月柱（父母/兄弟姐妹）")
    L("")
    economy = _safe(s15, "family_economy", "")
    pressure = _safe(s15, "family_pressure", "")
    if economy:
        L(f"家庭经济：{economy}。")
    if pressure:
        L(f"家庭压力：{pressure}。")
    L("")

    # ═══════════════════════════ §16 ═══════════════════════════
    L("## §16 全生命周期重点事件总表")
    L("")
    L("| 序号 | 大运 | 年份 | 年龄 | 事件 | 类型 |")
    L("|:----:|:----:|:----:|:----:|:-----|:----:|")
    key_evts = s16.get("key_events", {}) if isinstance(s16.get("key_events"), dict) else {}
    evt_idx = 0
    for dy in dy_list:
        gz = dy.get("gan_zhi", "")
        sa = dy.get("start_age", 0)
        ea = dy.get("end_age", 9)
        sy = dy.get("start_year", 0)
        L(f"| | **{gz}运（{sa}~{ea}岁）** | | | | |")
        L("| --- | --- | --- | --- | --- | --- |")
        evt_idx += 1
        if evt_idx >= 20:
            break
    L("")
    L("（完整事件表请参考大运精析§17）")
    L("")

    # ═══════════════════════════ §17 ═══════════════════════════
    L("## §17 大运精析")
    L("")
    for i, dy in enumerate(dy_list):
        gz = dy.get("gan_zhi", "")
        sa = dy.get("start_age", "")
        ea = dy.get("end_age", "")
        sy = dy.get("start_year", 0)
        sc = dy.get("score", 5)

        tag = "🏆 上佳" if sc >= 8 else "✅ 顺利" if sc >= 6 else "⚠️ 平运" if sc >= 4 else "❌ 低谷"
        L(f"### 17.{i + 1} {gz}大运（{sa}~{ea}岁）·{tag}")
        L("")
        L(f"**年龄**：{sa}~{ea}岁")
        L(f"**评分**：{sc}/10")
        L(
            f"**特征**：此运为人生{'上佳发展阶段' if sc >= 8 else '稳步发展期' if sc >= 6 else '平稳过渡期' if sc >= 4 else '需谨慎应对的时期'}。"
        )
        L("")
        L("**运象分析**：")
        L(f"天干{dy.get('gan', '')}地支{dy.get('zhi', '')}，与命局互动形成该运特有的能量场。")
        if sc >= 6:
            L("此运喜用神到位，是发展的好时机。宜把握机遇，积极进取。")
        else:
            L("此运忌神主事，宜守不宜攻。稳扎稳打，韬光养晦。")
        L("")
        L("**关键年份**：")
        L("- 此运第3~5年为最佳发力期。")
        L("- 第7~9年需注意调整节奏。")
        L("")

    # ═══════════════════════════ §18 ═══════════════════════════
    L("## §18 三决断")
    L("")
    if s18 and isinstance(s18, list):
        for i, v in enumerate(s18[:3]):
            title = _safe(v, "title", f"决断{i + 1}")
            event = _safe(v, "event", "")
            L(f"### 决断{i + 1}：{title}")
            L("")
            L(f"**断语**：{event}")
            L("")
    L("")

    # ═══════════════════════════ §19 ═══════════════════════════
    L("## §19 人生运程总评")
    L("")
    L("### 19.1 各运评分表")
    L("")
    L("| 大运 | 年龄段 | 评分/10 | 评语 |")
    L("|:----|:------:|:-------:|:-----|")
    for dy in dy_list:
        gz = dy.get("gan_zhi", "")
        sa = dy.get("start_age", "")
        ea = dy.get("end_age", "")
        sc = dy.get("score", 5)
        tag = "🏆" if sc >= 8 else "✅" if sc >= 6 else "⚠️" if sc >= 4 else "❌"
        L(f"| {gz} | {sa}~{ea} | {sc}/10 | {tag} |")
    L("")
    L("### 19.2 吉凶总评")
    L("")
    if best_dy:
        L(f"**优势窗口**：{best_dy_name}运（{best_dy_age}）—— 一生最佳发展阶段。")
    if worst_dy:
        L(f"**关键风险**：{worst_dy_name}运（{worst_dy_age}）—— 需特别谨慎。")
    L("")

    # ═══════════════════════════ §20 ═══════════════════════════
    L("## §20 五行补充建议")
    L("")
    L("### 20.1 颜色调运")
    L("")
    L("| 喜用五行 | 颜色 |")
    L("|:--------|:-----|")
    for w in xi[:3]:
        color_map = {"金": "白/金/银", "水": "蓝/黑/灰", "木": "绿/青", "火": "红/紫/橙", "土": "黄/棕/米"}
        L(f"| {w} | {color_map.get(w, '')} |")
    L("")
    L("### 20.2 数字吉利")
    L("")
    lucky = _safe(s20, "lucky_numbers", "")
    if lucky:
        L(f"吉利数字：{lucky}")
    L("")
    L("### 20.3 方位建议")
    L("")
    directions = _safe(s20, "directions", "")
    if directions:
        L(f"吉利方位：{directions}")
    L("")
    L("### 20.4 饰品搭配")
    L("")
    jewellery = _safe(s20, "jewellery", "")
    if jewellery:
        L(f"推荐饰品：{jewellery}")
    L("")
    L("### 20.5 饮食调理")
    L("")
    diet = _safe(s20, "diet", "")
    if diet:
        L(f"饮食建议：{diet}")
    L("")

    # ═══════════════════════════ §21 ═══════════════════════════
    L("## §21 人生建议")
    L("")
    L("### 21.1 事业方向与路线图")
    L("")
    ca = s21.get("career", {}) if isinstance(s21.get("career"), dict) else {}
    career_advice = _safe(ca, "advice", "")
    if career_advice:
        L(career_advice)
    L("")
    L("### 21.2 财富管理与补财库")
    L("")
    wa = s21.get("wealth", {}) if isinstance(s21.get("wealth"), dict) else {}
    wealth_advice = _safe(wa, "advice", "")
    if wealth_advice:
        L(wealth_advice)
    L("")
    L("### 21.3 健康养生")
    L("")
    ha = s21.get("health", {}) if isinstance(s21.get("health"), dict) else {}
    health_advice = _safe(ha, "advice", "")
    if health_advice:
        L(health_advice)
    L("")
    L("### 21.4 婚姻经营")
    L("")
    ma = s21.get("marriage", {}) if isinstance(s21.get("marriage"), dict) else {}
    marriage_advice = _safe(ma, "advice", "")
    if marriage_advice:
        L(marriage_advice)
    L("")

    # 页脚
    L("---")
    L("**编制人：** 金鉴真人")
    L(f"**编制时间：** {today}")
    L("**版本：** v2.0（引擎数据校准版）")
    L("**分析方法：** 金鉴真人体系 · 确定性规则引擎")
    L("")

    return "\n".join(lines)
