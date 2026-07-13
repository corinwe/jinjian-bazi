# 金鉴真人·八字平台 公网部署指南

> **部署日期**：2026-07-09
> **最后更新**：2026-07-09 (session 3: pipeline crash修复 + API response结构修正)
> **服务器**：腾讯云轻量服务器 43.162.90.39
> **网站URL**：http://43.162.90.39/

## 架构

```
用户浏览器 → nginx:80 (反向代理) → uvicorn:8000 (FastAPI)
                                     ↓
                              pipeline_v5 引擎 → subprocess调用
```

## 组件

| 组件 | 详情 |
|:----|:------|
| **Web服务器** | nginx 1.24.0, 监听80端口, 反代到127.0.0.1:8000 |
| **API服务** | uvicorn + FastAPI, `api/main.py:app` |
| **前端** | Vue 3 + Vite, 已编译到 `frontend/dist/` |
| **引擎** | `engine/pipeline_v5.py` + 36个模块 |
| **数据库** | SQLite `database/bazi.db` |
| **持久化** | systemd服务 `jinjian-api.service` |

## 部署命令速查

```bash
# 1. API服务管理（systemd）
sudo systemctl start jinjian-api      # 启动
sudo systemctl stop jinjian-api       # 停止
sudo systemctl restart jinjian-api    # 重启
sudo systemctl status jinjian-api     # 查看状态
sudo systemctl enable jinjian-api     # 开机自启
sudo journalctl -u jinjian-api -f     # 查看实时日志

# 2. nginx管理
sudo nginx -t                         # 测试配置
sudo systemctl reload nginx           # 重载
sudo systemctl restart nginx          # 重启

# 3. 手动运行（调试用）
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform
python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

# 4. 健康检查
curl http://localhost/health          # API健康检查
curl http://43.162.90.39/            # 公网访问检查
```

## ⚠️ 常见部署问题与修复

### ① pipeline_v5.py 报告格式化崩溃（KeyError）

**现象**：`POST /api/v1/analyze` 返回500，body含 `format_21_section_report` 报错。
**根因**：`format_21_section_report()` 函数在L429/L553等处以硬编码dict key访问(`dy['score']`)，当引擎返回数据中该key缺失时抛出 `KeyError`。
**修复**：
- 在 `run_pipeline()` 中把 `format_21_section_report(result)` 调用包在 `try/except` 里（pipeline_v5.py L655-658）
- 单字段修复：把硬编码key访问改为 `.get()` 带默认值（如L429 `s1.get('best_da_yun_score', 0)`）
- **双重防御**：try/except兜底 + .get()安全访问，缺一不可

```python
# pipeline_v5.py run_pipeline():
try:
    text_report = format_21_section_report(result)
except Exception:
    text_report = ""  # 不阻塞JSON输出
```

### ② 前端页面空白（`result`字段缺失）

**现象**：前端报告页显示空白，API `/api/v1/analyze` 返回 `analysis` 但不含 `result`。
**根因**：前端ReportPage.vue通过 `this.report?.result?.sec_*` 读取数据，但API服务层 `analysis_service.py` 没有把引擎返回的 `result`（含22个sec_*模块）传递到API响应中。
**修复链**（三个文件必须同时改）：
1. `api/schemas/response.py` → `AnalyzeResponse` 加 `result: dict | None = None`
2. `api/services/analysis_service.py` → 返回值加 `"result": engine_result.get("result")`
3. `api/routers/analyze.py` → `AnalyzeResponse()` 构造函数加 `result=result.get("result")`

**验证**：重启后 `curl /api/v1/analyze | jq '.result.sec_3_shen_qiang_ruo.label'` 应返回非空。

### ③ 旧进程占端口（systemctl restart后仍无法访问）

**现象**：`systemctl restart jinjian-api` 后 `curl localhost:8000/health` 超时。
**根因**：之前通过 `terminal(background=true)` 启动的旧uvicorn进程仍占用8000端口，systemd新进程绑定失败。
**修复**：
```bash
# 杀了所有uvicorn再重启
pkill -f uvicorn
sleep 2
sudo systemctl restart jinjian-api
# 验证新进程
curl -s http://localhost:8000/health
```

### ④ 依赖缺失（ModuleNotFoundError）

**现象**：`journalctl -u jinjian-api` 显示 `ModuleNotFoundError: No module named 'fpdf'`。
**根因**：`systemd` 使用系统python3（/usr/bin/python3），而fpdf2安装在venv中。
**修复**：对系统python3单独安装：
```bash
sudo /usr/bin/python3 -m pip install fpdf2 --break-system-packages
```

**涉及依赖**：`fastapi`, `uvicorn`, `sqlite3`(内置), `slowapi`, `fpdf2`, `loguru`, `prometheus-client`, `Pillow`, `fonttools`

### ⑤ nginx配置冲突（conflicting server name）

**现象**：`nginx -t` 警告 `conflicting server name "_" on 0.0.0.0:80`。
**根因**：多个nginx sites-enabled同时监听80端口（hermes-webui/offerpath等）。
**修复**：禁用冲突站点
```bash
sudo rm -f /etc/nginx/sites-enabled/hermes-webui /etc/nginx/sites-enabled/offerpath
sudo nginx -t && sudo systemctl reload nginx
```

## 关键文件

| 文件 | 说明 |
|:----|:------|
| `/etc/systemd/system/jinjian-api.service` | systemd服务单元文件 |
| `/etc/nginx/sites-available/jinjian` | nginx站点配置 |
| `api/main.py` | FastAPI入口 |
| `api/services/engine_client.py` | 引擎subprocess调用封装（⚠️ 容易踩坑：确保pipeline_v5.py --json能正常返回） |
| `api/services/analysis_service.py` | 分析业务逻辑（⚠️ 必须传递result字段给前端） |
| `engine/pipeline_v5.py` | 核心管线（⚠️ format_21_section_report可能崩溃） |
| `frontend/src/views/InputPage.vue` | 输入表单页面 |
| `frontend/src/views/ReportPage.vue` | 报告展示页面（读 `this.report?.result?.sec_*`） |

## 注意事项

- nginx serve前端静态文件 + 反代API请求到uvicorn
- 静态文件（JS/CSS/图片）在 `frontend/dist/` 下，nginx设置了7天缓存
- systemd服务挂了自动重启（Restart=always），RestartSec=3秒
- 如需HTTPS → 用certbot申请证书，改nginx配置代理443端口
- 端口8000在腾讯云安全组中已开放（入站规则）
- **前端改动后需重新编译**：`cd frontend && npx vite build` 生成新的dist
- **service重启后检测OpenAPI是否生效**：`curl http://localhost:8000/openapi.json | jq '.components.schemas.AnalyzeResponse.properties | keys'`
