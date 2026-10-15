"""配件主数据：列表 / 新增 / 删除 / 模糊搜索 / 补货建议。"""

import json
import os
import re
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlmodel import Session, select

from app.config import UPLOAD_DIR
from app.database import get_session
from app.deps import Actor, get_current_actor
from app.models import AutoPart
from app.services.audit import log_action

router = APIRouter(tags=["配件"])


@router.get("/api/parts", response_model=List[AutoPart])
def get_parts(session: Session = Depends(get_session)):
    return session.exec(select(AutoPart)).all()


@router.post("/api/parts")
def create_part(
    oem: str = Form(...),
    name: str = Form(...),
    brand: str = Form(...),
    category: str = Form(...),
    stock: int = Form(...),
    price: float = Form(...),
    cross_references: str = Form(default=""),
    files: List[UploadFile] = File(default=[]),
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    image_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_paths.append(f"/uploads/{file.filename}")

    new_part = AutoPart(
        oem=oem,
        name=name,
        brand=brand,
        category=category,
        stock=stock,
        price=price,
        cross_references=cross_references,
        image_url=json.dumps(image_paths) if image_paths else "",
    )
    session.add(new_part)
    session.commit()

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="CREATE_PART",
        details=f"新增了配件商品: {name} (OEM: {oem}, 库存: {stock}, 价格: ${price})",
    )

    return {"status": "success", "message": "Part created successfully"}


@router.delete("/api/parts/{part_id}")
def delete_part(
    part_id: int,
    actor: Actor = Depends(get_current_actor),
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
def search_parts(q: str = Query(...), session: Session = Depends(get_session)):
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
        suggestions.append({
            "oem": p.oem,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "current_stock": p.stock,
            "suggested_qty": suggested_qty,
            "unit_price": p.price,
            "estimated_cost": suggested_qty * p.price,
        })
    return suggestions
