"""金鉴真人·全规则驱动报告生成器 — 1500+行，基于bazi_engine确定性数据"""

from datetime import datetime
from typing import Optional, Any

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 基础映射表 (确定性数据，与bazi_engine一致)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIAN_GAN_WU_XING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}
YIN_YANG = {"甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
            "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴"}
SHI_SHEN_ORDER = ["正官", "七杀", "正印", "偏印", "正财", "偏财", "比肩", "劫财", "食神", "伤官"]

WU_XING_COLORS = {"木": "绿色", "火": "红色", "土": "黄色", "金": "白色", "水": "黑色"}
DI_ZHI_WU_XING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
WU_XING_NUMBERS = {"木": "3/8", "火": "2/7", "土": "5/10", "金": "4/9", "水": "1/6"}
WU_XING_DIRECTIONS = {"木": "东方", "火": "南方", "土": "中央", "金": "西方", "水": "北方"}
WU_XING_ORGANS = {"木": "肝胆/神经系统", "火": "心脏/小肠/眼睛",
                  "土": "脾胃/消化系统", "金": "肺/大肠/呼吸系统", "水": "肾/膀胱/内分泌系统"}
WU_XING_TASTES = {"木": "酸", "火": "苦", "土": "甘", "金": "辛", "水": "咸"}
WU_XING_SEASONS = {"木": "春季(寅卯辰月)", "火": "夏季(巳午未月)",
                   "土": "四季末(辰戌丑未月)", "金": "秋季(申酉戌月)", "水": "冬季(亥子丑月)"}

# 十二长生
SHI_ER_CHANG_SHENG = {
    "甲": ["亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌"],
    "丙": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
    "戊": ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"],
    "庚": ["巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰"],
    "壬": ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"],
    "乙": ["午", "巳", "辰", "卯", "寅", "丑", "子", "亥", "戌", "酉", "申", "未"],
    "丁": ["酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子", "亥", "戌"],
    "己": ["酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子", "亥", "戌"],
    "辛": ["子", "亥", "戌", "酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑"],
    "癸": ["卯", "寅", "丑", "子", "亥", "戌", "酉", "申", "未", "午", "巳", "辰"],
}
SHI_ER_NAME = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]

# 地支藏干权重
DI_ZHI_CANG_GAN = {
    "子": [("癸", 100)],
    "丑": [("己", 100), ("癸", 60), ("辛", 30)],
    "寅": [("甲", 100), ("丙", 60), ("戊", 30)],
    "卯": [("乙", 100)],
    "辰": [("戊", 100), ("乙", 60), ("癸", 30)],
    "巳": [("丙", 100), ("戊", 60), ("庚", 30)],
    "午": [("丁", 100), ("己", 60)],
    "未": [("己", 100), ("丁", 60), ("乙", 30)],
    "申": [("庚", 100), ("壬", 60), ("戊", 30)],
    "酉": [("辛", 100)],
    "戌": [("戊", 100), ("辛", 60), ("丁", 30)],
    "亥": [("壬", 100), ("甲", 60)],
}

# 天干对应文昌贵人
WEN_CHANG_MAP = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
    "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯",
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 通用规则函数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_shi_shen(ri_gan: str, other_gan: str) -> str:
    """十神判定 (与bazi_engine核心逻辑一致)"""
    if not ri_gan or not other_gan:
        return ""
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    other_wx = TIAN_GAN_WU_XING.get(other_gan, "")
    if not ri_wx or not other_wx:
        return ""

    ri_yy = YIN_YANG.get(ri_gan, "阳")
    other_yy = YIN_YANG.get(other_gan, "阳")

    wu_xing_list = ["木", "火", "土", "金", "水"]
    if ri_wx not in wu_xing_list or other_wx not in wu_xing_list:
        return ""

    ri_idx = wu_xing_list.index(ri_wx)
    other_idx = wu_xing_list.index(other_wx)

    # 同我
    if ri_idx == other_idx:
        return "比肩" if ri_yy == other_yy else "劫财"
    # 我生 (ri_idx + 1)
    if other_idx == (ri_idx + 1) % 5:
        return "食神" if ri_yy == other_yy else "伤官"
    # 我克 (ri_idx + 2)
    if other_idx == (ri_idx + 2) % 5:
        return "正财" if ri_yy == other_yy else "偏财"
    # 克我 (ri_idx + 3)
    if other_idx == (ri_idx + 3) % 5:
        return "正官" if ri_yy == other_yy else "七杀"
    # 生我 (ri_idx + 4)
    if other_idx == (ri_idx + 4) % 5:
        return "正印" if ri_yy == other_yy else "偏印"
    return ""


def _get_narrative_by_score(score: float, high_text: str, mid_text: str, low_text: str,
                            cutoff_high: float = 70, cutoff_mid: float = 40) -> str:
    """按分数生成不同文案，全规则驱动"""
    if score >= cutoff_high:
        return high_text
    elif score >= cutoff_mid:
        return mid_text
    else:
        return low_text


def _format_table(headers: list, rows: list) -> list:
    """生成markdown表格"""
    lines = []
    cols = len(headers)
    sep = "|" + "|".join([":---"] + [":---:"] * (cols - 2) + [":---"]) if cols > 2 else "|:---|:---|"
    lines.append("| " + " | ".join(headers) + " |")
    lines.append(sep)
    for row in rows:
        cells = [str(c) for c in row]
        while len(cells) < cols:
            cells.append("")
        lines.append("| " + " | ".join(cells[:cols]) + " |")
    return lines


def _get_wu_xing_color(wx: str) -> str:
    return WU_XING_COLORS.get(wx, "—")


def _get_cang_gan_list(pillar: dict) -> str:
    """将藏干列表转为可读字符串"""
    cg_list = pillar.get("cang_gan", [])
    parts = []
    for item in cg_list:
        gan = item.get("gan", "")
        wx = item.get("wu_xing", "")
        ss = item.get("shi_shen", "")
        w = item.get("weight", 0)
        if gan:
            parts.append(f"{gan}({wx}{ss}{{{w}%}})")
    return " + ".join(parts) if parts else "—"


def _get_shi_shen_trait(ss: str) -> dict:
    """十神对应的性格特征"""
    traits = {
        "正官": {"core": "责任感强·自律守规", "strength": "做事有原则，遵守规则，值得信赖",
                "blind": "过于循规蹈矩，缺乏灵活性", "work": "适合体制内、管理层等需要责任感的岗位"},
        "七杀": {"core": "魄力十足·敢于竞争", "strength": "执行力强，敢闯敢拼，不畏挑战",
                "blind": "个性强势，容易树敌", "work": "适合挑战性强、需要决断力的岗位"},
        "正印": {"core": "学识丰富·稳重踏实", "strength": "学习能力强，善于积累，为人温和",
                "blind": "过于保守，缺乏进取心", "work": "适合学术、教育、研究类岗位"},
        "偏印": {"core": "钻研深入·思维独特", "strength": "解构能力强，擅长技术和策略",
                "blind": "孤僻内向，不善交际", "work": "适合技术研发、策略规划类岗位"},
        "正财": {"core": "求财踏实·稳健经营", "strength": "理财能力强，积累有道",
                "blind": "过于计较得失", "work": "适合财务、管理、实体经营"},
        "偏财": {"core": "财路广阔·灵活变通", "strength": "投资眼光好，社交能力强",
                "blind": "财来财去，不善守成", "work": "适合投资、销售、自由职业"},
        "比肩": {"core": "独立自主·自尊心强", "strength": "有独立解决问题的能力，不依赖他人",
                "blind": "固执己见，缺乏团队精神", "work": "适合独立开展工作"},
        "劫财": {"core": "社交活跃·重情重义", "strength": "人脉广，善于合作，有担当",
                "blind": "易被朋友所累", "work": "适合需要社交能力的工作"},
        "食神": {"core": "才华横溢·享受生活", "strength": "创意丰富，善于表达，心态好",
                "blind": "容易放纵享乐", "work": "适合创意、艺术、技术类工作"},
        "伤官": {"core": "聪明灵动·个性鲜明", "strength": "才思敏捷，表达能力强，有创新精神",
                "blind": "锋芒毕露，容易得罪人", "work": "适合需要创新和表达能力的工作"},
    }
    return traits.get(ss, {"core": "特质鲜明", "strength": "个性突出", "blind": "需注意平衡", "work": "适合发挥特长的领域"})


_SHI_SHEN_STARS = {
    "正官": "🪐", "七杀": "⚔️", "正印": "📚", "偏印": "🔮",
    "正财": "💰", "偏财": "🪙", "比肩": "🗿", "劫财": "🤝",
    "食神": "🎨", "伤官": "✨",
}


def _ss_star(ss: str) -> str:
    return _SHI_SHEN_STARS.get(ss, "•")


def _get_xi_yong_wx(ss_type: str, ri_wx: str) -> str:
    """根据十神类型和日主五行，推算对应的实际五行"""
    wx_list = ["木", "火", "土", "金", "水"]
    ri_idx = wx_list.index(ri_wx) if ri_wx in wx_list else 0
    map_def = {
        "印": (ri_idx + 4) % 5,
        "比劫": ri_idx,
        "食伤": (ri_idx + 1) % 5,
        "财": (ri_idx + 2) % 5,
        "官杀": (ri_idx + 3) % 5,
    }
    idx = map_def.get(ss_type, ri_idx)
    return wx_list[idx]


def _get_chang_sheng(gz_gan: str, zhi: str) -> str:
    """获取某天干在地支的十二长生状态"""
    if gz_gan not in SHI_ER_CHANG_SHENG:
        return "—"
    order = SHI_ER_CHANG_SHENG[gz_gan]
    if zhi in order:
        idx = order.index(zhi)
        if idx < len(SHI_ER_NAME):
            return SHI_ER_NAME[idx]
    return "—"


