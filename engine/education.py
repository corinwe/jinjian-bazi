"""
金鉴真人·学历学业分析引擎 v1.0

六步排查法（金鉴真人原始规则）:
  Step 1: 印星情况 — 原局印星+大运补印
  Step 2: 官杀影响 — 学业压力
  Step 3: 食伤情况 — 聪明程度
  Step 4: 文昌贵人 — 是否到位
  Step 5: 大运配合 — 关键运期
  Step 6: 综合判定

学校等级六档:
  👑 顶尖 — ≥5项✅+文昌月令+身强印格
  🥇 985   — 3-4项✅+文昌日/月+月令印强
  🥇 211   — 3项✅+文昌在局
  🥈 本科  — 2项✅+文昌大运补救
  🥉 专科  — 1-2项✅+文昌缺+食伤导向
  🪜 初中以下 — ≤1项✅+无印无文昌+财破印
"""

from __future__ import annotations

from shen_sha import get_wen_chang
from shi_shen import get_shi_shen_for_gan, is_tou_gan

# ── 文昌贵人表 ──
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
    学历分析完整体系

    返回: 学历等级+六步排查详细
    """
    # ── Step 1: 印星情况 ──
    has_yin = (
        is_tou_gan("", BaZi.__new__(BaZi), "正印") or is_tou_gan("", BaZi.__new__(BaZi), "偏印") if False else False
    )
    # 简化: 检查天干是否有正印/偏印
    yin_score = 0
    yin_detail = ""
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ["正印", "偏印"]:
            yin_score += 1
            yin_detail = f"天干{ss}透出"

    # 大运补印
    for dg in da_yun_gans[:3]:  # 前3步大运
        ss = get_shi_shen_for_gan(dg, ri_zhu)
        if ss in ["正印", "偏印"]:
            yin_score += 1
            yin_detail = f"大运{ss}补救"

    yin_result = "印星有力" if yin_score >= 2 else "大运补印" if yin_score == 1 else "印星弱"

    # ── Step 2: 官杀影响 ──
    guan_sha_count = 0
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ["正官", "七杀"]:
            guan_sha_count += 1

    guan_result = "压力大" if guan_sha_count >= 2 else "有压力" if guan_sha_count == 1 else "压力小"

    # ── Step 3: 食伤情况 ──
    shi_shang_count = 0
    for g in bazi_gans:
        ss = get_shi_shen_for_gan(g, ri_zhu)
        if ss in ["食神", "伤官"]:
            shi_shang_count += 1

    shang_result = "聪明" if shi_shang_count >= 1 else "中规中矩"
    if "伤官" in [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]:
        shang_result = "聪明有才华(伤官)"
    elif "食神" in [get_shi_shen_for_gan(g, ri_zhu) for g in bazi_gans]:
        shang_result = "聪明(食神)"

    # ── Step 4: 文昌贵人 ──
    wen_chang_zhi = get_wen_chang(ri_zhu)
    wen_chang_gans = [g for g in bazi_gans if get_wen_chang(g)]
    wen_chang_in_local = wen_chang_zhi in bazi_zhis if wen_chang_zhi else False
    wen_chang_in_da_yun = any(wen_chang_zhi == dz for dz in da_yun_zhis[:3]) if wen_chang_zhi else False

    wen_chang_result = "文昌在局" if wen_chang_in_local else "大运有文昌" if wen_chang_in_da_yun else "文昌缺"

    # ── Step 5: 大运配合 ──
    da_yun_edu_score = 0
    for dg, dz, sa in zip(da_yun_gans[:4], da_yun_zhis[:4], da_yun_start_ages[:4]):
        dg_ss = get_shi_shen_for_gan(dg, ri_zhu)
        if dg_ss in ["正印", "偏印"] and sa >= 6 and sa <= 30:
            da_yun_edu_score += 1
        if dg_ss in ["比肩", "劫财"] and sa >= 6 and sa <= 25:
            da_yun_edu_score += 1

    da_yun_result = "大运有利" if da_yun_edu_score >= 2 else "大运一般" if da_yun_edu_score == 1 else "大运不利"

    # ── Step 6: 综合判定 ──
    checks = 0
    if yin_score >= 1:
        checks += 1
    if guan_sha_count <= 1:
        checks += 1
    if shi_shang_count >= 1:
        checks += 1
    if wen_chang_in_local or wen_chang_in_da_yun:
        checks += 1
    if da_yun_edu_score >= 1:
        checks += 1

    # 学校等级
    if checks >= 5 and wen_chang_in_local and shen_label == "身强":
        school_level = "👑 顶尖"
    elif checks >= 3 and wen_chang_in_local:
        school_level = "🥇 985/211"
    elif checks >= 2 and wen_chang_in_da_yun:
        school_level = "🥇 211一本"
    elif checks >= 2:
        school_level = "🥈 普通本科"
    elif checks >= 1:
        school_level = "🥉 大专职校"
    else:
        school_level = "🪜 初中以下"

    # 学历层级
    if da_yun_edu_score >= 2:
        degree = "硕士及以上"
    elif da_yun_edu_score >= 1:
        degree = "本科"
    else:
        degree = "专科"

    return {
        "school_level": school_level,
        "degree": degree,
        "six_steps": {
            "印星": {"result": yin_result, "detail": yin_detail, "score": yin_score},
            "官杀": {"result": guan_result, "detail": f"官杀{guan_sha_count}个"},
            "食伤": {"result": shang_result},
            "文昌": {"result": wen_chang_result, "zhi": wen_chang_zhi or "无"},
            "大运配合": {"result": da_yun_result, "score": da_yun_edu_score},
        },
        "checks_passed": f"{checks}/5",
    }


if __name__ == "__main__":
    # 快速测试 - 需要构建BaZi对象
    pass
