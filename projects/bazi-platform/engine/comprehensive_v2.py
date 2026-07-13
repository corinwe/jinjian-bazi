"""
金鉴真人·确定性规则引擎 v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
基于九龙道长原始规则体系的确定性计算模块
所有函数输入为确定性数据，输出为确定性JSON
零幻觉、零硬编码、零大模型推理

来源: bazi-career-analysis / bazi-education-analysis / bazi-marriage-analysis
      bazi-children-analysis / bazi-health-psychology / bazi-foundation-analysis
"""

from __future__ import annotations

from career_v2 import analyze_career_full as analyze_career_advanced
from children_v2 import analyze_children_full as analyze_children_advanced
from constants import DI_ZHI_CANG_GAN, TIAN_GAN_WU_XING, BaZi
from health_v2 import analyze_health_full as analyze_health_advanced
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan
from shi_shang import calc_shi_shang_score
from wealth_v2 import analyze_wealth_full as analyze_wealth_advanced

# ════════════════════════════════════════════
# §7 身材外貌（基于bazi-foundation-analysis）
# ════════════════════════════════════════════

# 日主五行定长相基调
RI_ZHU_APPEARANCE = {
    "甲": {"build": "高挑修长", "face": "五官端正、额头饱满", "skin": "偏白偏黄", "style": "正直大气"},
    "乙": {"build": "柔美匀称", "face": "面容柔和、眉眼清秀", "skin": "偏白", "style": "温婉文艺"},
    "丙": {"build": "偏丰满、中等身高", "face": "面色红润、眼睛有神", "skin": "偏红润", "style": "热情开朗"},
    "丁": {"build": "适中不胖不瘦", "face": "面容精致、眼神温柔", "skin": "偏白偏红润", "style": "温润细腻"},
    "戊": {"build": "敦厚结实、骨架偏大", "face": "五官敦厚、鼻头圆", "skin": "偏黄", "style": "稳重可靠"},
    "己": {"build": "肉感适中、体态柔美", "face": "面容柔和、圆脸鹅蛋脸", "skin": "偏黄", "style": "内敛含蓄"},
    "庚": {"build": "骨架硬朗、肩宽", "face": "五官立体、下颌线分明", "skin": "偏白", "style": "刚毅果断"},
    "辛": {"build": "骨感匀称、身材纤细", "face": "面容精致、鼻梁秀挺", "skin": "白皙", "style": "清秀高雅"},
    "壬": {"build": "丰腴饱满、体态圆润", "face": "大眼睛、面部饱满", "skin": "偏白偏黑", "style": "智慧灵动"},
    "癸": {"build": "柔美纤细、腰身明显", "face": "面容柔美、眼神含蓄", "skin": "偏白偏暗", "style": "含蓄聪慧"},
}

# 格局定气质
GE_JU_STYLE = {
    "正官格": "端庄正气、光明磊落",
    "七杀格": "霸气锐利、干练果断",
    "正印格": "书卷气、慈眉善目",
    "偏印格": "清冷孤傲、独特气质",
    "正财格": "朴实稳重、务实感",
    "偏财格": "豪爽大方、江湖气",
    "食神格": "福态圆润、亲和力",
    "伤官格": "灵秀叛逆、有灵气",
}


def analyze_appearance(
    ri_zhu: str, shen_label: str, shen_score: float, bazi_gans: list[str], bazi_zhis: list[str], ge_ju_main: str = ""
) -> dict:
    """§7 身材外貌分析 — 基于bazi-foundation-analysis §23规则"""

    # 日主五行基调
    base = RI_ZHU_APPEARANCE.get(ri_zhu, {"build": "中等", "face": "端正", "skin": "正常", "style": "温和"})

    # 格局气质修正
    style_extra = GE_JU_STYLE.get(ge_ju_main, "")

    # 身强弱修正
    if shen_label == "身强":
        height_estimate = "中等偏上(175-185cm)"
        build_extra = "骨架偏大/肌肉型"
    elif shen_label == "身弱":
        height_estimate = "中等(165-178cm)"
        build_extra = "骨架偏小/纤细型"
    else:
        height_estimate = "中等(168-180cm)"
        build_extra = "骨架适中"

    # 食神/伤官定胖瘦
    shi_shen_all = []
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        shi_shen_all.append(ss)

    has_shi_shen = "食神" in shi_shen_all
    has_shang_guan = "伤官" in shi_shen_all

    if has_shi_shen and not has_shang_guan:
        weight_tendency = "易发胖（食神福相）"
    elif has_shang_guan and not has_shi_shen:
        weight_tendency = "偏瘦精干（伤官泄秀）"
    elif has_shi_shen and has_shang_guan:
        weight_tendency = "中等，食伤平衡"
    else:
        weight_tendency = "普通，不易胖"

    # 五行特殊修正
    wx_count = {}
    for g in bazi_gans:
        wx = TIAN_GAN_WU_XING[g]
        wx_count[wx] = wx_count.get(wx, 0) + 1
    for z in bazi_zhis:
        for cg, _ in DI_ZHI_CANG_GAN.get(z, []):
            wx = TIAN_GAN_WU_XING[cg]
            wx_count[wx] = wx_count.get(wx, 0) + 1

    # 金水两旺出美女
    has_jin_shui = wx_count.get("金", 0) >= 2 and wx_count.get("水", 0) >= 2
    if has_jin_shui and bazi_gans[2:] and TIAN_GAN_WU_XING.get(bazi_gans[2], "") in ("庚", "辛"):
        beauty_note = "金水相生，皮肤白皙、气质出众、鼻子高挺"
    else:
        beauty_note = ""

    return {
        "ri_zhu_appearance": f"{base['build']}，{base['face']}，皮肤{base['skin']}",
        "height_estimate": height_estimate,
        "build": build_extra,
        "style": f"{base['style']}·{style_extra}" if style_extra else base["style"],
        "weight_tendency": weight_tendency,
        "beauty_note": beauty_note,
    }


