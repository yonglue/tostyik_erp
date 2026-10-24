import os
import sys
import json
from pathlib import Path

# 🌟 核心修复：将项目根目录加入 sys.path，防止 ModuleNotFoundError
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlmodel import Session, select
from app.database import engine
from app.models import AutoPart

UPLOAD_DIR = BASE_DIR / "uploads"

def get_used_images():
    """扫描数据库，找出所有被引用的图片文件名（只比对纯文件名）"""
    used = set()
    with Session(engine) as session:
        parts = session.exec(select(AutoPart)).all()
        for p in parts:
            if p.image_url:
                try:
                    # image_url 可能是 JSON 数组字符串，也可能是单个文件名
                    imgs = json.loads(p.image_url)
                    if isinstance(imgs, list):
                        for img in imgs:
                            used.add(os.path.basename(img))  # 🌟 只取文件名
                    else:
                        used.add(os.path.basename(p.image_url))
                except Exception:
                    used.add(os.path.basename(p.image_url))
    return used
def audit():
    print("🔍 正在扫描数据库关联与上传目录...")
    if not UPLOAD_DIR.exists():
        print("❌ uploads 目录不存在")
        return

    used_files = get_used_images()
    
    # 获取所有上传的文件名（包含 pdf 和 jpg）
    disk_files = set(os.listdir(UPLOAD_DIR))
    
    # 筛选出：在硬盘上，但数据库里没用的文件
    orphans = disk_files - used_files
    
    # 排除 PDF，只审计图片（因为 PDF 是报价单，跟商品关联的逻辑不一样）
    orphan_images = [f for f in orphans if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    used_images = [f for f in disk_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and f not in orphans]
    
    print(f"\n📊 审计报告：")
    print(f"✅ 正常使用的商品图片: {len(used_images)} 张")
    print(f"⚠️ 疑似孤儿图片 (可安全删除): {len(orphan_images)} 张")
    print(f"📄 报价单 PDF (未参与审计): {len([f for f in disk_files if f.lower().endswith('.pdf')])} 份")
    
    if orphan_images:
        print("\n🗑️ 以下图片未被任何商品引用（按大小排序）：")
        orphan_images.sort(key=lambda x: os.path.getsize(UPLOAD_DIR / x), reverse=True)
        for f in orphan_images[:10]:
            size_kb = os.path.getsize(UPLOAD_DIR / f) / 1024
            print(f"  - {f} ({size_kb:.1f} KB)")
        if len(orphan_images) > 10:
            print(f"  ... 等共 {len(orphan_images)} 张")
        print("\n💡 确认无误后，你可以手动删除这些文件，或者以后我们写个参数加上 --fix 让脚本自动删。")

if __name__ == "__main__":
    audit()




    