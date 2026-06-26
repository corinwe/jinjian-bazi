# 金鉴真人·八字命理分析平台 架构设计文档 v1.0

## 一、整体架构（三层分离）

```
┌──────────────────────────────────────────────────────┐
│                      前端层                          │
│           Frontend (SPA / 小程序 / H5)              │
│  - 纯展示，不参与任何计算                            │
│  - 通过 RESTful API 获取数据                         │
│  - 可独立部署 (CDN / Nginx)                         │
└──────────────────────┬───────────────────────────────┘
                       │ HTTP/JSON
                       ▼
┌──────────────────────────────────────────────────────┐
│                       API层                          │
│            Backend (FastAPI + SQLite/PG)             │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │
│  │ Router层   │→│ Service层  │→│ 规则引擎调用   │  │
│  │ (路由分发)  │  │ (业务逻辑)  │  │ (异步subprocess)│  │
│  └────────────┘  └────────────┘  └───────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────┐      │
│  │ 数据访问层 (Repository Pattern)            │      │
│  │ - 用户 CRUD                                │      │
│  │ - 报告 CRUD + 版本管理                     │      │
│  │ - 缓存管理                                 │      │
│  └────────────────────────────────────────────┘      │
└──────────────────────┬───────────────────────────────┘
                       │ SQL / 进程调用
                       ▼
┌──────────────────────────────────────────────────────┐
│                    数据层                             │
│          Database + Config + 规则引擎                 │
│                                                      │
│  ┌────────────────┐  ┌──────────────────────────┐   │
│  │ SQLite/PG      │  │ 规则引擎 engine/         │   │
│  │ - 用户表        │  │ - 完全确定性计算         │   │
│  │ - 报告表        │  │ - 可独立运行 (CLI)      │   │
│  │ - 版本历史      │  │ - 从 config/* 读配置    │   │
│  │ - (预留)流月分析 │  │                         │   │
│  │ - (预留)流日分析 │  └──────────────────────────┘   │
│  └────────────────┘                                   │
└──────────────────────────────────────────────────────┘
```

## 二、数据库设计

### 2.1 核心表

```sql
-- 用户表
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,              -- 姓名
    gender        TEXT NOT NULL CHECK(gender IN ('男','女')),
    birth_year    INTEGER NOT NULL,           -- 公历出生年
    birth_month   INTEGER NOT NULL,           -- 公历出生月
    birth_day     INTEGER NOT NULL,           -- 公历出生日
    birth_hour    INTEGER NOT NULL DEFAULT 0,  -- 出生时
    birth_minute  INTEGER NOT NULL DEFAULT 0,  -- 出生分
    
    -- 扩展字段（预留）
    calendar_type TEXT DEFAULT 'solar',        -- solar/lunar（日历类型）
    lunar_month   INTEGER,                     -- 农历月（用户提供时才填）
    lunar_day     INTEGER,                     -- 农历日（用户提供时才填）
    birth_place   TEXT,                        -- 出生地（真太阳时用，预留）
    
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 八字分析主表（每次分析一条记录）
CREATE TABLE analyses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    
    -- 八字原始数据
    bazi            TEXT NOT NULL,             -- "庚申 癸未 辛亥 辛卯"
    year_pillar     TEXT NOT NULL,             -- 年柱 "庚申"
    month_pillar    TEXT NOT NULL,             -- 月柱 "癸未"
    day_pillar      TEXT NOT NULL,             -- 日柱 "辛亥"
    hour_pillar     TEXT NOT NULL,             -- 时柱 "辛卯"
    ri_zhu          TEXT NOT NULL,             -- 日主 "辛"
    
    -- 版本号
    version         TEXT NOT NULL DEFAULT '1.0',
    engine_version  TEXT NOT NULL DEFAULT '1.0',
    
    -- 备注
    notes           TEXT,                      -- 用户备注
    tags            TEXT,                      -- 标签（JSON数组）
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 基础数据表（第1大步的11行×4列，JSON存储）
CREATE TABLE basic_data (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id     INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    
    -- 四柱数据（JSON，每柱包含十神/天干/地支/藏干/纳音/空亡/神煞）
    year_data       TEXT NOT NULL,
    month_data      TEXT NOT NULL,
    day_data        TEXT NOT NULL,
    hour_data       TEXT NOT NULL,
    
    -- 日主信息
    ri_zhu_gan      TEXT NOT NULL,
    ri_zhu_wx       TEXT NOT NULL,             -- 五行
    ri_zhu_yy       TEXT NOT NULL,             -- 阴阳
    
    -- 干支留意（JSON数组）
    tian_gan_notes  TEXT,                      -- 天干五合/冲
    di_zhi_notes    TEXT,                      -- 刑冲合害
    
    -- 称骨
    cheng_gu_weight TEXT,
    cheng_gu_comment TEXT,
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分析结果表（第2大步，JSON存储，易于扩展）
CREATE TABLE analysis_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id     INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    
    -- 各维度分析结果（JSON，每项包含：原局分+大运赋能+总分+等级描述）
    shen_qiang_ruo  TEXT,                      -- 身强弱评分
    cai_xing        TEXT,                      -- 财星评分
    ge_ju           TEXT,                      -- 格局
    xi_yong_shen    TEXT,                      -- 喜用神
    energy          TEXT,                      -- 五行能量
    da_yun          TEXT,                      -- 大运（JSON数组，每步干支+年份+评级）
    dimensions      TEXT,                      -- 8维度评分
    shen_sha_detail TEXT,                      -- 神煞详情
    
    -- 预留扩展字段（流月/流日将来加在这里）
    liu_nian        TEXT,                      -- 流年分析（预留）
    liu_yue         TEXT,                      -- 流月分析（预留）
    liu_ri          TEXT,                      -- 流日分析（预留）
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 报告表
CREATE TABLE reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id     INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    
    -- 报告内容
    format          TEXT NOT NULL DEFAULT 'markdown',  -- markdown/html/json
    content         TEXT NOT NULL,             -- 报告正文
    summary         TEXT,                      -- 摘要（前情提要）
    
    -- 版本信息
    version         TEXT NOT NULL DEFAULT '1.0',
    is_latest       INTEGER DEFAULT 1,         -- 是否最新版
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_bazi ON analyses(bazi);
CREATE INDEX idx_reports_analysis_id ON reports(analysis_id);
CREATE INDEX idx_reports_is_latest ON reports(is_latest);
```

