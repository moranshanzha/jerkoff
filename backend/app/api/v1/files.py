from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from backend.app.crud import create_file_record, get_file, get_user_files, delete_file
from backend.app.schemas import FileResponse, FileUploadResponse, FileInDB
from backend.app.api.v1.auth import get_current_active_user
from backend.app.core.storage import get_storage_backend
from backend.app.utils import verify_file_upload, generate_unique_filename, scan_file_for_viruses
from typing import Optional, List
import os


router = APIRouter()


# 文件上传
@router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user)
):
    """文件上传"""
    # 验证文件上传
    try:
        verify_file_upload(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 读取文件内容
    file_content = await file.read()
    
    # 生成唯一文件名
    filename = generate_unique_filename(file.filename)
    
    # 获取存储后端
    storage = get_storage_backend()
    
    # 保存文件到存储后端
    try:
        file_path = await storage.save_file(file_content, filename, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 扫描文件是否包含病毒
    if not settings.DEBUG:
        # 创建临时文件进行病毒扫描
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            is_safe = await scan_file_for_viruses(tmp_file_path)
            if not is_safe:
                # 删除不安全的文件
                await storage.delete_file(file_path)
                os.unlink(tmp_file_path)
                raise HTTPException(status_code=400, detail="文件包含病毒，上传失败")
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    # 创建文件记录
    file_record = await create_file_record(
        user_id=current_user.id,
        filename=filename,
        file_path=file_path,
        file_size=file.size,
        content_type=file.content_type,
        storage_type=settings.STORAGE_TYPE
    )
    
    return FileUploadResponse(data={
        "file_id": file_record.id,
        "filename": file_record.filename,
        "file_size": file_record.file_size,
        "content_type": file_record.content_type,
        "download_url": f"/api/v1/files/download/{file_record.id}"
    })


# 文件下载
@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    current_user = Depends(get_current_active_user)
):
    """文件下载"""
    # 获取文件记录
    file_record = await get_file(file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查权限
    if not current_user.is_admin and file_record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限下载该文件")
    
    # 获取存储后端
    storage = get_storage_backend()
    
    # 读取文件内容
    try:
        file_content = await storage.read_file(file_record.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件读取失败: {str(e)}")
    
    # 返回文件响应
    return Response(
        content=file_content,
        media_type=file_record.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={file_record.filename}",
            "Content-Length": str(file_record.file_size)
        }
    )


# 获取文件信息
@router.get("/{file_id}", response_model=FileResponse)
async def get_file_info(
    file_id: int,
    current_user = Depends(get_current_active_user)
):
    """获取文件信息"""
    # 获取文件记录
    file_record = await get_file(file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查权限
    if not current_user.is_admin and file_record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限查看该文件信息")
    
    return FileResponse(data=file_record)


# 获取当前用户的文件列表
@router.get("/me", response_model=List[FileInDB])
async def get_current_user_files(
    skip: int = 0,
    limit: int = 10,
    current_user = Depends(get_current_active_user)
):
    """获取当前用户的文件列表"""
    files = await get_user_files(current_user.id, skip=skip, limit=limit)
    return files


# 删除文件
@router.delete("/{file_id}", response_model=dict)
async def delete_file(
    file_id: int,
    current_user = Depends(get_current_active_user)
):
    """删除文件"""
    # 获取文件记录
    file_record = await get_file(file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 检查权限
    if not current_user.is_admin and file_record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限删除该文件")
    
    # 获取存储后端
    storage = get_storage_backend()
    
    # 删除文件
    try:
        await storage.delete_file(file_record.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")
    
    # 删除文件记录
    success = await delete_file(file_id)
    if not success:
        raise HTTPException(status_code=500, detail="文件记录删除失败")
    
    return {"message": "文件已删除"}
