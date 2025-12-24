"""Meetings API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies.auth import get_current_team_id
from app.models.meeting import Meeting
from app.models.participant import Participant
from app.models.role_assignment import RoleAssignment
from app.schemas import meeting as schemas
from app.schemas.role_assignment import RoleAssignment as RoleAssignmentSchema, RoleAssignmentResult
from app.services.assignment_engine import assign_roles

router = APIRouter()


@router.get("/", response_model=list[schemas.Meeting])
async def list_meetings(
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """List all meetings for the current team."""
    result = await db.execute(
        select(Meeting)
        .where(Meeting.team_id == team_id)
        .options(selectinload(Meeting.participants))
    )
    return result.scalars().all()


@router.post("/", response_model=schemas.Meeting, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: schemas.MeetingCreate,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new meeting with participants for the current team."""
    # Create meeting
    meeting = Meeting(
        title=meeting_data.title,
        meeting_type=meeting_data.meeting_type,
        scheduled_time=meeting_data.scheduled_time,
        team_id=team_id
    )

    # Add participants (only from the same team)
    if meeting_data.participant_ids:
        stmt = select(Participant).where(
            Participant.id.in_(meeting_data.participant_ids),
            Participant.team_id == team_id
        )
        result = await db.execute(stmt)
        participants = result.scalars().all()

        if len(participants) != len(meeting_data.participant_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some participants do not belong to your team"
            )

        meeting.participants = list(participants)

    db.add(meeting)
    await db.commit()
    await db.refresh(meeting, ["participants"])
    return meeting


@router.get("/{meeting_id}", response_model=schemas.Meeting)
async def get_meeting(
    meeting_id: int,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Get meeting by ID (only from current team)."""
    stmt = select(Meeting).options(selectinload(Meeting.participants)).where(
        Meeting.id == meeting_id,
        Meeting.team_id == team_id
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found in your team"
        )
    return meeting


@router.put("/{meeting_id}", response_model=schemas.Meeting)
async def update_meeting(
    meeting_id: int,
    meeting_data: schemas.MeetingUpdate,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Update meeting (only from current team)."""
    stmt = select(Meeting).options(selectinload(Meeting.participants)).where(
        Meeting.id == meeting_id,
        Meeting.team_id == team_id
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found in your team"
        )

    # Update only provided fields
    update_data = meeting_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)

    await db.commit()
    await db.refresh(meeting, ["participants"])
    return meeting


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete meeting (only from current team)."""
    stmt = select(Meeting).where(
        Meeting.id == meeting_id,
        Meeting.team_id == team_id
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found in your team"
        )

    await db.delete(meeting)
    await db.commit()
    return None


@router.post("/{meeting_id}/participants")
async def add_participants(
    meeting_id: int,
    participant_ids: list[int],
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Add participants to meeting (only from current team)."""
    stmt = select(Meeting).options(selectinload(Meeting.participants)).where(
        Meeting.id == meeting_id,
        Meeting.team_id == team_id
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found in your team"
        )

    # Verify participants belong to the same team
    stmt_participants = select(Participant).where(
        Participant.id.in_(participant_ids),
        Participant.team_id == team_id
    )
    result_participants = await db.execute(stmt_participants)
    participants = result_participants.scalars().all()
    if len(participants) != len(participant_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some participants do not belong to your team"
        )

    # Add new participants (avoid duplicates)
    for participant in participants:
        if participant not in meeting.participants:
            meeting.participants.append(participant)

    await db.commit()
    return {"message": f"Added {len(participants)} participants"}


@router.delete("/{meeting_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(
    meeting_id: int,
    participant_id: int,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Remove participant from meeting (only from current team)."""
    stmt = select(Meeting).options(selectinload(Meeting.participants)).where(
        Meeting.id == meeting_id,
        Meeting.team_id == team_id
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found in your team"
        )

    stmt_participant = select(Participant).where(
        Participant.id == participant_id,
        Participant.team_id == team_id
    )
    result_participant = await db.execute(stmt_participant)
    participant = result_participant.scalar_one_or_none()
    if not participant or participant not in meeting.participants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not in meeting"
        )

    meeting.participants.remove(participant)
    await db.commit()
    return None


@router.post("/{meeting_id}/assign-roles", response_model=RoleAssignmentResult)
async def assign_meeting_roles(
    meeting_id: int,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign roles to participants for this meeting (only from current team).

    Runs the role distribution algorithm and stores results.
    """
    # Verify meeting belongs to team
    stmt_meeting = select(Meeting).where(
        Meeting.id == meeting_id,
        Meeting.team_id == team_id
    )
    result_meeting = await db.execute(stmt_meeting)
    meeting = result_meeting.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found in your team"
        )

    try:
        assignments = await assign_roles(db, meeting_id)

        # Build response with participant names
        result_assignments = []
        for assignment in assignments:
            stmt = select(Participant).where(Participant.id == assignment.participant_id)
            result = await db.execute(stmt)
            participant = result.scalar_one_or_none()
            result_assignments.append(
                RoleAssignmentSchema(
                    id=assignment.id,
                    meeting_id=assignment.meeting_id,
                    participant_id=assignment.participant_id,
                    role=assignment.role,
                    fitness_score=assignment.fitness_score,
                    created_at=assignment.created_at,
                    participant_name=participant.name if participant else None
                )
            )

        return RoleAssignmentResult(
            meeting_id=meeting_id,
            assignments=result_assignments,
            total_assigned=len(result_assignments)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{meeting_id}/assignments", response_model=list[RoleAssignmentSchema])
async def get_meeting_assignments(
    meeting_id: int,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Get role assignments for a meeting (only from current team)."""
    # Verify meeting belongs to team
    stmt_meeting = select(Meeting).where(
        Meeting.id == meeting_id,
        Meeting.team_id == team_id
    )
    result_meeting = await db.execute(stmt_meeting)
    meeting = result_meeting.scalar_one_or_none()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting {meeting_id} not found in your team"
        )

    stmt = select(RoleAssignment).where(RoleAssignment.meeting_id == meeting_id)
    result_query = await db.execute(stmt)
    assignments = result_query.scalars().all()

    # Add participant names
    result = []
    for assignment in assignments:
        stmt_participant = select(Participant).where(Participant.id == assignment.participant_id)
        result_participant = await db.execute(stmt_participant)
        participant = result_participant.scalar_one_or_none()
        result.append(
            RoleAssignmentSchema(
                id=assignment.id,
                meeting_id=assignment.meeting_id,
                participant_id=assignment.participant_id,
                role=assignment.role,
                fitness_score=assignment.fitness_score,
                created_at=assignment.created_at,
                participant_name=participant.name if participant else None
            )
        )

    return result
