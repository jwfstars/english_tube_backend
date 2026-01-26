from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_accessible_video_by_file_id
from app.models.video import Video
from app.utils.vod_psign import generate_psign

router = APIRouter()


@router.get("/psign")
async def get_vod_psign(
    video: Video = Depends(get_accessible_video_by_file_id)
):
    """
    获取 VOD 播放签名 - 支持可选认证

    - **file_id**: VOD FileId（通过查询参数传递）
    - 免费视频：无需登录即可获取 psign
    - 付费视频：需要登录才能获取 psign
    - 子视频继承父视频的权限设置
    """
    try:
        return generate_psign(video.vod_file_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
