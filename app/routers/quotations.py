"""报价单 PDF 生成（ReportLab）。

从 main.py 的 `/api/quotations/generate` 中抽离，原文逻辑与排版逐行保留，
仅把 `payload` 依赖改为显式入参。
"""

"""报价单：列表 / 删除 / 生成（含开单出库 + PDF）/ 下载最新 PDF。"""

"""报价单：列表 / 删除 / 生成（含开单出库 + PDF）/ 下载最新 PDF。"""

import json
import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select, update

from app.config import PUBLIC_BASE_URL, UPLOAD_DIR
from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import AutoPart, Client, InventoryTransaction, QuotationRecord
from app.schemas import CreateQuotationRequest
from app.services.audit import log_action
from app.services.bcv import get_official_rate
from app.services.numbering import make_quotation_no
from app.services.quotation_pdf import build_quotation_pdf, normalize_lang

# 🌟 必须显式声明 router，否则主应用引入时会报 AttributeError
router = APIRouter(tags=["报价单"])


@router.get("/api/quotations", response_model=List[QuotationRecord])
def get_quotations(session: Session = Depends(get_session)):
    return session.exec(select(QuotationRecord).order_by(QuotationRecord.id.desc())).all()


@router.delete("/api/quotations/{quotation_id}")
def delete_quotation(quotation_id: int, session: Session = Depends(get_session)):
    record = session.get(QuotationRecord, quotation_id)
    if not record:
        raise HTTPException(status_code=404, detail="报价单记录不存在")
    session.delete(record)
    session.commit()
    return {"status": "success"}


@router.post("/api/quotations/generate")
def generate_and_save_quotation(
    payload: CreateQuotationRequest,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    bcv_rate = get_official_rate()

    total_usd = sum(item.price * item.quantity for item in payload.items)
    total_bs = total_usd * bcv_rate
    quotation_no = make_quotation_no()
    items_snapshot = [item.model_dump() for item in payload.items]

    client_name = payload.client_name.strip() if payload.client_name else "Cliente General"
    client_obj = session.exec(select(Client).where(Client.name == client_name)).first()

    if not client_obj and client_name != "Cliente General":
        client_obj = Client(name=client_name, client_type="Regular", debt=0.0)
        session.add(client_obj)
        session.flush()

    stock_logs: list[tuple[str, str, int, int]] = []

    for item in payload.items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"❌ 非法操作：商品 {item.oem} 的购买数量必须大于 0！",
            )

        part = session.exec(select(AutoPart).where(AutoPart.oem == item.oem)).first()
        if not part:
            raise HTTPException(status_code=404, detail=f"商品 {item.oem} 不存在或已被删除！")

        old_stock = part.stock
        new_stock = old_stock - item.quantity

        result = session.exec(
            update(AutoPart)
            .where(AutoPart.oem == item.oem, AutoPart.stock >= item.quantity)
            .values(stock=AutoPart.stock - item.quantity)
        )
        if result.rowcount == 0:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"商品 {part.name} 库存不足，无法成交出库！")

        stock_logs.append((part.name, item.oem, old_stock, new_stock))

        tx = InventoryTransaction(
            part_oem=item.oem,
            part_name=item.name,
            type="OUT",
            quantity=item.quantity,
            unit_price=item.price,
            total_amount=item.quantity * item.price,
            customer_or_supplier=client_name,
        )
        session.add(tx)

    pay_method = str(payload.payment_method).lower()
    is_fiado = any(keyword in pay_method for keyword in ["fiado", "debt", "赊账", "挂账", "credit"])

    if client_obj and (is_fiado or payload.payment_method in ["Fiado_Debt", "Fiado", "赊账", "挂账", "Debt"]):
        projected_debt = client_obj.debt + total_usd
        if projected_debt > client_obj.credit_limit:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=(
                    f"⚠️ 信用额度超限警报！该客户当前欠款 ${client_obj.debt:.2f}，"
                    f"本次挂账 ${total_usd:.2f}，总计 ${projected_debt:.2f} 已超出设定的信用额度上限 "
                    f"(${client_obj.credit_limit:.2f})，拒绝挂账！"
                ),
            )
        claimed = session.exec(
            update(Client)
            .where(
                Client.id == client_obj.id,
                Client.debt + total_usd <= Client.credit_limit,
            )
            .values(debt=Client.debt + total_usd)
        )
        if claimed.rowcount == 0:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=(
                    f"⚠️ 信用额度超限警报！该客户当前欠款 ${client_obj.debt:.2f}，"
                    f"本次挂账 ${total_usd:.2f} 会超出信用额度上限 "
                    f"(${client_obj.credit_limit:.2f})，拒绝挂账！"
                ),
            )

    lang = normalize_lang(getattr(payload, "lang", "es"))

    record = QuotationRecord(
        quotation_no=quotation_no,
        client_name=client_name,
        total_usd=total_usd,
        total_bs=total_bs,
        bcv_rate=bcv_rate,
        lang=lang,
        items_json=json.dumps(items_snapshot, ensure_ascii=False),
    )
    session.add(record)
    session.commit()

    for part_name, item_oem, old_stock, new_stock in stock_logs:
        log_action(
            session=session,
            username=actor.username,
            role=actor.role,
            action="UPDATE_STOCK",
            details=f"开单销售出库: {part_name} (OEM: {item_oem}), 原库存: {old_stock} -> 新库存: {new_stock}",
        )

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_QUOTATION",
        details=(
            f"完成开单/挂账成交, 单号: {quotation_no}, 客户: {client_name}, "
            f"总价: ${total_usd:.2f} (Bs. {total_bs:.2f}), 方式: {payload.payment_method}"
        ),
    )

    pdf_path = os.path.join(UPLOAD_DIR, f"quotation_{quotation_no}.pdf")
    
    build_quotation_pdf(
        pdf_path=pdf_path,
        quotation_no=quotation_no,
        client_name=client_name,
        client_obj=client_obj,
        items=payload.items,
        total_usd=total_usd,
        total_bs=total_bs,
        lang=lang,
    )

    return {
        "status": "success",
        "quotation_no": quotation_no,
        "pdf_url": f"{PUBLIC_BASE_URL}/api/quotation/pdf/download?t={int(datetime.now().timestamp())}",
    }


