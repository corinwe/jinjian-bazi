#!/usr/bin/env python3
"""
金鉴真人·八字健康心理分析引擎 v2
=======================================
来源：bazi-health-psychology/SKILL.md v7.5（2026-06-11）
       + references/疾病诊断自动化工作流.md (12步流程)

入口函数：analyze_health_full(bazi_gans, bazi_zhis, ri_zhu, shen_label, shen_score, xi_yong, age=35) -> dict

所有规则逐条翻译，docstring标注原始来源段落。
"""

from __future__ import annotations

from typing import Any

# =====================================================================
# §11.1 五行对应身体表 — 天干/地支/五行 → 人体器官映射
# =====================================================================

# 口诀：甲胆乙肝丙小肠，丁心戊胃己脾乡，庚金大肠辛金肺，壬是膀胱癸肾藏
TIANGAN_ORGAN: dict[str, str] = {
    "甲": "肝",
    "乙": "胆",
    "丙": "小肠",
    "丁": "心脏",
    "戊": "胃",
    "己": "脾",
    "庚": "大肠",
    "辛": "肺",
    "壬": "膀胱",
    "癸": "肾",
}
"""§11.1 天干对应脏器"""

# 地支对应：子肾/丑脾/寅胆/卯肝/辰胃/巳心/午心眼/未脾脊/申大肠/酉肺/戌胃腿/亥肾头
DIZHI_ORGAN: dict[str, str] = {
    "子": "肾",
    "丑": "脾",
    "寅": "胆",
    "卯": "肝",
    "辰": "胃",
    "巳": "心",
    "午": "心眼",
    "未": "脾脊",
    "申": "大肠",
    "酉": "肺",
    "戌": "胃腿",
    "亥": "肾头",
}
"""§11.1 地支对应脏器"""

# 五行 → 人体系统
WUXING_ORGAN_SYSTEM: dict[str, list[str]] = {
    "木": ["肝胆", "神经", "筋骨", "毛发", "眼睛"],
    "火": ["心脏", "血液", "小肠", "眼睛"],
    "土": ["脾胃", "消化", "肌肉", "皮肤"],
    "金": ["肺", "大肠", "鼻子", "皮肤", "气管"],
    "水": ["肾", "膀胱", "泌尿", "生殖", "耳朵", "骨骼"],
}
"""§11.1 五行对应身体系统"""

WUXING_TIANGAN: dict[str, list[str]] = {
    "木": ["甲", "乙"],
    "火": ["丙", "丁"],
    "土": ["戊", "己"],
    "金": ["庚", "辛"],
    "水": ["壬", "癸"],
}

WUXING_DIZHI: dict[str, list[str]] = {
    "木": ["寅", "卯"],
    "火": ["巳", "午"],
    "土": ["辰", "戌", "丑", "未"],
    "金": ["申", "酉"],
    "水": ["亥", "子"],
}

GAN_WUXING: dict[str, str] = {g: w for w, gs in WUXING_TIANGAN.items() for g in gs}
ZHI_WUXING: dict[str, str] = {z: w for w, zs in WUXING_DIZHI.items() for z in zs}

# =====================================================================
# 地支藏干（本气/中气/余气）
# =====================================================================
# 来源：SKILL.md §藏干计分规则 + 通用藏干标准表
# 格式：{地支: [(藏干, 比例因子, 等级), ...]}
# 比例因子：本气=1.0, 中气=0.6, 余气=0.3
ZANGGAN_TABLE: dict[str, list[tuple[str, float, str]]] = {
    "子": [("癸", 1.0, "本气")],
    "丑": [("己", 1.0, "本气"), ("癸", 0.6, "中气"), ("辛", 0.3, "余气")],
    "寅": [("甲", 1.0, "本气"), ("丙", 0.6, "中气"), ("戊", 0.3, "余气")],
    "卯": [("乙", 1.0, "本气")],
    "辰": [("戊", 1.0, "本气"), ("乙", 0.6, "中气"), ("癸", 0.3, "余气")],
    "巳": [("丙", 1.0, "本气"), ("庚", 0.6, "中气"), ("戊", 0.3, "余气")],
    "午": [("丁", 1.0, "本气"), ("己", 0.6, "中气")],
    "未": [("己", 1.0, "本气"), ("丁", 0.6, "中气"), ("乙", 0.3, "余气")],
    "申": [("庚", 1.0, "本气"), ("壬", 0.6, "中气"), ("戊", 0.3, "余气")],
    "酉": [("辛", 1.0, "本气")],
    "戌": [("戊", 1.0, "本气"), ("辛", 0.6, "中气"), ("丁", 0.3, "余气")],
    "亥": [("壬", 1.0, "本气"), ("甲", 0.6, "中气")],
}
"""来源：通用藏干标准表 + §藏干计分规则"""

# 宫位基础分：年支=4分  月令=40分  日支=12分  时支=12分
ZHIZANG_BASE: dict[str, float] = {"年": 4.0, "月": 40.0, "日": 12.0, "时": 12.0}

# =====================================================================
# 一扎定位法 — 精确到身体分区
# =====================================================================
# §11.2 七杀断病法 - 一扎定位法（精确到身体分区）
YIZHA_MAP: dict[str, str] = {
    "年干": "头顶~鼻子（头部/大脑/眼睛/耳鼻喉）",
    "年支": "鼻子~锁骨（颈椎/喉咙/牙齿/肩部）",
    "月干": "锁骨~胸口（胸部/乳房/肺/心脏上部）",
    "月令": "胸口~肚脐（上腹部/胃/脾/肝/胆）",
    "日支": "小腹/胯部（子宫/卵巢/膀胱/大肠/男科妇科）",
    "时干": "大腿（大腿骨/肌肉/血管）",
    "时支": "膝盖以下（小腿/脚踝/脚/关节）",
}
"""§11.2 一扎定位法"""

YIZHA_INDEX: dict[str, int] = {"年干": 0, "年支": 1, "月干": 2, "月令": 3, "日支": 4, "时干": 5, "时支": 6}

# 宫位简称
GONGWEI_LABELS = ["年干", "年支", "月干", "月令", "日支", "时干", "时支"]

# =====================================================================
# 六冲映射 → 疾病
# =====================================================================
# §11.2 + §11.4 五行交战→具体疾病
LIUCHONG_DISEASE: dict[str, dict[str, str]] = {
    "子午冲": {"部位": "心肾", "疾病": "心血系统（心肾不交/失眠/高血压）", "五行": "水火交战"},
    "卯酉冲": {"部位": "肝胆筋骨", "疾病": "肝胆（肝气郁结/四肢酸痛/胆囊炎/筋骨损伤）", "五行": "金木交战"},
    "寅申冲": {"部位": "筋骨神经", "疾病": "筋骨损伤（神经痛/腰部扭伤/关节）", "五行": "金木交战"},
    "巳亥冲": {"部位": "心脑血管", "疾病": "心脑血管（头晕/血压波动）", "五行": "水火交战"},
    "辰戌冲": {"部位": "脾胃", "疾病": "脾胃不和（消化不良/胃痛）", "五行": "土土交战"},
    "丑未冲": {"部位": "脾胃免疫", "疾病": "脾胃/免疫（慢性胃炎/免疫紊乱）", "五行": "土土交战"},
}
"""§11.2 + §11.4 五行交战→具体疾病"""

# 天干四冲
TIANGAN_CHONG = {
    ("甲", "庚"): "甲庚冲",
    ("庚", "甲"): "甲庚冲",
    ("乙", "辛"): "乙辛冲",
    ("辛", "乙"): "乙辛冲",
    ("丙", "壬"): "丙壬冲",
    ("壬", "丙"): "丙壬冲",
    ("丁", "癸"): "丁癸冲",
    ("癸", "丁"): "丁癸冲",
}
# 戊己土居中，不与任何天干相冲

DIZHI_CHONG_PAIRS = [
    ("子", "午"),
    ("午", "子"),
    ("卯", "酉"),
    ("酉", "卯"),
    ("寅", "申"),
    ("申", "寅"),
    ("巳", "亥"),
    ("亥", "巳"),
    ("辰", "戌"),
    ("戌", "辰"),
    ("丑", "未"),
    ("未", "丑"),
]

