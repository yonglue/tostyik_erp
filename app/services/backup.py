import os
import sqlite3
import asyncio
from datetime import datetime
from app.database import engine

# 设定备份文件夹（存放在项目根目录的 backups 下）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def perform_backup():
    """执行备份的核心函数，使用 SQLite 内置 API 避免文件占用"""
    # 从 SQLAlchemy 的 engine 获取真实的数据库路径
    db_url = str(engine.url)
    if not db_url.startswith("sqlite:///"):
        print(f"❌ 不支持的数据库类型: {db_url}")
        return False
        
    # 提取绝对路径
    db_path = db_url.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        db_path = os.path.join(BASE_DIR, db_path)

    if not os.path.exists(db_path):
        print(f"❌ 备份失败：找不到数据库文件 {db_path}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.db"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        # 使用 SQLite 原生的 backup 方法，完美避开文件被锁定的问题
        source_conn = sqlite3.connect(db_path)
        target_conn = sqlite3.connect(backup_filepath)
        with target_conn:
            source_conn.backup(target_conn)
        source_conn.close()
        target_conn.close()
        
        # 清理旧备份：只保留最近 30 天的
        backups = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
        backups.sort(key=os.path.getmtime)
        if len(backups) > 30:
            for old_file in backups[:-30]:
                os.remove(old_file)
        print(f"✅ 备份成功: {backup_filename}")
        return True
    except Exception as e:
        print(f"❌ 备份失败异常: {e}")
        return False

async def auto_backup_task():
    """后台常驻协程，每天自动备份"""
    await asyncio.sleep(10)
    perform_backup()
    
    while True:
        # 每隔 24 小时执行一次
        await asyncio.sleep(86400)
        perform_backup()