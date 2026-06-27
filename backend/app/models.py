"""数据库模型 — 含将来收费/会员预留"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Enum as SAEnum
from app.database import Base
import enum


class ReportType(str, enum.Enum):
    BASIC = "basic"        # 基础版(免费)
    PREMIUM = "premium"    # 详细版(付费)


class Gender(str, enum.Enum):
    MALE = "男"
    FEMALE = "女"


class MemberLevel(str, enum.Enum):
    FREE = "free"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


# ─── 用户表(将来) ──────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(200), nullable=True)
    member_level = Column(SAEnum(MemberLevel), default=MemberLevel.FREE)
    member_expire_at = Column(DateTime, nullable=True)
    total_reports = Column(Integer, default=0)
    free_reports_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


# ─── 生辰信息表 ────────────────────────────────────────────
class BirthInfo(Base):
    __tablename__ = "birth_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # 可为空(未登录)
    session_id = Column(String(100), index=True, nullable=True)  # 匿名用户标识
    name = Column(String(50), nullable=False)
    gender = Column(SAEnum(Gender), nullable=False)
    birth_year = Column(Integer, nullable=False)
    birth_month = Column(Integer, nullable=False)
    birth_day = Column(Integer, nullable=False)
    birth_hour = Column(Integer, nullable=True)
    birth_minute = Column(Integer, default=0)
    is_lunar = Column(Boolean, default=False)  # True=农历 False=公历
    birthplace = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ─── 报告表 ────────────────────────────────────────────────
class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    birth_info_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(100), index=True, nullable=True)
    report_type = Column(SAEnum(ReportType), default=ReportType.BASIC)
    title = Column(String(200))
    content_md = Column(Text)  # Markdown完整报告
    content_html = Column(Text)  # HTML格式(用于展示+PDF)
    line_count = Column(Integer, default=0)
    is_paid = Column(Boolean, default=False)
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ─── 订单表(将来) ──────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    report_id = Column(Integer, nullable=True)
    amount = Column(Float, default=0)
    payment_method = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")  # pending/paid/refunded
    trade_no = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)


# ─── 会员订阅表(将来) ──────────────────────────────────────
class Membership(Base):
    __tablename__ = "memberships"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    level = Column(SAEnum(MemberLevel), default=MemberLevel.FREE)
    price = Column(Float, default=0)
    start_at = Column(DateTime, nullable=False)
    expire_at = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, default=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
