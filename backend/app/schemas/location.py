"""Location schemas (Pydantic models)."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(warehouse|office|project_site|supplier|virtual)$")
    address: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|inactive)$")


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = Field(None, pattern="^(warehouse|office|project_site|supplier|virtual)$")
    address: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class LocationResponse(LocationBase):
    id: UUID
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
