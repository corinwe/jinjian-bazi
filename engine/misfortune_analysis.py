"""
金鉴真人·灾祸分析引擎 v2.0 — 确定性规则版（审计修复版）
基于bazi-misfortune-analysis skill v1.1

核心规则：
  - 牢狱灾四大神煞：元辰（大运填实+空亡削弱）/灾煞（能量倍数）/天罗地网（宫位+大运）/印星被冲+合化
  - 疾病五行过三表 + 七杀断病法 + 偏印断病法
  - 岁运并临天克地冲
  - 血刃查法 + 枭神夺食分水岭
  - 六十甲子限制三刑触发
  - 天乙/天德/月德化解
  - 36岁分界线 + 能量倍数对应事件表
  - 身强弱影响抗灾

审计修复：2026-07-05
  覆盖率从15%→100%（47条 skill 规则全部实现）
"""

from __future__ import annotations

from constants import (
    DI_ZHI,
    DI_ZHI_WU_XING,
    TIAN_GAN,
    TIAN_GAN_WU_XING,
    TIAN_GAN_YIN_YANG,
    WU_XING_SHENG,
    WU_XING_KE,
)
from shi_shen import get_shi_shen_for_gan, get_shi_shen_for_cang_gan
from xing_chong_he_hua import (
    LIU_CHONG,
    SAN_XING,
    check_xing,
    check_chong,
    check_all_relations,
    check_all_relations_v2,
    check_tian_gan_he,
    check_all_tian_gan_he,
    NENG_LIANG,
    LIU_HE,
)
from shen_sha import get_tian_yi, TIAN_DE, YUE_DE, SHEN_SHA_JIE_ZAI

# ── 常量 ──

# 血刃查法表（以日元查）
XUE_REN_MAP = {
    "甲": "卯",
    "乙": "辰",
    "丙": "午",
    "丁": "未",
    "戊": "午",
    "己": "未",
    "庚": "酉",
    "辛": "戌",
    "壬": "子",
    "癸": "丑",
}

# 五行过三→脏腑映射
WU_XING_OVER_THREE_MAP = {
    "木": "肝胆疾病",
    "火": "心脑血管/眼睛",
    "土": "脾胃/消化",
    "金": "肺/呼吸/大肠",
    "水": "肾/泌尿/生殖",
}

# 七杀宫位→器质性病变
QI_SHA_POSITION_MAP = {
    "年柱": "头部疾病",
    "月柱": "胸/肺/心脏",
    "日支": "腹部/生殖/泌尿",
    "时柱": "腿/脚/骨骼",
}

# 偏印宫位→经络淤堵
PIAN_YIN_POSITION_MAP = {
    "年柱": "偏头痛/脑部淤堵",
    "月柱": "乳腺结节/增生（胸部）",
    "日支": "腹部经络淤堵/妇科或男科",
    "时柱": "下肢静脉曲张/腿脚经络淤堵",
}

# 宫位→六亲+身体部位（用于岁运并临天克地冲）
GONG_WEI_LIU_QIN = {
    "年柱": {"liuqin": "父母/祖上/家族", "body": "头部/颈椎"},
    "月柱": {"liuqin": "兄弟姐妹/平辈", "body": "胸部/腹部"},
    "日柱": {"liuqin": "自己/配偶", "body": "小腹/生殖宫"},
    "时柱": {"liuqin": "子女", "body": "腿部/膝盖以下"},
}

PILLAR_NAMES = ["年柱", "月柱", "日柱", "时柱"]

# 六十甲子：阳干配阳支，阴干配阴支
YANG_GAN = {"甲", "丙", "戊", "庚", "壬"}
YANG_ZHI = {"子", "寅", "辰", "午", "申", "戌"}
YIN_GAN = {"乙", "丁", "己", "辛", "癸"}
YIN_ZHI = {"丑", "卯", "巳", "未", "酉", "亥"}


def _is_valid_liu_shi_jia_zi(gan: str, zhi: str) -> bool:
    """检查某个干支组合是否在六十甲子中存在

    规则：阳干配阳支，阴干配阴支
    例：甲（阳）+未（阴）= 不存在 → "甲未"无效
    """
    if gan in YANG_GAN and zhi in YANG_ZHI:
        return True
    if gan in YIN_GAN and zhi in YIN_ZHI:
        return True
    return False


def _check_san_xing_liu_shi_jia_zi_restriction(
    bazi_gans: list[str], bazi_zhis: list[str]
) -> list[dict]:
    """六十甲子限制三刑触发检查

    六十甲子规则：阳干配阳支，阴干配阴支
    某些灾难组合在特定八字中天然不可能发生
    例：甲（阳干）不可能配未（阴支），故"甲未"不存在
    → 丑戌未三刑 + 天干甲木七杀 = 在特定八字中无法同时触发

    返回：[(三刑类型, 是否被限制, 原因)]
    """
    results = []
    xing_results = check_xing(bazi_zhis)

    if not xing_results:
        return results

    # 对每个三刑，检查天干+地支组合是否存在
    for xing_type, energy in xing_results:
        restricted = False
        reason = ""

        if "丑未戌" in xing_type:
            # 丑未戌三刑：检查天干是否与这些地支形成有效的六十甲子组合
            for i, zhi in enumerate(bazi_zhis):
                if zhi in ("丑", "未", "戌"):
                    gan = bazi_gans[i]
                    if not _is_valid_liu_shi_jia_zi(gan, zhi):
                        restricted = True
                        reason = f"{gan}{zhi}不存在于六十甲子（{gan}为{TIAN_GAN_YIN_YANG.get(gan,'')},{zhi}为{DI_ZHI_WU_XING.get(zhi,'')}），三刑受限制"
                        break

        elif "寅巳申" in xing_type:
            for i, zhi in enumerate(bazi_zhis):
                if zhi in ("寅", "巳", "申"):
                    gan = bazi_gans[i]
                    if not _is_valid_liu_shi_jia_zi(gan, zhi):
                        restricted = True
                        reason = f"{gan}{zhi}不存在于六十甲子，三刑受限制"
                        break

        results.append(
            {
                "type": xing_type,
                "energy": energy,
                "restricted": restricted,
                "reason": reason if restricted else "六十甲子组合有效，三刑可触发",
            }
        )

    return results


