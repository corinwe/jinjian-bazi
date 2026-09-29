#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起运唯一算法 v1.0 —— 金鉴真人·全系统唯一口径（SINGLE SOURCE OF TRUTH）
=====================================================================
🚨 任何地方要算起运/大运年龄/大运年份，**必须** import 本模块，禁止另行实现。
   历史教训：全库曾有 4 套并行实现（bazi-engine.py 精确版 / da_yun.py 固定日期表版 /
   bazi-full-verify.py 估算版 / bazi-verify.py 又一份固定表），导致同一个命造
   起运年龄 8岁8个月 vs 8岁10个月 并存、大运年龄带差 1 岁、大运起始年差 1 年。

── 唯一规则（R1~R9）─────────────────────────────────────
R1 顺逆：阳男阴女顺排、阴男阳女逆排；年干阴阳按 **立春精确定界**（jieqi.year_gan_zhi）
R2 节气：一律走 engine/jieqi.py 精确节气（真太阳时口径，精确到分钟），
        顺排取「下一个节」、逆排取「上一个节」——禁止使用固定日期近似表
R3 天数：days_diff = |节气时刻 − 出生时刻| 秒级精度 ÷ 86400
R4 起运年龄（真值）= days_diff / 3.0  （3天折1年）
R5 展示折算：年=int(d//3) 月=int(余*4) 天=int((余*4−月)*30)  （1天折4个月）
R6 起运年龄基准（大运年龄带用）：<1年→1；≥1年→**int() 向下取整**（8.7岁→8岁起运，不向上取整）
        —— 九龙道长标准·2026-06-25 老板校准，禁止 math.ceil
R7 大运起始年：起运**实际日期**所在年；若该月 ≥10月（Q4）→ 进位次年
R8 步长：每步 10 年；默认输出 11 步（覆盖起运年 ~ 起运年+100）
R9 展示格式（唯一）：`起运8岁8个月18天（8.72岁·约2015年2月起运·阳女逆排）`
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import jieqi  # noqa: E402

TIAN_GAN = list("甲乙丙丁戊己庚辛壬癸")
DI_ZHI = list("子丑寅卯辰巳午未申酉戌亥")

__all__ = ["compute_qi_yun", "da_yun_series", "format_qi_yun", "direction_of", "CANONICAL_RULES"]


def direction_of(birth_dt: datetime, gender: str) -> tuple[str, str]:
    """R1 顺逆判定（年干阴阳按立春精确定界）"""
    gan, _ = jieqi.year_gan_zhi(birth_dt)
    is_yang = gan in "甲丙戊庚壬"
    if (is_yang and gender == "男") or (not is_yang and gender == "女"):
        return "顺排", ("阳男顺排" if is_yang else "阴女顺排")
    return "逆排", ("阴男逆排" if gender == "男" else "阳女逆排")


def compute_qi_yun(birth_dt: datetime, gender: str, *,
                   month_gan: "str | None" = None, month_zhi: "str | None" = None,
                   n_steps: int = 11, direction: "str | None" = None) -> dict:
    """起运唯一算法。birth_dt = 真太阳时修正后的出生时刻（与排盘同一时点）。
    direction: 已知顺逆时（'顺排'/'逆排'）可直接传入，跳过 R1 推断——供验证脚本复用，禁止另写实现。"""
    direction_label = direction_of(birth_dt, gender)[1]
    direction = direction or direction_of(birth_dt, gender)[0]

    # R2 精确节气（jieqi.py，分钟级）+ R3 秒级天数
    jq_name, jq_dt = jieqi.next_jieqi(birth_dt) if direction == "顺排" else jieqi.prev_jieqi(birth_dt)
    days_diff = abs((jq_dt - birth_dt).total_seconds()) / 86400.0

    # R4 起运年龄真值
    age = days_diff / 3.0
    # R5 年/月/天折算
    y = int(days_diff // 3)
    rem = days_diff % 3
    m = int(rem * 4)
    d = int((rem * 4 - m) * 30)

    # R6 年龄基准（向下取整·九龙2026-06-25校准）
    age_base = 1 if age < 1 else int(age)

    # R7 起始年（实际起运日期，Q4进位）
    from datetime import timedelta
    start_dt = birth_dt + timedelta(days=age * 365.25)
    start_year = start_dt.year + (1 if start_dt.month >= 10 else 0)

    out = {
        "顺逆": direction, "顺逆标签": direction_label,
        "节气": jq_name, "节气时刻": jq_dt.strftime("%Y-%m-%d %H:%M"),
        "出生时刻": birth_dt.strftime("%Y-%m-%d %H:%M"),
        "天数": round(days_diff, 4),
        "起运年龄": round(age, 2), "年龄基准": age_base,
        "岁": y, "个月": m, "天": d,
        "起运日期": start_dt.strftime("%Y-%m-%d"), "起始年": start_year,
    }
    if month_gan and month_zhi:
        gi, zi = TIAN_GAN.index(month_gan), DI_ZHI.index(month_zhi)
        step = 1 if direction == "顺排" else -1
        out["大运"] = [{
            "序号": i + 1,
            "干支": f"{TIAN_GAN[(gi + step * (i + 1)) % 10]}{DI_ZHI[(zi + step * (i + 1)) % 12]}",
            "起始岁": age_base + i * 10, "结束岁": age_base + i * 10 + 9,
            "起始年": start_year + i * 10, "结束年": start_year + i * 10 + 9,
        } for i in range(n_steps)]
    return out


def da_yun_series(bazi, birth_dt: datetime, n_steps: int = 11) -> dict:
    """便捷入口：传 BaZi 对象（有 gender/year/month 柱）+ 出生时刻"""
    return compute_qi_yun(birth_dt, bazi.gender,
                          month_gan=bazi.month.gan, month_zhi=bazi.month.zhi, n_steps=n_steps)


def format_qi_yun(qy: dict) -> str:
    """R9 唯一展示格式"""
    return (f"起运{qy['岁']}岁{qy['个月']}个月{qy['天']}天"
            f"（{qy['起运年龄']}岁·约{qy['起始年']}年{qy['起运日期'][5:7].lstrip('0')}月起运·{qy['顺逆标签']}）")


CANONICAL_RULES = "R1顺逆·R2精确节气·R3秒级天数·R4年龄=d/3·R5折算·R6向下取整·R7实际起运年Q4进位·R8每步10年11步·R9统一展示格式"

if __name__ == "__main__":
    import json
    from datetime import datetime as dt
    # 自检样例：静（阳女逆排·应得 8岁8个月+ / 8.72岁 / 2015年起运）
    for name, bdt, g, mg, mz in [
        ("静", dt(2006, 4, 1, 5, 25), "女", "辛", "卯"),
        ("家主", dt(1980, 8, 6, 5, 30), "男", "癸", "未"),
        ("少爷", dt(2011, 5, 21, 10, 30), "男", "癸", "巳"),
    ]:
        qy = compute_qi_yun(bdt, g, month_gan=mg, month_zhi=mz)
        print(f"【{name}】{format_qi_yun(qy)} | 节气{qy['节气']} {qy['节气时刻']} | 天数{qy['天数']}")
        print(f"      首运 {qy['大运'][0]['干支']} {qy['大运'][0]['起始岁']}~{qy['大运'][0]['结束岁']}岁 "
              f"{qy['大运'][0]['起始年']}~{qy['大运'][0]['结束年']}")
