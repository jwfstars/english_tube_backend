# 开发指南

## 🐍 虚拟环境

### Python 版本
- **Python 3.12.12**

### 激活虚拟环境

```bash
# 方法 1：使用激活脚本（推荐）
source activate_venv.sh

# 方法 2：直接激活
source venv/bin/activate

# 方法 3：使用绝对路径
source /Users/winfield/workspace/Apps/projects/english_tube_backend/venv/bin/activate
```

### 退出虚拟环境

```bash
deactivate
```

## 📦 依赖管理

### 安装新包

```bash
# 激活虚拟环境后
pip install package_name

# 或使用清华镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 安装所有依赖

```bash
# 使用清华镜像源（推荐）
pip install --trusted-host pypi.tuna.tsinghua.edu.cn -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 或使用配置文件
pip install -r requirements.txt
```

## 🚀 本地开发

### 启动开发服务器

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或指定不同端口
uvicorn app.main:app --reload --port 8002
```

访问：
- API 文档: http://localhost:8000/api/docs
- ReDoc 文档: http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/api/health

### 使用 Docker 开发

```bash
# 启动所有服务（PostgreSQL + Backend + Nginx）
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down

# 重启后端
docker-compose restart backend
```

## 🗄️ 数据库

### 本地 PostgreSQL（Docker）

```bash
# 连接数据库
docker-compose exec postgres psql -U english_tube -d english_tube

# 查看表
\dt

# 退出
\q
```

### 数据库迁移（Alembic）

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述你的更改"

# 执行迁移
alembic upgrade head

# 回滚一个版本
alembic downgrade -1

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### Docker 中执行迁移

```bash
# 执行迁移
docker-compose exec backend alembic upgrade head

# 创建迁移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 查看历史
docker-compose exec backend alembic history
```

## 🛠️ 开发工具

### 代码格式化

```bash
# 安装开发工具
pip install black isort flake8 mypy

# 格式化代码
black app/

# 整理 imports
isort app/

# 代码检查
flake8 app/

# 类型检查
mypy app/
```

### 测试

```bash
# 安装测试工具
pip install pytest pytest-asyncio pytest-cov httpx

# 运行测试
pytest

# 运行测试并显示覆盖率
pytest --cov=app --cov-report=html

# 运行特定测试
pytest tests/test_auth.py
```

## 🔧 环境变量

### 本地开发配置

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
vim .env
```

关键配置：
```bash
# 数据库（Docker）
DATABASE_URL=postgresql://english_tube:dev_local_password_2024@localhost:5432/english_tube
ASYNC_DATABASE_URL=postgresql+asyncpg://english_tube:dev_local_password_2024@localhost:5432/english_tube

# JWT
SECRET_KEY=your-secret-key-here

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:8858","http://localhost:3000"]
```

## 📝 常用命令

### 创建超级用户

```bash
# Docker 环境
docker-compose exec backend python -m scripts.create_superuser \
  --email admin@localhost.com \
  --password admin123 \
  --username admin

# 本地虚拟环境
python -m scripts.create_superuser \
  --email admin@localhost.com \
  --password admin123
```

### 查看日志

```bash
# Docker 日志
docker-compose logs -f backend

# 本地日志文件
tail -f logs/app.log
```

### 重启服务

```bash
# Docker
docker-compose restart backend

# 本地开发（Ctrl+C 后重启）
uvicorn app.main:app --reload
```

## 🐛 调试

### VSCode 调试配置

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### Python 调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用 breakpoint()
breakpoint()
```

## 📚 API 开发流程

### 1. 添加新模型

在 `app/models/` 创建新模型：

```python
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class MyModel(Base):
    __tablename__ = "my_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
```

### 2. 创建 Schema

在 `app/schemas/` 创建 Pydantic 模型：

```python
from pydantic import BaseModel

class MyModelBase(BaseModel):
    name: str

class MyModelCreate(MyModelBase):
    pass

class MyModel(MyModelBase):
    id: int
    
    class Config:
        from_attributes = True
```

### 3. 创建迁移

```bash
alembic revision --autogenerate -m "add my_model"
alembic upgrade head
```

### 4. 添加端点

在 `app/api/v1/endpoints/` 创建路由：

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/my-models")
async def list_models(db: AsyncSession = Depends(get_db)):
    # 实现逻辑
    pass
```

### 5. 注册路由

在 `app/api/v1/api.py` 注册：

```python
from app.api.v1.endpoints import my_models

api_router.include_router(
    my_models.router,
    prefix="/my-models",
    tags=["my-models"]
)
```

## 🔍 故障排查

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   # 杀死进程
   kill -9 <PID>
   ```

2. **数据库连接失败**
   - 检查 PostgreSQL 是否运行
   - 检查 `.env` 中的数据库连接字符串
   - 确认数据库端口未被占用

3. **依赖安装失败**
   - 使用清华镜像源
   - 检查 Python 版本是否为 3.12
   - 清理缓存：`pip cache purge`

4. **迁移失败**
   - 检查数据库连接
   - 查看迁移历史：`alembic history`
   - 回滚并重试

## 📖 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)

## 🎯 下一步

1. 熟悉项目结构
2. 查看 API 文档
3. 运行现有测试
4. 尝试添加新功能
5. 提交 Pull Request

有问题？查看 [README.md](./README.md) 或 [部署指南](./DEPLOYMENT_ZEABUR.md)。
