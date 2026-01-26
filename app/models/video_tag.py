from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VideoTag(Base):
    __tablename__ = "video_tags"

    video_id = Column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    is_primary = Column(Boolean, default=False)

    # 关系
    video = relationship("Video", backref="video_tags")
    tag = relationship("Tag", backref="video_tags")

    def __repr__(self):
        return f"<VideoTag video_id={self.video_id} tag_id={self.tag_id}>"
