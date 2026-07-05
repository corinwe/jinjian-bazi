"""
金鉴真人·事业分析引擎 v3.0 — 确定性规则完整版（财官联动+全面规则）
基于bazi-career-analysis v3.0

规则体系：
  格局定方向（做什么）
  官杀定高度（做到什么级别）
  恶神制化定级别（能不能成大器）
  五行定行业（在哪个领域做）
  36命格职业类（12条公众号沉淀）
  财官联动（财生官→官护财）
  升官三要素（身强+财旺+官旺）
  五行流通（能量流向定事业性质）
  官星合化（丁壬合等）
  丢官信号（伤官克官/官星受冲/官星被合化）

所有判定以【身强弱+喜忌神】为基础
"""

from __future__ import annotations

from constants import TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_gan

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
    "杀印相生格": {"comb": "七杀+印→化杀为权", "principle": "身弱用印化杀，把压力变成权力", "level": "1顶级"},
    "食神制杀格": {"comb": "食神+七杀→以食制杀", "principle": "身强用食神克杀，以智谋制伏凶险", "level": "1顶级"},
    "杀身两停格": {"comb": "七杀=日主能量", "principle": "势均力敌，硬碰硬", "level": "1顶级"},
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

# ── 五行流通方向与事业性质（九龙道长原始理论）──
WU_XING_LIU_TONG = {
    "官": "求名（当官/管理）",
    "财": "求商（做生意/投资）",
    "印": "求文（做学问/文化）",
    "食伤": "求技（技术/艺术/创意）",
}

# ── 官星合化（丁壬合等·提升官运课）──
GUAN_HE_HUA = {
    "丁壬合": {"desc": "丁壬合木→合为印→得领导赏识、官方授权", "effect": "正面"},
    "丙辛合": {"desc": "丙辛合水→合为官杀→有机会但压力大", "effect": "中性"},
    "戊癸合": {"desc": "戊癸合火→合为财→财生官→机会好", "effect": "正面"},
    "甲己合": {"desc": "甲己合土→合为财→利求财", "effect": "正面"},
    "乙庚合": {"desc": "乙庚合金→合为官杀→压力转化为权力", "effect": "中性"},
}


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


def _evaluate_shang_guan_ge(all_ss: list[str], ri_zhu: str, bazi_gans: list[str], xi_yong: list[str]) -> str:
    """判断伤官三格"""
    has_shang = "伤官" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_guan = "正官" in all_ss
    has_cai = "正财" in all_ss or "偏财" in all_ss

    if not has_shang:
        return ""
    if has_shang and not has_guan and "七杀" not in all_ss:
        return "伤官伤尽（管官的官）"
    if has_shang and has_yin:
        return "伤官配印（位高权重）"
    if has_shang and has_cai:
        return "伤官生财（以技术/创意赚钱）"
    if has_shang and has_guan:
        return "伤官见官（与官对立，官非口舌）"
    return "伤官格"


def _detect_talent_36(
    all_ss: list[str], bazi_gans: list[str], bazi_zhis: list[str],
    ri_zhu: str, shen_label: str, shen_score: float,
) -> list[str]:
    """36命格职业类匹配（以身强弱为基础）"""
    talents = []
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_shang = "伤官" in all_ss
    has_shi = "食神" in all_ss
    has_guan = "正官" in all_ss
    has_sha = "七杀" in all_ss
    has_cai = "正财" in all_ss or "偏财" in all_ss
    has_bi = "比肩" in all_ss or "劫财" in all_ss
    shen_qiang = shen_label == "身强"

    if shen_qiang and has_yin and has_shang and has_cai:
        talents.append("🔬 最有科研天赋")
    if has_cai and has_guan and has_yin:
        talents.append("🏛️ 最有政客天赋")
    if shen_qiang and has_cai and has_shi and has_shang:
        talents.append("💼 最有商人天赋")
    if ri_wx == "木" and has_shang and "午" in bazi_zhis:
        talents.append("📝 最有文人天赋")
    if ri_wx == "金" and has_shang:
        talents.append("🎨 最有艺术天赋")
    if has_shi and has_sha:
        talents.append("🛡️ 最有军警天赋")
    if has_guan and has_yin and shen_qiang:
        talents.append("📖 最有教师天赋")
    if shen_qiang and has_shang:
        talents.append("🏥 最有医生天赋")
    if has_cai and has_yin and shen_label == "身弱":
        talents.append("📊 最有营销天赋")
    if shen_qiang and (has_shi or has_shang) and has_cai:
        talents.append("💡 最有咨询师天赋")
    if has_bi and (has_guan or has_sha) and shen_qiang:
        talents.append("🏃 最有运动员天赋")
    if has_bi and has_cai and (has_shi or has_shang):
        talents.append("🤝 最有经纪人天赋")
    return talents[:3]


