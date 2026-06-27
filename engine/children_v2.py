"""
金鉴真人·子女/生育完整判断引擎 v2.0

来源：bazi-children-analysis SKILL.md v2.0（2026-06-15更新）
      含2026-06-25九龙道长公众号文章校准规则

完整判断流程（10步）:
  Step 0: 逻辑一致性检查（🚨 门禁！先过）
  Step 1: 子女星定位（分阴阳规则）
  Step 2: 十二长生基数法
  Step 3: 子女宫喜忌判断
  Step 4: 时支生育力评级
  Step 5: 子女缘分三层合参法计算
  Step 6: 子女出生年份推理（大运流年引动）
  Step 7: 缘薄因素排查
  Step 8: 生育窗口排查
  Step 9: 子女成就判断
  Step 10: 综合输出 + 用户确认
"""

from __future__ import annotations

from constants import (
    DI_ZHI,
    DI_ZHI_CANG_GAN,
    DI_ZHI_WU_XING,
    TIAN_GAN,
    TIAN_GAN_WU_XING,
    TIAN_GAN_YIN_YANG,
    WU_XING_KE,
    WU_XING_SHENG,
)
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan
from xing_chong_he_hua import BAN_HE, LIU_CHONG, LIU_HAI, LIU_HE, SAN_HE, check_xing

# ════════════════════════════════════════════════════════════════
# 全局常量
# ════════════════════════════════════════════════════════════════

# 天干阴阳判定
TIAN_GAN_IS_YANG = {g: (y == "阳") for g, y in TIAN_GAN_YIN_YANG.items()}

# ── 流派A（不分阴阳·通用版）子女星映射 ──
# SKILL.md §「子女星规则」流派A
SCHOOL_A_CHILDREN_STAR = {"男": {"子": "七杀", "女": "正官"}, "女": {"子": "伤官", "女": "食神"}}

# ── 流派B（分阴阳·精细版）子女星映射 ──
# SKILL.md §「子女星规则」流派B — 搜狐尚泽先生
SCHOOL_B_CHILDREN_STAR = {
    # 男命
    ("男", True): {"子": "七杀", "女": "正官"},  # 阳干：七杀=儿子，正官=女儿
    ("男", False): {"子": "正官", "女": "七杀"},  # 阴干：正官=儿子，七杀=女儿
    # 女命
    ("女", True): {"子": "伤官", "女": "食神"},  # 阳干：伤官=儿子，食神=女儿
    ("女", False): {"子": "食神", "女": "伤官"},  # 阴干：食神=儿子，伤官=女儿
}

# ── 十二长生位对应基数表 ──
# SKILL.md §「十二长生基数法」
SHI_ER_CHANG_SHENG_BASE = {
    "长生": 4,  # 长生四子中旬半
    "沐浴": 2,  # 沐浴一双保安康
    "冠带": 3,  # 冠带临官三子位
    "临官": 3,  # 冠带临官三子位
    "帝旺": 5,  # 旺中五子自成行
    "衰": 2,  # 衰中二子病中一
    "病": 1,  # 衰中二子病中一
    "死": 0,  # 死中晚景少儿郎（极少）
    "墓": -1,  # 入墓之时多不良（不良/抱养）
    "绝": 1,  # 受气为绝一个子
    "胎": 1,  # 胎中头胎是姑娘
    "养": 3,  # 养中三子只留一
}

