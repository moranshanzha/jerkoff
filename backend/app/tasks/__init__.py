from celery import shared_task
from backend.app.core.config import settings
from backend.app.core.storage import get_storage_backend
from backend.app.models import File
from datetime import datetime, timedelta
import os


@shared_task
async def process_file_upload(file_id: int) -> None:
    """处理文件上传后的异步任务"""
    # 获取文件信息
    file = await File.get_or_none(id=file_id)
    if not file:
        return
    
    # 这里可以添加文件处理逻辑，例如：
    # 1. 图片压缩
    # 2. 视频转码
    # 3. 文档转换
    # 4. 其他自定义处理
    
    # 示例：更新文件处理状态
    file.is_active = True
    await file.save()


@shared_task
async def clean_expired_files(days: int = 30) -> int:
    """清理过期文件"""
    storage = get_storage_backend()
    
    # 计算过期时间
    expiration_date = datetime.now() - timedelta(days=days)
    
    # 查询过期文件
    expired_files = await File.filter(created_at__lt=expiration_date).all()
    
    deleted_count = 0
    for file in expired_files:
        try:
            # 从存储中删除文件
            await storage.delete_file(file.file_path)
            
            # 从数据库中删除记录
            await file.delete()
            
            deleted_count += 1
        except Exception:
            # 如果删除失败，继续处理下一个文件
            continue
    
    return deleted_count


@shared_task
async def generate_game_stats() -> Dict[str, any]:
    """生成游戏统计数据"""
    from backend.app.models import User, ScoreRecord
    
    # 获取统计数据
    total_users = await User.filter(is_active=True).count()
    total_games = await ScoreRecord.all().count()
    
    # 获取最高分
    highest_score = await ScoreRecord.all().order_by('-score').first()
    highest_score_data = {
        'score': highest_score.score if highest_score else 0,
        'user_id': highest_score.user_id if highest_score else None,
        'date': highest_score.date if highest_score else None
    }
    
    # 获取平均分数
    average_score = await ScoreRecord.all().aggregate(avg_score=models.Avg('score'))
    average_score = average_score['avg_score'] or 0
    
    # 获取各难度级别的游戏次数
    difficulty_stats = await ScoreRecord.all().values('difficulty').annotate(count=models.Count('id'))
    
    # 生成统计报告
    stats = {
        'total_users': total_users,
        'total_games': total_games,
        'highest_score': highest_score_data,
        'average_score': average_score,
        'difficulty_stats': difficulty_stats,
        'generated_at': datetime.now()
    }
    
    # 这里可以将统计数据保存到数据库或文件中
    # 示例：保存到文件
    if settings.STORAGE_TYPE == 'local':
        stats_file_path = os.path.join(settings.LOCAL_STORAGE_PATH, 'game_stats.json')
        import json
        with open(stats_file_path, 'w') as f:
            json.dump(stats, f, default=str)
    
    return stats


@shared_task
async def send_notification(user_id: int, message: str) -> bool:
    """发送通知"""
    # 这里可以集成各种通知服务，例如：
    # 1. 电子邮件通知
    # 2. 短信通知
    # 3. 推送通知
    # 4. 其他通知方式
    
    # 示例：打印通知（实际应用中应该替换为真实的通知逻辑）
    print(f"向用户 {user_id} 发送通知: {message}")
    
    return True
