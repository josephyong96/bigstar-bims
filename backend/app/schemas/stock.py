"""Stock schemas (Pydantic models)."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StockInRequest(BaseModel):
    item_id: UUID
    location_id: UUID
    project_id: Optional[UUID] = None
    quantity: int = Field(..., gt=0)
    reference_no: Optional[str] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None


class StockOutRequest(BaseModel):
    item_id: UUID
    location_id: UUID
    project_id: Optional[UUID] = None
    quantity: int = Field(..., gt=0)
    reference_no: Optional[str] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None


class TransferRequest(BaseModel):
    item_id: UUID
    from_location_id: UUID
    to_location_id: UUID
    project_id: Optional[UUID] = None
    quantity: int = Field(..., gt=0)
    reference_no: Optional[str] = None
    notes: Optional[str] = None


class AdjustmentRequest(BaseModel):
    item_id: UUID
    location_id: UUID
    new_quantity: int = Field(..., ge=0)
    reason: str = Field(..., min_length=1)


class StockResponse(BaseModel):
    id: UUID
    item_id: UUID
    location_id: UUID
    project_id: Optional[UUID] = None
    quantity: int
    reserved_quantity: int
    unit_cost: Optional[Decimal] = None
    item_name: Optional[str] = None
    item_sku: Optional[str] = None
    location_name: Optional[str] = None
    location_code: Optional[str] = None
    project_code: Optional[str] = None

    class Config:
        from_attributes = True


class StockMovementResponse(BaseModel):
    id: UUID
    movement_type: str
    item_id: UUID
    from_location_id: Optional[UUID] = None
    to_location_id: Optional[UUID] = None
    quantity: int
    reference_no: Optional[str] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True
