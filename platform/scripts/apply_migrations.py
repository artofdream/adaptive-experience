from __future__ import annotations

import os
from pathlib import Path

import psycopg


ROOT = Path(__file__).resolve().parents[1]
DSN = os.environ.get(
    "AEA_POSTGRES_DSN",
    "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience",
)


def main() -> None:
    migrations = sorted((ROOT / "migrations").glob("[0-9][0-9][0-9]_*.sql"))
    with psycopg.connect(DSN, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('orchestration.schema_migration')")
            initialized = cursor.fetchone()[0] is not None
            applied: set[int] = set()
            if initialized:
                cursor.execute("SELECT version FROM orchestration.schema_migration")
                applied = {row[0] for row in cursor.fetchall()}
        for migration in migrations:
            version = int(migration.name[:3])
            if version not in applied:
                connection.execute(migration.read_text(encoding="utf-8"))
                print(f"applied {migration.name}")


if __name__ == "__main__":
    main()

