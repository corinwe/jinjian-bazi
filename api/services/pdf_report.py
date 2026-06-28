"""金鉴真人·PDF报告生成器 v1.0 — 真正的文本PDF，不是截图"""

from fpdf import FPDF

# ── 字体 ──
FONT_REGULAR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

# ── 颜色方案 ──
C_GOLD = (201, 168, 76)
C_DARK = (30, 30, 46)
C_TEXT = (60, 60, 80)
C_MUTED = (140, 130, 120)
C_BG = (245, 244, 240)
C_WHITE = (255, 255, 255)


class JinjianPDF(FPDF):
    """金鉴真人·PDF报告类"""

    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("CJK", "", FONT_REGULAR)
        self.add_font("CJK", "B", FONT_BOLD)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # 页眉仅在首页不显示，其他页显示简洁页码信息
        pass

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("CJK", "", 7)
            self.set_text_color(*C_MUTED)
            self.cell(0, 10, f"第 {self.page_no()} 页", align="C")

    # ── 章节标题 ──
    def chapter_title(self, title):
        self.set_font("CJK", "B", 14)
        self.set_text_color(*C_GOLD)
        self.cell(0, 8, _clean_emoji(title))
        self.ln(3)
        # 下划线
        self.set_draw_color(*C_GOLD)
        self.set_line_width(0.3)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(5)

    def sub_title(self, title):
        self.set_font("CJK", "B", 11)
        self.set_text_color(*C_DARK)
        self.cell(0, 6, _clean_emoji(title))
        self.ln(5)

    def body_text(self, text, indent=0):
        self.set_font("CJK", "", 9)
        self.set_text_color(*C_TEXT)
        if indent:
            self.cell(indent, 0, "")
        self.multi_cell(0, 5, _clean_emoji(str(text)))
        self.ln(1)

    def key_value(self, key, value):
        """如：学历：本科"""
        self.set_font("CJK", "B", 9)
        self.set_text_color(*C_DARK)
        kw = self.get_string_width(_clean_emoji(key + "：")) + 2
        self.cell(kw, 5, _clean_emoji(key + "："))
        self.set_font("CJK", "", 9)
        self.set_text_color(*C_TEXT)
        self.multi_cell(0, 5, _clean_emoji(str(value)))
        self.ln(0.5)

    def score_bar(self, label, score, max_score=10):
        """如：身强弱 ████████░░ 8.0/10"""
        self.set_font("CJK", "", 9)
        self.set_text_color(*C_DARK)
        lw = 25
        self.cell(lw, 5, _clean_emoji(label))
        bar_len = 50
        fill = int(score / max_score * bar_len)
        bar = "█" * fill + "░" * (bar_len - fill)
        self.set_text_color(*C_GOLD)
        self.cell(52, 5, bar)
        self.set_text_color(*C_MUTED)
        self.cell(0, 5, f"{score:.1f}/10", align="R")
        self.ln(5.5)


# ── 评分转文字 ──
def _score_label(s):
    if s >= 8:
        return "极佳"
    if s >= 6:
        return "良好"
    if s >= 4:
        return "中等"
    return "偏弱"


def _clean_emoji(text):
    """清除字符串中的emoji符号（PDF字体不支持）"""
    import re

    # 只匹配已知emoji范围，不触及CJK汉字(U+4E00-U+9FFF)
    emoji_pat = re.compile(
        "[\U0001f300-\U0001f9ff"  # 杂项符号和图形
        "\U0001fa00-\U0001fa6f"  # 国际象棋符号
        "\U0001fa70-\U0001faff"  # 扩展图形
        "\u2600-\u26ff"  # 杂项符号（不含CJK冲突）
        "\u2702-\u27b0"  # 印刷符号
        "\u24c2-\u24ff"  # 包围字母数字（仅包围字母段）
        "\U0001f1e0-\U0001f1ff"  # 区域指示符
        "\ufe00-\ufe0f"  # 变体选择符
        "\u2726\u2705\u274c\u2b50"  # 个别符号
        "]+",
        re.UNICODE,
    )
    return emoji_pat.sub("", text)


# ═══════════════════════════════════════════
# 各章节叙事函数 — 把字段数据合并为连贯段落
# ═══════════════════════════════════════════


