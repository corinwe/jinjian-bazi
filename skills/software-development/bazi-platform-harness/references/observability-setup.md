# 金鉴真人·可观测性体系 v1.0

> 搭建时间：2026-06-27
> 涉及文件：`api/observability.py`, `/etc/systemd/system/bazi-api.service`

## 架构

```
客户端请求
    │
    ▼
┌─────────────────────────────────────────────┐
│  ObservabilityMiddleware                     │
│  ├─ 生成 trace_id (uuid8)                    │
│  ├─ 记录请求开始时间                          │
│  ├─ 计数：bazi_http_requests_total            │
│  ├─ 计时：bazi_http_request_duration_seconds  │
│  ├─ 计数：bazi_http_active_requests            │
│  └─ 慢/错误请求 → 结构化日志                   │
├─────────────────────────────────────────────┤
│  引擎调用 (engine_client.py)                 │
│  ├─ 计数：bazi_engine_calls_total              │
│  ├─ 记录耗时+状态(success/fail/timeout)       │
│  └─ 慢调用(>5s) → 告警日志                    │
├─────────────────────────────────────────────┤
│  loguru 日志系统                              │
│  ├─ 控制台：彩色格式化                        │
│  ├─ 文件：/var/log/bazi-api/api_YYYY-MM-DD.log│
│  ├─ 错误文件：/var/log/bazi-api/error_*.log   │
│  ├─ 轮转：100MB/文件, 保留30天               │
│  └─ 压缩：.gz                                │
└─────────────────────────────────────────────┘
```

## 日志格式

```
# 控制台
2026-06-27 10:33:51 | INFO     | api.main:startup:65 - API服务启动完成

# JSON日志文件（结构化的）
{time} | {level} | {extra[service]} | {extra[trace_id]} | {message}
```

## RED指标 (/metrics端点)

| 指标名 | 类型 | Labels | 说明 |
|--------|------|--------|------|
| `bazi_http_requests_total` | Counter | method, endpoint, status | 总请求数 |
| `bazi_http_request_duration_seconds` | Histogram | method, endpoint | 请求延迟分布 |
| `bazi_http_active_requests` | Gauge | — | 当前活跃连接 |
| `bazi_engine_calls_total` | Counter | module, status | 引擎调用计数 |

## systemd自愈

```bash
# 服务文件位置
/etc/systemd/system/bazi-api.service

# 关键配置
Restart=always       # crash后自动重启
RestartSec=5         # 5秒后重试
ExecStart=/usr/bin/python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# 日志位置
journalctl -u bazi-api --no-pager -n 50
```

## 速率限制

```yaml
工具: slowapi
默认限制: 30 req/minute per IP
超限响应: HTTP 429 Too Many Requests
配置位置: api/main.py (Limiter初始化)
```