# =====================================================================
# 枭神夺食断病
# =====================================================================
# §11.2
XIAOSHEN_DUOSHI_DISEASE: dict[str, str] = {
    ("枭金", "夺木"): "手脚头伤",
    ("枭木", "夺土"): "血光",
    ("枭土", "夺水"): "车祸外伤",
    ("枭水", "夺火"): "溺水性病",
    ("枭火", "夺金"): "烫伤骨折",
}
"""§11.2 枭神夺食断病"""

# =====================================================================
# 两旺断病
# =====================================================================
LIANGWANG_DISEASE: dict[str, str] = {
    "金水": "美女帅哥（皮肤好容貌佳）",
    "土木": "伤疤脾胃差",
    "金木": "四肢腰疼",
    "水土": "皮肤病",
}
"""§11.2 两旺断病"""

# =====================================================================
# 情绪与五脏对应（§15.6）
# =====================================================================
EMOTION_ORGAN: dict[str, dict[str, str]] = {
    "怒": {"五脏": "肝", "病症": "乳腺增生/甲状腺结节/肝气郁结", "养生": "柔肝息风，可吃醋（山西陈醋）"},
    "喜": {"五脏": "心", "病症": "过喜伤心/心悸/失眠", "养生": "保持平静，不可大喜大悲"},
    "忧": {"五脏": "肺", "病症": "气短/咳嗽/呼吸系统弱", "养生": "宽心解郁，多呼吸新鲜空气"},
    "思": {"五脏": "脾", "病症": "脾胃虚弱/消化不良", "养生": "劳逸结合，规律饮食"},
    "恐": {"五脏": "肾", "病症": "腰膝酸软/尿频/肾气不固", "养生": "固肾安神，避免惊吓"},
}
"""§15.6 情绪与五脏对应"""

# =====================================================================
# 流年疾病预测速查（§11.5 已校准年份）
# =====================================================================
LIUNIAN_YUCE: dict[str, dict[str, Any]] = {
    "壬寅": {"天干冲": "丙壬冲→小肠", "地支冲": "寅申冲→肠胃系统", "预测": "肠胃疾病/大肠小肠问题高发"},
    "癸卯": {"天干冲": "丁癸冲→心脏", "地支冲": "卯酉冲→肝胆", "预测": "心肺/胸部疾病+肝胆问题高发"},
    "甲辰": {"天干冲": "甲庚冲→大肠", "地支冲": "辰戌冲→脾胃", "预测": "消化系统/大肠胃问题高发"},
    "乙巳": {"天干冲": "乙辛冲→肺", "地支冲": "巳亥冲→心脑血管", "预测": "肺/呼吸+心脑血管问题高发"},
    "丙午": {"天干冲": "丙壬冲→小肠/膀胱", "地支冲": "子午冲→心血系统", "预测": "心肾不交/高血压/泌尿问题高发"},
    "丁未": {"天干冲": "丁癸冲→心脏/肾", "地支冲": "丑未冲→脾胃免疫", "预测": "心脏+免疫系统问题高发"},
    "戊申": {"天干冲": "—（戊己土不冲）", "地支冲": "寅申冲→筋骨神经", "预测": "筋骨损伤/神经痛高发"},
    "己酉": {"天干冲": "—（戊己土不冲）", "地支冲": "卯酉冲→肝胆", "预测": "肝胆/胆囊炎问题高发"},
    "庚戌": {"天干冲": "甲庚冲→肝/大肠", "地支冲": "辰戌冲→脾胃", "预测": "肝胆+消化系统高发"},
    "辛亥": {"天干冲": "乙辛冲→肝/肺", "地支冲": "巳亥冲→心脑血管", "预测": "心肺+心脑血管问题高发"},
    "壬子": {"天干冲": "丙壬冲→小肠/膀胱", "地支冲": "子午冲→心血", "预测": "心肾不交/失眠/泌尿高发"},
    "癸丑": {"天干冲": "丁癸冲→心脏/肾", "地支冲": "丑未冲→脾胃", "预测": "心脏+脾胃+免疫高发"},
}

# =====================================================================
# 五行颜色/方位/物品补法（§11.2 五行调和法）
# =====================================================================
WUXING_HARMONY: dict[str, dict[str, Any]] = {
    "木": {"颜色": "绿", "方位": "东方", "饰品": "绿色木牌/玉佩", "石头": "翡翠/绿松石"},
    "火": {"颜色": "红", "方位": "南方", "饰品": "红色饰品", "石头": "红玛瑙/石榴石"},
    "土": {"颜色": "黄", "方位": "中央/本地", "饰品": "黄色饰品/黄玉", "石头": "黄水晶/田黄"},
    "金": {"颜色": "白", "方位": "西方", "饰品": "白色平安无事牌（配金链）", "石头": "白水晶/金银饰品"},
    "水": {"颜色": "黑", "方位": "北方", "饰品": "黑色衣服", "石头": "黑曜石/青金石"},
}
"""§11.2 五行调和法"""

# =====================================================================
# 严重程度分级（§15.2）
# =====================================================================
SEVERITY_LEVELS = [
    ("无", 0, "能量<3倍，无非印比帮身", "无明显不适", "正常生活"),
    ("轻度", 1, "3-5倍恶神/五行小失衡", "偶尔不适，不影响工作", "注意调养"),
    ("中度", 2, "5-10倍冲刑/七杀旺", "需就医，影响生活工作", "体检+调理"),
    ("重度", 3, "≥10倍冲刑+七杀攻身", "危及生命或严重疾病", "必须就医"),
    ("致命", 4, "15倍+多机制叠加", "寿元终结（仅回顾）", "回顾分析"),
]

# =====================================================================
# 四大薄弱系统（§15.3）
# =====================================================================
WEAK_SYSTEMS = [
    {"系统": "心血管🚨", "五行根源": "水克火/火过亢反吸水", "高危特征": "身强水旺无火调候/身弱火旺无水救"},
    {"系统": "肝胆/筋骨", "五行根源": "金木交战/原局无木", "高危特征": "身弱金被木耗/卯酉冲/寅申冲"},
    {"系统": "肾水/泌尿", "五行根源": "水被土壅/金水寒", "高危特征": "丑戌相刑/全局金水寒湿"},
    {"系统": "消化/脾胃", "五行根源": "土被木克/燥湿失衡", "高危特征": "未戌燥土+木旺/辰丑湿土+火弱"},
]


# =====================================================================
# 36岁分界线系数
# =====================================================================
def age_factor(age: int) -> float:
    """
    §11.2 / 实战规则：年龄系数
    36岁前 × 0.7，36-55岁 × 1.0，56岁后 × 1.3
    """
    if age < 36:
        return 0.7
    elif age <= 55:
        return 1.0
    else:
        return 1.3


# =====================================================================
# 辅助函数
# =====================================================================


def _extract_pillar(position: str, gans: list[str], zhis: list[str]) -> tuple[str, str]:
    """提取某一柱的天干地支"""
    idx_map = {"年": 0, "月": 1, "日": 2, "时": 3}
    idx = idx_map.get(position, 0)
    return gans[idx], zhis[idx]


def _calc_zanggan_score(gan: str, zhi: str, zhi_position: str) -> dict[str, float]:
    """
    计算地支藏干得分
    §藏干计分规则 + 疾病诊断自动化工作流第2步
    年支=4分  月令=40分  日支=12分  时支=12分
    """
    base = ZHIZANG_BASE.get(zhi_position, 12.0)
    scores: dict[str, float] = {}
    if zhi in ZANGGAN_TABLE:
        for cang_gan, ratio, _level in ZANGGAN_TABLE[zhi]:
            wuxing = GAN_WUXING.get(cang_gan, "")
            score = base * ratio
            scores[wuxing] = scores.get(wuxing, 0.0) + score
    return scores


def calc_wuxing_scores(gans: list[str], zhis: list[str]) -> dict[str, float]:
    """
    计算五行能量分数（0-100+）
    疾病诊断自动化工作流 第2步
    包含天干 + 地支藏干
    ⚠️ 纳音五行不计入
    """
    scores: dict[str, float] = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}
    positions = ["年", "月", "日", "时"]

    # 天干
    for gan in gans:
        w = GAN_WUXING.get(gan, "")
        if w:
            scores[w] += 10.0  # 天干每字10分

    # 地支藏干
    for i, zhi in enumerate(zhis):
        pos = positions[i]
        zang = _calc_zanggan_score(gans[i], zhi, pos)
        for w, s in zang.items():
            scores[w] = scores.get(w, 0.0) + s

    return scores