def _narrative_overview(sec, r, a):
    """一、一页总览"""
    s3 = r.get("sec_3_shen_qiang_ruo", a.get("shen_qiang_ruo", {}))
    s2 = r.get("sec_2_ge_ju", a.get("ge_ju", {}))
    s4 = r.get("sec_4_xi_yong", a.get("xi_yong_shen", {}))
    s8 = r.get("sec_8_wealth", {})

    label = s3.get("label", "")
    score = s3.get("score", 0)
    geju = s2.get("detail", "")
    xi = "、".join(s4.get("xi", a.get("xi_yong_shen", {}).get("xi", [])))
    ji = "、".join(s4.get("ji", a.get("xi_yong_shen", {}).get("ji", [])))
    cai = s8.get("cai_xing_total", a.get("cai_xing", {}).get("total", 0))
    wealth = s8.get("wealth_level", "")
    tiaohou = s4.get("tiao_hou", a.get("xi_yong_shen", {}).get("tiao_hou", ""))

    paras = []
    status = "偏旺" if label == "身强" and score >= 70 else label
    paras.append(f"命局为{status}格（{score}分）。")
    if geju:
        paras.append(f"格局为{geju}，为命局之纲领，主宰人生大方向。")
    if xi:
        paras.append(f"喜用神为{xi}，此乃命局平衡之关键，补之则运势顺遂。忌神为{ji}，宜避让。")
    else:
        paras.append(f"忌神为{ji}，宜避让。")
    if tiaohou:
        clean_th = str(tiaohou).replace("['", "").replace("']", "").replace("'", "").replace('"', "")
        paras.append(f"调候用神为{clean_th}，调候为先，补足寒暖燥湿之偏。")
    if cai:
        paras.append(f"财星{cai}分，属{wealth}层次。")
    return paras


def _narrative_ge_ju(sec, r, a):
    """二、格局分析"""
    detail = sec.get("detail", a.get("ge_ju", {}).get("detail", ""))
    desc = sec.get("description", "")

    geju_map = {
        "正官格": "正官格者，为人正直，有管理才能，宜走体制内或大型企业路线。",
        "七杀格": "七杀格者，魄力非凡，敢于决断，适合军警、管理、创业等充满挑战的领域。",
        "正财格": "正财格者，求财踏实，步步为营，宜稳定收入型职业。",
        "偏财格": "偏财格者，财路宽广，善于投资，有经商天赋。",
        "正印格": "正印格者，学识渊博，有贵人运，宜文职、教育、研究等。",
        "偏印格": "偏印格者，思维独特，有冷门专长，适合技术研发、玄学艺术等。",
        "食神格": "食神格者，心态好，福气厚，适合创意、餐饮、娱乐等行业。",
        "伤官格": "伤官格者，才华横溢，灵气逼人，宜发挥创造力。",
    }

    paras = []
    if detail:
        paras.append(f"核心格局为{detail}。")
        paras.append(geju_map.get(detail, "格局结构清晰，为命局之主框架。"))
    if desc:
        paras.append(desc)
    return paras if paras else ["格局分析数据详见核心指标。"]


def _narrative_shen_qiang_ruo(sec, r, a):
    """三、身强弱判定"""
    label = sec.get("label", "")
    score = sec.get("score", 0)
    detail_text = sec.get("detail", a.get("shen_qiang_ruo", {}).get("detail", ""))

    paras = []
    if label == "从弱":
        paras.append(
            f"命局为特殊格局——从弱格（{score}分）。全局能量高度集中，弃命相从，非常人能驾驭。此类格局往往出非凡人物，但须顺势而为，不可逆势强求。"
        )
    elif label == "身强" and score >= 70:
        paras.append(
            f"命局身强偏旺（{score}分）。体质强健，精力充沛，能扛压力，有担当大事的能量底子。但过刚易折，宜用克泄耗（财官食伤）来平衡全局。"
        )
    elif label == "身强":
        paras.append(
            f"命局身强（{score}分）。根基扎实，有一定的抗压能力和事业基础。适合在压力环境中成长，不宜过于安逸。"
        )
    elif label == "身弱":
        paras.append(
            f"命局身弱（{score}分）。能量内敛，宜借平台和贵人发力。适合在大平台、大机构中发展，借团队之力成就事业，不宜单打独斗。"
        )
    else:
        paras.append(f"命局中和（{score}分）。五行相对平衡，适应力强，喜忌随大运灵活变化。")

    if detail_text:
        clean = detail_text.replace("【金鉴真人·身强弱规则·月令本气印=40分·比劫全算】", "")
        if len(clean) > 10:
            paras.append(clean)
    return paras


