"""用户认证接口"""

from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.schemas.common import success, error as error_response
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """注册新用户"""
    user, token = AuthService.register(db, req)
    return success(data={
        "user": UserResponse.model_validate(user).model_dump(),
        "access_token": token,
        "token_type": "bearer",
    }, message="注册成功")


@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user, token = AuthService.login(db, req.email, req.password)
    return success(data={
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user).model_dump(),
    }, message="登录成功")


@router.get("/me")
async def get_me(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """获取当前登录用户信息"""
    if not authorization:
        raise UnauthorizedException()
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise UnauthorizedException()
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException()
    user_id = int(payload.get("sub"))
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise UnauthorizedException()
    return success(data=UserResponse.model_validate(user).model_dump())
