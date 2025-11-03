from celery import Celery
from backend.app.core.config import settings


# 创建Celery实例
celery_app = Celery(
    "play_plane_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend.app.tasks"]
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    # 任务结果过期时间
    result_expires=3600,
    # 并发设置
    worker_concurrency=8,
    # 任务预取设置
    worker_prefetch_multiplier=1,
)

# 设置任务路由
celery_app.conf.task_routes = {
    "backend.app.tasks.*": {
        "queue": "play_plane_queue"
    },
}

# 配置定时任务
if settings.DEBUG:
    # 开发环境下不启用定时任务
    celery_app.conf.beat_schedule = {}
else:
    celery_app.conf.beat_schedule = {
        # 每天凌晨1点清理过期文件
        "clean-expired-files": {
            "task": "backend.app.tasks.clean_expired_files",
            "schedule": crontab(hour=1, minute=0),
        },
        # 每天凌晨2点生成游戏统计数据
        "generate-game-stats": {
            "task": "backend.app.tasks.generate_game_stats",
            "schedule": crontab(hour=2, minute=0),
        },
    }


if __name__ == "__main__":
    celery_app.start()