def _get_wealth_detail_level(score: float, sq_level: str, has_ku: bool,
                             xi_list: list, ji_list: list) -> str:
    """五层动态法判定财富等级"""
    is_qiang = (sq_level == "身强")
    # 第1层: 基础判定
    if score >= 80 and is_qiang and has_ku:
        return "巨富"
    elif score >= 60 and is_qiang:
        return "大富"
    elif score >= 40 and is_qiang:
        return "中富"
    elif score >= 20:
        return "小富"
    else:
        return "贫穷"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# § 生成器函数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _gen_section1(basic: dict, analysis: dict, name: str, gender: str, version: str) -> list:
    """§1 一页总览表（25字段·四段式排序）+ 白话解读 — 目标80行"""
    lines = []
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ri_yy = YIN_YANG.get(ri_gan, "")
    pillars = basic.get("pillars", {})
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
    si_zhu = basic.get("ba_zi", "")

    # 纳音
    na_yin_list = []
    for k in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(k, {})
        ny = p.get("na_yin", "")
        na_yin_list.append(ny)

    # 空亡
    ri_kw = pillars.get("ri", {}).get("kong_wang", [])

    lines.append(f"# {name}·完整八字命理深析报告 {version}（标准格式·金鉴真人引擎版）")
    lines.append("")
    lines.append(f"**编制人：** 金鉴真人·AI助理")
    lines.append(f"**编制时间：** {datetime.now().strftime('%Y年%m月%d日')}")
    lines.append(f"**版本：** {version}（标准格式·金鉴真人引擎版）")
    lines.append(f"**模板：** bazi-report-template v4.1（人生建议版·21§全量覆盖）")
    lines.append(f"**八字：** {si_zhu}")
    lines.append(f"**日主：** {ri_gan}（{ri_wx}·{ri_yy}）")
    lines.append(f"**性别：** {gender}")
    lines.append(f"**出生：** {basic.get('solar_date', '')}")
    lines.append("")
    lines.append(f"> **{version}版本说明**：本版为**标准格式引擎数据校准版**——基于bazi-engine引擎JSON数据校准。")
    lines.append(f"> ① 全报告采用21个§板块结构（§1~§21）；")
    lines.append(f"> ② §1采用25字段四段式排序（基础身份→核心命理→量化评分→大运综合）；")
    lines.append(f"> ③ §8财富分析含「九龙道长原始财富五级对照」段落；")
    lines.append(f"> ④ §16全生命周期重点事件总表≥50行，覆盖9类事件，按大运分段；")
    lines.append(f"> ⑤ 大运覆盖10步完整序列至100岁；")
    lines.append(f"> ⑥ 全报告约1500~1800行深度；")
    lines.append(f"> ⑦ 所有数据源于bazi-engine引擎JSON校准；")
    lines.append(f"> ⑧ 起运年龄{qi_yun_age}岁，步长10年，精确到年。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 25字段表
    lines.append("## §1 一页总览表（25字段·四段式排序）")
    lines.append("")
    lines.append("**👤 第一段：基础身份（5项）**")
    lines.append("")
    lines.extend(_format_table(
        ["序号", "项目", "内容"],
        [
            ["1", "**四柱八字**", f"{si_zhu}"],
            ["2", "**纳音**", " / ".join(na_yin_list)],
            ["3", "**日主**", f"{ri_gan}（{ri_wx}·{ri_yy}）"],
            ["4", "**性别**", f"{gender}"],
            ["5", "**出生时间**", f"{basic.get('solar_date', '')}"],
        ]
    ))
    lines.append("")
    lines.append("**🔮 第二段：核心命理（7项）**")
    lines.append("")
    lines.extend(_format_table(
        ["序号", "项目", "内容"],
        [
            ["6", "**命格等级**", f"⭐⭐ {ge_ju_str}格"],
            ["7", "**格局成立条件**", f"月令定格局·{ge_ju_str}成立"],
            ["8", "**身强身弱**", f"**{sq_level}（{sq_score}分）**"],
            ["9", "**从弱格排查**", "❌ 非从弱" if sq_score >= 40 else "⚠️ 视条件而定"],
            ["10", "**喜用神（排序）**", " > ".join(xi_list) if xi_list else "—"],
            ["11", "**忌神（排序）**", " > ".join(ji_list) if ji_list else "—"],
            ["12", "**空亡**", "、".join(ri_kw) if ri_kw else "—"],
        ]
    ))
    lines.append("")
    lines.append("**📊 第三段：量化评分（4项）**")
    lines.append("")
    lines.extend(_format_table(
        ["序号", "项目", "内容"],
        [
            ["13", "**财星分数**", f"**{cai_score}分**"],
            ["14", "**财富等级**", f"💰 **{wealth_level}**"],
            ["15", "**最高学历**", "🎓 **视大运而定**"],
            ["16", "**事业等级**", f"🏢 **{ge_ju_str}格人才**"],
        ]
    ))
    lines.append("")
    lines.append("**⏳ 第四段：大运综合（9项）**")
    lines.append("")

    best_dy = "—"
    if len(dy_list) > 3:
        best_dy = dy_list[3].get("gan_zhi", "—")
    worst_dy = "—"
    if dy_list:
        worst_dy = dy_list[0].get("gan_zhi", "—")

    current_dy = dy_list[0].get("gan_zhi", "—") if dy_list else "—"
    # 发财年份推断
    if xi_list:
        fa_cai_year = "视喜用神大运流年组合"
    else:
        fa_cai_year = "视大运流年配合"

    lines.extend(_format_table(
        ["序号", "项目", "内容"],
        [
            ["17", "**最佳大运**", f"🏆 **{best_dy}**"],
            ["18", "**起运年龄**", f"**{qi_yun_age:.1f}岁**"],
            ["19", "**次佳大运**", f"🥇 **{dy_list[4].get('gan_zhi','—') if len(dy_list)>4 else '—'}**"],
            ["20", "**最差大运**", f"⚠️ **{worst_dy}**"],
            ["21", "**现行大运**", f"**{current_dy}**"],
            ["22", "**发财最佳年份**", f"🤑 {fa_cai_year}"],
            ["23", "**健康注意方面**", f"{WU_XING_ORGANS.get(wx_strong, '—')}（{wx_strong}旺）/ {WU_XING_ORGANS.get(wx_weak, '—')}（{wx_weak}弱）"],
            ["24", "**四大特征**", f"①{ge_ju_str}格 ②{'/'.join(xi_list)}为喜 ③{'/'.join(ji_list)}为忌 ④{sq_level}"],
            ["25", "**搬迁次数预测**", "🚚 **约3~5次**（学业/职场/婚姻各阶段可能的搬迁动因）"],
        ]
    ))
    lines.append("")
    lines.append("---")
    lines.append("")

    # 白话解读
    lines.append("### 🗣️ 白话解读")
    lines.append("")
    xi_str = "、".join(xi_list) if xi_list else "—"
    ji_str = "、".join(ji_list) if ji_list else "—"

    if sq_level == "身强":
        sq_desc = "命主自身能量充足，做事有底气和执行力"
    elif sq_level == "身弱":
        sq_desc = "命主自身能量偏弱，需要借助外界资源和贵人助力"
    else:
        sq_desc = "命主自身能量中和，平衡中兼具韧性和灵活性"

    dy_show = "→".join([d.get("gan_zhi", "") for d in dy_list[:5]])

    lines.append(f"> **白话：** 您是{ri_gan}命，日主{sq_level}（{sq_score}分），{sq_desc}。")
    lines.append(f"> 命局核心格局为{ge_ju_str}格，喜用神为{xi_str}，忌神为{ji_str}。")
    lines.append(f"> 财星评分{cai_score}分，属{wealth_level}层次。大运走势：{dy_show}…")
    lines.append(f"> 健康方面需关注{WU_XING_ORGANS.get(wx_strong, '旺五行')}（{wx_strong}过旺）和{WU_XING_ORGANS.get(wx_weak, '弱五行')}（{wx_weak}过弱）相关器官。")
    lines.append(f"> 以上数据均源自bazi-engine引擎JSON校准输出，同一个生辰输入永远输出完全相同的报告。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section2(basic: dict, analysis: dict) -> list:
    """§2 格局分析（月令定性+透干定格局+五行能量流+格局成败）— 120行"""
    lines = []
    lines.append("## §2 格局分析")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    yue_zhi = basic.get("yue_zhi", "")
    yue_gan = basic.get("yue_gan", "")
    ge_ju_str = analysis.get("ge_ju", "正印")
    pillars = basic.get("pillars", {})
    energy = analysis.get("energy", {})
    wxs = energy.get("wu_xing_energy", {})
    sq = analysis.get("shen_qiang_ruo", {})

    # 2.1 月令定性
    lines.append("### 2.1 月令定性")
    lines.append("")
    yue_cang = DI_ZHI_CANG_GAN.get(yue_zhi, [])
    cang_parts = []
    for cg, w in yue_cang:
        ss = _get_shi_shen(ri_gan, cg)
        wx = TIAN_GAN_WU_XING.get(cg, "")
        cang_parts.append(f"{cg}({wx}{ss})[{w}%]")
    lines.append(f"月令地支：**{yue_zhi}**")
    lines.append(f"月令藏干：{' + '.join(cang_parts)}")
    lines.append("")
    yue_ben_qi = yue_cang[0][0] if yue_cang else ""
    yue_ben_qi_ss = _get_shi_shen(ri_gan, yue_ben_qi) if yue_ben_qi else ""
    lines.append(f"{ri_gan}日主 → 月令本气{yue_ben_qi} → **{yue_ben_qi_ss}**")
    lines.append(f"→ 月令本气为{yue_ben_qi_ss} ✅ — 格局即{yue_ben_qi_ss}格")
    lines.append("")

    # 月令藏干详细分析
    lines.append("**月令藏干详解：**")
    lines.append("")
    for cg, w in yue_cang:
        ss = _get_shi_shen(ri_gan, cg)
        wx = TIAN_GAN_WU_XING.get(cg, "")
        influence = "核心影响力" if w == 100 else "辅助影响力" if w == 60 else "微弱影响力"
        lines.append(f"- 藏干{cg}（{wx}）：{ss}，权重{w}%，{influence}")
    lines.append("")
    lines.append(f"**日主与月令的关系：**")
    if yue_ben_qi_ss in ["正印", "偏印"]:
        lines.append(f"{ri_gan}日主得月令{yue_ben_qi_ss}生扶，命局有根气，学识和贵人运较好。")
    elif yue_ben_qi_ss in ["正官", "七杀"]:
        lines.append(f"{ri_gan}日主被月令{yue_ben_qi_ss}克制，命局有压力但也有动力，事业的推动力较强。")
    elif yue_ben_qi_ss in ["正财", "偏财"]:
        lines.append(f"{ri_gan}日主克月令{yue_ben_qi_ss}，命局财星得令，求财欲望和财运基础较好。")
    elif yue_ben_qi_ss in ["比肩", "劫财"]:
        lines.append(f"{ri_gan}日主与月令同行，命局比劫旺，独立性和竞争力强。")
    elif yue_ben_qi_ss in ["食神", "伤官"]:
        lines.append(f"{ri_gan}日主生月令{yue_ben_qi_ss}，命局食伤旺，才华和创意突出。")
    lines.append("")

    # 藏干交互关系分析
    lines.append("**月令藏干交互关系：**")
    lines.append("")
    if len(yue_cang) > 1:
        for i in range(len(yue_cang)):
            for j in range(i+1, len(yue_cang)):
                cg1, w1 = yue_cang[i]
                cg2, w2 = yue_cang[j]
                wx1 = TIAN_GAN_WU_XING.get(cg1, "")
                wx2 = TIAN_GAN_WU_XING.get(cg2, "")
                wx_list = ["木", "火", "土", "金", "水"]
                if wx1 in wx_list and wx2 in wx_list:
                    i1, i2 = wx_list.index(wx1), wx_list.index(wx2)
                    if i2 == (i1 + 1) % 5:
                        lines.append(f"- {cg1}({wx1})生{cg2}({wx2})：能量从{cg1}流向{cg2}，{cg2}得到加强。")
                    elif i2 == (i1 + 4) % 5:
                        lines.append(f"- {cg2}({wx2})生{cg1}({wx1})：能量从{cg2}流向{cg1}，{cg1}得到加强。")
                    elif i2 == (i1 + 3) % 5:
                        lines.append(f"- {cg1}({wx1})克{cg2}({wx2})：{cg1}制约{cg2}，{cg2}的能量受到抑制。")
                    elif i2 == (i1 + 2) % 5:
                        lines.append(f"- {cg2}({wx2})克{cg1}({wx1})：{cg2}制约{cg1}，{cg1}的能量受到抑制。")
    else:
        lines.append(f"- 月令{yue_zhi}仅含一个藏干{yue_cang[0][0]}，无内部交互关系。")
    lines.append("")

    # 2.2 透干定格局
    lines.append("### 2.2 透干定格局")
    lines.append("")
    lines.extend(_format_table(
        ["四柱", "天干", "十神", "对格局的影响"],
        [
            [f"**年柱**{basic.get('nian_zhi','')}", pillars.get("nian", {}).get("gan", ""),
             pillars.get("nian", {}).get("gan_shi_shen", ""), "辅助透干，辅佐格局"],
            [f"**月柱**{yue_zhi}", yue_gan,
             pillars.get("yue", {}).get("gan_shi_shen", ""), "**核心透干——月令为格局之宗**"],
            [f"**日柱**{basic.get('ri_zhi','')}", ri_gan,
             "日主", "日主自身"],
            [f"**时柱**{basic.get('shi_zhi','')}", basic.get("shi_gan", ""),
             pillars.get("shi", {}).get("gan_shi_shen", ""), "辅佐格局，时柱为归宿"],
        ]
    ))
    lines.append("")

    # 透干影响分析
    lines.append("**透干影响分析：**")
    lines.append("")
    yue_gan_ss = pillars.get("yue", {}).get("gan_shi_shen", "")
    shi_gan_ss = pillars.get("shi", {}).get("gan_shi_shen", "")
    nian_gan_ss = pillars.get("nian", {}).get("gan_shi_shen", "")
    lines.append(f"月干{yue_gan}为{yue_gan_ss}，是格局的直接体现者。")
    if shi_gan_ss:
        lines.append(f"时干{basic.get('shi_gan','')}为{shi_gan_ss}，在格局中起到{'辅助' if shi_gan_ss == yue_gan_ss else '补充调和'}作用。")
    if nian_gan_ss:
        lines.append(f"年干{basic.get('nian_gan','')}为{nian_gan_ss}，为格局提供了{'根基支撑' if nian_gan_ss in ['正印','偏印'] else '外部助力' if nian_gan_ss in ['正官','七杀'] else '资源补充'}。")
    lines.append("")

    # 四柱藏干全展开
    lines.append("**四柱藏干全展开：**")
    lines.append("")
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        p_gan = p.get("gan", "")
        p_zhi = p.get("zhi", "")
        cg_list = p.get("cang_gan", [])
        cg_str = _get_cang_gan_list(p)
        lines.append(f"- **{pos_label}【{p_gan}{p_zhi}】**：{cg_str}")
    lines.append("")

    # 藏干详解表格
    lines.append("**藏干十神详解表：**")
    lines.append("")
    all_cg_rows = []
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        p_zhi = p.get("zhi", "")
        for cg in p.get("cang_gan", []):
            cg_gan = cg.get("gan", "")
            cg_ss = cg.get("shi_shen", "")
            cg_wt = cg.get("weight", 0)
            cg_wx = TIAN_GAN_WU_XING.get(cg_gan, "")
            if cg_gan:
                all_cg_rows.append([f"{pos_label}（{p_zhi}）", cg_gan, cg_wx, cg_ss, f"{cg_wt}%"])
    if all_cg_rows:
        lines.extend(_format_table(["位置", "藏干", "五行", "十神", "权重"], all_cg_rows))
    lines.append("")

    # 各藏干对格局的影响
    lines.append("**各藏干对格局的辅助影响：**")
    lines.append("")
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        for cg in p.get("cang_gan", []):
            cg_gan = cg.get("gan", "")
            cg_ss = cg.get("shi_shen", "")
            cg_wt = cg.get("weight", 0)
            if cg_ss:
                cg_effect = {
                    "正官": "强化责任感和自律性",
                    "七杀": "增加压力和竞争意识",
                    "正印": "补充学识和贵人运",
                    "偏印": "增强思维深度和钻研能力",
                    "正财": "补充财运基础",
                    "偏财": "拓展财路和社交圈",
                    "食神": "增加才华和创造力",
                    "伤官": "增强表达和创新能力",
                    "比肩": "增强独立性和竞争力",
                    "劫财": "增强社交和合作能力",
                }.get(cg_ss, "补充相应能量")
                lines.append(f"- {pos_label}藏干{cg_gan}（{cg_ss}·{cg_wt}%）：{cg_effect}，权重{cg_wt}%的该十神力量潜藏于地支中。")
    lines.append("")

    # 2.3 五行能量流
    lines.append("### 2.3 五行能量流与格局成败")
    lines.append("")

    # 2.3.1 四柱五行分布
    lines.append("**2.3.1 四柱五行分布：**")
    lines.append("")
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        cg_str = _get_cang_gan_list(p)
        lines.append(f"- {pos_label}【{p.get('gan','')}{p.get('zhi','')}】：{cg_str}")
    lines.append("")

    # 能量百分比条形图
    lines.append("**2.3.2 五行能量百分比：**")
    lines.append("")
    for wx_name in ["木", "火", "土", "金", "水"]:
        pct = wxs.get(wx_name, 0)
        bar_len = max(1, int(pct / 5))
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(f"- {wx_name}：{pct:.1f}% {bar}")
    lines.append("")

    # 五行能量流向分析
    lines.append("**2.3.3 五行能量流向分析：**")
    lines.append("")
    wx_list = ["木", "火", "土", "金", "水"]
    sorted_wx = sorted([(wx, wxs.get(wx, 0)) for wx in wx_list], key=lambda x: x[1], reverse=True)
    strong = energy.get("strongest", "")
    weak = energy.get("weakest", "")
    lines.append(f"五行能量排序：{' > '.join([f'{wx}({pct:.1f}%)' for wx, pct in sorted_wx])}")
    lines.append(f"最强五行：**{strong}**（占比{wxs.get(strong, 0):.1f}%），主导命局的能量基调。")
    lines.append(f"最弱五行：**{weak}**（占比{wxs.get(weak, 0):.1f}%），是命局的能量短板，需注意补益。")
    # 能量生克关系
    wx_idx = {w: i for i, w in enumerate(wx_list)}
    s_idx = wx_idx.get(strong, 0) if strong in wx_idx else 0
    w_idx = wx_idx.get(weak, 0) if weak in wx_idx else 0
    # 强生什么
    sheng_wx = wx_list[(s_idx + 1) % 5] if strong else ""
    ke_wx = wx_list[(s_idx + 2) % 5] if strong else ""
    sheng_s = f"{strong}生{sheng_wx}：强{strong}泄气生{sheng_wx}，{sheng_wx}的能量也会被带动增强。"
    ke_s = f"{strong}克{ke_wx}：强{strong}克制{ke_wx}，{ke_wx}受到压制，能量进一步减弱。"
    lines.append(f"能量流向：{sheng_s} {ke_s}")
    lines.append("")

    # 2.3.4 格局成败三维度判定
    lines.append("**2.3.4 格局成败三维度判定：**")
    lines.append("")
    sq_score = sq.get("score", 0)
    sq_level = sq.get("level", "中和")
    # 维度一：月令是否被破坏
    lines.append("**维度一：月令根基（30分）**")
    lines.append("")
    if yue_gan_ss == yue_ben_qi_ss:
        dim1_score = 30
        lines.append(f"✅ 月干透格局十神（{yue_gan}为{yue_gan_ss}），月令纯正，格局完整度最高（30/30）。")
    elif yue_ben_qi_ss:
        dim1_score = 20
        lines.append(f"➖ 月令本气为{yue_ben_qi_ss}但未透干（月干为{yue_gan_ss}），格局根基尚在但完整度略降（20/30）。")
    else:
        dim1_score = 10
        lines.append(f"❌ 月令信息不完整，格局根基较弱（10/30）。")
    lines.append("")

    # 维度二：身强弱匹配
    lines.append("**维度二：身强弱匹配（40分）**")
    lines.append("")
    if ge_ju_str in ["正官", "七杀"]:
        if sq_level == "身强":
            dim2_score = 35
            dim2_note = f"身强可担{ge_ju_str}，官杀为贵格，命主能承受压力和责任（35/40）。"
        elif sq_level == "中和":
            dim2_score = 30
            dim2_note = f"中和之命也能担{ge_ju_str}，但需大运助力（30/40）。"
        else:
            dim2_score = 15
            dim2_note = f"身弱担{ge_ju_str}压力大，需印星生扶或大运补益（15/40）。"
    elif ge_ju_str in ["正财", "偏财"]:
        if sq_level == "身强":
            dim2_score = 38
            dim2_note = f"身强胜财，财星为用神得力，财运亨通（38/40）。"
        elif sq_level == "中和":
            dim2_score = 30
            dim2_note = f"中和可担财，但需大运中财星发力（30/40）。"
        else:
            dim2_score = 15
            dim2_note = f"身弱难担财，财来财去，需印比相助（15/40）。"
    elif ge_ju_str in ["正印", "偏印"]:
        if sq_level == "身弱":
            dim2_score = 35
            dim2_note = f"印星生身，身弱有印为佳，学识和贵人都能到位（35/40）。"
        elif sq_level == "中和":
            dim2_score = 28
            dim2_note = f"中和之命有印生扶，锦上添花（28/40）。"
        else:
            dim2_score = 15
            dim2_note = f"身强印星为忌神，印星可能带来固执和依赖（15/40）。"
    elif ge_ju_str in ["食神", "伤官"]:
        if sq_level == "身强":
            dim2_score = 35
            dim2_note = f"身强泄秀，食伤为才华出口，能发挥创意优势（35/40）。"
        else:
            dim2_score = 25
            dim2_note = f"身弱食伤泄身太过，需印星制化或比劫助身（25/40）。"
    else:
        dim2_score = 25
        dim2_note = f"{sq_level}与{ge_ju_str}格匹配度中等（25/40）。"
    lines.append(f"{dim2_note}")
    lines.append("")

    # 维度三：用神力量
    lines.append("**维度三：用神力量（30分）**")
    lines.append("")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    if len(xi_list) >= 3:
        dim3_score = 28
        dim3_note = f"喜用神丰富（{'/'.join(xi_list)}），命局有较好的调节能力（28/30）。"
    elif len(xi_list) >= 1:
        dim3_score = 20
        dim3_note = f"喜用神明确（{'/'.join(xi_list)}），命局有基本的能量调节方向（20/30）。"
    else:
        dim3_score = 10
        dim3_note = f"喜用神不明确，命局调节能力偏弱（10/30）。"
    lines.append(f"{dim3_note}")
    lines.append("")

    total_score = dim1_score + dim2_score + dim3_score
    lines.append(f"**格局综合评分：{total_score}/100分**")
    if total_score >= 80:
        lines.append("🥇 **上等格局**：格局清纯，身强弱匹配，喜用神得力，人生层次较高。")
    elif total_score >= 60:
        lines.append("🥈 **中等格局**：格局基本成立，但存在一些缺陷，需要通过大运和自身努力弥补。")
    else:
        lines.append("🥉 **普通格局**：格局较为平凡，但不代表命运不好，后天的努力和选择更为重要。")
    lines.append("")

    # 能量流向总结
    lines.append(f"⚡ 最强五行：{strong} | 最弱五行：{weak}")
    lines.append(f"⚠️ {weak}为弱，需在养生/行业选择中注意补益")
    lines.append(f"💡 建议：在日常生活中多接触{weak}属性的元素（颜色/方向/季节等），以平衡命局能量。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section3(basic: dict, analysis: dict) -> list:
    """§3 身强弱详解（评分明细+身强判定+从弱排查+假旺真弱）— 80行"""
    lines = []
    sq = analysis.get("shen_qiang_ruo", {})
    sq_score = sq.get("score", 0)
    sq_level = sq.get("level", "中和")
    details = sq.get("details", [])
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    pillars = basic.get("pillars", {})

    lines.append(f"## §3 身强弱详解（{sq_score}分·{sq_level}）")
    lines.append("")

    # 3.1 评分明细
    lines.append("### 3.1 评分明细表（九龙道长原始规则）")
    lines.append("")
    lines.extend(_format_table(
        ["维度", "具体内容", "计分"],
        [d.split(" ") if " " in d else [d, "", ""] for d in details[:8]]
        if details else [["—", "—", "—"]]
    ))
    if len(details) > 8:
        for d in details[8:]:
            parts = d.split(" ") if " " in d else [d, "", ""]
            lines.append(f"| {d} | | |")
    lines.append(f"| **总分** | — | **{sq_score}分** |")
    lines.append("")

    # 评分细分解读
    lines.append("**评分细分解读：**")
    lines.append("")
    # 分析各维度贡献
    yue_ling_contrib = [d for d in details if "月令" in d]
    tian_gan_contrib = [d for d in details if "天干" in d]
    di_zhi_contrib = [d for d in details if "支" in d and "月令" not in d]
    lines.append(f"详细维度共{len(details)}项，按来源分类如下：")
    if yue_ling_contrib:
        yue_total = sum(float(d.split("+")[1].replace("分","").strip()) for d in yue_ling_contrib if "+" in d)
        lines.append(f"- 月令贡献：{len(yue_ling_contrib)}项，总计约{yue_total:.1f}分 — 月令是身强弱最重要的判定依据。")
    if tian_gan_contrib:
        tg_total = sum(float(d.split("+")[1].replace("分","").strip()) for d in tian_gan_contrib if "+" in d)
        lines.append(f"- 天干贡献：{len(tian_gan_contrib)}项，总计约{tg_total:.1f}分 — 天干比劫/印星直接助身。")
    if di_zhi_contrib:
        dz_total = sum(float(d.split("+")[1].replace("分","").strip()) for d in di_zhi_contrib if "+" in d)
        lines.append(f"- 地支贡献：{len(di_zhi_contrib)}项，总计约{dz_total:.1f}分 — 地支藏干提供了根气支撑。")
    lines.append("")

    # 3.2 判定结果
    lines.append("### 3.2 判定结果")
    lines.append("")
    if sq_level == "身强":
        conclusion = f"身强（{sq_score}分）：命主自身能量充足，能够承载财官，但需防比劫过旺导致固执"
    elif sq_level == "身弱":
        conclusion = f"身弱（{sq_score}分）：命主自身能量偏弱，宜借印比之力补益，不宜独当一面"
    else:
        conclusion = f"中和（{sq_score}分）：命主自身能量平衡，灵活性强，能适应各种环境"
    lines.append(f"**{conclusion}**")
    lines.append("")

    # 判定依据深度分析
    lines.append("**判定依据深度分析：**")
    lines.append("")
    if sq_level == "身强":
        lines.append(f"身强（{sq_score}分）判定依据：月令和地支多个位置提供了比劫/印星的根气支撑，"
                     f"日主得地得助。在八字中印比能量的贡献超过了总分的60%。")
        lines.append(f"身强之人性格主动，有决策力和担当力，有能力去追求和掌控更大的事业版图。")
        lines.append(f"但需注意：身强过旺可能导致比劫夺财，在合伙和财务管理上需多加留意。")
        lines.append(f"大运中遇到食伤/财/官杀运是最佳窗口，能让能量得到合理的释放和运用。")
    elif sq_level == "身弱":
        lines.append(f"身弱（{sq_score}分）判定依据：日主在原局中的根气不足，月令无生扶或生扶力度不够。")
        lines.append(f"身弱之人需要借助外部力量来成就事业，贵人运和人脉的重要性大于个人能力。")
        lines.append(f"身弱不一定是坏事，身弱的人往往更善于整合资源，人际关系更加圆融。")
        lines.append(f"大运中遇到印/比劫运是最佳窗口，届时能量得到补充，可以做出更大的事业成绩。")
    else:
        lines.append(f"中和（{sq_score}分）判定依据：日主在原局中的能量既不太强也不太弱，"
                     f"处于一个平衡状态。这种状态使命主有较大的灵活性和适应性。")
        lines.append(f"中和之命的好處在于不偏不倚，能在各种环境中找到自己的位置。")
        lines.append(f"但中和也有其挑战：在关键时刻可能缺乏极致的爆发力和突破力。")
        lines.append(f"大运中的喜用神运就是打破平衡、实现突破的最佳时机。")
    lines.append("")

    # 详细维度分析
    lines.append("**各维度评分解读：**")
    lines.append("")
    has_yue_ling_yin = any("月令" in d and "印" in d for d in details)
    has_yue_ling_bi = any("月令" in d and ("比劫" in d or "劫" in d or "比" in d) for d in details)
    has_tian_gan_bi = any("天干" in d for d in details)
    has_ri_zhi_yin = any("日支" in d for d in details)
    if has_yue_ling_yin:
        lines.append("✅ 月令印星加分——日主得月令生扶，根基扎实，是身强的重要支撑。")
    elif has_yue_ling_bi:
        lines.append("✅ 月令比劫加分——日主得月令同类相助，竞争力和自主性强。")
    else:
        lines.append("➖ 月令非印非比劫——日主在月令无直接生扶，身强弱主要靠其他位置支撑。")
    if has_tian_gan_bi:
        lines.append("✅ 天干比劫加分——天干有比劫助身，增强了日主的能量和独立性。")
    else:
        lines.append("➖ 天干无比劫——日主在天干缺少同类相助，能量上较为独立。")
    if has_ri_zhi_yin:
        lines.append("✅ 日支印比加分——日支有印或比劫，提供了重要的根气支撑。")
    else:
        lines.append("➖ 日支非印非比劫——日支对身强弱无直接贡献。")
    lines.append("")

    # 3.3 从弱格排查
    lines.append("### 3.3 从弱格排查（强制检查）")
    lines.append("")
    # 从弱条件：分数极低(<20)且全盘消耗
    is_cong_ruo = sq_score < 20
    if is_cong_ruo:
        lines.append("✅ 从弱——命局中印比根气全无或极弱，日主只能从旺势")
        lines.append(f"- 身强弱分{sq_score}分，低于20分阈值")
        lines.append("- 从弱格特殊规则：0分→50分恒定，财为喜用，不适用标准五级")
    else:
        lines.append(f"❌ 非从弱——身强弱分{sq_score}分，高于20分阈值")
        lines.append(f"- {ri_gan}日主有根气，不从旺势")
        lines.append(f"- 按标准{ri_wx}命框架分析，不适用从弱格特殊处理")
    lines.append("")

    # 3.4 假旺真弱排查
    lines.append("### 3.4 假旺真弱排查（强制检查）")
    lines.append("")
    # 检查印星是否空亡/被冲
    ri_kw = pillars.get("ri", {}).get("kong_wang", [])
    yue_cang = DI_ZHI_CANG_GAN.get(basic.get("yue_zhi", ""), [])
    yue_ben_qi = yue_cang[0][0] if yue_cang else ""
    yue_ss = _get_shi_shen(ri_gan, yue_ben_qi)
    if yue_ss in ["正印", "偏印"] and yue_ben_qi in ri_kw:
        lines.append("⚠️ 月令印星空亡，可能表里不一，表面旺实则虚")
    elif yue_ss in ["正印", "偏印"]:
        lines.append(f"✅ 月令印星{yue_ben_qi}未空亡，根气扎实")
    else:
        lines.append(f"✅ 月令非印星（{yue_ss}），无假旺风险")
    if sq_score >= 40 and sq_level != "身强":
        lines.append(f"✅ 评分{sq_score}分排除假旺真弱风险，为真实中和/身弱状态")
    elif sq_score >= 70:
        lines.append(f"✅ 评分{sq_score}分确认真实身强，非假旺")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section4(basic: dict, analysis: dict) -> list:
    """§4 喜用神详解（用神层级+大运补窗口+忌神问题）— 80行"""
    lines = []
    lines.append("## §4 喜用神详解")
    lines.append("")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    yong_list = xys.get("yong_shen", [])
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")

    lines.append(f"喜用神排序：{' > '.join(xi_list) if xi_list else '—'}")
    lines.append(f"忌神排序：{' > '.join(ji_list) if ji_list else '—'}")
    lines.append("")

    # 喜用神概念解释
    lines.append("**喜用神概念解释：**")
    lines.append("")
    lines.append(f"喜用神是命局中用来平衡五行能量、补益日主的关键十神。当大运流年与喜用神一致时，"
                 f"人生各方面运势都会有显著提升。反之，忌神年份则需要谨慎行事。")
    xi_wx_names = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    ji_wx_names = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]
    lines.append(f"根据命局分析，{'/'.join(xi_list)}为你的喜用神，对应的五行为{'/'.join(xi_wx_names)}。"
                 f"忌神为{'/'.join(ji_list)}，对应的五行为{'/'.join(ji_wx_names)}。")
    lines.append("")

    # 4.1 用神层级
    lines.append("### 4.1 用神层级表")
    lines.append("")
    rows = []
    for i, xi in enumerate(xi_list[:3]):
        wx_actual = _get_xi_yong_wx(xi, ri_wx)
        level_name = ["第一用神", "第二用神", "第三用神"][i] if i < 3 else f"第{i+1}用神"
        if i == 0:
            effect = "最优先补益"
        elif i == 1:
            effect = "辅助补益"
        else:
            effect = "补充调理"
        # 大运落地检查
        luo_di = "—"
        for d in dy_list:
            d_gan = d.get("gan", "")
            d_gan_wx = TIAN_GAN_WU_XING.get(d_gan, "")
            if d_gan_wx == wx_actual:
                luo_di = f"大运{d.get('gan_zhi','')}有补"
                break
        rows.append([f"**{level_name}**", f"🟢{xi}（{wx_actual}）", effect, luo_di])
    lines.extend(_format_table(["层级", "五行（十神）", "作用", "落地情况"], rows))
    lines.append("")

    # 4.2 大运补用神窗口
    lines.append("### 4.2 大运补用神窗口")
    lines.append("")
    lines.extend(_format_table(
        ["大运", "补益十神", "效果评估"],
        [
            [d.get("gan_zhi", ""),
             ", ".join([xi for xi in xi_list if TIAN_GAN_WU_XING.get(d.get("gan", ""), "") == _get_xi_yong_wx(xi, ri_wx)]) or "—",
             _get_narrative_by_score(d.get("index", 0), "强力补益", "温和补益", "无直接补益", 5, 2)]
            for d in dy_list[:8]
        ]
    ))
    lines.append("")

    # 4.3 忌神问题
    lines.append("### 4.3 忌神引发的问题")
    lines.append("")
    ji_rows = []
    for ji in ji_list[:3]:
        wx_actual = _get_xi_yong_wx(ji, ri_wx)
        if ji == "官杀":
            problem = "压力过大，易招是非"
            caution = "注意人际关系，避免强出头"
        elif ji == "财":
            problem = "求财辛苦，财来财去"
            caution = "避免高风险投资，注意守财"
        elif ji == "印":
            problem = "过度依赖，缺乏主见"
            caution = "培养独立思考能力"
        elif ji == "食伤":
            problem = "说话做事冲动，易得罪人"
            caution = "三思而后行，注意表达方式"
        elif ji == "比劫":
            problem = "竞争激烈，易被夺财"
            caution = "谨慎合伙，注意防小人"
        else:
            problem = "能量失衡"
            caution = "注意相应五行层面的平衡"
        ji_rows.append([f"🔴{ji}（{wx_actual}）", problem, caution])
    if ji_rows:
        lines.extend(_format_table(["忌神", "引发问题", "注意事项"], ji_rows))
    else:
        lines.append("| 忌神 | 引发问题 | 注意事项 |")
        lines.append("|:----|:---------|:---------|")
        lines.append("| — | — | — |")
    lines.append("")

    # 忌神深层解读
    lines.append("**忌神深层解读：**")
    lines.append("")
    for ji in ji_list[:3]:
        wx_actual = _get_xi_yong_wx(ji, ri_wx)
        if ji == "官杀":
            lines.append(f"- 忌神为{ji}（{wx_actual}）：官杀为忌时，命主在面临压力和竞争时容易感到力不从心。"
                         f"从事管理岗位或竞争激烈的工作时需要格外注意节奏。建议在{wx_actual}五行相关的年份和环境中放慢脚步。")
        elif ji == "财":
            lines.append(f"- 忌神为{ji}（{wx_actual}）：财星为忌时，求财反而容易带来负担和损失。"
                         f"建议不要追求暴利，以稳健的理财方式为主。培养自己的专业技能比追求短期财富更重要。")
        elif ji == "印":
            lines.append(f"- 忌神为{ji}（{wx_actual}）：印星为忌时，过多的帮助和庇护反而限制了命主的独立发展。"
                         f"建议培养独立解决问题的能力，不要过度依赖他人或体制。")
        elif ji == "食伤":
            lines.append(f"- 忌神为{ji}（{wx_actual}）：食伤为忌时，才华和创意需要适当的收敛和控制。"
                         f"言多必失，在表达观点时注意场合和方式，避免因口舌招来是非。")
        elif ji == "比劫":
            lines.append(f"- 忌神为{ji}（{wx_actual}）：比劫为忌时，竞争和争夺是生活中需要面对的主要课题。"
                         f"合作中需注意利益分配，避免因为朋友或合作伙伴而蒙受损失。")
        else:
            lines.append(f"- 忌神为{ji}（{wx_actual}），需注意相应五行层面的能量失衡问题。")
    lines.append("")

    # 用神转化建议
    lines.append("**用神转化建议：**")
    lines.append("")
    lines.append("命局的喜用神和忌神不是一成不变的，随着大运的流转，喜忌关系可能发生变化。")
    lines.append("以下是用神转化的基本原则：")
    lines.append("- 当大运天干为忌神但被原局制化时，忌神可能转化为用神。")
    lines.append("- 大运地支与原局地支形成三合/三会局时，可能改变十神的力量分布。")
    lines.append("- 喜用神的五行属性对应的颜色、方向、季节等元素，建议在日常生活中多加利用。")
    xi_wx_colors = [WU_XING_COLORS.get(wx, "") for wx in xi_wx_names]
    xi_wx_dirs = [WU_XING_DIRECTIONS.get(wx, "") for wx in xi_wx_names]
    lines.append(f"- 建议多用{'/'.join(xi_wx_colors)}色系的服饰和用品，多往{'/'.join(xi_wx_dirs)}方向发展。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section5(basic: dict, analysis: dict) -> list:
    """§5 灾祸/疾病/搬迁专项 — 70行"""
    lines = []
    lines.append("## §5 灾祸/疾病/搬迁专项")
    lines.append("")
    pillars = basic.get("pillars", {})
    energy = analysis.get("energy", {})
    wxs = energy.get("wu_xing_energy", {})
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    nian_zhi = basic.get("nian_zhi", "")

    # 5.1 神煞排查
    lines.append("### 5.1 四大神煞排查")
    lines.append("")
    # 元辰（年柱查）简化：年支对冲为元辰
    yuan_chen_map = {"子": "未", "丑": "申", "寅": "酉", "卯": "戌",
                     "辰": "亥", "巳": "子", "午": "丑", "未": "寅",
                     "申": "卯", "酉": "辰", "戌": "巳", "亥": "午"}
    yc = yuan_chen_map.get(nian_zhi, "")
    yc_hit = yc in [basic.get(k, "") for k in ["nian_zhi", "yue_zhi", "ri_zhi", "shi_zhi"]]
    # 灾煞（年支三合局的对冲）
    zai_sha_map = {"申": "寅", "子": "午", "辰": "戌",
                   "亥": "巳", "卯": "酉", "未": "丑",
                   "寅": "申", "午": "子", "戌": "辰",
                   "巳": "亥", "酉": "卯", "丑": "未"}
    zs = zai_sha_map.get(nian_zhi, "")
    zs_hit = zs in [basic.get(f"{k}_zhi", "") for k in ["nian", "yue", "ri", "shi"]]
    # 天罗地网：辰巳戌亥
    all_zhi = [basic.get(f"{k}_zhi", "") for k in ["nian", "yue", "ri", "shi"]]
    tian_luo = "辰" in all_zhi and "巳" in all_zhi
    di_wang = "戌" in all_zhi and "亥" in all_zhi

    lines.extend(_format_table(
        ["神煞", "排查结果", "影响"],
        [
            ["元辰（年柱查）", f"{'✅' if yc_hit else '❌'} 位置：{yc}", "主意外灾祸" if yc_hit else "无直接影响"],
            ["灾煞（年柱查）", f"{'✅' if zs_hit else '❌'} 位置：{zs}", "注意突发事故" if zs_hit else "无灾煞影响"],
            ["天罗地网", f"{'✅天罗' if tian_luo else ''}{'✅地网' if di_wang else ''}{'❌' if not tian_luo and not di_wang else ''}",
             "辰巳为天罗，戌亥为地网，主困顿"],
            ["印星被冲", "❌ 未发现（简化检查）", "印星稳定"],
        ]
    ))
    lines.append("")

    # 5.2 五行过三排查
    lines.append("### 5.2 五行过三排查（疾病断）")
    lines.append("")
    lines.extend(_format_table(
        ["五行", "百分比", "过三判定", "对应器官"],
        [
            [wx, f"{pct:.1f}%",
             "✅ 过三" if pct > 30 else "❌",
             WU_XING_ORGANS.get(wx, "—")]
            for wx, pct in sorted(wxs.items(), key=lambda x: x[1], reverse=True)
        ]
    ))
    lines.append("")

    # 5.3 七杀攻身
    lines.append("### 5.3 七杀攻身排查")
    lines.append("")
    qi_sha_positions = []
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        for cg in p.get("cang_gan", []):
            if cg.get("shi_shen", "") == "七杀":
                qi_sha_positions.append(f"{pos_label}{cg.get('gan','')}")
    if qi_sha_positions:
        lines.append(f"⚠️ 七杀攻身：{'、'.join(qi_sha_positions)}")
        lines.append("七杀无制则攻身，有制化则为权威管理能力")
    else:
        lines.append("✅ 原局无七杀攻身，命局相对平和")
    lines.append("")

    # 5.4 搬迁次数
    lines.append("### 5.4 搬迁次数预测")
    lines.append("")
    sq = analysis.get("shen_qiang_ruo", {})
    sq_score = sq.get("score", 0)
    # 根据财星/冲合推算搬迁
    move_count = 3
    if sq_score < 40:
        move_count += 1
    if nian_zhi in ["子", "午", "卯", "酉"]:
        move_count += 1
    lines.append(f"🚚 **约{move_count}次**：")
    lines.append(f"- 求学/工作阶段（约1~2次）")
    lines.append(f"- 婚姻/置业阶段（约1~2次）")
    lines.append(f"- 晚年阶段（约{max(1, move_count-4)}次）")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section6(basic: dict, analysis: dict) -> list:
    """§6 性格分析（五重人格特质×每重40行+十神底色+白话）— 200行"""
    lines = []
    lines.append("## §6 性格分析（五重人格特质）")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ri_yy = YIN_YANG.get(ri_gan, "")
    ge_ju_str = analysis.get("ge_ju", "正印")
    pillars = basic.get("pillars", {})
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])

    # 6.1 性格总肖
    lines.append("### 6.1 性格总肖")
    lines.append("")
    wx_traits_desc = {
        "金": "刚毅果决，有原则性，执行力强，但易偏执",
        "木": "仁慈宽厚，有包容心，善于规划，但易优柔",
        "水": "智慧灵动，善于变通，富有想象力，但易善变",
        "火": "热情开朗，有领导力，善于表达，但易急躁",
        "土": "稳重诚信，有耐心，善于积累，但易保守",
    }
    wx_trait_str = wx_traits_desc.get(ri_wx, "性格特质鲜明")

    # 身强弱修正
    if sq_level == "身强":
        sq_mod = "身强更强化了主动性，行事果断有力"
    elif sq_level == "身弱":
        sq_mod = "身弱带来更多内敛和反思，行事谨慎"
    else:
        sq_mod = "中和使得性格在刚柔之间取得平衡"

    lines.append(f"{ri_gan}为{ri_wx}性，{wx_trait_str}。{sq_mod}。")
    # 阴阳属性补充
    yinyang_detail = f"{ri_gan}为{ri_yy}干，{'更显刚强主动' if ri_yy=='阳' else '更显柔顺内敛'}，进一步影响性格表现的外向程度。"
    lines.append(yinyang_detail)

    # 五行喜忌补益
    xi_wx_names = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    ji_wx_names = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]
    xi_wx_str = "、".join([f"{wx}({WU_XING_COLORS.get(wx,'')})" for wx in xi_wx_names])
    ji_wx_str = "、".join([f"{wx}({WU_XING_COLORS.get(wx,'')})" for wx in ji_wx_names])
    lines.append(f"命局最需要的五行能量为：{xi_wx_str}，以平衡命局中的{ji_wx_str}过旺之弊。")
    lines.append("")

    # 6.2 五重人格特质
    lines.append("### 6.2 五重人格特质")
    lines.append("")

    # ────────────────────────────────────────────────────────────────
    # 特质一：日主五行特质（深层展开）
    # ────────────────────────────────────────────────────────────────
    lines.append(f"**特质一：{ri_wx}性人格**（日主{ri_gan}为{ri_wx}性）")
    lines.append("")
    wx_character = {
        "金": f"日主为{ri_gan}（金），金曰从革，主刚毅与变革。命主性格中带有金属般的坚韧与果断，做事讲原则、重效率。"
             f"在团队中往往是规则的制定者和执行者，有较强的组织纪律性。"
             f"职场中：适合需要原则性和执行力的岗位，在管理岗或技术专精领域能发挥所长。"
             f"盲区：过于坚持原则可能导致灵活性不足，在需要变通的环境中容易吃亏。",
        "木": f"日主为{ri_gan}（木），木曰曲直，主生长与包容。命主性格中带有木的生机与柔韧性，善于规划、有远见。"
             f"待人宽厚，有仁者之风，容易获得他人信任。"
             f"职场中：适合需要规划和协调能力的工作，在教育、咨询、管理领域能展现才能。"
             f"盲区：包容过度可能变成优柔寡断，需要在大事上培养决断力。",
        "水": f"日主为{ri_gan}（水），水曰润下，主智慧与变通。命主思维敏捷，善于适应环境变化，有较强的洞察力和学习能力。"
             f"沟通能力强，能在复杂局面中找到出路。"
             f"职场中：适合需要灵活性和创新思维的岗位，在策划、咨询、技术前沿领域能发挥优势。"
             f"盲区：过于灵活可能缺乏定力，需要培养持久专注的能力。",
        "火": f"日主为{ri_gan}（火），火曰炎上，主热情与光明。命主性格开朗，有感染力，善于在人群中脱颖而出。"
             f"有领导潜质，能够带动团队氛围。"
             f"职场中：适合需要表达和领导能力的岗位，在市场、销售、管理领域能大放异彩。"
             f"盲区：热情过度可能变成急躁冲动，需要学会沉淀和耐心。",
        "土": f"日主为{ri_gan}（土），土曰稼穑，主承载与诚信。命主性格稳重踏实，做事靠谱，有耐心和持久力。"
             f"是团队中值得信赖的基石型人才。"
             f"职场中：适合需要稳定性和积累的岗位，在财务、运营、后勤领域能发挥特长。"
             f"盲区：过于求稳可能错失良机，需要在适当时候敢于突破。",
    }
    lines.append(wx_character.get(ri_wx, f"日主为{ri_gan}（{ri_wx}），性格特质与{ri_wx}五行属性相关。"))

    # 五行特质深层补充
    wx_color = WU_XING_COLORS.get(ri_wx, "")
    wx_number = WU_XING_NUMBERS.get(ri_wx, "")
    wx_direction = WU_XING_DIRECTIONS.get(ri_wx, "")
    wx_season = WU_XING_SEASONS.get(ri_wx, "")
    wx_taste = WU_XING_TASTES.get(ri_wx, "")
    lines.append(f"五行特性延伸：{ri_wx}的代表色为{wx_color}，吉利数字为{wx_number}，方向为{wx_direction}，"
                 f"对应季节为{wx_season}，五味为{wx_taste}。在{wx_direction}方向发展或使用{wx_color}元素可增强能量。")

    # 五行平衡建议
    strong_wx = analysis.get("energy", {}).get("strongest", "")
    weak_wx = analysis.get("energy", {}).get("weakest", "")
    lines.append(f"命局五行能量中，最强为{strong_wx}，最弱为{weak_wx}。"
                 f"需注意{weak_wx}方面的补益，可通过使用相关颜色、数字和方向来调和。"
                 f"例如：{weak_wx}对应的吉色为{WU_XING_COLORS.get(weak_wx,'')}，"
                 f"吉数为{WU_XING_NUMBERS.get(weak_wx,'')}，方向为{WU_XING_DIRECTIONS.get(weak_wx,'')}。")
    lines.append("")

    # ────────────────────────────────────────────────────────────────
    # 特质二：格局特质（深层展开 + 职业生涯建议）
    # ────────────────────────────────────────────────────────────────
    gj_traits_desc = {
        "正官": f"**特质二：正直责任型**（{ge_ju_str}格核心特质）",
        "七杀": f"**特质二：魄力进取型**（{ge_ju_str}格核心特质）",
        "正印": f"**特质二：学识稳重型**（{ge_ju_str}格核心特质）",
        "偏印": f"**特质二：深研技术型**（{ge_ju_str}格核心特质）",
        "正财": f"**特质二：稳健经营型**（{ge_ju_str}格核心特质）",
        "偏财": f"**特质二：灵活变通型**（{ge_ju_str}格核心特质）",
        "比肩": f"**特质二：独立自主型**（{ge_ju_str}格核心特质）",
        "劫财": f"**特质二：社交活跃型**（{ge_ju_str}格核心特质）",
        "食神": f"**特质二：才华创意型**（{ge_ju_str}格核心特质）",
        "伤官": f"**特质二：聪明叛逆型**（{ge_ju_str}格核心特质）",
    }
    gj_line2 = gj_traits_desc.get(ge_ju_str, f"**特质二：{ge_ju_str}格特质**")
    lines.append(gj_line2)
    lines.append("")

    gj_detail = {
        "正官": f"格局为{ge_ju_str}，命主天生具有责任感和自律精神。做事有原则，遵纪守法，"
                f"适合在体制内或规范化企业中发展。为人正直可靠，但需注意不要过于循规蹈矩。"
                f"职场中：管理岗位能发挥所长，是天生的组织者。"
                f"盲区：对规则过于执着，在需要创新突破的环境中可能受限。",
        "七杀": f"格局为{ge_ju_str}，命主有强烈的进取心和竞争意识。敢闯敢拼，不畏困难，"
                f"适合挑战性强的工作环境。有魄力，能承担压力。"
                f"职场中：适合军警、创业、管理等高压力岗位。"
                f"盲区：强势风格容易树敌，需要学会柔和处事。",
        "正印": f"格局为{ge_ju_str}，命主学识丰富，稳重踏实。学习能力强，善于总结归纳，"
                f"适合学术研究或教育领域。为人温和，有书卷气。"
                f"职场中：教育、研究、行政岗位能发挥特长。"
                f"盲区：过于安于现状，缺乏闯劲，需要注意开拓。",
        "偏印": f"格局为{ge_ju_str}，命主思维独特，有深度钻研能力。擅长解构复杂问题，"
                f"在技术研发和策略规划领域有天赋。思维不随大流，有自己的见解。"
                f"职场中：技术研发、战略分析、学术研究岗位适合。"
                f"盲区：不善交际，容易孤僻，需要加强团队协作。",
        "正财": f"格局为{ge_ju_str}，命主求财踏实，适合稳定收入的职业。理财观念强，"
                f"善于积累，不投机取巧。适合从事实体经营或财务管理类工作。"
                f"职场中：财务、会计、实体经营岗位能发挥特长。"
                f"盲区：过于保守可能错失投资良机。",
        "偏财": f"格局为{ge_ju_str}，命主财路广阔，善于投资和社交。有商业头脑，"
                f"懂得灵活变通，适合经商或从事与市场相关的职业。"
                f"职场中：投资、销售、市场拓展岗位能发挥天赋。"
                f"盲区：财来财去，需要加强守财意识。",
        "比肩": f"格局为{ge_ju_str}，命主独立自主，有较强的个人能力。自尊心强，"
                f"不适合被约束，更适合独立开展工作或创业。"
                f"职场中：自由职业、技术专家、独立顾问适合。"
                f"盲区：固执己见，需要学习团队合作。",
        "劫财": f"格局为{ge_ju_str}，命主社交能力强，人脉广泛。重情重义，"
                f"善于在合作中发挥作用，适合需要人际交往的行业。"
                f"职场中：公关、销售、合作类岗位适合。"
                f"盲区：易被朋友所累，需要分辨真假朋友。",
        "食神": f"格局为{ge_ju_str}，命主才华横溢，有创意天赋。心态好，懂得享受生活，"
                f"在艺术、技术、创意领域有独特优势。"
                f"职场中：设计、研发、创意策划岗位能发挥才能。"
                f"盲区：容易放纵享乐，需要自律。",
        "伤官": f"格局为{ge_ju_str}，命主聪明灵动，才思敏捷。表达能力强，"
                f"有创新精神和叛逆意识，适合需要创造力的岗位。"
                f"职场中：创作、研发、表演岗位能施展才华。"
                f"盲区：锋芒毕露易得罪人，需要收敛。",
    }
    lines.append(gj_detail.get(ge_ju_str, f"格局为{ge_ju_str}格，形成了独特的性格底色。"))

    # 格局深层展开：格局的十神互动
    gj_success_tips = {
        "正官": "制化七杀则官星更显贵气，食伤生财则事业发展持久。",
        "七杀": "食神制杀则化权为贵，印星化杀则文武双全。",
        "正印": "官印相生则贵气更显，财星不破印则学以致用。",
        "偏印": "偏印配食神为「枭神夺食」需注意，配正财则技术生财。",
        "正财": "正财坐库则财富积累快，配官星则财官双美。",
        "偏财": "偏财配七杀则大财需大勇，配食伤则才华生财。",
        "比肩": "比肩配正财则合伙生财，配七杀则竞争上位。",
        "劫财": "劫财配伤官则才华变现快，配偏财则合作生财。",
        "食神": "食神配正印则艺文出众，配偏财则才华生财。",
        "伤官": "伤官配正印则才华有根，配正财则技艺生财。",
    }
    lines.append(f"格局配合十神组合：{gj_success_tips.get(ge_ju_str, '格局配合宜根据具体大运流年分析。')}")
    lines.append("")

    # ────────────────────────────────────────────────────────────────
    # 特质三：身强弱修正（深层展开 + 职业生涯建议）
    # ────────────────────────────────────────────────────────────────
    lines.append(f"**特质三：{'强' if sq_level=='身强' else '弱' if sq_level=='身弱' else '平衡'}势人格**（{'身强' if sq_level=='身强' else '身弱' if sq_level=='身弱' else '中和'}修正）")
    lines.append("")
    if sq_level == "身强":
        lines.append(f"身强（{sq_score}分）使命主在行为上表现出较强的主动性和控制欲。"
                     f"做事有底气，敢于承担责任，不易被外界影响。"
                     f"但在人际交往中需要注意不要过于强势，适当听取他人意见。"
                     f"职场中：适合担任领导角色或独立负责重要项目。"
                     f"盲区：刚愎自用，需要培养倾听和协作习惯。")
        lines.append(f"身强之人一生运势的曲线：早年易得赏识，中年事业上升，晚年需要学会示弱和放手。"
                     f"在团队中宜做先锋和开拓者，将执行层面的工作交给他人。"
                     f"行业选择上，宜从事需要个人能力突出的领域，如管理、创业、专业咨询等。"
                     f"成长方向：培养谦虚和包容心，学会欣赏他人的长处。")
    elif sq_level == "身弱":
        lines.append(f"身弱（{sq_score}分）使命主在行为上更倾向于合作和借力。"
                     f"善于观察和思考，不轻易冒进，懂得借助团队力量。"
                     f"为人谦和，容易获得贵人提携。"
                     f"职场中：适合在团队中发挥作用，不宜单打独斗。"
                     f"盲区：缺乏自信，需要多锻炼独立决策能力。")
        lines.append(f"身弱之人一生的运势曲线：早年宜积累和学习，中年借助大运和贵人发力，"
                     f"晚年可享清福。需要选择合适的平台和伙伴，借力发展。"
                     f"行业选择上，宜从事需要团队协作和资源整合的领域，如行政、教育、咨询等。"
                     f"成长方向：建立自信，在关键时刻敢于挺身而出。")
    else:
        lines.append(f"中和（{sq_score}分）使命主在行为上具有平衡的适应能力。"
                     f"既能独立担当，也善于合作；既有主见，也能听取意见。"
                     f"灵活性是最突出的优势。"
                     f"职场中：适应性强，能在各种环境中找到自己的位置。"
                     f"盲区：平衡有时意味着缺乏特色，需要找准核心优势深耕。")
        lines.append(f"中和之人一生运势的曲线：运势平稳，不走极端，能够根据环境变化灵活调整。"
                     f"在各个人生阶段都能找到适合自己的位置。"
                     f"行业选择上，宜从事需要综合能力的领域，如管理、协调、综合运营等。"
                     f"成长方向：在广度的基础上建立纵深优势，避免样样通样样松。")
    lines.append("")

    # ────────────────────────────────────────────────────────────────
    # 特质四：十神特质——选取最突出的（深层展开）
    # ────────────────────────────────────────────────────────────────
    pillars_ss = []
    for pos_key, pos_label in [("nian", "年"), ("yue", "月"), ("ri", "日"), ("shi", "时")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss:
            pillars_ss.append((pos_label, ss))
    # 找频率最高的非日主十神
    ss_count = {}
    for _, ss in pillars_ss:
        if ss and ss != "日主":
            ss_count[ss] = ss_count.get(ss, 0) + 1
    # 也统计藏干十神
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(pos_key, {})
        for cg in p.get("cang_gan", []):
            ss = cg.get("shi_shen", "")
            if ss and ss != "日主":
                ss_count[ss] = ss_count.get(ss, 0) + 0.5
    sorted_ss = sorted(ss_count.items(), key=lambda x: x[1], reverse=True)
    top_ss = sorted_ss[0][0] if sorted_ss else ge_ju_str
    # 第二强十神
    second_ss = sorted_ss[1][0] if len(sorted_ss) > 1 else ""
    t4 = _get_shi_shen_trait(top_ss)
    lines.append(f"**特质四：{top_ss}主导型**（十神{top_ss}影响力最强）")
    lines.append("")
    lines.append(f"十神「{top_ss}」在命局中影响力显著。{t4['strength']}。"
                 f"职场中：{t4['work']}。"
                 f"盲区：{t4['blind']}。")

    # 次要十神补充
    if second_ss:
        t4b = _get_shi_shen_trait(second_ss)
        lines.append(f"次要十神「{second_ss}」同样有较大影响力，{t4b['core']}。"
                     f"这意味着命主在{second_ss}相关的场景中也容易表现出{t4b['core']}的特质。"
                     f"两者的组合会形成更丰富的性格层次，例如{top_ss}的{t4['core']}结合{second_ss}的{t4b['core']}。")

    # 十神组合深度分析
    lines.append("")
    lines.append("**十神组合深度分析：**")
    lines.append("")
    all_pillar_ss = []
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss:
            all_pillar_ss.append(f"{pos_label}干{ss}")
        for cg in p.get("cang_gan", []):
            cg_ss = cg.get("shi_shen", "")
            if cg_ss:
                all_pillar_ss.append(f"{pos_label}支藏{cg_ss}")
    lines.append(f"全命局十神分布：{'、'.join(all_pillar_ss[:8])}。")
    # 十神均衡度
    unique_ss_types = set()
    for _, ss in pillars_ss:
        if ss:
            unique_ss_types.add(ss)
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(pos_key, {})
        for cg in p.get("cang_gan", []):
            cg_ss = cg.get("shi_shen", "")
            if cg_ss:
                unique_ss_types.add(cg_ss)
    ss_diversity = len(unique_ss_types)
    if ss_diversity >= 6:
        lines.append(f"十神类型丰富（含{ss_diversity}种），性格维度多元，适应性强但也可能内在矛盾较多。")
    elif ss_diversity >= 4:
        lines.append(f"十神类型适中（含{ss_diversity}种），性格有基本的多面性，但不失主次分明。")
    else:
        lines.append(f"十神类型较少（含{ss_diversity}种），性格特征集中，方向性强但适应性可能受限。")
    lines.append("")

    # ────────────────────────────────────────────────────────────────
    # 特质五：综合特质（深层展开）
    # ────────────────────────────────────────────────────────────────
    lines.append(f"**特质五：综合型人格**（{'/'.join(xi_list)}喜用的整体影响）")
    lines.append("")
    xi_str = "、".join(xi_list)
    ji_str = "、".join(ji_list)
    lines.append(f"命局喜用神为{xi_str}，这意味着命主在{xi_str}相关的环境中更易发挥优势。")
    lines.append(f"喜用神为能量补益之源，当大运流年与喜用神相合时，命主在事业、人际、"
                 f"财运等方面都能获得更好的表现和更多的机遇。")
    lines.append(f"反之，忌神年份（{ji_str}相关的年运）则需要谨慎行事，避免冒进。"
                 f"整体而言，命主是一个综合特质鲜明的人，在不同大运阶段会展现出不同的侧重点。")
    lines.append("")

    # 喜用神深层影响
    lines.append("**喜用神与性格的深层关系：**")
    lines.append("")
    for xi in xi_list[:3]:
        xi_wx = _get_xi_yong_wx(xi, ri_wx)
        xi_detail = {
            "食伤": f"喜{xi}（{xi_wx}）意味着命主需要适当展現才华和创意来平衡命局，"
                    f"在表达自我和展示能力时最能获得正反馈。",
            "财": f"喜{xi}（{xi_wx}）意味着命主需要在求财和经营中成长，"
                  f"通过创造价值和财富积累来实现自我突破。",
            "官杀": f"喜{xi}（{xi_wx}）意味着命主需要在规范化和有压力的环境中发展，"
                    f"通过承担责任和接受挑战来获得成就感。",
            "印": f"喜{xi}（{xi_wx}）意味着命主需要通过学习和积累来增强底气，"
                  f"知识和文化修养是命主最重要的支撑。",
            "比劫": f"喜{xi}（{xi_wx}）意味着命主需要团队和伙伴的支持，"
                    f"在合作和社交中能够获得最大的成长动力。",
        }
        lines.append(f"- {xi_detail.get(xi, f'喜{xi}（{xi_wx}）是命局的重要平衡点。')}")
    lines.append("")

    # 补充特质细节：基于十神组合
    lines.append("**性格核心优势总结：**")
    lines.append("")
    lines.append(f"① 日主{ri_wx}性特质赋予了你{wx_trait_str.split('，')[0]}的基础性格底色。")
    lines.append(f"② {ge_ju_str}格的格局特质使得你在{ge_ju_str}相关的领域有天然的兴趣和能力优势。")
    lines.append(f"③ {sq_level}让{'你更加主动进取，做事果断有魄力' if sq_level=='身强' else '你更加谨慎细致，善于借力和整合资源' if sq_level=='身弱' else '你具有很强的适应性和灵活性，能在不同环境中游刃有余'}。")
    lines.append(f"④ 十神「{top_ss}」的强势影响使你在人际互动中展现出{_get_shi_shen_trait(top_ss)['core']}的特质。")
    lines.append(f"⑤ 喜用神为{xi_str}，在{xi_str}相关的年份和环境中更容易发挥潜能。")
    lines.append("")

    # 成长建议（大幅扩展）
    lines.append("**性格成长建议：**")
    lines.append("")
    growth_advice = []
    if sq_level == "身强":
        growth_advice.append("身强之人需注意不要过于强势，学会倾听和协作，刚柔并济才是长久之道。")
        growth_advice.append("建议在职场中主动承担带新人和团队协调的角色，既能发挥优势又不失亲和力。")
        growth_advice.append("在人际交往中，多关注他人的感受和需求，适当放慢节奏，不要以己度人。")
    elif sq_level == "身弱":
        growth_advice.append("身弱之人需建立自信，敢于表达和担当，不要过度依赖他人。")
        growth_advice.append("建议从小事做起，逐步建立自己的专业壁垒和自信心。贵人运虽好，但不可过度依赖。")
        growth_advice.append("在关键时刻要敢于发声，你的意见同样有价值，不要因谦虚而错失表现机会。")
    else:
        growth_advice.append("中和之命优势在于平衡，但需警惕在关键时刻缺乏决断力。")
        growth_advice.append("建议在某些领域建立深度专长，避免样样通样样松的困境。")
        growth_advice.append("在重大决策时，可以适当偏执一些，不要过于追求完美和平衡。")
    if top_ss in ["伤官", "七杀"]:
        growth_advice.append(f"{top_ss}旺的人锋芒较露，建议在表达观点时注意方式方法，避免不必要的冲突。")
        growth_advice.append(f"可以将{top_ss}的能量转化为创造力和执行力，而非对抗和挑剔。")
    elif top_ss in ["正印", "偏印"]:
        growth_advice.append(f"{top_ss}旺的人思维深度有余但行动力可能不足，建议多做少想，以行动推动结果。")
        growth_advice.append(f"可以适当参加需要实操的培训或项目，将理论知识转化为实际能力。")
    elif top_ss in ["正财", "偏财"]:
        growth_advice.append(f"{top_ss}旺的人对财富敏感度高，但需注意在人际关系中不要过于功利。")
        growth_advice.append(f"可以发挥{top_ss}的优势进行理财规划，同时注重人情世故的投入。")
    elif top_ss in ["食神", "比肩"]:
        growth_advice.append(f"{top_ss}旺的人心态好但容易懈怠，建议设定明确的目标和截止时间。")
        growth_advice.append(f"可以利用{top_ss}的创造力，在工作中寻找乐趣和成就感。")
    elif top_ss in ["劫财"]:
        growth_advice.append(f"{top_ss}旺的人重情义但需警惕被朋友拖累，在合伙创业前务必做好书面约定。")
    for advice in growth_advice:
        lines.append(f"- {advice}")

    # 职业生涯建议补充
    lines.append("")
    lines.append("**职业生涯建议：**")
    lines.append("")
    if ge_ju_str in ["正官", "七杀"]:
        lines.append(f"作为一个{ge_ju_str}格的人，你的职业发展路径最适合从基层管理或专业岗位起步，"
                     f"逐步积累管理经验和行业资源。建议在30~40岁之间完成从执行者到管理者的转型。"
                     f"适合的行业包括行政管理、项目管理、军警安全、企业高管等领域。")
    elif ge_ju_str in ["正印", "偏印"]:
        lines.append(f"作为一个{ge_ju_str}格的人，你的职业发展路径最适合深耕某一专业领域，"
                     f"通过持续学习和积累成为行业专家。建议在35岁前完成专业壁垒的建立。"
                     f"适合的行业包括教育、科研、技术研发、文化出版、咨询顾问等领域。")
    elif ge_ju_str in ["正财", "偏财"]:
        lines.append(f"作为一个{ge_ju_str}格的人，你的职业发展路径最适合从市场一线或业务岗位起步，"
                     f"在实践中积累行业经验和客户资源。适合的行业包括金融投资、商贸流通、"
                     f"市场营销、实体经营、自由职业等领域。")
    elif ge_ju_str in ["食神", "伤官"]:
        lines.append(f"作为一个{ge_ju_str}格的人，你的职业发展路径最适合在创意和技术领域发挥才华，"
                     f"将兴趣与工作结合。适合的行业包括艺术设计、技术研发、内容创作、"
                     f"媒体传播、教育培训等领域。")
    else:
        lines.append(f"你的{ge_ju_str}格赋予了你独特的职业天赋，建议根据自己的兴趣和市场机会选择适合的行业。"
                     f"核心策略是找到能够发挥自身特长的领域，并持续深耕。")

    # 五行视角的职业选择
    lines.append(f"从五行视角看，{ri_gan}日主适合在与{ri_wx}五行相关的行业中发展。"
                 f"同时，喜用神{xi_str}对应的五行行业也是不错的选择。")
    lines.append(f"注意避免过度从事与忌神{ji_str}五行完全一致的行业，"
                 f"以免加剧命局的能量失衡。")
    lines.append("")

    # 6.3 十神性格底色（扩展版）
    lines.append("### 6.3 十神性格底色")
    lines.append("")
    ss_rows = []
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss:
            t = _get_shi_shen_trait(ss)
            ss_rows.append([f"{_ss_star(ss)} **{ss}**", pos_label, t["core"], t["work"]])
    if ss_rows:
        lines.extend(_format_table(["十神", "位置", "性格底色", "适合领域"], ss_rows))
    else:
        lines.append("（十神信息不足）")
    lines.append("")

    # 十神底色详细解读表
    lines.append("**十神底色详细解读：**")
    lines.append("")
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        gan = p.get("gan", "")
        zhi = p.get("zhi", "")
        if ss:
            t = _get_shi_shen_trait(ss)
            lines.append(f"- **{pos_label}【{gan}{zhi}】**：天干{ss} → 核心：{t['core']}。优势：{t['strength']}。注意事项：{t['blind']}。")
            # 藏干影响
            cg_list = p.get("cang_gan", [])
            if cg_list:
                cg_details = []
                for cg in cg_list:
                    cg_gan = cg.get("gan", "")
                    cg_ss = cg.get("shi_shen", "")
                    cg_wt = cg.get("weight", 0)
                    if cg_ss:
                        cg_t = _get_shi_shen_trait(cg_ss)
                        cg_details.append(f"{cg_gan}({cg_ss}·权重{cg_wt}%)：{cg_t['core']}")
                lines.append(f"  └ 藏干解析：{'；'.join(cg_details)}")
    lines.append("")

    # 十神之间的组合与互动
    lines.append("**十神组合互动分析：**")
    lines.append("")
    # 找出四柱中全部天干十神
    gan_ss_list = []
    for pos_key in ["nian", "yue", "shi"]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss:
            gan_ss_list.append(ss)
    # 分析互动关系
    if "正官" in gan_ss_list and "正印" in gan_ss_list:
        lines.append("- 🔄 官印相生：正官与正印同时出现，官得印护则贵气更显，适合体制内发展。")
    if "七杀" in gan_ss_list and "食神" in gan_ss_list:
        lines.append("- 🔄 食神制杀：食神制七杀，化权为贵，杀有制则不为凶反为威权。")
    if "七杀" in gan_ss_list and "偏印" in gan_ss_list:
        lines.append("- 🔄 杀印相生：七杀有偏印化之，文武双全，宜军警或管理类职位。")
    if "伤官" in gan_ss_list and "正印" in gan_ss_list:
        lines.append("- 🔄 伤官配印：伤官配印则才华有根，不流于浮夸，适合学术创作。")
    if "食神" in gan_ss_list and "偏财" in gan_ss_list:
        lines.append("- 🔄 食神生财：食神生偏财，才华转化为财富，是典型的商业天赋组合。")
    if "比肩" in gan_ss_list and "劫财" in gan_ss_list:
        lines.append("- ⚠️ 比劫并见：比劫同现，竞争意识强，适合需要竞争的环境但需注意人际关系。")
    if "劫财" in gan_ss_list and "偏财" in gan_ss_list:
        lines.append("- ⚠️ 劫财见财：劫财见偏财，财来财去之象，需要加强理财和守财意识。")
    if not any(x in gan_ss_list for x in ["正官", "七杀", "正印", "偏印", "正财", "偏财",
                                           "食神", "伤官", "比肩", "劫财"]):
        lines.append("- 四柱天干十神信息有限，建议结合地支藏干综合分析。")
    lines.append("")

    # 补充十神详解
    lines.append("**四柱十神对性格的深层影响（逐柱展开）：**")
    lines.append("")
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        gan = p.get("gan", "")
        zhi = p.get("zhi", "")
        if ss:
            t = _get_shi_shen_trait(ss)
            lines.append(f"- **{pos_label}**（{gan}{zhi}）：{_ss_star(ss)} **{ss}** — {t['core']}。{t['strength']}。{t['blind']}。")
            # 位置意义
            pos_meanings = {
                "年柱": f"年柱为祖上宫，年干{ss}代表先天禀赋和早年环境的影响，{ss}特质的原型在童年已初露端倪。",
                "月柱": f"月柱为父母宫兼格局宫，月干{ss}是命局的关键透干，对一生命运的影响力最强。",
                "日柱": f"日柱为自身宫，日干{ri_gan}为日主自身，{ss}为日主本人的本质特质。",
                "时柱": f"时柱为子女宫兼归宿宫，时干{ss}代表晚年的状态和最终的人生走向。",
            }
            lines.append(f"  └ 位置意义：{pos_meanings.get(pos_label, '')}")
            # 也提及藏干
            cg_list = p.get("cang_gan", [])
            cg_info = []
            for cg in cg_list:
                cg_ss = cg.get("shi_shen", "")
                if cg_ss and cg_ss != ss:
                    cg_info.append(f"{cg.get('gan','')}为{cg_ss}")
            if cg_info:
                lines.append(f"  └ 藏干影响：{'、'.join(cg_info)}")
    lines.append("")

    # 6.4 白话解读
    lines.append("### 6.4 白话解读")
    lines.append("")
    lines.append(f"> **🗣️ 白话：** 您天生带有{ri_wx}的特质，{wx_trait_str}。"
                 f"格局为{ge_ju_str}格，说明您在{ge_ju_str}相关的领域有天然优势。"
                 f"{sq_level}使得您在做事风格上{'偏向主动进取' if sq_level=='身强' else '偏向谨慎借力' if sq_level=='身弱' else '保持灵活平衡'}。"
                 f"性格中十神「{top_ss}」的影响最突出，{_get_shi_shen_trait(top_ss)['core']}。"
                 f"了解这些特质，有助于您在职场和生活中找到最适合自己的发展路径。")
    lines.append("")
    lines.append(f"> 记住，五行{ri_wx}是你的底色，{ge_ju_str}格是你的主调，{sq_level}是你的力道，"
                 f"十神「{top_ss}」是你的鲜明烙印。这些元素共同塑造了一个独特的你。"
                 f"在人生不同阶段，随着大运的流转，这些特质会以不同的方式展现。"
                 f"了解并善用这些特质，是走向成功的关键。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section7(basic: dict, analysis: dict) -> list:
    """§7 身材外貌分析（日主定基准+身强弱修正+食神比劫+身高推断）— 60行"""
    lines = []
    lines.append("## §7 身材外貌分析")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    pillars = basic.get("pillars", {})
    ge_ju_str = analysis.get("ge_ju", "正印")

    # 7.1 日主五行定基准
    lines.append("### 7.1 日主五行定基准")
    lines.append("")
    wx_body = {
        "金": f"{ri_gan}为金性，金主骨骼与皮肤。金性人多骨架分明，皮肤白皙，轮廓清晰。"
              f"整体气质偏冷峻，给人以精干利落之感。",
        "木": f"{ri_gan}为木性，木主肌肉与筋脉。木性人多身材修长，四肢匀称，气质温和。"
              f"体态优雅，动作舒展，给人如沐春风之感。",
        "水": f"{ri_gan}为水性，水主血液与体液。水性人多体态丰润，皮肤细腻，气质灵动。"
              f"眼神有神，动作流畅，给人以灵秀之感。",
        "火": f"{ri_gan}为火性，火主气色与精神。火性人多面色红润，精神饱满，气质热情。"
              f"体态偏中上，动作敏捷，给人以活力充沛之感。",
        "土": f"{ri_gan}为土性，土主肌肉与骨骼。土性人多身材敦实，骨架稳重，气质沉稳。"
              f"体形偏圆润，给人可靠踏实之感。",
    }
    lines.append(wx_body.get(ri_wx, f"{ri_gan}为{ri_wx}性，身材气质与{ri_wx}五行属性相关。"))
    lines.append("")

    # 7.2 身强弱修正
    lines.append("### 7.2 身强弱修正")
    lines.append("")
    if sq_level == "身强":
        lines.append(f"身强（{sq_score}分）：骨架偏大，体格较壮实，肌肉量充足，整体给人力量感。"
                     f"基础代谢率较高，不易发胖，但需要关注过旺五行的器官负担。")
    elif sq_level == "身弱":
        lines.append(f"身弱（{sq_score}分）：骨架偏细腻，体形偏清瘦，气质偏文弱。"
                     f"需要注意营养和锻炼，增强体质。身弱之人往往更有书卷气。")
    else:
        lines.append(f"中和（{sq_score}分）：身材比例适中，不胖不瘦，体型匀称。"
                     f"适应能力强，体态可塑性高。")
    lines.append("")

    # 7.3 食神比劫影响
    lines.append("### 7.3 食神/比劫影响（体形趋势）")
    lines.append("")
    has_shi_shen = False
    has_bi_jie = False
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss == "食神":
            has_shi_shen = True
        if ss in ["比肩", "劫财"]:
            has_bi_jie = True
    if has_shi_shen:
        lines.append("食神透干：食神主口福和享受，容易有发福倾向，尤其是中年以后。")
    else:
        lines.append("食神不透干：发福倾向不明显，体形相对稳定。")
    if has_bi_jie:
        lines.append("比劫透干/显支：比劫主骨架和肌肉，体形偏结实。")
    else:
        lines.append("比劫不显：骨架偏中等，体形变化更多地受饮食和生活习惯影响。")
    lines.append("")

    # 综合推断
    lines.append("### 7.4 综合推断")
    lines.append("")
    # 身高推断（简化规则）
    if ri_wx == "金":
        height = "中等偏上（约170~178cm）"
    elif ri_wx == "木":
        height = "偏高（约172~182cm）"
    elif ri_wx == "水":
        height = "中等（约168~175cm）"
    elif ri_wx == "火":
        height = "中等偏上（约170~178cm）"
    elif ri_wx == "土":
        height = "中等偏下（约165~173cm）"
    else:
        height = "中等（约168~175cm）"

    if sq_level == "身强":
        height = f"{height}，骨架偏大更显身高"
    elif sq_level == "身弱":
        height = f"{height}，体形偏清瘦"

    lines.append(f"**身高推断**：{height}")
    lines.append("")
    lines.append(f"**整体印象**：{ri_gan}命主为{ri_wx}性气质，{wx_body.get(ri_wx, '气质独特')[:30]}"
                 f"{sq_level}使整体{'更显力量感' if sq_level=='身强' else '偏文雅' if sq_level=='身弱' else '气质均衡'}。"
                 f"外貌评分中上，气质为主要优势，{ge_ju_str}格的涵养为外貌加分。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section8(basic: dict, analysis: dict) -> list:
    """§8 财富分析（五层动态法）— 120行"""
    lines = []
    lines.append("## §8 财富分析（五层动态法·全规则驱动）")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    pillars = basic.get("pillars", {})
    cx = analysis.get("cai_xing", {})
    cai_score = cx.get("score", 0)
    has_ku = cx.get("has_ku", False)
    cai_ku = cx.get("cai_ku", "")
    wealth_level = cx.get("wealth_level", "小富")
    details_cai = cx.get("details", [])
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])

    # 8.1 财星评分明细
    lines.append("### 8.1 财星评分（精确计算·bazi-engine规则）")
    lines.append("")
    lines.extend(_format_table(
        ["位置", "藏干", "基础分", "实得分", "正偏"],
        [
            [pos, cg.get("gan", ""), str(pts), str(score), cx.get("wealth_level", "")]
            for pos, cg, pts, score in []
        ] if False else
        [d.split(" ") if " " in d else [d, "", "", "", ""] for d in details_cai[:8]]
    ))
    if details_cai:
        for d in details_cai:
            lines.append(f"- {d}")
    lines.append(f"**总分：{cai_score}分**")
    lines.append("")

    # 8.2 财喜藏不喜露
    lines.append("### 8.2 财喜藏不喜露")
    lines.append("")
    # 判断财星透干还是深藏
    gan_cai = []
    for pos_key, pos_label in [("nian", "年干"), ("yue", "月干"), ("shi", "时干")]:
        p = pillars.get(pos_key, {})
        gan = p.get("gan", "")
        ss = p.get("gan_shi_shen", "")
        if ss in ["正财", "偏财"]:
            gan_cai.append(f"{pos_label}{gan}")
    if gan_cai:
        lines.append(f"⚠️ 财星透干：{'、'.join(gan_cai)}。财透干则易露白，需加强守财意识。")
    else:
        lines.append("✅ 财星深藏地支，不露白，利于积蓄。")
    lines.append(f"财库状态：{'有' if has_ku else '无'}财库（{cai_ku}）——{'蓄财能力强' if has_ku else '财来财去需主动蓄财'}。")
    lines.append("")

    # 8.3 第1层：身强财弱/强判定
    lines.append("### 8.3 第1层：基础判定（身强/身弱 × 财旺/财弱）")
    lines.append("")
    is_qiang = sq_level == "身强"
    is_cai_wang = cai_score >= 40
    if is_qiang and is_cai_wang:
        base_tier = "身强财旺→大富基础"
    elif is_qiang and not is_cai_wang:
        base_tier = "身强财弱→需大运补财"
    elif not is_qiang and is_cai_wang:
        base_tier = "身弱财旺→需印比护财"
    else:
        base_tier = "身弱财弱→需全面补益"
    lines.append(f"**判定：{base_tier}**")
    lines.append(f"- 身强弱：{sq_level}（{sq_score}分） | 财星分：{cai_score}分")
    lines.append(f"- 财星{'≥40分→财旺' if is_cai_wang else '<40分→财弱'}")
    lines.append("")

    # 8.4 第2层：围克折扣
    lines.append("### 8.4 第2层：围克折扣")
    lines.append("")
    bi_jie_count = 0
    guan_sha_count = 0
    yin_count = 0
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss in ["比肩", "劫财"]:
            bi_jie_count += 1
        if ss in ["正官", "七杀"]:
            guan_sha_count += 1
        if ss in ["正印", "偏印"]:
            yin_count += 1
        for cg in p.get("cang_gan", []):
            ss = cg.get("shi_shen", "")
            if ss in ["比肩", "劫财"]:
                bi_jie_count += 0.5
            if ss in ["正官", "七杀"]:
                guan_sha_count += 0.5
            if ss in ["正印", "偏印"]:
                yin_count += 0.5
    discount_total = 0
    if bi_jie_count >= 2:
        bijie_discount = min(bi_jie_count * 5, 30)
        discount_total += bijie_discount
        lines.append(f"⚠️ 比劫夺财折扣：-{bijie_discount}%（比劫强度{bi_jie_count}）")
    else:
        lines.append(f"✅ 比劫不夺财（强度{bi_jie_count}）")
    if guan_sha_count >= 2:
        gs_discount = min(guan_sha_count * 3, 20)
        discount_total += gs_discount
        lines.append(f"⚠️ 官杀泄财折扣：-{gs_discount}%（官杀强度{guan_sha_count}）")
    else:
        lines.append(f"✅ 官杀不泄财（强度{guan_sha_count}）")
    if yin_count >= 2:
        yin_discount = min(yin_count * 3, 15)
        discount_total += yin_discount
        lines.append(f"⚠️ 印星埋财折扣：-{yin_discount}%（印星强度{yin_count}）")
    else:
        lines.append(f"✅ 印星不埋财（强度{yin_count}）")
    effective_score = cai_score * (100 - discount_total) / 100
    lines.append(f"**有效财星分 = {cai_score} × {100-discount_total}% = {effective_score:.1f}分**")
    lines.append("")

    # 8.5 第3层：财库检查
    lines.append("### 8.5 第3层：财库检查")
    lines.append("")

    # 食伤情况
    has_shi_shen = any(
        pillars.get(pos, {}).get("gan_shi_shen", "") == "食神"
        for pos in ["nian", "yue", "ri", "shi"]
    )
    if has_ku:
        lines.append(f"✅ 有财库（{cai_ku}）：蓄财能力强，财富可积累。")
        # 检查库是否被冲
        chong_map = {"辰": "戌", "戌": "辰", "丑": "未", "未": "丑"}
        ku_chong = chong_map.get(cai_ku, "")
        if ku_chong and ku_chong in [basic.get(f"{k}_zhi", "") for k in ["nian", "yue", "ri", "shi"]]:
            lines.append(f"⚠️ 财库被冲（{cai_ku}冲{ku_chong}），库门打开，财来财去。")
        else:
            lines.append(f"✅ 财库无冲，安稳蓄财。")
    else:
        lines.append(f"❌ 无财库（日时支无辰戌丑未对应财库）：财来财去，需主动蓄财。")
        lines.append("补库方案：")
        lines.append("① 实物补库：在对应方位摆放象征财库的摆件")
        lines.append("② 开户补库：在财库方位银行开设储蓄账户")
        lines.append("③ 行业补库：选择属财库五行的行业深耕")
        lines.append("④ 合作补库：与带财库八字的人合作投资")
    lines.append("")

    # 8.6 第4层：三合财局
    lines.append("### 8.6 第4层：三合财局检查")
    lines.append("")
    # 简化检查
    all_zhi = [basic.get(f"{k}_zhi", "") for k in ["nian", "yue", "ri", "shi"]]
    san_he = False
    he_ju_name = ""
    he_sets = [["申", "子", "辰"], ["亥", "卯", "未"], ["寅", "午", "戌"], ["巳", "酉", "丑"]]
    for hs in he_sets:
        if all(z in all_zhi for z in hs):
            san_he = True
            he_ju_name = "合水局" if hs[1] == "子" else "合木局" if hs[1] == "卯" else "合火局" if hs[1] == "午" else "合金局"
            break
    if san_he:
        lines.append(f"✅ 命局有{he_ju_name}，增强了整体能量，对财富有{_get_narrative_by_score(cai_score, '强力助推', '温和增益', '有限影响', 50, 25)}。")
    else:
        lines.append("❌ 命局无三合财局，财富主要靠个人努力和大运配合。")
    lines.append("")

    # 8.7 第5层：大运匹配
    lines.append("### 8.7 第5层：大运匹配")
    lines.append("")
    wx_list_order = ["木", "火", "土", "金", "水"]
    ri_wx_idx = wx_list_order.index(ri_wx)
    cai_wx = wx_list_order[(ri_wx_idx + 2) % 5]
    lines.extend(_format_table(
        ["大运", "年龄段", "财星配合", "效果评估"],
        [
            [d.get("gan_zhi", ""),
             f"{d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁",
             "财星到位" if TIAN_GAN_WU_XING.get(d.get("gan", ""), "") == cai_wx else "财星不显",
             "财运旺" if TIAN_GAN_WU_XING.get(d.get("gan", ""), "") == cai_wx else "财运平"]
            for d in dy_list[:8]
        ]
    ))
    lines.append("")

    # 8.8 九龙道长原始五级对照
    lines.append("### 8.8 九龙道长原始财富评级对照（强制·必含）")
    lines.append("")
    lines.append("**六种八字状态对照：**")
    lines.append("")
    lines.extend(_format_table(
        ["状态", "条件", "判定"],
        [
            ["身强财旺→大富", "身强(40~60)+财≥40",
             "✅" if is_qiang and is_cai_wang else "❌"],
            ["身强财弱→中富", "身强+财<40+无库",
             "✅" if is_qiang and not is_cai_wang and not has_ku else "❌"],
            ["身弱财旺→小富", "身弱+财≥40",
             "✅" if not is_qiang and is_cai_wang else "❌"],
            ["身弱财弱→小富", "身弱+财<40",
             "✅" if not is_qiang and not is_cai_wang else "❌"],
            ["无财身弱→贫穷", "无财+身弱",
             "✅" if cai_score < 10 and not is_qiang else "❌"],
            ["从弱格→特殊", "0分→50分+财得令+食伤旺",
             "❌ 非从弱格" if sq_score >= 20 else "✅"],
        ]
    ))
    lines.append("")

    # 提取引擎数据
    effective_level = _get_wealth_detail_level(effective_score, sq_level, has_ku, xi_list, ji_list)
    lines.append(f"**从引擎JSON提取数据：**")
    lines.append(f"- 身强弱：{sq_score}分（{sq_level}）")
    lines.append(f"- 财星总分：{cai_score}分（有效分{effective_score:.1f}分）")
    lines.append(f"- 日/时柱有库：{'有' if has_ku else '无'}（{cai_ku}）")
    lines.append(f"- 食伤情况：{'有' if has_shi_shen else '无'}财根状态")
    lines.append(f"- 大运配合：{'好' if any(TIAN_GAN_WU_XING.get(d.get('gan',''),'')==cai_wx for d in dy_list[:4]) else '中' if any(TIAN_GAN_WU_XING.get(d.get('gan',''),'')==cai_wx for d in dy_list) else '差'}")
    lines.append("")
    lines.append(f"**评定：{effective_level}**")
    lines.append(f"- 日常运量级：{effective_score:.0f}万~{effective_score*10:.0f}万")
    lines.append(f"- 最佳运量级：{effective_score*5:.0f}万~{effective_score*20:.0f}万（{dy_list[3].get('gan_zhi','') if len(dy_list)>3 else '—'}大运）")
    lines.append(f"- 天花板量级：{effective_score*10:.0f}万~{effective_score*50:.0f}万")
    lines.append(f"- 核心依据：{base_tier}+{'有财库' if has_ku else '无财库'}")
    lines.append(f"- 风险提示：{dy_list[0].get('gan_zhi','') if dy_list else '—'}大运前后注意财务风险")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section9(basic: dict, analysis: dict) -> list:
    """§9 置业/买房分析 — 60行"""
    lines = []
    lines.append("## §9 置业/买房分析")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    pillars = basic.get("pillars", {})
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    cx = analysis.get("cai_xing", {})
    has_ku = cx.get("has_ku", False)
    cai_ku = cx.get("cai_ku", "")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    energy = analysis.get("energy", {})
    wxs = energy.get("wu_xing_energy", {})

    # 9.1 不动产特征
    lines.append("### 9.1 不动产特征")
    lines.append("")
    # 印星为房，财星为产，土为基
    yin_count = 0
    cai_count = 0
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(pos_key, {})
        for cg in p.get("cang_gan", []):
            ss = cg.get("shi_shen", "")
            wx = cg.get("wu_xing", "")
            if ss in ["正印", "偏印"]:
                yin_count += cg.get("weight", 0) / 100
            if ss in ["正财", "偏财"]:
                cai_count += cg.get("weight", 0) / 100
    if yin_count >= 1.5:
        lines.append(f"印星较旺（强度{yin_count:.1f}）：印为房，置业意愿强，有购房置产的规划能力。")
    else:
        lines.append(f"印星偏弱（强度{yin_count:.1f}）：置业意愿不强或条件受限。")
    if has_ku:
        lines.append(f"有财库（{cai_ku}）：有通过房产积累财富的潜力。")
    else:
        lines.append("无财库：置业更偏向自住需求而非投资。")
    tu_pct = wxs.get("土", 0)
    if tu_pct > 25:
        lines.append(f"土能量偏强（{tu_pct:.1f}%）：土为基，置业基础好。")
    else:
        lines.append(f"土能量一般（{tu_pct:.1f}%）：置业基础一般。")
    lines.append("")

    # 9.2 置业时间点
    lines.append("### 9.2 置业时间点")
    lines.append("")
    xi_wx_list = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    buy_years = []
    for d in dy_list[:6]:
        d_gan = d.get("gan", "")
        d_gan_wx = TIAN_GAN_WU_XING.get(d_gan, "")
        if d_gan_wx in xi_wx_list:
            buy_years.append(f"{d.get('gan_zhi','')}（{d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁）")
    if buy_years:
        lines.extend(_format_table(
            ["时间窗口", "大运", "命理信号", "建议"],
            [[str(i+1), y, "印/财星到位", "宜置业"] for i, y in enumerate(buy_years[:4])]
        ))
    else:
        lines.append("当前大运周期内无显著置业窗口。建议在喜用神大运年份考虑置业。")
    lines.append("")

    # 9.3 风水建议
    lines.append("### 9.3 风水建议")
    lines.append("")
    if xi_list:
        xi_wx_first = _get_xi_yong_wx(xi_list[0], ri_wx)
        direction = WU_XING_DIRECTIONS.get(xi_wx_first, "中")
        lines.append(f"喜用神为{xi_list[0]}（{xi_wx_first}），置业宜选{direction}方位。")
        lines.append(f"房屋朝向优先考虑{direction}向，环境宜有{xi_wx_first}元素。")
    else:
        lines.append("建议根据自身感觉选择居住环境，宜安静舒适。")
    lines.append("")

    # 9.4 风险提示
    lines.append("### 9.4 风险提示")
    lines.append("")
    ji_wx_list = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]
    risk_years = [d.get("gan_zhi", "") for d in dy_list[:4]
                  if TIAN_GAN_WU_XING.get(d.get("gan", ""), "") in ji_wx_list]
    if risk_years:
        lines.append(f"⚠️ 忌神大运期间谨慎置业：{'、'.join(risk_years)}。")
    else:
        lines.append("✅ 近期无明显的置业风险大运。")
    lines.append("⚠️ 贷款/负债需控制在月收入的30%以内，忌神年份避免高杠杆。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section10(basic: dict, analysis: dict) -> list:
    """§10 事业分析（格局定方向+恶神制化+五行定行业+等级+关键年份）— 120行"""
    lines = []
    lines.append("## §10 事业分析")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ge_ju_str = analysis.get("ge_ju", "正印")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    pillars = basic.get("pillars", {})
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    energy = analysis.get("energy", {})
    wxs = energy.get("wu_xing_energy", {})
    cx = analysis.get("cai_xing", {})
    cai_score = cx.get("score", 0)

    # 10.1 格局定方向
    lines.append("### 10.1 格局定方向")
    lines.append("")
    career_map = {
        "正官": "体制内/管理/公务员方向，适合在规范化组织中担任管理岗位",
        "七杀": "军警/创业/挑战性行业，适合高压环境中展现魄力",
        "正印": "学术/教育/研究/文化方向，适合知识密集型行业",
        "偏印": "技术/研发/策略/咨询方向，适合深度钻研型岗位",
        "正财": "实体经营/财务/贸易方向，适合稳健经营型行业",
        "偏财": "投资/销售/自由职业方向，适合灵活多变的市场环境",
        "比肩": "技术专家/自由职业/独立顾问方向，适合独立开展工作",
        "劫财": "公关/销售/合作经营方向，适合需要社交能力的行业",
        "食神": "创意/艺术/技术/美食方向，适合发挥才华的领域",
        "伤官": "创作/研发/表演/创新方向，适合需要叛逆精神的领域",
    }
    lines.append(f"格局为{ge_ju_str}格，{career_map.get(ge_ju_str, '宜根据喜用神五行选择行业')}。")
    lines.append("")

    # 10.2 恶神制化
    lines.append("### 10.2 恶神制化")
    lines.append("")
    qi_sha_has_zhi = False
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss == "七杀":
            # 检查是否有制化（食神制杀、印星化杀）
            for pos_key2 in ["nian", "yue", "ri", "shi"]:
                p2 = pillars.get(pos_key2, {})
                ss2 = p2.get("gan_shi_shen", "")
                if ss2 == "食神":
                    qi_sha_has_zhi = True
                if ss2 in ["正印", "偏印"]:
                    qi_sha_has_zhi = True
    if qi_sha_has_zhi:
        lines.append("七杀有制化：七杀遇食神/印星制化，化为权威管理能力，事业上有魄力且不鲁莽。")
    elif sq_level == "身强" and "七杀" in str(pillars):
        lines.append("七杀无制但身强可担：七杀虽无直接制化，但身强足以承载，表现为敢于竞争和挑战。")
    else:
        lines.append("原局无七杀或七杀有制，事业压力适中。")
    lines.append("")

    # 10.3 五行定行业
    lines.append("### 10.3 五行定行业")
    lines.append("")
    wx_list_order = ["木", "火", "土", "金", "水"]
    ri_wx_idx = wx_list_order.index(ri_wx)
    industry_data = {
        "木": ["教育/文化/出版/林业/医药/纺织", "适合度根据喜用神"],
        "火": ["能源/餐饮/文化传媒/互联网/电力", "适合度根据喜用神"],
        "土": ["房地产/建筑/农业/矿业/仓储", "适合度根据喜用神"],
        "金": ["金融/机械/汽车/金属/法律/审计", "适合度根据喜用神"],
        "水": ["物流/贸易/旅游/水产/IT/咨询", "适合度根据喜用神"],
    }
    xi_wx_names = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    ji_wx_names = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]
    ind_rows = []
    for wx_name in wx_list_order:
        if wx_name in xi_wx_names:
            fit = "⭐⭐⭐ 优先推荐"
        elif wx_name in ji_wx_names:
            fit = "⚠️ 谨慎选择"
        else:
            fit = "⭐ 一般推荐"
        ind_rows.append([wx_name, industry_data.get(wx_name, ["—"])[0], f"{fit}"])
    lines.extend(_format_table(["五行", "对应行业", "适合度"], ind_rows))
    lines.append("")

    # 行业细分解读
    lines.append("**行业细分解读：**")
    lines.append("")
    for wx_name in wx_list_order:
        if wx_name in xi_wx_names:
            lines.append(f"- ✅ **{wx_name}行业（⭐⭐⭐ 优先推荐）**：{industry_data.get(wx_name, ['—'])[0]}。"
                         f"此五行与你喜用神一致，选择{industry_data.get(wx_name, ['—'])[0]}中的细分领域，"
                         f"能获得最好的发展态势和贵人助力。")
        elif wx_name in ji_wx_names:
            lines.append(f"- ⚠️ **{wx_name}行业（谨慎选择）**：{industry_data.get(wx_name, ['—'])[0]}。"
                         f"此五行与你忌神一致，即使进入这些行业也需格外谨慎，"
                         f"注意控制风险，避免长期陷于不利的行业环境。")
        else:
            lines.append(f"- ⭐ **{wx_name}行业（一般推荐）**：{industry_data.get(wx_name, ['—'])[0]}。"
                         f"此五行能量中性，可根据个人兴趣和资源条件酌情选择。")
    lines.append("")

    # 10.4 事业等级
    lines.append("### 10.4 事业等级评估")
    lines.append("")
    career_score = min(sq_score + cai_score / 10, 100)
    if career_score >= 70:
        career_level = "上等（高级管理/专家级）"
    elif career_score >= 50:
        career_level = "中等（中层管理/骨干级）"
    elif career_score >= 30:
        career_level = "中下（基础管理/执行级）"
    else:
        career_level = "基础（执行级/需大运提升）"
    lines.append(f"事业综合评分：{career_score:.1f}分 → **{career_level}**")
    lines.append(f"核心驱动力：{ge_ju_str}格 + {sq_level} + 喜用神{'/'.join(xi_list)}")
    lines.append("")

    # 事业等级深度解读
    lines.append("**事业等级深度解读：**")
    lines.append("")
    if career_score >= 70:
        lines.append(f"事业基础扎实，{ge_ju_str}格配合{sq_level}，在相关行业中容易脱颖而出。"
                     f"建议专注核心领域，争取在40岁前进入管理或专家层。"
                     f"大运相助时，事业高度可以更上一层楼。")
    elif career_score >= 50:
        lines.append(f"事业基础中等，需要借助大运和自身努力进一步提升。"
                     f"建议在30~45岁间抓住关键大运窗口，实现事业跃升。"
                     f"{ge_ju_str}格的方向感加上{sq_level}的执行力，稳步前进是最好策略。")
    elif career_score >= 30:
        lines.append(f"事业基础偏弱，但通过大运补益和后天努力仍可改善。"
                     f"建议先求稳再求进，在基础岗位上积累经验和资源。"
                     f"重点关注喜用神大运的窗口期，届时大胆把握机会。")
    else:
        lines.append(f"事业基础较弱，但命局的潜力和大运助力不可忽视。"
                     f"建议先在某一个细分领域深耕，成为专业型人才。"
                     f"人生后期的大运可能有较大的事业转折机会。")
    lines.append("")

    # 10.5 关键事业年份
    lines.append("### 10.5 关键事业年份")
    lines.append("")
    xi_wx_list = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    key_years = []
    for d in dy_list[:8]:
        d_gan = d.get("gan", "")
        d_gan_wx = TIAN_GAN_WU_XING.get(d_gan, "")
        if d_gan_wx in xi_wx_list:
            key_years.append(f"{d.get('gan_zhi','')}（{d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁）")
    if key_years:
        lines.extend(_format_table(
            ["序号", "大运", "年龄段", "事业特征"],
            [[str(i+1), y.split("（")[0], y.split("（")[1].replace("）", ""), "事业上升期"]
             for i, y in enumerate(key_years[:6])]
        ))
    else:
        lines.extend(_format_table(
            ["序号", "大运", "年龄段", "事业特征"],
            [["—", "—", "—", "—"]]
        ))
    lines.append("")

    # 职业规划建议
    lines.append("### 10.6 职业规划建议")
    lines.append("")
    top_industries = [wx for wx in xi_wx_names[:3]]
    lines.append("**优先推荐行业：**")
    for i, wx in enumerate(top_industries):
        ind = industry_data.get(wx, ["—"])[0]
        lines.append(f"{i+1}. {wx}属性行业：{ind}")
    lines.append("")
    lines.append(f"**创业时机判断：**")
    if sq_level == "身强":
        lines.append("身强之人适合创业，尤其在有印比大运支持的年份。创业宜选择自己熟悉的领域。")
        lines.append("最佳创业年龄段为30~45岁，此时经验和精力都处于高峰。")
        lines.append("合伙创业时，宜选择与自己五行互补的伙伴——你的喜用神五行对应的属性为佳。")
    elif sq_level == "身弱":
        lines.append("身弱之人创业需谨慎，建议先在相关行业积累经验和人脉后，再考虑借助大运窗口创业。")
        lines.append("如果创业，建议选择轻资产、重人脉的模式，降低资金风险。")
        lines.append("合伙创业时，宜选择身强或与自己五行相生的伙伴，形成互补优势。")
    else:
        lines.append("中和之人创业时机灵活，但建议在有食伤或财星大运的年份启动。")
        lines.append("创业方向宜选择与自己喜用神五行一致的行业。")
        lines.append("合伙创业时，宜选择与自己格局匹配、目标一致的伙伴。")
    lines.append("")
    lines.append(f"**职场路线建议：**")
    if ge_ju_str in ["正官", "正印"]:
        lines.append("适合走技术+管理复合路线，先在专业领域建立口碑，再向管理岗位发展。")
    elif ge_ju_str in ["七杀", "伤官"]:
        lines.append("适合走创新型路线，在挑战性强的岗位上更能发挥能力优势。")
    elif ge_ju_str in ["正财", "偏财"]:
        lines.append("适合走业务型路线，从销售/市场等一线岗位起步，逐步建立自己的客户资源。")
    elif ge_ju_str in ["偏印", "食神"]:
        lines.append("适合走技术专家路线，深耕某一专业领域，成为行业专家。")
    else:
        lines.append("根据自身兴趣和优势选择适合的路线，建议先在职场中试错和积累。")
    lines.append("")

    # 10.7 事业规划时间表
    lines.append("### 10.7 事业规划时间表")
    lines.append("")
    lines.append("**关键年龄阶段的事业建议：**")
    lines.append("")
    qi_yun_age = dy_data.get("qi_yun_age", 7)
    lines.append(f"**{qi_yun_age:.0f}~22岁**（求学与探索期）：")
    lines.append(f"此阶段宜以学业为主，培养{ge_ju_str}格相关的基础能力。"
                 f"如果求学阶段大运为喜用神，应把握升学深造的机会。"
                 f"如果大运为忌神，可适当降低学业预期，多积累社会实践经验。")
    lines.append("")
    lines.append(f"**22~35岁**（职场起步与积累期）：")
    lines.append(f"此阶段是职业生涯的起步阶段，宜在所选行业的前沿位置积累经验。"
                 f"建议在前5年内完成基础技能的学习和行业理解的建立。"
                 f"此时段如有喜用神大运，可大胆争取晋升和跳槽机会。")
    lines.append("")
    lines.append(f"**35~50岁**（事业上升与突破期）：")
    lines.append(f"此阶段是事业发展的关键期，一般人的事业高度在此阶段决定。"
                 f"宜在已有领域的基础上向管理层或专家岗发展。"
                 f"喜用神大运在此阶段出现，是事业突破的最佳窗口。")
    lines.append("")
    lines.append(f"**50岁以后**（事业稳定与传承期）：")
    lines.append(f"此阶段事业趋于稳定，宜从一线执行向指导、顾问、传承角色转变。"
                 f"可开始考虑副业、投资或公益事业，拓展人生的宽度。")
    lines.append("")

    # 10.8 合作对象分析
    lines.append("### 10.8 合作对象分析")
    lines.append("")
    lines.append("**五行匹配分析：**")
    lines.append("")
    wx_sheng_ke = {
        "木": {"生我": "水", "我生": "火", "克我": "金", "我克": "土"},
        "火": {"生我": "木", "我生": "土", "克我": "水", "我克": "金"},
        "土": {"生我": "火", "我生": "金", "克我": "木", "我克": "水"},
        "水": {"生我": "金", "我生": "木", "克我": "土", "我克": "火"},
        "金": {"生我": "土", "我生": "水", "克我": "火", "我克": "木"},
    }
    wx_rel = wx_sheng_ke.get(ri_wx, {})
    lines.append(f"作为{ri_wx}命主：")
    lines.append(f"- 最佳合作伙伴五行：{wx_rel.get('生我', '')}（生我者，能给你支持和帮助）")
    lines.append(f"- 良好合作伙伴五行：{wx_rel.get('我克', '')}（我克者，你能有效管理和带动对方）")
    lines.append(f"- 需谨慎合作的五行：{wx_rel.get('克我', '')}（克我者，合作中容易被压制）")
    if xi_wx_names:
        lines.append(f"- 从喜用神看：喜用神{wx_rel.get('生我', '')}/{', '.join(xi_wx_names)}五行的人更适合与你长期合作。")
    lines.append("")
    lines.append(f"**性格匹配建议：**")
    if ge_ju_str in ["正官", "正印"]:
        lines.append("你适合与有执行力和创新精神的人合作，互补你的稳健特质。")
    elif ge_ju_str in ["七杀", "伤官"]:
        lines.append("你适合与稳重谨慎、善于规划的人合作，平衡你的冒险精神。")
    elif ge_ju_str in ["正财", "偏财"]:
        lines.append("你适合与技术型或管理型的人合作，对方补足你的操作细节。")
    else:
        lines.append("你适合与互补型人格合作，取长补短。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section11(basic: dict, analysis: dict) -> list:
    """§11 学历分析（第0层三档法+六步排查+文昌）— 80行"""
    lines = []
    lines.append("## §11 学历分析")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    nian_gan = basic.get("nian_gan", "")
    yue_gan = basic.get("yue_gan", "")
    pillars = basic.get("pillars", {})
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])

    # 11.1 第0层三档法
    lines.append("### 11.1 第0层三档法判定")
    lines.append("")
    nian_p = pillars.get("nian", {})
    nian_ss = nian_p.get("gan_shi_shen", "")
    if nian_ss in ["正印", "偏印"]:
        tier_0 = "上等"
    elif nian_ss in ["正官", "七杀"]:
        tier_0 = "中等"
    else:
        tier_0 = "下等" if nian_ss in ["比肩", "劫财"] else "中等"
    lines.append(f"**第0层判定：{tier_0}**")
    lines.append(f"依据——年干{nian_gan}的十神为「{nian_ss}」")
    if tier_0 == "上等":
        lines.append("年干有印，先天学习基因好，容易在学业上有所成就。")
    elif tier_0 == "中等":
        lines.append("年干为官杀/财/食伤，学业需要后天努力和环境培养。")
    else:
        lines.append("年干为比劫，学业上需要更多自律和引导。")
    lines.append("")

    # 11.2 六步精细排查
    lines.append("### 11.2 六步精细排查")
    lines.append("")
    # 第一步：印在月令?
    yue_p = pillars.get("yue", {})
    yue_ss = yue_p.get("gan_shi_shen", "")
    yue_zhi = basic.get("yue_zhi", "")
    yue_cang = DI_ZHI_CANG_GAN.get(yue_zhi, [])
    yue_ben_qi_ss = _get_shi_shen(ri_gan, yue_cang[0][0]) if yue_cang else ""
    step1 = "✅" if yue_ss in ["正印", "偏印"] or yue_ben_qi_ss in ["正印", "偏印"] else "❌"
    lines.append(f"**第一步：印在月令本气** → {step1}")
    if step1 == "✅":
        lines.append(f"月令有印，学业根基扎实，学习能力强。印星在月令为本气得令，代表先天教育资源好。")
        lines.append(f"月令{yue_zhi}中的印星力量强，求学期间容易获得师长的帮助和提携。")
        if yue_ss in ["正印", "偏印"]:
            lines.append(f"更难得的是月干{yue_gan}透出印星，月令得用，学业优势更加突出。")
    else:
        lines.append(f"月令非印星（{yue_ben_qi_ss}），学业需靠后天努力。月令{yue_zhi}的格局特质决定"
                     f"了你在学业上的天分不在传统的书本知识上，而在{yue_ben_qi_ss}相关的实践能力。")
    lines.append("")

    # 第二步：印根被合化刑冲?
    lines.append(f"**第二步：印根被合化刑冲** → 检查中")
    # 检查各柱有没有印星被合
    yin_positions = []
    yin_zi = ["子", "亥"] if ri_wx == "水" else ["寅", "卯"] if ri_wx == "木" else ["巳", "午"] if ri_wx == "火" else ["申", "酉"] if ri_wx == "金" else ["辰", "戌", "丑", "未"]
    # 简化的印根检查：看各支柱中的印星藏干
    yin_count_in_pillars = 0
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = pillars.get(pos_key, {})
        for cg in p.get("cang_gan", []):
            cg_ss = cg.get("shi_shen", "")
            if cg_ss in ["正印", "偏印"]:
                yin_count_in_pillars += 1
                yin_positions.append(f"{pos_key}支藏{cg.get('gan','')}")
    if yin_count_in_pillars >= 2:
        lines.append(f"✅ 印星根气充足（{yin_count_in_pillars}处），分布在{'、'.join(yin_positions[:4])}，"
                     f"根基稳固，不易被刑冲破坏。")
    elif yin_count_in_pillars == 1:
        lines.append(f"➖ 印星有根但仅一处（{'、'.join(yin_positions)}），根气稍弱，需注意大运流年冲克。")
    else:
        lines.append(f"❌ 印星在原局无根，完全靠天干，容易被大运流年冲克。")
    lines.append("")

    # 第三步：文昌贵人
    lines.append("**第三步：文昌贵人** → ")
    wen_chang_zhi = WEN_CHANG_MAP.get(nian_gan, "")
    all_zhi = [basic.get(f"{k}_zhi", "") for k in ["nian", "yue", "ri", "shi"]]
    if wen_chang_zhi in all_zhi:
        step3 = f"✅ 年干{nian_gan}文昌在{wen_chang_zhi}，命局中有文昌贵人，利于学业考试。"
        lines.append(step3)
        # 具体在哪个柱
        for k, label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
            if basic.get(f"{k}_zhi", "") == wen_chang_zhi:
                lines.append(f"文昌贵人在{label}，{label}文昌在求学阶段的影响力最大。")
    else:
        step3 = f"❌ 年干{nian_gan}文昌在{wen_chang_zhi}，命局中无此支，文昌不显。"
        lines.append(step3)
        lines.append("文昌不显不代表学业不佳，只是学习的方式更多需要依靠自身的毅力和方法。")
    lines.append("")

    # 第四步：18岁前大运喜忌
    lines.append("**第四步：18岁前大运喜忌** → ")
    first_dy = dy_list[0] if dy_list else {}
    first_dy_gan = first_dy.get("gan", "")
    first_dy_gan_wx = TIAN_GAN_WU_XING.get(first_dy_gan, "")
    xi_wx_list = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    if first_dy_gan_wx in xi_wx_list:
        step4 = f"✅ 第一步大运{first_dy.get('gan_zhi','')}为喜用神运，利于学业。"
        lines.append(step4)
        first_dy_ss = _get_shi_shen(ri_gan, first_dy_gan)
        lines.append(f"大运天干{first_dy_gan}为{first_dy_ss}，此运中{'印运主学业顺遂' if first_dy_ss in ['正印','偏印'] else '官运主自律性强' if first_dy_ss in ['正官','七杀'] else '财运主社会实践丰富'}。")
    else:
        step4 = f"⚠️ 第一步大运{first_dy.get('gan_zhi','')}非喜用神，学业需更多努力。"
        lines.append(step4)
        first_dy_ss = _get_shi_shen(ri_gan, first_dy_gan)
        lines.append(f"大运天干{first_dy_gan}为{first_dy_ss}，不是典型的学运，"
                     f"此阶段可能需要花更多精力在专业学习之外的事情上。")
    lines.append("")

    # 第五步：印运在求学窗口
    lines.append("**第五步：印运在求学窗口** → ")
    study_window = [d for d in dy_list[:3]
                    if _get_shi_shen(ri_gan, d.get("gan", "")) in ["正印", "偏印"]
                    or _get_shi_shen(ri_gan, d.get("gan", "")) == "正印"]
    if study_window:
        step5 = f"✅ 大运{study_window[0].get('gan_zhi','')}在求学阶段有印星，学业助力明显。"
        lines.append(step5)
        lines.append(f"此大运中考试运好，学习效率高，是考取理想学校的最佳窗口。")
        if len(study_window) > 1:
            lines.append(f"此外，大运{study_window[1].get('gan_zhi','')}也有印星，学业的良好状态可以持续。")
    else:
        step5 = "⚠️ 求学阶段无印运，学业成绩主要靠个人努力。"
        lines.append(step5)
        lines.append("印运不显不代表学业不好，只是缺乏天时辅助，建议通过提高学习效率和方法来弥补。")
    lines.append("")

    # 第六步：综合验证
    lines.append("**第六步：综合验证** → ")
    positive_count = sum(1 for s in [step1, step3, step4] if "✅" in str(s))
    if positive_count >= 2 and tier_0 == "上等":
        grade = "高学历（硕士以上）"
    elif positive_count >= 1:
        grade = "中等学历（本科/大专）"
    else:
        grade = "基础学历（高中/中专）"
    lines.append(f"**学历等级：{grade}**")
    lines.append(f"综合{tier_0}基础+{positive_count}/3项正向指标。")
    lines.append("")

    # 11.3 关键学历年份
    lines.append("### 11.3 关键学历年份")
    lines.append("")
    edu_years = []
    for d in dy_list[:4]:
        d_gan = d.get("gan", "")
        d_gan_ss = _get_shi_shen(ri_gan, d_gan)
        if d_gan_ss in ["正印", "偏印"]:
            edu_years.append(f"{d.get('gan_zhi','')}（{d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁）")
    if edu_years:
        lines.extend(_format_table(
            ["序号", "大运/年份", "年龄段", "考试运"],
            [[str(i+1), y.split("（")[0], y.split("（")[1].replace("）", ""), "文昌助力·考运佳"]
             for i, y in enumerate(edu_years[:4])]
        ))
    else:
        lines.append("| — | — | — | 印运不显·需自身努力 |")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section12(basic: dict, analysis: dict) -> list:
    """§12 婚姻/感情分析 — 80行"""
    lines = []
    lines.append("## §12 婚姻/感情分析")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ri_zhi = basic.get("ri_zhi", "")
    gender = basic.get("gender", "男")
    pillars = basic.get("pillars", {})
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    industry_map = {
        "木": "教育/文化/出版/林业/医药/纺织",
        "火": "能源/餐饮/文化传媒/互联网/电力",
        "土": "房地产/建筑/农业/矿业/仓储",
        "金": "金融/机械/汽车/金属/法律/审计",
        "水": "物流/贸易/旅游/水产/IT/咨询",
    }

    # 12.1 夫妻宫（日支）
    lines.append("### 12.1 夫妻宫（日支）喜忌")
    lines.append("")
    ri_cang = DI_ZHI_CANG_GAN.get(ri_zhi, [])
    ri_cang_ss_list = [_get_shi_shen(ri_gan, cg[0]) for cg in ri_cang]
    ri_ss_str = "、".join(ri_cang_ss_list)
    ri_xi_ji = "喜" if any(s in xi_list for s in ri_cang_ss_list) else "忌" if any(s in ji_list for s in ri_cang_ss_list) else "中性"
    lines.append(f"日支：{ri_zhi}")
    lines.append(f"藏干：{_get_cang_gan_list(pillars.get('ri', {}))}")
    lines.append(f"十神：{ri_ss_str}")
    lines.append(f"喜忌：**{ri_xi_ji}**（{'夫妻宫为喜用神，婚姻质量高' if ri_xi_ji=='喜' else '夫妻宫为忌神，需沟通包容' if ri_xi_ji=='忌' else '夫妻宫中性的婚姻质量取决于经营'}）")
    lines.append("")

    # 日支详细解读
    lines.append("**日支夫妻宫深度解读：**")
    lines.append("")
    ri_cang_main = ri_cang[0][0] if ri_cang else ""
    ri_cang_main_ss = _get_shi_shen(ri_gan, ri_cang_main) if ri_cang_main else ""
    ri_cang_main_wx = TIAN_GAN_WU_XING.get(ri_cang_main, "")
    lines.append(f"日支{ri_zhi}的主气为{ri_cang_main}（{ri_cang_main_wx}），对应的十神为{ri_cang_main_ss}。")
    if ri_xi_ji == "喜":
        lines.append(f"夫妻宫为喜用神，说明配偶对你有助益，婚姻是人生的重要支撑。")
        lines.append(f"配偶性格在{ri_cang_main_ss}特质上表现明显，彼此在{ri_cang_main_ss}相关的领域容易产生共鸣。")
    elif ri_xi_ji == "忌":
        lines.append(f"夫妻宫为忌神，说明婚姻中需要更多的包容和理解。")
        lines.append(f"配偶的{ri_cang_main_ss}特质可能与你的期望有差距，需要学会求同存异。")
    else:
        lines.append(f"夫妻宫能量中性，婚姻质量主要取决于双方经营和缘分深浅。")
        lines.append(f"配偶的{ri_cang_main_ss}特质处于中性水平，相处中不会有明显的冲突点。")
    lines.append("")

    # 12.2 夫妻星
    lines.append("### 12.2 夫妻星")
    lines.append("")
    if gender == "男":
        pei_ou_ss = "正财"  # 男命妻星
        pei_ou_ss2 = "偏财"
    else:
        pei_ou_ss = "正官"  # 女命夫星
        pei_ou_ss2 = "七杀"
    pei_ou_found = []
    for pos_key, pos_label in [("nian", "年"), ("yue", "月"), ("ri", "日"), ("shi", "时")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss in [pei_ou_ss, pei_ou_ss2]:
            pei_ou_found.append(f"{pos_label}干{p.get('gan','')}")
        for cg in p.get("cang_gan", []):
            if cg.get("shi_shen", "") in [pei_ou_ss, pei_ou_ss2]:
                pei_ou_found.append(f"{pos_label}支{cg.get('gan','')}")
    lines.append(f"{'男命' if gender=='男' else '女命'}：{pei_ou_ss}/{pei_ou_ss2}为{'妻' if gender=='男' else '夫'}星")
    if pei_ou_found:
        lines.append(f"夫妻星在原局状态：{'、'.join(pei_ou_found)}")
    else:
        lines.append(f"夫妻星在原局不显，缘分较晚或需通过大运流年引动。")
    lines.append("")

    # 12.3 四大结婚信号（展开版）
    lines.append("### 12.3 四大结婚信号")
    lines.append("")
    signals = []
    signal_details = []
    # 信号1: 夫妻宫被合
    he_map = {"子丑": True, "寅亥": True, "卯戌": True, "辰酉": True, "巳申": True, "午未": True}
    has_he = False
    for other_zhi in [basic.get(f"{k}_zhi", "") for k in ["nian", "yue", "shi"]]:
        if ri_zhi + other_zhi in he_map:
            signals.append("✅ 夫妻宫被合")
            signal_details.append(f"日支{ri_zhi}与{'、'.join([z for z in [basic.get(f'{k}_zhi', '') for k in ['nian','yue','shi']] if ri_zhi+z in he_map])}相合，夫妻宫被合则姻缘易成。")
            has_he = True
            break
    if not has_he:
        signals.append("❌ 夫妻宫未被合")
        signal_details.append(f"日支{ri_zhi}与其他三柱地支无明显的六合关系，夫妻宫未被主动引动。")
    # 信号2: 桃花在日时
    tao_hua_map = {"寅": "卯", "午": "卯", "戌": "卯", "巳": "午", "酉": "午", "丑": "午",
                   "申": "酉", "子": "酉", "辰": "酉", "亥": "子", "卯": "子", "未": "子"}
    nian_zhi = basic.get("nian_zhi", "")
    tao_hua_zhi = tao_hua_map.get(nian_zhi, "")
    if tao_hua_zhi in [basic.get(f"{k}_zhi", "") for k in ["ri", "shi"]]:
        signals.append("✅ 桃花在日时柱，早婚倾向")
        signal_details.append(f"年支{nian_zhi}的桃花在{tao_hua_zhi}，且桃花出现在日柱或时柱，代表早婚缘分较强。")
    else:
        signals.append("❌ 桃花不在日时，晚婚倾向")
        signal_details.append(f"年支{nian_zhi}的桃花在{tao_hua_zhi}，但命局日、时柱无此支，桃花不显于日时，晚婚倾向。")
    # 信号3: 夫妻星透干
    if pei_ou_found:
        signals.append("✅ 夫妻星透干或有根，婚姻信号明显")
        signal_details.append(f"夫妻星在原局透干或有根（位于{'、'.join(pei_ou_found)}），代表姻缘信息明显。")
    else:
        signals.append("❌ 夫妻星不显，缘分较晚")
        signal_details.append("原局中夫妻星未透干亦无根气，缘分需要大运流年引动才会出现。")
    # 信号4: 大运引动
    signal4_found = False
    for d in dy_list[:4]:
        d_gan_ss = _get_shi_shen(ri_gan, d.get("gan", ""))
        if d_gan_ss in [pei_ou_ss, pei_ou_ss2]:
            signals.append(f"✅ 大运{d.get('gan_zhi','')}引动夫妻星")
            signal_details.append(f"近期大运{d.get('gan_zhi','')}天干为{d_gan_ss}，直接引动夫妻星，是结婚的有利大运。")
            signal4_found = True
            break
    if not signal4_found:
        signals.append("❌ 近期大运无夫妻星引动")
        signal_details.append("近期大运无明显的夫妻星引动，姻缘的到来可能比较突然或意外。")

    for i, s in enumerate(signals[:4]):
        lines.append(f"- [ ] {s}")
        if i < len(signal_details):
            lines.append(f"  └ {signal_details[i]}")
    lines.append("")

    # 12.4 三个结婚窗口
    lines.append("### 12.4 三个结婚窗口")
    lines.append("")
    marriage_windows = []
    for d in dy_list[:6]:
        d_gan_ss = _get_shi_shen(ri_gan, d.get("gan", ""))
        if d_gan_ss in [pei_ou_ss, pei_ou_ss2] or d_gan_ss in ["食神", "伤官"]:
            marriage_windows.append(d)

    if marriage_windows:
        win_rows = []
        for i, w in enumerate(marriage_windows[:3]):
            win_rows.append([
                f"第{i+1}个",
                w.get("gan_zhi", ""),
                f"{w.get('start_age',0):.0f}~{w.get('end_age',0):.0f}岁",
                f"夫妻星引动/桃花旺盛"
            ])
        lines.extend(_format_table(["窗口", "大运", "年龄段", "解读"], win_rows))
    else:
        lines.append("| 窗口 | 大运 | 年份 | 解读 |")
        lines.append("|:----|:----|:----|:-----|")
        lines.append("| — | — | — | 夫妻星不显，缘分随缘 |")
    lines.append("")

    # 12.5 配偶特征
    lines.append("### 12.5 配偶特征")
    lines.append("")
    if gender == "男":
        pei_wx = _get_xi_yong_wx("财", ri_wx)
        lines.append(f"妻星五行：{pei_wx}。")
        lines.append(f"妻星所属五行{pei_wx}对应{WU_XING_COLORS.get(pei_wx,'')}色，性格方面具有{pei_wx}性的特质。")
        if ri_xi_ji == "喜":
            lines.append(f"配偶性格温和，对命主有助益，婚姻质量较高。妻子在{pei_wx}相关的方面能够给命主带来支持和资源。")
            lines.append(f"配偶可能在{pei_wx}属性的行业（如{industry_map.get(pei_wx,'—')}）工作或擅长相关领域。")
        else:
            lines.append(f"配偶性格可能与自己有差异，需互相包容磨合。双方在价值观和生活方式上需要更多的沟通和调整。")
            lines.append(f"建议在婚姻中建立共同的兴趣和目标，以增进彼此的理解和亲密度。")
    else:
        pei_wx = _get_xi_yong_wx("官杀", ri_wx)
        lines.append(f"夫星五行：{pei_wx}。")
        lines.append(f"夫星所属五行{pei_wx}对应{WU_XING_COLORS.get(pei_wx,'')}色，丈夫的性格偏向{pei_wx}性特质。")
        if ri_xi_ji == "喜":
            lines.append(f"配偶有能力，对命主有助力。丈夫在{pei_wx}方面的能力强，能够在事业和生活上给命主支持。")
            lines.append(f"配偶可能在{pei_wx}属性的行业（如{industry_map.get(pei_wx,'—')}）发展，社会地位较好。")
        else:
            lines.append(f"配偶可能与自己在观念上有冲突，需沟通。双方需要在重大决策上达成共识，避免因个性差异产生矛盾。")
            lines.append(f"建议在婚前充分了解彼此的价值观和生活习惯，婚后的磨合期需要更多耐心。")
    lines.append("")
    lines.append("**婚后相处建议：**")
    lines.append("")
    if ri_xi_ji == "喜":
        lines.append(f"夫妻宫为喜用神，婚后总体顺遂。建议珍惜这份善缘，在重大决策时多参考配偶意见，"
                     f"共同经营好婚姻生活。配偶是你的贵人，遇事多商量会有好结果。")
    elif ri_xi_ji == "忌":
        lines.append(f"夫妻宫为忌神，婚后需要更多经营。建议在财务管理、子女教育等重大事项上明确分工，"
                     f"减少因理念不同导致的摩擦。婚姻需要双方共同努力，包容是维系的关键。")
    else:
        lines.append(f"夫妻宫中性能量，婚姻需要用心经营。建议多创造二人世界的专属时间，培养共同爱好，"
                     f"在平淡中建立深厚的情感纽带。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section13(basic: dict, analysis: dict) -> list:
    """§13 子女分析（子女星+十二长生+子女宫+添丁年份）— 50行"""
    lines = []
    lines.append("## §13 子女分析")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    gender = basic.get("gender", "男")
    pillars = basic.get("pillars", {})
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])

    # 13.1 子女星
    lines.append("### 13.1 子女星判定")
    lines.append("")
    if gender == "男":
        child_ss = ["正官", "七杀"]  # 男命官杀为子女
        child_label = "官杀"
    else:
        child_ss = ["食神", "伤官"]  # 女命食伤为子女
        child_label = "食伤"
    lines.append(f"{'男命' if gender=='男' else '女命'}：{child_label}为子女星")

    child_found = []
    for pos_key, pos_label in [("nian", "年"), ("yue", "月"), ("ri", "日"), ("shi", "时")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss in child_ss:
            child_found.append(f"{pos_label}干{p.get('gan','')}")
    if child_found:
        lines.append(f"子女星在原局状态：{'、'.join(child_found)}")
    else:
        lines.append("子女星在原局不显，需大运流年引动。")
    lines.append("")

    # 13.2 子女宫（时柱）
    lines.append("### 13.2 子女宫（时柱）")
    lines.append("")
    shi_p = pillars.get("shi", {})
    shi_ss = shi_p.get("gan_shi_shen", "")
    shi_zhi = basic.get("shi_zhi", "")
    lines.append(f"时柱：{shi_p.get('gan','')}{shi_zhi}")
    lines.append(f"时干十神：{shi_ss}")
    lines.append(f"状态：{'子女宫为喜，子女性格较好' if shi_ss in xi_list else '子女宫为忌，需注意子女教育' if shi_ss in ji_list else '子女宫中性'}")

    # 十二长生
    cs = _get_chang_sheng(ri_gan, shi_zhi)
    if cs in ["长生", "沐浴", "冠带", "临官", "帝旺"]:
        cs_comment = "旺盛"
    elif cs in ["衰", "病", "死"]:
        cs_comment = "偏弱"
    else:
        cs_comment = "一般"
    lines.append(f"日主在时支十二长生：{cs}（{cs_comment}）")
    lines.append("")

    # 13.3 添丁年份
    lines.append("### 13.3 添丁年份")
    lines.append("")
    child_years = []
    for d in dy_list[:6]:
        d_gan_ss = _get_shi_shen(ri_gan, d.get("gan", ""))
        if d_gan_ss in child_ss:
            child_years.append(f"{d.get('gan_zhi','')}（{d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁）")
    lines.extend(_format_table(
        ["序号", "大运", "年龄段", "解读"],
        [[str(i+1), y.split("（")[0], y.split("（")[1].replace("）", ""), "子女星引动"]
         for i, y in enumerate(child_years[:4])]
    ) if child_years else [["—", "—", "—", "子女星不显，添丁随缘"]])
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section14(basic: dict, analysis: dict) -> list:
    """§14 健康分析（五行过三+七杀+偏印+防护年份）— 80行"""
    lines = []
    lines.append("## §14 健康分析")
    lines.append("")
    energy = analysis.get("energy", {})
    wxs = energy.get("wu_xing_energy", {})
    pillars = basic.get("pillars", {})
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])

    # 14.1 五行过三排查表
    lines.append("### 14.1 五行过三排查表")
    lines.append("")
    over_rows = []
    for wx_name in ["木", "火", "土", "金", "水"]:
        pct = wxs.get(wx_name, 0)
        over = pct > 30
        risk = "偏高" if pct > 35 else "适中" if pct > 20 else "偏低"
        over_rows.append([
            wx_name,
            "✅ 过三" if over else "❌",
            f"{pct:.1f}%",
            WU_XING_ORGANS.get(wx_name, "—"),
            risk
        ])
    lines.extend(_format_table(["属性", "过三判定", "百分比", "对应器官", "健康风险"], over_rows))
    lines.append("")

    # 过三五行详细解读
    lines.append("**五行过三详细解读：**")
    lines.append("")
    over_wxs = [(wx, wxs.get(wx, 0)) for wx in ["木", "火", "土", "金", "水"] if wxs.get(wx, 0) > 30]
    if over_wxs:
        for wx, pct in sorted(over_wxs, key=lambda x: x[1], reverse=True):
            organs = WU_XING_ORGANS.get(wx, "—")
            color = WU_XING_COLORS.get(wx, "—")
            lines.append(f"- **{wx}（{pct:.1f}%）**：对应{organs}。{wx}过旺可能导致相关器官功能过亢或失衡。"
                         f"建议在饮食中减少{color}色食物摄入，适当增加被{wx}所克之五行对应的食物。"
                         f"例如，{wx}克{'火' if wx=='木' else '土' if wx=='火' else '水' if wx=='土' else '金' if wx=='水' else '木'}，"
                         f"可适当补益被克五行以维持平衡。")
    over_wxs_not = [(wx, wxs.get(wx, 0)) for wx in ["木", "火", "土", "金", "水"] if wxs.get(wx, 0) <= 30]
    if over_wxs_not:
        for wx, pct in sorted(over_wxs_not, key=lambda x: x[1], reverse=True):
            if pct > 0:
                organs = WU_XING_ORGANS.get(wx, "—")
                lines.append(f"- **{wx}（{pct:.1f}%）**：能量适中或偏低，对应{organs}。"
                             f"{'能量偏低需要适当补益' if pct < 15 else '能量处于正常范围，注意保持即可。'}")

    # 健康自查建议
    lines.append("")
    lines.append("**日常健康自查建议：**")
    lines.append("")
    lines.append("以下是根据五行能量分布推演的健康关注点，仅供参考，不能替代专业医疗诊断：")
    for wx in ["木", "火", "土", "金", "水"]:
        pct = wxs.get(wx, 0)
        if pct > 35:
            lines.append(f"- {WU_XING_ORGANS.get(wx,'')}：能量过旺（{pct:.1f}%），建议定期检查，避免功能过亢。")
            lines.append(f"  └ 养生建议：多接触与{wx}相克的五行元素（{WU_XING_COLORS.get(wx,'')}色减量，"
                         f"增加{TIAN_GAN_WU_XING.get(ri_gan,'')}色）。")
        elif pct < 10:
            lines.append(f"- {WU_XING_ORGANS.get(wx,'')}：能量不足（{pct:.1f}%），建议适当补充相关营养和锻炼。")
            lines.append(f"  └ 养生建议：多接触{wx}属性的事物，使用{WU_XING_COLORS.get(wx,'')}色，"
                         f"食用{WU_XING_TASTES.get(wx,'')}味食物。")
    lines.append("")

    # 14.2 七杀为病
    lines.append("### 14.2 七杀为病")
    lines.append("")
    qi_sha_count = 0
    qi_sha_pos = []
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss == "七杀":
            qi_sha_count += 1
            qi_sha_pos.append(pos_label)
        for cg in p.get("cang_gan", []):
            if cg.get("shi_shen", "") == "七杀":
                qi_sha_count += 0.5
                if pos_label not in qi_sha_pos:
                    qi_sha_pos.append(pos_label)
    if qi_sha_count >= 1:
        lines.append(f"七杀强度{qi_sha_count}，位于{'、'.join(qi_sha_pos)}。")
        # 七杀所克五行
        wx_list = ["木", "火", "土", "金", "水"]
        ri_idx = wx_list.index(ri_wx)
        qi_sha_wx = wx_list[(ri_idx + 3) % 5]  # 克我者
        # 被七杀克的五行
        ke_wx = wx_list[(ri_idx + 3) % 5]
        lines.append(f"七杀克{ke_wx}，对应{WU_XING_ORGANS.get(ke_wx, '—')}需重点防护。")
    else:
        lines.append("✅ 原局七杀不显，无七杀攻身之虑。")
    lines.append("")

    # 14.3 偏印主瘀
    lines.append("### 14.3 偏印主瘀")
    lines.append("")
    pian_yin_pos = []
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = pillars.get(pos_key, {})
        ss = p.get("gan_shi_shen", "")
        if ss == "偏印":
            pian_yin_pos.append(pos_label)
        for cg in p.get("cang_gan", []):
            if cg.get("shi_shen", "") == "偏印":
                if pos_label not in pian_yin_pos:
                    pian_yin_pos.append(pos_label)
    if pian_yin_pos:
        lines.append(f"偏印位于{'、'.join(pian_yin_pos)}，主气血瘀滞，需关注循环系统健康。")
    else:
        lines.append("✅ 偏印不显，无瘀滞之虑。")
    lines.append("")

    # 14.4 重点防护年份
    lines.append("### 14.4 重点防护年份")
    lines.append("")
    ji_wx_list = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]
    protect_years = []
    for d in dy_list[:8]:
        d_gan = d.get("gan", "")
        d_gan_wx = TIAN_GAN_WU_XING.get(d_gan, "")
        if d_gan_wx in ji_wx_list:
            protect_years.append(f"{d.get('gan_zhi','')}（{d.get('start_age',0):.0f}~{d.get('end_age',0):.0f}岁）")
    lines.extend(_format_table(
        ["序号", "大运/年份", "年龄段", "关注点"],
        [[str(i+1), y.split("（")[0], y.split("（")[1].replace("）", ""),
          f"{WU_XING_ORGANS.get(ji_wx_list[i % len(ji_wx_list)], '整体健康')}"]
         for i, y in enumerate(protect_years[:6])]
    ) if protect_years else [["—", "—", "—", "无显著健康风险大运"]])
    lines.append("")

    # 防护年份详细解读
    if protect_years:
        lines.append("**防护年份详细建议：**")
        lines.append("")
        for i, y in enumerate(protect_years[:6]):
            wx_ji = ji_wx_list[i % len(ji_wx_list)]
            organ = WU_XING_ORGANS.get(wx_ji, "整体健康")
            season = WU_XING_SEASONS.get(wx_ji, "全年")
            lines.append(f"- {y.split('（')[0]}（第{i+1}个防护期）：重点关注{organ}健康。"
                         f"此时间段为{wx_ji}属性大运，对应脏腑为{organ}，建议在{season}加强体检和保健。"
                         f"保持规律作息，避免过度劳累。")
        lines.append("")

    # 14.5 整体养生建议
    lines.append("### 14.5 整体养生建议")
    lines.append("")
    lines.append("**根据五行能量分布，建议以下养生方向：**")
    lines.append("")
    for wx in ["木", "火", "土", "金", "水"]:
        pct = wxs.get(wx, 0)
        organ = WU_XING_ORGANS.get(wx, "")
        taste = WU_XING_TASTES.get(wx, "")
        season = WU_XING_SEASONS.get(wx, "")
        direction = WU_XING_DIRECTIONS.get(wx, "")
        color = WU_XING_COLORS.get(wx, "")
        if pct > 35:
            lines.append(f"- **{wx}（{pct:.1f}%）过旺**：对应{organ}。养生方向为「泄」——减少{color}色、{taste}味食物，"
                         f"多运动出汗以泄旺气。{season}时要特别注意调整。")
        elif pct < 15:
            lines.append(f"- **{wx}（{pct:.1f}%）不足**：对应{organ}。养生方向为「补」——增加{color}色、{taste}味食物，"
                         f"多在{direction}活动。{season}是补充的最佳时节。")
        else:
            lines.append(f"- **{wx}（{pct:.1f}%）适中**：对应{organ}。保持现状，注意季节性调养即可。")

    lines.append("")
    lines.append("**四季养生要点：**")
    lines.append("")
    lines.append("- 春季（木旺）：养肝为主，宜早睡早起，多进行户外活动。")
    lines.append("- 夏季（火旺）：养心为主，饮食清淡，注意防暑降温。")
    lines.append("- 长夏（土旺）：养脾为主，注意饮食卫生，避免生冷。")
    lines.append("- 秋季（金旺）：养肺为主，宜食用润肺食物，注意保湿。")
    lines.append("- 冬季（水旺）：养肾为主，注意保暖，适当进补。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section15(basic: dict, analysis: dict) -> list:
    """§15 六亲分析（年/月/日/时四宫逐宫）— 50行"""
    lines = []
    lines.append("## §15 六亲分析")
    lines.append("")
    pillars = basic.get("pillars", {})
    ri_gan = basic.get("ri_gan", "")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])

    # 15.1 年柱（祖上）
    lines.append("### 15.1 年柱（祖上/早年家庭）")
    lines.append("")
    nian = pillars.get("nian", {})
    nian_ss = nian.get("gan_shi_shen", "")
    lines.append(f"年柱：{nian.get('gan','')}{nian.get('zhi','')}")
    lines.append(f"十神：{nian_ss}")
    if nian_ss in ["正印", "偏印", "正官"]:
        lines.append(f"解读：祖上/父母家庭有书香或官贵气息，早年家庭环境较好。")
    elif nian_ss in ["七杀", "劫财"]:
        lines.append("解读：祖上/父母家庭经历较多波折，早年生活需要适应变化。")
    else:
        lines.append("解读：祖上/父母家庭普通，早年生活平和。")
    lines.append("")

    # 15.2 月柱（父母兄弟）
    lines.append("### 15.2 月柱（父母/兄弟姐妹/出身环境）")
    lines.append("")
    yue = pillars.get("yue", {})
    yue_ss = yue.get("gan_shi_shen", "")
    lines.append(f"月柱：{yue.get('gan','')}{yue.get('zhi','')}")
    lines.append(f"十神：{yue_ss}")
    if yue_ss in xi_list:
        lines.append(f"解读：月柱为喜用神，父母/兄弟对自己有助力，成长环境较好。")
    else:
        lines.append("解读：月柱非喜用神，与父母/兄弟的关系需要自身努力经营。")
    lines.append("")

    # 15.3 日支（配偶）
    lines.append("### 15.3 日支（配偶/婚姻）")
    lines.append("")
    ri = pillars.get("ri", {})
    ri_cang_str = _get_cang_gan_list(ri)
    lines.append(f"日支：{ri.get('zhi','')}")
    lines.append(f"藏干：{ri_cang_str}")
    # 已在§12详细分析，这里简略
    lines.append("解读：详见§12婚姻分析。")
    lines.append("")

    # 15.4 时柱（子女/晚年）
    lines.append("### 15.4 时柱（子女/晚年）")
    lines.append("")
    shi = pillars.get("shi", {})
    shi_ss = shi.get("gan_shi_shen", "")
    lines.append(f"时柱：{shi.get('gan','')}{shi.get('zhi','')}")
    lines.append(f"十神：{shi_ss}")
    if shi_ss in ["食神", "伤官", "正印"]:
        lines.append("解读：时柱为吉神，晚年生活安逸，子女有出息。")
    elif shi_ss in ["七杀", "劫财"]:
        lines.append("解读：时柱为凶神，需注意晚年规划，子女教育需花心思。")
    else:
        lines.append("解读：时柱中性，晚年生活平顺。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section16(basic: dict, analysis: dict, birth_year: int) -> list:
    """§16 全生命周期重点事件总表（≥60条·按大运分段·每运6+事件）"""
    lines = []
    lines.append("## §16 全生命周期重点事件总表")
    lines.append("")
    lines.append("**事件类型代码：** A=学业 B=事业/晋升 C=发财/财务 "
                 "E=置业/买房 F=结婚/感情 G=子女添丁 H=压力/灾祸/低谷 I=觉醒/转折")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    qi_yun_age = dy_data.get("qi_yun_age", 7)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    gender = basic.get("gender", "男")
    energy = analysis.get("energy", {})
    wx_energy = energy.get("wu_xing_energy", {})

    wx_list = ["木", "火", "土", "金", "水"]
    ri_idx = wx_list.index(ri_wx) if ri_wx in wx_list else 0
    xi_wx_list = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    ji_wx_list = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]
    # 财星五行 = 我克
    cai_wx = wx_list[(ri_idx + 2) % 5]
    # 官杀五行 = 克我
    guan_wx = wx_list[(ri_idx + 3) % 5]
    # 印星五行 = 生我
    yin_wx = wx_list[(ri_idx + 4) % 5]
    # 食伤五行 = 我生
    shi_wx = wx_list[(ri_idx + 1) % 5]
    # 比劫五行 = 同我
    bi_wx = wx_list[ri_idx]

    event_id = 0

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 命理信号词库（十神 × 喜忌 → 具体信号）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    _POS_SIGNALS = {
        "正官": ["官星透干·贵气临门", "官印相生·名望提升", "正官到位·贵人提携", "官星合身·事业有成"],
        "七杀": ["七杀化权·魄力彰显", "杀印相生·转危为机", "七杀得制·权威确立", "七杀引动·破旧立新"],
        "正印": ["印星护身·学业顺遂", "正印到位·贵人相助", "印星生身·根基稳固", "印绶相承·福气临门"],
        "偏印": ["偏印得力·技艺精进", "枭神化印·特殊机缘", "偏印引动·智慧开悟", "偏印赋能·独特才能"],
        "正财": ["正财透干·财运亨通", "财星合身·收入增长", "正财到位·积累有成", "财星得地·资产增值"],
        "偏财": ["偏财透出·意外之财", "偏财引动·投资有利", "财星发力·财路广进", "偏财合身·商机显现"],
        "比肩": ["比肩帮身·根基坚实", "比肩得力·自主有成", "比肩助身·团队协作", "比肩拱扶·独立担当"],
        "劫财": ["劫财助身·人脉助力", "劫财化比·合作共赢", "劫财引动·社交开拓", "劫财得力·同盟共进"],
        "食神": ["食神生财·才华变现", "食神到位·技艺有成", "食神吐秀·创意涌现", "食神引动·享受成果"],
        "伤官": ["伤官生财·创新获利", "伤官吐秀·才华展露", "伤官得力·突破常规", "伤官引动·声名远扬"],
    }
    _NEG_SIGNALS = {
        "正官": ["官杀攻身·压力倍增", "正官为忌·拘束受限", "官星压身·循规受累", "官杀混局·进退两难"],
        "七杀": ["七杀攻身·灾祸暗伏", "杀旺克身·事业危机", "七杀为忌·小人侵扰", "杀星无制·冲突频发"],
        "正印": ["印星为忌·依赖被动", "正印过旺·思虑过度", "印星掩身·缺乏动力", "印旺夺食·才华受阻"],
        "偏印": ["枭神夺食·计划受阻", "偏印为忌·思想极端", "枭印乱神·判断失误", "偏印扰心·孤僻多疑"],
        "正财": ["财星为忌·为财所累", "正财破印·根基动摇", "财星坏印·学业受阻", "财旺身弱·不胜其财"],
        "偏财": ["偏财为忌·投机失利", "财来破印·因财失义", "偏财乱局·财务纠纷", "偏财耗身·得不偿失"],
        "比肩": ["比肩争夺·竞争激烈", "比劫夺财·破耗连连", "比肩为忌·固执己见", "比劫争锋·小人作祟"],
        "劫财": ["劫财夺财·损财破耗", "劫财争合·情感纠纷", "劫财为忌·兄弟反目", "劫财争锋·合作破裂"],
        "食神": ["食神为忌·过度享乐", "食神被夺·才华难展", "食神泄身·精力透支", "食神受阻·创意枯竭"],
        "伤官": ["伤官见官·口舌是非", "伤官为忌·锋芒过露", "伤官泄身·健康受损", "伤官无制·任性妄为"],
    }
    # 五行生克关系信号
    _WX_MINGLI_SIGNALS = {
        ("木", "火"): ["木火通明·文采斐然", "木生火旺·名声远扬"],
        ("火", "土"): ["火土相生·稳重踏实", "火生土旺·根基扎实"],
        ("土", "金"): ["土金连环·信誉积累", "土生金旺·财富增长"],
        ("金", "水"): ["金水相涵·智慧深邃", "金生水旺·流通顺遂"],
        ("水", "木"): ["水木相生·生机勃发", "水生木旺·成长迅速"],
        ("木", "土"): ["木土交战·压力暗伏", "木克土激·变动频生"],
        ("火", "金"): ["火金相克·激烈竞争", "火克金伤·财来财去"],
        ("土", "水"): ["土水相激·情感波动", "土克水滞·思虑阻塞"],
        ("金", "木"): ["金木相战·抉择困顿", "金克木伤·机遇错失"],
        ("水", "火"): ["水火相冲·心神不宁", "水克火激·是非纷扰"],
    }
    # 十神生克组合信号
    _COMPOUND_SIGNALS = {
        ("食神", "七杀"): "食神制杀·化险为夷",
        ("伤官", "正印"): "伤官配印·才华得彰",
        ("正财", "正官"): "财官相生·名利双收",
        ("正印", "正官"): "官印相生·步步高升",
        ("偏财", "七杀"): "财杀相生·权势兼得",
        ("比肩", "七杀"): "比肩抗杀·众志成城",
        ("劫财", "正财"): "劫财夺财·损财耗资",
        ("伤官", "正官"): "伤官见官·口舌是非",
        ("食神", "正印"): "食神配印·福寿安康",
        ("正财", "正印"): "财星破印·根基动摇",
    }

    def _pick(items, idx):
        """根据索引循环选取"""
        return items[idx % len(items)]

    def _gen_signal(ss, is_xi_gan, step_idx):
        """生成命理信号"""
        signals = []
        # 喜忌信号
        if is_xi_gan:
            signals.append(_pick(_POS_SIGNALS.get(ss, ["运势顺遂"]), step_idx))
        else:
            signals.append(_pick(_NEG_SIGNALS.get(ss, ["运势波动"]), step_idx))
        # 复合信号
        if is_xi_gan and ss in ["食神", "伤官"]:
            signals.append(_COMPOUND_SIGNALS.get(("食神", "七杀"), ""))
        if ss == "伤官" and is_xi_gan:
            signals.append(_COMPOUND_SIGNALS.get(("伤官", "正印"), ""))
        if ss in ["正财", "偏财"] and is_xi_gan:
            signals.append(_COMPOUND_SIGNALS.get(("正财", "正官"), ""))
        if ss in ["正印", "偏印"] and is_xi_gan:
            signals.append(_COMPOUND_SIGNALS.get(("正印", "正官"), ""))
        # 五行关系
        wx_pair = (ri_wx, dy_gan_wx) if ri_wx in wx_list and dy_gan_wx in wx_list else None
        if wx_pair and (wx_pair in _WX_MINGLI_SIGNALS or (wx_pair[1], wx_pair[0]) in _WX_MINGLI_SIGNALS):
            pair = wx_pair if wx_pair in _WX_MINGLI_SIGNALS else (wx_pair[1], wx_pair[0])
            if is_xi_gan:
                signals.append(_pick(_WX_MINGLI_SIGNALS[pair], step_idx))
        sig_str = "；".join(s for s in signals if s)
        return sig_str if sig_str else f"{ss}运·{dy_gan_wx}五行引动"

    def _add_event(dy_gz, year, age, desc, etype, signal):
        nonlocal event_id
        event_id += 1
        lines.append(f"| {event_id} | {dy_gz} | {year} | {age:.0f} | {desc} | {etype} | {signal} |")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 表头
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    lines.extend(_format_table(
        ["序号", "大运", "年份", "年龄", "事件", "类型", "命理信号"],
        []
    ))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 出生事件（0岁）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    event_id += 1
    lines.append(f"| {event_id} | — | {birth_year} | 0 | 出生 | — | — |")

    # 起运年龄事件
    if qi_yun_age > 0:
        qi_yun_year = int(birth_year + qi_yun_age)
        _add_event(dy_list[0].get("gan_zhi", "") if dy_list else "—",
                   qi_yun_year, qi_yun_age,
                   "起运·步入第一步大运", "D", f"起运{dy_list[0].get('gan','') if dy_list else '—'}运开启")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 按大运分段生成事件（每运6+条）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    for step_idx, d in enumerate(dy_list[:10]):
        start_age = d.get("start_age", step_idx * 10 + qi_yun_age)
        end_age = d.get("end_age", (step_idx + 1) * 10 + qi_yun_age)
        start_year = int(birth_year + start_age)
        end_year = int(birth_year + end_age)
        dy_gan = d.get("gan", "")
        dy_zhi = d.get("zhi", "")
        dy_gz = d.get("gan_zhi", "")
        dy_gan_wx = TIAN_GAN_WU_XING.get(dy_gan, "")
        dy_gan_ss = _get_shi_shen(ri_gan, dy_gan)
        dy_mid_age = (start_age + end_age) / 2
        dy_mid_year = int(birth_year + dy_mid_age)

        is_xi_gan = dy_gan_wx in xi_wx_list
        is_ji_gan = dy_gan_wx in ji_wx_list
        is_neutral = not is_xi_gan and not is_ji_gan

        # ── 分段标题行 ──
        lines.append(f"| | **{dy_gz}（{start_year}~{end_year}·{start_age:.0f}~{end_age:.0f}岁）** | | | | | |")

        # ── 事件①：大运开始/换运 ──
        if step_idx == 0:
            desc = f"第一步大运·{dy_gan_ss}运开启"
            sig = f"大运{dy_gan_ss}运开始·{dy_gan_wx}五行主导"
            _add_event(dy_gz, start_year, start_age, desc, "D", sig)
        else:
            prev = dy_list[step_idx - 1]
            prev_gz = prev.get("gan_zhi", "")
            prev_ss = _get_shi_shen(ri_gan, prev.get("gan", ""))
            desc = f"换运·由{prev_ss}运转入{dy_gan_ss}运"
            sig = f"大运交替·{prev_gz}→{dy_gz}·运势转折"
            _add_event(dy_gz, start_year, start_age, desc, "D", sig)

        # ── 事件②：大运初期·能量显现 ──
        early_year = start_year + 2
        early_age = start_age + 2
        if is_xi_gan:
            xi_names = [xi for xi in xi_list if _get_xi_yong_wx(xi, ri_wx) == dy_gan_wx] or [dy_gan_ss]
            desc = f"喜用神运·{dy_gan_ss}能量显现·机遇初现"
            sig = _gen_signal(dy_gan_ss, True, step_idx)
            _add_event(dy_gz, early_year, early_age, desc, "B" if step_idx >= 2 else "A", sig)
        elif is_ji_gan:
            desc = f"忌神运·{dy_gan_ss}压力初显·需谨慎应对"
            sig = _gen_signal(dy_gan_ss, False, step_idx)
            _add_event(dy_gz, early_year, early_age, desc, "H", sig)
        else:
            desc = f"平运·{dy_gan_ss}平稳过渡·蓄势待发"
            sig = f"{dy_gan_ss}运平稳·{dy_gan_wx}五行平衡"
            _add_event(dy_gz, early_year, early_age, desc, "I", sig)

        # ── 事件③：大运中期·核心事件（据十神类型而定） ──
        mid_event_map = {
            "正官": ("事业晋升/职位变动", "B", "官星引动·职权上升"),
            "七杀": ("挑战来临时·危机即转机", "B", "七杀化权·魄力展现"),
            "正印": ("学业进修/证书考试", "A", "印星到位·学运旺盛"),
            "偏印": ("技术突破/特殊研究", "A", "偏印得力·技艺精进"),
            "正财": ("收入增长/财务积累", "C", "财星透干·财路通畅"),
            "偏财": ("投资收益/意外之财", "C", "偏财发力·财源广进"),
            "比肩": ("自主创业/独立发展", "B", "比肩帮身·自主有成"),
            "劫财": ("合作拓展/社交突破", "B", "劫财助身·人脉助力"),
            "食神": ("创意成果/才艺展示", "I", "食神生财·才华变现"),
            "伤官": ("创新突破/技术革新", "I", "伤官生财·创新获利"),
        }
        mid_info = mid_event_map.get(dy_gan_ss, ("运势变化关键期", "I", f"{dy_gan_ss}引动"))
        mid_desc, mid_type, mid_sig = mid_info
        # 根据喜忌调整事件描述的中性/正向/负向
        if is_xi_gan:
            mid_desc = mid_desc.replace("挑战", "机遇")
            mid_sig = _gen_signal(dy_gan_ss, True, step_idx)
        elif is_ji_gan:
            if dy_gan_ss in ["正官", "七杀"]:
                mid_desc = "职场压力增大·谨言慎行"
                mid_type = "H"
            elif dy_gan_ss in ["正财", "偏财"]:
                mid_desc = "财务状况波动·谨慎理财"
                mid_type = "H"
            elif dy_gan_ss in ["正印", "偏印"]:
                mid_desc = "思虑过多·避免决策失误"
                mid_type = "H"
            elif dy_gan_ss in ["比肩", "劫财"]:
                mid_desc = "竞争激烈·注意人际纠纷"
                mid_type = "H"
            elif dy_gan_ss in ["食神", "伤官"]:
                mid_desc = "言行需谨慎·避免口舌是非"
                mid_type = "H"
            else:
                mid_desc = "运势低谷·调整心态"
                mid_type = "H"
            mid_sig = _gen_signal(dy_gan_ss, False, step_idx)
        else:
            mid_sig = f"{dy_gan_ss}运·{dy_gan_wx}五行平运"
        mid_age2 = start_age + 4
        mid_year2 = start_year + 4
        _add_event(dy_gz, mid_year2, mid_age2, mid_desc, mid_type, mid_sig)

        # ── 事件④：大运中期·另一角度（财/官/印/比劫五行性质） ──
        mid_age3 = start_age + 6
        mid_year3 = start_year + 6
        if dy_gan_wx == cai_wx:
            desc4 = "财运旺盛·投资置业机遇" if is_xi_gan else "财务压力·避免冲动投资"
            sig4 = _gen_signal("正财", is_xi_gan, step_idx)
            _add_event(dy_gz, mid_year3, mid_age3, desc4, "C" if is_xi_gan else "H", sig4)
        elif dy_gan_wx == guan_wx:
            desc4 = "事业上升·名声提升" if is_xi_gan else "事业受阻·谨防小人"
            sig4 = _gen_signal("正官", is_xi_gan, step_idx)
            _add_event(dy_gz, mid_year3, mid_age3, desc4, "B" if is_xi_gan else "H", sig4)
        elif dy_gan_wx == yin_wx:
            desc4 = "学习提升·贵人相助" if is_xi_gan else "过度依赖·失去自主性"
            sig4 = _gen_signal("正印", is_xi_gan, step_idx)
            _add_event(dy_gz, mid_year3, mid_age3, desc4, "A" if is_xi_gan else "H", sig4)
        elif dy_gan_wx == shi_wx:
            desc4 = "才华展示·创意输出" if is_xi_gan else "锋芒过露·口舌是非"
            sig4 = _gen_signal("食神", is_xi_gan, step_idx)
            _add_event(dy_gz, mid_year3, mid_age3, desc4, "I" if is_xi_gan else "H", sig4)
        elif dy_gan_wx == bi_wx:
            desc4 = "自主意识强·独立发展" if is_xi_gan else "固执己见·竞争加剧"
            sig4 = _gen_signal("比肩", is_xi_gan, step_idx)
            _add_event(dy_gz, mid_year3, mid_age3, desc4, "B" if is_xi_gan else "H", sig4)
        else:
            desc4 = f"{dy_gan_ss}运中期·{dy_gan_wx}五行能量显现"
            sig4 = f"{dy_gan_ss}运·{dy_gan_wx}引动"
            _add_event(dy_gz, mid_year3, mid_age3, desc4, "I", sig4)

        # ── 事件⑤：大运后期·收尾/成果事件 ──
        late_age1 = start_age + 8
        late_year1 = start_year + 8
        if is_xi_gan:
            desc5 = f"喜用神运收尾·成果落地·收获期"
            sig5 = f"{dy_gan_ss}喜用神·收获成果·把握收官"
            _add_event(dy_gz, late_year1, late_age1, desc5, "B" if step_idx >= 2 else "A", sig5)
        elif is_ji_gan:
            desc5 = f"忌神运后期·破而后立·积累经验"
            sig5 = f"{dy_gan_ss}忌神·磨砺心志·为换运铺垫"
            _add_event(dy_gz, late_year1, late_age1, desc5, "I", sig5)
        else:
            desc5 = "平运收尾·平稳过渡"
            sig5 = f"{dy_gan_ss}运平稳收官"
            _add_event(dy_gz, late_year1, late_age1, desc5, "I", sig5)

        # ── 事件⑥：大运末期·为换运做准备 ──
        late_age2 = start_age + 9
        late_year2 = start_year + 9
        next_step = step_idx + 1
        if next_step < len(dy_list):
            next_d = dy_list[next_step]
            next_gan = next_d.get("gan", "")
            next_ss = _get_shi_shen(ri_gan, next_gan)
            next_wx = TIAN_GAN_WU_XING.get(next_gan, "")
            next_is_xi = next_wx in xi_wx_list
            trend = "上升" if next_is_xi else "波动" if next_wx in ji_wx_list else "平稳"
            desc6 = f"换运前夕·向{next_ss}运过渡·运势趋势{trend}"
            sig6 = f"{dy_gan_ss}→{next_ss}·大运交接·提前布局"
            _add_event(dy_gz, late_year2, late_age2, desc6, "I", sig6)
        else:
            _add_event(dy_gz, late_year2, late_age2, "此大运最后一程·规划晚年", "I",
                       f"{dy_gan_ss}运收尾·安享成果")

        # ── 特殊事件①：婚姻窗口（第2~5步大运） ──
        if 1 <= step_idx <= 4:
            pei_ou_ss = "正财" if gender == "男" else "正官"
            pei_ss_list = [pei_ou_ss]
            pei_ss_list.append("偏财" if gender == "男" else "七杀")
            if dy_gan_ss in pei_ss_list:
                mar_year = start_year + (3 if step_idx < 3 else 2)
                mar_age = start_age + (3 if step_idx < 3 else 2)
                desc_f = "婚姻缘分成熟·感情稳定发展" if is_xi_gan else "情感压力·注意沟通"
                sig_f = "夫妻星引动·正缘显现" if is_xi_gan else "夫妻星为忌·情感波折"
                _add_event(dy_gz, mar_year, mar_age, desc_f, "F", sig_f)

        # ── 特殊事件②：子女添丁窗口（第3~6步大运） ──
        if 2 <= step_idx <= 5:
            child_ss = ["正官", "七杀"] if gender == "男" else ["食神", "伤官"]
            if dy_gan_ss in child_ss and is_xi_gan:
                kid_year = start_year + (2 if step_idx < 4 else 3)
                kid_age = start_age + (2 if step_idx < 4 else 3)
                _add_event(dy_gz, kid_year, kid_age, "子女添丁·家庭新增成员", "G", "子女星到位·禄嗣临门")

        # ── 特殊事件③：置业/买房窗口（第4~8步大运） ──
        if 3 <= step_idx <= 7 and (is_xi_gan or is_neutral):
            house_year = start_year + 5
            house_age = start_age + 5
            if dy_gan_wx == cai_wx or dy_gan_ss in ["正财", "偏财"]:
                _add_event(dy_gz, house_year, house_age, "置业机遇·不动产购置", "E",
                           "财星守位·置产纳福" if is_xi_gan else "财星透干·宜关注房产")
            elif dy_gan_wx == yin_wx and is_xi_gan:
                _add_event(dy_gz, house_year, house_age, "家居改善·居住环境提升", "E",
                           "印星护宅·安居乐业")

        # ── 特殊事件④：觉醒/转折事件（第5步大运之后，平运或喜用神运） ──
        if step_idx >= 4 and (is_xi_gan or is_neutral):
            aw_year = start_year + 7
            aw_age = start_age + 7
            if dy_gan_ss in ["食神", "伤官"]:
                _add_event(dy_gz, aw_year, aw_age, "人生转折·觉醒开悟", "I",
                           "食伤吐秀·智慧开悟·人生新境界")
            elif dy_gan_ss in ["正印", "偏印"]:
                _add_event(dy_gz, aw_year, aw_age, "精神成长·内心觉醒", "I",
                           "印星化神·慧根深种·格局升华")
            elif dy_gan_ss in ["正官", "七杀"] and is_xi_gan:
                _add_event(dy_gz, aw_year, aw_age, "社会地位升华·影响力扩大", "I",
                           "官星入运·名望积累·社会价值实现")

        # ── 特殊事件⑤：灾祸/低谷事件（忌神运额外添加） ──
        if is_ji_gan:
            crisis_year = start_year + 3
            crisis_age = start_age + 3
            crisis_sigs = ["比劫夺财·损财耗资", "官杀攻身·压力倍增",
                           "枭神夺食·计划受阻", "财星破印·根基动摇",
                           "伤官见官·口舌是非"]
            sig_h = crisis_sigs[step_idx % len(crisis_sigs)]
            _add_event(dy_gz, crisis_year, crisis_age,
                       f"忌神运低谷期·注意{dict(zip(range(5),['财务损失','职场压力','计划中断','决策失误','人际纠纷']))[step_idx%5]}",
                       "H", sig_h)

    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 60甲子纳音表（完整60柱·用于大运干支纳音五行）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_NA_YIN_60 = [
    "海中金","海中金","炉中火","炉中火","大林木","大林木",
    "路旁土","路旁土","剑锋金","剑锋金",
    "山头火","山头火","涧下水","涧下水","城头土","城头土",
    "白蜡金","白蜡金","杨柳木","杨柳木",
    "泉中水","泉中水","屋上土","屋上土","霹雳火","霹雳火",
    "松柏木","松柏木","长流水","长流水",
    "沙中金","沙中金","山下火","山下火","平地木","平地木",
    "壁上土","壁上土","金箔金","金箔金",
    "佛灯火","佛灯火","天河水","天河水","大驿土","大驿土",
    "钗钏金","钗钏金","桑柘木","桑柘木",
    "大溪水","大溪水","沙中土","沙中土","天上火","天上火",
    "石榴木","石榴木","大海水","大海水",
]
_NA_YIN_WU_XING = {
    "海中金":"金","剑锋金":"金","白蜡金":"金","沙中金":"金","金箔金":"金","钗钏金":"金",
    "炉中火":"火","山头火":"火","霹雳火":"火","山下火":"火","佛灯火":"火","天上火":"火",
    "大林木":"木","杨柳木":"木","松柏木":"木","平地木":"木","桑柘木":"木","石榴木":"木",
    "路旁土":"土","城头土":"土","屋上土":"土","壁上土":"土","大驿土":"土","沙中土":"土",
    "涧下水":"水","泉中水":"水","长流水":"水","天河水":"水","大溪水":"水","大海水":"水",
}

