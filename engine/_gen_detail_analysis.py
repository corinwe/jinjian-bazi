"""
金鉴真人·detail_analysis 生成器
对所有21个§生成基于规则计算结果的详细分析文本
"""

from constants import TIAN_GAN_WU_XING, DI_ZHI_WU_XING


def _s(d, key, default=""):
    if isinstance(d, dict):
        return d.get(key, default)
    return default


def _fmt(lst, joiner="、"):
    if not lst or not isinstance(lst, list):
        return ""
    return joiner.join(str(x) for x in lst if x)


def _wx_desc(wx):
    descs = {"金": "刚毅果断·金属性能量", "木": "仁厚生机·木属性能量",
             "水": "智慧流动·水属性能量", "火": "热烈向上·火属性能量",
             "土": "稳定包容·土属性能量"}
    return descs.get(wx, f"{wx}属性能量")


def _shen_qiang_ruo_detail(result: dict) -> str:
    """§3 身强弱分析"""
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    det = s3.get("details", {})
    score = s3.get("score", 0)
    label = s3.get("label", "")
    parts = []
    parts.append(f"【身强弱判定】{label}（{score}分）")
    parts.append(f"【金鉴真人·身强弱规则·月令本气印=40分·比劫全算】")
    parts.append(f"月令印星计{det.get('yue_yin',0)}分 | 月令比劫计{det.get('yue_bi',0)}分 | "
                 f"天干比劫计{det.get('tg_bi',0)}分 | "
                 f"日支印比计{det.get('rz',0)}分 | "
                 f"年时支印比计{det.get('nsz',0)}分")
    
    if isinstance(score, (int, float)):
        if score >= 60:
            parts.append("结论：身强偏旺。体质强健，能扛压力，有担当大事的能量底子。宜用克泄耗（财官食伤）平衡。")
        elif score >= 40:
            parts.append("结论：中和。五行相对平衡，适应力强，喜忌随大运灵活变化。")
        elif score >= 25:
            parts.append("结论：身弱。宜借平台和贵人发力，不宜单打独斗。喜印比帮身。")
        else:
            parts.append("结论：身极弱。需大运印比强力补救方能发力。")
    return "\n".join(parts)


def _xi_yong_detail(result: dict) -> str:
    """§4 喜用神分析"""
    s4 = result.get("sec_4_xi_yong", {})
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    xi = s4.get("xi", [])
    ji = s4.get("ji", [])
    label = s3.get("label", "")
    parts = []
    
    if isinstance(xi, list) and xi:
        parts.append(f"【喜用神】{' > '.join(str(x) for x in xi)}")
    if isinstance(ji, list) and ji:
        parts.append(f"【忌神】{' > '.join(str(x) for x in ji)}")
    
    xi_fmt = '、'.join(str(x) for x in (xi if isinstance(xi, list) else [])) if xi else "无"
    ji_fmt = '、'.join(str(x) for x in (ji if isinstance(ji, list) else [])) if ji else "无"
    
    if "身强" in str(label):
        parts.append(f"判定逻辑：{label} → 喜克泄耗（{xi_fmt}），忌生扶（{ji_fmt}）")
        parts.append(f"【金鉴真人·喜忌规则·身强喜克泄耗】")
    elif "身弱" in str(label):
        parts.append(f"判定逻辑：{label} → 喜生扶（{xi_fmt}），忌克泄耗（{ji_fmt}）")
        parts.append(f"【金鉴真人·喜忌规则·身弱喜生扶】")
    else:
        parts.append(f"判定逻辑：{label} → 喜忌随大运灵活变化")
    
    th = s4.get("tiao_hou", "")
    if th:
        th_str = '、'.join(str(t) for t in th) if isinstance(th, list) else str(th)
        parts.append(f"调候用神：{th_str}。【金鉴真人·调候规则·穷通宝鉴】")
    
    return "\n".join(parts)


