import os
import aiofiles
import magic
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
from backend.app.core.config import settings


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    async def save_file(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        """保存文件"""
        pass
    
    @abstractmethod
    async def read_file(self, file_path: str) -> bytes:
        """读取文件"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        pass


class LocalStorageBackend(StorageBackend):
    """本地文件系统存储后端"""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or settings.LOCAL_STORAGE_PATH
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        # 生成唯一的文件路径
        file_path = self.storage_path / filename
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return str(file_path.relative_to(self.storage_path))
    
    async def read_file(self, file_path: str) -> bytes:
        full_path = self.storage_path / file_path
        
        if not full_path.exists() or not full_path.is_file():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()
    
    async def delete_file(self, file_path: str) -> bool:
        full_path = self.storage_path / file_path
        
        if not full_path.exists() or not full_path.is_file():
            return False
        
        try:
            os.remove(full_path)
            return True
        except Exception:
            return False
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        full_path = self.storage_path / file_path
        
        if not full_path.exists() or not full_path.is_file():
            return None
        
        # 获取文件大小
        file_size = full_path.stat().st_size
        
        # 获取文件类型
        try:
            file_type = magic.from_file(str(full_path), mime=True)
        except Exception:
            file_type = 'application/octet-stream'
        
        return {
            'file_path': str(full_path.relative_to(self.storage_path)),
            'filename': full_path.name,
            'file_size': file_size,
            'content_type': file_type,
            'storage_type': 'local'
        }


class S3StorageBackend(StorageBackend):
    """AWS S3存储后端"""
    
    def __init__(self):
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError("请安装boto3库以使用S3存储后端")
            
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
    
    async def save_file(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_content,
                ContentType=content_type or 'application/octet-stream'
            )
            return filename
        except ClientError as e:
            raise Exception(f"保存文件到S3失败: {e}")
    
    async def read_file(self, file_path: str) -> bytes:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"文件不存在: {file_path}")
            raise Exception(f"读取S3文件失败: {e}")
    
    async def delete_file(self, file_path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return False
            raise Exception(f"删除S3文件失败: {e}")
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'file_size': response['ContentLength'],
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'storage_type': 's3'
            }
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise Exception(f"获取S3文件信息失败: {e}")


class OSSStorageBackend(StorageBackend):
    """阿里云OSS存储后端"""
    
    def __init__(self):
        try:
            import oss2
        except ImportError:
            raise ImportError("请安装oss2库以使用阿里云OSS存储后端")
            
        auth = oss2.Auth(settings.ALIYUN_OSS_ACCESS_KEY_ID, settings.ALIYUN_OSS_ACCESS_KEY_SECRET)
        self.bucket = oss2.Bucket(auth, settings.ALIYUN_OSS_ENDPOINT, settings.ALIYUN_OSS_BUCKET_NAME)
    
    async def save_file(self, file_content: bytes, filename: str, content_type: str = None) -> str:
        try:
            self.bucket.put_object(
                key=filename,
                data=file_content,
                content_type=content_type or 'application/octet-stream'
            )
            return filename
        except oss2.exceptions.OssError as e:
            raise Exception(f"保存文件到OSS失败: {e}")
    
    async def read_file(self, file_path: str) -> bytes:
        try:
            result = self.bucket.get_object(file_path)
            return result.read()
        except oss2.exceptions.NoSuchKey:
            raise FileNotFoundError(f"文件不存在: {file_path}")
        except oss2.exceptions.OssError as e:
            raise Exception(f"读取OSS文件失败: {e}")
    
    async def delete_file(self, file_path: str) -> bool:
        try:
            self.bucket.delete_object(file_path)
            return True
        except oss2.exceptions.NoSuchKey:
            return False
        except oss2.exceptions.OssError as e:
            raise Exception(f"删除OSS文件失败: {e}")
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.bucket.head_object(file_path)
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'file_size': int(result.headers['Content-Length']),
                'content_type': result.headers.get('Content-Type', 'application/octet-stream'),
                'storage_type': 'oss'
            }
        except oss2.exceptions.NoSuchKey:
            return None
        except oss2.exceptions.OssError as e:
            raise Exception(f"获取OSS文件信息失败: {e}")


def get_storage_backend() -> StorageBackend:
    """获取存储后端实例"""
    storage_type = settings.STORAGE_TYPE.lower()
    
    if storage_type == 'local':
        return LocalStorageBackend()
    elif storage_type == 's3':
        return S3StorageBackend()
    elif storage_type == 'oss':
        return OSSStorageBackend()
    else:
        raise ValueError(f"不支持的存储类型: {storage_type}")
