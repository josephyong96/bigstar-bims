"""Repair Ticket schemas (Pydantic models)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RepairTicketBase(BaseModel):
    issue_description: str = Field(..., min_length=1)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    resolution_notes: Optional[str] = None


class RepairTicketCreate(RepairTicketBase):
    item_id: UUID
    serial_id: Optional[UUID] = None


class RepairTicketUpdate(BaseModel):
    issue_description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(open|in_progress|on_hold|resolved|closed|cancelled)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    assigned_to: Optional[UUID] = None
    resolution_notes: Optional[str] = None


class RepairTicketResponse(RepairTicketBase):
    id: UUID
    ticket_number: str
    item_id: UUID
    serial_id: Optional[UUID] = None
    reported_by: UUID
    status: str
    assigned_to: Optional[UUID] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    item_name: Optional[str] = None
    item_sku: Optional[str] = None
    reported_by_name: Optional[str] = None
    assigned_to_name: Optional[str] = None

    class Config:
        from_attributes = True


class RepairTicketFilter(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    item_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    search: Optional[str] = None
