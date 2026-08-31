from __future__ import annotations

import re
from pathlib import Path

from backend.app.db import get_connection


MIGRATIONS_DIR = (
    Path(__file__).resolve().parent.parent / "migrations"
)

MIGRATION_PATTERN = re.compile(
    r"^(?P<number>\d+)_(?P<name>.+)\.sql$"
)


def _get_migration_files() -> list[tuple[int, Path]]:
    migrations: list[tuple[int, Path]] = []

    for path in MIGRATIONS_DIR.glob("*.sql"):
        match = MIGRATION_PATTERN.match(path.name)

        if match is None:
            continue

        migrations.append(
            (
                int(match.group("number")),
                path,
            )
        )

    migrations.sort(key=lambda item: item[0])

    return migrations


def _ensure_migration_table(cur) -> None:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )


def _get_applied_versions(cur) -> set[int]:
    cur.execute(
        """
        SELECT version
        FROM schema_migrations
        """
    )

    return {row[0] for row in cur.fetchall()}


def apply_migrations() -> list[str]:
    migrations = _get_migration_files()
    applied: list[str] = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            _ensure_migration_table(cur)

            applied_versions = _get_applied_versions(cur)

            for version, path in migrations:
                if version in applied_versions:
                    continue

                sql = path.read_text(
                    encoding="utf-8"
                )

                cur.execute(sql)

                cur.execute(
                    """
                    INSERT INTO schema_migrations (
                        version,
                        filename
                    )
                    VALUES (%s, %s)
                    """,
                    (
                        version,
                        path.name,
                    ),
                )

                applied.append(path.name)

        conn.commit()

    return applied


if __name__ == "__main__":
    applied = apply_migrations()

    if applied:
        print("Applied migrations:")

        for migration in applied:
            print(f"  {migration}")
    else:
        print("No pending migrations.")