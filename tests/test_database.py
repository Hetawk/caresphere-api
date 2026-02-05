from __future__ import annotations

import os
import importlib

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection

# Use an in-memory SQLite database for DB tests
os.environ["DB_URL"] = "sqlite:///:memory:"

# reload database module to re-create engine with test DB
import app.database as database
import app.config as config
import app.models as models


def test_engine_connects():
    # confirm engine is available and we can connect
    engine = database.engine
    with engine.begin() as conn:  # type: Connection
        # create tables in memory
        models.Base.metadata.create_all(bind=engine)
        # confirm at least one table is present
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert len(tables) > 0