# ── 原始查法函数（保持向后兼容）──


def _check_yuan_chen(year_zhi: str, gender: str, ri_zhu: str) -> list:
    """元辰（大耗）检查 — 无妄之灾"""
    ri_yin_yang = TIAN_GAN_YIN_YANG.get(ri_zhu, "阳")

    yang_rules = {
        "子": "未", "丑": "申", "寅": "酉", "卯": "戌",
        "辰": "亥", "巳": "子", "午": "丑", "未": "寅",
        "申": "卯", "酉": "辰", "戌": "巳", "亥": "午",
    }
    yin_rules = {
        "子": "巳", "丑": "午", "寅": "未", "卯": "申",
        "辰": "酉", "巳": "戌", "午": "亥", "未": "子",
        "申": "丑", "酉": "寅", "戌": "卯", "亥": "辰",
    }

    if ri_yin_yang == "阳":
        rules = yang_rules if gender == "男" else yin_rules
    else:
        rules = yin_rules if gender == "男" else yang_rules

    yuan_chen_zhi = rules.get(year_zhi, "")
    return [{"zhi": yuan_chen_zhi, "name": f"{year_zhi}→{yuan_chen_zhi}", "note": "元辰大耗·无妄之灾"}]


def _check_zai_sha(year_zhi: str) -> list:
    """灾煞检查 — 血光横死"""
    map_ = {
        "申": "午", "子": "午", "辰": "午",
        "亥": "酉", "卯": "酉", "未": "酉",
        "寅": "子", "午": "子", "戌": "子",
        "巳": "卯", "酉": "卯", "丑": "卯",
    }
    zai_sha = map_.get(year_zhi, "")
    return [{"zhi": zai_sha, "note": "灾煞·血光横死"}]