# ════════════════════════════════════════════
# §9 置业/买房（基于喜用神+财星规则）
# ════════════════════════════════════════════

DIRECTION_MAP = {"金": "西/西北", "水": "北", "木": "东/东南", "火": "南", "土": "中/西南/东北"}


def analyze_property(
    ri_zhu: str, ri_zhi: str, xi_yong: list[str], da_yun_list: list[dict], best_idx: int, cai_xing_total: float,
    bazi_zhis: list[str] | None = None,
) -> dict:
    """§9 置业分析"""
    from xing_chong_he_hua import check_all_relations

    xi = xi_yong[0] if xi_yong else "土"
    direction = DIRECTION_MAP.get(xi, "吉")

    windows = []
    if best_idx >= 0 and best_idx < len(da_yun_list):
        dy = da_yun_list[best_idx]
        windows.append(
            {
                "age_range": f"{dy.get('start_age', '?')}~{dy.get('end_age', '?')}岁",
                "da_yun": dy.get("gan_zhi", ""),
                "type": "最佳置业期",
            }
        )

    # 财星定置业能力
    if cai_xing_total >= 40:
        property_level = "强，有能力购置多处房产"
    elif cai_xing_total >= 20:
        property_level = "中，有能力购房自住"
    else:
        property_level = "偏弱，需大运配合"

    # 刑冲合害→房产/搬迁判断
    property_timing = []
    if bazi_zhis and len(bazi_zhis) >= 4:
        rel = check_all_relations(bazi_zhis)
        # 土冲→住宅变动（辰戌/丑未为土冲）
        for ch in rel["冲"]:
            if "辰戌" in ch or "丑未" in ch:
                property_timing.append(f"{ch}→土冲越冲越强，房产/住宅变动机遇期")
        # 驿马冲→搬迁/搬家
        for ch in rel["冲"]:
            if ch in ("寅申冲", "申寅冲", "巳亥冲", "亥巳冲"):
                property_timing.append(f"{ch}→驿马冲，搬迁/换房机遇期")
        # 三合→购房窗口
        for he in rel["三合"]:
            if he.get("energy", 0) >= 1.0:
                property_timing.append(f"{he['type']}→能量共振，可把握购房窗口")

    return {
        "property_potential": f"喜用{xi}→宜选{direction}方位",
        "property_level": property_level,
        "windows": windows,
        "property_timing": property_timing if property_timing else ["无明显冲合信号"],
        "risk": "忌在忌神大运购置大额不动产",
    }


# ════════════════════════════════════════════
# §10 事业分析（基于bazi-career-analysis v2.0）
# ════════════════════════════════════════════

# 格局定方向
GE_JU_CAREER = {
    "正官格": {"direction": "公职/管理", "desc": "守法负责，适合体制内"},
    "七杀格": {"direction": "执法/军警/管理", "desc": "果断魄力，适合有压力岗位"},
    "正财格": {"direction": "稳定收入", "desc": "踏实做事，不适合投机"},
    "偏财格": {"direction": "做生意/投资", "desc": "灵活财路，适合创业"},
    "正印格": {"direction": "教育/文化/服务", "desc": "慈悲，适合文职"},
    "偏印格": {"direction": "冷门研究/分析师", "desc": "独特，适合技术岗"},
    "食神格": {"direction": "餐饮/文艺/鉴赏", "desc": "福气，适合享受型行业"},
    "伤官格": {"direction": "歌唱/影视/特技", "desc": "才华，适合创新型行业"},
}

# 五行定行业
WX_CAREER = {
    "金": "五金矿产、汽车交通、金融证券、金属加工、珠宝玉器、机械、电器电子",
    "木": "木材家具、园林园艺、纸业出版、教育文化、服装纺织、中医",
    "水": "服务业、物流运输、化妆品、饮料、银行出纳、水产品、旅游",
    "火": "广告传媒、文化教育、灯光照明、电子电器、餐饮饭店、周易文化",
    "土": "房地产建筑、土方工程、农产品种植、食品加工、装修工程",
}

# 名望五元素
FAME_MAP = {
    "正官": "正途名望（体制内认可）",
    "七杀": "权威型名望/争议型人物",
    "印星": "德高望重（学养声誉）",
    "食伤": "知名度（作品/技能传播）",
    "财星": "社会地位（富甲一方）",
}


