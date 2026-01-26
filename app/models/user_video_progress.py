import uuid
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class UserVideoProgress(Base):
    __tablename__ = "user_video_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uq_user_video_progress_user_video"),
        Index("ix_user_video_progress_user_lastwatched", "user_id", "last_watched_at"),
        Index("ix_user_video_progress_user_completed", "user_id", "is_completed", "completed_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    current_progress = Column(Integer, nullable=False, default=0)
    total_duration = Column(Integer, nullable=False)
    is_completed = Column(Boolean, nullable=False, default=False)
    last_watched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