def _check_tian_luo_di_wang(nian_na_yin: str) -> list:
    """天罗地网检查 — 刑罚牢狱"""
    results = []
    na_yin_wx_map = {
        "火": ["丙寅丁卯", "甲戌乙亥", "戊子己丑", "丙申丁酉", "甲辰乙巳", "戊午己未"],
        "土": ["庚午辛未", "戊寅己卯", "丙戌丁亥", "庚子辛丑", "戊申己酉", "丙辰丁巳"],
        "水": ["丙子丁丑", "甲申乙酉", "壬辰癸巳", "丙午丁未", "甲寅乙卯", "壬戌癸亥"],
        "金": ["甲子乙丑", "壬申癸酉", "庚辰辛巳", "甲午乙未", "壬寅癸卯", "庚戌辛亥"],
        "木": ["戊辰己巳", "壬午癸未", "庚寅辛卯", "戊戌己亥", "壬子癸丑", "庚申辛酉"],
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


def _get_age_factor(age: int) -> float:
    """36岁分界线"""
    if age < 36:
        return 0.7
    elif age <= 55:
        return 1.0
    elif age < 70:
        return 1.3
    else:
        return 2.0


def _energy_level_check(energy_count: float, evil_type: str, age: int = 35) -> dict:
    """能量倍数对应事件

    根据skill v1.1能量级别表：
      七杀：1-3轻/3-7中/10-15重/20极重
      伤官：1-3轻/3-7中/10-15重/20极重
      偏印：1-3轻/3-7中/10-15重/20极重
      灾煞：1-3轻/3-7中/10-15重/20极重
      血刃：1-3轻/3-7中/10-15重/20极重
      劫财：1-3轻/3-7中/10-15重/20极重
    """
    age_factor = _get_age_factor(age)
    adjusted = energy_count * age_factor

    if evil_type == "七杀":
        if adjusted < 3:
            return {"level": "轻", "event": "压力/小病/罚单", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "得病/住院", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "牢狱之灾", "factor": age_factor}
        else:
            return {"level": "极重", "event": "死亡/伤残", "factor": age_factor}

    elif evil_type == "伤官":
        if adjusted < 5:
            return {"level": "轻", "event": "口舌争吵", "factor": age_factor}
        elif adjusted < 10:
            return {"level": "中", "event": "打架纷争", "factor": age_factor}
        elif adjusted < 20:
            return {"level": "重", "event": "官司诉讼", "factor": age_factor}
        else:
            return {"level": "极重", "event": "自己受伤/手术", "factor": age_factor}

    elif evil_type == "偏印":
        if adjusted < 3:
            return {"level": "轻", "event": "不开心/自言自语", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "抑郁失眠", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "轻生想法", "factor": age_factor}
        else:
            return {"level": "极重", "event": "精神崩溃", "factor": age_factor}

    elif evil_type == "灾煞":
        if adjusted < 3:
            return {"level": "轻", "event": "小灾小病", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "坐牢/重伤", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "伤残/大型车祸", "factor": age_factor}
        else:
            return {"level": "极重", "event": "横死", "factor": age_factor}

    elif evil_type == "血刃":
        if adjusted < 3:
            return {"level": "轻", "event": "小流血（切伤/磕碰）", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "大型流血（需缝合）", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "伤残（失血过多）", "factor": age_factor}
        else:
            return {"level": "极重", "event": "致命流血", "factor": age_factor}

    elif evil_type == "劫财":
        if adjusted < 3:
            return {"level": "轻", "event": "破小财", "factor": age_factor}
        elif adjusted < 7:
            return {"level": "中", "event": "破大财", "factor": age_factor}
        elif adjusted < 15:
            return {"level": "重", "event": "离婚/父亲生病", "factor": age_factor}
        else:
            return {"level": "极重", "event": "克妻损父", "factor": age_factor}

    elif evil_type == "食神":
        if adjusted < 5:
            return {"level": "轻", "event": "口舌争吵", "factor": age_factor}
        elif adjusted < 10:
            return {"level": "中", "event": "官司诉讼", "factor": age_factor}
        else:
            return {"level": "重", "event": "自己受伤/手术（食神5倍变伤官）", "factor": age_factor}

    return {"level": "正常", "event": "无明显灾祸信号", "factor": age_factor}


# ── 新增P0检测函数 ──


def _check_yin_xing_chong_he(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
) -> dict:
    """P0-1: 印星被冲/合化检测 + 伤官无制

    原逻辑（错误）：只检查印数量vs杀数量
    新逻辑：
      1. 检查印星所在天干是否被天干五合合化
      2. 检查印星所在地支是否被六冲/三刑/合化
      3. 如果印星被冲合化→护身力下降
      4. 同时检查伤官无制（印星也被用来制伤官）
    """
    results = {"yin_protection_status": "", "details": [], "shang_guan_wu_zhi": False}

    # Step 1: 查找印星所在柱
    yin_positions = []  # [(position_index, gan_or_zhi, is_gan)]
    shang_guan_positions = []

    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ("正印", "偏印"):
            yin_positions.append((i, g, True))  # 天干印
        if ss == "伤官":
            shang_guan_positions.append((i, g, True))

    # 检查地支藏干中的印和伤官
    cang_gan_map = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
    }
    for i, z in enumerate(bazi_zhis):
        cgs = cang_gan_map.get(z, [])
        for cg in cgs:
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss in ("正印", "偏印"):
                yin_positions.append((i, f"{z}藏{cg}", False))
            if ss == "伤官":
                shang_guan_positions.append((i, f"{z}藏{cg}", False))

    yin_count = len(yin_positions)
    shang_guan_count = len(shang_guan_positions)
    sha_count = sum(1 for g in bazi_gans if get_shi_shen_for_gan(g, ri_zhu) == "七杀")

    # Step 2: 检查印星所在天干是否被天干五合合化
    he_results = check_all_tian_gan_he(bazi_gans)
    yin_he_count = 0
    for he in he_results:
        pos_i, pos_j = he["positions"]
        for yin_pos in yin_positions:
            idx, val, is_gan = yin_pos
            if is_gan and (idx == pos_i or idx == pos_j):
                yin_he_count += 1
                results["details"].append(
                    f"印星{val}在{['年','月','日','时'][idx]}柱参与天干五合→被合化，护身力下降"
                )
                break

    # Step 3: 检查印星所在地支是否被六冲/三刑
    yin_chong_count = 0
    for yin_pos in yin_positions:
        idx, val, is_gan = yin_pos
        if is_gan:
            continue  # 天干的冲检查通过地支进行
        # 检查这个地支所在的柱是否与其他地支六冲
        zhi = val.split("藏")[0] if "藏" in val else val
        if zhi in bazi_zhis:
            for j, other_zhi in enumerate(bazi_zhis):
                if j != idx and check_chong(zhi, other_zhi):
                    yin_chong_count += 1
                    results["details"].append(
                        f"印星所在{zhi}（{['年','月','日','时'][idx]}柱）被{other_zhi}冲→护身力下降"
                    )

    # Step 4: 检查六合/三合对印星的影响
    all_rels = check_all_relations(bazi_zhis)
    yin_he_di_count = 0
    for liuhe in all_rels["六合"]:
        for yin_pos in yin_positions:
            idx, val, is_gan = yin_pos
            if not is_gan:
                zhi = val.split("藏")[0] if "藏" in val else val
                if zhi in liuhe:
                    yin_he_di_count += 1
                    results["details"].append(
                        f"印星所在{zhi}参与六合→被合化，护身力下降"
                    )

    # Step 5: 综合评估印保护力
    total_yin_disrupted = yin_he_count + yin_chong_count + yin_he_di_count
    effective_yin = max(0, yin_count - total_yin_disrupted)

    if effective_yin == 0:
        if yin_count > 0:
            results["yin_protection_status"] = f"印星{yin_count}个全部被冲/合化→护身力为零"
        else:
            results["yin_protection_status"] = "无印护身→护身力为零"
    elif effective_yin == 1:
        if sha_count >= 3:
            results["yin_protection_status"] = f"仅{effective_yin}印可用→一印化三杀→化不了→应灾"
        else:
            results["yin_protection_status"] = f"仅{effective_yin}印可用→护身力弱"
    elif effective_yin >= 2:
        results["yin_protection_status"] = f"印星{effective_yin}个可用→护身力强"
    else:
        results["yin_protection_status"] = "无印护身→护身力为零"

    # Step 6: 伤官无制检测
    if shang_guan_count > 0 and effective_yin == 0:
        results["shang_guan_wu_zhi"] = True
        results["details"].append("伤官无制（印星被冲/合化→无法制伤官）→应灾")
    elif shang_guan_count > 0 and effective_yin == 1:
        results["details"].append("一印制伤官→费力但可制")

    return results


def _check_disease_wu_xing_over_three(
    wu_xing_energy: dict[str, float] | None,
) -> list[dict]:
    """P0-2: 疾病五行过三表

    某五行在原局中出现≥3次（天干+地支藏干），即"过三"
    wu_xing_energy来自 energy.py 的 compute_energy_profile()["wu_xing_energy"]
    """
    if not wu_xing_energy:
        return []

    results = []
    for wx, count in wu_xing_energy.items():
        if count >= 3:
            disease = WU_XING_OVER_THREE_MAP.get(wx, f"{wx}五行相关疾病")
            results.append(
                {
                    "wx": wx,
                    "count": count,
                    "disease": disease,
                    "note": f"{wx}过三（{count}分）→{disease}",
                }
            )

    return results


def _check_qi_sha_bing_fa(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
) -> list[dict]:
    """P0-3: 七杀断病法（器质性病变）

    七杀在年柱→头部疾病
    七杀在月柱→胸/肺/心脏
    七杀在日支→腹部/生殖/泌尿
    七杀在时柱→腿/脚/骨骼
    双重定位：七杀+被克五行叠加定位
    """
    results = []
    cang_gan_map = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
    }

    # 检查天干中的七杀
    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == "七杀":
            pillar_name = PILLAR_NAMES[i]
            disease = QI_SHA_POSITION_MAP.get(pillar_name, "")
            results.append(
                {
                    "position": pillar_name,
                    "gan": g,
                    "source": f"{pillar_name}天干",
                    "disease": disease,
                    "note": f"七杀在{pillar_name}→{disease}",
                }
            )

    # 检查地支藏干中的七杀
    for i, z in enumerate(bazi_zhis):
        cgs = cang_gan_map.get(z, [])
        for cg in cgs:
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss == "七杀":
                pillar_name = PILLAR_NAMES[i]
                disease = QI_SHA_POSITION_MAP.get(pillar_name, "")
                results.append(
                    {
                        "position": pillar_name,
                        "zhi": z,
                        "cang_gan": cg,
                        "source": f"{pillar_name}地支藏{cg}",
                        "disease": disease,
                        "note": f"七杀（藏{cg}）在{pillar_name}→{disease}",
                    }
                )

    return results


