"""八字分析路由"""
import os
import tempfile
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.bazi_engine import calculate_bazi
from app.services.report_generator_simple import generate_report
from app.services.pdf_service import generate_pdf

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["analyze"])

_analyses = {}
_next_id = 1


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_bazi(req: AnalyzeRequest):
    global _next_id
    try:
        # 排盘
        # 性别映射: "男"→1, "女"→0
        gender_int = 1 if req.gender == "男" else 0

        bazi_result = calculate_bazi(
            year=req.birth_year,
            month=req.birth_month,
            day=req.birth_day,
            hour=req.birth_hour or 12,
            minute=req.birth_minute,
            is_lunar=req.is_lunar,
            gender=gender_int,
        )

        # 生成报告
        birth_info = {
            "birth_year": req.birth_year,
            "birth_month": req.birth_month,
            "birth_day": req.birth_day,
            "birth_hour": req.birth_hour,
            "is_lunar": req.is_lunar,
            "birthplace": req.birthplace,
        }
        report = generate_report(bazi_result, req.name, req.gender, birth_info)

        # 存储
        analysis_id = _next_id
        _next_id += 1
        _analyses[analysis_id] = {
            "id": analysis_id,
            "name": req.name,
            "report_md": report["content_md"],
            "line_count": report["line_count"],
        }

        return AnalyzeResponse(
            analysis_id=analysis_id,
            status="completed",
            message="分析完成",
            basic=bazi_result.get("basic", {}),
            analysis=bazi_result.get("analysis", {}),
            report_md=report["content_md"],
            line_count=report["line_count"],
            pdf_url=f"/api/v1/analyses/{analysis_id}/pdf",
        )

    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)[:200]}")


@router.get("/analyses/{analysis_id}", response_model=AnalyzeResponse)
async def get_analysis(analysis_id: int):
    if analysis_id not in _analyses:
        raise HTTPException(status_code=404, detail="分析结果不存在")
    a = _analyses[analysis_id]
    return AnalyzeResponse(
        analysis_id=analysis_id,
        status="completed",
        message="",
        basic={},
        analysis={},
        report_md=a["report_md"],
        line_count=a["line_count"],
        pdf_url=f"/api/v1/analyses/{analysis_id}/pdf",
    )


@router.get("/analyses/{analysis_id}/pdf")
async def download_pdf(analysis_id: int):
    if analysis_id not in _analyses:
        raise HTTPException(status_code=404, detail="分析结果不存在")
    a = _analyses[analysis_id]
    md_text = a["report_md"]
    name = a["name"]

    # Generate PDF to temp file
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf", prefix=f"jinjian_{analysis_id}_")
    os.close(fd)

    pdf_path = generate_pdf(md_text, pdf_path)
    if not pdf_path or not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
        raise HTTPException(status_code=500, detail="PDF生成失败")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"金鉴真人_八字命理报告_{name}.pdf",
        headers={"Content-Disposition": f'attachment; filename="jinjian_report_{analysis_id}.pdf"'},
    )
