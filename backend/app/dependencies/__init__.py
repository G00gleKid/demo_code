"""Dependencies for dependency injection."""

from app.dependencies.auth import get_current_user, get_current_team_id

__all__ = ["get_current_user", "get_current_team_id"]
