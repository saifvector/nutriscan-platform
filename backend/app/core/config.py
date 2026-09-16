from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Nutrient Deficiency Screening & Personalized Nutrition AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://nutrient_admin:nutrient_secure_password_2026@localhost:5432/nutrient_screening_db"
    DATABASE_ENGINE: str = "auto"  # "auto" (switches by ENVIRONMENT), "sqlite", "postgresql"
    MAX_POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: float = 30.0
    POOL_RECYCLE: int = 1800  # Recycle idle sockets after 30 mins

    # Redis configuration
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # JWT & Auth
    JWT_SECRET: str = "super_secret_jwt_key_phase1_screening_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Environment & Logging
    ENVIRONMENT: str = "development"  # "development", "staging", "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    # Automated Backups
    BACKUP_DIR: str = "data/backups"
    BACKUP_RETENTION_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ["production", "prod"]

    def get_effective_db_engine(self) -> str:
        """Determines active database engine based on configuration and environment."""
        if self.DATABASE_ENGINE.lower() in ["sqlite", "sqlite3"]:
            return "sqlite"
        if self.DATABASE_ENGINE.lower() in ["postgresql", "postgres"]:
            return "postgresql"
        # Auto mode: Production defaults to postgresql, Development defaults to sqlite
        return "postgresql" if self.is_production() else "sqlite"


settings = Settings()
