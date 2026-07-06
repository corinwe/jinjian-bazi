"""
金鉴真人·流年精准断事引擎 v2.1 — 全量事件断法（宫位+四要素+分时段+干透干藏+五行类象）

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

断语四要素:
  {事件类型}: {六亲}的{身体}方面，{程度}，{应期}

分时段断事（R31）:
  - 上半年（1-6月）：天干主导70%
  - 下半年（7-12月）：地支主导70%

宫位·身体·六亲对应体系（R25）:
  - 年柱应事 → 祖上/长辈 + 头部/大脑/眼睛
  - 月柱应事 → 父母/兄弟姐妹 + 胸部/肩颈/心肺
  - 日柱应事 → 配偶/自身 + 腹部/腰肾/生殖
  - 时柱应事 → 子女/下属 + 腿部/足部/关节

干透干藏应事规则（R35）:
  - 比劫透干 + 身强 → 他人劫夺/竞争失利
  - 比劫透干 + 身弱 → 朋友帮身/合作顺利

地支五行类象逢冲应事（R36）:
  - 土（辰戌丑未）冲 → 住宅变动/房地产变化/搬迁
  - 寅申巳亥冲 → 职业变化/工作调动/远行
  - 子午卯酉冲 → 权力变化/地位变动/情感纠纷
"""

from __future__ import annotations

from constants import DI_ZHI_WU_XING, TIAN_GAN_WU_XING, WU_XING_KE, WU_XING_SHENG
from shen_qiang_ruo import compute_shen_qiang_ruo
from shen_sha import compute_all_shen_sha
from shi_shen import get_shi_shen_for_gan
from xing_chong_he_hua import (
    check_all_relations,
    check_all_relations_v2,
    check_chong,
    check_liu_he,
    check_san_hui,
    _get_kong_wang,
    SAN_HUI,
)

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

# ── R39: 恶神×能量级别对应表 ──
E_SHEN_LEVEL = {
    "七杀": {
        1: "压力/罚单/小人口舌",
        3: "纠纷/病痛/破财",
        10: "官非/重伤/大破财",
        15: "横死/猝死/重大灾祸",
    },
    "伤官": {
        1: "口舌/误解",
        3: "官非/失业",
        10: "官司/名声扫地",
    },
}

# ── R40: 神煞系统 vs 十神系统界限 ──
# 天乙贵人等神煞只能解神煞类灾祸（灾煞/血刃），不能解十神类灾祸（七杀/枭神夺食）
SHEN_SHA_BOUNDARY_NOTE = "【神煞界限】天乙贵人等只能化解神煞类灾祸（灾煞/血刃/劫煞），不能化解十神系统灾祸（七杀/枭神夺食/伤官见官）"

# ── 宫位·身体·六亲对应体系（R25） ──
GONG_WEI_MAP = {
    0: {"六亲": "祖上/父母", "身体": "头部/大脑/眼睛"},
    1: {"六亲": "父母/兄弟姐妹", "身体": "胸部/肩颈/心肺"},
    2: {"六亲": "配偶/自身", "身体": "腹部/腰肾/生殖"},
    3: {"六亲": "子女/下属", "身体": "腿部/足部/关节"},
}

PILLAR_NAMES = ["年柱", "月柱", "日柱", "时柱"]

# ── 地支五行类象逢冲应事（R36） ──
# 寅申巳亥 → 驿马类 → 职业变化
YI_MA_ZHI = {"寅", "申", "巳", "亥"}
# 子午卯酉 → 桃花类 → 权力/情感
TAO_HUA_ZHI = {"子", "午", "卯", "酉"}
# 辰戌丑未 → 土类 → 住宅
TU_ZHI = {"辰", "戌", "丑", "未"}

CHONG_WU_XING_LEI_XIANG = {
    "土": "住宅变动/房地产变化/搬迁",
    "驿马": "职业变化/工作调动/远行",
    "桃花": "权力变化/地位变动/情感纠纷",
}

# ── 恶神能量级别对应表（R39） ──
# 来源：skill §12.8 恶神能量表
# 数字为原局中该恶神的数量阈值
E_SHEN_LEVEL = {
    "七杀": {20: "横死猝死(20倍)", 10: "重病手术(10倍)", 7: "官非牢狱(7倍)", 3: "压力/罚单(3倍)", 1: "小麻烦(1倍)"},
    "伤官": {10: "官非破财(10倍)", 7: "口舌是非(7倍)", 3: "言语冲突(3倍)", 1: "不满情绪(1倍)"},
    "枭印": {10: "精神异常(10倍)", 7: "思维混乱(7倍)", 3: "焦虑多疑(3倍)", 1: "灵感波动(1倍)"},
    "劫财": {10: "破财破产(10倍)", 7: "合作破裂(7倍)", 3: "小破财(3倍)", 1: "应酬多(1倍)"},
}

# 神煞 vs 十神系统界限（R40）
SHEN_SHA_BOUNDARY_NOTE = "（天乙贵人不能解十神系统恶神，仅解神煞系统）"


# ── 流月映射表（R26） ──
MONTH_GAN_ZHI = {
    1: "甲寅", 2: "乙卯", 3: "丙辰", 4: "丁巳", 5: "戊午", 6: "己未",
    7: "庚申", 8: "辛酉", 9: "壬戌", 10: "癸亥", 11: "甲子", 12: "乙丑",
}

# ── 合化优先级（R14补充）──
# 三会(20倍) > 三合(15倍) > 半合/六合(10倍) > 拱合(10倍) > 暗合
HE_HUA_PRIORITY = {"三会": 4, "三合": 3, "六合": 2, "半合": 2, "拱合": 2, "暗合": 1}

# ── 犯太岁体系（原 liu_nian.py 内联，2026-07-05 旧版归档）──
FAN_TAI_SUI = {
    "值太岁": 1.0,  # 本命年
    "冲太岁": 1.2,  # 六冲
    "刑太岁": 1.0,  # 三刑
    "害太岁": 0.8,  # 六害
    "破太岁": 0.6,  # 六破
}


