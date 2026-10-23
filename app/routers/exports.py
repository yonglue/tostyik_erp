"""数据导入导出与数据库备份。"""

import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

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

    # 🌟 如果解析出来连一行数据都没有，直接抛错
    if not rows:
        raise HTTPException(status_code=400, detail="未读取到任何数据，请确保文件有内容并已保存")

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
        ([p.oem, p.name, p.brand, p.category, p.stock, p.price, p.cost_price, p.bin_location, p.cross_references] for p in parts),
        ["oem", "name", "brand", "category", "stock", "price", "cost_price", "bin_location", "cross_references"],
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
    filename = file.filename.lower()
    
    imported_count = 0
    skipped_count = 0
    errors = []
    rows = []

    # 1. 智能解析文件
    try:
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            wb = load_workbook(io.BytesIO(contents), data_only=True)
            ws = wb.active
            
            headers = [str(cell.value).strip() if cell.value else "" for cell in ws[1]]
            
            if not any(h in headers for h in ["OEM编号", "oem", "OEM"]):
                raise HTTPException(status_code=400, detail="Excel 表头错误：找不到 'OEM编号' 列。请下载标准模板！")

            for row in ws.iter_rows(min_row=2, values_only=True):
                if not any(row): continue
                rows.append(dict(zip(headers, row)))
        else:
            decoded = contents.decode("utf-8-sig", errors="ignore")
            reader = csv.DictReader(io.StringIO(decoded))
            fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
            
            if not any(h in fieldnames for h in ["OEM编号", "oem", "OEM"]):
                raise HTTPException(status_code=400, detail="CSV 表头错误：找不到 'OEM编号' 列。请下载标准模板！")
                
            for r in reader:
                if any(r.values()): rows.append(r)
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    if len(rows) == 0:
        raise HTTPException(status_code=400, detail="文件内没有找到任何数据行，请检查文件是否已保存，或是否填在了第一个Sheet中。")

    # 2. 逐行处理
    for idx, row in enumerate(rows, start=2):
        oem = str(row.get("oem") or row.get("OEM") or row.get("OEM编号") or "").strip()
        name = str(row.get("name") or row.get("配件名称") or row.get("Name") or "").strip()

        if not oem or not name:
            skipped_count += 1
            if len(errors) < 5:
                errors.append(f"第 {idx} 行: 缺少 OEM编号 或 配件名称")
            continue

        def safe_float(val):
            try: return float(val or 0.0)
            except: return 0.0
        def safe_int(val):
            try: return int(val or 0)
            except: return 0

        stock_val = safe_int(row.get("stock") or row.get("库存数量"))
        price_val = safe_float(row.get("price") or row.get("销售价(USD)"))
        cost_price_val = safe_float(row.get("cost_price") or row.get("进货价(USD)"))
        
        brand = str(row.get("brand") or row.get("品牌") or "GENERAL").strip() or "GENERAL"
        category = str(row.get("category") or row.get("分类") or "未分类").strip()
        bin_loc = str(row.get("bin_location") or row.get("货架位") or "Estante A-1").strip()
        cross_refs = str(row.get("cross_references") or row.get("交叉参考号") or "").strip()

        existing = session.exec(select(AutoPart).where(AutoPart.oem == oem, AutoPart.brand == brand)).first()
        if existing:
            existing.name = name
            existing.category = category
            existing.stock = stock_val
            existing.price = price_val
            existing.cost_price = cost_price_val
            existing.bin_location = bin_loc
            existing.cross_references = cross_refs
            session.add(existing)
        else:
            session.add(AutoPart(
                oem=oem, name=name, brand=brand, category=category, 
                stock=stock_val, price=price_val, cost_price=cost_price_val,
                bin_location=bin_loc, cross_references=cross_refs
            ))
        imported_count += 1

    # 3. 提交数据库
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="文件中存在重复的 (OEM编号, 品牌) 组合，请先去重")

    return {
        "status": "success",
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "errors": errors
    }


@router.get("/api/backup/download")
def download_database_backup():
    if DB_PATH.exists():
        return FileResponse(str(DB_PATH), media_type="application/x-sqlite3", filename="tostiyk_backup.db")
    raise HTTPException(status_code=404, detail="数据库文件不存在")


@router.get("/api/export/template/parts")
def export_parts_template():
    """下载商品导入的 Excel 模板 (带下拉框，统一中英文)"""
    wb = Workbook()
    ws = wb.active
    ws.title = "商品导入模板"

    # 补齐了进货价和交叉参考号
    headers = ["OEM编号", "配件名称", "品牌", "分类", "库存数量", "销售价(USD)", "进货价(USD)", "货架位", "交叉参考号"]
    ws.append(headers)

    # 美化表头
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    center_alignment = Alignment(horizontal="center", vertical="center")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_alignment

    # 设置列宽
    column_widths = [20, 30, 15, 15, 10, 15, 15, 15, 25]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = width

    # 示例数据
    ws.append(["17801-74060", "空气滤清器", "Toyota", "滤清器", 10, 15.50, 10.00, "A-1-2", "WIX: 51348"])

    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Parts_Import_Template.xlsx"}
    )