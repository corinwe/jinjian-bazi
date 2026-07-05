"""
金鉴真人·流年精准断事引擎 v2.0 — 全量事件断法

核心规则框架（所有断语严格遵循以下逻辑链）:
  Step 1: 定身强弱 → 定喜用忌神
  Step 2: 流年干支 → 十神定位（对日主吉凶含义）
  Step 3: 流年与大运 + 原局之地支关系（冲刑合害破）
  Step 4: 五行能量变化（生扶克泄）
  Step 5: 神煞触发（重点年份）
  Step 6: 综合断事（发财·灾祸·结婚·职业·学业·健康·搬迁）

断事逻辑:
  ✅ 发财年: 喜用神流年 + 财星引动 + 三合财局/财库冲开
  ✅ 灾祸年: 忌神流年 + 官杀攻身 + 冲刑太岁/大运
  ✅ 结婚年: 夫妻宫引动 + 财星/官星到位 + 印星帮身
  ✅ 职业年: 官杀印星引动 + 冲合大运
  ✅ 学业年: 印星+文昌到位
  ✅ 健康年: 五行过三 + 七杀攻身
"""

from __future__ import annotations

from constants import DI_ZHI_WU_XING, TIAN_GAN_WU_XING, WU_XING_KE, WU_XING_SHENG
from shen_qiang_ruo import compute_shen_qiang_ruo
from shen_sha import compute_all_shen_sha
from shi_shen import get_shi_shen_for_gan
from xing_chong_he_hua import check_all_relations, check_chong, check_liu_he

# ── 事件类型 ──
EVENT_TYPES = {
    "wealth": "发财/财富增长",
    "misfortune": "灾祸/低谷",
    "marriage": "结婚/姻缘",
    "career": "事业/职业转折",
    "education": "学业/考试",
    "health": "健康/疾病",
    "move": "搬迁/变动",
    "birth": "添丁/子女",
}


class EventPrediction:
    """事件预测"""

    def __init__(self, year: int, event_type: str, description: str, confidence: float, energy: float = 1.0):
        self.year = year
        self.event_type = event_type
        self.description = description
        self.confidence = confidence  # 0.0-1.0
        self.energy = energy  # 能量系数

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "event_type": self.event_type,
            "event_label": EVENT_TYPES.get(self.event_type, self.event_type),
            "description": self.description,
            "confidence": round(self.confidence, 2),
            "energy": round(self.energy, 1),
        }


def _get_wx_relation(wx1: str, wx2: str) -> str:
    """五行关系: 生扶/克泄/同"""
    if wx1 == wx2:
        return "同"
    if WU_XING_SHENG.get(wx1) == wx2:
        return "生"  # wx1生wx2
    if WU_XING_SHENG.get(wx2) == wx1:
        return "被生"  # wx2生wx1
    if WU_XING_KE.get(wx1) == wx2:
        return "克"  # wx1克wx2
    if WU_XING_KE.get(wx2) == wx1:
        return "被克"  # wx2克wx1
    return "其他"