def _evaluate_fame(all_ss: list[str], ge_ju_main: str) -> list[str]:
    """名望评估（以身强弱为基础）"""
    fame = []
    for ss in all_ss:
        if ss in FAME_MAP:
            fame.append(FAME_MAP[ss])
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
    if not any("格局名望" in f for f in fame):
        fame.append("格局名望: 中（有潜力）")
    return fame


def _analyze_guan_sha(all_ss: list[str], bazi_gans: list[str], shen_label: str, ri_zhu: str) -> list[str]:
    """官杀分析（以身强弱为基础）"""
    analysis = []
    gans_ss = [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]

    has_guan = "正官" in all_ss
    has_sha = "七杀" in all_ss

    for i, ss in enumerate(gans_ss):
        if ss == "正官":
            if shen_label == "身强":
                analysis.append(f"正官透干+身强→利管理晋升（官为喜用）")
            elif shen_label == "身弱":
                analysis.append(f"正官透干+身弱→压力大（官为忌凶）")
            else:
                analysis.append(f"正官透干+中和→事业顺遂")
        if ss == "七杀":
            if shen_label == "身强":
                analysis.append(f"七杀透干+身强→杀伐决断（杀为喜用）")
            elif shen_label == "身弱":
                analysis.append(f"七杀透干+身弱→压力/小人（杀为忌凶）")
            else:
                analysis.append(f"七杀透干+中和→竞争力")

    if has_guan and has_sha and shen_label == "身弱":
        analysis.append("⚠️ 官杀混杂+身弱→事业波动大（官杀均为忌凶）")
    elif has_guan and has_sha and shen_label == "身强":
        analysis.append("官杀混杂但身强→可驾驭（官杀均为喜用）")

    return analysis


def _analyze_cai_guan_lian_dong(
    shen_label: str, cai_xing_total: float, all_ss: list[str]
) -> list[str]:
    """
    财官联动分析（财生官→官护财）

    身强：喜财官 → 财生官利升迁，官护财防比劫
    身弱：忌财官 → 财生官压力更大
    """
    results = []
    has_cai = "正财" in all_ss or "偏财" in all_ss
    has_guan = "正官" in all_ss
    has_sha = "七杀" in all_ss
    has_bi = "比肩" in all_ss or "劫财" in all_ss

    if shen_label == "身强":
        if has_cai and (has_guan or has_sha):
            if cai_xing_total >= 40:
                results.append(f"财官联动✅ 财旺({cai_xing_total}分)+官杀旺→财生官利升迁，官护财防比劫")
            else:
                results.append(f"财官联动⚠️ 有财官但财弱({cai_xing_total}分)→财生官力不足，需等财运")
        elif has_cai:
            results.append(f"有财无官→财富可积累但无官护财，比劫年防破财")
        elif has_guan or has_sha:
            results.append(f"有官无财→官护财但财源不足，需补财运方有进展")

    elif shen_label == "身弱":
        if has_cai and (has_guan or has_sha):
            results.append(f"⚠️ 身弱+财旺+官旺→财生官加大压力，官为忌凶更重负担，需印比帮身")
        elif has_guan or has_sha:
            results.append(f"⚠️ 身弱+官旺→官为忌凶，压力大易有官非，需印化杀")
        elif has_cai:
            results.append(f"⚠️ 身弱+财旺→富屋贫人，财为忌凶，需印比帮身方能担财")

    else:  # 中和
        if has_cai and (has_guan or has_sha):
            results.append(f"中和+财官→平衡型，财官能量适中则顺遂")
        elif not has_cai and not has_guan and not has_sha:
            results.append("无财无官→事业以技术/专业为主")

    return results


