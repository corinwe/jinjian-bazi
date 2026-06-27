"""FastAPI主入口 v1.2 — 带可观测性（结构化日志+RED指标）"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import analyze, health
from database.connection import init_db
from api.observability import ObservabilityMiddleware, get_metrics_response, logger

app = FastAPI(
    title="金鉴真人·八字命理分析API",
    version="5.0.0",
    description="""## 确定性规则驱动的八字命理分析服务

### 核心特性
- **确定性引擎**：所有计算由规则引擎完成，零幻觉
- **21维度分析**：财富、事业、婚姻、子女、学业、健康等
- **农历支持**：自动将农历日期转为公历
- **完整报告**：返回结构化JSON，支持前端直接渲染

### 使用方式
1. `POST /api/v1/analyze` — 提交八字分析
2. `GET /api/v1/analyses/{id}` — 获取分析结果
3. `POST /api/v1/report` — 生成完整命理报告
4. `POST /api/v1/engine/debug` — 调试模式查看引擎原始数据
    """,
    contact={"name": "金鉴真人", "url": "https://github.com/corinwe/jinjian-bazi"},
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS（允许前端跨域）
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# 注册可观测中间件（放在CORS之后）
app.add_middleware(ObservabilityMiddleware)

# 注册路由（必须在StaticFiles挂载之前）
app.include_router(health.router)
app.include_router(analyze.router)

# /metrics端点（必须在StaticFiles挂载之前）
@app.get("/metrics")
async def metrics():
    """Prometheus指标端点（供监控系统抓取）"""
    return get_metrics_response()

# 挂载前端静态文件（如果存在）
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.on_event("startup")
async def startup():
    """启动时初始化数据库"""
    init_db()
    logger.bind(service="api", trace_id="system").info("API服务启动完成")


@app.on_event("shutdown")
async def shutdown():
    logger.bind(service="api", trace_id="system").info("API服务关闭")
