"""报价单：列表 / 删除 / 生成（含开单出库 + PDF）/ 下载最新 PDF。"""

import json
import os
from datetime import datetime
from typing import List

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
        # 只 flush 取 id：新客户也并入本单事务，开单失败时不会留下孤立客户档案
        session.flush()

    # 库存变动先只做扣减、不写审计日志：log_action 内部会 session.commit()，
    # 若在循环里调用，会把前面几件的扣减提前提交，导致后续某件校验失败时无法整体回滚。
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

        # ⚠️ SQLite 不支持 SELECT ... FOR UPDATE（with_for_update 会被静默忽略），
        # 因此"先读库存再写库存"存在并发超卖竞态：5 人抢 1 件可能多人同时成功。
        # 改为原子条件更新 + 校验影响行数。
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
            # 必须回滚：此时本单的库存扣减还未提交，不回滚就会变成"拒单但扣了库存"
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=(
                    f"⚠️ 信用额度超限警报！该客户当前欠款 ${client_obj.debt:.2f}，"
                    f"本次挂账 ${total_usd:.2f}，总计 ${projected_debt:.2f} 已超出设定的信用额度上限 "
                    f"(${client_obj.credit_limit:.2f})，拒绝挂账！"
                ),
            )
        # 带额度守卫的原子自增：并发挂账时由数据库保证不会突破信用上限
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

    # 报价单记录也是本单的一部分，必须与库存扣减、流水、欠款同事务落库
    record = QuotationRecord(
        quotation_no=quotation_no,
        client_name=client_name,
        total_usd=total_usd,
        total_bs=total_bs,
        bcv_rate=bcv_rate,
        lang=payload.lang,
        items_json=json.dumps(items_snapshot, ensure_ascii=False),
    )
    session.add(record)

    # 唯一一次提交：库存扣减 + 进销存流水 + 客户欠款 + 报价单记录
    session.commit()

    # 数据落库之后再写审计日志（log_action 自带 commit，放前面会把业务数据提前提交）
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

    lang = normalize_lang(getattr(payload, "lang", "es"))
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
def download_existing_pdf():
    """返回 uploads 目录下最新生成的一份报价单 PDF。"""
    files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith("quotation_") and f.endswith(".pdf")]
    if files:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)), reverse=True)
        latest_pdf = os.path.join(UPLOAD_DIR, files[0])
        return FileResponse(latest_pdf, media_type="application/pdf", filename="Tostiyk_Quotation.pdf")

    raise HTTPException(status_code=404, detail="PDF 文件不存在")
