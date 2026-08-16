"""
Database core utilities for RCKG.

Provides database connection, session management, and transaction handling.
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Database URL from environment or fallback to active container on 5433/5432
DEFAULT_DB_URLS = [
    "postgresql://rckg:rckg_secret_password@localhost:5432/rckg_db",
    "postgresql://rckg_user:rckg_password@localhost:5433/rckg_test",
    "postgresql://postgres:postgres@localhost:5432/rckg",
]

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Auto-detect available PostgreSQL port
    import socket
    DATABASE_URL = DEFAULT_DB_URLS[0]  # default to 5433 test container
    for url in DEFAULT_DB_URLS:
        try:
            port = int(url.split(":")[-1].split("/")[0])
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                if s.connect_ex(("localhost", port)) == 0:
                    DATABASE_URL = url
                    break
        except Exception:
            continue

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,

    pool_pre_ping=True,  # Automatically verify connections
    pool_size=10,  # Number of connections to keep open
    max_overflow=20,  # Additional connections allowed
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",  # SQL logging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as session:
            results = session.query(GoldenControl).all()

    Automatically commits on success and rolls back on exception.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_db() -> Session:
    """
    Dependency function for FastAPI or similar frameworks.

    Usage in FastAPI:
        @app.get("/controls")
        def get_controls(db: Session = Depends(get_db)):
            return db.query(GoldenControl).all()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def ping_database() -> bool:
    """
    Check if the database is reachable.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False



__all__ = [
    "engine",
    "SessionLocal",
    "get_db_session",
    "get_db",
    "ping_database",
    "DATABASE_URL",
]
