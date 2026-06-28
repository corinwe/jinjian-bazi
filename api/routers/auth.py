"""金鉴真人·用户认证路由 v1.0 — JWT注册/登录/鉴权"""

import hashlib
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from database.connection import get_connection

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# ── 简单JWT实现（不依赖外部库）──
# 生产环境建议用python-jose，这里用自带hashlib简洁实现
SECRET_KEY = os.environ.get("JWT_SECRET", "jinjian-zhenren-secret-key-2026")


def _sign_token(payload: dict) -> str:
    """生成简易签名token"""
    import base64
    import json

    header = base64.b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
    payload_enc = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode()).decode()
    msg = f"{header}.{payload_enc}"
    sig = hashlib.sha256(f"{msg}.{SECRET_KEY}".encode()).hexdigest()[:32]
    return f"{msg}.{sig}"


def _verify_token(token: str) -> dict | None:
    """验证并解码token"""
    import base64
    import json

    parts = token.split(".")
    if len(parts) != 3:
        return None
    msg = f"{parts[0]}.{parts[1]}"
    expected = hashlib.sha256(f"{msg}.{SECRET_KEY}".encode()).hexdigest()[:32]
    if parts[2] != expected:
        return None
    try:
        payload = json.loads(base64.b64decode(parts[1] + "==").decode())
        if payload.get("exp", 0) < datetime.now().timestamp():
            return None
        return payload
    except:
        return None


def get_current_user(authorization: str = Header(None)) -> dict:
    """依赖注入：从Authorization header获取当前用户"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "")
    payload = _verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    return payload


# ── Schema ──
class AuthRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=30, description="用户名")
    password: str = Field(..., min_length=4, max_length=50, description="密码")


class AuthResponse(BaseModel):
    success: bool
    token: str = ""
    user_id: int = 0
    username: str = ""
    message: str = ""


# ── 密码处理 ──
def _hash_password(password: str) -> str:
    return hashlib.sha256(f"{password}.jinjian".encode()).hexdigest()


# ── 路由 ──
@router.post("/register", response_model=AuthResponse)
async def register(request: AuthRequest):
    """注册新用户"""
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT id FROM auth_users WHERE username = ?", (request.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")

        conn.execute(
            "INSERT INTO auth_users (username, password_hash) VALUES (?, ?)",
            (request.username, _hash_password(request.password)),
        )
        conn.commit()

        # 获取ID
        cursor = conn.execute("SELECT id FROM auth_users WHERE username = ?", (request.username,))
        user = cursor.fetchone()

        token = _sign_token(
            {
                "user_id": user["id"],
                "username": request.username,
                "exp": (datetime.now() + timedelta(days=30)).timestamp(),
            }
        )

        return AuthResponse(
            success=True, token=token, user_id=user["id"], username=request.username, message="注册成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {e}")
    finally:
        conn.close()


@router.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest):
    """用户登录"""
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT id, password_hash FROM auth_users WHERE username = ?", (request.username,))
        user = cursor.fetchone()
        if not user or user["password_hash"] != _hash_password(request.password):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        token = _sign_token(
            {
                "user_id": user["id"],
                "username": request.username,
                "exp": (datetime.now() + timedelta(days=30)).timestamp(),
            }
        )

        return AuthResponse(
            success=True, token=token, user_id=user["id"], username=request.username, message="登录成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {e}")
    finally:
        conn.close()


@router.post("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    """验证token是否有效"""
    return {"valid": True, "user_id": user["user_id"], "username": user["username"]}
