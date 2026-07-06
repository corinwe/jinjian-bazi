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

from constants import DI_ZHI, TIAN_GAN

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

# ── 天干五合 ──
TIAN_GAN_HE = {
    ("甲", "己"): "土", ("己", "甲"): "土",
    ("乙", "庚"): "金", ("庚", "乙"): "金",
    ("丙", "辛"): "水", ("辛", "丙"): "水",
    ("丁", "壬"): "木", ("壬", "丁"): "木",
    ("戊", "癸"): "火", ("癸", "戊"): "火",
}

# ── 三会局 ──
SAN_HUI = {
    ("寅", "卯", "辰"): "木",
    ("巳", "午", "未"): "火",
    ("申", "酉", "戌"): "金",
    ("亥", "子", "丑"): "水",
}

# ── 拱合 ──
GONG_HE = {
    ("亥", "未"): ("卯", "木"),
    ("寅", "戌"): ("午", "火"),
    ("巳", "丑"): ("酉", "金"),
    ("申", "辰"): ("子", "水"),
    ("亥", "卯"): ("未", "木"),
    ("寅", "午"): ("戌", "火"),
    ("巳", "酉"): ("丑", "金"),
    ("申", "子"): ("辰", "水"),
    ("卯", "未"): ("亥", "木"),
    ("午", "戌"): ("寅", "火"),
    ("酉", "丑"): ("巳", "金"),
    ("子", "辰"): ("申", "水"),
}

# ── 暗合 ──
AN_HE = {
    ("子", "巳"): "水", ("巳", "子"): "水",
    ("寅", "午"): "火", ("午", "寅"): "火",
    ("亥", "午"): "木", ("午", "亥"): "木",
}

