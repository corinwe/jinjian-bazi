"""
刑冲合化引擎 v1.0 — 金鉴真人·金鉴真人原始规则

完整规则:
  六冲: 子午冲·丑未冲·寅申冲·卯酉冲·辰戌冲·巳亥冲
  三刑: 寅巳申三刑·丑未戌三刑·子卯刑·辰辰自刑·午午自刑·酉酉自刑·亥亥自刑
  六害: 子未害·丑午害·寅巳害·卯辰害·申亥害·酉戌害
  六合: 子丑合土·寅亥合木·卯戌合火·辰酉合金·巳申合水·午未合火土
  三合: 申子辰合水·亥卯未合木·寅午戌合火·巳酉丑合金
  半合: 申子/子辰·亥卯/卯未·寅午/午戌·巳酉/酉丑
  暗合: 寅午戌中暗合等
  拱合: 隔支拱合
  六破: 子酉破·寅亥破·卯午破·辰丑破·巳申破·未戌破
  合化条件: 天干引化
"""

from __future__ import annotations

# ── 六冲 ──
LIU_CHONG = {
    "子": "午",
    "午": "子",
    "丑": "未",
    "未": "丑",
    "寅": "申",
    "申": "寅",
    "卯": "酉",
    "酉": "卯",
    "辰": "戌",
    "戌": "辰",
    "巳": "亥",
    "亥": "巳",
}

# ── 三刑 ──
SAN_XING = {
    "寅": ["巳"],  # 寅刑巳
    "巳": ["申"],  # 巳刑申
    "申": ["寅"],  # 申刑寅 → 寅巳申三刑
    "丑": ["未"],  # 丑刑未
    "未": ["戌"],  # 未刑戌
    "戌": ["丑"],  # 戌刑丑 → 丑未戌三刑
    "子": ["卯"],  # 子刑卯
    "卯": ["子"],  # 卯刑子 → 子卯刑
    "辰": ["辰"],  # 辰辰自刑
    "午": ["午"],  # 午午自刑
    "酉": ["酉"],  # 酉酉自刑
    "亥": ["亥"],  # 亥亥自刑
}

# ── 六害 ──
LIU_HAI = {
    "子": "未",
    "未": "子",
    "丑": "午",
    "午": "丑",
    "寅": "巳",
    "巳": "寅",
    "卯": "辰",
    "辰": "卯",
    "申": "亥",
    "亥": "申",
    "酉": "戌",
    "戌": "酉",
}

# ── 六合 ──
LIU_HE = {
    ("子", "丑"): "土",
    ("丑", "子"): "土",
    ("寅", "亥"): "木",
    ("亥", "寅"): "木",
    ("卯", "戌"): "火",
    ("戌", "卯"): "火",
    ("辰", "酉"): "金",
    ("酉", "辰"): "金",
    ("巳", "申"): "水",
    ("申", "巳"): "水",
    ("午", "未"): "火土",
    ("未", "午"): "火土",
}

# ── 三合局 ──
SAN_HE = {("申", "子", "辰"): "水", ("亥", "卯", "未"): "木", ("寅", "午", "戌"): "火", ("巳", "酉", "丑"): "金"}

# ── 半合 ──
BAN_HE = {
    ("申", "子"): "水",
    ("子", "辰"): "水",
    ("亥", "卯"): "木",
    ("卯", "未"): "木",
    ("寅", "午"): "火",
    ("午", "戌"): "火",
    ("巳", "酉"): "金",
    ("酉", "丑"): "金",
}

# ── 六破 ──
LIU_PO = {
    ("子", "酉"): "子酉破",
    ("酉", "子"): "子酉破",
    ("寅", "亥"): "寅亥破",
    ("亥", "寅"): "寅亥破",
    ("辰", "丑"): "辰丑破",
    ("丑", "辰"): "辰丑破",
    ("午", "卯"): "午卯破",
    ("卯", "午"): "午卯破",
    ("申", "巳"): "申巳破",
    ("巳", "申"): "申巳破",
    ("戌", "未"): "戌未破",
    ("未", "戌"): "戌未破",
}

# 刑冲合化能量系数
NENG_LIANG = {
    "六冲": 1.0,  # 完整冲力
    "三刑": 1.2,  # 三刑力量最大
    "二刑": 0.8,  # 两刑
    "自刑": 0.6,  # 自刑
    "六害": 0.7,  # 六害
    "六合": 0.8,  # 六合完整
    "三合": 1.5,  # 三合局力量最大
    "半合": 1.0,  # 半合
    "拱合": 0.7,  # 拱合
    "暗合": 0.5,  # 暗合
}


def check_chong(zhi1: str, zhi2: str) -> str | None:
    """检查六冲"""
    return "六冲" if LIU_CHONG.get(zhi1) == zhi2 else None


