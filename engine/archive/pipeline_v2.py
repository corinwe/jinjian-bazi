"""
金鉴真人·统一分析引擎 v2.0 — 全量规则集成

分析步骤（严格按照序）:
  Step 1: 排盘（四柱+大运）
  Step 2: 十神判定（天干+藏干）
  Step 3: 身强弱评分（金鉴真人原始规则）
  Step 4: 财星评分
  Step 5: 格局判定
  Step 6: 喜用神（含调候）
  Step 7: 五行能量分析
  Step 8: 地支关系（刑冲合害）
  Step 9: 神煞系统
  Step 10: 大运评估+排序
  Step 11: 流年分析
  Step 12: 8大维度评分
  Step 13: 结构化JSON输出
"""

from __future__ import annotations

from cai_xing import compute_cai_xing
from constants import TIAN_GAN_WU_XING, BaZi, Pillar
from da_yun import compute_da_yun, compute_da_yun_scores
from dimensions import DEFAULT_DIMENSIONS
from energy import compute_energy_profile
from ge_ju import determine_ge_ju, determine_xi_yong_shen, get_tiao_hou_yong_shen
from liu_nian import analyze_liu_nian, generate_liu_nian_years, get_liu_nian_gan_zhi
from shen_qiang_ruo import compute_shen_qiang_ruo
from shen_sha import compute_all_shen_sha
from shi_shen import get_all_cang_gan_shi_shen, get_shi_shen_all_dry
from xing_chong_he_hua import check_all_relations


