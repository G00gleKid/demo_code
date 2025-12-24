"""Authentication dependencies for route protection."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import verify_token
from app.services.user_service import get_user_by_email
from app.schemas.user import UserWithTeam

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserWithTeam:
    """
    Dependency to get current authenticated user from JWT token.

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: UserWithTeam = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    token = credentials.credentials

    # Verify and decode token
    payload = verify_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = await get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserWithTeam.model_validate(user)


async def get_current_team_id(current_user: UserWithTeam = Depends(get_current_user)) -> int:
    """
    Dependency to extract team_id from current user.

    Usage:
        @router.get("/participants")
        async def list_participants(team_id: int = Depends(get_current_team_id)):
            # Filter by team_id
            pass
    """
    return current_user.team_id
