from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.crud import get_score_record, get_user_score_records, get_top_score_records, get_total_score_records, create_score_record
from backend.app.schemas import ScoreRecordCreate, ScoreRecordResponse, ScoreRecordsListResponse
from backend.app.api.v1.auth import get_current_active_user
from typing import Optional


router = APIRouter()


# 创建分数记录
@router.post("/", response_model=ScoreRecordResponse, status_code=201)
async def create_record(record_in: ScoreRecordCreate, current_user = Depends(get_current_active_user)):
    """创建分数记录"""
    record = await create_score_record(current_user.id, record_in)
    return ScoreRecordResponse(data=record)


# 根据ID获取分数记录
@router.get("/{record_id}", response_model=ScoreRecordResponse)
async def get_record(record_id: int, current_user = Depends(get_current_active_user)):
    """根据ID获取分数记录"""
    record = await get_score_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="分数记录不存在")
    
    # 普通用户只能查看自己的分数记录，管理员可以查看所有记录
    if not current_user.is_admin and record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限查看该分数记录")
    
    return ScoreRecordResponse(data=record)


# 获取当前用户的分数记录
@router.get("/me", response_model=ScoreRecordsListResponse)
async def get_current_user_records(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页显示的记录数"),
    current_user = Depends(get_current_active_user)
):
    """获取当前用户的分数记录"""
    records = await get_user_score_records(current_user.id, skip=skip, limit=limit)
    total = await get_total_score_records()
    
    return ScoreRecordsListResponse(data=records, total=total)


# 获取最高分记录（排行榜）
@router.get("/top", response_model=ScoreRecordsListResponse)
async def get_top_records(
    limit: int = Query(10, ge=1, le=100, description="显示的记录数"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    current_user = Depends(get_current_active_user)
):
    """获取最高分记录（排行榜）"""
    records = await get_top_score_records(limit=limit, difficulty=difficulty)
    total = await get_total_score_records()
    
    return ScoreRecordsListResponse(data=records, total=total)
