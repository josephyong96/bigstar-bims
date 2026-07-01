"""Reports router for dashboards, summaries, and analytics."""

from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.stock import Stock
from app.models.purchase_order import PurchaseOrder
from app.models.repair_ticket import RepairTicket
from app.models.project import Project
from app.models.serial_number import SerialNumber
from app.models.batch_number import BatchNumber

router = APIRouter(prefix="/reports", tags=["Reports"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])


@router.get("/dashboard")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get dashboard summary statistics."""
    total_items = db.query(func.count(Item.id)).scalar()
    total_stock = db.query(func.coalesce(func.sum(Stock.quantity), 0)).scalar()
    low_stock_count = db.query(func.count(Item.id)).filter(
        Item.total_quantity <= Item.reorder_level
    ).scalar()
    
    pending_pos = db.query(func.count(PurchaseOrder.id)).filter(
        PurchaseOrder.status.in_(["pending", "partial"])
    ).scalar()
    
    open_repairs = db.query(func.count(RepairTicket.id)).filter(
        RepairTicket.status.in_(["open", "in_progress"])
    ).scalar()
    
    active_projects = db.query(func.count(Project.id)).filter(
        Project.status == "active"
    ).scalar()
    
    return {
        "total_items": total_items,
        "total_stock": int(total_stock),
        "low_stock_count": low_stock_count,
        "pending_purchase_orders": pending_pos,
        "open_repair_tickets": open_repairs,
        "active_projects": active_projects,
    }


@router.get("/inventory-summary")
def get_inventory_summary(
    category_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get inventory summary grouped by category."""
    from app.models.category import Category
    
    query = db.query(
        Category.name.label("category"),
        func.count(Item.id).label("item_count"),
        func.coalesce(func.sum(Stock.quantity), 0).label("total_quantity"),
    ).join(Item, Item.category_id == Category.id).outerjoin(
        Stock, Stock.item_id == Item.id
    ).group_by(Category.name)
    
    if category_id:
        query = query.filter(Category.id == category_id)
    
    results = query.all()
    
    return [
        {
            "category": r.category,
            "item_count": r.item_count,
            "total_quantity": int(r.total_quantity),
        }
        for r in results
    ]


@router.get("/stock-movements")
def get_stock_movements(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get stock movements for the last N days."""
    from app.models.stock_movement import StockMovement
    
    since = datetime.utcnow() - timedelta(days=days)
    
    movements = db.query(StockMovement).filter(
        StockMovement.created_at >= since
    ).order_by(desc(StockMovement.created_at)).limit(100).all()
    
    return [
        {
            "id": m.id,
            "movement_type": m.movement_type,
            "item_id": m.item_id,
            "quantity": m.quantity,
            "from_location_id": m.from_location_id,
            "to_location_id": m.to_location_id,
            "reference_no": m.reference_no,
            "created_at": m.created_at,
        }
        for m in movements
    ]


@router.get("/purchase-order-summary")
def get_po_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get purchase order summary by status."""
    summary = db.query(
        PurchaseOrder.status,
        func.count(PurchaseOrder.id).label("count"),
        func.coalesce(func.sum(PurchaseOrder.total_amount), 0).label("total_amount"),
    ).group_by(PurchaseOrder.status).all()
    
    return [
        {
            "status": s.status,
            "count": s.count,
            "total_amount": float(s.total_amount),
        }
        for s in summary
    ]


@router.get("/repair-summary")
def get_repair_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get repair ticket summary by status and priority."""
    by_status = db.query(
        RepairTicket.status,
        func.count(RepairTicket.id).label("count"),
    ).group_by(RepairTicket.status).all()
    
    by_priority = db.query(
        RepairTicket.priority,
        func.count(RepairTicket.id).label("count"),
    ).group_by(RepairTicket.priority).all()
    
    return {
        "by_status": [{"status": s.status, "count": s.count} for s in by_status],
        "by_priority": [{"priority": p.priority, "count": p.count} for p in by_priority],
    }


@router.get("/low-stock")
def get_low_stock_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get items with stock below reorder level."""
    items = db.query(Item).filter(
        Item.total_quantity <= Item.reorder_level
    ).all()
    
    return [
        {
            "id": item.id,
            "sku": item.sku,
            "name": item.name,
            "total_quantity": item.total_quantity,
            "reorder_level": item.reorder_level,
            "shortage": item.reorder_level - item.total_quantity,
        }
        for item in items
    ]
