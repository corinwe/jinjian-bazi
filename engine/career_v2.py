"""
金鉴真人·事业分析引擎 v2.0 — 确定性规则完整版
基于bazi-career-analysis v2.1

规则体系：
  格局定方向（做什么）
  官杀定高度（做到什么级别）
  恶神制化定级别（能不能成大器）
  五行定行业（在哪个领域做）
  36命格职业类（12条公众号沉淀）
"""

from __future__ import annotations
from constants import TIAN_GAN_WU_XING, DI_ZHI_WU_XING, DI_ZHI_CANG_GAN
from shi_shen import get_shi_shen_for_gan, get_shi_shen_for_cang_gan

# ── 正八格事业方向 ──
GE_JU_DIRECTION = {
    "正官格": "公职/管理",
    "七杀格": "执法/军警/管理",
    "正财格": "稳定收入",
    "偏财格": "做生意/投资",
    "正印格": "教育/文化/服务",
    "偏印格": "冷门研究/分析师",
    "食神格": "餐饮/文艺/鉴赏",
    "伤官格": "歌唱/影视/特技",
}

GE_JU_DESC = {
    "正官格": "守法负责，适合体制内",
    "七杀格": "果断魄力，适合有压力岗位",
    "正财格": "踏实做事，不适合投机",
    "偏财格": "灵活财路，适合创业",
    "正印格": "慈悲，适合文职",
    "偏印格": "独特，适合技术岗",
    "食神格": "福气，适合享受型行业",
    "伤官格": "才华，适合创新型行业",
}

# ── 三大伟人格 ──
WEI_REN_GE = {
    "杀印相生格": {"comb": "七杀+印→化杀为权", "principle": "身弱用印化杀，把压力变成权力", "level": "👑顶级"},
    "食神制杀格": {"comb": "食神+七杀→以食制杀", "principle": "身强用食神克杀，以智谋制伏凶险", "level": "👑顶级"},
    "杀身两停格": {"comb": "七杀=日主能量", "principle": "势均力敌，硬碰硬", "level": "👑顶级"},
}

# ── 伤官三格 ──
SHANG_GUAN_SAN_GE = {
    "伤官配印": "位高权重，文化管理",
    "伤官生财": "以技术/创意赚钱",
    "伤官见官": "与官对立，官非口舌",
    "伤官伤尽": "管官的官（纪检/监察部级）",
}

# ── 五行定行业 ──
WX_INDUSTRY = {
    "金": "五金矿产、汽车交通、金融证券、金属加工、珠宝玉器、机械、电器电子、医疗器械",
    "木": "木材家具、园林园艺、纸业出版、教育文化、服装纺织、中医、水果店",
    "水": "服务业、物流运输、化妆品、饮料、银行出纳、水产品、旅游、新闻传播、医生",
    "火": "广告传媒、文化教育、灯光照明、电子电器、餐饮饭店、周易文化、美容美发",
    "土": "房地产建筑、土方工程、农产品种植、食品加工、装修工程、陶瓷砖瓦、宠物饲料",
}

# ── 正官/七杀职业细化 ──
GUAN_SHA_CAREER = {
    "正官格": "军官、法官、警官、地方官、社长（企业管理者）",
    "七杀格": "军警、运动员、法官、律师、记者、建筑业、造船业、运输业",
}

# ── 名望五元素 ──
FAME_MAP = {
    "正官": "正途名望（体制内认可）",
    "七杀": "权威型名望/争议型人物",
    "正印": "德高望重（学养声誉）",
    "偏印": "独特专长名望",
    "食神": "知名度（作品/技能传播）",
    "伤官": "创新知名度",
    "正财": "社会地位（富甲一方）",
    "偏财": "财富名气",
}

