from sqlalchemy import Column, String, Integer, Text, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class PhraseCard(Base):
    __tablename__ = "phrase_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    phrase = Column(String(200), nullable=False, index=True)
    phonetic = Column(String(200))

    chinese_definition = Column(Text)
    synonyms = Column(Text)

    context = Column(Text)
    context_translation = Column(Text)

    subtitle_id = Column(Integer, ForeignKey('subtitles.id'))
    first_appearance_time = Column(DECIMAL(10, 3))

    difficulty_level = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    video = relationship("Video", backref="phrase_cards")
    subtitle = relationship("Subtitle", backref="phrase_cards")

    def __repr__(self):
        return f"<PhraseCard {self.phrase}>"