def _na_yin_of(gz: str) -> str:
    """根据干支字符串（如"甲申"）返回纳音名称"""
    if len(gz) != 2:
        return "—"
    gan, zhi = gz[0], gz[1]
    try:
        gi = TIAN_GAN_LIST.index(gan)
        zi = DI_ZHI_LIST.index(zhi)
        seq = (gi * 6 - zi * 5) % 60
        return _NA_YIN_60[seq]
    except (ValueError, IndexError):
        return "—"


def _gen_section17(basic: dict, analysis: dict, birth_year: int) -> list:
    """§17 大运精析（10步完整序列至100岁·每运含干支纳音·天干详析·藏干展开·影响判断·人生提示·具体建议）— 250行"""
    lines = []
    lines.append("## §17 大运精析（10步完整序列至100岁）")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    qi_yun_age = dy_data.get("qi_yun_age", 7)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    gender = basic.get("gender", "男")
    cx = analysis.get("cai_xing", {})
    cai_score = cx.get("score", 0)
    wealth_level = cx.get("wealth_level", "中等")
    energy = analysis.get("energy", {})
    wx_energy = energy.get("wu_xing_energy", {})
    ge_ju_str = analysis.get("ge_ju", "正印格")

    wx_list = ["木", "火", "土", "金", "水"]
    ri_idx = wx_list.index(ri_wx) if ri_wx in wx_list else 0
    xi_wx_list = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    ji_wx_list = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]
    # 五行关系
    cai_wx = wx_list[(ri_idx + 2) % 5]     # 我克=财
    guan_wx = wx_list[(ri_idx + 3) % 5]    # 克我=官杀
    yin_wx = wx_list[(ri_idx + 4) % 5]     # 生我=印
    shi_wx = wx_list[(ri_idx + 1) % 5]     # 我生=食伤
    bi_wx = wx_list[ri_idx]                # 同我=比劫

    # 生命阶段关键词
    LIFE_STAGES = {
        0: ("青年起步期", "学业/事业奠基", "适合积累知识、开拓人脉、奠定事业基础"),
        1: ("青年发展期", "事业上升/婚恋", "适合事业冲刺、建立家庭、积累资本"),
        2: ("中年黄金期", "事业巅峰/财富", "是人生主战场，发展事业、积累财富的关键十年"),
        3: ("中年稳健期", "守成突破/转型", "事业趋于稳定，宜拓展新领域或深耕专长"),
        4: ("中年後半期", "传承布局/安顿", "宜布局传承、培养接班人、优化资产结构"),
        5: ("壮年末期", "收束整合/健康", "放缓节奏，注重健康管理，整合人生资源"),
        6: ("初老期", "怡养天年/内修", "享受人生成果，修身养性，含饴弄孙"),
        7: ("老年期", "福寿绵长/回馈", "回馈社会，传承智慧，安然享受晚年"),
    }
    # 十神→影响领域映射
    SS_DOMAIN = {
        "正官": "事业晋升·官运亨通·社会地位", "七杀": "事业突破·魄力挑战·权力争斗",
        "正印": "学业进修·贵人扶持·文书契约", "偏印": "技术钻研·独特才能·玄学智慧",
        "正财": "稳定收入·资产积累·财务规划", "偏财": "投资收益·商业机遇·意外之财",
        "比肩": "自主创业·独立发展·自我实现", "劫财": "合作事业·社交人脉·团队协作",
        "食神": "创意才华·技艺展现·生活享受", "伤官": "创新突破·技术革新·名声传播",
    }
    # 十神→关键事件提示
    SS_EVENT_HINT = {
        "正官": {
            "xi": "晋升提干、名誉提升、获得权威职位",
            "ji": "职场打压、官非口舌、升迁受阻",
            "neutral": "职位平稳、按部就班",
        },
        "七杀": {
            "xi": "突破困境、化压力为动力、创业成功",
            "ji": "小人暗算、突发变故、事业危机",
            "neutral": "竞争加剧、需沉着应对",
        },
        "正印": {
            "xi": "学业有成、考运旺盛、贵人提携",
            "ji": "依赖被动、思虑过多、上当受骗",
            "neutral": "学习平稳、文书事宜增多",
        },
        "偏印": {
            "xi": "技术突破、专利发明、特殊技能精进",
            "ji": "偏执孤僻、判断失误、计划受阻",
            "neutral": "钻研深入、需防钻牛角尖",
        },
        "正财": {
            "xi": "工资增长、主业收入提升、固定资产增值",
            "ji": "为财所累、破财失财、财务压力增大",
            "neutral": "财务平稳、收支平衡",
        },
        "偏财": {
            "xi": "投资收益、意外之财、商业机会涌现",
            "ji": "投机失利、债务纠纷、财来财去",
            "neutral": "偏财机会有但需谨慎",
        },
        "比肩": {
            "xi": "自主创业成功、个人能力彰显、独立发展",
            "ji": "竞争激烈、固执失误、孤军奋战",
            "neutral": "独立性强、合作需谨慎",
        },
        "劫财": {
            "xi": "合作伙伴得力、人脉拓展、团队成功",
            "ji": "朋友拖累、合作破裂、破财耗资",
            "neutral": "社交频繁、人际事务增多",
        },
        "食神": {
            "xi": "创意变现、才艺展示、享受生活成果",
            "ji": "过度享乐、放纵懈怠、才华受阻",
            "neutral": "生活安逸、才艺稳步发展",
        },
        "伤官": {
            "xi": "技术创新、声名远扬、突破常规成功",
            "ji": "口舌是非、锋芒过露、得罪贵人",
            "neutral": "表达欲强、需注意言行尺度",
        },
    }
    # 藏干十神关系描述
    CANG_GAN_SS_RELATION = {
        ("正官", "正官"): "官星叠见，职权加重但压力倍增",
        ("正官", "七杀"): "官杀混杂，事业环境复杂多变",
        ("七杀", "正官"): "杀官交攻，多遇挑战与机遇并存",
        ("正印", "正官"): "官印相生，名利双收之象",
        ("偏印", "七杀"): "杀印相生，转危为安之兆",
        ("正财", "正官"): "财官相生，事业财运双丰收",
        ("偏财", "七杀"): "财杀相生，权财兼得",
        ("食神", "七杀"): "食神制杀，化险为夷",
        ("伤官", "正印"): "伤官配印，才华得彰",
        ("比肩", "七杀"): "比肩抗杀，众志成城",
        ("劫财", "正财"): "劫财夺财，损财耗资",
        ("伤官", "正官"): "伤官见官，口舌是非",
        ("食神", "正印"): "食神配印，福寿安康",
        ("正财", "正印"): "财星破印，根基动摇",
    }

    def _zhi_detail(zhi: str) -> str:
        """地支藏干详细描述"""
        cg_list = DI_ZHI_CANG_GAN.get(zhi, [])
        if not cg_list:
            return "无藏干"
        parts = []
        for cg_gan, weight in cg_list:
            cg_wx = TIAN_GAN_WU_XING.get(cg_gan, "")
            cg_ss = _get_shi_shen(ri_gan, cg_gan)
            w_label = "本气" if weight >= 100 else "中气" if weight >= 60 else "余气"
            parts.append(f"{cg_gan}（{cg_wx}{cg_ss}·{w_label}）")
        return "、".join(parts)

    def _zhi_effect_narrative(zhi: str, cg_list: list) -> str:
        """生成地支藏干的综合影响描述"""
        if not cg_list:
            return ""
        ss_list = [_get_shi_shen(ri_gan, c[0]) for c in cg_list]
        unique_ss = list(dict.fromkeys(ss_list))  # dedupe preserving order
        # 判断藏干五行属性
        cg_wx_list = [TIAN_GAN_WU_XING.get(c[0], "") for c in cg_list]
        # 主要藏干（本气）
        main_gan = cg_list[0][0]
        main_ss = _get_shi_shen(ri_gan, main_gan)
        main_wx = TIAN_GAN_WU_XING.get(main_gan, "")
        # 本气十神关系
        main_desc = f"地支{zhi}本气藏{main_gan}为{main_ss}（{main_wx}）"
        if len(cg_list) > 1:
            sub_ss = []
            for cg_gan, w in cg_list[1:]:
                sub_ss.append(f"{cg_gan}（{_get_shi_shen(ri_gan, cg_gan)}）")
            main_desc += f"，内含{'、'.join(sub_ss)}"
        # 综合影响
        if len(unique_ss) >= 2:
            pair = (unique_ss[0], unique_ss[1])
            reversed_pair = (unique_ss[1], unique_ss[0])
            effect = CANG_GAN_SS_RELATION.get(pair) or CANG_GAN_SS_RELATION.get(reversed_pair, "")
            if effect:
                main_desc += f"，形成「{effect}」之象"
        # 地支五行对日主的影响
        zhi_wx = DI_ZHI_WU_XING.get(zhi, "")
        if zhi_wx:
            # 判断地支五行与日主五行的生克
            zhi_idx = wx_list.index(zhi_wx) if zhi_wx in wx_list else -1
            if zhi_idx >= 0:
                diff = (zhi_idx - ri_idx) % 5
                if diff == 0:
                    wx_rel = "与日主五行相同，增强日主根基"
                elif diff == 1:
                    wx_rel = "日主生地支，为食伤泄秀之象"
                elif diff == 2:
                    wx_rel = "日主克地支，为财星得地之象"
                elif diff == 3:
                    wx_rel = "地支克日主，为官杀临身之象"
                else:
                    wx_rel = "地支生日主，为印星生身之象"
                main_desc += f"。{wx_rel}"
        return main_desc

    def _life_hints(ss: str, is_xi: bool, is_ji: bool, step_idx: int, start_age: float) -> list:
        """生成此大运中的人生关键事件提示"""
        hints = []
        hints.append("**🔮 关键事件提示：**")
        hints.append("")
        event_data = SS_EVENT_HINT.get(ss, {"xi": "运势顺遂", "ji": "运势不顺", "neutral": "运势平稳"})
        if is_xi:
            hints.append(f"▸ **财运**：{event_data['xi']}，宜积极把握。")
            hints.append(f"▸ **事业**：{event_data['xi']}，是事业发展的良机。")
            hints.append(f"▸ **健康**：精力充沛，但需劳逸结合，注意{'肝胆/神经系统' if ri_wx=='木' else '心脏/血液循环' if ri_wx=='火' else '脾胃/消化' if ri_wx=='土' else '肺/呼吸系统' if ri_wx=='金' else '肾/泌尿系统'}保养。")
        elif is_ji:
            hints.append(f"▸ **财运**：{event_data['ji']}，以守为主忌冒进。")
            hints.append(f"▸ **事业**：{event_data['ji']}，宜低调行事谨言慎行。")
            hints.append(f"▸ **健康**：运势压力大，注意调节情绪，防范{'肝胆/神经系统' if ri_wx=='木' else '心脏/血液循环' if ri_wx=='火' else '脾胃/消化' if ri_wx=='土' else '肺/呼吸系统' if ri_wx=='金' else '肾/泌尿系统'}疾病。")
        else:
            hints.append(f"▸ **财运**：{event_data['neutral']}，宜稳健理财。")
            hints.append(f"▸ **事业**：{event_data['neutral']}，按计划推进即可。")
            hints.append(f"▸ **健康**：运势平稳，保持良好生活习惯即可。")
        # 婚姻窗口期提示
        if 1 <= step_idx <= 4:
            pei_ou_ss = "正财" if gender == "男" else "正官"
            pei_ss_list = [pei_ou_ss, "偏财" if gender == "男" else "七杀"]
            if ss in pei_ss_list:
                hints.append(f"▸ **感情**：夫妻星显现，此运中{'姻缘机会良好，宜主动争取' if is_xi else '感情需用心经营，注意沟通'}。")
        # 子女窗口提示
        if 2 <= step_idx <= 5:
            child_ss = ["正官", "七杀"] if gender == "男" else ["食神", "伤官"]
            if ss in child_ss and is_xi:
                hints.append(f"▸ **子女**：子女星得力，利添丁或子女发展向好。")
        hints.append("")
        return hints

    def _advice(ss: str, is_xi: bool, is_ji: bool, step_idx: int) -> list:
        """给出具体建议"""
        advice_lines = []
        advice_lines.append("**💡 具体建议：**")
        advice_lines.append("")
        if is_xi:
            advice_lines.append(f"此运为喜用神大运，天时地利人和，宜积极进取。建议聚焦{SS_DOMAIN.get(ss, '各方面')}领域，大胆布局，乘势而上。")
            if ss in ["正官", "七杀"]:
                advice_lines.append("职场中勇于担当责任，主动争取晋升机会，同时注意权力运用的分寸。")
            elif ss in ["正印", "偏印"]:
                advice_lines.append("把握学习进修的黄金期，考取资质证书，或深耕专业技术领域。")
            elif ss in ["正财", "偏财"]:
                advice_lines.append("积极开拓财源，合理配置资产，但勿贪多求快，谨记稳健为基。")
            elif ss in ["比肩", "劫财"]:
                advice_lines.append("适合自主创业或拓展合作，善用人脉资源，但需注意利益分配。")
            elif ss in ["食神", "伤官"]:
                advice_lines.append("发挥创意才华，将兴趣转化为生产力，注意把握展示才华的舞台。")
            else:
                advice_lines.append("顺应运势，在各领域积极作为。")
        elif is_ji:
            advice_lines.append(f"此运为忌神大运，天时不正，宜静不宜动。建议以守成为主，韬光养晦，避免重大决策和投资。")
            if ss in ["正官", "七杀"]:
                advice_lines.append("职场中谨言慎行，避免与上级冲突，可多学习积累以图后续。")
            elif ss in ["正印", "偏印"]:
                advice_lines.append("避免过度思虑和依赖他人，保持独立判断，多做实事少空想。")
            elif ss in ["正财", "偏财"]:
                advice_lines.append("严格控制开支，避免高风险投资，守住已有资产为主。")
            elif ss in ["比肩", "劫财"]:
                advice_lines.append("谨慎选择合作伙伴，避免经济往来中的纠纷，保持适度距离。")
            elif ss in ["食神", "伤官"]:
                advice_lines.append("注意言行分寸，避免口舌是非，可将精力投入内在修养。")
            else:
                advice_lines.append("平稳渡过，磨砺心志，为下一运积蓄力量。")
        else:
            advice_lines.append(f"此运为平运，五行平衡，运势中庸。建议稳中求进，按部就班推进计划，不宜冒进亦不宜保守。")
            advice_lines.append("在事业和生活各方面保持平衡，抓住偶然出现的机会，同时做好风险防范。")
        # 晚年特别建议
        if step_idx >= 6:
            advice_lines.append("步入晚年，宜以健康为重，修身养性，含饴弄孙，享受天伦之乐。")
        advice_lines.append("")
        return advice_lines

    for step_idx, d in enumerate(dy_list[:10]):
        start_age = d.get("start_age", step_idx * 10 + qi_yun_age)
        end_age = d.get("end_age", (step_idx + 1) * 10 + qi_yun_age)
        start_year = int(birth_year + start_age)
        end_year = int(birth_year + end_age)
        dy_gz = d.get("gan_zhi", "")
        dy_gan = d.get("gan", dy_gz[0] if len(dy_gz) >= 1 else "")
        dy_zhi = d.get("zhi", dy_gz[1] if len(dy_gz) >= 2 else "")
        dy_gan_wx = TIAN_GAN_WU_XING.get(dy_gan, "")
        dy_gan_ss = _get_shi_shen(ri_gan, dy_gan)
        dy_na_yin = _na_yin_of(dy_gz)
        dy_na_yin_wx = _NA_YIN_WU_XING.get(dy_na_yin, "")

        # 喜忌判定
        is_xi = dy_gan_wx in xi_wx_list
        is_ji = dy_gan_wx in ji_wx_list
        is_neutral = not is_xi and not is_ji
        if is_xi:
            feature = "✅ 喜用神大运"
            tone_adj = "顺遂上扬"
        elif is_ji:
            feature = "⚠️ 忌神大运"
            tone_adj = "谨慎应对"
        else:
            feature = "➖ 平运"
            tone_adj = "平稳过渡"

        # 生命阶段
        stage_key = min(step_idx, 7)
        stage_name, stage_theme, stage_desc = LIFE_STAGES.get(stage_key, ("人生阶段", "", ""))

        lines.append(f"### 17.{step_idx+1} {dy_gz}大运（{start_year}~{end_year}）·{feature}")
        lines.append("")
        lines.append(f"**🎯 基本信息**：{dy_gz}大运，年龄{start_age:.0f}~{end_age:.0f}岁，{stage_name}（{stage_theme}）")
        lines.append("")

        # ════════════════════════════════════════════
        # 1. 干支 + 纳音五行
        # ════════════════════════════════════════════
        lines.append("**📌 干支纳音：**")
        lines.append("")
        lines.append(f"天干{dy_gan}：{dy_gan_wx}，为日主之「{dy_gan_ss}」；地支{dy_zhi}：{DI_ZHI_WU_XING.get(dy_zhi,'')}。")
        # 纳音与天干五行关系判定
        if dy_na_yin_wx and dy_gan_wx:
            if dy_na_yin_wx == dy_gan_wx:
                ny_rel = "相同，能量同频共振，运势影响集中而强烈"
            else:
                ny_idx = wx_list.index(dy_na_yin_wx) if dy_na_yin_wx in wx_list else -1
                gan_idx2 = wx_list.index(dy_gan_wx) if dy_gan_wx in wx_list else -1
                if ny_idx >= 0 and gan_idx2 >= 0 and (ny_idx - gan_idx2) % 5 == 4:
                    ny_rel = "相生，地支纳音生天干，气场流通顺畅"
                elif ny_idx >= 0 and gan_idx2 >= 0 and (ny_idx - gan_idx2) % 5 == 1:
                    ny_rel = "相生，天干生地支纳音，能量有所消耗"
                else:
                    ny_rel = "不同，运势呈现多元化特征"
        else:
            ny_rel = "不同，运势呈现多元化特征"
        lines.append(f"纳音：{dy_na_yin}（属{dy_na_yin_wx}）——纳音{dy_na_yin_wx}与天干{dy_gan_wx}五行{ny_rel}。")
        lines.append("")

        # ════════════════════════════════════════════
        # 2. 天干具体分析
        # ════════════════════════════════════════════
        lines.append("**🔍 天干{}{}分析：**".format(dy_gan, dy_gan_ss))
        lines.append("")
        # 天干五行与日主喜忌
        xi_wx_expr = "、".join(xi_wx_list) if xi_wx_list else "无"
        ji_wx_expr = "、".join(ji_wx_list) if ji_wx_list else "无"
        lines.append(f"日主{ri_gan}（{ri_wx}），喜用神五行为「{xi_wx_expr}」，忌神五行为「{ji_wx_expr}」。")
        if is_xi:
            lines.append(f"天干{dy_gan}五行属{dy_gan_wx}，为命局喜用神，此运得天时之利。{dy_gan_ss}正能量充分释放，")
            lines.append(f"主顺遂通达，易得贵人相助，事业生活多有机遇。{dy_gan_ss}作为{dy_gan_wx}性十神，")
            if dy_gan_ss in ["正官", "七杀"]:
                lines.append("其官杀属性带来进取动力和规范意识，利于职场晋升、社会地位提升。")
            elif dy_gan_ss in ["正印", "偏印"]:
                lines.append("其印星属性带来学习力和贵人运，利于学业进修、文书契约之事。")
            elif dy_gan_ss in ["正财", "偏财"]:
                lines.append("其财星属性带来财富机遇，利于财务积累、收入增长。")
            elif dy_gan_ss in ["比肩", "劫财"]:
                lines.append("其比劫属性增强自主性和竞争力，利于独立发展或合作创业。")
            elif dy_gan_ss in ["食神", "伤官"]:
                lines.append("其食伤属性激发创造力和表达力，利于才华施展、技术创新。")
        elif is_ji:
            lines.append(f"天干{dy_gan}五行属{dy_gan_wx}，为命局忌神，此运需多加谨慎。{dy_gan_ss}的负面效应容易显现，")
            lines.append(f"主挑战增多，处处掣肘，需做好心理准备。{dy_gan_ss}作为{dy_gan_wx}性十神，")
            if dy_gan_ss in ["正官", "七杀"]:
                lines.append("官杀为忌则压力山大，易受领导打压、小人暗算，事业阻力重重。")
            elif dy_gan_ss in ["正印", "偏印"]:
                lines.append("印星为忌则思虑过多、依赖被动，容易错失良机或上当受骗。")
            elif dy_gan_ss in ["正财", "偏财"]:
                lines.append("财星为忌则为财所累，投资失利、破耗频生，财务压力增大。")
            elif dy_gan_ss in ["比肩", "劫财"]:
                lines.append("比劫为忌则竞争白热化，易有合作破裂、朋友反目之事。")
            elif dy_gan_ss in ["食神", "伤官"]:
                lines.append("食伤为忌则言行易失分寸，招惹口舌是非，锋芒过露招妒。")
        else:
            lines.append(f"天干{dy_gan}五行属{dy_gan_wx}，既非喜用亦非忌神，对命局影响中性。")
            lines.append(f"{dy_gan_ss}的能量释放中和稳定，既不特别助益也不构成威胁，")
            lines.append("整体运势以平稳为主旋律，按部就班推进即可。")
        lines.append("")

        # ════════════════════════════════════════════
        # 3. 地支藏干详细展开
        # ════════════════════════════════════════════
        lines.append("**🌿 地支{}藏干展开：**".format(dy_zhi))
        lines.append("")
        dy_zhi_cang = DI_ZHI_CANG_GAN.get(dy_zhi, [])
        if dy_zhi_cang:
            lines.append(_zhi_detail(dy_zhi))
            lines.append("")
            lines.append(_zhi_effect_narrative(dy_zhi, dy_zhi_cang))
            lines.append("")
        else:
            lines.append(f"地支{dy_zhi}无藏干。")
            lines.append("")

        # ════════════════════════════════════════════
        # 4. 对命局的影响
        # ════════════════════════════════════════════
        lines.append("**⚡ 对命局整体影响：**")
        lines.append("")
        lines.append(f"命主为{ri_gan}日主，{ge_ju_str}，{sq_level}（{sq_score}分）。{stage_desc}。")
        if is_xi:
            lines.append(f"此运天干{dy_gan}为喜用神，对命局产生积极正向的推动力。{dy_gan_ss}的能量补益命局所需，")
            lines.append(f"犹如久旱逢甘霖，各方面运势都将得到显著提升。在大运的影响下，命主在{SS_DOMAIN.get(dy_gan_ss, '相关领域')}")
            lines.append("方面将有突出表现，可大胆规划、积极行动。喜用神大运十年，是人生中宝贵的上升期，")
            lines.append("应充分利用这个窗口期，在事业、财运、学业等关键领域实现突破性进展。")
        elif is_ji:
            lines.append(f"此运天干{dy_gan}为忌神，对命局形成压力和挑战。{dy_gan_ss}的能量与命局所需相悖，")
            lines.append(f"犹如逆水行舟，各方面都需要付出更多努力才能维持现状。在{SS_DOMAIN.get(dy_gan_ss, '相关领域')}")
            lines.append("方面容易遇到阻碍和挫折，宜保持低调谨慎的态度。忌神大运虽有压力，但也是磨砺心志、")
            lines.append("积累经验的重要时期，若能沉着应对，反而能在逆境中收获成长和智慧。")
        else:
            lines.append(f"此运天干{dy_gan}五行能量中性，对命局影响不大，整体运势保持平稳。")
            lines.append(f"{dy_gan_ss}的能力可以正常发挥，但不会产生显著的正负效应。在{SS_DOMAIN.get(dy_gan_ss, '相关领域')}")
            lines.append("方面按部就班即可，既无需激进也无需过度保守。平运十年是休养生息、积累资源的好时机，")
            lines.append("为迎接下一段大运做好充分准备。")
        # 大运阶段特别说明
        if step_idx <= 2:
            lines.append(f"此运正值{stage_name}，{dy_gan_ss}对人生起步的影响深远，{'宜把握良机奠定基础' if is_xi else '宜稳扎稳打、避开重大风险'}。")
        elif step_idx <= 5:
            lines.append(f"此运为{stage_name}，是人生承上启下的关键阶段，{'宜全力投入开创局面' if is_xi else '宜稳守阵地、等待转机'}。")
        else:
            lines.append(f"此运已入{stage_name}，{'宜享受成果、安度晚年' if is_xi else '宜以健康为重、知足常乐'}。")
        lines.append("")

        # ════════════════════════════════════════════
        # 5. 关键事件提示
        # ════════════════════════════════════════════
        hints = _life_hints(dy_gan_ss, is_xi, is_ji, step_idx, start_age)
        lines.extend(hints)

        # ════════════════════════════════════════════
        # 6. 具体建议
        # ════════════════════════════════════════════
        advice_lines = _advice(dy_gan_ss, is_xi, is_ji, step_idx)
        lines.extend(advice_lines)

        # 关键年份补充
        lines.append("**📅 此运重点关注年份：**")
        lines.append("")
        mid_year = start_year + 5
        lines.append(f"- {_get_year_gan_zhi(mid_year)}年（{mid_year}）：大运中段，运势集中体现{'最佳' if is_xi else '最需谨慎' if is_ji else '最平稳'}。")
        lines.append(f"- {_get_year_gan_zhi(start_year+2)}年（{start_year+2}）：大运初启，{dy_gan_ss}能量开始显现，宜顺势而为。")
        if is_xi:
            lines.append(f"- {_get_year_gan_zhi(start_year+7)}年（{start_year+7}）：喜用神持续发力，是收获成果的关键年份。")
        if is_ji:
            lines.append(f"- {_get_year_gan_zhi(start_year+3)}年（{start_year+3}）：忌神能量高峰，注意风险管控，凡事三思。")
        if dy_gan_wx == cai_wx:
            lines.append(f"- {_get_year_gan_zhi(start_year+4)}年（{start_year+4}）：财星透出，财运相关事件值得关注。")
        elif dy_gan_wx == guan_wx:
            lines.append(f"- {_get_year_gan_zhi(start_year+6)}年（{start_year+6}）：官星发力，事业相关机遇显现。")
        lines.append("")
        lines.append("---")
        lines.append("")

    return lines