def count_wuxing_numeric(gans: list[str], zhis: list[str], include_rizhu: bool = True) -> dict[str, int]:
    """
    五行个数统计（天干+地支本气）
    疾病诊断自动化工作流 第1步
    §11.2 核心原理：五行超过3个以上 → 该五行能量过强
    ⚠️ 包含日元（疾病诊断时）
    """
    counts: dict[str, int] = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    # 天干
    for gan in gans:
        w = GAN_WUXING.get(gan, "")
        if w:
            counts[w] += 1

    # 地支本气
    for zhi in zhis:
        if ZANGGAN_TABLE.get(zhi):
            benqi_gan = ZANGGAN_TABLE[zhi][0][0]
            w = GAN_WUXING.get(benqi_gan, "")
            if w:
                counts[w] += 1

    return counts


def check_wuxing_over_three(counts: dict[str, int]) -> list[dict[str, Any]]:
    """
    §11.2 核心原理：五行超过3个以上 → 该五行能量过强
    口诀：「一个为真，两个为假，三个为病」
    """
    results = []
    for wuxing, count in counts.items():
        if count >= 3:
            organs = WUXING_ORGAN_SYSTEM.get(wuxing, [])
            results.append(
                {
                    "五行": wuxing,
                    "个数": count,
                    "诊断": f"{wuxing}能量过强（{count}个）→ {wuxing}本身及所克五行系统易病",
                    "对应器官": organs,
                    "程度": "过强" if count >= 3 else "正常",
                }
            )
        elif count <= 1:
            organs = WUXING_ORGAN_SYSTEM.get(wuxing, [])
            results.append(
                {
                    "五行": wuxing,
                    "个数": count,
                    "诊断": f"{wuxing}能量偏弱（{count}个）→ 对应器官功能弱",
                    "对应器官": organs,
                    "程度": "偏弱" if count <= 1 else "正常",
                }
            )
    return results


def check_wuxing_energy_imbalance(scores: dict[str, float]) -> list[dict[str, Any]]:
    """
    §11.2 核心原理：五行能量评分
    >60分=太强  40-50分=最佳  <20分=太弱
    """
    results = []
    for wx, score in scores.items():
        status = "平衡"
        detail = ""
        if score > 60:
            status = "太强"
            detail = f"{wx}能量{score:.0f}分 > 60分 → 多出的能量去克其他五行 → 被克的五行出问题"
        elif score < 20:
            status = "太弱"
            detail = f"{wx}能量{score:.0f}分 < 20分 → 对应器官功能弱"
        elif 40 <= score <= 50:
            status = "最佳平衡"
            detail = f"{wx}能量{score:.0f}分 → 平衡状态，不易得病"

        results.append({"五行": wx, "分数": round(score, 1), "状态": status, "诊断": detail})
    return results


def check_dry_wet_balance(scores: dict[str, float]) -> dict[str, Any]:
    """
    §11.2 燥湿平衡（疾病诊断的关键视角）
    疾病诊断自动化工作流 第5步
    火 > 水 + 20分 → 燥热体质
    水 > 火 + 20分 → 寒性体质
    """
    fire = scores.get("火", 0)
    water = scores.get("水", 0)
    result: dict[str, Any] = {"火能量": round(fire, 1), "水能量": round(water, 1), "差值": round(fire - water, 1)}
    if fire - water > 20:
        result["体质"] = "燥热体质"
        result["诊断"] = "燥热体质 → 炎症/血热/高血压/糖尿病/痛风风险"
    elif water - fire > 20:
        result["体质"] = "寒性体质"
        result["诊断"] = "寒性体质 → 畏寒/血瘀/代谢慢"
    else:
        result["体质"] = "相对平衡"
        result["诊断"] = "燥湿相对平衡"

    return result


# =====================================================================
# 七杀断病法（§11.2）
# =====================================================================

# 十神判断简化：七杀定义（仅供健康分析参考）
# 七杀 = 克日主且阴阳相同的天干
# 日主五行 → 七杀天干
QISHA_GAN_BY_RIZHU: dict[str, str] = {
    "甲": "庚",
    "乙": "辛",
    "丙": "壬",
    "丁": "癸",
    "戊": "甲",
    "己": "乙",
    "庚": "丙",
    "辛": "丁",
    "壬": "戊",
    "癸": "己",
}


def find_qisha_positions(ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str]) -> list[dict[str, Any]]:
    """
    §11.2 七杀断病法（实疾之病痛）
    七杀所在的宫位 → 实际病灶所在
    一扎定位法（精确到身体分区）
    双重定位法：宫位 + 五行
    """
    results = []
    qisha_gan = QISHA_GAN_BY_RIZHU.get(ri_zhu, "")

    pillar_positions = [
        ("年干", bazi_gans[0], YIZHA_MAP.get("年干", "")),
        ("月干", bazi_gans[1], YIZHA_MAP.get("月干", "")),
        ("时干", bazi_gans[2], YIZHA_MAP.get("时干", "")),
        ("时支", bazi_zhis[3], YIZHA_MAP.get("时支", "")),
    ]

    # 天干七杀
    for pos_name, gan, yizha in pillar_positions:
        if gan == qisha_gan:
            organ = TIANGAN_ORGAN.get(gan, "未知")
            wx = GAN_WUXING.get(gan, "")
            results.append(
                {
                    "类型": "七杀（实疾）",
                    "位置": pos_name,
                    "天干": gan,
                    "五行": wx,
                    "对应器官": organ,
                    "身体分区": yizha,
                    "病灶定位": f"七杀在{gan}（{wx}）→ {organ}出问题",
                    "双重定位": f"宫位={pos_name}（{yizha.split('（')[0]}） + 五行={wx}（{organ}系统）",
                    "严重程度": "本气七杀 → 病已成型" if gan == qisha_gan else "中气/余气七杀",
                }
            )

    # 地支七杀检查（藏干中是否有七杀）
    zhi_positions = [
        ("年支", bazi_zhis[0], YIZHA_MAP.get("年支", "")),
        ("月令", bazi_zhis[1], YIZHA_MAP.get("月令", "")),
        ("日支", bazi_zhis[2], YIZHA_MAP.get("日支", "")),
    ]
    for pos_name, zhi, yizha in zhi_positions:
        if zhi in ZANGGAN_TABLE:
            for cang_gan, ratio, level in ZANGGAN_TABLE[zhi]:
                if cang_gan == qisha_gan:
                    organ = TIANGAN_ORGAN.get(cang_gan, "未知")
                    wx = GAN_WUXING.get(cang_gan, "")
                    severity_map = {
                        "本气": "病已成型，症状明显",
                        "中气": "潜在病灶，时有发作",
                        "余气": "轻微症状，偶有不适",
                    }
                    results.append(
                        {
                            "类型": "七杀（实疾）",
                            "位置": pos_name,
                            "地支": zhi,
                            "藏干": cang_gan,
                            "五行": wx,
                            "对应器官": organ,
                            "身体分区": yizha,
                            "藏干等级": level,
                            "病灶定位": f"七杀（{cang_gan}）在{zhi}藏干→ {organ}出问题",
                            "双重定位": f"宫位={pos_name}（{yizha.split('（')[0]}） + 五行={wx}（{organ}系统）",
                            "严重程度": severity_map.get(level, ""),
                        }
                    )
    return results


# =====================================================================
# 偏印断病法（§11.2）
# =====================================================================

# 偏印 = 生日主且阴阳相同的天干
PIANYIN_GAN_BY_RIZHU: dict[str, str] = {
    "甲": "壬",
    "乙": "癸",
    "丙": "甲",
    "丁": "乙",
    "戊": "丙",
    "己": "丁",
    "庚": "戊",
    "辛": "己",
    "壬": "庚",
    "癸": "辛",
}


