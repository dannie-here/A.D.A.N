"""Application configuration management for A.D.A.N.

Uses pydantic-settings when available, with a standard os.getenv fallback.
"""

import os
from typing import List

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        """Application configuration settings loaded from environment variables."""

        APP_NAME: str = "A.D.A.N. API"
        APP_VERSION: str = "0.1.0"
        APP_DESCRIPTION: str = (
            "AI Data Analysis & Verification Network - PS08: Proof-Carrying Data Analyst"
        )
        ENVIRONMENT: str = "development"
        DEBUG: bool = True
        HOST: str = "0.0.0.0"
        PORT: int = 8000
        CORS_ORIGINS: List[str] = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ]

        # Dataset storage configuration (Phase 2)
        DATA_DIR: str = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
        )
        MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB

        # Future Phase placeholders (no active keys or calls in Phase 1)
        LLM_PROVIDER: str = "placeholder"
        LLM_API_KEY: str = ""

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

    settings = Settings()

except ImportError:
    # Lightweight fallback for minimal environments without pydantic-settings installed
    class FallbackSettings:
        APP_NAME: str = os.getenv("APP_NAME", "A.D.A.N. API")
        APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
        APP_DESCRIPTION: str = os.getenv(
            "APP_DESCRIPTION",
            "AI Data Analysis & Verification Network - PS08: Proof-Carrying Data Analyst",
        )
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
        HOST: str = os.getenv("HOST", "0.0.0.0")
        PORT: int = int(os.getenv("PORT", "8000"))
        CORS_ORIGINS: List[str] = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
            ).split(",")
            if origin.strip()
        ]
        DATA_DIR: str = os.getenv(
            "DATA_DIR",
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
            ),
        )
        MAX_UPLOAD_SIZE_BYTES: int = int(
            os.getenv("MAX_UPLOAD_SIZE_BYTES", str(50 * 1024 * 1024))
        )
        LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "placeholder")
        LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")

    settings = FallbackSettings()  # type: ignore

# Ensure the upload data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)