def _narrative_xi_yong(sec, r, a):
    """四、喜用神与忌神"""
    xi = sec.get("xi", a.get("xi_yong_shen", {}).get("xi", []))
    ji = sec.get("ji", a.get("xi_yong_shen", {}).get("ji", []))
    tiaohou = sec.get("tiao_hou", a.get("xi_yong_shen", {}).get("tiao_hou", ""))

    paras = []
    if xi:
        paras.append(
            f"喜用神为{'、'.join(xi)}。喜用神是命局最需要的五行能量，代表贵人、机遇和顺境。在事业选择、方位朝向、颜色搭配上，应优先选择喜用神对应的元素。"
        )
    else:
        paras.append("命局中和，喜忌随大运灵活变化。")
    if ji:
        paras.append(
            f"忌神为{'、'.join(ji)}。忌神是命局过旺的五行，代表阻力、消耗和逆境。在重大决策时应尽量避开忌神所对应的领域和方向。"
        )
    if tiaohou:
        clean_th = str(tiaohou).replace("['", "").replace("']", "").replace("'", "").replace('"', "")
        paras.append(f"调候用神为{clean_th}。调候为先，寒暖燥湿之偏会影响命局的整体质量，补足调候则运势更为顺遂。")
    return paras


def _narrative_zai_huo(sec, r, a):
    """五、灾祸预警与化解"""
    risk = sec.get("misfortune_full", {}).get("risk_level", "低")
    chong = sec.get("shen_sha_chong", [])
    xing = sec.get("shen_sha_xing", [])
    hai = sec.get("shen_sha_hai", [])
    advice = sec.get("remission_advice", {}).get("advice", "")

    paras = [f"风险评级为{risk}。"]
    issues = []
    if chong:
        issues.append(f"地支相冲：{'、'.join(chong)}。冲则动，逢冲之年多有变动、搬迁、换工作或关系变化。")
    if xing:
        issues.append(f"地支相刑：{'、'.join(xing)}。刑则伤，逢刑之年人际易有摩擦，需注意口舌是非。")
    if hai:
        issues.append(f"地支相害：{'、'.join(hai)}。害则损，需防小人暗算，合作签约需谨慎。")
    if issues:
        paras.extend(issues)
    if advice:
        clean = advice.replace("喜用", "建议")
        paras.append(f"化解建议：{clean}。")
    return paras


def _narrative_character(sec, r, a):
    """六、性格解析"""
    ri_zhu = sec.get("ri_zhu_base", a.get("character", {}).get("ri_zhu_base", ""))
    ptype = sec.get("personality_type", "")
    traits = sec.get("key_traits", [])
    talents = sec.get("talents", [])

    # 从detail_analysis提取更多内容
    detail = sec.get("detail_analysis", a.get("character", {}).get("detail_analysis", ""))
    paras = []

    # 优先用detail_analysis
    if detail:
        # 去掉JSON格式
        clean = detail.replace("'", "").replace('"', "")
        for line in clean.split("\n"):
            line = line.strip()
            if line and len(line) > 10:
                paras.append(line)
        if paras:
            return paras[:5]  # 增加到5行

    if ri_zhu:
        paras.append(f"日主特质：{ri_zhu}。")
    if ptype:
        paras.append(f"性格类型倾向于{ptype}。")
    if traits:
        paras.append(f"关键特质为{'、'.join(traits)}。")
    if talents:
        paras.append(f"天赋潜能包括{'、'.join(talents)}，可在相关领域着重培养和发展。")
    return paras if paras else ["性格数据详见核心指标。"]


def _narrative_appearance(sec, r, a):
    """七、身材外貌"""
    base = sec.get("ri_zhu_appearance", "")
    build = sec.get("build", "")
    height = sec.get("height_estimate", "")
    style = sec.get("style", "")
    weight = sec.get("weight_tendency", "")

    paras = []
    if base:
        paras.append(f"基本特征：{base}。")
    parts = [s for s in [build, height] if s]
    if parts:
        paras.append("体型身高：" + "，".join(parts) + "。")
    if style:
        paras.append(f"气质风格偏向{style}。")
    if weight:
        clean = weight.replace("【金鉴真人·外貌规则·食神=胖·伤官=瘦】", "")
        paras.append(f"体重倾向：{clean}。")
    return paras if paras else ["外貌数据详见核心指标。"]


