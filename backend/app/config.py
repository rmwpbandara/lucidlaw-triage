"""Application configuration.

All settings are read from the environment (or a local ``.env`` file) so the
service follows the twelve-factor app principle of strict config/code separation.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the triage service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Anthropic ---------------------------------------------------------
    # Optional so the app can still boot to serve /health and /docs without a
    # key. The engine validates its presence at call time and returns a clean
    # 503 if it is missing, rather than crashing on startup.
    anthropic_api_key: str | None = None
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 1024
    request_timeout_seconds: float = 30.0
    brand_voice_retries: int = 1

    # --- Service -----------------------------------------------------------
    app_name: str = "LucidLaw Triage API"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read the environment once)."""
    return Settings()