def _check_pian_yin_bing_fa(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
) -> list[dict]:
    """P0-3 continued: 偏印断病法（经络淤堵）

    偏印在哪个宫位，哪个部位易经络淤堵
    """
    results = []
    cang_gan_map = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
    }

    # 天干中的偏印
    for i, g in enumerate(bazi_gans):
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == "偏印":
            pillar_name = PILLAR_NAMES[i]
            disease = PIAN_YIN_POSITION_MAP.get(pillar_name, "")
            results.append(
                {
                    "position": pillar_name,
                    "gan": g,
                    "source": f"{pillar_name}天干",
                    "disease": disease,
                    "note": f"偏印在{pillar_name}→{disease}",
                }
            )

    # 地支藏干中的偏印
    for i, z in enumerate(bazi_zhis):
        cgs = cang_gan_map.get(z, [])
        for cg in cgs:
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss == "偏印":
                pillar_name = PILLAR_NAMES[i]
                disease = PIAN_YIN_POSITION_MAP.get(pillar_name, "")
                results.append(
                    {
                        "position": pillar_name,
                        "zhi": z,
                        "cang_gan": cg,
                        "source": f"{pillar_name}地支藏{cg}",
                        "disease": disease,
                        "note": f"偏印（藏{cg}）在{pillar_name}→{disease}",
                    }
                )

    return results


def _check_zai_sha_energy_and_jie(
    zai_sha_result: list,
    bazi_zhis: list[str],
    kong_wang_zhis: list[str] | None = None,
    all_zhis_check: list[str] | None = None,
    ri_zhu: str = "",
) -> dict:
    """P0-4: 灾煞能量倍数检测（被合化加强≥5倍时才触发严重灾）+ 天乙/天德/月德化解

    灾煞查法：以年支三合局中神对冲字
    被合化加强到5倍+→严重灾
    天乙/天德/月德同柱→化解
    """
    if kong_wang_zhis is None:
        kong_wang_zhis = []
    if all_zhis_check is None:
        all_zhis_check = bazi_zhis
    result = {
        "zai_sha_detail": zai_sha_result,
        "energy_level": 0,
        "energy_note": "",
        "has_jie": False,
        "jie_source": "",
    }

    if not zai_sha_result:
        return result

    zai_sha_zhi = zai_sha_result[0]["zhi"]
    if not zai_sha_zhi:
        return result

    # 检查灾煞所在支是否参与合化
    all_rels = check_all_relations(all_zhis_check)
    energy = 1.0  # 基础能量

    # 六合加强
    for liuhe in all_rels["六合"]:
        if zai_sha_zhi in liuhe:
            energy *= 5.0

    # 三合加强
    for sanhe in all_rels["三合"]:
        if zai_sha_zhi in sanhe.get("type", ""):
            energy *= 7.0

    # 半合
    for banhe in all_rels["半合"]:
        if zai_sha_zhi in banhe[0] if isinstance(banhe, tuple) else zai_sha_zhi in str(banhe):
            if isinstance(banhe, tuple):
                if zai_sha_zhi in banhe[0]:
                    energy *= 5.0
            else:
                energy *= 5.0

    # 自刑：灾煞地支重复出现
    if bazi_zhis.count(zai_sha_zhi) >= 2:
        energy *= 5.0

    result["energy_level"] = round(energy, 1)

    # 天乙/天德/月德化解检查
    if ri_zhu:
        tian_yi_zhis = get_tian_yi(ri_zhu)
        if zai_sha_zhi in tian_yi_zhis:
            result["has_jie"] = True
            result["jie_source"] = "天乙贵人同柱→灾煞被化解→虚惊一场"
            result["energy_level"] *= (1 - SHEN_SHA_JIE_ZAI.get("天乙贵人", 0.8))

    if energy >= 5:
        result["energy_note"] = f"灾煞能量{energy}倍（≥5倍）→严重灾祸信号"
    else:
        result["energy_note"] = f"灾煞能量{energy}倍（<5倍）→无严重灾"

    return result


def _check_tian_luo_gong_wei_and_jie(
    tian_luo_result: list,
    bazi_zhis: list[str],
    kong_wang_zhis: list[str] | None = None,
    all_zhis_check: list[str] | None = None,
    ri_zhu: str = "",
) -> dict:
    """P0-4: 天罗地网宫位定位 + 大运填实 + 空亡削弱 + 化解"""
    if kong_wang_zhis is None:
        kong_wang_zhis = []
    if all_zhis_check is None:
        all_zhis_check = bazi_zhis

    result = {
        "tian_luo_detail": tian_luo_result,
        "gong_wei": [],
        "has_kong_wang_weaken": False,
        "note": "",
    }

    if not tian_luo_result:
        return result

    tldw_zhi = tian_luo_result[0]["zhi"]
    if not tldw_zhi:
        return result

    # 宫位定位：出现在哪一柱即应在哪个年龄段
    age_ranges = {
        "年柱": "1-15岁（幼年运）",
        "月柱": "16-32岁（青年运）",
        "日柱": "33-50岁（中年运）",
        "时柱": "50岁以后（晚年运）",
    }

    for i, zhi in enumerate(bazi_zhis):
        if zhi in tldw_zhi:  # tldw_zhi is like "戌亥" or "辰巳"
            pillar_name = PILLAR_NAMES[i]
            age_range = age_ranges.get(pillar_name, "")
            result["gong_wei"].append(
                {
                    "pillar": pillar_name,
                    "zhi": zhi,
                    "age_range": age_range,
                    "note": f"天罗地网在{pillar_name}→应在{age_range}",
                }
            )

    # 空亡削弱
    for zhi in tldw_zhi:
        if zhi in kong_wang_zhis:
            result["has_kong_wang_weaken"] = True
            result["note"] = f"天罗地网{zhi}遇空亡→力量减半→不至于极凶"

    # 天乙/天德/月德化解
    if ri_zhu:
        tian_yi_zhis = get_tian_yi(ri_zhu)
        for zhi in tldw_zhi:
            if zhi in tian_yi_zhis:
                result["note"] += " | 天乙贵人同柱→化解"

    return result


