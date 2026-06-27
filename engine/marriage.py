"""
金鉴真人·婚姻分析引擎 v1.0

四大结婚信号:
  信号一: 日支夫妻宫被引动（冲/合/刑）
  信号二: 正财/正官到位（男命正财、女命正官）
  信号三: 财星生官（异性缘增加）
  信号四: 印星帮身（身弱可担家庭责任）

三个结婚窗口:
  窗口1（最佳）: 喜用神大运 + 夫妻宫引动 + 财/官到位
  窗口2（次佳）: 喜用神大运 + 财/官到位
  窗口3（较晚）: 大运中后期 + 夫妻宫引动

配偶特征:
  五行角度: 夫妻宫藏干定五行属性
  十神角度: 夫妻宫十神定性格
"""

from __future__ import annotations

from constants import DI_ZHI_CANG_GAN, DI_ZHI_WU_XING, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan
from xing_chong_he_hua import check_chong, check_liu_he


def analyze_marriage(
    ri_zhu: str,
    ri_zhi: str,
    gender: str,
    bazi_gans: list[str],
    shen_label: str,
    shen_score: float,
    xi_yong: list[str],
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_ages: list[int],
) -> dict:
    """
    婚姻完整分析
    """
    # ── 夫妻宫（日支）分析 ──
    ri_zhi_cangs = DI_ZHI_CANG_GAN.get(ri_zhi, [])
    ri_zhi_shi_shens = []
    for cg, ratio in ri_zhi_cangs:
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        ri_zhi_shi_shens.append({"cang_gan": cg, "shi_shen": ss, "ratio": ratio})

    # 夫妻宫十神主星（本气）
    ri_zhi_master = ri_zhi_shi_shens[0]["shi_shen"] if ri_zhi_shi_shens else ""

    # 配偶特征
    spouse_traits = []
    if ri_zhi_master == "正财":
        spouse_traits = ["务实", "稳重", "会理财", "贤惠"]
    elif ri_zhi_master == "偏财":
        spouse_traits = ["大方", "社交能力强", "有经济头脑"]
    elif ri_zhi_master == "正官":
        spouse_traits = ["正直", "有责任感", "传统"]
    elif ri_zhi_master == "七杀":
        spouse_traits = ["强势", "有能力", "有个性"]
    elif ri_zhi_master == "正印":
        spouse_traits = ["温和", "有文化", "包容"]
    elif ri_zhi_master == "偏印":
        spouse_traits = ["独特", "有深度", "独立"]
    elif ri_zhi_master == "伤官":
        spouse_traits = ["聪明", "有才华", "有个性"]
    elif ri_zhi_master == "食神":
        spouse_traits = ["温柔", "有才艺", "懂生活"]
    else:
        spouse_traits = ["普通人", "性格温和"]

    # 配偶五行
    master_wx = TIAN_GAN_WU_XING[ri_zhi_cangs[0][0]] if ri_zhi_cangs else ""

    # ── 结婚窗口 ──
    marriage_windows = []

    for i, (dg, dz, sa) in enumerate(zip(da_yun_gans, da_yun_zhis, da_yun_start_ages)):
        if sa < 20 or sa > 55:
            continue
        if sa > 45:
            break

        window_score = 0
        reasons = []

        # 信号1: 夫妻宫引动
        if check_chong(dz, ri_zhi) or check_liu_he(dz, ri_zhi):
            window_score += 1
            reasons.append("夫妻宫引动")

        # 信号2: 正财/正官到位（男财女官）
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if gender == "男" and dg_ss == "正财":
            window_score += 2
            reasons.append("正财到位")
        elif gender == "女" and dg_ss == "正官":
            window_score += 2
            reasons.append("正官到位")

        # 信号3: 大运为喜用
        dg_wx = TIAN_GAN_WU_XING[dg]
        dz_wx = DI_ZHI_WU_XING[dz]
        if dg_wx in xi_yong or dz_wx in xi_yong:
            window_score += 1
            reasons.append("喜用大运")

        # 信号4: 印星帮身（身弱可担家庭责任）
        if shen_label == "身弱" and dg_ss in ["正印", "偏印"]:
            window_score += 1
            reasons.append("印星扶身")

        if window_score >= 2:
            label = "🏆最佳窗口" if window_score >= 4 else "✅次佳窗口" if window_score >= 3 else "⚠️一般窗口"
            marriage_windows.append(
                {
                    "da_yun": f"{dg}{dz}",
                    "age_range": f"{sa}~{sa + 9}岁",
                    "score": window_score,
                    "label": label,
                    "reasons": reasons,
                }
            )

    # 排序
    marriage_windows.sort(key=lambda w: w["score"], reverse=True)

    # 最佳结婚年份估算
    best_window = marriage_windows[0] if marriage_windows else None
    if best_window:
        best_window_age = best_window["age_range"].split("~")[0]
    else:
        best_window_age = "暂无明显窗口"

    # 感情质量评估
    quality = "中等"
    quality_score = 5
    if (ri_zhi_master == "正财" and gender == "男") or (ri_zhi_master == "正官" and gender == "女"):
        quality_score += 1

    if shen_label == "身强":
        quality_score += 1
    elif shen_label == "身弱":
        quality_score -= 1

    if quality_score >= 7:
        quality = "上等"
    elif quality_score >= 5:
        quality = "中等偏上"
    elif quality_score >= 3:
        quality = "中等"
    else:
        quality = "下等"

    return {
        "ri_zhi_analysis": {
            "zhi": ri_zhi,
            "master_shi_shen": ri_zhi_master,
            "master_wu_xing": master_wx,
            "all_cang_gan": ri_zhi_shi_shens,
        },
        "spouse_traits": spouse_traits,
        "spouse_description": f"配偶性格{','.join(spouse_traits)}，五行偏{master_wx}",
        "marriage_windows": marriage_windows,
        "best_window_age": best_window_age,
        "quality": quality,
        "quality_score": quality_score,
    }


if __name__ == "__main__":
    # 测试: 子源 甲午日 男
    result = analyze_marriage(
        "甲",
        "午",
        "男",
        ["庚", "辛", "甲", "丙"],
        "身弱",
        12.0,
        ["水", "木"],
        ["壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"],
        ["午", "未", "申", "酉", "戌", "亥", "子", "丑"],
        [0, 10, 20, 30, 40, 50, 60, 70],
    )
    print(f"配偶: {result['spouse_description']}")
    print(f"质量: {result['quality']}")
    print(f"最佳窗口: {result['best_window_age']}岁")