# ── 36命格职业类（12条）──
PROFESSION_36 = [
    {"命格": "最有科研天赋", "条件": "身旺有印伤官旺生财"},
    {"命格": "最有政客天赋", "条件": "财官印旺顺生日主"},
    {"命格": "最有商人天赋", "条件": "身旺坐财食伤旺生财"},
    {"命格": "最有文人天赋", "条件": "木火伤官（日主木有水为源旺，伤官火透出泄身）"},
    {"命格": "最有艺术天赋", "条件": "金水伤官"},
    {"命格": "最有军警天赋", "条件": "食神制杀"},
    {"命格": "最有教师天赋", "条件": "官印身旺连接相生"},
    {"命格": "最有医生天赋", "条件": "日旺伤旺+丙火辛金相合"},
    {"命格": "最有营销天赋", "条件": "财制旺印（印旺为病财制印为药）"},
    {"命格": "最有咨询师天赋", "条件": "身旺食伤生财"},
    {"命格": "最有运动员天赋", "条件": "比劫众官杀得用"},
    {"命格": "最有经纪人天赋", "条件": "比旺财旺食伤通关"},
]


def _evaluate_wei_ren_ge(all_ss: list[str], shen_label: str) -> tuple[str, bool]:
    """判断是否为三大伟人格"""
    has_sha = "七杀" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_shi = "食神" in all_ss
    
    if has_sha and has_yin and shen_label == "身弱":
        return "杀印相生格（伟人格）", True
    if has_sha and has_shi and shen_label == "身强":
        return "食神制杀格（伟人格）", True
    if has_sha and shen_label == "身强":
        sha_count = all_ss.count("七杀")
        if sha_count >= 2:
            return "杀身两停格（伟人格）", True
    return "", False


def _evaluate_shang_guan_ge(all_ss: list[str], ri_zhu: str,
                             bazi_gans: list[str], xi_yong: list[str]) -> str:
    """判断伤官三格"""
    has_shang = "伤官" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_guan = "正官" in all_ss
    has_cai = "正财" in all_ss or "偏财" in all_ss
    
    if not has_shang:
        return ""
    
    # 伤官伤尽（no官杀+伤官旺）→最贵
    if has_shang and not has_guan and "七杀" not in all_ss:
        return "伤官伤尽（管官的官）"
    if has_shang and has_yin:
        return "伤官配印（位高权重）"
    if has_shang and has_cai:
        return "伤官生财（以技术/创意赚钱）"
    if has_shang and has_guan:
        return "伤官见官（与官对立，官非口舌）"
    return "伤官格"


def _detect_talent_36(all_ss: list[str], bazi_gans: list[str], bazi_zhis: list[str],
                       ri_zhu: str, shen_label: str, shen_score: float) -> list[str]:
    """36命格职业类匹配"""
    talents = []
    
    # 读取八字数据
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_shang = "伤官" in all_ss
    has_shi = "食神" in all_ss
    has_guan = "正官" in all_ss
    has_sha = "七杀" in all_ss
    has_cai = "正财" in all_ss or "偏财" in all_ss
    has_bi = "比肩" in all_ss or "劫财" in all_ss
    shen_qiang = shen_label == "身强"
    
    # 规则1: 最有科研天赋 — 身旺有印伤官旺生财
    if shen_qiang and has_yin and has_shang and has_cai:
        talents.append("🔬 最有科研天赋")
    
    # 规则2: 最有政客天赋 — 财官印旺顺生日主
    if has_cai and has_guan and has_yin:
        talents.append("🏛️ 最有政客天赋")
    
    # 规则3: 最有商人天赋 — 身旺坐财食伤旺生财
    if shen_qiang and has_cai and has_shi and has_shang:
        talents.append("💼 最有商人天赋")
    
    # 规则4: 最有文人天赋 — 木火伤官
    if ri_wx == "木" and has_shang and "午" in bazi_zhis:
        talents.append("📝 最有文人天赋")
    
    # 规则5: 最有艺术天赋 — 金水伤官
    if ri_wx == "金" and has_shang:
        talents.append("🎨 最有艺术天赋")
    
    # 规则6: 最有军警天赋 — 食神制杀
    if has_shi and has_sha:
        talents.append("🛡️ 最有军警天赋")
    
    # 规则7: 最有教师天赋 — 官印身旺连接相生
    if has_guan and has_yin and shen_qiang:
        talents.append("📖 最有教师天赋")
    
    # 规则8: 最有医生天赋 — 日旺伤旺+丙火辛金相合
    if shen_qiang and has_shang:
        talents.append("🏥 最有医生天赋")
    
    # 规则9: 最有营销天赋 — 财制旺印
    if has_cai and has_yin and shen_label == "身弱":
        talents.append("📊 最有营销天赋")
    
    # 规则10: 最有咨询师天赋 — 身旺食伤生财
    if shen_qiang and (has_shi or has_shang) and has_cai:
        talents.append("💡 最有咨询师天赋")
    
    # 规则11: 最有运动员天赋 — 比劫众官杀得用
    if has_bi and (has_guan or has_sha) and shen_qiang:
        talents.append("🏃 最有运动员天赋")
    
    # 规则12: 最有经纪人天赋 — 比旺财旺食伤通关
    if has_bi and has_cai and (has_shi or has_shang):
        talents.append("🤝 最有经纪人天赋")
    
    return talents[:3]  # 最多3个


