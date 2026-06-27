"""
格局判定+喜用神引擎 v1.0 — 金鉴真人·金鉴真人原始规则

格局判定:
  - 月令本气定格局基础
  - 透干定格局名称
  - 常见格局: 正官格/七杀格/正财格/偏财格/正印格/偏印格/食神格/伤官格
  - 复合格局: 官杀混杂/伤官生财/杀印相生/食神生财等

喜用神:
  - 身强喜克泄耗（财官食）
  - 身弱喜生扶（印比）
  - 调候用神: 按出生月份
"""

from __future__ import annotations

from constants import TIAN_GAN_WU_XING, BaZi, Pillar
from shen_qiang_ruo import compute_shen_qiang_ruo
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan, is_tou_gan

# ── 月令定格局 ──
# 月令本气十神 = 格局主星
GE_JU_BY_YUE_LING = {
    "正印": "正印格",
    "偏印": "偏印格",
    "正官": "正官格",
    "七杀": "七杀格",
    "正财": "正财格",
    "偏财": "偏财格",
    "食神": "食神格",
    "伤官": "伤官格",
    "比肩": "建禄格",
    "劫财": "月刃格",
}


def determine_ge_ju(bazi: BaZi) -> tuple[str, str]:
    """
    判定格局
    返回: (主格局, 详细描述)
    """
    ri_zhu = bazi.ri_zhu
    yue_zhi = bazi.month.zhi

    # 月令本气
    ben_qi = bazi.month.cang_gan[0][0] if bazi.month.cang_gan else ""
    ben_qi_shi_shen = get_shi_shen_for_cang_gan(ben_qi, ri_zhu) if ben_qi else ""

    # 月干透出
    yue_gan = bazi.month.gan
    yue_gan_shi_shen = get_shi_shen_for_gan(yue_gan, ri_zhu)

    # 主格局：以月令本气为基础，月干透出为关键
    main_ge_ju = "正官格"  # 默认

    if ben_qi_shi_shen in GE_JU_BY_YUE_LING:
        main_ge_ju = GE_JU_BY_YUE_LING[ben_qi_shi_shen]

    # 如果月干透出不同十神且力量强，可能改变格局
    # 透干定格局：月干十神 > 月令本气
    if yue_gan_shi_shen in GE_JU_BY_YUE_LING:
        # 月干透出优先
        pass  # 保留月令为主

    # 复合格局检测
    extra_info = []

    # 官杀混杂
    has_guan = is_tou_gan("", bazi, "正官") or "正官" in [
        get_shi_shen_for_gan(p.gan, ri_zhu) for p in [bazi.year, bazi.month, bazi.day, bazi.hour]
    ]
    has_sha = is_tou_gan("", bazi, "七杀") or "七杀" in [
        get_shi_shen_for_gan(p.gan, ri_zhu) for p in [bazi.year, bazi.month, bazi.day, bazi.hour]
    ]

    # 更准确的检测
    all_shi_shen = [get_shi_shen_for_gan(p.gan, ri_zhu) for p in [bazi.year, bazi.month, bazi.day, bazi.hour]]
    has_guan = "正官" in all_shi_shen
    has_sha = "七杀" in all_shi_shen
    if has_guan and has_sha:
        extra_info.append("官杀混杂")

    # 伤官生财
    has_shang_guan = "伤官" in all_shi_shen
    has_zheng_cai = "正财" in all_shi_shen
    has_pian_cai = "偏财" in all_shi_shen
    if has_shang_guan and (has_zheng_cai or has_pian_cai):
        extra_info.append("伤官生财格")

    # 杀印相生
    if has_sha and ("正印" in all_shi_shen or "偏印" in all_shi_shen):
        extra_info.append("杀印相生")

    # 食神生财
    has_shi_shen = "食神" in all_shi_shen
    if has_shi_shen and (has_zheng_cai or has_pian_cai):
        extra_info.append("食神生财格")

    # 食神制杀
    if has_shi_shen and has_sha:
        extra_info.append("食神制杀")

    detail_parts = [main_ge_ju]
    if extra_info:
        detail_parts.extend(extra_info)

    detail = "+".join(detail_parts)

    return main_ge_ju, detail


def determine_xi_yong_shen(bazi: BaZi) -> tuple[list[str], list[str]]:
    """
    判定喜用神和忌神
    返回: (喜用五行列表[最喜在前], 忌神五行列表[最忌在前])

    身弱：喜印比（金水），忌财官食（火土木）
    身强：喜财官食（火土木），忌印比（金水）
    """
    score, label, _ = compute_shen_qiang_ruo(bazi)
    ri_wx = TIAN_GAN_WU_XING[bazi.ri_zhu]

    # 五行相生链
    sheng_mu = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    ke_mu = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    # 生我的五行
    sheng_wo = {v: k for k, v in sheng_mu.items()}[ri_wx]  # 印
    # 我生的五行
    wo_sheng = sheng_mu[ri_wx]  # 食伤
    # 克我的五行
    ke_wo = ke_mu[ri_wx]  # 官杀
    # 我克的五行
    wo_ke = ke_mu[ke_mu[ri_wx]] if False else ke_mu[ri_wx]  # 财
    # Actually let me think more carefully
    # 金克木, so if 日主=金, 木是我克的=财
    wo_ke = {v: k for k, v in ke_mu.items()}[ri_wx]

    if label == "身弱":
        # 喜印比（生我+同我）
        xi_yong = [sheng_wo, ri_wx]  # 先印后比
        ji_shen = [wo_ke, ke_wo, wo_sheng]  # 财>官>食伤
    elif label == "身强":
        # 喜财官食（我克+克我+我生）
        xi_yong = [wo_ke, ke_wo, wo_sheng]
        ji_shen = [sheng_wo, ri_wx]
    elif label == "从弱":
        # 从弱喜克泄耗
        xi_yong = [wo_ke, ke_wo, wo_sheng]
        ji_shen = [sheng_wo, ri_wx]
    else:  # from strong
        xi_yong = [sheng_wo, ri_wx]
        ji_shen = [wo_ke, ke_wo, wo_sheng]

    return xi_yong, ji_shen


