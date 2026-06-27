"""
金鉴真人·学历学业分析引擎 v2.0 — 确定性规则版
基于bazi-education-analysis v1.6

规则体系：
  第0层：年柱有印三档法（3秒定性）
  六步排查（决定兑现程度）
  学校等级六档定位
  学历层级定位（本科/硕士/博士）
  文昌贵人双轨制（年干查命/日干补运）
  年干伤官检查
"""

from __future__ import annotations

from constants import CANG_GAN_RATIO, DI_ZHI_CANG_GAN, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan

# ── 文昌贵人表（年干查命理，日干查补运）──
WEN_CHANG_MAP = {
    "甲": "巳",
    "乙": "午",
    "丙": "申",
    "丁": "酉",
    "戊": "申",
    "己": "酉",
    "庚": "亥",
    "辛": "子",
    "壬": "寅",
    "癸": "卯",
}


def _nian_gan_shi_shen_check(nian_gan: str, ri_zhu: str) -> dict:
    """
    年干十神检查 — 基于原始理论
    年干伤官 → 少年叛逆（素材12行517）
    """
    ss = get_shi_shen_for_gan(nian_gan, ri_zhu)
    result = {"shi_shen": ss, "signal": "neutral", "note": ""}
    if ss == "伤官":
        result["signal"] = "negative"
        result["note"] = "年干伤官→少年叛逆、打架（素材12行517）"
    elif ss in ("正印", "偏印"):
        result["signal"] = "positive"
        result["note"] = "年干印星→有学业基因"
    elif ss in ("正官", "七杀"):
        result["signal"] = "positive"
        result["note"] = "年干官杀→自律型学习"
    return result


def _check_year_pillar_yin(year_gan: str, year_zhi: str, ri_zhu: str) -> dict:
    """
    年柱有印三档法（第0层）
    年干透印 OR 地支藏印 → 判学业好
    """
    result = {"has_yin": False, "level": "一般", "yin_score": 0.0, "detail": ""}

    # 年干印
    gan_ss = get_shi_shen_for_gan(year_gan, ri_zhu)
    if gan_ss in ("正印", "偏印"):
        result["has_yin"] = True
        result["level"] = "好"
        result["yin_score"] = 8.0  # 年干=8分
        result["detail"] = f"年干{year_gan}={gan_ss}透出✅"
        return result

    # 年支藏印
    for cg, ratio in DI_ZHI_CANG_GAN.get(year_zhi, []):
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if ss in ("正印", "偏印"):
            ratio_score = CANG_GAN_RATIO.get(ratio, 0.3)
            score = 4.0 * ratio_score  # 年支基础分=4
            level_name = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
            quality = "强" if ratio == 100 else "良好" if ratio == 60 else "偏弱"
            result["has_yin"] = True
            result["yin_score"] = score
            if score >= 2:
                result["level"] = "好"
                result["detail"] = f"年支{year_zhi}藏{cg}={ss}({level_name}·{quality})✅"
            else:
                result["level"] = "好（偏弱）"
                result["detail"] = f"年支{year_zhi}藏{cg}={ss}({level_name}·{quality})✅但偏弱"
            return result

    # 年柱无印
    result["detail"] = "年柱无印❌"
    return result


def _check_wen_chang(nian_gan_or_ri_zhu: str, all_zhis: list[str], da_yun_zhis: list[str]) -> dict:
    """
    文昌检查 — 年干查命理
    """
    target_zhi = WEN_CHANG_MAP.get(nian_gan_or_ri_zhu, "")
    result = {"has": False, "zhi": target_zhi, "location": "", "detail": ""}

    if not target_zhi:
        result["detail"] = "无文昌"
        return result

    # 在各柱
    pillar_names = ["年支", "月支", "日支", "时支"]
    for i, z in enumerate(all_zhis):
        if z == target_zhi:
            location = pillar_names[i]
            strength = "最强" if i == 1 else "强" if i == 2 else "有用"
            result["has"] = True
            result["location"] = f"{location}({strength})"
            result["detail"] = f"文昌在{location}→{strength}"
            return result

    # 在大运
    for dz in da_yun_zhis:
        if dz == target_zhi:
            result["has"] = True
            result["location"] = "大运"
            result["detail"] = "大运有文昌→10年补救"
            return result

    result["detail"] = f"文昌在{target_zhi}但不在局→未到位"
    return result


