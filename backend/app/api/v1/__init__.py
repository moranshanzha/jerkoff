from fastapi import APIRouter
from backend.app.api.v1 import users, game_progress, score_records, files, auth


# 创建API路由
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(game_progress.router, prefix="/game-progress", tags=["游戏进度"])
api_router.include_router(score_records.router, prefix="/score-records", tags=["分数记录"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
