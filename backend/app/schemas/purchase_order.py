"""Purchase Order schemas (Pydantic models)."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class POItemCreate(BaseModel):
    item_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)


class POItemResponse(BaseModel):
    id: UUID
    po_id: UUID
    item_id: UUID
    quantity: int
    unit_price: Decimal
    received_qty: int
    item_name: Optional[str] = None
    item_sku: Optional[str] = None

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    supplier_name: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[POItemCreate]


class PurchaseOrderUpdate(BaseModel):
    supplier_name: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|partial|received|cancelled)$")


class PurchaseOrderResponse(PurchaseOrderBase):
    id: UUID
    po_number: str
    status: str
    total_amount: Decimal
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None
    po_items: List[POItemResponse] = []

    class Config:
        from_attributes = True


class PurchaseOrderFilter(BaseModel):
    status: Optional[str] = None
    supplier_name: Optional[str] = None
    search: Optional[str] = None