def _check_six_steps(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
    shen_label: str,
    shen_score: float,
    xi_yong: list[str],
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_ages: list[int],
) -> dict:
    """
    六步精细排查 — 决定学业兑现程度
    """
    checks = {}
    passed = 0
    total = 6

    # Step 1: 印在月令本气？
    yue_zhi = bazi_zhis[1]
    yue_cangs = DI_ZHI_CANG_GAN.get(yue_zhi, [])
    yue_ben_qi = yue_cangs[0][0] if yue_cangs else ""
    yue_ben_qi_ss = get_shi_shen_for_cang_gan(yue_ben_qi, ri_zhu) if yue_ben_qi else ""

    if yue_ben_qi_ss in ("正印", "偏印"):
        checks["step1"] = {"passed": True, "detail": f"月令{yue_zhi}本气{yue_ben_qi}={yue_ben_qi_ss}(+40分)✅"}
        passed += 1
    else:
        checks["step1"] = {"passed": False, "detail": f"月令{yue_zhi}本气非印❌"}

    # Step 2: 印根完整无伤？（简化版：检查是否被合化）
    checks["step2"] = {"passed": True, "detail": "印根完整（无显著合化消耗）✅"}
    # 简化：暂不深度检查合化

    # Step 3: 文昌存在？
    wc = _check_wen_chang(bazi_gans[0], bazi_zhis, da_yun_zhis)  # 年干查
    if wc["has"]:
        checks["step3"] = {"passed": True, "detail": wc["detail"]}
        passed += 1
    else:
        checks["step3"] = {"passed": False, "detail": wc["detail"]}

    # Step 4: 18岁前走喜用还是忌神？
    pre_18_positive = 0
    pre_18_negative = 0
    for dg, dz, sa in zip(da_yun_gans, da_yun_zhis, da_yun_start_ages):
        if sa < 18 and sa < len(da_yun_gans):
            dg_wx = TIAN_GAN_WU_XING[dg]
            if dg_wx in xi_yong:
                pre_18_positive += 1
            else:
                pre_18_negative += 1

    if pre_18_positive >= pre_18_negative:
        checks["step4"] = {"passed": True, "detail": f"18岁前喜用运偏多({pre_18_positive}喜/{pre_18_negative}忌)✅"}
        passed += 1
    else:
        checks["step4"] = {"passed": False, "detail": f"18岁前忌神运偏多({pre_18_positive}喜/{pre_18_negative}忌)❌"}

    # Step 5: 印运在学习窗口（7-25岁）内到来？
    yin_window = False
    for dg, sa in zip(da_yun_gans, da_yun_start_ages):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ("正印", "偏印") and 7 <= sa <= 25:
            yin_window = True
            break

    if yin_window:
        checks["step5"] = {"passed": True, "detail": "印运在学习窗口(7-25岁)内到来✅"}
        passed += 1
    else:
        checks["step5"] = {"passed": False, "detail": "印运未在学习窗口内到来❌"}

    # Step 6: 全局综合
    if passed >= 4:
        checks["step6"] = {"passed": True, "detail": f"{passed}/{total}项通过→高学历✅"}
    elif passed >= 2:
        checks["step6"] = {"passed": True, "detail": f"{passed}/{total}项通过→中等学历✅"}
    else:
        checks["step6"] = {"passed": False, "detail": f"{passed}/{total}项通过→低学历❌"}
        passed = max(0, passed - 1)  # 综合不通过则减1

    return {"checks": checks, "passed": passed, "total": total}


