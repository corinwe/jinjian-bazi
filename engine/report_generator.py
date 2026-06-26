"""
金鉴真人·命理报告生成器 v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
将21§结构化数据 → 流畅的八字命理报告
每个断语都有数据支撑，零幻觉，像真人命理师写的
"""

from __future__ import annotations
from typing import Any


# ── 日主五行性格基调 ──
RI_ZHU_NATURE = {
    "甲": {"name": "甲木", "trait": "正直担当，有领导力", "style": "参天大树，顶天立地"},
    "乙": {"name": "乙木", "trait": "柔韧灵活，善于变通", "style": "藤萝花草，以柔克刚"},
    "丙": {"name": "丙火", "trait": "热情开朗，光明磊落", "style": "太阳之火，普照万物"},
    "丁": {"name": "丁火", "trait": "温文尔雅，心思细腻", "style": "灯烛之火，温暖内敛"},
    "戊": {"name": "戊土", "trait": "稳重诚信，厚德载物", "style": "泰山之土，稳如磐石"},
    "己": {"name": "己土", "trait": "包容柔和，善解人意", "style": "田园之土，滋养万物"},
    "庚": {"name": "庚金", "trait": "刚毅果断，锐意进取", "style": "刀剑之金，锋芒毕露"},
    "辛": {"name": "辛金", "trait": "精致优雅，注重品质", "style": "珠玉之金，温润有华"},
    "壬": {"name": "壬水", "trait": "智慧灵动，包容万象", "style": "江河之水，奔流不息"},
    "癸": {"name": "癸水", "trait": "含蓄深沉，谋定后动", "style": "雨露之水，润物无声"},
}

# ── 格局详解 ──
GE_JU_DESC = {
    "正官格": "命带正官，为人正直守信，有管理才能，适合体制内发展的路线",
    "七杀格": "命带七杀，魄力非凡，有闯劲，适合高压环境或创业打拼",
    "正财格": "命带正财，求财踏实稳重，适合稳定收入型工作",
    "偏财格": "命带偏财，财路宽广灵活，商业嗅觉敏锐，适合经商",
    "正印格": "命带正印，学识渊博，有贵人运，适合文职/教育/文化行业",
    "偏印格": "命带偏印，思维独特，有冷门专长，适合技术研究/分析师",
    "食神格": "命带食神，心态好福气厚，适合文艺/餐饮/享受型行业",
    "伤官格": "命带伤官，才华横溢有灵气，适合创意/演艺/技术型工作",
}


def _xi_yong_to_text(xi: list, ji: list) -> str:
    """喜用神文字描述"""
    wx_names = {"金": "金", "木": "木", "水": "水", "火": "火", "土": "土"}
    xi_str = "、".join(xi) if xi else "（未明确）"
    ji_str = "、".join(ji) if ji else "（未明确）"
    return f"喜用{xi_str}五行，忌{ji_str}"


def _shen_qiang_ruo_to_text(label: str, score: float) -> str:
    """身强弱文字描述"""
    if label == "从弱":
        return f"格局为从弱格（{score}分），全局能量高度集中，非常人能驾驭。"
    if label == "身强" and score >= 70:
        return f"身强偏旺（{score}分），体质强健，能扛压力，有担当大事的底子。"
    if label == "身强":
        return f"身强（{score}分），根基扎实，有一定的抗压能力和事业基础。"
    if score < 20:
        return f"身弱（{score}分），体质偏弱，宜借平台和贵人发力，不宜单打独斗。"
    return f"身弱（{score}分），能量集中于一点，适合深耕专长领域。"


def _wealth_to_text(cai_score: float, level: str, cai_ku: dict) -> str:
    """财富文字描述"""
    ku_info = ""
    if cai_ku and cai_ku.get("has"):
        ku_info = f"命带财库（{','.join(cai_ku['zhi'])}），有储蓄和积累财富的能力。"
    else:
        ku_info = "命无明现财库，财富宜流转变现而非积存。"
    
    level_desc = {
        "巨富": "格局极高，有亿万级别的财富潜力",
        "大富": "财富层次高，可达数亿级别",
        "中富": "中富之命，财富可达千万级别",
        "小富": "小富之命，小康以上水平",
        "贫穷": "需大运配合方可聚财",
    }
    desc = level_desc.get(level, "中等财富格局")
    
    return f"财星{cai_score}分，属{level}层次。{desc}。{ku_info}"


