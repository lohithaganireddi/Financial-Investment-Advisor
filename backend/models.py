"""
SQLAlchemy Database Models

Defines the database schema for persisting financial analyses.
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

