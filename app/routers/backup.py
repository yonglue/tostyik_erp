from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime
from app.services.backup import perform_backup, BACKUP_DIR

router = APIRouter(tags=["备份"])

@router.post("/api/backup/trigger")
def trigger_manual_backup():
    """手动触发一次备份"""
    success = perform_backup()
    if success:
        return {"status": "success", "message": "手动备份成功"}
    raise HTTPException(status_code=500, detail="备份失败，请检查数据库文件是否存在")

@router.get("/api/backup/list")
def list_backups():
    """获取所有备份文件列表"""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    files = []
    try:
        for f in os.listdir(BACKUP_DIR):
            # 只处理 .db 结尾的文件
            if f.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, f)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        "filename": f,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
    except Exception as e:
        print(f"❌ 读取备份列表异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    # 按时间倒序排列
    return sorted(files, key=lambda x: x['created_at'], reverse=True)

@router.get("/api/backup/download/{filename}")
def download_backup(filename: str):
    """下载指定的备份文件"""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="非法的文件名")
        
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath) or not filename.endswith('.db'):
        raise HTTPException(status_code=404, detail="备份文件不存在")
        
    return FileResponse(filepath, media_type="application/x-sqlite3", filename=filename)