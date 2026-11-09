from functools import lru_cache

from pydantic import EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TOOLSHOP_",
        env_file=".env",
        extra="ignore",
    )

    ui_base_url: str = "http://localhost:4200"
    api_base_url: str = "http://localhost:8091"
    headless: bool = True
    action_timeout_ms: int = Field(default=10_000, ge=1)
    navigation_timeout_ms: int = Field(default=30_000, ge=1)
    api_timeout_ms: int = Field(default=30_000, ge=1)
    api_max_attempts: int = Field(default=3, ge=1, le=5)
    api_retry_initial_delay_seconds: float = Field(default=0.2, gt=0)
    api_retry_max_delay_seconds: float = Field(default=2.0, gt=0)
    admin_email: EmailStr
    admin_password: SecretStr


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
