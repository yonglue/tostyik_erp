"""报价单：列表 / 删除 / 生成（含开单出库 + PDF）/ 下载最新 PDF。"""

import json
import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from sqlmodel import Session, select, update

from app.config import PUBLIC_BASE_URL, UPLOAD_DIR
from app.database import get_session
from app.deps import Actor, get_current_actor, RequirePermission
from app.models import AutoPart, Client, InventoryTransaction, QuotationRecord
from app.schemas import CreateQuotationRequest
from app.services.audit import log_action
from app.services.bcv import get_official_rate
from app.services.numbering import make_quotation_no
from app.services.quotation_pdf import build_quotation_pdf, normalize_lang

router = APIRouter(tags=["报价单"])


@router.get("/api/quotations", response_model=List[QuotationRecord])
def get_quotations(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    return session.exec(select(QuotationRecord).order_by(QuotationRecord.id.desc())).all()


@router.delete("/api/quotations/{quotation_id}")
def delete_quotation(
    quotation_id: int,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access"))
):
    record = session.get(QuotationRecord, quotation_id)
    if not record:
        raise HTTPException(status_code=404, detail="报价单记录不存在")
    session.delete(record)
    session.commit()
    return {"status": "success"}


@router.post("/api/quotations/generate")
def generate_and_save_quotation(
    payload: CreateQuotationRequest,
    actor: Actor = Depends(RequirePermission("pos:access")),
    session: Session = Depends(get_session),
):
    bcv_rate = get_official_rate()
    
    # 🌟 核心修复：把数量校验提到最前面，防止负数污染后续的金额计算
    for item in payload.items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"❌ 非法操作：商品 {item.oem} 的购买数量必须大于 0！",
            )

    # 使用 Decimal 计算总价，防止精度丢失
    total_usd_dec = Decimal("0.00")
    for item in payload.items:
        line_total = (Decimal(str(item.price)) * item.quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_usd_dec += line_total
    
    total_usd = float(total_usd_dec) 
    total_bs = float((total_usd_dec * Decimal(str(bcv_rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    quotation_no = make_quotation_no()
    items_snapshot = [item.model_dump() for item in payload.items]

    client_name = payload.client_name.strip() if payload.client_name else "Cliente General"
    client_obj = session.exec(select(Client).where(Client.name == client_name)).first()

    if not client_obj and client_name != "Cliente General":
        client_obj = Client(name=client_name, client_type="Regular", debt=0.0)
        session.add(client_obj)
        session.flush()

    pay_method = str(payload.payment_method).lower()
    is_fiado = any(keyword in pay_method for keyword in ["fiado", "debt", "赊账", "挂账", "credit"])

    if client_obj and is_fiado:
        projected_debt = Decimal(str(client_obj.debt)) + total_usd_dec
        
        if projected_debt > Decimal(str(client_obj.credit_limit)):
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
            raise HTTPException(status_code=400, detail="信用额度超限，并发冲突导致挂账失败！")

    lang = normalize_lang(getattr(payload, "lang", "es"))

    record = QuotationRecord(
        quotation_no=quotation_no,
        client_name=client_name,
        total_usd=total_usd,
        total_bs=total_bs,
        bcv_rate=bcv_rate,
        lang=lang,
        items_json=json.dumps(items_snapshot, ensure_ascii=False, default=float),
    )
    session.add(record)
    session.commit()

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
        "pdf_url": f"{PUBLIC_BASE_URL}/api/quotation/pdf/download?quotation_no={quotation_no}",
    }


@router.get("/api/quotation/pdf/download", dependencies=[Depends(RequirePermission("pos:access"))])
def download_existing_pdf(
    request: Request,
    quotation_no: Optional[str] = None, 
    order_no: Optional[str] = None,
    lang: Optional[str] = None, 
    session: Session = Depends(get_session)
):
    """PDF 下载路由：直接响应并生成 PDF。"""
    
    target_no = quotation_no or order_no
    
    if target_no and any(bad_char in target_no for bad_char in ["/", "\\", "..", ":"]):
        raise HTTPException(status_code=400, detail="非法的单号格式")

    if target_no:
        class PdfItemAdapter:
            def __init__(self, oem, name, quantity, price):
                self.oem = oem
                self.name = name
                self.quantity = quantity
                self.price = price
                self.brand = ""

        record = session.exec(select(QuotationRecord).where(QuotationRecord.quotation_no == target_no)).first()
        if record:
            pdf_path = os.path.join(UPLOAD_DIR, f"quotation_{target_no}.pdf")
            items_data = json.loads(record.items_json)
            items = [
                PdfItemAdapter(
                    oem=i.get("oem", ""),
                    name=i.get("name", ""),
                    quantity=i.get("quantity", 1),
                    price=i.get("price", 0.0)
                ) for i in items_data
            ]
            client_obj = session.exec(select(Client).where(Client.name == record.client_name)).first()
            
            build_quotation_pdf(
                pdf_path=pdf_path,
                quotation_no=record.quotation_no,
                client_name=record.client_name,
                client_obj=client_obj,
                items=items,
                total_usd=record.total_usd,
                total_bs=record.total_bs,
                lang=normalize_lang(lang or record.lang),
            )
            if os.path.exists(pdf_path):
                return FileResponse(pdf_path, media_type="application/pdf", filename=f"Quotation_{target_no}.pdf")

        from app.models import Order
        order = session.exec(select(Order).where(Order.order_no == target_no)).first()
        if order:
            pdf_path = os.path.join(UPLOAD_DIR, f"quotation_{target_no}.pdf")
            items = [
                PdfItemAdapter(
                    oem=i.oem,
                    name=i.name,
                    quantity=i.quantity,
                    price=i.price_usd
                ) for i in order.items
            ]
            client_obj = session.exec(select(Client).where(Client.name == order.client_name)).first()
            
            build_quotation_pdf(
                pdf_path=pdf_path,
                quotation_no=order.order_no,
                client_name=order.client_name,
                client_obj=client_obj,
                items=items,
                total_usd=order.total_usd,
                total_bs=order.total_bs,
                lang="es",
            )
            if os.path.exists(pdf_path):
                return FileResponse(pdf_path, media_type="application/pdf", filename=f"Order_{target_no}.pdf")

    files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith("quotation_") and f.endswith(".pdf")]
    if files:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)), reverse=True)
        latest_pdf = os.path.join(UPLOAD_DIR, files[0])
        return FileResponse(latest_pdf, media_type="application/pdf", filename="Tostiyk_Quotation.pdf")

    raise HTTPException(status_code=404, detail="PDF 文件不存在")


from datetime import datetime, timezone
@router.post("/api/quotations/{quotation_id}/mark-converted")
def mark_quotation_converted(
    quotation_id: int,
    payload: dict,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("pos:access")),
):
    """POS 下单成功后，把对应报价单标记为已转订单。幂等：已转过就原样返回。"""
    quote = session.get(QuotationRecord, quotation_id)
    if not quote:
        raise HTTPException(status_code=404, detail="报价单不存在")
    if quote.converted_order_id:
        return {"status": "already_converted", "order_id": quote.converted_order_id}
    order_id = payload.get("order_id")
    if not order_id:
        raise HTTPException(status_code=400, detail="缺少 order_id")
    quote.converted_order_id = int(order_id)
    quote.converted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(quote)
    session.commit()
    return {"status": "success", "quotation_id": quotation_id, "order_id": order_id}