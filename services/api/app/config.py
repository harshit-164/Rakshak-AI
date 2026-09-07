from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Secret fields are never serialized by API routes."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Safeguard AI API"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    public_demo_only: bool = True
    engine_mode: Literal["hosted_baseline", "encoder", "qwen_adapter"] = "hosted_baseline"
    gemini_api_key: str | None = Field(default=None, repr=False)
    gemini_model_id: str = "gemini-2.5-flash"
    supabase_url: str | None = None
    supabase_anon_key: str | None = Field(default=None, repr=False)
    supabase_service_role_key: str | None = Field(default=None, repr=False)
    auth_issuer: str | None = None
    auth_audience: str = "authenticated"
    allowed_origins: str = "http://localhost:3000"
    enable_explicit_fallback: bool = False

    @property
    def provider_configured(self) -> bool:
        return self.engine_mode == "hosted_baseline" and bool(self.gemini_api_key)

    @property
    def database_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def worker_configured(self) -> bool:
        return bool(
            self.database_configured
            and self.supabase_service_role_key
            and self.provider_configured
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
