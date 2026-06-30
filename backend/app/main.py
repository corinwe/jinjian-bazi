"""金鉴真人·八字命理分析API"""
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db, engine, Base
from app.routers import analyze
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.app_name} v{settings.app_version} 启动中...")
    # 初始化数据库表(如果不存在)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表初始化完成")
    except Exception as e:
        logger.warning(f"数据库初始化失败(可能未配置): {e}")
    logger.info("金鉴真人服务启动完成")
    yield
    logger.info("金鉴真人服务关闭")


app = FastAPI(
    title=settings.app_name,
    description="确定性规则驱动的八字命理分析服务",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Process-Time-Ms"] = str(round(elapsed * 1000, 2))
    return response


@app.exception_handler(Exception)
async def global_exception(request: Request, exc: Exception):
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"code": -500, "message": f"服务器内部错误", "data": None})


# ─── 健康检查 ──────────────────────────────────────────
@app.get("/health", tags=["系统"])
async def health():
    return {"status": "ok", "service": "jinjian-backend", "version": settings.app_version, "name": settings.app_name}


@app.get("/", tags=["系统"])
async def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


# ─── 注册路由 ──────────────────────────────────────────
app.include_router(analyze.router)
# hook trigger Tue Jun 30 02:12:42 PM CST 2026
