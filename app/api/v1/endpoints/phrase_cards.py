from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth import fastapi_users, current_user_optional
from app.core.database import get_db
from app.dependencies import get_accessible_video
from app.models.phrase_card import PhraseCard
from app.models.user import User
from app.models.video import Video
from app.schemas import PhraseCardCreate, PhraseCardResponse, PhraseCardListResponse

router = APIRouter()

# 鉴权依赖
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


@router.get("/", response_model=PhraseCardListResponse)
async def get_phrase_cards(
    video: Video = Depends(get_accessible_video),
    difficulty_level: int = Query(None, ge=1, le=6, description="难度等级筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取视频的短语卡片列表 - 支持可选认证

    - **video_id**: 视频 UUID（通过查询参数传递）
    - **difficulty_level**: 难度等级筛选（1-6，可选）

    **访问控制**:
    - 免费视频：任何人都可以访问短语卡
    - 付费视频：需要登录才能访问短语卡
    - 子视频继承父视频的权限设置
    """
    stmt = select(PhraseCard).where(PhraseCard.video_id == video.id)
    if difficulty_level:
        stmt = stmt.where(PhraseCard.difficulty_level == difficulty_level)
    stmt = stmt.order_by(PhraseCard.created_at)
    result = await db.execute(stmt)
    phrase_cards = result.scalars().all()

    return PhraseCardListResponse(total=len(phrase_cards), items=phrase_cards)


@router.post("/", response_model=PhraseCardResponse, status_code=201)
async def create_phrase_card(
    phrase_card_in: PhraseCardCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    创建短语卡片

    为指定视频添加一个短语卡片。
    """
    phrase_card = PhraseCard(**phrase_card_in.model_dump())
    db.add(phrase_card)
    await db.commit()
    await db.refresh(phrase_card)
    return phrase_card


@router.post("/batch", response_model=PhraseCardListResponse, status_code=201)
async def create_phrase_cards_batch(
    phrase_cards_in: list[PhraseCardCreate],
    db: AsyncSession = Depends(get_db),
):
    """
    批量创建短语卡片

    一次性为视频添加多个短语卡片。
    """
    phrase_cards = [PhraseCard(**pc.model_dump()) for pc in phrase_cards_in]
    db.add_all(phrase_cards)
    await db.commit()

    for phrase_card in phrase_cards:
        await db.refresh(phrase_card)

    return PhraseCardListResponse(total=len(phrase_cards), items=phrase_cards)


@router.delete("/{phrase_card_id}", status_code=204)
async def delete_phrase_card(
    phrase_card_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    删除短语卡片

    - **phrase_card_id**: 短语卡片 UUID
    """
    result = await db.execute(
        select(PhraseCard).where(PhraseCard.id == phrase_card_id)
    )
    phrase_card = result.scalars().first()
    if not phrase_card:
        raise HTTPException(status_code=404, detail="短语卡片不存在")

    await db.delete(phrase_card)
    await db.commit()
    return None
