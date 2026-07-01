"""Application configuration settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Bigstar Inventory Management System"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://bigstar:bigstar123@localhost:5432/bigstar_inventory"

    # Security
    secret_key: str = "bigstar-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours

    # CORS
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
