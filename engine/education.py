"""
金鉴真人·学历学业分析引擎 v2.3 — 九龙道长原始理论版
基于bazi-education-analysis v1.6

═══════════════════════════════════════════════
九龙道长判学业原始逻辑（按优先级排列）：
═══════════════════════════════════════════════

第一层：身强弱（基准框架）
  身强(≥60分)：耐力足，能持续学，不依赖印运
  中和(40-60分)：平衡型，有印更好无印也能学
  身弱(<40分)：学得快但容易累，需印运托底
  身极弱(<15分)：学习吃力，需大运印比强力补救

第二层：印运+喜忌（核心·决定学历高度）
  学业窗口期 = 0-18岁（基础教育）+ 18-22岁（高等教育）
  
  身强(≥60分) → 印为忌凶
    印运在学业窗口→学非所用，拉低学历
    无印运在学业窗口→不影响，靠其他运也行
  
  身弱(<40分) → 印为喜用
    印运在学业窗口→能学进去 ✅ 关键
    无印运在学业窗口→学不进去 ❌

第三层：文昌贵人（辅助·决定学习效率）
  文昌在局 → 效率高，加持
  文昌在大运 → 10年补救
  文昌缺失 → 效率打折

第四层：其他十神（修正·非核心）
  正财运 → 倾向搞钱，无心向学
  食伤运 → 吃喝玩乐，聪明但贪玩（素材02行129）
  官杀运 → 自律，有压力（身强正向，身弱负向）
  比劫运 → 同伴影响（身弱正向，身强负向）
"""

from __future__ import annotations

from constants import CANG_GAN_RATIO, DI_ZHI_CANG_GAN, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan
from xing_chong_he_hua import check_liu_he

# ── 文昌贵人表 ──
WEN_CHANG_MAP = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
    "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
    "壬": "寅", "癸": "卯",
}

# ── 十神对学业的原始影响（九龙道长原始理论）──
# 素材02行129：食神与伤官格追求的是吃喝玩乐，享受生活
# 素材12行517：年柱伤官=少年叛逆打架
# 素材08行247：身弱走食神伤官运=学习不好
# 素材18行305：身弱走食神伤官大运=学习不好，贪玩偏科
# 素材03行497：伤官多=学一门技能，靠技能生财
SHI_SHEN_STUDY_EFFECT = {
    # 十神: (身强时的学业影响, 身弱时的学业影响)
    # 取值: "good"=有利, "bad"=不利, "mixed"=利但有副作用, "neutral"=中性
    "正印": ("bad", "good"),   # 身强忌凶学非所用；身弱喜用学得好
    "偏印": ("bad", "good"),   # 同上
    "比肩": ("bad", "good"),   # 身强忌凶拖累；身弱喜用得同学帮
    "劫财": ("bad", "good"),   # 同上
    "正官": ("good", "bad"),   # 身强喜用自律；身弱忌凶压力大
    "七杀": ("mixed", "bad"),  # 身强有竞争力但压力；身弱压力更大
    "正财": ("mixed", "bad"),  # 身强喜用但搞钱无心学习；身弱忌凶杂念
    "偏财": ("mixed", "bad"),  # 同上
    "食神": ("mixed", "bad"),  # 身强喜用但吃喝玩乐贪玩；身弱忌凶更贪玩
    "伤官": ("mixed", "bad"),  # 身强聪明但叛逆；身弱更叛逆
}


def _nian_gan_shi_shen_check(nian_gan: str, ri_zhu: str) -> dict:
    """年干十神检查（素材12行517：年干伤官→叛逆）"""
    ss = get_shi_shen_for_gan(nian_gan, ri_zhu)
    result = {"shi_shen": ss, "signal": "neutral", "note": ""}
    if ss == "伤官":
        result["signal"] = "negative"
        result["note"] = "年干伤官→少年叛逆打架【素材12行517】"
    elif ss in ("正印", "偏印"):
        result["signal"] = "positive"
        result["note"] = "年干印星→有学业基因"
    elif ss in ("正官", "七杀"):
        result["signal"] = "positive"
        result["note"] = "年干官杀→自律型学习"
    return result


