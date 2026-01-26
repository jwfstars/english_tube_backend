import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class UserVideoFavorite(Base):
    __tablename__ = "user_video_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uq_user_video_favorites_user_video"),
        Index("ix_user_video_favorites_user_favorited_at", "user_id", "favorited_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    favorited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
