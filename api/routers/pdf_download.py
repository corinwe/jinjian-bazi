"""金鉴真人·PDF报告下载路由 v1.0"""

import os
import sys

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from api.services.engine_client import call_engine
from api.services.pdf_report import generate_pdf_report

router = APIRouter(prefix="/api/v1/report", tags=["pdf"])


class PDFRequest(BaseModel):
    name: str = Field(..., description="姓名")
    gender: str = Field(..., pattern="^(男|女)$")
    birth_year: int = Field(..., ge=1900, le=2100)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(..., ge=0, le=23)
    calendar_type: str = Field(default="solar", pattern="^(solar|lunar)$")
    birth_place: str = Field(default="", description="出生地，可选")


@router.post("/pdf")
async def download_pdf(request: PDFRequest):
    """生成真正的文本PDF报告并下载"""
    try:
        # 农历→公历转换（同analyze路由逻辑）
        sy, sm, sd = request.birth_year, request.birth_month, request.birth_day
        lunar_month, lunar_day = None, None
        if request.calendar_type == "lunar":
            lunar_month, lunar_day = request.birth_month, request.birth_day
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
            from lunar import lunar_to_solar
            solar = lunar_to_solar(request.birth_year, request.birth_month, request.birth_day)
            sy, sm, sd = solar.year, solar.month, solar.day

        # 调用引擎（传递农历参数让引擎正确处理）
        engine_result = call_engine(
            request.name,
            request.gender,
            sy, sm, sd,
            request.birth_hour,
            lunar_month=lunar_month,
            lunar_day=lunar_day,
        )

        if not engine_result.get("success"):
            raise HTTPException(status_code=500, detail=engine_result.get("error", "引擎调用失败"))

        data = {k: v for k, v in engine_result.items() if k != "success"}
        meta = {
            "name": request.name,
            "gender": request.gender,
            "year": request.birth_year,
            "month": request.birth_month,
            "day": request.birth_day,
            "hour": request.birth_hour,
            "birthplace": request.birth_place or "东八区",
        }

        # 生成PDF
        pdf_bytes = generate_pdf_report(data, meta)

        # 直接用Response返回二进制
        from starlette.responses import Response as StarletteResponse

        return StarletteResponse(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="report.pdf"',
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF生成失败: {e}")