def _career_to_text(s10: dict) -> str:
    """事业文字描述"""
    if not s10:
        return ""
    direction = s10.get("career_direction", "")
    grade = s10.get("career_grade", "")
    industry = s10.get("recommended_industries", "")
    ent = s10.get("entrepreneurship", "")
    best = s10.get("best_path", "")
    
    lines = []
    if direction:
        lines.append(f"事业方向宜走{direction}路线。")
    if grade:
        lines.append(f"事业等级{grade}。")
    if industry:
        lines.append(f"五行定行业，适宜从事{industry}等相关领域。")
    if ent:
        lines.append(ent)
    if best:
        lines.append(best)
    return "".join(lines)


def _education_to_text(s11: dict) -> str:
    """学历文字描述"""
    if not s11:
        return ""
    display = s11.get("display", "")
    ypc = s11.get("year_pillar_check", {})
    nc = s11.get("nian_gan_check", {})
    
    parts = []
    if display:
        parts.append(f"学业层次：{display}。")
    if isinstance(ypc, dict) and ypc.get("detail"):
        parts.append(f"年柱分析：{ypc['detail']}。")
    if isinstance(nc, dict) and nc.get("shi_shen"):
        ss = nc["shi_shen"]
        if ss == "伤官":
            parts.append("年干带伤官，少年时期或有叛逆倾向，需正确引导。")
        elif ss in ("正印", "偏印"):
            parts.append("年干见印星，有学业基因，从小就展现出学习天赋。")
    sc = s11.get("wen_chang_ming_li", {})
    if isinstance(sc, dict) and sc.get("has"):
        parts.append(f"文昌入命，有学术或文化方面的天赋。")
    return "".join(parts)


def _marriage_to_text(s12: dict, gender: str) -> str:
    """婚姻文字描述"""
    if not s12:
        return ""
    quality = s12.get("quality", "")
    score = s12.get("quality_score", "")
    window = s12.get("best_window_age", "")
    trait = s12.get("spouse_trait", "")
    
    lines = []
    if quality:
        lines.append(f"婚姻质量{quality}（{score}/10分）。")
    if window:
        lines.append(f"最佳婚恋窗口在{window}。")
    if trait:
        lines.append(f"配偶特征：{trait}。")
    
    # 夫妻宫判断
    gong = s12.get("fu_fu_gong", "")
    if gong:
        lines.append(f"夫妻宫{gong}。")
    
    return "".join(lines)


def _children_to_text(s13: dict) -> str:
    """子女文字描述"""
    if not s13:
        return ""
    count = s13.get("child_count_estimate", "")
    achievement = s13.get("child_achievement", "")
    sheng_yu = s13.get("sheng_yu_potential", "")
    thin = s13.get("thin_factors", [])
    
    lines = []
    # child_count_estimate可能是dict
    if isinstance(count, dict):
        count_str = str(count.get("text", count.get("数量", list(count.values())[0] if count else "")))
    else:
        count_str = str(count)
    
    if count_str:
        lines.append(f"子女方面，约{count_str}。")
    
    if achievement:
        lines.append(f"子女成就趋势：{achievement}。")
    
    # sheng_yu_potential可能是dict
    if isinstance(sheng_yu, dict):
        sheng_yu_str = str(sheng_yu.get("desc", sheng_yu.get("text", "")))
    else:
        sheng_yu_str = str(sheng_yu)
    if sheng_yu_str and sheng_yu_str != "":
        lines.append(sheng_yu_str)
    
    if thin and isinstance(thin, list):
        thin_strs = []
        for t in thin[:2]:
            if isinstance(t, dict):
                thin_strs.append(str(t.get("text", t.get("desc", list(t.values())[0] if t else ""))))
            else:
                thin_strs.append(str(t))
        if thin_strs:
            lines.append(f"注意：{'。'.join(thin_strs)}")
    return "".join(lines)


