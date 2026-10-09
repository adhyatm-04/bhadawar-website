"""SQLAlchemy engine, session, model serialization, and migration helpers."""
from __future__ import annotations

import os
import threading
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session, sessionmaker


ROOT = Path(__file__).resolve().parents[1]
_engine = None
_engine_lock = threading.Lock()
_session_factory = None


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL mode.")
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def get_engine():
    """Return the shared PostgreSQL or local SQLite SQLAlchemy engine."""
    global _engine, _session_factory
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url:
        url = _database_url()
    else:
        path = Path(os.environ.get("BHADAWAR_DB_PATH", str(ROOT / "bhadawar.db"))).resolve()
        url = "sqlite:///" + path.as_posix()

    with _engine_lock:
        if _engine is None:
            if url.startswith("sqlite:"):
                _engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})

                @event.listens_for(_engine, "connect")
                def _configure_sqlite(dbapi_connection, _connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys = ON")
                    cursor.execute("PRAGMA busy_timeout = 30000")
                    cursor.execute("PRAGMA journal_mode = WAL")
                    cursor.close()
            else:
                _engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)
            _session_factory = sessionmaker(bind=_engine, class_=Session, expire_on_commit=False)
        return _engine


def connect_session() -> Session:
    get_engine()
    return _session_factory()


def lock_transaction(session: Session) -> None:
    """Serialize multi-row writes while domain workflows gain narrower locks."""
    if os.environ.get("DATABASE_URL", "").strip():
        session.execute(select(func.pg_advisory_xact_lock(736491020261009)))
    else:
        session.connection().exec_driver_sql("BEGIN IMMEDIATE")


def model_to_dict(record):
    """Convert an ORM model to the JSON field shape used by the browser UI."""
    if record is None:
        return None
    from sqlalchemy import inspect

    values = {}
    for attribute in inspect(record).mapper.column_attrs:
        value = getattr(record, attribute.key)
        if isinstance(value, datetime):
            value = value.isoformat(sep=" ", timespec="seconds")
        values[attribute.key] = value
    return values


def upgrade_schema():
    from alembic import command
    from alembic.config import Config

    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "backend" / "migrations"))
    config.set_main_option("sqlalchemy.url", _database_url().replace("%", "%%"))
    command.upgrade(config, "head")