def analyze_liu_nian_v2(
    liu_nian_gan: str,
    liu_nian_zhi: str,
    year: int,
    ri_zhu: str,
    ri_zhu_wx: str,
    year_zhi: str,
    month_zhi: str,
    da_yun_gan: str,
    da_yun_zhi: str,
    all_gans: list[str],
    all_zhis: list[str],
    shen_score: float,
    shen_label: str,
    xi_yong: list[str],
    ji_shen: list[str],
    birth_year: int,
    age: int,
) -> dict:
    """
    流年精准分析 v2 — 含全面事件断法

    逻辑链:
    1. 流年十神→定吉凶方向
    2. 流年地支与大运/原局的关系→定触发方式
    3. 五行能量变化→定程度
    4. 神煞→定性修正
    5. 综合断事
    """
    # ── 基本信息 ──
    liu_nian_wx = f"{TIAN_GAN_WU_XING[liu_nian_gan]}{DI_ZHI_WU_XING[liu_nian_zhi]}"
    liu_nian_shi_shen = get_shi_shen_for_gan(liu_nian_gan, ri_zhu)
    liu_nian_wx_gan = TIAN_GAN_WU_XING[liu_nian_gan]
    liu_nian_wx_zhi = DI_ZHI_WU_XING[liu_nian_zhi]

    # ── 地支关系 ──
    all_rels = check_all_relations(all_zhis + [liu_nian_zhi])
    dy_rels = check_all_relations([liu_nian_zhi, da_yun_zhi])

    # ── 神煞 ──
    shen_sha_full = compute_all_shen_sha(
        all_gans + [liu_nian_gan], all_zhis + [liu_nian_zhi], year_zhi, month_zhi, ri_zhu
    )

    # ── 综合评分 (0-10) ──
    score = 5.0

    # 十神吉凶
    xi_yong_ss = ["正印", "偏印", "比肩", "劫财", "食神"]
    ji_shen_ss = ["七杀", "正官", "伤官", "正财", "偏财"]

    if liu_nian_shi_shen in ["正印", "偏印"]:
        if "水" in xi_yong or "金" in xi_yong:
            score += 2.0
        else:
            score += 1.0
    elif liu_nian_shi_shen in ["比肩", "劫财"]:
        if ri_zhu_wx in xi_yong:
            score += 1.5
    elif liu_nian_shi_shen in ["七杀", "正官"]:
        if ri_zhu_wx in ji_shen:
            score -= 2.0
        else:
            score -= 1.0
    elif liu_nian_shi_shen in ["正财", "偏财"]:
        if ri_zhu_wx in ji_shen:
            score -= 1.0

    # 地支关系影响
    if "冲" in all_rels["summary"]:
        score -= 0.8
    if "三刑" in all_rels["summary"]:
        score -= 1.0
    if "三合" in all_rels["summary"]:
        score += 1.0
    if "六合" in all_rels["summary"]:
        score += 0.5

    # 五行关系
    gan_rel = _get_wx_relation(liu_nian_wx_gan, ri_zhu_wx)
    if gan_rel == "生" or gan_rel == "被生":
        score += 1.0
    elif gan_rel == "克" or gan_rel == "被克":
        score -= 1.0

    score = max(0, min(10, round(score, 1)))

    # ── 事件预测 ──
    events = []

    # ═══════════════════════════════════════
    # 发财事件检测
    # ═══════════════════════════════════════
    wealth_conf = 0.0
    wealth_desc = ""

    # 条件1: 财星流年 + 身强
    if liu_nian_shi_shen in ["正财", "偏财"] and shen_label == "身强":
        wealth_conf += 0.4
        wealth_desc = "财星流年"

    # 条件2: 财星为喜用
    if liu_nian_shi_shen in ["正财", "偏财"] and liu_nian_wx_gan in xi_yong:
        wealth_conf += 0.3
        wealth_desc = "喜用财星流年"

    # 条件3: 三合财局（动态判断财星五行）
    # 日主五行→财星五行
    CAI_WUXING_MAP = {"木": "土", "火": "金", "土": "水", "金": "火", "水": "火"}
    ri_cai_wx = CAI_WUXING_MAP.get(ri_zhu_wx, "")
    for he in all_rels["三合"]:
        he_wx = he.get("wx", "")
        if he_wx and ri_cai_wx and he_wx == ri_cai_wx:
            wealth_conf += 0.3
            wealth_desc = f"{he['type']}财局"

    # 条件4: 财库冲开
    for chong in all_rels["冲"]:
        if "辰戌" in chong or "丑未" in chong:
            wealth_conf += 0.2
            wealth_desc = "财库冲开"

    if wealth_conf >= 0.5:
        wealth_conf = min(1.0, wealth_conf)
        events.append(
            EventPrediction(
                year=year, event_type="wealth", description=f"💰 发财窗口: {wealth_desc}", confidence=wealth_conf
            )
        )

    # ═══════════════════════════════════════
    # 灾祸事件检测
    # ═══════════════════════════════════════
    mis_conf = 0.0
    mis_desc = ""

    # 条件1: 七杀攻身
    if liu_nian_shi_shen == "七杀" and shen_label == "身弱":
        mis_conf += 0.5
        mis_desc = "七杀攻身"

    # 条件2: 忌神流年+冲刑
    if liu_nian_wx_gan in ji_shen and ("冲" in all_rels["summary"] or "刑" in all_rels["summary"]):
        mis_conf += 0.3
        mis_desc = "忌神+冲刑"

    # 条件3: 犯太岁
    from liu_nian import check_fan_tai_sui

    fan_tai_sui = check_fan_tai_sui(year_zhi, liu_nian_zhi)
    if fan_tai_sui:
        mis_conf += fan_tai_sui[1] * 0.3
        mis_desc = f"{fan_tai_sui[0]}"

    # 条件4: 冲大运
    if "冲" in dy_rels["summary"]:
        mis_conf += 0.3
        mis_desc = "大运流年相冲"

    if mis_conf >= 0.5:
        mis_conf = min(1.0, mis_conf)  # 上限100%
        events.append(
            EventPrediction(
                year=year, event_type="misfortune", description=f"⚠️ 注意防范: {mis_desc}", confidence=mis_conf
            )
        )

    # ═══════════════════════════════════════
    # 结婚事件检测
    # ═══════════════════════════════════════
    mar_conf = 0.0
    mar_desc = ""

    # 条件1: 夫妻宫引动
    ri_zhi = all_zhis[2]  # 日支=夫妻宫
    if check_chong(liu_nian_zhi, ri_zhi) or check_liu_he(liu_nian_zhi, ri_zhi):
        mar_conf += 0.3
        mar_desc = "夫妻宫引动"

    # 条件2: 正财/正官流年（适婚年龄）
    if age >= 25 and age <= 45:
        if liu_nian_shi_shen == "正财":
            mar_conf += 0.4
            mar_desc = "正财到位"
        elif liu_nian_shi_shen == "正官":
            mar_conf += 0.3

    # 条件3: 印星帮身（身弱可担家庭责任）
    if liu_nian_shi_shen in ["正印", "偏印"] and shen_label == "身弱":
        mar_conf += 0.2
        mar_desc = "印星扶身"

    if mar_conf >= 0.5:
        mar_conf = min(1.0, mar_conf)
        events.append(
            EventPrediction(
                year=year, event_type="marriage", description=f"💍 姻缘窗口: {mar_desc}", confidence=mar_conf
            )
        )

    # ═══════════════════════════════════════
    # 职业事业事件检测
    # ═══════════════════════════════════════
    car_conf = 0.0
    car_desc = ""

    # 条件1: 官杀印星引动
    if liu_nian_shi_shen in ["正官", "七杀", "正印", "偏印"]:
        car_conf += 0.3
        car_desc = "官印流年"

    # 条件2: 驿马引动
    for ym in shen_sha_full.yi_ma:
        if liu_nian_zhi in ym:
            car_conf += 0.3
            car_desc = "驿马引动"

    # 条件3: 冲合大运
    if "冲" in dy_rels["summary"] or "合" in dy_rels["summary"]:
        car_conf += 0.3
        car_desc = "大运变动"

    if car_conf >= 0.4:
        events.append(
            EventPrediction(year=year, event_type="career", description=f"💼 事业窗口: {car_desc}", confidence=car_conf)
        )

    # ═══════════════════════════════════════
    # 学业事件检测
    # ═══════════════════════════════════════
    edu_conf = 0.0

    if liu_nian_shi_shen in ["正印", "偏印"] and shen_label == "身弱":
        edu_conf += 0.4
    if "文昌" in shen_sha_full.summary:
        edu_conf += 0.3
    if age >= 15 and age <= 30:
        edu_conf += 0.2

    if edu_conf >= 0.5:
        events.append(
            EventPrediction(
                year=year, event_type="education", description="📚 学业窗口: 印星到位+文昌引动", confidence=edu_conf
            )
        )

    # ═══════════════════════════════════════
    # 健康事件检测
    # ═══════════════════════════════════════
    health_conf = 0.0

    # 五行过三检测（简化）
    wx_count = {}
    for g in all_gans:
        wx = TIAN_GAN_WU_XING[g]
        wx_count[wx] = wx_count.get(wx, 0) + 1
    for z in all_zhis:
        from constants import DI_ZHI_CANG_GAN

        for cg, _ in DI_ZHI_CANG_GAN.get(z, []):
            wx = TIAN_GAN_WU_XING[cg]
            wx_count[wx] = wx_count.get(wx, 0) + 1

    for wx, count in wx_count.items():
        if count >= 3 and liu_nian_wx_gan == wx:
            health_conf += 0.4
        if count >= 3 and liu_nian_wx_zhi == wx:
            health_conf += 0.3

    if liu_nian_shi_shen == "七杀" and shen_label == "身弱":
        health_conf += 0.3

    if health_conf >= 0.5:
        events.append(
            EventPrediction(
                year=year, event_type="health", description="🏥 注意健康: 五行过三/七杀攻身", confidence=health_conf
            )
        )

    # ── 汇总 ──
    events_sorted = sorted(events, key=lambda e: e.confidence, reverse=True)

    return {
        "year": year,
        "age": age,
        "liu_nian": f"{liu_nian_gan}{liu_nian_zhi}",
        "gan_zhi_wx": liu_nian_wx,
        "shi_shen": liu_nian_shi_shen,
        "shen_sha_summary": shen_sha_full.summary,
        "di_zhi_guan_xi": all_rels["summary"],
        "da_yun_guan_xi": dy_rels["summary"],
        "comprehensive_score": score,
        "events": [e.to_dict() for e in events_sorted],
        "summary": _generate_summary(score, events_sorted, liu_nian_shi_shen, shen_label),
    }


