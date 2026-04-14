from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
        default="postgresql+psycopg://postgres:postgres@localhost:5432/adaptive_risk",
        description="SQLAlchemy URL for Postgres",
    )
    enable_simulator: bool = Field(
        validation_alias=AliasChoices("ENABLE_SIMULATOR", "enable_simulator"),
        default=False,
        description="Enable background trade simulator",
    )


def _normalize_sqlalchemy_url(url: str) -> str:
    # If user provides a plain Postgres URL, pick a sane default driver.
    #
    # Supabase pooler (PgBouncer) + psycopg3 can intermittently hit `_pg3_*`
    # prepared-statement errors. For pooler URLs, prefer psycopg2.
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        rest = url.split("://", 1)[1]
        if "pooler.supabase.com" in url:
            return "postgresql+psycopg2://" + rest
        return "postgresql+psycopg://" + rest
    return url


settings = Settings()
settings.database_url = _normalize_sqlalchemy_url(settings.database_url)
