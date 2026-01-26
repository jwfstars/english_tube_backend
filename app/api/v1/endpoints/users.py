from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import fastapi_users
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter()
current_superuser = fastapi_users.current_user(active=True, superuser=True)


@router.get("/users", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """List all users (superuser only)"""
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return users
