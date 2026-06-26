"""
金鉴真人·八字规则引擎 v0.1 — 主流水线
"""

from __future__ import annotations
import json
import sys
from typing import Optional
from datetime import datetime

from constants import (
    BaZi, Pillar, ReportResult, DaYun,
    TIAN_GAN_WU_XING, DI_ZHI_WU_XING, NA_YIN,
)
from shi_shen import (
    get_shi_shen_all_dry, get_all_cang_gan_shi_shen, is_tou_gan,
)
from shen_qiang_ruo import compute_shen_qiang_ruo, explain_score
from cai_xing import compute_cai_xing, cai_xing_explain
from ge_ju import (
    determine_ge_ju, determine_xi_yong_shen, get_tiao_hou_yong_shen,
)
from da_yun import compute_da_yun, compute_da_yun_scores
from dimensions import DEFAULT_DIMENSIONS


def parse_gan_zhi(gan_str: str, zhi_str: str) -> Pillar:
    """解析一柱"""
    return Pillar(gan=gan_str, zhi=zhi_str)


def run_pipeline(bazi: BaZi, birth_year: int = 1980,
                 birth_month_lunar: int = 1,
                 qi_yun_days: float = 1.1) -> dict:
    """
    执行完整流水线
    
    参数:
      bazi: 八字对象
      birth_year: 出生年份（用于大运计算）
      birth_month_lunar: 农历出生月份（用于调候用神）
      qi_yun_days: 距离节气的天数（简化）
    
    返回:
      完整JSON字典
    """
    # ── 1. 基本信息 ──
    bazi_str = bazi.summary()
    
    # 纳音
    na_yin_list = []
    for p in [bazi.year, bazi.month, bazi.day, bazi.hour]:
        key = f"{p.gan}{p.zhi}"
        # 找到对应纳音
        for k, v in NA_YIN.items():
            if key in k:
                na_yin_list.append(v)
                break
        else:
            na_yin_list.append("")
    
    # ── 十神 ──
    shi_shen_dry = get_shi_shen_all_dry(bazi)
    shi_shen_cang = get_all_cang_gan_shi_shen(bazi)
    
    # ── 身强弱 ──
    shen_score, shen_label, shen_detail = compute_shen_qiang_ruo(bazi)
    
    # ── 财星 ──
    cai_detail = compute_cai_xing(bazi)
    
    # ── 格局 ──
    main_ge, detail_ge = determine_ge_ju(bazi)
    
    # ── 喜用神 ──
    xi_yong, ji_shen = determine_xi_yong_shen(bazi)
    tiao_hou = get_tiao_hou_yong_shen(bazi.ri_zhu, birth_month_lunar)
    
    # ── 大运 ──
    da_yun_list, qi_yun_age, qi_yun_year = compute_da_yun(bazi, birth_year, qi_yun_days)
    da_yun_scores = compute_da_yun_scores(bazi, da_yun_list)
    
    # 最佳/最差大运
    best_idx = max(range(len(da_yun_scores)), key=lambda i: da_yun_scores[i][1]) if da_yun_scores else -1
    worst_idx = min(range(len(da_yun_scores)), key=lambda i: da_yun_scores[i][1]) if da_yun_scores else -1
    
    # ── 8大维度 ──
    dimensions = DEFAULT_DIMENSIONS(bazi)
    
    # ── 构建输出 ──
    result = {
        "meta": {
            "engine": "金鉴真人·八字规则引擎",
            "version": "0.1",
            "generated_at": datetime.now().isoformat(),
            "rules": "金鉴真人原始规则体系",
        },
        "basic": {
            "bazi": bazi_str,
            "gender": bazi.gender,
            "na_yin": na_yin_list,
            "ri_zhu": {
                "gan": bazi.ri_zhu,
                "wu_xing": TIAN_GAN_WU_XING[bazi.ri_zhu],
                "yin_yang": "阳" if ["甲","丙","戊","庚","壬"].count(bazi.ri_zhu) else "阴",
            },
        },
        "shi_shen": {
            "tian_gan": [
                {"position": s["position"], "gan": s["gan"], "shi_shen": s["shi_shen"]}
                for s in shi_shen_dry
            ],
            "cang_gan": [
                {"position": s["position"], "zhi": s["zhi"], 
                 "cang_gan": s["cang_gan"], "shi_shen": s["shi_shen"]}
                for s in shi_shen_cang
            ],
        },
        "shen_qiang_ruo": {
            "score": shen_score,
            "label": shen_label,
            "details": {
                "yue_ling_yin": shen_detail.yue_ling_yin,
                "yue_ling_bi_jie": shen_detail.yue_ling_bi_jie,
                "tian_gan_yin": shen_detail.tian_gan_yin,
                "tian_gan_bi_jie": shen_detail.tian_gan_bi_jie,
                "ri_zhi_yin_bi": shen_detail.ri_zhi_yin_bi,
                "nian_shi_zhi_yin_bi": shen_detail.nian_shi_zhi_yin_bi,
                "total": shen_detail.total,
            },
        },
        "cai_xing": {
            "total_score": cai_detail.total,
            "details": {
                "nian_zhi": cai_detail.nian_zhi_score,
                "yue_ling": cai_detail.yue_ling_score,
                "ri_zhi": cai_detail.ri_zhi_score,
                "shi_gan": cai_detail.shi_gan_score,
                "shi_zhi": cai_detail.shi_zhi_score,
                "yue_ling_ben_qi_is_cai": cai_detail.is_yue_ling_ben_qi_cai,
            },
        },
        "ge_ju": {
            "main": main_ge,
            "detail": detail_ge,
        },
        "xi_yong_shen": {
            "xi_yong_wu_xing": xi_yong,
            "ji_shen_wu_xing": ji_shen,
            "tiao_hou_yong_shen": tiao_hou,
        },
        "da_yun": {
            "qi_yun_age": round(qi_yun_age, 1),
            "qi_yun_year": qi_yun_year,
            "list": [
                {
                    "gan_zhi": dy.gan_zhi,
                    "start_age": dy.start_age,
                    "end_age": dy.end_age,
                    "start_year": dy.start_year,
                    "score": da_yun_scores[i][1] if i < len(da_yun_scores) else 5.0,
                }
                for i, dy in enumerate(da_yun_list)
            ],
            "best_index": best_idx,
            "worst_index": worst_idx,
        },
        "dimensions": {
            dim_name: {
                "base": ds.base,
                "da_yun_bonus": ds.da_yun_bonus,
                "total": ds.total,
            }
            for dim_name, ds in dimensions.items()
        },
    }
    
    return result