# ── 调候用神表（按出生月份）──
TIAO_HOU_YONG_SHEN = {
    "甲": {
        1: "丙",
        2: "丙",
        3: "庚",
        4: "庚",
        5: "壬",
        6: "壬",
        7: "壬",
        8: "癸",
        9: "庚",
        10: "庚",
        11: "丙",
        12: "丙",
    },
    "乙": {
        1: "丙",
        2: "丙",
        3: "丙",
        4: "癸",
        5: "壬",
        6: "壬",
        7: "癸",
        8: "癸",
        9: "癸",
        10: "癸",
        11: "丙",
        12: "丙",
    },
    "丙": {
        1: "壬",
        2: "壬",
        3: "壬",
        4: "壬",
        5: "壬",
        6: "壬",
        7: "壬",
        8: "壬",
        9: "甲",
        10: "甲",
        11: "壬",
        12: "壬",
    },
    "丁": {
        1: "甲",
        2: "甲",
        3: "甲",
        4: "甲",
        5: "壬",
        6: "壬",
        7: "甲",
        8: "甲",
        9: "甲",
        10: "甲",
        11: "甲",
        12: "甲",
    },
    "戊": {
        1: "丙",
        2: "丙",
        3: "丙",
        4: "丙",
        5: "壬",
        6: "壬",
        7: "庚",
        8: "庚",
        9: "丙",
        10: "甲",
        11: "丙",
        12: "丙",
    },
    "己": {
        1: "丙",
        2: "丙",
        3: "甲",
        4: "癸",
        5: "壬",
        6: "壬",
        7: "癸",
        8: "癸",
        9: "癸",
        10: "丙",
        11: "丙",
        12: "丙",
    },
    "庚": {
        1: "丁",
        2: "甲",
        3: "甲",
        4: "壬",
        5: "癸",
        6: "壬",
        7: "壬",
        8: "癸",
        9: "甲",
        10: "甲",
        11: "丁",
        12: "丙",
    },
    "辛": {
        1: "丙",
        2: "丙",
        3: "甲",
        4: "壬",
        5: "壬",
        6: "壬",
        7: "壬",
        8: "壬",
        9: "壬",
        10: "壬",
        11: "丙",
        12: "丙",
    },
    "壬": {
        1: "戊",
        2: "戊",
        3: "甲",
        4: "壬",
        5: "庚",
        6: "庚",
        7: "戊",
        8: "甲",
        9: "甲",
        10: "甲",
        11: "戊",
        12: "戊",
    },
    "癸": {
        1: "丙",
        2: "丙",
        3: "丙",
        4: "庚",
        5: "庚",
        6: "庚",
        7: "壬",
        8: "壬",
        9: "甲",
        10: "壬",
        11: "丙",
        12: "丙",
    },
}


def get_tiao_hou_yong_shen(ri_zhu: str, birth_month: int) -> list[str]:
    """
    获取调候用神（按出生月份）
    birth_month: 1-12 (农历月份)
    """
    yong_shen_gan = TIAO_HOU_YONG_SHEN.get(ri_zhu, {}).get(birth_month, "")
    if not yong_shen_gan:
        return []
    wx = TIAN_GAN_WU_XING.get(yong_shen_gan, "")
    return [wx] if wx else []


if __name__ == "__main__":
    from constants import BaZi, Pillar

    test_cases = [
        (
            "家主",
            BaZi(
                year=Pillar("甲", "午"),
                month=Pillar("己", "巳"),
                day=Pillar("戊", "午"),
                hour=Pillar("壬", "子"),
                gender="男",
            ),
        ),
        (
            "子源",
            BaZi(
                year=Pillar("庚", "申"),
                month=Pillar("辛", "巳"),
                day=Pillar("甲", "午"),
                hour=Pillar("丙", "寅"),
                gender="男",
            ),
        ),
        (
            "主母",
            BaZi(
                year=Pillar("戊", "午"),
                month=Pillar("甲", "子"),
                day=Pillar("庚", "戌"),
                hour=Pillar("丁", "亥"),
                gender="女",
            ),
        ),
    ]

    for name, b in test_cases:
        main_ge, detail = determine_ge_ju(b)
        xi, ji = determine_xi_yong_shen(b)
        print(f"【{name}】{b.summary()}")
        print(f"  格局: {detail}")
        print(f"  喜用神: {xi}")
        print(f"  忌神: {ji}")
        print()
