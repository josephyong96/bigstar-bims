"""Purchase Orders router with CRUD, receive, and PDF generation."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.purchase_order import PurchaseOrder
from app.models.po_item import POItem
from app.schemas.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse, POItemCreate,
)
from app.utils.pdf_generator import generate_po_pdf

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "warehouse"])


@router.get("", response_model=list[PurchaseOrderResponse])
def list_purchase_orders(
    status: Optional[str] = None,
    supplier_name: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List purchase orders with filtering."""
    query = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.po_items),
        joinedload(PurchaseOrder.created_by_user),
    )
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if supplier_name:
        query = query.filter(PurchaseOrder.supplier_name.ilike(f"%{supplier_name}%"))
    if search:
        query = query.filter(PurchaseOrder.po_number.ilike(f"%{search}%"))
    
    orders = query.offset(skip).limit(limit).all()
    return [PurchaseOrderResponse.model_validate(o) for o in orders]


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    order_data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create a new purchase order with items."""
    # Create PO
    po = PurchaseOrder(
        supplier_name=order_data.supplier_name,
        notes=order_data.notes,
        created_by=current_user.id,
    )
    db.add(po)
    db.flush()
    
    # Create PO items
    for item_data in order_data.items:
        po_item = POItem(
            po_id=po.id,
            item_id=item_data.item_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
        )
        db.add(po_item)
    
    db.commit()
    db.refresh(po)
    return PurchaseOrderResponse.model_validate(po)


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single purchase order by ID."""
    order = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.po_items),
        joinedload(PurchaseOrder.created_by_user),
    ).filter(PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    return PurchaseOrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=PurchaseOrderResponse)
def update_purchase_order(
    order_id: UUID,
    update_data: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update a purchase order."""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key != "items":
            setattr(order, key, value)
    
    db.commit()
    db.refresh(order)
    return PurchaseOrderResponse.model_validate(order)


@router.post("/{order_id}/receive")
def receive_purchase_order(
    order_id: UUID,
    receive_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Receive items from a purchase order.
    
    Updates stock quantities and marks items as received.
    """
    from app.models.stock import Stock
    from app.models.serial_number import SerialNumber
    
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if order.status not in ["pending", "partial"]:
        raise HTTPException(status_code=400, detail="PO is not in receivable status")
    
    # Process received items
    for item_receive in receive_data.get("items", []):
        item_id = item_receive.get("item_id")
        quantity = item_receive.get("quantity", 0)
        location_id = receive_data.get("location_id")
        serials = item_receive.get("serials", [])
        
        # Update PO item received quantity
        po_item = db.query(POItem).filter(
            POItem.po_id == order_id,
            POItem.item_id == item_id,
        ).first()
        
        if po_item:
            po_item.received_qty = (po_item.received_qty or 0) + quantity
        
        # Update stock
        stock = db.query(Stock).filter(
            Stock.item_id == item_id,
            Stock.location_id == location_id,
        ).first()
        
        if stock:
            stock.quantity += quantity
        else:
            stock = Stock(item_id=item_id, location_id=location_id, quantity=quantity)
            db.add(stock)
        
        # Create serial numbers if provided
        for serial in serials:
            sn = SerialNumber(
                serial_number=serial,
                item_id=item_id,
                po_id=order_id,
                status="in_stock",
                location_id=location_id,
            )
            db.add(sn)
    
    # Update PO status
    all_items = db.query(POItem).filter(POItem.po_id == order_id).all()
    if all(item.received_qty >= item.quantity for item in all_items):
        order.status = "received"
    else:
        order.status = "partial"
    
    db.commit()
    db.refresh(order)
    return PurchaseOrderResponse.model_validate(order)


@router.get("/{order_id}/pdf")
def get_purchase_order_pdf(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Generate a PDF for a purchase order."""
    order = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.po_items),
    ).filter(PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    pdf_bytes = generate_po_pdf(order)
    return Response(content=pdf_bytes, media_type="application/pdf")
