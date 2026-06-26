"""
金鉴真人·产品级主流水线 v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入：公历出生日期 + 性别 + 姓名
输出：完整的结构化八字分析JSON（零LLM，全部代码计算）

管线步骤：
  Step 1: 排盘 (bazi-engine.py)
  Step 2: 11行×4列基础数据 (step1_basic.py)
  Step 3: 规则引擎分析（身强弱/财星/格局/大运/能量/8维度/流年）
  Step 4: 组装完整输出JSON
"""

from __future__ import annotations
import json, os, subprocess, sys, datetime
from typing import Optional

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ENGINE_DIR)

from step1_basic import compute_basic_data, format_basic_data_table

# ── 导入规则引擎模块 ──
from constants import BaZi, Pillar
from shen_qiang_ruo import compute_shen_qiang_ruo
from cai_xing import compute_cai_xing
from ge_ju import determine_ge_ju, determine_xi_yong_shen, get_tiao_hou_yong_shen
from da_yun import compute_da_yun, compute_da_yun_scores
from energy import compute_energy_profile
from dimensions import DEFAULT_DIMENSIONS
from xing_chong_he_hua import check_all_relations
from liu_nian import analyze_liu_nian, get_liu_nian_gan_zhi


# ── 排盘 ──
BAZI_ENGINE = "/root/weiwuji-knowledge-base/07-国学哲学/八字命格/scripts/bazi-engine.py"
if not os.path.exists(BAZI_ENGINE):
    for p in ["/root/.hermes/profiles/jinjian-zhenren/scripts/bazi-engine.py"]:
        if os.path.exists(p): BAZI_ENGINE = p; break