SHI_ER_CHANG_SHENG_DESC = {
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

# ── 十二长生在地支的定位(日干→时支) ──
# 五行长生表: 木长生在亥、火长生在寅、金长生在巳、水土长生在申
# 十二长生循环顺序: 长生→沐浴→冠带→临官→帝旺→衰→病→死→墓→绝→胎→养
CHANG_SHENG_CYCLE = ["长生", "沐浴", "冠带", "临官", "帝旺", "衰", "病", "死", "墓", "绝", "胎", "养"]

# 五行长生起始地支
WU_XING_CHANG_SHENG_START = {
    "木": 2,  # 寅(地支index 2)
    "火": 3,  # 卯 → 不对，火长生在寅，index=2... 等等
}
# 更准确的：根据日干五行确定长生起始
# 甲木长生在亥(11)，乙木长生在午(6)...
# 但SKILL说的是"子女星在时支的十二长生位"
# 即先找子女星(比如正官)，再看这个子女星在时支的十二长生状态
# 子女星本身是十神，对应天干，所以需要查子女星的天干在时支的长生位

# 实际上，标准做法：
# 对于男命：子女星=正官/七杀，其五行属性是确定的
# 比如甲日主男命，正官=辛(金)，看辛金在时支的长生位
# 需要建立: 天干在十二地支的长生位表

# 天干在十二地支的十二长生状态（阳顺阴逆）
# 阳干顺行：长生→沐浴→冠带→临官→帝旺→衰→病→死→墓→绝→胎→养
# 阴干逆行：长生→沐浴→冠带→临官→帝旺→衰→病→死→墓→绝→胎→养
# （从长生起始地支开始，阳顺阴逆）

# 五行长生起始地支（阳干）
YANG_GAN_CHANG_SHENG_START = {
    "甲": 10,  # 甲木长生在亥(index 10)
    "丙": 2,  # 丙火长生在寅(index 2)
    "戊": 2,  # 戊土长生在寅(index 2)
    "庚": 4,  # 庚金长生在巳(index 4)
    "壬": 6,  # 壬水长生在申(index 6)
}

# 阴干长生起始地支
YIN_GAN_CHANG_SHENG_START = {
    "乙": 5,  # 乙木长生在午(index 5)
    "丁": 8,  # 丁火长生在酉(index 8)
    "己": 8,  # 己土长生在酉(index 8)
    "辛": 11,  # 辛金长生在子(index 11)
    "癸": 2,  # 癸水长生在寅(index 2)
}


# ── 时支生育力排名（SKILL.md §「生育能力 时支生育力排名」）──
SHI_ZHI_FERTILITY_RANK = {
    "卯": {"level": "最强", "range": "6-10个", "mid": 8},
    "子": {"level": "极强", "range": "5-8个", "mid": 6.5},
    "酉": {"level": "强", "range": "4-7个", "mid": 5.5},
    "午": {"level": "中强", "range": "3-6个", "mid": 4.5},
    "辰": {"level": "中等", "range": "2-5个", "mid": 3.5},
    "戌": {"level": "中等", "range": "2-5个", "mid": 3.5},
    "丑": {"level": "中等", "range": "2-5个", "mid": 3.5},
    "未": {"level": "中等", "range": "2-5个", "mid": 3.5},
    "寅": {"level": "偏弱", "range": "1-3个", "mid": 2},
    "申": {"level": "偏弱", "range": "1-3个", "mid": 2},
    "巳": {"level": "偏弱", "range": "1-3个", "mid": 2},
    "亥": {"level": "偏弱", "range": "1-3个", "mid": 2},
}

# ── 子女星评分体系（SKILL.md §「子女数量三层合参法」）──
CHILDREN_STAR_SCORE_MAP = {
    "tou_gan": 15,  # 天干透出 +15
    "zhen_gen": 20,  # 地支真根 +20
    "san_he_enhance": 20,  # 三会/三合加强 +20
    "da_yun_trigger": 10,  # 大运流年引动 +10
    "be_he_off": -30,  # 被合化走 -30
    "kong_wang": -25,  # 空亡 -25
    "chong_xing": -15,  # 被冲/刑 -15
}

CHILDREN_FATE_SCORE_THRESHOLD = {
    "深": 40,  # ≥40分 → 子女缘分深
    "中": 20,  # 20-39分 → 中等
    "薄": 0,  # <20分 → 缘分薄
}

# ── 半合组合(用于时支被合检查) ──
BAN_HE_PAIRS = {k for k in BAN_HE}

# ── 三会局 ──
SAN_HUI = {("寅", "卯", "辰"): "木", ("巳", "午", "未"): "火", ("申", "酉", "戌"): "金", ("亥", "子", "丑"): "水"}

# ── 缘薄因素（SKILL.md §「第六步：子女缘薄因素」）──
FATE_THIN_FACTORS = [
    "日时冲",  # 与子女缘分薄
    "时支劫财",  # 克子女
    "子女星空亡",  # 缘分薄，易流产
    "时柱空亡",  # 晚年孤独
    "命局无子女星",  # 缘分极薄
    "子女星被合化",  # 表面有实则无
    "子女星被冲刑",  # 生育困难
    "时支阳刃",  # 难产之象
    "全局缺水",  # 生殖系统弱
    "印旺制食伤",  # 不容易受孕
]

# ── 生育窗口信号强度（SKILL.md §「生育窗口排查」）──
FERTILITY_WINDOW_SIGNALS = [
    ("⭐⭐⭐⭐⭐", "子女星在流年天干透出"),
    ("⭐⭐⭐⭐", "子女宫（时支）被伏吟/合/冲"),
    ("⭐⭐⭐", "流年合化出子女星"),
    ("⭐⭐", "大运子女星透干+流年配合"),
    ("⭐", "身旺有能量生育的年份"),
]

# ── 双胞胎条件及倍数 ──
TWIN_CONDITIONS = [("丑未戌三刑", 15), ("寅卯辰三会", 20), ("巳午未三会", 20), ("辰午酉亥自刑", 10)]

# ── 时柱十神定子女方向（SKILL.md §「第八步：子女成就判断」）──
SHI_ZHU_TEN_GOD_CHILD_DIRECTION = {
    "正财": "孩子诚实稳重",
    "偏财": "孩子经济头脑好",
    "正官": "孩子能当官",
    "七杀": "孩子有魄力/有权威",
    "正印": "孩子爱学习",
    "偏印": "孩子有特殊才艺",
    "食神": "孩子口才好/有福气",
    "伤官": "孩子聪明/有才华",
    "比肩": "孩子做事坚持/有主见",
    "劫财": "孩子社交能力强",
}

# ── 时柱正官对子女影响（SKILL.md §「时柱正官对子女的影响」）──
ZHENG_GUAN_EFFECTS = {
    ("时干正官", "身旺"): ("吉", "子女得力，老而安乐"),
    ("时干正官", "归禄"): ("吉", "晚年衣食无忧，后人发达"),
    ("时干正官", "伤官"): ("凶", "子女有伤亡之兆"),
    ("时干正官", "食神"): ("吉", "晚年财旺，子女有良缘"),
    ("时干正官", "七杀"): ("凶", "官杀过旺，出不肖之子"),
}

# ── 父母合参规律口诀 ──
PARENT_JOINT_RHYME = "父母同频看合参，帮身条件是前提；子女星动加能量，两者俱全是应期；父看官杀母食伤，交叉引动更精准。"


# ════════════════════════════════════════════════════════════════
# 辅助函数
# ════════════════════════════════════════════════════════════════


def _is_yang_gan(gan: str) -> bool:
    """判定天干是否为阳干"""
    return TIAN_GAN_IS_YANG.get(gan, True)


def _get_shi_shen_wu_xing(shi_shen: str) -> str | None:
    """根据十神名称返回其五行克日主的反向五行。
    七杀/正官 = 克我 → 五行属性为"克日主的五行"
    """
    # 十神本身的五行 = 那个天干的五行
    # 但实际上我们需要的不是这个
    return None


def get_twelve_chang_sheng(gan: str, zhi: str) -> str:
    """
    获取某天干在地支的十二长生状态。

    阳干顺排：从长生地支开始，顺数到目标地支
    阴干逆排：从长生地支开始，逆数到目标地支

    SKILL.md §「十二长生基数法」
    """
    DI_ZHI_LIST = DI_ZHI  # ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

    if _is_yang_gan(gan):
        start_idx = YANG_GAN_CHANG_SHENG_START.get(gan, 0)
        # 阳干顺数
        target_idx = DI_ZHI_LIST.index(zhi)
        offset = (target_idx - start_idx) % 12
        return CHANG_SHENG_CYCLE[offset]
    else:
        start_idx = YIN_GAN_CHANG_SHENG_START.get(gan, 0)
        # 阴干逆数
        target_idx = DI_ZHI_LIST.index(zhi)
        offset = (start_idx - target_idx) % 12
        return CHANG_SHENG_CYCLE[offset]


def get_children_star_school_a(gender: str) -> dict:
    """
    流派A（不分阴阳·通用版）子女星规则。

    SKILL.md §「子女星规则」流派A：
      男命：七杀=子 / 正官=女
      女命：伤官=子 / 食神=女
    """
    return SCHOOL_A_CHILDREN_STAR.get(gender, {})


def get_children_star_school_b(gender: str, ri_zhu: str) -> dict:
    """
    流派B（分阴阳·精细版）子女星规则。

    SKILL.md §「子女星规则」流派B — 搜狐尚泽先生：
      男命阳干：七杀=儿子，正官=女儿
      男命阴干：正官=儿子，七杀=女儿
      女命阳干：伤官=儿子，食神=女儿
      女命阴干：食神=儿子，伤官=女儿
    """
    is_yang = _is_yang_gan(ri_zhu)
    return SCHOOL_B_CHILDREN_STAR.get((gender, is_yang), {})


def get_unified_children_stars(gender: str, ri_zhu: str) -> dict:
    """
    综合两派得到子女星列表。

    金鉴实战口诀（SKILL.md）：
      先用流派A判大体
      再用流派B验细节
      两派一致→确认
      两派矛盾→以流派A为准，流派B做参考偏女/偏子
    """
    school_a = get_children_star_school_a(gender)
    school_b = get_children_star_school_b(gender, ri_zhu)

    son_stars = set()
    daughter_stars = set()

    # 流派A
    son_stars.add(school_a.get("子"))
    daughter_stars.add(school_a.get("女"))

    # 流派B
    son_stars.add(school_b.get("子"))
    daughter_stars.add(school_b.get("女"))

    return {
        "school_a": school_a,
        "school_b": school_b,
        "son_stars": list(son_stars - {None}),
        "daughter_stars": list(daughter_stars - {None}),
        "all_children_stars": list((son_stars | daughter_stars) - {None}),
        "consensus": school_a == school_b,
    }


def scan_children_stars_in_bazi(
    ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str], children_stars: list[str]
) -> dict:
    """
    扫描八字中所有子女星的位置。

    SKILL.md §「第一步：子女星定位」
      ① 定日主阴阳 → 选流派A或B
      ② 扫天干 → 有无子女星透出
      ③ 扫所有地支藏干 → 本/中/余气
      ④ 子女星缺失检查 → 全无=该性别缘分薄
      ⑤ 子女星被合化检查 → 合=实际没有
    """
    result = {"透干": [], "地支藏干": [], "缺失": True}

    pillar_names = ["年柱", "月柱", "日柱", "时柱"]

    # 扫天干
    for i, gan in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(gan, ri_zhu)
        if ss in children_stars:
            result["透干"].append({"位置": pillar_names[i], "天干": gan, "十神": ss})
            result["缺失"] = False

    # 扫地支藏干
    for i, zhi in enumerate(bazi_zhis):
        cang_gan_list = DI_ZHI_CANG_GAN.get(zhi, [])
        for cg, ratio in cang_gan_list:
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss in children_stars:
                result["地支藏干"].append({"位置": pillar_names[i], "地支": zhi, "藏干": cg, "比例": ratio, "十神": ss})
                result["缺失"] = False

    return result


