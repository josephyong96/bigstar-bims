"""Batch Number schemas (Pydantic models)."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BatchNumberBase(BaseModel):
    batch_number: str = Field(..., min_length=1, max_length=100)
    supplier_batch: Optional[str] = None
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quantity: int = Field(default=0, ge=0)
    status: str = Field(default="active", pattern="^(active|inactive|expired)$")
    notes: Optional[str] = None


class BatchNumberCreate(BatchNumberBase):
    item_id: UUID
    location_id: Optional[UUID] = None


class BatchNumberUpdate(BaseModel):
    batch_number: Optional[str] = Field(None, min_length=1, max_length=100)
    supplier_batch: Optional[str] = None
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quantity: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive|expired)$")
    notes: Optional[str] = None
    location_id: Optional[UUID] = None


class BatchNumberResponse(BatchNumberBase):
    id: UUID
    item_id: UUID
    location_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    item_name: Optional[str] = None
    item_sku: Optional[str] = None
    location_name: Optional[str] = None
    location_code: Optional[str] = None

    class Config:
        from_attributes = True


class BatchNumberFilter(BaseModel):
    item_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    status: Optional[str] = None
    search: Optional[str] = None
