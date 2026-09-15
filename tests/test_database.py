"""
Unit Tests for Database Models and AnalysisRepository

Verifies database initialization, Analysis record creation, retrieval, ordering,
limits, and error handling using an isolated temporary in-memory SQLite database.
Tests do NOT modify production smartfinance.db or make external network calls.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Analysis
from services.analysis_repository import AnalysisRepository


@pytest.fixture
def db_session():
    """Fixture providing an isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_save_and_retrieve_analysis(db_session):
    """Test saving a full Analysis record and retrieving it by ID."""
    repo = AnalysisRepository(db_session=db_session)
    record = repo.save_analysis(
        query="Should I invest in Apple?",
        asset_type="stock",
        asset="AAPL",
        news_query="Apple",
        recommendation="buy",
        recommendation_score=100,
        confidence="high",
        risk_score=30,
        risk_level="low",
        market_direction="bullish",
        news_sentiment="positive",
        session=db_session
    )

    assert record is not None
    assert record.id == 1
    assert record.query == "Should I invest in Apple?"
    assert record.asset == "AAPL"
    assert record.recommendation == "buy"
    assert record.recommendation_score == 100

    retrieved = repo.get_analysis_by_id(record.id, session=db_session)
    assert retrieved is not None
    assert retrieved.id == record.id
    assert retrieved.asset == "AAPL"


def test_recent_analyses_ordering(db_session):
    """Test that get_recent_analyses returns records ordered newest first."""
    repo = AnalysisRepository(db_session=db_session)

    r1 = repo.save_analysis("Query 1", "stock", "AAPL", session=db_session)
    r2 = repo.save_analysis("Query 2", "crypto", "bitcoin", session=db_session)
    r3 = repo.save_analysis("Query 3", "stock", "TSLA", session=db_session)

    recent = repo.get_recent_analyses(limit=10, session=db_session)
    assert len(recent) == 3
    # Newest first -> r3, r2, r1
    assert recent[0].id == r3.id
    assert recent[1].id == r2.id
    assert recent[2].id == r1.id


def test_recent_analyses_limit(db_session):
    """Test that get_recent_analyses respects the limit parameter."""
    repo = AnalysisRepository(db_session=db_session)
    for i in range(15):
        repo.save_analysis(f"Query {i}", "stock", "AAPL", session=db_session)

    recent_5 = repo.get_recent_analyses(limit=5, session=db_session)
    assert len(recent_5) == 5

    # Limit capped at 50 max
    recent_max = repo.get_recent_analyses(limit=100, session=db_session)
    assert len(recent_max) == 15  # only 15 exist total


def test_missing_analysis_id(db_session):
    """Test retrieving a non-existent analysis ID returns None."""
    repo = AnalysisRepository(db_session=db_session)
    retrieved = repo.get_analysis_by_id(999, session=db_session)
    assert retrieved is None


def test_nullable_fields(db_session):
    """Test saving an Analysis record with optional fields set to None."""
    repo = AnalysisRepository(db_session=db_session)
    record = repo.save_analysis(
        query="Analyze Bitcoin",
        asset_type="crypto",
        asset="bitcoin",
        session=db_session
    )

    assert record is not None
    assert record.recommendation is None
    assert record.risk_score is None
    assert record.market_direction is None
