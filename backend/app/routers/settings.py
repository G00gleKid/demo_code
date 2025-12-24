"""API endpoints for algorithm settings."""
from fastapi import APIRouter
from ..constants.roles import ROLE_REQUIREMENTS
from ..constants.meeting_types import MEETING_MULTIPLIERS

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/role-requirements")
async def get_role_requirements():
    """Get role requirements matrix."""
    return ROLE_REQUIREMENTS


@router.get("/meeting-multipliers")
async def get_meeting_multipliers():
    """Get meeting type multipliers."""
    return MEETING_MULTIPLIERS
