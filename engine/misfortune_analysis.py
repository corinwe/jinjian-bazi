"""
金鉴真人·灾祸分析引擎 v1.0 — 确定性规则版
基于bazi-misfortune-analysis v1.0

核心规则：
  - 四大牢狱神煞：元辰/灾煞/天罗地网/印星被冲
  - 恶神能量倍数对应事件表
  - 36岁分界线
  - 三刑/冲/害应事规则
"""

from __future__ import annotations
from constants import (
    TIAN_GAN, TIAN_GAN_YIN_YANG, TIAN_GAN_WU_XING,
    DI_ZHI, DI_ZHI_WU_XING, DI_ZHI_CANG_GAN,
    WU_XING_SHENG, WU_XING_KE,
)
from shi_shen import get_shi_shen_for_gan, get_shi_shen_for_cang_gan


def _check_yuan_chen(year_zhi: str, gender: str, ri_zhu: str) -> list:
    """元辰（大耗）检查 — 无妄之灾"""
    ri_yin_yang = TIAN_GAN_YIN_YANG.get(ri_zhu, "阳")
    
    # 阳男阴女：子→未, 丑→申, 寅→酉, 卯→戌, 辰→亥, 巳→子
    #           午→丑, 未→寅, 申→卯, 酉→辰, 戌→巳, 亥→午
    yang_rules = {"子":"未","丑":"申","寅":"酉","卯":"戌","辰":"亥","巳":"子",
                  "午":"丑","未":"寅","申":"卯","酉":"辰","戌":"巳","亥":"午"}
    
    # 阴男阳女：子→巳, 丑→午, 寅→未, 卯→申, 辰→酉, 巳→戌
    #           午→亥, 未→子, 申→丑, 酉→寅, 戌→卯, 亥→辰
    yin_rules = {"子":"巳","丑":"午","寅":"未","卯":"申","辰":"酉","巳":"戌",
                 "午":"亥","未":"子","申":"丑","酉":"寅","戌":"卯","亥":"辰"}
    
    if ri_yin_yang == "阳":
        rules = yang_rules if gender == "男" else yin_rules
    else:
        rules = yin_rules if gender == "男" else yang_rules
    
    yuan_chen_zhi = rules.get(year_zhi, "")
    return [{"zhi": yuan_chen_zhi, "name": f"{year_zhi}→{yuan_chen_zhi}", "note": "元辰大耗·无妄之灾"}]


def _check_zai_sha(year_zhi: str) -> list:
    """灾煞检查 — 血光横死"""
    map_ = {
        "申": "午", "子": "午", "辰": "午",  # 申子辰→午
        "亥": "酉", "卯": "酉", "未": "酉",  # 亥卯未→酉
        "寅": "子", "午": "子", "戌": "子",  # 寅午戌→子
        "巳": "卯", "酉": "卯", "丑": "卯",  # 巳酉丑→卯
    }
    zai_sha = map_.get(year_zhi, "")
    return [{"zhi": zai_sha, "note": "灾煞·血光横死"}]


def _check_tian_luo_di_wang(nian_na_yin: str) -> list:
    """天罗地网检查 — 刑罚牢狱"""
    results = []
    # 纳音五行
    na_yin_wx_map = {
        "火": ["丙寅丁卯","甲戌乙亥","戊子己丑","丙申丁酉","甲辰乙巳","戊午己未"],
        "土": ["庚午辛未","戊寅己卯","丙戌丁亥","庚子辛丑","戊申己酉","丙辰丁巳"],
        "水": ["丙子丁丑","甲申乙酉","壬辰癸巳","丙午丁未","甲寅乙卯","壬戌癸亥"],
        "金": ["甲子乙丑","壬申癸酉","庚辰辛巳","甲午乙未","壬寅癸卯","庚戌辛亥"],
        "木": ["戊辰己巳","壬午癸未","庚寅辛卯","戊戌己亥","壬子癸丑","庚申辛酉"],
    }
    
    na_yin_wx = ""
    for wx, stems in na_yin_wx_map.items():
        for s in stems:
            if nian_na_yin.startswith(s[:2]):
                na_yin_wx = wx
                break
    
    if na_yin_wx == "火":
        results.append({"zhi": "戌亥", "note": "天罗（火命见戌亥）"})
    elif na_yin_wx in ("水", "土"):
        results.append({"zhi": "辰巳", "note": "地网（水土命见辰巳）"})
    elif na_yin_wx in ("金", "木"):
        pass  # 金木无天罗地网
    
    return results


