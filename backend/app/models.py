"""
数据模型 — SQLAlchemy ORM

用户体系:
  - User: 注册用户（手机号/微信）
  - Report: 八字分析报告（每次分析一条）
  - ReportVersion: 报告版本（报告更新历史）
  - Order: 订单/支付记录
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import hashlib
import jwt
import datetime
import os

from app.database import Base

# JWT密钥（生产环境应从环境变量读取）
JWT_SECRET = "jinjian-zhenren-bazi-dev-key"
JWT_ALGORITHM = "HS256"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)  # 手机号
    wechat_openid = Column(String(100), unique=True, index=True, nullable=True)  # 微信openid
    nickname = Column(String(50), default="用户")
    avatar = Column(String(200), nullable=True)
    password_hash = Column(String(200), nullable=True)
    
    # 会员体系
    level = Column(String(20), default="free")  # free, basic, premium, vip
    credits = Column(Integer, default=5)  # 剩余次数
    vip_expire = Column(DateTime, nullable=True)
    
    # 统计
    report_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联
    reports = relationship("Report", back_populates="user")
    orders = relationship("Order", back_populates="user")
    
    def set_password(self, password: str):
        """设置密码（SHA256哈希）"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self) -> str:
        """生成JWT token"""
        payload = {
            "user_id": self.id,
            "phone": self.phone,
            "level": self.level,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 用户输入的八字
    year_gan = Column(String(2), nullable=False)
    year_zhi = Column(String(2), nullable=False)
    month_gan = Column(String(2), nullable=False)
    month_zhi = Column(String(2), nullable=False)
    day_gan = Column(String(2), nullable=False)
    day_zhi = Column(String(2), nullable=False)
    hour_gan = Column(String(2), nullable=False)
    hour_zhi = Column(String(2), nullable=False)
    gender = Column(String(2), nullable=False)
    birth_year = Column(Integer, nullable=True)
    birth_month_lunar = Column(Integer, nullable=True)
    
    # 分析结果 (JSON)
    result_json = Column(Text, nullable=True)
    
    # 状态
    status = Column(String(20), default="completed")  # pending, completed, failed
    version = Column(String(10), default="2.0")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关联
    user = relationship("User", back_populates="reports")
    versions = relationship("ReportVersion", back_populates="report")
    
    @property
    def bazi_str(self) -> str:
        return f"{self.year_gan}{self.year_zhi} {self.month_gan}{self.month_zhi} {self.day_gan}{self.day_zhi} {self.hour_gan}{self.hour_zhi}"


class ReportVersion(Base):
    """报告版本记录"""
    __tablename__ = "report_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    version = Column(String(10), nullable=False)
    result_json = Column(Text, nullable=False)
    changelog = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    report = relationship("Report", back_populates="versions")


class Order(Base):
    """订单/支付记录"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_no = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)  # 金额(元)
    product = Column(String(50), nullable=False)  # 产品类型
    status = Column(String(20), default="pending")  # pending, paid, refunded
    payment_method = Column(String(30), nullable=True)  # 微信支付/支付宝
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="orders")
