from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    EMAIL_USERNAME: str = "your-email@example.com"
    EMAIL_PASSWORD: str = "your-email-password"
    EMAIL_FROM: str = "your-email@example.com"
    EMAIL_PORT: int = 587
    EMAIL_SERVER: str = "smtp.example.com"
    EMAIL_STARTTLS: bool = True  # Changed from EMAIL_TLS
    EMAIL_SSL_TLS: bool = False  # Changed from EMAIL_SSL

    class Config:
        env_file = ".env"

settings = Settings()