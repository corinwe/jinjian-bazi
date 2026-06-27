def _gen_section6(basic: dict, analysis: dict) -> list:
    """§6 性格分析（五重人格交织+十神底色+白话解读）— 220行"""
    lines = []
    lines.append("## §6 性格分析（五重人格交织）")
    lines.append("")

    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ri_yy = YIN_YANG.get(ri_gan, "")
    ri_zhi = basic.get("ri_zhi", "")
    ge_ju_str = analysis.get("ge_ju", "正印")
    pillars = basic.get("pillars", {})
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])

    yy_desc = {"阳": "阳刚", "阴": "阴柔"}.get(ri_yy, "")
    yy_gangrou = {"阳": "刚强主动，气势外放", "阴": "柔顺内敛，心思细腻"}.get(ri_yy, "")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 开头总述
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.append(f"{ri_gan}命主的性格并非单一维度，而是由五重人格交织而成——")
    lines.append(f"日主「{ri_wx}性{ri_gan}」赋予底色，格局「{ge_ju_str}格」定义主调，")
    lines.append("十神带来层次深度，身强弱决定行为力道，喜用神指引成长方向。")
    lines.append(f"这五重特质相互叠加、彼此修正，共同造就了一个独特而丰满的你。")
    lines.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 特质一：日主五行人格
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.append("### 特质一：日主五行人格")
    lines.append("")

    wx_base_desc = {
        "金": f"「金曰从革」——{ri_gan}为{ri_yy}金。你的骨子里带着金属般的坚韧与果断，做事讲原则、重效率，在团队中是规则的执行者和秩序的守护者。",
        "木": f"「木曰曲直」——{ri_gan}为{ri_yy}木。你天性中有木的生机与柔韧性，善于规划、有远见，待人宽厚有仁者之风，能包容不同的声音。",
        "水": f"「水曰润下」——{ri_gan}为{ri_yy}水。你思维敏捷灵动，善于适应环境变化，洞察力强，沟通出色，能在复杂局面中找到最优解。",
        "火": f"「火曰炎上」——{ri_gan}为{ri_yy}火。你热情开朗有感染力，善于在人群中脱颖而出，有领导潜质，能点燃团队的激情与动力。",
        "土": f"「土曰稼穑」——{ri_gan}为{ri_yy}土。你稳重踏实，做事靠谱持久，有耐心和韧性，是团队中值得信赖的基石型人物。",
    }
    lines.append(wx_base_desc.get(ri_wx, f"日主为{ri_gan}（{ri_wx}性），性格与{ri_wx}五行属性深度关联。"))

    wx_yy_desc = {
        "金": f"作为{yy_desc}金，{ri_gan}为{'庚' if ri_yy=='阳' else '辛'}金，{'锋芒外露、锐不可当，但需学会藏锋守拙' if ri_yy=='阳' else '内敛精致、追求完美，但需避免过于苛求细节'}。",
        "木": f"作为{yy_desc}木，{ri_gan}为{'甲' if ri_yy=='阳' else '乙'}木，{'高大挺拔、遮荫一方，但需注意根基稳固' if ri_yy=='阳' else '柔韧灵秀、随风而曲，但需培养内在定力'}。",
        "水": f"作为{yy_desc}水，{ri_gan}为{'壬' if ri_yy=='阳' else '癸'}水，{'江河奔涌、势不可挡，但需学会细水长流' if ri_yy=='阳' else '雨露润物、细腻入微，但需避免过度敏感'}。",
        "火": f"作为{yy_desc}火，{ri_gan}为{'丙' if ri_yy=='阳' else '丁'}火，{'烈日当空、普照万物，但需懂得收敛锋芒' if ri_yy=='阳' else '灯烛之光、温暖细腻，但需防止自我消耗'}。",
        "土": f"作为{yy_desc}土，{ri_gan}为{'戊' if ri_yy=='阳' else '己'}土，{'高山厚土、巍峨不动，但需避免固执己见' if ri_yy=='阳' else '田园沃土、滋养万物，但需建立边界意识'}。",
    }
    lines.append(wx_yy_desc.get(ri_wx, f"命主为{yy_desc}之{ri_wx}，{yy_gangrou}。"))

    sq_mod_wx = {
        "身强": f"身强（{sq_score}分）让日主{ri_wx}的能量更为外放，行事果决有力，但也容易过于刚硬。",
        "身弱": f"身弱（{sq_score}分）让日主{ri_wx}的能量更为内敛，行事谨慎周全，但也需要外力推动。",
        "中和": f"中和（{sq_score}分）让日主{ri_wx}的能量刚柔并济，行事张弛有度，是难得的平衡态。",
    }
    lines.append(sq_mod_wx.get(sq_level, f"身强弱修正：{sq_level}（{sq_score}分），影响日主的能量表达方式。"))

    # 五行特质延伸
    wx_color = WU_XING_COLORS.get(ri_wx, "")
    wx_number = WU_XING_NUMBERS.get(ri_wx, "")
    wx_direction = WU_XING_DIRECTIONS.get(ri_wx, "")
    wx_season = WU_XING_SEASONS.get(ri_wx, "")
    wx_taste = WU_XING_TASTES.get(ri_wx, "")
    lines.append(f"五行特性延伸：「{ri_wx}」的代表色为{wx_color}，吉利数字为{wx_number}，方向为{wx_direction}，对应季节为{wx_season}，五味为{wx_taste}。")
    lines.append(f"建议在日常生活中多使用{wx_color}元素、向{wx_direction}发展或选择{wx_season}相关的行业，有助于增强气场和运势。")

    strong_wx = analysis.get("energy", {}).get("strongest", "")
    weak_wx = analysis.get("energy", {}).get("weakest", "")
    if strong_wx and weak_wx:
        lines.append(f"命局五行能量分布中，最强为「{strong_wx}」，最弱为「{weak_wx}」。{weak_wx}是需要补益的方向，可通过相关颜色和方位来调和。")

    ba_hua_wx = {
        "金": f"🗣️ 白话类比：你就像一把经过千锤百炼的{'宝剑' if ri_yy=='阳' else '精致刀具'}，天生锋利、自带动能。但记住，最锋利的刀也需要刀鞘的保护——柔韧是你的必修课。",
        "木": f"🗣️ 白话类比：你就像一棵{'参天大树' if ri_yy=='阳' else '婀娜垂柳'}，根植大地、向阳而生。但别忘了，暴风雨来临时懂得弯腰的树才能活得更久——灵活是你的选修课。",
        "水": f"🗣️ 白话类比：你就像一条{'奔腾的江河' if ri_yy=='阳' else '涓涓的溪流'}，灵动自如、遇山开路。但水无定型，需要有河床的引导才能汇聚成海——方向感是你的必修课。",
        "火": f"🗣️ 白话类比：你就像一团{'熊熊烈火' if ri_yy=='阳' else '温暖的烛光'}，热情洋溢、自带光芒。但火需要燃料也需要节制——学会控制火候，才能温暖他人而不灼伤自己。",
        "土": f"🗣️ 白话类比：你就像{'一座巍峨的山峰' if ri_yy=='阳' else '一片肥沃的田野'}，承载包容、稳固可靠。但土也需要翻耕才能保持活力——适时打破舒适区，是你的成长方向。",
    }
    lines.append(ba_hua_wx.get(ri_wx, f"🗣️ 白话类比：你的{ri_wx}性底色注定了你的基础性格风格。"))
    lines.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 特质二：格局人格
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.append("### 特质二：格局人格")
    lines.append("")

    gj_four_god = ["正印", "食神", "正官", "正财"]
    gj_four_devil = ["七杀", "偏印", "伤官", "劫财"]

    if ge_ju_str in gj_four_god:
        gj_quality = "四大吉神之一，温和正面的能量场"
    elif ge_ju_str in gj_four_devil:
        gj_quality = "四大凶神之一，激烈反叛的能量场"
    else:
        gj_quality = "中性平和，能量中庸"

    lines.append(f"格局为「{ge_ju_str}格」，属于{gj_quality}。")
    lines.append(f"格局是命局中最稳定的性格框架，它决定了你在面对重大选择时的底层行为逻辑和价值判断标准。")
    lines.append("")

    gj_detail = {
        "正官": f"正官格局赋予你天生的责任感与自律精神。你做事有原则、遵纪守法，是天生的组织者和管理者。",
        "七杀": f"七杀格局赋予你强烈的进取心和竞争意识。你敢闯敢拼、不畏困难，有非凡的魄力和抗压能力。",
        "正印": f"正印格局赋予你稳重的学识气质。你学习能力强、善于总结归纳，有浓厚的书卷气和人文素养。",
        "偏印": f"偏印格局赋予你独特的思维方式和深度钻研能力。你擅长解构复杂问题，不随大流、有独立见解。",
        "正财": f"正财格局赋予你踏实求财的本能和稳健的理财观念。你善于积累、不投机取巧，是典型的稳健型人格。",
        "偏财": f"偏财格局赋予你广阔的财路和灵活的社交手腕。你有商业头脑，懂得灵活变通，是天生的生意人。",
        "比肩": f"比肩格局赋予你独立自主的个性和强大的个人能力。你自尊心强，不适合被过度约束。",
        "劫财": f"劫财格局赋予你广泛的社交能力和重情重义的品格。你善于在合作中发挥作用，是团队的粘合剂。",
        "食神": f"食神格局赋予你丰富的才华和乐观的生活态度。你有创意天赋，善于享受生活，是团队中的快乐源泉。",
        "伤官": f"伤官格局赋予你聪敏灵动的才思和鲜明的个性。你表达能力强，有创新精神和叛逆意识。",
    }
    lines.append(gj_detail.get(ge_ju_str, f"格局为{ge_ju_str}格，形成独特的性格行为模式。"))

    gj_traps = {
        "正官": "潜在陷阱：过于循规蹈矩，在需要创新突破的环境中可能束手束脚。建议在规则中找到灵活的空间。",
        "七杀": "潜在陷阱：强势风格容易树敌，需要学会柔和处事和化敌为友。刚猛有余而柔韧不足是最大的短板。",
        "正印": "潜在陷阱：安于现状、缺乏闯劲，需要主动开拓新战场。别让舒适区成为你的牢笼。",
        "偏印": "潜在陷阱：不善交际、容易孤僻，需要加强团队协作意识。孤胆英雄难成大事。",
        "正财": "潜在陷阱：过于保守可能错失良机，需要适度拓宽眼界。稳健不等于固步自封。",
        "偏财": "潜在陷阱：财来财去，需要建立稳健的守财机制。会赚更要会守。",
        "比肩": "潜在陷阱：固执己见，需要学习团队协作和换位思考。独立不等于独断。",
        "劫财": "潜在陷阱：易被朋友所累，需要学会分辨真假朋友和坚守底线。义气需要智慧来配。",
        "食神": "潜在陷阱：容易放纵享乐，需要保持自律和持续的进取心。安逸是才华的慢性毒药。",
        "伤官": "潜在陷阱：锋芒毕露易得罪人，需要学会收敛和控制表达方式。才华需要包装才能被接受。",
    }
    lines.append(gj_traps.get(ge_ju_str, ""))
    lines.append("")

    gj_skills = {
        "正官": "擅长领域：体制内、规范化企业、行政管理。你的组织能力是最大的职业资本。",
        "七杀": "擅长领域：军警、创业、高压力管理岗。越是高压的环境，你越能脱颖而出。",
        "正印": "擅长领域：教育、研究、文化出版、行政后勤。知识和文化是你的核心竞争力。",
        "偏印": "擅长领域：技术研发、战略分析、学术研究。你的独特视角是最大的创新源泉。",
        "正财": "擅长领域：财务管理、实体经营、会计审计。稳健的财务思维是最大的优势。",
        "偏财": "擅长领域：投资、销售、市场拓展、自由职业。灵活的思维是你最大的武器。",
        "比肩": "擅长领域：自由职业、技术专家、独立顾问。一个人的战斗力不容小觑。",
        "劫财": "擅长领域：公关、销售、合作创业、中介服务。人脉就是你最大的资产。",
        "食神": "擅长领域：设计、研发、创意策划、艺术创作。才华是你最闪亮的名片。",
        "伤官": "擅长领域：创作、研发、表演、策划。创新是你的核心竞争力。",
    }
    lines.append(gj_skills.get(ge_ju_str, ""))
    lines.append("")

    # 格局的十神互动组合
    gj_success_tips = {
        "正官": "格局配合：制化七杀则官星更显贵气，食伤生财则事业发展持久。官星喜清不喜杂，切忌比劫争官。",
        "七杀": "格局配合：食神制杀则化权为贵，印星化杀则文武双全。七杀有制者为将才，无制者为莽夫。",
        "正印": "格局配合：官印相生则贵气更显，财星不破印则学以致用。印星喜静，不宜被财星冲克。",
        "偏印": "格局配合：偏印配食神为「枭神夺食」需注意，配正财则技术生财。偏印宜深入某一领域，忌心浮气躁。",
        "正财": "格局配合：正财坐库则财富积累快，配官星则财官双美。正财喜稳固，切忌七杀破格。",
        "偏财": "格局配合：偏财配七杀则大财需大勇，配食伤则才华生财。偏财宜动中求财，忌坐守空等。",
        "比肩": "格局配合：比肩配正财则合伙生财，配七杀则竞争上位。比肩喜合作，忌孤军奋战。",
        "劫财": "格局配合：劫财配伤官则才华变现快，配偏财则合作生财。劫财喜团队作战，忌独吞利益。",
        "食神": "格局配合：食神配正印则艺文出众，配偏财则才华生财。食神宜发挥创意，忌被枭神夺之。",
        "伤官": "格局配合：伤官配正印则才华有根，配正财则技艺生财。伤官宜有制化，忌锋芒过露。",
    }
    lines.append(gj_success_tips.get(ge_ju_str, "格局的配合需根据具体大运流年综合判断。"))
    lines.append("")
    lines.append("【金鉴真人·§6·格局定性格】格局之吉凶不在于格名，而在于是否有制化、有配合。吉神需护，凶神有制反为权贵。四吉神顺用，四凶神逆制，方得格局之妙。")
    lines.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 特质三：十神底色
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.append("### 特质三：十神底色")
    lines.append("")

    ss_weights = {}
    ss_positions = {}

    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss and ss != "日主":
            ss_weights[ss] = ss_weights.get(ss, 0) + 1.0
            if ss not in ss_positions:
                ss_positions[ss] = []
            ss_positions[ss].append(f"{pos_label}干")
        for cg in p.get("cang_gan", []):
            cg_ss = cg.get("shi_shen", "")
            cg_wt = cg.get("weight", 50) / 100.0
            if cg_ss and cg_ss != "日主":
                ss_weights[cg_ss] = ss_weights.get(cg_ss, 0) + cg_wt
                if cg_ss not in ss_positions:
                    ss_positions[cg_ss] = []
                ss_positions[cg_ss].append(f"{pos_label}支")

    sorted_ss = sorted(ss_weights.items(), key=lambda x: x[1], reverse=True)
    top3_ss = [ss for ss, _ in sorted_ss[:3]]
    while len(top3_ss) < 3:
        if ge_ju_str not in top3_ss:
            top3_ss.append(ge_ju_str)
        else:
            top3_ss.append("正印")

    lines.append(f"十神是性格的调味剂——天干透出的是明面上的特质，地支藏干则是暗藏的能量底色。")
    lines.append(f"命局中影响力最强的三大十神为：{'、'.join([f'「{ss}」' for ss in top3_ss])}。它们分别在各自的位置上塑造着你的行为模式和人际风格。")

    gj_count = sum(1 for ss in top3_ss if ss in gj_four_god)
    xj_count = sum(1 for ss in top3_ss if ss in gj_four_devil)
    if gj_count > xj_count:
        lines.append(f"三大十神中吉神占优（{gj_count}:{xj_count}），整体性格偏向温和包容，人际中以善意为底色。")
    elif xj_count > gj_count:
        lines.append(f"三大十神中凶神占优（{xj_count}:{gj_count}），性格中有锐气和竞争意识，需要学会调节锋芒。")
    else:
        lines.append(f"三大十神吉凶均衡（{gj_count}:{xj_count}），性格中有刚有柔，能在不同场合灵活切换状态。")
    lines.append("")

    # 十神底色详解表
    lines.append("**十神底色详解表：**")
    lines.append("")
    table_rows = []
    for ss in top3_ss:
        t = _get_shi_shen_trait(ss)
        pos_str = "、".join(ss_positions.get(ss, ["月柱"]))
        table_rows.append([
            f"{_ss_star(ss)} {ss}",
            pos_str,
            t["core"],
            t["work"],
            t["blind"]
        ])
    lines.extend(_format_table(
        ["十神", "位置", "核心特质", "职场表现", "盲区"],
        table_rows
    ))
    lines.append("")

    ss_group_labels = {
        "正官": "吉神·责任型", "七杀": "凶神·魄力型",
        "正印": "吉神·学识型", "偏印": "凶神·钻研型",
        "正财": "吉神·稳健型", "偏财": "平神·灵活型",
        "比肩": "平神·独立型", "劫财": "凶神·社交型",
        "食神": "吉神·才华型", "伤官": "凶神·创意型",
    }

    pos_meaning = {
        "年柱": "代表先天禀赋和早年环境，此处的十神特质往往在童年就已初露端倪。",
        "月柱": "月柱是格局宫兼父母宫，此处的十神影响力最强，奠定一生的性格基调。",
        "日柱": "日支为配偶宫兼自身根基，藏干十神影响亲密关系和内在的深层动机。",
        "时柱": "时柱为归宿宫，此处的十神反映晚年的状态和最终的人生走向。",
    }

    for i, ss in enumerate(top3_ss):
        t = _get_shi_shen_trait(ss)
        star = _ss_star(ss)
        group_label = ss_group_labels.get(ss, "")
        pos_str = "、".join(ss_positions.get(ss, ["月柱"]))
        lines.append(f"**{'❶❷❸'[i]} {ss}{star}（{group_label}）**")
        lines.append("")
        lines.append(f"- 核心特质：{t['core']}。{t['strength']}。")
        lines.append(f"- 职场表现：{t['work']}。")
        lines.append(f"- 盲区提醒：{t['blind']}。")
        lines.append(f"- 命局分布：{pos_str}。")

        positions_found = ss_positions.get(ss, [])
        pos_notes = []
        for pf in positions_found:
            pillar_name = pf.replace("干", "柱").replace("支", "柱")
            if pillar_name in pos_meaning:
                pos_notes.append(f"{pf}{pos_meaning[pillar_name]}")
        if pos_notes:
            lines.append(f"  └ 位置解读：{' '.join(pos_notes)}")

        if ss in gj_four_god:
            lines.append(f"  └ 此十神为吉神，温和正面，但忌被冲克——大运流年中注意保护，切勿被恶神破坏。")
        elif ss in gj_four_devil:
            lines.append(f"  └ 此十神为凶神，激烈有锐气，但有制化则为权贵——找到能「制」你的十神（如食神制杀、印化七杀等），把破坏力转化为创造力。")
        else:
            lines.append(f"  └ 此十神为平神，中性平和，贵在配合——与吉神相伴则锦上添花，与凶神相伴则火上浇油。")

        ss_ba_hua = {
            "正官": f"🗣️ 你天生有「守规矩」的基因，适合在规则清晰的环境中发光，但别让规矩变成枷锁。",
            "七杀": f"🗣️ 你骨子里有股「不服输」的劲儿，越是有压力越来劲，但别忘了温柔也是一种力量。",
            "正印": f"🗣️ 学习是你最顺滑的成长路径，书卷气是你的魅力来源，但别只读书不读人。",
            "偏印": f"🗣️ 你的思维和别人不太一样，这是天赋也是壁垒——学会把深邃的思考转化为通俗的表达。",
            "正财": f"🗣️ 你对钱有天然的敏感度，稳健是你的财富密码，但适当冒险也是人生体验的一部分。",
            "偏财": f"🗣️ 你天生有「吸财」的体质，赚钱对你来说不太难，难的是把钱留住。",
            "比肩": f"🗣️ 你独立、不服管，一个人也能撑起一片天，但别忘了路是人走出来的、更是与人同行走出来的。",
            "劫财": f"🗣️ 你重情重义、朋友遍天下，但江湖义气需要配上清醒的判断力才不会被辜负。",
            "食神": f"🗣️ 你有才华又会享受生活，是天生的乐天派，但小心「安逸」偷走你的进取心。",
            "伤官": f"🗣️ 你聪明又有锋芒，是天生的创新者，但别忘了最锐利的刀也需要最稳的手来握。",
        }
        lines.append(ss_ba_hua.get(ss, f"🗣️ 白话解读：{ss}的能量在你身上以独特的方式展现。"))
        lines.append("")

    lines.append("【金鉴真人·§6·十神定层次】十神是性格的染色层，天干十神决定外显的「面子」，藏干十神影响内在的「里子」。吉神多者温厚包容、好相处但可能缺乏棱角；凶神多者锋芒锐利、有冲劲但需学会收敛；平神居中调和，起到平衡全局的作用。")
    lines.append("")

    # ── 十神组合互动（新增） ──
    lines.append("**十神组合互动分析：**")
    lines.append("")
    # 天干十神列表（非日主）
    gan_ss_list = []
    for pos_key in ["nian", "yue", "shi"]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss and ss != "日主":
            gan_ss_list.append(ss)

    combo_found = False
    if "正官" in gan_ss_list and "正印" in gan_ss_list:
        lines.append("- 🔄 官印相生：正官与正印同时出现，官得印护则贵气更显，适合体制内发展。")
        combo_found = True
    if "七杀" in gan_ss_list and "食神" in gan_ss_list:
        lines.append("- 🔄 食神制杀：食神制七杀，化权为贵，杀有制则不为凶反为威权。")
        combo_found = True
    if "七杀" in gan_ss_list and "偏印" in gan_ss_list:
        lines.append("- 🔄 杀印相生：七杀有偏印化之，文武双全，宜军警或管理类职位。")
        combo_found = True
    if "伤官" in gan_ss_list and "正印" in gan_ss_list:
        lines.append("- 🔄 伤官配印：伤官配印则才华有根，不流于浮夸，适合学术创作。")
        combo_found = True
    if "食神" in gan_ss_list and "偏财" in gan_ss_list:
        lines.append("- 🔄 食神生财：食神生偏财，才华转化为财富，是典型的商业天赋组合。")
        combo_found = True
    if "比肩" in gan_ss_list and "劫财" in gan_ss_list:
        lines.append("- ⚠️ 比劫并见：比劫同现，竞争意识强，适合需要竞争的环境但需注意人际关系。")
        combo_found = True
    if "劫财" in gan_ss_list and "偏财" in gan_ss_list:
        lines.append("- ⚠️ 劫财见财：劫财见偏财，财来财去之象，需要加强理财和守财意识。")
        combo_found = True

    if not combo_found:
        # 基于top3的组合通用分析
        if len(top3_ss) >= 2:
            # 分析top3之间的互动
            ss_pairs = [(top3_ss[0], top3_ss[1])]
            if len(top3_ss) >= 3:
                ss_pairs.append((top3_ss[0], top3_ss[2]))
            for ss_a, ss_b in ss_pairs:
                if ss_a in gj_four_devil and ss_b in gj_four_god:
                    lines.append(f"- 🔄 「{ss_a}」与「{ss_b}」形成制化组合——凶神有吉神制之，能量从破坏性转化为建设性。")
                elif ss_a in gj_four_god and ss_b in gj_four_devil:
                    lines.append(f"- 🔄 「{ss_a}」与「{ss_b}」形成制化组合——吉神为凶神提供方向引导，避免能量失控。")
                elif ss_a in gj_four_god and ss_b in gj_four_god:
                    lines.append(f"- 🌸 「{ss_a}」与「{ss_b}」双吉神组合——性格温和、人缘好，但需注意不要过于安逸。")
                elif ss_a in gj_four_devil and ss_b in gj_four_devil:
                    lines.append(f"- ⚡ 「{ss_a}」与「{ss_b}」双凶神组合——能量充沛、冲劲十足，但需学会收敛和制化。")
                else:
                    lines.append(f"- 💎 「{ss_a}」与「{ss_b}」性格互补——刚柔并济，能根据不同场景切换状态。")

    lines.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 特质四：身强弱修正
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.append("### 特质四：身强弱修正")
    lines.append("")

    if sq_level == "身强":
        lines.append(f"身强（{sq_score}分）——你的能量池水位较高，做事有底气、敢于担当，有天然的主动性和控制欲。")
        lines.append(f"身强之人有如满弓之箭，蓄势充足但容易用力过猛。一生运势曲线：早年锋芒崭露，中年事业持续上升，晚年需学会示弱与放手。")
        lines.append(f"在人际中，身强者容易不自觉地主导对话和决策，需要注意给他人留出空间。")
        lines.append(f"身强者宜做先锋和开拓者，忌事必躬亲——学会把执行层面的工作交给他人，自己专注战略和方向。")
        lines.append("🗣️ 一句话概括：你天生自带「发动机」，不需要外力驱动就能跑起来，但记得给自己装个「刹车」。")
    elif sq_level == "身弱":
        lines.append(f"身弱（{sq_score}分）——你的能量池水位偏低，更善于借力和合作，有敏锐的观察力和风险意识。")
        lines.append(f"身弱之人有如太极推手，以柔克刚是天赋技能。一生运势曲线：早年宜积累与学习，中年借大运和贵人发力腾飞，晚年可享清福。")
        lines.append(f"在人际中，身弱者善于倾听和观察，容易获得他人的信任和支持，贵人运是最大财富。")
        lines.append(f"身弱者宜做操盘手而非拼体力——借力打力、四两拨千斤是你的核心竞争力，不必硬碰硬。")
        lines.append("🗣️ 一句话概括：你不是能量不够，而是懂得「借力」才是最高级的智慧——刘邦的身弱，成就了帝王之业。")
    else:
        lines.append(f"中和（{sq_score}分）——你的能量池水位适中，刚柔并济、进退有度，适应性是你最大的优势。")
        lines.append(f"中和之人有如流水行云，随方就圆是天赋。一生运势曲线：运势平稳不走极端，能在各个人生阶段找到恰如其分的位置。")
        lines.append(f"在人际中，中和者是最受欢迎的合作伙伴——不过于强势也不过于弱势，恰到好处。")
        lines.append(f"但需警惕「平衡陷阱」——样样通不如一样精，选一个赛道深扎下去，做出差异化和护城河。")
        lines.append("🗣️ 一句话概括：你是天生的「平衡大师」，进可攻退可守，但要小心平衡到最后变成没有立场。")

    lines.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 特质五：综合画像
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.append("### 特质五：综合画像")
    lines.append("")

    top_ss_str = "、".join(top3_ss[:2])
    xi_str = "、".join(xi_list) if xi_list else "五行平衡"
    ji_str = "、".join(ji_list) if ji_list else "需注意的五行"

    lines.append(f"综观全局，你的性格是一幅由五重色彩交织的画卷：")
    lines.append("")
    lines.append(f"**底色**——{ri_wx}性{ri_gan}日主，{yy_gangrou}，赋予你最基本的行事风格和能量基调。")
    lines.append(f"**主调**——{ge_ju_str}格局，决定了你在人生关键节点的选择逻辑和价值取向。")
    lines.append(f"**层次**——十神「{top_ss_str}」等特质为性格注入丰富细节，在不同场景下展现出不同的侧面。")
    lines.append(f"**力道**——{sq_level}（{sq_score}分），控制着你能量的输出方式是「直给」还是「迂回」。")
    lines.append(f"**方向**——喜用神为{xi_str}，这是你成长的能量密码；忌神{ji_str}则是你需要谨慎对待的领域。")
    lines.append("")

    lines.append("**五重人格的互动关系：**")
    lines.append("")
    lines.append(f"- 你的{ri_wx}性底色决定了思维方式，{ge_ju_str}格局决定了价值取向——二者共同构成了你的核心人格。")
    if len(top3_ss) >= 2:
        lines.append(f"- 十神「{top3_ss[0]}」和「{top3_ss[1]}」则是在这个核心基础上添加的色彩，决定了你在社交、工作、情感中的具体表现。")
    lines.append(f"- {sq_level}的力道控制着以上所有特质的「输出音量」——{'音量大、气势足，但需要学会调节音量' if sq_level=='身强' else '音量小、柔和细腻，但需要学会在关键时刻调大音量' if sq_level=='身弱' else '音量适中、收放自如，是别人最舒服的相处对象'}。")
    lines.append(f"- 喜用神{xi_str}是你的人生「加速器」，在相关年份和场景中顺势而为，可以达到事半功倍的效果。")
    lines.append("")

    # 喜用神详细解读（直接显示五行名，跳过有bug的_get_xi_yong_wx）
    if xi_list:
        lines.append("**喜用神深层影响：**")
        lines.append("")
        xi_detail_map = {
            "木": "「木」对应的十神类型为「比劫」——你需要团队和伙伴的支持，合作和社交是你最重要的动力来源。木主生机，多接触自然和户外活动有助于提升能量。",
            "火": "「火」对应的十神类型为「食伤」——你需要适度展示才华和创意来平衡命局，在表达自我和创造价值时获得最大满足感。火主热情，保持对生活的热爱是最佳能量补充。",
            "土": "「土」对应的十神类型为「财」——你需要在求财和经营中成长，通过创造价值和财富积累来激发潜能。土主稳定，建立扎实的基础才能走得更远。",
            "金": "「金」对应的十神类型为「官杀」——你需要在有规则和压力的环境中发展，承担责任和接受挑战是你成长的催化剂。金主纪律，自律是你最大的武器。",
            "水": "「水」对应的十神类型为「印」——你需要通过学习和积累来增强底气，知识和文化修养是你最坚实的支撑。水主智慧，终身学习是你的人生主题。",
        }
        for xi in xi_list[:2]:
            lines.append(f"- {xi_detail_map.get(xi, f'「{xi}」是你命局的重要平衡点，善用其能量可事半功倍。')}")
        if ji_list:
            ji_detail = {
                "木": "「木」为忌神时，注意不要过于依赖他人，培养独立决策能力。",
                "火": "「火」为忌神时，注意不要过于急躁外放，学会沉淀和内敛。",
                "土": "「土」为忌神时，注意不要过于保守固执，适度打破舒适区。",
                "金": "「金」为忌神时，注意不要过于刚硬对抗，学会以柔克刚。",
                "水": "「水」为忌神时，注意不要过度敏感思虑，保持简单直接。",
            }
            for ji in ji_list[:2]:
                lines.append(f"  ⚠️ {ji_detail.get(ji, f'「{ji}」为忌神，相关年份需谨慎行事。')}")
        lines.append("")

    lines.append("**成长建议：**")
    lines.append("")
    growth_items = []

    if sq_level == "身强":
        growth_items.append("🛡️ 身强者最大的敌人是自己——学会倾听、示弱、放权，刚柔并济才是真正的强大。")
    elif sq_level == "身弱":
        growth_items.append("🌱 身弱者最大的靠山是贵人——但贵人不会永远在身边，趁势建立自己的专业壁垒才是根本。")
    else:
        growth_items.append("⚖️ 中和者最大的优势是适应力——但优势也可能是陷阱，选一个赛道深扎下去，做出差异化。")

    if ge_ju_str in gj_four_devil:
        growth_items.append(f"🔥 你的{ge_ju_str}格能量激烈，需要有制化手段——找到可以「制」你的十神（如食神制杀、印化杀），把破坏力转化为创造力。")
    elif ge_ju_str in gj_four_god:
        growth_items.append(f"🌸 你的{ge_ju_str}格温和正能量，但吉神需要护卫——注意大运流年中的冲克，保护好你的根基能量。")
    else:
        growth_items.append(f"💎 你的{ge_ju_str}格中性平和，中庸即定力——在浮躁的大环境中保持清醒节奏，是最难得的竞争力。")

    for ss in top3_ss[:2]:
        if ss in ["七杀", "伤官", "劫财"]:
            growth_items.append(f"💡 「{ss}」能量旺时，把对抗性转化为建设性——在竞争中保持风度，在批判中给出方案。")
        elif ss in ["正印", "偏印"]:
            growth_items.append(f"📖 「{ss}」能量旺时，多读万卷书也要行万里路——把理论知识转化为实操能力，别做纸上谈兵的人。")
        elif ss in ["正财", "偏财"]:
            growth_items.append(f"💰 「{ss}」能量旺时，赚钱不忘修行——财富是工具，不是目的，用它来撬动更大的价值。")
        elif ss in ["食神"]:
            growth_items.append(f"🎨 「{ss}」能量旺时，让才华被看见——不要羞于展示，你的创造力是最大的财富。")
        elif ss in ["比肩"]:
            growth_items.append(f"🤝 「{ss}」能量旺时，独行快、众行远——找志同道合的伙伴一起走，比单打独斗走得更远。")

    # 添加喜用神相关建议
    if xi_list:
        for xi in xi_list[:1]:
            xi_growth = {
                "木": "🌳 喜用「木」——多与自然接触，培养包容心，做长远规划，不要急功近利。",
                "火": "🔥 喜用「火」——多表达、多展示、多社交，你的能量需要在流动中释放。",
                "土": "🏔️ 喜用「土」——建立稳固的根基和系统，扎实每一步，厚积薄发。",
                "金": "⚔️ 喜用「金」——培养自律和规则意识，在规范中找到自由，在纪律中爆发创造力。",
                "水": "🌊 喜用「水」——持续学习和吸收新知，保持思维的流动性和开放性。",
            }
            growth_items.append(xi_growth.get(xi, ""))

    # 过滤空项
    growth_items = [item for item in growth_items if item]

    for item in growth_items[:6]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("【金鉴真人·§6·五重人格融合】五重人格不是独立的五个盒子，而是像五根琴弦——每一根都有自己的音高，但当它们同时被拨动时，奏响的才是你完整的生命乐章。了解这些特质，不是为了给自己贴标签，而是为了在不同的人生阶段善用它们。")
    lines.append("")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🗣️ 白话总结
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.append("---")
    lines.append("")

    wx_metaphor = {
        "金": "一把经过打磨的利器",
        "木": "一棵扎根沃土的大树",
        "水": "一条奔流不息的河流",
        "火": "一团温暖明亮的光芒",
        "土": "一片承载万物的大地",
    }
    metaphor = wx_metaphor.get(ri_wx, "一个独特的存在")
    sq_power_str = "身强" if sq_level == "身强" else ("借力蓄势" if sq_level == "身弱" else "恰到好处")

    lines.append(f"🗣️ **一句话总结你的性格：**")
    lines.append("")
    lines.append(f"> 你是「{metaphor}」，以{ge_ju_str}格的姿态行走于世，")
    lines.append(f"> 身上带着「{top_ss_str}」的鲜明烙印，力量收放{sq_power_str}，")
    lines.append(f"> 命中喜用「{xi_str}」来为你的人生注入能量。")
    lines.append(f"> 五重人格交织，独一无二的你。")
    lines.append("")
    lines.append(f"> 了解命格不是为了认命，而是为了更聪明地活。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines