"""
金鉴真人 食伤评分引擎 v1.0
食伤评分新算法(2026-07-01 老板校准,九龙道长体系):

食伤总分 = 比劫(生食伤)的全部分数 + 食伤(我生五行)本身的分数

比劫生食伤: 比劫为同我五行,生我生五行=食伤
食伤得令 = 月令有比劫(生食伤) = 月令有食伤本身

来源: 九龙道长能量链条 印->比劫->食伤->财->官
"""

from constants import DI_ZHI_CANG_GAN, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan

# 位置基础分（满分100分）
POS_SCORES = {"年干": 8.0, "月干": 12.0, "时干": 12.0, "年支": 4.0, "月令": 40.0, "日支": 12.0, "时支": 12.0}

# 藏干百分比
CANG_PCTS = [1.0, 0.6, 0.3]  # 本气100%, 中气60%, 余气30%

# 五行生克
WU_XING_SHENG = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}

# 五行名称速查
WX_CHARS = {"金": "庚辛申酉", "水": "壬癸亥子", "木": "甲乙寅卯", "火": "丙丁巳午", "土": "戊己辰戌丑未"}

# 五行中文名
WX_CN = {"金": "金", "水": "水", "木": "木", "火": "火", "土": "土"}


def calc_shi_shang_score(ri_zhu: str, gans: list[str], zhis: list[str]) -> dict:
    """
    计算食伤分数（新算法）

    返回:
        dict: {
            "ri_zhu": 日主,
            "shi_shang_wx": 食伤五行,
            "bi_jie_wx": 比劫五行,
            "bi_jie_score": 比劫生食伤分数,
            "shi_shang_score": 食伤本身分数,
            "total_score": 总分,
            "details": [详细计分明细]
        }
    """
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    bi_jie_wx = ri_wx  # 同我者 = 比劫五行
    shi_shang_wx = WU_XING_SHENG[ri_wx]  # 我生者 = 食伤五行

    bi_jie_total = 0.0
    shi_shang_total = 0.0
    details = []

    # 天干计分
    for pos, idx in [("年干", 0), ("月干", 1), ("时干", 3)]:
        if idx >= len(gans):
            continue
        wx = TIAN_GAN_WU_XING[gans[idx]]
        score = POS_SCORES[pos]

        if wx == bi_jie_wx:
            bi_jie_total += score
            ss = get_shi_shen_for_gan(gans[idx], ri_zhu)
            details.append(
                {
                    "position": pos,
                    "gan_or_cang": gans[idx],
                    "shi_shen": ss,
                    "score": score,
                    "category": "比劫生食伤",
                    "explanation": f"{gans[idx]}({wx})={ss}，比劫生食伤（{wx}生{shi_shang_wx}）",
                }
            )
        elif wx == shi_shang_wx:
            shi_shang_total += score
            ss = get_shi_shen_for_gan(gans[idx], ri_zhu)
            details.append(
                {
                    "position": pos,
                    "gan_or_cang": gans[idx],
                    "shi_shen": ss,
                    "score": score,
                    "category": "食伤本身",
                    "explanation": f"{gans[idx]}({wx})={ss}，食伤本身",
                }
            )

    # 地支藏干计分
    for pos, idx in [("年支", 0), ("月令", 1), ("日支", 2), ("时支", 3)]:
        if idx >= len(zhis):
            continue
        z = zhis[idx]
        cangs = DI_ZHI_CANG_GAN.get(z, [])
        for i, (cg, _) in enumerate(cangs):
            wx = TIAN_GAN_WU_XING[cg]
            pct = CANG_PCTS[i] if i < len(CANG_PCTS) else 0.3
            score = round(POS_SCORES[pos] * pct, 1)
            rank = ["本气", "中气", "余气"][i] if i < 3 else "余气"

            if wx == bi_jie_wx:
                bi_jie_total += score
                ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
                details.append(
                    {
                        "position": f"{pos}({z})",
                        "gan_or_cang": cg,
                        "rank": rank,
                        "shi_shen": ss,
                        "score": score,
                        "category": "比劫生食伤",
                        "explanation": f"{z}藏{rank}{cg}={ss}，比劫生食伤（{wx}生{shi_shang_wx}）",
                    }
                )
            elif wx == shi_shang_wx:
                shi_shang_total += score
                ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
                details.append(
                    {
                        "position": f"{pos}({z})",
                        "gan_or_cang": cg,
                        "rank": rank,
                        "shi_shen": ss,
                        "score": score,
                        "category": "食伤本身",
                        "explanation": f"{z}藏{rank}{cg}={ss}，食伤本身",
                    }
                )

    bi_jie_total = round(bi_jie_total, 1)
    shi_shang_total = round(shi_shang_total, 1)
    total_score = round(bi_jie_total + shi_shang_total, 1)

    # 等级判断
    if total_score >= 80:
        level = "极旺"
    elif total_score >= 55:
        level = "旺"
    elif total_score >= 30:
        level = "中等"
    elif total_score >= 15:
        level = "偏弱"
    else:
        level = "极弱"

    return {
        "ri_zhu": ri_zhu,
        "bi_jie_wx": bi_jie_wx,
        "shi_shang_wx": shi_shang_wx,
        "bi_jie_score": bi_jie_total,
        "shi_shang_score": shi_shang_total,
        "total_score": total_score,
        "level": level,
        "details": details,
    }


def analyze_shi_shang_full(ri_zhu: str, gans: list[str], zhis: list[str]) -> str:
    """生成食伤分析文本"""
    result = calc_shi_shang_score(ri_zhu, gans, zhis)

    lines = []
    lines.append(f"食伤五行 = {result['shi_shang_wx']}（{WX_CHARS[result['shi_shang_wx']]}）")
    lines.append(f"比劫（生食伤）五行 = {result['bi_jie_wx']}（{WX_CHARS[result['bi_jie_wx']]}）")
    lines.append("")
    lines.append(f"【比劫生食伤】 +{result['bi_jie_score']}分")

    bi_items = [d for d in result["details"] if d["category"] == "比劫生食伤"]
    for d in bi_items:
        lines.append(f"  {d['position']} {d['gan_or_cang']} = {d['shi_shen']} → +{d['score']}")

    lines.append(f"【食伤本身】 +{result['shi_shang_score']}分")
    ss_items = [d for d in result["details"] if d["category"] == "食伤本身"]
    for d in ss_items:
        lines.append(f"  {d['position']} {d['gan_or_cang']} = {d['shi_shen']} → +{d['score']}")

    lines.append("")
    lines.append(
        f"食伤总分 = {result['bi_jie_score']} + {result['shi_shang_score']} = {result['total_score']}分（{result['level']}）"
    )

    return "\n".join(lines)


# ── 测试 ──
if __name__ == "__main__":
    test_cases = [
        ("家主", "辛", ["庚", "癸", "辛", "辛"], ["申", "未", "亥", "卯"]),
        ("主母", "庚", ["丁", "丁", "庚", "壬"], ["卯", "未", "午", "午"]),
        ("子源", "丙", ["辛", "癸", "丙", "癸"], ["卯", "巳", "戌", "巳"]),
        ("祖母", "癸", ["壬", "戊", "癸", "戊"], ["辰", "申", "巳", "午"]),
    ]

    for name, rz, gs, zs in test_cases:
        print(f"\n{'=' * 50}")
        print(f"{name}（{rz}日主）")
        print(analyze_shi_shang_full(rz, gs, zs))
