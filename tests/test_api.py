"""
Unit and Integration Tests for FastAPI Backend Endpoints

Verifies /, /health, and /api/analyze using FastAPI TestClient and mock Orchestrator.
Tests do NOT make live network or external API requests.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes import get_orchestrator


client = TestClient(app)


def test_read_root():
    """Test the root welcome endpoint GET /."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Welcome to SmartFinancial Advisor" in data["message"]
    assert data["docs_url"] == "/docs"


def test_health_check():
    """Test the health check endpoint GET /health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "smartfinance-backend"
    assert data["version"] == "0.1.0"


def test_analyze_valid_stock_request():
    """Test POST /api/analyze with a valid stock analysis request."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run.return_value = {
        "success": True,
        "agent": "Orchestrator",
        "asset": "AAPL",
        "asset_type": "stock",
        "market_data": {
            "success": True,
            "agent": "StockAgent",
            "symbol": "AAPL",
            "price": 184.50,
            "change_percent": 1.37,
            "market_direction": "bullish"
        },
        "news_data": {
            "success": True,
            "agent": "NewsAgent",
            "overall_sentiment": "positive"
        },
        "risk_data": {
            "success": True,
            "agent": "RiskAgent",
            "risk_score": 30,
            "risk_level": "low"
        },
        "recommendation": {
            "success": True,
            "agent": "PortfolioAgent",
            "recommendation": "buy",
            "confidence": "high"
        },
        "summary": "Based on bullish market conditions...",
        "disclaimer": "This is a software-generated educational recommendation, not financial advice."
    }

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator

    try:
        payload = {
            "asset_type": "stock",
            "asset": "AAPL",
            "news_query": "Apple earnings"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["asset"] == "AAPL"
        assert data["asset_type"] == "stock"
        assert data["recommendation"]["recommendation"] == "buy"

        mock_orchestrator.run.assert_called_once_with(
            asset_type="stock",
            asset="AAPL",
            news_query="Apple earnings"
        )
    finally:
        app.dependency_overrides.clear()


def test_analyze_valid_crypto_request():
    """Test POST /api/analyze with a valid crypto analysis request."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run.return_value = {
        "success": True,
        "agent": "Orchestrator",
        "asset": "bitcoin",
        "asset_type": "crypto",
        "recommendation": {
            "success": True,
            "recommendation": "hold",
            "confidence": "medium"
        }
    }

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator

    try:
        payload = {
            "asset_type": "crypto",
            "asset": "bitcoin"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["asset"] == "bitcoin"
        assert data["asset_type"] == "crypto"

        mock_orchestrator.run.assert_called_once_with(
            asset_type="crypto",
            asset="bitcoin",
            news_query="finance"
        )
    finally:
        app.dependency_overrides.clear()


def test_analyze_missing_required_asset():
    """Test POST /api/analyze with missing required 'asset' field returns 422 Unprocessable Entity."""
    payload = {
        "asset_type": "stock"
        # "asset" missing
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_analyze_invalid_request_structure():
    """Test POST /api/analyze with invalid JSON structure returns 422."""
    payload = "not a json object"
    response = client.post(
        "/api/analyze",
        content=payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_analyze_orchestrator_application_failure():
    """Test POST /api/analyze when Orchestrator returns a application-level failure response."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run.return_value = {
        "success": False,
        "agent": "Orchestrator",
        "step": "market_agent",
        "error": "Failed to retrieve stock quote data."
    }

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator

    try:
        payload = {
            "asset_type": "stock",
            "asset": "INVALID_SYMBOL"
        }
        response = client.post("/api/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["agent"] == "Orchestrator"
        assert data["step"] == "market_agent"
        assert "Failed to retrieve stock quote data" in data["error"]
    finally:
        app.dependency_overrides.clear()
