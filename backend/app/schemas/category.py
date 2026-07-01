"""Category schemas (Pydantic models)."""

from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True


class CategoryWithItemCount(CategoryResponse):
    item_count: int = 0
