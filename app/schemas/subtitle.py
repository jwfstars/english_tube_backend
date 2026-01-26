from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# 字幕基础 Schema
class SubtitleBase(BaseModel):
    start_time: float = Field(..., ge=0, description="开始时间（秒）")
    end_time: float = Field(..., ge=0, description="结束时间（秒）")
    english_text: str = Field(..., description="英文字幕")
    chinese_text: Optional[str] = Field(None, description="中文字幕")
    sequence_number: Optional[int] = Field(None, description="字幕序号")
    word_refs: Optional[Dict[str, str]] = Field(default={}, description="词汇引用：{实际词形: 原形}")


# 创建字幕
class SubtitleCreate(SubtitleBase):
    video_id: UUID = Field(..., description="视频 ID")


# 字幕响应
class SubtitleResponse(SubtitleBase):
    id: int  # 字幕使用整型 ID
    video_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 字幕列表响应
class SubtitleListResponse(BaseModel):
    total: int
    items: list[SubtitleResponse]
