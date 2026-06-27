"""引擎输出 → 报告生成器 数据适配层"""
import logging

logger = logging.getLogger(__name__)


def adapt_engine_to_report(bazi_result: dict, name: str, gender: str) -> dict:
    """将bazi_engine的输出转换为report_generator期望的格式"""
    basic = bazi_result.get("basic", {})
    analysis = bazi_result.get("analysis", {})

    # ─── 基本数据 ──────────────────────────────────
    ri_gan = basic.get("ri_gan", "")
    ri_zhi_str = basic.get("ri_zhi", "")

    # 五行映射
    wx_map = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
              "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

    # 阴阳映射
    yy_map = {"甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
              "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴"}

    pillars_raw = basic.get("pillars", {})
    pillars = {}
    for key, p in pillars_raw.items():
        cang_gan_data = p.get("cang_gan", [])
        pillars[key] = {
            "gan": p.get("gan", ""),
            "zhi": p.get("zhi", ""),
            "shi_shen": p.get("gan_shi_shen", ""),
            "gan_shi_shen": p.get("gan_shi_shen", ""),
            "gan_wu_xing": p.get("gan_wu_xing", ""),
            "zhi_wu_xing": p.get("zhi_wu_xing", ""),
            "na_yin": p.get("na_yin", ""),
            "kong_wang": " ".join(p.get("kong_wang", [])),
            "cang_gan": cang_gan_data,
            "cang_gan_objects": cang_gan_data,
        }

    # ─── 身强弱 ──────────────────────────────────
    sqr = analysis.get("shen_qiang_ruo", {})
    sqr_level = sqr.get("level", "中和")
    adapted_sqr = {
        "score": sqr.get("score", 0),
        "label": sqr_level,
        "level": sqr_level,
        "details": {"detail_analysis": "; ".join(sqr.get("details", []))},
        "narrative": f"命主{sqr_level}（{sqr.get('score', 0)}分）。",
    }

    # ─── 格局 ──────────────────────────────────
    ge_ju_str = analysis.get("ge_ju", "正印")
    adapted_gj = {
        "main": ge_ju_str,
        "detail": ge_ju_str,
        "shi_shen": [],
        "narrative": f"命局核心格局为{ge_ju_str}格。",
    }

    # ─── 喜用神 ──────────────────────────────────
    xys = analysis.get("xi_yong_shen", {})
    adapted_xys = {
        "xi": xys.get("xi_shen", []),
        "xi_shen": xys.get("xi_shen", []),
        "ji": xys.get("ji_shen", []),
        "ji_shen": xys.get("ji_shen", []),
        "yong_shen": xys.get("yong_shen", xys.get("xi_shen", [])),
        "tiao_hou": [],
        "narrative": f"喜用神为{'/'.join(xys.get('xi_shen', []))}；忌神为{'/'.join(xys.get('ji_shen', []))}。",
    }

    # ─── 财星 ──────────────────────────────────
    cx = analysis.get("cai_xing", {})
    adapted_cx = {
        "total": cx.get("score", 0),
        "cai_xing_total": cx.get("score", 0),
        "has_ku": cx.get("has_ku", False),
        "cai_ku": cx.get("cai_ku", {}),
        "wealth_level": cx.get("wealth_level", "小富"),
        "narrative": f"财星总评{cx.get('score', 0)}分，属{cx.get('wealth_level', '小富')}层次。",
    }

    # ─── 大运 ──────────────────────────────────
    dy = analysis.get("da_yun", {})
    da_yun_list = dy.get("da_yun", [])
    adapted_dy_list = []
    for i, yun in enumerate(da_yun_list):
        sa = yun.get("start_age", 0)
        ea = yun.get("end_age", 10)
        adapted_dy_list.append({
            "gan_zhi": yun.get("gan_zhi", ""),
            "start_age": int(sa),
            "end_age": int(ea),
            "start_year": 2024 - int((sa + ea) / 2),
            "end_year": 2024 + int((ea - sa) / 2),
            "score": 5,
            "gan_ss": "",
        })

    adapted_dy = {"list": adapted_dy_list, "qi_yun_age": dy.get("qi_yun_age", 0)}

    # ─── 五行能量（从四柱藏干计算）──────────────────
    wx_map_inv = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
    cang_gan_weight = {"子":[("癸",100)],"丑":[("己",100),("癸",60),("辛",30)],
        "寅":[("甲",100),("丙",60),("戊",30)],"卯":[("乙",100)],
        "辰":[("戊",100),("乙",60),("癸",30)],"巳":[("丙",100),("戊",60),("庚",30)],
        "午":[("丁",100),("己",60)],"未":[("己",100),("丁",60),("乙",30)],
        "申":[("庚",100),("壬",60),("戊",30)],"酉":[("辛",100)],
        "戌":[("戊",100),("辛",60),("丁",30)],"亥":[("壬",100),("甲",60)]}
    wx_energy = {"木":0.0,"火":0.0,"土":0.0,"金":0.0,"水":0.0}
    # 天干贡献（每干1分）
    for g in [basic.get("nian_gan",""),basic.get("yue_gan",""),basic.get("ri_gan",""),basic.get("shi_gan","")]:
        if g in wx_map_inv:
            wx_energy[wx_map_inv[g]] += 1.0
    # 地支藏干贡献（按权重比例）
    for z in [basic.get("nian_zhi",""),basic.get("yue_zhi",""),basic.get("ri_zhi",""),basic.get("shi_zhi","")]:
        for cg, w in cang_gan_weight.get(z, []):
            if cg in wx_map_inv:
                wx_energy[wx_map_inv[cg]] += w / 100.0
    # 计算百分比
    total = sum(wx_energy.values())
    pct = {}
    for k, v in wx_energy.items():
        pct[k] = round(v / total * 100, 1) if total > 0 else 0.0
    sorted_wx = sorted(wx_energy.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_wx[0][0] if sorted_wx else ""
    weakest = sorted_wx[-1][0] if sorted_wx else ""
    adapted_energy = {
        "wu_xing": {k: f"{v}%" for k, v in pct.items()},
        "wu_xing_energy": {k: v for k, v in pct.items()},
        "strongest_wx": strongest,
        "weakest_wx": weakest,
    }

    # ─── 维度评分 ──────────────────────────────────
    dimensions = analysis.get("dimensions", {})
    if not dimensions:
        dimensions = {
            "财富根基": {"score": min(10, adapted_cx["total"] / 3), "narrative": ""},
            "事业发展": {"score": 5, "narrative": ""},
            "婚姻感情": {"score": 5, "narrative": ""},
            "学业学历": {"score": 5, "narrative": ""},
            "子女运势": {"score": 5, "narrative": ""},
            "健康体质": {"score": 5, "narrative": ""},
            "人际贵人": {"score": 5, "narrative": ""},
            "综合家运": {"score": 5, "narrative": ""},
        }

    # ─── 组装 ──────────────────────────────────
    result = {
        "basic": {
            "bazi": basic.get("ba_zi", ""),
            "ba_zi": basic.get("ba_zi", ""),
            "ri_zhu": ri_gan + ri_zhi_str,
            "ri_gan": ri_gan,
            "ri_zhi": ri_zhi_str,
            "nian_gan": basic.get("nian_gan", ""),
            "nian_zhi": basic.get("nian_zhi", ""),
            "yue_gan": basic.get("yue_gan", ""),
            "yue_zhi": basic.get("yue_zhi", ""),
            "shi_gan": basic.get("shi_gan", ""),
            "shi_zhi": basic.get("shi_zhi", ""),
            "gender": gender,
            "solar_date": basic.get("solar_date", ""),
            "pillars": pillars,
            "ri_zhu_obj": {"gan": ri_gan, "wu_xing": wx_map.get(ri_gan, "")},
            "birth_info": {
                "name": name,
                "gender": gender,
                "solar_date": basic.get("solar_date", ""),
            },
        },
        "analysis": {
            "shen_qiang_ruo": adapted_sqr,
            "ge_ju": ge_ju_str,
            "xi_yong_shen": adapted_xys,
            "cai_xing": adapted_cx,
            "energy": adapted_energy,
            "da_yun": adapted_dy,
            "dimensions": dimensions,
        },
    }

    return result
