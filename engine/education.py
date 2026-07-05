"""
金鉴真人·学历学业分析引擎 v2.1 — 确定性规则版（九龙道长原始理论修正）
基于bazi-education-analysis v1.6

规则体系：
  第0层：年柱有印三档法（3秒定性）
  六步排查（决定兑现程度）
  学校等级六档定位
  学历层级定位（身强弱×印运窗口联合判定）
  文昌贵人双轨制（年干查命/日干补运）
  年干伤官检查
"""

from __future__ import annotations

from constants import CANG_GAN_RATIO, DI_ZHI_CANG_GAN, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan
from xing_chong_he_hua import check_liu_he

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


def _check_yin_gen_he_hua(bazi_zhis: list[str], ri_zhu: str) -> dict:
    """
    印根合化消耗检查（六步第2步·九龙道长原始理论）
    
    印根被合化（如卯戌合火→戌中戊土变火）→ 印根虚 ❌
    印根被冲 → 印根动摇 ❌
    印根被刑/害 → 印根受损 ❌
    """
    # 找到所有藏干为印的地支
    yin_roots = []
    for i, z in enumerate(bazi_zhis):
        for cg, ratio in DI_ZHI_CANG_GAN.get(z, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss in ("正印", "偏印") and ratio == 100:
                yin_roots.append((i, z, cg))

    if not yin_roots:
        return {"passed": False, "detail": "原局无印根❌"}

    # 检查印根是否被合化消耗
    he_hua_issues = []
    for idx, zhi, cg in yin_roots:
        for other_zhi in bazi_zhis:
            if other_zhi != zhi:
                result = check_liu_he(zhi, other_zhi)
                if result:
                    he_hua_issues.append(f"{zhi}与{other_zhi}合化{result}→消耗{cg}印根")

    if he_hua_issues:
        return {"passed": False, "detail": "；".join(he_hua_issues), "issues": he_hua_issues}
    
    return {"passed": True, "detail": "印根完整无伤✅", "issues": []}


def _check_six_steps(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
    shen_label: str,
    shen_score: float,
    xi_yong: list[str],
    da_yun_gans: list[str],
    da_yun_zhis: list[str],
    da_yun_start_ages: list[float],
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

    # Step 2: 印根完整无伤？（九龙道长原始理论·检查合化消耗）
    yin_root_check = _check_yin_gen_he_hua(bazi_zhis, ri_zhu)
    checks["step2"] = {"passed": yin_root_check["passed"], "detail": yin_root_check["detail"]}
    if yin_root_check["passed"]:
        passed += 1

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
    for dg, dz, sa in zip(da_yun_gans, da_yun_zhis, da_yun_start_ages, strict=False):
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
    yin_window_ages = []
    for dg, sa in zip(da_yun_gans, da_yun_start_ages, strict=False):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ("正印", "偏印") and 7 <= sa <= 25:
            yin_window = True
            yin_window_ages.append(int(sa))

    if yin_window:
        checks["step5"] = {"passed": True, "detail": f"印运在学习窗口内到来({yin_window_ages}岁)✅", "yin_window_ages": yin_window_ages}
        passed += 1
    else:
        checks["step5"] = {"passed": False, "detail": "印运未在学习窗口内到来❌", "yin_window_ages": []}

    # Step 6: 全局综合
    if passed >= 4:
        checks["step6"] = {"passed": True, "detail": f"{passed}/{total}项通过→高学历✅"}
    elif passed >= 2:
        checks["step6"] = {"passed": True, "detail": f"{passed}/{total}项通过→中等学历✅"}
    else:
        checks["step6"] = {"passed": False, "detail": f"{passed}/{total}项通过→低学历❌"}
        passed = max(0, passed - 1)  # 综合不通过则减1

    return {"checks": checks, "passed": passed, "total": total}


def _determine_degree(
    shen_score: float, shen_label: str, checks_passed: int,
    da_yun_gans: list[str], da_yun_start_ages: list[float],
    year_check: dict, nian_check: dict, wen_chang: dict,
    ri_zhu: str,
) -> tuple[str, str]:
    """
    学历层级判定 — 身强弱×印运窗口 联合判定
    
    原始理论依据（bazi-education-analysis v1.6）：
    
    身强(≥60分)：
      官杀/食伤/财均为喜用 → 什么运都能学，不依赖印运
      印为忌凶 → 印运反而不利（学非所用）
      后劲足，能持续学习
      
    中和(40-60分)：
      最理想，能学也能玩
      印运可锦上添花，没有也能学
      
    身弱(<40分)：
      只有印/比为喜用 → 必须印运托底才能学得好
      官杀忌凶→压力大发挥失常
      食伤忌凶→贪玩偏科
      财星忌凶→杂念早恋
      
    身极弱(<15分)：
      学习非常吃力
      除非大运印比强力补救
      
    印运时间线（与身强弱联合判定）：
      - 身强者什么运都能学→印运反而不利，但官杀食伤财运皆可出成绩
      - 身弱者必须印运在学龄期到来→才能学得进去
    """
    # 获取印运窗口年龄
    yin_window_ages = []
    for dg, sa in zip(da_yun_gans, da_yun_start_ages, strict=False):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ("正印", "偏印") and sa <= 30:
            yin_window_ages.append(int(sa))
    
    yin_before_18 = any(age < 18 for age in yin_window_ages)
    yin_18_22 = any(18 <= age <= 22 for age in yin_window_ages)
    yin_after_22 = any(age > 22 for age in yin_window_ages)
    has_yin_window = bool(yin_window_ages)
    
    # 年干伤官负向修正
    nian_negative = (nian_check.get("signal") == "negative")
    
    # ── 身强（≥60分）：框架大，什么运都能学好 ──
    if shen_score >= 60:
        if checks_passed >= 4:
            school_level = "👑 顶尖（清北/常春藤）"
            degree = "硕士及以上"
            reason = "身强框架大+六步≥4项→高学历"
        elif checks_passed >= 3 and wen_chang["has"]:
            school_level = "🥇 985顶级大学"
            degree = "硕士" if yin_before_18 else "本科"
            reason = f"身强+六步≥3项+文昌→985层级" + \
                     (f"印运18岁前到→硕士" if yin_before_18 else "")
        elif checks_passed >= 3:
            school_level = "🥇 211/一本"
            degree = "本科"
            reason = "身强+六步≥3项→211层级"
        elif checks_passed >= 2:
            school_level = "🥈 普通本科"
            degree = "本科"
            reason = "身强+六步≥2项→本科"
        else:
            school_level = "🥉 大专/职校"
            degree = "专科"
            reason = "身强但六步≤1项→学历偏低"
    
    # ── 中和（40-60分）：平衡型 ──
    elif shen_score >= 40:
        if checks_passed >= 4 and yin_before_18:
            school_level = "🥇 985顶级大学"
            degree = "硕士及以上"
            reason = "中和+印运早到+六步≥4项→高学历"
        elif checks_passed >= 3 and wen_chang["has"]:
            school_level = "🥇 985顶级大学" if yin_before_18 else "🥇 211/一本"
            degree = "硕士" if yin_before_18 else "本科"
            reason = f"中和+文昌+" + ("印运早到→硕士" if yin_before_18 else "印运未早到→本科")
        elif checks_passed >= 2:
            school_level = "🥈 普通本科" if checks_passed >= 2 else "🥉 大专/职校"
            degree = "本科"
            reason = "中和+六步≥2项→本科"
        else:
            school_level = "🥉 大专/职校"
            degree = "专科"
            reason = "中和但六步≤1项→学历偏低"
    
    # ── 身弱（<40分）：必须印运托底 ──
    elif shen_score >= 15:
        if checks_passed >= 3 and has_yin_window and wen_chang["has"]:
            school_level = "🥇 211/一本"
            degree = "本科" if yin_before_18 else "专科"
            reason = f"身弱+印运{yin_window_ages}岁到+文昌→" + ("本科" if yin_before_18 else "专科（印运晚到）")
        elif checks_passed >= 2 and (has_yin_window or wen_chang["has"]):
            school_level = "🥈 普通本科"
            degree = "本科" if yin_before_18 else "专科"
            reason = "身弱+文昌/印运补救→" + ("本科" if yin_before_18 else "专科")
        else:
            school_level = "🥉 大专/职校"
            degree = "专科"
            reason = "身弱+六步≤1项→低学历"
    
    # ── 身极弱（<15分）：除非大运强力补救 ──
    else:
        if checks_passed >= 3 and has_yin_window and wen_chang["has"]:
            school_level = "🥈 普通本科"
            degree = "本科"
            reason = "身极弱但大运印比强力补救→本科"
        else:
            school_level = "🪜 初中/高中"
            degree = "初中/专科"
            reason = "身极弱无补救→低学历"
    
    # 年干伤官拉低学历上限
    if nian_negative:
        if "985" in school_level or "211" in school_level:
            school_level = school_level.replace("🥇 ", "🥈 ")
            school_level += "（年干伤官拉低）"
        degree = "专科" if degree in ("硕士及以上", "硕士") else degree
        reason += "【年干伤官·叛逆拉低上限】"
    
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
    da_yun_start_ages: list[float],
) -> dict:
    """
    学历分析完整体系 v2.1
    
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
        bazi_gans, bazi_zhis, ri_zhu, shen_label, shen_score, xi_yong,
        da_yun_gans, da_yun_zhis, da_yun_start_ages
    )

    # ── 学校等级+学历层级（身强弱×印运窗口联合判定） ──
    school_level, degree = _determine_degree(
        shen_score, shen_label, six_steps["passed"],
        da_yun_gans, da_yun_start_ages,
        year_check, nian_check, wen_chang,
        ri_zhu,
    )

    # ── 最终结论 ──
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

    if nian_check["signal"] == "negative":
        final_note += "【年干伤官·少年叛逆影响学业】"

    # 文昌补文昌（日干查补运）
    bu_wen_chang_zhi = WEN_CHANG_MAP.get(ri_zhu, "")

    # 六步详细推理
    step_details = _build_step_details(
        year_check, six_steps, nian_check, wen_chang,
        da_yun_gans, da_yun_zhis, da_yun_start_ages,
        shen_score, shen_label
    )

    # 学校等级推理
    school_reason = _build_school_reasoning(year_check, six_steps, wen_chang, shen_label, nian_check)

    # 学历层级推理
    degree_reason = _build_degree_reasoning(degree, da_yun_gans, da_yun_zhis, da_yun_start_ages, shen_score, shen_label, ri_zhu)

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


def _build_step_details(year_check, six_steps, nian_check, wen_chang,
                         dy_gans, dy_zhis, dy_ages, score, label):
    """构建六步详细推理"""
    details = []
    if year_check.get("has_yin"):
        details.append(f"年柱有印（{year_check.get('yin_detail', '')}）→学业基因✅")
    else:
        details.append("年柱无印→学业基因偏弱")
    if nian_check.get("shi_shen") == "伤官":
        details.append("年干伤官→少年叛逆，非学历导向【素材12行517】")
    
    # 身强弱影响（原始理论：决定十神喜忌→学习表现）
    if score >= 60:
        details.append(f"身强({round(score,1)}分)→框架大，官杀食伤皆喜用，不依赖印运")
    elif score >= 40:
        details.append(f"中和({round(score,1)}分)→平衡型，有印更好无印也能学")
    elif score >= 15:
        details.append(f"身弱({round(score,1)}分)→需印运托底才能学得进去")
    else:
        details.append(f"身极弱({round(score,1)}分)→学习非常吃力，除非大运强力补救")
    
    if wen_chang.get("has"):
        details.append(f"文昌在局（{wen_chang.get('detail', '')}）→学业助力✅")
    else:
        details.append("原局无文昌→需大运文昌补救")
    details.append(f"六步排查通过{six_steps.get('passed', 0)}项/{six_steps.get('total', 6)}项")
    
    # 各步骤详情
    for step_key in ["step1", "step2", "step3", "step4", "step5"]:
        step = six_steps.get("checks", {}).get(step_key, {})
        if step:
            details.append(f"  {step_key}: {step.get('detail', '')}")
    
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
    if wen_chang.get("has"):
        parts.append("文昌加持")
    if nian_check.get("shi_shen") == "伤官":
        parts.append("但年干伤官拉低学历上限")
    return "；".join(parts)


def _build_degree_reasoning(degree, dy_gans, dy_zhis, dy_ages, shen_score, shen_label, ri_zhu):
    """构建学历层级推理（身强弱×印运窗口）"""
    # 找印运
    yin_ages = []
    for dg, sa in zip(dy_gans, dy_ages, strict=False):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ("正印", "偏印") and sa <= 30:
            yin_ages.append(int(sa))
    
    parts = []
    if shen_score >= 60:
        parts.append(f"身强({round(shen_score,1)}分)→框架大不依赖印运")
    elif shen_score >= 40:
        parts.append(f"中和({round(shen_score,1)}分)→平衡型")
    elif shen_score >= 15:
        parts.append(f"身弱({round(shen_score,1)}分)→需印运托底")
    else:
        parts.append(f"身极弱({round(shen_score,1)}分)→需大运强力补救")
    
    if yin_ages:
        parts.append(f"印运{min(yin_ages)}岁到")
        if min(yin_ages) < 18:
            parts.append("→硕士窗口")
        else:
            parts.append("→学龄后到，本科上限")
    
    if "硕士" in degree:
        parts.append("→硕士及以上层级")
    elif "本科" in degree:
        parts.append("→本科学历")
    else:
        parts.append("→专科/初中层级")
    
    return "；".join(parts)


def analyze_education_simple(
    bazi_gans, bazi_zhis, ri_zhu, shen_score, shen_label, xi_yong,
    da_yun_gans, da_yun_zhis, da_yun_start_ages
) -> dict:
    """简化版入口 — 兼容旧接口"""
    result = analyze_education(
        bazi_gans, bazi_zhis, ri_zhu, shen_score, shen_label, xi_yong,
        da_yun_gans, da_yun_zhis, da_yun_start_ages
    )
    return {
        "school_level": result["school_level"],
        "degree": result["degree"],
        "summary": f"{result['school_level']}·{result['degree']}",
        "checks_passed": f"{result['six_steps']['passed']}/{result['six_steps']['total']}",
        **result,
    }
