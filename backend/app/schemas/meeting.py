from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.participant import Participant


class MeetingBase(BaseModel):
    """Base schema for meeting data."""

    title: str = Field(..., min_length=1, max_length=200)
    meeting_type: str = Field(..., pattern="^(brainstorm|review|planning|status_update)$")
    scheduled_time: datetime


class MeetingCreate(MeetingBase):
    """Schema for creating a new meeting."""

    participant_ids: list[int] = Field(default_factory=list, description="List of participant IDs")


class MeetingUpdate(BaseModel):
    """Schema for updating a meeting (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=200)
    meeting_type: str | None = Field(None, pattern="^(brainstorm|review|planning|status_update)$")
    scheduled_time: datetime | None = None


class Meeting(MeetingBase):
    """Schema for meeting response."""

    id: int
    created_at: datetime
    participants: list[Participant] = []

    model_config = {"from_attributes": True}


class MeetingList(MeetingBase):
    """Schema for meeting list (without full participant data)."""

    id: int
    created_at: datetime
    participant_count: int = 0

    model_config = {"from_attributes": True}
