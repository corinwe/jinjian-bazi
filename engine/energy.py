"""
能量等级分析引擎 v1.0 — 金鉴真人·金鉴真人原始规则

能量分析维度:
  1. 原局五行能量分布（干支含藏全部计算）
  2. 地支关系能量（冲刑合害）
  3. 大运能量加成
  4. 流年触发能量
  5. 神煞能量修正
"""

from __future__ import annotations

from constants import TIAN_GAN_WU_XING, WU_XING_KE, WU_XING_SHENG, BaZi, Pillar
from xing_chong_he_hua import NENG_LIANG, check_all_relations


def compute_wu_xing_energy(bazi: BaZi) -> dict:
    """
    计算五行能量分布
    返回: {五行: 能量分}
    计算规则: 天干全计(1分), 地支藏干按比例
    """
    energy = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    # 天干能量
    for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
        wx = TIAN_GAN_WU_XING[p.gan]
        energy[wx] += 1.0  # 天干=1分

    # 地支本气能量
    for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
        # 本气
        ben_qi = p.cang_gan[0] if p.cang_gan else None
        if ben_qi:
            wx = TIAN_GAN_WU_XING[ben_qi[0]]
            energy[wx] += 1.0  # 本气=1分
        # 中气(60%)
        if len(p.cang_gan) > 1:
            zhong_qi = p.cang_gan[1]
            wx = TIAN_GAN_WU_XING[zhong_qi[0]]
            energy[wx] += 0.6
        # 余气(30%)
        if len(p.cang_gan) > 2:
            yu_qi = p.cang_gan[2]
            wx = TIAN_GAN_WU_XING[yu_qi[0]]
            energy[wx] += 0.3

    # 四舍五入到1位小数
    for k in energy:
        energy[k] = round(energy[k], 1)

    return energy


def compute_relation_energy(zhi_list: list[str]) -> dict:
    """
    计算地支关系能量
    """
    result = check_all_relations(zhi_list)
    total_energy = 0

    # 六冲能量
    for chong in result["冲"]:
        total_energy += NENG_LIANG["六冲"]  # 1.0

    # 三刑能量
    for xing in result["刑"]:
        total_energy += xing["energy"]

    # 六害能量
    for hai in result["害"]:
        total_energy += NENG_LIANG["六害"]

    # 三合能量
    for san_he in result["三合"]:
        total_energy += san_he["energy"]

    # 半合能量
    for ban_he in result["半合"]:
        total_energy += ban_he["energy"]

    # 六合能量
    for liu_he in result["六合"]:
        total_energy += NENG_LIANG["六合"]

    return {
        "details": result,
        "total_energy": round(total_energy, 1),
        "energy_level": "高" if total_energy >= 3 else "中" if total_energy >= 1 else "低",
    }


def compute_energy_profile(bazi: BaZi) -> dict:
    """
    完整能量分析
    """
    # 五行能量
    wx_energy = compute_wu_xing_energy(bazi)

    # 地支能量
    zhi_list = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]
    rel_energy = compute_relation_energy(zhi_list)

    # 日主能量分析
    ri_wx = TIAN_GAN_WU_XING[bazi.ri_zhu]

    # 生扶五行: 生日主的 + 同五行
    sheng_wo = WU_XING_SHENG.get(ri_wx, "")
    sheng_energy = wx_energy.get(sheng_wo, 0) + wx_energy.get(ri_wx, 0)

    # 克泄五行: 日主克的 + 克日主的 + 日主生的
    ke_zuo = WU_XING_KE.get(ri_wx, "")  # 日主克的
    ke_wo = {v: k for k, v in WU_XING_KE.items()}.get(ri_wx, "")  # 克日主的
    wo_sheng = WU_XING_SHENG.get(ri_wx, "")  # 日主生的
    ke_energy = wx_energy.get(ke_zuo, 0) + wx_energy.get(ke_wo, 0) + wx_energy.get(wo_sheng, 0)

    # 综合能量等级
    energy_balance = "身强" if sheng_energy > ke_energy else "身弱" if ke_energy > sheng_energy else "中和"

    return {
        "wu_xing_energy": wx_energy,
        "relation_energy": rel_energy,
        "ri_zhu_energy": {
            "ri_zhu_wx": ri_wx,
            "sheng_fu_energy": round(sheng_energy, 1),
            "ke_xie_energy": round(ke_energy, 1),
            "balance": energy_balance,
        },
        "strongest_wx": max(wx_energy, key=wx_energy.get),
        "weakest_wx": min(wx_energy, key=wx_energy.get),
    }


if __name__ == "__main__":
    from constants import BaZi, Pillar

    bazi = BaZi(
        year=Pillar("庚", "申"), month=Pillar("辛", "巳"), day=Pillar("甲", "午"), hour=Pillar("丙", "寅"), gender="男"
    )
    profile = compute_energy_profile(bazi)
    print(f"五行能量: {profile['wu_xing_energy']}")
    print(f"地支关系: {profile['relation_energy']['details']['summary']}")
    print(
        f"日主能量: 生扶{profile['ri_zhu_energy']['sheng_fu_energy']} vs 克泄{profile['ri_zhu_energy']['ke_xie_energy']}"
    )
    print(f"最强: {profile['strongest_wx']}, 最弱: {profile['weakest_wx']}")
