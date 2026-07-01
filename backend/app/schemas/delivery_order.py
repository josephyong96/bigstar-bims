"""Delivery Order schemas (Pydantic models)."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class DeliveryOrderItem(BaseModel):
    item_id: UUID
    quantity: int = Field(..., gt=0)
    serial_ids: Optional[List[UUID]] = None
    notes: Optional[str] = None


class DeliveryOrderBase(BaseModel):
    do_number: str = Field(..., min_length=1, max_length=50)
    project_id: UUID
    destination_location_id: Optional[UUID] = None
    delivery_date: Optional[datetime] = None
    status: str = Field(default="pending", pattern="^(pending|dispatched|in_transit|delivered|cancelled|returned)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    notes: Optional[str] = None


class DeliveryOrderCreate(DeliveryOrderBase):
    items: List[DeliveryOrderItem]


class DeliveryOrderUpdate(BaseModel):
    do_number: Optional[str] = Field(None, min_length=1, max_length=50)
    project_id: Optional[UUID] = None
    destination_location_id: Optional[UUID] = None
    delivery_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(pending|dispatched|in_transit|delivered|cancelled|returned)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    notes: Optional[str] = None


class DeliveryOrderResponse(DeliveryOrderBase):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None
    project_code: Optional[str] = None
    project_name: Optional[str] = None

    class Config:
        from_attributes = True


class DeliveryOrderFilter(BaseModel):
    project_id: Optional[UUID] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    search: Optional[str] = None
