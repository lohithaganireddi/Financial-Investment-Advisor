"""
Database Configuration Module

Configures SQLAlchemy engine, session factory, and base model class.
Reads DATABASE_URL from environment with a safe local SQLite default.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Retrieve database URL from environment or default to local SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartfinance.db").strip()

# SQLite requires specific connect_args for multithreaded FastAPI requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session and closes it cleanly after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables defined in models.py if they do not exist.
    """
    from backend import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
