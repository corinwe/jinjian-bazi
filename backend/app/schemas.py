"""Pydantic schemas for API"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    phone: str
    password: str
    nickname: Optional[str] = None

class UserLogin(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    nickname: str
    level: str
    credits: int

class UserInfo(BaseModel):
    id: int
    nickname: str
    phone: Optional[str]
    level: str
    credits: int
    report_count: int
    created_at: Optional[datetime]

class AnalyzeRequest(BaseModel):
    year_gan: str
    year_zhi: str
    month_gan: str
    month_zhi: str
    day_gan: str
    day_zhi: str
    hour_gan: str
    hour_zhi: str
    gender: str  # 男/女
    birth_year: Optional[int] = 1980
    birth_month_lunar: Optional[int] = 1

class ReportResponse(BaseModel):
    id: int
    bazi: str
    gender: str
    version: str
    result: Optional[dict]
    created_at: Optional[datetime]

class ReportListResponse(BaseModel):
    total: int
    items: List[ReportResponse]

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
