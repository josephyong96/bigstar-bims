"""Barcodes router for generating and scanning barcodes/QR codes."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.utils.barcode_generator import generate_barcode, generate_qrcode, lookup_item_by_barcode

router = APIRouter(prefix="/barcode", tags=["Barcodes"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])


@router.get("/{item_id}")
def get_barcode(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Generate a barcode image (Code128) for an item.
    
    - **item_id**: The item ID, SKU, or barcode string to encode
    """
    try:
        barcode_bytes = generate_barcode(item_id, width=300, height=100)
        return Response(content=barcode_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Barcode generation failed: {str(e)}")


@router.get("/qrcode/{item_id}")
def get_qrcode(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Generate a QR code image for an item.
    
    - **item_id**: The item ID or SKU to encode in the QR code
    """
    try:
        qr_bytes = generate_qrcode(item_id, size=300)
        return Response(content=qr_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")


@router.get("/scan/{code}")
def scan_barcode(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Look up an item by barcode scan.
    
    Tries to match by barcode, SKU, or ID in that order.
    """
    item = lookup_item_by_barcode(db, code)
    if not item:
        raise HTTPException(status_code=404, detail=f"No item found for code: {code}")
    
    return {
        "item_id": str(item.id),
        "sku": item.sku,
        "name": item.name,
        "barcode": item.barcode,
        "description": item.description,
        "inventory_type": item.inventory_type,
        "brand": item.brand,
        "model": item.model,
        "unit_cost": float(item.unit_cost) if item.unit_cost else None,
    }
