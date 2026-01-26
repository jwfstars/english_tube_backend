import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class UserPhraseFavorite(Base):
    __tablename__ = "user_phrase_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "phrase_card_id", name="uq_user_phrase_favorites_user_phrase"),
        Index("ix_user_phrase_favorites_user_favorited_at", "user_id", "favorited_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    phrase_card_id = Column(UUID(as_uuid=True), ForeignKey("phrase_cards.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    favorited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
