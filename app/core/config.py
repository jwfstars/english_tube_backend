from typing import List
from pydantic_settings import BaseSettings
import json


class Settings(BaseSettings):
    # API 配置
    PROJECT_NAME: str = "English Tube API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 数据库
    DATABASE_URL: str = "postgresql://english_tube:password@localhost:5432/english_tube"
    ASYNC_DATABASE_URL: str = ""

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8848",
        "http://192.168.50.140:8000",  # Mac 局域网 IP（真机调试）
        "*",  # 开发环境允许所有来源
    ]

    # 腾讯云短信
    TENCENT_SMS_SECRET_ID: str = ""
    TENCENT_SMS_SECRET_KEY: str = ""
    TENCENT_SMS_SDK_APP_ID: str = ""
    TENCENT_SMS_SIGN_NAME: str = ""
    TENCENT_SMS_TEMPLATE_ID: str = ""
    TENCENT_SMS_REGION: str = "ap-guangzhou"
    SMS_CODE_EXPIRE_MINUTES: int = 10
    SMS_DEBUG: bool = False

    # 激活码预注册
    ACTIVATION_SESSION_EXPIRE_MINUTES: int = 30

    # 腾讯云 VOD 播放签名
    VOD_APP_ID: int = 0
    VOD_PLAY_KEY: str = ""
    VOD_PSIGN_EXPIRE_SECONDS: int = 60 * 60
    VOD_PSIGN_AUDIO_VIDEO_TYPE: str = "Original"
    VOD_PSIGN_RAW_ADAPTIVE_DEFINITION: str = ""
    VOD_PSIGN_TRANSCODE_DEFINITION: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略 .env 中的额外字段（如 Docker Compose 变量）


settings = Settings()
