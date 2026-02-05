#!/usr/bin/env python3
"""Run Alembic migrations safely in dev/prod.

This helper checks the target database for existing tables and automatically
stamps the head revision if the schema already exists but is not tracked by
Alembic (i.e. "alembic_version" table absent). Otherwise it runs normal
`alembic upgrade head`.

It supports providing a temporary DB URL with `--db-url`.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

# Ensure the app package is importable
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import settings
from app.database import sanitize_db_url


CORE_TABLES: List[str] = [
    "users",
    "members",
    "messages",
    "templates",
]


def run_alembic_command(cmd: List[str], env: dict | None = None) -> int:
    env = env or os.environ.copy()
    # Ensure DB_URL is available to alembic via env
    return subprocess.run(cmd, env=env).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe Alembic runner")
    parser.add_argument("action", choices=["upgrade", "stamp"], nargs="?", default="upgrade")
    parser.add_argument("--db-url", dest="db_url", default=None, help="Database URL override")
    parser.add_argument("--force", action="store_true", help="Force upgrade even if tables exist (danger)")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")

    args = parser.parse_args()

    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

    db_url = args.db_url or settings.DATABASE_URL
    if not db_url:
        print("No DB_URL configured; set DB_URL in .env or pass --db-url", file=sys.stderr)
        return 2

    sanitized = sanitize_db_url(db_url)

    engine = create_engine(sanitized)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not args.quiet:
        print("Connected to DB; found tables:", tables)

    env = os.environ.copy()
    env["DB_URL"] = sanitized

    if args.action == "stamp":
        print("Stamping DB at head")
        return run_alembic_command(["alembic", "stamp", "head"], env=env)

    # action == upgrade, but we have logic for stamp fallback
    if "alembic_version" in tables:
        if not args.quiet:
            print("Found alembic_version; running normal upgrade head")
        return run_alembic_command(["alembic", "upgrade", "head"], env=env)

    # no alembic_version; if core tables present we'll stamp instead to avoid duplicate-create
    present_core = [t for t in CORE_TABLES if t in tables]
    if present_core and not args.force:
        print("Found existing app tables ({}). Alembic has not been stamped.".format(
            ", ".join(present_core)
        ))
        print("To prevent table-creation errors, running 'alembic stamp head'.")
        return run_alembic_command(["alembic", "stamp", "head"], env=env)

    if present_core and args.force:
        print("Forcing upgrade against DB with existing tables (use with caution)")

    # Normal upgrade
    return run_alembic_command(["alembic", "upgrade", "head"], env=env)


if __name__ == "__main__":
    raise SystemExit(main())