def _wealth_detail(result: dict) -> str:
    """§8 财富分析"""
    s8 = result.get("sec_8_wealth", {})
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    total = s8.get("cai_xing_total", 0)
    level = s8.get("wealth_level", "")
    ck = s8.get("cai_ku", {})
    cd = s8.get("cai_xing_details", {})
    parts = []
    
    parts.append(f"【财星评分】总分{total}分 | 等级：{level}")
    parts.append(f"【金鉴真人·财星规则·只含正偏财·不含劫财】")
    parts.append(f"财星明细：月令{cd.get('yue',0)}分 | 日支{cd.get('ri',0)}分 | "
                 f"时干{cd.get('sg',0)}分 | 时支{cd.get('sz',0)}分 | 年支{cd.get('nian',0)}分")
    
    sqr_n = float(s3.get("score", 50) if s3.get("score") else 50)
    cai_n = float(total) if total else 0
    
    if cai_n >= 40 and sqr_n >= 40:
        parts.append("状态：身强财旺 → 天生发财格，不缺钱")
    elif cai_n < 40 and sqr_n >= 40:
        parts.append("状态：身强财弱 → 底子好但财星弱，等财星/食伤大运发中财")
    elif cai_n >= 40 and sqr_n < 40:
        parts.append("状态：身弱财旺 → 富屋贫人，等印比帮身大运才变现")
    elif cai_n == 0 and sqr_n < 40:
        parts.append("状态：无财身弱 → 对钱看淡，难发财")
    else:
        parts.append(f"状态：身弱财弱 → 辛苦钱，遇印比发中财")
    
    if isinstance(ck, dict) and ck.get("has"):
        zhis = ck.get("zhi", [])
        parts.append(f"财库：✅ 日/时柱带财库（{_fmt(zhis)}），蓄财能力强")
        parts.append(f"【金鉴真人·财富规则·日时柱有库=蓄财能力强】")
    else:
        parts.append("财库：❌ 无财库，财来财去需主动蓄财")
    
    parts.append(f"【金鉴真人·财富五级标准·{level}】")
    return "\n".join(parts)


def _character_detail(result: dict) -> str:
    """§6 性格分析 - 复用已有detail_analysis或生成"""
    s6 = result.get("sec_6_character", {})
    da = s6.get("detail_analysis", "")
    if da:
        return da
    # fallback: generate basic
    parts = []
    ri_wx = s6.get("ri_wx", "")
    parts.append(f"【性格基调】日主五行{ri_wx}，{_wx_desc(ri_wx)}")
    traits = s6.get("tags", [])
    if isinstance(traits, list) and traits:
        parts.append(f"核心特质：{_fmt(traits)}")
    ss_traits = s6.get("shi_shen_traits", [])
    if isinstance(ss_traits, list) and ss_traits:
        for t in ss_traits[:3]:
            if isinstance(t, dict):
                parts.append(f"十神{_s(t,'ten_god','')}（{_s(t,'label','')}）：{_fmt(t.get('traits',[]))}")
    return "\n".join(parts)

