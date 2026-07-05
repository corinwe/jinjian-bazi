"""
金鉴真人·学历学业分析引擎 v2.2 — 确定性规则版（正反面逻辑完整）
基于bazi-education-analysis v1.6

规则体系：
  第0层：年柱有印三档法（3秒定性）
  六步排查（决定兑现程度）
  学校等级六档定位
  学历层级判定：身强弱×(十神正反面+印运窗口)联合判定
  文昌贵人双轨制（年干查命/日干补运）
  年干伤官检查

学业期时间窗口（九龙道长原始划分）：
  0-18岁：小学→高中，基础学业期，决定能否考大学
  18-22岁：本科窗口
  22-25岁：硕士窗口
  25-30岁：博士窗口

身强（≥60分）：官杀/食伤/财=喜用；印/比=忌凶
  ✅ 官杀/食伤/财运 → 学得好
  ❌ 印运 → 学非所用，尤其8岁前遇印=基础不好
  ❌ 比劫运 → 拖累

身弱（<40分）：印/比=喜用；官杀/食伤/财=忌凶
  ✅ 印/比运 → 学得进去
  ❌ 官杀运 → 压力大发挥失常
  ❌ 食伤运 → 贪玩偏科
  ❌ 财运 → 杂念早恋弃学
"""

from __future__ import annotations

from constants import CANG_GAN_RATIO, DI_ZHI_CANG_GAN, TIAN_GAN_WU_XING
from shi_shen import get_shi_shen_for_cang_gan, get_shi_shen_for_gan
from xing_chong_he_hua import check_liu_he

# ── 文昌贵人表（年干查命理，日干查补运）──
WEN_CHANG_MAP = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
    "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
    "壬": "寅", "癸": "卯",
}

# ── 身强弱决定的学业十神正反面 ──
# 身强：官杀/食伤/财=喜用(正面)；印/比=忌凶(反面)
# 身弱：印/比=喜用(正面)；官杀/食伤/财=忌凶(反面)
SHI_SHEN_POSITIVE_QIANG = {"正官", "七杀", "食神", "伤官", "正财", "偏财"}
SHI_SHEN_NEGATIVE_QIANG = {"正印", "偏印", "比肩", "劫财"}
SHI_SHEN_POSITIVE_RUO = {"正印", "偏印", "比肩", "劫财"}
SHI_SHEN_NEGATIVE_RUO = {"正官", "七杀", "食神", "伤官", "正财", "偏财"}


def _nian_gan_shi_shen_check(nian_gan: str, ri_zhu: str) -> dict:
    """年干十神检查（素材12行517：年干伤官→叛逆）"""
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


def _analyze_da_yun_shi_shen_effect(
    da_yun_gans: list[str], da_yun_start_ages: list[float],
    ri_zhu: str, shen_score: float
) -> dict:
    """
    学业期大运十神正反面分析

    身强（≥60分）：官杀/食伤/财=正面；印/比=反面
    身弱（<40分）：印/比=正面；官杀/食伤/财=反面
    中和（40-60分）：正反面各半

    按学业期时间窗口分析：
      0-18岁：基础学业期
      18-22岁：本科窗口
      22-25岁：硕士窗口
      25-30岁：博士窗口
    """
    # 定义时间窗口
    windows = {
        "basic_0_18": {"name": "0-18岁基础期", "positive": 0, "negative": 0, "details": []},
        "college_18_22": {"name": "18-22岁本科窗口", "positive": 0, "negative": 0, "details": []},
        "master_22_25": {"name": "22-25岁硕士窗口", "positive": 0, "negative": 0, "details": []},
        "phd_25_30": {"name": "25-30岁博士窗口", "positive": 0, "negative": 0, "details": []},
    }

    # 按身强弱确定正反面十神集合
    if shen_score >= 60:
        positive_ss = SHI_SHEN_POSITIVE_QIANG  # 官杀/食伤/财
        negative_ss = SHI_SHEN_NEGATIVE_QIANG  # 印/比
    elif shen_score >= 40:
        # 中和：所有十神都算中性，无正反面
        positive_ss = set()
        negative_ss = set()
    else:
        positive_ss = SHI_SHEN_POSITIVE_RUO  # 印/比
        negative_ss = SHI_SHEN_NEGATIVE_RUO  # 官杀/食伤/财

    for dg, sa in zip(da_yun_gans, da_yun_start_ages, strict=False):
        ss = get_shi_shen_for_gan(dg, ri_zhu)
        tag = ""
        if shen_score >= 60:
            if ss in positive_ss:
                tag = "✅正面"
            elif ss in negative_ss:
                tag = "❌反面"
            else:
                tag = "➖中性"
        elif shen_score >= 40:
            tag = "➖中性"
        else:
            if ss in positive_ss:
                tag = "✅正面"
            elif ss in negative_ss:
                tag = "❌反面"
            else:
                tag = "➖中性"

        item = {"age": int(sa), "gan": dg, "shi_shen": ss, "tag": tag}

        # 分配到各时间窗口
        if sa < 18:
            windows["basic_0_18"]["details"].append(item)
            if "正面" in tag:
                windows["basic_0_18"]["positive"] += 1
            elif "反面" in tag:
                windows["basic_0_18"]["negative"] += 1
        elif 18 <= sa < 22:
            windows["college_18_22"]["details"].append(item)
            if "正面" in tag:
                windows["college_18_22"]["positive"] += 1
            elif "反面" in tag:
                windows["college_18_22"]["negative"] += 1
        elif 22 <= sa < 25:
            windows["master_22_25"]["details"].append(item)
            if "正面" in tag:
                windows["master_22_25"]["positive"] += 1
            elif "反面" in tag:
                windows["master_22_25"]["negative"] += 1
        elif 25 <= sa < 30:
            windows["phd_25_30"]["details"].append(item)
            if "正面" in tag:
                windows["phd_25_30"]["positive"] += 1
            elif "反面" in tag:
                windows["phd_25_30"]["negative"] += 1

    # 综合评分：正面运 - 反面运
    total_score = 0
    for wk, wv in windows.items():
        net = wv["positive"] - wv["negative"]
        wv["net"] = net
        total_score += net

    return {
        "windows": windows,
        "total_net": total_score,
        "shen_level": "身强" if shen_score >= 60 else "中和" if shen_score >= 40 else "身弱" if shen_score >= 15 else "身极弱",
    }


