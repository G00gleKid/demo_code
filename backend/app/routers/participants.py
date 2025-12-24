"""Participants API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_team_id
from app.models.participant import Participant
from app.schemas import participant as schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.Participant])
async def list_participants(
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """List all participants for the current team."""
    result = await db.execute(
        select(Participant).where(Participant.team_id == team_id)
    )
    return result.scalars().all()


@router.post("/", response_model=schemas.Participant, status_code=status.HTTP_201_CREATED)
async def create_participant(
    participant_data: schemas.ParticipantCreate,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new participant for the current team."""
    # Check if email already exists in this team
    stmt = select(Participant).where(
        Participant.email == participant_data.email,
        Participant.team_id == team_id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Participant with email {participant_data.email} already exists in your team"
        )

    participant = Participant(**participant_data.model_dump(), team_id=team_id)
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant


@router.get("/{participant_id}", response_model=schemas.Participant)
async def get_participant(
    participant_id: int,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Get participant by ID (only from current team)."""
    stmt = select(Participant).where(
        Participant.id == participant_id,
        Participant.team_id == team_id
    )
    result = await db.execute(stmt)
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not found in your team"
        )
    return participant


@router.put("/{participant_id}", response_model=schemas.Participant)
async def update_participant(
    participant_id: int,
    participant_data: schemas.ParticipantUpdate,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Update participant (only from current team)."""
    stmt = select(Participant).where(
        Participant.id == participant_id,
        Participant.team_id == team_id
    )
    result = await db.execute(stmt)
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not found in your team"
        )

    # Update only provided fields
    update_data = participant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(participant, field, value)

    await db.commit()
    await db.refresh(participant)
    return participant


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participant(
    participant_id: int,
    team_id: int = Depends(get_current_team_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete participant (only from current team)."""
    stmt = select(Participant).where(
        Participant.id == participant_id,
        Participant.team_id == team_id
    )
    result = await db.execute(stmt)
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not found in your team"
        )

    await db.delete(participant)
    await db.commit()
    return None
