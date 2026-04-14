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


settings = Settings()