@router.get("/api/quotation/pdf/download")
def download_existing_pdf(quotation_no: str = None, session: Session = Depends(get_session)):
    """支持按单号下载对应语言的 PDF，每次都根据最新系统设置实时重新生成以确保抬头同步。"""
    if quotation_no:
        record = session.exec(select(QuotationRecord).where(QuotationRecord.quotation_no == quotation_no)).first()
        if record:
            pdf_path = os.path.join(UPLOAD_DIR, f"quotation_{quotation_no}.pdf")
            import json
            items_data = json.loads(record.items_json)
            from app.schemas import QuotationItemPayload
            items = [QuotationItemPayload(**i) for i in items_data]
            client_obj = session.exec(select(Client).where(Client.name == record.client_name)).first()
            
            # 🌟 每次下载都实时重生成，确保最新的公司名称和 RIF 立即生效
            build_quotation_pdf(
                pdf_path=pdf_path,
                quotation_no=record.quotation_no,
                client_name=record.client_name,
                client_obj=client_obj,
                items=items,
                total_usd=record.total_usd,
                total_bs=record.total_bs,
                lang=normalize_lang(record.lang),
            )
            if os.path.exists(pdf_path):
                return FileResponse(pdf_path, media_type="application/pdf", filename=f"Quotation_{quotation_no}.pdf")

    # 降级逻辑：返回最新的 PDF
    files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith("quotation_") and f.endswith(".pdf")]
    if files:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)), reverse=True)
        latest_pdf = os.path.join(UPLOAD_DIR, files[0])
        return FileResponse(latest_pdf, media_type="application/pdf", filename="Tostiyk_Quotation.pdf")

    raise HTTPException(status_code=404, detail="PDF 文件不存在")

    