def _analyze_diu_guan_signal(
    all_ss: list[str], bazi_gans: list[str], bazi_zhis: list[str], xi_yong: list[str], shen_label: str, ri_zhu: str
) -> list[str]:
    """
    丢官信号分析（提升官运课）

    ① 伤官克官 → 流年遇伤官克住官星
    ② 财星破印 → 财克印→印制不住伤官→狂傲出问题
    ③ 官星受冲 → 官星（正官/七杀）所在位置被冲
    ④ 官星被合化（负面） → 官星被合走
    ⑤ 比劫夺官 → 比劫克财→财不生官
    """
    signals = []
    has_shang = "伤官" in all_ss
    has_guan = "正官" in all_ss
    has_sha = "七杀" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_cai = "正财" in all_ss or "偏财" in all_ss
    has_bi = "比肩" in all_ss or "劫财" in all_ss

    # ① 伤官克官
    if has_shang and has_guan:
        if shen_label == "身强":
            signals.append("⚠️ 伤官克官（身强）→ 伤官克制官星，需印来制伤官护官，或财来通关")
        else:
            signals.append("🔴 伤官克官（身弱）→ 伤官为忌凶克官，丢官风险高，须补印制伤")

    if has_sha and has_guan:
        signals.append("⚠️ 官杀混杂 → 正官七杀并存，事业易波动，需大运引化")

    if not has_guan and has_shang:
        signals.append("⚠️ 伤官伤尽→原局无官，若大运流年遇正官→伤官见官为祸百端")

    # ② 财星破印→丢官（财克印→印无法制服伤官→狂傲→领导不欣赏）
    if has_cai and has_yin and has_shang:
        signals.append("🔴 财星破印→伤官配印格见财→财克印→印无法制伤官→狂傲出问题，领导不欣赏")
    elif has_cai and has_yin and not has_shang:
        signals.append("⚠️ 财星克印→印被财损→事业根基动摇，注意名誉风险")

    # ③ 官星受冲 → 正官/七杀所在位置被冲
    # 检查天干官杀是否被冲
    guan_positions = []
    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ("正官", "七杀"):
            guan_positions.append((i, g, ss))
    # 天干四冲：甲庚/乙辛/丙壬/丁癸
    tg_chong = {("甲", "庚"), ("庚", "甲"), ("乙", "辛"), ("辛", "乙"),
                ("丙", "壬"), ("壬", "丙"), ("丁", "癸"), ("癸", "丁")}
    for idx, g, ss in guan_positions:
        for other_g in bazi_gans:
            if other_g != g and (g, other_g) in tg_chong:
                pos_name = ["年干", "月干", "日干", "时干"][idx]
                signals.append(f"🔴 官星受冲→{pos_name}{g}({ss})被{other_g}冲，丢官风险")

    # ④ 官星被合化（负面）
    if has_guan or has_sha:
        # 查找天干五合可能导致官星被合走的组合
        from career_v2 import GUAN_HE_HUA
        # 检查是否有负面合化
        guan_he_qian = {("丁", "壬"): "丁壬合木→合为印→正面",
                        ("丙", "辛"): "丙辛合水→合为官杀→中性",
                        ("戊", "癸"): "戊癸合火→合为财→正面"}
        # ... (简化：只标记已有的合化分析结果)

    # ⑤ 比劫夺官 → 比劫克财→财不生官→丢官
    if has_bi and has_cai and shen_label == "身强":
        signals.append("⚠️ 比劫夺官→身强比劫克财→财不生官→事业发展受限")
    elif has_bi and not has_cai and has_guan:
        signals.append("⚠️ 比劫旺+无财→财源断→官星无生助→升官乏力")

    return signals