def _check_year_pillar_yin(year_gan: str, year_zhi: str, ri_zhu: str) -> dict:
    """年柱有印三档法（第0层）"""
    result = {"has_yin": False, "level": "一般", "yin_score": 0.0, "detail": ""}
    gan_ss = get_shi_shen_for_gan(year_gan, ri_zhu)
    if gan_ss in ("正印", "偏印"):
        result["has_yin"] = True
        result["level"] = "好"
        result["yin_score"] = 8.0
        result["detail"] = f"年干{year_gan}={gan_ss}透出✅"
        return result
    for cg, ratio in DI_ZHI_CANG_GAN.get(year_zhi, []):
        ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
        if ss in ("正印", "偏印"):
            ratio_score = CANG_GAN_RATIO.get(ratio, 0.3)
            score = 4.0 * ratio_score
            level_name = "本气" if ratio == 100 else "中气" if ratio == 60 else "余气"
            quality = "强" if ratio == 100 else "良好" if ratio == 60 else "偏弱"
            result["has_yin"] = True
            result["yin_score"] = score
            result["level"] = "好" if score >= 2 else "好（偏弱）"
            result["detail"] = f"年支{year_zhi}藏{cg}={ss}({level_name}·{quality})✅" + ("" if score >= 2 else "但偏弱")
            return result
    result["detail"] = "年柱无印❌"
    return result


def _check_wen_chang(nian_gan_or_ri_zhu: str, all_zhis: list[str], da_yun_zhis: list[str]) -> dict:
    """文昌检查 — 年干查命理"""
    target_zhi = WEN_CHANG_MAP.get(nian_gan_or_ri_zhu, "")
    result = {"has": False, "zhi": target_zhi, "location": "", "detail": ""}
    if not target_zhi:
        result["detail"] = "无文昌"
        return result
    pillar_names = ["年支", "月支", "日支", "时支"]
    for i, z in enumerate(all_zhis):
        if z == target_zhi:
            location = pillar_names[i]
            strength = "最强" if i == 1 else "强" if i == 2 else "有用"
            result["has"] = True
            result["location"] = f"{location}({strength})"
            result["detail"] = f"文昌在{location}→{strength}"
            return result
    for dz in da_yun_zhis:
        if dz == target_zhi:
            result["has"] = True
            result["location"] = "大运"
            result["detail"] = "大运有文昌→10年补救"
            return result
    result["detail"] = f"文昌在{target_zhi}但不在局→未到位"
    return result


def _check_yin_gen_he_hua(bazi_zhis: list[str], ri_zhu: str) -> dict:
    """印根合化消耗检查（六步第2步）"""
    yin_roots = []
    for i, z in enumerate(bazi_zhis):
        for cg, ratio in DI_ZHI_CANG_GAN.get(z, []):
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss in ("正印", "偏印") and ratio == 100:
                yin_roots.append((i, z, cg))
    if not yin_roots:
        return {"passed": False, "detail": "原局无印根❌"}
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
    bazi_gans: list[str], bazi_zhis: list[str], ri_zhu: str,
    shen_label: str, shen_score: float, xi_yong: list[str],
    da_yun_gans: list[str], da_yun_zhis: list[str], da_yun_start_ages: list[float],
) -> dict:
    """六步精细排查"""
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

    # Step 2: 印根完整无伤？
    yin_root_check = _check_yin_gen_he_hua(bazi_zhis, ri_zhu)
    checks["step2"] = {"passed": yin_root_check["passed"], "detail": yin_root_check["detail"]}
    if yin_root_check["passed"]:
        passed += 1

    # Step 3: 文昌存在？
    wc = _check_wen_chang(bazi_gans[0], bazi_zhis, da_yun_zhis)
    if wc["has"]:
        checks["step3"] = {"passed": True, "detail": wc["detail"]}
        passed += 1
    else:
        checks["step3"] = {"passed": False, "detail": wc["detail"]}

    # Step 4: 18岁前走喜用还是忌神？（五行维度）
    pre_18_positive = 0
    pre_18_negative = 0
    for dg, dz, sa in zip(da_yun_gans, da_yun_zhis, da_yun_start_ages, strict=False):
        if sa < 18:
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

    # Step 5: 印运在学业期（0-25岁）内到来？
    yin_window_ages = []
    for dg, sa in zip(da_yun_gans, da_yun_start_ages, strict=False):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ("正印", "偏印") and sa <= 25:
            yin_window_ages.append(int(sa))
    if yin_window_ages:
        checks["step5"] = {"passed": True, "detail": f"印运{min(yin_window_ages)}岁到✅", "yin_ages": yin_window_ages}
        passed += 1
    else:
        checks["step5"] = {"passed": False, "detail": "学业期无印运❌", "yin_ages": []}

    # Step 6: 全局综合
    if passed >= 4:
        checks["step6"] = {"passed": True, "detail": f"{passed}/{total}项通过→高学历✅"}
    elif passed >= 2:
        checks["step6"] = {"passed": True, "detail": f"{passed}/{total}项通过→中等学历✅"}
    else:
        checks["step6"] = {"passed": False, "detail": f"{passed}/{total}项通过→低学历❌"}
        passed = max(0, passed - 1)

    return {"checks": checks, "passed": passed, "total": total}


