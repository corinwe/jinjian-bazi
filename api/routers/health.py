"""健康检查路由 v1.1 — 修复路径+添加详情"""

import os

from fastapi import APIRouter

router = APIRouter(tags=["health"])

# 引擎文件存在性检查
ENGINE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "engine")


def _check_engine_health() -> dict:
    """检查引擎各模块状态"""
    checks = {}
    modules = ["paipan", "shen_qiang_ruo", "pipeline_v5", "constants"]
    for mod in modules:
        mod_path = os.path.join(ENGINE_DIR, f"{mod}.py")
        checks[mod] = os.path.exists(mod_path)
    return checks


@router.get("/ping")
async def ping():
    return {"status": "ok", "message": "金鉴真人·八字命理分析API"}


@router.get("/health")
async def health():
    engine_checks = _check_engine_health()
    all_ok = all(engine_checks.values())
    return {
        "status": "healthy" if all_ok else "degraded",
        "version": "5.0.0",
        "engine": {"available": all_ok, "modules": engine_checks, "dir": ENGINE_DIR},
        "service": "金鉴真人·八字命理分析平台",
    }


@router.get("/version")
async def version():
    engine_checks = _check_engine_health()
    return {
        "version": "5.0.0",
        "engine": "金鉴真人·确定性规则引擎 v5.0",
        "engine_available": all(engine_checks.values()),
        "modules": list(engine_checks.keys()),
    }
