"""配件主数据：列表 / 新增 / 删除 / 模糊搜索 / 补货建议。"""

import json
import os
import re
import shutil
import io
import pandas as pd
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
    tax_rate: float = Form(...),  # 用户手动选择税率 (如 0.16 或 0.0)
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
        tax_rate=tax_rate,
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
        details=f"新增了配件商品: {name} (OEM: {oem}, 税率: {int(tax_rate*100)}%, 库存: {stock}, 价格: ${price})",
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
    price: float = Form(...),
    tax_rate: float = Form(...),  # 用户手动选择税率
    bin_location: str = Form(default="Estante A-1"),
    cross_references: str = Form(default=""),
    files: List[UploadFile] = File(default=[]),
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    part = session.get(AutoPart, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")

    image_paths = []
    if files:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_paths.append(f"/uploads/{file.filename}")
        part.image_url = json.dumps(image_paths)

    part.oem = oem
    part.name = name
    part.brand = brand
    part.category = category
    part.stock = stock
    part.price = price
    part.tax_rate = tax_rate
    part.bin_location = bin_location
    part.cross_references = cross_references

    session.add(part)
    session.commit()

    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="UPDATE_PART",
        details=f"更新了配件商品档案: {name} (OEM: {oem}, 税率: {int(tax_rate*100)}%, 库存: {stock}, 价格: ${price})",
    )

    return {"status": "success", "message": "Part updated successfully"}


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

@router.post("/api/import/parts")
async def import_parts(
    file: UploadFile = File(...),
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_session),
):
    """智能批量导入接口：完美支持 Excel (.xlsx) 和 CSV 文件，自动兼容中英文表头"""
    contents = await file.read()
    
    try:
        filename = file.filename.lower()
        print(f"📂 正在接收导入文件: {file.filename}, 大小: {len(contents)} 字节")
        
        if filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            for encoding in ['utf-8-sig', 'latin1', 'cp1252']:
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise HTTPException(status_code=400, detail="❌ CSV 文件编码无法识别，请使用 UTF-8！")
    except Exception as e:
        print(f"❌ 文件读取异常: {e}")
        raise HTTPException(status_code=400, detail=f"❌ 文件解析失败: {str(e)}")

    # 统一将列名转为小写去空格，并兼容中文表头映射
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    col_mapping = {
        '编号': 'oem', '代码': 'oem', 'sku': 'oem',
        '名称': 'name', '品名': 'name', '商品名称': 'name',
        '品牌': 'brand',
        '分类': 'category', '商品分类': 'category',
        '库存': 'stock', '数量': 'stock',
        '价格': 'price', '单价': 'price', '零售价': 'price',
        '货架': 'bin_location', '库位': 'bin_location', '货架位': 'bin_location'
    }
    df = df.rename(columns=col_mapping)

    imported_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():
        try:
            oem = str(row.get('oem', '')).strip()
            name = str(row.get('name', '')).strip()
            
            if not oem or oem == 'nan' or not name or name == 'nan':
                skipped_count += 1
                continue

            brand = str(row.get('brand', 'GENERAL')).strip()
            if not brand or brand == 'nan': brand = 'GENERAL'

            category = str(row.get('category', '未分类')).strip()
            if not category or category == 'nan': category = '未分类'

            bin_location = str(row.get('bin_location', 'Estante A-1')).strip()
            if not bin_location or bin_location == 'nan': bin_location = 'Estante A-1'

            try:
                stock = int(float(row.get('stock', 0)))
            except Exception:
                stock = 0

            try:
                price = float(row.get('price', 0.0))
            except Exception:
                price = 0.0

            # 检查数据库中是否已存在该 OEM
            existing = session.exec(select(AutoPart).where(AutoPart.oem == oem)).first()
            if existing:
                existing.name = name
                existing.brand = brand
                existing.category = category
                existing.stock = stock
                existing.price = price
                existing.bin_location = bin_location
                session.add(existing)
            else:
                new_part = AutoPart(
                    oem=oem,
                    name=name,
                    brand=brand,
                    category=category,
                    stock=stock,
                    price=price,
                    bin_location=bin_location,
                    cross_references="",
                    image_url=""
                )
                session.add(new_part)
                
            imported_count += 1
        except Exception as e:
            print(f"⚠️ 处理第 {idx+2} 行出错: {e}")
            skipped_count += 1

    session.commit()

    # 🌟 写入系统审计日志
    log_action(
        session=session,
        username=actor.username,
        role=actor.role,
        action="IMPORT_PARTS",
        details=f"成功批量导入 {imported_count} 个商品，跳过 {skipped_count} 个无效行",
    )

    print(f"✨ 导入完成统计 -> 成功: {imported_count}, 跳过: {skipped_count}")

    return {
        "status": "success", 
        "message": f"成功导入 {imported_count} 个商品，跳过 {skipped_count} 个无效行",
        "imported_count": imported_count,
        "updated_count": imported_count,
        "count": imported_count
    }