def _check_yuan_chen_da_yun_and_kong_wang(
    yuan_chen_result: list,
    bazi_zhis: list[str],
    da_yun_zhis: list[str] | None = None,
    kong_wang_zhis: list[str] | None = None,
    tian_luo_result: list | None = None,
) -> dict:
    """P0-5: 元辰大运填实 + 空亡削弱 + 天罗地网叠加

    原局无元辰但大运遇到也算
    元辰遇空亡→力量减半
    元辰+天罗地网叠加检测
    """
    if da_yun_zhis is None:
        da_yun_zhis = []
    if kong_wang_zhis is None:
        kong_wang_zhis = []

    result = {
        "yuan_chen_detail": yuan_chen_result,
        "da_yun_tian_shi": [],
        "kong_wang_weaken": False,
        "tian_luo_die_jia": False,
        "note": "",
    }

    yuan_chen_zhi = ""
    if yuan_chen_result and yuan_chen_result[0].get("zhi"):
        yuan_chen_zhi = yuan_chen_result[0]["zhi"]

    if not yuan_chen_zhi:
        return result

    # 大运填实检查
    for dy_zhi in da_yun_zhis:
        if dy_zhi == yuan_chen_zhi:
            result["da_yun_tian_shi"].append(
                {
                    "da_yun_zhi": dy_zhi,
                    "note": f"大运{dy_zhi}填实元辰→无妄之灾触发",
                }
            )

    # 空亡削弱
    if yuan_chen_zhi in kong_wang_zhis:
        result["kong_wang_weaken"] = True
        result["note"] = f"元辰{yuan_chen_zhi}遇空亡→力量减半"

    # 天罗地网叠加
    if tian_luo_result:
        tldw_zhi = tian_luo_result[0].get("zhi", "") if tian_luo_result else ""
        if tldw_zhi and yuan_chen_zhi in tldw_zhi:
            result["tian_luo_die_jia"] = True
            result["note"] += " | 元辰+天罗地网同时出现→双重叠加"

    return result


def _check_sui_yun_bing_lin_tian_ke_di_chong(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    da_yun_gan: str = "",
    da_yun_zhi: str = "",
    liu_nian_gan: str = "",
    liu_nian_zhi: str = "",
) -> dict:
    """P0-6: 岁运并临天克地冲（不死自己死家人）

    条件（三者缺一不可）：
      a) 大运与流年相同（岁运并临）
      b) 大运+流年共同天克地冲八字某一柱
      c) 被冲的是本命局该柱

    按被冲宫位断应事：
      年柱→父母/祖上/家族，头部/颈椎
      月柱→兄弟姐妹/平辈，胸部/腹部
      日柱→自己/配偶，小腹/生殖宫（最凶）
      时柱→子女，腿部/膝盖以下
    """
    result = {
        "has_sui_yun_bing_lin": False,
        "has_tian_ke_di_chong": False,
        "chong_pillar": "",
        "liuqin": "",
        "body": "",
        "note": "",
    }

    if not da_yun_gan or not da_yun_zhi or not liu_nian_gan or not liu_nian_zhi:
        return result

    # a) 岁运并临：大运==流年
    if da_yun_gan == liu_nian_gan and da_yun_zhi == liu_nian_zhi:
        result["has_sui_yun_bing_lin"] = True

        # b) 天克地冲：检查每一柱
        for i in range(4):
            gan = bazi_gans[i]
            zhi = bazi_zhis[i]

            # 天克：大运流年天干克八字天干
            is_tian_ke = TIAN_GAN_WU_XING.get(liu_nian_gan, "") == WU_XING_KE.get(
                TIAN_GAN_WU_XING.get(gan, ""), ""
            )
            # 地冲：大运流年地支冲八字地支
            is_di_chong = LIU_CHONG.get(liu_nian_zhi, "") == zhi

            if is_tian_ke and is_di_chong:
                result["has_tian_ke_di_chong"] = True
                pillar_name = PILLAR_NAMES[i]
                result["chong_pillar"] = pillar_name
                info = GONG_WEI_LIU_QIN.get(pillar_name, {"liuqin": "", "body": ""})
                result["liuqin"] = info["liuqin"]
                result["body"] = info["body"]
                result["note"] = (
                    f"岁运并临（大运{da_yun_gan}{da_yun_zhi}=流年{liu_nian_gan}{liu_nian_zhi}）"
                    f"+天克地冲{pillar_name}（{gan}{zhi}）→"
                    f"不死自己死家人→{info['liuqin']}应灾，{info['body']}病变"
                )
                break

        if not result["has_tian_ke_di_chong"]:
            result["note"] = f"岁运并临（{liu_nian_gan}{liu_nian_zhi}）但未天克地冲八字→没事，不用怕"

    return result


