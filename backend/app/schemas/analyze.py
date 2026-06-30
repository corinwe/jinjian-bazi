"""Pydantic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnalyzeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(..., pattern="^(男|女)$")
    birth_year: int = Field(..., ge=1900, le=2100)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: Optional[int] = Field(None, ge=0, le=23)
    birth_minute: int = Field(0, ge=0, le=59)
    is_lunar: bool = False
    birthplace: str = ""


class AnalyzeResponse(BaseModel):
    analysis_id: int
    status: str
    message: str = ""
    name: str = ""
    gender: str = ""
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    birth_hour: Optional[int] = None
    birth_minute: int = 0
    is_lunar: bool = False
    birthplace: str = ""
    basic: dict = {}
    analysis: dict = {}
    report_md: str = ""
    report_sections: list = []  # pre-rendered HTML sections: [{icon, title, content_html}]
    line_count: int = 0
    pdf_url: str = ""


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
