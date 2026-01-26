from typing import Optional
from uuid import UUID

from fastapi import Depends
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.password import PasswordHelper
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from passlib.context import CryptContext
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


password_helper = PasswordHelper(
    CryptContext(schemes=["argon2"], deprecated="auto")
)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY


async def get_user_db(db: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(db, User)


def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db, password_helper=password_helper)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


bearer_transport = BearerTransport(
    tokenUrl=f"{settings.API_V1_STR}/auth/jwt/login"
)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

# 可选的当前用户依赖（允许未登录访问）
current_user_optional = fastapi_users.current_user(optional=True)
