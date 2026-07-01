"""Project schemas (Pydantic models)."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    project_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = Field(default="active", pattern="^(active|completed|on_hold|cancelled)$")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|on_hold|cancelled)$")


class ProjectResponse(ProjectBase):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectStockSummary(BaseModel):
    project_id: UUID
    project_code: str
    project_name: str
    total_items: int
    total_quantity: int
