from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth import current_user_optional
from app.core.database import get_db
from app.models.user import User
from app.models.video import Video


async def get_accessible_video(
    video_id: UUID = Query(..., description="视频 ID"),
    user: Optional[User] = Depends(current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Video:
    """
    统一的视频权限检查依赖

    功能：
    1. 查询视频是否存在
    2. 如果是子视频，自动检查父视频的权限
    3. 验证用户是否有访问权限（免费视频公开，付费视频需登录）
    4. 返回视频对象供后续使用

    Returns:
        Video: 验证通过的视频对象

    Raises:
        HTTPException(404): 视频不存在
        HTTPException(401): 无权访问（付费视频未登录）
    """
    # 查询视频
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 权限检查：如果是子视频，检查父视频的权限
    check_video = video
    if video.parent_id:
        parent_result = await db.execute(
            select(Video).where(Video.id == video.parent_id)
        )
        parent_video = parent_result.scalars().first()
        if parent_video:
            check_video = parent_video

    # 付费视频需要登录
    if not check_video.is_free and not user:
        raise HTTPException(
            status_code=401,
            detail="未登录或登录已过期，请重新登录"
        )

    return video


async def get_accessible_video_by_file_id(
    file_id: str = Query(..., description="VOD FileId"),
    user: Optional[User] = Depends(current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Video:
    """
    通过 VOD file_id 获取可访问的视频

    功能：
    1. 通过 vod_file_id 查询视频是否存在
    2. 如果是子视频，自动检查父视频的权限
    3. 验证用户是否有访问权限（免费视频公开，付费视频需登录）
    4. 返回视频对象供后续使用

    Returns:
        Video: 验证通过的视频对象

    Raises:
        HTTPException(404): 视频不存在
        HTTPException(401): 无权访问（付费视频未登录）
    """
    # 通过 file_id 查询视频
    result = await db.execute(
        select(Video).where(Video.vod_file_id == file_id)
    )
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 权限检查：如果是子视频，检查父视频的权限
    check_video = video
    if video.parent_id:
        parent_result = await db.execute(
            select(Video).where(Video.id == video.parent_id)
        )
        parent_video = parent_result.scalars().first()
        if parent_video:
            check_video = parent_video

    # 付费视频需要登录
    if not check_video.is_free and not user:
        raise HTTPException(
            status_code=401,
            detail="未登录或登录已过期，请重新登录"
        )

    return video
