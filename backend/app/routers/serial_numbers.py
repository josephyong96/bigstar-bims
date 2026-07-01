"""Serial Numbers router for CRUD and bulk operations."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.serial_number import SerialNumber
from app.schemas.serial_number import (
    SerialNumberCreate, SerialNumberUpdate, SerialNumberResponse, SerialNumberFilter,
)

router = APIRouter(prefix="/serials", tags=["Serial Numbers"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "warehouse"])


@router.get("", response_model=list[SerialNumberResponse])
def list_serial_numbers(
    item_id: Optional[UUID] = None,
    status: Optional[str] = None,
    po_id: Optional[UUID] = None,
    location_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List serial numbers with filtering."""
    query = db.query(SerialNumber).options(
        joinedload(SerialNumber.item),
        joinedload(SerialNumber.location),
        joinedload(SerialNumber.project),
    )
    
    if item_id:
        query = query.filter(SerialNumber.item_id == item_id)
    if status:
        query = query.filter(SerialNumber.status == status)
    if po_id:
        query = query.filter(SerialNumber.po_id == po_id)
    if location_id:
        query = query.filter(SerialNumber.location_id == location_id)
    if project_id:
        query = query.filter(SerialNumber.project_id == project_id)
    if search:
        query = query.filter(SerialNumber.serial_number.ilike(f"%{search}%"))
    
    serials = query.offset(skip).limit(limit).all()
    return [SerialNumberResponse.model_validate(s) for s in serials]


@router.post("", response_model=list[SerialNumberResponse], status_code=status.HTTP_201_CREATED)
def create_serial_numbers(
    batch_data: list[SerialNumberCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create serial numbers in bulk."""
    created = []
    for sn_data in batch_data:
        existing = db.query(SerialNumber).filter(
            SerialNumber.serial_number == sn_data.serial_number,
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Serial number already exists: {sn_data.serial_number}",
            )
        
        sn = SerialNumber(**sn_data.model_dump())
        db.add(sn)
        created.append(sn)
    
    db.commit()
    for sn in created:
        db.refresh(sn)
    
    return [SerialNumberResponse.model_validate(s) for s in created]


@router.get("/{serial_id}", response_model=SerialNumberResponse)
def get_serial_number(
    serial_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single serial number by ID."""
    sn = db.query(SerialNumber).options(
        joinedload(SerialNumber.item),
        joinedload(SerialNumber.location),
        joinedload(SerialNumber.project),
    ).filter(SerialNumber.id == serial_id).first()
    
    if not sn:
        raise HTTPException(status_code=404, detail="Serial number not found")
    
    return SerialNumberResponse.model_validate(sn)


@router.put("/{serial_id}", response_model=SerialNumberResponse)
def update_serial_number(
    serial_id: UUID,
    update_data: SerialNumberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update a serial number."""
    sn = db.query(SerialNumber).filter(SerialNumber.id == serial_id).first()
    if not sn:
        raise HTTPException(status_code=404, detail="Serial number not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(sn, key, value)
    
    db.commit()
    db.refresh(sn)
    return SerialNumberResponse.model_validate(sn)


@router.post("/bulk-update")
def bulk_update_serial_status(
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Bulk update serial number status."""
    serial_ids = update_data.get("serial_ids", [])
    new_status = update_data.get("status")
    location_id = update_data.get("location_id")
    project_id = update_data.get("project_id")
    
    query = db.query(SerialNumber).filter(SerialNumber.id.in_(serial_ids))
    
    updates = {}
    if new_status:
        updates["status"] = new_status
    if location_id:
        updates["location_id"] = location_id
    if project_id:
        updates["project_id"] = project_id
    
    count = query.update(updates, synchronize_session=False)
    db.commit()
    
    return {"updated": count, "serial_ids": serial_ids}