def _narrative_wealth(sec, r, a):
    """八、财富格局"""
    total = sec.get("cai_xing_total", a.get("cai_xing", {}).get("total", 0))
    level = sec.get("wealth_level", "")
    ck = sec.get("cai_ku", {})
    detail = sec.get("detail", "")
    detail_a = sec.get("detail_analysis", "")

    level_desc = {
        "巨富": "亿万级别",
        "大富": "数千万至亿级",
        "中富": "百万至千万级",
        "小富": "小康以上",
        "一般": "普通水平",
    }

    paras = [f"财星评分为{total}分，属{level}层次（{level_desc.get(level, '')}）。"]
    if ck.get("has"):
        paras.append(f"命带财库（{', '.join(ck.get('zhi', []))}），有储存和积累财富的能力，财不易散。")
    if detail_a:
        clean = detail_a.replace("'", "").replace('"', "")
        for line in clean.split("\n"):
            line = line.strip()
            if line and len(line) > 10 and "金鉴真人" not in line:
                paras.append(line)
                if len(paras) >= 5:  # 最多5行
                    break
    elif detail:
        clean = detail.replace("金鉴真人·", "")
        if len(clean) > 10:
            paras.append(clean)
    return paras


def _narrative_property(sec, r, a):
    """九、置业分析"""
    potential = sec.get("property_potential", "")
    level = sec.get("property_level", "")
    risk = sec.get("risk", "")

    paras = []
    if potential:
        paras.append(f"置业方位宜选{potential}。")
    if level:
        paras.append(f"置业能力{level}。")
    if risk:
        paras.append(f"注意事项：{risk}。")
    return paras if paras else ["暂无置业分析详细数据。"]


def _narrative_career(sec, r, a):
    """十、事业发展"""
    direction = sec.get("career_direction", "")
    grade = sec.get("career_grade", "")
    industry = sec.get("recommended_industries", "")
    ent = sec.get("entrepreneurship", "")
    best = sec.get("best_path", "")
    detail = sec.get("detail_analysis", "")

    paras = []
    if detail:
        clean = detail.replace("'", "").replace('"', "")
        for line in clean.split("\n"):
            line = line.strip()
            if line and len(line) > 15:
                paras.append(line)
        if len(paras) >= 2:
            return paras[:5]

    if direction:
        paras.append(f"事业方向宜走{direction}路线。")
    if grade:
        paras.append(f"{grade}。")
    if industry:
        paras.append(f"五行定行业，适宜从事{industry}等相关领域，利用五行能量助益事业发展。")
    if ent:
        clean = ent.replace("从", "")
        paras.append(clean + "。")
    if best:
        paras.append(best + "。")
    return paras if paras else ["暂无事业分析详细数据。"]


def _narrative_education(sec, r, a):
    """十一、学业学历"""
    level = sec.get("display", sec.get("school_level", ""))
    ypc = sec.get("year_pillar_check", {})
    detail = sec.get("detail_analysis", "")

    paras = []
    if detail:
        clean = detail.replace("'", "").replace('"', "")
        for line in clean.split("\n"):
            line = line.strip()
            if line and len(line) > 10 and "金鉴真人" not in line:
                paras.append(line)
        if len(paras) >= 2:
            return paras[:5]

    if level:
        clean = level.replace("🎓 ", "").replace("🥈 ", "").replace("🥇 ", "")
        paras.append(f"学业层次为{clean}。")
    if ypc:
        yin_info = ypc.get("detail", "")
        if yin_info:
            clean = yin_info.replace("✅", "")
            paras.append(f"年柱分析：{clean}。")
    return paras if paras else ["暂无学历分析详细数据。"]


def _narrative_marriage(sec, r, a):
    """十二、婚姻感情"""
    quality = sec.get("quality", "")
    score = sec.get("quality_score", "")
    window = sec.get("best_window_age", "")
    spouse = sec.get("spouse_trait", "")

    paras = []
    if quality:
        paras.append(
            f"婚姻质量为{quality}",
        )
    if score:
        paras.append(f"综合评分{score}/10分。")
    if window:
        clean = str(window).replace("暂无明显窗口岁", "暂无明显婚恋窗口")
        paras.append(f"最佳婚恋窗口在{clean}。")
    if spouse:
        paras.append(f"配偶特征：{spouse}。")
    return paras if paras else ["暂无婚姻分析详细数据。"]


