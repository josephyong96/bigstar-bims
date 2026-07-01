"""User schemas (Pydantic models)."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="viewer", pattern="^(management|project_manager|sales|warehouse|technician|viewer)$")
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, pattern="^(management|project_manager|sales|warehouse|technician|viewer)$")
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponse(UserBase):
    id: UUID
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
