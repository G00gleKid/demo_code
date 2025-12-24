"""Assignments API router."""

from datetime import datetime, timedelta, timezone, date
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_team_id
from app.models.role_assignment import RoleAssignment
from app.models.participant import Participant
from app.models.meeting import Meeting
from app.schemas.role_assignment import RoleAssignment as RoleAssignmentSchema
from app.schemas.statistics import ParticipantStatistics, DailyRoleBreakdown

router = APIRouter()


@router.get("/participant/{participant_id}/history", response_model=list[RoleAssignmentSchema])
async def get_participant_role_history(
    participant_id: int,
    limit: int = 10,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Get role assignment history for a participant (only from current team)."""
    # Verify participant belongs to team
    stmt_participant = select(Participant).where(
        Participant.id == participant_id,
        Participant.team_id == team_id
    )
    result_participant = await db.execute(stmt_participant)
    participant = result_participant.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found in your team")

    stmt = (
        select(RoleAssignment)
        .where(RoleAssignment.participant_id == participant_id)
        .order_by(RoleAssignment.created_at.desc())
        .limit(limit)
    )
    result_query = await db.execute(stmt)
    assignments = result_query.scalars().all()

    # Add participant names
    result = []
    for assignment in assignments:
        result.append(
            RoleAssignmentSchema(
                id=assignment.id,
                meeting_id=assignment.meeting_id,
                participant_id=assignment.participant_id,
                role=assignment.role,
                fitness_score=assignment.fitness_score,
                created_at=assignment.created_at,
                participant_name=participant.name
            )
        )

    return result


@router.get("/participant/{participant_id}/statistics", response_model=ParticipantStatistics)
async def get_participant_statistics(
    participant_id: int,
    days: int = 7,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Get role assignment statistics for a participant over the last N days (only from current team)."""
    # Verify participant exists and belongs to team
    stmt_participant = select(Participant).where(
        Participant.id == participant_id,
        Participant.team_id == team_id
    )
    result_participant = await db.execute(stmt_participant)
    participant = result_participant.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found in your team")

    # Calculate date range
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    end_date = now

    # Query role assignments joined with meetings
    stmt = (
        select(RoleAssignment, Meeting)
        .join(Meeting, RoleAssignment.meeting_id == Meeting.id)
        .where(
            RoleAssignment.participant_id == participant_id,
            Meeting.scheduled_time >= start_date,
            Meeting.scheduled_time <= end_date
        )
        .order_by(Meeting.scheduled_time.asc())
    )
    result_query = await db.execute(stmt)
    assignments = result_query.all()

    # Calculate role distribution
    role_distribution = defaultdict(int)
    daily_data = defaultdict(lambda: defaultdict(int))

    for assignment, meeting in assignments:
        role_distribution[assignment.role] += 1
        meeting_date = meeting.scheduled_time.date()
        daily_data[meeting_date][assignment.role] += 1

    # Create daily breakdown for all days in the period (including empty days)
    daily_breakdown = []
    current_date = start_date.date()
    end_date_date = end_date.date()

    while current_date <= end_date_date:
        roles_on_date = dict(daily_data.get(current_date, {}))
        total_on_date = sum(roles_on_date.values())

        daily_breakdown.append(
            DailyRoleBreakdown(
                date=current_date,
                roles=roles_on_date,
                total=total_on_date
            )
        )
        current_date += timedelta(days=1)

    return ParticipantStatistics(
        participant_id=participant.id,
        participant_name=participant.name,
        period_days=days,
        start_date=start_date,
        end_date=end_date,
        total_meetings=len(assignments),
        role_distribution=dict(role_distribution),
        daily_breakdown=daily_breakdown
    )
