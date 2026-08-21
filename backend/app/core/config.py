"""
NIVAG AI Business Automation
Application Configuration

Production configuration layer.

All runtime configuration is loaded from environment variables.
No secrets are hardcoded in application source code.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from environment variables and, for local
    development, from the backend .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = Field(
        default="NIVAG AI Business Automation",
        validation_alias="APP_NAME",
    )

    app_version: str = Field(
        default="1.0.0",
        validation_alias="APP_VERSION",
    )

    environment: str = Field(
        default="development",
        validation_alias="ENVIRONMENT",
    )

    debug: bool = Field(
        default=False,
        validation_alias="DEBUG",
    )

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    api_v1_prefix: str = Field(
        default="/api/v1",
        validation_alias="API_V1_PREFIX",
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/nivag_business_automation",
        validation_alias="DATABASE_URL",
    )

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    jwt_secret_key: str = Field(
        default="",
        validation_alias="JWT_SECRET_KEY",
    )

    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias="JWT_ALGORITHM",
    )

    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
        ge=1,
    )

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        validation_alias="CORS_ORIGINS",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a normalized list."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the process-wide cached settings instance.
    """
    return Settings()


settings = get_settings()