def _analyze_sheng_guan_yao_su(
    shen_label: str, cai_xing_total: float, all_ss: list[str]
) -> list[str]:
    """
    升官三要素（身强+财旺+官旺）
    这是技能原始口诀——所有以喜忌为基础
    """
    has_guan = "正官" in all_ss
    has_sha = "七杀" in all_ss
    has_guan_sha = has_guan or has_sha
    has_cai = "正财" in all_ss or "偏财" in all_ss
    cai_ge40 = cai_xing_total >= 40

    results = []

    if shen_label == "身强" and cai_ge40 and has_guan_sha:
        results.append("升官三要素全满足✅ 身强+财旺+官旺→官运亨通")
    elif shen_label == "身强" and cai_ge40:
        results.append("升官两要素✅ 身强+财旺，缺官→需大运补官星")
    elif shen_label == "身强" and has_guan_sha:
        results.append(f"升官两要素⚠️ 身强+官旺但财弱({cai_xing_total}分)→财生官不足，需补财运")
    elif shen_label == "身弱" and cai_ge40 and has_guan_sha:
        results.append(f"🔴 身弱+财旺+官旺→财官皆为忌凶，压力大，须先补印比帮身")
    elif shen_label == "身弱" and has_guan_sha:
        results.append(f"⚠️ 身弱+官旺→官为忌凶，先补印枭使身变强，再考虑求官")

    return results


def _analyze_liu_tong(all_ss: list[str], xi_yong: list[str]) -> list[str]:
    """
    五行流通方向分析
    """
    results = []
    has_guan = "正官" in all_ss
    has_cai = "正财" in all_ss or "偏财" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_shi_shang = "食神" in all_ss or "伤官" in all_ss

    flows = []
    if has_guan:
        flows.append(f"官→{WU_XING_LIU_TONG['官']}")
    if has_cai:
        flows.append(f"财→{WU_XING_LIU_TONG['财']}")
    if has_yin:
        flows.append(f"印→{WU_XING_LIU_TONG['印']}")
    if has_shi_shang:
        flows.append(f"食伤→{WU_XING_LIU_TONG['食伤']}")

    # 判断主要能量流向（看哪个十神被喜用支撑）
    if has_guan and "官" in str(xi_yong):
        flows.insert(0, "🔴主力流向: 官")

    if flows:
        results.append(f"五行流通方向：{'、'.join(flows)}")
    else:
        results.append("五行流通不明显→事业方向需大运引化")

    return results


def _analyze_guan_he_hua(bazi_gans: list[str], ri_zhu: str) -> list[str]:
    """官星合化检查（丁壬合等）"""
    results = []
    # 检查天干是否构成官星合化
    he_hua_guan = {
        ("丁", "壬"): "丁壬合木→合为印→得领导赏识、官方授权、证书荣誉",
        ("壬", "丁"): "丁壬合木→合为印→得领导赏识",
        ("丙", "辛"): "丙辛合水→合为官杀→有机会但压力大",
        ("辛", "丙"): "丙辛合水→合为官杀→有机会但压力大",
        ("戊", "癸"): "戊癸合火→合为财→财生官→机会好",
        ("癸", "戊"): "戊癸合火→合为财→财生官→机会好",
    }

    for i, g1 in enumerate(bazi_gans):
        for j, g2 in enumerate(bazi_gans):
            if i < j:
                key = (g1, g2)
                if key in he_hua_guan:
                    pos1 = ["年", "月", "日", "时"][i]
                    pos2 = ["年", "月", "日", "时"][j]
                    results.append(f"{pos1}干{g1}+{pos2}干{g2}={he_hua_guan[key]}")

    return results