# 刑冲合化能量系数
# 来源：bazi-liunian-analysis §3.9 能量倍数速查表
# 注：有引化/无引化的区分未在此版本实现，取有引化倍数为标准值
NENG_LIANG = {
    "六冲": 10.0,  # 辰戌/丑未冲=10倍（有引化）/5倍（无引化）— 取有引化最大值
    "丑未戌三刑": 15.0,  # 丑未戌三刑=15倍（有引化）/10倍（无引化）
    "寅巳申三刑": 10.0,  # 寅巳申三刑=10倍（有引化）/8倍（无引化）
    "二刑": 8.0,   # 寅巳申二刑（不全）=约7~8倍
    "自刑": 10.0,  # 辰午酉亥自刑=10倍（有引化）/5倍（无引化）
    "六害": 5.0,   # 六害=5倍
    "六破": 5.0,   # 六破=5倍
    "六合": 10.0,  # 六合=10倍（有引化）/5倍（无引化）
    "三合": 15.0,  # 三合=15倍（有引化）/7倍（无引化）
    "半合": 10.0,  # 半合=10倍（有引化）/5倍（无引化）
    "拱合": 10.0,  # 拱合=10倍（有引化）/5倍（无引化）
    "暗合": 0.5,   # 暗合不改变五行能量，仅代表人际关系
    "天干五合": 10.0,  # 天干五合=10倍
    "三会": 20.0,  # 三会=20倍
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
        results.append(("寅巳申三刑", NENG_LIANG["寅巳申三刑"]))
    elif (has_yin and has_si) or (has_si and has_shen) or (has_shen and has_yin):
        results.append(("寅巳申二刑", NENG_LIANG["二刑"]))

    has_chou = "丑" in zhi_list
    has_wei = "未" in zhi_list
    has_xu = "戌" in zhi_list
    if has_chou and has_wei and has_xu:
        results.append(("丑未戌三刑", NENG_LIANG["丑未戌三刑"]))
    elif (has_chou and has_wei) or (has_wei and has_xu) or (has_xu and has_chou):
        results.append(("丑未戌二刑", NENG_LIANG["二刑"]))

    if "子" in zhi_list and "卯" in zhi_list:
        results.append(("子卯刑", NENG_LIANG["二刑"]))

    # 辰午酉亥自刑 — 自刑四字中任意2个及以上即构成自刑（含跨字组合）
    zi_xing_zhis = ["辰", "午", "酉", "亥"]
    present_zi_xing = [z for z in zi_xing_zhis if z in zhi_list]
    if len(present_zi_xing) >= 2:
        results.append((f"{''.join(present_zi_xing)}自刑", NENG_LIANG["自刑"]))

    return results


def check_hai(zhi1: str, zhi2: str) -> str | None:
    """检查六害"""
    return "六害" if LIU_HAI.get(zhi1) == zhi2 else None


def check_liu_he(zhi1: str, zhi2: str) -> str | None:
    """检查六合"""
    return LIU_HE.get((zhi1, zhi2))


def check_san_he(zhi_list: list[str], kong_wang_zhis: list[str] | None = None) -> list[tuple[str, str, float]]:
    """检查三合局 返回[(合局类型, 五行, 能量系数)]

    三合局完整度等级（R42）:
      - 完整三合（三字齐全+中神无破）→ energy=15
      - 虚邀三合（三字齐全但中神空亡）→ energy=7
      - 半三合（两字）→ energy=5
      - 拱合（两字缺中神）→ energy=3
    """
    if kong_wang_zhis is None:
        kong_wang_zhis = []

    # 三合局中神映射（中间那个地支）
    ZHONG_SHEN_MAP = {
        ("申", "子", "辰"): "子",
        ("亥", "卯", "未"): "卯",
        ("寅", "午", "戌"): "午",
        ("巳", "酉", "丑"): "酉",
    }

    results = []
    for trio, wx in SAN_HE.items():
        if all(z in zhi_list for z in trio):
            # 三字齐全 → 检查中神空亡
            zhong_shen = ZHONG_SHEN_MAP.get(trio, "")
            if zhong_shen and zhong_shen in kong_wang_zhis:
                # 虚邀三合：中神空亡，能量减半
                results.append((f"{''.join(trio)}虚邀三合{wx}局", wx, 7.0))
            else:
                # 完整三合：中神无破
                results.append((f"{''.join(trio)}三合{wx}局", wx, 15.0))

    return results


def check_ban_he(zhi_list: list[str]) -> list[tuple[str, str, float]]:
    """检查半合"""
    results = []
    for pair, wx in BAN_HE.items():
        if all(z in zhi_list for z in pair):
            results.append((f"{''.join(pair)}半合{wx}", wx, NENG_LIANG["半合"]))
    return results


def check_tian_gan_he(gan1: str, gan2: str) -> tuple[bool, str]:
    """检查两个天干是否五合，返回(是否合, 合化五行)"""
    result = TIAN_GAN_HE.get((gan1, gan2))
    if result:
        return True, result
    return False, ""


def check_all_tian_gan_he(gans: list[str]) -> list[dict]:
    """检查八字四天干中所有五合关系，返回列表"""
    results = []
    for i in range(len(gans)):
        for j in range(i + 1, len(gans)):
            matched, wx = check_tian_gan_he(gans[i], gans[j])
            if matched:
                results.append({
                    "type": "天干五合", "positions": (i, j),
                    "gans": (gans[i], gans[j]), "wx": wx
                })
    return results


def check_san_hui(zhis: list[str]) -> list[dict]:
    """检查八字中是否有三会局"""
    results = []
    for trio, wx in SAN_HUI.items():
        if all(z in zhis for z in trio):
            results.append({"type": f"{''.join(trio)}三会{wx}局", "wx": wx, "energy": NENG_LIANG["三会"]})
    return results


def check_gong_he(zhis: list[str]) -> list[dict]:
    """检查八字中是否有拱合关系"""
    results = []
    for (z1, z2), (mid, wx) in GONG_HE.items():
        if z1 in zhis and z2 in zhis:
            results.append({"type": f"{z1}{z2}拱{mid}合{wx}", "wx": wx, "missing": mid, "energy": NENG_LIANG["拱合"]})
    return results


def check_an_he(zhis: list[str]) -> list[dict]:
    """检查八字中是否有暗合关系"""
    results = []
    for i in range(len(zhis)):
        for j in range(i + 1, len(zhis)):
            wx = AN_HE.get((zhis[i], zhis[j]))
            if wx:
                results.append({"type": f"{zhis[i]}{zhis[j]}暗合{wx}", "wx": wx, "energy": NENG_LIANG["暗合"]})
    return results


def _get_kong_wang(day_gan: str, day_zhi: str) -> list[str]:
    """获取日柱对应的空亡地支列表。

    旬空规则：
      甲子旬→戌亥空, 甲戌旬→申酉空, 甲申旬→午未空,
      甲午旬→辰巳空, 甲辰旬→寅卯空, 甲寅旬→子丑空
    """
    gi = TIAN_GAN.index(day_gan)
    zi = DI_ZHI.index(day_zhi)
    xun_idx = 0
    for idx in range(60):
        if idx % 10 == gi and idx % 12 == zi:
            xun_idx = idx // 10
            break
    KONG_WANG_MAP = {
        0: ["戌", "亥"],  # 甲子旬
        1: ["申", "酉"],  # 甲戌旬
        2: ["午", "未"],  # 甲申旬
        3: ["辰", "巳"],  # 甲午旬
        4: ["寅", "卯"],  # 甲辰旬
        5: ["子", "丑"],  # 甲寅旬
    }
    return KONG_WANG_MAP.get(xun_idx, [])


def check_all_relations(zhi_list: list[str], kong_wang_zhis: list[str] | None = None) -> dict:
    """
    全面检查地支关系
    返回结构化结果
    """
    if kong_wang_zhis is None:
        kong_wang_zhis = []
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
    for he_type, wx, energy in check_san_he(zhi_list, kong_wang_zhis):
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


def check_all_relations_v2(zhi_list: list[str], gan_list: list[str] | None = None, kong_wang_zhis: list[str] | None = None) -> dict:
    """
    全面检查地支+天干关系 v2
    新增: 天干五合/三会/拱合/暗合 + 合化优先级

    合化优先级（只保留最高）:
      三会(20倍) > 三合(15倍) > 半合/六合(10倍) > 拱合(10倍) > 暗合(0.5倍)
    """
    # 先跑v1获取基础数据
    result = check_all_relations(zhi_list, kong_wang_zhis)

    # 天干五合
    if gan_list:
        result["天干五合"] = check_all_tian_gan_he(gan_list)
    else:
        result["天干五合"] = []

    # 三会
    result["三会"] = check_san_hui(zhi_list)

    # 拱合
    result["拱合"] = check_gong_he(zhi_list)

    # 暗合
    result["暗合"] = check_an_he(zhi_list)

    # ── 合化优先级（只保留最高优先级） ──
    # 收集所有合化关系
    all_he = []

    # 三会 优先级 4 (最高)
    for h in result["三会"]:
        all_he.append(("三会", h, 4))

    # 三合 优先级 3
    for h in result["三合"]:
        all_he.append(("三合", h, 3))

    # 六合 优先级 2
    for h in result["六合"]:
        all_he.append(("六合", h, 2))

    # 半合 优先级 2
    for h in result["半合"]:
        all_he.append(("半合", h, 2))

    # 拱合 优先级 2
    for h in result["拱合"]:
        all_he.append(("拱合", h, 2))

    # 暗合 优先级 1 (最低)
    for h in result["暗合"]:
        all_he.append(("暗合", h, 1))

    if all_he:
        # 按优先级降序排列
        all_he.sort(key=lambda x: x[2], reverse=True)
        max_priority = all_he[0][2]
        # 只保留最高优先级的
        kept = [item for item in all_he if item[2] == max_priority]
        result["highest_priority"] = {
            "level": max_priority,
            "label": {4: "三会", 3: "三合", 2: "六合/半合/拱合", 1: "暗合"}.get(max_priority, ""),
            "items": [{"category": cat, "detail": h} for cat, h, _ in kept],
        }
    else:
        result["highest_priority"] = None

    # 更新summary
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
    if result["三会"]:
        parts.append(f"三会: {','.join(r['type'] for r in result['三会'])}")
    if result["拱合"]:
        parts.append(f"拱合: {','.join(r['type'] for r in result['拱合'])}")
    if result["暗合"]:
        parts.append(f"暗合: {','.join(r['type'] for r in result['暗合'])}")
    if result["天干五合"]:
        he_strs = [f'{r["gans"][0]}{r["gans"][1]}合{r["wx"]}' for r in result["天干五合"]]
        parts.append(f"天干五合: {','.join(he_strs)}")
    result["summary"] = " | ".join(parts) if parts else "无特殊关系"

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
    print(f"关系(v1): {result['summary']}")

    # 测试 v2（含天干）
    test_gan = ["甲", "己", "丙", "辛"]
    result_v2 = check_all_relations_v2(test_zhi, test_gan)
    print(f"\n天干: {test_gan}")
    print(f"关系(v2): {result_v2['summary']}")
    if result_v2["天干五合"]:
        for h in result_v2["天干五合"]:
            print(f"  天干五合: {h['gans'][0]}{h['gans'][1]}合{h['wx']}")
    if result_v2["三会"]:
        for h in result_v2["三会"]:
            print(f"  三会: {h['type']}")
    if result_v2["highest_priority"]:
        print(f"  最高优先级: {result_v2['highest_priority']['label']} (level {result_v2['highest_priority']['level']})")
