from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = Field(default="postgresql://nikitamelnikovr:postgres@localhost:5432/test_roles")
    # CORS_ORIGINS: list[str] = Field(default=["http://localhost:5173"])

    # Auth settings
    SECRET_KEY: str = Field(default="demo-secret-key-change-in-production-min-32-chars-long")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_HOURS: int = Field(default=24)

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        case_sensitive=False
    )


settings = Settings()
