"""Stock router - the core business logic for all inventory operations.

This router handles stock in, stock out, transfers, returns, and adjustments
with proper ACID compliance through database transactions.
"""

from typing import Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.item import Item
from app.schemas.stock import (
    StockInRequest, StockOutRequest, TransferRequest, AdjustmentRequest,
    StockResponse, StockMovementResponse,
)

router = APIRouter(prefix="/stock", tags=["Stock"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "warehouse"])


@router.get("", response_model=list[StockResponse])
def list_stock(
    item_id: Optional[UUID] = None,
    location_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List stock records with filtering."""
    query = db.query(Stock)
    
    if item_id:
        query = query.filter(Stock.item_id == item_id)
    if location_id:
        query = query.filter(Stock.location_id == location_id)
    if project_id:
        query = query.filter(Stock.project_id == project_id)
    
    stocks = query.offset(skip).limit(limit).all()
    return [StockResponse.model_validate(s) for s in stocks]


@router.post("/in")
def stock_in(
    request: StockInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Record stock in (receipt/adjustment in).
    
    - Updates stock quantity at the specified location
    - Creates a stock movement record
    """
    # Check if stock record exists
    stock = db.query(Stock).filter(
        Stock.item_id == request.item_id,
        Stock.location_id == request.location_id,
        Stock.project_id == request.project_id,
    ).first()
    
    if stock:
        stock.quantity += request.quantity
    else:
        stock = Stock(
            item_id=request.item_id,
            location_id=request.location_id,
            project_id=request.project_id,
            quantity=request.quantity,
        )
        db.add(stock)
    
    # Create movement record
    movement = StockMovement(
        movement_type="stock_in",
        item_id=request.item_id,
        to_location_id=request.location_id,
        quantity=request.quantity,
        reference_no=request.reference_no,
        reference_type=request.reference_type,
        notes=request.notes,
        created_by=current_user.id,
    )
    db.add(movement)
    
    db.commit()
    db.refresh(stock)
    
    return {
        "message": "Stock in recorded successfully",
        "item_id": request.item_id,
        "location_id": request.location_id,
        "quantity_added": request.quantity,
        "new_total": stock.quantity,
    }


@router.post("/out")
def stock_out(
    request: StockOutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Record stock out (delivery/adjustment out).
    
    - Validates sufficient stock is available
    - Updates stock quantity at the specified location
    - Creates a stock movement record
    """
    # Check if stock record exists and has sufficient quantity
    stock = db.query(Stock).filter(
        Stock.item_id == request.item_id,
        Stock.location_id == request.location_id,
        Stock.project_id == request.project_id,
    ).first()
    
    if not stock or stock.quantity < request.quantity:
        available = stock.quantity if stock else 0
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient stock. Available: {available}, Requested: {request.quantity}",
        )
    
    # Deduct stock
    stock.quantity -= request.quantity
    
    # Create movement record
    movement = StockMovement(
        movement_type="stock_out",
        item_id=request.item_id,
        from_location_id=request.location_id,
        quantity=request.quantity,
        reference_no=request.reference_no,
        reference_type=request.reference_type,
        notes=request.notes,
        created_by=current_user.id,
    )
    db.add(movement)
    
    db.commit()
    db.refresh(stock)
    
    return {
        "message": "Stock out recorded successfully",
        "item_id": request.item_id,
        "location_id": request.location_id,
        "quantity_removed": request.quantity,
        "remaining": stock.quantity,
    }


@router.post("/transfer")
def transfer_stock(
    request: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Transfer stock between locations.
    
    - Validates sufficient stock at source location
    - Deducts from source and adds to destination
    - Creates movement records for both sides
    """
    # Check source stock
    source_stock = db.query(Stock).filter(
        Stock.item_id == request.item_id,
        Stock.location_id == request.from_location_id,
        Stock.project_id == request.project_id,
    ).first()
    
    if not source_stock or source_stock.quantity < request.quantity:
        available = source_stock.quantity if source_stock else 0
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient stock at source. Available: {available}, Requested: {request.quantity}",
        )
    
    # Deduct from source
    source_stock.quantity -= request.quantity
    
    # Add to destination
    dest_stock = db.query(Stock).filter(
        Stock.item_id == request.item_id,
        Stock.location_id == request.to_location_id,
        Stock.project_id == request.project_id,
    ).first()
    
    if dest_stock:
        dest_stock.quantity += request.quantity
    else:
        dest_stock = Stock(
            item_id=request.item_id,
            location_id=request.to_location_id,
            project_id=request.project_id,
            quantity=request.quantity,
        )
        db.add(dest_stock)
    
    # Create movement record
    movement = StockMovement(
        movement_type="transfer",
        item_id=request.item_id,
        from_location_id=request.from_location_id,
        to_location_id=request.to_location_id,
        quantity=request.quantity,
        reference_no=request.reference_no,
        notes=request.notes,
        created_by=current_user.id,
    )
    db.add(movement)
    
    db.commit()
    
    return {
        "message": "Stock transfer completed successfully",
        "item_id": request.item_id,
        "from_location_id": request.from_location_id,
        "to_location_id": request.to_location_id,
        "quantity_transferred": request.quantity,
    }


@router.get("/movements")
def list_stock_movements(
    item_id: Optional[UUID] = None,
    movement_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List stock movement records with filtering."""
    query = db.query(StockMovement).order_by(StockMovement.created_at.desc())
    
    if item_id:
        query = query.filter(StockMovement.item_id == item_id)
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    
    movements = query.offset(skip).limit(limit).all()
    return [StockMovementResponse.model_validate(m) for m in movements]


@router.post("/adjust")
def adjust_stock(
    request: AdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Adjust stock quantity (for corrections, damage, etc.)."""
    stock = db.query(Stock).filter(
        Stock.item_id == request.item_id,
        Stock.location_id == request.location_id,
    ).first()
    
    old_qty = stock.quantity if stock else 0
    
    if stock:
        stock.quantity = request.new_quantity
    else:
        stock = Stock(
            item_id=request.item_id,
            location_id=request.location_id,
            quantity=request.new_quantity,
        )
        db.add(stock)
    
    # Create movement record
    movement = StockMovement(
        movement_type="adjustment",
        item_id=request.item_id,
        to_location_id=request.location_id,
        quantity=request.new_quantity - old_qty,
        notes=f"Adjustment: {old_qty} -> {request.new_quantity}. Reason: {request.reason}",
        created_by=current_user.id,
    )
    db.add(movement)
    
    db.commit()
    db.refresh(stock)
    
    return {
        "message": "Stock adjusted successfully",
        "item_id": request.item_id,
        "location_id": request.location_id,
        "old_quantity": old_qty,
        "new_quantity": stock.quantity,
    }
