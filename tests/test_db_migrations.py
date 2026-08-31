from pathlib import Path

from backend.app.db_migrations import (
    _get_migration_files,
)


def test_migration_files_are_sorted_and_unique():
    migrations = _get_migration_files()

    versions = [version for version, _ in migrations]
    paths = [path for _, path in migrations]

    assert versions == sorted(versions)
    assert len(versions) == len(set(versions))

    for path in paths:
        assert isinstance(path, Path)
        assert path.suffix == ".sql"