def find_pianyin_positions(ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str]) -> list[dict[str, Any]]:
    """
    §11.2 偏印断病法（经络淤堵）
    偏印→经络淤堵（天干=右半身，地支=左半身）
    配合一扎法使用
    """
    results = []
    pianyin_gan = PIANYIN_GAN_BY_RIZHU.get(ri_zhu, "")

    # 天干偏印（右半身）
    tian_positions = [
        ("年干", bazi_gans[0], YIZHA_MAP.get("年干", "")),
        ("月干", bazi_gans[1], YIZHA_MAP.get("月干", "")),
        ("时干", bazi_gans[2], YIZHA_MAP.get("时干", "")),
    ]
    for pos_name, gan, yizha in tian_positions:
        if gan == pianyin_gan:
            wx = GAN_WUXING.get(gan, "")
            results.append(
                {
                    "类型": "偏印（经络淤堵）",
                    "位置": pos_name,
                    "天干": gan,
                    "半身": "右半身",
                    "五行": wx,
                    "身体分区": yizha,
                    "诊断": f"偏印在{pos_name}（天干=右半身）→ {yizha.split('（')[0]}经络淤堵",
                    "淤堵部位": yizha.split("（")[0],
                }
            )

    # 地支偏印（左半身）
    di_positions = [
        ("年支", bazi_zhis[0], YIZHA_MAP.get("年支", "")),
        ("月令", bazi_zhis[1], YIZHA_MAP.get("月令", "")),
        ("日支", bazi_zhis[2], YIZHA_MAP.get("日支", "")),
        ("时支", bazi_zhis[3], YIZHA_MAP.get("时支", "")),
    ]
    for pos_name, zhi, yizha in di_positions:
        if zhi in ZANGGAN_TABLE:
            for cang_gan, ratio, level in ZANGGAN_TABLE[zhi]:
                if cang_gan == pianyin_gan:
                    wx = GAN_WUXING.get(cang_gan, "")
                    results.append(
                        {
                            "类型": "偏印（经络淤堵）",
                            "位置": pos_name,
                            "地支": zhi,
                            "藏干": cang_gan,
                            "半身": "左半身",
                            "五行": wx,
                            "身体分区": yizha,
                            "藏干等级": level,
                            "诊断": f"偏印（{cang_gan}）在{zhi}藏干（地支=左半身）→ {yizha.split('（')[0]}经络淤堵",
                            "淤堵部位": yizha.split("（")[0],
                        }
                    )

    # 偏印落配偶宫（日支）→ 配偶性冷淡
    ri_zhi = bazi_zhis[2]  # 日支
    if ri_zhi in ZANGGAN_TABLE:
        for cang_gan, ratio, level in ZANGGAN_TABLE[ri_zhi]:
            if cang_gan == pianyin_gan:
                results.append(
                    {
                        "类型": "偏印（配偶宫）",
                        "位置": "日支（配偶宫）",
                        "诊断": "偏印落配偶宫（日支）→ 配偶性冷淡（偏印克食伤，食伤处死地，不喜欢享受行乐）",
                        "备选": "食神落配偶宫→欲望强，喜行房事（与此相反）",
                    }
                )

    return results


# =====================================================================
# 五行交战检查（§11.2 + §11.4）
# =====================================================================


def check_liuchong(gans: list[str], zhis: list[str]) -> list[dict[str, Any]]:
    """
    §11.4 受冲五行断病法（冲力距离规则）
    §11.2 五行交战→具体疾病
    天干四冲 + 地支六冲
    冲力与距离：相邻=100%，隔位=60%，隔两位=30%
    """
    results = []

    # 天干相冲
    pillar_names_gan = ["年干", "月干", "日干", "时干"]
    for i in range(len(gans)):
        for j in range(i + 1, len(gans)):
            pair = (gans[i], gans[j])
            if pair in TIANGAN_CHONG:
                dist = j - i
                if dist == 1:
                    power = 100
                elif dist == 2:
                    power = 60
                else:
                    power = 30
                chong_name = TIANGAN_CHONG[pair]
                # 找对应的疾病
                disease_info = _get_chong_disease(chong_name, "天干")
                results.append(
                    {
                        "类型": "天干相冲",
                        "组合": chong_name,
                        "对冲双方": f"{pillar_names_gan[i]}({gans[i]}) vs {pillar_names_gan[j]}({gans[j]})",
                        "距离": f"{'相邻' if dist == 1 else '隔一' if dist == 2 else '隔二'}位",
                        "冲力": f"{power}%",
                        "疾病": disease_info,
                    }
                )

    # 地支相冲
    pillar_names_zhi = ["年支", "月令", "日支", "时支"]
    for i in range(len(zhis)):
        for j in range(i + 1, len(zhis)):
            pair = (zhis[i], zhis[j])
            if pair in DIZHI_CHONG_PAIRS:
                dist = j - i
                if dist == 1:
                    power = 100
                elif dist == 2:
                    power = 60
                else:
                    power = 30
                chong_name = f"{zhis[i]}{zhis[j]}冲"
                disease_info = _get_chong_disease(chong_name, "地支")
                results.append(
                    {
                        "类型": "地支六冲",
                        "组合": chong_name,
                        "对冲双方": f"{pillar_names_zhi[i]}({zhis[i]}) vs {pillar_names_zhi[j]}({zhis[j]})",
                        "距离": f"{'相邻' if dist == 1 else '隔一' if dist == 2 else '隔二'}位",
                        "冲力": f"{power}%",
                        "疾病": disease_info,
                    }
                )

    return results


def _get_chong_disease(chong_name: str, level: str) -> str:
    """根据冲的组合返回对应的疾病描述"""
    if chong_name in LIUCHONG_DISEASE:
        info = LIUCHONG_DISEASE[chong_name]
        return f"{info['部位']}：{info['疾病']}"
    # 天干冲处理
    tg_map = {
        "甲庚冲": "肝胆/大肠（金木交战→肝胆湿热/大肠问题）",
        "乙辛冲": "肝胆/肺（金木交战→肝气郁结/肺热）",
        "丙壬冲": "小肠/膀胱（水火交战→心肾不交/泌尿问题）",
        "丁癸冲": "心脏/肾（水火交战→心悸/失眠/肾虚）",
    }
    return tg_map.get(chong_name, "未具体分类，需根据五行生克分析")


# =====================================================================
# 宫位受伤断病法（§11.3）
# =====================================================================


def check_gongwei_injury(gans: list[str], zhis: list[str], scores: dict[str, float]) -> list[dict[str, Any]]:
    """
    §11.3 宫位受伤断病法（全新模块·2026-06-10新增）
    原理：某一柱/某一字被周围全是克它的能量包围，无任何生助 → 宫位重伤
    三要素：「孤零零」+「被群克」+「无生助」同时满足才算
    """
    results = []

    # 简化评估：对每个天干检查是否有生助
    gongwei_info = [
        ("年干", gans[0], "头部斑秃/头发成片脱落 + 父亲缘分薄"),
        ("月干", gans[1], "胸闷/心悸/胸部问题"),
        ("日支（夫妻宫）", zhis[2], "克配偶/配偶遭遇意外 + 小腹/妇科/男科问题"),
        ("时干", gans[3], "子女/晚年健康出问题 + 腿部问题"),
    ]

    for name, element, symptom in gongwei_info:
        wx = GAN_WUXING.get(element, "") if element in GAN_WUXING else ZHI_WUXING.get(element, "")
        if not wx:
            continue

        # 检查其它柱是否有生助该五行的
        all_elements = list(gans) + zhis
        other_wuxings = [GAN_WUXING.get(e, ZHI_WUXING.get(e, "")) for e in all_elements if e != element]
        other_wuxings = [w for w in other_wuxings if w]

        # 生助判断：生该五行的五行
        sheng_map = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
        sheng_wx = sheng_map.get(wx, "")
        has_sheng = sheng_wx in other_wuxings

        # 被群克：克该五行的五行数量
        ke_map = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
        ke_wx = ke_map.get(wx, "")
        ke_count = other_wuxings.count(ke_wx)

        # 自身能量
        self_score = scores.get(wx, 0)

        is_isolated = self_score < 10  # 孤零零
        is_mass_ke = ke_count >= 2  # 被群克
        no_support = not has_sheng  # 无生助

        conditions_met = sum([is_isolated, is_mass_ke, no_support])

        if conditions_met >= 2:
            level = "重伤" if conditions_met == 3 else "中度受伤"
            results.append(
                {
                    "宫位": name,
                    "五行": wx,
                    "元素": element,
                    "孤零零": is_isolated,
                    "被群克": is_mass_ke,
                    "无生助": no_support,
                    "满足条件数": conditions_met,
                    "受伤程度": level,
                    "典型病症": symptom,
                    "诊断": f"「{'孤零零' if is_isolated else ''}{' + ' if is_isolated and is_mass_ke else ''}{'被群克' if is_mass_ke else ''}{' + ' if (is_isolated or is_mass_ke) and no_support else ''}{'无生助' if no_support else ''}」→ {name}受伤 → {symptom}",
                }
            )

    return results