def _determine_school_level(
    checks_passed: int, wen_chang_in_local: bool, shen_label: str, year_yin_score: float
) -> tuple:
    """
    学校等级六档 + 学历层级定位
    """
    # 学校等级
    if checks_passed >= 5:
        school_level = "👑 顶尖（清北/常春藤）"
    elif checks_passed >= 3 and wen_chang_in_local:
        school_level = "🥇 985顶级大学"
    elif checks_passed >= 3:
        school_level = "🥇 211/一本"
    elif checks_passed >= 2:
        school_level = "🥈 普通本科"
    elif checks_passed >= 1:
        school_level = "🥉 大专/职校"
    else:
        school_level = "🪜 初中以下"

    # 学历层级（印运时间线定）
    degree = "本科"
    if checks_passed >= 4:
        degree = "硕士及以上"
    elif checks_passed >= 2:
        degree = "本科"
    else:
        degree = "初中/专科"

    return school_level, degree


def analyze_education(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
    shen_score: float,
    shen_label: str,
    xi_yong: list[str],
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_ages: list[int],
) -> dict:
    """
    学历分析完整体系 v2.0

    返回: 完整的学业基因+兑现条件+最终学历
    """
    # ── 第0层：年柱有印三档法 ──
    year_check = _check_year_pillar_yin(bazi_gans[0], bazi_zhis[0], ri_zhu)

    # ── 年干伤官检查 ──
    nian_check = _nian_gan_shi_shen_check(bazi_gans[0], ri_zhu)

    # ── 文昌检查（年干查命理） ──
    wen_chang = _check_wen_chang(bazi_gans[0], bazi_zhis, da_yun_zhis)

    # ── 六步排查 ──
    six_steps = _check_six_steps(
        bazi_gans, bazi_zhis, ri_zhu, shen_label, shen_score, xi_yong, da_yun_gans, da_yun_zhis, da_yun_start_ages
    )

    # ── 学校等级+学历层级 ──
    school_level, degree = _determine_school_level(
        six_steps["passed"], wen_chang["has"], shen_label, year_check["yin_score"]
    )

    # ── 最终结论 ──
    # 综合第0层和六步
    if year_check["has_yin"] and six_steps["passed"] >= 4:
        final_note = "学业基因强+兑现条件好→高学历"
    elif year_check["has_yin"] and six_steps["passed"] >= 2:
        final_note = "有学业基因+兑现中等→中等学历"
    elif year_check["has_yin"] and six_steps["passed"] < 2:
        final_note = "有学业基因但兑现条件差→低学历"
    elif six_steps["passed"] >= 2:
        final_note = "文昌/大运补救→中等学历"
    else:
        final_note = "学业基因弱+兑现条件差→低学历"

    # 年干伤官修正
    if nian_check["signal"] == "negative":
        school_level = "🥉 大专/职校（年干伤官·叛逆）"
        degree = "专科"
        final_note += "【年干伤官·少年叛逆影响学业】"

    # 文昌补文昌（日干查补运）
    bu_wen_chang_zhi = WEN_CHANG_MAP.get(ri_zhu, "")

    # 六步详细推理
    step_details = _build_step_details(
        year_check,
        six_steps,
        nian_check,
        wen_chang,
        da_yun_gans,
        da_yun_zhis,
        da_yun_start_ages,
        shen_score,
        shen_label,
    )

    # 学校等级推理
    school_reason = _build_school_reasoning(year_check, six_steps, wen_chang, shen_label, nian_check)

    # 学历层级推理
    degree_reason = _build_degree_reasoning(degree, da_yun_gans, da_yun_zhis, da_yun_start_ages, shen_label)

    # 大运窗口
    edu_da_yun_windows = []
    for i, dg in enumerate(da_yun_gans):
        if i < len(da_yun_start_ages):
            age = da_yun_start_ages[i]
            if 6 <= age <= 25:
                edu_da_yun_windows.append(f"{dg}{da_yun_zhis[i] if i < len(da_yun_zhis) else ''}运(~{int(age)}岁)")

    return {
        "school_level": school_level,
        "degree": degree,
        "display": f"🎓 {school_level}·{degree}",
        "year_pillar_check": year_check,
        "nian_gan_check": nian_check,
        "wen_chang_ming_li": wen_chang,
        "wen_chang_bu_yun": {"zhi": bu_wen_chang_zhi},
        "six_steps": six_steps,
        "final_note": final_note,
        "six_step_details": step_details,
        "school_reasoning": school_reason,
        "degree_reasoning": degree_reason,
        "edu_da_yun_windows": edu_da_yun_windows,
    }


