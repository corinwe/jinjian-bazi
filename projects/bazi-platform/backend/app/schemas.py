"""Pydantic schemas for API"""

from datetime import datetime

from pydantic import BaseModel


class UserRegister(BaseModel):
    phone: str
    password: str
    nickname: str | None = None


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
    phone: str | None
    level: str
    credits: int
    report_count: int
    created_at: datetime | None


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
    birth_year: int | None = 1980
    birth_month_lunar: int | None = 1


class ReportResponse(BaseModel):
    id: int
    bazi: str
    gender: str
    version: str
    result: dict | None
    created_at: datetime | None


class ReportListResponse(BaseModel):
    total: int
    items: list[ReportResponse]


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