def get_twelve_chang_sheng_base(gender: str, ri_zhu: str, hour_zhi: str, unified_stars: dict) -> dict:
    """
    计算十二长生基数。

    SKILL.md §「第二步：十二长生基数法」
      ① 找子女星（男命七杀/正官）
      ② 看子女星在时支的十二长生位
      ③ 按口诀得基数
      ④ 刑冲合害调基数
    """
    results = []

    # 取子女星的天干代表（按流派A的主要子女星）
    school_a = unified_stars["school_a"]
    son_star_a = school_a.get("子")
    daughter_star_a = school_a.get("女")

    # 需要找到能代表子女星的天干
    # 子女星是十神名，我们需要找到其对应的天干五行
    # 七杀/正官 → 克我的五行
    # 伤官/食神 → 我生的五行

    ri_zhu_wx = TIAN_GAN_WU_XING[ri_zhu]

    # 找到对应十神的天干示例
    # 七杀/正官：克我者，五行属性为克日主的五行
    if "七杀" in unified_stars["all_children_stars"] or "正官" in unified_stars["all_children_stars"]:
        ke_wo_wx = WU_XING_KE.get(ri_zhu_wx)  # 克日主的五行
        if ke_wo_wx:
            # 取该五行的第一个阳干和阴干作为代表
            representative_gans = [g for g in TIAN_GAN if TIAN_GAN_WU_XING[g] == ke_wo_wx]
            for rep_gan in representative_gans:
                cs_state = get_twelve_chang_sheng(rep_gan, hour_zhi)
                base_num = SHI_ER_CHANG_SHENG_BASE.get(cs_state, 1)
                desc = SHI_ER_CHANG_SHENG_DESC.get(cs_state, "")
                results.append(
                    {"子女星天干": rep_gan, "时支": hour_zhi, "十二长生": cs_state, "基数": base_num, "口诀": desc}
                )

    # 伤官/食神：我生者，五行属性为日主所生的五行
    if "伤官" in unified_stars["all_children_stars"] or "食神" in unified_stars["all_children_stars"]:
        wo_sheng_wx = WU_XING_SHENG.get(ri_zhu_wx)  # 日主所生的五行
        if wo_sheng_wx:
            representative_gans = [g for g in TIAN_GAN if TIAN_GAN_WU_XING[g] == wo_sheng_wx]
            for rep_gan in representative_gans:
                cs_state = get_twelve_chang_sheng(rep_gan, hour_zhi)
                base_num = SHI_ER_CHANG_SHENG_BASE.get(cs_state, 1)
                desc = SHI_ER_CHANG_SHENG_DESC.get(cs_state, "")
                results.append(
                    {"子女星天干": rep_gan, "时支": hour_zhi, "十二长生": cs_state, "基数": base_num, "口诀": desc}
                )

    # 取主基数（第一个子女星的基数）
    main_base = results[0]["基数"] if results else 1
    main_state = results[0]["十二长生"] if results else "未知"
    main_desc = results[0]["口诀"] if results else ""

    return {"明细": results, "主基数": main_base, "主状态": main_state, "口诀": main_desc}


def get_shi_zhi_fertility(hour_zhi: str, bazi_zhis: list[str]) -> dict:
    """
    时支生育力排名及调校。

    SKILL.md §「第四步：生育能力（时支生育力排名）」

    特殊加强规则：
      时支被三合/三会/六合加强 → 加一档
      时支被冲/刑/害 → 减一档
      时支空亡 → 减半
    """
    base = SHI_ZHI_FERTILITY_RANK.get(hour_zhi, {"level": "未知", "range": "未知", "mid": 1})
    result = {
        "时支": hour_zhi,
        "基础等级": base["level"],
        "基础范围": base["range"],
        "基础中值": base["mid"],
        "加强因素": [],
        "削弱因素": [],
        "调校后中值": base["mid"],
        "调校说明": "无特殊调校",
    }

    # 检查加强
    # 三合: 时支 + 其他两支构成三合
    for trio, wx in SAN_HE.items():
        if hour_zhi in trio:
            others = [z for z in trio if z != hour_zhi]
            if all(o in bazi_zhis for o in others):
                result["加强因素"].append(f"{''.join(trio)}三合{wx}局")

    # 三会
    for trio, wx in SAN_HUI.items():
        if hour_zhi in trio:
            others = [z for z in trio if z != hour_zhi]
            if all(o in bazi_zhis for o in others):
                result["加强因素"].append(f"{''.join(trio)}三会{wx}局")

    # 六合
    for (z1, z2), wx in LIU_HE.items():
        if hour_zhi == z1 and z2 in bazi_zhis:
            result["加强因素"].append(f"{hour_zhi}{z2}六合{wx}")
        elif hour_zhi == z2 and z1 in bazi_zhis:
            result["加强因素"].append(f"{z1}{hour_zhi}六合{wx}")

    # 检查削弱
    # 冲
    chong_zhi = LIU_CHONG.get(hour_zhi)
    if chong_zhi and chong_zhi in bazi_zhis:
        result["削弱因素"].append(f"{hour_zhi}{chong_zhi}六冲")

    # 刑
    xing_results = check_xing(bazi_zhis)
    for xing_type, _ in xing_results:
        if hour_zhi in xing_type:
            result["削弱因素"].append(xing_type)

    # 害
    for z1, z2 in LIU_HAI.items():
        if hour_zhi == z1 and z2 in bazi_zhis:
            result["削弱因素"].append(f"{z1}{z2}六害")

    # 调校
    adjusted = result["基础中值"]
    if result["加强因素"]:
        adjusted += 1.5  # 加一档
        result["调校说明"] = "有加强因素，中值+1.5"
    if result["削弱因素"]:
        adjusted -= 1.5  # 减一档
        result["调校说明"] = "有削弱因素，中值-1.5" if not result["加强因素"] else "同时有加强和削弱因素"
    if result["加强因素"] and result["削弱因素"]:
        adjusted = result["基础中值"]  # 抵消
        result["调校说明"] = "加强和削弱并存，基本抵消"

    result["调校后中值"] = max(adjusted, 0.5)  # 最低0.5
    return result


