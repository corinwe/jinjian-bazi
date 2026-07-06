# ═══════════════════════════════════════════════
# 金鉴真人·八字排盘平台 — 项目配置/凭据
# 敏感信息！不要在对话中泄露完整token
# ═══════════════════════════════════════════════

## GitHub

- 仓库: corinwe/jinjian-bazi
- 完整PAT: 存于本地文件，未提交到Git（安全保护✅）
- PAT权限: repo + workflow（完整权限）
- 远程: 使用PAT认证的git remote

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

- 项目路径: projects/bazi-platform/
- API端口: 8000
- 服务地址: http://43.162.90.39:8000/
- API文档: http://43.162.90.39:8000/docs
- 启动命令: cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level warning
- 一键启动: cd /root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform && ./run.sh

## 知识库（人物档案存放）

```yaml
知识库路径: /root/weiwuji-knowledge-base
人物档案目录: 07-国学哲学/八字命格/02-人物档案/
编码规则: {序号}-{姓名}/（序号为当前目录最大号+1）
GitHub: git@github.com:corinwe/weiwuji-knowledge-base.git
```

## 铁律（物理强制规则）

```yaml
🔥 铁律① — 排盘必须跑引擎，禁止手算
  理由: 2026-06-29梦的日柱算错(壬戌→癸亥)教训
  强制: 任何八字分析前，必须先运行 paipan.py 或 pipeline_v5.py
  验证: 排盘输出必须与 engine/paipan.py 计算结果一致

🔥 铁律② — 知识库路径不依赖记忆
  理由: 错误提交到 bazi-platform/reports/ 的教训
  强制: 人物报告必须放到 weiwuji-knowledge-base/02-人物档案/

🔥 铁律③ — 所有规则不能依赖LLM记忆
  理由: 金鉴真人核心原则
  强制: 规则写在脚本/SKILL.md/config文件中，每次分析前加载

🔥 铁律④ — 报告必须按标准格式输出
  理由: bazi-report-template v5.2 定义了21§标准格式
  强制: 每次出报告前，必须先 skill_view('bazi-report-template')
        逐条对照模板格式，禁止自创格式
        21§板块必须齐全，深度≥1,500行

🔥 铁律⑤ — 财富判断必须完整应用全部规则（2026-07-01固化）
  理由: 老板多次纠正我只用部分规则(漏了围克折扣/墓库/大运冲库/合作伙伴等)
  强制: 任何财富分析前，先 skill_view('bazi-wealth-analysis')
        然后逐条检查§0~§17强制完整应用清单（全部打勾）
        完成后必须派独立Checker验证所有规则是否应用
        核心：发财=能量链条(比劫→食伤→财)完整且够力
        发财五法：①身强财旺 ②遇库 ③五鬼 ④禄神 ⑤大运流年补足(6种状态)
        合作伙伴：身强→财官食/身弱→印比+天乙贵人

🔥 铁律⑥ — 新知识学习必须走六步协议（2026-07-01固化）
  理由: 2026-07-01 老板教我财富规则时，我扫了几眼就以为学会了，
        实际上漏了能量链条/发财五法/搭档规则等核心内容。
        学习≠看过，学习=逐字精读+复述+举一反三+验证+汇报+入库。
  强制: 任何文档/音频/视频/链接/图片，先 skill_view('learning-protocol')
        然后走六步：①逐字精读 → ②用自己的话复述 → ③举一反三(≥3例)
        → ④派独立Checker验证 → ⑤向老板汇报查缺补漏
        → ⑥推库/更新技能/更新记忆
        全部完成后才可应用所学知识。
        禁止跳步骤、禁止扫读、禁止只看摘要。
```

## 项目结构

```
projects/bazi-platform/
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

- 全量验证: `cd projects/bazi-platform/engine/tests && python3 validate_all.py`
- **四柱校验**: **`python3 projects/bazi-platform/scripts/pillar-verify.py`** （分析结论发布前强制跑）
- 引擎测试: `cd projects/bazi-platform/engine && python3 tests/test_full_suite.py`
- 导入验证: `cd projects/bazi-platform/engine && python3 tests/test_imports.py`

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
