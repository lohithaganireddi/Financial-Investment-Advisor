"""
SQLAlchemy Database Models

Defines the database schema for persisting financial analyses, user profiles, and watchlists.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from backend.database import Base


class Analysis(Base):
    """
    SQLAlchemy model representing a saved financial asset analysis record.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query = Column(String, nullable=False, index=True)
    asset_type = Column(String, nullable=False)
    asset = Column(String, nullable=False, index=True)
    news_query = Column(String, nullable=True)
    recommendation = Column(String, nullable=True)
    recommendation_score = Column(Integer, nullable=True)
    confidence = Column(String, nullable=True)
    risk_score = Column(Integer, nullable=True)
    risk_level = Column(String, nullable=True)
    market_direction = Column(String, nullable=True)
    news_sentiment = Column(String, nullable=True)
    agent_activity = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class User(Base):
    """
    SQLAlchemy model representing a registered user account.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst", nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class Watchlist(Base):
    """
    SQLAlchemy model representing a user's saved asset watchlist item.
    """
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    asset_type = Column(String, nullable=False)
    asset = Column(String, nullable=False, index=True)
    target_price = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    added_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
