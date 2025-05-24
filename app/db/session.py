# app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config import settings

# deferred globals
engine = None
SessionLocal = None
Base = declarative_base()

def _get_database_url() -> str:
    return os.getenv("DATABASE_URL", settings.DATABASE_URL)

def init_db():
    """
    Initialize the global `engine` + `SessionLocal` factory.
    Uses a StaticPool for SQLite in-memory so all sessions share one DB.
    """
    global engine, SessionLocal

    database_url = _get_database_url()

    if database_url.startswith("sqlite") and ":memory:" in database_url:
        # in-memory DB: single connection pool
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        engine = create_engine(database_url, connect_args=connect_args)

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

def get_db():
    """
    FastAPI dependency: yield a session and then close it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
