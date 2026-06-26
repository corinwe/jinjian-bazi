"""
数据库连接管理
支持SQLite（开发）和PostgreSQL（生产），通过配置切换
"""
import os, json, sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "bazi.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection() -> sqlite3.Connection:
    """获取数据库连接（每次调用返回新连接，线程安全）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")       # 写前日志，并发读
    conn.execute("PRAGMA foreign_keys=ON")        # 外键约束
    conn.execute("PRAGMA busy_timeout=5000")      # 锁等待5秒
    return conn


def init_db():
    """初始化数据库（建表）"""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema文件不存在: {SCHEMA_PATH}")
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    
    conn = get_connection()
    try:
        conn.executescript(schema)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def row_to_dict(row) -> dict:
    """将sqlite3.Row转为dict"""
    if row is None:
        return {}
    return dict(row)


def rows_to_dicts(rows) -> list[dict]:
    """将sqlite3.Row列表转为dict列表"""
    return [dict(r) for r in rows]


# ── Repository基类 ──
class BaseRepository:
    """数据访问基类"""
    
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        self._conn = conn
    
    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = get_connection()
        return self._conn
    
    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