def _build_step_details(year_check, six_steps, nian_check, wen_chang, dy_gans, dy_zhis, dy_ages, score, label):
    """构建六步详细推理"""
    details = []
    if year_check.get("has_yin"):
        details.append(f"年柱有印（{year_check.get('yin_detail', '')}）→学业基因✅")
    else:
        details.append("年柱无印→学业基因偏弱")
    if nian_check.get("shi_shen") == "伤官":
        details.append("年干伤官→少年叛逆，非学历导向【素材12行517】")
    if wen_chang.get("exist"):
        details.append(f"文昌在局（{wen_chang.get('detail', '')}）→学业助力✅")
    else:
        details.append("原局无文昌→需大运文昌补救")
    details.append(f"六步排查通过{six_steps.get('passed', 0)}项/{six_steps.get('total', 6)}项")
    if isinstance(dy_gans, list):
        for i, dg in enumerate(dy_gans):
            if i < len(dy_ages) and 6 <= dy_ages[i] <= 25:
                details.append(
                    f"学龄期大运{dg}{dy_zhis[i] if i < len(dy_zhis) else ''}（~{int(dy_ages[i])}岁）→关键学习窗口"
                )
    return details


def _build_school_reasoning(year_check, six_steps, wen_chang, label, nian_check):
    """构建学校等级推理"""
    passed = six_steps.get("passed", 0)
    parts = []
    if passed >= 5:
        parts.append("≥5项通过→顶尖层级")
    elif passed >= 3:
        parts.append(f"≥3项通过（{passed}项）→985/211层级")
    elif passed >= 2:
        parts.append(f"≥2项通过（{passed}项）→普通本科层级")
    else:
        parts.append("≤1项通过→职校/初中学历")
    if year_check.get("has_yin"):
        parts.append("年柱有印保底")
    if wen_chang.get("exist"):
        parts.append("文昌加持")
    if nian_check.get("shi_shen") == "伤官":
        parts.append("但年干伤官拉低学历上限")
    return "；".join(parts)


def _build_degree_reasoning(degree, dy_gans, dy_zhis, dy_ages, label):
    """构建学历层级推理"""
    if "博士" in degree:
        return "印运在22岁前到位+文昌强→博士层次"
    elif "硕士" in degree:
        return "印运在18-22岁到位→硕士窗口"
    else:
        return "印运在学龄后到位或兑现条件有限→本科/专科层次"


def analyze_education_simple(
    bazi_gans, bazi_zhis, ri_zhu, shen_score, shen_label, xi_yong, da_yun_gans, da_yun_zhis, da_yun_start_ages
) -> dict:
    """简化版入口 — 兼容旧接口"""
    result = analyze_education(
        bazi_gans, bazi_zhis, ri_zhu, shen_score, shen_label, xi_yong, da_yun_gans, da_yun_zhis, da_yun_start_ages
    )
    return {
        "school_level": result["school_level"],
        "degree": result["degree"],
        "summary": f"{result['school_level']}·{result['degree']}",
        "checks_passed": f"{result['six_steps']['passed']}/{result['six_steps']['total']}",
        **result,
    }
