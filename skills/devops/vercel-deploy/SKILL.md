---
name: vercel-deploy
description: Vercel官方部署指南——项目配置、环境变量、预览部署、生产部署、域名设置。来自vercel-labs/agent-skills(28.4K⭐)
category: devops
---

# Deploy to Vercel (Vercel官方部署指南)

## 概述

使用Vercel部署前端应用的最佳实践。自动部署、预览环境、环境变量管理和域名配置。

## 项目配置

### vercel.json
```json
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "devCommand": "next dev"
}
```

### 环境变量
在Vercel仪表板或vercel CLI中设置：
```bash
vercel env add DATABASE_URL production
vercel env add API_KEY development
```

## 部署工作流

### 自动部署
- 每个推送到main分支 → 自动部署到生产环境
- 每个PR → 自动创建预览部署
- 预览部署有唯一的URL

### 预览部署
```bash
# 每个PR自动生成
https://my-app-git-feature-login-org.vercel.app
```

## CI/CD配置

### GitHub集成
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./
```
