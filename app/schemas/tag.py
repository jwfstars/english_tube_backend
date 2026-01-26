from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


# 标签基础 Schema
class TagBase(BaseModel):
    name: str = Field(..., max_length=100, description="标签名称")
    description: Optional[str] = Field(None, description="标签描述")


# 创建标签
class TagCreate(TagBase):
    pass


# 更新标签
class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


# 标签响应
class TagResponse(TagBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# 标签列表响应
class TagListResponse(BaseModel):
    total: int
    items: list[TagResponse]
