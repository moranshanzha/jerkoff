from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from backend.app.models import User, GameProgress, ScoreRecord, File
from backend.app.schemas import (
    UserCreate, UserUpdate,
    GameProgressCreate, GameProgressUpdate,
    ScoreRecordCreate,
)
from backend.app.core.config import settings
from backend.app.utils import generate_file_hash, generate_unique_filename
import bcrypt


# 用户相关CRUD操作
async def create_user(user_in: UserCreate) -> User:
    """创建用户"""
    # 检查用户是否已存在
    existing_user = await User.get_or_none(username=user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    existing_email = await User.get_or_none(email=user_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 哈希密码
    hashed_password = bcrypt.hashpw(user_in.password.encode('utf-8'), bcrypt.gensalt())
    
    # 创建用户
    user = await User.create(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password.decode('utf-8'),
        full_name=user_in.full_name,
        is_admin=False,
        is_active=True
    )
    
    return user


async def get_user(user_id: int) -> Optional[User]:
    """获取用户"""
    return await User.get_or_none(id=user_id, is_active=True)


async def get_user_by_username(username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return await User.get_or_none(username=username, is_active=True)


async def update_user(user_id: int, user_in: UserUpdate) -> User:
    """更新用户"""
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    update_data = user_in.dict(exclude_unset=True)
    await user.update_from_dict(update_data).save()
    
    return user


async def delete_user(user_id: int) -> bool:
    """删除用户（软删除）"""
    user = await get_user(user_id)
    if not user:
        return False
    
    user.is_active = False
    await user.save()
    
    return True


# 游戏进度相关CRUD操作
async def create_game_progress(user_id: int, progress_in: GameProgressCreate) -> GameProgress:
    """创建游戏进度"""
    # 检查用户是否存在
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 创建游戏进度
    progress = await GameProgress.create(
        user_id=user_id,
        level=progress_in.level,
        score=progress_in.score,
        lives=progress_in.lives,
        bombs=progress_in.bombs,
        game_state=progress_in.game_state or {},
    )
    
    return progress


async def get_game_progress(progress_id: int) -> Optional[GameProgress]:
    """获取游戏进度"""
    return await GameProgress.get_or_none(id=progress_id, is_active=True)


async def get_user_game_progress(user_id: int) -> Optional[GameProgress]:
    """获取用户的游戏进度"""
    return await GameProgress.get_or_none(user_id=user_id, is_active=True)


async def update_game_progress(progress_id: int, progress_in: GameProgressUpdate) -> GameProgress:
    """更新游戏进度"""
    progress = await get_game_progress(progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="游戏进度不存在")
    
    # 更新游戏进度
    update_data = progress_in.dict(exclude_unset=True)
    await progress.update_from_dict(update_data).save()
    
    return progress


async def delete_game_progress(progress_id: int) -> bool:
    """删除游戏进度"""
    progress = await get_game_progress(progress_id)
    if not progress:
        return False
    
    progress.is_active = False
    await progress.save()
    
    return True


# 分数记录相关CRUD操作
async def create_score_record(user_id: int, record_in: ScoreRecordCreate) -> ScoreRecord:
    """创建分数记录"""
    # 检查用户是否存在
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 创建分数记录
    record = await ScoreRecord.create(
        user_id=user_id,
        score=record_in.score,
        level=record_in.level,
        difficulty=record_in.difficulty,
        play_time=record_in.play_time,
    )
    
    return record


async def get_score_record(record_id: int) -> Optional[ScoreRecord]:
    """获取分数记录"""
    return await ScoreRecord.get_or_none(id=record_id)


async def get_user_score_records(user_id: int, skip: int = 0, limit: int = 10) -> List[ScoreRecord]:
    """获取用户的分数记录"""
    return await ScoreRecord.filter(user_id=user_id).order_by('-score').offset(skip).limit(limit).all()


async def get_top_score_records(limit: int = 10, difficulty: str = None) -> List[ScoreRecord]:
    """获取最高分记录"""
    query = ScoreRecord.all().order_by('-score')
    
    if difficulty:
        query = query.filter(difficulty=difficulty)
    
    return await query.limit(limit).all()


async def get_total_score_records() -> int:
    """获取总分数记录数"""
    return await ScoreRecord.all().count()


# 文件相关CRUD操作
async def create_file_record(user_id: int, filename: str, file_path: str, file_size: int, content_type: str, storage_type: str) -> File:
    """创建文件记录"""
    # 创建文件记录
    file = await File.create(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        content_type=content_type,
        storage_type=storage_type,
    )
    
    return file


async def get_file(file_id: int) -> Optional[File]:
    """获取文件记录"""
    return await File.get_or_none(id=file_id)


async def get_user_files(user_id: int, skip: int = 0, limit: int = 10) -> List[File]:
    """获取用户的文件记录"""
    return await File.filter(user_id=user_id).offset(skip).limit(limit).all()


async def delete_file(file_id: int) -> bool:
    """删除文件"""
    file = await get_file(file_id)
    if not file:
        return False
    
    await file.delete()
    
    return True
