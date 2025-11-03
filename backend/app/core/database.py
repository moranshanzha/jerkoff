from typing import AsyncGenerator
from fastapi import Depends
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise
from backend.app.core.config import settings


async def init_db() -> None:
    """初始化数据库连接"""
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["backend.app.models"]},
    )
    
    # 创建数据库表
    await Tortoise.generate_schemas(safe=True)


async def close_db() -> None:
    """关闭数据库连接"""
    await Tortoise.close_connections()


# 数据库依赖项
async def get_db() -> AsyncGenerator:
    """获取数据库连接"""
    # 对于Tortoise ORM，我们不需要显式地获取和释放连接
    # 它会自动管理连接池
    yield None


# 注册Tortoise ORM到FastAPI应用

def register_database(app) -> None:
    register_tortoise(
        app,
        db_url=settings.DATABASE_URL,
        modules={"models": ["backend.app.models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