def _analyze_da_yun_for_study(
    da_yun_gans: list[str], da_yun_start_ages: list[float],
    ri_zhu: str, shen_score: float,
) -> dict:
    """
    学业期大运分析（基于九龙道长原始十神影响）

    学业窗口：0-18岁（基础教育）+ 18-22岁（高等教育）

    每个十神对学业的影响（原始理论）：
      印枭 → 学习本身（身强忌凶=学非所用；身弱喜用=学得好）
      正财 → 搞钱，无心向学
      食伤 → 吃喝玩乐贪玩（素材02行129）
      伤官 → 聪明但叛逆（素材12行517）
      官杀 → 自律但压力
      比劫 → 同伴影响
    """
    windows = {
        "basic_0_18": {"name": "0-18岁基础教育", "effect": 0, "details": []},
        "college_18_22": {"name": "18-22岁高等教育", "effect": 0, "details": []},
    }

    for dg, sa in zip(da_yun_gans, da_yun_start_ages, strict=False):
        ss = get_shi_shen_for_gan(dg, ri_zhu)

        # 查十神学业影响表
        effect_map = SHI_SHEN_STUDY_EFFECT.get(ss, ("neutral", "neutral"))
        if shen_score >= 60:
            effect = effect_map[0]  # 身强的效果
        elif shen_score >= 40:
            effect = "neutral"  # 中和=中性
        else:
            effect = effect_map[1]  # 身弱的效果

        # 量化
        if effect == "good":
            score = 1
            tag = "✅有利"
        elif effect == "bad":
            score = -1
            tag = "❌不利"
        elif effect == "mixed":
            score = 0
            tag = "⚠️混合"
        else:
            score = 0
            tag = "➖中性"

        item = {"age": int(sa), "gan": dg, "shi_shen": ss, "effect": effect, "tag": tag}

        if sa < 18:
            windows["basic_0_18"]["effect"] += score
            windows["basic_0_18"]["details"].append(item)
        elif 18 <= sa < 22:
            windows["college_18_22"]["effect"] += score
            windows["college_18_22"]["details"].append(item)

    return {
        "windows": windows,
        "total_effect": sum(w["effect"] for w in windows.values()),
        "shen_level": "身强" if shen_score >= 60 else "中和" if shen_score >= 40 else "身弱" if shen_score >= 15 else "身极弱",
    }


