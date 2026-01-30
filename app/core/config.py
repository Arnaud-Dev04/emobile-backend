from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Mobile API"
    API_V1_STR: str = "/api/v1"
    
    # Database - Railway provides DATABASE_URL directly
    DATABASE_URL: Optional[str] = None
    
    # Legacy Postgres config (for docker-compose)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "emobile"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 jours
    GOOGLE_CLIENT_ID: Optional[str] = None
    
    # Firebase Cloud Messaging
    FCM_SERVER_KEY: Optional[str] = None

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    def get_database_url(self) -> str:
        # Priority 1: DATABASE_URL from environment (Railway)
        if self.DATABASE_URL:
            # Railway uses postgres:// but SQLAlchemy needs postgresql://
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        
        # Priority 2: Use SQLite for local development
        return "sqlite:///./sql_app.db"

settings = Settings()

