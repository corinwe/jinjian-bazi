"""
金鉴真人·叙述引擎 v1.0 — 将结构化数据转化为命理师口吻的连贯分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
每个函数接收该章节的结构化数据，输出200-500字的连贯段落
"""

# ═══════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════


def _s(score):
    """评分转等级描述"""
    if score >= 8:
        return "极佳"
    if score >= 6:
        return "良好"
    if score >= 4:
        return "中等"
    return "偏弱"


def _c(v):
    """清理Python语法字符"""
    return str(v).replace("'", "").replace('"', "").replace("[", "").replace("]", "")


def _l(items, conj="、"):
    """列表转字符串"""
    return conj.join(str(x) for x in items if x)


# ═══════════════════════════════════════════
# 章节叙述器
# ═══════════════════════════════════════════


def narrative_overview(
    bazi,
    ri_zhu,
    ri_zhu_wx,
    gender,
    shen_label,
    shen_score,
    ge_ju_detail,
    xi_yong,
    ji_shen,
    cai_total,
    wealth_level,
    tiao_hou,
):
    """§1 一页总览 — 开篇总述"""
    gender_cn = "男性" if gender == "男" else "女性"

    # 日主性格
    wx_nature = {
        "甲": "甲木为阳木，如参天大树，正直担当，有领导风范。",
        "乙": "乙木为阴木，如藤萝花草，柔韧灵活，善于适应环境。",
        "丙": "丙火为阳火，如太阳之火，热情开朗，光明磊落。",
        "丁": "丁火为阴火，如灯烛之火，温文尔雅，内心细腻。",
        "戊": "戊土为阳土，如泰山之土，稳重诚信，厚德载物。",
        "己": "己土为阴土，如田园之土，包容柔和，善于协调。",
        "庚": "庚金为阳金，如刀剑之金，刚毅果断，有进取精神。",
        "辛": "辛金为阴金，如珠玉之金，精致优雅，追求完美。",
        "壬": "壬水为阳水，如江河之水，智慧灵动，胸怀宽广。",
        "癸": "癸水为阴水，如雨露之水，含蓄深沉，心思缜密。",
    }

    parts = []
    parts.append(f"八字【{bazi}】，日主{ri_zhu}{ri_zhu_wx}，{gender_cn}。")
    parts.append(wx_nature.get(ri_zhu, f"日主{ri_zhu}{ri_zhu_wx}，特质鲜明。"))

    # 身强弱
    if shen_label == "从弱":
        parts.append(f"命局为从弱格（{shen_score}分），格局非常特殊，全局能量高度集中，弃命相从，非寻常之格。")
    elif shen_label == "身强" and shen_score >= 70:
        parts.append(
            f"命局身强偏旺（{shen_score}分），体质强健，精力充沛，能扛得住常人难以承受的压力，有担当大事的底子。"
        )
    elif shen_label == "身强":
        parts.append(f"命局身强（{shen_score}分），根基扎实，有一定的抗压能力和事业基础，适合在压力中成长。")
    elif shen_label == "身弱":
        parts.append(f"命局身弱（{shen_score}分），能量内敛，不宜单打独斗，宜借平台和贵人之力成就事业。")
    else:
        parts.append(f"命局中和（{shen_score}分），五行相对平衡，适应力强，喜忌随大运灵活变化。")

    # 格局
    geju_desc = {
        "正官格": "正官格者，为人正直，有管理才能，宜走体制内路线。",
        "七杀格": "七杀格者，魄力非凡，敢于决断，适合挑战性工作。",
        "正财格": "正财格者，求财踏实，步步为营，宜稳定型职业。",
        "偏财格": "偏财格者，财路宽广，善于投资，有经商天赋。",
        "正印格": "正印格者，学识渊博，有贵人运，宜文职教育。",
        "偏印格": "偏印格者，思维独特，有冷门专长，适合技术研发。",
        "食神格": "食神格者，心态好福气厚，适合创意餐饮等行业。",
        "伤官格": "伤官格者，才华横溢，灵气逼人，宜发挥创造力。",
    }
    if ge_ju_detail:
        parts.append(f"格局为{ge_ju_detail}。{geju_desc.get(ge_ju_detail, '格局结构清晰，为命局主框架。')}")

    # 喜用忌神
    xi_str = _l(xi_yong)
    ji_str = _l(ji_shen)
    if xi_str:
        parts.append(f"喜用神为{xi_str}，此乃命局平衡之关键，补之则运势顺遂。忌神为{ji_str}，宜避让。")
    if tiao_hou:
        th = _c(tiao_hou)
        parts.append(f"调候用神为{th}。调候为先，寒暖燥湿之偏影响命局整体质量，补足调候则顺遂。")

    # 财星
    if cai_total:
        parts.append(f"财星{int(cai_total)}分，属{wealth_level}层次。身财配置决定求财方式，财星旺衰影响财富格局。")

    return "".join(parts)


