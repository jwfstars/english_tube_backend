from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth import fastapi_users, current_user_optional
from app.core.database import get_db
from app.dependencies import get_accessible_video
from app.models.user import User
from app.models.video import Video
from app.models.word_card import WordCard
from app.schemas import WordCardCreate, WordCardResponse, WordCardListResponse

router = APIRouter()

# 鉴权依赖
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


@router.get("/", response_model=WordCardListResponse)
async def get_word_cards(
    video: Video = Depends(get_accessible_video),
    difficulty_level: int = Query(None, ge=1, le=6, description="难度等级筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取视频的单词卡片列表 - 支持可选认证

    - **video_id**: 视频 UUID（通过查询参数传递）
    - **difficulty_level**: 难度等级筛选（1-6，可选）

    **访问控制**:
    - 免费视频：任何人都可以访问单词卡
    - 付费视频：需要登录才能访问单词卡
    - 子视频继承父视频的权限设置
    """
    stmt = select(WordCard).where(WordCard.video_id == video.id)
    if difficulty_level:
        stmt = stmt.where(WordCard.difficulty_level == difficulty_level)
    stmt = stmt.order_by(WordCard.created_at)
    result = await db.execute(stmt)
    word_cards = result.scalars().all()

    return WordCardListResponse(total=len(word_cards), items=word_cards)


@router.post("/", response_model=WordCardResponse, status_code=201)
async def create_word_card(
    word_card_in: WordCardCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    创建单词卡片

    为指定视频添加一个单词卡片。
    """
    word_card = WordCard(**word_card_in.model_dump())
    db.add(word_card)
    await db.commit()
    await db.refresh(word_card)
    return word_card


@router.post("/batch", response_model=WordCardListResponse, status_code=201)
async def create_word_cards_batch(
    word_cards_in: list[WordCardCreate],
    db: AsyncSession = Depends(get_db),
):
    """
    批量创建单词卡片

    一次性为视频添加多个单词卡片。
    """
    word_cards = [WordCard(**wc.model_dump()) for wc in word_cards_in]
    db.add_all(word_cards)
    await db.commit()

    for word_card in word_cards:
        await db.refresh(word_card)

    return WordCardListResponse(total=len(word_cards), items=word_cards)


@router.delete("/{word_card_id}", status_code=204)
async def delete_word_card(
    word_card_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    删除单词卡片

    - **word_card_id**: 单词卡片 UUID
    """
    result = await db.execute(select(WordCard).where(WordCard.id == word_card_id))
    word_card = result.scalars().first()
    if not word_card:
        raise HTTPException(status_code=404, detail="单词卡片不存在")

    await db.delete(word_card)
    await db.commit()
    return None
