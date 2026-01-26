from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

def _build_async_url(url: str) -> str:
    """将数据库 URL 转换为 asyncpg 格式
    
    支持多种 URL 格式：
    - postgresql://  (标准格式)
    - postgres://    (Zeabur/Heroku 格式)
    - postgresql+asyncpg://  (已经是 asyncpg 格式)
    """
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        # Zeabur 使用 postgres:// 格式
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url

async_url = settings.ASYNC_DATABASE_URL.strip() or _build_async_url(settings.DATABASE_URL)

engine = create_async_engine(
    async_url,
    pool_pre_ping=True,
    echo=False  # 生产环境设为 False
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


# 依赖注入
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