def narrative_ge_ju(ge_ju_main, ge_ju_detail, bazi, ri_zhu, shen_label, shen_score):
    """§2 格局分析"""
    gj = ge_ju_detail or ge_ju_main
    if not gj:
        return "格局分析数据不足。"

    text = f"命局核心格局为{gj}。格局是命局的灵魂和纲领，决定了人生的主攻方向和成就上限。"

    if "杀" in gj:
        text += "七杀格局，代表魄力与决断，敢于冲锋陷阵，能在逆境中崛起。七杀有制则为权柄，无制则为压力。命局中有印星化杀或食神制杀，则能将杀之压力转化为权柄和成就。"
    if "印" in gj:
        text += "印星格局，代表学识、贵人和保护。正印为常规学习能力，偏印为特殊才能。印星得力者多有学历文凭，人生中有贵人提携。"
    if "财" in gj:
        text += "财星格局，代表求财能力和商业头脑。正财为稳定收入，偏财为意外之财和投资能力。"
    if "官" in gj:
        text += "官星格局，代表管理能力和社会地位。正官为正式职位和名誉，适合体制内发展。"
    if "食" in gj or "伤" in gj:
        text += "食伤格局，代表才华、创意和表达能力。食神为福气享受，伤官为才华突破。食伤生财者有靠才华赚钱的天赋。"

    return text


def narrative_shen_qiang_ruo(shen_label, shen_score, shen_detail):
    """§3 身强弱判定"""
    if shen_label == "从弱":
        text = (
            f"命局为从弱格（{shen_score}分）。"
            + '这是一种特殊的格局，全局能量高度倾斜。所谓"从"就是放弃自我、顺从大势的性格。这类人往往灵活变通，不固执己见，能够在复杂的局面中找到生存之道。但逆运时容易迷失自我，需要保持内心定力。'
        )
    elif shen_label == "身强" and shen_score >= 70:
        text = (
            f"命局身强偏旺（{shen_score}分）。"
            + "体质强健，精力过人，能扛得住常人难以承受的压力。性格独立自主，不喜欢受人管束。但过刚易折，身强无制则容易刚愎自用，需要财官食伤来平衡消耗。身强者适合从事竞争性强的工作，但也需要注意控制脾气和冲动。"
        )
    elif shen_label == "身强":
        text = (
            f"命局身强（{shen_score}分）。"
            + "根基比较扎实，有一定的抗压能力和事业基础。性格偏向自信主动，做事有自己的主见。但身强不代表万事大吉，需要看喜用是否得力。如果喜用得力，则能充分发挥自身优势；如果喜用被制，则身强反而是一种负担。"
        )
    elif shen_label == "身弱":
        text = (
            f"命局身弱（{shen_score}分）。"
            + "能量内敛，不适合单打独斗。这类人往往心思细腻敏感，善于借力。看似柔弱，实则韧性极强。身弱者的生存策略是找对平台、跟对人，在大机构大平台中发挥自己的价值，而不是自己出头创业。一旦找到合适的喜用大运，也能成就一番事业。"
        )
    else:
        text = (
            f"命局中和（{shen_score}分）。"
            + "五行相对平衡，适应力强，性格中庸。中和之命虽然没有极端的长处，但也没有明显的短板，稳定性好，适合大多数职业。但中和之命更看大运的引动，好运来时也能一飞冲天。"
        )

    # 添加计分细节
    if shen_detail and hasattr(shen_detail, "_asdict"):
        d = shen_detail._asdict()
        parts = []
        for k, v in d.items():
            if isinstance(v, (int, float)) and v > 0:
                parts.append(f"{k}={v}分")
        if parts:
            text += "计分明细：" + "，".join(parts) + "。"
    elif isinstance(shen_detail, dict):
        parts = []
        for k, v in shen_detail.items():
            if isinstance(v, (int, float)) and v > 0:
                parts.append(f"{str(k).replace('_', '')}={v}分")
        if parts:
            text += "计分明细：" + "，".join(parts) + "。"

    return text


def narrative_xi_yong(xi_yong, ji_shen, tiao_hou):
    """§4 喜用神与忌神"""
    xi_str = _l(xi_yong)
    ji_str = _l(ji_shen)
    th = _c(tiao_hou) if tiao_hou else ""

    parts = []
    if xi_str:
        parts.append(
            f"喜用神为{xi_str}。喜用神是命局最需要的五行能量，代表贵人、机遇和顺境。在职业选择上，应优先选择喜用神对应的行业；在居住方位上，宜朝向喜用神的方位；在颜色搭配上，多使用喜用神对应的颜色。"
        )
    if ji_str:
        parts.append(
            f"忌神为{ji_str}。忌神是命局中过旺的五行，代表阻力、消耗和逆境。在重大决策时应尽量避开忌神所对应的领域和方向。忌神大运期间宜守不宜攻。"
        )
    if th:
        parts.append(
            f"调候用神为{th}。调候为先——寒暖燥湿的平衡对命局质量影响很大。补足调候则整体运势更为顺遂，事半功倍。"
        )

    if not xi_str and not ji_str:
        return "命局中和，喜忌随大运灵活变化，需要结合具体大运来定。"

    return "".join(parts)


