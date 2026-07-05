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

from constants import DI_ZHI, DI_ZHI_WU_XING, TIAN_GAN, TIAN_GAN_WU_XING, BaZi, DaYun

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


# ── 节气日期表（简化版）──
# 用于计算起运天数（节气距离）
# 格式: 月支序号(寅=1) → (节气月, 节气日)
# 节气日期每年略有波动(±1天)，这里取平均值
# 月支对应的「节」：寅=立春, 卯=惊蛰, 辰=清明, 巳=立夏,
# 午=芒种, 未=小暑, 申=立秋, 酉=白露, 戌=寒露,
# 亥=立冬, 子=大雪, 丑=小寒
JIE_QI = {
    1: (2, 4),   # 寅→立春·2月4日
    2: (3, 6),   # 卯→惊蛰·3月6日
    3: (4, 5),   # 辰→清明·4月5日
    4: (5, 6),   # 巳→立夏·5月6日
    5: (6, 6),   # 午→芒种·6月6日
    6: (7, 7),   # 未→小暑·7月7日
    7: (8, 7),   # 申→立秋·8月7日
    8: (9, 8),   # 酉→白露·9月8日
    9: (10, 8),  # 戌→寒露·10月8日
    10: (11, 7), # 亥→立冬·11月7日
    11: (12, 7), # 子→大雪·12月7日
    12: (1, 6),  # 丑→小寒·1月6日
}
# 月支序号映射（寅=1, 卯=2, ..., 丑=12）
ZHI_IDX = {"寅": 1, "卯": 2, "辰": 3, "巳": 4, "午": 5, "未": 6,
           "申": 7, "酉": 8, "戌": 9, "亥": 10, "子": 11, "丑": 12}


def compute_qi_yun_days(birth_year: int, birth_month: int, birth_day: int, month_zhi: str, is_shun: bool) -> float:
    """
    计算起运天数（节气距离天数）

    顺排(阳男阴女): 出生日 → 下一个节气 的天数
    逆排(阴男阳女): 上一个节气 → 出生日 的天数

    Args:
        birth_year: 出生年
        birth_month: 出生月
        birth_day: 出生日
        month_zhi: 月支（如"未"）
        is_shun: True=顺排, False=逆排

    Returns:
        qi_yun_days: 节气距离天数（至少1天）
    """
    from datetime import date

    zhi_idx = ZHI_IDX.get(month_zhi, 1)
    birth = date(birth_year, birth_month, birth_day)

    if is_shun:
        # 顺排：下一个节气 = 月支的下一个序号的节
        next_idx = zhi_idx + 1 if zhi_idx < 12 else 1
        jie_month, jie_day = JIE_QI[next_idx]
        jie_year = birth_year
        # 节气月跨年处理
        if jie_month == 1 and birth_month > 6:
            jie_year = birth_year + 1
        jie_date = date(jie_year, jie_month, jie_day)
        delta = (jie_date - birth).days
    else:
        # 逆排：上一个节气 = 月支对应的节
        jie_month, jie_day = JIE_QI[zhi_idx]
        jie_year = birth_year
        # 节气月跨年处理
        if jie_month > birth_month and jie_month - birth_month > 6:
            jie_year = birth_year + 1
        elif jie_month > birth_month:
            jie_year = birth_year - 1
        jie_date = date(jie_year, jie_month, jie_day)
        delta = (birth - jie_date).days

    return max(1.0, float(delta))


