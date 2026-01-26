from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# 短语卡片基础 Schema
class PhraseCardBase(BaseModel):
    phrase: str = Field(..., max_length=200, description="短语")
    phonetic: Optional[str] = Field(None, max_length=200, description="音标")
    chinese_definition: Optional[str] = Field(None, description="中文含义")
    synonyms: Optional[str] = Field(None, description="同义词")
    context: Optional[str] = Field(None, description="上下文/例句")
    context_translation: Optional[str] = Field(None, description="上下文翻译")
    difficulty_level: int = Field(default=1, ge=1, le=6, description="难度等级 (1-6 对应 A1-C2)")


# 创建短语卡片
class PhraseCardCreate(PhraseCardBase):
    video_id: UUID = Field(..., description="视频 ID")


# 短语卡片响应
class PhraseCardResponse(PhraseCardBase):
    id: UUID
    video_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 短语卡片列表响应
class PhraseCardListResponse(BaseModel):
    total: int
    items: list[PhraseCardResponse]
