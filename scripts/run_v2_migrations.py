#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from pathlib import Path


def apply_migrations(db_path: Path, migrations_dir: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              version TEXT PRIMARY KEY,
              applied_at INTEGER NOT NULL
            )
            """
        )
        applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
        for path in sorted(migrations_dir.glob("*.sql")):
            version = path.name
            if version in applied:
                continue
            sql = path.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.execute("INSERT INTO schema_migrations(version, applied_at) VALUES(?, strftime('%s','now'))", (version,))
            conn.commit()
            print(f"applied: {version}")
    finally:
        conn.close()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    db_path = root / "data" / "work_mgmt_v2.db"
    migrations_dir = root / "db" / "migrations"
    if not migrations_dir.exists():
        raise SystemExit(f"migrations directory missing: {migrations_dir}")
    apply_migrations(db_path, migrations_dir)
    print(f"database ready: {db_path}")


if __name__ == "__main__":
    main()
