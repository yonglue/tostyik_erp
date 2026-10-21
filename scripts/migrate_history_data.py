"""历史订单与成本数据回填脚本

作用：
1. 回填历史订单的净营收（base_amount_usd = 总额 - 税额 - IGTF）。
2. 回填历史订单行的成本快照（cost_price_usd），取当前商品的 cost_price。
3. 校验数据是否对齐，确保平滑迁移。
"""

import sys
from pathlib import Path

# 将项目根目录加入 path，以便导入 app 模块
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from decimal import Decimal
from sqlmodel import Session, select
from app.database import engine
from app.models import Order, OrderItem, AutoPart


def migrate_data():
    print("🚀 开始执行历史数据回填...")
    
    with Session(engine) as session:
        # 1. 回填历史订单的 base_amount_usd
        orders = session.exec(select(Order).where(Order.base_amount_usd == 0)).all()
        updated_orders_count = 0
        
        for order in orders:
            total = Decimal(str(order.total_usd or 0))
            tax = Decimal(str(order.tax_amount_usd or 0))
            igtf = Decimal(str(order.igtf_amount_usd or 0))
            
            # 计算净额 = 总额 - 税 - IGTF
            base = total - tax - igtf
            if base < 0:
                base = Decimal("0.00")
                
            order.base_amount_usd = float(base.quantize(Decimal("0.01")))
            session.add(order)
            updated_orders_count += 1
            
        print(f"📦 已成功回填 {updated_orders_count} 个历史订单的 base_amount_usd。")

        # 2. 回填历史订单行的成本快照 (cost_price_usd)
        items = session.exec(select(OrderItem).where(OrderItem.cost_price_usd == 0)).all()
        updated_items_count = 0
        
        for item in items:
            if item.part_id:
                part = session.get(AutoPart, item.part_id)
                if part and part.cost_price:
                    item.cost_price_usd = float(part.cost_price)
                    session.add(item)
                    updated_items_count += 1
            else:
                # 如果没有关联 part_id，尝试按 oem 匹配
                part = session.exec(select(AutoPart).where(AutoPart.oem == item.oem)).first()
                if part and part.cost_price:
                    item.cost_price_usd = float(part.cost_price)
                    session.add(item)
                    updated_items_count += 1

        print(f"🏷️ 已成功回填 {updated_items_count} 个历史订单行的成本快照 (cost_price_usd)。")

        session.commit()
        print("✅ 数据库历史数据回填提交成功！")

        # 3. 校验一致性
        print("\n🔍 正在进行数据对齐校验...")
        mismatch_count = session.exec(
            select(Order).where(
                (Order.total_usd - (Order.base_amount_usd + Order.tax_amount_usd + Order.igtf_amount_usd)) > 0.05
            )
        ).all()
        
        if mismatch_count:
            print(f"⚠️ 警告: 发现 {len(mismatch_count)} 个订单的总额与分项计算存在轻微差额（可能由历史舍入引起）。")
        else:
            print("✨ 校验通过：所有订单的金额分项完美对齐！")


if __name__ == "__main__":
    migrate_data()