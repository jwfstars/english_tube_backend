from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.video import VideoResponse
from app.schemas.subtitle import SubtitleResponse
from app.schemas.word_card import WordCardResponse
from app.schemas.phrase_card import PhraseCardResponse


class LearningProgressUpdateRequest(BaseModel):
    video_id: UUID
    current_progress: int = Field(..., ge=0, description="当前进度（秒）")
    total_duration: Optional[int] = Field(None, gt=0, description="视频总时长（秒）")
    is_completed: Optional[bool] = Field(None, description="是否手动标记完成")


class LearningProgressResponse(BaseModel):
    video_id: UUID
    current_progress: int
    total_duration: int
    progress_percent: float
    is_completed: bool
    last_watched_at: datetime
    completed_at: Optional[datetime] = None


class LearningRecentItem(BaseModel):
    video: VideoResponse
    current_progress: int
    total_duration: int
    progress_percent: float
    last_watched_at: datetime
    is_completed: bool
    completed_at: Optional[datetime] = None


class LearningRecentResponse(BaseModel):
    total: int
    items: List[LearningRecentItem]


class LearningCompletedItem(BaseModel):
    video: VideoResponse
    completed_at: datetime


class LearningCompletedResponse(BaseModel):
    total: int
    items: List[LearningCompletedItem]


class FavoriteItem(BaseModel):
    video: VideoResponse
    favorited_at: datetime


class FavoriteListResponse(BaseModel):
    total: int
    items: List[FavoriteItem]


class FavoriteActionResponse(BaseModel):
    video_id: UUID
    is_favorite: bool


class FavoriteCheckResponse(BaseModel):
    video_id: UUID
    is_favorite: bool


class FavoriteBatchCheckRequest(BaseModel):
    video_ids: List[UUID]


class FavoriteBatchCheckResponse(BaseModel):
    results: dict[str, bool]


# Subtitle Favorites
class SubtitleFavoriteItem(BaseModel):
    subtitle: SubtitleResponse
    video: VideoResponse
    favorited_at: datetime


class SubtitleFavoriteListResponse(BaseModel):
    total: int
    items: List[SubtitleFavoriteItem]


class SubtitleFavoriteActionResponse(BaseModel):
    subtitle_id: int
    is_favorite: bool


class SubtitleFavoriteCheckResponse(BaseModel):
    subtitle_id: int
    is_favorite: bool


# Word Favorites (Word Book)
class WordFavoriteItem(BaseModel):
    word_card: WordCardResponse
    video: VideoResponse
    favorited_at: datetime


class WordFavoriteListResponse(BaseModel):
    total: int
    items: List[WordFavoriteItem]


class WordFavoriteActionResponse(BaseModel):
    word_card_id: UUID
    is_favorite: bool


class WordFavoriteCheckResponse(BaseModel):
    word_card_id: UUID
    is_favorite: bool


# Phrase Favorites
class PhraseFavoriteItem(BaseModel):
    phrase_card: PhraseCardResponse
    video: VideoResponse
    favorited_at: datetime


class PhraseFavoriteListResponse(BaseModel):
    total: int
    items: List[PhraseFavoriteItem]


class PhraseFavoriteActionResponse(BaseModel):
    phrase_card_id: UUID
    is_favorite: bool


class PhraseFavoriteCheckResponse(BaseModel):
    phrase_card_id: UUID
    is_favorite: bool

