"""Authentication API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import user as schemas
from app.services.user_service import authenticate_user
from app.services.auth_service import create_access_token
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
async def login(credentials: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    - **email**: User email
    - **password**: User password (plain text for demo)

    Returns JWT token valid for 24 hours.
    """
    user = await authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.email, "team_id": user.team_id}
    )

    return schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserWithTeam.model_validate(user)
    )


@router.get("/me", response_model=schemas.UserWithTeam)
async def get_current_user_info(current_user: schemas.UserWithTeam = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user


@router.post("/logout")
async def logout():
    """
    Logout endpoint (stateless JWT - client should discard token).

    Note: With JWT tokens, logout is handled client-side by removing the token.
    This endpoint exists for API consistency and could be extended with token blacklisting.
    """
    return {"message": "Successfully logged out. Please discard your token."}
