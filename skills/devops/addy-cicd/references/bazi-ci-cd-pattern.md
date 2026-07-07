# CI/CD 工作流参考（金鉴真人·八字平台实战）

## GitHub Actions 三阶段管道

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  # Phase 1: 验证
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5 with python-version: '3.11' cache: pip
      - run: pip install -r api/requirements.txt
      - run: cd engine && python3 tests/test_imports.py
      - run: cd engine && python3 tests/test_full_suite.py
      - run: cd engine && python3 tests/validate_all.py

  # Phase 2: 构建
  build:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v5
        with: context: . push: false tags: app:latest

  # Phase 3: 部署
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && git pull && pip install -r api/requirements.txt
            cd engine && python3 tests/validate_all.py
            pkill -f "uvicorn api.main" || true
            nohup python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level warning &
            sleep 2 && curl -s http://localhost:8000/health | grep '"status":"healthy"'
```

## 需要配置的 GitHub Secrets

| Secret | 用途 |
|--------|------|
| `DEPLOY_HOST` | 服务器IP |
| `DEPLOY_USER` | SSH用户名 |
| `DEPLOY_KEY` | SSH私钥 |

## 注意

- PAT必须有 `workflow` scope 才能推 `.github/workflows/*.yml` 文件
- 无workflow scope时：可将workflow文件放在 `docs/` 目录，手动配置
