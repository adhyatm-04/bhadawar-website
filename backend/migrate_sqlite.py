"""Copy local SQLite application data into the configured PostgreSQL database.

Run with ``python -m backend.migrate_sqlite --apply`` after configuring DATABASE_URL.
The command is intentionally opt-in, idempotent, and prints counts only.
"""
from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, MetaData
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.database import get_engine, upgrade_schema
from backend.runtime import DB_PATH


TABLES = (
    "menu_items",
    "corporate_menu",
    "wallet_accounts",
    "orders",
    "bookings",
    "food_stories",
    "wallet_transactions",
    "reviews",
    "customer_accounts",
    "delivery_riders",
)


def _sqlite_value(value, column):
    if value is None or not isinstance(column.type, DateTime) or isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return value


def migrate(source_path: Path, apply_changes: bool) -> dict[str, int]:
    if not source_path.is_file():
        raise FileNotFoundError(f"SQLite source database was not found: {source_path}")
    if not apply_changes:
        raise RuntimeError("This command only runs with --apply; no data was copied.")

    engine = get_engine()
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Set DATABASE_URL to the target PostgreSQL database before migrating.")
    upgrade_schema()
    target_metadata = MetaData()
    target_metadata.reflect(bind=engine, only=TABLES)
    counts: dict[str, int] = {}

    with sqlite3.connect(str(source_path)) as source:
        source.row_factory = sqlite3.Row
        existing = {row[0] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        with engine.begin() as destination:
            for table_name in TABLES:
                if table_name not in existing or table_name not in target_metadata.tables:
                    counts[table_name] = 0
                    continue
                table = target_metadata.tables[table_name]
                target_columns = {column.name: column for column in table.columns}
                source_cursor = source.execute(f'SELECT * FROM "{table_name}"')
                inserted = 0
                while rows := source_cursor.fetchmany(500):
                    batch = []
                    for source_row in rows:
                        values = {
                            key: _sqlite_value(source_row[key], target_columns[key])
                            for key in source_row.keys() if key in target_columns
                        }
                        batch.append(values)
                    if batch:
                        result = destination.execute(
                            pg_insert(table).values(batch).on_conflict_do_nothing()
                        )
                        inserted += max(0, result.rowcount or 0)
                counts[table_name] = inserted

            for table_name in ("wallet_transactions", "reviews"):
                table = target_metadata.tables[table_name]
                if "id" not in table.c:
                    continue
                destination.exec_driver_sql(
                    f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table_name}), 1), "
                    f"EXISTS(SELECT 1 FROM {table_name}))"
                )
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy Bhadawar SQLite data into PostgreSQL.")
    parser.add_argument("--source", type=Path, default=Path(DB_PATH), help="SQLite database path (default: local app database).")
    parser.add_argument("--apply", action="store_true", help="Confirm and run the idempotent import.")
    args = parser.parse_args()
    counts = migrate(args.source.resolve(), args.apply)
    print("Rows inserted by table:")
    for name, count in counts.items():
        print(f"  {name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