def _determine_degree(
    shen_score: float, shen_label: str, checks_passed: int,
    da_yun_gans: list[str], da_yun_start_ages: list[float],
    year_check: dict, nian_check: dict, wen_chang: dict,
    ri_zhu: str,
) -> tuple[str, str, str]:
    """
    学历层级判定（九龙道长原始逻辑）
    
    第一层：身强弱（基准）
    第二层：印运+喜忌（核心） 
    第三层：文昌（辅助）
    第四层：其他十神修正
    """
    # ── 第二层：印运分析 ──
    yin_ages = []
    for dg, sa in zip(da_yun_gans, da_yun_start_ages, strict=False):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ("正印", "偏印") and sa <= 30:
            yin_ages.append(int(sa))

    # 印运在学业窗口(0-22岁)内到来
    yin_in_basic = any(a < 18 for a in yin_ages)
    yin_in_college = any(18 <= a <= 22 for a in yin_ages)
    yin_in_master = any(22 <= a <= 25 for a in yin_ages)
    yin_in_phd = any(25 <= a <= 30 for a in yin_ages)
    has_yin = bool(yin_ages)

    # ── 第四层：十神修正 ──
    dy_analysis = _analyze_da_yun_for_study(da_yun_gans, da_yun_start_ages, ri_zhu, shen_score)
    basic_eff = dy_analysis["windows"]["basic_0_18"]["effect"]
    college_eff = dy_analysis["windows"]["college_18_22"]["effect"]

    nian_negative = (nian_check.get("signal") == "negative")

    # ── 推理理由 ──
    def _build_reason():
        parts = [dy_analysis["shen_level"]]
        if shen_score >= 60 or shen_score < 40:
            parts.append(f"({round(shen_score,1)}分)")
        if yin_ages:
            parts.append(f"印{min(yin_ages)}岁到")
        if wen_chang["has"]:
            parts.append("文昌")
        if checks_passed >= 3:
            parts.append(f"六步{checks_passed}/6")
        if basic_eff > 0:
            parts.append("0-18岁利学")
        elif basic_eff < 0:
            parts.append("0-18岁不利")
        if college_eff > 0:
            parts.append("18-22岁利学")
        elif college_eff < 0:
            parts.append("18-22岁不利")
        if nian_negative:
            parts.append("年干伤官")
        return "；".join(parts)

    # ==========================================
    # 判定逻辑
    # ==========================================

    # ── 身强（≥60分）：印为忌凶，印运=学非所用 ──
    if shen_score >= 60:
        if checks_passed >= 4 and wen_chang["has"]:
            level, degree = "👑 顶尖（清北/常春藤）", "硕士及以上"
        elif checks_passed >= 3:
            if yin_in_basic:
                # 身强遇印运=学非所用，拉低上限
                level = "🥇 985顶级大学" if not nian_negative else "🥇 211/一本"
            else:
                level = "🥇 985顶级大学"
            degree = "本科"
        elif checks_passed >= 2:
            level, degree = "🥈 普通本科", "本科"
        else:
            level, degree = "🥉 大专/职校", "专科"

    # ── 中和（40-60分）：有印更好无印也能学 ──
    elif shen_score >= 40:
        if yin_in_basic and checks_passed >= 4 and wen_chang["has"]:
            level, degree = "🥇 985顶级大学", "硕士及以上"
        elif yin_in_basic and checks_passed >= 3:
            level, degree = "🥇 985顶级大学", "本科"
        elif yin_in_college and checks_passed >= 3:
            level, degree = "🥇 211/一本", "本科"
        elif checks_passed >= 3:
            level, degree = "🥇 211/一本", "本科"
        elif checks_passed >= 2:
            level, degree = "🥈 普通本科", "本科"
        else:
            level, degree = "🥉 大专/职校", "专科"

    # ── 身弱（<40分）：必须印运托底 ──
    elif shen_score >= 15:
        if yin_in_basic and checks_passed >= 3 and wen_chang["has"]:
            level, degree = "🥇 211/一本", "本科"
        elif yin_in_basic and checks_passed >= 2:
            level, degree = "🥈 普通本科", "本科"
        elif yin_in_college and checks_passed >= 2:
            level, degree = "🥈 普通本科", "专科"
        elif has_yin:
            level, degree = "🥉 大专/职校", "专科"
        else:
            # 身弱+无印运 → 学不进去
            level, degree = "🪜 初中/高中", "初中/专科"

    # ── 身极弱（<15分）：除非大运印比强力补救 ──
    else:
        if yin_in_basic and checks_passed >= 3 and wen_chang["has"]:
            level, degree = "🥈 普通本科", "本科"
        else:
            level, degree = "🪜 初中/高中", "初中/专科"

    # ── 年干伤官拉低 ──
    if nian_negative:
        if "顶尖" in level or "985" in level:
            level = "🥇 211/一本（年干伤官拉低）" if "985" not in level else level.replace("985", "211")
        if degree in ("硕士及以上", "硕士"):
            degree = "本科"

    return level, degree, _build_reason()