def analyze_career(
    ri_zhu: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    shen_label: str,
    shen_score: float,
    xi_yong: list[str],
    ji_shen: list[str],
    ge_ju_main: str,
    ge_ju_detail: str,
) -> dict:
    """§10 事业分析 — 基于bazi-career-analysis v2.0规则"""

    # ① 格局定方向
    ge_info = GE_JU_CAREER.get(ge_ju_main, {"direction": "多元化", "desc": ""})

    # ② 身强弱定工作模式
    if shen_label == "身强":
        work_mode = "管理/领导岗位，有能力担事，越挫越勇"
        level = "高管/管理型" if ge_ju_main in ("正官格", "七杀格", "偏财格") else "专家/管理型"
    elif shen_label == "身弱":
        work_mode = "技术/专业岗，需贵人/平台托底"
        level = "专家/技术型"
    else:
        work_mode = "文武兼备，灵活性最高"
        level = "中高层/专业型"

    # ③ 恶神制化定级别
    all_ss = [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]
    has_sha = "七杀" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_shi = "食神" in all_ss
    has_shang = "伤官" in all_ss

    # 杀印相生格
    if has_sha and has_yin and shen_label == "身弱":
        career_grade = "👑 顶级·杀印相生格：化压力为权力"
        grade_score = 9
    # 食神制杀格
    elif has_sha and has_shi and shen_label == "身强":
        career_grade = "👑 顶级·食神制杀格：以智谋制伏凶险"
        grade_score = 9
    # 正官格身强
    elif ge_ju_main == "正官格" and shen_label == "身强":
        career_grade = "🌟 上等·正官得用"
        grade_score = 8
    # 七杀有制
    elif has_sha and (has_yin or has_shi):
        career_grade = "🌟 上等·恶神有制"
        grade_score = 7
    # 正官格
    elif ge_ju_main in ("正官格", "七杀格"):
        career_grade = "🥈 中等偏上"
        grade_score = 6
    # 财格或印格
    elif ge_ju_main in ("正财格", "偏财格", "正印格", "偏印格"):
        career_grade = "🏠 中等"
        grade_score = 5
    # 食伤格
    elif ge_ju_main in ("食神格", "伤官格"):
        career_grade = "🥉 中等偏下"
        grade_score = 4
    else:
        career_grade = "🪜 下等"
        grade_score = 3

    # ④ 五行定行业
    xi_wx = xi_yong[0] if xi_yong else "土"
    industry = WX_CAREER.get(xi_wx, "多元化")

    # ⑤ 名望分析
    fame_items = []
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in FAME_MAP:
            fame_items.append(FAME_MAP[ss])
    if not fame_items:
        if has_yin:
            fame_items.append("印星→德高望重")
        else:
            fame_items.append("无显著名望特征")

    # ⑥ 创业判断（铁律：身弱不创业）
    if shen_label == "身弱" and shen_score < 40:
        entrepreneurship = "❌ 不适合自己单干创业（身弱扛不住物理压力和不确定性）"
        best_path = "✅ 借平台（大公司/体制内）+ 借贵人 + 借专业深耕"
    elif shen_label == "身强" and ge_ju_main in ("偏财格", "七杀格"):
        entrepreneurship = "✅ 适合创业，身强能扛压力"
        best_path = "适合自主创业或承担高风险岗位"
    else:
        entrepreneurship = "⚠️ 创业需谨慎，建议先在大平台积累经验"
        best_path = "建议大平台积累→时机成熟再考虑自主"

    # 恶神制化描述
    e_shen_desc = ""
    if has_sha and has_yin:
        e_shen_desc = "七杀有印星化解→杀印相生，化为权威管理力"
    elif has_sha and has_shi:
        e_shen_desc = "七杀有食神制约→食神制杀，以智谋制伏凶险"
    elif has_sha:
        e_shen_desc = "七杀无制→事业压力大，需借大运印星化解"
    elif has_shang and has_yin:
        e_shen_desc = "伤官配印→才华有度，位高权重"
    else:
        e_shen_desc = "无显著恶神或恶神已有制化"

    return {
        "career_direction": ge_info["direction"],
        "career_desc": ge_info["desc"],
        "work_mode": work_mode,
        "career_level": level,
        "career_grade": career_grade,
        "grade_score": grade_score,
        "recommended_industries": industry,
        "fame_analysis": fame_items,
        "entrepreneurship": entrepreneurship,
        "best_path": best_path,
        "e_shen_zhi_hua": e_shen_desc,
        "key_career_years": [],  # 由调用方填充
    }


# ════════════════════════════════════════════
# §13 子女分析（基于bazi-children-analysis v2.0）
# ════════════════════════════════════════════

# 十二长生基数法
SHI_ER_CHANG_SHENG_CHILDREN = {
    "长生": 4,
    "沐浴": 2,
    "冠带": 3,
    "临官": 3,
    "帝旺": 5,
    "衰": 2,
    "病": 1,
    "死": 0,
    "墓": -1,
    "绝": 1,
    "胎": 1,
    "养": 3,
}

SHI_ER_KOU_JUE = {
    "长生": "长生四子中旬半",
    "沐浴": "沐浴一双保安康",
    "冠带": "冠带临官三子位",
    "临官": "冠带临官三子位",
    "帝旺": "旺中五子自成行",
    "衰": "衰中二子病中一",
    "病": "衰中二子病中一",
    "死": "死中晚景少儿郎",
    "墓": "入墓之时多不良",
    "绝": "受气为绝一个子",
    "胎": "胎中头胎是姑娘",
    "养": "养中三子只留一",
}