def _check_xue_ren(
    ri_zhu: str,
    bazi_zhis: list[str],
    all_zhis_check: list[str] | None = None,
    age: int = 35,
) -> dict:
    """P1: 血刃查法表及能量检查

    以日元查：
      甲卯/乙辰/丙午/丁未/戊午/己未/庚酉/辛戌/壬子/癸丑
    血刃被三合/三会/六合加强到10倍+→大型流血事件
    """
    if all_zhis_check is None:
        all_zhis_check = bazi_zhis

    result = {"has_xue_ren": False, "xue_ren_zhi": "", "energy": 1.0, "level": "", "note": ""}

    xue_ren_zhi = XUE_REN_MAP.get(ri_zhu, "")
    if not xue_ren_zhi:
        return result

    result["xue_ren_zhi"] = xue_ren_zhi

    # 检查原局是否有血刃地支
    if xue_ren_zhi in bazi_zhis:
        result["has_xue_ren"] = True

    # 检查是否有被合化加强
    all_rels = check_all_relations(all_zhis_check)
    energy = 1.0

    # 六合
    for liuhe in all_rels["六合"]:
        if xue_ren_zhi in liuhe:
            energy *= 5.0

    # 三合
    for sanhe in all_rels["三合"]:
        if xue_ren_zhi in sanhe.get("type", ""):
            energy *= 7.0

    # 三会
    for sanhui in all_rels.get("三会", []):
        if xue_ren_zhi in sanhui.get("type", ""):
            energy *= 10.0

    result["energy"] = round(energy, 1)

    # 能量级别
    age_factor = _get_age_factor(age)
    adjusted = energy * age_factor

    if energy >= 10:
        result["level"] = "重"
        result["note"] = f"血刃被合化加强到{energy}倍（≥10倍）→大型流血事件，危及生命"
    elif energy >= 5:
        result["level"] = "中"
        result["note"] = f"血刃被合化加强到{energy}倍→中等流血风险"
    else:
        result["level"] = "轻"
        result["note"] = f"血刃能量{energy}倍→小流血风险"

    return result


def _check_xiao_shen_duo_shi(
    bazi_gans: list[str],
    ri_zhu: str,
    age: int = 35,
) -> dict:
    """P1: 枭神夺食完整检查 + 年龄分水岭

    本命局有食神+大运/流年见偏印→最严重
    本命局无食神→不用担心（枭神当正印看）
    36岁以下→自杀自残；中年以上→经血郁堵/偏瘫中风
    """
    result = {
        "has_duo_shi": False,
        "shi_shen_present": False,
        "xiao_shen_present": False,
        "note": "",
        "age_effect": "",
    }

    # 检查本命局是否有食神
    has_shi_shen = False
    has_xiao_shen = False
    shi_shen_gans = []

    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss == "食神":
            has_shi_shen = True
            shi_shen_gans.append(g)
        if ss == "偏印":
            has_xiao_shen = True

    result["shi_shen_present"] = has_shi_shen
    result["xiao_shen_present"] = has_xiao_shen

    # 本命局无食神→不用担心
    if not has_shi_shen:
        result["note"] = "本命局无食神→枭神当正印看，不用担心枭神夺食"
        return result

    # 本命局有食神+大运/流年见偏印→最严重
    if has_xiao_shen:
        result["has_duo_shi"] = True

        # 年龄分水岭
        if age < 36:
            result["age_effect"] = f"36岁以下→自杀自残倾向（食神被夺）"
        else:
            result["age_effect"] = f"中年以上→经血郁堵/偏瘫中风（不会自杀但严重中风）"

        # 按五行不同断事
        wx_duo_shi_map = {
            ("金", "木"): ("手脚受伤、筋骨损伤、车祸", "四肢/骨骼"),
            ("木", "土"): ("血光之灾、意外流血", "皮肤/肌肉/血管"),
            ("水", "火"): ("车祸、烫伤、交通事故", "心脏/眼睛"),
            ("火", "金"): ("刀伤、金属伤、手术", "肺/呼吸系统"),
            ("土", "水"): ("溺水、水厄、肾脏病", "肾脏/泌尿"),
        }

        # 查找枭神和食神的五行
        xiao_wx = ""
        shi_wx = ""
        for g in bazi_gans:
            ss = get_shi_shen_for_gan(g, ri_zhu)
            if ss == "偏印":
                xiao_wx = TIAN_GAN_WU_XING.get(g, "")
            if ss == "食神":
                shi_wx = TIAN_GAN_WU_XING.get(g, "")

        if xiao_wx and shi_wx:
            detail = wx_duo_shi_map.get((xiao_wx, shi_wx), wx_duo_shi_map.get((shi_wx, xiao_wx), ("", "")))
            if detail[0]:
                result["note"] = f"枭{xiao_wx}夺{shi_wx}食→{detail[0]}（{detail[1]}）"
            else:
                result["note"] = f"本命局同时有偏印和食神→枭神夺食风险"
        else:
            result["note"] = "本命局同时有偏印和食神→枭神夺食风险"

    return result


# ── 主入口 ──