def check_fan_tai_sui(year_zhi: str, liu_nian_zhi: str) -> tuple[str, float] | None:
    """检查犯太岁"""
    from xing_chong_he_hua import LIU_CHONG, LIU_HAI, LIU_PO, SAN_XING

    # 值太岁（本命年）
    if liu_nian_zhi == year_zhi:
        return ("值太岁", FAN_TAI_SUI["值太岁"])
    # 冲太岁
    if LIU_CHONG.get(year_zhi) == liu_nian_zhi:
        return ("冲太岁", FAN_TAI_SUI["冲太岁"])
    # 刑太岁
    if year_zhi in SAN_XING and liu_nian_zhi in SAN_XING[year_zhi]:
        return ("刑太岁", FAN_TAI_SUI["刑太岁"])
    # 害太岁
    if LIU_HAI.get(year_zhi) == liu_nian_zhi:
        return ("害太岁", FAN_TAI_SUI["害太岁"])
    # 破太岁
    if (year_zhi, liu_nian_zhi) in LIU_PO or (liu_nian_zhi, year_zhi) in LIU_PO:
        return ("破太岁", FAN_TAI_SUI["破太岁"])
    return None


def _get_key_months(liu_nian_wx_gan: str, liu_nian_wx_zhi: str, xi_yong: list[str], ji_shen: list[str]) -> str:
    """R26: 根据流年干支五行和喜忌，标注关键应事月份"""
    from constants import TIAN_GAN_WU_XING, DI_ZHI_WU_XING

    key_months = []
    for month_num, month_gz in MONTH_GAN_ZHI.items():
        mg = month_gz[0]  # 月天干
        mz = month_gz[1]  # 月地支
        mg_wx = TIAN_GAN_WU_XING[mg]
        mz_wx = DI_ZHI_WU_XING[mz]

        # 月份的天干/地支五行与流年天干/地支五行相同 → 能量共振
        if mg_wx == liu_nian_wx_gan or mz_wx == liu_nian_wx_zhi:
            key_months.append(month_num)

    if not key_months:
        return ""

    # 取前3个关键月份（最多3个）
    key_str = "、".join(str(m) for m in key_months[:3])
    return f"重点月份：{key_str}月"


def _da_yun_dual_dimension(
    da_yun_gan: str, da_yun_zhi: str, ri_zhu: str, ri_zhu_wx: str,
    xi_yong: list[str], shen_label: str,
) -> str:
    """R43: 大运定性双维度原则
    - 能量层面：用神大运=能量得到补充
    - 感受层面：用神大运≠舒服大运，可能伴随挑战
    """
    from constants import TIAN_GAN_WU_XING
    from shi_shen import get_shi_shen_for_gan

    dy_gan_wx = TIAN_GAN_WU_XING[da_yun_gan] if da_yun_gan else ""
    dy_zhi_wx = TIAN_GAN_WU_XING.get(da_yun_zhi, "")

    # 能量层面
    is_xi_da_yun = dy_gan_wx in xi_yong or dy_zhi_wx in xi_yong
    if is_xi_da_yun:
        energy_effect = "能量得到补充（用神大运）"
    else:
        energy_effect = "能量消耗（非用神大运）"

    # 感受层面
    dy_shi_shen = get_shi_shen_for_gan(da_yun_gan, ri_zhu) if da_yun_gan else ""
    if is_xi_da_yun:
        if dy_shi_shen in ["七杀", "伤官", "劫财"]:
            feeling_effect = "虽是用神但感受挑战（七杀/伤官/劫财类用神）"
        elif dy_shi_shen in ["正印", "偏印", "正官"]:
            feeling_effect = "用神到位且感受相对舒适"
        else:
            feeling_effect = "用神大运，感受偏正面"
    else:
        if shen_label == "身弱":
            feeling_effect = "非用神大运，身弱难担"
        else:
            feeling_effect = "非用神大运，需主动调整"

    return f"大运{da_yun_gan}{da_yun_zhi}: 能量层面{energy_effect}，感受层面{feeling_effect}"


def _five_dimensional_da_yun_score(
    da_yun_gan: str, da_yun_zhi: str,
    ri_zhu: str, ri_zhu_wx: str,
    xi_yong: list[str], ji_shen: list[str],
    all_gans: list[str], all_zhis: list[str],
    shen_label: str,
) -> dict:
    """R44: 最佳大运综合判断法五维评分

    五维:
    1. 表面十神 — 大运天干的十神对日主的影响
    2. 合局引化 — 三合/六合加强（大运与原局发生合化）
    3. 空亡 — 空亡减半
    4. 神煞 — 天乙/文昌加分
    5. 十二长生 — 临官/帝旺加分
    """
    from constants import TIAN_GAN_WU_XING, DI_ZHI_WU_XING
    from shi_shen import get_shi_shen_for_gan

    scores = {}
    total = 0.0

    # ── 维度1: 表面十神（权重3）──
    dy_shi_shen = get_shi_shen_for_gan(da_yun_gan, ri_zhu) if da_yun_gan else ""
    dy_wx = TIAN_GAN_WU_XING[da_yun_gan] if da_yun_gan else ""

    shen_score = 0
    if dy_shi_shen in ["正印", "偏印", "正官"] and dy_wx in xi_yong:
        shen_score = 3  # 吉神喜用
    elif dy_shi_shen in ["正财", "偏财", "食神"] and dy_wx in xi_yong:
        shen_score = 2  # 财食喜用
    elif dy_shi_shen in ["七杀", "伤官", "劫财"] and dy_wx in xi_yong:
        shen_score = 1  # 恶神但喜用
    elif dy_wx in ji_shen:
        shen_score = -2  # 忌神
    else:
        shen_score = 0
    scores["表面十神"] = {"score": shen_score, "weight": 3, "desc": dy_shi_shen}
    total += shen_score * 3

    # ── 维度2: 合局引化（权重2）──
    from xing_chong_he_hua import check_all_relations_v2
    rels_v2 = check_all_relations_v2([da_yun_zhi] + all_zhis[:4], [da_yun_gan] + all_gans[:4])

    he_score = 0
    he_desc_parts = []
    # 三会（最高优先级）
    if rels_v2.get("三会"):
        for h in rels_v2["三会"]:
            he_score += 3
            he_desc_parts.append(h["type"])
    # 三合
    if rels_v2.get("三合"):
        for h in rels_v2["三合"]:
            he_score += 2
            he_desc_parts.append(h["type"])
    # 六合/半合
    if rels_v2.get("六合"):
        he_score += 1
        he_desc_parts.append("六合")
    he_score = min(he_score, 5)
    scores["合局引化"] = {"score": he_score, "weight": 2, "desc": "、".join(he_desc_parts) if he_desc_parts else "无合局"}
    total += he_score * 2

    # ── 维度3: 空亡（权重2）──
    kong = _check_da_yun_kong_wang(da_yun_zhi, ri_zhu, all_zhis[2])
    kong_score = -2 if kong else 0
    scores["空亡"] = {"score": kong_score, "weight": 2, "desc": "逢空亡（能量减半）" if kong else "未逢空亡"}
    total += kong_score * 2

    # ── 维度4: 神煞（权重1.5）──
    shen_sha = compute_all_shen_sha(
        all_gans + [da_yun_gan], all_zhis + [da_yun_zhi],
        all_zhis[0], all_zhis[1], ri_zhu,
    )
    sha_score = 0
    sha_parts = []
    if "天乙" in shen_sha.summary:
        sha_score += 2
        sha_parts.append("天乙贵人")
    if "文昌" in shen_sha.summary:
        sha_score += 2
        sha_parts.append("文昌")
    if "天德" in shen_sha.summary:
        sha_score += 1
        sha_parts.append("天德")
    if "月德" in shen_sha.summary:
        sha_score += 1
        sha_parts.append("月德")
    scores["神煞"] = {"score": sha_score, "weight": 1.5, "desc": "、".join(sha_parts) if sha_parts else "无特殊加分神煞"}
    total += sha_score * 1.5

    # ── 维度5: 十二长生（权重1.5）──
    from comprehensive_v2 import get_shi_er_chang_sheng
    try:
        chang_sheng = get_shi_er_chang_sheng(ri_zhu, da_yun_zhi)
    except (ImportError, AttributeError):
        chang_sheng = ""
    cs_score = 0
    if chang_sheng in ["临官", "帝旺"]:
        cs_score = 2
    elif chang_sheng in ["长生", "冠带"]:
        cs_score = 1
    elif chang_sheng in ["死", "墓", "绝"]:
        cs_score = -1
    scores["十二长生"] = {"score": cs_score, "weight": 1.5, "desc": chang_sheng if chang_sheng else "未知"}
    total += cs_score * 1.5

    # 归一化到 -10~10
    max_possible = 3*3 + 5*2 + 0*2 + 4*1.5 + 2*1.5  # = 9+10+0+6+3 = 28
    min_possible = -2*3 + 0 + -2*2 + 0 + -1*1.5  # = -6-4-1.5 = -11.5
    if max_possible - min_possible > 0:
        normalized = round(((total - min_possible) / (max_possible - min_possible)) * 10 - 5, 1)
    else:
        normalized = 0.0

    return {
        "五维总分": normalized,
        "五维明细": scores,
        "综合判断": "上佳大运" if normalized >= 4 else "良好大运" if normalized >= 2 else "平运" if normalized >= -2 else "不佳大运",
    }


