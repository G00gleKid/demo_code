"""Team schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    """Base schema for team data."""

    name: str = Field(..., min_length=1, max_length=200)


class TeamCreate(TeamBase):
    """Schema for creating a team."""

    pass


class Team(TeamBase):
    """Schema for team response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
