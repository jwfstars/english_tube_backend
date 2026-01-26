from fastapi import APIRouter

from app.api.v1.endpoints import (
    videos,
    subtitles,
    tags,
    word_cards,
    phrase_cards,
    vod,
    auth,
    routes,
    users,
    learning,
    favorites,
)

api_router = APIRouter()

# 注册所有路由
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(subtitles.router, prefix="/subtitles", tags=["subtitles"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(word_cards.router, prefix="/word-cards", tags=["word-cards"])
api_router.include_router(phrase_cards.router, prefix="/phrase-cards", tags=["phrase-cards"])
api_router.include_router(vod.router, prefix="/vod", tags=["vod"])
api_router.include_router(auth.router)
api_router.include_router(routes.router)
api_router.include_router(users.router, tags=["users"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
