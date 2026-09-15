"""
Database Configuration Module

Configures SQLAlchemy engine, session factory, and base model class.
Reads DATABASE_URL from environment with a safe local SQLite default.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
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
    Initialize database tables defined in models.py if they do not exist,
    and ensure missing columns are added for SQLite backward compatibility.
    """
    from backend import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    if DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(analyses)"))
                existing_cols = {row[1] for row in result.fetchall()}

                if "recommendation_score" not in existing_cols and "analyses" in [
                    r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
                ]:
                    conn.execute(text("ALTER TABLE analyses ADD COLUMN recommendation_score INTEGER"))
                if "agent_activity" not in existing_cols and "analyses" in [
                    r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
                ]:
                    conn.execute(text("ALTER TABLE analyses ADD COLUMN agent_activity TEXT"))
                conn.commit()
        except Exception as exc:
            print(f"init_db migration notice: {exc}")
