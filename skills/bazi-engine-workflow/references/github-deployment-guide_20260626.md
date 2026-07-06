# GitHub部署与代码管理（2026-06-26实战沉淀）

## 凭证管理

**优先使用经典PAT**（`ghp_`开头）：
- 兼容 git push HTTPS，支持 `gh repo create`
- 细粒度PAT（`github_pat_`开头）需要额外权限，不能直接创建仓库

快速验证：`curl -s -H "Authorization: token ghp_xxx" https://api.github.com/user`

## 创建并推送仓库

```bash
# 1. 创建仓库（用API）
curl -s -H "Authorization: token ghp_xxx" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/user/repos \
  -d '{"name":"jinjian-bazi","description":"项目描述","private":false}'

# 2. 初始化并推送
cd /project
git init
git branch -m main
git remote add origin https://username:ghp_xxx@github.com/username/jinjian-bazi.git
git add -A
git commit -m "🎯 项目初始化描述"
git push -u origin main

# 3. 验证
git log --oneline -1
git ls-remote origin main | head -1
```

## 服务器部署

```bash
cd /root/bazi-platform
export PYTHONPATH=/root/bazi-platform:$PYTHONPATH
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level warning

# 验证
curl -s http://localhost:8000/ping
curl -s http://localhost:8000/api/v1/engine/debug -X POST -H "Content-Type: application/json" \
  -d '{"name":"测试","gender":"男","birth_year":1980,"birth_month":7,"birth_day":15,"birth_hour":4}'
```

## Docker部署

```bash
docker build -t jinjian-bazi /root/bazi-platform
docker run -p 8000:8000 jinjian-bazi
```

## 踩坑记录

1. **Token被Hermes mask**：终端输出显示 `ghp_...xxx` 是正常行为，不代表token无效
2. **GitHub禁纯密码HTTPS**：2021年起必须用token替代密码，格式 `https://username:token@github.com/...`
3. **.gitignore必备**：`.db`, `.env`, `__pycache__/`, `output/`, `node_modules/`
4. **信息泄露敏感**：token不应硬编码在代码或提交记录中

## 老板模式

> 「开工 所有缺失的补都补上」= 自己扫描全系统找不完备，列优先级全修完，测试通过再汇报，不逐条问。
