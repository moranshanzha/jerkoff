from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime


# 基础响应模型
class BaseResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("成功", description="响应消息")
    
    class Config:
        orm_mode = True


# 用户相关模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    avatar_url: Optional[str] = Field(None, description="头像URL")


class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True


class UserResponse(BaseResponse):
    data: Optional[UserInDB] = Field(None, description="用户数据")


# 游戏进度相关模型
class GameProgressCreate(BaseModel):
    level: Optional[int] = Field(1, description="当前关卡")
    score: Optional[int] = Field(0, description="当前分数")
    lives: Optional[int] = Field(3, description="剩余生命值")
    bombs: Optional[int] = Field(3, description="剩余炸弹数")
    game_state: Optional[Dict] = Field(None, description="游戏状态数据")


class GameProgressUpdate(BaseModel):
    level: Optional[int] = Field(None, description="当前关卡")
    score: Optional[int] = Field(None, description="当前分数")
    lives: Optional[int] = Field(None, description="剩余生命值")
    bombs: Optional[int] = Field(None, description="剩余炸弹数")
    game_state: Optional[Dict] = Field(None, description="游戏状态数据")


class GameProgressInDB(BaseModel):
    id: int
    user_id: int
    level: int
    score: int
    lives: int
    bombs: int
    game_state: Dict
    last_played_at: datetime
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True


class GameProgressResponse(BaseResponse):
    data: Optional[GameProgressInDB] = Field(None, description="游戏进度数据")


# 分数记录相关模型
class ScoreRecordCreate(BaseModel):
    score: int = Field(..., description="得分")
    level: Optional[int] = Field(1, description="关卡")
    difficulty: Optional[str] = Field("normal", description="难度")
    play_time: Optional[int] = Field(0, description="游戏时间（秒）")


class ScoreRecordInDB(BaseModel):
    id: int
    user_id: int
    score: int
    level: int
    difficulty: str
    play_time: int
    date: datetime
    
    class Config:
        orm_mode = True


class ScoreRecordResponse(BaseResponse):
    data: Optional[ScoreRecordInDB] = Field(None, description="分数记录数据")


class ScoreRecordsListResponse(BaseResponse):
    data: Optional[List[ScoreRecordInDB]] = Field(None, description="分数记录列表")
    total: Optional[int] = Field(None, description="总条数")


# 文件上传下载相关模型
class FileUploadResponse(BaseResponse):
    data: Optional[Dict[str, str]] = Field(None, description="文件信息")


class FileInDB(BaseModel):
    id: int
    user_id: Optional[int]
    filename: str
    file_path: str
    file_size: int
    content_type: str
    storage_type: str
    created_at: datetime
    
    class Config:
        orm_mode = True


class FileResponse(BaseResponse):
    data: Optional[FileInDB] = Field(None, description="文件信息")


# 认证相关模型
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
