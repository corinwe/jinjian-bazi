"""
金鉴真人·API可观测性模块 v1.0
RED指标 + 结构化日志 + 健康增强
"""

import time
import json
from pathlib import Path
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# ── 日志配置 ──
LOG_DIR = Path("/var/log/bazi-api")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 移除默认handler
logger.remove()

# 控制台输出（带颜色）
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# 文件输出（结构化JSON）
logger.add(
    LOG_DIR / "api_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[service]} | {extra[trace_id]} | {message}",
    rotation="100 MB",
    retention="30 days",
    compression="gz",
    level="DEBUG",
    enqueue=True,
)

# 错误日志独立文件
logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[service]} | {extra[trace_id]} | {message}",
    rotation="50 MB",
    retention="90 days",
    compression="gz",
    level="ERROR",
    enqueue=True,
)

# ── RED指标 ──
METRIC_REQUEST_COUNT = Counter(
    "bazi_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

METRIC_REQUEST_DURATION = Histogram(
    "bazi_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

METRIC_ENGINE_CALLS = Counter(
    "bazi_engine_calls_total",
    "Total engine calls",
    ["module", "status"],
)

METRIC_ACTIVE_REQUESTS = Gauge(
    "bazi_http_active_requests",
    "Currently active HTTP requests",
)

# ── 中间件 ──
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """为每个请求添加RED指标 + 结构化日志"""

    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())[:8]
        request.state.trace_id = trace_id
        request.state.start_time = time.time()

        METRIC_ACTIVE_REQUESTS.inc()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            logger.bind(service="api", trace_id=trace_id).error(
                "Unhandled exception: {exc}", exc=exc
            )
            raise
        finally:
            METRIC_ACTIVE_REQUESTS.dec()

        duration = time.time() - request.state.start_time
        endpoint = request.url.path
        method = request.method

        # RED指标
        METRIC_REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        METRIC_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        # 结构化日志（仅慢请求和错误做详细日志）
        if status_code >= 400 or duration > 1.0:
            logger.bind(service="api", trace_id=trace_id).warning(
                "{method} {path} → {status} ({duration:.3f}s)",
                method=method, path=endpoint, status=status_code, duration=duration,
            )

        return response


def get_metrics_response():
    """获取Prometheus metrics"""
    from starlette.responses import Response
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