def compute_da_yun(bazi: BaZi, birth_year: int = 1980, birth_month: int = 1, birth_day: int = 1,
                   qi_yun_days: float | None = None) -> tuple[list[DaYun], float, int]:
    """
    计算大运

    参数:
      bazi: 八字
      birth_year: 出生年份
      birth_month: 出生月份（用于节气计算）
      birth_day: 出生日（用于节气计算）
      qi_yun_days: 节气距离天数（None=自动基于节气表计算）

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

    # ── 起运天数计算 ──
    # 如果未提供qi_yun_days, 基于节气表自动计算
    if qi_yun_days is None:
        qi_yun_days = compute_qi_yun_days(birth_year, birth_month, birth_day, month_zhi, is_shun)

    # ── 起运年龄计算 ──
    # 规则: (节气距离天数) / 3 = 起运年龄(岁)
    qi_yun_age = round(qi_yun_days / 3, 2)

    # ── 最大步数计算 ──
    # 按平均寿命100岁计算所需大运步数
    max_steps = max(8, int((100 - qi_yun_age) / 10) + 2)  # 至少8步, 最多12步
    max_steps = min(max_steps, 12)

    # ── 生成大运干支序列 ──
    da_yun_list = []
    for step in range(max_steps):
        day_step = step + 1  # 从第一步开始
        if is_shun:
            gan_ = next_gan(month_gan, day_step)
            zhi_ = next_zhi(month_zhi, day_step)
        else:
            gan_ = prev_gan(month_gan, day_step)
            zhi_ = prev_zhi(month_zhi, day_step)

        # 填充大运年龄（基于浮点数qi_yun_age，不截断！）
        start_age = round(qi_yun_age + step * 10, 1)
        end_age = round(qi_yun_age + (step + 1) * 10, 1)

        # 起运年份 = 出生年 + 起运年龄(取整)
        start_year = birth_year + int(qi_yun_age + step * 10)

        da_yun_list.append(
            DaYun(
                gan=gan_,
                zhi=zhi_,
                start_age=start_age,
                end_age=end_age,
                start_year=start_year,
            )
        )

    # ── 起运年份计算 ──
    # 规则: 出生年 + 起运年龄的整数部分, 小数>=0.5则进1
    qi_yun_age_int = int(qi_yun_age)
    qi_yun_age_frac = qi_yun_age - qi_yun_age_int
    qi_yun_year = birth_year + qi_yun_age_int
    if qi_yun_age_frac >= 0.5:
        qi_yun_year += 1

    # 如果起运年>出生年但第一步大运start_year=出生年, 保持一致性
    # 例如: 1980年出生, 0.37岁起运, 第一步大运从1980年开始(0.37~10.37岁)

    return da_yun_list, qi_yun_age, qi_yun_year


def compute_da_yun_scores(bazi: BaZi, da_yun_list: list[DaYun]) -> list[tuple[int, float]]:
    """
    评估每步大运的吉凶评分

    ⚠️ 审计标记 (2026-06-29): 评分公式为自创，九龙道长原始素材无此数值体系
       - 基准分5.0: 无原始依据
       - 主喜用+2.0/次喜用+1.5/主忌神-2.0/次忌神-1.5: 无原始依据
       - 建议: 待修改为基于原始素材的定性判断，或标注为实验性评分

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
        # ⚠️ 以下数值(5.0/2.0/1.5)均为自创，无九龙道长原始素材支撑
        score = 5.0  # 基准分 (自创数值)

        # 天干独立计分
        if gan_wx in xi_yong:
            if gan_wx == xi_yong[0]:
                score += 2.0  # 自创
            else:
                score += 1.5  # 自创
        if gan_wx in ji_shen:
            if gan_wx == ji_shen[0]:
                score -= 2.0  # 自创
            else:
                score -= 1.5  # 自创

        # 地支独立计分
        if zhi_wx in xi_yong:
            if zhi_wx == xi_yong[0]:
                score += 2.0  # 自创
            else:
                score += 1.5  # 自创
        if zhi_wx in ji_shen:
            if zhi_wx == ji_shen[0]:
                score -= 2.0  # 自创
            else:
                score -= 1.5  # 自创

        score = max(0, min(10, score))
        results.append((i, round(score, 1)))

    return results


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
            1968,
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
            1980,
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
            1976,
        ),
    ]

    for name, b, byear in test_cases:
        dy_list, qy_age, qy_year = compute_da_yun(b, byear, qi_yun_days=1.1)
        scores = compute_da_yun_scores(b, dy_list)

        print(f"【{name}】{b.summary()}")
        print(f"  起运年龄: {qy_age:.1f}岁 ≈ {qy_year}年起")
        print("  大运序列:")
        for i, dy in enumerate(dy_list):
            score = scores[i][1]
            star = "🏆" if score >= 8 else "✅" if score >= 6 else "⚠️" if score >= 4 else "❌"
            print(f"    {star} {dy.gan_zhi} ({dy.start_age}~{dy.end_age}岁, {dy.start_year}年起) — {score}/10")
        print()