def _education_detail(result: dict) -> str:
    """§11 学历分析"""
    s11 = result.get("sec_11_education", {})
    parts = []
    
    display = s11.get("display", "")
    school = s11.get("school_level", "")
    degree = s11.get("degree", "")
    
    if display:
        parts.append(f"【学历判定】{display}")
    elif school or degree:
        parts.append(f"【学历判定】学校等级：{school} | 学历层级：{degree}")
    
    ypc = s11.get("year_pillar_check", {})
    if isinstance(ypc, dict):
        parts.append(f"年柱印星：{_s(ypc,'detail','未详')}。【金鉴真人·学业规则·年柱有印=学业基因】")
    
    nc = s11.get("nian_gan_check", {})
    if isinstance(nc, dict):
        ss = _s(nc, "shi_shen", "")
        if ss:
            parts.append(f"年干十神：{ss}。{'年干伤官=叛逆·非学历导向【素材12行517】' if '伤官' in ss else ''}")
    
    wc = s11.get("wen_chang_ming_li", {})
    if isinstance(wc, dict):
        parts.append(f"文昌贵人：{_s(wc,'detail','未查')}。【金鉴真人·学业规则·文昌=学业助力】")
    
    steps = s11.get("six_steps", {})
    if isinstance(steps, dict):
        passed = steps.get("passed", 0)
        total = steps.get("total", 6)
        parts.append(f"六步排查：{passed}/{total}项通过")
    
    # 新字段：六步详细推理
    step_details = s11.get("six_step_details", [])
    if isinstance(step_details, list) and step_details:
        parts.append("学业推理过程：")
        for sd in step_details[:6]:
            parts.append(f"  - {sd}")
    
    # 新字段：学校等级推理
    school_reason = s11.get("school_reasoning", "")
    if school_reason:
        parts.append(f"学校等级推理：{school_reason}")
    
    # 新字段：学历层级推理
    degree_reason = s11.get("degree_reasoning", "")
    if degree_reason:
        parts.append(f"学历层级推理：{degree_reason}")
    
    # 新字段：学龄段大运窗口
    edu_windows = s11.get("edu_da_yun_windows", [])
    if isinstance(edu_windows, list) and edu_windows:
        parts.append(f"学龄期大运窗口：{'；'.join(edu_windows)}")
    
    # 学校六档标准速查
    parts.append("【学校等级六档标准】 👑顶尖(≥5项✅+文昌月令) > 🥇985(3-4项✅+文昌日/月) > 🥇211(3项✅+文昌在局) > 🥈普通(2项✅+文昌大运) > 🥉大专(1-2项✅+文昌缺) > 🪜初中(≤1项✅+无印无文昌)")
    parts.append("【金鉴真人·学业规则·第0层三档法+六步排查+学校六档+文昌双轨】")
    parts.append("【规则引用】年柱有印→学业基因(素材12行517·素材03行541)；文昌=学业助力(文昌贵人理论)；印运时间线定学历层级")
    return "\n".join(parts)


def _marriage_detail(result: dict) -> str:
    """§12 婚姻分析"""
    s12 = result.get("sec_12_marriage", {})
    parts = []
    
    quality = s12.get("quality", "")
    qs = s12.get("quality_score", "")
    parts.append(f"【婚姻质量】{quality}（{qs}/10）")
    
    spouse = s12.get("spouse_trait", "")
    if spouse:
        parts.append(f"配偶特征：{spouse}")
    
    bwa = s12.get("best_window_age", "")
    if bwa:
        parts.append(f"最佳窗口：{bwa}岁")
    
    windows = s12.get("marriage_windows", [])
    if isinstance(windows, list) and windows:
        for i, w in enumerate(windows[:3]):
            if isinstance(w, dict):
                parts.append(f"窗口{i+1}：{_s(w,'da_yun','')}运{_s(w,'age_range','')}岁——{_s(w,'reason','')}")
    
    peiou_xing = s12.get("peiou_xing", "")
    if isinstance(peiou_xing, dict):
        parts.append(f"配偶星：{'存在' if peiou_xing.get('has_primary') else '缺失'}【金鉴真人·婚姻规则·男财女官】")
        if peiou_xing.get("primary_star"):
            parts.append(f"主配偶星：{peiou_xing['primary_star']}")
    elif peiou_xing:
        parts.append(f"配偶星：{peiou_xing}")
    
    fuqi_gong = s12.get("fuqi_gong_shi_shen", "")
    if fuqi_gong:
        parts.append(f"夫妻宫十神：{fuqi_gong}【金鉴真人·婚姻规则·夫妻宫十神定婚姻基调】")
    
    signal_detail = s12.get("signal_detail", "")
    if signal_detail:
        parts.append(f"结婚信号：{signal_detail}")
    
    pei_ou_detail = s12.get("pei_ou_detail", "")
    if pei_ou_detail:
        parts.append(f"配偶星详情：{pei_ou_detail}")
    
    parts.append("【结婚四大信号】⭐⭐⭐⭐正财/正官透干流年 > ⭐⭐⭐流年合夫妻宫 > ⭐⭐流年冲夫妻宫 > ⭐桃花年引动")
    parts.append("【婚姻质量规则】夫妻宫为喜用+配偶星入本位+无严重刑冲→高分婚姻(≥7/10)；反之则需更多经营")
    parts.append("【金鉴真人·婚姻规则·配偶星定位+夫妻宫喜忌+四大信号+三窗口】")
    parts.append("【规则引用】男命正财=妻星·女命正官=夫星(素材12)；夫妻宫十神断婚姻质量(婚姻skill)；四大信号排序(素材17)")
    return "\n".join(parts)


