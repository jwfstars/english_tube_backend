#!/usr/bin/env python3
"""直接创建所有数据库表"""

import asyncio
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.database import Base

# 导入所有模型
from app.models.video import Video
from app.models.subtitle import Subtitle
from app.models.tag import Tag
from app.models.video_tag import VideoTag
from app.models.word_card import WordCard
from app.models.phrase_card import PhraseCard
from app.models.user import User
from app.models.sms_code import SmsCode
from app.models.user_video_progress import UserVideoProgress
from app.models.user_video_favorite import UserVideoFavorite
from app.models.user_word_favorite import UserWordFavorite
from app.models.user_subtitle_favorite import UserSubtitleFavorite
from app.models.user_phrase_favorite import UserPhraseFavorite

def create_tables():
    """创建所有表"""
    try:
        print("🔌 连接数据库...")
        engine = create_engine(settings.DATABASE_URL)
        
        print("🗄️  创建所有表...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ 所有表创建成功！")
        
        # 显示创建的表
        print("\n📋 已创建的表:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_tables()
    exit(0 if success else 1)
