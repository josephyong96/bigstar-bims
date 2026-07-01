"""Batch Numbers router for CRUD and quantity tracking."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.batch_number import BatchNumber
from app.schemas.batch_number import (
    BatchNumberCreate, BatchNumberUpdate, BatchNumberResponse, BatchNumberFilter,
)

router = APIRouter(prefix="/batches", tags=["Batch Numbers"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "warehouse"])


@router.get("", response_model=list[BatchNumberResponse])
def list_batches(
    item_id: Optional[UUID] = None,
    location_id: Optional[UUID] = None,
    status: Optional[str] = None,
    expiry_before: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List batch numbers with filtering."""
    from datetime import date
    query = db.query(BatchNumber).options(
        joinedload(BatchNumber.item),
        joinedload(BatchNumber.location),
    )
    
    if item_id:
        query = query.filter(BatchNumber.item_id == item_id)
    if location_id:
        query = query.filter(BatchNumber.location_id == location_id)
    if status:
        query = query.filter(BatchNumber.status == status)
    if expiry_before:
        query = query.filter(BatchNumber.expiry_date <= date.fromisoformat(expiry_before))
    if search:
        query = query.filter(BatchNumber.batch_number.ilike(f"%{search}%"))
    
    batches = query.offset(skip).limit(limit).all()
    
    return [
        BatchNumberResponse(
            id=b.id,
            item_id=b.item_id,
            batch_number=b.batch_number,
            location_id=b.location_id,
            quantity=b.quantity,
            expiry_date=b.expiry_date,
            manufacture_date=b.manufacture_date,
            supplier_batch=b.supplier_batch,
            status=b.status,
            created_at=b.created_at,
            item_name=b.item.name if b.item else None,
            item_sku=b.item.sku if b.item else None,
            location_name=b.location.name if b.location else None,
            location_code=b.location.code if b.location else None,
        )
        for b in batches
    ]


@router.post("", response_model=BatchNumberResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    batch_data: BatchNumberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create a batch number record."""
    existing = db.query(BatchNumber).filter(
        BatchNumber.item_id == batch_data.item_id,
        BatchNumber.batch_number == batch_data.batch_number,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Batch number already exists for this item")
    
    batch = BatchNumber(**batch_data.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return BatchNumberResponse.model_validate(batch)


@router.get("/{batch_id}", response_model=BatchNumberResponse)
def get_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single batch number by ID."""
    batch = db.query(BatchNumber).options(
        joinedload(BatchNumber.item),
        joinedload(BatchNumber.location),
    ).filter(BatchNumber.id == batch_id).first()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch number not found")
    
    return BatchNumberResponse.model_validate(batch)


@router.put("/{batch_id}", response_model=BatchNumberResponse)
def update_batch(
    batch_id: UUID,
    update_data: BatchNumberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update a batch number record."""
    batch = db.query(BatchNumber).filter(BatchNumber.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch number not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(batch, key, value)
    
    db.commit()
    db.refresh(batch)
    return BatchNumberResponse.model_validate(batch)


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Delete a batch number record."""
    batch = db.query(BatchNumber).filter(BatchNumber.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch number not found")
    
    db.delete(batch)
    db.commit()
    return None
