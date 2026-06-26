"""
金鉴真人·性格分析引擎 v1.0

逻辑链:
  Step 1: 日主五行 → 性格底色
  Step 2: 十神透干 → 核心特质（每个透干十神=一个性格维度）
  Step 3: 身强弱 → 修正（身强自信外放，身弱内敛敏感）
  Step 4: 刑冲合害 → 性格冲突点
  Step 5: 神煞 → 特殊天赋
  综合: 核心价值观 + 性格冲突 + 成长处方
"""

from __future__ import annotations
from constants import TIAN_GAN_WU_XING, DI_ZHI_WU_XING
from shi_shen import get_shi_shen_for_gan


# ── 日主五行性格底色 ──
RI_ZHU_CHARACTER = {
    "甲": {"base": "阳木·参天大树", "traits": ["正直", "进取", "有领导力", "固执"],
           "desc": "性格刚直、有担当，像大树一样顶天立地。目标感强，不轻易低头。"},
    "乙": {"base": "阴木·花草藤蔓", "traits": ["柔韧", "适应力强", "细腻", "固执"],
           "desc": "性格柔韧、善于适应环境，像藤蔓一样能找到生长的路。心思细腻，有艺术气质。"},
    "丙": {"base": "阳火·太阳之火", "traits": ["热情", "开朗", "大方", "急躁"],
           "desc": "性格热情奔放，像太阳一样温暖他人。慷慨大方但有急躁的一面。"},
    "丁": {"base": "阴火·灯烛之火", "traits": ["温和", "细腻", "有修养", "含蓄"],
           "desc": "性格温和内敛，像灯火一样给人温暖。注重细节，有文化和艺术修养。"},
    "戊": {"base": "阳土·高山厚土", "traits": ["稳重", "可靠", "包容", "固执"],
           "desc": "性格稳重可靠，像高山一样值得依靠。包容心强但有固执己见的一面。"},
    "己": {"base": "阴土·田园之土", "traits": ["务实", "细致", "善于理财", "保守"],
           "desc": "性格务实细致，像田园一样滋养万物。善于规划和理财，但偏保守。"},
    "庚": {"base": "阳金·刀剑之金", "traits": ["果断", "刚毅", "有魄力", "锐利"],
           "desc": "性格果断刚毅，像刀剑一样锋利。有魄力和执行力，但容易伤人。"},
    "辛": {"base": "阴金·珠宝之金", "traits": ["精致", "敏感", "优雅", "挑剔"],
           "desc": "性格精致敏感，像珠宝一样需要精心打磨。品味高雅但有时过于挑剔。"},
    "壬": {"base": "阳水·江河之水", "traits": ["智慧", "灵活", "善于变通", "深沉"],
           "desc": "性格智慧灵动，像江河一样奔流不息。思维敏捷善于变通，但难以捉摸。"},
    "癸": {"base": "阴水·雨露之水", "traits": ["聪明", "敏感", "细腻", "内向"],
           "desc": "性格聪明敏感，像雨露一样滋润万物。心思细腻感知力强，偏内向。"},
}


# ── 十神性格特质 ──
SHI_SHEN_CHARACTER = {
    "正印": {"label": "学识型", "traits": ["稳重", "好学", "守规矩", "传统"], "positive": "学习能力强，有文化底蕴", "negative": "过于保守，缺乏突破"},
    "偏印": {"label": "研究型", "traits": ["独特", "深度", "孤僻", "创新"], "positive": "思维独特有深度，擅长研究", "negative": "孤僻不合群，钻牛角尖"},
    "正官": {"label": "规则型", "traits": ["负责", "自律", "守时", "谨慎"], "positive": "责任心强，自律性好", "negative": "过于刻板，缺乏弹性"},
    "七杀": {"label": "权威型", "traits": ["有魄力", "好胜", "强势", "决断"], "positive": "有领袖气质，执行力强", "negative": "霸道专横，容易树敌"},
    "正财": {"label": "务实型", "traits": ["务实", "节俭", "稳重", "顾家"], "positive": "脚踏实地，善于理财", "negative": "过于功利，缺乏浪漫"},
    "偏财": {"label": "社交型", "traits": ["大方", "灵活", "人脉广", "慷慨"], "positive": "社交能力强，人脉广泛", "negative": "花钱大手大脚"},
    "比肩": {"label": "独立型", "traits": ["独立", "自信", "好胜", "自我"], "positive": "独立自主，不依赖他人", "negative": "自我中心，合作能力弱"},
    "劫财": {"label": "竞争型", "traits": ["好强", "竞争", "义气", "冲动"], "positive": "有竞争意识，讲义气", "negative": "冲动易怒，容易破财"},
    "食神": {"label": "享受型", "traits": ["温和", "乐观", "有才艺", "懂生活"], "positive": "心态乐观，有艺术天赋", "negative": "过于安逸，缺乏进取"},
    "伤官": {"label": "才华型", "traits": ["聪明", "有才华", "叛逆", "高傲"], "positive": "才华横溢，创新能力强", "negative": "叛逆高傲，人际关系紧张"},
}


