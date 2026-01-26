from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import os
import time
from pathlib import Path

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import get_db

# 确保日志目录存在
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/api/docs",  # 文档路径改为 /api/docs
    redoc_url="/api/redoc",  # ReDoc 路径改为 /api/redoc
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求的详细信息"""
    start_time = time.time()

    # 获取请求信息
    method = request.method
    url = str(request.url)
    client_host = request.client.host if request.client else "unknown"

    # 记录请求
    logger.info(f"→ {method} {url} from {client_host}")

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 记录响应
    status_code = response.status_code
    if status_code >= 400:
        logger.warning(f"← {method} {url} - {status_code} ({process_time:.3f}s)")
    else:
        logger.info(f"← {method} {url} - {status_code} ({process_time:.3f}s)")

    return response

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "message": "English Tube API",
        "version": settings.VERSION,
        "docs": "/api/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    健康检查端点
    检查服务和数据库连接状态
    """
    try:
        # 检查数据库连接
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"

    return {
        "status": "ok",
        "database": db_status,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
