"""
SQLAlchemy Database Models

Defines the database schema for persisting financial analyses, user profiles, and watchlists.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from backend.database import Base


class Analysis(Base):
    """
    SQLAlchemy model representing a saved financial asset analysis record.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
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


class RefreshToken(Base):
    """
    SQLAlchemy model representing a server-side refresh token / user session record.
    Stores cryptographically secure SHA-256 hashes of issued refresh tokens.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)
    family_id = Column(String, nullable=True, index=True)
    replaced_by_id = Column(Integer, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired based on current UTC time."""
        if not self.expires_at:
            return True
        now = datetime.now(timezone.utc)
        exp = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=timezone.utc)
        return now >= exp

    @property
    def is_revoked(self) -> bool:
        """Check if token has been revoked."""
        return self.revoked_at is not None

    @property
    def is_valid(self) -> bool:
        """Check if token is active (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired

