from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# 单词卡片基础 Schema
class WordCardBase(BaseModel):
    word: str = Field(..., max_length=100, description="单词")
    phonetic: Optional[str] = Field(None, max_length=100, description="音标")
    chinese_definition: Optional[str] = Field(None, description="中文释义")
    english_definition: Optional[str] = Field(None, description="英文释义")
    example_from_video: Optional[str] = Field(None, description="视频中的例句")
    difficulty_level: int = Field(..., ge=1, le=6, description="难度等级 (1-6 对应 A1-C2)")


# 创建单词卡片
class WordCardCreate(WordCardBase):
    video_id: UUID = Field(..., description="视频 ID")


# 单词卡片响应
class WordCardResponse(WordCardBase):
    id: UUID
    video_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 单词卡片列表响应
class WordCardListResponse(BaseModel):
    total: int
    items: list[WordCardResponse]
