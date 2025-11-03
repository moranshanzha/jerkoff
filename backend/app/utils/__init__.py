import magic
import hashlib
import tempfile
import os
from typing import Optional
from fastapi import UploadFile
from backend.app.core.config import settings


def verify_file_upload(file: UploadFile, max_size: int = None) -> bool:
    """验证文件上传
    
    Args:
        file: 上传的文件对象
        max_size: 最大文件大小（字节），默认使用配置中的MAX_FILE_SIZE
        
    Returns:
        bool: 文件是否合法
    """
    max_size = max_size or settings.MAX_FILE_SIZE
    
    # 检查文件大小
    if file.size > max_size:
        raise ValueError(f"文件大小超过限制，最大允许 {max_size / 1024 / 1024:.2f} MB")
    
    # 检查文件类型
    content_type = file.content_type
    if content_type not in settings.ALLOWED_FILE_TYPES:
        # 尝试使用magic库检测真实文件类型
        try:
            file_bytes = file.file.read(1024)
            file.file.seek(0)  # 重置文件指针
            detected_type = magic.from_buffer(file_bytes, mime=True)
            if detected_type not in settings.ALLOWED_FILE_TYPES:
                raise ValueError(f"不支持的文件类型: {detected_type}")
        except Exception:
            raise ValueError(f"无法检测文件类型或不支持的文件类型: {content_type}")
    
    return True


def generate_file_hash(file_content: bytes, algorithm: str = 'sha256') -> str:
    """生成文件哈希值"""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(file_content)
    return hash_obj.hexdigest()


def generate_unique_filename(filename: str) -> str:
    """生成唯一文件名"""
    # 分离文件名和扩展名
    name, ext = os.path.splitext(filename)
    
    # 生成文件内容的哈希值
    # 注意：这里我们需要读取文件内容来生成哈希，但在函数外部已经读取过文件内容
    # 所以这里简化处理，使用时间戳和随机数生成唯一文件名
    import time
    import random
    timestamp = int(time.time())
    random_num = random.randint(0, 9999)
    
    return f"{name}_{timestamp}_{random_num}{ext}"


async def scan_file_for_viruses(file_path: str) -> bool:
    """扫描文件是否包含病毒
    
    注意：这只是一个示例实现，实际应用中需要集成专业的病毒扫描服务
    例如：ClamAV、Symantec、McAfee等
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否安全（True表示安全，False表示包含病毒）
    """
    # 在实际应用中，这里应该集成真实的病毒扫描服务
    # 这里只是一个模拟实现
    if settings.DEBUG:
        # 开发环境下跳过病毒扫描
        return True
    
    # 示例：检查文件名中是否包含病毒相关关键字
    filename = os.path.basename(file_path)
    virus_keywords = ['virus', 'malware', 'trojan', 'worm', 'spyware']
    for keyword in virus_keywords:
        if keyword in filename.lower():
            return False
    
    # 示例：检查文件内容中是否包含病毒特征码
    try:
        with open(file_path, 'rb') as f:
            content = f.read(1024)
            if b'virus' in content or b'malware' in content:
                return False
    except Exception:
        pass
    
    return True