# 时支生育力排名
SHI_ZHI_SHENG_YU = {
    "卯": 8,
    "子": 6.5,
    "酉": 5.5,
    "午": 4.5,
    "辰": 3.5,
    "戌": 3.5,
    "丑": 3.5,
    "未": 3.5,
    "寅": 2,
    "申": 2,
    "巳": 2,
    "亥": 2,
}


def get_shi_er_chang_sheng(gan: str, zhi: str) -> str:
    """根据天干地支查十二长生（简化版）"""
    chang_sheng_map = {
        "甲": {
            "亥": "长生",
            "子": "沐浴",
            "丑": "冠带",
            "寅": "临官",
            "卯": "帝旺",
            "辰": "衰",
            "巳": "病",
            "午": "死",
            "未": "墓",
            "申": "绝",
            "酉": "胎",
            "戌": "养",
        },
        "丙": {
            "寅": "长生",
            "卯": "沐浴",
            "辰": "冠带",
            "巳": "临官",
            "午": "帝旺",
            "未": "衰",
            "申": "病",
            "酉": "死",
            "戌": "墓",
            "亥": "绝",
            "子": "胎",
            "丑": "养",
        },
        "戊": {
            "寅": "长生",
            "卯": "沐浴",
            "辰": "冠带",
            "巳": "临官",
            "午": "帝旺",
            "未": "衰",
            "申": "病",
            "酉": "死",
            "戌": "墓",
            "亥": "绝",
            "子": "胎",
            "丑": "养",
        },
        "庚": {
            "巳": "长生",
            "午": "沐浴",
            "未": "冠带",
            "申": "临官",
            "酉": "帝旺",
            "戌": "衰",
            "亥": "病",
            "子": "死",
            "丑": "墓",
            "寅": "绝",
            "卯": "胎",
            "辰": "养",
        },
        "壬": {
            "申": "长生",
            "酉": "沐浴",
            "戌": "冠带",
            "亥": "临官",
            "子": "帝旺",
            "丑": "衰",
            "寅": "病",
            "卯": "死",
            "辰": "墓",
            "巳": "绝",
            "午": "胎",
            "未": "养",
        },
        "乙": {
            "午": "长生",
            "巳": "沐浴",
            "辰": "冠带",
            "卯": "临官",
            "寅": "帝旺",
            "丑": "衰",
            "子": "病",
            "亥": "死",
            "戌": "墓",
            "酉": "绝",
            "申": "胎",
            "未": "养",
        },
        "丁": {
            "酉": "长生",
            "申": "沐浴",
            "未": "冠带",
            "午": "临官",
            "巳": "帝旺",
            "辰": "衰",
            "卯": "病",
            "寅": "死",
            "丑": "墓",
            "子": "绝",
            "亥": "胎",
            "戌": "养",
        },
        "己": {
            "酉": "长生",
            "申": "沐浴",
            "未": "冠带",
            "午": "临官",
            "巳": "帝旺",
            "辰": "衰",
            "卯": "病",
            "寅": "死",
            "丑": "墓",
            "子": "绝",
            "亥": "胎",
            "戌": "养",
        },
        "辛": {
            "子": "长生",
            "亥": "沐浴",
            "戌": "冠带",
            "酉": "临官",
            "申": "帝旺",
            "未": "衰",
            "午": "病",
            "巳": "死",
            "辰": "墓",
            "卯": "绝",
            "寅": "胎",
            "丑": "养",
        },
        "癸": {
            "卯": "长生",
            "寅": "沐浴",
            "丑": "冠带",
            "子": "临官",
            "亥": "帝旺",
            "戌": "衰",
            "酉": "病",
            "申": "死",
            "未": "墓",
            "午": "绝",
            "巳": "胎",
            "辰": "养",
        },
    }
    return chang_sheng_map.get(gan, {}).get(zhi, "")