# =====================================================================
# 木的特殊对应（§11.2）
# =====================================================================


def check_mu_special(bazi_gans: list[str], bazi_zhis: list[str], scores: dict[str, float]) -> dict[str, Any]:
    """
    §11.2 木的特殊对应
    - 八字缺木→身高偏矮+酒量差
    - 年柱宫位落金或土→发质不好
    - 年柱宫位落木→头发浓密
    """
    mu_score = scores.get("木", 0)
    mu_count = count_wuxing_numeric(bazi_gans, bazi_zhis).get("木", 0)

    result: dict[str, Any] = {"木能量": round(mu_score, 1), "木个数": mu_count}

    # 缺木判断
    if mu_score < 10 and mu_count <= 1:
        result["缺木"] = True
        result["身高判断"] = "八字缺木 → 身高不会太高（发育大运无木补充则较矮，女命一般不高于1.60米）"
        result["酒量判断"] = "八字缺木→酒量差（木主肝，肝脏解酒能力差，喝一点就脸红/醉）"
    else:
        result["缺木"] = False
        result["身高判断"] = "有木，身高发育正常"
        result["酒量判断"] = "木能量正常，酒量看个人"

    # 年柱宫位判断发质
    nian_gan = bazi_gans[0]
    nian_zhi = bazi_zhis[0]
    nian_wx_gan = GAN_WUXING.get(nian_gan, "")
    nian_wx_zhi = ZHI_WUXING.get(nian_zhi, "")

    if nian_wx_gan in ("金", "土") or nian_wx_zhi in ("金", "土"):
        result["发质判断"] = (
            f"年柱落{egan if (egan := (nian_wx_gan or nian_wx_zhi)) else ''} → 发质不好（{'金克木' if nian_wx_gan == '金' or nian_wx_zhi == '金' else '土囚木'}）"
        )
    elif nian_wx_gan == "木" or nian_wx_zhi == "木":
        result["发质判断"] = "年柱落木 → 头发浓密"
    else:
        result["发质判断"] = "发质正常"

    return result


# =====================================================================
# 配偶身体判断法（§11.2）
# =====================================================================


def check_spouse_health(ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str]) -> dict[str, Any]:
    """
    §11.2 配偶身体判断法（从己身八字看配偶健康）
    直断法 + 官星/财星法
    - 女命看日支（夫妻宫）五行
    - 男命同理，日支五行克什么→妻子对应的器官系统偏弱
    """
    ri_zhi = bazi_zhis[2]  # 日支=配偶宫
    ri_zhi_wx = ZHI_WUXING.get(ri_zhi, "")

    # 判断性别（根据日主粗略判断，实际需要更精确的方法）
    # 简单假设：甲丙戊庚壬为阳干→偏向男命，乙丁己辛癸为阴干→偏向女命
    yang_gan = ["甲", "丙", "戊", "庚", "壬"]
    is_male_likely = ri_zhu in yang_gan

    result: dict[str, Any] = {"日支（夫妻宫）": ri_zhi, "日支五行": ri_zhi_wx}

    # 直断法
    zhichang_map = {
        "土": {"克": "水", "部位": "肾", "诊断": "日支属土（辰戌丑未）→ 土克水 → 肾功能偏弱/性功能差"},
        "火": {"克": "金", "部位": "肺", "诊断": "日支属火（巳午）→ 火旺克金 → 肺/呼吸道偏弱"},
        "金": {"克": "木", "部位": "肝胆", "诊断": "日支属金（申酉）→ 金克木 → 肝胆/筋骨偏弱"},
        "木": {"克": "土", "部位": "脾胃", "诊断": "日支属木（寅卯）→ 木克土 → 消化系统偏弱"},
        "水": {"克": "火", "部位": "心脏", "诊断": "日支属水（亥子）→ 水旺 → 肾功能强（但水多克火→心脏注意）"},
    }

    if ri_zhi_wx in zhichang_map:
        info = zhichang_map[ri_zhi_wx]
        result["直断法"] = {
            "性别倾向": "男命→看妻子" if is_male_likely else "女命→看丈夫",
            "判断": f"日支五行={ri_zhi_wx} → {info['诊断']}",
        }

    # 官星/财星法（简化）
    # 女命官星法：官星=克日主且阴阳不同的天干
    # 男命财星法：财星=日主所克且阴阳不同的天干
    guanxing_gan = ""
    caixing_gan = ""
    for gan in ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]:
        g_wx = GAN_WUXING.get(gan, "")
        r_wx = GAN_WUXING.get(ri_zhu, "")
        # 官星：克日主
        ke_map = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
        if ke_map.get(r_wx, "") == g_wx:
            # 阴阳不同
            if (ri_zhu in yang_gan) != (gan in yang_gan):
                guanxing_gan = gan
        # 财星：日主所克
        if ke_map.get(g_wx, "") == r_wx:
            if (ri_zhu in yang_gan) != (gan in yang_gan):
                caixing_gan = gan

    # 检查官星/财星在八字中的位置
    for i, gan in enumerate(bazi_gans):
        if guanxing_gan and gan == guanxing_gan:
            result["官星法（女命看夫）"] = {
                "官星位置": ["年干", "月干", "日干", "时干"][i],
                "官星天干": gan,
                "官星五行": GAN_WUXING.get(gan, ""),
                "诊断": f"女命官星（{gan}）在{'年干=头部' if i == 0 else '月干=胸部' if i == 1 else '日干=自身' if i == 2 else '时干=下肢'} → 官星五行克什么，配偶对应部位偏弱",
            }
        if caixing_gan and gan == caixing_gan:
            result["财星法（男命看妻）"] = {
                "财星位置": ["年干", "月干", "日干", "时干"][i],
                "财星天干": gan,
                "财星五行": GAN_WUXING.get(gan, ""),
                "诊断": f"男命财星（{gan}）在{'年干=头部' if i == 0 else '月干=胸部' if i == 1 else '日干=自身' if i == 2 else '时干=下肢'} → 财星五行被克，配偶对应部位偏弱",
            }

    return result


# =====================================================================
# 流年疾病预测法（§11.5）
# =====================================================================


def predict_liunian_disease(year_gan: str, year_zhi: str) -> dict[str, Any]:
    """
    §11.5 流年疾病预测法
    根据流年干支预测该年高发疾病方向
    1. 流年天干 → 与哪个天干相冲 → 对应哪个脏器高发
    2. 流年地支 → 与哪个地支相冲 → 对应哪个宫位高发
    3. 双重叠加 = 该年最容易集中出问题的疾病系统
    """
    liunian = year_gan + year_zhi
    result: dict[str, Any] = {"流年": liunian}

    if liunian in LIUNIAN_YUCE:
        result.update(LIUNIAN_YUCE[liunian])
    else:
        # 通用推算
        tg_disease = ""
        for (g1, g2), name in TIANGAN_CHONG.items():
            if year_gan == g1:
                tg_disease = f"{year_gan}{g2}冲 → 对应脏器高发"
            elif year_gan == g2:
                tg_disease = f"{g1}{year_gan}冲 → 对应脏器高发"

        dz_disease = ""
        for dz_pair in DIZHI_CHONG_PAIRS:
            if year_zhi == dz_pair[0]:
                dz_disease = f"{year_zhi}{dz_pair[1]}冲 → 对应宫位高发"

        result["天干冲"] = tg_disease or "无直接天干冲"
        result["地支冲"] = dz_disease or "无直接地支冲"

    return result


# =====================================================================
# 五行调和法（§11.2）
# =====================================================================


def get_wuxing_harmony_advice(deficient_wuxing: list[str]) -> list[dict[str, Any]]:
    """
    §11.2 五行调和法
    八字缺某个五行导致五行不流通 → 疾病
    用补该五行的方式可以辅助调理
    """
    advice = []
    for wx in deficient_wuxing:
        if wx in WUXING_HARMONY:
            info = WUXING_HARMONY[wx]
            advice.append(
                {
                    "缺失五行": wx,
                    "调和颜色": info["颜色"],
                    "调和方位": info["方位"],
                    "推荐饰品": info["饰品"],
                    "推荐石头": info["石头"],
                    "建议": f"补{wx}：穿{info['颜色']}色衣服，带{info['石头']}，在{info['方位']}位办公/居住",
                }
            )
    return advice


