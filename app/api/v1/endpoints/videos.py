from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func as sql_func, text, select, delete, or_

from app.auth import fastapi_users, current_user_optional
from app.core.database import get_db
from app.models.tag import Tag
from app.models.user import User
from app.models.video import Video
from app.models.video_tag import VideoTag
from app.schemas import VideoCreate, VideoUpdate, VideoResponse, VideoListResponse, VideoDetailResponse, VideoBrief

router = APIRouter()

# 鉴权依赖
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

DEFAULT_TAG_TYPE = "topic"


def _ensure_https_url(url: Optional[str]) -> Optional[str]:
    """确保 URL 包含 https:// 前缀"""
    if not url:
        return url
    if url.startswith(('http://', 'https://')):
        return url
    return f'https://{url}'


def _normalize_names(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    normalized = []
    seen = set()
    for value in values:
        if not value or not isinstance(value, str):
            continue
        name = value.strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(name)
    return normalized


async def _upsert_tags(db: AsyncSession, tag_names: List[str]) -> List[Tag]:
    if not tag_names:
        return []
    result = await db.execute(select(Tag).where(Tag.name.in_(tag_names)))
    existing = result.scalars().all()
    existing_map = {tag.name: tag for tag in existing}
    created = []
    for name in tag_names:
        if name in existing_map:
            continue
        tag = Tag(name=name, type=DEFAULT_TAG_TYPE)
        db.add(tag)
        created.append(tag)
    await db.flush()
    return existing + created


async def _set_video_tags(
    db: AsyncSession, video: Video, tags: Optional[List[str]]
) -> Optional[List[str]]:
    if tags is None:
        return None
    normalized = _normalize_names(tags)
    await db.execute(delete(VideoTag).where(VideoTag.video_id == video.id))
    if not normalized:
        return []
    tags = await _upsert_tags(db, normalized)
    for tag in tags:
        db.add(VideoTag(video_id=video.id, tag_id=tag.id))
    return normalized


def _get_video_tags(video: Video) -> List[str]:
    return [vt.tag.name for vt in video.video_tags if vt.tag]


def _video_to_dict(video: Video, segment_count: int = 0, tags: Optional[List[str]] = None) -> dict:
    return {
        'id': video.id,
        'title': video.title,
        'title_zh': video.title_zh,
        'description': video.description,
        'description_zh': video.description_zh,
        'video_url': video.video_url,
        'vod_file_id': video.vod_file_id,
        'thumbnail_url': _ensure_https_url(video.thumbnail_url),
        'duration': video.duration,
        'difficulty': video.difficulty,
        'youtube_id': video.youtube_id,
        'youtube_url': video.youtube_url,
        'original_author': video.original_author,
        'author_avatar_url': _ensure_https_url(video.author_avatar_url),
        'tags': tags if tags is not None else _get_video_tags(video),
        'categories': video.categories_zh or video.categories or [],
        'categories_zh': video.categories_zh or [],
        'status': video.status,
        'is_published': video.is_published,
        'is_free': video.is_free,
        'display_order': video.display_order,
        'parent_id': video.parent_id,
        'segment_index': video.segment_index,
        'video_type': video.video_type or 'full',
        'segment_count': segment_count,
        'created_at': video.created_at,
        'updated_at': video.updated_at,
    }


async def _add_segment_count(videos: List[Video], db: AsyncSession) -> List[dict]:
    """为视频列表添加 segment_count 字段"""
    if not videos:
        return []

    # 获取所有视频组的 ID
    group_ids = [v.id for v in videos if v.video_type == 'group']

    # 批量查询每个视频组的子视频数量
    segment_counts = {}
    if group_ids:
        result = await db.execute(
            select(
                Video.parent_id,
                sql_func.count(Video.id).label('count')
            ).where(
                Video.parent_id.in_(group_ids)
            ).group_by(Video.parent_id)
        )
        counts = result.all()

        segment_counts = {str(parent_id): count for parent_id, count in counts}

    # 构造响应
    result = []
    for video in videos:
        result.append(_video_to_dict(video, segment_counts.get(str(video.id), 0)))

    return result


@router.get("/", response_model=VideoListResponse)
async def get_videos(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    search: Optional[str] = Query(None, description="搜索关键词（标题、作者、分类）"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    is_published: Optional[bool] = Query(None, description="是否发布"),
    video_type: Optional[str] = Query(None, description="视频类型筛选: full/segment/group"),
    parent_id: Optional[UUID] = Query(None, description="父视频ID，获取某视频组下的片段"),
    original_author: Optional[str] = Query(None, description="按原作者/频道筛选"),
    min_duration: Optional[int] = Query(None, ge=0, description="最小时长（秒）"),
    max_duration: Optional[int] = Query(None, ge=0, description="最大时长（秒）"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(current_user_optional),
):
    """
    获取视频列表 - 支持搜索和筛选

    - **skip**: 跳过记录数（分页）
    - **limit**: 每页记录数
    - **search**: 搜索关键词，匹配标题、描述、作者、分类
    - **difficulty**: 难度筛选（beginner/intermediate/advanced）
    - **is_published**: 是否只显示已发布的视频
    - **video_type**: 视频类型筛选（full/segment/group）
    - **parent_id**: 获取某视频组下的片段
    - **original_author**: 按原作者/频道筛选
    - **min_duration**: 最小时长（秒）
    - **max_duration**: 最大时长（秒）

    **访问控制**:
    - 未认证用户：默认只返回已发布的视频
    - 已认证用户：默认返回所有视频（包括未发布的）
    - 可通过 is_published 参数明确指定筛选条件

    默认只返回主视频（full 和 group），不返回片段（segment）。
    返回的视频包含 is_free 字段，前端可根据此字段显示锁图标。
    """
    query = select(Video)

    # 发布状态筛选
    if is_published is None:
        # 如果未明确指定，根据认证状态决定
        if not user:
            # 未认证用户只能看到已发布的视频
            query = query.where(Video.is_published == True)
        # 已认证用户可以看到所有视频
    else:
        # 明确指定了 is_published 参数
        query = query.where(Video.is_published == is_published)

    # 搜索功能
    if search and search.strip():
        search_pattern = f"%{search.strip()}%"
        # 构建搜索条件：匹配标题、描述、作者
        search_conditions = [
            Video.title.ilike(search_pattern),
            Video.title_zh.ilike(search_pattern),
            Video.description.ilike(search_pattern),
            Video.description_zh.ilike(search_pattern),
            Video.original_author.ilike(search_pattern),
        ]

        # 搜索分类（JSONB 数组）
        # 使用 JSONB 的 @> 操作符检查数组是否包含元素
        try:
            # 尝试匹配完整的分类名称
            search_conditions.append(
                Video.categories.cast(text("text")).ilike(search_pattern)
            )
            search_conditions.append(
                Video.categories_zh.cast(text("text")).ilike(search_pattern)
            )
        except Exception:
            # 如果转换失败，忽略分类搜索
            pass

        query = query.where(or_(*search_conditions))

    # 筛选条件
    if difficulty:
        query = query.where(Video.difficulty == difficulty)
    if video_type:
        query = query.where(Video.video_type == video_type)
    if parent_id:
        query = query.where(Video.parent_id == parent_id)
    if original_author:
        query = query.where(Video.original_author == original_author)
    if min_duration is not None:
        query = query.where(Video.duration >= min_duration)
    if max_duration is not None:
        query = query.where(Video.duration <= max_duration)

    # 默认排除片段，除非明确指定 video_type=segment 或 parent_id
    if not video_type and not parent_id:
        query = query.where(Video.video_type != 'segment')

    # 总数
    total_result = await db.execute(
        select(sql_func.count()).select_from(query.subquery())
    )
    total = total_result.scalar_one()

    # 分页和排序
    if parent_id:
        # 如果是查询片段，按 segment_index 排序
        stmt = query.options(
            selectinload(Video.video_tags).selectinload(VideoTag.tag)
        ).order_by(Video.segment_index.asc()).offset(skip).limit(limit)
    else:
        stmt = query.options(
            selectinload(Video.video_tags).selectinload(VideoTag.tag)
        ).order_by(Video.display_order.desc(), Video.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    videos = result.scalars().all()

    # 添加 segment_count 字段
    items = await _add_segment_count(videos, db)

    return VideoListResponse(total=total, items=items)


@router.get("/categories", response_model=List[str])
async def get_video_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有视频分类（去重）- 公开接口
    """
    result = await db.execute(text("""
        SELECT DISTINCT jsonb_array_elements_text(
            CASE
                WHEN categories_zh IS NULL OR jsonb_array_length(categories_zh) = 0
                THEN categories
                ELSE categories_zh
            END
        ) AS category
        FROM videos
        WHERE (categories IS NOT NULL AND jsonb_array_length(categories) > 0)
           OR (categories_zh IS NOT NULL AND jsonb_array_length(categories_zh) > 0)
    """))
    rows = result.all()

    categories = sorted(
        {row[0].strip() for row in rows if row[0] and row[0].strip()},
        key=str.lower,
    )
    return categories


@router.get("/authors", response_model=List[dict])
async def get_video_authors(
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有视频作者/频道列表（去重）- 公开接口

    返回格式：
    [
        {
            "name": "频道名称",
            "avatar_url": "头像URL",
            "video_count": 视频数量
        }
    ]
    """
    result = await db.execute(text("""
        SELECT
            original_author,
            author_avatar_url,
            COUNT(*) as video_count
        FROM videos
        WHERE original_author IS NOT NULL
          AND original_author != ''
          AND video_type != 'segment'
        GROUP BY original_author, author_avatar_url
        ORDER BY video_count DESC, original_author ASC
    """))
    rows = result.all()

    authors = [
        {
            "name": row[0],
            "avatar_url": row[1],
            "video_count": row[2]
        }
        for row in rows
    ]
    return authors


@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(current_user_optional),
):
    """
    获取单个视频详情 - 支持可选认证

    - **video_id**: 视频 UUID
    - 如果是视频组，会返回其下的所有片段列表

    **访问控制**:
    - 免费视频 (is_free=true): 任何人都可以访问
    - 付费视频 (is_free=false): 需要登录才能访问
    - 子视频继承父视频的权限设置
    """
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 访问控制：如果是子视频，检查父视频的权限；否则检查自身权限
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
            detail="该视频需要登录后观看，请先登录或注册"
        )

    # 手动获取tags
    tag_result = await db.execute(
        select(Tag)
        .join(VideoTag, VideoTag.tag_id == Tag.id)
        .where(VideoTag.video_id == video_id)
    )
    tags = [tag.name for tag in tag_result.scalars().all()]

    # 如果是视频组，获取其下的片段
    segments = []
    if video.video_type == 'group':
        result = await db.execute(
            select(Video)
            .where(Video.parent_id == video_id)
            .order_by(Video.segment_index.asc())
        )
        segment_videos = result.scalars().all()

        segments = [
            VideoBrief(
                id=seg.id,
                title=seg.title,
                title_zh=seg.title_zh,
                duration=seg.duration,
                segment_index=seg.segment_index,
                thumbnail_url=_ensure_https_url(seg.thumbnail_url),
                vod_file_id=seg.vod_file_id,
            )
            for seg in segment_videos
        ]

    # 构造响应
    response = VideoDetailResponse(
        id=video.id,
        title=video.title,
        title_zh=video.title_zh,
        description=video.description,
        description_zh=video.description_zh,
        video_url=video.video_url,
        vod_file_id=video.vod_file_id,
        thumbnail_url=_ensure_https_url(video.thumbnail_url),
        duration=video.duration,
        difficulty=video.difficulty,
        youtube_id=video.youtube_id,
        youtube_url=video.youtube_url,
        original_author=video.original_author,
        tags=tags,
        categories=video.categories_zh or video.categories or [],
        categories_zh=video.categories_zh or [],
        status=video.status,
        is_published=video.is_published,
        is_free=video.is_free,
        display_order=video.display_order,
        parent_id=video.parent_id,
        segment_index=video.segment_index,
        video_type=video.video_type or 'full',
        segment_count=len(segments),
        created_at=video.created_at,
        updated_at=video.updated_at,
        segments=segments,
    )

    return response


@router.get("/{video_id}/segments", response_model=List[VideoBrief])
async def get_video_segments(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(current_user_optional),
):
    """
    获取视频组下的所有片段 - 支持可选认证

    - **video_id**: 视频组 UUID

    **访问控制**:
    - 免费视频组: 任何人都可以访问
    - 付费视频组: 需要登录才能访问
    - 子视频继承父视频（视频组）的权限
    """
    # 验证视频存在
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 访问控制：检查父视频（视频组）的权限
    if not video.is_free and not user:
        raise HTTPException(
            status_code=401,
            detail="该视频需要登录后观看，请先登录或注册"
        )

    # 获取片段
    result = await db.execute(
        select(Video)
        .where(Video.parent_id == video_id)
        .order_by(Video.segment_index.asc())
    )
    segments = result.scalars().all()

    return [
        VideoBrief(
            id=seg.id,
            title=seg.title,
            title_zh=seg.title_zh,
            duration=seg.duration,
            segment_index=seg.segment_index,
            thumbnail_url=_ensure_https_url(seg.thumbnail_url),
            vod_file_id=seg.vod_file_id,
        )
        for seg in segments
    ]


@router.get("/by-youtube-id/{youtube_id}", response_model=VideoResponse)
async def get_video_by_youtube_id(
    youtube_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(current_user_optional),
):
    """
    根据 YouTube ID 获取视频 - 支持可选认证

    - **youtube_id**: YouTube 视频 ID

    **访问控制**:
    - 免费视频: 任何人都可以访问
    - 付费视频: 需要登录才能访问
    """
    result = await db.execute(
        select(Video).where(Video.youtube_id == youtube_id)
    )
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 访问控制：付费视频需要登录
    if not video.is_free and not user:
        raise HTTPException(
            status_code=401,
            detail="该视频需要登录后观看，请先登录或注册"
        )
    segment_count = 0
    if video.video_type == 'group':
        count_result = await db.execute(
            select(sql_func.count()).select_from(Video).where(Video.parent_id == video.id)
        )
        segment_count = count_result.scalar_one()
    return _video_to_dict(video, segment_count)


@router.post("/", response_model=VideoResponse, status_code=201)
async def create_video(
    video_in: VideoCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    创建新视频

    需要提供视频的基本信息，包括标题、URL、时长等。

    **视频类型 (video_type)**:
    - `full`: 完整视频（默认）
    - `segment`: 视频片段（需要指定 parent_id 和 segment_index）
    - `group`: 视频组（包含多个片段的父视频）
    """
    # 检查 youtube_id 是否已存在
    if video_in.youtube_id:
        result = await db.execute(
            select(Video).where(Video.youtube_id == video_in.youtube_id)
        )
        existing = result.scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="该 YouTube 视频已存在")

    # 如果是片段，验证父视频存在
    if video_in.parent_id:
        result = await db.execute(
            select(Video).where(Video.id == video_in.parent_id)
        )
        parent = result.scalars().first()
        if not parent:
            raise HTTPException(status_code=400, detail="父视频不存在")
        # 自动设置为片段类型
        video_in_dict = video_in.model_dump()
        video_in_dict['video_type'] = 'segment'
        tags = video_in_dict.pop("tags", None)
        categories = video_in_dict.pop("categories", None)
        categories_zh = video_in_dict.pop("categories_zh", None)
        video = Video(**video_in_dict)
    else:
        video_in_dict = video_in.model_dump()
        tags = video_in_dict.pop("tags", None)
        categories = video_in_dict.pop("categories", None)
        categories_zh = video_in_dict.pop("categories_zh", None)
        video = Video(**video_in_dict)

    if categories is not None:
        video.categories = _normalize_names(categories)
    if categories_zh is not None:
        video.categories_zh = _normalize_names(categories_zh)
    db.add(video)
    await db.flush()
    normalized_tags = await _set_video_tags(db, video, tags)
    await db.commit()
    await db.refresh(video)
    # 传入 normalized_tags 避免懒加载触发 MissingGreenlet 错误
    payload = _video_to_dict(video, segment_count=0, tags=normalized_tags or [])
    return payload


@router.patch("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: UUID,
    video_in: VideoUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    更新视频信息

    - **video_id**: 视频 UUID
    - 只更新提供的字段
    """
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    # 更新字段
    update_data = video_in.model_dump(exclude_unset=True)
    tags = update_data.pop("tags", None)
    categories = update_data.pop("categories", None)
    categories_zh = update_data.pop("categories_zh", None)
    for field, value in update_data.items():
        setattr(video, field, value)

    if categories is not None:
        video.categories = _normalize_names(categories)
    if categories_zh is not None:
        video.categories_zh = _normalize_names(categories_zh)
    normalized_tags = await _set_video_tags(db, video, tags)
    await db.commit()

    # 重新加载视频以获取最新数据，并预加载关联的 tags
    result = await db.execute(
        select(Video)
        .options(selectinload(Video.video_tags).selectinload(VideoTag.tag))
        .where(Video.id == video_id)
    )
    video = result.scalars().first()

    # 如果有 normalized_tags，使用它；否则从预加载的关系中获取
    if normalized_tags is not None:
        payload = _video_to_dict(video, segment_count=0, tags=normalized_tags)
    else:
        payload = _video_to_dict(video, segment_count=0)
    return payload


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(current_superuser),
):
    """
    删除视频

    - **video_id**: 视频 UUID
    - 会级联删除相关的字幕和学习卡片
    - 如果是视频组，会级联删除所有片段
    """
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")

    await db.delete(video)
    await db.commit()
    return None
