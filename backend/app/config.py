"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def to_sync_database_url(url: str) -> str:
    """Convert an async SQLAlchemy URL to a sync psycopg URL for Alembic."""
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql+asyncpg://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    """Runtime settings for the Behavioral Monitor backend.

    Values are loaded from environment variables (and optional `.env`):
    `APP_NAME`, `DEBUG`, `HOST`, `PORT`, `DATABASE_URL`,
    `ARTIFACTS_DIR`, `BOOTSTRAP_ADMIN_TOKEN`.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Behavioral Monitor API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8765
    database_url: str = (
        "postgresql+asyncpg://behavioral:behavioral@localhost:5432/behavioral_monitor"
    )
    artifacts_dir: str = "artifacts"
    bootstrap_admin_token: str = ""

    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL URL used by Alembic migrations."""
        return to_sync_database_url(self.database_url)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
