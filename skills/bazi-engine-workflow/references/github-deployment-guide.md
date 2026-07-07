# 金鉴真人·GitHub部署与服务器运维指南

> 创建时间：2026-06-26
> 用途：将bazi-platform推送到GitHub并在服务器上部署

## 仓库初始化

```bash
git config --global user.name "corinwe"
git config --global user.email "corinwe@users.noreply.github.com"
cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform
git init
echo '__pycache__/
*.pyc
*.db-shm
*.db-wal
*.db
.env
.venv/
venv/
.DS_Store
*.log
output/' > .gitignore
git add -A
git commit -m "金鉴真人·八字命理分析平台 v5.0 - 确定性规则引擎"
gh repo create jinjian-zhenren-engine --public --description "金鉴真人·八字命理确定性规则引擎" --source . --remote origin --push
```

## 服务器部署

```bash
# Docker方式
docker build -t jinjian-zhenren:latest .
docker run -d --name jinjian-zhenren --restart unless-stopped -p 80:8000 -v jinjian-data:/app/database jinjian-zhenren:latest

# 直接部署
cd /opt/jinjian-zhenren && PYTHONPATH=/opt/jinjian-zhenren:$PYTHONPATH python3 -m uvicorn api.main:app --host 0.0.0.0 --port 80

# Supervisor管理
```

## API端点

GET /ping - 健康检查
POST /api/v1/analyze - 全量分析
POST /api/v1/engine/debug - 调试JSON
GET /  - 前端首页

## 踩坑

1. PYTHONPATH必须设置
2. Docker重启数据库丢失 → 挂载volume
3. 端口冲突检查 `lsof -i:80`
