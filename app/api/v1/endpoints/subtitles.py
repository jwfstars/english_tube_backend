from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth import fastapi_users, current_user_optional
from app.core.database import get_db
from app.dependencies import get_accessible_video
from app.models.subtitle import Subtitle
from app.models.user import User
from app.models.video import Video
from app.schemas import SubtitleCreate, SubtitleResponse, SubtitleListResponse

router = APIRouter()

# 鉴权依赖
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


@router.get("/", response_model=SubtitleListResponse)
async def get_subtitles(
    video: Video = Depends(get_accessible_video),
    db: AsyncSession = Depends(get_db)
):
    """
    获取视频的字幕列表 - 支持可选认证

    - **video_id**: 视频 UUID（通过查询参数传递）
    - 按时间顺序返回

    **访问控制**:
    - 免费视频：任何人都可以访问字幕
    - 付费视频：需要登录才能访问字幕
    - 子视频继承父视频的权限设置
    """
    result = await db.execute(
        select(Subtitle)
        .where(Subtitle.video_id == video.id)
        .order_by(Subtitle.start_time)
    )
    subtitles = result.scalars().all()

    return SubtitleListResponse(total=len(subtitles), items=subtitles)


@router.post("/", response_model=SubtitleResponse, status_code=201)
async def create_subtitle(
    subtitle_in: SubtitleCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    创建字幕

    为指定视频添加一条字幕。
    """
    subtitle = Subtitle(**subtitle_in.model_dump())
    db.add(subtitle)
    await db.commit()
    await db.refresh(subtitle)
    return subtitle


@router.post("/batch", response_model=SubtitleListResponse, status_code=201)
async def create_subtitles_batch(
    subtitles_in: list[SubtitleCreate],
    db: AsyncSession = Depends(get_db),
):
    """
    批量创建字幕

    一次性为视频添加多条字幕。
    """
    subtitles = [Subtitle(**s.model_dump()) for s in subtitles_in]
    db.add_all(subtitles)
    await db.commit()

    # 刷新所有对象
    for subtitle in subtitles:
        await db.refresh(subtitle)

    return SubtitleListResponse(total=len(subtitles), items=subtitles)


@router.delete("/{subtitle_id}", status_code=204)
async def delete_subtitle(
    subtitle_id: int,  # 字幕 ID 是整型
    db: AsyncSession = Depends(get_db),
):
    """
    删除字幕

    - **subtitle_id**: 字幕 ID（整型）
    """
    result = await db.execute(select(Subtitle).where(Subtitle.id == subtitle_id))
    subtitle = result.scalars().first()
    if not subtitle:
        raise HTTPException(status_code=404, detail="字幕不存在")

    await db.delete(subtitle)
    await db.commit()
    return None
