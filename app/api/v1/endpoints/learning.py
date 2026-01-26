from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import fastapi_users
from app.core.database import get_db
from app.models.user import User
from app.models.video import Video
from app.models.user_video_progress import UserVideoProgress
from app.schemas import (
    LearningProgressUpdateRequest,
    LearningProgressResponse,
    LearningRecentResponse,
    LearningCompletedResponse,
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


def _progress_percent(current_progress: int, total_duration: int) -> float:
    if total_duration <= 0:
        return 0.0
    return round((current_progress / total_duration) * 100, 2)


@router.post("/progress", response_model=LearningProgressResponse)
async def update_learning_progress(
    progress_in: LearningProgressUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(select(Video).where(Video.id == progress_in.video_id))
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    total_duration = progress_in.total_duration or video.duration
    current_progress = min(progress_in.current_progress, total_duration)
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(UserVideoProgress).where(
            UserVideoProgress.user_id == user.id,
            UserVideoProgress.video_id == progress_in.video_id,
        )
    )
    progress = result.scalars().first()
    if progress:
        progress.current_progress = current_progress
        progress.total_duration = total_duration
        progress.last_watched_at = now
        if progress_in.is_completed is True:
            progress.is_completed = True
            progress.completed_at = now
        elif progress_in.is_completed is False:
            progress.is_completed = False
            progress.completed_at = None
        elif not progress.is_completed and current_progress >= total_duration * 0.9:
            progress.is_completed = True
            progress.completed_at = now
    else:
        is_completed = progress_in.is_completed is True or current_progress >= total_duration * 0.9
        progress = UserVideoProgress(
            user_id=user.id,
            video_id=progress_in.video_id,
            current_progress=current_progress,
            total_duration=total_duration,
            is_completed=is_completed,
            last_watched_at=now,
            completed_at=now if is_completed else None,
        )
        db.add(progress)

    await db.commit()
    await db.refresh(progress)

    return LearningProgressResponse(
        video_id=progress.video_id,
        current_progress=progress.current_progress,
        total_duration=progress.total_duration,
        progress_percent=_progress_percent(progress.current_progress, progress.total_duration),
        is_completed=progress.is_completed,
        last_watched_at=progress.last_watched_at,
        completed_at=progress.completed_at,
    )


@router.get("/recent", response_model=LearningRecentResponse)
async def get_recent_learning(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    total_result = await db.execute(
        select(func.count())
        .select_from(UserVideoProgress)
        .where(UserVideoProgress.user_id == user.id)
    )
    total = total_result.scalar_one()

    stmt = (
        select(UserVideoProgress, Video)
        .join(Video, Video.id == UserVideoProgress.video_id)
        .where(UserVideoProgress.user_id == user.id)
        .order_by(desc(UserVideoProgress.last_watched_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = []
    for progress, video in result.all():
        items.append(
            {
                "video": _video_payload(video),
                "current_progress": progress.current_progress,
                "total_duration": progress.total_duration,
                "progress_percent": _progress_percent(
                    progress.current_progress, progress.total_duration
                ),
                "last_watched_at": progress.last_watched_at,
                "is_completed": progress.is_completed,
                "completed_at": progress.completed_at,
            }
        )

    return LearningRecentResponse(total=total, items=items)


@router.get("/completed", response_model=LearningCompletedResponse)
async def get_completed_learning(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    total_result = await db.execute(
        select(func.count())
        .select_from(UserVideoProgress)
        .where(
            UserVideoProgress.user_id == user.id,
            UserVideoProgress.is_completed.is_(True),
        )
    )
    total = total_result.scalar_one()

    stmt = (
        select(UserVideoProgress, Video)
        .join(Video, Video.id == UserVideoProgress.video_id)
        .where(
            UserVideoProgress.user_id == user.id,
            UserVideoProgress.is_completed.is_(True),
        )
        .order_by(desc(UserVideoProgress.completed_at).nullslast())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = []
    for progress, video in result.all():
        completed_at = progress.completed_at or progress.last_watched_at
        items.append(
            {
                "video": _video_payload(video),
                "completed_at": completed_at,
            }
        )

    return LearningCompletedResponse(total=total, items=items)


@router.get("/progress/{video_id}", response_model=LearningProgressResponse)
async def get_learning_progress(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserVideoProgress).where(
            UserVideoProgress.user_id == user.id,
            UserVideoProgress.video_id == video_id,
        )
    )
    progress = result.scalars().first()
    if not progress:
        raise HTTPException(status_code=404, detail="学习记录不存在")

    return LearningProgressResponse(
        video_id=progress.video_id,
        current_progress=progress.current_progress,
        total_duration=progress.total_duration,
        progress_percent=_progress_percent(progress.current_progress, progress.total_duration),
        is_completed=progress.is_completed,
        last_watched_at=progress.last_watched_at,
        completed_at=progress.completed_at,
    )


@router.post("/complete/{video_id}", response_model=LearningProgressResponse)
async def complete_learning(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    now = datetime.now(timezone.utc)
    total_duration = video.duration

    result = await db.execute(
        select(UserVideoProgress).where(
            UserVideoProgress.user_id == user.id,
            UserVideoProgress.video_id == video_id,
        )
    )
    progress = result.scalars().first()
    if progress:
        progress.current_progress = total_duration
        progress.total_duration = total_duration
        progress.is_completed = True
        progress.completed_at = now
        progress.last_watched_at = now
    else:
        progress = UserVideoProgress(
            user_id=user.id,
            video_id=video_id,
            current_progress=total_duration,
            total_duration=total_duration,
            is_completed=True,
            completed_at=now,
            last_watched_at=now,
        )
        db.add(progress)

    await db.commit()
    await db.refresh(progress)

    return LearningProgressResponse(
        video_id=progress.video_id,
        current_progress=progress.current_progress,
        total_duration=progress.total_duration,
        progress_percent=_progress_percent(progress.current_progress, progress.total_duration),
        is_completed=progress.is_completed,
        last_watched_at=progress.last_watched_at,
        completed_at=progress.completed_at,
    )


@router.delete("/progress/{video_id}", status_code=204)
async def delete_learning_progress(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(UserVideoProgress).where(
            UserVideoProgress.user_id == user.id,
            UserVideoProgress.video_id == video_id,
        )
    )
    progress = result.scalars().first()
    if not progress:
        raise HTTPException(status_code=404, detail="学习记录不存在")

    await db.delete(progress)
    await db.commit()
    return None