def _health_to_text(s14: dict) -> str:
    """健康文字描述"""
    if not s14:
        return ""
    constitution = s14.get("constitution", "")
    over_three = s14.get("wu_xing_over_three", [])
    battles = s14.get("wu_xing_battles", [])
    
    lines = []
    if constitution:
        lines.append(f"体质方面：{constitution}。")
    if over_three and isinstance(over_three, list):
        for item in over_three[:2]:
            if isinstance(item, dict):
                wx = item.get("wx", "")
                organ = item.get("organ", "")
                if wx and organ:
                    lines.append(f"注意{wx}五行过旺，对应{organ}需要留意保养。")
    if battles and isinstance(battles, list):
        for b in battles[:2]:
            if isinstance(b, dict):
                disease = b.get("disease", "")
                if disease:
                    lines.append(f"地支冲克提示：{disease}。")
    return "".join(lines)


def _verdicts_to_text(s18: list) -> str:
    """三决断文字描述"""
    if not s18 or not isinstance(s18, list):
        return ""
    lines = []
    for v in s18[:3]:
        if isinstance(v, dict):
            title = v.get("title", "")
            event = v.get("event", "")
            if title and event:
                lines.append(f"【{title}】{event}")
    return "\n".join(lines)


def _da_yun_to_text(s17: dict) -> str:
    """大运走势文字描述"""
    dy_list = s17.get("list", [])
    if not dy_list:
        return ""
    
    best_idx = s17.get("best_idx", -1)
    worst_idx = s17.get("worst_idx", -1)
    
    lines = []
    lines.append(f"命主共{len(dy_list)}步大运：")
    
    for i, dy in enumerate(dy_list):
        gz = dy.get("gan_zhi", "")
        start = dy.get("start_age", "")
        end = dy.get("end_age", "")
        score = dy.get("score", 0)
        
        # 评分定性
        if score >= 8:
            tag = "🏆 上佳"
        elif score >= 6:
            tag = "✅ 顺利"
        elif score >= 4:
            tag = "⚠️ 平运"
        else:
            tag = "❌ 低谷"
        
        lines.append(f"  · {gz}运（{start}~{end}岁）— {tag}（{score}分）")
    
    if best_idx >= 0 and best_idx < len(dy_list):
        best = dy_list[best_idx]
        lines.append(f"一生最佳运在{best.get('gan_zhi','')}运（{best.get('start_age','')}~{best.get('end_age','')}岁），宜全力把握。")
    
    return "\n".join(lines)


def _wu_xing_advice_to_text(s20: dict) -> str:
    """五行开运建议"""
    if not s20:
        return ""
    colors = s20.get("colors", "")
    directions = s20.get("directions", "")
    jewellery = s20.get("jewellery", "")
    diet = s20.get("diet", "")
    advice = s20.get("advice", "")
    
    lines = []
    if colors:
        lines.append(f"【颜色】宜多用{colors}色系。")
    if directions:
        lines.append(f"【方位】宜选{directions}方向。")
    if jewellery:
        lines.append(f"【饰品】宜佩戴{jewellery}。")
    if diet:
        lines.append(f"【饮食】{diet}。")
    if advice:
        lines.append(advice)
    return "\n".join(lines)