def narrative_zai_huo(misfortune_full, shen_sha_chong, shen_sha_xing, shen_sha_hai, remission_advice):
    """§5 灾祸预警与化解"""
    risk = misfortune_full.get("risk_level", "低") if isinstance(misfortune_full, dict) else "低"

    text = f"风险评级为{risk}。"

    if shen_sha_chong:
        text += f"地支有{_l(shen_sha_chong)}相冲。冲主动荡、变动，逢冲之年易有搬家、换工作、关系变化之事。若无喜用神解救，则冲为凶。"
    if shen_sha_xing:
        text += f"地支有{_l(shen_sha_xing)}相刑。刑主是非、摩擦，逢刑之年人际易紧张，需注意口舌官司。"
    if shen_sha_hai:
        text += f"地支有{_l(shen_sha_hai)}相害。害主暗算、损耗，逢害之年需防小人，合同签约需谨慎。"

    if not shen_sha_chong and not shen_sha_xing and not shen_sha_hai:
        text += "命局地支无明显刑冲害，整体平和，无重大灾祸信号。"

    if remission_advice:
        adv = remission_advice.get("advice", "") if isinstance(remission_advice, dict) else str(remission_advice)
        if adv:
            text += f"化解建议：{_c(adv)}。"

    return text


def narrative_character(ri_zhu, ri_zhu_wx, shen_label, shen_score, ge_ju_main, xi_yong, ji_shen, character_data):
    """§6 性格解析"""
    parts = []

    # 日主天性
    ri_zhu_desc = {
        "甲": "甲木日主，性格正直，有担当，做事光明磊落，不喜暗箱操作。如同参天大树，为他人遮风挡雨。",
        "乙": "乙木日主，性格柔韧灵活，能屈能伸，善于适应各种环境。如同藤萝，看似柔弱实则生命力极强。",
        "丙": "丙火日主，性格热情开朗，慷慨大方，乐于助人。如同太阳，照亮他人但也容易消耗自己。",
        "丁": "丁火日主，性格温文尔雅，心思细腻，情感丰富。如同灯烛之火，温暖而含蓄。",
        "戊": "戊土日主，性格稳重诚信，一诺千金，做事踏实可靠。如同泰山之土，厚重而值得信赖。",
        "己": "己土日主，性格包容柔和，善于协调，是好的倾听者和调解者。如同田园之土，滋养万物。",
        "庚": "庚金日主，性格刚毅果断，讲义气重承诺，有强烈的进取心。如同刀剑之金，锋芒毕露。",
        "辛": "辛金日主，性格精致优雅，追求完美，有审美天赋。如同珠宝之金，需要精心打磨才发光。",
        "壬": "壬水日主，性格智慧灵动，胸怀宽广，善于变通。如同江河之水，奔流不息，永不停歇。",
        "癸": "癸水日主，性格含蓄深沉，心思缜密，有极强的洞察力。如同雨露之水，润物细无声。",
    }

    parts.append(ri_zhu_desc.get(ri_zhu, f"{ri_zhu}{ri_zhu_wx}日主，特质鲜明。"))

    # 性格特质 - 基于身强弱和格局
    if shen_label == "身强" and shen_score >= 60:
        parts.append(
            "身强者性格偏向自信主动，有不达目的不罢休的韧劲。做事有主见，不轻易受人影响。但需注意不要过于固执己见，适当听取他人意见会更有利于发展。"
        )
    elif shen_label == "身弱":
        parts.append(
            "身弱者性格偏向内敛谨慎，心思细腻，善于观察和思考。做事不冲动，懂得借力。看似柔弱，实则内心坚韧，能在关键时刻爆发出惊人的能量。"
        )

    # 格局影响
    if ge_ju_main:
        gj_style = {
            "正官格": "正官格的人注重规则和秩序，责任心强，做事严谨。",
            "七杀格": "七杀格的人魄力非凡，敢作敢当，有领袖气质和冒险精神。",
            "正印格": "正印格的人慈悲为怀，有书卷气息，学习能力强。",
            "偏印格": "偏印格的人思维独特，不走寻常路，有冷门专长和艺术天赋。",
            "正财格": "正财格的人务实稳重，精打细算，适合守成。",
            "偏财格": "偏财格的人豪爽大方，善交际，有经商头脑。",
            "食神格": "食神格的人心态好，乐观豁达，有福气，懂得享受生活。",
            "伤官格": "伤官格的人才华横溢，聪明伶俐，但清高孤傲，不喜受约束。",
        }
        parts.append(gj_style.get(ge_ju_main, ""))

    # 关键特质
    key_traits = character_data.get("key_traits", []) if isinstance(character_data, dict) else []
    if key_traits:
        parts.append(f"综合来看，性格关键特质为{_l(key_traits)}。")

    return "".join(parts)