def _energy_level_check(energy_count: int, evil_type: str, age: int = 35) -> dict:
    """能量倍数对应事件"""
    age_factor = 1.0
    if age < 36:
        age_factor = 0.7
    elif age > 55 and age < 70:
        age_factor = 1.3
    elif age >= 70:
        age_factor = 2.0
    
    adjusted = energy_count * age_factor
    
    # 七杀能量表
    if evil_type == "七杀":
        if adjusted < 3:
            return {"level": "轻", "event": "压力/小病/罚单", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "得病/住院", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "牢狱之灾", "factor": age_factor}
        else:
            return {"level": "极重", "event": "死亡/伤残", "factor": age_factor}
    
    # 伤官能量表
    elif evil_type == "伤官":
        if adjusted < 3:
            return {"level": "轻", "event": "口舌争吵", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "打架纷争", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "官司诉讼", "factor": age_factor}
        else:
            return {"level": "极重", "event": "自己受伤/手术", "factor": age_factor}
    
    # 枭神能量表
    elif evil_type == "偏印":
        if adjusted < 3:
            return {"level": "轻", "event": "不开心/自言自语", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "抑郁失眠", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "轻生想法", "factor": age_factor}
        else:
            return {"level": "极重", "event": "精神崩溃", "factor": age_factor}
    
    # 灾煞能量表
    elif evil_type == "灾煞":
        if adjusted < 3:
            return {"level": "轻", "event": "小灾小病", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "坐牢/重伤", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "伤残/大型车祸", "factor": age_factor}
        else:
            return {"level": "极重", "event": "横死", "factor": age_factor}
    
    return {"level": "正常", "event": "无明显灾祸信号", "factor": age_factor}


def analyze_misfortune(
    bazi_gans: list[str], bazi_zhis: list[str],
    ri_zhu: str, gender: str,
    shen_label: str, shen_score: float,
    year_zhi: str, nian_na_yin: str = "",
    age: int = 35,
) -> dict:
    """
    灾祸完整分析
    返回 四大神煞+恶神能量检查+综合风险评级
    """
    result = {}
    
    # ① 元辰检查
    yuan_chen = _check_yuan_chen(year_zhi, gender, ri_zhu)
    result["yuan_chen"] = yuan_chen
    
    # ② 灾煞检查
    zai_sha = _check_zai_sha(year_zhi)
    result["zai_sha"] = zai_sha
    
    # ③ 天罗地网检查
    tian_luo = _check_tian_luo_di_wang(nian_na_yin)
    result["tian_luo_di_wang"] = tian_luo
    
    # ④ 印星被冲检查
    yin_chong = []
    all_ss = [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]
    yin_count = sum(1 for ss in all_ss if ss in ("正印", "偏印"))
    sha_count = sum(1 for ss in all_ss if ss == "七杀")
    
    if sha_count > 0:
        if yin_count == 0:
            yin_chong.append("无印护身→七杀无制")
        elif yin_count == 1 and sha_count >= 3:
            yin_chong.append("一印化三杀→印力不足")
        elif yin_count >= 2:
            yin_chong.append(f"印星{yin_count}个→护身力强")
    result["yin_protection"] = yin_chong if yin_chong else ["印星护身正常"]
    
    # ⑤ 恶神能量检查
    evil_types = []
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ("七杀", "伤官", "偏印"):
            evil_types.append(ss)
    
    energy_checks = []
    for et in set(evil_types):
        count = evil_types.count(et)
        check = _energy_level_check(count, et, age)
        energy_checks.append({"type": et, "count": count, **check})
    
    result["evil_energy"] = energy_checks
    
    # ⑥ 综合评级
    risk_level = "低"
    risk_score = 0
    for ec in energy_checks:
        if ec["level"] == "极重":
            risk_score += 3
        elif ec["level"] == "重":
            risk_score += 2
        elif ec["level"] == "中":
            risk_score += 1
    
    if yuan_chen:
        risk_score += 0.5
    if zai_sha:
        risk_score += 1
    
    if risk_score >= 4:
        risk_level = "高"
    elif risk_score >= 2:
        risk_level = "中"
    
    result["risk_level"] = risk_level
    result["risk_score"] = round(risk_score, 1)
    
    return result


def analyze_remission(
    xi_yong: list[str], ji_shen: list[str],
    risk_level: str = "低",
) -> dict:
    """
    化解方法分析
    基于bazi-remission-methods的五行补运+神煞化解
    """
    xi = xi_yong[0] if xi_yong else "土"
    ji = ji_shen[0] if ji_shen else ""
    
    color_map = {"金": "白/金/银", "水": "蓝/黑/灰", "木": "绿/青", "火": "红/紫/橙", "土": "黄/棕/米"}
    direction_map = {"金": "西/西北", "水": "北", "木": "东/东南", "火": "南", "土": "中/西南/东北"}
    stone_map = {"金": "白水晶/银饰", "水": "黑曜石/海蓝宝", "木": "绿松石/翡翠", "火": "红玛瑙/石榴石", "土": "黄水晶/蜜蜡"}
    
    base = {
        "color": color_map.get(xi, "白"),
        "direction": direction_map.get(xi, "北"),
        "jewellery": stone_map.get(xi, "白水晶"),
        "advice": f"喜用{xi}→多接触{color_map.get(xi,'')}色，{direction_map.get(xi,'')}方位有利",
    }
    
    # 灾祸化解建议
    if risk_level == "高":
        base["misfortune_advice"] = "⚠️ 风险较高 → 建议献血应灾+拜太岁+放生行善"
    elif risk_level == "中":
        base["misfortune_advice"] = "注意防范，建议年初拜太岁、避免高风险行为"
    else:
        base["misfortune_advice"] = "运势平稳，正常生活即可"
    
    return base
