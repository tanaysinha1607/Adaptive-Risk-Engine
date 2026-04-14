from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.core.config import settings

Base = declarative_base()

_is_supabase_pooler = "pooler.supabase.com" in settings.database_url
_is_psycopg2 = "+psycopg2://" in settings.database_url
_is_psycopg3 = "+psycopg://" in settings.database_url

# Supabase poolers (and many proxies) can break psycopg3 prepared statements and
# also interact badly with connection reuse + pre-ping.
#
# For pooler URLs we prefer stability over throughput:
# - disable prepared statements
# - disable pre-ping
# - avoid connection reuse (NullPool)
engine_kwargs: dict = {
    "pool_pre_ping": not _is_supabase_pooler,
}

if _is_supabase_pooler:
    engine_kwargs["poolclass"] = NullPool

# Only psycopg3 supports prepare_threshold; psycopg2 will error on unknown args.
if _is_psycopg3 and not _is_psycopg2:
    engine_kwargs["connect_args"] = {"prepare_threshold": 0}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    # Import models for metadata registration
    from backend.db import base as _base  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