def narrative_appearance(ri_zhu, ge_ju_main, shen_label):
    """§7 身材外貌"""
    # 基于日主五行
    app = {
        "甲": "甲木日主身材高挑修长，五官端正、额头饱满，肤色偏白偏黄，气质正直大气。",
        "乙": "乙木日主身材柔美匀称，面容柔和、眉眼清秀，肤色偏白，气质温婉文艺。",
        "丙": "丙火日主偏丰满、中等身高，面色红润、眼睛有神，肤色偏红润，气质热情开朗。",
        "丁": "丁火日主身材适中不胖不瘦，面容精致、眼神温柔，肤色偏白偏红润，气质温润细腻。",
        "戊": "戊土日主敦厚结实、骨架偏大，五官敦厚、鼻头圆，肤色偏黄，气质稳重可靠。",
        "己": "己土日主肉感适中、体态柔美，面容柔和、圆形鹅蛋脸，肤色偏黄，气质内敛含蓄。",
        "庚": "庚金日主骨架硬朗、肩宽，五官立体、下颌线分明，肤色偏白，气质刚毅果断。",
        "辛": "辛金日主骨感匀称、身材纤细，面容精致、鼻梁秀挺，皮肤白皙，气质清秀高雅。",
        "壬": "壬水日主丰腴饱满、体态圆润，大眼睛、面部饱满，肤色偏白偏黑，气质智慧灵动。",
        "癸": "癸水日主柔美纤细、腰身明显，面容柔美、眼神含蓄，肤色偏白偏暗，气质含蓄聪慧。",
    }
    text = app.get(ri_zhu, "五官端正，体态适中。")

    # 格局修正气质
    style_map = {
        "正官格": "气质端庄正气，给人可靠信赖之感。",
        "七杀格": "气质霸气锐利，眼神有杀气，气场强大。",
        "正印格": "气质温润儒雅，有书卷气息，慈眉善目。",
        "偏印格": "气质清冷孤傲，有独特的气质和神秘感。",
        "正财格": "气质朴实稳重，给人务实可靠的印象。",
        "偏财格": "气质豪爽大方，有江湖气，善于交际。",
        "食神格": "气质福态圆润，有亲和力，令人愉悦。",
        "伤官格": "气质灵秀叛逆，有灵气，与众不同。",
    }
    if ge_ju_main:
        text += style_map.get(ge_ju_main, "")

    return text


def narrative_wealth(cai_total, wealth_level, cai_ku, xi_yong, ji_shen, shen_label):
    """§8 财富格局"""
    level_desc = {
        "巨富": "亿万级别，属于顶级财富阶层，可掌控大量资源。",
        "大富": "数千万至亿级，属于富裕阶层，财务自由度很高。",
        "中富": "百万至千万级，属于中产以上，有较强的财务安全感。",
        "小富": "小康以上，生活富足，但还未达到完全财务自由。",
        "一般": "普通水平，求财需要付出较多努力。",
    }

    text = f"财星总评{int(cai_total)}分，属{wealth_level}层次。{level_desc.get(wealth_level, '')}"

    if cai_ku and cai_ku.get("has"):
        text += f"命带财库（{_l(cai_ku.get('zhi', []))}），有储存和积累财富的能力，财不易散。财库代表蓄财能力，库旺者能存钱、能守财，不至于赚多少花多少。"

    # 身强身弱对财的影响
    if shen_label == "身强":
        text += "身强者能扛财，财星为喜用时求财顺利，有赚钱的能力和魄力。但身强财弱则容易大手大脚，需注意理财规划。"
    else:
        text += "身弱者财星为压力，求财辛苦，宜借平台之力。不建议过早创业或独立经商，先在大机构积累实力。"

    # 喜用关系
    xi_str = _l(xi_yong)
    ji_str = _l(ji_shen)
    if xi_str:
        text += f"喜用与财富方向：选择{xi_str}对应的行业求财，事半功倍。"
    if ji_str:
        text += f"避开{ji_str}对应的领域。"

    return text


def narrative_career(career_data, ge_ju_main, ge_ju_detail, shen_label, shen_score, xi_yong):
    """§10 事业发展"""
    direction = career_data.get("career_direction", "")
    grade = career_data.get("career_grade", "")
    industry = career_data.get("recommended_industries", "")
    best = career_data.get("best_path", "")
    ent = career_data.get("entrepreneurship", "")

    parts = []
    if direction:
        parts.append(f"事业方向宜走{direction}路线。")
    if grade:
        grade_clean = _c(grade)
        parts.append(f"事业评估为{grade_clean}。")
    if industry:
        parts.append(f"五行定行业，适宜从事{industry}等领域，利用五行能量助益事业发展。")

    # 格局建议
    if "杀" in (ge_ju_detail or ""):
        parts.append(
            "七杀格局建议选择有压力的工作环境，军警、管理、创业等领域能发挥杀格优势。杀有制则贵，无制则压力大。"
        )
    if "印" in (ge_ju_detail or ""):
        parts.append("印星格局适合文职、教育、研究等稳定性工作，也适合在国企、大平台发展。")
    if "财" in (ge_ju_detail or ""):
        parts.append("财星格局适合经商、金融、财务等领域，正财宜守，偏财宜攻。")

    # 创业建议
    if ent:
        ent_clean = _c(ent)
        parts.append(f"{ent_clean}。")

    # 最佳路径
    if best:
        parts.append(f"{_c(best)}。")

    return "".join(parts)


