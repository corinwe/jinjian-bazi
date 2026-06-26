"""八字分析路由 v2.0 — 修复_service实例化+端点缺失"""
from fastapi import APIRouter, HTTPException
from api.schemas.request import AnalyzeRequest
from api.schemas.response import AnalyzeResponse
from api.services.analysis_service import AnalysisService
from concurrent.futures import ThreadPoolExecutor
import asyncio

router = APIRouter(prefix="/api/v1", tags=["analyze"])

# 线程池（引擎调用是I/O等待，非CPU密集）
_executor = ThreadPoolExecutor(max_workers=4)
_service = AnalysisService()  # ✅ 修复：实例化_service


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """提交八字分析"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, _run_analysis, request)

    if result.get("status") == "failed":
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "分析失败")
        )

    return AnalyzeResponse(
        analysis_id=result["analysis_id"],
        status="completed",
        basic=result["basic"],
        analysis=result.get("analysis"),
        message=result.get("message"),
    )


def _run_analysis(request: AnalyzeRequest) -> dict:
    """在线程中执行分析（避免asyncio阻塞）"""
    svc = AnalysisService()
    return svc.analyze(
        name=request.name, gender=request.gender,
        birth_year=request.birth_year, birth_month=request.birth_month,
        birth_day=request.birth_day, birth_hour=request.birth_hour,
        birth_minute=request.birth_minute,
        calendar_type=request.calendar_type,
        lunar_month=request.lunar_month, lunar_day=request.lunar_day,
        notes=request.notes, tags=request.tags,
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
    """调试模式：返回规则引擎完整JSON"""
    from api.services.engine_client import call_engine

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, call_engine,
        request.name, request.gender,
        request.birth_year, request.birth_month, request.birth_day,
        request.birth_hour, request.birth_minute,
        request.lunar_month, request.lunar_day)

    return result