def _narrative_children(sec, r, a):
    """十三、子女运势"""
    count = sec.get("child_count_estimate", "")
    ach = sec.get("child_achievement", "")
    detail = sec.get("detail_analysis", "")

    paras = []
    if detail:
        clean = detail.replace("'", "").replace('"', "")
        for line in clean.split("\n"):
            line = line.strip()
            if line and len(line) > 10:
                paras.append(line)
        if len(paras) >= 2:
            return paras[:5]
    if count:
        txt = str(count)
        if txt.startswith("{"):
            import re

            m = re.search(r"数量['\":：]*\d+", txt)
            if m:
                txt = m.group().split(":")[-1].split("：")[-1] + "个"
        paras.append(f"子女数量估计为{txt}。")
    if ach:
        if ach.startswith("{"):
            import re

            m = re.search(r"子女方向['\":：]*([^'\"}]+)", ach)
            if m:
                paras.append(f"子女成就趋势：{m.group(1)}。")
        else:
            paras.append(f"子女成就趋势：{ach}。")
    return paras if paras else ["暂无子女分析详细数据。"]


def _narrative_health(sec, r, a):
    """十四、健康注意"""
    constitution = sec.get("constitution", "")
    wx_over = sec.get("wu_xing_over_three", [])
    detail = sec.get("detail_analysis", "")

    paras = []
    if detail:
        clean = detail.replace("'", "").replace('"', "")
        for line in clean.split("\n"):
            line = line.strip()
            if line and len(line) > 10 and "{" not in line and "}" not in line:
                paras.append(line)
        if len(paras) >= 2:
            return paras[:5]
    if constitution:
        paras.append(f"先天体质{constitution}。")
    for w in wx_over[:2]:
        if w.get("wx") and w.get("organ"):
            paras.append(f"五行{w['wx']}过旺，对应{w['organ']}系统需留意日常保养。")
    return paras if paras else ["暂无健康分析详细数据。"]


def _narrative_family(sec, r, a):
    """十五、六亲关系"""
    summary = sec.get("summary", "")
    eco = sec.get("family_economy", "")
    pressure = sec.get("family_pressure", "")

    paras = []
    if summary:
        paras.append(f"{summary}。")
    if eco:
        paras.append(f"家庭经济状况{eco}。")
    if pressure:
        paras.append(f"{pressure}。")
    return paras if paras else ["暂无六亲分析详细数据。"]


def _narrative_events(sec, r, a):
    """十六、流年关键事件"""
    key_events = sec.get("key_events", {})
    detail = sec.get("detail", "")

    all_events = []
    for etype, evts in key_events.items():
        if isinstance(evts, list):
            for e in evts:
                if isinstance(e, dict) and e.get("year") and e.get("description"):
                    all_events.append(e)

    all_events.sort(key=lambda x: x.get("year", 0))

    paras = []
    if all_events:
        paras.append("未来数年关键节点如下：")
        for e in all_events[:15]:
            paras.append(f"{e['year']}年：{e['description']}。")
    if detail:
        paras.append(detail)
    return paras if paras else ["当前无显著流年事件触发。"]


def _narrative_da_yun_detail(sec, r, a):
    """十七、大运详批"""
    nar = sec.get("narrative", "")
    if nar:
        return [nar]
    paras = []
    dy_list = sec.get("list", [])
    if dy_list:
        paras.append(f"共行{len(dy_list)}步大运，每步十年。")
        best_idx = sec.get("best_idx", -1)
        worst_idx = sec.get("worst_idx", -1)
        if best_idx >= 0 and best_idx < len(dy_list):
            b = dy_list[best_idx]
            paras.append(f"最佳大运为{b.get('gan_zhi', '')}运（{b.get('start_age', '')}~{b.get('end_age', '')}岁）。")
        if worst_idx >= 0 and worst_idx < len(dy_list) and worst_idx != best_idx:
            w = dy_list[worst_idx]
            paras.append(f"需防范{w.get('gan_zhi', '')}运（{w.get('start_age', '')}~{w.get('end_age', '')}岁）。")
    return paras if paras else ["暂无大运详批数据。"]


