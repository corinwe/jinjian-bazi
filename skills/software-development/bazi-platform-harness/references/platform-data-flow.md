# 八字排盘平台 · 数据流架构

> 引擎→报告→API→前端 完整链路

## 核心数据流

```
用户输入(姓名/性别/公历日期/时辰)
    │
    ▼
┌─────────────────────┐
│  API/routers/analyze │  ← FastAPI端点
│  农历→公历转换      │      _ensure_solar_date()
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  API/services/       │  ← AnalysisService.analyze()
│  engine_client.py    │      call_engine()
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  engine/paipan.py    │  ← 排盘 → 四柱八字
│  公历+时辰→八字     │      返回dict{bazi, pillars...}
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  engine/pipeline_v5  │  ← run_v5() 核心分析流水线
│  │                   │      调用所有子模块
│  ├─ shen_qiang_ruo   │      身强弱评分
│  ├─ cai_xing         │      财星计算
│  ├─ ge_ju            │      格局判定
│  ├─ da_yun           │      大运计算
│  ├─ shen_sha         │      神煞
│  ├─ energy           │      五行能量
│  ├─ wealth_v2        │      财富分析
│  ├─ career_v2        │      事业分析
│  ├─ marriage_v2      │      婚姻分析
│  ├─ education_v2     │      学历分析
│  ├─ children_v2      │      子女分析
│  ├─ health_v2        │      健康分析
│  ├─ liu_nian_v2      │      流年分析
│  ├─ dimensions_v2    │      八维评分
│  └─ xing_chong_he_hua│      刑冲合害
│                      │
│  输出: dict(21§完整)  │      sec_1_overview ~ sec_21_advice
└─────────┬───────────┘
          │
          ├──────────────────┐
          ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│  engine/          │  │  API返回JSON     │
│  report_generator │  │  → 前端渲染      │
│  .py              │  │  (index.html)    │
│  generate_report  │  │  renderReport()  │
│  → 640行文本      │  │  → 21§HTML展示   │
│  → /api/v1/report │  │  → /api/v1/      │
│                     │  │    engine/debug  │
└──────────────────┘  └──────────────────┘
```

## 引擎模块清单

| 文件 | 行数 | 功能 |
|------|:----:|------|
| paipan.py | 6,989 | 公历→八字排盘 |
| shen_qiang_ruo.py | 11,321 | 身强弱评分(月令印40/比劫全计/燥土条件) |
| cai_xing.py | 4,730 | 财星计算(正偏财) |
| shi_shen.py | 4,217 | 十神判定 |
| ge_ju.py | 8,120 | 格局判定 |
| da_yun.py | 6,096 | 大运计算 |
| constants.py | 7,845 | 常量/类型定义 |
| shen_sha.py | 9,103 | 神煞计算 |
| energy.py | 4,784 | 五行能量 |
| xing_chong_he_hua.py | 7,657 | 刑冲合害 |
| pipeline_v5.py | 27,880 | 全量分析流水线 + 报告格式化 |
| report_generator.py | 29,013 | 文本报告生成(深版+标准版) |
| dimensions_v2.py | 7,805 | 八维评分 |
| wealth_v2.py | 7,396 | 财富分析 |
| career_v2.py | 15,323 | 事业分析 |
| marriage_v2.py | 11,882 | 婚姻分析 |
| education_v2.py | 11,761 | 学历分析 |
| children_v2.py | 56,518 | 子女分析 |
| health_v2.py | 64,689 | 健康分析 |
| misfortune_analysis.py | 9,639 | 灾祸分析 |
| liu_nian_v2.py | 17,253 | 流年分析 |
| comprehensive_v2.py | 37,790 | 综合报告 |
| **总计** | **~12,437行** | **22个主模块** |

## API端点(当前版本5.0.0)

| 端点 | 方法 | 输入 | 输出 |
|------|------|------|------|
| /ping | GET | — | {"status":"ok"} |
| /health | GET | — | 引擎模块级健康检查, 含各模块存在性 |
| /version | GET | — | 版本+引擎状态 |
| /docs | GET | — | Swagger UI OpenAPI文档 |
| /api/v1/analyze | POST | {name,gender,birth_year,birth_month,birth_day,birth_hour,calendar_type} | 结构化JSON(含全部21§数据) |
| /api/v1/report | POST | 同上 | 文本报告(640行/12K字) |
| /api/v1/engine/debug | POST | 同上 | 引擎原始JSON(paipan+basic_data+result) |

## 验证体系

| 验证 | 位置 | 内容 | 触发 |
|------|------|------|------|
| test_imports.py | engine/tests/ | 19模块导入+预期函数验证 | 手动 |
| test_full_suite.py | engine/tests/ | 320条引擎测试 | 手动/CI |
| validate_all.py | engine/tests/ | 26项全量验证(引擎+API+前端+农历+格式) | 每次提交前必跑 |
| test_imports | engine/tests/ | 模块导入完整性 | 手动 |

## 报告标准输出格式

报告的21§结构由 `bazi-report-template` v5.2 定义，输出形态有两种：

1. **API JSON** (`/api/v1/analyze`) → 结构化JSON，包含 `basic` + `analysis` 两个对象
2. **文本报告** (`/api/v1/report`) → `report_generator.py` 生成的640行+文本
3. **前端HTML** → `index.html` 的 `renderReport()` 函数从JSON渲染为HTML

三种形态的§顺序、内容、深度必须与 `bazi-report-template` v5.2 一致。

## 关键踩坑记录

### 1. Git PAT workflow scope
- 推 `.github/workflows/*` 文件需要 PAT 有 `workflow` scope
- 只有 `repo` scope 会被拒绝 → 方案：workflow 文件放 `docs/` 目录

### 2. 配置信息存文件不存记忆
- 重要信息(PAT/服务器IP/项目路径)必须存独立文件
- 记忆只存指针("去哪个文件找")

### 3. API后台进程管理
- 🔥 禁止在foreground terminal中使用 `&` 或 `nohup`
- 必须用 `terminal(background=true)` 启动
- 测试用 `curl` 在单独的 `terminal()` 调用中执行

### 4. paipan()函数签名
```python
paipan(name, gender, birth_year, birth_month, birth_day, birth_hour) -> dict
# 返回dict, 不是BaZi对象
# 返回的pillars是dict: year_pillar={'gan':'辛','zhi':'卯'}
# 要得到BaZi对象需手动构造:
bazi = BaZi(
    year=Pillar(r['year_pillar']['gan'], r['year_pillar']['zhi']),
    ...
)
```

### 5. run_pipeline vs run_v5
- `run_pipeline(name, gender, year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi, hour_gan, hour_zhi)` → 直接调用
- `run_v5(bazi_obj, birth_year, birth_month_lunar, qi_yun_days)` → 需要BaZi对象
- 后者是完整的全量分析入口

### 6. 前端获取数据的两种方式
- `/api/v1/analyze` → 结构化JSON(含basic+analysis两部分)
- `/api/v1/engine/debug` → 原始引擎JSON(含paipan+basic_data+result=21§)
- 前端 `index.html` 使用的是 `/api/v1/engine/debug` 获取全部数据