def run_v2(
    bazi: BaZi,
    birth_year: int = 1980,
    birth_month_lunar: int = 1,
    qi_yun_days: float = 1.1,
    current_year: int | None = None,
) -> dict:
    """
    完整分析流水线 v2 — 全量规则
    """
    if current_year is None:
        import datetime

        current_year = datetime.datetime.now().year

    ri_zhu = bazi.ri_zhu
    all_gans = [bazi.year.gan, bazi.month.gan, bazi.day.gan, bazi.hour.gan]
    all_zhis = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]

    # ── Step 1: 基本信息 ──
    basic = {
        "bazi": bazi.summary(),
        "gender": bazi.gender,
        "ri_zhu": {"gan": ri_zhu, "wu_xing": TIAN_GAN_WU_XING[ri_zhu]},
    }

    # ── Step 2: 十神 ──
    shi_shen = {"tian_gan": get_shi_shen_all_dry(bazi), "cang_gan": get_all_cang_gan_shi_shen(bazi)}

    # ── Step 3: 身强弱 ──
    sqr_score, sqr_label, sqr_detail = compute_shen_qiang_ruo(bazi)
    shen_qiang_ruo = {
        "score": sqr_score,
        "label": sqr_label,
        "details": {
            "yue_ling_yin": sqr_detail.yue_ling_yin,
            "yue_ling_bi_jie": sqr_detail.yue_ling_bi_jie,
            "tian_gan_bi_jie": sqr_detail.tian_gan_bi_jie,
            "ri_zhi_yin_bi": sqr_detail.ri_zhi_yin_bi,
            "nian_shi_zhi_yin_bi": sqr_detail.nian_shi_zhi_yin_bi,
            "total": sqr_detail.total,
        },
    }

    # ── Step 4: 财星 ──
    cai = compute_cai_xing(bazi)
    cai_xing = {
        "total": cai.total,
        "details": {
            "nian_zhi": cai.nian_zhi_score,
            "yue_ling": cai.yue_ling_score,
            "ri_zhi": cai.ri_zhi_score,
            "shi_gan": cai.shi_gan_score,
            "shi_zhi": cai.shi_zhi_score,
        },
    }

    # ── Step 5: 格局 ──
    main_ge, detail_ge = determine_ge_ju(bazi)
    ge_ju = {"main": main_ge, "detail": detail_ge}

    # ── Step 6: 喜用神 ──
    xi, ji = determine_xi_yong_shen(bazi)
    th = get_tiao_hou_yong_shen(ri_zhu, birth_month_lunar)
    xi_yong_shen = {"xi": xi, "ji": ji, "tiao_hou": th}

    # ── Step 7: 五行能量 ──
    energy = compute_energy_profile(bazi)

    # ── Step 8: 地支关系 ──
    di_zhi_guan_xi = check_all_relations(all_zhis)

    # ── Step 9: 神煞 ──
    shen_sha = compute_all_shen_sha(all_gans, all_zhis, bazi.year.zhi, bazi.month.zhi, ri_zhu)

    # ── Step 10: 大运 ──
    dy_list, qy_age, qy_year = compute_da_yun(bazi, birth_year, qi_yun_days)
    dy_scores = compute_da_yun_scores(bazi, dy_list)

    best_idx = max(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1
    worst_idx = min(range(len(dy_scores)), key=lambda i: dy_scores[i][1]) if dy_scores else -1

    da_yun = {
        "qi_yun_age": round(qy_age, 1),
        "qi_yun_year": qy_year,
        "list": [
            {
                "gan_zhi": dy.gan_zhi,
                "start_age": dy.start_age,
                "end_age": dy.end_age,
                "start_year": dy.start_year,
                "score": dy_scores[i][1],
            }
            for i, dy in enumerate(dy_list)
        ],
        "best_index": best_idx,
        "worst_index": worst_idx,
    }

    # ── Step 11: 流年 ──
    current_da_yun = None
    for i, dy in enumerate(dy_list):
        if dy.start_year <= current_year < dy.start_year + 10:
            current_da_yun = (i, dy)
            break

    liu_nian_list = []
    for year in generate_liu_nian_years(birth_year, current_year, 10):
        lg, lz = get_liu_nian_gan_zhi(year)
        dy_gan = current_da_yun[1].gan if current_da_yun else ""
        dy_zhi = current_da_yun[1].zhi if current_da_yun else ""
        ln = analyze_liu_nian(lg, lz, ri_zhu, TIAN_GAN_WU_XING[ri_zhu], bazi.year.zhi, dy_gan, dy_zhi, all_zhis)
        ln["year"] = year
        liu_nian_list.append(ln)

    # ── Step 12: 8大维度 ──
    dimensions = {
        name: {"base": ds.base, "da_yun_bonus": ds.da_yun_bonus, "total": ds.total}
        for name, ds in DEFAULT_DIMENSIONS(bazi).items()
    }

    # ── 聚合输出 ──
    result = {
        "version": "2.0",
        "engine": "金鉴真人·统一分析引擎 v2.0",
        "basic": basic,
        "shi_shen": shi_shen,
        "shen_qiang_ruo": shen_qiang_ruo,
        "cai_xing": cai_xing,
        "ge_ju": ge_ju,
        "xi_yong_shen": xi_yong_shen,
        "energy": {
            "wu_xing": energy["wu_xing_energy"],
            "relation": energy["relation_energy"]["details"]["summary"],
            "strongest": energy["strongest_wx"],
            "weakest": energy["weakest_wx"],
        },
        "di_zhi_guan_xi": {
            "summary": di_zhi_guan_xi["summary"],
            "chong": di_zhi_guan_xi["冲"],
            "xing": [x["type"] for x in di_zhi_guan_xi["刑"]],
            "hai": di_zhi_guan_xi["害"],
            "liu_he": di_zhi_guan_xi["六合"],
            "san_he": [s["type"] for s in di_zhi_guan_xi["三合"]],
            "ban_he": [s["type"] for s in di_zhi_guan_xi["半合"]],
        },
        "shen_sha": shen_sha.to_dict(),
        "da_yun": da_yun,
        "liu_nian": liu_nian_list,
        "dimensions": dimensions,
    }

    return result


def format_report_text(result: dict) -> str:
    """生成可读报告文本（供LLM润色用）"""
    lines = []
    b = result["basic"]
    lines.append(f"八字: {b['bazi']}")
    lines.append(f"日主: {b['ri_zhu']['gan']}({b['ri_zhu']['wu_xing']})")

    s = result["shen_qiang_ruo"]
    lines.append(f"身强弱: {s['score']}分 → {s['label']}")

    c = result["cai_xing"]
    lines.append(f"财星: {c['total']}分")

    g = result["ge_ju"]
    lines.append(f"格局: {g['detail']}")

    x = result["xi_yong_shen"]
    lines.append(f"喜用: {x['xi']} 忌神: {x['ji']}")

    e = result["energy"]
    lines.append(f"五行能量: {e['wu_xing']}")
    lines.append(f"地支关系: {e['relation']}")

    ss = result["shen_sha"]
    lines.append(f"神煞: {ss['summary']}")

    dy = result["da_yun"]
    best = dy["list"][dy["best_index"]] if dy["best_index"] >= 0 else None
    worst = dy["list"][dy["worst_index"]] if dy["worst_index"] >= 0 else None
    if best:
        lines.append(f"最佳大运: {best['gan_zhi']}({best['start_age']}~{best['end_age']}岁) {best['score']}/10")
    if worst:
        lines.append(f"最差大运: {worst['gan_zhi']}({worst['start_age']}~{worst['end_age']}岁) {worst['score']}/10")

    dims = result["dimensions"]
    lines.append("维度评分:")
    for name, ds in sorted(dims.items()):
        lines.append(f"  {name}: {ds['total']}/10")

    return "\n".join(lines)


if __name__ == "__main__":
    from constants import BaZi, Pillar

    test_cases = [
        ("家主", "甲", "午", "己", "巳", "戊", "午", "壬", "子", "男", 1968, 4),
        ("子源", "庚", "申", "辛", "巳", "甲", "午", "丙", "寅", "男", 1980, 4),
        ("主母", "戊", "午", "甲", "子", "庚", "戌", "丁", "亥", "女", 1976, 11),
    ]

    for name, yg, yz, mg, mz, dg, dz, hg, hz, gn, by, bm in test_cases:
        bazi = BaZi(year=Pillar(yg, yz), month=Pillar(mg, mz), day=Pillar(dg, dz), hour=Pillar(hg, hz), gender=gn)
        result = run_v2(bazi, by, bm)
        print(f"\n{'=' * 50}")
        print(f"【{name}】{bazi.summary()}")
        print(f"{'=' * 50}")
        print(format_report_text(result))
        print("流年(近3年):")
        for ln in result["liu_nian"][:3]:
            print(
                f"  {ln['year']} {ln['流年']}: {ln['流年十神']} 评分{ln['综合评分']}/10 {'⚠️' + ln['犯太岁']['类型'] if ln['犯太岁'] else ''}"
            )