def generate_report(result: dict, name: str = "", gender: str = "") -> str:
    """
    生成完整命理报告 —— 将21§结构化数据转为流畅的命理文章
    
    result: engine返回的result字典
    name: 姓名
    gender: 性别
    """
    s1 = result.get("sec_1_overview", {})
    s3 = result.get("sec_3_shen_qiang_ruo", {})
    s4 = result.get("sec_4_xi_yong", {})
    s8 = result.get("sec_8_wealth", {})
    s10 = result.get("sec_10_career", {})
    s11 = result.get("sec_11_education", {})
    s12 = result.get("sec_12_marriage", {})
    s13 = result.get("sec_13_children", {})
    s14 = result.get("sec_14_health", {})
    s17 = result.get("sec_17_da_yun_detail", {})
    s18 = result.get("sec_18_verdicts", [])
    s20 = result.get("sec_20_wu_xing_advice", {})
    
    bazi = s1.get("bazi", "")
    ri_zhu_gan = ""
    ri_zhu_wx = ""
    if isinstance(s1.get("ri_zhu"), dict):
        ri_zhu_gan = s1["ri_zhu"].get("gan", "")
        ri_zhu_wx = s1["ri_zhu"].get("wx", "")
    
    ri_nature = RI_ZHU_NATURE.get(ri_zhu_gan, {})
    ge_ju_detail = (result.get("sec_2_ge_ju") or {}).get("detail", "")
    
    # ── 开始生成 ──
    parts = []
    
    # 标题
    display_name = name or "命主"
    parts.append(f"# {display_name} 八字命理报告")
    parts.append("")
    
    # ═══════════════════════ §1 一页总览 ═══════════════════════
    parts.append("## 一、一页总览")
    parts.append("")
    parts.append(f"八字：{bazi}")
    parts.append(f"日主：{ri_zhu_gan}（{ri_zhu_wx}五行）")
    parts.append("")
    if ri_nature:
        parts.append(f"日主{ri_nature.get('name','')}，性格{ri_nature.get('trait','')}，犹如{ri_nature.get('style','')}。")
    
    sqr_label = s3.get("label", "")
    sqr_score = s3.get("score", 0)
    parts.append(_shen_qiang_ruo_to_text(sqr_label, sqr_score))
    
    if ge_ju_detail:
        ge_desc = GE_JU_DESC.get(ge_ju_detail.split("格")[0] + "格" if "格" in ge_ju_detail else ge_ju_detail, "")
        parts.append(f"格局{ge_ju_detail}。{ge_desc}" if ge_desc else f"格局{ge_ju_detail}。")
    
    xi = s4.get("xi", [])
    ji = s4.get("ji", [])
    parts.append(_xi_yong_to_text(xi, ji) + "。")
    parts.append("")
    
    # ═══════════════════════ §8 财富 ═══════════════════════
    parts.append("## 二、财富格局")
    parts.append("")
    cai_score = s8.get("cai_xing_total", 0)
    level = s8.get("wealth_level", "")
    cai_ku = s8.get("cai_ku", {})
    parts.append(_wealth_to_text(cai_score, level, cai_ku))
    parts.append("")
    
    # ═══════════════════════ §10 事业 ═══════════════════════
    parts.append("## 三、事业发展")
    parts.append("")
    career_text = _career_to_text(s10)
    parts.append(career_text if career_text else "事业格局需结合具体大运流年综合判断。")
    parts.append("")
    
    # ═══════════════════════ §11 学历 ═══════════════════════
    parts.append("## 四、学业学历")
    parts.append("")
    edu_text = _education_to_text(s11)
    parts.append(edu_text if edu_text else "学业方面需结合早年大运流年判断。")
    parts.append("")
    
    # ═══════════════════════ §12 婚姻 ═══════════════════════
    parts.append("## 五、婚姻感情")
    parts.append("")
    mar_text = _marriage_to_text(s12, gender)
    parts.append(mar_text if mar_text else "婚姻方面需结合具体大运流年引动。")
    parts.append("")
    
    # ═══════════════════════ §13 子女 ═══════════════════════
    parts.append("## 六、子女运势")
    parts.append("")
    child_text = _children_to_text(s13)
    parts.append(child_text if child_text else "子女方面常规配置，平顺发展。")
    parts.append("")
    
    # ═══════════════════════ §14 健康 ═══════════════════════
    parts.append("## 七、健康注意")
    parts.append("")
    health_text = _health_to_text(s14)
    parts.append(health_text if health_text else "体质中等，注意日常调养即可。")
    parts.append("")
    
    # ═══════════════════════ §17 大运 ═══════════════════════
    parts.append("## 八、大运走势")
    parts.append("")
    parts.append(_da_yun_to_text(s17))
    parts.append("")
    
    # ═══════════════════════ §18 三决断 ═══════════════════════
    verdict_text = _verdicts_to_text(s18)
    if verdict_text:
        parts.append("## 九、人生三决断")
        parts.append("")
        parts.append(verdict_text)
        parts.append("")
    
    # ═══════════════════════ §20 五行开运 ═══════════════════════
    parts.append("## 十、五行开运建议")
    parts.append("")
    parts.append(_wu_xing_advice_to_text(s20))
    parts.append("")
    
    # 结语
    parts.append("---")
    parts.append("金鉴真人 · 八字命理分析 | 确定性规则引擎 v5.0")
    parts.append("本报告基于确定性规则计算生成，仅供参考。命理是概率，不是宿命。")
    
    return "\n".join(parts)
