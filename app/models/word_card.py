from sqlalchemy import Column, String, Integer, Text, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class WordCard(Base):
    __tablename__ = "word_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    word = Column(String(100), nullable=False, index=True)
    phonetic = Column(String(100))

    chinese_definition = Column(Text)
    english_definition = Column(Text)

    example_from_video = Column(Text)
    example_translation = Column(Text)

    subtitle_id = Column(Integer, ForeignKey('subtitles.id'))
    first_appearance_time = Column(DECIMAL(10, 3))

    difficulty_level = Column(Integer, default=1)  # 1-6 对应 A1-C2
    frequency_rank = Column(Integer)
    part_of_speech = Column(String(20))
    other_pos_definitions = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    video = relationship("Video", backref="word_cards")
    subtitle = relationship("Subtitle", backref="word_cards")

    def __repr__(self):
        return f"<WordCard {self.word}>"
