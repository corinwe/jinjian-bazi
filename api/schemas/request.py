"""请求Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """八字分析请求"""
    name: str = Field(..., description="姓名", min_length=1, max_length=20)
    gender: str = Field(..., description="性别", pattern="^(男|女)$")
    
    # 公历出生日期
    birth_year: int = Field(..., description="公历出生年", ge=1900, le=2100)
    birth_month: int = Field(..., description="公历出生月", ge=1, le=12)
    birth_day: int = Field(..., description="公历出生日", ge=1, le=31)
    birth_hour: int = Field(..., description="出生时", ge=0, le=23)
    birth_minute: int = Field(default=0, description="出生分", ge=0, le=59)
    
    # 可选字段
    calendar_type: str = Field(default="solar", description="日历类型", pattern="^(solar|lunar)$")
    lunar_month: Optional[int] = Field(default=None, description="农历月", ge=1, le=12)
    lunar_day: Optional[int] = Field(default=None, description="农历日", ge=1, le=30)
    birth_place: Optional[str] = Field(default=None, description="出生地")
    tags: Optional[list[str]] = Field(default=None, description="标签")
    notes: Optional[str] = Field(default=None, description="备注")


class DebugAnalyzeRequest(AnalyzeRequest):
    """调试分析（返回完整JSON）"""
    pass