def narrative_education(education_result, shen_label):
    """§11 学业学历"""
    level = education_result.get("display", education_result.get("school_level", ""))
    ypc = education_result.get("year_pillar_check", {})

    parts = []
    if level:
        clean = level.replace("🎓 ", "").replace("🥈 ", "").replace("🥇 ", "")
        parts.append(f"学业层次为{clean}。")

    yin_detail = ypc.get("detail", "") if isinstance(ypc, dict) else ""
    if yin_detail:
        clean = yin_detail.replace("✅", "")
        parts.append(f"年柱印星分析：{clean}。年柱有印代表有学业基因，祖上有读书人，家庭重视教育。")

    # 文昌
    wc = education_result.get("wen_chang", education_result.get("wen_chang_ming_li", {}))
    if isinstance(wc, dict):
        if wc.get("has") or wc.get("zhi"):
            parts.append(f"文昌星在{wc.get('zhi', '局中')}，文昌到位则学业顺利，考试运佳。文昌不显则需要后天加倍努力。")

    # 身强弱的影响
    if shen_label == "身弱" and not level:
        parts.append("身弱者的学业之路可能比常人更辛苦，需要付出更多努力。但身弱也有优势——心思细腻，适合钻研学问。")

    return "".join(parts) or "暂无详细的学历分析数据。"


def narrative_marriage(marriage_result, ri_zhu, gender):
    """§12 婚姻感情"""
    quality = marriage_result.get("quality", "")
    score = marriage_result.get("quality_score", "")
    window = marriage_result.get("best_window_age", "")
    spouse = marriage_result.get("spouse_trait", "")

    parts = []
    if quality:
        parts.append(f"婚姻质量为{quality}。")
    if score:
        parts.append(f"综合评分{score}/10分。")
    if window:
        w = str(window).replace("暂无明显窗口岁", "暂无明显婚恋窗口")
        parts.append(f"最佳婚恋窗口在{w}。")

    # 夫妻宫分析
    ri_zhi = marriage_result.get("ri_zhi_analysis", {})
    if isinstance(ri_zhi, dict) and ri_zhi.get("master"):
        parts.append(f"夫妻宫坐{ri_zhi['master']}，{ri_zhi.get('quality_note', '配偶个性鲜明')}。")
        if ri_zhi.get("appearance"):
            parts.append(f"配偶相貌{ri_zhi['appearance']}。")

    # 配偶特征
    traits = marriage_result.get("spouse_traits", [])
    if traits:
        parts.append(f"配偶特征为{_l(traits)}。")

    if spouse:
        parts.append(f"{_c(spouse)}。")

    return "".join(parts) or "暂无详细的婚姻分析数据。"


def narrative_children(children_data, ri_zhu):
    """§13 子女运势"""
    count = children_data.get("child_count_estimate", "")
    ach = children_data.get("child_achievement", "")
    potential = children_data.get("sheng_yu_potential", "")

    parts = []
    if count:
        cnt = _c(count)
        parts.append(f"子女数量约{cnt}个。")

    # 子女成就
    ach_text = ""
    if isinstance(ach, str) and ach.startswith("{"):
        import re

        m = re.search(r"子女方向['\\\":：]*([^'\\\"}]+)", ach)
        if m:
            ach_text = m.group(1)
    elif isinstance(ach, dict):
        ach_text = str(ach.get("子女方向", ""))
    else:
        ach_text = str(ach)

    if ach_text:
        parts.append(f"子女成就趋势：{ach_text}。时柱为子女宫，时柱喜用神得力则子女有出息。")

    # 生育力
    if potential:
        pot = _c(potential)
        parts.append(f"生育力{pot}。")

    return "".join(parts) or "暂无详细的子女分析数据。"


def narrative_health(health_data, ri_zhu, shen_label):
    """§14 健康注意"""
    constitution = health_data.get("constitution", "")
    wx_over = health_data.get("wu_xing_over_three", [])

    parts = []
    if constitution:
        parts.append(f"先天体质{constitution}。")

    # 五行过三
    for w in wx_over[:3]:
        if isinstance(w, dict) and w.get("wx") and w.get("organ"):
            parts.append(f"五行{w['wx']}过旺，对应{w['organ']}系统需注意保养。每十年需做一次相关体检。")

    if not wx_over:
        parts.append("五行能量分布均衡，无显著过载风险。")

    # 七杀攻身
    qi_sha = health_data.get("qi_sha_risks", {})
    if isinstance(qi_sha, dict) and qi_sha.get("detail") and "无显著信号" not in str(qi_sha.get("detail")):
        parts.append(f"七杀攻身提示：{_c(qi_sha['detail'][:200])}。")

    # 流年健康预警
    protect = health_data.get("protect_years", [])
    if protect:
        parts.append(f"重点防护年份：{_l(protect[:5])}年。这些年份健康方面需格外留意，建议提前体检。")

    if not parts:
        return "暂无详细的健康分析数据。"
    return "".join(parts)


