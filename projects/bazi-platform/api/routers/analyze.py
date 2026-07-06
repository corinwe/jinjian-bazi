"""八字分析路由 v2.1 — 农历转公历支持 + 完整端点"""

import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException

from api.schemas.request import AnalyzeRequest
from api.schemas.response import AnalyzeResponse
from api.services.analysis_service import AnalysisService

# 引入引擎模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from lunar import lunar_to_solar
from report_generator import generate_report as gen_report

router = APIRouter(prefix="/api/v1", tags=["analyze"])

# 线程池
_executor = ThreadPoolExecutor(max_workers=4)
_service = AnalysisService()


def _ensure_solar_date(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    calendar_type: str = "solar",
    lunar_month: int = None,
    lunar_day: int = None,
):
    """
    如果用户选择农历，将出生日期转为公历
    返回 (solar_year, solar_month, solar_day)
    """
    if calendar_type == "lunar":
        try:
            lm = lunar_month if lunar_month else birth_month
            ld = lunar_day if lunar_day else birth_day
            solar_date = lunar_to_solar(birth_year, lm, ld)
            return (solar_date.year, solar_date.month, solar_date.day)
        except Exception as e:
            raise ValueError(f"农历转公历失败({birth_year}年{birth_month}月{birth_day}日): {e}")
    return (birth_year, birth_month, birth_day)


def _call_engine_direct(
    name,
    gender,
    birth_year,
    birth_month,
    birth_day,
    birth_hour,
    birth_minute=0,
    calendar_type="solar",
    lunar_month=None,
    lunar_day=None,
) -> dict:
    """统一引擎调用入口（含农历转换）"""
    from api.services.engine_client import call_engine

    # 农历→公历转换
    sy, sm, sd = _ensure_solar_date(birth_year, birth_month, birth_day, calendar_type, lunar_month, lunar_day)

    return call_engine(name, gender, sy, sm, sd, birth_hour, birth_minute, lunar_month, lunar_day)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """提交八字分析（含农历支持）"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, _run_analysis, request)

    if result.get("status") == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "分析失败"))

    return AnalyzeResponse(
        analysis_id=result["analysis_id"],
        status="completed",
        basic=result["basic"],
        analysis=result.get("analysis"),
        message=result.get("message"),
    )


def _run_analysis(request: AnalyzeRequest) -> dict:
    """在线程中执行分析"""
    svc = AnalysisService()
    # 先转公历
    sy, sm, sd = _ensure_solar_date(
        request.birth_year,
        request.birth_month,
        request.birth_day,
        request.calendar_type,
        request.lunar_month,
        request.lunar_day,
    )
    return svc.analyze(
        name=request.name,
        gender=request.gender,
        birth_year=sy,
        birth_month=sm,
        birth_day=sd,
        birth_hour=request.birth_hour,
        birth_minute=request.birth_minute,
        calendar_type=request.calendar_type,
        lunar_month=request.lunar_month,
        lunar_day=request.lunar_day,
        notes=request.notes,
        tags=request.tags,
    )


@router.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: int):
    """获取分析结果"""
    result = _service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    return result


@router.get("/users/{user_id}/analyses")
async def get_user_analyses(user_id: int, limit: int = 20):
    """获取用户分析历史"""
    return _service.get_user_analyses(user_id)


@router.post("/engine/debug")
async def debug_analyze(request: AnalyzeRequest):
    """调试模式：返回规则引擎完整JSON（含农历支持）"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        _executor,
        _call_engine_direct,
        request.name,
        request.gender,
        request.birth_year,
        request.birth_month,
        request.birth_day,
        request.birth_hour,
        request.birth_minute,
        request.calendar_type,
        request.lunar_month,
        request.lunar_day,
    )
    return result


@router.post("/report")
async def report_endpoint(request: AnalyzeRequest):
    """生成完整命理报告（含农历支持）"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        _executor,
        _call_engine_direct,
        request.name,
        request.gender,
        request.birth_year,
        request.birth_month,
        request.birth_day,
        request.birth_hour,
        request.birth_minute,
        request.calendar_type,
        request.lunar_month,
        request.lunar_day,
    )

    if not result.get("success"):
        return {"success": False, "error": result.get("error", "引擎调用失败")}

    engine_result = result.get("result", {})
    report_text = gen_report(engine_result, request.name, request.gender)

    return {
        "success": True,
        "report": report_text,
        "bazi": result.get("paipan", {}).get("bazi", ""),
        "analysis_id": None,
    }
