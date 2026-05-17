from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Health & Wellness Social PWA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./health_wellness.db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set[str] = {"jpg", "jpeg", "png", "gif", "webp"}
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
