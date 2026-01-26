from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.auth import fastapi_users
from app.core.database import get_db
from app.models.tag import Tag
from app.models.user import User
from app.schemas import TagCreate, TagUpdate, TagResponse, TagListResponse

router = APIRouter()

# 鉴权依赖
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


@router.get("/", response_model=TagListResponse)
async def get_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_user),
):
    """
    获取标签列表

    - **skip**: 跳过记录数
    - **limit**: 每页记录数
    """
    total_result = await db.execute(select(func.count()).select_from(Tag))
    total = total_result.scalar_one()
    result = await db.execute(
        select(Tag).order_by(Tag.created_at.desc()).offset(skip).limit(limit)
    )
    tags = result.scalars().all()

    return TagListResponse(total=total, items=tags)


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_user),
):
    """
    获取单个标签详情

    - **tag_id**: 标签 UUID
    """
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.post("/", response_model=TagResponse, status_code=201)
async def create_tag(
    tag_in: TagCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    创建新标签

    - **name**: 标签名称（必填）
    - **description**: 标签描述（可选）
    """
    # 检查名称是否已存在
    result = await db.execute(select(Tag).where(Tag.name == tag_in.name))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="标签名称已存在")

    tag = Tag(**tag_in.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    tag_in: TagUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    更新标签

    - **tag_id**: 标签 UUID
    """
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 如果更新名称，检查是否重复
    if tag_in.name and tag_in.name != tag.name:
        result = await db.execute(select(Tag).where(Tag.name == tag_in.name))
        existing = result.scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="标签名称已存在")

    update_data = tag_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    删除标签

    - **tag_id**: 标签 UUID
    """
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalars().first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    await db.delete(tag)
    await db.commit()
    return None