def run_pipeline_from_stems(
    year_gan: str, year_zhi: str,
    month_gan: str, month_zhi: str,
    day_gan: str, day_zhi: str,
    hour_gan: str, hour_zhi: str,
    gender: str,
    birth_year: int = 1980,
    birth_month_lunar: int = 1,
    qi_yun_days: float = 1.1,
) -> dict:
    """从天干地支字符串运行流水线"""
    bazi = BaZi(
        year=Pillar(year_gan, year_zhi),
        month=Pillar(month_gan, month_zhi),
        day=Pillar(day_gan, day_zhi),
        hour=Pillar(hour_gan, hour_zhi),
        gender=gender,
    )
    return run_pipeline(bazi, birth_year, birth_month_lunar, qi_yun_days)


def print_report(result: dict):
    """打印可读报告"""
    print("=" * 60)
    print(f"金鉴真人·八字规则引擎 v0.1")
    print("=" * 60)
    
    b = result["basic"]
    print(f"\n📋 八字: {b['bazi']}")
    print(f"👤 性别: {b['gender']}")
    print(f"🎵 纳音: {', '.join(b['na_yin'])}")
    print(f"☀️ 日主: {b['ri_zhu']['gan']}（{b['ri_zhu']['wu_xing']}·{b['ri_zhu']['yin_yang']}）")
    
    s = result["shen_qiang_ruo"]
    print(f"\n💪 身强弱: {s['score']}分 → {s['label']}")
    
    c = result["cai_xing"]
    print(f"💰 财星: {c['total_score']}分（月令本气为财: {'是' if c['details']['yue_ling_ben_qi_is_cai'] else '否'}）")
    
    g = result["ge_ju"]
    print(f"🏛️  格局: {g['detail']}")
    
    x = result["xi_yong_shen"]
    print(f"🟢 喜用神: {x['xi_yong_wu_xing']}")
    print(f"🔴 忌神: {x['ji_shen_wu_xing']}")
    if x["tiao_hou_yong_shen"]:
        print(f"🌡️  调候用神: {x['tiao_hou_yong_shen']}")
    
    dy = result["da_yun"]
    qy_age_val = dy['qi_yun_age']
    qy_year_val = dy['qi_yun_year']
    print(f"\n🚀 大运（{qy_age_val}岁起运·{qy_year_val}年起）:")
    for d in dy["list"]:
        star = "🏆" if d["score"] >= 8 else "✅" if d["score"] >= 6 else "⚠️" if d["score"] >= 4 else "❌"
        print(f"  {star} {d['gan_zhi']} ({d['start_age']}~{d['end_age']}岁, {d['start_year']}年起) — {d['score']}/10")
    
    print(f"\n📊 8大维度评分:")
    for dim_name, ds in result["dimensions"].items():
        bar = "█" * int(ds["total"]) + "░" * (10 - int(ds["total"]))
        print(f"  {dim_name}: {bar} {ds['total']}/10（原局{ds['base']}+大运{ds['da_yun_bonus']}）")


def save_json(result: dict, path: str):
    """输出JSON文件"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 测试
    test_cases = [
        ("家主·魏启令", "甲", "午", "己", "巳", "戊", "午", "壬", "子", "男", 1968, 4),
        ("主母·成", "戊", "午", "甲", "子", "庚", "戌", "丁", "亥", "女", 1976, 11),
        ("子源", "庚", "申", "辛", "巳", "甲", "午", "丙", "寅", "男", 1980, 4),
        ("父亲·魏肇君", "己", "丑", "癸", "酉", "癸", "亥", "戊", "午", "男", 1949, 7),
        ("凤", "戊", "午", "甲", "子", "庚", "戌", "丁", "亥", "女", 1980, 11),
    ]
    
    for name, yg, yz, mg, mz, dg, dz, hg, hz, gender, byear, blunar in test_cases:
        result = run_pipeline_from_stems(
            yg, yz, mg, mz, dg, dz, hg, hz, gender, byear, blunar
        )
        print_report(result)
        
        # 保存JSON
        filename = f"/root/bazi-engine/output/{name.replace('·', '_')}.json"
        import os
        os.makedirs("/root/bazi-engine/output", exist_ok=True)
        save_json(result, filename)
        print(f"\n💾 已保存: {filename}")
        print()
