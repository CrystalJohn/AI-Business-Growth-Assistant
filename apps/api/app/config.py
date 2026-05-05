from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql://admin:password@localhost:5432/bizgrowth"
    llm_provider: str = "mock"
    cors_origins_raw: str = "http://localhost:3000"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    pii_masking_key: str = "change-me-masking-key"

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_aliases={"cors_origins_raw": "CORS_ORIGINS"}
    )

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
