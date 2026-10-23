#!/usr/bin/env python
"""扫描 supplier.debt_usd 与真值的偏差，可选修复。

真值 = sum(received PO 的 items_json 重算) - sum(付款 amount_usd)
默认 dry-run；--fix 前自动备份，--yes 跳过交互确认。
"""
import argparse
import json
import shutil
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from sqlmodel import Session, select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DB_PATH
from app.database import engine
from app.models import Supplier, PurchaseOrder, SupplierPaymentRecord

THRESHOLD = Decimal("0.005")
CENT = Decimal("0.01")


def _to_decimal(v) -> Decimal:
    if v is None:
        return Decimal("0")
    return Decimal(str(v))


def recompute_po_total(po: PurchaseOrder) -> Decimal:
    try:
        items = json.loads(po.items_json or "[]")
    except json.JSONDecodeError:
        print(f"  ⚠️  PO {po.po_no} items_json 解析失败，按 0 处理", file=sys.stderr)
        return Decimal("0")
    total = Decimal("0")
    for item in items:
        qty = _to_decimal(item.get("quantity"))
        price = _to_decimal(item.get("unit_price"))
        total += (qty * price).quantize(CENT, rounding=ROUND_HALF_UP)
    return total


def compute_true_debt(session: Session, supplier_id: int) -> Decimal:
    pos = session.exec(
        select(PurchaseOrder).where(
            PurchaseOrder.supplier_id == supplier_id,
            PurchaseOrder.status == "received",
        )
    ).all()
    po_total = sum((recompute_po_total(po) for po in pos), Decimal("0"))

    pays = session.exec(
        select(SupplierPaymentRecord).where(
            SupplierPaymentRecord.supplier_id == supplier_id
        )
    ).all()
    pay_total = sum((_to_decimal(p.amount_usd) for p in pays), Decimal("0"))

    return (po_total - pay_total).quantize(CENT, rounding=ROUND_HALF_UP)


def report_orphans(session: Session) -> None:
    orphan_pays = session.exec(
        select(SupplierPaymentRecord).where(
            ~SupplierPaymentRecord.supplier_id.in_(select(Supplier.id))
        )
    ).all()
    if orphan_pays:
        print(f"\n⚠️  孤儿付款记录（supplier_id 找不到）: {len(orphan_pays)} 条")
        for p in orphan_pays:
            print(f"   id={p.id} supplier_id={p.supplier_id} amount={p.amount_usd}")
    else:
        print("\n✅ 无孤儿付款记录")


def main() -> int:
    ap = argparse.ArgumentParser(description="审计供应商欠款")
    ap.add_argument("--fix", action="store_true", help="实际修改 debt_usd（默认只报告）")
    ap.add_argument("--yes", action="store_true", help="跳过 --fix 的交互确认")
    args = ap.parse_args()

    with Session(engine) as session:
        suppliers = session.exec(select(Supplier).order_by(Supplier.id)).all()

        print(f"{'ID':>4}  {'Name':<24}  {'实际':>10}  {'真值':>10}  {'diff':>10}")
        print("-" * 72)

        drifts = []
        for s in suppliers:
            actual = _to_decimal(s.debt_usd).quantize(CENT, rounding=ROUND_HALF_UP)
            true = compute_true_debt(session, s.id)
            diff = actual - true
            mark = ""
            if abs(diff) > THRESHOLD:
                mark = "  ← DRIFT"
                drifts.append((s, actual, true, diff))
            print(f"{s.id:>4}  {s.name:<24}  {actual:>10}  {true:>10}  {diff:>10}{mark}")

        print(f"\n共 {len(suppliers)} 个供应商，{len(drifts)} 个漂移")

        report_orphans(session)

        if not args.fix or not drifts:
            return 0

        if not args.yes:
            ans = input(f"\n确认修复 {len(drifts)} 个供应商？输入 yes 继续: ").strip().lower()
            if ans != "yes":
                print("已取消")
                return 1

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = DB_PATH.parent / f"{DB_PATH.stem}.bak_audit_{ts}{DB_PATH.suffix}"
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ 备份: {backup_path}")

        for s, actual, true, _ in drifts:
            s.debt_usd = float(true)
            session.add(s)
            print(f"   ✅ {s.name} (id={s.id}): {actual} → {true}")
        session.commit()
        print("修复完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())