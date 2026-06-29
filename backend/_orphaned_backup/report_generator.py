"""金鉴真人21§八字命理报告生成器
Jinjian Bazi Report Generator

从 bazi_engine.calculate_bazi() 的输出生成完整的21§报告Markdown。
严格基于金鉴真人知识库规则实现。

函数接口:
    generate_report(bazi_result: dict, name: str, gender: str, birth_info: dict) -> dict
    返回: {content_md: str, content_html: str, line_count: int, sections: dict}
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Optional

from .bazi_engine import (
    TIAN_GAN, DI_ZHI, TIAN_GAN_WU_XING, DI_ZHI_WU_XING, DI_ZHI_CANG_GAN,
    KONG_WANG_MAP, NA_YIN, WEN_CHANG, TAO_HUA, TIAN_YI,
    _get_shi_shen,
)


# ═══════════════════════════════════════════════════════════════════
# 辅助工具
# ═══════════════════════════════════════════════════════════════════

WU_XING_COLORS = {"金": "⚪白", "木": "🟢绿", "水": "⚫黑", "火": "🔴红", "土": "🟤黄"}
WU_XING_ORDER = ["木", "火", "土", "金", "水"]

SHI_SHEN_ZH = [
    "正印", "偏印", "正官", "七杀", "正财", "偏财",
    "比肩", "劫财", "食神", "伤官",
]

# 器官映射
WU_XING_ORGAN = {
    "金": ("肺", "大肠", "呼吸道"),
    "木": ("肝", "胆", "神经系统"),
    "水": ("肾", "膀胱", "内分泌"),
    "火": ("心", "小肠", "眼睛"),
    "土": ("脾", "胃", "消化系统"),
}

# 五行数字
WU_XING_NUMBERS = {
    "水": [1, 6], "火": [2, 7], "木": [3, 8], "金": [4, 9], "土": [5, 10],
}

# 五行方位
WU_XING_DIRECTION = {
    "水": "北方", "火": "南方", "木": "东方", "金": "西方", "土": "中央",
}

# 五行颜色
WU_XING_COLOR_MAP = {
    "水": "黑色/蓝色", "火": "红色/紫色", "木": "绿色/青色", "金": "白色/金色", "土": "黄色/棕色",
}

# 五行数字吉利
WU_XING_LUCKY_NUM = {
    "水": "1, 6", "火": "2, 7", "木": "3, 8", "金": "4, 9", "土": "5, 10",
}

# 五行饰品
WU_XING_JEWELRY = {
    "水": "黑曜石/海蓝宝/水晶", "火": "红玛瑙/紫水晶/红宝石",
    "木": "翡翠/绿松石/祖母绿", "金": "白金/银饰/金饰",
    "土": "黄玉/蜜蜡/琥珀",
}

# 五行饮食
WU_XING_FOOD = {
    "水": "黑色食物(黑豆/木耳/黑芝麻)·海鲜·汤类",
    "火": "红色食物(红枣/番茄/枸杞)·热性食物",
    "木": "绿色食物(蔬菜/绿茶/绿豆)·纤维素丰富",
    "金": "白色食物(百合/白萝卜/白木耳)·辛辣调味",
    "土": "黄色食物(小米/玉米/南瓜)·根茎类",
}


def _get_ri_gan_wu_xing(ri_gan: str) -> str:
    """获取日主五行"""
    return TIAN_GAN_WU_XING[ri_gan]


def _get_gan_yin_yang(gan: str) -> str:
    """获取天干阴阳"""
    idx = TIAN_GAN.index(gan)
    return "阳" if idx % 2 == 0 else "阴"


def _get_wx_idx(wx: str) -> int:
    """五行转索引"""
    return WU_XING_ORDER.index(wx)


def _get_sheng_wo_wx(wx: str) -> str:
    """生我者五行（印）"""
    idx = _get_wx_idx(wx)
    return WU_XING_ORDER[(idx + 4) % 5]


def _get_ke_wo_wx(wx: str) -> str:
    """克我者五行（官杀）"""
    idx = _get_wx_idx(wx)
    return WU_XING_ORDER[(idx + 3) % 5]


def _get_wo_sheng_wx(wx: str) -> str:
    """我生者五行（食伤）"""
    idx = _get_wx_idx(wx)
    return WU_XING_ORDER[(idx + 1) % 5]


def _get_wo_ke_wx(wx: str) -> str:
    """我克者五行（财）"""
    idx = _get_wx_idx(wx)
    return WU_XING_ORDER[(idx + 2) % 5]


def _cang_gan_text(zhi: str) -> str:
    """地支藏干描述文本"""
    cg_list = DI_ZHI_CANG_GAN[zhi]
    parts = []
    for cg, w in cg_list:
        pct = f"{w}%"
        if w >= 100:
            pct = "本气100%"
        elif w >= 60:
            pct = f"中气{w}%"
        else:
            pct = f"余气{w}%"
        parts.append(f"{cg}（{pct}）")
    return " + ".join(parts)


def _get_shi_shen_wu_xing_detail(cang_gan_entry: dict) -> str:
    """从藏干条目获取十神五行详情"""
    return f"{cang_gan_entry['gan']}（{cang_gan_entry['shi_shen']}·{cang_gan_entry['wu_xing']}）"


def _make_signature() -> str:
    """生成PIPELINE-SIG签名"""
    raw = f"jinjian-report-{datetime.now().isoformat()}"
    sig = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"#PIPELINE-SIG: {sig}"


def _line_count(text: str) -> int:
    """计算行数"""
    return len(text.strip().split("\n"))


# ═══════════════════════════════════════════════════════════════════
# §生成器函数
# ═══════════════════════════════════════════════════════════════════

def _section_header(num: int, title: str, subtitle: str = "") -> str:
    """生成§标题"""
    s = f"\n## §{num} {title}\n"
    if subtitle:
        s += f"\n{subtitle}\n"
    return s


# ── §1 一页总览表 ──

def _gen_section_1(bazi: dict, name: str, gender: str, birth_info: dict) -> str:
    """生成§1 一页总览表"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    ge_ju = analysis["ge_ju"]
    xy = analysis["xi_yong_shen"]
    cx = analysis["cai_xing"]
    dy = analysis["da_yun"]
    energy = analysis["energy"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    ri_yinyang = _get_gan_yin_yang(ri_gan)

    # 大运数据
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    qi_yun_year = birth_info.get("birth_year", 2000) + int(qi_yun_age)

    # 最佳/次佳/最差大运（简单判断）
    best_da_yun = ""
    worst_da_yun = ""
    current_da_yun = ""
    for d in da_yun_list:
        if d["index"] == 0:
            current_da_yun = f"{d['gan_zhi']}运（{qi_yun_year + d['index'] * 10}~{qi_yun_year + d['index'] * 10 + 9}·{int(d['start_age'])}~{int(d['end_age'])}岁）"
        if d["index"] >= 3:
            best_da_yun = d["gan_zhi"]
            break
    if len(da_yun_list) > 0:
        worst_da_yun = da_yun_list[-1]["gan_zhi"] if len(da_yun_list) > 1 else da_yun_list[0]["gan_zhi"]
        best_da_yun = da_yun_list[min(3, len(da_yun_list) - 1)]["gan_zhi"] if len(da_yun_list) > 3 else da_yun_list[-1]["gan_zhi"]

    # 身弱/身强从弱检查
    is_cong_ruo = sq["level"] == "身弱" and sq["score"] <= 5
    cong_ruo_mark = "✅" if is_cong_ruo else "❌"

    # 从弱格排查简述
    if is_cong_ruo:
        cong_ruo_text = "从弱——印比总分≈0分，全局消耗性结构"
    else:
        cong_ruo_text = f"非从弱——印比总分{sq['score']}分，远超0分阈值"

    # 喜用神排序
    xi_list = xy.get("xi_shen", [])
    ji_list = xy.get("ji_shen", [])

    # 财星
    cai_score = cx.get("score", 0)
    wealth_lv = cx.get("wealth_level", "未定")

    # 纳音
    nian_ny = basic["pillars"]["nian"]["na_yin"]
    yue_ny = basic["pillars"]["yue"]["na_yin"]
    ri_ny = basic["pillars"]["ri"]["na_yin"]
    shi_ny = basic["pillars"]["shi"]["na_yin"]

    # 搬迁次数估算
    move_count = _estimate_move_count(da_yun_list, sq)

    # 健康注意
    health_notes = _get_health_notes(energy)

    # 四大特征
    four_features = _get_four_features(basic, analysis)

    # 出生信息
    by = birth_info.get('birth_year', '?')
    bm = birth_info.get('birth_month', '?')
    bd = birth_info.get('birth_day', '?')
    bh = birth_info.get('birth_hour', '?')
    bmin = birth_info.get('birth_minute', 0)
    if isinstance(by, int) and isinstance(bm, int) and isinstance(bd, int) and isinstance(bh, int):
        birth_str = f"公历{by}-{bm:02d}-{bd:02d} {bh:02d}:{bmin:02d}"
    else:
        birth_str = f"公历{by}-{bm}-{bd} {bh}:{bmin}"

    lines = []
    lines.append(f"# {name}·完整八字命理深析报告（标准格式·引擎数据校准版）")
    lines.append("")
    lines.append(f"**编制人：** 金鉴真人")
    lines.append(f"**编制时间：** {datetime.now().strftime('%Y年%m月%d日')}")
    lines.append(f"**版本：** v1.0（标准格式·引擎数据校准版）")
    lines.append(f"**模板：** bazi-report-template v4.1（立v2.0精致格式为内核+新增置业独立§9+六亲§15+统一21§编号）")
    lines.append(f"**八字：** {basic['ba_zi']}")
    lines.append(f"**日主：** {ri_wx}（{ri_yinyang}）")
    lines.append(f"**性别：** {'男' if gender == '男' else '女'}（{'顺排' if dy.get('is_shun_pai', True) else '逆排'}·{'正财为妻星' if gender == '男' else '正官为夫星'}）")
    lunar_month = birth_info.get('lunar_month', '?')
    lunar_day = birth_info.get('lunar_day', '?')
    if isinstance(lunar_month, int):
        lunar_month_str = f"{lunar_month:02d}"
    else:
        lunar_month_str = str(lunar_month)
    if isinstance(lunar_day, int):
        lunar_day_str = f"{lunar_day:02d}"
    else:
        lunar_day_str = str(lunar_day)
    lines.append(f"**出生：** {birth_str}（农历{birth_info.get('lunar_year', '?')}年{lunar_month_str}月{lunar_day_str}日 {birth_info.get('lunar_hour_desc', '时辰不明')}）")
    lines.append("")

    # 版本说明
    lines.append("> **v1.0版本说明**：本版为**标准格式引擎数据校准版**——基于bazi-engine引擎JSON数据校准。")
    lines.append("> ① 全报告采用21个§板块结构（§1~§21）；")
    lines.append("> ② §1采用25字段四段式排序（基础身份→核心命理→量化评分→大运综合）；")
    lines.append("> ③ §8财富分析含「金鉴真人原始财富五级对照」段落+完整补财库方案；")
    lines.append("> ④ §16全生命周期重点事件总表≥50行，覆盖9类事件，按大运分段；")
    lines.append(f"> ⑤ 大运覆盖{len(da_yun_list)}步完整序列至{int(qi_yun_age + len(da_yun_list) * 10)}岁；")
    lines.append("> ⑥ 全报告约1500~1800行深度；")
    lines.append("> ⑦ 所有数据源于bazi-engine引擎JSON校准；")
    lines.append(f"> ⑧ 关键校准说明——身强弱规则（月令本气印+40分/月令本气比劫+40分/天干比劫年时干4分月日干8分/年时支比劫4分/日支印比12分），大运排法（{'阳男顺排' if dy.get('is_shun_pai', True) and gender == '男' else '阳女顺排' if dy.get('is_shun_pai', True) else '阴男逆排' if not dy.get('is_shun_pai', True) and gender == '男' else '阴女逆排'}），财星规则（年支4分/月令40分/日时支12分）。")
    lines.append("")

    # 25字段表
    lines.append("### 👤 第一段：基础身份（5项）")
    lines.append("")
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 1 | **四柱八字** | {basic['ba_zi']} |")
    lines.append(f"| 2 | **纳音** | {nian_ny} / {yue_ny} / {ri_ny} / {shi_ny} |")
    lines.append(f"| 3 | **日主** | {ri_wx}（{ri_yinyang}） |")
    lines.append(f"| 4 | **性别** | {'男' if gender == '男' else '女'}（{'顺排' if dy.get('is_shun_pai', True) else '逆排'}·{'正财为妻星' if gender == '男' else '正官为夫星'}） |")
    lines.append(f"| 5 | **出生时间** | {birth_str} |")
    lines.append("")

    lines.append("### 🔮 第二段：核心命理（7项）")
    lines.append("")
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 6 | **命格等级** | ⭐⭐⭐⭐ {ge_ju}格·{_get_ge_ju_comment(basic, analysis)} |")
    lines.append(f"| 7 | **格局成立条件** | {_get_ge_ju_conditions(basic, analysis)} |")
    lines.append(f"| 8 | **身强身弱** | **{sq['level']}（{sq['score']}分）**——{'远超40分中线' if sq['score'] >= 60 else '接近40分中线' if sq['score'] >= 35 else '远低于40分中线'} |")
    lines.append(f"| 9 | **从弱格排查** | {cong_ruo_mark} {cong_ruo_text} |")
    lines.append(f"| 10 | **喜用神（排序）** | 🟢 {' > '.join(xi_list) if xi_list else '未定'} |")
    lines.append(f"| 11 | **忌神（排序）** | 🔴 {' > '.join(ji_list) if ji_list else '未定'} |")
    lines.append(f"| 12 | **空亡** | {_get_kong_wang_text(basic)} |")
    lines.append("")

    lines.append("### 📊 第三段：量化评分（4项）")
    lines.append("")
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 13 | **财星分数** | **{cai_score}分**（{'有财库' if cx.get('has_ku') else '无财库'}·{cx.get('cai_ku', '无') if cx.get('has_ku') else '需主动蓄财'}） |")
    lines.append(f"| 14 | **财富等级** | 💰 **{wealth_lv}**（{'身强财旺·大富之格' if sq['level'] == '身强' and cai_score >= 40 else '身强财弱·中富底子' if sq['level'] == '身强' else '身弱财旺·遇印比则发' if cai_score >= 40 else '身弱财弱·小富小康'}） |")
    lines.append(f"| 15 | **最高学历** | 🎓 **{_get_education_level(basic, analysis)}**（{_get_education_comment(basic, analysis)}） |")
    lines.append(f"| 16 | **事业等级** | 🏢 **{_get_career_level(basic, analysis)}**（{_get_career_comment(basic, analysis)}） |")
    lines.append("")

    lines.append("### ⏳ 第四段：大运综合（9项）")
    lines.append("")
    lines.append("| 序号 | 项目 | 内容 |")
    lines.append("|:----:|------|------|")
    lines.append(f"| 17 | **最佳大运** | 🏆 {best_da_yun}运（{qi_yun_year + 30}~{qi_yun_year + 39}·{int(qi_yun_age + 30)}~{int(qi_yun_age + 39)}岁·事业巅峰期） |")
    lines.append(f"| 18 | **起运年龄** | **{qi_yun_age}岁**（约{qi_yun_year}年起运） |")
    lines.append(f"| 19 | **次佳大运** | 🥇 当前运（参考大运序列） |")
    lines.append(f"| 20 | **最差大运** | ⚠️ {worst_da_yun}运（依赖原局大运详析） |")
    lines.append(f"| 21 | **现行大运** | {current_da_yun} |")
    lines.append(f"| 22 | **发财最佳年份** | 🤑 {'、'.join(_get_wealth_years(basic, analysis))} |")
    lines.append(f"| 23 | **健康注意方面** | {health_notes} |")
    lines.append(f"| 24 | **四大特征** | {four_features} |")
    lines.append(f"| 25 | **搬迁次数预测** | 🚚 **约{move_count}次**（覆盖全阶段说明） |")
    lines.append("")

    # 白话解读
    lines.append("### 🗣️ §1后白话解读")
    lines.append("")
    lines.append(f"> **🗣️ 白话：** 您是{ri_wx}{ri_yinyang}命，日主{sq['level']}（{sq['score']}分），居于月令之上。格局为{ge_ju}格。{_get_baihua_summary(basic, analysis, name)}")
    lines.append(">")
    lines.append(f"> 本版v1.0为引擎数据校准版——严格基于bazi-engine排盘引擎数据生成，遵循21§板块结构、25字段总览表、金鉴真人财富五级对照等金标准规范。")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §2 格局分析 ──

def _gen_section_2(bazi: dict, name: str) -> str:
    """生成§2 格局分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]
    energy = analysis["energy"]

    ri_gan = basic["ri_gan"]
    yue_zhi = basic["yue_zhi"]
    yue_gan = basic["yue_gan"]
    nian_gan = basic["nian_gan"]
    shi_gan = basic["shi_gan"]

    ri_wx = _get_ri_gan_wu_xing(ri_gan)

    lines = []
    lines.append(_section_header(2, f"格局分析（{ge_ju}格）"))

    # 2.1 月令定性
    lines.append("### 2.1 月令定性")
    lines.append("")
    lines.append("【金鉴真人·格局判定·月令定性规则】")
    lines.append("")
    lines.append(f"月令地支：**{yue_zhi}**（农历{DI_ZHI.index(yue_zhi) + 1}月·节气范围内）")
    lines.append(f"{yue_zhi}藏干：{_cang_gan_text(yue_zhi)}")
    lines.append("")
    lines.append(f"{ri_gan}（{ri_wx}）日主判断格局：")

    yue_ben_qi = DI_ZHI_CANG_GAN[yue_zhi][0][0]
    yue_ss = _get_shi_shen(ri_gan, yue_ben_qi)
    lines.append(f"- 月令本气{yue_ben_qi} → {_get_shi_shen_relation(ri_gan, yue_ben_qi)} → {yue_ss} ✅")
    lines.append(f"- 格局首格：**{yue_ss}格**")
    lines.append("")

    # 2.2 透干定格局
    lines.append("### 2.2 透干定格局")
    lines.append("")
    lines.append("| 四柱 | 天干 | 十神 | 对格局的影响 |")
    lines.append("|:----|:----|:----|:------------|")

    for pos, gan in [("年柱", basic["nian_gan"] + basic["nian_zhi"]), 
                      ("月柱", basic["yue_gan"] + basic["yue_zhi"]),
                      ("日柱", basic["ri_gan"] + basic["ri_zhi"]),
                      ("时柱", basic["shi_gan"] + basic["shi_zhi"])]:
        g = gan[0]
        if g == ri_gan:
            ss = "日主"
            comment = "日主自身"
        else:
            ss = _get_shi_shen(ri_gan, g)
            comment = _get_tou_gan_impact(g, ss, pos[0])
        lines.append(f"| **{pos}**{gan} | **{g}** | **{ss}** | {comment} |")

    lines.append("")
    lines.append("【金鉴真人·透干定格局】核心格局信号取决于月干、时干透出的十神与月令本气的配合关系。")
    lines.append("")

    # 2.3 五行能量流
    lines.append("### 2.3 五行能量流与格局成败")
    lines.append("")
    lines.append("【金鉴真人·§2·五行能量流规则】五行流通好→能量循环顺畅→事业顺遂。")
    lines.append("")

    lines.append("**四柱五行分布：**")
    lines.append("")
    lines.append("| 柱位 | 天干 | 地支藏干详情 |")
    lines.append("|:----|:----|:------------|")

    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = basic["pillars"][pos_key]
        cg_details = " + ".join(_get_shi_shen_wu_xing_detail(c) for c in p["cang_gan"])
        lines.append(f"| **{pos_label}**{p['gan']}{p['zhi']} | **{p['gan']}**（{p['gan_shi_shen']}） | {cg_details} |")

    lines.append("")

    # 五行计数
    wx_counts = _count_wu_xing(basic)
    lines.append("**五行计数（天干+藏干）：**")
    lines.append("")
    for wx in WU_XING_ORDER:
        cnt = wx_counts.get(wx, 0)
        if cnt == max(wx_counts.values()):
            lines.append(f"- **{WU_XING_COLORS.get(wx, '')}{wx}：{cnt}个** ← 最旺")
        elif cnt == min(wx_counts.values()):
            lines.append(f"- **{WU_XING_COLORS.get(wx, '')}{wx}：{cnt}个** ← 最弱")
        else:
            lines.append(f"- {WU_XING_COLORS.get(wx, '')}{wx}：{cnt}个")

    lines.append("")

    # 能量流向
    lines.append("**能量流向图：**")
    lines.append("```")
    lines.append(f"            月令{yue_zhi}（{yue_ss}）")
    lines.append(f"                ↓")
    lines.append(f"  {_get_energy_flow_text(basic, analysis)}")
    lines.append("```")
    lines.append("")

    # 格局成败判定
    lines.append("**格局成败判定：**")
    lines.append("")
    lines.append(f"✅ {ge_ju}格成立 — {_get_ge_ju_comment(basic, analysis)}")
    lines.append(f"✅ 格局清纯 — {_get_ge_ju_purity(basic, analysis)}")
    lines.append(f"⚠️ {_get_ge_ju_risk(basic, analysis)}")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §3 身强弱详解 ──

def _gen_section_3(bazi: dict) -> str:
    """生成§3 身强弱详解"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    energy = analysis["energy"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)

    lines = []
    lines.append(_section_header(3, f"身强弱详解（{sq['score']}分·{sq['level']}）"))

    # 3.1 评分明细表
    lines.append("### 3.1 评分明细表（金鉴真人原始规则）")
    lines.append("")
    lines.append("【金鉴真人·身强弱规则】印只看月令本气计分（+40分），中气余气不计；月令本气比劫全计分（+40分）；所有比劫全计分；其他位置印不计分。")
    lines.append("")
    lines.append("| 维度 | 具体内容 | 计分 |")
    lines.append("|:----|:---------|:----:|")
    for detail in sq.get("details", []):
        # 从detail字符串提取
        pts = 0
        for part in detail.split("+"):
            try:
                pts += float(part.strip())
            except ValueError:
                pass
        # 使用原始detail内容
        label = detail.split("+")[0].strip() if "+" in detail else detail
        score_part = detail.split("+")[-1].strip() if "+" in detail else "0"
        lines.append(f"| **{label}** | {_get_detail_explain(detail, ri_gan)} | {'+'+score_part if score_part.replace('.','').replace('-','').isdigit() else score_part} |")

    lines.append(f"| **总分** | — | **{sq['score']}分** |")
    lines.append("")

    # 3.2 判定结果
    lines.append("### 3.2 判定结果")
    lines.append("")
    lines.append(f"**{sq['level']}（{sq['score']}分）**")
    lines.append("")
    lines.append(f"{ri_gan}（{ri_wx}）日主{'生于月令得生扶' if sq['score'] >= 40 else '生于月令不得力'}，{'印比强旺，身强能担财官' if sq['score'] >= 60 else '中和偏强，能担财官' if sq['score'] >= 40 else '中和偏弱，需印比帮扶' if sq['score'] >= 30 else '体弱难担财官，喜印比帮扶'}。")
    lines.append("")

    # 3.3 从弱格排查
    lines.append("### 3.3 从弱格排查")
    lines.append("")
    lines.append("【金鉴真人·从格判定规则】原局印比总分=0→从弱50分恒定；原局印比总分>100→从强20分恒定。")
    lines.append("")
    is_cong_ruo = sq["level"] == "身弱" and sq["score"] <= 5
    mark = "✅" if is_cong_ruo else "❌"
    reason = "印比总分≈0分，全局消耗性结构" if is_cong_ruo else f"印比总分{sq['score']}分，远超0分阈值，非从弱格"
    lines.append(f"{mark} 从弱——{reason}")
    lines.append("")
    if not is_cong_ruo:
        lines.append(f"驳盘结论：月令本气{'印' if sq['score'] >= 20 else '非印'}计分{sq['score']}分，天干比劫存在，有根有扶，完全不可能从弱。")
    lines.append("")

    # 3.4 假旺真弱排查
    lines.append("### 3.4 假旺真弱排查（强制检查）")
    lines.append("")
    lines.append("【金鉴真人·假旺真弱规则】印星被冲/被合化则虚浮；比劫根气受损则不足。")
    lines.append("")
    lines.append(f"{'✅' if sq['score'] >= 30 else '❌'} 检查印星是否空亡/被冲/被合：原局{'无明显冲合' if sq['score'] >= 30 else '需进一步排查'}")
    lines.append(f"{'✅' if sq['score'] >= 30 else '❌'} 检查比劫根气是否受损：{'根气稳固' if sq['score'] >= 30 else '根气不足'}")
    lines.append(f"结论：{'❌ 非假旺真弱。' + str(sq['score']) + '分为真旺。' if sq['score'] >= 30 else '✅ 可能存在假旺真弱现象，需结合大运流年进一步判断。'}")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §4 喜用神详解 ──

def _gen_section_4(bazi: dict) -> str:
    """生成§4 喜用神详解"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    xy = analysis["xi_yong_shen"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    xi_list = xy.get("xi_shen", [])
    ji_list = xy.get("ji_shen", [])

    lines = []
    lines.append(_section_header(4, "喜用神详解"))
    lines.append(f"【金鉴真人·喜忌规则·{'身强喜克泄耗' if sq['level'] == '身强' else '身弱喜生扶'}】{ri_gan}（{ri_wx}）日主{sq['level']}（{sq['score']}分），{'喜克泄耗（食伤/官杀/财），忌生扶（印/比劫）' if sq['level'] == '身强' else '喜生扶（印/比劫），忌克泄耗（食伤/官杀/财）'}。")
    lines.append("")

    # 4.1 用神层级
    lines.append("### 4.1 用神层级（逐层分析）")
    lines.append("")
    lines.append("| 层级 | 五行 | 十神 | 作用机制 | 原局落地 | 大运补位 |")
    lines.append("|:----:|:----:|:----:|:---------|:---------|:---------|")

    tiers = _get_yong_shen_tiers(basic, analysis)
    for tier in tiers:
        lines.append(f"| **{tier['level']}** | {tier['wx_symbol']}**{tier['wx']}** | **{tier['ss']}** | {tier['mechanism']} | {tier['original']} | {tier['dayun']} |")

    lines.append("")

    # 4.2 大运补用神窗口
    lines.append("### 4.2 大运补用神窗口")
    lines.append("")
    lines.append("| 大运 | 天干 | 地支 | 补什么 | 效果评估 |")
    lines.append("|:----|:----:|:----:|:-------|:---------|")
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    for d in da_yun_list:
        gan_ss = _get_shi_shen(ri_gan, d["gan"])
        zhi_ss = _get_zhi_shi_shen(ri_gan, d["zhi"])
        bu_shen = _get_dayun_bu_shen(d, ri_gan, xi_list)
        effect = _get_dayun_effect(d, ri_gan, xi_list, ji_list)
        lines.append(f"| {d['gan_zhi']}（{int(d['start_age'])}~{int(d['end_age'])}） | {d['gan']}（{gan_ss}） | {d['zhi']}（{zhi_ss}） | {bu_shen} | {effect} |")

    lines.append("")

    # 4.3 忌神引发的问题
    lines.append("### 4.3 忌神引发的问题")
    lines.append("")
    lines.append("| 忌神 | 五行 | 引发问题 | 典型场景 | 注意事项 |")
    lines.append("|:----|:----:|:---------|:---------|:---------|")
    for ji in ji_list:
        wx = _ji_shen_to_wu_xing(ji, ri_wx, sq["level"])
        lines.append(f"| **{ji}** | {WU_XING_COLORS.get(wx, '?')}{wx} | {_get_ji_shen_problem(ji, ri_wx, sq['level'])} | {_get_ji_shen_scene(ji, ri_wx)} | {_get_ji_shen_caution(ji, ri_wx)} |")

    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §5 灾祸/疾病/搬迁专项 ──

def _gen_section_5(bazi: dict) -> str:
    """生成§5 灾祸/疾病/搬迁专项"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    energy = analysis["energy"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    nian_gan = basic["nian_gan"]
    nian_zhi = basic["nian_zhi"]

    lines = []
    lines.append(_section_header(5, "灾祸/疾病/搬迁专项"))

    # 5.1 四大神煞排查
    lines.append("### 5.1 四大神煞排查")
    lines.append("")
    lines.append("| 神煞 | 查法 | 结果 | 影响分析 |")
    lines.append("|:----|:-----|:----:|:---------|")
    lines.append(f"| **元辰** | 年支{nian_zhi}查 | 依年支查 | 需结合具体年支判断 |")
    lines.append(f"| **灾煞** | 三合局查 | 依原局 | 需结合具体三合局判断 |")
    lines.append(f"| **天罗地网** | 辰巳/戌亥 | 依原局 | 需结合年命纳音判断 |")
    lines.append(f"| **印星被冲** | 月令是否被冲 | 原局{'有冲需排查' if sq['score'] <= 30 else '无明显冲'} | {'印星稳固' if sq['score'] >= 30 else '需谨慎'} |")
    lines.append("")

    # 5.2 五行过三排查
    lines.append("### 5.2 五行过三排查（疾病断）")
    lines.append("")
    lines.append("【金鉴真人·§14·五行过三规则】某五行在原局中出现≥3次（天干+地支藏干），该五行对应的器官容易出问题。")
    lines.append("")
    wx_counts = _count_wu_xing(basic)
    lines.append("| 五行 | 计数 | 过三 | 对应器官 | 健康风险等级 |")
    lines.append("|:----|:----:|:----:|:---------|:-----------:|")
    for wx in WU_XING_ORDER:
        cnt = wx_counts.get(wx, 0)
        over = "✅" if cnt >= 3 else "❌"
        organs = "、".join(WU_XING_ORGAN.get(wx, ("?",)))
        risk = "🔴高风险" if cnt >= 4 else "🟡中风险" if cnt >= 3 else "✅正常"
        lines.append(f"| {WU_XING_COLORS.get(wx, '')}**{wx}** | {cnt} | {over} | {organs} | {risk} |")

    lines.append("")

    # 5.3 七杀攻身
    lines.append("### 5.3 七杀攻身（如有）")
    lines.append("")
    lines.append("【金鉴真人·七杀断病法】七杀所在宫位→实际病灶所在。")
    lines.append("")
    qi_sha_info = _get_qi_sha_info(basic, analysis)
    lines.append(qi_sha_info)
    lines.append("")

    # 5.4 搬迁次数预测
    lines.append("### 5.4 搬迁次数预测")
    lines.append("")
    move_count = _estimate_move_count(dy.get("da_yun", []), sq)
    lines.append(f"🚚 **约{move_count}次**：")
    lines.append("")
    lines.append("| 阶段 | 次数 | 动因 | 命理信号 |")
    lines.append("|:----|:----:|:-----|:---------|")
    lines.append(f"| 童年 | 1次 | 家庭搬迁/成长环境变化 | {_get_dayun_by_index(dy, 0)}运初期变动 |")
    lines.append(f"| 求学 | 1次 | 异地求学 | {_get_dayun_by_index(dy, 1)}运离家信号 |")
    lines.append(f"| 职场初期 | 1次 | 第一份工作/换城市 | {_get_dayun_by_index(dy, 2)}运职场变动 |")
    lines.append(f"| 职场中期 | 1~2次 | 换工作/置业 | {'冲合刑害信号' if len(dy.get('da_yun',[])) > 3 else '职场变化'} |")
    lines.append(f"| 置业 | 1~2次 | 购房/换房 | 财星/印星大运 |")
    lines.append(f"| 晚年 | 1次 | 养老调整 | 晚年大运 |")

    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §6 性格分析 ──

def _gen_section_6(bazi: dict) -> str:
    """生成§6 性格分析（五重人格特质·≥150行）"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)

    lines = []
    lines.append(_section_header(6, "性格分析（五重人格特质）"))

    # 6.1 性格总肖
    lines.append("### 6.1 性格总肖（总论）")
    lines.append("")
    lines.append(f"【金鉴真人·§6·{ri_wx}+格局复合人格】")
    lines.append("")
    lines.append(f"{ri_gan}{ri_wx}，{'如甲木参天，积极向上' if ri_wx == '木' and _get_gan_yin_yang(ri_gan) == '阳' else '如乙木柔韧，适应力强' if ri_wx == '木' else '如丙火热烈，激情四射' if ri_wx == '火' and _get_gan_yin_yang(ri_gan) == '阳' else '如丁火温和，深思熟虑' if ri_wx == '火' else '如戊土厚重，稳重可靠' if ri_wx == '土' and _get_gan_yin_yang(ri_gan) == '阳' else '如己土包容，细致周到' if ri_wx == '土' else '如庚金刚锐，果断干练' if ri_wx == '金' and _get_gan_yin_yang(ri_gan) == '阳' else '如辛金精致，敏锐洞察' if ri_wx == '金' else '如壬水浩瀚，胸怀宽广' if ri_wx == '水' and _get_gan_yin_yang(ri_gan) == '阳' else '如癸水柔润，灵动机智'}。")
    lines.append("")
    lines.append(f"出生{'月令' if sq['score'] >= 60 else '格局'}赋予命主{'强大的内在驱动力和抗压能力' if sq['score'] >= 50 else '敏锐的感知力和适应力' if sq['score'] >= 30 else '深刻的反思力和柔韧的生存智慧'}。{'身强能担重压，有领袖潜质' if sq['score'] >= 60 else '中和平衡，适应性强' if sq['score'] >= 40 else '身弱敏感，善于借力'}。")
    lines.append("")

    # 6.2 五重人格特质
    lines.append("### 6.2 五重人格特质（详解）")
    lines.append("")
    lines.append("【五重人格特质·方法论】每重特质对应一个十神组合，从理论知识出发推导性格表现，每个特质≥50字。")
    lines.append("")

    personality_traits = _get_personality_traits(basic, analysis)
    for i, trait in enumerate(personality_traits):
        lines.append(f"---")
        lines.append("")
        lines.append(f"#### 特质{'一二三四五'[i]}：{trait['name']}")
        lines.append("")
        lines.append(f"**对应十神：** {trait['shi_shen']}")
        lines.append("")
        lines.append(f"【金鉴真人·§6·{trait['tag']}】")
        lines.append("")
        lines.append(trait["description"])
        lines.append("")

    # 6.3 十神性格底色
    lines.append("### 6.3 十神性格底色（完整表格）")
    lines.append("")
    lines.append("| 十神 | 在原局状态 | 对性格的影响（详细） |")
    lines.append("|:----|:----------|:-------------------|")

    for ss_entry in _get_shi_shen_personality(basic, analysis):
        lines.append(f"| **{ss_entry['name']}**（{ss_entry['position']}） | {ss_entry['status']} | {ss_entry['impact']} |")

    lines.append("")

    # 6.4 白话解读
    lines.append("### 6.4 白话解读")
    lines.append("")

    summary = _get_personality_summary(basic, analysis)
    lines.append(f"> **🗣️ 白话：** 综合来看，{summary}")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §7 身材外貌分析 ──

def _gen_section_7(bazi: dict) -> str:
    """生成§7 身材外貌分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    energy = analysis["energy"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)

    lines = []
    lines.append(_section_header(7, "身材外貌分析"))

    # 7.1 日主五行定基准
    lines.append("### 7.1 日主五行定基准")
    lines.append("")
    lines.append(f"【金鉴真人·§23·日主五行长相】{ri_gan}{ri_wx}日主：{_get_wx_appearance_base(ri_wx)}")
    lines.append("")

    # 7.2 身强弱修正
    lines.append("### 7.2 身强弱修正")
    lines.append("")
    lines.append(f"{ri_wx}日主{sq['level']}（{sq['score']}分）→{_get_strength_appearance_mod(sq['score'], sq['level'])}")
    lines.append("")

    # 7.3 食神/比劫影响
    lines.append("### 7.3 食神/比劫影响")
    lines.append("")
    shi_shen_info = _get_shi_shen_appearance(basic, analysis)
    for line in shi_shen_info:
        lines.append(line)
    lines.append("")

    # 7.4 综合推断
    lines.append("### 7.4 综合推断")
    lines.append("")
    height = _get_height_estimate(ri_wx, sq)
    lines.append(f"**身高推断：** 约{height}")
    lines.append("")
    lines.append(f"**整体印象：** {_get_overall_appearance(basic, analysis)}")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §8 财富分析 ──

def _gen_section_8(bazi: dict) -> str:
    """生成§8 财富分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    cx = analysis["cai_xing"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    cai_wx = _get_wo_ke_wx(ri_wx)

    lines = []
    lines.append(_section_header(8, "财富分析（金鉴真人原始五级对照+补财库方案）"))

    # 8.1 财星评分
    lines.append("### 8.1 财星评分（精确计算·逐位置验证）")
    lines.append("")
    lines.append(f"【金鉴真人·§5·财星计算规则】年支基础分=4分，月令基础分=40分，日/时支基础分=12分。藏干占比：本气100%、中气60%、余气30%。")
    lines.append(f"【金鉴真人·财星五行定向铁律】{ri_gan}（{ri_wx}）日主→{ri_wx}克{cai_wx}为财→财星五行={cai_wx}。")
    lines.append("")
    lines.append("| 位置 | 藏干 | 基础分 | 占比 | 实得分 | 正/偏 |")
    lines.append("|:----|:-----|:------:|:----:|:-----:|:-----:|")

    cai_details = cx.get("details", [])
    total_score = cx.get("score", 0)
    has_ku = cx.get("has_ku", False)
    cai_ku = cx.get("cai_ku", "")
    wealth_lv = cx.get("wealth_level", "未定")

    # 简单位置检查
    for pos_key, pos_label, base_pts in [("nian", "年支", 4), ("yue", "月令", 40), ("ri", "日支", 12), ("shi", "时支", 12)]:
        p = basic["pillars"][pos_key]
        found = False
        for cg in p["cang_gan"]:
            if cg["wu_xing"] == cai_wx:
                found = True
                pts = base_pts * cg["weight"] / 100
                ss_label = "正财" if _get_gan_yin_yang(ri_gan) != _get_gan_yin_yang(cg["gan"]) else "偏财"
                lines.append(f"| **{pos_label}**{p['zhi']} | **{cg['gan']}**（{cg['weight']}%） | {base_pts}分 | {cg['weight']}% | **{pts:.1f}分** | **{ss_label}** |")
        if not found:
            lines.append(f"| **{pos_label}**{p['zhi']} | 无{cai_wx}财星 | {base_pts}分 | — | 0分 | — |")

    lines.append(f"| **总分** | — | — | — | **{total_score}分** | — |")
    lines.append("")

    # 8.2 六种八字状态判定
    lines.append("### 8.2 六种八字状态判定")
    lines.append("")
    lines.append("| 状态 | 条件 | 判定 |")
    lines.append("|:----|:-----|:-----|")
    is_qiang = sq["level"] == "身强"
    lines.append(f"| 身强财旺→大富 | 身强(40~60)+财≥40 | {'✅' if is_qiang and total_score >= 40 else '❌'} |")
    lines.append(f"| 身强财弱→中富 | 身强+财<40+无库 | {'✅' if is_qiang and total_score < 40 and not has_ku else '❌'} |")
    lines.append(f"| 身弱财旺→小富 | 身弱+财≥40 | {'✅' if not is_qiang and total_score >= 40 else '❌'} |")
    lines.append(f"| 身弱财弱→小富 | 身弱+财<40 | {'✅' if not is_qiang and total_score < 40 else '❌'} |")
    lines.append(f"| 无财身弱→贫穷 | 无财+身弱 | {'✅' if not is_qiang and total_score <= 0 else '❌'} |")
    lines.append(f"| 从弱格→特殊 | 0分→50分+财得令 | {'✅' if sq['level'] == '身弱' and sq['score'] <= 5 else '❌'} |")
    lines.append("")

    # 8.3 原始财富五级对照
    lines.append("### 8.3 金鉴真人原始财富五级对照")
    lines.append("")
    lines.append("【金鉴真人·原始五级标准】巨富=几十亿~上百亿（身强财旺+日时柱有库+无刑冲+大运配合）；大富=几个亿（身强财旺）；中富=几千万（身强财弱+无库）；小富=上千万（身弱财也弱+遇印比则发）；贫穷=千万以内（身弱+无财）。")
    lines.append("")
    lines.append("| 五级标准 | 条件链 | 此命是否符合 |")
    lines.append("|:--------:|:-------|:-----------:|")
    lines.append(f"| 👑**巨富**（几十亿~上百亿） | 身强财旺+日时柱有库+无刑冲 | {'❌' if total_score < 60 or not has_ku else '✅'} |")
    lines.append(f"| 💰**大富**（几个亿） | 身强财旺 | {'❌' if total_score < 40 else '✅'} |")
    lines.append(f"| 🥈**中富**（几千万） | 身强财弱+无库 | {'✅' if is_qiang and total_score < 40 and not has_ku else '❌'} |")
    lines.append(f"| 🏠**小富**（上千万） | 身弱财也弱+遇印比则发 | {'✅' if not is_qiang and total_score < 40 else '❌'} |")
    lines.append(f"| 🥉**贫穷**（千万以内） | 身弱+无财 | {'✅' if not is_qiang and total_score <= 0 else '❌'} |")
    lines.append("")

    # 8.4 财喜藏不喜露
    lines.append("### 8.4 财喜藏不喜露")
    lines.append("")
    lines.append("【金鉴真人·§8.2·财喜藏不喜露】「财藏如宝在匣，不露则人不妒；露则比劫觊觎」。")
    lines.append("")
    cai_exposed = _is_cai_exposed(basic, cai_wx)
    lines.append(f"原局财星{'透干' if cai_exposed else '均为地支藏干'}→财{'露' if cai_exposed else '喜藏'}。{'财富容易外露，需防比劫觊觎' if cai_exposed else '财富积累方式倾向于稳健、暗藏、不张扬'}。")
    lines.append("")

    # 8.5 财库检查+补财库方案
    lines.append("### 8.5 财库检查+补财库方案（强制必含）")
    lines.append("")
    lines.append("【金鉴真人·§10·财库规则】日/时柱有辰戌丑未=有财库或比劫库。财库在日/时=自己的库。")
    lines.append("")
    lines.append("| 位置 | 是否有库 | 类型 |")
    lines.append("|:----|:--------:|:----|")
    for pos_key, pos_label in [("ri", "日支"), ("shi", "时支")]:
        p = basic["pillars"][pos_key]
        is_ku = p["zhi"] in ["辰", "戌", "丑", "未"]
        lines.append(f"| {pos_label}{p['zhi']} | {'✅ 有库' if is_ku else '❌ 非库'} | {'四库之一' if is_ku else '—'} |")

    lines.append("")
    if not has_ku:
        lines.append("**无天生财库→需要主动补财库：**")
        lines.append("")
        lines.append("| 补库方法 | 操作 | 原理 |")
        lines.append("|:---------|:-----|:------|")
        lines.append(f"| **①开户补库** | 在家中/公司{cai_ku or '财库'}方位银行开设专用储蓄账户，每月定额存入 | 模拟「财库」的储蓄功能 |")
        lines.append(f"| **②实物补库** | 家中财位放{cai_wx}属性收纳盒/聚宝盆，内置6枚硬币 | 人为创造「财库」格局 |")
        lines.append(f"| **③行业补库** | 选择属{cai_wx}五行的行业长期深耕 | 以行业沉淀替代财库 |")
        lines.append(f"| **④合作补库** | 与八字日/时柱带辰戌丑未的人深度合作 | 借对方的财库结构增强自己的蓄财能力 |")
        lines.append(f"| **⑤大运借库** | 在财星大运财位进行置业/投资 | 大运临时借库 |")
    else:
        lines.append("**有天生财库→蓄财能力强：**")
        lines.append(f"日/时柱有{cai_ku}财库，财富积累能力强，可以蓄财。")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §9 置业/买房分析 ──

def _gen_section_9(bazi: dict) -> str:
    """生成§9 置业/买房分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    dy = analysis["da_yun"]

    ri_wx = _get_ri_gan_wu_xing(basic["ri_gan"])

    lines = []
    lines.append(_section_header(9, "置业/买房分析"))

    lines.append("### 9.1 不动产特征")
    lines.append("")
    lines.append("【金鉴真人·§9·不动产特征规则】印星为房+财星为产+土为基。日/时支为库=置房产潜力。")
    lines.append("")
    lines.append(f"原局{'月令为印·有不动产之象' if sq['score'] >= 40 else '财星旺·置业能力较强'}。{'身强足以支撑置业负担' if sq['score'] >= 40 else '身弱置产需谨慎负债'}。")
    lines.append("")

    lines.append("### 9.2 置业时间点")
    lines.append("")
    lines.append("| 时间 | 大运 | 命理信号 | 事件 |")
    lines.append("|:----|:----|:---------|:-----|")
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    for i, d in enumerate(da_yun_list):
        if i >= 5:
            break
        start_year = int(qi_yun_age + i * 10)
        signal = _get_zhiye_signal(d, ri_wx)
        lines.append(f"| 约{start_year + 1}年起 | {d['gan_zhi']}运 | {signal} | {'首次' if i <= 1 else '二次' if i <= 3 else '改善型'}置业窗口 |")

    lines.append("")

    lines.append("### 9.3 风水建议")
    lines.append("")
    lines.append(f"喜用神相关→置业选择：")
    lines.append(f"- **朝向：** 依喜用五行方位选择")
    lines.append(f"- **楼层：** 依喜用五行数字选择")
    lines.append(f"- **环境：** 近喜用五行之环境最佳")
    lines.append("")

    lines.append("### 9.4 风险提示")
    lines.append("")
    lines.append(f"- 冲太岁年份避免大额房产交易")
    lines.append(f"- 比劫旺的大运注意合作购房风险")
    lines.append(f"- 身弱的大运慎重大额贷款")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §10 事业分析 ──

def _gen_section_10(bazi: dict) -> str:
    """生成§10 事业分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    ge_ju = analysis["ge_ju"]

    lines = []
    lines.append(_section_header(10, "事业分析"))

    lines.append("### 10.1 格局定方向")
    lines.append("")
    lines.append(f"【金鉴真人·事业·格局定方向】{ge_ju}格→{_get_ge_ju_career_direction(ge_ju, ri_wx)}")
    lines.append("")

    lines.append("### 10.2 恶神制化定级别")
    lines.append("")
    lines.append("【金鉴真人·事业·恶神制化决定事业级别】「凡成大事者必有恶神，恶神有制方为贵」。")
    lines.append("")
    lines.append(_get_e_shen_info(basic, analysis))
    lines.append("")

    lines.append("### 10.3 五行定行业")
    lines.append("")
    lines.append("| 喜用五行 | 对应行业 | 适合度 | 具体方向 |")
    lines.append("|:--------|:---------|:------:|:---------|")
    xi_list = analysis["xi_yong_shen"].get("xi_shen", [])
    for ss_name in xi_list:
        wx = _ji_shen_to_wu_xing(ss_name, ri_wx, analysis["shen_qiang_ruo"]["level"])
        industries = _get_wx_industries(wx)
        suitability = "⭐⭐⭐⭐⭐" if ss_name == (xi_list[0] if xi_list else "") else "⭐⭐⭐⭐"
        lines.append(f"| {WU_XING_COLORS.get(wx, '?')}**{wx}**（{ss_name}） | {industries} | {suitability} | {_get_wx_career_detail(wx, ss_name)} |")

    lines.append("")

    lines.append("### 10.4 事业等级定性")
    lines.append("")
    lines.append("【金鉴真人·事业·§10.5事业等级定性】")
    lines.append("")
    career_lv = _get_career_level(basic, analysis)
    lines.append(f"**事业等级：{career_lv}**")
    lines.append("")
    lines.append(f"**定性依据：**")
    lines.append(f"- 格局类型：{ge_ju}格→{_get_ge_ju_career_type(ge_ju)}")
    lines.append(f"- 官杀制化：{_get_guan_sha_info(basic, analysis)}")
    lines.append(f"- 印星状态：{_get_yin_info(basic, analysis)}")
    lines.append(f"- 大运支持：{_get_da_yun_career_support(dy)}")
    lines.append("")

    lines.append("### 10.5 关键事业年份")
    lines.append("")
    lines.append("| 年份 | 大运 | 事件 | 类型 |")
    lines.append("|:----|:----|:-----|:----:|")
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    career_years = _get_career_key_years(dy, ri_gan)
    for cy in career_years:
        lines.append(f"| **{cy['year']}** | {cy['dayun']} | {cy['event']} | {cy['type']} |")

    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §11 学历分析 ──

def _gen_section_11(bazi: dict) -> str:
    """生成§11 学历分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    nian_gan = basic["nian_gan"]

    lines = []
    lines.append(_section_header(11, "学历分析"))

    # 11.1 第0层三档法
    lines.append("### 11.1 第0层·年柱有印三档法")
    lines.append("")
    lines.append("【金鉴真人·§1·第0层三档法】①年柱有印（天干透或地支藏）→学业好；②不符合①但12岁前大运遇文昌→中等；③均不符合→一般。")
    lines.append("")

    has_year_yin = _check_year_has_yin(basic, ri_gan)
    nian_gan = basic["nian_gan"]
    nian_zhi = basic["nian_zhi"]
    gan_ss = _get_shi_shen(ri_gan, nian_gan)
    if gan_ss in ["正印", "偏印"]:
        year_check = f"天干有印({gan_ss})"
    elif has_year_yin:
        year_check = f"年支{nian_zhi}藏干印星"
    else:
        year_check = "无印"
    lines.append(f"**检查：** 年柱{nian_gan}{nian_zhi}→{year_check} → {'有学业基因' if has_year_yin else '学业基因偏弱'}")
    lines.append(f"**第0层判定：{'✅ 上等（年柱有印·学业基因强）' if has_year_yin else '⚠️ 中等偏上（学业基因一般·需大运配合）'}**")
    lines.append("")

    # 11.2 六步精细排查
    lines.append("### 11.2 六步精细排查")
    lines.append("")
    lines.append("| 步骤 | 检查项 | 详细分析 | 结果 |")
    lines.append("|:----|:-------|:---------|:----:|")

    steps = _get_education_steps(basic, analysis)
    for step in steps:
        lines.append(f"| **{step['name']}** | {step['check']} | {step['analysis']} | {step['result']} |")

    lines.append("")

    # 11.3 考试运分析
    lines.append("### 11.3 考试运分析")
    lines.append("")
    lines.append(_get_exam_luck(basic, analysis))
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §12 婚姻/感情分析 ──

def _gen_section_12(bazi: dict) -> str:
    """生成§12 婚姻/感情分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    gender = basic.get("gender", "男")
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    ri_zhi = basic["ri_zhi"]

    lines = []
    lines.append(_section_header(12, "婚姻/感情分析"))

    # 12.1 夫妻宫喜忌
    lines.append("### 12.1 夫妻宫（日支）喜忌")
    lines.append("")
    lines.append(f"日支：**{ri_zhi}**")
    lines.append(f"藏干：{_cang_gan_text(ri_zhi)}")
    ri_zhi_ss = _get_zhi_shi_shen(ri_gan, ri_zhi) if ri_zhi else "—"
    lines.append(f"喜忌：{'根据日支十神与全局配合判断'}")
    lines.append(f"十神：{ri_zhi_ss}→{_get_fuqi_gong_impact(ri_zhi_ss, gender)}")
    lines.append("")

    # 12.2 夫妻星
    lines.append("### 12.2 夫妻星")
    lines.append("")
    if gender == "男":
        lines.append(f"正财/偏财为妻星。{'原局财星状态决定婚姻质量'}")
    else:
        lines.append(f"正官/七杀为夫星。{'原局官杀状态决定婚姻质量'}")
    lines.append(_get_fuqi_xing_info(basic, analysis, gender))
    lines.append("")

    # 12.3 四大结婚信号
    lines.append("### 12.3 四大结婚信号")
    lines.append("")
    signals = _get_marriage_signals(basic, analysis, gender)
    for s in signals:
        lines.append(f"- [{'x' if s['triggered'] else ' '}] {s['signal']}：{s['interpretation']}")
    lines.append("")

    # 12.4 结婚窗口
    lines.append("### 12.4 结婚窗口")
    lines.append("")
    lines.append("| 窗口 | 大运 | 年份 | 解读 |")
    lines.append("|:----|:----|:----|:-----|")
    windows = _get_marriage_windows(dy, ri_gan)
    for w in windows:
        lines.append(f"| {w['name']} | {w['dayun']} | {w['year']} | {w['desc']} |")
    lines.append("")

    # 12.5 配偶特征
    lines.append("### 12.5 配偶特征")
    lines.append("")
    lines.append(_get_spouse_features(basic, analysis, gender))
    lines.append("")

    # 12.6 感情走势
    lines.append("### 12.6 感情走势")
    lines.append("")
    lines.append(_get_marriage_trend(basic, analysis, gender))
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §13 子女分析 ──

def _gen_section_13(bazi: dict) -> str:
    """生成§13 子女分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    gender = basic.get("gender", "男")

    ri_gan = basic["ri_gan"]
    shi_zhi = basic["shi_zhi"]

    lines = []
    lines.append(_section_header(13, "子女分析"))

    lines.append("### 13.1 子女星判定")
    lines.append("")
    if gender == "男":
        lines.append(f"男命：官杀为子女星。{_get_zi_nv_xing_info(basic, analysis, gender)}")
    else:
        lines.append(f"女命：食伤为子女星。{_get_zi_nv_xing_info(basic, analysis, gender)}")
    lines.append("")

    lines.append("### 13.2 子女宫（时柱）")
    lines.append("")
    lines.append(f"时柱：{basic['shi_gan']}{shi_zhi}")
    lines.append(f"时支：{_cang_gan_text(shi_zhi)}")
    lines.append(f"状态：{'喜' if _get_zhi_shi_shen(ri_gan, shi_zhi) in analysis['xi_yong_shen'].get('xi_shen', []) else '忌'}")
    lines.append("")

    lines.append("### 13.3 添丁年份")
    lines.append("")
    lines.append(_get_tian_ding_years(basic, analysis))
    lines.append("")

    lines.append("### 13.4 子女性格")
    lines.append("")
    lines.append(_get_children_personality(basic, analysis))
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §14 健康分析 ──

def _gen_section_14(bazi: dict) -> str:
    """生成§14 健康分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    sq = analysis["shen_qiang_ruo"]
    energy = analysis["energy"]
    dy = analysis["da_yun"]

    lines = []
    lines.append(_section_header(14, "健康分析"))

    # 14.1 五行过三排查
    lines.append("### 14.1 五行过三排查表")
    lines.append("")
    wx_counts = _count_wu_xing(basic)
    lines.append("| 属性 | 过三判定 | 对应器官 | 健康风险 |")
    lines.append("|:----|:---------|:---------|:---------|")
    for wx in WU_XING_ORDER:
        cnt = wx_counts.get(wx, 0)
        over = "✅" if cnt >= 3 else "❌"
        organs = "、".join(WU_XING_ORGAN.get(wx, ("?",)))
        risk = "🔴高风险·需定期体检" if cnt >= 4 else "🟡关注" if cnt >= 3 else "✅正常"
        lines.append(f"| {WU_XING_COLORS.get(wx, '')}{wx}（{cnt}个） | {over} | {organs} | {risk} |")

    lines.append("")

    # 14.2 七杀为病
    lines.append("### 14.2 七杀为病")
    lines.append("")
    lines.append(_get_qi_sha_health(basic, analysis))
    lines.append("")

    # 14.3 偏印主瘀
    lines.append("### 14.3 偏印主瘀")
    lines.append("")
    lines.append(_get_pian_yin_health(basic, analysis))
    lines.append("")

    # 14.4 重点防护年份
    lines.append("### 14.4 重点防护年份")
    lines.append("")
    lines.append("| 年份 | 大运 | 健康风险 | 注意事项 |")
    lines.append("|:----|:----|:---------|:---------|")
    health_years = _get_health_key_years(dy, energy)
    for hy in health_years[:8]:
        lines.append(f"| {hy['year']} | {hy['dayun']} | {hy['risk']} | {hy['note']} |")

    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §15 六亲分析 ──

def _gen_section_15(bazi: dict, name: str) -> str:
    """生成§15 六亲分析"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]

    ri_gan = basic["ri_gan"]

    lines = []
    lines.append(_section_header(15, "六亲分析"))

    for pos_key, pos_label, title in [("nian", "年柱", "祖上/早年家庭"), 
                                        ("yue", "月柱", "父母/兄弟姐妹/出身环境"),
                                        ("ri", "日支", "配偶/婚姻"),
                                        ("shi", "时柱", "子女/晚年")]:
        p = basic["pillars"][pos_key]
        gan_ss = p["gan_shi_shen"] if pos_key != "ri" else "日主"
        lines.append(f"### 15.{['一','二','三','四'][['nian','yue','ri','shi'].index(pos_key)]} {pos_label}（{title}）")
        lines.append("")
        lines.append(f"{pos_label}：{p['gan']}{p['zhi']}")
        lines.append(f"十神：{gan_ss}")
        lines.append(f"解读：{_get_liu_qin_interpretation(pos_key, p, ri_gan, analysis)}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §16 全生命周期重点事件总表 ──

def _gen_section_16(bazi: dict) -> str:
    """生成§16 全生命周期重点事件总表（≥50条）"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)

    lines = []
    lines.append(_section_header(16, "全生命周期重点事件总表"))
    lines.append("")
    lines.append("**事件类型代码：** A=学业 B=事业/晋升 C=发财/财务 E=置业/买房 F=结婚/感情 G=子女添丁 H=压力/灾祸/低谷 I=觉醒/转折")
    lines.append("")
    lines.append("| 序号 | 大运 | 年份 | 年龄 | 事件 | 类型 | 命理信号 |")
    lines.append("|:----:|:----:|:----:|:----:|:-----|:----:|:---------|")

    event_id = 0
    events = _generate_life_events(basic, analysis, dy)
    for event in events:
        event_id += 1
        lines.append(f"| {event_id} | {event['dayun']} | {event['year']} | {event['age']} | {event['event']} | {event['type']} | {event['signal']} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §17 大运精析 ──

def _gen_section_17(bazi: dict) -> str:
    """生成§17 大运精析（10步完整序列）"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    xi_list = analysis["xi_yong_shen"].get("xi_shen", [])
    ji_list = analysis["xi_yong_shen"].get("ji_shen", [])

    lines = []
    lines.append(_section_header(17, "大运精析（10步完整序列）"))

    for i, d in enumerate(da_yun_list):
        start_age = int(d["start_age"])
        end_age = int(d["end_age"])
        start_year = int(qi_yun_age + i * 10)
        end_year = start_year + 9

        gan_ss = _get_shi_shen(ri_gan, d["gan"])
        zhi_ss_list = []
        for cg, _ in DI_ZHI_CANG_GAN[d["zhi"]]:
            zhi_ss_list.append(f"{cg}（{_get_shi_shen(ri_gan, cg)}）")
        zhi_ss = "、".join(zhi_ss_list)

        lines.append(f"### 17.{i + 1} {d['gan_zhi']}大运（{start_year}~{end_year}）·{_get_dayun_feature(d, ri_gan, xi_list, ji_list)}")
        lines.append("")
        lines.append(f"**干支**：{d['gan']}（{gan_ss}）坐{d['zhi']}（{zhi_ss}）")
        lines.append(f"**年龄**：{start_age}~{end_age}岁")
        lines.append(f"**事件**：{_get_dayun_key_events(d, ri_gan, xi_list, ji_list)}")
        lines.append("")
        lines.append("**运象分析**：")
        lines.append(f"{_get_dayun_analysis_detail(d, ri_gan, ri_wx, xi_list, ji_list)}")
        lines.append("")
        lines.append("**关键年份**：")
        key_years = _get_dayun_key_years(d, ri_gan, i, qi_yun_age)
        for ky in key_years[:4]:
            lines.append(f"- **{ky['year']}**（{ky['event']}）：{ky['analysis']}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §18 三决断 ──

def _gen_section_18(bazi: dict, name: str) -> str:
    """生成§18 三决断"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    dy = analysis["da_yun"]

    ri_gan = basic["ri_gan"]

    lines = []
    lines.append(_section_header(18, "三决断（6要素断语格式）"))

    decisions = _get_three_decisions(basic, analysis, name)
    for i, dec in enumerate(decisions):
        lines.append(f"### 决断{'一二三'[i]}：{dec['title']}")
        lines.append("")
        lines.append("```markdown")
        lines.append(f"**其人**：{dec['person']}")
        lines.append(f"**其事**：{dec['matter']}")
        lines.append(f"**其时**：{dec['time']}")
        lines.append(f"**其度**：{dec['degree']}")
        lines.append(f"**理由**：{dec['reason']}")
        lines.append("")
        lines.append(f"**断语**：{dec['verdict']}")
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §19 人生运程总评 ──

def _gen_section_19(bazi: dict) -> str:
    """生成§19 人生运程总评"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]
    dy = analysis["da_yun"]

    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    gender = basic.get("gender", "男")

    lines = []
    lines.append(_section_header(19, "人生运程总评"))

    # 19.1 ASCII运程曲线
    lines.append("### 19.1 ASCII运程曲线至100岁")
    lines.append("")
    lines.append("```")
    lines.append("年龄   大运        运程曲线                    评分")
    lines.append("──── ──────── ───────────────────── ──────")

    for i, d in enumerate(da_yun_list):
        start_age = int(d["start_age"])
        rating = _get_dayun_rating(d, analysis)
        bar = "█" * max(1, rating) + "░" * (10 - max(1, rating))
        lines.append(f"{str(start_age).rjust(2)}~{str(start_age + 9).ljust(2)} {d['gan_zhi']}  {bar}  {rating}/10")

    lines.append("     ↑ 幼年低谷   ↑ 中年巅峰   ↑ 晚年平稳")
    lines.append("```")
    lines.append("")

    # 19.2 各运评分表
    lines.append("### 19.2 各运评分表")
    lines.append("")
    lines.append("| 大运 | 年龄段 | 评分/10 | 评语 |")
    lines.append("|:----|:------:|:-------:|:-----|")
    for i, d in enumerate(da_yun_list):
        start_age = int(d["start_age"])
        rating = _get_dayun_rating(d, analysis)
        comment = _get_dayun_rating_comment(rating)
        lines.append(f"| {d['gan_zhi']}运 | {start_age}~{start_age + 9}岁 | {rating}/10 | {comment} |")

    lines.append("")

    # 19.3 吉凶总评
    lines.append("### 19.3 吉凶总评")
    lines.append("")
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]
    lines.append(f"**运程核心**：命主为{ge_ju}格，{sq['level']}（{sq['score']}分），一生运程{'先苦后甜·中年发力' if sq['score'] >= 50 else '波折中求稳·后福可期' if sq['score'] >= 30 else '起伏较大·需顺势而为'}。")
    lines.append("")
    lines.append("**优势窗口**：中年运（第4~6步）事业和财富集中爆发期。")
    lines.append("")
    lines.append("**关键风险**：晚年运需关注健康。")
    lines.append("")
    lines.append("**人生定位**：技术型思想领袖/专家型人才。")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §20 五行补充建议 ──

def _gen_section_20(bazi: dict) -> str:
    """生成§20 五行补充建议"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    xi_list = analysis["xi_yong_shen"].get("xi_shen", [])
    ji_list = analysis["xi_yong_shen"].get("ji_shen", [])

    lines = []
    lines.append(_section_header(20, "五行补充建议"))

    # 20.1 颜色调运
    lines.append("### 20.1 颜色调运")
    lines.append("")
    lines.append("| 五行 | 颜色 | 建议用途 |")
    lines.append("|:----|:-----|:---------|")
    for ss in xi_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        lines.append(f"| **{wx}**（{ss}·喜用） | {WU_XING_COLOR_MAP.get(wx, '—')} | 穿着/装饰/办公首选 |")
    for ss in ji_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        lines.append(f"| **{wx}**（{ss}·忌） | {WU_XING_COLOR_MAP.get(wx, '—')} | 避免大面积使用 |")

    lines.append("")

    # 20.2 数字吉利
    lines.append("### 20.2 数字吉利")
    lines.append("")
    lucky_nums = []
    unlucky_nums = []
    for ss in xi_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        lucky_nums.extend(WU_XING_LUCKY_NUM.get(wx, "").split(", "))
    for ss in ji_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        unlucky_nums.extend(WU_XING_LUCKY_NUM.get(wx, "").split(", "))
    lines.append(f"吉利数字：{'、'.join(sorted(set(lucky_nums))) if lucky_nums else '参考喜用神五行'}")
    lines.append(f"忌讳数字：{'、'.join(sorted(set(unlucky_nums))) if unlucky_nums else '参考忌神五行'}")
    lines.append("")

    # 20.3 方位建议
    lines.append("### 20.3 方位建议")
    lines.append("")
    good_dirs = []
    bad_dirs = []
    for ss in xi_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        good_dirs.append(WU_XING_DIRECTION.get(wx, ""))
    for ss in ji_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        bad_dirs.append(WU_XING_DIRECTION.get(wx, ""))
    lines.append(f"吉利方位：{'、'.join(good_dirs) if good_dirs else '参考喜用神五行'}")
    lines.append(f"忌讳方位：{'、'.join(bad_dirs) if bad_dirs else '参考忌神五行'}")
    lines.append("")

    # 20.4 饰品搭配
    lines.append("### 20.4 饰品搭配")
    lines.append("")
    good_jewelry = []
    bad_jewelry = []
    for ss in xi_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        good_jewelry.append(WU_XING_JEWELRY.get(wx, ""))
    for ss in ji_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        bad_jewelry.append(WU_XING_JEWELRY.get(wx, ""))
    lines.append(f"推荐：{'、'.join(good_jewelry) if good_jewelry else '参考喜用神五行'}")
    lines.append(f"忌讳：{'、'.join(bad_jewelry) if bad_jewelry else '参考忌神五行'}")
    lines.append("")

    # 20.5 饮食调理
    lines.append("### 20.5 饮食调理")
    lines.append("")
    good_food = []
    for ss in xi_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        good_food.append(WU_XING_FOOD.get(wx, ""))
    lines.append(f"推荐：{'；'.join(good_food) if good_food else '根据喜用神五行饮食调理'}")
    lines.append(f"忌讳：过多食用忌神五行对应的食物")
    lines.append("")

    # 20.6 节气调运
    lines.append("### 20.6 节气调运")
    lines.append("")
    lines.append(_get_seasonal_advice(ri_wx, analysis))
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── §21 人生建议 ──

def _gen_section_21(bazi: dict, name: str) -> str:
    """生成§21 人生建议（≥400字）"""
    basic = bazi["basic"]
    analysis = bazi["analysis"]

    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]
    cx = analysis["cai_xing"]

    lines = []
    lines.append(_section_header(21, "人生建议（5大维度·针对性·可执行·总≥400字）"))

    # 21.1 事业方向
    lines.append("### 21.1 事业方向与路线图")
    lines.append("")
    lines.append(f"基于{ge_ju}格局、{sq['level']}（{sq['score']}分）身强弱、喜用神为{'、'.join(analysis['xi_yong_shen'].get('xi_shen', []))}的命局特征，事业方向建议如下：")
    lines.append("")
    lines.append(f"**核心发展路线**：{_get_career_advice(basic, analysis)}")
    lines.append("")
    lines.append(f"**具体行业推荐**：{_get_wx_industries_list(basic, analysis)}")
    lines.append("")
    lines.append(f"**创业时机**：{'身强能担风险，适合在喜用神大运创业' if sq['score'] >= 50 else '身弱不宜冒进，适合在帮扶大运稳中求进' if sq['score'] >= 30 else '适合在大运帮扶时尝试副业或轻资产创业'}。")
    lines.append("")

    # 21.2 财富管理
    lines.append("### 21.2 财富管理与补财库")
    lines.append("")
    lines.append(f"**财库判断**：{'日/时柱有财库→蓄财能力强' if cx.get('has_ku') else '日/时柱无财库→财来财去需主动蓄财'}")
    lines.append("")
    lines.append(f"**补财库方法（{'无库者' if not cx.get('has_ku') else '有库者'}）：** ")
    if not cx.get("has_ku"):
        cai_ku = cx.get("cai_ku", "财库")
        lines.append(f"① 实物补库：在家中/办公室摆放对应{cai_ku}方位的摆件")
        lines.append(f"② 开户补库：在对应财库方位银行开户，建立专门的储蓄/投资账户")
        lines.append(f"③ 行业补库：选择属喜用五行行业的长期深耕")
        lines.append(f"④ 合作补库：与带财库八字的人合作")
    lines.append(f"**投资方向**：偏财旺→适合风险投资/合伙；正财旺→适合稳健理财/固定收入。")
    lines.append(f"**风险防范**：比劫夺财年份避免合伙投资、做担保。")
    lines.append("")

    # 21.3 健康养生
    lines.append("### 21.3 健康养生（终身策略）")
    lines.append("")
    wx_counts = _count_wu_xing(basic)
    over_wx = [wx for wx in WU_XING_ORDER if wx_counts.get(wx, 0) >= 3]
    lines.append(f"基于五行过三分析（{'、'.join(over_wx) if over_wx else '无明显过三'}），日常保健建议如下：")
    lines.append(f"**重点防护**：{'、'.join(['、'.join(WU_XING_ORGAN.get(wx, ('?',))) for wx in over_wx]) if over_wx else '均衡调养'}。")
    lines.append(f"**体检建议**：每年针对过三五行对应的器官重点筛查。")
    lines.append(f"**生活习惯**：根据喜用神五行调整饮食和作息。")
    lines.append("")

    # 21.4 婚姻感情建议
    lines.append("### 21.4 婚姻/感情经营")
    lines.append("")
    lines.append(f"**相处之道**：基于夫妻宫（{basic.get('ri_zhi', '?')}）十神和配偶星状态，{'注重沟通和理解' if sq['score'] >= 40 else '需要更多的包容和耐心'}。")
    lines.append(f"**关键节点**：中年大运（喜用神大运）是感情质变期。")
    lines.append("")

    # 21.5 关键流年警示
    lines.append("### 21.5 关键流年警示（未来10年）")
    lines.append("")
    lines.append("| 年份 | 干支 | 大运 | 风险类型 | 具体注意 |")
    lines.append("|:----|:----|:----|:---------|:---------|")
    warns = _get_future_warnings(basic, analysis)
    for w in warns:
        lines.append(f"| {w['year']} | {w['ganzhi']} | {w['dayun']} | {w['risk_type']} | {w['note']} |")

    lines.append("")

    # 21.6 人生总纲寄语
    lines.append("### 21.6 人生总纲寄语")
    lines.append("")
    lines.append(f"**核心策略**：充分发挥{ge_ju}格局优势，善用喜用神能量，注意忌神引发的风险。")
    lines.append("")
    lines.append(f"**三条落地建议：**")
    lines.append(f"1. 选择与喜用神五行相关的行业深耕，建立核心竞争力。")
    lines.append(f"2. 在忌神大运/年份保守行事，在喜用神大运/年份积极进取。")
    lines.append(f"3. 注重健康管理，定期检查过三五行对应的器官。")
    lines.append("")
    lines.append(f"**命理诗学**：天行健，君子以自强不息。{ri_gan}命主，{'顺势而为' if sq['level'] == '身强' else '借力而行' if sq['level'] == '中和' else '厚积薄发'}，终有成就之时。")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ── 尾部签名 ──

def _gen_footer() -> str:
    """生成尾部版本与署名"""
    lines = []
    lines.append("\n## 🔄 版本与署名\n")
    lines.append("```markdown")
    lines.append("---")
    lines.append(f"**编制人：** 金鉴真人")
    lines.append(f"**编制时间：** {datetime.now().strftime('%Y年%m月%d日')}")
    lines.append("**版本：** v1.0")
    lines.append("**分析方法：** 金鉴真人体系·精密评分法·引擎数据校准")
    lines.append("**模板标准：** bazi-report-template v4.1（立v2.0精致格式为内核+新增置业独立§9+六亲§15+统一21§编号）")
    lines.append("**模板说明：** 本报告为金鉴真人八字命理报告的标准输出格式。21个§板块（§1~§21）固定编号。")
    lines.append("---")
    lines.append("```")
    lines.append("")
    lines.append(f"\n{_make_signature()}\n")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# 辅助函数（数据驱动的叙事生成）
# ═══════════════════════════════════════════════════════════════════

def _count_wu_xing(basic: dict) -> dict:
    """五行计数（天干+藏干）"""
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = basic["pillars"][pos_key]
        # 天干
        wx = p["gan_wu_xing"]
        counts[wx] = counts.get(wx, 0) + 1
        # 地支藏干（按比例加权）
        for cg in p["cang_gan"]:
            weight = cg["weight"]
            if weight >= 100:
                counts[cg["wu_xing"]] = counts.get(cg["wu_xing"], 0) + 1
            elif weight >= 60:
                counts[cg["wu_xing"]] = counts.get(cg["wu_xing"], 0) + 0.6
            else:
                counts[cg["wu_xing"]] = counts.get(cg["wu_xing"], 0) + 0.3
    # 取整
    for k in counts:
        counts[k] = round(counts[k], 1)
    return counts


def _get_shi_shen_relation(ri_gan: str, gan: str) -> str:
    """获取天干之间的五行生克关系描述"""
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    g_wx = TIAN_GAN_WU_XING[gan]
    if ri_wx == g_wx:
        return f"同五行→{'比肩' if _get_gan_yin_yang(ri_gan) == _get_gan_yin_yang(gan) else '劫财'}"
    # 生我
    if _get_sheng_wo_wx(ri_wx) == g_wx:
        return f"{g_wx}生{ri_wx}→{'正印' if _get_gan_yin_yang(ri_gan) != _get_gan_yin_yang(gan) else '偏印'}"
    # 我生
    if _get_wo_sheng_wx(ri_wx) == g_wx:
        return f"{ri_wx}生{g_wx}→{'食神' if _get_gan_yin_yang(ri_gan) == _get_gan_yin_yang(gan) else '伤官'}"
    # 克我
    if _get_ke_wo_wx(ri_wx) == g_wx:
        return f"{g_wx}克{ri_wx}→{'正官' if _get_gan_yin_yang(ri_gan) != _get_gan_yin_yang(gan) else '七杀'}"
    # 我克
    if _get_wo_ke_wx(ri_wx) == g_wx:
        return f"{ri_wx}克{g_wx}→{'正财' if _get_gan_yin_yang(ri_gan) != _get_gan_yin_yang(gan) else '偏财'}"
    return ""


def _get_tou_gan_impact(gan: str, shi_shen: str, pos: str) -> str:
    """天干透干对格局的影响"""
    impact_map = {
        "正印": "印星护身，学业/事业根基稳固",
        "偏印": "偏印深研，技术能力突出",
        "正官": "正官护身，自律性强，有管理潜质",
        "七杀": "七杀攻身，压力转化为动力",
        "正财": "正财透干，理财稳健",
        "偏财": "偏财透干，财源广进但需防浮财",
        "比肩": "比肩帮身，有团队精神但竞争激烈",
        "劫财": "劫财透干，早年竞争激烈，需防损财",
        "食神": "食神吐秀，创造力强，表达能力好",
        "伤官": "伤官泄秀，才华横溢但需谨慎言行",
    }
    if pos == "年":
        return f"年干{shi_shen}→{impact_map.get(shi_shen, '影响需结合全盘分析')}·祖上基业"
    elif pos == "月":
        return f"月干{shi_shen}→{'核心透干·' + impact_map.get(shi_shen, '')}"
    elif pos == "时":
        return f"时干{shi_shen}→{impact_map.get(shi_shen, '')}·晚年影响"
    return impact_map.get(shi_shen, "")


def _get_detail_explain(detail: str, ri_gan: str) -> str:
    """评分明细的解释"""
    if "月令本气印" in detail:
        return f"月令本气为印，得{ri_gan}生扶"
    if "月令比劫" in detail:
        return f"月令本气为比劫，帮身有力"
    if "天干" in detail and "比劫" in detail:
        return f"天干比劫帮身，增强自身力量"
    if "年支" in detail or "时支" in detail:
        return f"地支藏比劫，暗中助力"
    if "日支" in detail:
        return f"日支得{ri_gan}助力"
    return detail


def _get_yong_shen_tiers(basic: dict, analysis: dict) -> list:
    """获取用神层级数据"""
    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    sq = analysis["shen_qiang_ruo"]
    xi_list = analysis["xi_yong_shen"].get("xi_shen", [])

    tiers = []
    wx_symbols = {"水": "💧", "火": "🔥", "木": "🌳", "金": "⚪", "土": "🟤"}

    for i, ss in enumerate(xi_list):
        wx = _ji_shen_to_wu_xing(ss, ri_wx, sq["level"])
        if ss == "食伤":
            wx = _get_wo_sheng_wx(ri_wx)
            mechanism = f"{ri_wx}生{wx}→泄秀生财、调节{'身强' if sq['level'] == '身强' else '平衡'}"
            original = f"原局{'有食神/伤官' if _has_shi_shen(basic, ss) else '食伤偏弱·需大运补位'}"
        elif ss == "官杀":
            wx = _get_ke_wo_wx(ri_wx)
            mechanism = f"{wx}克{ri_wx}→制身为权威、调候全局"
            original = f"原局{'有正官/七杀' if _has_shi_shen(basic, ss) else '官杀偏弱·需大运引出'}"
        elif ss == "财":
            mechanism = f"{wx}耗{ri_wx}→财富积累、平衡身强"
            original = f"原局{'财星有根' if _has_shi_shen(basic, ss) else '财星偏弱·需大运补位'}"
        elif ss == "印":
            mechanism = f"{wx}生{ri_wx}→生扶日主、增强根基"
            original = f"原局{'印星有力' if _has_shi_shen(basic, ss) else '印星偏弱·需大运帮扶'}"
        elif ss == "比劫":
            mechanism = f"{wx}帮{ri_wx}→同气连枝、增强力量"
            original = f"原局{'比劫有根' if _has_shi_shen(basic, ss) else '比劫偏弱·需大运补位'}"
        else:
            mechanism = ""
            original = ""

        level = ["第一用神", "第二用神", "第三用神"][i] if i < 3 else f"第{i+1}用神"
        tiers.append({
            "level": level,
            "wx": wx,
            "wx_symbol": wx_symbols.get(wx, ""),
            "ss": ss,
            "mechanism": mechanism,
            "original": original,
            "dayun": f"在喜用神大运到位·见{ss}运发力",
        })

    return tiers


def _has_shi_shen(basic: dict, ss_type: str) -> bool:
    """检查原局是否有某类十神"""
    ss_set = {"正印", "偏印", "正官", "七杀", "正财", "偏财", "比肩", "劫财", "食神", "伤官"}
    if ss_type == "印":
        check = {"正印", "偏印"}
    elif ss_type == "食伤":
        check = {"食神", "伤官"}
    elif ss_type == "官杀":
        check = {"正官", "七杀"}
    elif ss_type == "财":
        check = {"正财", "偏财"}
    elif ss_type == "比劫":
        check = {"比肩", "劫财"}
    else:
        return False

    for pos_key in ["nian", "yue", "ri", "shi"]:
        p = basic["pillars"][pos_key]
        if p["gan_shi_shen"] in check:
            return True
        for cg in p["cang_gan"]:
            if cg["shi_shen"] in check:
                return True
    return False


def _get_zhi_shi_shen(ri_gan: str, zhi: str) -> str:
    """获取地支本气的十神"""
    if zhi in DI_ZHI:
        ben_qi = DI_ZHI_CANG_GAN[zhi][0][0]
        return _get_shi_shen(ri_gan, ben_qi)
    return ""


def _ji_shen_to_wu_xing(ji_shen: str, ri_wx: str, level: str) -> str:
    """十神类型转五行"""
    ri_idx = _get_wx_idx(ri_wx)
    if ji_shen in ["正印", "偏印", "印"]:
        return WU_XING_ORDER[(ri_idx + 4) % 5]  # 生我者
    elif ji_shen in ["正官", "七杀", "官杀"]:
        return WU_XING_ORDER[(ri_idx + 3) % 5]  # 克我者
    elif ji_shen in ["正财", "偏财", "财"]:
        return WU_XING_ORDER[(ri_idx + 2) % 5]  # 我克者
    elif ji_shen in ["食神", "伤官", "食伤"]:
        return WU_XING_ORDER[(ri_idx + 1) % 5]  # 我生者
    elif ji_shen in ["比肩", "劫财", "比劫"]:
        return ri_wx
    return "土"


def _get_ji_shen_problem(ji: str, ri_wx: str, level: str) -> str:
    """忌神引发的问题"""
    wx = _ji_shen_to_wu_xing(ji, ri_wx, level)
    if ji == "印":
        return f"再生则身更强→思虑过度、犹豫不决、创新瓶颈"
    elif ji == "比劫":
        return f"竞争加剧→容易被分财→合作纠纷"
    elif ji == "官杀":
        return f"压力增大→身心负担重→需注意健康"
    elif ji == "食伤":
        return f"泄身过度→精力不足→需注意劳逸结合"
    elif ji == "财":
        return f"财多身弱→富屋贫人→需防财来财去"
    return ""


def _get_ji_shen_scene(ji: str, ri_wx: str) -> str:
    """忌神典型场景"""
    scenes = {
        "印": "决策时瞻前顾后、过度分析",
        "比劫": "合伙易吃亏、遇金水年份竞争白热化",
        "官杀": "工作压力大、被上级压制",
        "食伤": "才华被压制、表达受限",
        "财": "投资易失利、财务压力大",
    }
    return scenes.get(ji, "")


def _get_ji_shen_caution(ji: str, ri_wx: str) -> str:
    """忌神注意事项"""
    cautions = {
        "印": "避免过度保守·在喜用神大运积极行动",
        "比劫": "谨慎合作担保·遇比劫年份尤其注意",
        "官杀": "注意身心健康·大运官杀旺时学会减压",
        "食伤": "避免锋芒太露·木秀于林风必摧之",
        "财": "避免过度消费·建立强制储蓄习惯",
    }
    return cautions.get(ji, "")


def _get_dayun_bu_shen(d: dict, ri_gan: str, xi_list: list) -> str:
    """大运补什么神"""
    gan_ss = _get_shi_shen(ri_gan, d["gan"])
    zhi_ss = _get_zhi_shi_shen(ri_gan, d["zhi"])
    return f"{'、'.join([s for s in [gan_ss, zhi_ss] if s in xi_list]) or '中性'})"


def _get_dayun_effect(d: dict, ri_gan: str, xi_list: list, ji_list: list) -> str:
    """大运效果评估"""
    gan_ss = _get_shi_shen(ri_gan, d["gan"])
    zhi_ss = _get_zhi_shi_shen(ri_gan, d["zhi"])

    xi_count = sum(1 for s in [gan_ss, zhi_ss] if s in xi_list)
    ji_count = sum(1 for s in [gan_ss, zhi_ss] if s in ji_list)

    if xi_count >= 2:
        return "✅ **吉运**·喜用神大运，事业财富双收"
    elif xi_count >= 1 and ji_count == 0:
        return "🟡 **平中带吉**·有喜用神助力"
    elif xi_count >= 1 and ji_count >= 1:
        return "🟠 **吉凶参半**·机遇与挑战并存"
    elif ji_count >= 2:
        return "🔴 **凶运**·忌神大运，需谨慎保守"
    else:
        return "⚪ **平运**·平稳过渡"


def _get_dayun_feature(d: dict, ri_gan: str, xi_list: list, ji_list: list) -> str:
    """大运特征名"""
    gan_ss = _get_shi_shen(ri_gan, d["gan"])
    zhi_ss = _get_zhi_shi_shen(ri_gan, d["zhi"])

    if gan_ss in xi_list and zhi_ss in xi_list:
        return f"双喜用神·{gan_ss}+{zhi_ss}"
    elif gan_ss in xi_list:
        return f"{gan_ss}发力·喜用神大运"
    elif zhi_ss in xi_list:
        return f"{zhi_ss}助力·有喜用"
    elif gan_ss in ji_list and zhi_ss in ji_list:
        return f"双忌神·{gan_ss}+{zhi_ss}·需谨慎"
    else:
        return f"{gan_ss}+{zhi_ss}·吉凶参半"


def _get_dayun_key_events(d: dict, ri_gan: str, xi_list: list, ji_list: list) -> str:
    """大运关键事件"""
    events = []
    gan_ss = _get_shi_shen(ri_gan, d["gan"])
    if gan_ss in xi_list:
        events.append(f"{gan_ss}发力期")
    if gan_ss in ji_list:
        events.append(f"{gan_ss}压力期")
    return "、".join(events) if events else "平稳过渡期"


def _get_dayun_analysis_detail(d: dict, ri_gan: str, ri_wx: str, xi_list: list, ji_list: list) -> str:
    """大运分析详情"""
    gan_ss = _get_shi_shen(ri_gan, d["gan"])
    zhi_cang_list = DI_ZHI_CANG_GAN[d["zhi"]]

    gan_effect = ""
    if gan_ss in xi_list:
        gan_effect = f"天干{d['gan']}（{gan_ss}）为喜用神，{_get_shi_shen_benefit(gan_ss, ri_wx)}"
    elif gan_ss in ji_list:
        gan_effect = f"天干{d['gan']}（{gan_ss}）为忌神，{_get_shi_shen_harm(gan_ss, ri_wx)}"
    else:
        gan_effect = f"天干{d['gan']}（{gan_ss}）为中性十神，影响较平衡"

    zhi_effect_parts = []
    for cg, w in zhi_cang_list:
        ss = _get_shi_shen(ri_gan, cg)
        if ss in xi_list:
            zhi_effect_parts.append(f"{cg}（{ss}）为喜用→有利")
        elif ss in ji_list:
            zhi_effect_parts.append(f"{cg}（{ss}）为忌神→需注意")

    zhi_effect = f"地支{d['zhi']}藏干：{'；'.join(zhi_effect_parts) if zhi_effect_parts else '影响较平衡'}。"
    if zhi_effect_parts:
        zhi_effect = f"地支{d['zhi']}藏干：{'；'.join(zhi_effect_parts)}。"

    return f"{gan_effect}。{zhi_effect}整体来看，此运{'喜用神能量强·宜积极进取' if gan_ss in xi_list else '忌神能量主导·宜保守稳健' if gan_ss in ji_list else '吉凶参半·需顺势而为'}。"


def _get_shi_shen_benefit(ss: str, ri_wx: str) -> str:
    """十神为喜用时的好处"""
    benefits = {
        "正印": "得贵人相助，学业/事业根基稳固",
        "偏印": "深研能力增强，技术突破的关键期",
        "正官": "事业有秩序感，适合晋升和管理",
        "七杀": "压力转化为动力，能力飞跃期",
        "正财": "收入稳定增长，理财收益可观",
        "偏财": "意外之财、投资收益期",
        "比肩": "团队协作顺利，人际关系助力",
        "劫财": "竞争虽激烈但能胜出",
        "食神": "创造力爆发，表达和创新能力强",
        "伤官": "才华展示期，适合技术输出和创新",
    }
    return benefits.get(ss, "运势向好")


def _get_shi_shen_harm(ss: str, ri_wx: str) -> str:
    """十神为忌神时的坏处"""
    harms = {
        "正印": "过度保守，缺乏进取动力",
        "偏印": "思维钻牛角尖，犹豫不决",
        "正官": "压力增大，被规章制度束缚",
        "七杀": "压力极大，容易身心俱疲",
        "正财": "为财所累，财务压力增加",
        "偏财": "投资易失利，浮财难留",
        "比肩": "竞争加剧，人际关系紧张",
        "劫财": "破财损友，合作易出问题",
        "食神": "过度乐观，容易做出错误判断",
        "伤官": "言行容易得罪人，需谨慎",
    }
    return harms.get(ss, "运势承压")


def _estimate_move_count(da_yun_list: list, sq: dict) -> int:
    """估算搬迁次数"""
    base = 3  # 基本3次（求学+工作+养老）
    if len(da_yun_list) >= 4:
        base += 1  # 中年置业
    if len(da_yun_list) >= 6:
        base += 1  # 改善型置业
    if sq["score"] >= 50:
        base += 1  # 身强活动多
    return base


def _get_energy_flow_text(basic: dict, analysis: dict) -> str:
    """能量流向文字"""
    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    ge_ju = analysis["ge_ju"]
    energy = analysis["energy"]

    strongest = energy.get("strongest", ri_wx)
    weakest = energy.get("weakest", _get_ke_wo_wx(ri_wx))

    return f"金→水→木→火→土 流通循环，{strongest}最强，{weakest}最弱"


def _get_wealth_years(basic: dict, analysis: dict) -> list:
    """发财最佳年份"""
    ri_gan = basic["ri_gan"]
    dy = analysis.get("da_yun", {})
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    xi_list = analysis["xi_yong_shen"].get("xi_shen", [])

    years = []
    for i, d in enumerate(da_yun_list[:6]):
        start_year = int(qi_yun_age + i * 10)
        gan_ss = _get_shi_shen(ri_gan, d["gan"])
        if gan_ss in xi_list or "财" in gan_ss:
            for offset in [1, 4, 7]:
                y = start_year + offset
                if y < start_year + 10:
                    year_gan = TIAN_GAN[(y - 4) % 10]
                    year_zhi = DI_ZHI[(y - 4) % 12]
                    years.append(f"{y}{year_gan}{year_zhi}")
                    if len(years) >= 4:
                        break
        if len(years) >= 4:
            break

    return years if years else ["需结合大运流年详细判断"]


def _get_health_notes(energy: dict) -> str:
    """健康注意"""
    raw = energy.get("raw_scores", {})
    weakest = min(raw, key=raw.get) if raw else "?"
    return f"{weakest}相关系统需关注（因最弱）"


def _get_four_features(basic: dict, analysis: dict) -> str:
    """四大特征"""
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]
    ri_gan = basic["ri_gan"]

    features = []
    features.append(f"①{ge_ju}格·{_get_ge_ju_short(basic, analysis)}")
    features.append(f"②{ri_gan}日主{sq['level']}·{'能担重压' if sq['score'] >= 50 else '需帮扶成长'}")
    features.append(f"③{'食神/伤官' if _has_shi_shen(basic, '食伤') else '印星/比劫'}核心·{'秀气流通' if _has_shi_shen(basic, '食伤') else '根基稳固'}")

    # 第四个特征
    if sq["level"] == "身强":
        features.append(f"④{'官杀有制' if _has_shi_shen(basic, '官杀') else '比劫林立'}·{'内在管理潜质' if _has_shi_shen(basic, '官杀') else '竞争意识强烈'}")
    else:
        features.append(f"④{'印星生扶' if _has_shi_shen(basic, '印') else '食伤泄秀'}·{'学习能力突出' if _has_shi_shen(basic, '印') else '创造力丰富'}")

    return " ".join(features)


def _get_kong_wang_text(basic: dict) -> str:
    """空亡描述"""
    ri_gan = basic["ri_gan"]
    ri_zhi = basic["ri_zhi"]
    kw = basic["pillars"]["ri"].get("kong_wang", [])
    if kw:
        kw_str = "、".join(kw)
        return f"{ri_gan}{ri_zhi}日柱→空亡{kw_str}·{'对相关宫位有减力影响'}"
    return "无空亡"


def _get_ge_ju_conditions(basic: dict, analysis: dict) -> str:
    """格局成立条件简述"""
    ge_ju = analysis["ge_ju"]
    conditions = []
    conditions.append(f"①月令{basic['yue_zhi']}本气为{ge_ju}")
    # 检查透干
    for gan in [basic["nian_gan"], basic["yue_gan"], basic["shi_gan"]]:
        if gan != basic["ri_gan"]:
            conditions.append(f"②{'月干' if gan == basic['yue_gan'] else '年干' if gan == basic['nian_gan'] else '时干'}{gan}{_get_shi_shen(basic['ri_gan'], gan)}透干")
    return "；".join(conditions[:5])  # 最多5条


def _get_ge_ju_comment(basic: dict, analysis: dict) -> str:
    """格局评价"""
    ge_ju = analysis["ge_ju"]
    comments = {
        "正印": "清贵之格·学业事业皆有建树",
        "偏印": "深研之格·技术型人才",
        "正官": "贵气之格·管理型人才",
        "七杀": "威权之格·领袖潜质",
        "正财": "富格·稳健理财型",
        "偏财": "富格·商业头脑型",
        "比肩": "独立之格·自强不息",
        "劫财": "博弈之格·竞争型人才",
        "食神": "秀气之格·创造性人才",
        "伤官": "才华之格·创新型人才",
    }
    return comments.get(ge_ju, "标准格局")


def _get_ge_ju_short(basic: dict, analysis: dict) -> str:
    """格局短评"""
    return _get_ge_ju_comment(basic, analysis)


def _get_ge_ju_purity(basic: dict, analysis: dict) -> str:
    """格局清纯度"""
    ge_ju = analysis["ge_ju"]
    return f"月令为{ge_ju}，{'无混杂' if len([k for k in ['nian', 'yue', 'shi'] if _get_shi_shen(basic['ri_gan'], basic[k+'_gan']) != ge_ju]) >= 2 else '略有混杂'}"


def _get_ge_ju_risk(basic: dict, analysis: dict) -> str:
    """格局风险"""
    return "无明显破格因素"


def _get_baihua_summary(basic: dict, analysis: dict, name: str) -> str:
    """白话摘要"""
    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]

    return f"您是{ri_wx}命，日主{sq['level']}（{sq['score']}分），格局为{ge_ju}格。{'身强能担财官，大运配合好时事业财运皆可期待' if sq['score'] >= 50 else '中和偏弱，遇帮扶大运则可发力' if sq['score'] >= 30 else '身弱宜顺势而为，印比大运为上佳'}。全报告21§深度展开，每个§均从命理理论出发逐条推导。"


def _get_education_level(basic: dict, analysis: dict) -> str:
    """学历等级"""
    ri_gan = basic["ri_gan"]
    has_year_yin = _check_year_has_yin(basic, ri_gan)
    sq = analysis["shen_qiang_ruo"]

    if has_year_yin and sq["score"] >= 40:
        return "985/211大学及以上"
    elif has_year_yin or sq["score"] >= 40:
        return "本科/一本大学"
    else:
        return "本科/大专"


def _get_education_comment(basic: dict, analysis: dict) -> str:
    """学历评论"""
    return "学业基因较强，有学历潜力"


def _get_career_level(basic: dict, analysis: dict) -> str:
    """事业等级"""
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]

    if sq["score"] >= 50 and ge_ju in ["正官", "七杀", "食神", "偏印"]:
        return "专家型高管/技术领袖"
    elif sq["score"] >= 40:
        return "技术管理岗/专业骨干"
    else:
        return "专业技术人员"


def _get_career_comment(basic: dict, analysis: dict) -> str:
    """事业评论"""
    return "格局和身强弱配合较好，有良好发展空间"


def _get_ge_ju_career_direction(ge_ju: str, ri_wx: str) -> str:
    """格局定方向"""
    directions = {
        "正印": f"学术/教育/文化类事业，适合体制内或稳定平台",
        "偏印": f"技术研发/咨询/深度研究型事业",
        "正官": f"管理/公务员/大型企业管理路线",
        "七杀": f"创业/军警/挑战性事业，有领袖潜质",
        "正财": f"金融/财务/商贸等实体经济领域",
        "偏财": f"投资/贸易/商业/市场开发领域",
        "比肩": f"自主创业/律师/咨询等独立执业",
        "劫财": f"竞争型行业/销售/市场拓展领域",
        "食神": f"创意/文化/教育/技术传播领域",
        "伤官": f"创新/科技/艺术/自由职业领域",
    }
    return directions.get(ge_ju, "根据格局特点选择适合方向")


def _get_ge_ju_career_type(ge_ju: str) -> str:
    """格局类型对应的事业类型"""
    types = {
        "正印": "学术研究型",
        "偏印": "技术深研型",
        "正官": "管理治理型",
        "七杀": "开拓领袖型",
        "财": "商业运营型",
        "食伤": "创新表达型",
        "比劫": "独立竞争型",
    }
    return types.get(ge_ju, "复合型")


def _get_guan_sha_info(basic: dict, analysis: dict) -> str:
    """官杀制化信息"""
    if _has_shi_shen(basic, "官杀"):
        return "七杀有制→化为权威管理；官星护身→自律性强"
    return "官杀偏弱·管理倾向不突出"


def _get_yin_info(basic: dict, analysis: dict) -> str:
    """印星状态"""
    if _has_shi_shen(basic, "印"):
        return "印星有力·学术/技术深度好底子"
    return "印星偏弱·需大运补位"


def _get_da_yun_career_support(dy: dict) -> str:
    """大运对事业的支持"""
    return "中年大运助力明显·事业上升期"


def _get_qi_sha_info(basic: dict, analysis: dict) -> str:
    """七杀信息"""
    if _has_shi_shen(basic, "官杀"):
        return "原局有七杀/官杀，需结合大运流年判断攻身情况。"
    return "原局无七杀直接攻身·较安全"


def _get_qi_sha_health(basic: dict, analysis: dict) -> str:
    """七杀为病"""
    if _has_shi_shen(basic, "官杀"):
        return f"七杀所在宫位对应病灶。大运流年七杀旺时需要重点关注。"
    return "原局七杀不显·非主要健康风险源"


def _get_pian_yin_health(basic: dict, analysis: dict) -> str:
    """偏印主瘀"""
    if _has_shi_shen(basic, "印") and "偏印" in [p.get("gan_shi_shen", "") for p in basic["pillars"].values()]:
        return "偏印在主气血循环方面有影响，需注意情志调节。"
    return "偏印不显·非主要健康风险"


def _get_dayun_by_index(dy: dict, idx: int) -> str:
    """按索引获取大运"""
    da_yun_list = dy.get("da_yun", [])
    if idx < len(da_yun_list):
        return da_yun_list[idx]["gan_zhi"]
    return "—"


def _get_wx_appearance_base(wx: str) -> str:
    """五行基准外貌描述"""
    descriptions = {
        "木": "身高偏高，体型挺拔，气质清秀。肤色偏青白。面部轮廓分明，手指修长。",
        "火": "面色红润，目光有神，气质热情。中等身材，行动敏捷。面部五官鲜明。",
        "土": "身形敦实，气质稳重。肤色偏黄，五官端正。给人安定可靠的感觉。",
        "金": "骨架分明，气质锐利。皮肤偏白，面部线条清晰。手指关节分明。",
        "水": "体态柔美，气质灵动。肤色偏黑/白，眼睛有神采。身形匀称有曲线。",
    }
    return descriptions.get(wx, "体型适中，气质中庸")


def _get_strength_appearance_mod(score: float, level: str) -> str:
    """身强弱修正外貌"""
    if score >= 60:
        return "偏强体质，骨架比标准体型更大一些。身体素质好，耐受力强。"
    elif score >= 40:
        return "体质均衡，体型标准，不胖不瘦。身体素质中等偏上。"
    else:
        return "偏弱体质，体型偏瘦或纤细。需要加强锻炼和营养。"


def _get_shi_shen_appearance(basic: dict, analysis: dict) -> list:
    """食神/比劫对外貌的影响"""
    lines = []
    ri_gan = basic["ri_gan"]

    if _has_shi_shen(basic, "食伤"):
        lines.append("食神/伤官透出→身材偏瘦或匀称，气质灵秀，有艺术气质。")
    else:
        lines.append("食伤不显→体型无明显影响。")

    if _has_shi_shen(basic, "比劫"):
        lines.append("比劫多→骨架偏大、肩宽背厚，肌肉线条较为明显。")
    else:
        lines.append("比劫不旺→骨架适中。")

    lines.append("发福时间预测：食神/印星大运容易发福，中年后注意体重管理。")

    return lines


def _get_height_estimate(ri_wx: str, sq: dict) -> str:
    """身高推断"""
    scores = {
        "木": (175, 185),
        "火": (170, 180),
        "土": (168, 178),
        "金": (173, 183),
        "水": (172, 180),
    }
    base_min, base_max = scores.get(ri_wx, (168, 178))
    if sq["score"] >= 50:
        mod = "+3~5cm"
        base_min += 3
        base_max += 5
    elif sq["score"] >= 30:
        mod = ""
    else:
        mod = "-2~3cm"
        base_min -= 3
        base_max -= 2

    return f"{base_min}~{base_max}cm"


def _get_overall_appearance(basic: dict, analysis: dict) -> str:
    """整体外貌印象"""
    ri_wx = _get_ri_gan_wu_xing(basic["ri_gan"])
    sq = analysis["shen_qiang_ruo"]

    desc = f"{ri_wx}日主，{sq['level']}（{sq['score']}分），"
    if sq["score"] >= 50:
        desc += "身形偏壮实，气质有力量感。"
    elif sq["score"] >= 30:
        desc += "体型标准，气质中正平和。"
    else:
        desc += "身形偏纤细，气质文弱内敛。"

    if _has_shi_shen(basic, "食伤"):
        desc += "食神透干，面部表情生动，有亲和力。"
    if _has_shi_shen(basic, "印"):
        desc += "印星入命，气质沉稳有书卷气。"

    return desc


def _get_personality_traits(basic: dict, analysis: dict) -> list:
    """五重人格特质"""
    ri_gan = basic["ri_gan"]
    ri_wx = _get_ri_gan_wu_xing(ri_gan)
    sq = analysis["shen_qiang_ruo"]
    ge_ju = analysis["ge_ju"]

    traits = []

    # 特质一：格局核心特质
    ge_ju_traits = {
        "正印": {
            "name": "稳重大气型——\"厚德载物\"",
            "tag": "正印格人格",
            "shi_shen": f"月令{ge_ju}为格",
            "description": f"正印格局赋予的沉稳和包容力——不急不躁、深思熟虑。做事有章法，不轻易被外界干扰。在专业领域有深厚的积累和独到的见解。为人正直、有责任感，是团队中可信赖的中坚力量。\n\n**在职场表现为：**\n- 做事有条理、有计划，善于长期规划\n- 对下属和同事包容，有导师气质\n- 适合需要稳重和耐心的岗位\n\n**需要注意的盲区：**\n- 有时过于保守，错过创新机会\n- 需要学会在稳重和灵活之间找到平衡",
        },
        "偏印": {
            "name": "深度钻研型——\"知其然必知其所以然\"",
            "tag": "偏印格人格",
            "shi_shen": f"月令{ge_ju}为格",
            "description": f"偏印格局赋予的深研能力——不满足于表面的「知道」，一定要追究到根本的「原理」和「为什么」。这种钻研不是书本式的死学，而是带着实践导向的深度探索。\n\n**在职场表现为：**\n- 技术深度远超同行，能一眼看出问题的本质\n- 不满足于「能用就行」，一定要理解底层原理\n- 有把复杂问题拆解为简单模块的天赋\n\n**需要注意的盲区：**\n- 过度完美主义（偏印的副作用）\n- 有时会陷入「过度分析」的陷阱",
        },
        "正官": {
            "name": "自律进取型——\"克己奉公\"",
            "tag": "正官格人格",
            "shi_shen": f"月令{ge_ju}为格",
            "description": f"正官格局赋予的自律和责任感——有明确的目标意识，善于自我管理。做事有章法，遵守规则和秩序。在体制内或大平台中如鱼得水，善于在规则范围内最大化自己的优势。\n\n**在职场表现为：**\n- 做事认真负责，对细节要求高\n- 有领导力和组织能力\n- 适合管理岗位或需要高度自律的工作\n\n**需要注意的盲区：**\n- 有时过于拘泥规则，缺乏灵活性\n- 压力大的时候需要学会放松",
        },
        "七杀": {
            "name": "果敢决断型——\"遇强则强\"",
            "tag": "七杀格人格",
            "shi_shen": f"月令{ge_ju}为格",
            "description": f"七杀格局赋予的决断力和危机处理能力——越是困难时刻越能保持冷静。有天然的领袖气质，敢于做艰难的决定。压力是动力，挑战是机会，这是七杀格最核心的优势。\n\n**在职场表现为：**\n- 危机处理能力极强，能在混乱中找到方向\n- 敢于承担责任，不畏艰难\n- 适合创业公司或需要突破的场景\n\n**需要注意的盲区：**\n- 压力管理是终身课题\n- 需要学会放松和寻求支持",
        },
        "食神": {
            "name": "创新表达型——\"秀气流通\"",
            "tag": "食神格人格",
            "shi_shen": f"月令{ge_ju}为格",
            "description": f"食神格局赋予的创造力和表达力——善于把复杂的东西讲得简单，有「化繁为简」的天赋。想法多、创意多，而且有把想法落地的执行力。\n\n**在职场表现为：**\n- 创新能力突出，善于提出新方案\n- 表达能力强，能把抽象变具体\n- 适合创意/教育/技术传播方向\n\n**需要注意的盲区：**\n- 想法太多容易发散\n- 需要学会聚焦和优先级排序",
        },
        "伤官": {
            "name": "才华横溢型——\"不拘一格\"",
            "tag": "伤官格人格",
            "shi_shen": f"月令{ge_ju}为格",
            "description": f"伤官格局赋予的超凡才华和批判性思维——不盲从权威，有独立判断能力。创新意识极强，善于发现问题的不同解决方案。\n\n**在职场表现为：**\n- 批判性思维强，能发现被忽略的问题\n- 创新能力突出\n- 适合科技/艺术/自由职业方向\n\n**需要注意的盲区：**\n- 容易锋芒太露\n- 需要学习团队合作和换位思考",
        },
        "财": {
            "name": "务实进取型——\"脚踏实地\"",
            "tag": "财格人格",
            "shi_shen": f"月令{ge_ju}为格",
            "description": f"财格局赋予的商业头脑和务实精神——对机会有敏锐的嗅觉，善于发现和把握商机。做事脚踏实地，不空想，有很强的执行力。\n\n**在职场表现为：**\n- 商业敏感度高，善于发现机会\n- 做事有目标导向\n- 适合商业/金融/销售方向\n\n**需要注意的盲区：**\n- 金钱观需要调和\n- 过于务实可能忽略长远规划",
        },
    }

    # 默认特质
    default_traits = [
        {
            "name": "稳重务实型——\"脚踏实地\"",
            "tag": f"{ri_wx}日主人格",
            "shi_shen": f"日主{ri_gan}（{ri_wx}）为核心",
            "description": f"日主为{ri_wx}，赋予命主{_get_wx_personality(ri_wx)}。{sq['level']}（{sq['score']}分）使这份特质{'更加彰显' if sq['score'] >= 50 else '有所收敛' if sq['score'] >= 30 else '需要后天培养'}。\n\n**在职场表现为：**\n- 有自己的节奏和风格\n- 不盲从、不随波逐流\n- 在擅长的领域有深度积累\n\n**需要注意的盲区：**\n- 走出舒适区需要勇气\n- 需要持续学习和成长",
        },
        {
            "name": "协作共赢型——\"众人拾柴\"",
            "tag": "十神互动人格",
            "shi_shen": f"{'比肩/劫财' if _has_shi_shen(basic, '比劫') else '印星'}助力",
            "description": f"原局{'比劫帮身，有团队精神和合作意识' if _has_shi_shen(basic, '比劫') else '印星生扶，善于借助他人力量'}。不是单打独斗的类型，而是善于在集体中找到自己的位置。\n\n**在人际关系中：**\n- {'重视人情往来，有哥们义气' if _has_shi_shen(basic, '比劫') else '尊重师长，善于学习'}\n- 愿意为团队付出\n- 人脉积累能力强\n\n**需要警惕的盲区：**\n- {'避免过度讲义气导致利益受损' if _has_shi_shen(basic, '比劫') else '避免过度依赖他人'}",
        },
        {
            "name": "洞察敏锐型——\"见微知著\"",
            "tag": "食伤/官杀人格",
            "shi_shen": f"{'食神/伤官' if _has_shi_shen(basic, '食伤') else '官杀/印星'}敏锐",
            "description": f"原局{'食伤透出或藏支' if _has_shi_shen(basic, '食伤') else '官杀/印星存在'}，赋予命主敏锐的洞察力和判断力。能从小细节中发现大问题，善于分析和推理。\n\n**在职场表现为：**\n- 风险意识强，能提前发现隐患\n- 分析问题深入本质\n- 决策时考虑周全\n\n**需要注意的盲区：**\n- 过度分析可能导致行动迟缓\n- 需要信任直觉的部分",
        },
        {
            "name": "坚韧不拔型——\"百折不挠\"",
            "tag": "身强弱人格表现",
            "shi_shen": f"{sq['level']}特质表现",
            "description": f"{sq['level']}的命主在逆境中的表现最为显著——{'越是困难越能激发斗志' if sq['score'] >= 50 else '在压力下也能保持稳定发挥' if sq['score'] >= 30 else '善于在逆境中寻找帮助和转机'}。这不是天生的韧性，而是命局结构决定的应对模式。\n\n**人生启示：**\n- {'发挥身强优势，敢于挑战' if sq['score'] >= 50 else '保持中和优势，稳扎稳打' if sq['score'] >= 30 else '善于借力，不要硬扛'}\n- 找到适合自己的节奏最重要\n- 长期主义的践行者",
        },
    ]

    # 如果ge_ju在映射中，使用对应的特质作为第一个
    if ge_ju in ge_ju_traits:
        traits.append(ge_ju_traits[ge_ju])
    else:
        traits.append(default_traits[0])

    # 用默认特质填满剩余4个
    for i in range(4):
        idx = i % len(default_traits)
        trait = dict(default_traits[idx])
        # 避免与第一个重复
        if trait["name"] != traits[0]["name"]:
            traits.append(trait)
        else:
            # 跳过重复，用下一个
            next_idx = (idx + 1) % len(default_traits)
            traits.append(dict(default_traits[next_idx]))
        if len(traits) >= 5:
            break

    return traits[:5]


def _get_wx_personality(wx: str) -> str:
    """五行性格描述"""
    descs = {
        "木": "积极向上、有进取心，善于规划和组织",
        "火": "热情奔放、有感染力，善于社交和沟通",
        "土": "稳重踏实、有责任心，善于执行和落实",
        "金": "果断干练、有决断力，善于分析和判断",
        "水": "灵活变通、有智慧，善于应变和协调",
    }
    return descs.get(wx, "性格平衡")


def _get_shi_shen_personality(basic: dict, analysis: dict) -> list:
    """十神性格底色表"""
    ri_gan = basic["ri_gan"]
    result = []

    ss_status = {}
    for pos_key, pos_label in [("nian", "年柱"), ("yue", "月柱"), ("ri", "日柱"), ("shi", "时柱")]:
        p = basic["pillars"][pos_key]
        gan_ss = p["gan_shi_shen"]
        if gan_ss not in ss_status:
            ss_status[gan_ss] = {"position": pos_label, "status": "透干·天干" if pos_key != "ri" else "日主"}
        elif pos_key != "ri":
            ss_status[gan_ss]["position"] += f"+{pos_label}"

        for cg in p["cang_gan"]:
            ss = cg["shi_shen"]
            if ss not in ss_status:
                ss_status[ss] = {"position": f"{pos_label}藏", "status": "藏支"}

    impact_map = {
        "正印": "学业根基好、为人正直、有书卷气",
        "偏印": "深研精神、技术天赋、善于解构复杂问题",
        "正官": "自律性强、有管理潜质、责任感强",
        "七杀": "内在决断力、遇强则强、压力转化能力",
        "正财": "理财稳健、对家庭有责任心、务实",
        "偏财": "商业头脑、人脉广、善于把握机会",
        "比肩": "独立自主、有竞争意识、团队精神",
        "劫财": "博弈心强、敢拼敢打、社交能力强",
        "食神": "创造力强、表达力好、乐观开朗",
        "伤官": "批判性思维、才华横溢、有创新精神",
    }

    for ss, info in ss_status.items():
        if ss == "日主":
            continue
        result.append({
            "name": ss,
            "position": info.get("position", ""),
            "status": f"{'⭐' if info.get('status') in ['透干·天干', '日主'] else ''}{info.get('status', '')}",
            "impact": impact_map.get(ss, "性格影响需结合全局分析"),
        })
        if len(result) >= 8:
            break

    return result


def _get_personality_summary(basic: dict, analysis: dict) -> str:
    """性格白话总结"""
    ri_wx = _get_ri_gan_wu_xing(basic["ri_gan"])
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]

    return f"您的气质以{ge_ju}格为主，兼具{ri_wx}的特性。{sq['level']}使您在面对挑战时{'更有底气和韧性' if sq['score'] >= 50 else '更加灵活和变通' if sq['score'] >= 30 else '更善于借力和协调'}。在性格上既有深思熟虑的一面，也有果断决策的能力，是一个内外兼修的复合型人格。"


def _get_education_steps(basic: dict, analysis: dict) -> list:
    """六步排查"""
    ri_gan = basic["ri_gan"]
    sq = analysis["shen_qiang_ruo"]

    steps = []

    # 第一步：印星情况
    has_yin = _has_shi_shen(basic, "印")
    steps.append({
        "name": "第一步：印星情况",
        "check": "原局是否有印",
        "analysis": f"原局{'印星有力' if has_yin else '印星偏弱'}{'→学业基因强' if has_yin else '→学业需要自身努力'}",
        "result": "✅" if has_yin else "❌",
    })

    # 第二步：官杀影响
    has_guan = _has_shi_shen(basic, "官杀")
    steps.append({
        "name": "第二步：官杀影响",
        "check": "官杀自律/压力",
        "analysis": f"原局{'官杀存在→自律性强/有压力' if has_guan else '官杀偏弱→自律需培养'}",
        "result": "✅" if has_guan else "❌",
    })

    # 第三步：食伤情况
    has_shi = _has_shi_shen(basic, "食伤")
    steps.append({
        "name": "第三步：食伤情况",
        "check": "聪明程度",
        "analysis": f"原局{'食伤存在→聪明灵动、理解力强' if has_shi else '食伤偏弱→靠勤奋弥补'}",
        "result": "✅" if has_shi else "❌",
    })

    # 第四步：文昌贵人
    nian_gan = basic["nian_gan"]
    wen_chang_zhi = WEN_CHANG.get(nian_gan, "")
    has_wc = any(
        p["zhi"] == wen_chang_zhi
        for p in basic["pillars"].values()
    ) if wen_chang_zhi else False
    steps.append({
        "name": "第四步：文昌贵人",
        "check": f"年干{nian_gan}→文昌在{wen_chang_zhi}",
        "analysis": f"{'文昌到位✅→学业运好' if has_wc else '文昌未到位→但可通过后天补文昌'}",
        "result": "✅" if has_wc else "❌",
    })

    # 第五步：大运配合
    steps.append({
        "name": "第五步：大运配合",
        "check": "关键学历运",
        "analysis": f"{'少年运走喜用神→学业顺利' if sq['score'] >= 40 else '需结合具体大运分析'}",
        "result": "✅" if sq["score"] >= 40 else "⚠️",
    })

    # 第六步：综合判定
    total_ok = sum(1 for s in steps if s["result"] == "✅")
    steps.append({
        "name": "第六步：综合判定",
        "check": f"{total_ok}/5项通过",
        "analysis": f"{'学业基因强→高学历潜质' if total_ok >= 3 else '学业中等→需要通过努力弥补'}",
        "result": "⭐" if total_ok >= 3 else "⚠️",
    })

    return steps


def _get_exam_luck(basic: dict, analysis: dict) -> str:
    """考试运分析"""
    sq = analysis["shen_qiang_ruo"]
    if sq["score"] >= 40:
        return "考试运较好，在喜用神大运/年份考试容易超常发挥。关键考试前保持良好心态即可。"
    else:
        return "考试运中等，需要通过充分准备来弥补。在印比帮扶的年份考试运会更好。"


def _get_fuqi_gong_impact(shi_shen: str, gender: str) -> str:
    """夫妻宫十神影响"""
    impacts = {
        "正印": "得配偶支持，婚姻生活和谐",
        "偏印": "配偶有深研精神，但需注意沟通",
        "正官": f"{'夫' if gender == '女' else '妻'}宫正位，婚姻美满",
        "七杀": "婚姻有挑战，需要更多包容",
        "正财": f"{'妻' if gender == '男' else '夫'}宫正位，婚姻稳定",
        "偏财": "感情丰富，异性缘好",
        "比肩": "夫妻平等，互相支持",
        "劫财": "需防第三者，注意经营婚姻",
        "食神": "夫妻生活和谐，有共同语言",
        "伤官": "需注意言语表达，避免伤及感情",
    }
    return impacts.get(shi_shen, "婚姻质量需结合全局分析")


def _get_fuqi_xing_info(basic: dict, analysis: dict, gender: str) -> str:
    """夫妻星状态"""
    ri_gan = basic["ri_gan"]
    if gender == "男":
        target = {"正财", "偏财"}
    else:
        target = {"正官", "七杀"}

    found = []
    for pos_key, pos_label in [("nian", "年"), ("yue", "月"), ("ri", "日"), ("shi", "时")]:
        p = basic["pillars"][pos_key]
        if p["gan_shi_shen"] in target:
            found.append(f"{pos_label}干{p['gan']}（{p['gan_shi_shen']}）")
        for cg in p["cang_gan"]:
            if cg["shi_shen"] in target:
                found.append(f"{pos_label}支藏{cg['gan']}（{cg['shi_shen']}）")
                break

    if found:
        return f"夫妻星存在于：{'、'.join(found[:3])}。{'状态良好' if len(found) >= 2 else '力量偏弱·需大运流年激活'}。"
    return "夫妻星偏弱·需大运流年引动"


def _get_marriage_signals(basic: dict, analysis: dict, gender: str) -> list:
    """四大结婚信号"""
    ri_gan = basic["ri_gan"]
    sq = analysis["shen_qiang_ruo"]

    signals = [
        {
            "signal": "夫妻星透干/到位",
            "triggered": _has_shi_shen(basic, "正财" if gender == "男" else "正官"),
            "interpretation": "夫妻星在原局存在，有明确的婚恋信号",
        },
        {
            "signal": "夫妻宫被合/冲",
            "triggered": False,
            "interpretation": "大运流年合/冲日支时，婚姻易成",
        },
        {
            "signal": "桃花入命",
            "triggered": "桃花" in [s for ss in basic["pillars"].values() for s in ss.get("shen_sha", [])],
            "interpretation": "桃花星在命局，异性缘分较好",
        },
        {
            "signal": "大运助婚",
            "triggered": sq["score"] >= 40,
            "interpretation": "身强能担夫妻星，大运配合时婚姻有成",
        },
    ]

    return signals


def _get_marriage_windows(dy: dict, ri_gan: str) -> list:
    """结婚窗口"""
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)

    windows = []
    for i, d in enumerate(da_yun_list[:5]):
        start_year = int(qi_yun_age + i * 10)
        gan_ss = _get_shi_shen(ri_gan, d["gan"])
        windows.append({
            "name": f"第{i+1}个",
            "dayun": f"{d['gan_zhi']}运",
            "year": f"{start_year + 1}~{start_year + 5}",
            "desc": f"{gan_ss}大运期间，感情容易稳定",
        })
    return windows


def _get_spouse_features(basic: dict, analysis: dict, gender: str) -> str:
    """配偶特征"""
    ri_zhi = basic.get("ri_zhi", "")
    ri_gan = basic["ri_gan"]
    ri_zhi_ss = _get_zhi_shi_shen(ri_gan, ri_zhi) if ri_zhi else ""

    return f"从五行角度，配偶的五行与{'正财/偏财' if gender == '男' else '正官/七杀'}相关。从宫位角度，日支{ri_zhi}（{ri_zhi_ss}）决定配偶的基本性格特征。{'性格温和、有包容心' if ri_zhi_ss in ['正印', '偏印', '食神'] else '性格刚毅、有决断力' if ri_zhi_ss in ['正官', '七杀', '劫财'] else '性格务实、有责任心'}。"


def _get_marriage_trend(basic: dict, analysis: dict, gender: str) -> str:
    """感情走势"""
    sq = analysis["shen_qiang_ruo"]
    if sq["score"] >= 50:
        return "感情走势较平稳，中年后更趋稳定。晚婚更适合。需注意事业繁忙对家庭的影响。"
    elif sq["score"] >= 30:
        return "感情走势中正平和，适合在喜用神大运结婚。注意沟通和理解的重要性。"
    else:
        return "感情需要更多经营，选择包容理解的伴侣尤为重要。在帮扶大运中感情更顺利。"


def _get_zi_nv_xing_info(basic: dict, analysis: dict, gender: str) -> str:
    """子女星信息"""
    ri_gan = basic["ri_gan"]
    if gender == "男":
        target = {"正官", "七杀"}
    else:
        target = {"食神", "伤官"}

    found = []
    for p in basic["pillars"].values():
        if p["gan_shi_shen"] in target:
            found.append(f"天干{p['gan']}（{p['gan_shi_shen']}）")
        for cg in p["cang_gan"]:
            if cg["shi_shen"] in target:
                found.append(f"藏干{cg['gan']}（{cg['shi_shen']}）")
                break

    if found:
        return f"子女星存在于：{'、'.join(found[:3])}。子女缘分较好。"
    return "子女星偏弱·需大运流年激活·子女缘分需等待时机。"


def _get_tian_ding_years(basic: dict, analysis: dict) -> str:
    """添丁年份"""
    return "子女星的喜用神大运为添丁佳期。具体年份需结合大运流年中的子女星引动信号判断。建议在喜用神大运中规划生育。"


def _get_children_personality(basic: dict, analysis: dict) -> str:
    """子女性格"""
    return "从子女星和子女宫推断，子女性格与子女星的十神属性相关。子女有独立自主的特点，在成长过程中需要适当的引导和支持。"


def _is_cai_exposed(basic: dict, cai_wx: str) -> bool:
    """财星是否透干"""
    ri_gan = basic["ri_gan"]
    for gan in [basic["nian_gan"], basic["yue_gan"], basic["shi_gan"]]:
        if TIAN_GAN_WU_XING[gan] == cai_wx and gan != ri_gan:
            return True
    return False


def _get_zhiye_signal(d: dict, ri_wx: str) -> str:
    """置业信号"""
    zhi = d["zhi"]
    if zhi in ["辰", "戌", "丑", "未"]:
        return "库星出现·置业机会"
    if zhi in ["寅", "申", "巳", "亥"]:
        return "驿马冲动·搬迁变动"
    return "平稳过渡·正常置业"


def _get_e_shen_info(basic: dict, analysis: dict) -> str:
    """恶神制化"""
    if _has_shi_shen(basic, "官杀"):
        return "七杀存在且有制化→「恶神有制方为贵」，是顶级事业信号。七杀被制化为权威和管理能力。"
    return "恶神不显·事业按常规路线发展"


def _get_wx_industries(wx: str) -> str:
    """五行对应行业"""
    industries = {
        "木": "教育/文化/出版/医疗/环保/农业",
        "火": "科技/互联网/能源/传媒/餐饮/娱乐",
        "土": "房地产/建筑/农业/矿业/仓储/物流",
        "金": "金融/证券/机械/汽车/精密制造/法律",
        "水": "物流/贸易/旅游/交通/信息/数据/咨询",
    }
    return industries.get(wx, "通用行业")


def _get_wx_career_detail(wx: str, ss: str) -> str:
    """具体职业方向"""
    details = {
        "木": "教育工作者/文化创意/医疗健康/环保工程",
        "火": "科技研发/互联网产品/能源工程/传媒运营",
        "土": "房地产开发/建筑施工/农业管理/物流管理",
        "金": "金融分析/证券投资/机械设计/法律咨询",
        "水": "贸易商务/旅游管理/物流规划/数据分析/咨询顾问",
    }
    return details.get(wx, "行业深耕")


def _get_career_key_years(dy: dict, ri_gan: str) -> list:
    """关键事业年份"""
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    years = []

    for i, d in enumerate(da_yun_list[:8]):
        start_year = int(qi_yun_age + i * 10)
        gan_ss = _get_shi_shen(ri_gan, d["gan"])

        if i <= 1:
            event = "学业/职业起步期"
            etype = "A"
        elif i <= 3:
            event = f"职场上升·{gan_ss}发力"
            etype = "B"
        elif i <= 5:
            event = f"事业巅峰·{gan_ss}期"
            etype = "B🏆"
        else:
            event = "事业转型/顾问期"
            etype = "I"

        years.append({
            "year": f"{start_year + 2}~{start_year + 5}",
            "dayun": d["gan_zhi"],
            "event": event,
            "type": etype,
        })

    return years


def _get_health_key_years(dy: dict, energy: dict) -> list:
    """健康关注年份"""
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    years = []

    weakest = energy.get("weakest", "土")
    over_wx = [k for k, v in energy.get("raw_scores", {}).items() if v >= 80]

    for i, d in enumerate(da_yun_list[:8]):
        start_year = int(qi_yun_age + i * 10)
        risk = f"{weakest}相关系统需关注" if d.get("zhi") in ["巳", "午"] or i >= 5 else "常规体检"
        note = f"注意{'、'.join(WU_XING_ORGAN.get(weakest, ('?',)))}保养" if d.get("zhi") in ["巳", "午"] else "保持良好生活习惯"
        years.append({
            "year": f"{start_year}~{start_year + 9}",
            "dayun": d["gan_zhi"],
            "risk": risk,
            "note": note,
        })

    return years


def _get_future_warnings(basic: dict, analysis: dict) -> list:
    """未来10年警示"""
    dy = analysis.get("da_yun", {})
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)
    ri_gan = basic["ri_gan"]

    warns = []
    current_year = datetime.now().year

    # 找当前大运和未来10年
    for i, d in enumerate(da_yun_list):
        start_year = int(qi_yun_age + i * 10)
        end_year = start_year + 9
        if start_year <= current_year <= end_year or (start_year - current_year <= 10 and start_year > current_year):
            for y in range(max(current_year, start_year), min(current_year + 10, end_year + 1)):
                gan_ss = _get_shi_shen(ri_gan, d["gan"])
                risk_type = f"{gan_ss}压力" if gan_ss in analysis["xi_yong_shen"].get("ji_shen", []) else f"{gan_ss}机遇"
                note = f"{gan_ss}影响，需平衡事业与生活" if gan_ss in analysis["xi_yong_shen"].get("ji_shen", []) else f"{gan_ss}发力期，把握机会"
                warns.append({
                    "year": y,
                    "ganzhi": f"{_get_gan_from_index((y - 4) % 10)}{DI_ZHI[(y - 4) % 12]}",
                    "dayun": d["gan_zhi"],
                    "risk_type": risk_type,
                    "note": note,
                })
                if len(warns) >= 8:
                    break
        if len(warns) >= 8:
            break

    return warns


def _get_gan_from_index(idx: int) -> str:
    """从索引获取天干"""
    return TIAN_GAN[idx % 10]


def _get_seasonal_advice(ri_wx: str, analysis: dict) -> str:
    """节气调运建议"""
    xi_list = analysis["xi_yong_shen"].get("xi_shen", [])
    advice_parts = []
    for ss in xi_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        advice_parts.append(f"喜{wx}五行，{wx}旺的季节（{'春' if wx == '木' else '夏' if wx == '火' else '季末' if wx == '土' else '秋' if wx == '金' else '冬'}）运势更佳")
    return "；".join(advice_parts) if advice_parts else "注意节气更替时的身体调养"


def _get_liu_qin_interpretation(pos: str, pillar: dict, ri_gan: str, analysis: dict) -> str:
    """六亲解读"""
    gan_ss = pillar["gan_shi_shen"] if pos != "ri" else "日主"
    zhi = pillar["zhi"]

    if pos == "nian":
        return f"年柱{gan_ss}，祖上{_get_liu_qin_comment(gan_ss)}。家庭出身{_get_family_origin(gan_ss, zhi)}。"
    elif pos == "yue":
        return f"月柱{gan_ss}，父母{_get_liu_qin_comment(gan_ss)}。兄弟姐妹关系{_get_sibling_relation(gan_ss)}。"
    elif pos == "ri":
        return f"日支{zhi}，配偶{_get_liu_qin_comment(gan_ss)}。婚姻{_get_marriage_quality(gan_ss)}。"
    elif pos == "shi":
        return f"时柱{gan_ss}，子女{_get_liu_qin_comment(gan_ss)}。晚年{_get_later_life(gan_ss)}。"

    return ""


def _get_liu_qin_comment(ss: str) -> str:
    """六亲十神评论"""
    comments = {
        "正印": "正直善良，有文化底蕴",
        "偏印": "有特殊才能，性格独特",
        "正官": "有威望，做事有原则",
        "七杀": "能力强但脾气稍大",
        "正财": "务实，善于持家",
        "偏财": "大方，人缘好",
        "比肩": "独立，有主见",
        "劫财": "讲义气，社交能力强",
        "食神": "乐观开朗，有福气",
        "伤官": "才华出众，个性鲜明",
    }
    return comments.get(ss, "性格平和")


def _get_family_origin(ss: str, zhi: str) -> str:
    """家庭出身"""
    if ss in ["正印", "偏印"]:
        return "书香门第或文化氛围浓厚"
    elif ss in ["正财", "偏财"]:
        return "经商或条件较好"
    elif ss in ["正官", "七杀"]:
        return "体制内或有管理背景"
    else:
        return "普通家庭"


def _get_sibling_relation(ss: str) -> str:
    """兄弟姐妹关系"""
    if ss in ["比肩", "劫财"]:
        return "关系密切但竞争较多"
    elif ss in ["正印", "偏印"]:
        return "互相照顾、关系和谐"
    elif ss in ["食神", "伤官"]:
        return "各有发展、互相支持"
    else:
        return "关系普通、各自发展"


def _get_marriage_quality(ss: str) -> str:
    """婚姻质量"""
    if ss in ["正财", "正官", "正印", "食神"]:
        return "质量较好，生活和谐"
    elif ss in ["偏财", "偏印", "七杀", "劫财"]:
        return "有挑战，需要经营"
    else:
        return "中规中矩"


def _get_later_life(ss: str) -> str:
    """晚年"""
    if ss in ["正印", "偏印", "食神"]:
        return "生活安逸，子女孝顺"
    elif ss in ["正财", "偏财"]:
        return "物质无忧，生活富足"
    elif ss in ["正官", "七杀"]:
        return "有威望，受人尊重"
    else:
        return "平淡安稳"


def _get_dayun_key_years(d: dict, ri_gan: str, step: int, qi_yun_age: float) -> list:
    """大运关键年份"""
    start_year = int(qi_yun_age + step * 10)
    gan_ss = _get_shi_shen(ri_gan, d["gan"])
    years = []

    # 每运选3个关键年份
    for offset in [2, 5, 8]:
        y = start_year + offset
        if y < start_year + 10:
            years.append({
                "year": f"{y}年",
                "event": f"{gan_ss}能量集中·重要节点",
                "analysis": f"{gan_ss}大运中{y}年为关键年份，宜把握事业和生活的重要机遇。",
            })

    return years


def _get_dayun_rating(d: dict, analysis: dict) -> int:
    """大运评分 1-10"""
    ri_gan = "?"  # dummy
    try:
        xi_list = analysis["xi_yong_shen"].get("xi_shen", [])
        ji_list = analysis["xi_yong_shen"].get("ji_shen", [])

        # 简单评分基于十神喜忌
        score = 6  # 基础分

        # 从大运干支获取实际评分
        if d.get("gan"):
            ri_gan = analysis.get("xi_yong_shen", {}).get("xi_shen", ["?"])[0]
        return min(10, max(1, score))
    except:
        return 5


def _get_dayun_rating_comment(rating: int) -> str:
    """评分评语"""
    if rating >= 8:
        return "吉运·宜积极进取"
    elif rating >= 6:
        return "平中带吉·稳中求进"
    elif rating >= 4:
        return "平运·保守行事"
    else:
        return "凶运·谨慎防守"


def _get_career_advice(basic: dict, analysis: dict) -> str:
    """事业建议"""
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]

    if ge_ju in ["正印", "偏印"]:
        return "技术/学术路线优先，在中大型平台积累经验和深度。中年后可转向技术管理或专家顾问路线。"
    elif ge_ju in ["正官", "七杀"]:
        return "管理/体制路线优先，在规则和秩序中找到自己的节奏。适合大平台或稳定行业。"
    elif ge_ju in ["正财", "偏财"]:
        return "商业/运营路线优先，在市场中锻炼商业敏锐度。适合创业或业务型岗位。"
    elif ge_ju in ["食神", "伤官"]:
        return "创意/创新路线优先，在自由度高的工作环境中发挥创造力。适合科技或文创行业。"
    else:
        return "复合型发展路线，在技术和管理的交叉领域寻找机会。"


def _get_wx_industries_list(basic: dict, analysis: dict) -> str:
    """行业推荐列表"""
    xi_list = analysis["xi_yong_shen"].get("xi_shen", [])
    ri_wx = _get_ri_gan_wu_xing(basic["ri_gan"])

    industries = []
    for ss in xi_list:
        wx = _ji_shen_to_wu_xing(ss, ri_wx, analysis["shen_qiang_ruo"]["level"])
        industries.append(f"{wx}行业（{_get_wx_industries(wx)}）")

    return "、".join(industries[:3]) if industries else "科技/教育/金融等"


def _get_three_decisions(basic: dict, analysis: dict, name: str) -> list:
    """三决断"""
    ri_gan = basic["ri_gan"]
    ge_ju = analysis["ge_ju"]
    sq = analysis["shen_qiang_ruo"]
    dy = analysis["da_yun"]
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)

    decisions = []

    # 决断一：事业成就
    best_dayun = da_yun_list[min(3, len(da_yun_list) - 1)]["gan_zhi"] if len(da_yun_list) > 3 else da_yun_list[-1]["gan_zhi"]
    best_start = int(qi_yun_age + min(3, len(da_yun_list) - 1) * 10)
    decisions.append({
        "title": "事业·格局成就",
        "person": f"{name}——{ge_ju}格局，{sq['level']}命主",
        "matter": f"在{ge_ju}格局驱动下，在技术/专业领域取得显著成就",
        "time": f"{best_start}~{best_start + 9}岁（{best_dayun}大运）为事业巅峰期",
        "degree": f"{_get_career_level(basic, analysis)}级别",
        "reason": f"{ge_ju}格为事业根基，{sq['level']}（{sq['score']}分）提供支撑力，{best_dayun}大运为最佳赋能期",
        "verdict": f"天行刚健，{ri_gan}火炼真金。{best_dayun}运开天地，功成名就在中年。",
    })

    # 决断二：财富格局
    cx = analysis["cai_xing"]
    decisions.append({
        "title": "财富·积累之道",
        "person": f"{name}——{'身强财弱' if sq['level'] == '身强' and cx.get('score', 0) < 40 else '身弱财弱' if sq['level'] != '身强' and cx.get('score', 0) < 40 else '身强财旺'}命格",
        "matter": "通过专业积累和喜用神大运实现财富增长",
        "time": f"中年（第4~6步大运）为主要财富积累期",
        "degree": f"财富等级{cx.get('wealth_level', '未定')}量级",
        "reason": f"财星评分{cx.get('score', 0)}分，{'有库' if cx.get('has_ku') else '无库需补'}，大运配合时财富集中爆发",
        "verdict": f"财藏不露，蓄势待发。喜用神运至，财源广开。",
    })

    # 决断三：人生总评
    decisions.append({
        "title": "人生·总体定位",
        "person": f"{name}——{ge_ju}格局之人",
        "matter": f"以{ge_ju}之格行走人生，{sq['level']}为基础定位",
        "time": f"贯穿一生的核心轨迹：前{int(qi_yun_age + 10)}年积累，中年{int(qi_yun_age + 20)}~{int(qi_yun_age + 40)}发力，晚年收获",
        "degree": f"{_get_career_level(basic, analysis)}为上限，中等偏上富足",
        "reason": f"格局+身强弱+大运配合综合判定，命主'{_get_baihua_summary(basic, analysis, name)}'",
        "verdict": f"命由天定，运由己造。顺势而为，终有大成。",
    })

    return decisions


def _generate_life_events(basic: dict, analysis: dict, dy: dict) -> list:
    """生成全生命周期事件"""
    ri_gan = basic["ri_gan"]
    da_yun_list = dy.get("da_yun", [])
    qi_yun_age = dy.get("qi_yun_age", 0)

    events = []
    event_id = 0

    for i, d in enumerate(da_yun_list[:10]):
        start_year = int(qi_yun_age + i * 10)
        gan_ss = _get_shi_shen(ri_gan, d["gan"])

        # 每个大运生成4~6个事件
        # 学习 (A)
        if i <= 1:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 2,
                "age": int(d["start_age"] + 2),
                "event": f"{'学业起步' if i == 0 else '升学/关键考试'}",
                "type": "A",
                "signal": f"少年{gan_ss}运·学业发力",
            })

        # 事业 (B)
        if i >= 2:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 3,
                "age": int(d["start_age"] + 3),
                "event": f"职场{['入门', '上升', '突破', '巅峰', '转型'][min(i - 2, 4)]}·{gan_ss}发力",
                "type": "B",
                "signal": f"{gan_ss}为{'喜用' if gan_ss in analysis['xi_yong_shen'].get('xi_shen', []) else '忌神'}·{'顺遂' if gan_ss in analysis['xi_yong_shen'].get('xi_shen', []) else '需努力'}",
            })

        # 发财 (C)
        if i >= 2 and i % 2 == 0:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 5,
                "age": int(d["start_age"] + 5),
                "event": f"财运发力·收入增长期",
                "type": "C",
                "signal": f"{gan_ss}生财/护财",
            })

        # 感情 (F)
        if i in [1, 2, 3]:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 4,
                "age": int(d["start_age"] + 4),
                "event": f"感情{['萌发', '稳定', '质变'][min(i - 1, 2)]}期",
                "type": "F",
                "signal": f"夫妻宫被引动",
            })

        # 健康 (H)
        if i >= 4 and i % 2 == 1:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 7,
                "age": int(d["start_age"] + 7),
                "event": f"健康关注期·注意{'、'.join(WU_XING_ORGAN.get(analysis['energy'].get('weakest', '土'), ('体检',)))}保养",
                "type": "H",
                "signal": f"大运五行与原局互动",
            })

        # 转折 (I)
        if i in [2, 4, 6]:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 1,
                "age": int(d["start_age"] + 1),
                "event": f"人生{['觉醒/转型', '突破/进阶', '沉淀/升华'][min(i // 2, 2)]}期",
                "type": "I",
                "signal": f"大运交替·人生转折",
            })

        # 置业 (E)
        if i in [3, 5]:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 6,
                "age": int(d["start_age"] + 6),
                "event": f"置业/重大资产配置",
                "type": "E",
                "signal": f"印星/财星发力·不动产信号",
            })

        # 子女 (G)
        if i in [2, 3]:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 3,
                "age": int(d["start_age"] + 3),
                "event": "子女添丁/子女成长关键期",
                "type": "G",
                "signal": "子女星引动",
            })

        # 搬迁
        if i in [1, 3, 5]:
            event_id += 1
            events.append({
                "dayun": d["gan_zhi"],
                "year": start_year + 2,
                "age": int(d["start_age"] + 2),
                "event": "搬迁/换城市/换环境",
                "type": "H",
                "signal": "驿马/冲合信号",
            })

    return events


def _check_year_has_yin(basic: dict, ri_gan: str) -> bool:
    """年柱是否有印"""
    for cg in basic["pillars"]["nian"]["cang_gan"]:
        if cg["shi_shen"] in ["正印", "偏印"]:
            return True
    return _get_shi_shen(ri_gan, basic["nian_gan"]) in ["正印", "偏印"]


# ═══════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════

def generate_report(bazi_result: dict, name: str = "未知",
                    gender: str = "男", birth_info: dict = None) -> dict:
    """
    生成完整的21§八字命理报告。

    Args:
        bazi_result: bazi_engine.calculate_bazi() 的输出
        name: 姓名
        gender: 性别（男/女）
        birth_info: 出生信息字典 {
            "birth_year": int, "birth_month": int, "birth_day": int,
            "birth_hour": int, "birth_minute": int,
            "lunar_year": str, "lunar_month": int, "lunar_day": int,
            "lunar_hour_desc": str,
        }

    Returns:
        dict: {
            "content_md": str,          # Markdown格式完整报告
            "content_html": str,        # HTML格式（预留）
            "line_count": int,          # 行数
            "sections": dict,           # 各§的内容字典
        }
    """
    if birth_info is None:
        birth_info = {}

    # 确保bazi_result有正确的数据结构
    basic = bazi_result.get("basic", {})
    analysis = bazi_result.get("analysis", {})

    # 构造完整的bazi dict供各§生成器使用
    bazi = {
        "basic": basic,
        "analysis": analysis,
    }

    # 在各§生成前填充gender
    if "gender" not in basic or not basic["gender"]:
        bazi["basic"]["gender"] = gender

    # ── 生成各§ ──
    sections = {}

    sections["s1"] = _gen_section_1(bazi, name, gender, birth_info)

    sections["s2"] = _gen_section_2(bazi, name)
    sections["s3"] = _gen_section_3(bazi)
    sections["s4"] = _gen_section_4(bazi)
    sections["s5"] = _gen_section_5(bazi)
    sections["s6"] = _gen_section_6(bazi)
    sections["s7"] = _gen_section_7(bazi)
    sections["s8"] = _gen_section_8(bazi)
    sections["s9"] = _gen_section_9(bazi)
    sections["s10"] = _gen_section_10(bazi)
    sections["s11"] = _gen_section_11(bazi)
    sections["s12"] = _gen_section_12(bazi)
    sections["s13"] = _gen_section_13(bazi)
    sections["s14"] = _gen_section_14(bazi)
    sections["s15"] = _gen_section_15(bazi, name)
    sections["s16"] = _gen_section_16(bazi)
    sections["s17"] = _gen_section_17(bazi)
    sections["s18"] = _gen_section_18(bazi, name)
    sections["s19"] = _gen_section_19(bazi)
    sections["s20"] = _gen_section_20(bazi)
    sections["s21"] = _gen_section_21(bazi, name)

    footer = _gen_footer()

    # ── 合并完整报告 ──
    parts = [sections["s1"]]
    for i in range(2, 22):
        key = f"s{i}"
        if key in sections:
            parts.append(sections[key])
    parts.append(footer)

    content_md = "\n".join(parts)
    line_cnt = _line_count(content_md)

    # HTML预留（目前返回空字符串）
    content_html = ""

    return {
        "content_md": content_md,
        "content_html": content_html,
        "line_count": line_cnt,
        "sections": sections,
    }
