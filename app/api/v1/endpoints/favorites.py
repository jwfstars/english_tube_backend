from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import fastapi_users
from app.core.database import get_db
from app.models.user import User
from app.models.video import Video
from app.models.subtitle import Subtitle
from app.models.word_card import WordCard
from app.models.phrase_card import PhraseCard
from app.models.user_video_favorite import UserVideoFavorite
from app.models.user_subtitle_favorite import UserSubtitleFavorite
from app.models.user_word_favorite import UserWordFavorite
from app.models.user_phrase_favorite import UserPhraseFavorite
from app.schemas import (
    FavoriteListResponse,
    FavoriteActionResponse,
    FavoriteCheckResponse,
    FavoriteBatchCheckRequest,
    FavoriteBatchCheckResponse,
    SubtitleFavoriteListResponse,
    SubtitleFavoriteActionResponse,
    SubtitleFavoriteCheckResponse,
    WordFavoriteListResponse,
    WordFavoriteActionResponse,
    WordFavoriteCheckResponse,
    PhraseFavoriteListResponse,
    PhraseFavoriteActionResponse,
    PhraseFavoriteCheckResponse,
)

router = APIRouter()

current_user = fastapi_users.current_user(active=True)


def _video_payload(video: Video) -> dict:
    return {
        "id": video.id,
        "title": video.title,
        "title_zh": video.title_zh,
        "description": video.description,
        "description_zh": video.description_zh,
        "video_url": video.video_url,
        "vod_file_id": video.vod_file_id,
        "thumbnail_url": video.thumbnail_url,
        "duration": video.duration,
        "difficulty": video.difficulty,
        "youtube_id": video.youtube_id,
        "youtube_url": video.youtube_url,
        "original_author": video.original_author,
        "author_avatar_url": video.author_avatar_url,
        "tags": [],
        "categories": video.categories_zh or video.categories or [],
        "categories_zh": video.categories_zh or [],
        "status": video.status,
        "is_published": video.is_published,
        "display_order": video.display_order,
        "parent_id": video.parent_id,
        "segment_index": video.segment_index,
        "video_type": video.video_type or "full",
        "segment_count": 0,
        "created_at": video.created_at,
        "updated_at": video.updated_at,
    }


def _subtitle_payload(subtitle: Subtitle) -> dict:
    return {
        "id": subtitle.id,
        "video_id": subtitle.video_id,
        "start_time": float(subtitle.start_time),
        "end_time": float(subtitle.end_time),
        "english_text": subtitle.english_text,
        "chinese_text": subtitle.chinese_text,
        "sequence_number": subtitle.sequence_number,
        "word_refs": subtitle.word_refs or {},
        "created_at": subtitle.created_at,
    }


def _word_card_payload(word_card: WordCard) -> dict:
    return {
        "id": word_card.id,
        "video_id": word_card.video_id,
        "word": word_card.word,
        "phonetic": word_card.phonetic,
        "chinese_definition": word_card.chinese_definition,
        "english_definition": word_card.english_definition,
        "example_from_video": word_card.example_from_video,
        "difficulty_level": word_card.difficulty_level,
        "created_at": word_card.created_at,
    }


def _phrase_card_payload(phrase_card: PhraseCard) -> dict:
    return {
        "id": phrase_card.id,
        "video_id": phrase_card.video_id,
        "phrase": phrase_card.phrase,
        "phonetic": phrase_card.phonetic,
        "chinese_definition": phrase_card.chinese_definition,
        "synonyms": phrase_card.synonyms,
        "context": phrase_card.context,
        "context_translation": phrase_card.context_translation,
        "difficulty_level": phrase_card.difficulty_level,
        "created_at": phrase_card.created_at,
    }




@router.post("/{video_id}", response_model=FavoriteActionResponse, status_code=201)
async def add_favorite(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    result = await db.execute(
        select(UserVideoFavorite).where(
            UserVideoFavorite.user_id == user.id,
            UserVideoFavorite.video_id == video_id,
        )
    )
    favorite = result.scalars().first()
    if not favorite:
        favorite = UserVideoFavorite(user_id=user.id, video_id=video_id)
        db.add(favorite)
        await db.commit()

    return FavoriteActionResponse(video_id=video_id, is_favorite=True)


@router.delete("/{video_id}", response_model=FavoriteActionResponse)
async def remove_favorite(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserVideoFavorite).where(
            UserVideoFavorite.user_id == user.id,
            UserVideoFavorite.video_id == video_id,
        )
    )
    favorite = result.scalars().first()
    if favorite:
        await db.delete(favorite)
        await db.commit()

    return FavoriteActionResponse(video_id=video_id, is_favorite=False)


