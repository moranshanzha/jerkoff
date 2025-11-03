from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.crud import get_user, get_user_by_username, update_user, delete_user
from backend.app.schemas import UserUpdate, UserResponse
from backend.app.api.v1.auth import get_current_active_user, get_current_admin_user


router = APIRouter()


# 获取当前用户信息
@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return UserResponse(data=current_user)


# 根据ID获取用户信息
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, current_user = Depends(get_current_active_user)):
    """根据ID获取用户信息"""
    # 普通用户只能查看自己的信息，管理员可以查看所有用户
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看该用户信息"
        )
    
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(data=user)


# 更新用户信息
@router.put("/{user_id}", response_model=UserResponse)
async def update_user_info(user_id: int, user_in: UserUpdate, current_user = Depends(get_current_active_user)):
    """更新用户信息"""
    # 普通用户只能更新自己的信息，管理员可以更新所有用户
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新该用户信息"
        )
    
    user = await update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(data=user)


# 删除用户
@router.delete("/{user_id}", response_model=dict)
async def delete_user_info(user_id: int, current_user = Depends(get_current_admin_user)):
    """删除用户"""
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"message": "用户已删除"}
