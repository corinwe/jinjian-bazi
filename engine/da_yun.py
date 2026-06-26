"""
大运计算引擎 v1.0 — 金鉴真人·金鉴真人原始规则

核心规则:
  1. 阳男阴女顺排，阴男阳女逆排
  2. 顺排: 从月柱开始顺数到下一个节气
  3. 逆排: 从月柱开始逆数到上一个节气
  4. 起运年龄: (节气天数差额) / 3
  5. 十年一大运
  6. 大运排序: 按喜用神逻辑（纯喜用最佳·纯忌神最差）
"""

from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from constants import (
    TIAN_GAN, DI_ZHI, DaYun, BaZi, TIAN_GAN_YIN_YANG,
    TIAN_GAN_WU_XING, DI_ZHI_WU_XING,
)
from shen_qiang_ruo import compute_shen_qiang_ruo


# ── 节气日期（简化版·只用于测试）──
# 实际应用中需要专业排盘表或API

# ── 天干地支顺序 ──
TIAN_GAN_ORDER = {g: i for i, g in enumerate(TIAN_GAN)}
DI_ZHI_ORDER = {z: i for i, z in enumerate(DI_ZHI)}


def next_gan(gan: str, steps: int) -> str:
    """天干顺走steps步"""
    idx = (TIAN_GAN_ORDER[gan] + steps) % 10
    return TIAN_GAN[idx]


def prev_gan(gan: str, steps: int) -> str:
    """天干逆走steps步"""
    idx = (TIAN_GAN_ORDER[gan] - steps) % 10
    return TIAN_GAN[idx]


def next_zhi(zhi: str, steps: int) -> str:
    """地支顺走steps步"""
    idx = (DI_ZHI_ORDER[zhi] + steps) % 12
    return DI_ZHI[idx]


def prev_zhi(zhi: str, steps: int) -> str:
    """地支逆走steps步"""
    idx = (DI_ZHI_ORDER[zhi] - steps) % 12
    return DI_ZHI[idx]


def compute_da_yun(bazi: BaZi, birth_year: int = 1980, 
                   qi_yun_days: float = 1.1) -> tuple[list[DaYun], float, int]:
    """
    计算大运
    
    参数:
      bazi: 八字
      birth_year: 出生年份（用于计算起始年份）
      qi_yun_days: 节气距离天数（简化，实际应精确计算）
      
    返回:
      (大运列表, 起运年龄, 起运年份)
    """
    # 判定顺排/逆排
    # 阳男阴女顺排，阴男阳女逆排
    gan = bazi.year.gan
    gender = bazi.gender
    # 年干阴阳: 甲丙戊庚壬为阳（偶数索引0,2,4,6,8）
    year_gan_idx = TIAN_GAN_ORDER[gan]
    is_yang = year_gan_idx % 2 == 0
    
    is_shun = (is_yang and gender == "男") or (not is_yang and gender == "女")
    
    # 月柱干支
    month_gan = bazi.month.gan
    month_zhi = bazi.month.zhi
    
    # 生成10步大运
    da_yun_list = []
    for step in range(8):  # 8步大运
        day_step = step + 1  # 从第一步开始
        if is_shun:
            gan_ = next_gan(month_gan, day_step)
            zhi_ = next_zhi(month_zhi, day_step)
        else:
            gan_ = prev_gan(month_gan, day_step)
            zhi_ = prev_zhi(month_zhi, day_step)
        
        da_yun_list.append(DaYun(
            gan=gan_,
            zhi=zhi_,
            start_age=0,   # 待填充
            end_age=0,     # 待填充
            start_year=0,  # 待填充
        ))
    
    # 起运年龄计算
    qi_yun_age = round(qi_yun_days / 3, 2)
    
    # 起运年份
    qi_yun_year = birth_year
    
    # 取整
    qi_yun_age_int = int(qi_yun_age)
    if qi_yun_age - qi_yun_age_int >= 0.7:
        qi_yun_year = birth_year + qi_yun_age_int + 1
    else:
        qi_yun_year = birth_year + qi_yun_age_int
    
    # 填充大运年龄
    for i, dy in enumerate(da_yun_list):
        start_age = qi_yun_age_int + i * 10
        end_age = qi_yun_age_int + (i + 1) * 10 - 1
        start_year = birth_year + qi_yun_age_int + i * 10
        
        dy.start_age = start_age
        dy.end_age = end_age
        dy.start_year = start_year
    
    return da_yun_list, qi_yun_age, qi_yun_year


def compute_da_yun_scores(bazi: BaZi,
                           da_yun_list: list[DaYun]) -> list[tuple[int, float]]:
    """
    评估每步大运的吉凶评分

    返回: [(index, score), ...]  score越高越好
    评分逻辑: 大运干支为喜用则加分，为忌神则减分
    """
    from ge_ju import determine_xi_yong_shen

    xi_yong, ji_shen = determine_xi_yong_shen(bazi)

    results = []
    for i, dy in enumerate(da_yun_list):
        # 大运天干五行 + 地支五行
        gan_wx = TIAN_GAN_WU_XING[dy.gan]
        zhi_wx = DI_ZHI_WU_XING[dy.zhi]
        dy_wx = {gan_wx, zhi_wx}

        score = 5.0  # 基准分

        for wx in dy_wx:
            if wx in xi_yong:
                if wx == xi_yong[0]:
                    score += 2.0  # 第一喜用
                else:
                    score += 1.5  # 其他喜用
            if wx in ji_shen:
                if wx == ji_shen[0]:
                    score -= 2.0  # 第一忌神
                else:
                    score -= 1.5  # 其他忌神

        score = max(0, min(10, score))
        results.append((i, round(score, 1)))

    return results


if __name__ == "__main__":
    from constants import BaZi, Pillar
    
    test_cases = [
        ("家主", BaZi(year=Pillar("甲", "午"), month=Pillar("己", "巳"),
                      day=Pillar("戊", "午"), hour=Pillar("壬", "子"), gender="男"),
         1968),
        ("子源", BaZi(year=Pillar("庚", "申"), month=Pillar("辛", "巳"),
                      day=Pillar("甲", "午"), hour=Pillar("丙", "寅"), gender="男"),
         1980),
        ("主母", BaZi(year=Pillar("戊", "午"), month=Pillar("甲", "子"),
                      day=Pillar("庚", "戌"), hour=Pillar("丁", "亥"), gender="女"),
         1976),
    ]
    
    for name, b, byear in test_cases:
        dy_list, qy_age, qy_year = compute_da_yun(b, byear, qi_yun_days=1.1)
        scores = compute_da_yun_scores(b, dy_list)
        
        print(f"【{name}】{b.summary()}")
        print(f"  起运年龄: {qy_age:.1f}岁 ≈ {qy_year}年起")
        print(f"  大运序列:")
        for i, dy in enumerate(dy_list):
            score = scores[i][1]
            star = "🏆" if score >= 8 else "✅" if score >= 6 else "⚠️" if score >= 4 else "❌"
            print(f"    {star} {dy.gan_zhi} ({dy.start_age}~{dy.end_age}岁, {dy.start_year}年起) — {score}/10")
        print()