def _children_detail(result: dict) -> str:
    """§13 子女分析"""
    s13 = result.get("sec_13_children", {})
    parts = []
    
    cce = s13.get("child_count_estimate", "")
    if cce:
        parts.append(f"【子女数量】{cce}")
    
    ca = s13.get("child_achievement", "")
    if ca:
        parts.append(f"子女成就：{ca}")
    
    sp = s13.get("sheng_yu_potential", "")
    if sp:
        parts.append(f"生育力：{sp}。【金鉴真人·子女规则·时支生育力排名】")
    
    thin = s13.get("thin_factors", [])
    if isinstance(thin, list) and thin:
        parts.append(f"缘薄因素：{' | '.join(str(t) for t in thin[:3])}。【金鉴真人·子女规则·缘薄排查】")
    
    years = s13.get("child_birth_years", [])
    if isinstance(years, list) and years:
        parts.append(f"添丁窗口年份：{_fmt(years)}")
    
    part_detail = s13.get("part_detail", "")
    if part_detail:
        parts.append(f"子女宫（时柱）：{part_detail}")
    
    windows = s13.get("windows", [])
    if isinstance(windows, list) and windows:
        parts.append(f"生育窗口：{'；'.join(str(w) for w in windows[:3])}")
    
    return "\n".join(parts)
def _health_detail(result: dict) -> str:
    """§14 健康分析"""
    s14 = result.get("sec_14_health", {})
    parts = []
    
    cons = s14.get("constitution", "")
    if cons:
        parts.append(f"【先天体质】{cons}")
    else:
        parts.append("【先天体质】未详")
    
    wxot = s14.get("wu_xing_over_three", [])
    has_wxot = isinstance(wxot, list) and wxot
    if has_wxot:
        parts.append("五行过三排查（≥3个该五行=对应器官系统风险）：")
        for item in wxot:
            if isinstance(item, dict):
                parts.append(f"  {_s(item,'wx','')}五行过{_s(item,'count','')}→{_s(item,'organ','')}。【金鉴真人·健康规则·五行过三】")
    else:
        parts.append("五行过三排查：无。各五行能量未超过3个，器官系统无显著过载风险。")
    
    qi_sha = s14.get("qi_sha_risks", {})
    qi_sha_detail = qi_sha.get("detail", "") if isinstance(qi_sha, dict) else (str(qi_sha) if qi_sha else "")
    if qi_sha_detail:
        parts.append(f"七杀攻身：{qi_sha_detail}。【金鉴真人·健康规则·七杀=实质病灶】")
    else:
        parts.append("七杀攻身：无显著七杀攻身信号。")
    
    pian_yin = s14.get("pian_yin_risks", {})
    piano_detail = pian_yin.get("detail", "") if isinstance(pian_yin, dict) else (str(pian_yin) if pian_yin else "")
    if piano_detail:
        parts.append(f"偏印瘀堵：{piano_detail}。【金鉴真人·健康规则·偏印=经络淤堵】")
    else:
        parts.append("偏印瘀堵：无明显淤堵信号。")
    
    battles = s14.get("wu_xing_battles", {})
    if isinstance(battles, dict):
        details = battles.get("detail", "")
        if details:
            parts.append(f"五行交战：{details}")
    
    parts.append("【七杀断病法】七杀所在宫位=实际病灶(素材课程)；偏印通则络淤堵(素材课程)")
    parts.append("【五行过三规则】某五行≥3个→该五行及所克五行对应的器官系统有风险(素材课程)")
    parts.append("【十二长生节奏】长生→帝旺(上升期/健康好)→衰→病→死(下降期/机能衰退)")
    parts.append("【金鉴真人·健康规则·五行过三+七杀断病+偏印主瘀】")
    return "\n".join(parts)


