-- 金鉴真人·八字命理分析平台 数据库结构 v1.0
-- 设计原则：预留扩展字段，JSON存储异构分析结果，索引全覆盖

-- ── 认证用户表（登录凭证）──
CREATE TABLE IF NOT EXISTS auth_users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 用户表 ──
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,                        -- 姓名
    gender          TEXT NOT NULL CHECK(gender IN ('男','女')),
    birth_year      INTEGER NOT NULL,                     -- 公历出生年
    birth_month     INTEGER NOT NULL,                     -- 公历出生月
    birth_day       INTEGER NOT NULL,                     -- 公历出生日
    birth_hour      INTEGER NOT NULL DEFAULT 0,           -- 出生时
    birth_minute    INTEGER NOT NULL DEFAULT 0,           -- 出生分

    -- 扩展字段（用户提供时才填，预留）
    calendar_type   TEXT DEFAULT 'solar',                  -- solar/lunar
    lunar_month     INTEGER,                               -- 农历月
    lunar_day       INTEGER,                               -- 农历日
    birth_place     TEXT,                                  -- 出生地（真太阳时预留）
    tags            TEXT,                                  -- 标签 JSON数组

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 八字分析主表 ──
CREATE TABLE IF NOT EXISTS analyses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),

    -- 八字原始数据
    bazi            TEXT NOT NULL,                         -- "庚申 癸未 辛亥 辛卯"
    year_pillar     TEXT NOT NULL,                         -- 年柱 "庚申"
    month_pillar    TEXT NOT NULL,                         -- 月柱 "癸未"
    day_pillar      TEXT NOT NULL,                         -- 日柱 "辛亥"
    hour_pillar     TEXT NOT NULL,                         -- 时柱 "辛卯"
    ri_zhu          TEXT NOT NULL,                         -- 日主 "辛"

    -- 版本号
    version         TEXT NOT NULL DEFAULT '1.0',
    engine_version  TEXT NOT NULL DEFAULT '1.0',

    notes           TEXT,                                  -- 用户备注
    status          TEXT DEFAULT 'pending',                 -- pending/completed/failed
    error_message   TEXT,                                  -- 失败原因

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 基础数据表（第一大步：11行×4列）──
CREATE TABLE IF NOT EXISTS basic_data (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id     INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,

    -- 四柱数据（每柱完整JSON）
    year_data       TEXT NOT NULL,  -- {shi_shen, tian_gan, di_zhi, cang_gan[], na_yin, kong_wang, shen_sha[]}
    month_data      TEXT NOT NULL,
    day_data        TEXT NOT NULL,
    hour_data       TEXT NOT NULL,

    -- 日主信息
    ri_zhu_gan      TEXT NOT NULL,
    ri_zhu_wx       TEXT NOT NULL,  -- 五行
    ri_zhu_yy       TEXT NOT NULL,  -- 阴阳

    -- 干支留意（JSON数组）
    tian_gan_notes  TEXT,           -- 天干五合/冲 ["丙辛合水", ...]
    di_zhi_notes    TEXT,           -- 刑冲合害 ["亥卯未合木", "申亥相害", ...]

    -- 称骨
    cheng_gu_weight TEXT,           -- "1两3钱"
    cheng_gu_comment TEXT,          -- 评语

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 分析结果表（第二大步：规则引擎输出，JSON存储易于扩展）──
CREATE TABLE IF NOT EXISTS analysis_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id     INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,

    -- 各维度分析结果（JSON）
    shen_qiang_ruo  TEXT,            -- 身强弱 {score, label, details{}}
    cai_xing        TEXT,            -- 财星 {total, details{}}
    ge_ju           TEXT,            -- 格局 {main, extra[], special}
    xi_yong_shen    TEXT,            -- 喜用神 {xi[], ji[], tiao_hou}
    energy          TEXT,            -- 五行能量 {wu_xing{}, strongest, weakest}
    da_yun          TEXT,            -- 大运 [{gan_zhi, start, end, rating}, ...]
    dimensions      TEXT,            -- 8维度 {财富, 事业, 婚姻, ...}
    shen_sha_detail TEXT,            -- 神煞详表

    -- 预留扩展字段（流月/流日未来加，不改表结构）
    liu_nian        TEXT,            -- 流年分析（已有引擎模块）
    liu_yue         TEXT,            -- 流月分析（预留）
    liu_ri          TEXT,            -- 流日分析（预留）
    extra           TEXT,            -- 额外扩展（JSON，任意扩展）

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 报告表 ──
CREATE TABLE IF NOT EXISTS reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id     INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id),

    -- 报告内容
    format          TEXT NOT NULL DEFAULT 'markdown',
    content         TEXT NOT NULL,                         -- 报告正文

    -- 版本信息
    version         TEXT NOT NULL DEFAULT '1.0',
    is_latest       INTEGER DEFAULT 1,                      -- 1=最新版

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── 索引 ──
CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_bazi ON analyses(bazi);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_basic_data_analysis ON basic_data(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis ON analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_reports_analysis_id ON reports(analysis_id);
CREATE INDEX IF NOT EXISTS idx_reports_is_latest ON reports(is_latest);