def analyze_children(
    ri_zhu: str,
    gender: str,
    hour_gan: str,
    hour_zhi: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    da_yun_list: list[dict],
) -> dict:
    """§13 子女分析 — 基于bazi-children-analysis v2.0规则"""

    # ① 子女星定位（流派A通用版）
    if gender == "男":
        child_star_zi = "七杀"  # 子
        child_star_nv = "正官"  # 女
    else:
        child_star_zi = "伤官"  # 子
        child_star_nv = "食神"  # 女

    # 时柱十神
    hour_ss = get_shi_shen_for_gan(hour_gan, ri_zhu)

    # ② 十二长生基数法
    # 时支查子女星的十二长生
    cs = get_shi_er_chang_sheng(ri_zhu, hour_zhi)
    base_count = SHI_ER_CHANG_SHENG_CHILDREN.get(cs, 2)
    kou_jue = SHI_ER_KOU_JUE.get(cs, "")

    # ③ 时支生育力
    sheng_yu_score = SHI_ZHI_SHENG_YU.get(hour_zhi, 3)
    sheng_yu_rank = "强" if sheng_yu_score >= 5 else "中" if sheng_yu_score >= 3 else "弱"

    # ④ 子女星检查
    child_star_score = 0
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in (child_star_zi, child_star_nv):
            child_star_score += 15  # 透干+15分
        if ss in ("正官", "七杀"):
            child_star_score += 5

    if child_star_score >= 30:
        child_star_result = "子女缘分深，易孕"
    elif child_star_score >= 15:
        child_star_result = "中等，需大运流年引动"
    else:
        child_star_result = "缘分偏薄"

    # ⑤ 生育窗口
    windows = []
    for dy in da_yun_list:
        start = dy.get("start_age", 0)
        if 25 <= start <= 45 and dy.get("score", 5) >= 5:
            windows.append(f"{start}~{start + 9}岁")
            if len(windows) >= 2:
                break
    if not windows:
        windows = ["35~45岁"]

    # ⑥ 时柱喜忌判断子女成就
    if hour_ss in ("正官", "正印", "食神", "正财"):
        child_achievement = "子女有出息、孝顺"
    elif hour_ss in ("七杀", "伤官", "劫财"):
        child_achievement = "子女个性强，需用心教导"
    else:
        child_achievement = "子女普通，平顺发展"

    # 缘薄因素排查
    thin_factors = []
    if bazi_zhis[2] == bazi_zhis[3]:
        pass  # 日时相同不算
    # 日时冲
    chong_pairs = [
        ("子", "午"),
        ("午", "子"),
        ("丑", "未"),
        ("未", "丑"),
        ("寅", "申"),
        ("申", "寅"),
        ("卯", "酉"),
        ("酉", "卯"),
        ("辰", "戌"),
        ("戌", "辰"),
        ("巳", "亥"),
        ("亥", "巳"),
    ]
    if (bazi_zhis[2], bazi_zhis[3]) in chong_pairs:
        thin_factors.append("日时冲→与子女缘分薄")

    return {
        "hour_shi_shen": hour_ss,
        "child_star": {"son": child_star_zi, "daughter": child_star_nv},
        "shi_er_chang_sheng": {"position": cs, "base_count": base_count, "kou_jue": kou_jue},
        "sheng_yu_potential": f"时支{hour_zhi}→生育力{sheng_yu_rank}({sheng_yu_score})",
        "child_star_assessment": child_star_result,
        "child_count_estimate": f"约{max(1, base_count)}个（含缘分）",
        "windows": windows,
        "child_achievement": child_achievement,
        "thin_factors": thin_factors if thin_factors else ["无显著缘薄因素"],
    }


# ════════════════════════════════════════════
# §14 健康分析（基于bazi-health-psychology）
# ════════════════════════════════════════════

# 五行对应身体
WX_ORGAN = {
    "金": "肺/大肠/呼吸系统/皮肤",
    "木": "肝/胆/神经/筋骨",
    "水": "肾/膀胱/内分泌/生殖",
    "火": "心/小肠/眼/血液",
    "土": "脾/胃/消化系统",
}

# 宫位一扎法（用于七杀/偏印证病）
YI_ZHA = {
    "year_gan": "头顶~鼻子（头部/大脑/眼睛/耳鼻喉）",
    "year_zhi": "鼻子~锁骨（颈椎/喉咙/牙齿/肩部）",
    "month_gan": "锁骨~胸口（胸部/乳房/肺/心脏上部）",
    "month_zhi": "胸口~肚脐（上腹部/胃/脾/肝/胆）",
    "day_zhi": "小腹/胯部（子宫/卵巢/膀胱/大肠）",
    "hour_gan": "大腿（大腿骨/肌肉/血管）",
    "hour_zhi": "膝盖以下（小腿/脚踝/脚/关节）",
}

# 五行交战→疾病
WX_BATTLE_DISEASE = {
    "子午冲": "心血系统（心肾不交/失眠/高血压）",
    "卯酉冲": "肝胆/筋骨（肝气郁结/四肢酸痛）",
    "寅申冲": "筋骨损伤（神经痛/腰部扭伤）",
    "巳亥冲": "心脑血管（头晕/血压波动）",
    "辰戌冲": "脾胃不和（消化不良/胃痛）",
    "丑未冲": "脾胃/免疫（慢性胃炎/免疫紊乱）",
    "金木交战": "肝胆/筋骨/毛发",
    "水火交战": "心肾不交（失眠/耳鸣/心悸）",
    "土木交战": "脾胃/神经（胃痛/焦虑）",
    "火金交战": "肺/血（咳嗽/皮肤过敏）",
}


