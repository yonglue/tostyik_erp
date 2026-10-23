"""配件主数据：列表 / 新增 / 删除 / 模糊搜索 / 补货建议。"""

import json
import os
import re
import shutil
import io
import pandas as pd
from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.config import UPLOAD_DIR
from app.database import get_session
from app.deps import Actor, get_current_actor, RequirePermission
from app.models import AutoPart, InventoryTransaction
from app.services.audit import log_action

from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["配件"])

# 🌟 防护：限制允许上传的图片后缀
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def _ensure_unique_oem_brand(
    session: Session, oem: str, brand: str, exclude_id: Optional[int] = None
) -> None:
    """(oem, brand) 是库存唯一键，重复建档会让按 OEM 的批量操作再次出现歧义。"""
    stmt = select(AutoPart).where(AutoPart.oem == oem, AutoPart.brand == brand)
    if exclude_id is not None:
        stmt = stmt.where(AutoPart.id != exclude_id)
    if session.exec(stmt).first():
        raise HTTPException(
            status_code=409,
            detail=f"OEM {oem} + 品牌 {brand} 的商品已存在，请直接修改该商品",
        )


def _save_uploaded_files(files: List[UploadFile]) -> List[str]:
    """安全地保存上传文件，返回访问路径"""
    image_paths = []
    for file in files:
        if not file.filename:
            continue
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file.filename}")
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_paths.append(f"/uploads/{file.filename}")
    return image_paths

@router.get("/api/parts", response_model=List[AutoPart])
def get_parts(
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("parts:view")) 
):
    return session.exec(select(AutoPart)).all()


@router.post("/api/parts")
def create_part(
    oem: str = Form(...),
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    stock: int = Form(...),
    price: str = Form(...),
    cost_price: str = Form(default="0.00"), # 🌟 新增：进货价
    tax_rate: str = Form(...),  
    cross_references: str = Form(default=""),
    bin_location: str = Form(default="Estante A-1"),
    files: List[UploadFile] = File(default=[]),
    actor: Actor = Depends(RequirePermission("parts:manage")),
    session: Session = Depends(get_session),
):
    image_paths = _save_uploaded_files(files)
    _ensure_unique_oem_brand(session, oem, brand)
    
    # 🌟 精度处理
    d_price = Decimal(price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    d_cost_price = Decimal(cost_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) # 🌟 新增
    d_tax_rate = Decimal(tax_rate)

    new_part = AutoPart(
        oem=oem,
        name=name,
        brand=brand,
        category=category,
        stock=stock,
        price=float(d_price),
        cost_price=float(d_cost_price), # 🌟 新增
        tax_rate=float(d_tax_rate),
        cross_references=cross_references,
        bin_location=bin_location,
        image_url=json.dumps(image_paths) if image_paths else "",
    )
    session.add(new_part)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"OEM {oem} + 品牌 {brand} 的商品已存在",
        )

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_PART",
        details=f"新增了配件商品: {name} (OEM: {oem}, 税率: {tax_rate}, 库存: {stock}, 售价: ${price}, 进货价: ${cost_price})",
    )

    return {"status": "success", "message": "Part created successfully"}


@router.put("/api/parts/{part_id}")
def update_part(
    part_id: int,
    oem: str = Form(...),
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    stock: int = Form(...),
    price: str = Form(...),
    cost_price: str = Form(default="0.00"), # 🌟 新增
    tax_rate: str = Form(...),
    bin_location: str = Form(default="Estante A-1"),
    cross_references: str = Form(default=""),
    files: List[UploadFile] = File(default=[]),
    actor: Actor = Depends(RequirePermission("parts:manage")),
    session: Session = Depends(get_session),
):
    part = session.get(AutoPart, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    if files:
        image_paths = _save_uploaded_files(files)
        part.image_url = json.dumps(image_paths)

    _ensure_unique_oem_brand(session, oem, brand, exclude_id=part_id)

    d_price = Decimal(price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    d_cost_price = Decimal(cost_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) # 🌟 新增
    d_tax_rate = Decimal(tax_rate)

    part.oem = oem
    part.name = name
    part.brand = brand
    part.category = category
    part.stock = stock
    part.price = float(d_price)
    part.cost_price = float(d_cost_price) # 🌟 新增
    part.tax_rate = float(d_tax_rate)
    part.bin_location = bin_location
    part.cross_references = cross_references

    session.add(part)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"OEM {oem} + 品牌 {brand} 的商品已存在",
        )

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="UPDATE_PART",
        details=f"更新了配件商品档案: {name} (OEM: {oem}, 税率: {tax_rate}, 库存: {stock}, 售价: ${price}, 进货价: ${cost_price})",
    )

    return {"status": "success", "message": "Part updated successfully"}


