"""
Database configuration and session management
Handles SQLAlchemy setup and database connections
"""

from sqlalchemy import create_engine
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
def sanitize_db_url(url: str) -> str:
    """Return a DB URL with unsupported query params (e.g., ssl) removed.

    Some DB drivers like PyMySQL expect an 'ssl' argument to be a mapping;
    passing a string like 'false' causes an AttributeError during connect.
    Strip the 'ssl' parameter out of the querystring so SQLAlchemy doesn't
    pass it straight through.
    """
    try:
        parts = urlsplit(url)
        # sqlite URLs rely on triples slashes; avoid altering sqlite URLs
        if parts.scheme == "sqlite":
            return url
        qs = parse_qs(parts.query, keep_blank_values=True)
        if "ssl" in qs:
            qs.pop("ssl")
        new_query = urlencode(qs, doseq=True)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    except Exception:
        return url

# Alias for other modules (e.g. alembic.env) to avoid coupling to a private name
_sanitize_db_url = sanitize_db_url


engine = create_engine(
    _sanitize_db_url(settings.DATABASE_URL),
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
