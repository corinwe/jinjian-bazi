# ═══════════════════════════════════════════════
# 金鉴真人·八字排盘平台 — 项目配置/凭据
# 敏感信息！不要在对话中泄露完整token
# ═══════════════════════════════════════════════

## GitHub

- 仓库: corinwe/jinjian-bazi
- 完整PAT: ghp_zM...swnG（已存memory，此处不重复明文）
- PAT权限: repo（完整） + workflow（需要手动在GitHub Settings加）
- 远程: https://corinwe:{PAT}@github.com/corinwe/jinjian-bazi.git

### PAT注意事项
- 推 workflow 文件（.github/workflows/*）需要 `workflow` scope
- 当前PAT有 `repo` scope → 推代码ok，推workflow文件不行
- CI/CD的workflow文件已存 `docs/ci-cd.yml`，需要复制到 `.github/workflows/` 并配secrets

### GitHub Secrets 需要配置（用于自动部署）
| Secret | 说明 |
|--------|------|
| DEPLOY_HOST | 服务器IP |
| DEPLOY_USER | 服务器用户名 |
| DEPLOY_KEY | SSH私钥 |

## 部署

- 项目路径: /root/bazi-platform/
- API端口: 8000
- 服务地址: http://43.162.90.39:8000/
- API文档: http://43.162.90.39:8000/docs
- 启动命令: cd /root/bazi-platform && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level warning
- 一键启动: cd /root/bazi-platform && ./run.sh

## 项目结构

```
/root/bazi-platform/
├── engine/           # 规则引擎（12,437行Python，36模块）
│   ├── paipan.py         # 排盘
│   ├── shen_qiang_ruo.py # 身强弱计算
│   ├── pipeline_v5.py    # 全量报告流水线
│   ├── cai_xing.py       # 财星
│   ├── dimensions_v2.py  # 八维评分
│   ├── wealth_v2.py      # 财富分析
│   ├── career_v2.py      # 事业分析
│   ├── marriage_v2.py    # 婚姻分析
│   ├── education_v2.py   # 学业分析
│   ├── children_v2.py    # 子女分析
│   ├── health_v2.py      # 健康分析
│   ├── da_yun.py         # 大运计算
│   ├── liu_nian_v2.py    # 流年分析
│   ├── report_generator.py # 报告生成器
│   ├── constants.py      # 常量/类型定义
│   ├── config/           # 配置文件
│   └── tests/            # 测试
│       ├── validate_all.py     # 全量26项验证
│       ├── test_full_suite.py  # 320条引擎测试
│       └── test_imports.py     # 19模块导入验证
├── api/              # FastAPI服务
│   ├── main.py           # 入口 + OpenAPI配置
│   ├── routers/          # 路由（health, analyze）
│   ├── schemas/          # 请求/响应模型
│   ├── services/         # 业务逻辑
│   └── repositories/     # 数据访问
├── frontend/         # 前端SPA
│   └── index.html        # 515行SPA（暗金配色、移动优先）
├── database/         # SQLite数据库
├── docs/             # 文档
│   └── ci-cd.yml         # CI/CD workflow配置
├── Dockerfile        # 生产Docker镜像
└── run.sh            # 一键启动脚本
```

## 验证流水线

- 全量验证: `cd /root/bazi-platform/engine/tests && python3 validate_all.py`
- 引擎测试: `cd /root/bazi-platform/engine && python3 tests/test_full_suite.py`
- 导入验证: `cd /root/bazi-platform/engine && python3 tests/test_imports.py`

### 26项验证覆盖
1-4: 引擎320测试 + 排盘正确性(身强弱/财星/paipan)
5-8: API端点(/ping /version /debug /report)  
9-11: 21§完整性(21/21覆盖 + 552行)
12-18: 格式对齐(版本说明+25字段+白话+五行颜色+财富五级+建议+署名)
19-22: 农历转换(4项)
23-26: 前端(加载+四柱+分析+PDF)

## API端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ping | 存活检查 |
| GET | /health | 详细健康检查（含引擎模块状态） |
| GET | /version | 版本信息 |
| POST | /api/v1/analyze | 八字分析（完整JSON） |
| GET | /api/v1/analyses/{id} | 获取历史分析 |
| GET | /api/v1/users/{user_id}/analyses | 用户分析列表 |
| POST | /api/v1/engine/debug | 调试模式（引擎原始JSON） |
| POST | /api/v1/report | 生成完整21§报告（文本） |
| GET | /docs | Swagger UI文档 |
| GET | /openapi.json | OpenAPI规范 |
