from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.crud import get_game_progress, get_user_game_progress, create_game_progress, update_game_progress, delete_game_progress
from backend.app.schemas import GameProgressCreate, GameProgressUpdate, GameProgressResponse
from backend.app.api.v1.auth import get_current_active_user


router = APIRouter()


# 创建游戏进度
@router.post("/", response_model=GameProgressResponse, status_code=status.HTTP_201_CREATED)
async def create_progress(progress_in: GameProgressCreate, current_user = Depends(get_current_active_user)):
    """创建游戏进度"""
    # 检查用户是否已有游戏进度
    existing_progress = await get_user_game_progress(current_user.id)
    if existing_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已存在游戏进度，无法创建新的进度"
        )
    
    progress = await create_game_progress(current_user.id, progress_in)
    return GameProgressResponse(data=progress)


# 获取当前用户的游戏进度
@router.get("/me", response_model=GameProgressResponse)
async def get_current_user_progress(current_user = Depends(get_current_active_user)):
    """获取当前用户的游戏进度"""
    progress = await get_user_game_progress(current_user.id)
    if not progress:
        raise HTTPException(status_code=404, detail="游戏进度不存在")
    
    return GameProgressResponse(data=progress)


# 根据ID获取游戏进度
@router.get("/{progress_id}", response_model=GameProgressResponse)
async def get_progress(progress_id: int, current_user = Depends(get_current_active_user)):
    """根据ID获取游戏进度"""
    progress = await get_game_progress(progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="游戏进度不存在")
    
    # 普通用户只能查看自己的游戏进度，管理员可以查看所有进度
    if not current_user.is_admin and progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看该游戏进度"
        )
    
    return GameProgressResponse(data=progress)


# 更新游戏进度
@router.put("/{progress_id}", response_model=GameProgressResponse)
async def update_progress(progress_id: int, progress_in: GameProgressUpdate, current_user = Depends(get_current_active_user)):
    """更新游戏进度"""
    progress = await get_game_progress(progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="游戏进度不存在")
    
    # 普通用户只能更新自己的游戏进度，管理员可以更新所有进度
    if not current_user.is_admin and progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新该游戏进度"
        )
    
    updated_progress = await update_game_progress(progress_id, progress_in)
    return GameProgressResponse(data=updated_progress)


# 删除游戏进度
@router.delete("/{progress_id}", response_model=dict)
async def delete_progress(progress_id: int, current_user = Depends(get_current_active_user)):
    """删除游戏进度"""
    progress = await get_game_progress(progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="游戏进度不存在")
    
    # 普通用户只能删除自己的游戏进度，管理员可以删除所有进度
    if not current_user.is_admin and progress.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除该游戏进度"
        )
    
    success = await delete_game_progress(progress_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除游戏进度失败")
    
    return {"message": "游戏进度已删除"}
