"""数据导入导出与数据库备份。"""

import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel import Session, select

from app.config import DB_PATH
from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import AuditLog, AutoPart, Client, InventoryTransaction, QuotationRecord
from app.services.audit import log_action

router = APIRouter(tags=["导入导出"])


def _csv_response(rows, header, filename: str) -> StreamingResponse:
    """把二维行数据渲染成带 BOM 无关的 UTF-8 CSV 下载响应。"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/api/export/transactions")
def export_transactions_excel(session: Session = Depends(get_session)):
    txs = session.exec(select(InventoryTransaction)).all()
    return _csv_response(
        ([t.id, t.timestamp, t.part_oem, t.part_name, t.type, t.quantity,
          t.unit_price, t.total_amount, t.customer_or_supplier] for t in txs),
        ["单据编号", "时间", "OEM编号", "配件名称", "操作类型", "数量", "单价(USD)", "总金额(USD)", "客户/供应商"],
        "Tostiyk_Transactions.csv",
    )


@router.get("/api/export/quotations")
def export_quotations_excel(session: Session = Depends(get_session)):
    quotes = session.exec(select(QuotationRecord)).all()
    return _csv_response(
        ([q.quotation_no, q.timestamp, q.client_name, q.total_usd, q.total_bs, q.bcv_rate] for q in quotes),
        ["报价单号", "生成时间", "客户名称", "总价(USD)", "总价(Bs.)", "当时BCV汇率"],
        "Tostiyk_Quotations.csv",
    )


@router.get("/api/export/audit-logs")
def export_audit_logs(
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="EXPORT_AUDIT_LOGS",
        details="导出了系统安全操作审计日志报表 (CSV)",
    )
    logs = session.exec(select(AuditLog).order_by(AuditLog.id.desc())).all()
    return _csv_response(
        ([l.id, l.username, l.role, l.action, l.details, l.created_at] for l in logs),
        ["ID", "Username", "Role", "Action", "Details", "Timestamp"],
        "tostiyk_audit_logs.csv",
    )


@router.get("/api/export/parts")
def export_parts_csv(session: Session = Depends(get_session)):
    parts = session.exec(select(AutoPart)).all()
    return _csv_response(
        ([p.oem, p.name, p.brand, p.category, p.stock, p.price, p.bin_location] for p in parts),
        ["oem", "name", "brand", "category", "stock", "price", "bin_location"],
        "Tostiyk_Parts_Catalog.csv",
    )


@router.get("/api/export/clients")
def export_clients_csv(session: Session = Depends(get_session)):
    clients = session.exec(select(Client)).all()
    return _csv_response(
        ([c.name, c.phone, c.address, c.rif_or_cedula, c.client_type, c.debt, c.notes] for c in clients),
        ["Name", "Phone", "Address", "RIF/Cedula", "Type", "Debt(USD)", "Notes"],
        "Tostiyk_Clients_Directory.csv",
    )


@router.post("/api/import/parts")
async def import_parts_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    contents = await file.read()
    decoded = contents.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))
    count = 0
    for row in reader:
        oem = row.get("oem") or row.get("OEM")
        name = row.get("name") or row.get("配件名称")
        if not oem or not name:
            continue

        try:
            stock_val = int(row.get("stock", 0))
        except (ValueError, TypeError):
            stock_val = 0

        try:
            price_val = float(row.get("price", 0.0))
        except (ValueError, TypeError):
            price_val = 0.0

        existing = session.exec(select(AutoPart).where(AutoPart.oem == oem)).first()
        if existing:
            existing.name = name
            existing.brand = row.get("brand", existing.brand)
            existing.category = row.get("category", existing.category)
            existing.stock = stock_val
            existing.price = price_val
            existing.bin_location = row.get("bin_location", existing.bin_location)
            session.add(existing)
        else:
            session.add(AutoPart(
                oem=oem,
                name=name,
                brand=row.get("brand", "GENERAL"),
                category=row.get("category", "未分类"),
                stock=stock_val,
                price=price_val,
                bin_location=row.get("bin_location", "Estante A-1"),
            ))
        count += 1
    session.commit()
    return {"status": "success", "imported_count": count}


@router.get("/api/backup/download")
def download_database_backup():
    if DB_PATH.exists():
        return FileResponse(str(DB_PATH), media_type="application/x-sqlite3", filename="tostiyk_backup.db")
    raise HTTPException(status_code=404, detail="数据库文件不存在")