@router.delete("/api/parts/{part_id}")
def delete_part(
    part_id: int,
    actor: Actor = Depends(RequirePermission("parts:manage")),
    session: Session = Depends(get_session),
):
    part = session.get(AutoPart, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    part_name = part.name
    session.delete(part)
    session.commit()

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="DELETE_PART",
        details=f"删除了配件商品: {part_name} (ID: {part_id})",
    )

    return {"status": "success", "message": "Part deleted"}


@router.get("/api/parts/search")
def search_parts(
    q: str = Query(...), 
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("parts:view"))
):
    if not q or not q.strip():
        return []

    cleaned_query = re.sub(r"[^A-Z0-9]", "", q.upper())
    raw_query = q.strip()

    all_parts = session.exec(select(AutoPart)).all()
    matched_parts = []

    for part in all_parts:
        clean_db_oem = re.sub(r"[^A-Z0-9]", "", part.oem.upper()) if part.oem else ""
        clean_db_refs = (
            re.sub(r"[^A-Z0-9]", "", part.cross_references.upper())
            if part.cross_references
            else ""
        )
        clean_db_name = part.name.upper() if part.name else ""
        clean_db_brand = part.brand.upper() if part.brand else ""

        if (
            cleaned_query in clean_db_oem
            or cleaned_query in clean_db_refs
            or raw_query.upper() in clean_db_name
            or raw_query.upper() in clean_db_brand
            or clean_db_oem in cleaned_query
        ):
            matched_parts.append(part)

    return matched_parts


@router.get("/api/procurement/suggestions")
def get_procurement_suggestions(
    brand: Optional[str] = None,
    category: Optional[str] = None,
    threshold: int = 5,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("procurement:view"))
):
    query = select(AutoPart).where(AutoPart.stock <= threshold)
    if brand and brand != "ALL":
        query = query.where(AutoPart.brand == brand)
    if category and category != "ALL":
        query = query.where(AutoPart.category == category)

    parts = session.exec(query).all()
    suggestions = []
    for p in parts:
        suggested_qty = max(10 - p.stock, 5)
        
        # 精度保护
        d_price = Decimal(str(p.price))
        d_cost = d_price * suggested_qty
        
        suggestions.append({
            "oem": p.oem,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "current_stock": p.stock,
            "suggested_qty": suggested_qty,
            "unit_price": float(d_price),
            "estimated_cost": float(d_cost),
        })

    return suggestions



# ==================== 🌟 库存盘点接口 ====================
class AuditItemPayload(BaseModel):
    part_id: int
    actual_stock: int
    reason: Optional[str] = ""

class AuditPayload(BaseModel):
    items: List[AuditItemPayload]

@router.post("/api/inventory/audit")
def audit_inventory(
    payload: AuditPayload,
    session: Session = Depends(get_session),
    actor: Actor = Depends(RequirePermission("parts:manage")),
):
    """接收前端提交的盘点单，比对系统库存并生成损益流水"""
    changed_count = 0
    
    # 🌟 新增：生成全局唯一的批次号，并获取当前操作人
    batch_no = f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    operator = actor.username
    
    for item in payload.items:
        part = session.get(AutoPart, item.part_id)
        if not part:
            continue
            
        diff = item.actual_stock - part.stock
        if diff == 0:
            continue
            
        old_stock = part.stock
        part.stock = item.actual_stock
        session.add(part)
        
        tx_type = "IN" if diff > 0 else "OUT"
        tx = InventoryTransaction(
            part_oem=part.oem,
            part_name=part.name,
            type=tx_type,
            quantity=abs(diff),
            unit_price=part.cost_price or 0.0,
            total_amount=abs(diff) * (part.cost_price or 0.0),
            # 🌟 核心修改：写入批次号和操作人
            customer_or_supplier=f"库存盘点调整|{batch_no}|{operator}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        session.add(tx)
        changed_count += 1
        
        log_action(
            session=session,
            username=actor.username,
            role=actor.role,
            action="UPDATE_STOCK",
            details=f"盘点调整(批次:{batch_no}): {part.name}(OEM:{part.oem}) 原库存:{old_stock} -> 实盘:{item.actual_stock}，原因:{item.reason}"
        )
        
    session.commit()
    return {"status": "success", "message": f"盘点完成，共调整了 {changed_count} 个商品库存"}






