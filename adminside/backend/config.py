"""
Admin Portal Backend Configuration
All settings are configurable via environment variables
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database - PostgreSQL connection string
    # For Supabase: postgresql://postgres.[project-ref]:[password]@[host]:5432/postgres
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/artpriv"
    
    # JWT Configuration - should match main application for token compatibility
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # App Configuration
    APP_NAME: str = "ArtPriv Admin Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS - comma-separated list of allowed origins
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    class Config:
        env_file = ".env"
        extra = "ignore"
        
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
