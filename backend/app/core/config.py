"""Application configuration using Pydantic Settings.

Reads from environment variables and .env file.
All configuration is centralized here for the entire application.
"""

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
    DATABASE_URL: str = (
        "postgresql://synapse:synapse@localhost:5432/synapse"
    )

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Default Provider (used when no specific model override is given)
    DEFAULT_PROVIDER: str = "gemini"

    # ── Provider API Keys ─────────────────────────────────
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    # ── Provider Model Overrides ──────────────────────────
    # Each provider has a default model; these env vars let you
    # switch to a different model without code changes.
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # OpenRouter uses full model paths (e.g. deepseek/deepseek-r1)
    OPENROUTER_MODEL: str = "deepseek/deepseek-r1"

    # Legacy OpenAI fallback
    OPENAI_MODEL: str = "gpt-4o-mini"


settings = Settings()

# Resolve the backend root directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
