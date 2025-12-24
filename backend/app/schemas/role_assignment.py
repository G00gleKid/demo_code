from datetime import datetime
from pydantic import BaseModel


class RoleAssignmentBase(BaseModel):
    """Base schema for role assignment data."""

    meeting_id: int
    participant_id: int
    role: str
    fitness_score: float


class RoleAssignment(RoleAssignmentBase):
    """Schema for role assignment response."""

    id: int
    created_at: datetime
    participant_name: str | None = None

    model_config = {"from_attributes": True}


class RoleAssignmentResult(BaseModel):
    """Schema for assignment algorithm result."""

    meeting_id: int
    assignments: list[RoleAssignment]
    total_assigned: int
