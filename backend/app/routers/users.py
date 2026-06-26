"""用户路由: 注册/登录/信息"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse, UserInfo
from app.auth import get_current_user, require_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查手机号是否已注册
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")
    
    user = User(
        phone=data.phone,
        nickname=data.nickname or f"用户{data.phone[-4:]}",
        level="free",
        credits=5,
    )
    user.set_password(data.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = user.generate_token()
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        nickname=user.nickname,
        level=user.level,
        credits=user.credits,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not user.check_password(data.password):
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    
    token = user.generate_token()
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        nickname=user.nickname,
        level=user.level,
        credits=user.credits,
    )


@router.get("/me", response_model=UserInfo)
def get_me(user: User = Depends(require_user)):
    """获取当前用户信息"""
    return UserInfo(
        id=user.id,
        nickname=user.nickname,
        phone=user.phone,
        level=user.level,
        credits=user.credits,
        report_count=user.report_count,
        created_at=user.created_at,
    )


@router.post("/credits")
def buy_credits(amount: int, user: User = Depends(require_user),
                db: Session = Depends(get_db)):
    """购买次数（简化）"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="数量必须大于0")
    user.credits += amount
    db.commit()
    return {"credits": user.credits, "added": amount}
