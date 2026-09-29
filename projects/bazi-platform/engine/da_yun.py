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


# ── ⛔ [legacy] 节气日期固定近似表 —— 起运已改走 engine/qi_yun.py（精确节气），本表仅供历史代码读取 ──
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
    🚨 [已废弃·legacy] 起运天数计算 —— 固定日期近似表版（无时辰、±1天误差）

    ⛔ 禁止在新代码中调用。唯一口径 = engine/qi_yun.py（精确节气·秒级）。
    本函数仅为兼容旧调用保留：内部已改为委派 qi_yun.py 的唯一算法
    （用 12:00 作为缺省出生时刻，精度足够但非真值；含时辰的调用请直接用 qi_yun.compute_qi_yun）。
    """
    import warnings
    from datetime import datetime as _dt
    warnings.warn("da_yun.compute_qi_yun_days 已废弃 → 请用 engine/qi_yun.compute_qi_yun", DeprecationWarning, stacklevel=2)
    from qi_yun import compute_qi_yun
    qy = compute_qi_yun(_dt(birth_year, birth_month, birth_day, 12, 0), "男" if is_shun else "女",
                        month_zhi=month_zhi)
    return qy["天数"]


def compute_da_yun(bazi: BaZi, birth_year: int = 1980, birth_month: int = 1, birth_day: int = 1,
                   qi_yun_days: float | None = None, birth_hour: int = 12, birth_minute: int = 0) -> tuple[list[DaYun], float, int]:
    """
    计算大运 —— 🚨 唯一口径：起运一律委派 engine/qi_yun.py（R1~R9）

    参数:
      bazi: 八字
      birth_year/month/day: 出生年月日
      qi_yun_days: [已废弃] 旧版外部传入的起运天数；仍被接受但仅用于一致性告警，
                   真值一律由 qi_yun.py 依精确节气重算（禁止用旧口径结果）
      birth_hour/birth_minute: 出生时刻（真太阳时），默认 12:00

    返回:
      (大运列表, 起运年龄, 起运年份)
    """
    import warnings
    from datetime import datetime as _dt
    from qi_yun import compute_qi_yun

    # ── 唯一口径：qi_yun.py ──
    birth_dt = _dt(birth_year, birth_month, birth_day, birth_hour, birth_minute)
    qy = compute_qi_yun(birth_dt, bazi.gender,
                        month_gan=bazi.month.gan, month_zhi=bazi.month.zhi)
    if qi_yun_days is not None and abs(float(qi_yun_days) - qy["天数"]) > 0.01:
        warnings.warn(
            f"[qi_yun] 忽略外部传入 qi_yun_days={qi_yun_days}（旧口径），"
            f"采用 qi_yun.py 唯一口径 {qy['天数']}", RuntimeWarning, stacklevel=2)

    qi_yun_age = qy["起运年龄"]
    age_base = qy["年龄基准"]
    start_year_base = qy["起始年"]

    da_yun_list = []
    for i, step in enumerate(qy.get("大运", [])):
        da_yun_list.append(DaYun(
            gan=step["干支"][0],
            zhi=step["干支"][1],
            start_age=step["起始岁"],
            end_age=step["结束岁"],
            start_year=step["起始年"],
        ))

    return da_yun_list, qi_yun_age, start_year_base



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