@router.get("/", response_model=FavoriteListResponse)
async def get_favorites(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    total_result = await db.execute(
        select(func.count())
        .select_from(UserVideoFavorite)
        .where(UserVideoFavorite.user_id == user.id)
    )
    total = total_result.scalar_one()

    stmt = (
        select(UserVideoFavorite, Video)
        .join(Video, Video.id == UserVideoFavorite.video_id)
        .where(UserVideoFavorite.user_id == user.id)
        .order_by(desc(UserVideoFavorite.favorited_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = []
    for favorite, video in result.all():
        items.append(
            {
                "video": _video_payload(video),
                "favorited_at": favorite.favorited_at,
            }
        )

    return FavoriteListResponse(total=total, items=items)


@router.get("/{video_id}/check", response_model=FavoriteCheckResponse)
async def check_favorite(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserVideoFavorite).where(
            UserVideoFavorite.user_id == user.id,
            UserVideoFavorite.video_id == video_id,
        )
    )
    favorite = result.scalars().first()
    return FavoriteCheckResponse(video_id=video_id, is_favorite=bool(favorite))


@router.post("/batch-check", response_model=FavoriteBatchCheckResponse)
async def batch_check_favorites(
    payload: FavoriteBatchCheckRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    if not payload.video_ids:
        return FavoriteBatchCheckResponse(results={})

    result = await db.execute(
        select(UserVideoFavorite.video_id).where(
            UserVideoFavorite.user_id == user.id,
            UserVideoFavorite.video_id.in_(payload.video_ids),
        )
    )
    favorited_ids = {str(row[0]) for row in result.all()}
    results = {str(video_id): str(video_id) in favorited_ids for video_id in payload.video_ids}
    return FavoriteBatchCheckResponse(results=results)


# ==================== Subtitle Favorites ====================

@router.post("/subtitles/{subtitle_id}", response_model=SubtitleFavoriteActionResponse, status_code=201)
async def add_subtitle_favorite(
    subtitle_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    # 检查字幕是否存在
    result = await db.execute(select(Subtitle).where(Subtitle.id == subtitle_id))
    subtitle = result.scalars().first()
    if not subtitle:
        raise HTTPException(status_code=404, detail="字幕不存在")

    # 检查是否已收藏
    result = await db.execute(
        select(UserSubtitleFavorite).where(
            UserSubtitleFavorite.user_id == user.id,
            UserSubtitleFavorite.subtitle_id == subtitle_id,
        )
    )
    favorite = result.scalars().first()
    if not favorite:
        favorite = UserSubtitleFavorite(
            user_id=user.id,
            subtitle_id=subtitle_id,
            video_id=subtitle.video_id,
        )
        db.add(favorite)
        await db.commit()

    return SubtitleFavoriteActionResponse(subtitle_id=subtitle_id, is_favorite=True)


@router.delete("/subtitles/{subtitle_id}", response_model=SubtitleFavoriteActionResponse)
async def remove_subtitle_favorite(
    subtitle_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserSubtitleFavorite).where(
            UserSubtitleFavorite.user_id == user.id,
            UserSubtitleFavorite.subtitle_id == subtitle_id,
        )
    )
    favorite = result.scalars().first()
    if favorite:
        await db.delete(favorite)
        await db.commit()

    return SubtitleFavoriteActionResponse(subtitle_id=subtitle_id, is_favorite=False)


@router.get("/subtitles", response_model=SubtitleFavoriteListResponse)
async def get_subtitle_favorites(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    # 获取总数
    total_result = await db.execute(
        select(func.count())
        .select_from(UserSubtitleFavorite)
        .where(UserSubtitleFavorite.user_id == user.id)
    )
    total = total_result.scalar_one()

    # 获取收藏列表
    stmt = (
        select(UserSubtitleFavorite, Subtitle, Video)
        .join(Subtitle, Subtitle.id == UserSubtitleFavorite.subtitle_id)
        .join(Video, Video.id == UserSubtitleFavorite.video_id)
        .where(UserSubtitleFavorite.user_id == user.id)
        .order_by(desc(UserSubtitleFavorite.favorited_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = []
    for favorite, subtitle, video in result.all():
        items.append(
            {
                "subtitle": _subtitle_payload(subtitle),
                "video": _video_payload(video),
                "favorited_at": favorite.favorited_at,
            }
        )

    return SubtitleFavoriteListResponse(total=total, items=items)


@router.get("/subtitles/{subtitle_id}/check", response_model=SubtitleFavoriteCheckResponse)
async def check_subtitle_favorite(
    subtitle_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserSubtitleFavorite).where(
            UserSubtitleFavorite.user_id == user.id,
            UserSubtitleFavorite.subtitle_id == subtitle_id,
        )
    )
    favorite = result.scalars().first()
    return SubtitleFavoriteCheckResponse(subtitle_id=subtitle_id, is_favorite=bool(favorite))


# ==================== Word Favorites (Word Book) ====================

@router.post("/words/{word_card_id}", response_model=WordFavoriteActionResponse, status_code=201)
async def add_word_favorite(
    word_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    # 检查单词卡片是否存在
    result = await db.execute(select(WordCard).where(WordCard.id == word_card_id))
    word_card = result.scalars().first()
    if not word_card:
        raise HTTPException(status_code=404, detail="单词卡片不存在")

    # 检查是否已收藏
    result = await db.execute(
        select(UserWordFavorite).where(
            UserWordFavorite.user_id == user.id,
            UserWordFavorite.word_card_id == word_card_id,
        )
    )
    favorite = result.scalars().first()
    if not favorite:
        favorite = UserWordFavorite(
            user_id=user.id,
            word_card_id=word_card_id,
            video_id=word_card.video_id,
        )
        db.add(favorite)
        await db.commit()

    return WordFavoriteActionResponse(word_card_id=word_card_id, is_favorite=True)


@router.delete("/words/{word_card_id}", response_model=WordFavoriteActionResponse)
async def remove_word_favorite(
    word_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserWordFavorite).where(
            UserWordFavorite.user_id == user.id,
            UserWordFavorite.word_card_id == word_card_id,
        )
    )
    favorite = result.scalars().first()
    if favorite:
        await db.delete(favorite)
        await db.commit()

    return WordFavoriteActionResponse(word_card_id=word_card_id, is_favorite=False)


@router.get("/words", response_model=WordFavoriteListResponse)
async def get_word_favorites(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    # 获取总数
    total_result = await db.execute(
        select(func.count())
        .select_from(UserWordFavorite)
        .where(UserWordFavorite.user_id == user.id)
    )
    total = total_result.scalar_one()

    # 获取收藏列表
    stmt = (
        select(UserWordFavorite, WordCard, Video)
        .join(WordCard, WordCard.id == UserWordFavorite.word_card_id)
        .join(Video, Video.id == UserWordFavorite.video_id)
        .where(UserWordFavorite.user_id == user.id)
        .order_by(desc(UserWordFavorite.favorited_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = []
    for favorite, word_card, video in result.all():
        items.append(
            {
                "word_card": _word_card_payload(word_card),
                "video": _video_payload(video),
                "favorited_at": favorite.favorited_at,
            }
        )

    return WordFavoriteListResponse(total=total, items=items)


@router.get("/words/{word_card_id}/check", response_model=WordFavoriteCheckResponse)
async def check_word_favorite(
    word_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserWordFavorite).where(
            UserWordFavorite.user_id == user.id,
            UserWordFavorite.word_card_id == word_card_id,
        )
    )
    favorite = result.scalars().first()
    return WordFavoriteCheckResponse(word_card_id=word_card_id, is_favorite=bool(favorite))



# ===== Phrase Favorites APIs =====

@router.post("/phrases/{phrase_card_id}", response_model=PhraseFavoriteActionResponse, status_code=201)
async def add_phrase_favorite(
    phrase_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    # 检查短语卡片是否存在
    phrase_card = await db.get(PhraseCard, phrase_card_id)
    if not phrase_card:
        raise HTTPException(status_code=404, detail="短语卡片不存在")

    # 检查是否已收藏
    existing = await db.execute(
        select(UserPhraseFavorite).where(
            UserPhraseFavorite.user_id == user.id,
            UserPhraseFavorite.phrase_card_id == phrase_card_id,
        )
    )
    if not existing.scalars().first():
        # 创建收藏记录
        favorite = UserPhraseFavorite(
            user_id=user.id,
            phrase_card_id=phrase_card_id,
            video_id=phrase_card.video_id,
        )
        db.add(favorite)
        await db.commit()

    return PhraseFavoriteActionResponse(phrase_card_id=phrase_card_id, is_favorite=True)


@router.delete("/phrases/{phrase_card_id}", response_model=PhraseFavoriteActionResponse)
async def remove_phrase_favorite(
    phrase_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserPhraseFavorite).where(
            UserPhraseFavorite.user_id == user.id,
            UserPhraseFavorite.phrase_card_id == phrase_card_id,
        )
    )
    favorite = result.scalars().first()

    if favorite:
        await db.delete(favorite)
        await db.commit()

    return PhraseFavoriteActionResponse(phrase_card_id=phrase_card_id, is_favorite=False)


@router.get("/phrases", response_model=PhraseFavoriteListResponse)
async def get_phrase_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    # 获取总数
    total_result = await db.execute(
        select(func.count())
        .select_from(UserPhraseFavorite)
        .where(UserPhraseFavorite.user_id == user.id)
    )
    total = total_result.scalar_one()

    # 获取收藏列表
    stmt = (
        select(UserPhraseFavorite, PhraseCard, Video)
        .join(PhraseCard, PhraseCard.id == UserPhraseFavorite.phrase_card_id)
        .join(Video, Video.id == UserPhraseFavorite.video_id)
        .where(UserPhraseFavorite.user_id == user.id)
        .order_by(desc(UserPhraseFavorite.favorited_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = []
    for favorite, phrase_card, video in result.all():
        items.append(
            {
                "phrase_card": _phrase_card_payload(phrase_card),
                "video": _video_payload(video),
                "favorited_at": favorite.favorited_at,
            }
        )

    return PhraseFavoriteListResponse(total=total, items=items)


@router.get("/phrases/{phrase_card_id}/check", response_model=PhraseFavoriteCheckResponse)
async def check_phrase_favorite(
    phrase_card_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserPhraseFavorite).where(
            UserPhraseFavorite.user_id == user.id,
            UserPhraseFavorite.phrase_card_id == phrase_card_id,
        )
    )
    favorite = result.scalars().first()
    return PhraseFavoriteCheckResponse(phrase_card_id=phrase_card_id, is_favorite=bool(favorite))