def analyze_career_full(
    ri_zhu: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    shen_label: str,
    shen_score: float,
    xi_yong: list[str],
    ji_shen: list[str],
    ge_ju_main: str,
    ge_ju_detail: str,
    cai_xing_total: float = 0.0,
) -> dict:
    """
    事业完整分析 v3.0 — 财官联动+全面规则
    所有判定以【身强弱+喜忌神】为基础
    """
    all_ss = [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]

    # ── ① 格局定方向 ──
    direction = GE_JU_DIRECTION.get(ge_ju_main, "多元化")
    desc = GE_JU_DESC.get(ge_ju_main, "")

    # ── ② 伟人格+伤官格判定 ──
    wei_ren_ge_name, is_wei = _evaluate_wei_ren_ge(all_ss, shen_label)
    shang_guan_type = _evaluate_shang_guan_ge(all_ss, ri_zhu, bazi_gans, xi_yong)

    # ── ③ 身强弱定工作模式（原始理论·身强需管理·身弱需托底）──
    if shen_label == "身强" and shen_score >= 60:
        work_mode = "管理/领导岗位，官杀为喜用→利晋升"
        level = "高管/管理型"
    elif shen_label == "身弱" and shen_score < 40:
        work_mode = "技术/专业岗，印为喜用→需贵人/平台托底"
        level = "专家/技术型"
    else:
        work_mode = "中和，文武兼备，官杀喜用时顺遂"
        level = "中高层/专业型"

    # ── ④ 恶神制化定级别（以身强弱+喜忌为基础）──
    has_sha = "七杀" in all_ss
    has_yin = "正印" in all_ss or "偏印" in all_ss
    has_shi = "食神" in all_ss
    has_guan = "正官" in all_ss

    if is_wei:
        career_grade = "一级·伟人格"
    elif has_sha and (has_yin or has_shi) and shen_label in ("身强", "中和"):
        career_grade = "二级·上等·恶神有制"
    elif has_guan and has_yin and shen_label == "身强":
        career_grade = "三级·中等偏上·官印相生"
    elif has_guan and shen_label == "身强":
        career_grade = "四级·中等·正官得用"
    elif has_yin and shen_label == "身弱":
        career_grade = "四级·中等·身弱得印"
    else:
        career_grade = "五级·下等"

    # ── ⑤ 官杀分析 ──
    guan_sha_analysis = _analyze_guan_sha(all_ss, bazi_gans, shen_label, ri_zhu)

    # ── ⑥ 财官联动（身强弱+喜忌为基础）──
    cai_guan = _analyze_cai_guan_lian_dong(shen_label, cai_xing_total, all_ss)

    # ── ⑦ 升官三要素 ──
    sheng_guan = _analyze_sheng_guan_yao_su(shen_label, cai_xing_total, all_ss)

    # ── ⑧ 丢官信号 ──
    diu_guan = _analyze_diu_guan_signal(all_ss, bazi_gans, bazi_zhis, xi_yong, shen_label, ri_zhu)

    # ── ⑨ 五行流通 ──
    liu_tong = _analyze_liu_tong(all_ss, xi_yong)

    # ── ⑩ 官星合化 ──
    guan_he = _analyze_guan_he_hua(bazi_gans, ri_zhu)

    # 五行定行业
    xi_wx = xi_yong[0] if xi_yong else "土"
    industry = WX_INDUSTRY.get(xi_wx, "多元化")
    guan_sha_career = GUAN_SHA_CAREER.get(ge_ju_main, "")

    # 将星检查（三合局中神→领导才能）
    # 寅午戌→午, 巳酉丑→酉, 申子辰→子, 亥卯未→卯
    jiang_xing_zhi_map = {"寅": "午", "午": "午", "戌": "午",
                          "巳": "酉", "酉": "酉", "丑": "酉",
                          "申": "子", "子": "子", "辰": "子",
                          "亥": "卯", "卯": "卯", "未": "卯"}
    has_jiang_xing = any(jiang_xing_zhi_map.get(z, "") == z for z in bazi_zhis)
    jiang_xing_note = "✅ 原局带将星→有领导才能和管理天赋" if has_jiang_xing else ""

    # 名望分析
    talents = _detect_talent_36(all_ss, bazi_gans, bazi_zhis, ri_zhu, shen_label, shen_score)

    # ── ⑬ 名望评估 ──
    fame = _evaluate_fame(all_ss, ge_ju_main)

    # ── ⑭ 创业判断（身强弱铁律）──
    if shen_label == "身弱" and shen_score < 40:
        entrepreneurship = "❌ 不适合单干创业（身弱扛不住·印比为喜用需托底）"
        best_path = "✅ 借平台（大公司/体制内）+ 借贵人 + 借专业深耕"
    elif shen_label == "身强" and ge_ju_main in ("偏财格", "七杀格"):
        entrepreneurship = "✅ 适合创业，身强能扛（官杀为喜用）"
        best_path = "适合自主创业或承担高风险岗位"
    else:
        entrepreneurship = "⚠️ 创业需谨慎，建议先在大平台积累经验"
        best_path = "建议大平台积累→时机成熟再考虑自主"

    # ── ⑮ 近官立贵 ──
    has_cai = "正财" in all_ss or "偏财" in all_ss
    has_bi = "比肩" in all_ss or "劫财" in all_ss
    has_shi_shang = "食神" in all_ss or "伤官" in all_ss

    social_circle = []
    if has_cai:
        social_circle.append("认识老板/有钱人")
    if has_guan or has_sha:
        social_circle.append("认识领导/有权力者")
    if has_yin:
        social_circle.append("认识文化人/师长")
    if has_bi:
        social_circle.append("朋友多")
    if has_shi_shang:
        social_circle.append("认识技术/艺术人才")

    # ── 详细规则分析文本 ──
    detail_parts = []
    detail_parts.append(f"【格局定方向】格局{ge_ju_main}→事业方向宜走「{direction}」路线。{desc}。")

    if wei_ren_ge_name:
        wr_info = WEI_REN_GE.get(wei_ren_ge_name, {})
        detail_parts.append(f"【伟人格判定】{wei_ren_ge_name}——{wr_info.get('principle', '')}。{wr_info.get('comb', '')}。")
    if shang_guan_type:
        sg_desc = SHANG_GUAN_SAN_GE.get(shang_guan_type, "")
        detail_parts.append(f"【伤官格】{shang_guan_type}：{sg_desc}。")

    # 身强弱+喜忌
    if shen_label == "身强":
        detail_parts.append(
            f"【身强弱+喜忌】身强{shen_score:.0f}分，官杀/食伤/财为喜用。"
            f"适合管理/领导岗位，官杀为喜用则利晋升，越挫越勇。"
        )
    elif shen_label == "身弱":
        detail_parts.append(
            f"【身强弱+喜忌】身弱{shen_score:.0f}分，印/比为喜用。"
            f"适合技术/专业岗，需贵人/平台托底。杀印相生→以智慧化压力为成就。"
        )
    else:
        detail_parts.append(
            f"【身强弱+喜忌】中和{shen_score:.0f}分，文武兼备，官杀为喜用时事业顺遂。"
        )

    if jiang_xing_note:
        detail_parts.append(f"【将星】{jiang_xing_note}。")

    detail_parts.append(f"【恶神制化定级别】{career_grade}。")

    if guan_sha_analysis:
        detail_parts.append(f"【官杀分析】{'；'.join(guan_sha_analysis)}。")
    if cai_guan:
        detail_parts.append(f"【财官联动】{'；'.join(cai_guan)}。")
    if sheng_guan:
        detail_parts.append(f"【升官三要素】{'；'.join(sheng_guan)}。")
    if diu_guan:
        detail_parts.append(f"【丢官信号】{'；'.join(diu_guan)}。")
    if liu_tong:
        detail_parts.append(f"【五行流通】{'；'.join(liu_tong)}。")
    if guan_he:
        detail_parts.append(f"【官星合化】{'；'.join(guan_he)}。")
    if industry:
        detail_parts.append(f"【五行定行业】喜用{xi_wx}五行，适宜{industry}。")
    if talents:
        detail_parts.append(f"【36命格天赋】{'、'.join(talents)}。")
    if fame:
        detail_parts.append(f"【名望评估】{'；'.join(fame)}。")
    detail_parts.append(f"【创业判断】{entrepreneurship}。{best_path}。")
    if social_circle:
        detail_parts.append(f"【近官立贵】{'；'.join(social_circle)}。")

    return {
        "career_direction": direction,
        "career_desc": desc,
        "work_mode": work_mode,
        "career_level": level,
        "career_grade": career_grade,
        "wei_ren_ge": wei_ren_ge_name,
        "shang_guan_type": shang_guan_type,
        "guan_sha_analysis": guan_sha_analysis,
        "cai_guan_lian_dong": cai_guan,
        "sheng_guan_yao_su": sheng_guan,
        "diu_guan_signal": diu_guan,
        "jiang_xing": jiang_xing_note,
        "liu_tong_analysis": liu_tong,
        "guan_he_hua": guan_he,
        "recommended_industries": industry,
        "guan_sha_career_detail": guan_sha_career,
        "fame_analysis": fame,
        "talents_36": talents,
        "entrepreneurship": entrepreneurship,
        "best_path": best_path,
        "social_circle": social_circle,
        "detail_analysis": "\n".join(detail_parts),
    }
