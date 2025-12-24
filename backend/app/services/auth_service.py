"""Authentication service for JWT token management."""

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config import settings


def create_access_token(data: dict) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload to encode (typically {"sub": user_email, "team_id": team_id})

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify password (plain text comparison for demo).

    SECURITY WARNING: Passwords are stored UNHASHED for demo purposes only.
    In production, use proper password hashing (bcrypt, argon2, etc.)
    """
    return plain_password == stored_password
