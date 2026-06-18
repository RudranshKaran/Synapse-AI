"""Application configuration using Pydantic Settings.

Reads from environment variables and .env file.
All configuration is centralized here for the entire application.
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "Synapse AI"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql://synapse:synapse@localhost:5432/synapse"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM Providers
    DEFAULT_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"


settings = Settings()

# Resolve the backend root directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
