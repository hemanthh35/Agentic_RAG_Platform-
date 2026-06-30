import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class.

    Loads environment variables from `.env` file and validates them.
    """

    API_TITLE: str = "Agentic RAG Platform API"
    API_DESCRIPTION: str = "Production-ready backend API for Agentic RAG Platform"
    API_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parses CORS origins from a comma-separated string to a list of strings."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database Configuration
    DATABASE_URL: str

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Document Configuration
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    SUPPORTED_DOCUMENT_TYPES: List[str] = [".pdf", ".docx", ".txt", ".md"]

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # Settings configurations
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instantiate settings for import across application
settings = Settings()
