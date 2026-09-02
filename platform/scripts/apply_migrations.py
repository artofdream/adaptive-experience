"""
Idempotent PostgreSQL migration runner for Adaptive Experience Architecture.

Applies pending SQL migrations under platform/migrations/ in numerical sequence.
Supports --dry-run for non-destructive pre-deploy inspection.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
DSN = os.environ.get(
    "AEA_POSTGRES_DSN",
    "postgresql://aea_migration:local-migration-only@localhost:5432/adaptive_experience",
)


def run_migrations(dsn: str = DSN, dry_run: bool = False) -> list[str]:
    migrations = sorted((ROOT / "migrations").glob("[0-9][0-9][0-9]_*.sql"))
    applied_now: list[str] = []
    with psycopg.connect(dsn, autocommit=True) as connection:
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
                if dry_run:
                    print(f"[DRY-RUN] Pending migration: {migration.name}")
                    applied_now.append(migration.name)
                else:
                    connection.execute(migration.read_text(encoding="utf-8"))
                    print(f"applied {migration.name}")
                    applied_now.append(migration.name)
    return applied_now


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply platform SQL schema migrations")
    parser.add_argument("--dry-run", action="store_true", help="Print pending migrations without applying")
    parser.add_argument("--dsn", default=DSN, help="PostgreSQL connection DSN")
    args = parser.parse_args()

    try:
        pending_or_applied = run_migrations(dsn=args.dsn, dry_run=args.dry_run)
        if args.dry_run:
            print(f"[SUMMARY] {len(pending_or_applied)} pending migration(s)")
        else:
            print(f"[SUMMARY] {len(pending_or_applied)} migration(s) applied successfully")
    except Exception as e:
        print(f"Migration execution error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
