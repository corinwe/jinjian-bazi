"""健康检查路由"""
from fastapi import APIRouter
import os

router = APIRouter(tags=["health"])

ENGINE_PIPELINE = os.path.join(
    os.path.dirname(__file__), "..", "..", "engine", "pipeline_product.py"
)


@router.get("/ping")
async def ping():
    return {"status": "ok", "message": "金鉴真人·八字命理分析API"}


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "5.0",
        "engine_available": os.path.exists(ENGINE_PIPELINE),
        "service": "金鉴真人·八字命理分析平台",
    }


@router.get("/version")
async def version():
    return {
        "version": "5.0",
        "engine": "金鉴真人·确定性规则引擎 v5.0",
        "engine_available": os.path.exists(ENGINE_PIPELINE),
    }