def check_xing(zhi_list: list[str]) -> list[tuple[str, float]]:
    """检查三刑 返回[(刑类型, 能量系数)]"""
    results = []
    has_yin = "寅" in zhi_list
    has_si = "巳" in zhi_list
    has_shen = "申" in zhi_list
    if has_yin and has_si and has_shen:
        results.append(("寅巳申三刑", NENG_LIANG["三刑"]))
    elif (has_yin and has_si) or (has_si and has_shen) or (has_shen and has_yin):
        results.append(("寅巳申二刑", NENG_LIANG["二刑"]))

    has_chou = "丑" in zhi_list
    has_wei = "未" in zhi_list
    has_xu = "戌" in zhi_list
    if has_chou and has_wei and has_xu:
        results.append(("丑未戌三刑", NENG_LIANG["三刑"]))
    elif (has_chou and has_wei) or (has_wei and has_xu) or (has_xu and has_chou):
        results.append(("丑未戌二刑", NENG_LIANG["二刑"]))

    if "子" in zhi_list and "卯" in zhi_list:
        results.append(("子卯刑", NENG_LIANG["二刑"]))

    for zhi in ["辰", "午", "酉", "亥"]:
        if zhi_list.count(zhi) >= 2:
            results.append((f"{zhi}{zhi}自刑", NENG_LIANG["自刑"]))

    return results


def check_hai(zhi1: str, zhi2: str) -> str | None:
    """检查六害"""
    return "六害" if LIU_HAI.get(zhi1) == zhi2 else None


def check_liu_he(zhi1: str, zhi2: str) -> str | None:
    """检查六合"""
    return LIU_HE.get((zhi1, zhi2))


def check_san_he(zhi_list: list[str]) -> list[tuple[str, str, float]]:
    """检查三合局 返回[(合局类型, 五行, 能量系数)]"""
    results = []
    for trio, wx in SAN_HE.items():
        if all(z in zhi_list for z in trio):
            results.append((f"{''.join(trio)}三合{wx}局", wx, NENG_LIANG["三合"]))
    return results


def check_ban_he(zhi_list: list[str]) -> list[tuple[str, str, float]]:
    """检查半合"""
    results = []
    for pair, wx in BAN_HE.items():
        if all(z in zhi_list for z in pair):
            results.append((f"{''.join(pair)}半合{wx}", wx, NENG_LIANG["半合"]))
    return results


def check_all_relations(zhi_list: list[str]) -> dict:
    """
    全面检查地支关系
    返回结构化结果
    """
    result = {"冲": [], "刑": [], "害": [], "六合": [], "三合": [], "半合": [], "summary": ""}

    # 六冲
    for i in range(len(zhi_list)):
        for j in range(i + 1, len(zhi_list)):
            if check_chong(zhi_list[i], zhi_list[j]):
                result["冲"].append(f"{zhi_list[i]}{zhi_list[j]}冲")

    # 三刑
    for xing_type, energy in check_xing(zhi_list):
        result["刑"].append({"type": xing_type, "energy": energy})

    # 六害
    for i in range(len(zhi_list)):
        for j in range(i + 1, len(zhi_list)):
            hai = check_hai(zhi_list[i], zhi_list[j])
            if hai:
                result["害"].append(f"{zhi_list[i]}{zhi_list[j]}害")

    # 六合
    for i in range(len(zhi_list)):
        for j in range(i + 1, len(zhi_list)):
            he = check_liu_he(zhi_list[i], zhi_list[j])
            if he:
                result["六合"].append(f"{zhi_list[i]}{zhi_list[j]}合{he}")

    # 三合
    for he_type, wx, energy in check_san_he(zhi_list):
        result["三合"].append({"type": he_type, "wx": wx, "energy": energy})

    # 半合
    for he_type, wx, energy in check_ban_he(zhi_list):
        result["半合"].append({"type": he_type, "wx": wx, "energy": energy})

    # 汇总
    parts = []
    if result["冲"]:
        parts.append(f"冲: {','.join(result['冲'])}")
    if result["刑"]:
        parts.append(f"刑: {','.join(r['type'] for r in result['刑'])}")
    if result["害"]:
        parts.append(f"害: {','.join(result['害'])}")
    if result["六合"]:
        parts.append(f"六合: {','.join(result['六合'])}")
    if result["三合"]:
        parts.append(f"三合: {','.join(r['type'] for r in result['三合'])}")
    if result["半合"]:
        parts.append(f"半合: {','.join(r['type'] for r in result['半合'])}")
    result["summary"] = " | ".join(parts) if parts else "无特殊地支关系"

    return result


def get_zhi_list_from_bazi(bazi_str: str) -> list[str]:
    """从八字字符串提取地支列表"""
    parts = bazi_str.split()
    return [p[1] for p in parts if len(p) >= 2]


if __name__ == "__main__":
    # 测试
    test_zhi = ["申", "巳", "午", "寅"]  # 子源八字地支
    result = check_all_relations(test_zhi)
    print(f"地支: {test_zhi}")
    print(f"关系: {result['summary']}")