### 2.2 设计思路

```
为什么用JSON字段存储分析结果，而不是用单独表？
- 每个分析模块的输出结构不同（身强弱有明细字段，财星有逐项，大运有数组）
- JSON天然可以容纳异构数据，扩展时只需加字段，不需要改表结构
- 预留liu_yue/liu_ri字段，未来加流月/流日分析直接填JSON即可
- 不牺牲查询性能（通过analysis_id索引，每次查整条记录）

为什么user_id不冗余？
- 分析结果和报告都直接用analysis_id关联analysis表
- analysis表再关联user_id，减少数据冗余
- 查询时join分析时间短（数据量不大）
```

## 三、API设计

### 3.1 路由结构

```
POST   /api/v1/analyze              # 提交八字分析
GET    /api/v1/analyses/{id}        # 获取分析结果
GET    /api/v1/analyses/{id}/report # 获取报告（渲染好的）
GET    /api/v1/users/{id}/analyses  # 获取用户历史分析

# 管理员/调试
GET    /api/v1/ping                 # 健康检查
GET    /api/v1/engine/version       # 规则引擎版本
POST   /api/v1/engine/debug         # 调试模式（输出完整JSON）
```

### 3.2 输入Schema

```json
// POST /api/v1/analyze
{
    "name": "张三",
    "gender": "男",
    "birth_year": 1980,
    "birth_month": 8,
    "birth_day": 6,
    "birth_hour": 6,
    "birth_minute": 0,
    
    // 以下可选
    "calendar_type": "solar",       // "solar" 或 "lunar"
    "lunar_month": 6,               // 如果calendar_type="lunar"
    "lunar_day": 26,                // 如果calendar_type="lunar"
    "birth_place": "北京",           // 真太阳时（预留）
    "tags": ["家族", "老板"],        // 标签
    "notes": "家主"
}
```

### 3.3 输出Schema

```json
// 200 Response
{
    "analysis_id": 1,
    "status": "completed",
    "basic": {
        "bazi": "庚申 癸未 辛亥 辛卯",
        "pillars": { /* 四柱 */ },
        "ri_zhu": { "gan": "辛", "wu_xing": "金", "yin_yang": "阴" },
        "kong_wang": { "year": "子丑", "month": "申酉", "day": "寅卯", "hour": "午未" },
        "shen_sha": { "year": [...], "month": [...], "day": [...], "hour": [...] },
        "na_yin": { "year": "石榴木", ... },
        "tian_gan_notes": [],
        "di_zhi_notes": ["申亥相害", "亥卯未合木", ...],
        "cheng_gu": { "weight": "1两3钱", "comment": "..." }
    },
    "analysis": {
        "shen_qiang_ruo": { "score": 73.6, "level": "身强", ... },
        "cai_xing": { "total": 31.2, ... },
        "ge_ju": { "main": "偏印格", ... },
        "xi_yong_shen": { "xi": ["水", "金"], "ji": ["土", "火"] },
        "da_yun": [{"gan_zhi": "甲申", "start": 1981, "end": 1990, "rating": "佳"}, ...],
        "dimensions": { "财富": 7.5, "事业": 6.8, ... }
    },
    "report_url": "/api/v1/analyses/1/report"
}
```