def _generate_summary(score: float, events: list, shi_shen: str, shen_label: str) -> str:
    """生成流年总结"""
    parts = []

    if score >= 8:
        parts.append("🟢 大吉之年")
    elif score >= 6:
        parts.append("🟡 吉年")
    elif score >= 4:
        parts.append("🟠 平年")
    else:
        parts.append("🔴 凶年")

    parts.append(f"流年十神: {shi_shen}")

    if events:
        top = events[0]
        parts.append(f"关键事件: {top.description}(置信度{top.confidence:.0%})")

    return " | ".join(parts)


def get_liu_nian_gan_zhi(year: int) -> tuple[str, str]:
    """根据年份获取流年干支"""
    gan_map = {4: "甲", 5: "乙", 6: "丙", 7: "丁", 8: "戊", 9: "己", 0: "庚", 1: "辛", 2: "壬", 3: "癸"}
    zhi_map = {
        0: "子",
        1: "丑",
        2: "寅",
        3: "卯",
        4: "辰",
        5: "巳",
        6: "午",
        7: "未",
        8: "申",
        9: "酉",
        10: "戌",
        11: "亥",
    }
    return gan_map[year % 10], zhi_map[year % 12]


def analyze_liu_nian_range(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
    ri_zhu_wx: str,
    year_zhi: str,
    month_zhi: str,
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_years: list[int],
    shen_score: float,
    shen_label: str,
    xi_yong: list[str],
    ji_shen: list[str],
    birth_year: int,
    current_year: int = 2026,
    years: int = 30,
) -> list[dict]:
    """
    分析未来N年流年

    da_yun_gans: 每步大运的天干列表
    da_yun_zhis: 每步大运的地支列表
    da_yun_start_years: 每步大运的起始年份
    """
    results = []

    for offset in range(years):
        year = current_year + offset
        lg, lz = get_liu_nian_gan_zhi(year)
        age = year - birth_year

        # 确定当前大运
        dy_idx = 0
        for i, sy in enumerate(da_yun_start_years):
            if year >= sy:
                dy_idx = i

        dy_gan = da_yun_gans[dy_idx] if dy_idx < len(da_yun_gans) else ""
        dy_zhi = da_yun_zhis[dy_idx] if dy_idx < len(da_yun_zhis) else ""

        result = analyze_liu_nian_v2(
            lg,
            lz,
            year,
            ri_zhu,
            ri_zhu_wx,
            year_zhi,
            month_zhi,
            dy_gan,
            dy_zhi,
            bazi_gans,
            bazi_zhis,
            shen_score,
            shen_label,
            xi_yong,
            ji_shen,
            birth_year,
            age,
        )
        results.append(result)

    return results


