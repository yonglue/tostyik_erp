import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# 假设你的备份都在项目根目录的 backups 文件夹下
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKUP_DIR = BASE_DIR / "backups"

logger = logging.getLogger("housekeeping")

def cleanup_old_backups(retention_days=30):
    """清理过期的数据库备份文件，保留最近 30 天以及每月 1 号的备份"""
    if not BACKUP_DIR.exists():
        return

    now = datetime.now()
    cutoff_date = now - timedelta(days=retention_days)
    
    deleted_count = 0
    
    # 遍历 backups 目录下所有 .db 文件
    for file_path in BACKUP_DIR.glob("*.db"):
        # 只处理自动备份的文件名 (格式通常包含 backup_202xxxxx_xxxxxx)
        if not file_path.name.startswith("backup_"):
            continue
            
        try:
            # 从文件名提取时间，例如 backup_20261022_223030.db
            # 提取出 20261022
            date_str = file_path.name.split("_")[1]
            file_date = datetime.strptime(date_str, "%Y%m%d")
            
            # 1. 如果是 30 天内的，无条件保留
            if file_date > cutoff_date:
                continue
                
            # 2. 如果是每月 1 号的备份，作为月度归档永久保留
            if file_date.day == 1:
                continue
                
            # 3. 其他情况，说明是 30 天前且非 1 号的冗余备份，删除
            file_path.unlink()
            deleted_count += 1
            logger.info(f"[Housekeeping] 已清理过期备份: {file_path.name}")
            
        except Exception as e:
            # 如果文件名不符合规范或解析失败，跳过并记录警告，绝不误删
            logger.warning(f"[Housekeeping] 跳过无法解析的文件: {file_path.name} ({e})")
            
    if deleted_count > 0:
        print(f"🧹 [Housekeeping] 数据库备份清理完成，共删除了 {deleted_count} 个过期文件。")
    else:
        print(f"✨ [Housekeeping] 数据库备份检查完成，无需清理。")