def analyze_education(
    bazi_gans: list[str], bazi_zhis: list[str], ri_zhu: str,
    shen_score: float, shen_label: str, xi_yong: list[str],
    da_yun_gans: list[str], da_yun_zhis: list[str], da_yun_start_ages: list[float],
) -> dict:
    """学历分析完整体系 v2.3 — 九龙道长原始理论"""
    year_check = _check_year_pillar_yin(bazi_gans[0], bazi_zhis[0], ri_zhu)
    nian_check = _nian_gan_shi_shen_check(bazi_gans[0], ri_zhu)
    wen_chang = _check_wen_chang(bazi_gans[0], bazi_zhis, da_yun_zhis)

    six_steps = _check_six_steps(
        bazi_gans, bazi_zhis, ri_zhu, shen_label, shen_score, xi_yong,
        da_yun_gans, da_yun_zhis, da_yun_start_ages
    )

    dy_analysis = _analyze_da_yun_for_study(da_yun_gans, da_yun_start_ages, ri_zhu, shen_score)

    school_level, degree, reason = _determine_degree(
        shen_score, shen_label, six_steps["passed"],
        da_yun_gans, da_yun_start_ages,
        year_check, nian_check, wen_chang, ri_zhu,
    )

    bu_wen_chang_zhi = WEN_CHANG_MAP.get(ri_zhu, "")

    # 构建细节
    step_details = []
    step_details.append(f"【第0层】年柱有印: {year_check['detail']}")
    step_details.append(f"【年干】{nian_check['shi_shen']}: {nian_check['note']}")
    step_details.append(f"【身强弱】{dy_analysis['shen_level']}({round(shen_score,1)}分)")
    
    # 印运信息
    edu_yin_ages = six_steps.get("checks", {}).get("step5", {}).get("yin_ages", [])
    if edu_yin_ages:
        step_details.append(f"【印运】{min(edu_yin_ages)}岁到")
    else:
        step_details.append("【印运】学业窗口期无印运")
    
    step_details.append(f"【文昌】{wen_chang['detail']}")
    step_details.append(f"【六步】{six_steps['passed']}/{six_steps['total']}项通过")
    for wk, wv in dy_analysis["windows"].items():
        if wv["details"]:
            effects = ", ".join(f"{d['age']}岁{d['gan']}={d['shi_shen']}({d['tag']})" for d in wv["details"])
            step_details.append(f"【{wv['name']}】{effects} → 净{wv['effect']}")

    return {
        "school_level": school_level,
        "degree": degree,
        "display": f"🎓 {school_level}·{degree}",
        "year_pillar_check": year_check,
        "nian_gan_check": nian_check,
        "wen_chang_ming_li": wen_chang,
        "wen_chang_bu_yun": {"zhi": bu_wen_chang_zhi},
        "six_steps": six_steps,
        "final_note": reason,
        "six_step_details": step_details,
        "edu_da_yun_windows": [
            f"{dg}{da_yun_zhis[i] if i < len(da_yun_zhis) else ''}运(~{int(age)})"
            for i, (dg, age) in enumerate(zip(da_yun_gans, da_yun_start_ages))
            if 6 <= age <= 25
        ],
    }


def analyze_education_simple(
    bazi_gans, bazi_zhis, ri_zhu, shen_score, shen_label, xi_yong,
    da_yun_gans, da_yun_zhis, da_yun_start_ages
) -> dict:
    """简化版入口"""
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
