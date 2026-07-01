"""Locations router for CRUD."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_any_role, get_current_user
from app.models.user import User
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter(prefix="/locations", tags=["Locations"])

read_role = require_any_role(["management", "project_manager", "sales", "warehouse", "technician"])
write_role = require_any_role(["management", "warehouse"])


@router.get("", response_model=list[LocationResponse])
def list_locations(
    location_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """List locations with filtering."""
    query = db.query(Location)
    
    if location_type:
        query = query.filter(Location.type == location_type)
    if status:
        query = query.filter(Location.status == status)
    if search:
        query = query.filter(Location.name.ilike(f"%{search}%"))
    
    locations = query.offset(skip).limit(limit).all()
    return [LocationResponse.model_validate(l) for l in locations]


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    location_data: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Create a new location."""
    existing = db.query(Location).filter(Location.code == location_data.code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Location code already exists: {location_data.code}")
    
    location = Location(**location_data.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return LocationResponse.model_validate(location)


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(read_role),
):
    """Get a single location by ID."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return LocationResponse.model_validate(location)


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: UUID,
    update_data: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Update a location."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(location, key, value)
    
    db.commit()
    db.refresh(location)
    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_role),
):
    """Delete a location."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    db.delete(location)
    db.commit()
    return None
