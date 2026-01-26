from typing import Optional
from uuid import UUID
from fastapi_users import schemas


class UserRead(schemas.BaseUser[UUID]):
    phone: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    apple_sub: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
