"""
TEMPORARY: Public testing router for demo purposes only.

This router provides unauthenticated endpoints for the EI testing module.
It bypasses authentication to allow public access for demonstration.

REMOVE THIS ROUTER before production deployment when real EI integration exists.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.participant import Participant
from app.models.team import Team
from app.schemas import testing as schemas

router = APIRouter()


@router.get("/teams", response_model=list[schemas.TeamBasic])
async def list_teams(db: AsyncSession = Depends(get_db)):
    """
    List all teams (public endpoint, no authentication required).

    TEMPORARY: For demo purposes only.
    """
    result = await db.execute(select(Team).order_by(Team.name))
    teams = result.scalars().all()
    return teams


@router.get("/teams/{team_id}/participants", response_model=list[schemas.ParticipantWithEI])
async def list_team_participants(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    List all participants for a specific team (public endpoint, no authentication required).

    TEMPORARY: For demo purposes only.
    """
    # Check if team exists
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    # Get participants
    result = await db.execute(
        select(Participant)
        .where(Participant.team_id == team_id)
        .order_by(Participant.name)
    )
    participants = result.scalars().all()
    return participants


@router.get("/participants/{participant_id}", response_model=schemas.ParticipantWithEI)
async def get_participant(
    participant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get participant details (public endpoint, no authentication required).

    Used to display participant name and check current EI score.

    TEMPORARY: For demo purposes only.
    """
    result = await db.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not found"
        )
    return participant


@router.put("/participants/{participant_id}/ei-score", response_model=schemas.ParticipantWithEI)
async def update_ei_score(
    participant_id: int,
    score_data: schemas.EIScoreUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update participant's emotional intelligence score (public endpoint, no authentication required).

    Only updates the emotional_intelligence field.

    TEMPORARY: For demo purposes only.
    """
    result = await db.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not found"
        )

    # Update only EI score
    participant.emotional_intelligence = score_data.ei_score

    await db.commit()
    await db.refresh(participant)
    return participant


@router.get("/participants/{participant_id}/si", response_model=schemas.ParticipantWithSI)
async def get_participant_si(
    participant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get participant details for SI testing (public endpoint, no authentication required).

    Used to display participant name and check current SI score.

    TEMPORARY: For demo purposes only.
    """
    result = await db.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not found"
        )
    return participant


@router.get("/teams/{team_id}/participants/si", response_model=list[schemas.ParticipantWithSI])
async def list_team_participants_si(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    List all participants for a specific team with SI data (public endpoint, no authentication required).

    TEMPORARY: For demo purposes only.
    """
    # Check if team exists
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found"
        )

    # Get participants
    result = await db.execute(
        select(Participant)
        .where(Participant.team_id == team_id)
        .order_by(Participant.name)
    )
    participants = result.scalars().all()
    return participants


@router.put("/participants/{participant_id}/si-score", response_model=schemas.ParticipantWithSI)
async def update_si_score(
    participant_id: int,
    score_data: schemas.SIScoreUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update participant's social intelligence score (public endpoint, no authentication required).

    Only updates the social_intelligence field.

    TEMPORARY: For demo purposes only.
    """
    result = await db.execute(
        select(Participant).where(Participant.id == participant_id)
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participant {participant_id} not found"
        )

    # Update only SI score
    participant.social_intelligence = score_data.si_score

    await db.commit()
    await db.refresh(participant)
    return participant
