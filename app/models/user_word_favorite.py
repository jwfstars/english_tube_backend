import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class UserWordFavorite(Base):
    __tablename__ = "user_word_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "word_card_id", name="uq_user_word_favorites_user_word"),
        Index("ix_user_word_favorites_user_favorited_at", "user_id", "favorited_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    word_card_id = Column(UUID(as_uuid=True), ForeignKey("word_cards.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    favorited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
