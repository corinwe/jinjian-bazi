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

import math

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
        # 逆排节气月跨年处理：节气在出生月之后→节气在上一年
        if jie_month > birth_month and jie_month - birth_month > 6:
            jie_year = birth_year - 1  # 逆排跨年：如子月(12月)节气在1月出生之前→上一年
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

        # 填充大运年龄（九龙道长向上取整规则）
        # 起运年龄向上取整为起始岁数，每步管10年
        # 例: 0.33→1, 第一步1~10岁, 第二步11~20岁
        base = math.ceil(qi_yun_age)
        start_age = base + step * 10
        end_age = base + (step + 1) * 10 - 1

        # ── 大运起算年份（基于浮点偏移，不用int截断）──
        # 原始规则: "一天为四个月" → qi_yun_age是浮点年数
        # 大运起算 = 出生 + qi_yun_age年 + step*10年
        # 用浮点年份偏移代替int()截断，精确到月份
        start_age_float = qi_yun_age + step * 10
        start_age_int = int(start_age_float)
        start_month_offset = int(round((start_age_float - start_age_int) * 12))

        # 从出生月偏移
        effective_month = birth_month + start_month_offset
        year_carry = 0
        while effective_month > 12:
            effective_month -= 12
            year_carry += 1

        # 如果偏移后在下半年(≥7月), 大运已过该年核心区间
        # 大运主要覆盖下一个完整年度开始的10年
        start_year = birth_year + start_age_int + year_carry
        # 如果在第4季度(10~12月)起运, 该年只占尾巴, 跳到下一年
        if effective_month >= 10:
            start_year += 1

        # 计算结束年份 = 起始年 + 10 - 1（因为大运管10年）
        end_year = start_year + 9

        da_yun_list.append(
            DaYun(
                gan=gan_,
                zhi=zhi_,
                start_age=start_age,
                end_age=end_age,
                start_year=start_year,
            )
        )

    # ── 起运年份计算（与各步大运的浮点偏移算法一致）──
    # 规则: 出生年 + 起运年龄的整数部分, 小数>=0.5则进1
    qi_yun_age_int = int(qi_yun_age)
    qi_yun_age_frac = qi_yun_age - qi_yun_age_int
    qi_yun_year = birth_year + qi_yun_age_int
    if qi_yun_age_frac >= 0.5:
        qi_yun_year += 1

    # 如果起运年>出生年但第一步大运start_year=出生年, 保持一致性
    # 👆 旧逻辑（int截断）. 新逻辑改用浮点月份偏移+Q4进位:
    # 0.33岁=4个月→出生月+4=Q4(12月)→进位→start_year=出生年+1
    # 不再依赖int(qi_yun_age)取整，而是精确到月份的浮点偏移

    return da_yun_list, qi_yun_age, qi_yun_year


def classify_da_yun(bazi: BaZi, da_yun_list: list[DaYun]) -> list[dict]:
    """
    大运定性分类（基于原始理论·2026-07-07替换自创评分）
    
    规则来源：bazi-fortune-analysis §6.9（格局判定与身强弱校验）
    每个大运的天干和地支，分别判断是喜用还是忌神：
      - 双喜用（天干+地支都是喜用）→ 最佳大运
      - 一喜一忌 → 中等大运
      - 双忌神（天干+地支都是忌神）→ 最差大运
    
    返回: [{"index": i, "gan": gan, "zhi": zhi, "gan_xi_ji": str, "zhi_xi_ji": str, "label": str}, ...]
      label: "纯喜用🏆" / "一喜一忌" / "纯忌神⚠️"
    """
    from ge_ju import determine_xi_yong_shen
    
    xi_yong, ji_shen = determine_xi_yong_shen(bazi)
    
    results = []
    for i, dy in enumerate(da_yun_list):
        gan_wx = TIAN_GAN_WU_XING[dy.gan]
        zhi_wx = DI_ZHI_WU_XING[dy.zhi]
        
        gan_label = "喜用" if gan_wx in xi_yong else ("忌神" if gan_wx in ji_shen else "平")
        zhi_label = "喜用" if zhi_wx in xi_yong else ("忌神" if zhi_wx in ji_shen else "平")
        
        if gan_label == "喜用" and zhi_label == "喜用":
            label = "纯喜用🏆"
        elif gan_label == "忌神" and zhi_label == "忌神":
            label = "纯忌神⚠️"
        elif gan_label == "喜用" and zhi_label == "忌神":
            label = "一喜一忌(天喜地忌)"
        elif gan_label == "忌神" and zhi_label == "喜用":
            label = "一喜一忌(天忌地喜)"
        else:
            label = "中等"
        
        results.append({
            "index": i,
            "gan": dy.gan,
            "zhi": dy.zhi,
            "gan_gan_zhi": f"{dy.gan}{dy.zhi}",
            "gan_xi_ji": gan_label,
            "zhi_xi_ji": zhi_label,
            "label": label
        })
    
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
        classified = classify_da_yun(b, dy_list)

        print(f"【{name}】{b.summary()}")
        print(f"  起运年龄: {qy_age:.1f}岁 ≈ {qy_year}年起")
        print("  大运定性序列:")
        for i, dy in enumerate(dy_list):
            dc = classified[i] if i < len(classified) else {}
            print(f"    {dc.get('label','?')} {dy.gan_zhi} ({dy.start_age}~{dy.end_age}岁, {dy.start_year}年起)")
        print()