def analyze_health(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
    shen_label: str,
    shen_score: float,
    xi_yong: list[str],
    liu_nian_events: list = None,
) -> dict:
    """§14 健康分析 — 基于bazi-health-psychology规则"""

    # ① 五行过三检查
    wx_count = {}
    for g in bazi_gans:
        wx = TIAN_GAN_WU_XING[g]
        wx_count[wx] = wx_count.get(wx, 0) + 1
    for z in bazi_zhis:
        for cg, _ in DI_ZHI_CANG_GAN.get(z, []):
            wx = TIAN_GAN_WU_XING[cg]
            wx_count[wx] = wx_count.get(wx, 0) + 1
    # 包含日主
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    wx_count[ri_wx] = wx_count.get(ri_wx, 0) + 1

    # 五行过三→对应器官疾病
    over_three = []
    for wx, count in wx_count.items():
        if count >= 3:
            over_three.append(
                {
                    "wx": wx,
                    "count": count,
                    "organ": WX_ORGAN.get(wx, ""),
                    "risk": f"该五行能量过强({count}个)→注意{WX_ORGAN.get(wx, '')}",
                }
            )

    # ② 七杀断病法
    sha_risks = []
    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == "七杀":
            position_name = ["年干", "月干", "日干", "时干"][i]
            zha = YI_ZHA.get(
                "year_gan" if i == 0 else "month_gan" if i == 1 else "day_zhi" if i == 2 else "hour_gan", ""
            )
            sha_risks.append({"qi_sha_position": position_name, "body_area": zha, "level": "实际病痛"})

    for i, z in enumerate(bazi_zhis):
        for cg, ratio in DI_ZHI_CANG_GAN.get(z, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss == "七杀":
                position_name = ["年支", "月支", "日支", "时支"][i]
                zha = YI_ZHA.get(
                    "year_zhi" if i == 0 else "month_zhi" if i == 1 else "day_zhi" if i == 2 else "hour_zhi", ""
                )
                level = "本气→病已成型" if ratio >= 100 else "中气→潜在病灶" if ratio >= 60 else "余气→轻微不适"
                sha_risks.append({"qi_sha_position": f"{position_name}(藏干{cg})", "body_area": zha, "level": level})

    # ③ 偏印断病法
    pian_yin_risks = []
    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == "偏印":
            position_name = ["年干", "月干", "日干", "时干"][i]
            side = "右半身" if i % 2 == 0 else "左半身"
            pian_yin_risks.append(
                {"pian_yin_position": position_name, "side": side, "risk": f"{position_name}偏印→经络淤堵({side})"}
            )

    # ④ 五行交战
    battles = []
    chong_pairs = [("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"), ("辰", "戌"), ("巳", "亥")]
    for i, z1 in enumerate(bazi_zhis):
        for j, z2 in enumerate(bazi_zhis):
            if i < j and ((z1, z2) in chong_pairs or (z2, z1) in chong_pairs):
                key = f"{z1}{z2}冲"
                if key in WX_BATTLE_DISEASE:
                    battles.append({"type": key, "disease": WX_BATTLE_DISEASE[key]})

    # ⑤ 体质总评
    if shen_label == "身强" and shen_score >= 70:
        constitution = "体质强健，先天能量充足"
    elif shen_label == "身弱" and shen_score < 30:
        constitution = "体质偏弱，需注意调养"
    else:
        constitution = "体质中等，平顺健康"

    return {
        "constitution": constitution,
        "wu_xing_over_three": over_three,
        "qi_sha_risks": sha_risks[:3],  # 最多3条
        "pian_yin_risks": pian_yin_risks[:2],  # 最多2条
        "wu_xing_battles": battles,
        "focus_areas": list(set([o["organ"] for o in over_three] + [r["body_area"] for r in sha_risks[:1]])),
    }


# ════════════════════════════════════════════
# §18 三决断（确定性计算）
# ════════════════════════════════════════════


def generate_three_verdicts(
    shen_label: str,
    cai_score: float,
    ge_ju_detail: str,
    best_da_yun: dict,
    marriage_info: dict,
    career_grade_score: int,
) -> list:
    """§18 三决断 — 基于实际数据的确定性输出"""

    verdicts = []

    # 决断一：财富格局
    if cai_score >= 50:
        wealth_degree = "大富以上"
    elif cai_score >= 30:
        wealth_degree = "中富"
    elif cai_score >= 15:
        wealth_degree = "小富"
    else:
        wealth_degree = "小康"

    verdicts.append(
        {
            "title": "💰 财富格局",
            "person": f"财星{cai_score}分+{shen_label}",
            "event": f"财富等级：{wealth_degree}",
            "time": f"最佳运：{best_da_yun.get('gan_zhi', '')}（{best_da_yun.get('start_age', '?')}~{best_da_yun.get('end_age', '?')}岁）"
            if best_da_yun
            else "大运配合",
            "degree": wealth_degree,
            "reason": f"财星{cai_score}分+格局{ge_ju_detail}",
        }
    )

    # 决断二：事业/人生定位
    verdicts.append(
        {
            "title": "🏆 事业定位",
            "person": f"{shen_label}·{ge_ju_detail}",
            "event": f"事业等级：{['普通', '中等', '中上', '上等', '顶级'][min(4, max(0, career_grade_score - 3))]}",
            "time": f"最佳运：{best_da_yun.get('gan_zhi', '')}" if best_da_yun else "中年发力",
            "degree": f"等级{career_grade_score}/10",
            "reason": f"{shen_label}+{ge_ju_detail}→选择正确赛道持续深耕",
        }
    )

    # 决断三：婚姻/家庭
    marriage_quality = marriage_info.get("quality", "中等") if marriage_info else "中等"
    verdicts.append(
        {
            "title": "❤️ 婚姻家庭",
            "person": "夫妻宫配置",
            "event": f"婚姻质量：{marriage_quality}",
            "time": marriage_info.get("best_window_age", "适婚年龄") if marriage_info else "适婚年龄",
            "degree": marriage_quality,
            "reason": "配偶特征+夫妻宫十神组合",
        }
    )

    return verdicts


# ════════════════════════════════════════════
# §19 运程总评（运程曲线图）
# ════════════════════════════════════════════


def generate_da_yun_curve(da_yun_list: list[dict]) -> dict:
    """§19 运程总评 — 每步大运评分可视化"""
    curve = []
    for dy in da_yun_list:
        score = dy.get("score", 5)
        bar = "█" * int(round(score)) + "░" * (10 - int(round(score)))
        curve.append(
            {
                "da_yun": dy.get("gan_zhi", ""),
                "age": f"{dy.get('start_age', '?')}~{dy.get('end_age', '?')}岁",
                "score": score,
                "bar": bar,
            }
        )
    return {"curve": curve}


# ════════════════════════════════════════════
# §20 五行补充（颜色/方位/饰品/饮食）
# ════════════════════════════════════════════

COLOR_MAP = {"金": "白/金/银", "水": "蓝/黑/灰", "木": "绿/青", "火": "红/紫/橙", "土": "黄/棕/米"}
DIRECTION_MAP_FULL = {"金": "西/西北", "水": "北", "木": "东/东南", "火": "南", "土": "中/西南/东北"}
STONE_MAP = {
    "金": "白水晶/银饰",
    "水": "黑曜石/海蓝宝",
    "木": "绿松石/翡翠",
    "火": "红玛瑙/石榴石",
    "土": "黄水晶/蜜蜡",
}
NUMBER_LUCKY = {"金": "4,9", "水": "1,6", "木": "3,8", "火": "2,7", "土": "5,0"}
DIET_MAP = {
    "金": "润肺食物（百合/银耳/豆腐）",
    "水": "补肾食物（黑豆/黑芝麻/海参）",
    "木": "养肝食物（菠菜/芹菜/绿豆）",
    "火": "养心食物（红枣/红豆/番茄）",
    "土": "养脾食物（小米/南瓜/黄豆）",
}


def generate_wu_xing_advice(xi_yong: list[str], ji_shen: list[str]) -> dict:
    """§20 五行补充"""
    xi = xi_yong[0] if xi_yong else "土"
    ji = ji_shen[0] if ji_shen else ""

    return {
        "xi_yong_wx": xi,
        "colors": COLOR_MAP.get(xi, "白/蓝"),
        "lucky_numbers": f"{NUMBER_LUCKY.get(xi, '')}（{xi}性数字）",
        "avoid_numbers": f"{NUMBER_LUCKY.get(ji, '')}（{ji}性数字·忌）" if ji else "无特殊禁忌",
        "directions": DIRECTION_MAP_FULL.get(xi, "北"),
        "jewellery": STONE_MAP.get(xi, "白水晶"),
        "diet": DIET_MAP.get(xi, "均衡饮食"),
        "advice": f"喜用{xi}→多接触{COLOR_MAP.get(xi, '')}色物品，{DIRECTION_MAP_FULL.get(xi, '')}方位有利，佩戴{STONE_MAP.get(xi, '')}",
    }


# ════════════════════════════════════════════
# §21 人生建议（结构化·基于实际数据）
# ════════════════════════════════════════════


def generate_life_advice(
    shen_label: str,
    cai_score: float,
    xi_yong: list[str],
    ge_ju_detail: str,
    da_yun_list: list[dict],
    marriage_info: dict,
    career_grade_score: int,
) -> dict:
    """§21 人生建议"""
    xi = xi_yong[0] if xi_yong else "土"
    best_dy = ""
    if da_yun_list:
        best_dy = max(da_yun_list, key=lambda d: d.get("score", 0)).get("gan_zhi", "")

    return {
        "career": {
            "advice": f"深耕专业领域，格局{ge_ju_detail}，选择{xi}行业",
            "grade": career_grade_score,
            "best_da_yun": best_dy,
        },
        "wealth": {
            "advice": f"财星{cai_score}分，{shen_label}，大运窗口期全力积累",
            "strategy": "保守理财" if shen_label == "身弱" else "积极投资",
        },
        "health": {"advice": f"体质{'偏强注意劳逸结合' if shen_label == '身强' else '偏弱注意调养'}"},
        "marriage": {
            "advice": f"婚姻质量{marriage_info.get('quality', '中等') if marriage_info else '中等'}，注意沟通经营"
        },
        "social": {"advice": f"喜用{xi}→多与{xi}五行属性的人合作"},
    }


# ════════════════════════════════════════════
# 综合引擎入口
# ════════════════════════════════════════════


def run_comprehensive_engine(
    bazi: BaZi,
    shen_score: float,
    shen_label: str,
    shen_detail,
    cai_detail,
    ge_ju_main: str,
    ge_ju_detail: str,
    xi_yong: list[str],
    ji_shen: list[str],
    da_yun_list: list[dict],
    da_yun_classified: list[dict],
    best_idx: int,
    worst_idx: int,
    marriage_result: dict,
    education_result: dict,
    birth_year: int = 1980,
    current_year: int = 2026,
) -> dict:
    """
    综合引擎入口 — 对指定八字运行全部21个§的分析
    所有输入均为已计算好的确定性数据
    """

    ri_zhu = bazi.ri_zhu
    all_gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    all_zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]

    # 构造大运列表（含定性标签）
    dy_list_with_score = []
    for i, dy in enumerate(da_yun_list):
        dc = da_yun_classified[i] if i < len(da_yun_classified) else {}
        dy_list_with_score.append(
            {
                "gan": getattr(dy, "gan", ""),
                "zhi": getattr(dy, "zhi", ""),
                "gan_zhi": getattr(dy, "gan_zhi", str(dy)),
                "start_age": getattr(dy, "start_age", 0),
                "end_age": getattr(dy, "end_age", 9),
                "start_year": getattr(dy, "start_year", 0),
                "label": dc.get("label", ""),
                "gan_xi_ji": dc.get("gan_xi_ji", ""),
                "zhi_xi_ji": dc.get("zhi_xi_ji", ""),
            }
        )

    best_dy = dy_list_with_score[best_idx] if best_idx >= 0 and best_idx < len(dy_list_with_score) else {}

    # 事业分析（v3.0完整版 — 财官联动+升官三要素+丢官信号+五行流通+官星合化）
    career = analyze_career_advanced(
        ri_zhu, all_gans, all_zhis, shen_label, shen_score, xi_yong, ji_shen, ge_ju_main, ge_ju_detail,
        cai_xing_total=cai_detail.total,
    )

    # 财富分析（五层动态体系）
    wealth = analyze_wealth_advanced(
        ri_zhu, all_gans, all_zhis, shen_label, shen_score, cai_detail.total, xi_yong, dy_list_with_score
    )

    # 教育分析（九龙道长原始理论 v2.3 — 来自pipeline_v5传入）

    # 食伤评分（引通引用链）
    shi_shang = calc_shi_shang_score(ri_zhu, all_gans, all_zhis)

    # 外貌分析
    appearance = analyze_appearance(ri_zhu, shen_label, shen_score, all_gans, all_zhis, ge_ju_main)

    # 置业分析
    property_analysis = analyze_property(ri_zhu, bazi.day.zhi, xi_yong, dy_list_with_score, best_idx, cai_detail.total, all_zhis)

    # 子女分析（v2完整版 — 十二长生+出生年份推理+父母合参）
    children = analyze_children_advanced(
        ri_zhu, bazi.gender, bazi.hour.gan, bazi.hour.zhi, all_gans, all_zhis,
        da_yun_list=dy_list_with_score, shen_label=shen_label, xi_yong=xi_yong, birth_year=birth_year
    )

    # 健康分析（v2完整版 — 五行过三+七杀断病法+流年预测）
    health = analyze_health_advanced(
        all_gans, all_zhis, ri_zhu, shen_label, shen_score, xi_yong, age=current_year - birth_year
    )

    # 三决断
    career_grade_score = career.get("grade_score", 5)
    verdicts = generate_three_verdicts(
        shen_label, cai_detail.total, ge_ju_detail, best_dy, marriage_result, career_grade_score
    )

    # 运程总评
    dy_curve = generate_da_yun_curve(dy_list_with_score)

    # 五行补充
    wx_advice = generate_wu_xing_advice(xi_yong, ji_shen)

    # 人生建议
    advice = generate_life_advice(
        shen_label, cai_detail.total, xi_yong, ge_ju_detail, dy_list_with_score, marriage_result, career_grade_score
    )

    # 格式映射：v2模块输出 → 21§标准格式
    def _map_children(c):
        return {
            "child_count_estimate": c.get("基础信息", {}).get("子女数量", "1-2个"),
            "windows": [str(w) for w in c.get("生育窗口", {}).get("窗口年份", [])[:3]],
            "child_star": c.get("子女星定位", {}),
            "shi_er_chang_sheng": c.get("十二长生基数", {}),
            "sheng_yu_potential": c.get("时支生育力", ""),
            "child_achievement": c.get("子女成就", "普通"),
            "thin_factors": c.get("缘薄因素", []),
            "child_birth_years": c.get("子女出生年份", []),
            "part_detail": c.get("子女宫", {}).get("时柱", ""),
            "sheng_yu_detail": c.get("生育能力", {}),
        }

    def _map_health(h):
        base = h.get("元数据", {})
        return {
            "constitution": base.get("体质", "中等"),
            "wu_xing_over_three": h.get("五行过三", []),
            "qi_sha_risks": {
                "detail": "; ".join(str(x) for x in h.get("七杀实疾", [])) if h.get("七杀实疾") else "无显著信号"
            },
            "pian_yin_risks": {
                "detail": "; ".join(str(x) for x in h.get("偏印淤堵", [])) if h.get("偏印淤堵") else "无明显淤堵"
            },
            "wu_xing_battles": {
                "detail": "; ".join(str(x) for x in h.get("五行相冲", [])) if h.get("五行相冲") else "无明显交战"
            },
            "protect_years": [str(y) for y in base.get("重点防护年份", [])][:5],
        }

    return {
        "sec_6_career": career,
        "sec_8_wealth_full": wealth,
        "sec_7_appearance": appearance,
        "sec_5_education": education_result,
        "sec_5b_shi_shang": shi_shang,
        "sec_9_property": property_analysis,
        "sec_13_children": _map_children(children),
        "sec_14_health": _map_health(health),
        "sec_18_verdicts": verdicts,
        "sec_19_overall": dy_curve,
        "sec_20_wu_xing_advice": wx_advice,
        "sec_21_advice": advice,
    }
