from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "ArtPriv"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB (for PDFs)
    
    # Supabase Storage Buckets
    BUCKET_CERTIFICATIONS: str = "certification-documents"
    BUCKET_CONSENT_FORMS: str = "consent-forms"
    BUCKET_TEST_REPORTS: str = "test-reports"
    BUCKET_COUNSELING_REPORTS: str = "counseling-reports"
    
    class Config:
        env_file = ".env"
        
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
