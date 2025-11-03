from pydantic_settings import BaseSettings
from typing import Optional, Dict, List
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent


class Settings(BaseSettings):
    # 应用基本配置
    PROJECT_NAME: str = "飞机游戏后端框架"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: Optional[str] = None
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Celery 配置
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # 文件存储配置
    STORAGE_TYPE: str = "local"  # 可选值: local, s3, oss
    
    # 本地存储配置
    LOCAL_STORAGE_PATH: Path = get_project_root() / "backend" / "storage"
    
    # AWS S3 配置
    AWS_S3_BUCKET_NAME: Optional[str] = None
    AWS_S3_ACCESS_KEY_ID: Optional[str] = None
    AWS_S3_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_REGION_NAME: Optional[str] = None
    
    # 阿里云 OSS 配置
    ALIYUN_OSS_BUCKET_NAME: Optional[str] = None
    ALIYUN_OSS_ACCESS_KEY_ID: Optional[str] = None
    ALIYUN_OSS_ACCESS_KEY_SECRET: Optional[str] = None
    ALIYUN_OSS_ENDPOINT: Optional[str] = None
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif",
        "application/octet-stream", "application/json"
    ]
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:5000"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# 初始化配置
settings = Settings()

# 确保存储目录存在
if settings.STORAGE_TYPE == "local":
    settings.LOCAL_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

# 如果未提供数据库URL，默认使用SQLite
if not settings.DATABASE_URL:
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{get_project_root()}/backend/app.db"

# 如果未提供Celery配置，默认使用Redis
if not settings.CELERY_BROKER_URL:
    settings.CELERY_BROKER_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
if not settings.CELERY_RESULT_BACKEND:
    settings.CELERY_RESULT_BACKEND = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
