"""响应Schema定义"""

from pydantic import BaseModel


class BasicData(BaseModel):
    """八字基础数据（灵活结构）"""

    bazi: str
    ri_zhu: dict
    pillars: dict
    tian_gan_notes: list
    di_zhi_notes: list
    cheng_gu: dict | None = None


class AnalyzeResponse(BaseModel):
    """分析响应"""

    analysis_id: int
    status: str
    basic: BasicData
    analysis: dict | None = None
    message: str | None = None


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str
    detail: str | None = None


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    version: str
    engine_available: bool
