import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class UserSubtitleFavorite(Base):
    __tablename__ = "user_subtitle_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "subtitle_id", name="uq_user_subtitle_favorites_user_subtitle"),
        Index("ix_user_subtitle_favorites_user_favorited_at", "user_id", "favorited_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subtitle_id = Column(Integer, ForeignKey("subtitles.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    favorited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
