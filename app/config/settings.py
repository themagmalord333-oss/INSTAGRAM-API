from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_ENV: str = "development"
    PROJECT_NAME: str = "InstaData Public Backend"
    
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "instadata_prod"
    REDIS_URI: str = "redis://localhost:6379"
    
    FAST_CACHE_TTL: int = 72000      # 20 hours
    STALE_CACHE_TTL: int = 86400     # 24 hours
    MAX_REQUEST_SIZE: int = 2048     # 2KB
    
    SENTRY_DSN: str | None = None
    ADMIN_API_KEY: str = "super-secret-admin-key"

    # Pydantic v2 automatically loads variables from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()