def _evaluate_fame(all_ss: list[str], ge_ju_main: str) -> list[str]:
    """名望评估"""
    fame = []
    for ss in all_ss:
        if ss in FAME_MAP:
            fame.append(FAME_MAP[ss])
    
    # 格局看名望
    ge_fame_map = {
        "杀印相生": "高（政界/军界）",
        "食神制杀": "高（政界/军界）",
        "食神配印": "高（文化/艺术）",
        "伤官配印": "中高（创新/争议）",
        "正官格": "中高（体制内）",
        "财官双美": "中（商界）",
    }
    for k, v in ge_fame_map.items():
        if k in ge_ju_main:
            fame.append(f"格局名望: {v}")
            break
    if not [f for f in fame if "格局名望" in f]:
        fame.append("格局名望: 中（有潜力）")
    
    return fame


def analyze_career_full(
    ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str],
    shen_label: str, shen_score: float,
    xi_yong: list[str], ji_shen: list[str],
    ge_ju_main: str, ge_ju_detail: str,
) -> dict:
    """
    事业完整分析 v2.0 — 基于bazi-career-analysis全部规则
    """
    all_ss = [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]
    
    # ── ① 格局定方向 ──
    direction = GE_JU_DIRECTION.get(ge_ju_main, "多元化")
    desc = GE_JU_DESC.get(ge_ju_main, "")
    
    # ── ② 伟人格+伤官格判定 ──
    wei_ren_ge_name, is_wei = _evaluate_wei_ren_ge(all_ss, shen_label)
    shang_guan_type = _evaluate_shang_guan_ge(all_ss, ri_zhu, bazi_gans, xi_yong)
    
    # ── ③ 身强弱定工作模式 ──
    if shen_label == "身强" and shen_score >= 60:
        work_mode = "管理/领导岗位，有能力担事，越挫越勇"
        level = "高管/管理型"
    elif shen_label == "身弱" and shen_score < 40:
        work_mode = "技术/专业岗，需贵人/平台托底"
        level = "专家/技术型"
    else:
        work_mode = "文武兼备，灵活性最高"
        level = "中高层/专业型"
    
    # ── ④ 恶神制化定级别 ──
    has_sha = "七杀" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_shi = "食神" in all_ss
    has_shang = "伤官" in all_ss
    has_guan = "正官" in all_ss
    has_cai = "正财" in all_ss or "偏财" in all_ss
    has_bi = "比肩" in all_ss or "劫财" in all_ss
    
    # 杀印相生格
    if is_wei:
        career_grade = "👑 顶级·伟人格"
        grade_score = 9
    elif has_sha and (has_yin or has_shi):
        career_grade = "🌟 上等·恶神有制"
        grade_score = 8
    elif has_guan and has_yin and (shen_label == "身强" or shen_label == "中和"):
        career_grade = "🌟 上等·官印相生"
        grade_score = 7
    elif has_guan and shen_label == "身强":
        career_grade = "🥈 中等偏上·正官得用"
        grade_score = 6
    elif has_cai and shen_label == "身强":
        career_grade = "🏠 中等·身强胜财"
        grade_score = 5
    elif has_yin and shen_label == "身弱":
        career_grade = "🏠 中等·身弱得印"
        grade_score = 5
    else:
        career_grade = "🪜 下等"
        grade_score = 3
    
    # ── ⑤ 官杀与事业关系 ──
    guan_sha_analysis = []
    gans_ss = [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]
    for i, ss in enumerate(gans_ss):
        if ss == "正官":
            if shen_label == "身强":
                guan_sha_analysis.append(f"正官透干+身强→利管理晋升")
            else:
                guan_sha_analysis.append(f"正官透干+身弱→压力大")
        if ss == "七杀":
            if shen_label == "身强":
                guan_sha_analysis.append(f"七杀透干+身强→杀伐决断")
            else:
                guan_sha_analysis.append(f"七杀透干+身弱→压力/小人")
    
    # 官杀混杂检查
    if has_guan and has_sha and shen_label == "身弱":
        guan_sha_analysis.append("⚠️ 官杀混杂+身弱→事业波动大")
    elif has_guan and has_sha and shen_label == "身强":
        guan_sha_analysis.append("官杀混杂但身强→可驾驭")
    
    # ── ⑥ 五行定行业 ──
    xi_wx = xi_yong[0] if xi_yong else "土"
    industry = WX_INDUSTRY.get(xi_wx, "多元化")
    
    # 正官/七杀职业细化
    guan_sha_career = GUAN_SHA_CAREER.get(ge_ju_main, "")
    
    # ── ⑦ 36命格职业天赋 ──
    talents = _detect_talent_36(all_ss, bazi_gans, bazi_zhis, ri_zhu, shen_label, shen_score)
    
    # ── ⑧ 名望评估 ──
    fame = _evaluate_fame(all_ss, ge_ju_main)
    
    # ── ⑨ 三起三落时间线 ──
    timeline = [
        {"period": "20~32岁", "desc": "入世探索→碰壁调整（第一步上升/下降）"},
        {"period": "32~44岁", "desc": "立业上升→瓶颈危机（第二步上升/下降）"},
        {"period": "44~56岁", "desc": "成就巅峰→传承转型（第三步上升/下降）"},
        {"period": "56岁+", "desc": "守成/退休（窗口关闭）"},
    ]
    
    # ── ⑩ 创业判断（铁律）──
    if shen_label == "身弱" and shen_score < 40:
        entrepreneurship = "❌ 不适合自己单干创业（身弱扛不住）"
        best_path = "✅ 借平台（大公司/体制内）+ 借贵人 + 借专业深耕"
    elif shen_label == "身强" and ge_ju_main in ("偏财格", "七杀格"):
        entrepreneurship = "✅ 适合创业，身强能扛压力"
        best_path = "适合自主创业或承担高风险岗位"
    else:
        entrepreneurship = "⚠️ 创业需谨慎，建议先在大平台积累经验"
        best_path = "建议大平台积累→时机成熟再考虑自主"
    
    # ── ⑪ 近官立贵 ──
    social_circle = []
    if has_cai:
        social_circle.append("认识老板/有钱人")
    if has_guan or has_sha:
        social_circle.append("认识领导/有权力者")
    if has_yin:
        social_circle.append("认识文化人/师长")
    if has_bi:
        social_circle.append("朋友多")
    if has_shi or has_shang:
        social_circle.append("认识技术/艺术人才")
    
    # ── ⑫ 详细规则分析文本（供深度报告使用）──
    detail_parts = []
    
    # 格局定方向
    if direction:
        detail_parts.append(f"【格局定方向】格局{ge_ju_main}，事业方向宜走「{direction}」路线。{desc}。")
    
    # 伟人格
    if wei_ren_ge_name:
        wr_info = WEI_REN_GE.get(wei_ren_ge_name, {})
        detail_parts.append(f"【伟人格判定】{wei_ren_ge_name}——{wr_info.get('principle', '')}。{wr_info.get('comb', '')}。")
        detail_parts.append(f"凡成大事者必有恶神，恶神有制方为贵。{wei_ren_ge_name}为顶级格局，若大运配合可成就非凡。")
    
    # 伤官格
    if shang_guan_type and shang_guan_type != "无":
        sg_desc = SHANG_GUAN_SAN_GE.get(shang_guan_type, "")
        detail_parts.append(f"【伤官格】{shang_guan_type}：{sg_desc}。")
    
    # 身强身弱定模式
    if shen_label == "身强":
        detail_parts.append(f"【身强定模式】身强{shen_score:.0f}分，有能力担事，适合管理/领导岗位。官杀为喜用时利晋升，越挫越勇，可挑战高压岗位。")
    elif shen_label == "身弱":
        detail_parts.append(f"【身弱定模式】身弱{shen_score:.0f}分，有能力但容易累，适合技术/专业岗。印为喜用时需贵人/平台托底。杀印相生→以智慧化压力为成就。")
    else:
        detail_parts.append(f"【中和定模式】中和{shen_score:.0f}分，文武兼备，灵活性最高。官杀为喜用时事业顺遂。")
    
    # 恶神制化
    detail_parts.append(f"【恶神制化定级别】{career_grade}（{grade_score}/10）。{ge_ju_main}中")
    if is_wei:
        detail_parts[-1] += "恶神有制，杀印相生/食神制杀，为伟人级别的格局配置。"
    elif has_sha and (has_yin or has_shi):
        detail_parts[-1] += "七杀有制，化为权威和执行力，能担当重任。"
    elif has_guan and has_yin:
        detail_parts[-1] += "官印相生，管理名望自然成，适合体制内或大平台发展。"
    elif has_guan:
        detail_parts[-1] += "正官得用，守法负责，适合管理岗位逐步晋升。"
    else:
        detail_parts[-1] += "无恶神激发，宜走专业路线深耕。"
    
    # 官杀分析
    if guan_sha_analysis:
        detail_parts.append(f"【官杀分析】{'；'.join(guan_sha_analysis)}。")
    
    # 五行定行业
    if industry:
        detail_parts.append(f"【五行定行业】喜用{xi_wx}五行，适宜从事{industry}等相关领域。")
    
    # 36命格天赋
    if talents:
        detail_parts.append(f"【36命格天赋】{'、'.join(talents)}。")
    
    # 名望
    if fame:
        detail_parts.append(f"【名望评估】{'；'.join(fame)}。")
    
    # 创业判断
    detail_parts.append(f"【创业判断】{entrepreneurship}。{best_path}。")
    
    # 社交圈
    if social_circle:
        detail_parts.append(f"【近官立贵】朋友圈决定事业层次：{'；'.join(social_circle)}。")
    
    detail_analysis = "\n".join(detail_parts)
    
    return {
        "career_direction": direction,
        "career_desc": desc,
        "work_mode": work_mode,
        "career_level": level,
        "career_grade": career_grade,
        "grade_score": grade_score,
        "wei_ren_ge": wei_ren_ge_name,
        "shang_guan_type": shang_guan_type,
        "guan_sha_analysis": guan_sha_analysis,
        "recommended_industries": industry,
        "guan_sha_career_detail": guan_sha_career,
        "fame_analysis": fame,
        "talents_36": talents,
        "timeline": timeline,
        "entrepreneurship": entrepreneurship,
        "best_path": best_path,
        "social_circle": social_circle,
        "detail_analysis": detail_analysis,  # 🆕 深度报告用
    }