def narrative_family(family_data, ri_zhu):
    """§15 六亲关系"""
    parts = []
    summary = family_data.get("summary", "") if isinstance(family_data, dict) else ""
    if summary:
        parts.append(f"{_c(summary)}。")

    eco = family_data.get("family_economy", "") if isinstance(family_data, dict) else ""
    if eco:
        parts.append(f"家庭经济状况{eco}。")

    pressure = family_data.get("family_pressure", "") if isinstance(family_data, dict) else ""
    if pressure:
        parts.append(f"{_c(pressure)}。")

    # 基于年柱的一般性分析
    if not summary:
        parts.append("年柱为祖上父母宫，年柱喜用得力则祖上根基好，父母有助力。年柱被冲克则祖业凋零，需白手起家。")

    return "".join(parts)


def narrative_events(key_events):
    """§16 流年事件"""
    all_events = []
    for etype, evts in key_events.items():
        if isinstance(evts, list):
            for e in evts:
                if isinstance(e, dict) and e.get("year") and e.get("description"):
                    all_events.append(e)

    if not all_events:
        return "当前无显著流年事件触发。运势平稳，按部就班发展即可。"

    all_events.sort(key=lambda x: x.get("year", 0))

    parts = ["未来数年关键节点如下："]
    for e in all_events[:10]:
        parts.append(f"{e['year']}年：{e['description']}")
    parts.append("以上为基于大运流年推演的关键节点，具体应事需结合现实情况判断。吉运应积极把握，凶运提前布局防范。")

    return "\n".join(parts)


# ═══════════════════════════════════════════
# §9 置业分析
# ═══════════════════════════════════════════


def narrative_property(property_data: dict) -> str:
    """§9 置业分析"""
    level = property_data.get("property_level", "")
    potential = property_data.get("property_potential", "")
    windows = property_data.get("windows", [])
    risk = property_data.get("risk", "")

    parts = []
    if potential:
        parts.append(f"置业方位原则：{potential}。")
    if level:
        # 避免level文本和描述重复
        level_str = str(level).strip()
        if "强" in level_str:
            desc = "强，有能力购置多处房产"
            parts.append(f"置业能力属{desc}。财星生官或印星护财格局下购置不动产相对轻松，可视运势窗口分批布局。")
        elif "中" in level_str:
            desc = "中等，有能力购房自住"
            parts.append(f"置业能力属{desc}。购房自住压力不大，但大规模配置不动产需要大运配合。")
        else:
            desc = "偏弱，需大运配合"
            parts.append(f"置业能力属{desc}。单靠原局财星力量稍显不足，需借助喜用大运方能完成大宗置业。")

    if windows:
        w = windows[0]
        parts.append(
            f"最佳置业窗口在{w.get('age_range', '中年')}，此运为{w.get('da_yun', '')}运，喜用到位，能量最足，宜在此阶段完成购房或换房计划。"
        )
    if risk:
        parts.append(f"注意事项：{risk}。忌神大运购置不动产容易导致资金链紧张或房产贬值，务必审慎。")

    if not parts:
        return "暂无详细的置业分析数据。"

    return "".join(parts)


# ═══════════════════════════════════════════
# §17 大运详批
# ═══════════════════════════════════════════


def narrative_da_yun_detail(dy_data: dict) -> str:
    """§17 大运详批 — 基于实际大运评分"""
    dy_list = dy_data.get("list", [])
    best_idx = dy_data.get("best_idx", -1)
    worst_idx = dy_data.get("worst_idx", -1)

    if not dy_list:
        return "暂无大运数据。"

    parts = []
    parts.append(
        f"命主共行{len(dy_list)}步大运，每步十年，起运后依次轮转。大运是天命的节奏，决定了人生不同阶段的运势走向。"
    )

    # 最佳大运
    if best_idx >= 0 and best_idx < len(dy_list):
        best = dy_list[best_idx]
        parts.append(
            f"最佳大运为{best['gan_zhi']}运（{best['start_age']}~{best['end_age']}岁），评分最高。此运喜用到位或忌神受制，是人生最顺遂的十年，事业、财富、人脉皆有明显突破。宜趁此窗口积极进取，完成职业生涯的关键跳跃。"
        )

    # 最差大运
    if worst_idx >= 0 and worst_idx < len(dy_list) and worst_idx != best_idx:
        worst = dy_list[worst_idx]
        parts.append(
            f"需重点防范{worst['gan_zhi']}运（{worst['start_age']}~{worst['end_age']}岁），此运为运势低谷。忌神当道或喜用受制，诸事不宜冒进。建议此运期间以稳守为主，不宜大规模投资或跳槽，避免与人发生正面冲突。"
        )

    # 大运十神概括
    shi_shen_count = {}
    for dy in dy_list:
        ss = dy.get("gan_ss", "")
        if ss:
            shi_shen_count[ss] = shi_shen_count.get(ss, 0) + 1
    if shi_shen_count:
        top_ss = sorted(shi_shen_count.items(), key=lambda x: -x[1])
        parts.append(
            f"大运十神以{top_ss[0][0]}出现最多（共{top_ss[0][1]}步），{top_ss[0][0]}主导了命主大半生的基调。{'、'.join(f'{k}({v}步)' for k, v in top_ss[:3])}共同构成了完整的运程曲线。"
        )

    return "".join(parts)