def _get_gong_wei_info(pillar_idx: int) -> str:
    """根据柱序号返回宫位描述"""
    info = GONG_WEI_MAP.get(pillar_idx, {})
    return f"{info.get('六亲', '')}·{info.get('身体', '')}"


def _find_pillar_interactions(liu_nian_zhi: str, all_zhis: list[str]) -> dict:
    """
    找到流年地支与四柱的地支关系（冲/合/刑/害/破）
    返回 {relation: [(pillar_idx, pillar_name, zhi), ...]}
    只考虑四柱（all_zhis[:4]）与流年地支的关系
    """
    from xing_chong_he_hua import check_chong, check_liu_he, check_hai, check_xing, LIU_PO

    result = {"冲": [], "合": [], "刑": [], "害": [], "破": []}

    for i in range(4):  # 只检查年/月/日/时四柱
        if i >= len(all_zhis):
            break
        pz = all_zhis[i]
        name = PILLAR_NAMES[i] if i < 4 else f"柱{i}"

        # 六冲
        if check_chong(liu_nian_zhi, pz):
            result["冲"].append((i, name, pz))

        # 六合
        if check_liu_he(liu_nian_zhi, pz):
            result["合"].append((i, name, pz))

        # 六害
        if check_hai(liu_nian_zhi, pz):
            result["害"].append((i, name, pz))

    # 三刑（传流年地支+四柱地支列表检查）
    zhi_list = [liu_nian_zhi] + all_zhis[:4]
    for xing_type, _ in check_xing(zhi_list):
        result["刑"].append(xing_type)

    # 六破
    for i in range(4):
        if i >= len(all_zhis):
            break
        if LIU_PO.get((liu_nian_zhi, all_zhis[i])) or LIU_PO.get((all_zhis[i], liu_nian_zhi)):
            result["破"].append((i, PILLAR_NAMES[i], all_zhis[i]))

    return result


def _get_chong_lei_xiang(liu_nian_zhi: str, other_zhi: str) -> str:
    """根据冲的地支返回五行类象描述（R36）"""
    zhis = {liu_nian_zhi, other_zhi}

    # 四土冲（辰戌丑未）= 土类 → 住宅变动
    if zhis.intersection(TU_ZHI) and len(zhis.intersection(TU_ZHI)) >= 1:
        # 确认是辰戌冲或丑未冲（同为土）
        wx1 = DI_ZHI_WU_XING.get(liu_nian_zhi, "")
        wx2 = DI_ZHI_WU_XING.get(other_zhi, "")
        if wx1 == "土" and wx2 == "土":
            return CHONG_WU_XING_LEI_XIANG["土"]

    # 寅申巳亥冲 = 驿马类 → 职业变化
    if zhis.intersection(YI_MA_ZHI) and len(zhis.intersection(YI_MA_ZHI)) >= 1:
        if liu_nian_zhi in YI_MA_ZHI and other_zhi in YI_MA_ZHI:
            return CHONG_WU_XING_LEI_XIANG["驿马"]

    # 子午卯酉冲 = 桃花类 → 权力变化
    if zhis.intersection(TAO_HUA_ZHI) and len(zhis.intersection(TAO_HUA_ZHI)) >= 1:
        if liu_nian_zhi in TAO_HUA_ZHI and other_zhi in TAO_HUA_ZHI:
            return CHONG_WU_XING_LEI_XIANG["桃花"]

    return ""


def _get_bi_jie_desc(liu_nian_shi_shen: str, shen_label: str) -> str:
    """干透干藏应事规则（R35）：比劫透干的身强/身弱区分"""
    if liu_nian_shi_shen not in ["比肩", "劫财"]:
        return ""
    if shen_label == "身强":
        return "他人劫夺/竞争失利，注意财物安全"
    else:
        return "朋友帮身/合作顺利，利社交"


