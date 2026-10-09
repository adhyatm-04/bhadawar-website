"""SQLAlchemy-backed PostgreSQL connection and migration helpers."""
from __future__ import annotations

import os
import threading
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text


ROOT = Path(__file__).resolve().parents[1]
_engine = None
_engine_lock = threading.Lock()


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL mode.")
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def get_engine():
    global _engine
    url = _database_url()
    with _engine_lock:
        if _engine is None:
            _engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)
        return _engine


def _named_parameters(sql: str, parameters=()):
    """Translate the existing qmark SQL to SQLAlchemy text bind parameters."""
    values = parameters or ()
    if isinstance(values, Mapping):
        return sql, dict(values)
    bind_names = []
    output = []
    quote = None
    i = 0
    while i < len(sql):
        char = sql[i]
        if quote:
            output.append(char)
            if char == quote:
                if i + 1 < len(sql) and sql[i + 1] == quote:
                    output.append(sql[i + 1])
                    i += 1
                else:
                    quote = None
        elif char in ("'", '"'):
            quote = char
            output.append(char)
        elif char == "?":
            name = f"p{len(bind_names)}"
            bind_names.append(name)
            output.append(f":{name}")
        else:
            output.append(char)
        i += 1
    if len(bind_names) != len(values):
        if not bind_names and not values:
            return sql, {}
        raise ValueError(f"SQL placeholder count {len(bind_names)} does not match parameter count {len(values)}.")
    return "".join(output), dict(zip(bind_names, values))


class HybridRow(Mapping):
    """A result row that preserves sqlite3.Row string and numeric indexing."""

    def __init__(self, names, values):
        self._names = tuple(names)
        self._values = tuple(
            value.isoformat(sep=" ", timespec="seconds") if isinstance(value, datetime) else value
            for value in values
        )
        self._mapping = dict(zip(self._names, self._values))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._mapping[key]

    def __iter__(self):
        return iter(self._names)

    def __len__(self):
        return len(self._names)

    def keys(self):
        return self._names


class CursorAdapter:
    def __init__(self, connection):
        self.connection = connection
        self.result = None
        self.columns = ()

    def execute(self, sql, parameters=()):
        raw_sql = str(sql).strip()
        if raw_sql.upper() == "BEGIN IMMEDIATE":
            # SQLite used this to reserve the writer lock before order, rider,
            # and payment state transitions. A transaction-scoped advisory lock
            # preserves that serialization on PostgreSQL until those operations
            # use narrower row locks.
            result = self.connection.execute(text("SELECT pg_advisory_xact_lock(736491020261009)"))
            result.close()
            self.result = None
            self.columns = ()
            return self
        sql, values = _named_parameters(raw_sql, parameters)
        self.result = self.connection.execute(text(sql), values)
        self.columns = tuple(self.result.keys())
        return self

    def executemany(self, sql, parameters):
        rows = list(parameters)
        if not rows:
            return self.execute(sql, ())
        first = rows[0]
        values_for_template = tuple(None for _ in first) if not isinstance(first, Mapping) else first
        sql, _ = _named_parameters(str(sql), values_for_template)
        batch = []
        for values in rows:
            if isinstance(values, Mapping):
                batch.append(dict(values))
            else:
                if len(values) != len(values_for_template):
                    raise ValueError("SQL placeholder count does not match executemany parameter count.")
                batch.append({f"p{i}": value for i, value in enumerate(values)})
        self.result = self.connection.execute(text(sql), batch)
        self.columns = tuple(self.result.keys())
        return self

    def _row(self, row):
        return HybridRow(self.columns, row) if row is not None else None

    def fetchone(self):
        return self._row(self.result.fetchone()) if self.result is not None else None

    def fetchall(self):
        return [self._row(row) for row in self.result.fetchall()] if self.result is not None else []

    @property
    def rowcount(self):
        return self.result.rowcount if self.result is not None else -1

    @property
    def lastrowid(self):
        return None

    def close(self):
        if self.result is not None:
            self.result.close()


class ConnectionAdapter:
    def __init__(self):
        self.connection = get_engine().connect()

    def execute(self, sql, parameters=()):
        return CursorAdapter(self.connection).execute(sql, parameters)

    def cursor(self):
        return CursorAdapter(self.connection)

    def commit(self):
        if self.connection.in_transaction():
            self.connection.commit()

    def rollback(self):
        if self.connection.in_transaction():
            self.connection.rollback()

    def close(self):
        self.connection.close()


def connect_database():
    return ConnectionAdapter()


def upgrade_schema():
    from alembic import command
    from alembic.config import Config

    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "backend" / "migrations"))
    config.set_main_option("sqlalchemy.url", _database_url().replace("%", "%%"))
    command.upgrade(config, "head")