def _family_detail(result: dict) -> str:
    """§15 六亲分析"""
    s15 = result.get("sec_15_family", {})
    parts = []
    
    summary = s15.get("summary", "")
    if summary:
        parts.append(f"【六亲总评】{summary}")
    
    for pos in ["year", "month", "day", "hour"]:
        p = s15.get(f"{pos}_pillar", {})
        if isinstance(p, dict):
            desc = _s(p, "detail", "")
            if desc:
                parts.append(f"【{pos}柱】{desc}")
    
    wz = s15.get("wu_xing_analysis", {})
    if isinstance(wz, dict):
        parents = wz.get("parent_help", "")
        if parents:
            parts.append(f"父母助力：{parents}。【金鉴真人·六亲规则·父母助力看印偏财】")
        spouse = wz.get("spouse_help", "")
        if spouse:
            parts.append(f"配偶助力：{spouse}")
        children = wz.get("children_help", "")
        if children:
            parts.append(f"子女助力：{children}")
    
    return "\n".join(parts)


def _career_detail(result: dict) -> str:
    """§10 事业分析"""
    s10 = result.get("sec_10_career", {})
    parts = []
    
    direction = s10.get("career_direction", "")
    if direction:
        parts.append(f"【事业方向】{direction}")
    
    grade = s10.get("career_grade", "")
    if grade:
        parts.append(f"【事业等级】{grade}")
    
    mode = s10.get("work_mode", "")
    if mode:
        parts.append(f"【工作模式】{mode}")
    
    industries = s10.get("recommended_industries", "")
    if industries:
        parts.append(f"【推荐行业】{industries}。【金鉴真人·事业规则·五行定行业】")
    
    entre = s10.get("entrepreneurship", "")
    if entre:
        parts.append(f"【创业判断】{entre}")
    
    e_shen = s10.get("e_shen_zhi_hua", "")
    if e_shen:
        parts.append(f"【恶神制化】{e_shen}。【金鉴真人·事业规则·七杀有制方为贵】")
    
    key_years = s10.get("key_career_years", [])
    if isinstance(key_years, list) and key_years:
        parts.append(f"关键事业年份：{_fmt(key_years)}")
    
    return "\n".join(parts)


def _appearance_detail(result: dict) -> str:
    """§7 外貌分析"""
    s7 = result.get("sec_7_appearance", {})
    parts = []
    
    app = s7.get("ri_zhu_appearance", "")
    if app:
        parts.append(f"【日主长相基准】{app}")
    
    build = s7.get("build", "")
    if build:
        parts.append(f"【体型】{build}")
    
    height = s7.get("height_estimate", "")
    if height:
        parts.append(f"【身高推断】{height}")
    
    style = s7.get("style", "")
    if style:
        parts.append(f"【气质】{style}")
    
    weight = s7.get("weight_tendency", "")
    if weight:
        parts.append(f"【体重倾向】{weight}。【金鉴真人·外貌规则·食神=胖·伤官=瘦】")
    
    dev = s7.get("development_timing", "")
    if dev:
        parts.append(f"【发育早晚】{dev}。【金鉴真人·五项规则】")
    
    return "\n".join(parts)