def _narrative_verdicts_text(sec, r, a):
    """十八、三决断"""
    nar = sec.get("narrative", "")
    if nar:
        return [nar]
    # 如果sec是list
    if isinstance(sec, list):
        verdicts = sec
    else:
        verdicts = sec.get("verdicts", sec.get("list", []))
    if not verdicts:
        return ["暂无三决断数据。"]
    paras = []
    for i, v in enumerate(verdicts[:3]):
        paras.append(f"{v.get('title', '')}：{v.get('event', '')}（{v.get('time', '')}）。")
    return paras


def _narrative_da_yun_curve_text(sec, r, a):
    """十九、运程总评"""
    nar = sec.get("narrative", "")
    if nar:
        return [nar]
    return ["暂无运程总评数据。"]


def _narrative_wu_xing_text(sec, r, a):
    """二十、五行开运"""
    nar = sec.get("narrative", "")
    if nar:
        return [nar]
    return ["暂无五行开运数据。"]


def _narrative_life_advice_text(sec, r, a):
    """二十一、人生建议"""
    nar = sec.get("narrative", "")
    if nar:
        return [nar]
    return ["暂无人生建议数据。"]


def generate_pdf_report(data: dict, meta: dict = None) -> bytes:
    """根据引擎输出数据生成PDF报告，返回bytes"""
    pdf = JinjianPDF()
    pdf.add_page()

    r = data.get("result", {})
    bd = data.get("basic_data", {})
    pp = data.get("paipan", {})
    m = meta or data.get("_meta", {})
    a = data.get("analysis", {})

    name = m.get("name", "用户")
    gender = m.get("gender", "")
    year = m.get("year", "")
    month = m.get("month", "")
    day = m.get("day", "")
    hour_val = m.get("hour", 0)
    birthplace = m.get("birthplace", "东八区")
    bazi = pp.get("bazi", "")
    ri_gan = bd.get("ri_zhu", {}).get("gan", "")

    hour_names = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    hour_label = hour_names[min(hour_val // 2, 11)]

    # ═══════════════════════════
    # 封面/个人信息
    # ═══════════════════════════
    pdf.set_font("CJK", "B", 22)
    pdf.set_text_color(*C_GOLD)
    pdf.cell(0, 12, "✦ 金鉴真人", align="C")
    pdf.ln(10)
    pdf.set_font("CJK", "", 12)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(0, 7, "八字命理分析报告", align="C")
    pdf.ln(16)

    # 个人信息框
    pdf.set_fill_color(*C_BG)
    pdf.rect(15, pdf.get_y(), 180, 42, "F")
    y_start = pdf.get_y() + 3

    pdf.set_xy(20, y_start)
    pdf.set_font("CJK", "B", 16)
    pdf.set_text_color(*C_DARK)
    pdf.cell(80, 7, name)

    pdf.set_xy(110, y_start)
    pdf.set_font("CJK", "", 9)
    pdf.set_text_color(*C_MUTED)
    pdf.cell(80, 7, f"{gender} | {hour_label}时出生")

    pdf.set_xy(20, y_start + 10)
    pdf.set_font("CJK", "B", 20)
    pdf.set_text_color(*C_GOLD)
    pdf.cell(170, 9, bazi)

    pdf.set_xy(20, y_start + 22)
    pdf.set_font("CJK", "", 8)
    pdf.set_text_color(*C_MUTED)
    birth_str = f"{year}年{month}月{day}日"
    pdf.cell(170, 5, f"{birth_str} | 出生地：{birthplace} | 日主：{ri_gan}")

    pdf.set_y(y_start + 42)
    pdf.ln(8)

    # 核心指标
    s3 = r.get("sec_3_shen_qiang_ruo", a.get("shen_qiang_ruo", {}))
    s8 = r.get("sec_8_wealth", {})
    s4 = r.get("sec_4_xi_yong", a.get("xi_yong_shen", {}))
    s2 = r.get("sec_2_ge_ju", a.get("ge_ju", {}))

    sqr_label = s3.get("label", "")
    sqr_score = s3.get("score", 0)
    cai_total = s8.get("cai_xing_total", a.get("cai_xing", {}).get("total", 0))
    wealth_level = s8.get("wealth_level", "")
    ge_ju = s2.get("detail", "")
    xi_arr = s4.get("xi", a.get("xi_yong_shen", {}).get("xi", []))
    ji_arr = s4.get("ji", a.get("xi_yong_shen", {}).get("ji", []))

    pdf.chapter_title("命局核心数据")
    pdf.score_bar("身强弱", sqr_score)
    pdf.score_bar("财星", min(cai_total, 10))
    if ge_ju:
        pdf.key_value("格局", ge_ju)
    pdf.key_value("喜用神", "、".join(xi_arr) if xi_arr else "—")
    pdf.key_value("忌神", "、".join(ji_arr) if ji_arr else "—")
    if wealth_level:
        pdf.key_value("财富等级", wealth_level)

    # ═══════════════════════════
    # 四柱信息
    # ═══════════════════════════
    pdf.add_page()
    pdf.chapter_title("四柱八字")
    pillars = bd.get("pillars", {})
    p_names = ["year", "month", "day", "hour"]
    p_labels = ["年柱", "月柱", "日柱", "时柱"]

    # 表格头
    col_w = 47
    pdf.set_font("CJK", "B", 9)
    pdf.set_fill_color(*C_DARK)
    pdf.set_text_color(*C_GOLD)
    pdf.cell(20, 7, "", 1)
    for pl in p_labels:
        pdf.cell(col_w, 7, pl, 1, align="C")
    pdf.ln()

    # 表格行
    rows = [
        ("十神", lambda p: pillars.get(p, {}).get("shi_shen", "")),
        ("天干", lambda p: pillars.get(p, {}).get("tian_gan", "")),
        ("地支", lambda p: pillars.get(p, {}).get("di_zhi", "")),
        (
            "藏干",
            lambda p: " ".join(
                [(x["gan"] if isinstance(x, dict) else str(x)) for x in (pillars.get(p, {}).get("cang_gan", []) or [])]
            ),
        ),
        ("纳音", lambda p: pillars.get(p, {}).get("na_yin", "")),
        ("空亡", lambda p: pillars.get(p, {}).get("kong_wang", "")),
    ]

    pdf.set_font("CJK", "", 8)
    pdf.set_text_color(*C_TEXT)
    for rlabel, rfn in rows:
        pdf.cell(20, 6, rlabel, 1, align="C")
        for p in p_names:
            v = rfn(p)
            pdf.cell(col_w, 6, v, 1, align="C")
        pdf.ln()

    # ═══════════════════════════
    # 各章节详细分析 — 用连贯段落，不是字段列表
    # ═══════════════════════════
    sections = [
        ("一、一页总览", "sec_1_overview", _narrative_overview),
        ("二、格局分析", "sec_2_ge_ju", _narrative_ge_ju),
        ("三、身强弱判定", "sec_3_shen_qiang_ruo", _narrative_shen_qiang_ruo),
        ("四、喜用神与忌神", "sec_4_xi_yong", _narrative_xi_yong),
        ("五、灾祸预警与化解", "sec_5_zai_huo", _narrative_zai_huo),
        ("六、性格解析", "sec_6_character", _narrative_character),
        ("七、身材外貌", "sec_7_appearance", _narrative_appearance),
        ("八、财富格局", "sec_8_wealth", _narrative_wealth),
        ("九、置业分析", "sec_9_property", _narrative_property),
        ("十、事业发展", "sec_10_career", _narrative_career),
        ("十一、学业学历", "sec_11_education", _narrative_education),
        ("十二、婚姻感情", "sec_12_marriage", _narrative_marriage),
        ("十三、子女运势", "sec_13_children", _narrative_children),
        ("十四、健康注意", "sec_14_health", _narrative_health),
        ("十五、六亲关系", "sec_15_family", _narrative_family),
        ("十六、流年关键事件", "sec_16_events", _narrative_events),
    ]

    for title, sec_key, narrative_fn in sections:
        sec = r.get(sec_key, {})
        if not sec:
            continue
        pdf.add_page()
        pdf.chapter_title(title)

        # 方案B: 优先使用引擎层narrative字段
        if sec.get("narrative"):
            text = sec["narrative"]
            # 处理换行
            for line in text.split("\n"):
                line = line.strip()
                if line and len(line) >= 5:
                    pdf.body_text(line)
        else:
            # 降级: 用PDF层narrative函数
            paragraphs = narrative_fn(sec, r, a)
            for p in paragraphs:
                pdf.body_text(p)

    # ═══════════════════════════
    # 大运走势
    # ═══════════════════════════
    dy_detail = r.get("sec_17_da_yun_detail", {})
    dy_list = dy_detail.get("list", a.get("da_yun", {}).get("list", []))
    if dy_detail and dy_detail.get("narrative"):
        pdf.add_page()
        pdf.chapter_title("大运详批")
        for line in dy_detail["narrative"].split("\n"):
            line = line.strip()
            if line and len(line) >= 5:
                pdf.body_text(line)
    elif dy_list and len(dy_list) > 0:
        pdf.add_page()
        pdf.chapter_title("大运走势")

        for dy in dy_list:
            gz = dy.get("gan_zhi", "")
            sa = dy.get("start_age", 0)
            ea = dy.get("end_age", 0)
            sc = dy.get("score", 5)
            sy = dy.get("start_year", "")
            ey = dy.get("end_year", "")

            # 条形图
            pdf.set_font("CJK", "B", 10)
            pdf.set_text_color(*C_DARK)
            pdf.cell(20, 6, gz)
            pdf.set_font("CJK", "", 8)
            pdf.set_text_color(*C_MUTED)
            pdf.cell(35, 6, f"{sa}~{ea}岁 ({sy}~{ey})")

            bar_len = 70
            fill = max(1, int(sc / 10 * bar_len))
            bar = "█" * fill + "░" * (bar_len - fill)
            pdf.set_text_color(*C_GOLD)
            pdf.cell(72, 6, bar)

            pdf.set_text_color(*C_DARK)
            pdf.set_font("CJK", "B", 9)
            pdf.cell(0, 6, f"{sc:.1f}分", align="R")
            pdf.ln(6.5)

    # ═══════════════════════════
    # 三决断
    # ═══════════════════════════
    verdicts = r.get("sec_18_verdicts", [])
    if verdicts:
        pdf.add_page()
        pdf.chapter_title("三决断")
        # 优先使用narrative
        if isinstance(verdicts, dict) and verdicts.get("narrative"):
            for line in verdicts["narrative"].split("\n"):
                line = line.strip()
                if line and len(line) >= 5:
                    pdf.body_text(line)
        elif isinstance(verdicts, list):
            for v in verdicts:
                vt = v.get("title", "")
                ve = v.get("event", "")
                if vt:
                    pdf.sub_title(vt)
                if ve:
                    pdf.body_text(ve)

    # ═══════════════════════════
    # 八维运势 / 运程总评
    # ═══════════════════════════
    dims = a.get("dimensions", r.get("sec_19_overall", {}).get("dimensions", {}))
    s19 = r.get("sec_19_overall", {})
    if s19 and s19.get("narrative"):
        pdf.add_page()
        pdf.chapter_title("运程总评")
        for line in s19["narrative"].split("\n"):
            line = line.strip()
            if line and len(line) >= 5:
                pdf.body_text(line)
    elif dims:
        pdf.add_page()
        pdf.chapter_title("八维运势评分")
        for k, v in dims.items():
            score = v.get("total", 0) if isinstance(v, dict) else float(v)
            pdf.score_bar(k, score)

    # ═══════════════════════════
    # 五行开运
    # ═══════════════════════════
    wx = r.get("sec_20_wu_xing_advice", {})
    if wx:
        pdf.add_page()
        pdf.chapter_title("五行开运指南")
        # 优先使用narrative
        if wx.get("narrative"):
            for line in wx["narrative"].split("\n"):
                line = line.strip()
                if line and len(line) >= 5:
                    pdf.body_text(line)
        else:
            for label, key in [
                ("颜色", "colors"),
                ("方位", "directions"),
                ("饰品", "jewellery"),
                ("饮食", "diet"),
                ("数字", "lucky_numbers"),
            ]:
                val = wx.get(key, "")
                if val:
                    pdf.key_value(label, val)
            if wx.get("advice"):
                pdf.ln(2)
                pdf.sub_title("综合建议")
                pdf.body_text(wx["advice"])

    # ═══════════════════════════
    # 人生建议 §21
    # ═══════════════════════════
    s21 = r.get("sec_21_advice", {})
    if s21:
        pdf.add_page()
        pdf.chapter_title("人生建议")
        if s21.get("narrative"):
            for line in s21["narrative"].split("\n"):
                line = line.strip()
                if line and len(line) >= 5:
                    pdf.body_text(line)
        else:
            for label, key in [("事业", "career"), ("财富", "wealth"), ("健康", "health"), ("婚姻", "marriage")]:
                item = s21.get(key, {})
                if isinstance(item, dict) and item.get("advice"):
                    pdf.sub_title(label)
                    pdf.body_text(item["advice"])

    # ── 输出 ──
    return bytes(pdf.output())
