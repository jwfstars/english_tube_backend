from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# 视频类型枚举
VIDEO_TYPES = ['full', 'segment', 'group']


# 视频基础 Schema
class VideoBase(BaseModel):
    title: str = Field(..., max_length=255, description="视频标题（英文）")
    title_zh: Optional[str] = Field(None, max_length=255, description="视频标题（中文）")
    description: Optional[str] = Field(None, description="视频描述（英文/原始）")
    description_zh: Optional[str] = Field(None, description="视频描述（中文，润色精简后）")
    video_url: Optional[str] = Field(None, description="视频 URL")
    vod_file_id: Optional[str] = Field(None, description="VOD 文件 ID")
    thumbnail_url: Optional[str] = Field(None, description="缩略图 URL")
    duration: int = Field(..., gt=0, description="视频时长（秒）")
    difficulty: str = Field(default="beginner", description="难度等级")
    youtube_id: Optional[str] = Field(None, max_length=50, description="YouTube 视频 ID")
    youtube_url: Optional[str] = Field(None, description="YouTube 原始 URL")
    original_author: Optional[str] = Field(None, max_length=255, description="原作者")
    author_avatar_url: Optional[str] = Field(None, description="作者/频道头像 URL")
    tags: List[str] = Field(default_factory=list, description="标签")
    categories: List[str] = Field(default_factory=list, description="分类")
    categories_zh: List[str] = Field(default_factory=list, description="中文分类")


# 创建视频
class VideoCreate(VideoBase):
    display_order: int = Field(default=0, description="显示顺序")
    is_published: bool = Field(default=False, description="是否发布")
    is_free: bool = Field(default=False, description="是否免费视频")
    # 视频组相关
    parent_id: Optional[UUID] = Field(None, description="父视频ID（视频组）")
    segment_index: Optional[int] = Field(None, ge=1, description="片段序号")
    video_type: str = Field(default="full", description="视频类型: full/segment/group")


# 更新视频
class VideoUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    title_zh: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_zh: Optional[str] = None
    video_url: Optional[str] = None
    vod_file_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = Field(None, gt=0)
    difficulty: Optional[str] = None
    display_order: Optional[int] = None
    is_published: Optional[bool] = None
    is_free: Optional[bool] = None
    status: Optional[str] = None
    youtube_id: Optional[str] = None
    youtube_url: Optional[str] = None
    original_author: Optional[str] = None
    author_avatar_url: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    categories_zh: Optional[List[str]] = None
    # 视频组相关
    parent_id: Optional[UUID] = None
    segment_index: Optional[int] = None
    video_type: Optional[str] = None


# 视频简要信息（用于列表中的子视频）
class VideoBrief(BaseModel):
    id: UUID
    title: str
    title_zh: Optional[str] = None
    duration: int
    segment_index: Optional[int] = None
    thumbnail_url: Optional[str] = None
    vod_file_id: Optional[str] = None  # 添加 VOD 文件 ID，用于播放

    class Config:
        from_attributes = True


# 视频响应
class VideoResponse(VideoBase):
    id: UUID
    status: str
    is_published: bool
    is_free: bool
    display_order: int
    # 视频组相关
    parent_id: Optional[UUID] = None
    segment_index: Optional[int] = None
    video_type: str = "full"
    segment_count: int = 0  # 子视频数量（仅视频组有值）
    # 时间
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 视频详情响应（包含子片段）
class VideoDetailResponse(VideoResponse):
    segments: List[VideoBrief] = []

    class Config:
        from_attributes = True


# 视频列表响应
class VideoListResponse(BaseModel):
    total: int
    items: list[VideoResponse]
