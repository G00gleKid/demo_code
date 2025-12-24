from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ParticipantBase(BaseModel):
    """Base schema for participant data."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    chronotype: str = Field(..., pattern="^(morning|evening|intermediate)$")
    peak_hours_start: int = Field(..., ge=0, le=23)
    peak_hours_end: int = Field(..., ge=0, le=23)
    emotional_intelligence: int = Field(..., ge=0, le=100)
    social_intelligence: int = Field(..., ge=0, le=100)


class ParticipantCreate(ParticipantBase):
    """Schema for creating a new participant."""

    pass


class ParticipantUpdate(BaseModel):
    """Schema for updating a participant (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    chronotype: str | None = Field(None, pattern="^(morning|evening|intermediate)$")
    peak_hours_start: int | None = Field(None, ge=0, le=23)
    peak_hours_end: int | None = Field(None, ge=0, le=23)
    emotional_intelligence: int | None = Field(None, ge=0, le=100)
    social_intelligence: int | None = Field(None, ge=0, le=100)


class Participant(ParticipantBase):
    """Schema for participant response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