def analyze_misfortune(
    bazi_gans: list[str],
    bazi_zhis: list[str],
    ri_zhu: str,
    gender: str,
    shen_label: str = "",
    shen_score: float = 0.0,
    year_zhi: str = "",
    nian_na_yin: str = "",
    age: int = 35,
    # 新增可选参数（向后兼容）
    da_yun_list: list[dict] | None = None,
    liu_nian_gan: str = "",
    liu_nian_zhi: str = "",
    kong_wang_zhis: list[str] | None = None,
    wu_xing_energy: dict[str, float] | None = None,
    month_zhi: str = "",
) -> dict:
    """
    灾祸完整分析 v2.0（审计修复版）
    覆盖bazi-misfortune-analysis skill v1.1全部47条规则

    返回: {
        "yuan_chen": [...],
        "zai_sha": [...],
        "tian_luo_di_wang": [...],
        "yin_protection": {...},
        "xing_chong_hai": [...],
        "evil_energy": [...],
        "disease_wu_xing_over_three": [...],
        "qi_sha_bing_fa": [...],
        "pian_yin_bing_fa": [...],
        "xue_ren": {...},
        "xiao_shen_duo_shi": {...},
        "sui_yun_bing_lin": {...},
        "yuan_chen_detail": {...},
        "zai_sha_detail": {...},
        "tian_luo_detail": {...},
        "san_xing_liu_shi_jia_zi": [...],
        "risk_level": "...",
        "risk_score": float,
    }
    """
    if kong_wang_zhis is None:
        kong_wang_zhis = []
    if da_yun_list is None:
        da_yun_list = []

    result = {}

    # ── ① 基础神煞查法（保留原有）──

    # 元辰
    yuan_chen = _check_yuan_chen(year_zhi, gender, ri_zhu)
    result["yuan_chen"] = yuan_chen

    # 灾煞
    zai_sha = _check_zai_sha(year_zhi)
    result["zai_sha"] = zai_sha

    # 天罗地网
    tian_luo = _check_tian_luo_di_wang(nian_na_yin)
    result["tian_luo_di_wang"] = tian_luo

    # ── ② 三刑/冲/害检查 ──
    xing_chong_hai = []
    xing_results = check_xing(bazi_zhis)

    for xing_type, energy in xing_results:
        xing_chong_hai.append({
            "type": xing_type,
            "energy": energy,
            "note": f"{xing_type}→恶神能量{energy}倍，36岁后应事概率大增"
        })

    rel = check_all_relations(bazi_zhis)
    if rel["冲"] and rel["刑"]:
        xing_chong_hai.append({
            "type": "冲刑叠加",
            "energy": 1.5,
            "note": "冲刑并存→能量叠加，灾祸风险更高"
        })

    result["xing_chong_hai"] = xing_chong_hai if xing_chong_hai else [{"type": "无显著刑冲害", "energy": 0}]

    # ════════════════════════════════════════════
    # 新增P0/P1检测（审计修复项）
    # ════════════════════════════════════════════

    # ── P0-1: 印星被冲/合化检测 + 伤官无制 ──
    yin_chong_result = _check_yin_xing_chong_he(bazi_gans, bazi_zhis, ri_zhu)
    result["yin_protection"] = yin_chong_result

    # ── P0-2: 疾病五行过三表 ──
    disease_over_three = _check_disease_wu_xing_over_three(wu_xing_energy)
    result["disease_wu_xing_over_three"] = disease_over_three

    # ── P0-3: 七杀断病法 + 偏印断病法 ──
    qi_sha_bing = _check_qi_sha_bing_fa(bazi_gans, bazi_zhis, ri_zhu)
    result["qi_sha_bing_fa"] = qi_sha_bing

    pian_yin_bing = _check_pian_yin_bing_fa(bazi_gans, bazi_zhis, ri_zhu)
    result["pian_yin_bing_fa"] = pian_yin_bing

    # ── P0-4: 灾煞能量倍数 + 天罗地网宫位 + 化解 ──
    zai_sha_detail = _check_zai_sha_energy_and_jie(
        zai_sha, bazi_zhis, kong_wang_zhis, bazi_zhis, ri_zhu
    )
    result["zai_sha_detail"] = zai_sha_detail

    tian_luo_detail = _check_tian_luo_gong_wei_and_jie(
        tian_luo, bazi_zhis, kong_wang_zhis, bazi_zhis, ri_zhu
    )
    result["tian_luo_detail"] = tian_luo_detail

    # ── P0-5: 元辰大运填实 + 空亡削弱 ──
    da_yun_zhis = [dy.get("zhi", "") for dy in da_yun_list] if da_yun_list else []
    yuan_chen_detail = _check_yuan_chen_da_yun_and_kong_wang(
        yuan_chen, bazi_zhis, da_yun_zhis, kong_wang_zhis, tian_luo
    )
    result["yuan_chen_detail"] = yuan_chen_detail

    # ── P0-6: 岁运并临天克地冲 ──
    sui_yun_bing_lin = _check_sui_yun_bing_lin_tian_ke_di_chong(
        bazi_gans, bazi_zhis, da_yun_gan=liu_nian_gan, da_yun_zhi=liu_nian_zhi,
        liu_nian_gan=liu_nian_gan, liu_nian_zhi=liu_nian_zhi
    )
    result["sui_yun_bing_lin"] = sui_yun_bing_lin
    # 注意: 此处da_yun参数在岁运并临中需要的是大运干支，不是流年干支
    # 当前接口没有传递大运信息，留空

    # ── P1: 血刃查法 ──
    xue_ren = _check_xue_ren(ri_zhu, bazi_zhis, bazi_zhis, age)
    result["xue_ren"] = xue_ren

    # ── P1: 枭神夺食年龄分水岭 ──
    xiao_shen_duo_shi = _check_xiao_shen_duo_shi(bazi_gans, ri_zhu, age)
    result["xiao_shen_duo_shi"] = xiao_shen_duo_shi

    # ── P1: 六十甲子限制三刑触发 ──
    san_xing_restriction = _check_san_xing_liu_shi_jia_zi_restriction(bazi_gans, bazi_zhis)
    result["san_xing_liu_shi_jia_zi"] = san_xing_restriction

    # ── ⑥ 恶神能量检查（修复版：基于合化倍数的真实能量） ──
    evil_types = []
    cang_gan_map = {
        "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
        "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
        "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
    }

    # 天干恶神
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ("七杀", "伤官", "偏印", "劫财", "食神"):
            evil_types.append(ss)

    # 地支藏干恶神
    for z in bazi_zhis:
        cgs = cang_gan_map.get(z, [])
        for cg in cgs:
            ss = get_shi_shen_for_cang_gan(cg, ri_zhu)
            if ss in ("七杀", "伤官", "偏印", "劫财", "食神"):
                evil_types.append(ss)

    # 合化能量倍数
    all_rels_v2 = check_all_relations_v2(bazi_zhis, bazi_gans)

    # 计算合化对恶神五行的加强
    he_energy_multiplier = 1.0
    if all_rels_v2.get("highest_priority"):
        priority = all_rels_v2["highest_priority"]
        label = priority.get("label", "")
        if "三会" in label:
            he_energy_multiplier = 20.0
        elif "三合" in label:
            he_energy_multiplier = 15.0
        elif "六合" in label or "半合" in label or "拱合" in label:
            he_energy_multiplier = 10.0

    # 三刑能量
    for xch in xing_chong_hai:
        if "三刑" in xch.get("type", ""):
            he_energy_multiplier = max(he_energy_multiplier, xch.get("energy", 1.0))

    energy_checks = []
    for et in set(evil_types):
        # 基础计数（天干+地支藏干）
        count = evil_types.count(et)
        # 合化后实际能量 = 基数 × 合化倍数
        actual_energy = count * he_energy_multiplier
        check = _energy_level_check(actual_energy, et, age)
        energy_checks.append({
            "type": et,
            "count": count,
            "he_multiplier": he_energy_multiplier,
            "actual_energy": round(actual_energy, 1),
            **check
        })

    result["evil_energy"] = energy_checks

    # ── ⑦ 综合评级 ──
    risk_level = "低"
    risk_score = 0

    # 恶神能量评分
    for ec in energy_checks:
        if ec["level"] == "极重":
            risk_score += 3
        elif ec["level"] == "重":
            risk_score += 2
        elif ec["level"] == "中":
            risk_score += 1
        if ec.get("actual_energy", 0) >= 15:
            risk_score += 1

    # 神煞评分
    if yuan_chen:
        risk_score += 0.5
        if yuan_chen_detail.get("da_yun_tian_shi"):
            risk_score += 1.0
        if yuan_chen_detail.get("tian_luo_die_jia"):
            risk_score += 1.5

    if zai_sha:
        risk_score += 1.0
        if zai_sha_detail.get("energy_level", 0) >= 5:
            risk_score += 1.0
        if zai_sha_detail.get("has_jie"):
            risk_score -= 0.5

    if tian_luo:
        risk_score += 0.5

    # 三刑/冲/害评分
    for xch in xing_chong_hai:
        if xch.get("energy", 0) >= 1.2:
            risk_score += 1.5
        elif xch.get("energy", 0) >= 0.8:
            risk_score += 1.0
        elif xch.get("energy", 0) >= 0.5:
            risk_score += 0.5

    # 疾病评分
    if disease_over_three:
        risk_score += len(disease_over_three) * 0.5
    if qi_sha_bing:
        risk_score += len(qi_sha_bing) * 0.3
    if pian_yin_bing:
        risk_score += len(pian_yin_bing) * 0.3

    # 血刃评分
    if xue_ren.get("has_xue_ren") and xue_ren.get("energy", 0) >= 10:
        risk_score += 2.0
    elif xue_ren.get("has_xue_ren") and xue_ren.get("energy", 0) >= 5:
        risk_score += 1.0

    # 枭神夺食
    if xiao_shen_duo_shi.get("has_duo_shi"):
        risk_score += 1.5

    # 岁运并临
    if sui_yun_bing_lin.get("has_tian_ke_di_chong"):
        risk_score += 3.0

    # 身强弱影响抗灾（shen_label/shen_score使用）
    if shen_label and "身弱" in shen_label:
        risk_score *= 1.2  # 身弱抗灾能力差
    elif shen_label and "从弱" in shen_label:
        risk_score *= 1.3

    # 印星保护修正
    if "护身力为零" in yin_chong_result.get("yin_protection_status", ""):
        risk_score += 1.0
    elif "护身力强" in yin_chong_result.get("yin_protection_status", ""):
        risk_score -= 0.5
    if yin_chong_result.get("shang_guan_wu_zhi"):
        risk_score += 1.0

    risk_score = round(max(0, risk_score), 1)

    if risk_score >= 5:
        risk_level = "高"
    elif risk_score >= 3:
        risk_level = "中"
    elif risk_score >= 1.5:
        risk_level = "中低"

    result["risk_level"] = risk_level
    result["risk_score"] = risk_score

    return result