def extract_key_events(liu_nian_results: list[dict]) -> dict:
    """提取关键事件年表"""
    events = {"wealth": [], "misfortune": [], "marriage": [], "career": [], "education": [], "health": []}

    for r in liu_nian_results:
        for e in r.get("events", []):
            etype = e["event_type"]
            if etype in events and e["confidence"] >= 0.5:
                events[etype].append(
                    {"year": e["year"], "description": e["description"], "confidence": e["confidence"]}
                )

    return events


if __name__ == "__main__":
    # 测试: 子源 庚申 辛巳 甲午 丙寅
    from constants import BaZi, Pillar
    from shen_qiang_ruo import compute_shen_qiang_ruo

    bazi = BaZi(
        year=Pillar("庚", "申"), month=Pillar("辛", "巳"), day=Pillar("甲", "午"), hour=Pillar("丙", "寅"), gender="男"
    )
    score, label, _ = compute_shen_qiang_ruo(bazi)

    results = analyze_liu_nian_range(
        ["庚", "辛", "甲", "丙"],
        ["申", "巳", "午", "寅"],
        "甲",
        "木",
        "申",
        "巳",
        ["壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"],
        ["午", "未", "申", "酉", "戌", "亥", "子", "丑"],
        [1980, 1990, 2000, 2010, 2020, 2030, 2040, 2050],
        score,
        label,
        ["水", "木"],
        ["金", "土", "火"],
        1980,
        2026,
        15,
    )

    events = extract_key_events(results)
    print("=== 关键事件年表 ===")
    for etype, items in events.items():
        if items:
            print(f"\n{etype} ({EVENT_TYPES[etype]}):")
            for item in items[:3]:
                print(f"  {item['year']}年: {item['description']} (置信度{item['confidence']:.0%})")
