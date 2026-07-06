"""分析路由: 排盘+全量规则引擎（支持日期输入）"""

import json
import os
import subprocess
import sys

from app.auth import get_current_user
from app.database import get_db
from app.models import Report, ReportVersion, User
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 引擎模块路径（pipeline_v4/constants/lunar等存在../engine/下）
ENGINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "engine"))
if not os.path.isdir(ENGINE_DIR):
    ENGINE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", "engine"))
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

# 验证过的排盘引擎（bazi-engine.py，ephem天文库+节气精确计算）
BAZI_ENGINE = "/root/weiwuji-knowledge-base/07-国学哲学/八字命格/scripts/bazi-engine.py"

router = APIRouter(prefix="/analyze", tags=["分析"])


class AnalyzeByDateRequest(BaseModel):
    """按日期分析请求"""

    name: str = "用户"
    gender: str
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    calendar: str = "solar"  # solar=阳历, lunar=农历


def run_paipan(name: str, gender: str, year: int, month: int, day: int, hour: int) -> dict:
    """调用bazi-engine.py排盘，返回解析后的字典"""
    if not os.path.isfile(BAZI_ENGINE):
        raise RuntimeError("排盘引擎不存在: " + BAZI_ENGINE)

    # hour时辰起始小时 → 时辰索引: 0→子(0), 2→丑(1), 4→寅(2), 6→卯(3), ...
    shichen_idx = hour // 2

    cmd = [
        "python3",
        BAZI_ENGINE,
        str(year),
        str(month),
        str(day),
        str(hour),
        "0",
        str(shichen_idx),
        gender,
        name,
        "",
        "--json",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError("排盘引擎错误: " + result.stderr)
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError("排盘引擎输出解析失败: " + str(e))
    except subprocess.TimeoutExpired:
        raise RuntimeError("排盘引擎超时")


def run_full_analysis_v4(
    name: str, gender: str, birth_year: int, birth_month: int, birth_day: int, birth_hour: int, calendar: str = "solar"
) -> dict:
    """排盘+完整分析（支持阳历/农历）"""
    from lunar import lunar_to_solar, validate_date

    # 校验日期
    err = validate_date(birth_year, birth_month, birth_day, calendar)
    if err:
        raise ValueError(err)

    # 农历转阳历
    if calendar == "lunar":
        try:
            solar_date = lunar_to_solar(birth_year, birth_month, birth_day)
            birth_year, birth_month, birth_day = solar_date.year, solar_date.month, solar_date.day
        except Exception as e:
            raise ValueError("农历转换失败: " + str(e))

    # 1. 排盘（用验证过的bazi-engine.py）
    engine_result = run_paipan(name, gender, birth_year, birth_month, birth_day, birth_hour)

    pillars = engine_result["四柱"]
    na_yin = engine_result.get("纳音", {})

    def parse_pillar(s):
        return {"gan": s[0], "zhi": s[1]}

    # hour→时辰中文名
    shi_chen_names = {
        0: "子时",
        2: "丑时",
        4: "寅时",
        6: "卯时",
        8: "辰时",
        10: "巳时",
        12: "午时",
        14: "未时",
        16: "申时",
        18: "酉时",
        20: "戌时",
        22: "亥时",
    }

    pai = {
        "name": name,
        "gender": gender,
        "birth_date": str(birth_year) + "年" + str(birth_month) + "月" + str(birth_day) + "日",
        "birth_hour": birth_hour,
        "shi_chen": shi_chen_names.get(birth_hour, str(birth_hour) + "时"),
        "bazi": engine_result["八字"],
        "year_pillar": parse_pillar(pillars["年柱"]),
        "month_pillar": parse_pillar(pillars["月柱"]),
        "day_pillar": parse_pillar(pillars["日柱"]),
        "hour_pillar": parse_pillar(pillars["时柱"]),
        "na_yin": na_yin,
        "cang_gan": engine_result.get("藏干", {}),
        "shi_shen": engine_result.get("十神", {}),
        "da_yun": engine_result.get("大运", {}),
        "calendar_type": "阳历" if calendar == "solar" else "农历",
        "_engine_version": engine_result.get("引擎版本", ""),
    }

    # 2. 构建BaZi对象（保持与pipeline_v4兼容）
    from constants import BaZi, Pillar

    bazi = BaZi(
        year=Pillar(pai["year_pillar"]["gan"], pai["year_pillar"]["zhi"]),
        month=Pillar(pai["month_pillar"]["gan"], pai["month_pillar"]["zhi"]),
        day=Pillar(pai["day_pillar"]["gan"], pai["day_pillar"]["zhi"]),
        hour=Pillar(pai["hour_pillar"]["gan"], pai["hour_pillar"]["zhi"]),
        gender=gender,
    )

    # 3. 全量分析 v5（2026-07-05 修复：v4已归档，改用v5）
    from pipeline_v5 import run_v5

    result = run_v5(bazi, birth_year, birth_month, birth_day)

    # 4. 合并排盘信息
    result["paipan_info"] = pai

    return result


# 旧的精确干支接口保留
class AnalyzeRequest(BaseModel):
    year_gan: str
    year_zhi: str
    month_gan: str
    month_zhi: str
    day_gan: str
    day_zhi: str
    hour_gan: str
    hour_zhi: str
    gender: str
    birth_year: int | None = 1980
    birth_month_lunar: int | None = 1


@router.post("")
@router.post("/date")
def analyze(data: AnalyzeByDateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """八字分析（支持日期输入+阳历/农历）"""
    if user and user.level == "free" and user.credits <= 0:
        raise HTTPException(status_code=402, detail="次数已用完")

    try:
        result = run_full_analysis_v4(
            data.name, data.gender, data.birth_year, data.birth_month, data.birth_day, data.birth_hour, data.calendar
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="分析失败: " + str(e))

    # 保存报告
    pi = result.get("paipan_info", {})
    report = Report(
        user_id=user.id if user else 0,
        year_gan=pi.get("year_pillar", {}).get("gan", ""),
        year_zhi=pi.get("year_pillar", {}).get("zhi", ""),
        month_gan=pi.get("month_pillar", {}).get("gan", ""),
        month_zhi=pi.get("month_pillar", {}).get("zhi", ""),
        day_gan=pi.get("day_pillar", {}).get("gan", ""),
        day_zhi=pi.get("day_pillar", {}).get("zhi", ""),
        hour_gan=pi.get("hour_pillar", {}).get("gan", ""),
        hour_zhi=pi.get("hour_pillar", {}).get("zhi", ""),
        gender=data.gender,
        birth_year=data.birth_year,
        birth_month_lunar=data.birth_month,
        result_json=json.dumps(result, ensure_ascii=False),
        version="4.0",
        status="completed",
    )
    db.add(report)
    db.flush()

    # 记录版本
    version = ReportVersion(
        report_id=report.id,
        version="4.0",
        result_json=json.dumps(result, ensure_ascii=False),
        changelog="日期输入自动排盘+21§全量输出",
    )
    db.add(version)

    if user and user.level == "free":
        user.credits -= 1
        user.report_count += 1

    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "name": data.name,
        "bazi": pi.get("bazi", ""),
        "result": result,
        "credits_remaining": user.credits if user else None,
    }


@router.post("/polish/{report_id}")
def polish_report(report_id: int, db: Session = Depends(get_db)):
    """LLM润色报告（生成自然语言报告）"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    if not report.result_json:
        raise HTTPException(status_code=400, detail="报告无数据")

    result = json.loads(report.result_json)

    # 调用LLM润色（模拟实现）
    polished = _polish_with_llm(result)

    return {"report_id": report_id, "polished": polished}


def _polish_with_llm(data: dict) -> str:
    """
    LLM润色：从结构化JSON生成自然语言报告
    实际生产环境调用大模型API
    """
    b = data["basic"]
    s = data["shen_qiang_ruo"]
    c = data["cai_xing"]
    g = data["ge_ju"]
    x = data["xi_yong_shen"]
    e = data["energy"]
    d = data["di_zhi_guan_xi"]
    ss = data["shen_sha"]
    dy = data["da_yun"]
    dims = data["dimensions"]

    lines = []
    lines.append("# 金鉴真人·八字命理分析报告")
    lines.append("")
    lines.append("## 八字信息")
    lines.append("**八字**: " + b["bazi"] + " | **日主**: " + b["ri_zhu"]["gan"] + "(" + b["ri_zhu"]["wu_xing"] + ")")
    lines.append("")
    lines.append("## 身强弱分析")
    lines.append("身强弱评分: **" + str(s["score"]) + "分** → **" + s["label"] + "**")
    lines.append(
        "月令印星: "
        + str(s["details"]["yue_ling_yin"])
        + "分 | 月令比劫: "
        + str(s["details"]["yue_ling_bi_jie"])
        + "分"
    )
    lines.append(
        "天干比劫: "
        + str(s["details"]["tian_gan_bi_jie"])
        + "分 | 地支印比: "
        + str(s["details"]["ri_zhi_yin_bi"])
        + "+"
        + str(s["details"]["nian_shi_zhi_yin_bi"])
        + "分"
    )
    lines.append("")
    lines.append("## 财星分析")
    lines.append(
        "财星总分: **"
        + str(c["total"])
        + "分**（月令"
        + str(c["details"]["yue_ling"])
        + " + 日支"
        + str(c["details"]["ri_zhi"])
        + " + 时干"
        + str(c["details"]["shi_gan"])
        + " + 时支"
        + str(c["details"]["shi_zhi"])
        + " + 年支"
        + str(c["details"]["nian_zhi"])
        + "）"
    )
    lines.append("")
    lines.append("## 格局判定")
    lines.append("**" + g["detail"] + "**")
    lines.append("喜用神: " + str(x["xi"]) + " | 忌神: " + str(x["ji"]))
    if x.get("tiao_hou"):
        lines.append("调候用神: " + x["tiao_hou"])
    lines.append("")
    lines.append("## 五行能量")
    lines.append(str(e["wu_xing"]))
    lines.append("最强: " + e["strongest"] + " | 最弱: " + e["weakest"])
    lines.append("")
    lines.append("## 地支关系")
    lines.append(d["summary"])
    lines.append("")
    lines.append("## 神煞")
    lines.append(ss["summary"])
    lines.append("")
    lines.append("## 大运走势")
    best = dy["list"][dy["best_index"]] if dy["best_index"] >= 0 else None
    worst = dy["list"][dy["worst_index"]] if dy["worst_index"] >= 0 else None
    if best:
        lines.append(
            "**最佳大运**: "
            + best["gan_zhi"]
            + "（"
            + str(best["start_age"])
            + "~"
            + str(best["end_age"])
            + "岁）- "
            + str(best["score"])
            + "/10"
        )
    if worst:
        lines.append(
            "**最差大运**: "
            + worst["gan_zhi"]
            + "（"
            + str(worst["start_age"])
            + "~"
            + str(worst["end_age"])
            + "岁）- "
            + str(worst["score"])
            + "/10"
        )
    lines.append("")
    lines.append("## 人生维度评分")
    for name, ds in sorted(dims.items()):
        bar = "█" * int(ds["total"]) + "░" * (10 - int(ds["total"]))
        lines.append(name + ": " + bar + " " + str(ds["total"]) + "/10")
    lines.append("")
    lines.append("---")
    lines.append("*报告由金鉴真人·八字规则引擎 v2.0 生成 | 确定性计算·零幻觉*")

    return "\n".join(lines)