# ═══════════════════════════════════════════
# §18 三决断
# ═══════════════════════════════════════════


def narrative_verdicts(verdicts: list) -> str:
    """§18 三决断 — 三大核心判断"""
    if not verdicts:
        return "暂无三决断数据。"

    parts = ["三决断是命理最核心的三个判断，涵盖财富、事业和婚姻三大支柱："]

    for i, v in enumerate(verdicts):
        title = v.get("title", "")
        event = v.get("event", "")
        time = v.get("time", "")
        reason = v.get("reason", "")
        parts.append(f"{title}：{event}。{time}。依据：{reason}。")

    # 综合判断
    wealth_deg = ""
    career_deg = ""
    marriage_deg = ""
    for v in verdicts:
        t = v.get("title", "")
        deg = v.get("degree", "")
        if "财富" in t:
            wealth_deg = deg
        elif "事业" in t:
            career_deg = deg
        elif "婚姻" in t or "家庭" in t:
            marriage_deg = deg

    if wealth_deg or career_deg or marriage_deg:
        summary_parts = []
        if wealth_deg:
            summary_parts.append(f"财富等级{wealth_deg}")
        if career_deg:
            summary_parts.append(f"事业评分为{career_deg}")
        if marriage_deg:
            summary_parts.append(f"婚姻质量{marriage_deg}")
        parts.append("综合来看，" + "，".join(summary_parts) + "。")

    parts.append(
        "三决断环环相扣——财富格局决定事业天花板，事业成败影响婚姻质量，婚姻安定反哺财富积累。三柱之中有一个短板，整体人生质量就会受到制约。短板所在的大运，就是人生的关键突破口。"
    )

    return "".join(parts)


# ═══════════════════════════════════════════
# §19 运程总评
# ═══════════════════════════════════════════