def _property_detail(result: dict) -> str:
    """§9 置业分析"""
    s9 = result.get("sec_9_property", {})
    parts = []
    
    pp = s9.get("property_potential", "")
    if pp:
        parts.append(f"【置业潜力】{pp}")
    
    pl = s9.get("property_level", "")
    if pl:
        parts.append(f"【置业能力】{pl}")
    
    timing = s9.get("property_timing", "")
    if timing:
        parts.append(f"【置业时机】{timing}")
    
    feng_shui = s9.get("feng_shui_advice", "")
    if feng_shui:
        parts.append(f"【风水建议】{feng_shui}")
    
    return "\n".join(parts)


def _verdicts_detail(result: dict) -> str:
    """§18 三决断"""
    s18 = result.get("sec_18_verdicts", [])
    parts = []
    if isinstance(s18, list):
        for i, v in enumerate(s18):
            if isinstance(v, dict):
                parts.append(f"【决断{i+1}·{_s(v,'title','')}】"
                             f"其人：{_s(v,'person','')} | "
                             f"其事：{_s(v,'event','')} | "
                             f"其时：{_s(v,'time','')} | "
                             f"其度：{_s(v,'degree','')}")
                parts.append(f"理由：{_s(v,'reason','')}")
                parts.append(f"断语：{_s(v,'verdict','')}")
    return "\n".join(parts)


def _da_yun_detail(result: dict) -> str:
    """§17 大运精析"""
    s17 = result.get("sec_17_da_yun_detail", {})
    s1 = result.get("sec_1_overview", {})
    parts = []
    
    dy_list = s17.get("list", [])
    if isinstance(dy_list, list):
        parts.append(f"【大运序列（{len(dy_list)}步至100岁）】")
        for dy in dy_list:
            gan_zhi = s17 if dy else ""
            score = dy.get("score", 0)
            star = "🏆" if score >= 8 else "✅" if score >= 6 else "⚠️"
            parts.append(f"  {star} {dy.get('gan_zhi','')} {dy.get('start_age','')}~{dy.get('end_age','')}岁 "
                         f"[{dy.get('start_year','')}~{dy.get('end_year','')}] {score}/10分")
        
        best = s17.get("best_idx", -1)
        worst = s17.get("worst_idx", -1)
        if best >= 0 and best < len(dy_list):
            parts.append(f"最佳大运：🏆 {dy_list[best].get('gan_zhi','')}（{dy_list[best].get('score',0)}/10分）")
            parts.append(f"【金鉴真人·大运规则·纯喜用运=最佳·以喜用神逻辑排序】")
        if worst >= 0 and worst < len(dy_list):
            parts.append(f"最差大运：⚠️ {dy_list[worst].get('gan_zhi','')}（{dy_list[worst].get('score',0)}/10分）")
    
    qy = s1.get("qi_yun_age", "")
    parts.append(f"起运年龄：{qy}岁")
    
    return "\n".join(parts)


def _events_detail(result: dict) -> str:
    """§16 事件表"""
    s16 = result.get("sec_16_events", {})
    parts = []
    
    key_evts = s16.get("key_events", {})
    if isinstance(key_evts, dict):
        overall_count = sum(len(v) if isinstance(v, list) else 0 for v in key_evts.values())
        parts.append(f"【事件总览】{overall_count}个关键事件，覆盖全生命周期")
        for etype, evts in key_evts.items():
            if isinstance(evts, list) and evts:
                parts.append(f"  [{etype}] 示例：{evts[0].get('year','')}年{evts[0].get('description','')}")
    
    recent = s16.get("recent_5", [])
    if isinstance(recent, list) and recent:
        parts.append("【近期流年】")
        for r in recent[:5]:
            if isinstance(r, dict):
                parts.append(f"  {r.get('year','')}年 | {r.get('description','')}")
    
    return "\n".join(parts)


