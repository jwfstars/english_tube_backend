from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from app.core.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    phone = Column(String(32), nullable=True, unique=True, index=True)
    username = Column(String(64), nullable=True, unique=True, index=True)
    display_name = Column(String(255), nullable=True)
    apple_sub = Column(String(255), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