# ═══════════════════════════════════════
# R32: 流年合各宫位应事规则
# ═══════════════════════════════════════
def _get_he_ying_shi(pillar_idx: int) -> str:
    """流年合各宫位应事（R32）

    合年宫 → 长辈身体欠安
    合月令 → 心情郁闷
    合夫妻宫(日支) → 结婚或离婚
    合时柱 → 怀胎或子女事
    """
    MAP = {
        0: "长辈身体欠安",
        1: "心情郁闷",
        2: "结婚或离婚",
        3: "怀胎或子女事",
    }
    return MAP.get(pillar_idx, "")


# ═══════════════════════════════════════
# R33: 流年逢冲各宫位应事规则
# ═══════════════════════════════════════
def _get_chong_ying_shi(liu_nian_zhi: str, other_zhi: str, pillar_idx: int) -> str:
    """流年逢冲应事（R33）
    
    分类：
      - 冲库(辰戌/丑未冲) → "库被冲开"
      - 冲驿马(寅申/巳亥冲) → "职业变动/搬迁"
      - 冲桃花(子午/卯酉冲) → "情感困扰"
      - 冲年柱 → "隐忍莫争执"
      - 冲月柱 → "动心起念"
      - 冲日柱(夫妻宫) → "婚姻变动"
      - 冲时柱 → "怀胎/子女事"
    """
    # 先判断特殊类型冲
    zhis = {liu_nian_zhi, other_zhi}
    wx1 = DI_ZHI_WU_XING.get(liu_nian_zhi, "")
    wx2 = DI_ZHI_WU_XING.get(other_zhi, "")

    # 冲库(辰戌/丑未冲，同为土)
    if wx1 == "土" and wx2 == "土":
        return "库被冲开"

    # 冲驿马(寅申/巳亥冲)
    if liu_nian_zhi in YI_MA_ZHI and other_zhi in YI_MA_ZHI:
        return "职业变动/搬迁"

    # 冲桃花(子午/卯酉冲)
    if liu_nian_zhi in TAO_HUA_ZHI and other_zhi in TAO_HUA_ZHI:
        return "情感困扰"

    # 按宫位判断
    PILLAR_MAP = {
        0: "隐忍莫争执",
        1: "动心起念",
        2: "婚姻变动",
        3: "怀胎/子女事",
    }
    return PILLAR_MAP.get(pillar_idx, "")


# ═══════════════════════════════════════
# R34: 流年来害各宫位应事规则
# ═══════════════════════════════════════
def _get_hai_ying_shi(pillar_idx: int) -> str:
    """流年来害应事（R34）

    害年宫 → "与长辈分开"
    害月柱 → "心情郁闷"
    害夫妻宫(日支) → "聚少离多"
    害时柱 → "与子女分开"
    """
    MAP = {
        0: "与长辈分开",
        1: "心情郁闷",
        2: "聚少离多",
        3: "与子女分开",
    }
    return MAP.get(pillar_idx, "")


# ═══════════════════════════════════════
# R37: 运年合绊相冲5条规律
# ═══════════════════════════════════════
def _get_yun_nian_he_ban_tiao_lv(liu_nian_gan: str, liu_nian_zhi: str,
                                 da_yun_gan: str, da_yun_zhi: str,
                                 all_gans: list[str], all_zhis: list[str],
                                 xi_yong: list[str]) -> list[str]:
    """运年合绊相冲5条规律（R37）
    
    返回该流年的合绊规律描述列表
    """
    results = []

    # 1. 以绊论吉凶 — 被合绊的十神功能受限
    has_he = any([
        check_chong(liu_nian_zhi, da_yun_zhi) is not None,
        check_liu_he(liu_nian_zhi, da_yun_zhi) is not None,
    ])
    if has_he:
        results.append("【合绊】以绊论吉凶：被合绊的十神功能受限")

    # 2. 实神被作用 — 大运/流年引动原局实神
    for pz in all_zhis[:4]:
        if check_chong(liu_nian_zhi, pz) or check_liu_he(liu_nian_zhi, pz):
            results.append("【实神】大运/流年引动原局实神")
            break

    # 3. 干支一气力大 — 流年干支同一五行，能量加倍
    gan_wx = TIAN_GAN_WU_XING.get(liu_nian_gan, "")
    zhi_wx = DI_ZHI_WU_XING.get(liu_nian_zhi, "")
    if gan_wx and zhi_wx and gan_wx == zhi_wx:
        results.append("【一气】干支一气力大：流年干支同一五行，能量加倍")

    # 4. 绊住后仍可作用 — 被合绊不是永久消失
    if has_he:
        results.append("【余气】绊住后仍可作用：被合绊不是永久消失")

    # 5. 虚神看喜忌 — 原局没有的字被引动，看其五行喜忌
    ln_not_in_yuanju = liu_nian_gan not in all_gans[:4] or liu_nian_zhi not in all_zhis[:4]
    if ln_not_in_yuanju:
        wx_str = f"（{gan_wx}）" if gan_wx else ""
        is_xi = gan_wx in xi_yong if gan_wx else False
        flavor = "引动喜神，吉" if is_xi else "引动忌神，凶"
        results.append(f"【虚神】原局没有的字被引动{flavor}{wx_str}")

    return results


def _build_degree_str(confidence: float) -> str:
    """根据置信度返回程度词"""
    if confidence >= 0.8:
        return "（程度：重大）"
    elif confidence >= 0.6:
        return "（程度：显著）"
    elif confidence >= 0.5:
        return "（程度：一般）"
    return "（程度：轻微）"


def _build_event_desc(
    event_type: str,
    base_desc: str,
    gong_wei_str: str = "",
    chong_lei_xiang: str = "",
    bi_jie_str: str = "",
    period: str = "",
    confidence: float = 0.0,
    key_months: str = "",
) -> str:
    """
    断语四要素（R30）:
    {事件类型}: {六亲}的{身体}方面，{程度}，{应期}

    参数:
      event_type: 事件类型标签（💰/⚠️等）
      base_desc: 基础描述
      gong_wei_str: 宫位信息（R25）
      chong_lei_xiang: 冲的五行类象（R36）
      bi_jie_str: 比劫透干描述（R35）
      period: 时段前缀（上半年/下半年）（R31）
      confidence: 置信度，用于程度词
      key_months: 重点月份标注（R26）
    """
    parts = []

    # 时段前缀
    if period:
        parts.append(f"[{period}]")

    # 事件类型
    parts.append(event_type)

    # 核心描述
    core_parts = []
    if gong_wei_str:
        core_parts.append(gong_wei_str)
    if base_desc:
        core_parts.append(base_desc)
    if chong_lei_xiang:
        core_parts.append(chong_lei_xiang)
    if bi_jie_str:
        core_parts.append(bi_jie_str)

    if core_parts:
        parts.append("：".join(core_parts))

    # 程度词
    if confidence >= 0.8:
        parts.append("（程度：重大）")
    elif confidence >= 0.6:
        parts.append("（程度：显著）")
    elif confidence >= 0.5:
        parts.append("（程度：一般）")

    # 重点月份（R26）
    if key_months:
        parts.append(f"（{key_months}）")

    # 应期提示
    if period == "上半年":
        parts.append("应期：1-6月天干主导70%")
    elif period == "下半年":
        parts.append("应期：7-12月地支主导70%")

    return "，".join(parts)


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