def _overall_detail(result: dict) -> str:
    """§19 运程总评"""
    s19 = result.get("sec_19_overall", {})
    parts = []
    
    curve = s19.get("curve", [])
    if isinstance(curve, list):
        parts.append("【运程曲线】")
        for c in curve:
            parts.append(f"  {c.get('da_yun','')}({c.get('age',0)}岁): {c.get('bar','')} {c.get('score',0)}/10")
    
    summary = s19.get("summary", "")
    if summary:
        parts.append(f"【运程核心】{summary}")
    
    risk = s19.get("risk_alert", "")
    if risk:
        parts.append(f"【风险提示】{risk}")
    
    return "\n".join(parts)


def _wu_xing_advice_detail(result: dict) -> str:
    """§20 五行补充"""
    s20 = result.get("sec_20_wu_xing_advice", {})
    parts = []
    
    colors = s20.get("colors", "")
    if colors:
        parts.append(f"【颜色调运】{colors}。【金鉴真人·五行规则·颜色补五行】")
    
    dirs = s20.get("directions", "")
    if dirs:
        parts.append(f"【吉利方位】{dirs}")
    
    jewels = s20.get("jewellery", "")
    if jewels:
        parts.append(f"【饰品搭配】{jewels}")
    
    diet = s20.get("diet", "")
    if diet:
        parts.append(f"【饮食调理】{diet}")
    
    numbers = s20.get("numbers", "")
    if numbers:
        parts.append(f"【吉利数字】{numbers}")
    
    return "\n".join(parts)


def _advice_detail(result: dict) -> str:
    """§21 人生建议"""
    s21 = result.get("sec_21_advice", {})
    parts = []
    
    for dim in ["career", "wealth", "health", "marriage", "interpersonal"]:
        d = s21.get(dim, {})
        if isinstance(d, dict):
            advice = _s(d, "advice", "")
            if advice:
                parts.append(f"【{dim}】{advice}")
    
    return "\n".join(parts)


def _ge_ju_detail(result: dict) -> str:
    """§2 格局分析"""
    s2 = result.get("sec_2_ge_ju", {})
    parts = []
    
    main = s2.get("main", "")
    detail = s2.get("detail", "")
    if main:
        parts.append(f"【核心格局】{main}")
    if detail:
        parts.append(f"格局详解：{detail}")
    
    ss_list = s2.get("shi_shen", [])
    if isinstance(ss_list, list):
        parts.append("十神分布：")
        for item in ss_list:
            if isinstance(item, dict):
                parts.append(f"  {_s(item,'position','')} {_s(item,'gan','')}→{_s(item,'shi_shen','')}（{_s(item,'yin_yang','')}·{_s(item,'wu_xing','')}）")
    
    return "\n".join(parts)


def _zai_huo_detail(result: dict) -> str:
    """§5 灾祸分析"""
    s5 = result.get("sec_5_zai_huo", {})
    parts = []
    
    parts.append("【神煞排查】")
    yuan = s5.get("yuan_chen", [])
    zai = s5.get("zai_sha", [])
    tl = s5.get("tian_luo", [])
    parts.append(f"  元辰：{_fmt(yuan) or '无'}。【金鉴真人·神煞·元辰=灾祸信号】")
    parts.append(f"  灾煞：{_fmt(zai) or '无'}。【金鉴真人·神煞·灾煞=意外信号】")
    parts.append(f"  天罗地网：{_fmt(tl) or '无'}。【金鉴真人·神煞·天罗地网=束缚信号】")
    
    chong = s5.get("shen_sha_chong", [])
    xing = s5.get("shen_sha_xing", [])
    hai = s5.get("shen_sha_hai", [])
    if chong or xing or hai:
        parts.append("【地支关系】")
        if chong:
            parts.append(f"  冲：{_fmt(chong)}。【冲主动荡·变化·分离】")
        if xing:
            parts.append(f"  刑：{_fmt(xing)}。【刑主是非·纠纷·口舌】")
        if hai:
            parts.append(f"  害：{_fmt(hai)}。【害主暗算·损耗】")
    
    wxot = s5.get("wu_xing_over_three", [])
    if wxot and isinstance(wxot, list):
        parts.append("【五行过三】")
        for item in wxot[:3]:
            if isinstance(item, dict):
                parts.append(f"  {_s(item,'wx','')}过{_s(item,'count','')}→{_s(item,'organ','')}")
    
    mf = s5.get("misfortune_full", {})
    if isinstance(mf, dict):
        rl = mf.get("risk_level", "")
        if rl:
            parts.append(f"【风险等级】{rl}")
    
    rm = s5.get("remission_advice", {})
    if isinstance(rm, dict):
        adv = rm.get("advice", "")
        if adv:
            parts.append(f"【化解建议】{adv}")
    
    return "\n".join(parts)


