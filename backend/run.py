#!/usr/bin/env python3
"""金鉴真人·FastAPI启动入口"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=1,
        reload=False,
    )
