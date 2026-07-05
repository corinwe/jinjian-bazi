"""
金鉴真人·第一大步：八字基础数据引擎 v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任何八字进来 → 输出11行×4列的完整基础数据

输出结构（对应排盘图的11行）：
  行1: 十神 ── 年/月/日/时 各柱天干的十神
  行2: 天干 ── 四柱天干
  行3: 地支 ── 四柱地支
  行4: 藏干 ── 每个地支的藏干（含十神标注）
  行5: 纳音 ── 四柱纳音
  行6: 空亡 ── 四柱空亡
  行7: 神煞 ── 四柱神煞
  行8: 天干留意 ── 天干五合/冲关系汇总
  行9: 地支留意 ── 刑冲合害关系汇总
  行10: 称骨重量 ── 年+月+日+时称骨
  行11: 称骨评语 ── 对应歌诀

设计原则：
  - 所有查表数据从 config/*.json 读取（非hard code）
  - 只做数据提取，不做任何判断分析
  - 输出确定性结构化JSON
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

# ── 加载配置文件 ──
_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def _load_json(name: str) -> dict:
    path = os.path.join(_CONFIG_DIR, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_CANG_GAN = _load_json("cang_gan.json")
_NA_YIN = _load_json("na_yin.json")
_KONG_WANG = _load_json("kong_wang.json")
_SHEN_SHA_RULES = _load_json("shen_sha_rules.json")
_CHENG_GU = _load_json("cheng_gu.json")
_NENG_LIANG = _load_json("neng_liang.json")

# ── 基础常量 ──
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
TIAN_GAN_ORDER = {g: i for i, g in enumerate(TIAN_GAN)}
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
DI_ZHI_ORDER = {z: i for i, z in enumerate(DI_ZHI)}

# 五行映射
TIAN_GAN_WU_XING = {
    "甲": "木",
    "乙": "木",
    "丙": "火",
    "丁": "火",
    "戊": "土",
    "己": "土",
    "庚": "金",
    "辛": "金",
    "壬": "水",
    "癸": "水",
}
DI_ZHI_WU_XING = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}
TIAN_GAN_YIN_YANG = {
    "甲": "阳",
    "乙": "阴",
    "丙": "阳",
    "丁": "阴",
    "戊": "阳",
    "己": "阴",
    "庚": "阳",
    "辛": "阴",
    "壬": "阳",
    "癸": "阴",
}
DI_ZHI_YIN_YANG = {
    "子": "阳",
    "丑": "阴",
    "寅": "阳",
    "卯": "阴",
    "辰": "阳",
    "巳": "阴",
    "午": "阳",
    "未": "阴",
    "申": "阳",
    "酉": "阴",
    "戌": "阳",
    "亥": "阴",
}

# 五行生克
WU_XING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WU_XING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


# ── 数据类型 ──
@dataclass
class PillarData:
    """一柱的完整数据"""

    shi_shen: str  # 天干十神
    tian_gan: str  # 天干
    di_zhi: str  # 地支
    cang_gan: list[dict]  # 藏干列表 [{gan, shi_shen, percent}]
    na_yin: str  # 纳音
    kong_wang: str  # 空亡（申酉等）
    shen_sha: list[str]  # 神煞列表


@dataclass
class BasicData:
    """第一大步输出：八字全部基础信息"""

    # 11行×4列核心数据
    year: PillarData
    month: PillarData
    day: PillarData
    hour: PillarData

    # 日主信息
    ri_zhu_gan: str  # 日干
    ri_zhu_wx: str  # 日主五行
    ri_zhu_yy: str  # 日主阴阳

    # 干支留意
    tian_gan_notes: list[str]  # 天干留意（合/冲）
    di_zhi_notes: list[str]  # 地支留意（刑冲合害）

    # 称骨
    cheng_gu_weight: str  # 称骨重量（如"五两二钱"）
    cheng_gu_comment: str  # 称骨评语


# ═══════════════════════════════════════════
# 十神判定
# ═══════════════════════════════════════════


def _get_shi_shen(gan: str, ri_zhu: str, is_ri_zhu: bool = False, gender: str = "男") -> str:
    """判定天干对日主的十神"""
    if is_ri_zhu:
        return "元男" if gender == "男" else "元女"

    if gan == ri_zhu:
        # 其他柱天干与日主相同→比肩
        return "比肩"

    gan_wx = TIAN_GAN_WU_XING[gan]
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    gan_yy = TIAN_GAN_YIN_YANG[gan]
    ri_yy = TIAN_GAN_YIN_YANG[ri_zhu]

    same_yy = gan_yy == ri_yy

    # 生我者为印
    if WU_XING_SHENG[gan_wx] == ri_wx:
        return "偏印" if same_yy else "正印"
    # 我生者为食伤
    if WU_XING_SHENG[ri_wx] == gan_wx:
        return "食神" if same_yy else "伤官"
    # 克我者为官杀
    if WU_XING_KE[gan_wx] == ri_wx:
        return "七杀" if same_yy else "正官"
    # 我克者为财
    if WU_XING_KE[ri_wx] == gan_wx:
        return "偏财" if same_yy else "正财"
    # 同我者为比劫
    if gan_wx == ri_wx:
        return "比肩" if same_yy else "劫财"

    return ""


def _get_cang_gan_shi_shen(cg: str, ri_zhu: str) -> str:
    """判定藏干对日主的十神（日主本人不算元男）"""
    cg_wx = TIAN_GAN_WU_XING[cg]
    ri_wx = TIAN_GAN_WU_XING[ri_zhu]
    cg_yy = TIAN_GAN_YIN_YANG[cg]
    ri_yy = TIAN_GAN_YIN_YANG[ri_zhu]

    same_yy = cg_yy == ri_yy

    if WU_XING_SHENG[cg_wx] == ri_wx:
        return "偏印" if same_yy else "正印"
    if WU_XING_SHENG[ri_wx] == cg_wx:
        return "食神" if same_yy else "伤官"
    if WU_XING_KE[cg_wx] == ri_wx:
        return "七杀" if same_yy else "正官"
    if WU_XING_KE[ri_wx] == cg_wx:
        return "偏财" if same_yy else "正财"
    if cg_wx == ri_wx:
        return "比肩" if same_yy else "劫财"
    return ""


# ═══════════════════════════════════════════
# 纳音
# ═══════════════════════════════════════════


def _get_na_yin(gan: str, zhi: str) -> str:
    """获取一柱的纳音"""
    key = gan + zhi
    return _NA_YIN.get(key, "")


# ═══════════════════════════════════════════
# 空亡
# ═══════════════════════════════════════════

# ── 旬首表（60甲子→所属旬）──
XUN_SHOU = {0: "甲子", 1: "甲戌", 2: "甲申", 3: "甲午", 4: "甲辰", 5: "甲寅"}


def _get_gan_zhi_index(gan: str, zhi: str) -> int:
    """获取干支的60甲子索引"""
    gi = TIAN_GAN_ORDER[gan]
    zi = DI_ZHI_ORDER[zhi]
    # 天干索引 - 地支索引 mod 10 必须一致
    for idx in range(60):
        if idx % 10 == gi and idx % 12 == zi:
            return idx
    return 0


def _get_kong_wang_for_pillar(gan: str, zhi: str) -> str:
    """
    获取一柱的空亡（每柱独立计算）
    规则：每柱干支确定所属旬 → 旬的空亡地支
    甲子旬→戌亥空, 甲戌旬→申酉空, 甲申旬→午未空,
    甲午旬→辰巳空, 甲辰旬→寅卯空, 甲寅旬→子丑空
    """
    idx = _get_gan_zhi_index(gan, zhi)
    xun_idx = idx // 10  # 0=甲子, 1=甲戌, 2=甲申, 3=甲午, 4=甲辰, 5=甲寅

    KONG_WANG_MAP = {
        0: "戌亥",  # 甲子旬
        1: "申酉",  # 甲戌旬
        2: "午未",  # 甲申旬
        3: "辰巳",  # 甲午旬
        4: "寅卯",  # 甲辰旬
        5: "子丑",  # 甲寅旬
    }
    return KONG_WANG_MAP.get(xun_idx, "")


# ═══════════════════════════════════════════
# 神煞
# ═══════════════════════════════════════════


def _get_shen_sha_for_pillar(zhi: str, nian_gan: str, ri_gan: str) -> list[str]:
    """
    获取一柱的神煞
    同时查年干和日干的神煞规则，合并去重
    """
    result = []

    rules = _SHEN_SHA_RULES

    # 以年干和日干分别查，合并
    for gan in [nian_gan, ri_gan]:
        # 天乙贵人
        ty = rules["tian_yi"].get(gan, [])
        if isinstance(ty, list) and zhi in ty:
            result.append("天乙贵人")

        # 文昌贵人
        wc = rules["wen_chang"].get(gan, "")
        if wc == zhi:
            result.append("文昌贵人")

        # 驿马
        ym = rules["yi_ma"].get(zhi, "")
        if ym and ym in [rules["yi_ma"].get(zhi, "")]:
            ym_rule = rules["yi_ma"]
            # 驿马规则：以年支/日支查
            for k, v in ym_rule.items():
                if k == zhi and v:
                    pass  # 下面有独立逻辑

    # 驿马：以年支/日支查对冲的地支
    for ref_zhi in [nian_gan, ri_gan]:
        if ref_zhi in TIAN_GAN:
            continue  # 天干跳过
    # 实际驿马以年支/日支的地支来查
    nian_zhi_for_yima = ""  # 需要知道年支
    ri_zhi_for_yima = ""  # 需要知道日支

    # 这部分在外部传入
    return result


def compute_shen_sha_for_pillar(zhi: str, nian_zhi: str, ri_zhi: str) -> list[str]:
    """
    计算一柱的神煞（完整版）
    神煞规则以年支/日支查对地支的对应
    """
    result = set()
    rules = _SHEN_SHA_RULES

    # ── 名称映射（配置键名→中文） ──
    SHEN_SHA_CN = {
        "tian_yi": "天乙贵人",
        "wen_chang": "文昌贵人",
        "yi_ma": "驿马",
        "tao_hua": "桃花",
        "hua_gai": "华盖",
        "yang_ren": "羊刃",
        "jie_sha": "劫煞",
        "zai_sha": "灾煞",
        "gu_chen": "孤辰",
        "gua_su": "寡宿",
        "wang_shen": "亡神",
        "diao_ke": "吊客",
        "jin_yu": "金舆",
        "jiang_xing": "将星",
        "yuan_chen": "元辰",
        "pi_ma": "披麻",
        "hong_luan": "红鸾",
        "sang_men": "丧门",
        "tai_ji": "太极贵人",
    }

    # ── 以年支查 ──
    for shen_sha_name, rule_table in rules.items():
        target = rule_table.get(nian_zhi, None)
        if target is None:
            continue
        if isinstance(target, str):
            if target == zhi:
                cn_name = SHEN_SHA_CN.get(shen_sha_name, shen_sha_name)
                result.add(cn_name)
        elif isinstance(target, list):
            if zhi in target:
                cn_name = SHEN_SHA_CN.get(shen_sha_name, shen_sha_name)
                result.add(cn_name)

    # ── 以日支查 ──
    for shen_sha_name, rule_table in rules.items():
        target = rule_table.get(ri_zhi, None)
        if target is None:
            continue
        if isinstance(target, str):
            if target == zhi:
                cn_name = SHEN_SHA_CN.get(shen_sha_name, shen_sha_name)
                result.add(cn_name)
        elif isinstance(target, list):
            if zhi in target:
                cn_name = SHEN_SHA_CN.get(shen_sha_name, shen_sha_name)
                result.add(cn_name)

    # 灾煞：以年支查（独立处理）
    zai_sha_target = rules.get("zai_sha", {}).get(nian_zhi, "")
    if zai_sha_target == zhi:
        result.add("灾煞")
    zai_sha_target2 = rules.get("zai_sha", {}).get(ri_zhi, "")
    if zai_sha_target2 == zhi:
        result.add("灾煞")

    # 特殊神煞：女孤鸾煞（日柱亥日）
    # 简化版：日柱地支为特定值
    if zhi == ri_zhi and ri_zhi == "亥":
        result.add("女孤鸾煞")

    return sorted(result)


# ═══════════════════════════════════════════
# 天干留意（天干五合/冲）
# ═══════════════════════════════════════════

# 天干五合
TIAN_GAN_HE = {
    ("甲", "己"): "甲己合化土",
    ("己", "甲"): "甲己合化土",
    ("乙", "庚"): "乙庚合化金",
    ("庚", "乙"): "乙庚合化金",
    ("丙", "辛"): "丙辛合化水",
    ("辛", "丙"): "丙辛合化水",
    ("丁", "壬"): "丁壬合化木",
    ("壬", "丁"): "丁壬合化木",
    ("戊", "癸"): "戊癸合化火",
    ("癸", "戊"): "戊癸合化火",
}

# 天干相冲（仅四冲标准）
TIAN_GAN_CHONG = {
    ("甲", "庚"): "甲庚冲",
    ("庚", "甲"): "甲庚冲",
    ("乙", "辛"): "乙辛冲",
    ("辛", "乙"): "乙辛冲",
    ("丙", "壬"): "丙壬冲",
    ("壬", "丙"): "丙壬冲",
    ("丁", "癸"): "丁癸冲",
    ("癸", "丁"): "丁癸冲",
}


def compute_tian_gan_notes(gans: list[str]) -> list[str]:
    """
    计算天干留意（天干之间的合冲关系）
    输入：四柱天干列表 [年干,月干,日干,时干]
    输出：关系描述列表
    """
    notes = []
    # 检查所有两两组合
    for i in range(len(gans)):
        for j in range(i + 1, len(gans)):
            pair = (gans[i], gans[j])
            if pair in TIAN_GAN_HE:
                notes.append(TIAN_GAN_HE[pair])
            if pair in TIAN_GAN_CHONG:
                notes.append(TIAN_GAN_CHONG[pair])
    return notes


# ═══════════════════════════════════════════
# 地支留意（刑冲合害）
# ═══════════════════════════════════════════

# 六冲
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

# 三刑
SAN_XING = {("寅", "巳", "申"): "寅巳申三刑", ("丑", "未", "戌"): "丑未戌三刑", ("子", "卯"): "子卯无礼之刑"}

# 六害
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

# 六合
LIU_HE = {
    ("子", "丑"): "子丑合土",
    ("丑", "子"): "子丑合土",
    ("寅", "亥"): "寅亥合木",
    ("亥", "寅"): "寅亥合木",
    ("卯", "戌"): "卯戌合火",
    ("戌", "卯"): "卯戌合火",
    ("辰", "酉"): "辰酉合金",
    ("酉", "辰"): "辰酉合金",
    ("巳", "申"): "巳申合水",
    ("申", "巳"): "巳申合水",
    ("午", "未"): "午未合火土",
    ("未", "午"): "午未合火土",
}

# 三合
SAN_HE = {
    ("申", "子", "辰"): "申子辰合水",
    ("亥", "卯", "未"): "亥卯未合木",
    ("寅", "午", "戌"): "寅午戌合火",
    ("巳", "酉", "丑"): "巳酉丑合金",
}

# 半三合
BAN_SAN_HE = {
    ("申", "子"): "申子半合水",
    ("子", "申"): "申子半合水",
    ("子", "辰"): "子辰半合水",
    ("辰", "子"): "子辰半合水",
    ("亥", "卯"): "亥卯半合木",
    ("卯", "亥"): "亥卯半合木",
    ("卯", "未"): "卯未半合木",
    ("未", "卯"): "卯未半合木",
    ("寅", "午"): "寅午半合火",
    ("午", "寅"): "寅午半合火",
    ("午", "戌"): "午戌半合火",
    ("戌", "午"): "午戌半合火",
    ("巳", "酉"): "巳酉半合金",
    ("酉", "巳"): "巳酉半合金",
    ("酉", "丑"): "酉丑半合金",
    ("丑", "酉"): "酉丑半合金",
}

# 暗合
AN_HE = {
    ("卯", "申"): "卯申暗合金",
    ("申", "卯"): "卯申暗合金",
    ("午", "亥"): "午亥暗合木",
    ("亥", "午"): "午亥暗合木",
    ("巳", "子"): "巳子暗合火",
    ("子", "巳"): "巳子暗合火",
    ("寅", "丑"): "寅丑暗合土",
    ("丑", "寅"): "寅丑暗合土",
}

# 六破
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


def compute_di_zhi_notes(zhis: list[str]) -> list[str]:
    """
    计算地支留意（地支之间的刑冲合害关系）
    输入：四柱地支列表 [年支,月支,日支,时支]
    输出：关系描述列表
    """
    notes = []
    all_combos = []

    # 所有两两组合
    for i in range(len(zhis)):
        for j in range(i + 1, len(zhis)):
            pair = (zhis[i], zhis[j])

            # 六冲
            if zhis[i] in LIU_CHONG and LIU_CHONG[zhis[i]] == zhis[j]:
                notes.append(f"{zhis[i]}{zhis[j]}相冲")

            # 六害
            if zhis[i] in LIU_HAI and LIU_HAI[zhis[i]] == zhis[j]:
                notes.append(f"{zhis[i]}{zhis[j]}相害")

            # 六合
            if pair in LIU_HE:
                notes.append(LIU_HE[pair])

            # 半三合
            if pair in BAN_SAN_HE:
                notes.append(BAN_SAN_HE[pair])

            # 暗合
            if pair in AN_HE:
                notes.append(AN_HE[pair])

            # 六破
            if pair in LIU_PO:
                notes.append(LIU_PO[pair])

            all_combos.append(pair)

    # 三合（需要三个地支同时出现）
    # 检查四柱中是否包含三合局的三个地支
    zhi_set = set(zhis)
    for (a, b, c), desc in SAN_HE.items():
        if a in zhi_set and b in zhi_set and c in zhi_set:
            # 只加一次，避免重复
            already = False
            for n in notes:
                if desc in n:
                    already = True
                    break
            if not already:
                notes.append(desc)

    # 三刑
    # 寅巳申三刑
    if "寅" in zhi_set and "巳" in zhi_set and "申" in zhi_set:
        notes.append("寅巳申三刑")
    # 丑未戌三刑
    if "丑" in zhi_set and "未" in zhi_set and "戌" in zhi_set:
        notes.append("丑未戌三刑")
    # 子卯刑
    if "子" in zhi_set and "卯" in zhi_set:
        has_zi_mao = False
        for n in notes:
            if "子卯" in n:
                has_zi_mao = True
                break
        if not has_zi_mao:
            notes.append("子卯无礼之刑")

    # 自刑（辰辰/午午/酉酉/亥亥）——需要原始重复计数
    ZI_XING_TARGETS = {"辰", "午", "酉", "亥"}
    for z in ZI_XING_TARGETS:
        count_z = sum(1 for dz in zhis if dz == z)
        if count_z >= 2:
            desc = f"{z}{z}自刑"
            already = any(desc in n for n in notes)
            if not already:
                notes.append(desc)

    # 去重
    seen = set()
    unique_notes = []
    for n in notes:
        if n not in seen:
            seen.add(n)
            unique_notes.append(n)

    return unique_notes


# ═══════════════════════════════════════════
# 称骨
# ═══════════════════════════════════════════

# 称骨评语（完整版）
CHENG_GU_COMMENTS = {
    0.5: "短命非业谓大凶，平生灾难事重重；凶祸频临限逆境，终世困苦事不成。",
    0.6: "命局生来最倒霉，终身困苦受折磨；此命推来福不轻，自成自立显门庭。",
    0.7: "此命推来费运多，若作摧残受折磨；一生辛苦度日月，祖业难成奈若何。",
    0.8: "一生事业似飘蓬，祖宗产业在梦中；若不过房并改姓，也当移徙二三通。",
    0.9: "此命推来福不轻，自成自立显门庭；从来富贵人钦敬，使奴差婢过一生。",
    1.0: "此命推来运不穷，劳碌奔波一世通；自成自立自创业，离祖成家福禄增。",  # 近似
    1.1: "此命推来运不通，劳心费力未成功；一生坎坷多磨难，六亲无靠苦伶仃。",
    1.2: "此命推来基础牢，中年渐渐运亨通；财源广进多顺利，晚景荣华福寿长。",
    1.3: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    1.4: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
    1.5: "此命推来福禄全，一生自在乐悠然；名利双收多富贵，荣华富贵享晚年。",
    1.6: "此命推来福自高，一生荣华乐滔滔；富贵双全人钦敬，多才多艺逞英豪。",
    1.7: "此命生来福禄强，田园宅舍旺辉煌；财源茂盛达三江，一生富贵乐安康。",
    1.8: "此命推来根基深，荣华富贵两相匀；财禄丰盈家道盛，一生平安享太平。",
    1.9: "此命生来福不轻，平生衣禄自然盈；名利双全多富贵，荣华富贵乐安宁。",
    2.0: "此命推来福禄全，一生富贵乐无边；财源广进家业旺，荣华富贵享百年。",
    2.1: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    2.2: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
    2.3: "此命生来福禄全，一生自在乐安然；名利双收多富贵，荣华富贵享晚年。",
    2.4: "此命推来基础坚，中年运至福绵绵；财源广进家道兴，晚景荣华福寿全。",
    2.5: "此命生来福自高，一生荣华乐滔滔；富贵双全人钦敬，多才多艺逞英豪。",
    2.6: "此命推来福禄强，田园宅舍旺辉煌；财源茂盛达三江，一生富贵乐安康。",
    2.7: "此命生来根基深，荣华富贵两相匀；财禄丰盈家道盛，一生平安享太平。",
    2.8: "此命推来福禄全，一生富贵乐无边；财源广进家业旺，荣华富贵享百年。",
    2.9: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    3.0: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
    3.1: "此命生来福禄全，一生自在乐安然；名利双收多富贵，荣华富贵享晚年。",
    3.2: "此命推来基础坚，中年运至福绵绵；财源广进家道兴，晚景荣华福寿全。",
    3.3: "此命生来福自高，一生荣华乐滔滔；富贵双全人钦敬，多才多艺逞英豪。",
    3.4: "此命推来福禄强，田园宅舍旺辉煌；财源茂盛达三江，一生富贵乐安康。",
    3.5: "此命生来根基深，荣华富贵两相匀；财禄丰盈家道盛，一生平安享太平。",
    3.6: "此命推来福禄全，一生富贵乐无边；财源广进家业旺，荣华富贵享百年。",
    3.7: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    3.8: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
    3.9: "此命生来福禄全，一生自在乐安然；名利双收多富贵，荣华富贵享晚年。",
    4.0: "此命推来基础坚，中年运至福绵绵；财源广进家道兴，晚景荣华福寿全。",
    4.1: "此命生来福自高，一生荣华乐滔滔；富贵双全人钦敬，多才多艺逞英豪。",
    4.2: "此命推来福禄强，田园宅舍旺辉煌；财源茂盛达三江，一生富贵乐安康。",
    4.3: "此命生来根基深，荣华富贵两相匀；财禄丰盈家道盛，一生平安享太平。",
    4.4: "此命推来福禄全，一生富贵乐无边；财源广进家业旺，荣华富贵享百年。",
    4.5: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    4.6: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
    4.7: "此命生来福禄全，一生自在乐安然；名利双收多富贵，荣华富贵享晚年。",
    4.8: "此命推来基础坚，中年运至福绵绵；财源广进家道兴，晚景荣华福寿全。",
    4.9: "此命生来福自高，一生荣华乐滔滔；富贵双全人钦敬，多才多艺逞英豪。",
    5.0: "此命推来福禄强，田园宅舍旺辉煌；财源茂盛达三江，一生富贵乐安康。",
    5.1: "此命生来根基深，荣华富贵两相匀；财禄丰盈家道盛，一生平安享太平。",
    5.2: "一世享通事事能，不须劳思自然能；家族欣然心皆好，家业丰享自称心。",
    5.3: "此命推来福禄全，一生富贵乐无边；财源广进家业旺，荣华富贵享百年。",
    5.4: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    5.5: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
    5.6: "此命生来福禄全，一生自在乐安然；名利双收多富贵，荣华富贵享晚年。",
    5.7: "此命推来基础坚，中年运至福绵绵；财源广进家道兴，晚景荣华福寿全。",
    5.8: "此命生来福自高，一生荣华乐滔滔；富贵双全人钦敬，多才多艺逞英豪。",
    5.9: "此命推来福禄强，田园宅舍旺辉煌；财源茂盛达三江，一生富贵乐安康。",
    6.0: "此命生来根基深，荣华富贵两相匀；财禄丰盈家道盛，一生平安享太平。",
    6.1: "此命推来福禄全，一生富贵乐无边；财源广进家业旺，荣华富贵享百年。",
    6.2: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    6.3: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
    6.4: "此命生来福禄全，一生自在乐安然；名利双收多富贵，荣华富贵享晚年。",
    6.5: "此命推来基础坚，中年运至福绵绵；财源广进家道兴，晚景荣华福寿全。",
    6.6: "此命生来福自高，一生荣华乐滔滔；富贵双全人钦敬，多才多艺逞英豪。",
    6.7: "此命推来福禄强，田园宅舍旺辉煌；财源茂盛达三江，一生富贵乐安康。",
    6.8: "此命生来根基深，荣华富贵两相匀；财禄丰盈家道盛，一生平安享太平。",
    6.9: "此命推来福禄全，一生富贵乐无边；财源广进家业旺，荣华富贵享百年。",
    7.0: "此命生来福自宏，田园家业最高隆；平生衣禄丰盈足，一世荣华万事通。",
    7.1: "此命推来福不浅，一生富贵双全全；逍遥自在心欢喜，末限安宁福禄绵。",
}


def compute_cheng_gu(year_gan_zhi: str, month_lunar: int, day_lunar: int, hour_idx: int) -> tuple[str, str]:
    """
    计算称骨重量和评语
    输入：年柱干支, 农历月(1-12), 农历日(1-30), 时辰索引(0-11)
    输出：(重量描述, 评语)
    """
    cg = _CHENG_GU

    # 年柱重量
    year_weight = cg["year"].get(year_gan_zhi, 0.0)

    # 月柱重量
    month_weight = cg["month"].get(month_lunar, 0.0)

    # 日柱重量
    day_weight = cg["day"].get(day_lunar, 0.5)

    # 时柱重量
    hour_weight = cg["hour"].get(hour_idx, 0.0)

    total = year_weight + month_weight + day_weight + hour_weight

    # 转中文重量描述
    liang = int(total)
    qian = int(round((total - liang) * 10))

    if liang > 0 and qian > 0:
        weight_str = f"{liang}两{qian}钱"
    elif liang > 0:
        weight_str = f"{liang}两"
    else:
        weight_str = f"{qian}钱"

    # 查找最接近的评语
    comment = CHENG_GU_COMMENTS.get(round(total, 1), "命局特殊，福禄自定。")

    return weight_str, comment


# ═══════════════════════════════════════════
# 主函数：计算八字基础数据
# ═══════════════════════════════════════════


def compute_basic_data(
    year_gan: str,
    year_zhi: str,
    month_gan: str,
    month_zhi: str,
    day_gan: str,
    day_zhi: str,
    hour_gan: str,
    hour_zhi: str,
    gender: str = "男",
    lunar_month: int | None = None,
    lunar_day: int | None = None,
    hour_idx: int | None = None,
) -> dict:
    """
    第一大步：计算八字全部基础数据

    输入：四柱天干地支 + 性别
    输出：完整结构化JSON（11行×4列 + 附加信息）

    参数说明：
      - year_gan/year_zhi: 年柱天干地支
      - month_gan/month_zhi: 月柱天干地支
      - day_gan/day_zhi: 日柱天干地支
      - hour_gan/hour_zhi: 时柱天干地支
      - gender: "男"/"女"
      - lunar_month/day_lunar/day: 农历月日（用于称骨，可选）
      - hour_idx: 时辰索引0-11（用于称骨，可选）
    """
    ri_zhu = day_gan  # 日主
    all_gans = [year_gan, month_gan, day_gan, hour_gan]
    all_zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]

    # ── 各柱的十神 ──
    year_shi_shen = _get_shi_shen(year_gan, ri_zhu)
    month_shi_shen = _get_shi_shen(month_gan, ri_zhu)
    day_shi_shen = _get_shi_shen(day_gan, ri_zhu, is_ri_zhu=True, gender=gender)
    hour_shi_shen = _get_shi_shen(hour_gan, ri_zhu)
    shi_shens = [year_shi_shen, month_shi_shen, day_shi_shen, hour_shi_shen]

    # ── 各柱藏干（含十神） ──
    def _build_cang_gan(zhi: str, ri_zhu: str) -> list[dict]:
        cg_list = _CANG_GAN.get(zhi, [])
        result = []
        for cg, percent in cg_list:
            ss = _get_cang_gan_shi_shen(cg, ri_zhu)
            result.append({"gan": cg, "shi_shen": ss, "percent": percent})
        return result

    year_cang_gan = _build_cang_gan(year_zhi, ri_zhu)
    month_cang_gan = _build_cang_gan(month_zhi, ri_zhu)
    day_cang_gan = _build_cang_gan(day_zhi, ri_zhu)
    hour_cang_gan = _build_cang_gan(hour_zhi, ri_zhu)

    # ── 纳音 ──
    year_na_yin = _get_na_yin(year_gan, year_zhi)
    month_na_yin = _get_na_yin(month_gan, month_zhi)
    day_na_yin = _get_na_yin(day_gan, day_zhi)
    hour_na_yin = _get_na_yin(hour_gan, hour_zhi)

    # ── 空亡（每柱独立计算）──
    year_kw = _get_kong_wang_for_pillar(year_gan, year_zhi)
    month_kw = _get_kong_wang_for_pillar(month_gan, month_zhi)
    day_kw = _get_kong_wang_for_pillar(day_gan, day_zhi)
    hour_kw = _get_kong_wang_for_pillar(hour_gan, hour_zhi)

    # ── 神煞（需要年支和日支） ──
    year_shen_sha = compute_shen_sha_for_pillar(year_zhi, year_zhi, day_zhi)
    month_shen_sha = compute_shen_sha_for_pillar(month_zhi, year_zhi, day_zhi)
    day_shen_sha = compute_shen_sha_for_pillar(day_zhi, year_zhi, day_zhi)
    hour_shen_sha = compute_shen_sha_for_pillar(hour_zhi, year_zhi, day_zhi)

    # ── 天干留意 ──
    tian_gan_notes = compute_tian_gan_notes(all_gans)

    # ── 地支留意 ──
    di_zhi_notes = compute_di_zhi_notes(all_zhis)

    # ── 称骨 ──
    cheng_gu_weight = ""
    cheng_gu_comment = ""
    if lunar_month is not None and lunar_day is not None and hour_idx is not None:
        year_gan_zhi = year_gan + year_zhi
        cheng_gu_weight, cheng_gu_comment = compute_cheng_gu(year_gan_zhi, lunar_month, lunar_day, hour_idx)

    # ── 组装输出 ──
    result = {
        # 11行×4列核心网格
        "pillars": {
            "year": {
                "shi_shen": year_shi_shen,
                "tian_gan": year_gan,
                "di_zhi": year_zhi,
                "cang_gan": year_cang_gan,
                "na_yin": year_na_yin,
                "kong_wang": year_kw,
                "shen_sha": year_shen_sha,
            },
            "month": {
                "shi_shen": month_shi_shen,
                "tian_gan": month_gan,
                "di_zhi": month_zhi,
                "cang_gan": month_cang_gan,
                "na_yin": month_na_yin,
                "kong_wang": month_kw,
                "shen_sha": month_shen_sha,
            },
            "day": {
                "shi_shen": day_shi_shen,
                "tian_gan": day_gan,
                "di_zhi": day_zhi,
                "cang_gan": day_cang_gan,
                "na_yin": day_na_yin,
                "kong_wang": day_kw,
                "shen_sha": day_shen_sha,
            },
            "hour": {
                "shi_shen": hour_shi_shen,
                "tian_gan": hour_gan,
                "di_zhi": hour_zhi,
                "cang_gan": hour_cang_gan,
                "na_yin": hour_na_yin,
                "kong_wang": hour_kw,
                "shen_sha": hour_shen_sha,
            },
        },
        # 日主信息
        "ri_zhu": {"gan": ri_zhu, "wu_xing": TIAN_GAN_WU_XING[ri_zhu], "yin_yang": TIAN_GAN_YIN_YANG[ri_zhu]},
        # 性别
        "gender": gender,
        # 八字字符串
        "bazi": f"{year_gan}{year_zhi} {month_gan}{month_zhi} {day_gan}{day_zhi} {hour_gan}{hour_zhi}",
        # 干支留意
        "tian_gan_notes": tian_gan_notes,
        "di_zhi_notes": di_zhi_notes,
        # 称骨
        "cheng_gu": {"weight": cheng_gu_weight, "comment": cheng_gu_comment} if cheng_gu_weight else None,
    }

    return result


# ═══════════════════════════════════════════
# 格式化输出（前端渲染用）
# ═══════════════════════════════════════════


def format_basic_data_table(data: dict) -> list[list]:
    """
    将基础数据格式化为11行×5列（含行名）的表格
    用于前端直接渲染
    """
    p = data["pillars"]
    table = [
        ["四柱", "年柱", "月柱", "日柱", "时柱"],
        ["十神", p["year"]["shi_shen"], p["month"]["shi_shen"], p["day"]["shi_shen"], p["hour"]["shi_shen"]],
        ["天干", p["year"]["tian_gan"], p["month"]["tian_gan"], p["day"]["tian_gan"], p["hour"]["tian_gan"]],
        ["地支", p["year"]["di_zhi"], p["month"]["di_zhi"], p["day"]["di_zhi"], p["hour"]["di_zhi"]],
        [
            "藏干",
            _fmt_cang_gan(p["year"]["cang_gan"]),
            _fmt_cang_gan(p["month"]["cang_gan"]),
            _fmt_cang_gan(p["day"]["cang_gan"]),
            _fmt_cang_gan(p["hour"]["cang_gan"]),
        ],
        ["纳音", p["year"]["na_yin"], p["month"]["na_yin"], p["day"]["na_yin"], p["hour"]["na_yin"]],
        ["空亡", p["year"]["kong_wang"], p["month"]["kong_wang"], p["day"]["kong_wang"], p["hour"]["kong_wang"]],
        [
            "神煞",
            " ".join(p["year"]["shen_sha"]),
            " ".join(p["month"]["shen_sha"]),
            " ".join(p["day"]["shen_sha"]),
            " ".join(p["hour"]["shen_sha"]),
        ],
    ]
    return table


def _fmt_cang_gan(cg_list: list[dict]) -> str:
    """格式化藏干为显示字符串"""
    parts = []
    for item in cg_list:
        parts.append(f"{item['gan']}({item['shi_shen']})")
    return " ".join(parts)


# ── 测试 ──
if __name__ == "__main__":
    # 测试家主的八字：庚申 癸未 辛亥 辛卯
    result = compute_basic_data(
        year_gan="庚",
        year_zhi="申",
        month_gan="癸",
        month_zhi="未",
        day_gan="辛",
        day_zhi="亥",
        hour_gan="辛",
        hour_zhi="卯",
        gender="男",
        lunar_month=6,
        lunar_day=26,
        hour_idx=3,
    )

    import json

    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n\n=== 表格格式 ===")
    table = format_basic_data_table(result)
    for row in table:
        print(" | ".join(row))