def _sec_1_detail(result: dict) -> str:
    """§1 总览分析"""
    s1 = result.get("sec_1_overview", {})
    parts = []
    parts.append(f"【八字】{s1.get('bazi','')}")
    parts.append(f"【日主】{_s(_s({},'ri_zhu',s1.get('ri_zhu',{})),'gan','')}（{_s(_s({},'ri_zhu',s1.get('ri_zhu',{})),'wx','')}）")
    parts.append(f"【身强弱】{s1.get('shen_qiang_ruo','')}")
    xi = s1.get('xi_yong', [])
    ji = s1.get('ji_shen', [])
    xi_str = '>'.join(str(x) for x in (xi if isinstance(xi,list) else []))
    ji_str = '>'.join(str(x) for x in (ji if isinstance(ji,list) else []))
    parts.append(f"【喜用】{xi_str} | 【忌】{ji_str}")
    parts.append(f"【财星】{s1.get('cai_xing_score','')}分 | 【最佳运】{s1.get('best_da_yun','')}")
    return "\n".join(parts)


def attach_detail_analysis(result: dict) -> dict:
    """向result中所有21个§添加detail_analysis字段"""
    SECTION_FUNCS = {
        "sec_1_overview": _sec_1_detail,
        "sec_2_ge_ju": _ge_ju_detail,
        "sec_3_shen_qiang_ruo": _shen_qiang_ruo_detail,
        "sec_4_xi_yong": _xi_yong_detail,
        "sec_5_zai_huo": _zai_huo_detail,
        "sec_6_character": _character_detail,
        "sec_7_appearance": _appearance_detail,
        "sec_8_wealth": _wealth_detail,
        "sec_9_property": _property_detail,
        "sec_10_career": _career_detail,
        "sec_11_education": _education_detail,
        "sec_12_marriage": _marriage_detail,
        "sec_13_children": _children_detail,
        "sec_14_health": _health_detail,
        "sec_15_family": _family_detail,
        "sec_16_events": _events_detail,
        "sec_17_da_yun_detail": _da_yun_detail,
        "sec_18_verdicts": _verdicts_detail,
        "sec_19_overall": _overall_detail,
        "sec_20_wu_xing_advice": _wu_xing_advice_detail,
        "sec_21_advice": _advice_detail,
    }
    
    for key, func in SECTION_FUNCS.items():
        if key in result:
            if isinstance(result[key], dict):
                try:
                    result[key]["detail_analysis"] = func(result)
                except Exception:
                    result[key]["detail_analysis"] = f"{key}: 引擎数据不足，无法展开详细分析"
            elif key == "sec_18_verdicts" and isinstance(result[key], list):
                # verdicts是list存到sec_18_verdicts的整体detail
                try:
                    result["sec_18_verdicts_detail"] = {"detail_analysis": func(result)}
                except Exception:
                    pass
    
    return result