# =====================================================================
# 九字真言（§14）
# =====================================================================


def get_nine_word_mantra() -> dict[str, Any]:
    """
    §14 九字真言（道家心法工具）
    口诀：临兵斗者皆阵列前行
    来源：葛洪《抱朴子》登涉篇
    """
    return {
        "口诀": "临兵斗者皆阵列前行",
        "来源": "葛洪《抱朴子》登涉篇，道教核心咒语，又称幻神咒",
        "本质": "召唤守护神到身边，保平安、护心神，克制心魔",
        "用法": "心魔来时默念3遍即可见效，不需出声",
        "注意事项": "不需要手印，默念即可",
        "应用场景": [
            {"场景": "心魔来袭（烦躁/恐惧/愤怒/焦虑）", "用法": "默念3遍", "效果": "内心恢复平静如水"},
            {"场景": "走夜路感觉不安", "用法": "边走边念", "效果": "守护神护佑"},
            {"场景": "与人争吵/情绪失控前", "用法": "先念3遍再开口", "效果": "压制冲动"},
            {"场景": "日常修行", "用法": "转动刻字戒指/手串，心中默念", "效果": "长期保持心静"},
        ],
        "八字应用": [
            "伤官旺/七杀旺命主 → 易情绪失控、心魔重 → 建议日常默念",
            "身弱遇七杀攻身 → 易恐惧/焦虑 → 建议睡前默念",
            "枭神夺食/五行严重失衡 → 易有心理问题 → 配合冥想默念",
        ],
    }


# =====================================================================
# 情绪与五脏分析（§15.6）
# =====================================================================


def check_emotion_health(scores: dict[str, float]) -> list[dict[str, Any]]:
    """
    §15.6 情绪与五脏（中医理论应用）
    怒伤肝、喜伤心、忧伤肺、思伤脾、恐伤肾
    结合五行能量判断情绪倾向
    """
    results = []
    # 根据五行能量推断情绪倾向
    if scores.get("木", 0) > 60:
        results.append(
            {
                "情绪": "怒",
                "五脏": "肝",
                "五行原因": "木能量过强 → 肝火旺 → 易怒",
                "病症": EMOTION_ORGAN["怒"]["病症"],
                "养生": EMOTION_ORGAN["怒"]["养生"],
            }
        )
    if scores.get("火", 0) > 60:
        results.append(
            {
                "情绪": "喜（过）",
                "五脏": "心",
                "五行原因": "火能量过强 → 心火旺 → 过喜伤心",
                "病症": EMOTION_ORGAN["喜"]["病症"],
                "养生": EMOTION_ORGAN["喜"]["养生"],
            }
        )
    if scores.get("金", 0) > 60:
        results.append(
            {
                "情绪": "忧",
                "五脏": "肺",
                "五行原因": "金能量过强 → 肺气过旺 → 多忧",
                "病症": EMOTION_ORGAN["忧"]["病症"],
                "养生": EMOTION_ORGAN["忧"]["养生"],
            }
        )
    if scores.get("土", 0) > 60:
        results.append(
            {
                "情绪": "思（过）",
                "五脏": "脾",
                "五行原因": "土能量过强 → 思虑过重 → 伤脾",
                "病症": EMOTION_ORGAN["思"]["病症"],
                "养生": EMOTION_ORGAN["思"]["养生"],
            }
        )
    if scores.get("水", 0) > 60:
        results.append(
            {
                "情绪": "恐",
                "五脏": "肾",
                "五行原因": "水能量过强 → 肾气过旺 → 易恐",
                "病症": EMOTION_ORGAN["恐"]["病症"],
                "养生": EMOTION_ORGAN["恐"]["养生"],
            }
        )

    # 能量偏弱的情绪倾向
    if scores.get("木", 0) < 20:
        results.append(
            {
                "情绪": "郁（木郁）",
                "五脏": "肝",
                "五行原因": "木能量偏弱 → 肝气郁结 → 情绪抑郁",
                "病症": "情绪低落/优柔寡断",
                "养生": "补木：穿绿色，东方位活动",
            }
        )
    if scores.get("金", 0) < 20:
        results.append(
            {
                "情绪": "悲",
                "五脏": "肺",
                "五行原因": "金能量偏弱 → 肺气虚 → 易悲",
                "病症": "气短/有气无力",
                "养生": "补金：白色，西方位活动",
            }
        )

    return results


# =====================================================================
# 五行流通检查（§11.6）
# =====================================================================


def check_wuxing_cycle(scores: dict[str, float]) -> dict[str, Any]:
    """
    §11.6 五行流通与伟人格
    五行全流通：金→水→木→火→土→金（循环相生）
    没有克战，五脏调和 → 长寿之相
    """
    cycle = ["金", "水", "木", "火", "土"]
    missing = [wx for wx in cycle if scores.get(wx, 0) < 5]

    result: dict[str, Any] = {"五行齐全": len(missing) == 0, "缺失五行": missing, "流通状态": ""}

    if len(missing) == 0:
        result["流通状态"] = "✅ 五行齐全 + 流通好 → 直接可断80岁以上寿命"
    elif len(missing) <= 2:
        result["流通状态"] = (
            f"⚠️ 缺{'/'.join(missing)} → 循环中断 → {', '.join([f'{wx}对应的器官弱' for wx in missing])}"
        )
        if "水" in missing:
            result["流通状态"] += "；缺水 → 卫气不足 → 易受风寒暑湿"
        if "土" in missing:
            result["流通状态"] += "；缺土 → 气血不足 → 整体虚弱"
        if "水" in missing and "土" in missing:
            result["流通状态"] += " ⚠️ 缺水+缺土 → 短命之相（水=先天之本，土=后天之本）"
    else:
        result["流通状态"] = f"❌ 严重缺失{'/'.join(missing)}，五行循环重度中断"

    return result


# =====================================================================
# 枭神夺食检查（§11.2）
# =====================================================================


def check_xiaoshen_duoshi(ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str]) -> list[str]:
    """
    §11.2 枭神夺食断病速查
    枭金夺木=手脚头伤，枭木夺土=血光，枭土夺水=车祸外伤
    枭水夺火=溺水性病，枭火夺金=烫伤骨折
    """
    # 简化实现：检查偏印（枭神）和食伤共存情况
    results = []

    # 偏印天干
    pianyin_gan = PIANYIN_GAN_BY_RIZHU.get(ri_zhu, "")
    # 食神天干（生日主且阴阳不同）
    shishen_gan_map = {
        "甲": "丙",
        "乙": "丁",
        "丙": "戊",
        "丁": "己",
        "戊": "庚",
        "己": "辛",
        "庚": "壬",
        "辛": "癸",
        "壬": "甲",
        "癸": "乙",
    }
    shishen_gan = shishen_gan_map.get(ri_zhu, "")

    has_pianyin = pianyin_gan in bazi_gans
    has_shishen = shishen_gan in bazi_gans

    if has_pianyin and has_shishen:
        py_wx = GAN_WUXING.get(pianyin_gan, "")
        ss_wx = GAN_WUXING.get(shishen_gan, "")
        key = (f"枭{py_wx}", f"夺{ss_wx}")
        if key in XIAOSHEN_DUOSHI_DISEASE:
            results.append(f"枭神夺食（{pianyin_gan}枭{py_wx}夺{shishen_gan}{ss_wx}）→ {XIAOSHEN_DUOSHI_DISEASE[key]}")

    return results


# =====================================================================
# 两旺断病（§11.2）
# =====================================================================


def check_liangwang(scores: dict[str, float]) -> list[str]:
    """
    §11.2 两旺断病
    """
    results = []
    pairs = [("金", "水"), ("土", "木"), ("金", "木"), ("水", "土")]
    for w1, w2 in pairs:
        if scores.get(w1, 0) > 50 and scores.get(w2, 0) > 50:
            key = w1 + w2
            if key in LIANGWANG_DISEASE:
                results.append(
                    f"{w1}{w2}两旺（{w1}={scores[w1]:.0f}分, {w2}={scores[w2]:.0f}分）→ {LIANGWANG_DISEASE[key]}"
                )
    return results


# =====================================================================
# 亥亥自刑检查（§11.3）
# =====================================================================