## 四、模块间通信

```
       前端                     API服务                    规则引擎
    ┌────────┐              ┌──────────┐              ┌──────────┐
    │ HTTP   │ ──POST─────▶ │ Router   │ ──调用─────▶ │ shell/   │
    │ 请求   │              │ →Service │              │ subprocess│
    │        │              │ →Repository            │ (独立进程) │
    │        │ ◀───JSON───  │          │ ◀───JSON───  │          │
    └────────┘              └──────────┘              └──────────┘
                                │
                                ▼
                           ┌──────────┐
                           │Database  │
                           │SQLite/PG │
                           └──────────┘
```

**关键设计决策：**

1. **规则引擎独立进程**：API通过subprocess调用pipeline_product.py，引擎不依赖API层，可单独测试和部署
2. **异步非阻塞**：FastAPI异步处理请求，引擎调用用run_in_executor不阻塞事件循环
3. **缓存策略**：相同八字+性别=相同结果，可以用analysis_id缓存（LRU cache）
4. **并发**：引擎调用是CPU密集型，用进程池（ProcessPoolExecutor）避免GIL限制

## 五、目录结构（最终版）

```
/root/bazi-platform/
├── database/                   # 数据层
│   ├── schema.sql              # 数据库建表SQL
│   ├── connection.py           # 数据库连接管理
│   └── migrations/             # 迁移历史
│       └── 001_init.sql
│
├── engine/                     # 规则引擎（纯计算，无外部依赖）
│   ├── config/                 # 配置文件
│   │   ├── cang_gan.json
│   │   ├── na_yin.json
│   │   ├── kong_wang.json
│   │   ├── shen_sha_rules.json
│   │   ├── cheng_gu.json
│   │   └── neng_liang.json
│   ├── step1_basic.py          # 第一大步：11行×4列基础数据
│   ├── step2_analysis.py       # 第二大步：分析模块（待集成）
│   ├── pipeline_product.py     # 产品级流水线（CLI入口）
│   ├── shi_shen.py
│   ├── shen_qiang_ruo.py
│   ├── cai_xing.py
│   ├── ge_ju.py
│   ├── da_yun.py
│   ├── energy.py
│   ├── xing_chong_he_hua.py
│   ├── shen_sha.py
│   ├── liu_nian.py
│   └── dimensions.py
│
├── api/                        # API服务端（Flask/FastAPI）
│   ├── requirements.txt
│   ├── main.py                 # 应用入口
│   ├── config.py               # 服务配置
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── analyze.py          # 八字分析路由
│   │   ├── reports.py          # 报告路由
│   │   └── health.py           # 健康检查
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py          # 请求Schema
│   │   └── response.py         # 响应Schema
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py # 分析业务逻辑
│   │   ├── engine_client.py    # 规则引擎调用封装
│   │   └── report_service.py   # 报告生成
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repo.py        # 用户数据访问
│   │   ├── analysis_repo.py    # 分析数据访问
│   │   └── report_repo.py      # 报告数据访问
│   └── tests/
│       ├── test_analyze.py
│       └── test_engine_integration.py
│
├── frontend/                   # 前端
│   ├── index.html
│   ├── assets/
│   │   ├── style.css
│   │   └── app.js
│   └── README.md
│
├── docs/                       # 文档
│   └── architecture.md         # 本文件
│
└── README.md                   # 项目说明
```

## 六、扩展性设计

### 6.1 流月/流日扩展（预留）

```sql
-- 当前 analysis_results 表已预留字段
liu_nian  TEXT,   -- 已有（流年分析）
liu_yue   TEXT,   -- 已预留（流月分析） 
liu_ri    TEXT,   -- 已预留（流日分析）
```

未来接入流月/流日分析时：
1. 规则引擎新增 `step3_liuyue.py` 模块
2. 输出JSON直接填进 `liu_yue` 字段
3. API返回新增字段
4. 前端新增展示板块
5. **不需要改表结构，不需要迁移数据库**

### 6.2 新增分析维度

未来如需新增维度（如健康/六亲/风水等）：
1. 规则引擎新增 `step4_xxx.py`
2. `analysis_results` 表新增字段（ALTER TABLE）
3. 新增路由/Service方法
4. 前端新增展示

### 6.3 并发扩展

- 当前：SQLite（单机够用，几千并发以内没问题）
- 未来量大了：换 PostgreSQL（SQL语法兼容）
- 规则引擎无状态，可水平扩展（多进程/多机器）
- API层用 FastAPI 异步 + uvicorn workers
