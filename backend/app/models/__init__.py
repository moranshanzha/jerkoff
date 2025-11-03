from tortoise.models import Model
from tortoise import fields
from typing import Optional
from datetime import datetime


class BaseModel(Model):
    """基础模型，包含通用字段"""
    id = fields.IntField(pk=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)
    
    class Meta:
        abstract = True


class User(BaseModel):
    """用户模型"""
    username = fields.CharField(max_length=50, unique=True, index=True)
    email = fields.CharField(max_length=100, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    avatar_url = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=100, null=True)
    is_admin = fields.BooleanField(default=False)
    
    class Meta:
        table = "users"


class GameProgress(BaseModel):
    """游戏进度模型"""
    user = fields.ForeignKeyField("models.User", related_name="game_progress")
    level = fields.IntField(default=1)
    score = fields.IntField(default=0)
    lives = fields.IntField(default=3)
    bombs = fields.IntField(default=3)
    game_state = fields.JSONField(default=dict)
    last_played_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "game_progress"


class ScoreRecord(BaseModel):
    """分数记录模型"""
    user = fields.ForeignKeyField("models.User", related_name="score_records")
    score = fields.IntField(index=True)
    level = fields.IntField(default=1)
    difficulty = fields.CharField(max_length=20, default="normal")  # easy, normal, hard
    play_time = fields.IntField(default=0)  # 游戏时间（秒）
    date = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "score_records"
        ordering = ["-score"]


class File(BaseModel):
    """文件存储模型"""
    user = fields.ForeignKeyField("models.User", related_name="files", null=True)
    filename = fields.CharField(max_length=255)
    file_path = fields.CharField(max_length=500)
    file_size = fields.IntField()
    content_type = fields.CharField(max_length=100)
    storage_type = fields.CharField(max_length=20, default="local")  # local, s3, oss
    
    class Meta:
        table = "files"