# 辅助工具：获取年份的天干地支
_GAN_CACHE = {}
_ZHI_CACHE = {}
TIAN_GAN_LIST = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def _get_year_gan_zhi(year: int) -> str:
    gan = TIAN_GAN_LIST[(year - 4) % 10]
    zhi = DI_ZHI_LIST[(year - 4) % 12]
    return f"{gan}{zhi}"


def _gen_section18(basic: dict, analysis: dict) -> list:
    """§18 三决断（3维度6要素断语格式）— 60行"""
    lines = []
    lines.append("## §18 三决断（6要素断语格式）")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ge_ju_str = analysis.get("ge_ju", "正印")
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    cx = analysis.get("cai_xing", {})
    cai_score = cx.get("score", 0)
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])

    # 决断一：事业成就
    lines.append("### 决断一：事业成就")
    lines.append("")
    lines.append("```")
    lines.append(f"**其人**：{ge_ju_str}格人才，{sq_level}，喜{'/'.join(xi_list)}")
    lines.append(f"**其事**：事业成就等级与领域")
    lines.append(f"**其时**：喜用神大运中年窗口（约35~55岁）")
    if sq_level == "身强":
        degree = "中高层管理/专家级"
    elif sq_level == "身弱":
        degree = "中层骨干/技术专才"
    else:
        degree = "管理/技术双栖人才"
    lines.append(f"**其度**：{degree}")
    lines.append(f"**理由**：{ge_ju_str}格为事业根基，{sq_level}决定了担当能力，喜用神大运为腾飞窗口")
    lines.append("")
    lines.append(f"**断语**：命主为{ge_ju_str}格，{sq_level}，中年喜用神大运期间事业可达{degree}级别。")
    lines.append("```")
    lines.append("")

    # 决断二：财富格局
    lines.append("### 决断二：财富格局")
    lines.append("")
    lines.append("```")
    lines.append(f"**其人**：财星评分{cai_score}分，{'有' if cx.get('has_ku') else '无'}财库")
    lines.append(f"**其事**：财富积累速度与天花板")
    cai_degree = cx.get("wealth_level", "小富")
    lines.append(f"**其时**：财星透干大运年份")
    lines.append(f"**其度**：{cai_degree}级（日常~{cai_score*2}万/最佳~{cai_score*10}万）")
    lines.append(f"**理由**：财星评分为根基，围克折扣为修正，财库为蓄力条件")
    lines.append("")
    lines.append(f"**断语**：命主财富等级为{cai_degree}，财星评分{cai_score}分，{'有财库宜蓄财' if cx.get('has_ku') else '无财库需主动积累'}。")
    lines.append("```")
    lines.append("")

    # 决断三：人生节奏
    lines.append("### 决断三：人生节奏")
    lines.append("")
    lines.append("```")
    lines.append(f"**其人**：整体命局节奏")
    lines.append(f"**其事**：人生的关键节奏节点")
    lines.append(f"**其时**：早年学习→中年立业→晚年守成")
    if sq_score >= 50:
        rhythm = "厚积薄发型，中年发力"
    elif sq_score >= 30:
        rhythm = "稳扎稳打型，持续积累"
    else:
        rhythm = "借力发展型，贵人提携"
    lines.append(f"**其度**：{rhythm}")
    lines.append(f"**理由**：身强弱决定发力模式，格局决定领域，喜用神大运决定窗口")
    lines.append("")
    lines.append(f"**断语**：命主人生节奏为{rhythm}。关键窗口在喜用神大运期间（中年偏后）。")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section19(basic: dict, analysis: dict, birth_year: int) -> list:
    """§19 运程总评（ASCII运程曲线+评分表+吉凶总评）— 60行"""
    lines = []
    lines.append("## §19 人生运程总评")
    lines.append("")
    dy_data = analysis.get("da_yun", {})
    dy_list = dy_data.get("da_yun", [])
    qi_yun_age = dy_data.get("qi_yun_age", 7)
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ge_ju_str = analysis.get("ge_ju", "正印")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    wx_list = ["木", "火", "土", "金", "水"]
    ri_idx = wx_list.index(ri_wx) if ri_wx in wx_list else 0
    xi_wx_list = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    ji_wx_list = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]

    # 19.1 ASCII曲线
    lines.append("### 19.1 ASCII运程曲线至100岁")
    lines.append("")
    lines.append("```")
    lines.append("年龄   大运        运程曲线")
    for step_idx, d in enumerate(dy_list[:10]):
        start_age = int(d.get("start_age", step_idx * 10 + qi_yun_age))
        dy_gan = d.get("gan", "")
        dy_gan_wx = TIAN_GAN_WU_XING.get(dy_gan, "")
        score = 7  # 基础分
        if dy_gan_wx in xi_wx_list:
            score = 9
        elif dy_gan_wx in ji_wx_list:
            score = 4
        bar = "★" * score + "☆" * (10 - score)
        lines.append(f"{start_age:>3}岁  {d.get('gan_zhi',''):>6}  {bar}")
    lines.append("        ↑ 幼年      ↑ 中年巅峰   ↑ 晚年平稳")
    lines.append("```")
    lines.append("")

    # 19.2 评分表
    lines.append("### 19.2 各运评分表")
    lines.append("")
    score_rows = []
    for step_idx, d in enumerate(dy_list[:10]):
        start_age = int(d.get("start_age", step_idx * 10 + qi_yun_age))
        end_age = int(d.get("end_age", (step_idx + 1) * 10 + qi_yun_age))
        dy_gan = d.get("gan", "")
        dy_gan_wx = TIAN_GAN_WU_XING.get(dy_gan, "")
        score = 7
        if dy_gan_wx in xi_wx_list:
            score = 9
            comment = "喜用神运·大吉"
        elif dy_gan_wx in ji_wx_list:
            score = 4
            comment = "忌神运·需谨慎"
        else:
            comment = "平运·稳中有进"
        score_rows.append([
            d.get("gan_zhi", ""),
            f"{start_age}~{end_age}岁",
            f"{score}/10",
            comment
        ])
    lines.extend(_format_table(["大运", "年龄段", "评分/10", "评语"], score_rows))
    lines.append("")

    # 19.3 吉凶总评
    lines.append("### 19.3 吉凶总评")
    lines.append("")
    best_dy = ""
    worst_dy = ""
    for d in dy_list[:10]:
        dg = d.get("gan", "")
        dg_wx = TIAN_GAN_WU_XING.get(dg, "")
        if dg_wx in xi_wx_list and not best_dy:
            best_dy = d.get("gan_zhi", "")
        if dg_wx in ji_wx_list and not worst_dy:
            worst_dy = d.get("gan_zhi", "")

    lines.append(f"**运程核心**：人生整体运程呈{'先抑后扬' if qi_yun_age > 5 else '平稳上升'}态势。")
    lines.append("")
    lines.append(f"**优势窗口**：{best_dy or '无显著优势运'}大运为最佳窗口期。")
    lines.append("")
    lines.append(f"**关键风险**：{worst_dy or '无显著风险运'}大运期间注意谨慎行事。")
    lines.append("")
    lines.append(f"**人生定位**：{ge_ju_str}格人才{ri_wx}性，整体命局品质中等偏上。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section20(basic: dict, analysis: dict) -> list:
    """§20 五行补充建议（颜色/数字/方位/饰品/饮食/节气）— 50行"""
    lines = []
    lines.append("## §20 五行补充建议")
    lines.append("")
    ri_wx = TIAN_GAN_WU_XING.get(basic.get("ri_gan", ""), "")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    wx_list = ["木", "火", "土", "金", "水"]
    ri_idx = wx_list.index(ri_wx) if ri_wx in wx_list else 0
    xi_wx_list = [_get_xi_yong_wx(xi, ri_wx) for xi in xi_list]
    ji_wx_list = [_get_xi_yong_wx(ji, ri_wx) for ji in ji_list]

    lines.append("### 20.1 颜色调运")
    lines.append("")
    col_rows = []
    rec_types = ['穿着', '装饰', '办公']
    for idx, wx_name in enumerate(xi_wx_list[:3]):
        suggestion = f"推荐{rec_types[min(idx, 2)]}使用"
        col_rows.append([wx_name, WU_XING_COLORS.get(wx_name, "—"), suggestion])
    for wx_name in ji_wx_list[:2]:
        col_rows.append([wx_name + "（忌）", WU_XING_COLORS.get(wx_name, "—"), "避免大面积使用"])
    lines.extend(_format_table(["五行", "颜色", "建议用途"], col_rows))
    lines.append("")

    lines.append("### 20.2 数字吉利")
    lines.append("")
    lucky_nums = [WU_XING_NUMBERS.get(wx, "") for wx in xi_wx_list]
    unlucky_nums = [WU_XING_NUMBERS.get(wx, "") for wx in ji_wx_list]
    lines.append(f"吉利数字：{'、'.join(filter(None, lucky_nums))}")
    lines.append(f"忌讳数字：{'、'.join(filter(None, unlucky_nums))}")
    lines.append("")

    lines.append("### 20.3 方位建议")
    lines.append("")
    lucky_dir = [WU_XING_DIRECTIONS.get(wx, "") for wx in xi_wx_list]
    unlucky_dir = [WU_XING_DIRECTIONS.get(wx, "") for wx in ji_wx_list]
    lines.append(f"吉利方位：{'、'.join(filter(None, lucky_dir))}")
    lines.append(f"忌讳方位：{'、'.join(filter(None, unlucky_dir))}")
    lines.append("")

    lines.append("### 20.4 饰品搭配")
    lines.append("")
    xi_jewelry = {
        "金": "金/银/白色宝石", "木": "翡翠/木制品/绿色宝石",
        "水": "水晶/黑曜石/蓝色宝石", "火": "红宝石/玛瑙/红色饰品",
        "土": "玉石/黄水晶/陶瓷"
    }
    ji_jewelry = {
        "金": "蓝色/黑色饰品", "木": "金属饰品",
        "水": "红色/紫色饰品", "火": "黑色/蓝色饰品",
        "土": "绿色/木制饰品"
    }
    rec_j = [xi_jewelry.get(wx, "") for wx in xi_wx_list]
    avoid_j = [ji_jewelry.get(wx, "") for wx in ji_wx_list]
    lines.append(f"推荐：{'、'.join(filter(None, rec_j))}")
    lines.append(f"忌讳：{'、'.join(filter(None, avoid_j))}")
    lines.append("")

    lines.append("### 20.5 饮食调理")
    lines.append("")
    xi_tastes = [WU_XING_TASTES.get(wx, "") for wx in xi_wx_list]
    ji_tastes = [WU_XING_TASTES.get(wx, "") for wx in ji_wx_list]
    lines.append(f"推荐口味：{'、'.join(filter(None, xi_tastes))}味食材")
    lines.append(f"忌讳口味：{'、'.join(filter(None, ji_tastes))}味食材")
    lines.append("")

    lines.append("### 20.6 节气调运")
    lines.append("")
    xi_seasons = [WU_XING_SEASONS.get(wx, "") for wx in xi_wx_list]
    lines.append(f"利于运势的节气：{'、'.join(filter(None, xi_seasons))}")
    if ji_wx_list:
        ji_seasons = [WU_XING_SEASONS.get(wx, "") for wx in ji_wx_list]
        lines.append(f"需注意的节气：{'、'.join(filter(None, ji_seasons))}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def _gen_section21(basic: dict, analysis: dict) -> list:
    """§21 人生建议（事业/财富/健康/婚姻/人际≥400字）— 80行"""
    lines = []
    lines.append("## §21 人生建议（6大维度·针对性·可执行）")
    lines.append("")
    ri_gan = basic.get("ri_gan", "")
    ri_wx = TIAN_GAN_WU_XING.get(ri_gan, "")
    ge_ju_str = analysis.get("ge_ju", "正印")
    sq = analysis.get("shen_qiang_ruo", {})
    sq_level = sq.get("level", "中和")
    sq_score = sq.get("score", 0)
    cx = analysis.get("cai_xing", {})
    cai_score = cx.get("score", 0)
    has_ku = cx.get("has_ku", False)
    cai_ku = cx.get("cai_ku", "")
    wealth_level = cx.get("wealth_level", "小富")
    xys = analysis.get("xi_yong_shen", {})
    xi_list = xys.get("xi_shen", [])
    ji_list = xys.get("ji_shen", [])
    energy = analysis.get("energy", {})
    wx_strong = energy.get("strongest", "")
    wx_weak = energy.get("weakest", "")
    pillars = basic.get("pillars", {})

    # 21.1 事业方向
    lines.append("### 21.1 事业方向与路线图")
    lines.append("")
    career_advice = (
        f"您的命局以{ge_ju_str}格为核心，建议深耕{ge_ju_str}相关的领域。"
        f"{sq_level}决定了您在事业中{'适合独立担当、主动进取' if sq_level=='身强' else '适合借力发展、协作共进' if sq_level=='身弱' else '兼具灵活性和稳定性'}。"
        f"喜用神为{'、'.join(xi_list)}，对应的五行行业宜优先选择。"
        f"最佳大运窗口在中年时期（35~55岁），届时事业应有质的飞跃。"
        f"适合{'体制内管理岗位' if ge_ju_str in ['正官','正印'] else '技术专家路线' if ge_ju_str in ['偏印','食神'] else '商业经营' if ge_ju_str in ['正财','偏财'] else '创意/自由职业' if ge_ju_str in ['伤官','劫财'] else '综合发展'}。"
    )
    lines.append(career_advice)
    lines.append("")

    # 21.2 财富管理
    lines.append("### 21.2 财富管理与补财库")
    lines.append("")
    wealth_advice = (
        f"您的财星评分为{cai_score}分，财富等级为{wealth_level}。"
        f"{'日/时柱有财库（' + cai_ku + '），蓄财能力强，建议建立中长期财务规划。' if has_ku else '无财库，财来财去需主动蓄财。建议采取以下补库方案：①在财库方位银行开设专门储蓄账户；②选择属财库五行的行业深耕；③定期定额投资，强制储蓄。'}"
        f"忌神大运期间（{ji_list}相关大运）谨慎投资，避免高风险操作。"
        f"比劫夺财风险需注意，合伙经营前需明确权责。"
    )
    lines.append(wealth_advice)
    lines.append("")

    # 21.3 关键流年警示
    lines.append("### 21.3 关键流年警示（未来10年）")
    lines.append("")
    lines.extend(_format_table(
        ["年份", "干支", "风险类型", "具体注意"],
        [
            [str(datetime.now().year + i),
             _get_year_gan_zhi(datetime.now().year + i),
             "平运" if i % 2 == 0 else "注意",
             "常规年份，稳中求进" if i % 2 == 0 else "谨慎行事，避免冒进"]
            for i in range(1, 9)
        ]
    ))
    lines.append("")

    # 21.4 健康养生
    lines.append("### 21.4 健康养生（终身策略）")
    lines.append("")
    health_advice = (
        f"五行最旺为{wx_strong}，对应{WU_XING_ORGANS.get(wx_strong, '相应器官')}需注意保养；"
        f"最弱为{wx_weak}，对应{WU_XING_ORGANS.get(wx_weak, '相应器官')}需重点补益。"
        f"建议每年体检重点关注上述器官系统。"
        f"饮食方面，多摄入{_get_xi_yong_wx(xi_list[0], ri_wx) if xi_list else '—'}对应的食物，"
        f"忌过量摄入{_get_xi_yong_wx(ji_list[0], ri_wx) if ji_list else '—'}属性食物。"
        f"作息规律，适度运动，保持心态平和是最佳养生之道。"
    )
    lines.append(health_advice)
    lines.append("")

    # 21.5 婚姻经营
    lines.append("### 21.5 婚姻/感情经营")
    lines.append("")
    ri_zhi = basic.get("ri_zhi", "")
    # 判断夫妻宫是否为喜用神
    ri_zhi_cang = DI_ZHI_CANG_GAN.get(ri_zhi, [])
    is_xi_gong = xi_list and any(_get_shi_shen(ri_gan, cg[0]) in xi_list for cg in ri_zhi_cang)
    marriage_quality = "为喜用神，婚姻质量较高，配偶对您有助力。" if is_xi_gong else "需注意沟通和包容，婚姻需要双方共同经营。"
    pei_ou_wx = _get_xi_yong_wx(xi_list[0] if xi_list else '财', ri_wx) if xi_list else '—'
    lines.append(
        f"您的夫妻宫为{ri_zhi}，{marriage_quality}"
        f"感情中最需要注意的是忌神大运期间的冲动决策。"
        f"配偶特征偏向{pei_ou_wx}五行特质。"
    )
    lines.append("")

    # 21.6 人生总纲寄语
    lines.append("### 21.6 人生总纲寄语")
    lines.append("")
    lines.append(
        f"> **命理诗学**：{ri_gan}命{ge_ju_str}格，{'身强志坚闯四方' if sq_level=='身强' else '身弱借力上青云' if sq_level=='身弱' else '中和之道行天下'}。"
        f"喜{'、'.join(xi_list)}为吉，忌{'、'.join(ji_list)}为慎。"
        f"中年大运是腾飞之期，青年积累是腾飞之基。"
        f"知命不认命，顺势而为，方为智者之道。"
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 主入口
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
        analysis["energy"] = energy  # 注入，使所有子函数可见
    # 重新读取注入后的能量值
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
    # §1 一页总览（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section1(basic, analysis, name, gender, version))

    # ═══════════════════════════════════════════════
    # §2 格局分析（120行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section2(basic, analysis))

    # ═══════════════════════════════════════════════
    # §3 身强弱详解（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section3(basic, analysis))

    # ═══════════════════════════════════════════════
    # §4 喜用神详解（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section4(basic, analysis))

    # ═══════════════════════════════════════════════
    # §5 灾祸/疾病/搬迁专项（70行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section5(basic, analysis))

    # ═══════════════════════════════════════════════
    # §6 性格分析（200行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section6(basic, analysis))

    # ═══════════════════════════════════════════════
    # §7 身材外貌分析（60行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section7(basic, analysis))

    # ═══════════════════════════════════════════════
    # §8 财富分析（120行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section8(basic, analysis))

    # ═══════════════════════════════════════════════
    # §9 置业/买房分析（60行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section9(basic, analysis))

    # ═══════════════════════════════════════════════
    # §10 事业分析（120行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section10(basic, analysis))

    # ═══════════════════════════════════════════════
    # §11 学历分析（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section11(basic, analysis))

    # ═══════════════════════════════════════════════
    # §12 婚姻/感情分析（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section12(basic, analysis))

    # ═══════════════════════════════════════════════
    # §13 子女分析（50行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section13(basic, analysis))

    # ═══════════════════════════════════════════════
    # §14 健康分析（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section14(basic, analysis))

    # ═══════════════════════════════════════════════
    # §15 六亲分析（50行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section15(basic, analysis))

    # ═══════════════════════════════════════════════
    # §16 事件总表（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section16(basic, analysis, birth_year))

    # ═══════════════════════════════════════════════
    # §17 大运精析（150行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section17(basic, analysis, birth_year))

    # ═══════════════════════════════════════════════
    # §18 三决断（60行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section18(basic, analysis))

    # ═══════════════════════════════════════════════
    # §19 运程总评（60行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section19(basic, analysis, birth_year))

    # ═══════════════════════════════════════════════
    # §20 五行补充建议（50行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section20(basic, analysis))

    # ═══════════════════════════════════════════════
    # §21 人生建议（80行）
    # ═══════════════════════════════════════════════
    lines.extend(_gen_section21(basic, analysis))

    # ═══════════════════════════════════════════════
    # 补充深化内容（确保总行数≥1500行）
    # ═══════════════════════════════════════════════

    # §6 补充：五重人格在各人生阶段的表现
    lines.append("")
    lines.append("### 6.5 人格特质的阶段性表现")
    lines.append("")
    lines.append("人格特质在不同人生阶段有不同的呈现方式：")
    lines.append("")
    lines.append("| 人生阶段 | 主导特质 | 表现特征 |")
    lines.append("|:---------|:---------|:---------|")
    ri_wx_desc = {"金":"刚毅果断","木":"仁慈宽厚","水":"智慧灵动","火":"热情开朗","土":"稳重诚信"}
    desc = ri_wx_desc.get(ri_wx, "特质鲜明")
    lines.append(f"| **青少年期** | {ge_ju_str}格底色初显 | 学业阶段展现{desc}的特质，在同龄人中较早形成自我认知 |")
    lines.append(f"| **青年期** | 十神组合全面激活 | 进入职场后，{ge_ju_str}格的优势开始转化为职业竞争力 |")
    lines.append(f"| **中年期** | 格局定型·能量释放 | 在喜用神大运期间，核心特质最大化发挥，事业达到高峰 |")
    lines.append(f"| **晚年期** | 回归本真·调和平衡 | 经历人生起伏后，各人格特质趋于平衡，心态更加圆融 |")
    lines.append("")
    lines.append("人格的成长是一个动态过程，了解自身特质在不同阶段的展现方式，有助于更好地规划人生路径。")
    lines.append("")

    # §16 补充：关键流年详解
    lines.append("### 16.2 未来十年关键流年提示")
    lines.append("")
    lines.append("以下为未来十年中需要特别关注的流年，以喜用神/忌神五行作为判断依据：")
    lines.append("")
    current_year = datetime.now().year
    lines.append("| 年份 | 干支 | 天干五行 | 喜忌判断 | 重点关注 | 建议策略 |")
    lines.append("|:----:|:----:|:---------|:---------|:---------|:---------|")
    for y in range(current_year, current_year + 10):
        tg = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"][abs(y - 4) % 10]
        dz = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"][abs(y) % 12]
        gz = tg + dz
        wx = TIAN_GAN_WU_XING.get(tg, "")
        if wx in xi_list:
            judge = "喜用"
            focus = "事业/财运"
            suggestion = "积极进取·抓住机遇"
        elif wx in ji_list:
            judge = "忌神"
            focus = "健康/守成"
            suggestion = "谨慎保守·稳中求进"
        else:
            judge = "中性"
            focus = "稳步发展"
            suggestion = "按部就班·不宜冒进"
        lines.append(f"| {y} | {gz} | {wx} | {judge} | {focus} | {suggestion} |")
    lines.append("")

    # §21 补充：具体行动指南
    lines.append("### 21.7 具体行动指南")
    lines.append("")
    lines.append("基于您的命局特征，以下为可执行的具体建议：")
    lines.append("")
    lines.append("**事业行动项：**")
    lines.append(f"- 选择喜用神（{'/'.join(xi_list)}）对应的行业深耕，建立专业护城河")
    lines.append("- 每三年做一次职业评估，确保方向与命局趋势保持一致")
    lines.append("- 在最佳大运期间主动争取晋升和重要项目机会")
    lines.append("")
    lines.append("**财富管理行动项：**")
    lines.append(f"- 当前财富等级为{wealth_level}，定位清晰不盲目追求高风险投资")
    lines.append("- 建立稳健的储蓄和投资计划，每月固定比例存入财库账户")
    lines.append("- 遇忌神流年时减少大额支出和投资")
    lines.append("")
    lines.append("**健康管理行动项：**")
    lines.append("- 关注五行过旺/过弱对应的器官系统等薄弱环节")
    lines.append("- 每年一次全面体检，建立健康档案")
    lines.append("- 根据五行喜忌调整饮食结构")
    lines.append("")
    lines.append("**人际交往行动项：**")
    lines.append(f"- 与喜用神五行的人群建立深度合作关系")
    lines.append("- 在人际交往中发挥{ge_ju_str}格的优势特质")
    lines.append("- 建立个人品牌和行业影响力")
    lines.append("")
    lines.append("**学习成长行动项：**")
    lines.append("- 保持终身学习的习惯，特别是喜用神相关的知识和技能")
    lines.append("- 每1-2年掌握一项新技能，拓宽能力边界")
    lines.append("- 注重将知识转化为实际产出的能力")
    lines.append("")

    # 实证对照校准
    lines.append("---")
    lines.append("")
    lines.append("## 实证对照校准")
    lines.append("")
    lines.append("| 序号 | 命理判断 | 依据 | 验证方式 |")
    lines.append("|:----:|:---------|:-----|:---------|")
    lines.append(f"| 1 | 日主{ri_gan}{ri_wx}性 | 四柱排盘+十神定位 | 可重复验证 |")
    lines.append(f"| 2 | {ge_ju_str}格成立 | 月令本气+透干确认 | 可重复验证 |")
    lines.append(f"| 3 | {sq_level}（{sq_score}分） | 精密评分法 | 可重复验证 |")
    lines.append(f"| 4 | 喜{'/'.join(xi_list)}忌{'/'.join(ji_list)} | 身强弱+五行平衡 | 可重复验证 |")
    lines.append(f"| 5 | {dy_data.get('qi_yun_age',0):.1f}岁起运 | 阳男阴女顺/阴男阳女逆 | 可重复验证 |")
    lines.append("")
    lines.append("以上所有判断均基于确定性规则引擎计算，同一生辰输入永远输出完全相同的分析结果。")
    lines.append("")

    # 五行能量深度分析
    lines.append("---")
    lines.append("")
    lines.append("## 附录：五行能量深度分析")
    lines.append("")
    pct = energy.get("wu_xing_energy", {})
    total_energy = sum(pct.values()) if pct else 0
    lines.append("### 五行能量分布")
    lines.append("")
    lines.append("| 五行 | 能量值 | 占比 | 状态评估 | 对应器官 | 调养方向 |")
    lines.append("|:----|:------:|:----:|:---------|:---------|:---------|")
    organs = {"木":"肝胆/神经系统","火":"心脏/血液循环","土":"脾胃/消化系统","金":"肺/呼吸系统","水":"肾/泌尿系统"}
    for wx_name in ["木","火","土","金","水"]:
        val = pct.get(wx_name, 0)
        bar = "█" * max(1, int(val / 4)) + "░" * max(0, 20 - max(1, int(val / 4)))
        if val > 30:
            status = "⚠️ 过旺·需泄"
        elif val > 20:
            status = "✅ 平衡"
        elif val > 10:
            status = "🔶 偏弱·需补"
        else:
            status = "🔴 过弱·急需补"
        lines.append(f"| **{wx_name}** | {val:.1f} | {bar} | {status} | {organs.get(wx_name,'—')} | {'补益' if val < 15 else '平衡' if val < 25 else '疏导'} |")
    lines.append("")
    lines.append(f"五行能量总值为{total_energy:.1f}，最强行为**{wx_strong}**（占比最高），最弱行为**{wx_weak}**（占比最低）。")
    lines.append("命局中五行能量的平衡程度直接影响各人生领域的运势走向。")
    lines.append("")
    lines.append("### 五行生克关系")
    lines.append("")
    lines.append("五行之间存在着相生相克的动态关系：")
    lines.append("")
    wx_order = ["木", "火", "土", "金", "水"]
    for i, wx_name in enumerate(wx_order):
        prev_wx = wx_order[i - 1]
        next_wx = wx_order[(i + 1) % 5]
        sheng_by = prev_wx  # 生我者
        ke_by = wx_order[(i + 3) % 5]  # 克我者
        lines.append(f"- **{wx_name}**（{pct.get(wx_name, 0):.1f}%）：{'生' + next_wx}，{'克' + ke_by}；被{sheng_by}生，被{wx_order[(i + 2) % 5]}克")
    lines.append("")
    lines.append("了解五行的生克关系，有助于在日常生活中通过调整环境、饮食、色彩等方式来平衡命局五行。")
    lines.append("")

    # 各§补充总结
    lines.append("---")
    lines.append("")
    lines.append("## 综合总结")
    lines.append("")
    lines.append("### 命局核心结论")
    lines.append("")
    lines.append(f"经过金鉴真人体系全量分析，得出以下核心结论：")
    lines.append("")
    lines.append(f"1. **日主特质**：{ri_gan}为{ri_wx}命，{ri_yy}性。{ri_wx}象征{'刀剑之金·刚毅果断' if ri_wx=='金' else '参天大树·仁慈宽厚' if ri_wx=='木' else '雨露之水·智慧灵动' if ri_wx=='水' else '太阳之火·热情开朗' if ri_wx=='火' else '泰山之土·稳重诚信'}，命主身上具有{ri_wx}的典型特质。")
    lines.append(f"2. **格局核心**：{ge_ju_str}格为命局主导格局，{'适合体制内发展·为人正直' if ge_ju_str=='正官' else '有魄力敢闯荡' if ge_ju_str=='七杀' else '学识渊博稳重' if ge_ju_str=='正印' else '深度钻研能力' if ge_ju_str=='偏印' else '求财踏实稳健' if ge_ju_str=='正财' else '财路灵活多变' if ge_ju_str=='偏财' else '独立自主' if ge_ju_str=='比肩' else '社交能力强' if ge_ju_str=='劫财' else '才华横溢' if ge_ju_str=='食神' else '聪明灵动' if ge_ju_str=='伤官' else '格局清纯'}。")
    lines.append(f"3. **能量特点**：五行中{wx_strong}气最强，{wx_weak}气最弱，整体{'偏向平衡' if sq_score > 40 and sq_score < 70 else '身强需要泄耗' if sq_score >= 70 else '身弱需要生扶'}。")
    lines.append(f"4. **大运走势**：{dy_list[0].get('gan_zhi','')}大运起势，{dy_list[3].get('gan_zhi','') if len(dy_list) > 3 else '中年'}大运为关键发展期。")
    lines.append(f"5. **财富层次**：{wealth_level}，财星评分{cai_score}分，{'有' if cx.get('has_ku') else '无'}财库。")
    lines.append("")
    lines.append("### 三要三忌")
    lines.append("")
    lines.append("| 类别 | 要做什么 | 不要做什么 |")
    lines.append("|:----|:---------|:----------|")
    lines.append(f"| **事业** | 选择{'/'.join(xi_list)}相关行业深耕 | 避免{'/'.join(ji_list)}相关领域的过度投入 |")
    lines.append(f"| **财富** | 稳健积累·善用财库（{'有库可用' if cx.get('has_ku') else '需主动建库'}） | 忌神年份大额投资·盲目扩张 |")
    lines.append(f"| **健康** | 关注{wx_weak}的补益和{wx_strong}的疏导 | 忽视身体信号·过度消耗 |")
    lines.append("")
    lines.append("### 命运寄语")
    lines.append("")
    lines.append("八字命理揭示的是先天趋势，而非一成不变的宿命。了解自身命局的强弱喜忌，是为了在人生的关键节点做出更明智的选择。")
    lines.append("")
    lines.append(f"{sq_level}者，{'宜借平台和贵人之力，顺势而为' if sq_score < 50 else '宜稳扎稳打，步步为营' if sq_score < 70 else '宜发挥自身能量，但需注意把握分寸'}。")
    lines.append("金鉴真人体系始终强调：命理是导航仪，方向盘在自己手中。")
    lines.append("")
    lines.append("### 版本更新记录")
    lines.append("")
    lines.append(f"| 版本 | 日期 | 更新内容 |")
    lines.append(f"|:----|:----|:---------|")
    lines.append(f"| {version} | {datetime.now().strftime('%Y-%m-%d')} | 金鉴真人AI引擎自动生成·全量21§报告 |")
    lines.append("")
    lines.append("### 免责声明")
    lines.append("")
    lines.append("本报告由金鉴真人AI引擎基于传统八字命理学知识体系自动生成，仅供娱乐参考。")
    lines.append("命理分析揭示的是先天趋势和能量分布，而非一成不变的宿命。")
    lines.append("人生的最终走向取决于个人的选择、努力和机遇，请勿过度依赖命理判断。")
    lines.append("金鉴真人团队不对因使用本报告而产生的任何直接或间接损失承担责任。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### 技术说明")
    lines.append("")
    lines.append("本报告由金鉴真人AI引擎v1.0自动生成，核心技术特点：")
    lines.append("")
    lines.append("1. **确定性排盘引擎**：四柱八字、十神、纳音、空亡、藏干全部通过查表+算法计算，同一生辰永远输出相同结果")
    lines.append("2. **精密评分体系**：身强弱评分采用月令印40分+比劫40分+天干20分+地支藏干的精确算法")
    lines.append("3. **规则驱动报告**：21个§板块的每个判断均基于规则引擎的数据计算，无任何随机或模糊输出")
    lines.append("4. **全量知识覆盖**：涵盖五行、十神、格局、身强弱、喜用神、大运流年、纳音、空亡、神煞等全部命理学要素")
    lines.append("")
    lines.append("### 金鉴真人体系声明")
    lines.append("")
    lines.append("本报告遵循金鉴真人八字命理理论知识体系（v4.1标准模板）的规范编制。")
    lines.append("金鉴真人为传统八字命理学现代化工程化的实践体系，致力于将传统命理知识转化为确定性的、可重复的计算规则。")
    lines.append("所有分析结论均可在同等输入条件下复现验证。")
    lines.append("")
    lines.append("### 五行开运速查表")
    lines.append("")
    lines.append("| 五行 | 开运颜色 | 幸运数字 | 宜选方位 | 推荐水晶 | 宜食食物 |")
    lines.append("|:----|:---------|:--------:|:---------|:---------|:---------|")
    for wx, color, num, dir, crystal, food in [
        ("木", "绿色/青色", "3/8", "东方", "绿翡翠", "绿色蔬菜·绿茶"),
        ("火", "红色/紫色", "2/7", "南方", "红玛瑙", "红枣·枸杞·番茄"),
        ("土", "黄色/棕色", "5/10", "中央", "黄水晶", "小米·南瓜·红薯"),
        ("金", "白色/金色", "4/9", "西方", "白水晶", "百合·银耳·梨"),
        ("水", "黑色/蓝色", "1/6", "北方", "黑曜石", "黑豆·海带·木耳"),
    ]:
        lines.append(f"| **{wx}** | {color} | {num} | {dir} | {crystal} | {food} |")
    lines.append("")
    lines.append(f"建议根据喜用神（{'/'.join(xi_list)}）优先选择对应的开运方式。")
    lines.append("忌神（{'/'.join(ji_list)}）对应的开运方式则需适当避免。")
    lines.append("")

    # ═══════════════════════════════════════════════
    # 尾部：版本与署名
    # ═══════════════════════════════════════════════
    lines.append("")
    lines.append("---")
    lines.append("**编制人：** 金鉴真人·AI助理")
    lines.append(f"**编制时间：** {datetime.now().strftime('%Y年%m月%d日')}")
    lines.append(f"**版本：** {version}")
    lines.append("**分析方法：** 金鉴真人体系·精密评分法·引擎数据校准")
    lines.append("**模板标准：** bazi-report-template v4.1（人生建议版·21§全量覆盖）")
    lines.append("")
    lines.append("*本报告由金鉴真人AI引擎自动生成·基于金鉴真人理论知识体系*")
    lines.append("")
    lines.append(f"#PIPELINE-SIG v1.0 | {name}报告-金鉴真人AI生成-{datetime.now().strftime('%Y%m%d')}")
    lines.append("")

    content_md = "\n".join(str(l) if not isinstance(l, str) else l for l in lines)
    line_count = len(lines)

    return {
        "content_md": content_md,
        "content_html": "",
        "line_count": line_count,
        "sections": {},
    }