def check_haizi_zixing(bazi_zhis: list[str]) -> list[dict[str, Any]]:
    """
    §11.3 亥亥自刑规则
    两个亥一见→天干无水引化=5倍，天干有水引化=10倍
    三个亥+引化+月令水=15倍
    """
    results = []
    hai_count = bazi_zhis.count("亥")

    if hai_count >= 2:
        result = {"亥个数": hai_count, "规则": ""}
        if hai_count == 2:
            result["规则"] = "两个亥 → 天干无水引化=5倍，天干有水引化=10倍"
        elif hai_count >= 3:
            result["规则"] = "三个亥+引化+月令水=15倍"
        result["诊断"] = "亥为水，水过旺则导致肾/膀胱/生殖系统问题"
        results.append(result)

    return results


# =====================================================================
# 日干强弱专项检查（§16.2 文章15补充）
# =====================================================================


def check_rigan_weakness(ri_zhu: str, scores: dict[str, float]) -> dict[str, Any]:
    """
    §16.2 疾病健康断法（5条·文章15）
    日干某五行弱 → 对应系统先天薄弱
    """
    ri_wx = GAN_WUXING.get(ri_zhu, "")
    score = scores.get(ri_wx, 0)

    weakness_map = {
        "庚": {"五行": "金", "薄弱": "呼吸系统（肺/支气管/皮肤/大肠/扁桃体/咽喉）先天薄弱"},
        "辛": {"五行": "金", "薄弱": "呼吸系统（肺/支气管/皮肤/大肠/扁桃体/咽喉）先天薄弱"},
        "甲": {"五行": "木", "薄弱": "肝胆功能欠缺、筋骨/毛发问题，白发脱发为警示信号"},
        "乙": {"五行": "木", "薄弱": "肝胆功能欠缺、筋骨/毛发问题，白发脱发为警示信号"},
        "壬": {"五行": "水", "薄弱": "肾/膀胱/泌尿/内分泌系统薄弱；脑力耗费肾气"},
        "癸": {"五行": "水", "薄弱": "肾/膀胱/泌尿/内分泌系统薄弱；脑力耗费肾气"},
        "丙": {"五行": "火", "薄弱": "畏寒怕冷、手脚冰凉、精神不振；火不生土→脾胃寒湿"},
        "丁": {"五行": "火", "薄弱": "畏寒怕冷、手脚冰凉、精神不振；火不生土→脾胃寒湿"},
        "戊": {"五行": "土", "薄弱": "脾胃功能弱（后天之本受损），易导致消渴症、百病丛生"},
        "己": {"五行": "土", "薄弱": "脾胃功能弱（后天之本受损），易导致消渴症、百病丛生"},
    }

    result: dict[str, Any] = {"日干": ri_zhu, "日干五行": ri_wx, "日干能量": round(score, 1)}

    if ri_zhu in weakness_map and score < 20:
        info = weakness_map[ri_zhu]
        result["诊断"] = f"日干{ri_zhu}（{info['五行']}）能量弱（{score:.0f}分）→ {info['薄弱']}"
    else:
        result["诊断"] = f"日干{ri_zhu}能量正常（{score:.0f}分），无明显先天薄弱"

    return result


# =====================================================================
# 严重程度综合评估（§15.2）
# =====================================================================


def assess_severity(
    wuxing_over_three: list, qisha_results: list, chong_results: list, gongwei_results: list
) -> dict[str, Any]:
    """
    §15.2 严重程度分级
    §12步 疾病断语严重程度
    """
    severity_score = 0

    # 五行过强加分
    for item in wuxing_over_three:
        count = item.get("个数", 0)
        if count >= 5:
            severity_score += 3
        elif count >= 4:
            severity_score += 2
        elif count >= 3:
            severity_score += 1

    # 七杀加分
    for item in qisha_results:
        if item.get("藏干等级") == "本气":
            severity_score += 2
        else:
            severity_score += 1

    # 相冲加分
    for item in chong_results:
        power_str = item.get("冲力", "0%")
        power = int(power_str.replace("%", ""))
        if power >= 100:
            severity_score += 2
        elif power >= 60:
            severity_score += 1

    # 宫位受伤加分
    for item in gongwei_results:
        if item.get("受伤程度") == "重伤":
            severity_score += 2
        else:
            severity_score += 1

    # 映射到等级
    if severity_score >= 8:
        level = "重度"
        detail = "≥10倍冲刑+七杀攻身，危及生命或严重疾病，必须就医"
    elif severity_score >= 5:
        level = "中度"
        detail = "5-10倍冲刑/七杀旺，需就医，影响生活工作，建议体检+调理"
    elif severity_score >= 3:
        level = "轻度"
        detail = "3-5倍恶神/五行小失衡，偶尔不适，注意调养"
    else:
        level = "无"
        detail = "能量<3倍，无明显不适，正常生活"

    return {
        "综合评分": severity_score,
        "严重级别": level,
        "详细描述": detail,
        "各级映射": {
            "无": {"范围": "0-2分", "描述": "正常生活"},
            "轻度": {"范围": "3-4分", "描述": "注意调养"},
            "中度": {"范围": "5-7分", "描述": "体检+调理"},
            "重度": {"范围": "8+分", "描述": "必须就医"},
        },
    }


# =====================================================================
# 疾病断语生成器（§12步 / 疾病诊断自动化工作流 第12步）
# =====================================================================


def generate_disease_summary(
    wuxing_results: list,
    energy_results: list,
    qisha_results: list,
    pianyin_results: list,
    dry_wet: dict,
    gongwei_results: list,
    chong_results: list,
    liunian: dict,
    emotion_results: list,
    severity: dict,
    mu_special: dict,
    age: int,
) -> dict[str, Any]:
    """
    整合所有分析结果，生成最终疾病断语
    """
    factor = age_factor(age)

    # 收集所有问题描述
    issues = []

    # 五行过三
    for item in wuxing_results:
        if item.get("程度") in ("过强", "偏弱"):
            issues.append(f"【五行{item['程度']}】{item['诊断']}")

    # 七杀
    for item in qisha_results:
        if "病灶定位" in item:
            issues.append(f"【七杀实疾】{item['病灶定位']}（{item.get('身体分区', '')}）")

    # 偏印
    for item in pianyin_results:
        if "诊断" in item and item.get("类型") != "偏印（配偶宫）":
            issues.append(f"【偏印淤堵】{item['诊断']}")

    # 配偶宫
    for item in pianyin_results:
        if item.get("类型") == "偏印（配偶宫）":
            issues.append(f"【配偶健康】{item['诊断']}")

    # 燥湿
    if dry_wet.get("体质") != "相对平衡":
        issues.append(f"【燥湿失衡】{dry_wet.get('诊断', '')}")

    # 宫位受伤
    for item in gongwei_results:
        issues.append(f"【宫位{item.get('受伤程度', '')}】{item['诊断']}")

    # 相冲
    for item in chong_results:
        if item.get("冲力", "0%") >= "60%":
            issues.append(f"【{item['类型']}】{item['组合']}（{item['冲力']}冲力）→ {item['疾病']}")

    # 流年
    if liunian.get("预测"):
        issues.append(f"【流年预警】{liunian['流年']}年 → {liunian['预测']}")

    # 情绪
    for item in emotion_results:
        issues.append(f"【情绪影响】{item.get('情绪', '')}→{item.get('五脏', '')}：{item.get('病症', '')}")

    # 木特殊
    if mu_special.get("缺木"):
        issues.append(f"【木特殊】{mu_special.get('身高判断', '')}")
        issues.append(f"【木特殊】{mu_special.get('酒量判断', '')}")

    # 年龄系数修正
    if factor != 1.0:
        issues.append(f"【年龄修正】{age}岁，系数×{factor}（{'36岁前减30%' if age < 36 else '56岁后加30%'})")

    # 综合断语
    if severity.get("综合评分", 0) >= 5:
        conclusion = f"健康风险较高（综合评分{severity['综合评分']}分/年龄系数{factor}），{severity['详细描述']}"
    elif severity.get("综合评分", 0) >= 3:
        conclusion = f"存在健康隐患（综合评分{severity['综合评分']}分/年龄系数{factor}），{severity['详细描述']}"
    else:
        conclusion = f"健康状况总体良好（综合评分{severity['综合评分']}分/年龄系数{factor}），{severity['详细描述']}"

    return {
        "年龄系数": factor,
        "问题数量": len(issues),
        "全部问题": issues,
        "综合结论": conclusion,
        "严重级别": severity.get("严重级别", "无"),
    }


# =====================================================================
# 主入口函数
# =====================================================================


