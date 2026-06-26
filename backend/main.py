"""
金鉴真人·八字平台 — 后端主入口
FastAPI + SQLite + JWT
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = FastAPI(
    title="金鉴真人·八字命理平台 API",
    description="B2C八字命理分析平台后端",
    version="1.0.0",
)

# CORS - 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（前端）
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# 注册路由
from app.routers import users, reports, analyze
app.include_router(users.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")

@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # 初始化数据库
    from app.database import init_db
    init_db()
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
