"""
TEMPORARY: Testing module schemas for demo purposes only.
This module will be removed when real EI/SI integration is implemented.
"""

from pydantic import BaseModel, Field


class EIScoreUpdate(BaseModel):
    """Schema for updating participant EI score."""
    ei_score: int = Field(..., ge=0, le=100, description="Emotional intelligence score (0-100)")


class SIScoreUpdate(BaseModel):
    """Schema for updating participant SI score."""
    si_score: int = Field(..., ge=0, le=100, description="Social intelligence score (0-100)")


class ParticipantWithEI(BaseModel):
    """Participant data for EI testing module (minimal fields)."""
    id: int
    name: str
    email: str
    emotional_intelligence: int

    model_config = {"from_attributes": True}


class ParticipantWithSI(BaseModel):
    """Participant data for SI testing module (minimal fields)."""
    id: int
    name: str
    email: str
    social_intelligence: int

    model_config = {"from_attributes": True}


class TeamBasic(BaseModel):
    """Basic team info for testing module."""
    id: int
    name: str

    model_config = {"from_attributes": True}
