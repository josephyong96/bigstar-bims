"""Serial Number schemas (Pydantic models)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SerialNumberBase(BaseModel):
    serial_number: str = Field(..., min_length=1, max_length=200)
    status: str = Field(default="in_stock", pattern="^(in_stock|allocated|in_use|under_repair|disposed|reserved)$")
    notes: Optional[str] = None


class SerialNumberCreate(SerialNumberBase):
    item_id: UUID
    po_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    project_id: Optional[UUID] = None


class SerialNumberUpdate(BaseModel):
    serial_number: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern="^(in_stock|allocated|in_use|under_repair|disposed|reserved)$")
    location_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    notes: Optional[str] = None


class SerialNumberResponse(SerialNumberBase):
    id: UUID
    item_id: UUID
    po_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    created_at: datetime
    item_name: Optional[str] = None
    item_sku: Optional[str] = None
    location_name: Optional[str] = None
    location_code: Optional[str] = None
    project_code: Optional[str] = None

    class Config:
        from_attributes = True


class SerialNumberFilter(BaseModel):
    item_id: Optional[UUID] = None
    status: Optional[str] = None
    po_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    search: Optional[str] = None