def calc_children_star_score(ri_zhu: str, bazi_gans: list[str], bazi_zhis: list[str], unified_stars: dict) -> dict:
    """
    第2层：子女星旺衰评分。

    SKILL.md §「子女数量三层合参法 — 第2层：子女星旺衰→子女缘分」
    """
    score = 0
    details = []
    children_stars = unified_stars["all_children_stars"]

    # 天干透出 +15
    for i, gan in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(gan, ri_zhu)
        if ss in children_stars:
            score += 15
            details.append({"项": f"{['年', '月', '日', '时'][i]}干{gan}透出{ss}", "分": 15})

    # 地支真根 +20（藏干中有子女星）
    for i, zhi in enumerate(bazi_zhis):
        for cg, ratio in DI_ZHI_CANG_GAN.get(zhi, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss in children_stars and ratio >= 60:
                score += 20
                details.append({"项": f"{['年', '月', '日', '时'][i]}支{zhi}藏{cg}为{ss}真根", "分": 20})

    # 三合/三会加强 +20
    all_zhis = bazi_zhis
    for trio, wx in SAN_HE.items():
        if all(z in all_zhis for z in trio):
            score += 20
            details.append({"项": f"{''.join(trio)}三合{wx}局加强子女星", "分": 20})
    for trio, wx in SAN_HUI.items():
        if all(z in all_zhis for z in trio):
            score += 20
            details.append({"项": f"{''.join(trio)}三会{wx}局加强子女星", "分": 20})

    # 合化走 -30 （TODO: 精确合化检测需要天干引化条件）
    for (z1, z2), wx in LIU_HE.items():
        if z1 in all_zhis and z2 in all_zhis:
            score -= 15
            details.append({"项": f"{z1}{z2}六合{wx}可能合化走子女星", "分": -15})

    # 冲/刑 -15
    for i, zhi in enumerate(bazi_zhis):
        chong = LIU_CHONG.get(zhi)
        if chong and chong in bazi_zhis:
            score -= 15
            details.append({"项": f"{zhi}{chong}冲损子女星", "分": -15})

    xing_list = check_xing(bazi_zhis)
    if xing_list:
        score -= 10
        details.append({"项": "地支刑损子女星", "分": -10})

    # 缘分判定
    if score >= 40:
        fate = "子女缘分深"
    elif score >= 20:
        fate = "中等"
    else:
        fate = "缘分薄"

    return {"得分": score, "明细": details, "判定": fate}


def calc_three_layer_fate(fertility: dict, star_score: dict, hour_shi_shen: str, ri_zhu_wx_xi_ji: str | None) -> dict:
    """
    子女数量三层合参法。

    SKILL.md §「第五步：子女数量三层合参法」
      子女缘分 = 第1层生育基准 × 第2层子女星系数 × 第3层子女宫系数

    第1层：时支类型 → 生育能力（取中值）
    第2层：子女星旺衰评分 → 缘分判定
    第3层：子女宫喜忌 → 子女质量
    """
    # 第1层
    layer1_value = fertility["调校后中值"]
    layer1_label = f"时支{fertility['时支']}生育力={layer1_value}"

    # 第2层
    score = star_score["得分"]
    if score >= 40:
        layer2_factor = 1.2  # 缘分深 → 放大
    elif score >= 20:
        layer2_factor = 1.0  # 中等 → 持平
    else:
        layer2_factor = 0.6  # 缘分薄 → 缩小
    layer2_label = f"子女星评分{score}分→系数{layer2_factor}"

    # 第3层
    if hour_shi_shen in ("正印", "正官", "食神", "正财"):
        layer3_factor = 1.1  # 喜用倾向 → 质量好
        layer3_label = f"时柱{hour_shi_shen}→子女质量好"
    elif hour_shi_shen in ("七杀", "劫财", "伤官"):
        layer3_factor = 0.8  # 忌凶倾向
        layer3_label = f"时柱{hour_shi_shen}→子女较叛逆/拖累"
    else:
        layer3_factor = 1.0
        layer3_label = f"时柱{hour_shi_shen}→中性"

    fate_count = round(layer1_value * layer2_factor * layer3_factor, 1)

    return {
        "第1层": {"值": layer1_value, "说明": layer1_label},
        "第2层": {"系数": layer2_factor, "说明": layer2_label},
        "第3层": {"系数": layer3_factor, "说明": layer3_label},
        "子女缘分值": fate_count,
        "估算范围": f"{max(0, int(fate_count - 1.5))}-{int(fate_count + 1.5)}个",
    }


def infer_child_birth_years(
    ri_zhu: str,
    gender: str,
    hour_gan: str,
    hour_zhi: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    da_yun_list: list[dict] | None = None,
    birth_year: int | None = None,
) -> dict:
    """
    子女出生年份推理。

    SKILL.md §「第三步：子女出生年份与年龄推理法」

    应期信号（按强度排序）：
      ⭐⭐⭐⭐⭐ 子女星在流年天干透出（最强）
      ⭐⭐⭐⭐ 子女宫（小时支）被伏吟/合/冲
      ⭐⭐⭐ 流年合化出子女星
      ⭐⭐ 大运子女星透干+流年配合
      ⭐ 身旺有能量生育的年份
    """
    result = {"推理依据": [], "可能年份": [], "说明": "以下年份为命理信号推测，需结合实际情况确认"}

    # 如果没提供大运，返回空
    if not da_yun_list:
        return result

    # 获取子女星列表
    unified = get_unified_children_stars(gender, ri_zhu)
    children_stars = unified["all_children_stars"]

    # 分析每个大运的流年
    for da_yun in da_yun_list:
        dy_gan = da_yun.get("gan", "") if isinstance(da_yun, dict) else da_yun.gan
        dy_zhi = da_yun.get("zhi", "") if isinstance(da_yun, dict) else da_yun.zhi
        start_year = da_yun.get("start_year", 0) if isinstance(da_yun, dict) else da_yun.start_year
        end_year = (
            da_yun.get("end_year", start_year + 9)
            if isinstance(da_yun, dict)
            else (da_yun.start_year + 9)
            if hasattr(da_yun, "start_year")
            else start_year + 9
        )
        start_age = da_yun.get("start_age", 0) if isinstance(da_yun, dict) else da_yun.start_age

        # 大运天干是否为子女星
        dy_ss = get_shi_shen_for_gan(dy_gan, ri_zhu)
        dy_has_child_star = dy_ss in children_stars

        # 检查大运范围内的各流年
        for year in range(start_year, min(end_year + 1, start_year + 15)):
            # 流年天干地支（简化：用年份计算）
            # 实际应用中需要专业万年历，这里用简化方法
            liu_nian_gan = _get_year_gan(year)
            liu_nian_zhi = _get_year_zhi(year)

            signals = []
            strength = 0

            # ⭐⭐⭐⭐⭐ 子女星在流年天干透出
            ln_ss = get_shi_shen_for_gan(liu_nian_gan, ri_zhu)
            if ln_ss in children_stars:
                signals.append(f"流年{year}天干{liu_nian_gan}={ln_ss}（子女星透出）")
                strength = max(strength, 5)

            # ⭐⭐⭐⭐ 時支被伏吟/合/冲
            if liu_nian_zhi == hour_zhi:
                signals.append(f"流年{year}地支{liu_nian_zhi}伏吟时支")
                strength = max(strength, 4)
            # 六合
            for (z1, z2), wx in LIU_HE.items():
                if (liu_nian_zhi == z1 and hour_zhi == z2) or (liu_nian_zhi == z2 and hour_zhi == z1):
                    signals.append(f"流年{year}{liu_nian_zhi}合时支{hour_zhi}（六合引动）")
                    strength = max(strength, 4)
            # 冲
            if LIU_CHONG.get(liu_nian_zhi) == hour_zhi:
                signals.append(f"流年{year}{liu_nian_zhi}冲时支{hour_zhi}（变动得子）")
                strength = max(strength, 4)

            # ⭐⭐⭐ 流年合化出子女星
            for (z1, z2), wx in LIU_HE.items():
                if liu_nian_zhi in (z1, z2):
                    other = z2 if liu_nian_zhi == z1 else z1
                    if other in bazi_zhis:
                        # 合化出的五行是否对应子女星
                        # 简化检测
                        signals.append(f"流年{year}{liu_nian_zhi}合{other}化{wx}")
                        strength = max(strength, 3)

            # ⭐⭐ 大运子女星透干+流年配合
            if dy_has_child_star:
                signals.append(f"大运{dy_gan}{dy_zhi}透{dy_ss}（十年趋势）")
                strength = max(strength, 2)

            # ⭐ 身旺有能量生育（简化为印比流年）
            liu_nian_wx = TIAN_GAN_WU_XING[liu_nian_gan]
            ri_wx = TIAN_GAN_WU_XING[ri_zhu]
            if liu_nian_wx == ri_wx or WU_XING_SHENG.get(liu_nian_wx) == ri_wx:
                signals.append(f"流年{year}{liu_nian_gan}帮身（有能量生育）")
                strength = max(strength, 1)

            if signals and strength >= 3:
                age = year - birth_year if birth_year else start_age + (year - start_year)
                result["可能年份"].append(
                    {
                        "年份": year,
                        "年龄": age if age > 0 else start_age + (year - start_year),
                        "信号强度": strength,
                        "信号": signals,
                    }
                )

    # 按信号强度排序
    result["可能年份"].sort(key=lambda x: -x["信号强度"])
    result["推理依据"] = [s[1] for s in FERTILITY_WINDOW_SIGNALS]

    return result


def _get_year_gan(year: int) -> str:
    """根据年份获取天干（简化版，非精确节气）"""
    gan_idx = (year - 4) % 10
    return TIAN_GAN[gan_idx]


def _get_year_zhi(year: int) -> str:
    """根据年份获取地支（简化版）"""
    zhi_idx = (year - 4) % 12
    return DI_ZHI[zhi_idx]


def check_thin_fate_factors(
    ri_zhu: str,
    gender: str,
    hour_gan: str,
    hour_zhi: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    unified_stars: dict,
    shen_label: str | None = None,
) -> dict:
    """
    子女缘薄因素排查。

    SKILL.md §「第六步：子女缘薄因素」
    """
    factors = []

    # 日时冲
    ri_zhi = bazi_zhis[2]  # 日支
    if LIU_CHONG.get(ri_zhi) == hour_zhi:
        factors.append(
            {"因素": "日时冲", "说明": f"日支{ri_zhi}冲时支{hour_zhi}，与子女缘分薄，或子女不在身边", "严重": True}
        )

    # 时支劫财
    hour_shi_shen = get_shi_shen_for_gan(hour_gan, ri_zhu)
    if hour_shi_shen == "劫财":
        factors.append({"因素": "时支劫财", "说明": "时干为劫财，克子女，或子女破家", "严重": True})

    # 子女星空亡（简化检测）
    children_stars = unified_stars["all_children_stars"]
    star_scan = scan_children_stars_in_bazi(ri_zhu, bazi_gans, bazi_zhis, children_stars)
    if star_scan["缺失"]:
        factors.append({"因素": "命局无子女星", "说明": "八字中无子女星，缘分极薄", "严重": True})

    # 时柱空亡（简化检测）
    # 空亡 = 旬空。甲子旬戌亥空，甲戌旬申酉空...
    # 简化：不精确计算，仅标记
    factors.append(
        {"因素": "时柱空亡", "说明": "需结合具体日柱计算旬空（简化检测），时柱空亡则晚年孤独", "严重": False}
    )

    # 子女星被合化
    for (z1, z2), wx in LIU_HE.items():
        if z1 in bazi_zhis and z2 in bazi_zhis:
            factors.append({"因素": "子女星被合化", "说明": f"{z1}{z2}六合化{wx}，可能合化走子女星能量", "严重": True})
            break

    # 全局缺水
    all_wx = [DI_ZHI_WU_XING[z] for z in bazi_zhis] + [TIAN_GAN_WU_XING[g] for g in bazi_gans]
    if "水" not in all_wx:
        factors.append({"因素": "全局缺水", "说明": "八字全局无水，生殖系统偏弱", "严重": False})

    # 时支阳刃（简化：阳刃=帝旺）
    hour_zhi_wx = DI_ZHI_WU_XING[hour_zhi]
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    # 阳刃条件较复杂，简化检测
    if _is_yang_gan(ri_zhu):
        # 阳干帝旺在...
        yang_ren_zhi = {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子"}
        if hour_zhi == yang_ren_zhi.get(ri_zhu):
            factors.append({"因素": "时支阳刃", "说明": f"时支{hour_zhi}为日主{ri_zhu}之阳刃，难产之象", "严重": True})

    # 印旺制食伤
    yin_count = 0
    shi_shang_count = 0
    for gan in bazi_gans:
        ss = get_shi_shen_for_gan(gan, ri_zhu)
        if ss in ("正印", "偏印"):
            yin_count += 1
        if ss in ("食神", "伤官"):
            shi_shang_count += 1
    if yin_count >= 2 and gender == "女":
        factors.append({"因素": "印旺制食伤", "说明": f"天干{yin_count}个印星克制食伤，不容易受孕", "严重": True})

    return {"因素列表": factors, "严重因素数": sum(1 for f in factors if f["严重"]), "总因素数": len(factors)}


def check_fertility_windows(
    gender: str,
    ri_zhu: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    hour_zhi: str,
    da_yun_list: list | None = None,
    age_range: tuple = (20, 45),
) -> dict:
    """
    生育窗口排查。

    SKILL.md §「第七步：生育窗口排查」
      女命遇食伤年 → 生育窗口
      男命遇官杀年 → 生育窗口
      流年合化出强子女星 → 生育窗口
      子女星被解合 → 生育窗口
      子女宫被加强 → 生育窗口
    """
    windows = []
    unified = get_unified_children_stars(gender, ri_zhu)

    # 女命窗口十神
    if gender == "女":
        window_shi_shens = ["食神", "伤官"]
    else:
        window_shi_shens = ["正官", "七杀"]

    # 如果有大运信息，分析未来年份
    if da_yun_list:
        for da_yun in da_yun_list:
            start_year = da_yun.get("start_year", 0) if isinstance(da_yun, dict) else da_yun.start_year
            end_year = da_yun.get("end_year", start_year + 9) if isinstance(da_yun, dict) else (da_yun.start_year + 9)

            for year in range(start_year, min(end_year + 1, 2050)):
                ln_gan = _get_year_gan(year)
                ln_zhi = _get_year_zhi(year)
                ln_ss = get_shi_shen_for_gan(ln_gan, ri_zhu)

                reasons = []

                # 女命遇食伤年 / 男命遇官杀年
                if ln_ss in window_shi_shens:
                    reasons.append(f"流年{ln_gan}={ln_ss}（{'女命食伤' if gender == '女' else '男命官杀'}年）")

                # 子女宫（时支）被加强
                if ln_zhi == hour_zhi:
                    reasons.append(f"流年{ln_zhi}伏吟时支")
                for (z1, z2), wx in LIU_HE.items():
                    if (ln_zhi == z1 and hour_zhi == z2) or (ln_zhi == z2 and hour_zhi == z1):
                        reasons.append(f"流年{ln_zhi}合时支{hour_zhi}")

                # 流年合化出子女星
                children_stars = unified["all_children_stars"]
                for (z1, z2), wx in LIU_HE.items():
                    if ln_zhi in (z1, z2):
                        other = z2 if ln_zhi == z1 else z1
                        if other in bazi_zhis:
                            reasons.append(f"流年{ln_zhi}合{other}化{wx}")

                if reasons:
                    windows.append({"年份": year, "原因": reasons})

        # 去重
        seen_years = set()
        unique_windows = []
        for w in windows:
            if w["年份"] not in seen_years:
                seen_years.add(w["年份"])
                unique_windows.append(w)
        windows = unique_windows
        windows.sort(key=lambda x: x["年份"])

    return {
        "窗口年份": windows[:30],  # 最多30个
        "窗口条件": window_shi_shens,
        "总窗口数": len(windows),
    }


def check_twin_conditions(bazi_zhis: list[str]) -> list[dict]:
    """
    双胞胎条件检查。

    SKILL.md §「生双胞胎条件」:
      丑未戌三刑（15倍）
      寅卯辰三会（20倍）
      巳午未三会（20倍）
      辰午酉亥自刑（10倍）
    """
    conditions = []

    # 丑未戌三刑
    has_chou = "丑" in bazi_zhis
    has_wei = "未" in bazi_zhis
    has_xu = "戌" in bazi_zhis
    if has_chou and has_wei and has_xu:
        conditions.append({"条件": "丑未戌三刑", "倍数": 15, "说明": "子女星能量被极其加强，可能双胞胎"})

    # 寅卯辰三会
    has_yin = "寅" in bazi_zhis
    has_mao = "卯" in bazi_zhis
    has_chen = "辰" in bazi_zhis
    if has_yin and has_mao and has_chen:
        conditions.append({"条件": "寅卯辰三会木局", "倍数": 20, "说明": "可能多胞胎"})

    # 巳午未三会
    has_si = "巳" in bazi_zhis
    has_wu = "午" in bazi_zhis
    if has_si and has_wu and has_wei:
        conditions.append({"条件": "巳午未三会火局", "倍数": 20, "说明": "可能多胞胎"})

    # 辰午酉亥自刑（至少两个自刑出现）
    zi_xing_count = sum(1 for z in bazi_zhis if z in ("辰", "午", "酉", "亥") and bazi_zhis.count(z) >= 2)
    if zi_xing_count >= 1:
        conditions.append({"条件": "辰午酉亥自刑", "倍数": 10, "说明": "可能双胞胎"})

    return conditions


def judge_child_achievement(hour_gan: str, hour_zhi: str, ri_zhu: str) -> dict:
    """
    子女成就判断。

    SKILL.md §「第八步：子女成就判断」
      时柱十神定子女方向
    """
    hour_shi_shen = get_shi_shen_for_gan(hour_gan, ri_zhu)
    direction = SHI_ZHU_TEN_GOD_CHILD_DIRECTION.get(hour_shi_shen, "普通")

    result = {"时干": hour_gan, "时支": hour_zhi, "时柱十神": hour_shi_shen, "子女方向": direction}

    # 时支藏干也分析
    cang_gan_info = []
    for cg, ratio in DI_ZHI_CANG_GAN.get(hour_zhi, []):
        cg_ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        cg_dir = SHI_ZHU_TEN_GOD_CHILD_DIRECTION.get(cg_ss, "")
        if cg_dir:
            cang_gan_info.append({"藏干": cg, "十神": cg_ss, "含义": cg_dir})
    result["藏干信息"] = cang_gan_info

    return result


def check_shi_zhu_qi_sha_you_zhi(
    ri_zhu: str,
    gender: str,
    hour_gan: str,
    hour_zhi: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    shen_label: str | None = None,
) -> dict:
    """
    时柱七杀有制生子规则。

    SKILL.md §「🆕 时柱七杀有制生子规则（2026-06-25·九龙道长公众号文章校准）」

    规则：
      时柱七杀有制→晚年生贵子
      七杀无根或制杀过重→子女缘薄

      男命阳日主 + 时柱七杀有制 → 得子
      男命阴日主 + 时柱七杀有制 → 得女
      女命阳日主 + 时柱七杀有制 → 得女
      女命阴日主 + 时柱七杀有制 → 得子
    """
    result = {"适用": False, "七杀有无": False, "七杀有制": False, "判定": "", "详细": ""}

    # 检查时柱是否有七杀
    hour_ss = get_shi_shen_for_gan(hour_gan, ri_zhu)
    has_qi_sha_in_hour = hour_ss == "七杀"

    # 也检查时支藏干
    for cg, ratio in DI_ZHI_CANG_GAN.get(hour_zhi, []):
        cg_ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if cg_ss == "七杀":
            has_qi_sha_in_hour = True

    if not has_qi_sha_in_hour:
        result["适用"] = False
        result["说明"] = "时柱无七杀，此规则不适用"
        return result

    result["七杀有无"] = True

    # 检查七杀是否有制
    # 有制条件：天干有食神制/印化/羊刃合杀
    has_zhi = False
    zhi_methods = []

    for gan in bazi_gans:
        ss = get_shi_shen_for_gan(gan, ri_zhu)
        if ss == "食神":
            has_zhi = True
            zhi_methods.append(f"天干{gan}食神制杀")
        if ss in ("正印", "偏印"):
            has_zhi = True
            zhi_methods.append(f"天干{gan}印化杀")
        if ss == "劫财" and _is_yang_gan(ri_zhu):
            has_zhi = True
            zhi_methods.append(f"天干{gan}羊刃合杀")

    # 检查地支合杀
    # 寅午戌合火（七杀为火时）等
    # 简化处理

    result["七杀有制"] = has_zhi
    result["制杀方式"] = zhi_methods if zhi_methods else ["无制"]

    # 判定
    is_yang = _is_yang_gan(ri_zhu)
    if has_zhi:
        if gender == "男":
            if is_yang:
                result["判定"] = "男命阳日主+时柱七杀有制→得子（晚年生贵子）"
            else:
                result["判定"] = "男命阴日主+时柱七杀有制→得女"
        else:
            if is_yang:
                result["判定"] = "女命阳日主+时柱七杀有制→得女"
            else:
                result["判定"] = "女命阴日主+时柱七杀有制→得子（晚年生贵子）"
        result["详细"] = "时柱七杀有制→晚年生贵子。" + "。".join(zhi_methods)
    else:
        result["判定"] = "时柱七杀无根或无制→子女缘薄"
        result["详细"] = "时柱七杀无根或制杀过重→终身贫困，子女缘薄"

    return result


def check_shi_zhu_zheng_guan_effect(
    ri_zhu: str, hour_gan: str, hour_zhi: str, bazi_gans: list[str], shen_label: str | None = None
) -> dict:
    """
    时柱正官对子女的影响规则。

    SKILL.md §「🆕 时柱正官对子女的影响（2026-06-25·九龙道长公众号校准）」
    """
    result = {"适用": False, "判定": "", "正官组合": "", "吉凶": ""}

    hour_ss = get_shi_shen_for_gan(hour_gan, ri_zhu)
    if hour_ss != "正官":
        result["适用"] = False
        result["说明"] = "时干非正官，此规则不适用"
        return result

    result["适用"] = True

    # 检查组合
    # 时干正官+身旺
    if shen_label and "身强" in shen_label:
        result["正官组合"] = "时杀正官+身旺"
        result["判定"] = "子女得力，老而安乐"
        result["吉凶"] = "吉"
    elif shen_label and "从强" in shen_label:
        result["正官组合"] = "时干正官+归禄（从强）"
        result["判定"] = "晚年衣食无忧，后人发达"
        result["吉凶"] = "吉"

    # 时干正官+伤官
    has_shang_guan = False
    has_shi_shen = False
    has_qi_sha = False
    for gan in bazi_gans:
        ss = get_shi_shen_for_gan(gan, ri_zhu)
        if ss == "伤官":
            has_shang_guan = True
        if ss == "食神":
            has_shi_shen = True
        if ss == "七杀":
            has_qi_sha = True

    if has_shang_guan:
        result["正官组合"] = "时干正官+伤官"
        result["判定"] = "子女有伤亡之兆"
        result["吉凶"] = "凶"
    elif has_shi_shen:
        result["正官组合"] = "时干正官+食神"
        result["判定"] = "晚年财旺，子女有良缘"
        result["吉凶"] = "吉"
    elif has_qi_sha:
        result["正官组合"] = "时干正官+七杀"
        result["判定"] = "官杀过旺，出不肖之子"
        result["吉凶"] = "凶"

    if not result["判定"]:
        # 默认：时干正官+无特殊组合
        zhi_wx = DI_ZHI_WU_XING[hour_zhi]
        if zhi_wx == TIAN_GAN_WU_XING[ri_zhu]:
            result["正官组合"] = "时干正官+归禄"
            result["判定"] = "晚年衣食无忧，后人发达"
            result["吉凶"] = "吉"
        else:
            result["正官组合"] = "时干正官"
            result["判定"] = "子女得力（需结合身旺程度）"
            result["吉凶"] = "吉"

    return result


def check_parent_joint_rules(
    father_ri_zhu: str | None,
    mother_ri_zhu: str | None,
    father_bazi_gans: list[str] | None,
    father_bazi_zhis: list[str] | None,
    mother_bazi_gans: list[str] | None,
    mother_bazi_zhis: list[str] | None,
    father_birth_year: int | None = None,
    mother_birth_year: int | None = None,
) -> dict:
    """
    父母合参子女规律。

    SKILL.md §「父母合参子女规律」

    规律①：父母同频
    规律②：帮身是生育前提
    规律③：子女星引动 + 有能量 = 应期
    规律④：交叉引动法
    """
    result = {"合参结论": "", "父母同频": False, "帮身前提": [], "交叉引动": [], "口诀": PARENT_JOINT_RHYME}

    # 规律①：父母同频
    if father_ri_zhu and mother_ri_zhu and father_ri_zhu == mother_ri_zhu:
        result["父母同频"] = True
        result["合参结论"] += "父母日主相同→命理同频，子女应期在双方命盘上都有信号。"
    elif father_ri_zhu and mother_ri_zhu:
        ri_wx_f = TIAN_GAN_WU_XING[father_ri_zhu]
        ri_wx_m = TIAN_GAN_WU_XING[mother_ri_zhu]
        if ri_wx_f == ri_wx_m:
            result["父母同频"] = True
            result["合参结论"] += "父母日主五行相同→命理同频。"

    # 规律②：帮身是生育前提
    # 印星/比劫帮身的年份最容易有子女
    if father_bazi_gans:
        help_elements = []
        for gan in father_bazi_gans:
            if father_ri_zhu:
                ss = get_shi_shen_for_gan(gan, father_ri_zhu)
                if ss in ("正印", "偏印", "比肩", "劫财"):
                    help_elements.append(gan)
        result["帮身前提"].append({"来源": "父命", "帮身十神": help_elements})

    if mother_bazi_gans and mother_ri_zhu:
        help_elements = []
        for gan in mother_bazi_gans:
            ss = get_shi_shen_for_gan(gan, mother_ri_zhu)
            if ss in ("正印", "偏印", "比肩", "劫财"):
                help_elements.append(gan)
        result["帮身前提"].append({"来源": "母命", "帮身十神": help_elements})

    # 规律④：交叉引动
    # 同一流年双方都有反应→应期更准
    result["合参结论"] = result["合参结论"] or "父母合参需要双方八字数据"

    return result


def consistency_check(report: dict) -> dict:
    """
    逻辑一致性门禁。

    SKILL.md §「🚨 逻辑一致性门禁（2026-06-15新增）」

    检查项：
    □ 子女顺序与文字描述一致吗？
    □ 子女数量前后一致吗？
    □ "长子/长女"的称谓与已有子女数一致吗？
    □ 子女出生年份与命主生育年龄合理吗？
    □ 子女推断与实际数据不冲突
    """
    issues = []
    warnings = []

    # 提取数据
    child_count_estimate = report.get("三层合参", {}).get("子女缘分值", 0)
    child_count_range = report.get("三层合参", {}).get("估算范围", "未知")

    # 检查子女数量一致性
    if child_count_estimate > 10:
        issues.append(f"子女缘分值{child_count_estimate}过高，需结合现实确认")

    # 检查称谓
    birth_years = report.get("出生年份推理", {}).get("可能年份", [])
    if len(birth_years) >= 2:
        # 如果有2+个年份，第一个不能叫"长子"如果前面已有
        pass  # 具体称谓需用户数据

    # 生育年龄检查
    if birth_years:
        ages = [y.get("年龄", 0) for y in birth_years[:3]]
        for age in ages:
            if 0 < age < 15:
                issues.append(f"生育年龄{age}岁不合理（<15岁）")
            elif age > 50:
                warnings.append(f"生育年龄{age}岁偏高（>50岁概率低）")

    result = {
        "通过": len(issues) == 0,
        "问题": issues,
        "警告": warnings,
        "口诀": "出报告前过三关，子女数量要一致；前面有子不叫长，出生年龄要合理。",
    }
    return result


# ════════════════════════════════════════════════════════════════
# 主入口函数
# ════════════════════════════════════════════════════════════════


def analyze_children_full(
    ri_zhu: str,
    gender: str,
    hour_gan: str,
    hour_zhi: str,
    bazi_gans: list[str],
    bazi_zhis: list[str],
    da_yun_list: list | None = None,
    shen_label: str | None = None,
    birth_year: int | None = None,
    father_ri_zhu: str | None = None,
    mother_ri_zhu: str | None = None,
    actual_children: list[dict] | None = None,
) -> dict:
    """
    子女/生育完整分析主入口。

    SKILL.md §「完整判断流程（10步）」

    参数：
      ri_zhu: 日主天干（如"甲"）
      gender: "男"或"女"
      hour_gan: 时柱天干
      hour_zhi: 时柱地支
      bazi_gans: 四柱天干列表 [年,月,日,时]
      bazi_zhis: 四柱地支列表 [年,月,日,时]
      da_yun_list: 大运列表 [{"gan":"","zhi":"","start_age":0,"start_year":0}, ...]
      shen_label: 身强弱标签（如"身强"）
      birth_year: 出生年份（用于计算生育年龄）
      father_ri_zhu: 父亲的日主（合参用）
      mother_ri_zhu: 母亲的日主（合参用）
      actual_children: 实际子女数据，用于校准

    返回：
      dict: 完整的子女分析结果
    """
    # ── Step 0: 子女星定位 ──
    unified_stars = get_unified_children_stars(gender, ri_zhu)

    # ── Step 1: 扫八字子女星 ──
    star_scan = scan_children_stars_in_bazi(ri_zhu, bazi_gans, bazi_zhis, unified_stars["all_children_stars"])

    # ── Step 2: 十二长生基数法 ──
    chang_sheng = get_twelve_chang_sheng_base(gender, ri_zhu, hour_zhi, unified_stars)

    # ── Step 3: 时支生育力 ──
    fertility = get_shi_zhi_fertility(hour_zhi, bazi_zhis)

    # ── Step 4: 子女星评分 ──
    star_score = calc_children_star_score(ri_zhu, bazi_gans, bazi_zhis, unified_stars)

    # ── Step 5: 时柱十神 ──
    hour_shi_shen = get_shi_shen_for_gan(hour_gan, ri_zhu)

    # ── Step 6: 三层合参 ──
    three_layer = calc_three_layer_fate(fertility, star_score, hour_shi_shen, None)

    # ── Step 7: 出生年份推理 ──
    birth_year_inference = infer_child_birth_years(
        ri_zhu, gender, hour_gan, hour_zhi, bazi_gans, bazi_zhis, da_yun_list, birth_year
    )

    # ── Step 8: 缘薄因素 ──
    thin_fate = check_thin_fate_factors(
        ri_zhu, gender, hour_gan, hour_zhi, bazi_gans, bazi_zhis, unified_stars, shen_label
    )

    # ── Step 9: 生育窗口 ──
    fertility_windows = check_fertility_windows(gender, ri_zhu, bazi_gans, bazi_zhis, hour_zhi, da_yun_list)

    # ── Step 10: 双胞胎条件 ──
    twin_conditions = check_twin_conditions(bazi_zhis)

    # ── Step 11: 子女成就 ──
    achievement = judge_child_achievement(hour_gan, hour_zhi, ri_zhu)

    # ── Step 12: 时柱七杀有制 ──
    qi_sha_rule = check_shi_zhu_qi_sha_you_zhi(ri_zhu, gender, hour_gan, hour_zhi, bazi_gans, bazi_zhis, shen_label)

    # ── Step 13: 时柱正官影响 ──
    zheng_guan_effect = check_shi_zhu_zheng_guan_effect(ri_zhu, hour_gan, hour_zhi, bazi_gans, shen_label)

    # ── Step 14: 父母合参 ──
    parent_joint = check_parent_joint_rules(
        father_ri_zhu=father_ri_zhu,
        mother_ri_zhu=mother_ri_zhu,
        father_bazi_gans=bazi_gans,
        father_bazi_zhis=bazi_zhis,
        mother_bazi_gans=None,
        mother_bazi_zhis=None,
    )

    # ── 构建报告 ──
    report = {
        "基础信息": {"日主": ri_zhu, "性别": gender, "时柱": f"{hour_gan}{hour_zhi}", "时柱十神": hour_shi_shen},
        "子女星定位": {
            "流派A": unified_stars["school_a"],
            "流派B": unified_stars["school_b"],
            "两派一致": unified_stars["consensus"],
            "儿子星": unified_stars["son_stars"],
            "女儿星": unified_stars["daughter_stars"],
            "八字扫描": star_scan,
        },
        "十二长生基数": chang_sheng,
        "时支生育力": fertility,
        "子女星评分": star_score,
        "三层合参": three_layer,
        "出生年份推理": birth_year_inference,
        "缘薄因素": thin_fate,
        "生育窗口": fertility_windows,
        "双胞胎条件": twin_conditions,
        "子女成就": achievement,
        "时柱七杀有制规则": qi_sha_rule,
        "时柱正官影响": zheng_guan_effect,
        "父母合参": parent_joint,
    }

    # ── Step 15: 逻辑一致性门禁 ──
    consistency = consistency_check(report)
    report["逻辑一致性"] = consistency

    # ── 简明总结 ──
    summary_parts = []

    # 子女数量
    summary_parts.append(f"子女缘分估算：{three_layer['估算范围']}")
    summary_parts.append(f"子女星评分：{star_score['得分']}分（{star_score['判定']}）")
    summary_parts.append(f"十二长生基数：{chang_sheng['主基数']}（{chang_sheng['主状态']}）")

    if thin_fate["严重因素数"] > 0:
        summary_parts.append(f"⚠️ 存在{thin_fate['严重因素数']}个严重缘薄因素")

    if qi_sha_rule.get("适用"):
        summary_parts.append(qi_sha_rule["判定"])

    if zheng_guan_effect.get("适用"):
        summary_parts.append(f"时柱正官：{zheng_guan_effect['判定']}")

    report["简明总结"] = "；".join(summary_parts)

    return report


# ════════════════════════════════════════════════════════════════
# 测试
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 测试用例：父亲（己丑 癸酉 癸亥 戊午）
    # SKILL.md 实战案例
    result = analyze_children_full(
        ri_zhu="癸",
        gender="男",
        hour_gan="戊",
        hour_zhi="午",
        bazi_gans=["己", "癸", "癸", "戊"],
        bazi_zhis=["丑", "酉", "亥", "午"],
        da_yun_list=[],
        birth_year=1950,
    )

    import json

    print(json.dumps(result, ensure_ascii=False, indent=2))
