# ══════════════════════════════════════════════════════════════════════════════
# REPLACEMENT FUNCTIONS for report_generator_simple.py
# 1. _gen_section10 — 事业分析（KB六级+格局定方向+恶神制化+五行定行业+创业判断）
# 2. _gen_section11 — 学业学历（第0层三档法+六步精细排查+文昌双轨制+伤官强负）
# 3. generate_report — 修正§10~§15编号顺序
# ══════════════════════════════════════════════════════════════════════════════

# ========================================================================
# FUNCTION 1: _gen_section10 — 事业分析（映射为§12）
# ========================================================================

def _gen_section10(basic: dict, analysis: dict, birth_year: int) -> list:
    """§12 事业分析（格局定方向+恶神制化定级别+五行定行业+KB六级等级+创业判断）"""
    lines = []
    lines.append("## §12 事业分析")
    lines.append("")

    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ge_ju_str = analysis.get("ge_ju", "")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 50.0)
    pillars = basic.get("pillars", {})
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    energy = analysis.get("energy", {})
    cx = analysis.get("cai_xing", {})

    wx_list_order = ["木", "火", "土", "金", "水"]

    def _ss(g1, g2):
        if not g1 or not g2:
            return ""
        w1, w2 = TIAN_GAN_WU_XING.get(g1, ""), TIAN_GAN_WU_XING.get(g2, "")
        if not w1 or not w2 or w1 not in wx_list_order or w2 not in wx_list_order:
            return ""
        yy1, yy2 = YIN_YANG.get(g1, "阳"), YIN_YANG.get(g2, "阳")
        i1, i2 = wx_list_order.index(w1), wx_list_order.index(w2)
        if i1 == i2: return "比肩" if yy1 == yy2 else "劫财"
        if i2 == (i1 + 1) % 5: return "食神" if yy1 == yy2 else "伤官"
        if i2 == (i1 + 2) % 5: return "正财" if yy1 == yy2 else "偏财"
        if i2 == (i1 + 3) % 5: return "正官" if yy1 == yy2 else "七杀"
        if i2 == (i1 + 4) % 5: return "正印" if yy1 == yy2 else "偏印"
        return ""

    def _ten_to_wx(ss_type):
        ri_idx = wx_list_order.index(ri_wx)
        m = {"印": (ri_idx + 4) % 5, "比劫": ri_idx, "食伤": (ri_idx + 1) % 5,
             "财": (ri_idx + 2) % 5, "官杀": (ri_idx + 3) % 5}
        return wx_list_order[m.get(ss_type, ri_idx)]

    def _count_qi_sha():
        cnt = 0
        for pos in ["nian", "yue", "ri", "shi"]:
            p = pillars.get(pos, {})
            if p.get("gan_shi_shen", "") == "七杀":
                cnt += 1
            for cg in p.get("cang_gan", []):
                if cg.get("shi_shen", "") == "七杀":
                    cnt += 1
        return cnt

    def _count_evil():
        cnt = 0
        for pos in ["nian", "yue", "ri", "shi"]:
            p = pillars.get(pos, {})
            if p.get("gan_shi_shen", "") in ["七杀", "伤官", "劫财"]:
                cnt += 1
            for cg in p.get("cang_gan", []):
                if cg.get("shi_shen", "") in ["七杀", "伤官", "劫财"]:
                    cnt += 1
        return cnt

    def _has_qi_sha_zhi():
        for pos in ["nian", "yue", "ri", "shi"]:
            p = pillars.get(pos, {})
            if p.get("gan_shi_shen", "") == "七杀":
                for pos2 in ["nian", "yue", "ri", "shi"]:
                    p2 = pillars.get(pos2, {})
                    s2 = p2.get("gan_shi_shen", "")
                    if s2 in ["食神", "正印", "偏印"]:
                        return True
        return False

    # ====================================================================
    # 12.1 格局定方向
    # ====================================================================
    lines.append("### 12.1 格局定方向")
    lines.append("")
    lines.append("**【金鉴真人·§12·格局定方向】** 格局决定事业大方向——什么格局的人适合什么赛道。")
    lines.append("")

    career_map = {
        "正官": "体制内/管理/公务员方向，适合在规范化组织中担任管理岗位。官星清透者宜走正统路线",
        "七杀": "军警/创业/挑战性行业，适合高压环境中展现魄力。七杀格者天生有冒险基因",
        "正印": "学术/教育/研究/文化方向，适合知识密集型行业。正印格者适合在已有框架内深耕",
        "偏印": "技术/研发/策略/咨询方向，适合深度钻研型岗位。偏印格者有解构复杂问题的天赋",
        "正财": "实体经营/财务/贸易方向，适合稳健经营型行业。正财格者务实且善于经营",
        "偏财": "投资/销售/自由职业方向，适合灵活多变的市场环境。偏财格者嗅觉敏锐",
        "比肩": "技术专家/自由职业/独立顾问方向，适合独立开展工作。比肩格者宜走专业路线",
        "劫财": "公关/销售/合作经营方向，适合需要社交能力的行业。劫财格者社交手腕强",
        "食神": "创意/艺术/技术/美食方向，适合发挥才华的领域。食神格者有创造力",
        "伤官": "创作/研发/表演/创新方向，适合需要叛逆精神的领域。伤官格者有颠覆式创新思维",
    }

    base_dir = career_map.get(ge_ju_str, "宜根据喜用神五行选择行业")
    lines.append(f"格局为{ge_ju_str}格→{base_dir}。所以您的事业发展应当以格局为纲，选择与格局特质匹配的赛道。")
    lines.append("")

    lines.append("🗣️ **白话解读：**")
    lines.append(f"> 您的{ge_ju_str}格决定了您最擅长的领域和做事风格。比如有的人天生适合闯荡，")
    lines.append(f"> 有的人适合深耕——您的格局已经指明了最佳赛道，强行去走不匹配的方向结果往往是事倍功半。")
    lines.append("")

    # ====================================================================
    # 12.2 恶神制化定级别
    # ====================================================================
    lines.append("### 12.2 恶神制化定级别")
    lines.append("")
    lines.append("**【金鉴真人·§12·恶神制化定级别】** 「凡成大事者必有恶神，恶神有制方为贵」。")
    lines.append("恶神（七杀/伤官/劫财）的数量决定压力级别，制化程度决定事业级别。")
    lines.append("")

    evil_cnt = _count_evil()
    qs_cnt = _count_qi_sha()
    qs_zhi = _has_qi_sha_zhi()

    lines.append(f"原局恶神统计：七杀{qs_cnt}处、其他恶神{evil_cnt - qs_cnt}处，共{evil_cnt}处恶神。")
    lines.append("")

    if qs_cnt > 0:
        if qs_zhi:
            lines.append("✅ **七杀有制化**：七杀遇食神/印星制化，化为权威管理能力。「恶神有制」是成大事者的标配——")
            lines.append("有压力但能转化为动力，有敌人但也能化为良师。这种结构是事业高度最重要的加分项。")
        else:
            lines.append("⚠️ **七杀无制化**：七杀无制则原局压力较大。")
            if sq_level == "身强":
                lines.append("但身强足以承载七杀的冲击，能在高压竞争中越挫越勇。「身杀两停」结构，是顶级竞争者的底色。")
            else:
                lines.append("同时身偏弱，建议在压力可控的环境中发展，避免过度承压。")
    else:
        lines.append("原局无七杀或七杀极弱，事业压力整体可控。")
        if evil_cnt >= 2:
            lines.append(f"但仍有{evil_cnt}处其他恶神（伤官/劫财），同样需关注是否存在制化。")
    lines.append("")

    # ---- KB 六级事业等级判定 ----
    lines.append("**【金鉴真人·§12·KB六级事业等级】**")
    lines.append("")

    # 计算喜用神五行集
    xi_wx_set = set()
    for xi in xi_list:
        if xi in ["正印", "偏印"]: xi_wx_set.add(_ten_to_wx("印"))
        elif xi in ["比肩", "劫财"]: xi_wx_set.add(_ten_to_wx("比劫"))
        elif xi in ["食神", "伤官"]: xi_wx_set.add(_ten_to_wx("食伤"))
        elif xi in ["正财", "偏财"]: xi_wx_set.add(_ten_to_wx("财"))
        elif xi in ["正官", "七杀"]: xi_wx_set.add(_ten_to_wx("官杀"))
    xi_wx_set.discard("")

    has_xi_da_yun = False
    for d in dy_list[:4]:
        dg = d.get("gan", "")
        if TIAN_GAN_WU_XING.get(dg, "") in xi_wx_set:
            has_xi_da_yun = True
            break

    # 定级
    level_tag = "中等"
    reasons = [f"格局：{ge_ju_str}格"]

    # 顶级
    if qs_zhi and sq_level == "身强" and has_xi_da_yun and qs_cnt >= 1 and evil_cnt >= 2:
        level_tag = "顶级"
        reasons += [
            "七杀有制：恶神有制方为贵，具备统帅级潜质",
            "身强扛压：能承受高压环境和管理责任",
            "大运支持：喜用神大运连续，事业有持续上升通道",
            "结论：适合在大平台担任高管/创始人级别，事业天花板极高",
        ]
    # 上等
    elif qs_zhi and sq_level == "身强":
        level_tag = "上等"
        reasons += [
            "七杀有制：恶神制化得力，管理潜力突出",
            "身强扛压：能在高压行业中脱颖而出",
            "结论：行业专家/技术高管/中型企业VP级别，事业高度可观",
        ]
    # 中上（七杀有制但身中和或身弱但有喜用大运）
    elif qs_zhi and sq_level == "中和":
        level_tag = "中上"
        reasons += [
            "七杀有制：恶神被制，管理潜力存在但需后天开发",
            "身中和：爆发力有限但稳健",
            "结论：适合走稳扎稳打的职业路线，确定性高于爆发性",
        ]
    elif not qs_zhi and sq_level == "身强" and evil_cnt >= 3:
        level_tag = "中上"
        reasons += [
            "身强+多恶神：压力转化的潜力大，但当前无制化",
            "恶神多而无制：事业上容易大起大落",
            "结论：等待大运流年制化后可爆发，需主动管理压力",
        ]
    # 中下
    elif not qs_zhi and (sq_level == "身弱" or sq_score < 45):
        level_tag = "中下"
        reasons += [
            f"身弱（{sq_score:.0f}分）且无恶神制化：事业根基偏弱",
            "建议先补足自身能量（印比），再谋事业发展",
            "结论：需要通过大运补益，不可强求，选择适合自身能量的行业",
        ]
    # 下等
    elif not qs_zhi and sq_level == "身弱" and sq_score < 35 and not has_xi_da_yun:
        level_tag = "下等"
        reasons += [
            "身极弱+无制化+大运无补：事业基础较差",
            "建议先在稳定环境中积累，不宜过早追求事业高度",
            "结论：注重稳扎稳打，等待大运救助",
        ]
    # 中等（默认兜底）
    else:
        level_tag = "中等"
        reasons += [
            f"格局+{sq_level}：各方面平衡，事业级别主要取决于大运配合",
            "无明显的恶神制化信号，也无身弱拖累",
            "结论：中等事业格局，大运助力可升级1~2级",
        ]

    alias = {
        "顶级": "⭐⭐⭐⭐⭐ 顶级事业格局",
        "上等": "⭐⭐⭐⭐ 上等事业格局",
        "中上": "⭐⭐⭐ 中上等事业格局",
        "中等": "⭐⭐ 中等事业格局",
        "中下": "⭐ 中下等事业格局",
        "下等": "☆ 基础事业格局",
    }

    lines.append(f"**事业等级：{alias.get(level_tag, '中等')}**")
    lines.append("")
    lines.append("**定级依据：**")
    for r in reasons:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("🗣️ **白话解读：**")
    lines.append(f"> 您的事业等级是「{level_tag}」。这不是拍脑袋的结论，而是基于三个核心维度：")
    lines.append(f"> **①格局定方向**——{ge_ju_str}格决定了您做什么行业容易出彩；")
    if qs_cnt > 0:
        lines.append(f"> **②恶神制化定级别**——您命中有{qs_cnt}处七杀，{'有制化所以压力变动力' if qs_zhi else '无制化所以压力较大'}；")
    lines.append(f"> **③身强弱定承载**——您{sq_level}，{'能扛得住大风大浪' if sq_level == '身强' else '需要印比大运助身' if sq_level == '身弱' else '平衡稳健'}。")
    lines.append("")

    # ====================================================================
    # 12.3 五行定行业
    # ====================================================================
    lines.append("### 12.3 五行定行业")
    lines.append("")
    lines.append("**【金鉴真人·§12·五行定行业】** 喜用神五行决定优先推荐行业，忌神五行对应应避开行业。")
    lines.append("")

    ji_wx_set = set()
    for ji in ji_list:
        if ji in ["正印", "偏印"]: ji_wx_set.add(_ten_to_wx("印"))
        elif ji in ["比肩", "劫财"]: ji_wx_set.add(_ten_to_wx("比劫"))
        elif ji in ["食神", "伤官"]: ji_wx_set.add(_ten_to_wx("食伤"))
        elif ji in ["正财", "偏财"]: ji_wx_set.add(_ten_to_wx("财"))
        elif ji in ["正官", "七杀"]: ji_wx_set.add(_ten_to_wx("官杀"))
    ji_wx_set.discard("")

    industry_data = {
        "木": "教育/文化/出版/林业/医药/纺织/设计",
        "火": "能源/餐饮/文化传媒/互联网/电力/美容",
        "土": "房地产/建筑/农业/矿业/仓储/地产",
        "金": "金融/机械/汽车/金属/法律/审计/科技制造",
        "水": "物流/贸易/旅游/水产/IT/咨询/航运",
    }

    rows = []
    for wx in wx_list_order:
        if wx in xi_wx_set: fit = "⭐⭐⭐ 优先推荐"
        elif wx in ji_wx_set: fit = "⚠️ 谨慎选择"
        else: fit = "⭐ 一般推荐"
        rows.append([wx, industry_data.get(wx, "—"), fit])
    lines.extend(_format_table(["五行", "对应行业", "适合度"], rows))
    lines.append("")

    lines.append("**行业细分解读：**")
    lines.append("")
    for wx in wx_list_order:
        if wx in xi_wx_set:
            lines.append(f"- ✅ **{wx}行业（⭐⭐⭐ 优先推荐）**：{industry_data.get(wx,'—')}。此五行与喜用神一致，优先推荐为主业方向。")
        elif wx in ji_wx_set:
            lines.append(f"- ⚠️ **{wx}行业（谨慎选择）**：{industry_data.get(wx,'—')}。此五行与忌神一致，注意控制风险。")
        else:
            lines.append(f"- ⭐ **{wx}行业（一般推荐）**：{industry_data.get(wx,'—')}。能量中性，可作为备选。")
    lines.append("")

    # ====================================================================
    # 12.4 创业判断
    # ====================================================================
    lines.append("### 12.4 创业判断")
    lines.append("")
    lines.append("**【金鉴真人·§12·创业铁律】** 杀印相生≠适合创业！创业的本质是「财星主导+食伤生财+身强能扛」。")
    lines.append("杀印相生格适合在大平台内担任高管而非自己当老板。真正的创业命需要：")
    lines.append("①财星透干有根（赚钱欲望强）②食伤生财（有产品/服务变现能力）③身强能扛风险。")
    lines.append("")

    cai_score = cx.get("score", 0)
    cai_tou = any(
        pillars.get(p, {}).get("gan_shi_shen", "") in ["正财", "偏财"]
        for p in ["nian", "yue", "ri", "shi"]
    )
    cai_gen = any(
        cg.get("shi_shen", "") in ["正财", "偏财"]
        for p in ["nian", "yue", "ri", "shi"]
        for cg in pillars.get(p, {}).get("cang_gan", [])
    )
    ss_sc = any(
        pillars.get(p, {}).get("gan_shi_shen", "") in ["食神", "伤官"]
        for p in ["nian", "yue", "ri", "shi"]
    )

    checks = []
    checks.append(f"{'✅' if cai_tou else '❌'} 财星透干")
    checks.append(f"{'✅' if cai_gen else '❌'} 财星有根")
    checks.append(f"{'✅' if ss_sc else '❌'} {'食伤生财' if ss_sc else '无食伤生财路径'}")
    checks.append(f"{'✅' if sq_level=='身强' else '❌'} {'身强能扛风险' if sq_level=='身强' else '身弱扛风险能力不足'}")
    checks.append(f"{'✅' if cai_score>=40 else '❌'} {'财星能量充足' if cai_score>=40 else '财星能量偏弱'}")

    lines.append("**创业条件自查：**")
    for c in checks:
        lines.append(f"- {c}")
    lines.append("")

    ok_cnt = sum(1 for c in checks if c.startswith("✅"))
    if ok_cnt >= 4:
        verdict = "**适合创业**——条件充足，原局就有创业基因。建议在喜用神大运启动。"
    elif ok_cnt >= 2:
        verdict = "**可尝试但需谨慎**——有一定创业潜力但条件不完美。建议先在相关行业积累，等大运补足短板。"
    else:
        verdict = "**不太适合创业**——原局条件偏弱，更适合在大平台内部发展。"
    lines.append(f"**创业判断：{verdict}**")
    lines.append("")

    if ok_cnt >= 3:
        lines.append(f"如果决定创业，建议选择喜用神五行（{'/'.join(xi_wx_set) if xi_wx_set else '印比'}）对应的行业。最佳年龄段30~45岁。")
    else:
        lines.append(f"如果确有创业打算：①选轻资产模式；②选喜用神行业；③在印比/食伤大运年份启动；④选择身强或五行相生的合伙人。")
    lines.append("")

    lines.append("**【金鉴真人·§12·创业铁律】** ⚠️ 杀印相生≠适合创业！杀印相生是高管命不是老板命。")
    lines.append("先在大企业内部完成「技术→管理→业务」的转型，积累足够再考虑独立创业。")
    lines.append("")

    # ====================================================================
    # 12.5 职业规划
    # ====================================================================
    lines.append("### 12.5 职业规划建议")
    lines.append("")
    lines.append("**职场路线建议：**")
    lines.append("")
    ge_ju_advice = {
        "正官": "走技术+管理复合路线，先在专业领域建立口碑，再向管理岗发展。",
        "七杀": "走创新型路线，在挑战性强的岗位上更能发挥能力优势。",
        "正印": "走学术+管理复合路线，先在专业领域深耕，再拓展管理宽度。",
        "偏印": "走技术专家路线，深耕某一专业领域，成为行业专家。",
        "正财": "走业务型路线，从销售/市场等一线岗位起步，积累客户资源。",
        "偏财": "走灵活型路线，适合多领域涉猎和多渠道收入模式。",
        "比肩": "走独立专家路线，适合自由职业或专业顾问。",
        "劫财": "走合作型路线，适合团队作战和合伙创业。",
        "食神": "走创意型路线，适合将才华转化为产品和服务。",
        "伤官": "走颠覆型路线，在传统行业中找到创新的切入点。",
    }
    lines.append(ge_ju_advice.get(ge_ju_str, "根据自身兴趣和优势选择适合的路线。"))
    lines.append("")

    lines.append("**合作对象分析：**")
    wx_sk = {"木":{"生我":"水","克我":"金"},"火":{"生我":"木","克我":"水"},"土":{"生我":"火","克我":"木"},"金":{"生我":"土","克我":"火"},"水":{"生我":"金","克我":"土"}}
    rel = wx_sk.get(ri_wx, {})
    lines.append(f"作为{ri_wx}命主：最佳合作伙伴：{rel.get('生我','')}（生我者能给您支持）；需谨慎：{rel.get('克我','')}（克我者容易被压制）。")
    if xi_wx_set:
        lines.append(f"喜用神{'/'.join(xi_wx_set)}五行的人更适合长期合作。")
    lines.append("")

    # ====================================================================
    # 12.6 关键事业年份
    # ====================================================================
    lines.append("### 12.6 关键事业年份")
    lines.append("")
    years = []
    for d in dy_list[:8]:
        dg = d.get("gan", "")
        if TIAN_GAN_WU_XING.get(dg, "") in xi_wx_set:
            years.append([str(len(years)+1), d.get("gan_zhi",""), f"{d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁", "事业上升期"])
    if years:
        lines.extend(_format_table(["序号", "大运", "年龄段", "特征"], years[:6]))
    else:
        lines.extend(_format_table(["序号", "大运", "年龄段", "特征"], [["—", "—", "—", "—"]]))
    lines.append("")

    # ====================================================================
    # 12.7 事业规划时间表
    # ====================================================================
    lines.append("### 12.7 事业规划时间表")
    lines.append("")
    qy = dy_data.get("qi_yun_age", 7)
    lines.append(f"**{qy:.0f}~22岁**（求学探索期）：以学业为主，培养{ge_ju_str}格相关的基础能力。")
    lines.append("**22~35岁**（职场起步期）：在所选行业前沿积累经验，前5年完成基础技能建设。")
    lines.append("**35~50岁**（事业突破期）：人的事业高度在此阶段决定，宜向管理或专家岗发展。")
    lines.append("**50岁以后**（稳定传承期）：从一线执行转向指导、顾问角色。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


# ========================================================================
# FUNCTION 2: _gen_section11 — 学业学历分析（映射为§14）
# ========================================================================

def _gen_section11(basic: dict, analysis: dict, birth_year: int) -> list:
    """§14 学业学历分析（第0层三档法+六步精细排查+文昌双轨制+年干伤官强负信号）"""
    lines = []
    lines.append("## §14 学业学历分析")
    lines.append("")

    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    nian_gan = basic.get("nian_gan", "")
    yue_gan = basic.get("yue_gan", "")
    pillars = basic.get("pillars", {})
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 50.0)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])

    wx_order = ["木", "火", "土", "金", "水"]

    def _ss(g1, g2):
        if not g1 or not g2: return ""
        w1, w2 = TIAN_GAN_WU_XING.get(g1, ""), TIAN_GAN_WU_XING.get(g2, "")
        if not w1 or not w2 or w1 not in wx_order or w2 not in wx_order: return ""
        yy1, yy2 = YIN_YANG.get(g1, "阳"), YIN_YANG.get(g2, "阳")
        i1, i2 = wx_order.index(w1), wx_order.index(w2)
        if i1 == i2: return "比肩" if yy1 == yy2 else "劫财"
        if i2 == (i1 + 1) % 5: return "食神" if yy1 == yy2 else "伤官"
        if i2 == (i1 + 2) % 5: return "正财" if yy1 == yy2 else "偏财"
        if i2 == (i1 + 3) % 5: return "正官" if yy1 == yy2 else "七杀"
        if i2 == (i1 + 4) % 5: return "正印" if yy1 == yy2 else "偏印"
        return ""

    def _ss_wx(ss_type):
        idx = wx_order.index(ri_wx)
        m = {"印": (idx + 4) % 5, "比劫": idx, "食伤": (idx + 1) % 5,
             "财": (idx + 2) % 5, "官杀": (idx + 3) % 5}
        return wx_order[m.get(ss_type, idx)]

    # ====================================================================
    # 14.1 第0层三档法
    # ====================================================================
    lines.append("### 14.1 第0层·年柱三档法")
    lines.append("")
    lines.append("**【金鉴真人·§14·第0层三档法】** ①年柱天干为印→上等学业基因；")
    lines.append("②年柱无印但文昌在原局或18岁前大运有文昌/印运→中等；③均不符合→下等。")
    lines.append("")

    np = pillars.get("nian", {})
    nian_ss = np.get("gan_shi_shen", "")
    nian_sg = (nian_ss == "伤官")

    # 年柱有印？
    nian_yin = nian_ss in ["正印", "偏印"]
    nian_yin_d = f"年干{nian_gan}为{nian_ss}" if nian_yin else ""
    if not nian_yin:
        for cg in np.get("cang_gan", []):
            if cg.get("shi_shen", "") in ["正印", "偏印"]:
                nian_yin = True
                nian_yin_d = f"年支藏{cg.get('gan','')}为{cg.get('shi_shen','')}"

    # 文昌
    wcz = WEN_CHANG_MAP.get(nian_gan, "")
    all_z = [basic.get(f"{k}_zhi", "") for k in ["nian", "yue", "ri", "shi"]]
    wc_in = wcz in all_z

    # 18岁前文昌/印运
    early_wc = False
    early_r = ""
    fd = dy_list[0] if dy_list else {}
    fd_ss = _ss(ri_gan, fd.get("gan", "")) if fd else ""
    if fd_ss in ["正印", "偏印"]:
        early_wc = True
        early_r = f"第一步大运{fd.get('gan_zhi','')}为印星"
    for di, d in enumerate(dy_list[:2]):
        dz = d.get("zhi", d.get("gan_zhi", "")[1] if len(d.get("gan_zhi", "")) > 1 else "")
        if dz == wcz:
            early_wc = True
            early_r = f"第{di+1}步大运{d.get('gan_zhi','')}带文昌"
            break

    if nian_yin:
        tier0 = "上等"
        t0r = f"年柱有印（{nian_yin_d}），先天学习基因好，学业下限不低。"
    elif wc_in or early_wc:
        tier0 = "中等"
        if wc_in:
            t0r = f"原局有文昌（{nian_gan}文昌在{wcz}），虽年干无印但文昌可补。"
        else:
            t0r = f"年干无印但{early_r}，学业可后天补足。"
    else:
        tier0 = "下等"
        t0r = "年柱无印+文昌不显+大运无补，学业需要付出更多后天努力。"

    if nian_sg:
        t0r += " ⚠️ **年干伤官：强负信号！** 代表早年叛逆倾向、不喜传统教育、挑战权威。这是学业分析中最强的负向信号。"

    lines.append(f"**第0层判定：{tier0}**")
    lines.append(f"依据：{t0r}")
    lines.append("")

    # ====================================================================
    # 14.2 六步精细排查
    # ====================================================================
    lines.append("### 14.2 六步精细排查")
    lines.append("")
    lines.append("**【金鉴真人·§14·六步排查】** 以下六步逐一检查，综合判定实际学历等级。")
    lines.append("")

    step_results = []

    # ─ 第一步：印在月令 ─
    yp = pillars.get("yue", {})
    yss = yp.get("gan_shi_shen", "")
    yz = basic.get("yue_zhi", "")
    yc = DI_ZHI_CANG_GAN.get(yz, [])
    ybq = _ss(ri_gan, yc[0][0]) if yc else ""
    s1 = yss in ["正印", "偏印"] or ybq in ["正印", "偏印"]

    if s1:
        ysrc = "月干" if yss in ["正印","偏印"] else "月支本气"
        yt = yss if yss in ["正印","偏印"] else ybq
        d1 = f"✅ **月令有印（{ysrc}{yz}为{yt}）**：印星在月令本气得令，学业根基扎实。"
        if ybq == "正印": d1 += " 正印主正统学历上限高。"
        elif ybq == "偏印": d1 += " 偏印主深研能力强但正统学历上限需看其他因素。"
        if yss in ["正印","偏印"]: d1 += f" 月干{yue_gan}透印，优势更加突出。"
    else:
        d1 = f"❌ **月令非印（月令{yz}本气为{ybq}）**：学业需靠后天努力。"
        if ybq in ["正财","偏财"]: d1 += " 财星在月令主早慧但实践能力强于书本学习。"
        elif ybq in ["食神","伤官"]: d1 += " 食伤在月令主领悟力强但不喜死记硬背。"

    step_results.append(("①印在月令", "✅" if s1 else "❌", d1.split("：")[0] if "：" in d1 else d1[:40]))
    lines.append(f"**第一步：印在月令本气** → {'✅' if s1 else '❌'}")
    lines.append(d1)
    lines.append("")

    # ─ 第二步：印根稳固度 ─
    yin_str = 0.0
    yin_pos = []
    for pk in ["nian", "yue", "ri", "shi"]:
        for cg in pillars.get(pk, {}).get("cang_gan", []):
            if cg.get("shi_shen", "") in ["正印", "偏印"]:
                w = cg.get("weight", 30)
                yin_str += w
                yin_pos.append(f"{pk}支藏{cg.get('gan','')}({w}%)")

    if yin_str >= 100:
        d2 = f"✅ **印星根气充足（{yin_str:.0f}%）**：分布在{'、'.join(yin_pos[:5])}，根基稳固。"
        s2 = "✅"
    elif yin_str >= 30:
        d2 = f"➖ **印星有根但偏轻（{yin_str:.0f}%）**：位于{'、'.join(yin_pos[:3])}，需注意大运冲克。"
        s2 = "➖"
    else:
        d2 = f"❌ **印星在原局无根（{yin_str:.0f}%）**：完全靠天干，易被大运流年冲克。"
        s2 = "❌"

    step_results.append(("②印根稳固度", s2, d2.split("：")[0] if "：" in d2 else d2[:40]))
    lines.append(f"**第二步：印根稳固度** → {s2}")
    lines.append(d2)
    lines.append("")

    # ─ 第三步：文昌（双轨制） ─
    lines.append("**第三步：文昌贵人（双轨制）** → ")
    wc_n = WEN_CHANG_MAP.get(nian_gan, "")
    wc_r = WEN_CHANG_MAP.get(ri_gan, "")
    wc_nf = wc_n in all_z
    wc_rf = wc_r in all_z
    s3 = wc_nf or wc_rf

    if wc_nf:
        for k, lb in [("nian","年柱"),("yue","月柱"),("ri","日柱"),("shi","时柱")]:
            if basic.get(f"{k}_zhi","") == wc_n:
                lines.append(f"✅ 年干{nian_gan}文昌在{wc_n}（命理标准），位于{lb}。")
                if lb == "日柱": lines.append("  文昌在日柱→中年学运好于少年期，终身学习能力突出。")
                elif lb == "时柱": lines.append("  文昌在时柱→晚运文昌，成年后深造能力强。")
                elif lb == "年柱": lines.append("  文昌在年柱→少年学运佳。")
                break
    else:
        lines.append(f"❌ 年干{nian_gan}文昌在{wc_n}，原局无此支，命理标准文昌不显。")

    if wc_r != wc_n:
        if wc_rf:
            for k, lb in [("nian","年柱"),("yue","月柱"),("ri","日柱"),("shi","时柱")]:
                if basic.get(f"{k}_zhi","") == wc_r:
                    lines.append(f"✅ 日干{ri_gan}文昌在{wc_r}（补法标准），位于{lb}，双轨符合其一。")
                    if not wc_nf:
                        lines.append("  年干文昌不显但日干文昌到位，同样有助学运。")
                    break
        else:
            if not wc_nf:
                lines.append(f"❌ 日干{ri_gan}文昌在{wc_r}（补法），原局亦无此支，文昌彻底不显。")
                lines.append("  文昌不显不代表学业不佳，后天毅力和方法同样关键。")

    step_results.append(("③文昌贵人", "✅" if s3 else "❌", "双轨制" if s3 else "文昌不显"))
    lines.append("")

    # ─ 第四步：18岁前大运喜忌 ─
    lines.append("**第四步：18岁前大运喜忌** → ")
    xi_wx = set()
    for xi in xi_list:
        if xi in ["正印","偏印"]: xi_wx.add(_ss_wx("印"))
        elif xi in ["比肩","劫财"]: xi_wx.add(_ss_wx("比劫"))
        elif xi in ["食神","伤官"]: xi_wx.add(_ss_wx("食伤"))
        elif xi in ["正财","偏财"]: xi_wx.add(_ss_wx("财"))
        elif xi in ["正官","七杀"]: xi_wx.add(_ss_wx("官杀"))
    ji_wx = set()
    for ji in ji_list:
        if ji in ["正印","偏印"]: ji_wx.add(_ss_wx("印"))
        elif ji in ["比肩","劫财"]: ji_wx.add(_ss_wx("比劫"))
        elif ji in ["食神","伤官"]: ji_wx.add(_ss_wx("食伤"))
        elif ji in ["正财","偏财"]: ji_wx.add(_ss_wx("财"))
        elif ji in ["正官","七杀"]: ji_wx.add(_ss_wx("官杀"))

    early_dys = [d for d in dy_list if d.get("start_age", 0) < 18]
    if early_dys:
        fav, unfav = 0, 0
        for d in early_dys:
            dw = TIAN_GAN_WU_XING.get(d.get("gan",""), "")
            if dw in xi_wx: fav += 1
            elif dw in ji_wx: unfav += 1
        ds = "、".join([f"{d.get('gan_zhi','')}({d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁)" for d in early_dys])
        if fav >= unfav:
            d4 = f"✅ 18岁前喜用神运占优（{fav}喜用+{unfav}忌），大运{ds}，求学黄金期有运势加持。"
        else:
            d4 = f"⚠️ 18岁前忌神运占优（{fav}喜用+{unfav}忌），大运{ds}，需靠个人努力弥补。"
    else:
        d4 = f"起运较晚（{dy_data.get('qi_yun_age',0):.0f}岁起运），18岁前无大运影响。"
        fav, unfav = 1, 0

    s4 = fav >= unfav
    lines.append(d4)
    step_results.append(("④18岁前大运", "✅" if s4 else "❌", d4[:40]))
    lines.append("")

    # ─ 第五步：印运在求学窗口 ─
    lines.append("**第五步：印运在求学窗口** → ")
    sw_dys = [(d, d.get("start_age",0), d.get("end_age",0))
              for d in dy_list[:3] if _ss(ri_gan, d.get("gan","")) in ["正印","偏印"]]
    if sw_dys:
        in_win = any(ds <= 22 and de >= 6 for _, ds, de in sw_dys)
        wins = [f"{d.get('gan_zhi','')}({ds:.0f}~{de:.0f}岁)" for d, ds, de in sw_dys]
        if in_win:
            d5 = f"✅ 印运在求学窗口内（{'、'.join(wins)}），考试运好，考取理想学校的最佳窗口。"
            if len(wins) > 1: d5 += " 多步印运叠加，学业优势可持续。"
        else:
            d5 = f"⚠️ 印运不在6~22岁求学窗口（{'、'.join(wins)}），对学历提升帮助有限。"
    else:
        in_win = False
        d5 = "⚠️ 求学阶段无印运，学业主要靠个人努力。"
    s5 = in_win
    lines.append(d5)
    step_results.append(("⑤印运在窗口内", "✅" if s5 else "❌" if sw_dys else "⚠️", d5[:40]))
    lines.append("")

    # ─ 第六步：年干伤官检查 ─
    lines.append("**第六步：年干伤官排除** → ")
    if nian_sg:
        d6 = "⚠️ **年干伤官——强负信号激活！** 年干伤官代表早年叛逆、不喜传统教育。需要极强的印星或文昌来抵消此信号。"
        s6 = False
    else:
        d6 = "✅ 年干非伤官，排除了学业上最强的负向信号。"
        s6 = True
    lines.append(d6)
    step_results.append(("⑥年干伤官排除", "✅" if s6 else "❌", "无伤官" if s6 else "伤官强负"))
    lines.append("")

    # 汇总表
    lines.append("**六步排查汇总表：**")
    lines.append("")
    lines.extend(_format_table(
        ["步骤", "结果", "关键判断"],
        [[n, r, d[:40]+"…" if len(d) > 40 else d] for n, r, d in step_results]
    ))
    lines.append("")

    # ====================================================================
    # 14.3 综合学历判定
    # ====================================================================
    lines.append("### 14.3 综合学历判定")
    lines.append("")
    lines.append("**【金鉴真人·§14·学历综合判定】** 学业基因×兑现条件=实际学历。")
    lines.append("")

    pos = sum(1 for _, r, _ in step_results if r == "✅")
    neg = sum(1 for _, r, _ in step_results if r == "❌")
    warn = sum(1 for _, r, _ in step_results if r in ("⚠️", "➖"))
    ts = 1 if tier0 == "上等" else 0 if tier0 == "中等" else -1
    sg_pen = -2 if nian_sg else 0
    total = ts + (pos - neg) + sg_pen + (warn * -0.5)

    if total >= 3:
        grade = "高学历（硕士以上）"
        gd = "学业基因极强+大运配合+文昌到位，具备冲刺硕博的能力。"
    elif total >= 1:
        grade = "中等偏上（本科~一本）"
        gd = "学业基因较好但存在制约因素，可达较好的本科水平。"
        if tier0 == "上等": gd += " 第0层虽为上等，但兑现条件限制了上限。"
    elif total >= -1:
        grade = "中等（大专~本科）"
        gd = "学业基因一般或兑现条件一般。"
        if nian_sg: gd += " 年干伤官的强负信号是主要制约。"
    elif total >= -3:
        grade = "基础学历（高中/中专）"
        gd = "学业基因偏弱，但可能在学业之外的领域有更强能力。"
    else:
        grade = "基础学历或学业后发"
        gd = "需要大运中的印星窗口补足，30岁后继续教育可能突破。"

    lines.append(f"**综合判定：{grade}**")
    lines.append(f"评分：第0层{tier0}({ts:+d}) + 六步{pos}正{neg}负 + {'' if sg_pen==0 else '伤官('+str(sg_pen)+')'} = 总分{total:.1f}")
    lines.append("")
    lines.append(gd)
    lines.append("")

    # ====================================================================
    # 14.4 文昌双轨制深度
    # ====================================================================
    lines.append("### 14.4 文昌双轨制深度解读")
    lines.append("")
    lines.append("**【金鉴真人·§14·文昌双轨制】** 两套查法互补：①年干查命理标准（传统）②日干查补法标准（现代）。")
    lines.append("")

    lines.append(f"**命理标准（年干{nian_gan}查）：**")
    lines.append(f"- 文昌在地支「{wc_n}」")
    if wc_nf:
        for k, lb in [("nian","年柱"),("yue","月柱"),("ri","日柱"),("shi","时柱")]:
            if basic.get(f"{k}_zhi","") == wc_n:
                lines.append(f"- ✅ 文昌在{lb}，文昌到位！")
                break
    else:
        lines.append(f"- ❌ 原局无「{wc_n}」，文昌不显")

    lines.append("")
    lines.append(f"**补法标准（日干{ri_gan}查）：**")
    lines.append(f"- 文昌在地支「{wc_r}」")
    if wc_rf:
        for k, lb in [("nian","年柱"),("yue","月柱"),("ri","日柱"),("shi","时柱")]:
            if basic.get(f"{k}_zhi","") == wc_r:
                lines.append(f"- ✅ 文昌在{lb}（补法），双轨制至少一轨符合！")
                break
    else:
        lines.append(f"- ❌ 原局无「{wc_r}」，补法亦不显")
        if not wc_nf:
            lines.append("- 两套查法均不显，文昌彻底缺失，但后天努力可补足")

    lines.append("")
    if birth_year >= 2001:
        lines.append("**文昌补位方案（2001年后出生适用）：**")
        lines.append("")
        if not wc_nf and not wc_rf:
            lines.append(f"文昌双轨均不显，建议：①方位补法——书房{wc_n}方位放文昌塔；②颜色补法——多用绿色/蓝色系；③佩戴补法——兔形饰品。")
        elif wc_nf:
            lines.append("命理文昌已到位，无需额外补文昌。")
        elif wc_rf:
            lines.append(f"日干补法文昌已到位，若想加强可在书房{wc_n}方位放文昌塔。")

    lines.append("")
    wc_late = False
    for k in ["ri", "shi"]:
        if wc_nf and basic.get(f"{k}_zhi","") == wc_n:
            wc_late = True
        if wc_rf and basic.get(f"{k}_zhi","") == wc_r:
            wc_late = True
    if wc_late:
        lines.append("文昌在日时柱→中年后学习能力强，适合终身学习。")
    else:
        lines.append("文昌在年/月柱→少年学运强于中年，成年后需更多主动投入。")
    lines.append("")

    # ====================================================================
    # 14.5 学历提升建议
    # ====================================================================
    lines.append("### 14.5 学历提升建议")
    lines.append("")
    if grade.startswith("高学历"):
        lines.append("命局已具高学历条件，建议继续深造。如有考研计划，选喜用神五行对应的大运年份成功率最高。")
    elif grade.startswith("中等"):
        yun_list = [d.get("gan_zhi","") for d in dy_list[:3] if _ss(ri_gan, d.get("gan","")) in ["正印","偏印"]]
        lines.append(f"建议在印比大运期间（{'、'.join(yun_list) if yun_list else '行印运的年份'}）重点发力，这是提升学历的最佳窗口。")
        lines.append("可考虑在职硕士/进修，利用文昌能量弥补学历短板。")
    else:
        lines.append("学业条件一般，但人生不只有学历一条路：")
        lines.append("如果还在求学，在印比大运期间加把劲仍有机会突破；")
        lines.append("如果已工作，建议通过职业技能认证提升竞争力。")
        lines.append("命局可能在实践型学习上更有优势，不必执着于学历。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


# ========================================================================
# FUNCTION 3: generate_report() — 修正§10~§15编号顺序
# ========================================================================

def generate_report(bazi_result: dict, name: str, gender: str,
                    birth_info: Optional[dict] = None) -> dict:
    """生成完整21§报告 — 全规则驱动，同一生辰输入永远输出相同报告"""
    basic = bazi_result.get("basic", {})
    analysis = bazi_result.get("analysis", {})
    pillars = basic.get("pillars", {})

    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ri_yy = YIN_YANG.get(ri_gan, "")

    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    ge_ju_str = analysis.get("ge_ju", "正印")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    cx = analysis.get("cai_xing", {})
    cai_score = cx.get("score", 0)
    wealth_level = cx.get("wealth_level", "小富")
    energy = analysis.get("energy", {})
    wx_strong = energy.get("strongest", "")
    wx_weak = energy.get("weakest", "")
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    qi_yun_age = dy_data.get("qi_yun_age", 0)

    # ─── 五行能量计算（引擎未提供时从四柱藏干推算）────
    if not energy or not energy.get("wu_xing_energy"):
        wx_map = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        cg_map = {"子":[("癸",100)],"丑":[("己",100),("癸",60),("辛",30)],
            "寅":[("甲",100),("丙",60),("戊",30)],"卯":[("乙",100)],
            "辰":[("戊",100),("乙",60),("癸",30)],"巳":[("丙",100),("戊",60),("庚",30)],
            "午":[("丁",100),("己",60)],"未":[("己",100),("丁",60),("乙",30)],
            "申":[("庚",100),("壬",60),("戊",30)],"酉":[("辛",100)],
            "戌":[("戊",100),("辛",60),("丁",30)],"亥":[("壬",100),("甲",60)]}
        wx_energy_raw = {"木":0.0,"火":0.0,"土":0.0,"金":0.0,"水":0.0}
        for g in [basic.get("nian_gan",""),basic.get("yue_gan",""),basic.get("ri_gan",""),basic.get("shi_gan","")]:
            if g in wx_map:
                wx_energy_raw[wx_map[g]] += 1.0
        for z in [basic.get("nian_zhi",""),basic.get("yue_zhi",""),basic.get("ri_zhi",""),basic.get("shi_zhi","")]:
            for cg, w in cg_map.get(z, []):
                if cg in wx_map:
                    wx_energy_raw[wx_map[cg]] += w / 100.0
        total = sum(wx_energy_raw.values())
        pct = {}
        for k, v in wx_energy_raw.items():
            pct[k] = round(v / total * 100, 1) if total > 0 else 0.0
        sorted_wx = sorted(wx_energy_raw.items(), key=lambda x: x[1], reverse=True)
        wx_strong = sorted_wx[0][0] if sorted_wx else ""
        wx_weak = sorted_wx[-1][0] if sorted_wx else ""
        energy = {"wu_xing": {k: f"{v}%" for k,v in pct.items()},
                  "wu_xing_energy": pct, "strongest_wx": wx_strong, "weakest_wx": wx_weak}
        analysis["energy"] = energy
    wx_strong = energy.get("strongest_wx", energy.get("strongest", ""))
    wx_weak = energy.get("weakest_wx", energy.get("weakest", ""))

    # 提取出生年份
    birth_year = 2000
    if birth_info and "birth_year" in birth_info:
        birth_year = birth_info["birth_year"]
    elif birth_info and "year" in birth_info:
        birth_year = birth_info["year"]
    else:
        solar_date = basic.get("solar_date", "")
        if "年" in solar_date:
            try:
                birth_year = int(solar_date.split("年")[0])
            except (ValueError, IndexError):
                pass

    lines = []
    version = f"v1.0.{datetime.now().strftime('%m%d')}"

    # ═══════════════════════════════════════════════
    # §1 一页总览
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section1(basic, analysis, name, gender, version))

    # §2 格局分析
    lines.extend(_gen_section2(basic, analysis))

    # §3 身强弱详解
    lines.extend(_gen_section3(basic, analysis))

    # §4 喜用神详解
    lines.extend(_gen_section4(basic, analysis))

    # §5 灾祸/疾病/搬迁专项
    lines.extend(_gen_section5(basic, analysis))

    # §6 性格分析（注：本节内部标记§6，之后重排到§13）
    lines.extend(_gen_section6(basic, analysis))

    # §7 身材外貌分析
    lines.extend(_gen_section7(basic, analysis))

    # §8 财富分析
    lines.extend(_gen_section8(basic, analysis))

    # §9 置业/买房分析（注：目标为§9父母六亲，待合并_gen_section15）
    lines.extend(_gen_section9(basic, analysis))

    # ═══════════════════════════════════════════════
    # §10 婚姻感情分析（← 原§12 _gen_section12）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section12(basic, analysis))

    # ═══════════════════════════════════════════════
    # §11 子女/文昌分析（← 原§13 _gen_section13）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section13(basic, analysis))

    # ═══════════════════════════════════════════════
    # §12 事业分析（← NEW _gen_section10）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section10(basic, analysis, birth_year))

    # ═══════════════════════════════════════════════
    # §13 性格分析（← 原§6 _gen_section6）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section6(basic, analysis))

    # ═══════════════════════════════════════════════
    # §14 学业学历分析（← NEW _gen_section11）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section11(basic, analysis, birth_year))

    # ═══════════════════════════════════════════════
    # §15 健康分析（← 原§14 _gen_section14）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section14(basic, analysis))

    # §15附属：六亲分析（原§15，待后续合并到§9父母六亲）
    lines.extend(_gen_section15(basic, analysis))

    # ═══════════════════════════════════════════════
    # §16 事件总表
    # §17 大运精析
    # §18 三决断
    # §19 运程总评
    # §20 五行补充建议
    # §21 人生建议
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section16(basic, analysis, birth_year))
    lines.extend(_gen_section17(basic, analysis, birth_year))
    lines.extend(_gen_section18(basic, analysis))
    lines.extend(_gen_section19(basic, analysis, birth_year))
    lines.extend(_gen_section20(basic, analysis))
    lines.extend(_gen_section21(basic, analysis))

    # ═══════════════════════════════════════════════
    # 补充深化内容
    # ═══════════════════════════════════════════════
    lines.append("")
    lines.append("### 13.5 人格特质的阶段性表现")
    lines.append("")
    lines.append("| 人生阶段 | 主导特质 | 表现特征 |")
    lines.append("|:---------|:---------|:---------|")
    ri_wx_desc = {"金":"刚毅果断","木":"仁慈宽厚","水":"智慧灵动","火":"热情开朗","土":"稳重诚信"}
    desc = ri_wx_desc.get(ri_wx, "特质鲜明")
    lines.append(f"| **青少年期** | {ge_ju_str}格底色初显 | 展现{desc}特质 |")
    lines.append(f"| **青年期** | 十神组合激活 | {ge_ju_str}格优势转化为竞争力 |")
    lines.append(f"| **中年期** | 格局定型·能量释放 | 喜用神大运期间核心特质最大化 |")
    lines.append(f"| **晚年期** | 回归本真·调和平衡 | 各人格特质趋于平衡 |")
    lines.append("")

    lines.append("### 16.2 未来十年关键流年提示")
    lines.append("")
    lines.append("| 年份 | 干支 | 天干五行 | 喜忌 | 重点关注 | 建议 |")
    lines.append("|:----:|:----:|:---------|:----|:---------|:-----|")
    cy = datetime.now().year
    for y in range(cy, cy + 10):
        tg = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"][abs(y - 4) % 10]
        dz = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"][abs(y) % 12]
        wx = TIAN_GAN_WU_XING.get(tg, "")
        if wx in xi_list:
            j, f, s = "喜用", "事业/财运", "积极进取"
        elif wx in ji_list:
            j, f, s = "忌神", "健康/守成", "谨慎保守"
        else:
            j, f, s = "中性", "稳步发展", "按部就班"
        lines.append(f"| {y} | {tg+dz} | {wx} | {j} | {f} | {s} |")
    lines.append("")

    lines.append("### 21.7 具体行动指南")
    lines.append("")
    lines.append(f"**事业：** 选择喜用神（{'/'.join(xi_list)}）对应行业深耕，每三年做职业评估，在最佳大运期间争取晋升。")
    lines.append(f"**财富：** 当前等级{wealth_level}，不盲目追求高风险，建立稳健储蓄计划。")
    lines.append("**健康：** 关注五行过旺/过弱对应的器官系统，每年全面体检。")
    lines.append("**人际：** 与喜用神五行人群建立深度合作。")
    lines.append("**学习：** 保持终身学习，每1~2年掌握一项新技能。")
    lines.append("")

    # 实证对照
    lines.append("---")
    lines.append("")
    lines.append("## 实证对照校准")
    lines.append("")
    lines.append("| 序号 | 命理判断 | 依据 |")
    lines.append("|:----:|:---------|:-----|")
    lines.append(f"| 1 | 日主{ri_gan}{ri_wx}性 | 四柱排盘+十神定位 |")
    lines.append(f"| 2 | {ge_ju_str}格成立 | 月令本气+透干确认 |")
    lines.append(f"| 3 | {sq_level}（{sq_score}分） | 精密评分法 |")
    lines.append(f"| 4 | 喜{'/'.join(xi_list)}忌{'/'.join(ji_list)} | 身强弱+五行平衡 |")
    lines.append(f"| 5 | {dy_data.get('qi_yun_age',0):.1f}岁起运 | 阳男阴女顺/阴男阳女逆 |")
    lines.append("")

    # 五行能量深度分析
    lines.append("---")
    lines.append("## 附录：五行能量深度分析")
    lines.append("")
    pct = energy.get("wu_xing_energy", {})
    lines.append("| 五行 | 能量值 | 状态 | 对应器官 | 调养方向 |")
    lines.append("|:----|:------:|:----|:---------|:---------|")
    organs = {"木":"肝胆","火":"心脏","土":"脾胃","金":"肺","水":"肾"}
    for wx_n in ["木","火","土","金","水"]:
        val = pct.get(wx_n, 0)
        if val > 30: st = "过旺·需泄"
        elif val > 20: st = "✅平衡"
        elif val > 10: st = "偏弱·需补"
        else: st = "极弱·急需补"
        dire = f"补{wx_n}（喜用）" if wx_n in xi_list else f"泄{wx_n}（忌神）" if wx_n in ji_list else "维持中性"
        lines.append(f"| {wx_n} | {val:.1f}% | {st} | {organs.get(wx_n,'—')} | {dire} |")
    lines.append("")
    lines.append("---")
    lines.append(f"*报告版本：{version} | 金鉴真人·全规则驱动·确定性输出*")
    lines.append("")

    report_text = "\n".join(lines)
    return {
        "report": report_text,
        "sections": 21,
        "total_lines": len(lines),
        "version": version,
    }
