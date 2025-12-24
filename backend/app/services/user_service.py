"""User service for authentication operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.services.auth_service import verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email with team information loaded."""
    stmt = select(User).options(selectinload(User.team)).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Authenticate user with email and password.

    Returns:
        User object if authentication succeeds, None otherwise
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password):
        return None
    return user