SHI_CHEN_INDICES = {h: h//2 for h in range(24)}
SHI_CHEN_NAMES = {0:"子时",1:"丑时",2:"寅时",3:"卯时",4:"辰时",5:"巳时",
                  6:"午时",7:"未时",8:"申时",9:"酉时",10:"戌时",11:"亥时"}


def run_paipan(name: str, gender: str, year: int, month: int, day: int,
               hour: int, minute: int = 0) -> dict:
    """Step 1: 排盘"""
    if not os.path.exists(BAZI_ENGINE):
        return {"success": False, "error": f"引擎不存在: {BAZI_ENGINE}"}
    
    hour_idx = SHI_CHEN_INDICES.get(hour, 0)
    cmd = ["python3", BAZI_ENGINE, str(year), str(month), str(day),
           str(hour), str(minute), str(hour_idx), gender, name, "", "--json"]
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return {"success": False, "error": r.stderr[:300]}
        data = json.loads(r.stdout)
        p = data["四柱"]
        ri_zhu_raw = data.get("日主", "")
        ri_zhu = ri_zhu_raw["gan"] if isinstance(ri_zhu_raw, dict) else ri_zhu_raw
        return {
            "success": True,
            "year_gan": p["年柱"][0], "year_zhi": p["年柱"][1],
            "month_gan": p["月柱"][0], "month_zhi": p["月柱"][1],
            "day_gan": p["日柱"][0], "day_zhi": p["日柱"][1],
            "hour_gan": p["时柱"][0], "hour_zhi": p["时柱"][1],
            "bazi": data.get("八字", ""), "ri_zhu": ri_zhu,
            "hour_idx": hour_idx, "shi_chen": SHI_CHEN_NAMES.get(hour_idx, ""),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def full_analysis(name: str, gender: str,
                  year: int, month: int, day: int,
                  hour: int, minute: int = 0,
                  lunar_month: Optional[int] = None,
                  lunar_day: Optional[int] = None,
                  current_year: Optional[int] = None) -> dict:
    """
    完整分析管线（Step 1→2→3→4）
    全部代码计算，零LLM
    """
    if current_year is None:
        current_year = datetime.datetime.now().year
    
    result = {
        "version": "1.0",
        "engine": "金鉴真人·确定性规则引擎",
        "name": name, "gender": gender,
        "birth": f"{year}年{month}月{day}日 {hour}:{minute:02d}",
    }
    
    # ═══ Step 1: 排盘 ═══
    paipan = run_paipan(name, gender, year, month, day, hour, minute)
    if not paipan.get("success"):
        result["error"] = f"排盘失败: {paipan.get('error', '')}"
        return result
    
    result["paipan"] = {
        "bazi": paipan["bazi"],
        "shi_chen": paipan["shi_chen"],
        "ri_zhu": paipan["ri_zhu"],
    }
    
    # ═══ Step 2: 11行×4列基础数据 ═══
    basic = compute_basic_data(
        year_gan=paipan["year_gan"], year_zhi=paipan["year_zhi"],
        month_gan=paipan["month_gan"], month_zhi=paipan["month_zhi"],
        day_gan=paipan["day_gan"], day_zhi=paipan["day_zhi"],
        hour_gan=paipan["hour_gan"], hour_zhi=paipan["hour_zhi"],
        gender=gender,
        lunar_month=lunar_month, lunar_day=lunar_day,
        hour_idx=paipan.get("hour_idx"),
    )
    result["basic_data"] = basic
    result["table"] = format_basic_data_table(basic)
    
    # ═══ Step 3: 规则引擎分析（全代码） ═══
    
    # 构建BaZi对象供引擎模块使用
    bazi = BaZi(
        year=Pillar(paipan["year_gan"], paipan["year_zhi"]),
        month=Pillar(paipan["month_gan"], paipan["month_zhi"]),
        day=Pillar(paipan["day_gan"], paipan["day_zhi"]),
        hour=Pillar(paipan["hour_gan"], paipan["hour_zhi"]),
        gender=gender,
    )
    
    analysis = {}
    
    # ① 身强弱评分
    sqr_score, sqr_label, sqr_details = compute_shen_qiang_ruo(bazi)
    analysis["shen_qiang_ruo"] = {
        "score": sqr_score,
        "label": sqr_label,
        "details": {
            "yue_ling_yin": sqr_details.yue_ling_yin,
            "yue_ling_bi_jie": sqr_details.yue_ling_bi_jie,
            "tian_gan_bi_jie": sqr_details.tian_gan_bi_jie,
            "ri_zhi_yin_bi": sqr_details.ri_zhi_yin_bi,
            "nian_shi_zhi_yin_bi": sqr_details.nian_shi_zhi_yin_bi,
            "total": sqr_details.total,
        }
    }
    
    # ② 财星评分
    cai_detail = compute_cai_xing(bazi)
    analysis["cai_xing"] = {
        "total": cai_detail.total,
        "details": {
            "nian_zhi": cai_detail.nian_zhi_score,
            "yue_ling": cai_detail.yue_ling_score,
            "ri_zhi": cai_detail.ri_zhi_score,
            "shi_gan": cai_detail.shi_gan_score,
            "shi_zhi": cai_detail.shi_zhi_score,
        },
        "is_yue_ling_ben_qi_cai": cai_detail.is_yue_ling_ben_qi_cai,
    }
    
    # ③ 格局
    ge_ju_main, ge_ju_desc = determine_ge_ju(bazi)
    analysis["ge_ju"] = {"main": ge_ju_main, "desc": ge_ju_desc}
    
    # ④ 喜用神
    xi, ji = determine_xi_yong_shen(bazi)
    tiao_hou = get_tiao_hou_yong_shen(bazi.ri_zhu, month)
    analysis["xi_yong_shen"] = {
        "xi": xi, "ji": ji,
        "tiao_hou": tiao_hou,
    }
    
    # ⑤ 五行能量
    energy = compute_energy_profile(bazi)
    analysis["energy"] = energy
    
    # ⑥ 大运
    da_yun_list, qi_yun_age, qi_yun_year = compute_da_yun(bazi, year)
    analysis["da_yun"] = {
        "qi_yun_age": round(qi_yun_age, 2),
        "list": []
    }
    for dy in da_yun_list:
        end_year = dy.start_year + 9
        analysis["da_yun"]["list"].append({
            "gan_zhi": dy.gan + dy.zhi,
            "start_year": dy.start_year,
            "end_year": end_year,
        })
    
    # 大运排序
    dy_scores = compute_da_yun_scores(bazi, da_yun_list)
    if dy_scores:
        dy_sorted = sorted(dy_scores, key=lambda x: x[1], reverse=True)
        analysis["da_yun"]["best"] = {"gan_zhi": dy_sorted[0][0], "score": round(dy_sorted[0][1], 1)}
        analysis["da_yun"]["worst"] = {"gan_zhi": dy_sorted[-1][0], "score": round(dy_sorted[-1][1], 1)}
    
    # ⑦ 8维度评分
    dims = DEFAULT_DIMENSIONS(bazi)
    analysis["dimensions"] = {}
    for dim_name, dim_score in dims.items():
        analysis["dimensions"][dim_name] = {
            "base": round(dim_score.base, 1),
            "da_yun_bonus": round(dim_score.da_yun_bonus, 1),
            "total": round(dim_score.total, 1),
        }
    
    # ⑧ 地支关系（刑冲合害）
    rel = check_all_relations(list(zh.zhi for zh in bazi.all_pillars()))
    analysis["di_zhi_relations"] = rel
    
    # ⑨ 流年（当前年份）
    liu_nian_gan_zhi = get_liu_nian_gan_zhi(current_year)
    if liu_nian_gan_zhi:
        liu_nian_gan, liu_nian_zhi = liu_nian_gan_zhi[0], liu_nian_gan_zhi[1]
        # 获取当前大运
        current_da_yun = None
        for dy in da_yun_list:
            if dy.start_year <= current_year <= dy.start_year + 9:
                current_da_yun = dy
                break
        dy_gan = current_da_yun.gan if current_da_yun else bazi.month.gan
        dy_zhi = current_da_yun.zhi if current_da_yun else bazi.month.zhi
        all_zhi = [bazi.year.zhi, bazi.month.zhi, bazi.day.zhi, bazi.hour.zhi]
        
        liu_nian = analyze_liu_nian(
            liu_nian_gan, liu_nian_zhi,
            bazi.ri_zhu, bazi.ri_zhu_wu_xing,
            bazi.year.zhi, dy_gan, dy_zhi, all_zhi
        )
    else:
        liu_nian = {"error": f"无法计算{current_year}年的干支"}
    analysis["liu_nian"] = liu_nian
    
    result["analysis"] = analysis
    
    # ═══ Step 4: 前端友好格式 ═══
    result["summary"] = {
        "bazi": paipan["bazi"],
        "ri_zhu": basic.get("ri_zhu", {}),
        "shen_qiang_ruo": f"{sqr_score}分({sqr_label})",
        "cai_xing": f"{cai_detail.total}分",
        "ge_ju": ge_ju_main,
        "xi_yong": " ".join(xi),
        "ji_shen": " ".join(ji),
    }
    
    return result


# ── CLI入口 ──
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="金鉴真人·八字确定性分析引擎")
    parser.add_argument("--name", required=True)
    parser.add_argument("--gender", required=True, choices=["男","女"])
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--hour", type=int, required=True)
    parser.add_argument("--minute", type=int, default=0)
    parser.add_argument("--lunar-month", type=int, default=None)
    parser.add_argument("--lunar-day", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    
    args = parser.parse_args()
    result = full_analysis(
        name=args.name, gender=args.gender,
        year=args.year, month=args.month, day=args.day,
        hour=args.hour, minute=args.minute,
        lunar_month=args.lunar_month, lunar_day=args.lunar_day,
    )
    
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))
