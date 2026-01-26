from sqlalchemy import Column, Integer, Text, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Subtitle(Base):
    __tablename__ = "subtitles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)

    start_time = Column(DECIMAL(10, 3), nullable=False)
    end_time = Column(DECIMAL(10, 3), nullable=False)

    english_text = Column(Text, nullable=False)
    chinese_text = Column(Text)

    sequence_number = Column(Integer)

    # 词汇引用：{实际词形: 原形}，如 {"cleanest": "clean", "landscapes": "landscape"}
    word_refs = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    video = relationship("Video", backref="subtitles")

    def __repr__(self):
        return f"<Subtitle {self.id}: {self.english_text[:30]}>"
