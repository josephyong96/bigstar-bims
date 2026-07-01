"""Delivery Orders router for CRUD and fulfillment workflow."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.delivery_order import DeliveryOrder
from app.schemas.delivery_order import (
    DeliveryOrderCreate, DeliveryOrderUpdate, DeliveryOrderResponse, DeliveryOrderFilter,
)

router = APIRouter(prefix="/delivery-orders", tags=["Delivery Orders"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "sales", "warehouse"])


@router.get("", response_model=list[DeliveryOrderResponse])
def list_delivery_orders(
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List delivery orders with filtering."""
    query = db.query(DeliveryOrder).options(
        joinedload(DeliveryOrder.project),
        joinedload(DeliveryOrder.created_by_user),
    )
    
    if project_id:
        query = query.filter(DeliveryOrder.project_id == project_id)
    if status:
        query = query.filter(DeliveryOrder.status == status)
    if priority:
        query = query.filter(DeliveryOrder.priority == priority)
    if search:
        query = query.filter(DeliveryOrder.do_number.ilike(f"%{search}%"))
    
    orders = query.offset(skip).limit(limit).all()
    return [DeliveryOrderResponse.model_validate(o) for o in orders]


@router.post("", response_model=DeliveryOrderResponse, status_code=status.HTTP_201_CREATED)
def create_delivery_order(
    order_data: DeliveryOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create a new delivery order."""
    order = DeliveryOrder(**order_data.model_dump(), created_by=current_user.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    return DeliveryOrderResponse.model_validate(order)


@router.get("/{order_id}", response_model=DeliveryOrderResponse)
def get_delivery_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single delivery order by ID."""
    order = db.query(DeliveryOrder).options(
        joinedload(DeliveryOrder.project),
        joinedload(DeliveryOrder.created_by_user),
    ).filter(DeliveryOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Delivery order not found")
    
    return DeliveryOrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=DeliveryOrderResponse)
def update_delivery_order(
    order_id: UUID,
    update_data: DeliveryOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update a delivery order."""
    order = db.query(DeliveryOrder).filter(DeliveryOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Delivery order not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(order, key, value)
    
    db.commit()
    db.refresh(order)
    return DeliveryOrderResponse.model_validate(order)


@router.patch("/{order_id}/status")
def update_do_status(
    order_id: UUID,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update delivery order status (dispatch, deliver, cancel)."""
    order = db.query(DeliveryOrder).filter(DeliveryOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Delivery order not found")
    
    new_status = status_update.get("status")
    if new_status not in ["pending", "dispatched", "in_transit", "delivered", "cancelled", "returned"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    return {"id": order.id, "status": order.status, "message": f"Status updated to {new_status}"}
