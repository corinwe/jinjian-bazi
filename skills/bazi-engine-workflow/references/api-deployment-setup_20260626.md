# API/部署层设置（2026-06-26新增）

## 文件位置
```
projects/bazi-platform/
├── run.sh                    # 一键启动脚本（检查环境→验证引擎→初始化DB→启动服务）
├── Dockerfile                # 生产镜像（含引擎验证+测试）
├── api/
│   ├── __init__.py           # 包声明
│   ├── main.py               # FastAPI入口（CORS+路由+前端挂载）
│   ├── config.py             # 引擎路径/超时配置
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py         # /ping /health /version
│   │   └── analyze.py        # POST /analyze + GET /analyses + POST /engine/debug
│   ├── schemas/
│   │   ├── request.py        # AnalyzeRequest (Pydantic)
│   │   └── response.py       # AnalyzeResponse
│   ├── services/
│   │   ├── analysis_service.py  # 用户管理+引擎调用+数据库
│   │   └── engine_client.py     # subprocess调用pipeline_v5.py
│   └── repositories/
│       ├── user_repo.py      # 用户CRUD
│       └── analysis_repo.py  # 分析记录CRUD
├── backend/                  # 旧版后端（保留但逐步废弃）
├── database/
│   ├── __init__.py
│   ├── connection.py         # SQLite连接管理+BaseRepository
│   └── schema.sql            # 5张表（users/analyses/basic_data/analysis_results/reports）
├── frontend/
│   └── index.html            # 单页SPA（内联JS，深色主题）
└── engine/                   # 规则引擎（36模块·12,437行）
```

## API端点

| 方法 | 路径 | 说明 | 状态 |
|:----|:-----|:-----|:----:|
| GET | /ping | 健康检查 | ✅ |
| GET | /health | 详细健康检查 | ✅ |
| GET | /version | 版本信息 | ✅ |
| POST | /api/v1/analyze | 完整分析（含数据库存储） | ✅ |
| GET | /api/v1/analyses/{id} | 获取分析结果 | ✅ |
| GET | /api/v1/users/{id}/analyses | 用户历史 | ✅ |
| POST | /api/v1/engine/debug | 调试（返回完整引擎JSON） | ✅ |
| GET | / | 前端页面 | ✅ |

## 启动方式

```bash
# 开发模式
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && ./run.sh
# 或手动
PYTHONPATH=/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform:$PYTHONPATH python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
docker build -t jinjian-zhenren .
docker run -p 8000:8000 jinjian-zhenren
```

## 前端请求格式

前端发送给API的请求体必须是：
```json
{
  "name": "姓名",
  "gender": "男/女",
  "birth_year": 1980,
  "birth_month": 7,
  "birth_day": 15,
  "birth_hour": 4
}
```

## 已知问题

- `/api/v1/analyze` 的 `AnalyzeResponse` 可能不包含完整的 `analysis.dimensions`（取决于引擎版本）
- `/api/v1/engine/debug` 返回完整引擎JSON，适合调试
- 数据库路径：`projects/bazi-platform/database/bazi.db`
- API使用ThreadPoolExecutor(max_workers=4)处理并发