def narrative_da_yun_curve(dy_curve_data: dict) -> str:
    """§19 运程总评 — 运程曲线解读"""
    curve = dy_curve_data.get("curve", [])
    if not curve:
        return "暂无运程曲线数据。"

    # 分段分析
    youth = [c for c in curve if any(k in str(c.get("age", "")) for k in ["0~", "1~", "2~", "3~"])]
    mid = [c for c in curve if any(k in str(c.get("age", "")) for k in ["4~", "5~"])]
    late = [c for c in curve if any(k in str(c.get("age", "")) for k in ["6~", "7~", "8~", "9~"])]

    scores = [c.get("score", 5) for c in curve]
    avg = round(sum(scores) / len(scores), 1) if scores else 5
    max_s = max(scores) if scores else 5
    min_s = min(scores) if scores else 5
    wave = round(max_s - min_s, 1)

    parts = []
    if wave >= 5:
        parts.append(
            f"运程波动幅度达{wave}分，属于大起大落型命局。最高{max_s}分到最低{min_s}分的落差，意味着命主一生将经历多次命运转折。"
        )
    elif wave >= 3:
        parts.append(f"运程波动约{wave}分，起伏适中。有高峰有低谷，但不至于极端的起落。")
    else:
        parts.append(f"运程波动约{wave}分，整体平稳。大运之间落差不大，人生节奏较为稳定。")

    parts.append(f"全盘平均分{avg}分，{_s(avg)}水平。")

    # 总体趋势
    if len(scores) >= 3:
        # 看趋势是上升还是下降
        first_half = scores[: len(scores) // 2]
        second_half = scores[len(scores) // 2 :]
        first_avg = round(sum(first_half) / len(first_half), 1) if first_half else 0
        second_avg = round(sum(second_half) / len(second_half), 1) if second_half else 0
        if second_avg > first_avg + 0.5:
            parts.append(
                f"运程整体呈上升趋势，后段大运（平均{second_avg}分）优于前段（平均{first_avg}分），属于先苦后甜型命局。越到人生后期越顺遂。"
            )
        elif first_avg > second_avg + 0.5:
            parts.append(
                f"运程整体呈下降趋势，前段大运（平均{first_avg}分）优于后段（平均{second_avg}分），属于早年得力型命局。宜趁年轻时多积累、多拼搏。"
            )
        else:
            parts.append(f"运程前后段较为均衡，前段平均{first_avg}分、后段平均{second_avg}分，人生起伏不大但节奏稳定。")

    # 分段
    if youth:
        youth_scores = [c.get("score", 5) for c in youth]
        youth_avg = round(sum(youth_scores) / len(youth_scores), 1)
        parts.append(
            f"青壮年时期（{youth[0].get('age', '早年')}）平均{youth_avg}分，{_s(youth_avg)}。此阶段奠定人生基础，学业、事业起步、婚姻皆在于此。"
        )
    if mid:
        mid_scores = [c.get("score", 5) for c in mid]
        mid_avg = round(sum(mid_scores) / len(mid_scores), 1)
        parts.append(
            f"中年时期（{mid[0].get('age', '中年')}）平均{mid_avg}分，{_s(mid_avg)}。这是人生事业和财富的顶峰期，抓住好运能实现阶层跃迁。"
        )
    if late:
        late_scores = [c.get("score", 5) for c in late]
        late_avg = round(sum(late_scores) / len(late_scores), 1)
        parts.append(
            f"晚年时期（{late[0].get('age', '晚年')}）平均{late_avg}分，{_s(late_avg)}。宜放慢节奏，享受成果，注重健康保养。"
        )

    return "".join(parts)


# ═══════════════════════════════════════════
# §20 五行补充
# ═══════════════════════════════════════════


def narrative_wu_xing_advice(wx_data: dict) -> str:
    """§20 五行补充 — 颜色/方位/饰品/饮食"""
    if not wx_data or not wx_data.get("xi_yong_wx"):
        return "暂无五行补充数据。"

    xi = wx_data["xi_yong_wx"]
    colors = wx_data.get("colors", "")
    directions = wx_data.get("directions", "")
    jewellery = wx_data.get("jewellery", "")
    diet = wx_data.get("diet", "")
    lucky_num = wx_data.get("lucky_numbers", "")
    avoid_num = wx_data.get("avoid_numbers", "")

    parts = []
    parts.append(f"喜用五行{xi}，日常生活中的五行补运策略如下：")

    if colors:
        parts.append(f"颜色运用：多用{colors}色系的服饰和家居用品，这些颜色能潜移默化地补益命局的喜用能量。")
    if directions:
        parts.append(f"方位选择：宜选{directions}方位发展或居住，这些方位的气场对命主最为有利。")
    if jewellery:
        parts.append(f"饰品佩戴：推荐佩戴{jewellery}，石材本身的五行属性可以直接补益命局。")
    if diet:
        parts.append(f"饮食调养：{diet}。五行对应五脏，补益喜用五行对应的脏器是养生根本。")
    if lucky_num:
        parts.append(f"幸运数字：{lucky_num}。在选号、定价等生活细节中多使用这些数字。")
    if avoid_num:
        parts.append(f"忌讳数字：{avoid_num}。这些数字对应的五行属忌神，日常尽量避免。")

    return "".join(parts)


# ═══════════════════════════════════════════
# §21 人生建议
# ═══════════════════════════════════════════


def narrative_life_advice(advice_data: dict) -> str:
    """§21 人生建议 — 基于引擎数据的综合性建议"""
    if not advice_data:
        return "暂无人生建议数据。"

    parts = ["以下是基于命局数据给出的五大领域建议："]

    # 事业
    career = advice_data.get("career", {})
    if career:
        adv = career.get("advice", "")
        grade = career.get("grade", 0)
        best_dy = career.get("best_da_yun", "")
        parts.append(
            f"【事业建议】{adv}。事业等级{grade}/10分，最佳大运{best_dy}宜重点把握。建议深耕专业领域积累核心竞争力，在大运窗口期主动争取晋升或转型机会。"
        )

    # 财富
    wealth = advice_data.get("wealth", {})
    if wealth:
        adv_w = wealth.get("advice", "")
        strategy = wealth.get("strategy", "")
        parts.append(
            f"【财富建议】{adv_w}。策略上宜{strategy}。财富积累需要耐心，不要试图一夜暴富，而是通过持续的积累和正确的投资策略稳步增长。"
        )

    # 健康
    health = advice_data.get("health", {})
    if health:
        adv_h = health.get("advice", "")
        parts.append(
            f"【健康建议】{adv_h}。健康是命局的根基，身体状态直接影响能否扛得住大运的吉凶。无论身强身弱，规律的体检和作息都是最基本的保障。"
        )

    # 婚姻
    marriage = advice_data.get("marriage", {})
    if marriage:
        adv_m = marriage.get("advice", "")
        parts.append(
            f"【婚姻建议】{adv_m}。婚姻靠经营，夫妻宫配置好的命局也不能忽视日常沟通和磨合；配置一般的更需要在理解和包容上下功夫。"
        )

    # 社交
    social = advice_data.get("social", {})
    if social:
        adv_s = social.get("advice", "")
        parts.append(
            f"【社交建议】{adv_s}。选择对的圈子和合作伙伴，等于主动优化了人生气场环境。五人之中必有我师，择其善者而从之。"
        )

    parts.append(
        "以上建议基于原局和大运推演，具体操作需结合实际情况灵活变通。命理是概率，不是宿命——知命是起点，改运靠行动。"
    )

    return "".join(parts)
