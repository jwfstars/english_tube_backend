from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

def _build_async_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
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
