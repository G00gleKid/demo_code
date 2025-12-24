"""User schemas for authentication and authorization."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.schemas.team import Team


class UserBase(BaseModel):
    """Base schema for user data."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=1)
    team_id: int


class UserLogin(BaseModel):
    """Schema for login request."""

    email: EmailStr
    password: str


class User(UserBase):
    """Schema for user response (without password)."""

    id: int
    team_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserWithTeam(User):
    """Schema for user response with team information."""

    team: Team

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for login response with JWT token."""

    access_token: str
    token_type: str = "bearer"
    user: UserWithTeam