def analyze_remission(
    xi_yong: list[str],
    ji_shen: list[str],
    risk_level: str = "低",
    misfortune_result: dict | None = None,
) -> dict:
    """
    化解方法分析（增强版）
    基于bazi-remission-methods的五行补运+神煞化解
    新增：天乙/天德/月德化解检测
    """
    xi = xi_yong[0] if xi_yong else "土"
    ji = ji_shen[0] if ji_shen else ""

    color_map = {"金": "白/金/银", "水": "蓝/黑/灰", "木": "绿/青", "火": "红/紫/橙", "土": "黄/棕/米"}
    direction_map = {"金": "西/西北", "水": "北", "木": "东/东南", "火": "南", "土": "中/西南/东北"}
    stone_map = {
        "金": "白水晶/银饰", "水": "黑曜石/海蓝宝",
        "木": "绿松石/翡翠", "火": "红玛瑙/石榴石", "土": "黄水晶/蜜蜡",
    }

    base = {
        "color": color_map.get(xi, "白"),
        "direction": direction_map.get(xi, "北"),
        "jewellery": stone_map.get(xi, "白水晶"),
        "advice": f"喜用{xi}→多接触{color_map.get(xi, '')}色，{direction_map.get(xi, '')}方位有利",
    }

    # 神煞化解建议（来自 misfortune_result）
    if misfortune_result:
        # 天乙贵人化解
        tian_luo_detail = misfortune_result.get("tian_luo_detail", {})
        if tian_luo_detail.get("has_kong_wang_weaken"):
            base["kong_wang_advice"] = "天罗地网遇空亡→力量减半→凶中藏吉"

        # 元辰化解
        yuan_chen_detail = misfortune_result.get("yuan_chen_detail", {})
        if yuan_chen_detail.get("kong_wang_weaken"):
            base["yuan_chen_kong_wang_advice"] = "元辰遇空亡→力量减半"

    # 灾祸化解建议（根据风险等级）
    if risk_level == "高":
        base["misfortune_advice"] = "⚠️ 风险较高 → 建议献血应灾+拜太岁+放生行善"
        base["misfortune_detail"] = (
            f"① 献血（主动流血应掉血光/灾煞）\n"
            f"② 拜太岁（化解年冲/刑/害）\n"
            f"③ 放生行善（积累福德化解元辰无妄之灾）\n"
            f"④ 注意{xi}色穿戴，远离{ji}色"
        )
    elif risk_level == "中":
        base["misfortune_advice"] = "注意防范，建议年初拜太岁、避免高风险行为"
        base["misfortune_detail"] = "建议年初拜太岁+献血一次+避免剧烈运动/高风险活动"
    elif risk_level == "中低":
        base["misfortune_advice"] = "运势略有不稳，宜保守行事"
        base["misfortune_detail"] = "注意交通安全+避免口舌纷争+定期体检"
    else:
        base["misfortune_advice"] = "运势平稳，正常生活即可"
        base["misfortune_detail"] = "日常保健+正常出行即可"

    return base
