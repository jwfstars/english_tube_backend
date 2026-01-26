from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    title_zh = Column(String(255), nullable=True)  # 中文标题
    description = Column(Text)
    description_zh = Column(Text)  # 中文描述（润色精简后）

    # 视频 URL
    video_url = Column(Text, nullable=True)  # 可选，仅字幕模式下可能没有视频
    vod_file_id = Column(Text, nullable=True)  # VOD 文件 ID（可选）
    thumbnail_url = Column(Text)

    # 元信息
    duration = Column(Integer, nullable=False)  # 秒
    difficulty = Column(String(20), default='beginner')  # beginner/intermediate/advanced

    # 视频组关系
    parent_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=True, index=True)
    segment_index = Column(Integer, nullable=True)  # 片段序号 (1, 2, 3...)
    video_type = Column(String(20), default='full')  # full(完整视频)/segment(片段)/group(视频组)

    # 状态
    status = Column(String(20), default='published')
    is_published = Column(Boolean, default=False)
    is_free = Column(Boolean, default=False)  # 是否免费视频
    display_order = Column(Integer, default=0, index=True)

    # YouTube 相关
    youtube_id = Column(String(50), unique=True, index=True)
    youtube_url = Column(Text)
    original_author = Column(String(255))
    author_avatar_url = Column(Text, nullable=True)  # 作者/频道头像
    categories = Column(JSONB, nullable=True, default=list)
    categories_zh = Column(JSONB, nullable=True)

    # 审计
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    segments = relationship(
        "Video",
        backref="parent",
        remote_side=[id],
        foreign_keys=[parent_id],
    )

    def __repr__(self):
        return f"<Video {self.title}>"
