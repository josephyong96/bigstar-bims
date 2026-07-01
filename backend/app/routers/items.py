"""Items router for CRUD, search, barcode lookup, and stock summary."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.stock import Stock
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemFilter, ItemStockSummary

router = APIRouter(prefix="/items", tags=["Items"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "warehouse"])


@router.get("", response_model=list[ItemResponse])
def list_items(
    category_id: Optional[UUID] = None,
    brand: Optional[str] = None,
    inventory_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List items with filtering, search, and low-stock alert.
    
    - **search**: Searches SKU, name, description, brand, model
    - **low_stock**: When true, only shows items below reorder level
    """
    query = db.query(Item).options(
        joinedload(Item.category),
        joinedload(Item.stocks),
    )
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    if brand:
        query = query.filter(Item.brand.ilike(f"%{brand}%"))
    if inventory_type:
        query = query.filter(Item.inventory_type == inventory_type)
    if status:
        query = query.filter(Item.status == status)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Item.sku.ilike(search_filter)) |
            (Item.name.ilike(search_filter)) |
            (Item.description.ilike(search_filter)) |
            (Item.brand.ilike(search_filter)) |
            (Item.model.ilike(search_filter))
        )
    if low_stock:
        query = query.filter(Item.total_quantity <= Item.reorder_level)
    
    items = query.offset(skip).limit(limit).all()
    return [ItemResponse.model_validate(i) for i in items]


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create a new item."""
    existing = db.query(Item).filter(Item.sku == item_data.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"SKU already exists: {item_data.sku}")
    
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single item by ID."""
    item = db.query(Item).options(
        joinedload(Item.category),
        joinedload(Item.stocks),
    ).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: UUID,
    update_data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return ItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Delete an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return None


@router.get("/{item_id}/stock-summary")
def get_item_stock_summary(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get stock summary for a specific item across all locations."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stocks = db.query(Stock).filter(Stock.item_id == item_id).all()
    total_qty = sum(s.quantity for s in stocks)
    total_reserved = sum(s.reserved_quantity for s in stocks)
    
    return {
        "item_id": item_id,
        "sku": item.sku,
        "name": item.name,
        "total_quantity": total_qty,
        "total_reserved": total_reserved,
        "available": total_qty - total_reserved,
        "reorder_level": item.reorder_level,
        "is_low_stock": total_qty <= item.reorder_level,
        "locations": [
            {
                "location_id": s.location_id,
                "quantity": s.quantity,
                "reserved": s.reserved_quantity,
            }
            for s in stocks
        ],
    }