def _check_six_steps(
    bazi_gans: list[str], bazi_zhis: list[str], ri_zhu: str,
    shen_label: str, shen_score: float, xi_yong: list[str],
    da_yun_gans: list[str], da_yun_zhis: list[str], da_yun_start_ages: list[float],
) -> dict:
    """六步精细排查 — 决定学业兑现程度"""
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

    # Step 4: 18岁前走喜用还是忌神？
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
        checks["step5"] = {"passed": True, "detail": f"印运来到{min(yin_window_ages)}岁✅", "yin_ages": yin_window_ages}
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


def _determine_degree(
    shen_score: float, shen_label: str, checks_passed: int,
    da_yun_gans: list[str], da_yun_start_ages: list[float],
    year_check: dict, nian_check: dict, wen_chang: dict,
    ri_zhu: str,
) -> tuple[str, str, str]:
    """
    学历层级判定 — 身强弱×(十神正反面+印运窗口)联合判定

    输入：
      - 身强/身弱（确定十神正反面）
      - 学业期大运十神正反面分析（正面运多→学得好；反面运多→学不好）
      - 印运窗口（印运在哪一年龄段到来）
      - 六步得分（综合兑现条件）

    输出：
      (学校等级, 学历层级, 推理理由)
    """
    # ── 学业期大运十神正反面分析 ──
    dy_effect = _analyze_da_yun_shi_shen_effect(da_yun_gans, da_yun_start_ages, ri_zhu, shen_score)
    win = dy_effect["windows"]

    # 各阶段净得分
    basic_net = win["basic_0_18"]["net"]       # 0-18岁
    college_net = win["college_18_22"]["net"]  # 18-22岁
    master_net = win["master_22_25"]["net"]    # 22-25岁
    phd_net = win["phd_25_30"]["net"]          # 25-30岁

    # 印运窗口年龄
    yin_ages = []
    for dg, sa in zip(da_yun_gans, da_yun_start_ages, strict=False):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ("正印", "偏印") and sa <= 30:
            yin_ages.append(int(sa))

    yin_before_18 = any(a < 18 for a in yin_ages)
    yin_18_22 = any(18 <= a <= 22 for a in yin_ages)
    yin_22_25 = any(22 <= a <= 25 for a in yin_ages)
    yin_25_30 = any(25 <= a <= 30 for a in yin_ages)
    has_yin = bool(yin_ages)

    nian_negative = (nian_check.get("signal") == "negative")

    # ── 推理理由构建 ──
    def _reason():
        parts = []
        parts.append(dy_effect["shen_level"])
        if shen_score >= 60:
            parts.append(f"({round(shen_score,1)}分)")
        # 0-18岁正反面
        if basic_net > 0:
            parts.append(f"0-18岁正面运偏多(+{basic_net})")
        elif basic_net < 0:
            parts.append(f"0-18岁反面运偏多({basic_net})")
        else:
            parts.append("0-18岁中性")
        if college_net > 0:
            parts.append(f"18-22岁正面")
        elif college_net < 0:
            parts.append(f"18-22岁反面")
        if yin_ages:
            parts.append(f"印运{min(yin_ages)}岁到")
        if checks_passed >= 3:
            parts.append(f"六步{checks_passed}/{6}")
        if wen_chang["has"]:
            parts.append("文昌")
        if nian_negative:
            parts.append("年干伤官")
        return "；".join(parts)

    # ── 等级判定 ──

    # ===== 身强（≥60分）：官杀/食伤/财=正面；印/比=反面 =====
    if shen_score >= 60:
        if basic_net >= 0 and checks_passed >= 4 and wen_chang["has"]:
            level, degree = "👑 顶尖（清北/常春藤）", "硕士及以上"
        elif basic_net >= 0 and checks_passed >= 3:
            level, degree = "🥇 985顶级大学", "硕士" if yin_18_22 else "本科"
        elif basic_net >= 0:
            level, degree = "🥇 211/一本", "本科"
        elif basic_net >= -1 and checks_passed >= 2:
            level, degree = "🥈 普通本科", "本科"
        elif checks_passed >= 2:
            level, degree = "🥈 普通本科", "专科"
        else:
            level, degree = "🥉 大专/职校", "专科"

        # 身强特别反面逻辑：8岁前遇印运=学非所用
        if basic_net < 0 and any(a < 8 for dg, a in zip(da_yun_gans, da_yun_start_ages)
                                  if get_shi_shen_for_gan(dg, ri_zhu) in ("正印", "偏印") and a < 8):
            # 8岁前遇印→基础学习不好
            if "985" in level or "顶尖" in level:
                level = "🥇 211/一本（8岁前遇印运·基础不好）"
                degree = "本科"

    # ===== 中和（40-60分）：平衡型 =====
    elif shen_score >= 40:
        if yin_before_18 and checks_passed >= 4:
            level, degree = "🥇 985顶级大学", "硕士及以上"
        elif yin_before_18 and checks_passed >= 3:
            level, degree = "🥇 985顶级大学", "硕士"
        elif yin_18_22 and checks_passed >= 3:
            level, degree = "🥇 211/一本", "本科"
        elif checks_passed >= 3:
            level, degree = "🥇 211/一本", "本科"
        elif checks_passed >= 2:
            level, degree = "🥈 普通本科", "本科"
        else:
            level, degree = "🥉 大专/职校", "专科"

    # ===== 身弱（<40分）：印/比=正面；官杀/食伤/财=反面 =====
    elif shen_score >= 15:
        # 身弱关键：0-18岁正面运（印/比）必须≥反面运（官杀/食伤/财）
        if basic_net > 0 and checks_passed >= 3 and wen_chang["has"]:
            level, degree = "🥇 211/一本", "本科"
        elif basic_net > 0 and checks_passed >= 2:
            level, degree = "🥈 普通本科", "本科"
        elif basic_net >= 0 and checks_passed >= 2:
            level, degree = "🥈 普通本科", "专科"
        elif has_yin and checks_passed >= 2:
            # 有印运补救但0-18岁反面运偏多→低一层
            level, degree = "🥉 大专/职校", "专科"
        else:
            level, degree = "🪜 初中/高中", "初中/专科"

    # ===== 身极弱（<15分）：除非大运强力补救 =====
    else:
        if basic_net > 0 and checks_passed >= 3 and wen_chang["has"]:
            level, degree = "🥈 普通本科", "本科"
        else:
            level, degree = "🪜 初中/高中", "初中/专科"

    # ── 年干伤官拉低 ──
    if nian_negative:
        if "顶尖" in level or "985" in level:
            level = level.replace("👑 ", "🥇 ").replace("🥇 ", "🥇 ")
            level += "（年干伤官拉低）"
        elif "211" in level or "一本" in level:
            level += "（年干伤官拉低）"
        if degree in ("硕士及以上", "硕士"):
            degree = "本科"
        _reason()

    return level, degree, _reason()


def analyze_education(
    bazi_gans: list[str], bazi_zhis: list[str], ri_zhu: str,
    shen_score: float, shen_label: str, xi_yong: list[str],
    da_yun_gans: list[str], da_yun_zhis: list[str], da_yun_start_ages: list[float],
) -> dict:
    """学历分析完整体系 v2.2"""
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

    # ── 学业期大运十神正反面分析 ──
    dy_effect = _analyze_da_yun_shi_shen_effect(da_yun_gans, da_yun_start_ages, ri_zhu, shen_score)

    # ── 学校等级+学历层级 ──
    school_level, degree, reason = _determine_degree(
        shen_score, shen_label, six_steps["passed"],
        da_yun_gans, da_yun_start_ages,
        year_check, nian_check, wen_chang, ri_zhu,
    )

    # ── 最终结论 ──
    final_note = reason

    # 文昌补文昌（日干查补运）
    bu_wen_chang_zhi = WEN_CHANG_MAP.get(ri_zhu, "")

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
        "da_yun_shi_shen_effect": dy_effect,
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
