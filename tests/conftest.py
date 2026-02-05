import os
import sys
from pathlib import Path

# Add project root to sys.path so `app` package is importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import os

# Use in-memory sqlite for tests by default
os.environ.setdefault("DB_URL", "sqlite:///:memory:")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models as models
from app.database import sanitize_db_url


def _create_test_engine():
	url = sanitize_db_url(os.environ.get("DB_URL") or "sqlite:///:memory:")
	engine = create_engine(url)
	return engine


@pytest.fixture(scope="session")
def engine():
	eng = _create_test_engine()
	models.Base.metadata.create_all(bind=eng)
	yield eng
	models.Base.metadata.drop_all(bind=eng)


@pytest.fixture()
def db(engine):
	SessionLocal = sessionmaker(bind=engine)
	session = SessionLocal()
	try:
		yield session
	finally:
		session.rollback()
		session.close()

# Ensure development .env is loaded by pydantic-settings
# but tests will override DB_URL where necessary