def analyze_character(
    ri_zhu: str,
    bazi_gans: list[str],
    shen_label: str, shen_score: float,
    di_zhi_summary: str,
    shen_sha_summary: str,
) -> dict:
    """
    完整性格分析
    """
    # ── Step 1: 日主底色 ──
    ri_char = RI_ZHU_CHARACTER.get(ri_zhu, {})
    base_desc = ri_char.get("desc", "")
    base_traits = ri_char.get("traits", [])
    
    # ── Step 2: 十神特质 ──
    shi_shen_traits = []
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        ss_info = SHI_SHEN_CHARACTER.get(ss, {})
        if ss_info:
            shi_shen_traits.append({
                "ten_god": ss,
                "label": ss_info.get("label", ""),
                "traits": ss_info.get("traits", []),
                "positive": ss_info.get("positive", ""),
                "negative": ss_info.get("negative", ""),
            })
    
    # ── Step 3: 身强弱修正 ──
    if shen_label == "身强":
        base_traits.append("自信外放")
        base_traits.append("能量充沛")
    elif shen_label == "身弱":
        base_traits.append("内敛敏感")
        base_traits.append("心思细腻")
    
    # ── Step 4: 性格冲突 ──
    conflicts = []
    ss_labels = [s["label"] for s in shi_shen_traits]
    if "规则型" in ss_labels and "叛逆型" in ss_labels:
        conflicts.append("内心有规则与叛逆的冲突")
    if "权威型" in ss_labels and "享受型" in ss_labels:
        conflicts.append("强势与安逸的矛盾")
    if "开拓型" in ss_labels and "保守型" in ss_labels:
        conflicts.append("进取与守成的拉锯")
    
    if "冲" in di_zhi_summary:
        conflicts.append("地支多冲→性格波动大，内心矛盾多")
    if "三刑" in di_zhi_summary:
        conflicts.append("地支三刑→内在压力大，容易自我消耗")
    
    # ── Step 5: 天赋 ──
    talents = []
    if "文昌" in shen_sha_summary:
        talents.append("🌟 文昌 → 学业/文化天赋")
    if "桃花" in shen_sha_summary:
        talents.append("🌸 桃花 → 人缘/艺术天赋")
    if "驿马" in shen_sha_summary:
        talents.append("🏃 驿马 → 行动/外交天赋")
    if "华盖" in shen_sha_summary:
        talents.append("🎭 华盖 → 玄学/艺术天赋")
    if "天乙" in shen_sha_summary:
        talents.append("🛡️ 天乙 → 贵人/机遇天赋")
    
    # ── 综合 ──
    personality_type = ", ".join(list(set([s["label"] for s in shi_shen_traits] + [ri_char.get("base", "")]))[:4])
    
    return {
        "ri_zhu_base": {"gan": ri_zhu, "base": ri_char.get("base", ""), "desc": base_desc},
        "personality_type": personality_type,
        "key_traits": list(set(base_traits)),
        "shi_shen_traits": shi_shen_traits,
        "conflicts": conflicts if conflicts else ["无明显性格冲突"],
        "talents": talents if talents else ["无明显特殊天赋"],
        "growth_advice": _generate_advice(shen_label, shi_shen_traits, conflicts),
    }


def _generate_advice(shen_label: str, traits: list, conflicts: list) -> str:
    """生成成长建议"""
    advice_parts = []
    
    if shen_label == "身弱":
        advice_parts.append("增强自信和行动力，不要过度思虑")
    else:
        advice_parts.append("发挥领导力，注意倾听他人意见")
    
    for t in traits:
        if "伤官" in t.get("ten_god", ""):
            advice_parts.append("发挥才华但注意收敛锋芒")
        if "七杀" in t.get("ten_god", ""):
            advice_parts.append("用印星化解压力，不要硬扛")
        if "正印" in t.get("ten_god", ""):
            advice_parts.append("持续学习是最好的成长路径")
    
    if conflicts:
        advice_parts.append("学会接纳自己的矛盾面，那正是你的独特之处")
    
    return "。".join(advice_parts)


if __name__ == "__main__":
    # 测试
    result = analyze_character(
        "甲", ["庚", "辛", "甲", "丙"], "身弱", 12.0,
        "冲: 申寅冲 | 刑: 寅巳申三刑",
        "文昌: 甲→巳 | 天乙: 甲→丑,甲→未"
    )
    print(f"性格类型: {result['personality_type']}")
    print(f"关键特质: {result['key_traits']}")
    print(f"天赋: {result['talents']}")
    print(f"冲突: {result['conflicts']}")
    print(f"建议: {result['growth_advice']}")