def _check_da_yun_kong_wang(da_yun_zhi: str, day_gan: str, day_zhi: str) -> bool:
    """R41: 检查大运地支是否逢空亡，空亡则能量减半"""
    kong_wang = _get_kong_wang(day_gan, day_zhi)
    return da_yun_zhi in kong_wang


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
    流年精准分析 v2.1 — 含全面事件断法（宫位+四要素+分时段+干透干藏+五行类象）

    逻辑链:
    1. 流年十神→定吉凶方向
    2. 流年地支与大运/原局的关系→定触发方式（含宫位对应R25）
    3. 五行能量变化→定程度（含干透干藏R35/五行类象R36）
    4. 分时段（上半年天干70%/下半年地支70% R31）
    5. 神煞→定性修正
    6. 综合断事（断语四要素格式 R30）
    """
    # ── 基本信息 ──
    liu_nian_wx = f"{TIAN_GAN_WU_XING[liu_nian_gan]}{DI_ZHI_WU_XING[liu_nian_zhi]}"
    liu_nian_shi_shen = get_shi_shen_for_gan(liu_nian_gan, ri_zhu)
    liu_nian_wx_gan = TIAN_GAN_WU_XING[liu_nian_gan]
    liu_nian_wx_zhi = DI_ZHI_WU_XING[liu_nian_zhi]

    # ── 地支关系（使用v2以获取三会局R11）──
    all_rels = check_all_relations_v2(all_zhis + [liu_nian_zhi], all_gans + [liu_nian_gan])
    dy_rels = check_all_relations([liu_nian_zhi, da_yun_zhi])

    # ── 宫位互动分析（R25）─ 流年与四柱的关系 ──
    pillar_interactions = _find_pillar_interactions(liu_nian_zhi, all_zhis)

    # ── 神煞 ──
    shen_sha_full = compute_all_shen_sha(
        all_gans + [liu_nian_gan], all_zhis + [liu_nian_zhi], year_zhi, month_zhi, ri_zhu
    )

    # ── R41: 大运空亡检测 ──
    da_yun_kong_wang = _check_da_yun_kong_wang(da_yun_zhi, ri_zhu, all_zhis[2])
    # 大运空亡→该步大运能量减半，流年事件强度下调
    da_yun_energy_factor = 0.5 if da_yun_kong_wang else 1.0

    # ── 综合评分 (0-10) ──
    score = 5.0

    # ✅ [P0-Bug-1] 用五行喜忌判定（不是十神硬编码）
    is_xi = liu_nian_wx_gan in xi_yong   # 在喜用中=吉
    is_ji = liu_nian_wx_gan in ji_shen   # 在忌神中=凶

    # 流年天干喜忌加分
    if is_xi:
        score += 1.5
    elif is_ji:
        score -= 1.5

    # ✅ [P0-Bug-2] 印星加分根据实际喜用神，不硬编码水/金
    if liu_nian_shi_shen in ["正印", "偏印"]:
        yin_wx = TIAN_GAN_WU_XING[liu_nian_gan]  # 印星五行
        if yin_wx in xi_yong:
            score += 1.5  # 印星为喜用 → 大加分
        elif yin_wx in ji_shen:
            score += 0.5  # 印星为忌神 → 小幅加分（印星本身有护身作用）

    # ✅ [P0-缺失-2] 贪合忘冲原则：流年某字同时有合和冲的关系，优先选合，不冲
    has_any_he = bool(all_rels.get("三会") or all_rels.get("三合") or all_rels.get("六合") or all_rels.get("半合"))
    has_any_chong = bool(all_rels.get("冲"))
    tan_he_wang_chong = has_any_he and has_any_chong  # 贪合忘冲启用

    # ✅ R14补充: 合化优先级 — 有多个合化时只应用优先级最高的
    # 三会(20倍/4) > 三合(15倍/3) > 半合/六合(10倍/2) > 拱合(1) > 暗合(0)
    def _get_highest_he_priority(rels: dict) -> int:
        max_p = 0
        if rels.get("三会"):
            max_p = max(max_p, HE_HUA_PRIORITY["三会"])
        if rels.get("三合"):
            max_p = max(max_p, HE_HUA_PRIORITY["三合"])
        if rels.get("六合"):
            max_p = max(max_p, HE_HUA_PRIORITY["六合"])
        if rels.get("半合"):
            max_p = max(max_p, HE_HUA_PRIORITY["半合"])
        return max_p

    # 地支关系影响（贪合忘冲：有合优先，不計冲的负面）
    if tan_he_wang_chong:
        # 贪合忘冲 → 合的能量为主，冲被化解
        he_priority = _get_highest_he_priority(all_rels)
        if he_priority >= 4:  # 三会最高
            score += 2.0  # 三会能量加倍
        elif he_priority >= 3:  # 三合
            score += 1.5
        else:
            score += 1.0  # 合带来的加分
    else:
        if has_any_chong:
            score -= 0.5
        if has_any_he:
            he_priority = _get_highest_he_priority(all_rels)
            if he_priority >= 4:
                score += 2.0
            elif he_priority >= 3:
                score += 1.5
            else:
                score += 1.0

    # ✅ 三刑=能量加强，不是扣分
    if all_rels.get("刑"):
        score += 0.5  # 三刑是能量加强，不扣分

    # 五行关系
    gan_rel = _get_wx_relation(liu_nian_wx_gan, ri_zhu_wx)
    if gan_rel == "生" or gan_rel == "被生":
        score += 0.5
    elif gan_rel == "克" or gan_rel == "被克":
        score -= 0.5

    # ✅ R46: 身过强>60分⇒比劫为忌⇒比劫年破财
    # 身过强时，比劫是忌神（不再扶身，反而争财）
    if shen_score > 60 and liu_nian_shi_shen in ["比肩", "劫财"]:
        bijie_wx = TIAN_GAN_WU_XING[liu_nian_gan]
        if bijie_wx in ji_shen or bijie_wx not in xi_yong:
            score -= 1.0  # 比劫为忌→破财

    score = max(0, min(10, round(score, 1)))

    # ═══════════════════════════════════════
    # 干透干藏应事规则（R35）
    # ═══════════════════════════════════════
    bi_jie_desc = _get_bi_jie_desc(liu_nian_shi_shen, shen_label)

    # ═══════════════════════════════════════
    # 地支五行类象逢冲应事（R36）
    # ═══════════════════════════════════════
    chong_lei_xiang_descs = []
    for chong_info in pillar_interactions.get("冲", []):
        p_idx, p_name, p_zhi = chong_info
        lei_xiang = _get_chong_lei_xiang(liu_nian_zhi, p_zhi)
        if lei_xiang:
            chong_lei_xiang_descs.append(lei_xiang)
    chong_lei_xiang_str = " + ".join(chong_lei_xiang_descs) if chong_lei_xiang_descs else ""

    # ── 构建事件宫位信息 ──
    # 收集所有有互动关系的宫位
    gong_wei_parts = []
    for rel_type in ["冲", "合", "刑", "害", "破"]:
        for item in pillar_interactions.get(rel_type, []):
            if isinstance(item, tuple) and len(item) >= 2:
                p_idx, p_name = item[0], item[1]
                gong_wei_str = _get_gong_wei_info(p_idx)
                gong_wei_parts.append(gong_wei_str)

    # 去重合并宫位信息
    gong_wei_deduped = list(dict.fromkeys(gong_wei_parts))  # 保持顺序去重
    gong_wei_combined = "；".join(gong_wei_deduped) if gong_wei_deduped else ""

    # ═══════════════════════════════════════
    # R32~R34: 流年合/冲/害各宫位应事
    # ═══════════════════════════════════════
    ying_shi_descs = []

    # R32: 合各宫位应事
    for he_info in pillar_interactions.get("合", []):
        if isinstance(he_info, tuple) and len(he_info) >= 2:
            p_idx = he_info[0]
            he_ys = _get_he_ying_shi(p_idx)
            if he_ys:
                ying_shi_descs.append(f"【合】{he_ys}")

    # R33: 冲各宫位应事
    for chong_info in pillar_interactions.get("冲", []):
        if isinstance(chong_info, tuple) and len(chong_info) >= 3:
            p_idx, p_name, p_zhi = chong_info
            chong_ys = _get_chong_ying_shi(liu_nian_zhi, p_zhi, p_idx)
            if chong_ys:
                ying_shi_descs.append(f"【冲】{chong_ys}")

    # R34: 害各宫位应事
    for hai_info in pillar_interactions.get("害", []):
        if isinstance(hai_info, tuple) and len(hai_info) >= 2:
            p_idx = hai_info[0]
            hai_ys = _get_hai_ying_shi(p_idx)
            if hai_ys:
                ying_shi_descs.append(f"【害】{hai_ys}")

    ying_shi_combined = "；".join(ying_shi_descs) if ying_shi_descs else ""

    # ═══════════════════════════════════════
    # R37: 运年合绊相冲5条规律
    # ═══════════════════════════════════════
    he_ban_tiao_lv = _get_yun_nian_he_ban_tiao_lv(
        liu_nian_gan, liu_nian_zhi,
        da_yun_gan, da_yun_zhi,
        all_gans, all_zhis,
        xi_yong,
    )
    he_ban_combined = " | ".join(he_ban_tiao_lv) if he_ban_tiao_lv else ""

    # ── R26: 流月重点月份 ──
    key_months_str = _get_key_months(liu_nian_wx_gan, liu_nian_wx_zhi, xi_yong, ji_shen)

    # ── R43: 大运定性双维度描述 ──
    da_yun_dual_desc = _da_yun_dual_dimension(
        da_yun_gan, da_yun_zhi, ri_zhu, ri_zhu_wx, xi_yong, shen_label,
    )

    # ── R44: 最佳大运综合判断法五维评分 ──
    da_yun_five_dim = _five_dimensional_da_yun_score(
        da_yun_gan, da_yun_zhi, ri_zhu, ri_zhu_wx, xi_yong, ji_shen,
        all_gans, all_zhis, shen_label,
    )

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
        wealth_desc = "财星引动"

    # 条件2: 财星为喜用
    if liu_nian_shi_shen in ["正财", "偏财"] and liu_nian_wx_gan in xi_yong:
        wealth_conf += 0.3
        wealth_desc = "喜用财星到位"

    # 条件3: 三合财局（动态判断财星五行）
    CAI_WUXING_MAP = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
    ri_cai_wx = CAI_WUXING_MAP.get(ri_zhu_wx, "")
    for he in all_rels["三合"]:
        he_wx = he.get("wx", "")
        if he_wx and ri_cai_wx and he_wx == ri_cai_wx:
            wealth_conf += 0.3
            wealth_desc = f"{he['type']}财局引动"

    # 条件3b: 三会财局（R11补充 — 三会能量20倍＞三合15倍）
    for hui in all_rels.get("三会", []):
        hui_wx = hui.get("wx", "")
        if hui_wx and ri_cai_wx and hui_wx == ri_cai_wx:
            wealth_conf += 0.4  # 三会比三合更强
            wealth_desc = f"{hui['type']}财局引动（三会20倍）"

    # 条件4: 财库冲开
    for chong in all_rels["冲"]:
        if "辰戌" in chong or "丑未" in chong:
            wealth_conf += 0.2
            wealth_desc = "财库冲开"

    if wealth_conf >= 0.5:
        wealth_conf = min(1.0, wealth_conf)
        events.append(
            EventPrediction(
                year=year,
                event_type="wealth",
                description=_build_event_desc(
                    "💰 发财",
                    wealth_desc,
                    gong_wei_str=gong_wei_combined,
                    chong_lei_xiang=chong_lei_xiang_str if "住宅" in chong_lei_xiang_str else "",
                    bi_jie_str=bi_jie_desc if "劫" in bi_jie_desc else "",
                    period="全年",
                    confidence=wealth_conf,
                    key_months=key_months_str,
                ),
                confidence=wealth_conf,
                energy=round(1.0 * da_yun_energy_factor, 1),
            )
        )

    # ═══════════════════════════════════════
    # 灾祸事件检测
    # ═══════════════════════════════════════
    mis_conf = 0.0
    mis_desc = ""
    mis_energy = 1.0  # 灾祸能量系数

    # 条件1: 七杀攻身
    if liu_nian_shi_shen == "七杀" and shen_label == "身弱":
        mis_conf += 0.5
        mis_desc = "七杀攻身"
        # R39: 计算原局七杀数量→对应能量级别
        qisha_count = sum(1 for g in all_gans if get_shi_shen_for_gan(g, ri_zhu) == "七杀")
        e_level = E_SHEN_LEVEL["七杀"]
        for threshold in sorted(e_level.keys(), reverse=True):
            if qisha_count >= threshold:
                mis_desc += f"({e_level[threshold]})"
                mis_energy = max(mis_energy, threshold / 10.0)
                break
        # R40: 神煞界限 — 天乙/天德只能解神煞类灾祸（灾煞/血刃），不能解十神类灾祸（七杀）
        # 即使命带天乙贵人，七杀攻身仍按十神规则判定，不因神煞而减免
        if "天乙" in shen_sha_full.summary or "天德" in shen_sha_full.summary:
            if qisha_count >= 3:  # 七杀能量≥3时显著标注界限
                mis_desc += SHEN_SHA_BOUNDARY_NOTE

    # 条件2: 伤官为忌（原局伤官多+流年引动）
    if liu_nian_shi_shen == "伤官":
        shang_guan_count = sum(1 for g in all_gans if get_shi_shen_for_gan(g, ri_zhu) == "伤官")
        if shang_guan_count >= 2 or (shang_guan_count >= 1 and liu_nian_wx_gan in ji_shen):
            mis_conf += 0.3
            mis_desc = "伤官为忌"
            # R39: 恶神能量对应
            e_level = E_SHEN_LEVEL["伤官"]
            for threshold in sorted(e_level.keys(), reverse=True):
                if shang_guan_count >= threshold:
                    mis_desc += f"({e_level[threshold]})"
                    mis_energy = max(mis_energy, threshold / 10.0)
                    break

    # 条件2: 忌神流年+冲刑
    if liu_nian_wx_gan in ji_shen and ("冲" in all_rels["summary"] or "刑" in all_rels["summary"]):
        mis_conf += 0.3
        mis_desc = "忌神+冲刑"

    # 条件3: 犯太岁
    fan_tai_sui = check_fan_tai_sui(year_zhi, liu_nian_zhi)
    if fan_tai_sui:
        mis_conf += fan_tai_sui[1] * 0.3
        mis_desc = f"{fan_tai_sui[0]}"

    # 条件4: 冲大运
    if "冲" in dy_rels["summary"]:
        mis_conf += 0.3
        mis_desc = "大运流年相冲"

    # 条件4b: 三会忌神局（R11补充 — 三会局能量20倍，增强灾祸）
    for hui in all_rels.get("三会", []):
        hui_wx = hui.get("wx", "")
        if hui_wx and hui_wx in ji_shen:
            mis_conf += 0.3
            mis_energy = max(mis_energy, 2.0)  # 三会20倍能量
            if "三会" not in mis_desc:
                mis_desc = f"{hui['type']}忌神局引动"
            else:
                mis_desc += f"+{hui['type']}忌神局"

    # ✅ [P0-缺失-1] 条件5: 岁运并临检测
    is_sui_yun_bing_lin = (liu_nian_gan == da_yun_gan and liu_nian_zhi == da_yun_zhi)
    if is_sui_yun_bing_lin:
        mis_conf += 0.6  # 岁运并临→重大灾祸信号
        # 岁运并临+天克地冲 → 不死自己死家人
        tian_ke_di_chong = False
        pillar_gans = all_gans[:4]  # 年/月/日/时 的天干
        pillar_zhis = all_zhis[:4]  # 年/月/日/时 的地支
        ln_gan_wx = TIAN_GAN_WU_XING[liu_nian_gan]
        for pg, pz in zip(pillar_gans, pillar_zhis):
            pg_wx = TIAN_GAN_WU_XING[pg]
            # 天克：流年天干五行克八字某柱天干五行
            if WU_XING_KE.get(ln_gan_wx) == pg_wx:
                # 地冲：流年地支六冲八字某柱地支
                if check_chong(liu_nian_zhi, pz):
                    tian_ke_di_chong = True
                    break

        if tian_ke_di_chong:
            mis_conf += 0.4  # 天克地冲+岁运并临=极凶
            mis_desc = "⚠️ 岁运并临+天克地冲→不死自己死家人"
        else:
            mis_desc = "⚠️ 岁运并临→该年运势极端，需谨慎"
        mis_conf = min(1.0, mis_conf)

    if mis_conf >= 0.5:
        mis_conf = min(1.0, mis_conf)
        events.append(
            EventPrediction(
                year=year,
                event_type="misfortune",
                description=_build_event_desc(
                    "⚠️ 注意防范",
                    mis_desc,
                    gong_wei_str=gong_wei_combined,
                    chong_lei_xiang=chong_lei_xiang_str,
                    bi_jie_str=bi_jie_desc if "劫夺" in bi_jie_desc else "",
                    period="全年",
                    confidence=mis_conf,
                    key_months=key_months_str,
                ),
                confidence=mis_conf,
                energy=round(mis_energy * da_yun_energy_factor, 1),
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
            mar_desc = "正官到位"

    # 条件3: 印星帮身（身弱可担家庭责任）
    if liu_nian_shi_shen in ["正印", "偏印"] and shen_label == "身弱":
        mar_conf += 0.2
        if "印星" in mar_desc or "到位" in mar_desc:
            mar_desc += "+印星扶身"
        else:
            mar_desc = "印星扶身"

    if mar_conf >= 0.5:
        mar_conf = min(1.0, mar_conf)
        events.append(
            EventPrediction(
                year=year,
                event_type="marriage",
                description=_build_event_desc(
                    "💍 姻缘窗口",
                    mar_desc,
                    gong_wei_str=gong_wei_combined if "配偶" in gong_wei_combined else "自身·腹部（夫妻宫）",
                    period="全年",
                    confidence=mar_conf,
                    key_months=key_months_str,
                ),
                confidence=mar_conf,
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
        car_desc = "官印流年引动"

    # 条件2: 驿马引动
    for ym in shen_sha_full.yi_ma:
        if liu_nian_zhi in ym:
            car_conf += 0.3
            car_desc = "驿马引动"

    # 条件3: 冲合大运
    if "冲" in dy_rels["summary"] or "合" in dy_rels["summary"]:
        car_conf += 0.3
        if car_desc:
            car_desc += "+大运变动"
        else:
            car_desc = "大运变动"

    if car_conf >= 0.4:
        events.append(
            EventPrediction(
                year=year,
                event_type="career",
                description=_build_event_desc(
                    "💼 事业窗口",
                    car_desc,
                    gong_wei_str=gong_wei_combined,
                    chong_lei_xiang=chong_lei_xiang_str if "职业" in chong_lei_xiang_str else "",
                    period="全年",
                    confidence=car_conf,
                    key_months=key_months_str,
                ),
                confidence=car_conf,
            )
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
                year=year,
                event_type="education",
                description=_build_event_desc(
                    "📚 学业窗口",
                    "印星到位+文昌引动",
                    gong_wei_str="自身·头部/大脑（学业用神）",
                    period="全年",
                    confidence=edu_conf,
                    key_months=key_months_str,
                ),
                confidence=edu_conf,
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

    guo_san_wx = ""
    for wx, count in wx_count.items():
        if count >= 3 and liu_nian_wx_gan == wx:
            health_conf += 0.4
            guo_san_wx = wx
        if count >= 3 and liu_nian_wx_zhi == wx:
            health_conf += 0.3
            if not guo_san_wx:
                guo_san_wx = wx

    health_desc_parts = []
    if guo_san_wx:
        health_desc_parts.append(f"{guo_san_wx}五行过三")

    if liu_nian_shi_shen == "七杀" and shen_label == "身弱":
        health_conf += 0.3
        health_desc_parts.append("七杀攻身")

    # 找出被冲的健康宫位
    health_gong_wei = ""
    for chong_info in pillar_interactions.get("冲", []):
        p_idx, p_name, p_zhi = chong_info
        health_gong_wei = _get_gong_wei_info(p_idx)
        # 只取身体部位
        if "·" in health_gong_wei:
            health_gong_wei = health_gong_wei.split("·")[1] if "·" in health_gong_wei else health_gong_wei

    health_desc = " + ".join(health_desc_parts) if health_desc_parts else "五行过三/七杀攻身"

    if health_conf >= 0.5:
        events.append(
            EventPrediction(
                year=year,
                event_type="health",
                description=_build_event_desc(
                    "🏥 注意健康",
                    health_desc,
                    gong_wei_str=f"自身·{health_gong_wei}" if health_gong_wei else "",
                    period="全年",
                    confidence=health_conf,
                    key_months=key_months_str,
                ),
                confidence=health_conf,
            )
        )

    # ═══════════════════════════════════════
    # 分时段断事（R31）：上半年/下半年补充描述
    # ═══════════════════════════════════════
    period_events = []
    for e in events:
        desc = e.description
        # 去掉[全年]前缀
        clean_desc = desc.replace("[全年]", "").strip().lstrip("，")
        # 提取事件标签（含emoji的片段）
        label = ""
        core = ""
        for c in ["💰", "⚠️", "💍", "💼", "📚", "🏥", "💊"]:
            if c in clean_desc:
                idx = clean_desc.find(c)
                # 取到第一个"，"之前
                end_idx = clean_desc.find("，", idx)
                if end_idx == -1:
                    label = clean_desc[idx:].split("（")[0].strip()
                else:
                    label = clean_desc[idx:end_idx].strip()
                # 核心内容 = 从标签之后到第一个"（程度"之前
                rest = clean_desc[end_idx:] if end_idx != -1 else ""
                degree_start = rest.find("（程度")
                if degree_start != -1:
                    core = rest[:degree_start].strip().lstrip("，").rstrip("，")
                else:
                    core = rest.strip().lstrip("，")
                break

        if not label:
            label = clean_desc.split("，")[0] if "，" in clean_desc else clean_desc

        # 上半年：天干主导70%
        half1_conf = min(1.0, e.confidence * 0.7 + 0.1)
        h1_desc = f"[上半年·天干主导70%] {label}"
        if core:
            h1_desc += f"，{core}"
        h1_desc += _build_degree_str(half1_conf)
        h1_desc += "，应期：1-6月"
        period_events.append(EventPrediction(year=e.year, event_type=e.event_type, description=h1_desc, confidence=half1_conf))

        # 下半年：地支主导70%
        half2_conf = min(1.0, e.confidence * 0.7 + 0.1)
        h2_desc = f"[下半年·地支主导70%] {label}"
        if core:
            h2_desc += f"，{core}"
        h2_desc += _build_degree_str(half2_conf)
        h2_desc += "，应期：7-12月"
        period_events.append(EventPrediction(year=e.year, event_type=e.event_type, description=h2_desc, confidence=half2_conf))

    # 将分时段事件加入原事件列表
    events.extend(period_events)

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
        "pillar_interactions": {
            rel: [str(item) for item in items]
            for rel, items in pillar_interactions.items()
            if items
        },
        "events": [e.to_dict() for e in events_sorted],
        "ying_shi": ying_shi_combined,
        "he_ban": he_ban_combined,
        "da_yun_dual_dimension": da_yun_dual_desc,
        "da_yun_five_dimension": da_yun_five_dim,
        "san_hui_relations": [hui["type"] for hui in all_rels.get("三会", [])],
        "key_months": key_months_str,
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


# ═══════════════════════════════════════
# R29: 过三关 — 每种类型只保留置信度最高的3件事
# ═══════════════════════════════════════
def apply_three_guan_filter(events: dict) -> dict:
    """过三关：只取每种类型中置信度最高的事件"""
    filtered = {}
    for etype, evts in events.items():
        if evts:
            sorted_evts = sorted(evts, key=lambda x: x.get("confidence", 0), reverse=True)
            filtered[etype] = sorted_evts[:3]
    return filtered


def extract_key_events(liu_nian_results: list[dict]) -> dict:
    """提取关键事件年表（含过三关 R29）"""
    events = {"wealth": [], "misfortune": [], "marriage": [], "career": [], "education": [], "health": []}

    for r in liu_nian_results:
        for e in r.get("events", []):
            etype = e["event_type"]
            if etype in events and e["confidence"] >= 0.5:
                events[etype].append(
                    {"year": e["year"], "description": e["description"], "confidence": e["confidence"]}
                )

    # R29: 过三关 — 只取每种类型置信度最高的3件事
    return apply_three_guan_filter(events)


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
