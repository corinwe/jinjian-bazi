"""
十神判定引擎 v1.0 — 金鉴真人·金鉴真人原始规则
"""

from constants import SHI_SHEN_MAP, TIAN_GAN_WU_XING, TIAN_GAN_YIN_YANG, WU_XING_KE, WU_XING_SHENG, BaZi, Pillar


def _wu_xing_relation(gan_wx: str, ri_zhu_wx: str) -> str:
    """
    判断天干五行与日主五行之间的关系类型
    返回: "生我" / "我生" / "克我" / "我克" / "同我"
    """
    if gan_wx == ri_zhu_wx:
        return "同我"
    if WU_XING_SHENG[gan_wx] == ri_zhu_wx:
        return "生我"  # gan生日主
    if WU_XING_SHENG[ri_zhu_wx] == gan_wx:
        return "我生"  # 日主生gan
    if WU_XING_KE[gan_wx] == ri_zhu_wx:
        return "克我"  # gan克日主
    if WU_XING_KE[ri_zhu_wx] == gan_wx:
        return "我克"  # 日主克gan
    return "同我"  # fallback


def _yin_yang_relation(gan_yy: str, ri_zhu_yy: str) -> str:
    """阴阳关系: '同' 或 '异'"""
    return "同" if gan_yy == ri_zhu_yy else "异"


def get_shi_shen_for_gan(gan: str, ri_zhu: str) -> str:
    """获取天干对应的十神"""
    relation = _wu_xing_relation(TIAN_GAN_WU_XING[gan], TIAN_GAN_WU_XING[ri_zhu])
    yy = _yin_yang_relation(TIAN_GAN_YIN_YANG[gan], TIAN_GAN_YIN_YANG[ri_zhu])
    return SHI_SHEN_MAP[(relation, yy)]


def get_shi_shen_all_dry(bazi: BaZi) -> list[dict]:
    """获取四柱天干十神"""
    ri_zhu = bazi.ri_zhu
    result = []
    pillars = bazi.all_pillars()
    names = ["年柱", "月柱", "日柱", "时柱"]
    for pillar, name in zip(pillars, names, strict=False):
        shi_shen = get_shi_shen_for_gan(pillar.gan, ri_zhu)
        result.append(
            {
                "position": name,
                "gan": pillar.gan,
                "shi_shen": shi_shen,
                "yin_yang": TIAN_GAN_YIN_YANG[pillar.gan],
                "wu_xing": TIAN_GAN_WU_XING[pillar.gan],
            }
        )
    return result


def get_shi_shen_for_cang_gan(cang_gan: str, ri_zhu: str) -> str:
    """获取地支藏干对应的十神"""
    relation = _wu_xing_relation(TIAN_GAN_WU_XING[cang_gan], TIAN_GAN_WU_XING[ri_zhu])
    yy = _yin_yang_relation(TIAN_GAN_YIN_YANG[cang_gan], TIAN_GAN_YIN_YANG[ri_zhu])
    return SHI_SHEN_MAP[(relation, yy)]


def get_all_cang_gan_shi_shen(bazi: BaZi) -> list[dict]:
    """获取所有地支藏干十神"""
    ri_zhu = bazi.ri_zhu
    result = []
    pillars = bazi.all_pillars()
    names = ["年柱", "月柱", "日柱", "时柱"]
    for pillar, name in zip(pillars, names, strict=False):
        for cg, ratio in pillar.cang_gan:
            shi_shen = get_shi_shen_for_cang_gan(cg, ri_zhu)
            result.append(
                {
                    "position": name,
                    "zhi": pillar.zhi,
                    "cang_gan": cg,
                    "ratio": ratio,
                    "shi_shen": shi_shen,
                    "wu_xing": TIAN_GAN_WU_XING[cg],
                }
            )
    return result


def is_tou_gan(gan: str, bazi: BaZi, shi_shen_name: str = "") -> bool:
    """
    判断某个天干是否透干。
    如果指定 shi_shen_name, 则判断该十神是否透出天干
    """
    if shi_shen_name:
        for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
            ss = get_shi_shen_for_gan(p.gan, bazi.ri_zhu)
            if ss == shi_shen_name:
                return True
        return False
    # 检查特定天干
    for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
        if p.gan == gan:
            return True
    return False


if __name__ == "__main__":
    # 快速测试
    from constants import BaZi, Pillar

    test_bazi = BaZi(
        year=Pillar("庚", "申"), month=Pillar("辛", "巳"), day=Pillar("甲", "午"), hour=Pillar("丙", "寅"), gender="男"
    )
    print("天干十神:")
    for item in get_shi_shen_all_dry(test_bazi):
        print(f"  {item['position']}: {item['gan']} → {item['shi_shen']}")
    print("\n地支藏干十神:")
    for item in get_all_cang_gan_shi_shen(test_bazi):
        print(f"  {item['position']} {item['zhi']}: {item['cang_gan']}({item['ratio']}%) → {item['shi_shen']}")
    print(f"\n是否透伤官: {is_tou_gan('', test_bazi, '伤官')}")
    print(f"是否透丙火: {is_tou_gan('丙', test_bazi)}")