def analyze_health_full(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
    shen_label: str = "",
    shen_score: float = 50.0,
    xi_yong: list[str] | None = None,
    age: int = 35,
) -> dict[str, Any]:
    """
    八字健康心理全面分析引擎 — 主入口

    参数：
        bazi_gans: 四柱天干列表 [年, 月, 日, 时]，如 ["甲", "丙", "戊", "庚"]
        bazi_zhis: 四柱地支列表 [年, 月, 日, 时]，如 ["子", "寅", "辰", "午"]
        ri_zhu: 日主天干（如 "戊"）
        shen_label: 身强弱标签（"身强"/"身弱"/"中和"）
        shen_score: 身强弱评分（0-100）
        xi_yong: 喜用神列表，如 ["火", "土"]
        age: 命主年龄（默认35），用于年龄系数

    返回：
        dict 包含完整健康分析结果
    """
    if xi_yong is None:
        xi_yong = []

    # Step 1: 五行计数（含日元）
    # 疾病诊断自动化工作流 第1步
    wuxing_counts = count_wuxing_numeric(bazi_gans, bazi_zhis, include_rizhu=True)

    # Step 2: 五行能量计算（0-100分）
    # 疾病诊断自动化工作流 第2步
    wuxing_scores = calc_wuxing_scores(bazi_gans, bazi_zhis)

    # §11.2 五行过三检查
    wuxing_over_three = check_wuxing_over_three(wuxing_counts)

    # §11.2 五行能量不平衡检查
    energy_imbalance = check_wuxing_energy_imbalance(wuxing_scores)

    # Step 3: 七杀定位（实疾）
    # §11.2 七杀断病法
    qisha_results = find_qisha_positions(ri_zhu, bazi_gans, bazi_zhis)

    # Step 4: 偏印定位（淤堵）
    # §11.2 偏印断病法
    pianyin_results = find_pianyin_positions(ri_zhu, bazi_gans, bazi_zhis)

    # Step 5: 燥湿平衡判断
    # §11.2 燥湿平衡
    dry_wet = check_dry_wet_balance(wuxing_scores)

    # Step 6: 特殊排查 — 木的特殊对应
    # §11.2 木的特殊对应
    mu_special = check_mu_special(bazi_gans, bazi_zhis, wuxing_scores)

    # Step 7: 五行缺少检查 + 五行流通
    # §11.6
    wuxing_cycle = check_wuxing_cycle(wuxing_scores)

    # Step 8: 宫位受伤检查
    # §11.3
    gongwei_injury = check_gongwei_injury(bazi_gans, bazi_zhis, wuxing_scores)

    # 亥亥自刑
    haizi_zixing = check_haizi_zixing(bazi_zhis)

    # Step 9: 受冲距离检查
    # §11.4 + §11.2 五行交战
    liuchong_results = check_liuchong(bazi_gans, bazi_zhis)

    # 枭神夺食
    xiaoshen = check_xiaoshen_duoshi(ri_zhu, bazi_gans, bazi_zhis)

    # 两旺断病
    liangwang = check_liangwang(wuxing_scores)

    # Step 10: 流年疾病预测（默认当前流年，可由外部传入）
    # §11.5
    # 这里传入空字符串表示需要外部提供，目前提供通用方法
    liunian_prediction = {}  # 需要外部传入当前流年干支

    # Step 11: 情绪五脏检查
    # §15.6
    emotion_results = check_emotion_health(wuxing_scores)

    # 配偶身体判断
    # §11.2 配偶身体判断法
    spouse_health = check_spouse_health(ri_zhu, bazi_gans, bazi_zhis)

    # 日干弱专项
    rigian_weak = check_rigan_weakness(ri_zhu, wuxing_scores)

    # 严重程度综合评估
    severity = assess_severity(wuxing_over_three, qisha_results, liuchong_results, gongwei_injury)

    # 五行调和法建议
    deficient_wuxing = [wx for wx in ["木", "火", "土", "金", "水"] if wuxing_scores.get(wx, 0) < 10]
    harmony_advice = get_wuxing_harmony_advice(deficient_wuxing)

    # 九字真言
    nine_word = get_nine_word_mantra()

    # 生成断语摘要
    summary = generate_disease_summary(
        wuxing_over_three,
        energy_imbalance,
        qisha_results,
        pianyin_results,
        dry_wet,
        gongwei_injury,
        liuchong_results,
        liunian_prediction,
        emotion_results,
        severity,
        mu_special,
        age,
    )

    # =================================================================
    # 最终输出
    # =================================================================
    return {
        "元数据": {
            "引擎版本": "health_v2.py v7.5",
            "来源": "bazi-health-psychology/SKILL.md (2026-06-11)",
            "八字": {"天干": bazi_gans, "地支": bazi_zhis, "日主": ri_zhu},
            "身强弱": {"标签": shen_label, "评分": shen_score},
            "喜用神": xi_yong,
            "年龄": age,
            "年龄系数": age_factor(age),
        },
        "五行统计": {
            "天干地支本气个数": wuxing_counts,
            "藏干五行能量分数": {k: round(v, 1) for k, v in wuxing_scores.items()},
            "五行过三检查": wuxing_over_three,
            "能量平衡分析": energy_imbalance,
        },
        "燥湿平衡": dry_wet,
        "七杀实疾": qisha_results,
        "偏印淤堵": pianyin_results,
        "五行相冲": liuchong_results,
        "宫位受伤": gongwei_injury,
        "特殊检查": {
            "木的特殊对应": mu_special,
            "亥亥自刑": haizi_zixing,
            "枭神夺食": xiaoshen,
            "两旺断病": liangwang,
            "日干弱专项检查": rigian_weak,
        },
        "五行流通": wuxing_cycle,
        "配偶健康": spouse_health,
        "情绪五脏": emotion_results,
        "严重程度评估": severity,
        "五行调和建议": harmony_advice,
        "九字真言": nine_word,
        "疾病断语摘要": summary,
    }


# =====================================================================
# 工具函数：流年疾病预测（外部调用）
# =====================================================================


def predict_annual_disease(year_gan: str, year_zhi: str) -> dict[str, Any]:
    """
    §11.5 流年疾病预测法
    外部独立调用：传入流年干支，返回该年疾病预警
    """
    return predict_liunian_disease(year_gan, year_zhi)


# =====================================================================
# 工具函数：快速健康评分
# =====================================================================


def quick_health_score(bazi_gans: list[str], bazi_zhis: list[str], age: int = 35) -> dict[str, Any]:
    """
    快速健康评分（无需十神信息）
    仅做五行层面的健康评估
    """
    scores = calc_wuxing_scores(bazi_gans, bazi_zhis)
    counts = count_wuxing_numeric(bazi_gans, bazi_zhis)

    # 评估各项
    issues = 0
    details = []

    # 五行过三
    for wx, cnt in counts.items():
        if cnt >= 3:
            issues += 1
            details.append(f"{wx}过多（{cnt}个）")

    # 能量过强或过弱
    for wx, sc in scores.items():
        if sc > 60:
            issues += 1
            details.append(f"{wx}过强（{sc:.0f}分）")
        elif sc < 20:
            issues += 1
            details.append(f"{wx}过弱（{sc:.0f}分）")

    # 五行缺失
    missing = [wx for wx, sc in scores.items() if sc < 5]
    if missing:
        issues += len(missing)
        details.append(f"缺{'/'.join(missing)}")

    # 年龄系数
    factor = age_factor(age)
    adjusted_score = max(0, 100 - issues * 12) * factor

    return {
        "原始健康分": max(0, 100 - issues * 12),
        "年龄系数": factor,
        "调整后健康分": round(adjusted_score, 1),
        "问题数量": issues,
        "问题明细": details,
        "评级": "优"
        if adjusted_score >= 80
        else "良"
        if adjusted_score >= 60
        else "中"
        if adjusted_score >= 40
        else "差",
    }


# =====================================================================
# 自测 / 示例
# =====================================================================
if __name__ == "__main__":
    # 示例：某八字
    test_gans = ["甲", "丙", "戊", "庚"]
    test_zhis = ["子", "寅", "辰", "午"]

    result = analyze_health_full(
        bazi_gans=test_gans,
        bazi_zhis=test_zhis,
        ri_zhu="戊",
        shen_label="身强",
        shen_score=72,
        xi_yong=["火", "土"],
        age=42,
    )

    import json

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
