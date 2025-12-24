"""Statistics schemas for participant role workload."""

from pydantic import BaseModel
from datetime import date, datetime


class DailyRoleBreakdown(BaseModel):
    """Daily breakdown of roles assigned to participant."""

    date: date
    roles: dict[str, int]  # role_name -> count
    total: int


class ParticipantStatistics(BaseModel):
    """Statistics for participant's role assignments over a time period."""

    participant_id: int
    participant_name: str
    period_days: int
    start_date: datetime
    end_date: datetime
    total_meetings: int
    role_distribution: dict[str, int]  # role_name -> total count
    daily_breakdown: list[DailyRoleBreakdown]
