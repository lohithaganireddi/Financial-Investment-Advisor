"""
Unit and Integration Tests for FastAPI Backend Endpoints

Verifies /, /health, /api/analyze, /api/query, and /api/history endpoints
using FastAPI TestClient, mock Orchestrator, mock QueryInterpreter, and mock AnalysisRepository.
Tests do NOT make live network or external API requests.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes import get_orchestrator, get_query_interpreter, get_repository


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


# ==========================================
# POST /api/query & Persistence Unit Tests
# ==========================================

def test_query_endpoint_valid_stock():
    """Test POST /api/query with a valid stock natural language query and verify persistence and agent_activity."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_intent.return_value = {
        "success": True,
        "agent": "Orchestrator",
        "intent": "STOCK_ANALYSIS",
        "agents_used": ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"],
        "agent_activity": [
            {"agent": "StockAgent", "status": "success", "order": 1, "summary": "AAPL market analysis completed"},
            {"agent": "NewsAgent", "status": "success", "order": 2, "summary": "Financial news sentiment evaluated (positive)"},
            {"agent": "RiskAgent", "status": "success", "order": 3, "summary": "Risk score evaluated: 30 (low)"},
            {"agent": "PortfolioAgent", "status": "success", "order": 4, "summary": "Recommendation generated: BUY"},
        ],
        "asset": "AAPL",
        "asset_type": "stock",
        "market_data": {"market_direction": "bullish"},
        "news_data": {"overall_sentiment": "positive"},
        "risk_data": {"risk_score": 30, "risk_level": "low"},
        "recommendation": {"recommendation": "buy", "recommendation_score": 100, "confidence": "high"}
    }

    mock_repo = MagicMock()
    mock_record = MagicMock()
    mock_record.id = 42
    mock_repo.save_analysis.return_value = mock_record

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        payload = {"query": "Should I invest in Apple?"}
        response = client.post("/api/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "Should I invest in Apple?"
        assert data["interpreted"]["asset"] == "AAPL"
        assert data["interpreted"]["intent"] == "STOCK_ANALYSIS"
        assert data["agents_used"] == ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]
        assert len(data["agent_activity"]) == 4
        assert data["agent_activity"][0]["agent"] == "StockAgent"
        assert data["saved_analysis_id"] == 42


        mock_orchestrator.run_intent.assert_called_once()
        mock_repo.save_analysis.assert_called_once_with(
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
            agent_activity=[
                {"agent": "StockAgent", "status": "success", "order": 1, "summary": "AAPL market analysis completed"},
                {"agent": "NewsAgent", "status": "success", "order": 2, "summary": "Financial news sentiment evaluated (positive)"},
                {"agent": "RiskAgent", "status": "success", "order": 3, "summary": "Risk score evaluated: 30 (low)"},
                {"agent": "PortfolioAgent", "status": "success", "order": 4, "summary": "Recommendation generated: BUY"},
            ]
        )
    finally:
        app.dependency_overrides.clear()


def test_query_endpoint_orchestrator_failure_does_not_persist():
    """Test that failed Orchestrator analysis is NOT saved to the database."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_intent.return_value = {
        "success": False,
        "agent": "Orchestrator",
        "intent": "STOCK_ANALYSIS",
        "agents_used": ["StockAgent"],
        "step": "market_agent",
        "error": "Upstream API timeout"
    }

    mock_repo = MagicMock()

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        payload = {"query": "Analyze Tesla"}
        response = client.post("/api/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True  # interpretation succeeded
        assert data["analysis"]["success"] is False
        assert data["saved_analysis_id"] is None
        mock_repo.save_analysis.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_query_endpoint_db_failure_does_not_break_analysis():
    """Test that a database saving failure does not crash the financial analysis response."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_intent.return_value = {
        "success": True,
        "agent": "Orchestrator",
        "intent": "STOCK_ANALYSIS",
        "agents_used": ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"],
        "asset": "AAPL",
        "asset_type": "stock",
        "recommendation": {"recommendation": "buy"}
    }

    mock_repo = MagicMock()
    mock_repo.save_analysis.return_value = None  # DB save failed

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        payload = {"query": "Should I invest in Apple?"}
        response = client.post("/api/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["saved_analysis_id"] is None
    finally:
        app.dependency_overrides.clear()


def test_query_endpoint_general_financial_news():
    """Test POST /api/query with a general financial news query routes via run_intent without DB persistence."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_intent.return_value = {
        "success": True,
        "agent": "Orchestrator",
        "intent": "GENERAL_FINANCIAL_NEWS",
        "agents_used": ["NewsAgent"],
        "news_data": {
            "success": True,
            "agent": "NewsAgent",
            "query": "finance",
            "overall_sentiment": "neutral",
            "summary": "Markets are mixed today.",
            "articles": []
        },
        "summary": "Markets are mixed today.",
        "disclaimer": "This is a software-generated financial news summary, not financial advice."
    }

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator

    try:
        payload = {"query": "What is happening in the financial market?"}
        response = client.post("/api/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "What is happening in the financial market?"
        assert data["interpreted"]["intent"] == "GENERAL_FINANCIAL_NEWS"
        assert data["interpreted"]["asset"] is None
        assert data["interpreted"]["asset_type"] is None
        assert data["agents_used"] == ["NewsAgent"]
        assert data["saved_analysis_id"] is None
        # Orchestrator.run_intent() is called; not orchestrator.run()
        mock_orchestrator.run_intent.assert_called_once()
        mock_orchestrator.run.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_query_endpoint_stock_response_includes_intent_and_agents_used():
    """Test POST /api/query stock query includes intent field and agents_used in response."""
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_intent.return_value = {
        "success": True,
        "agent": "Orchestrator",
        "intent": "STOCK_ANALYSIS",
        "agents_used": ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"],
        "asset": "TSLA",
        "asset_type": "stock",
        "market_data": {"market_direction": "bearish"},
        "news_data": {"overall_sentiment": "negative"},
        "risk_data": {"risk_score": 70, "risk_level": "high"},
        "recommendation": {"recommendation": "avoid", "recommendation_score": 20, "confidence": "medium"}
    }

    mock_repo = MagicMock()
    mock_record = MagicMock()
    mock_record.id = 7
    mock_repo.save_analysis.return_value = mock_record

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        payload = {"query": "Give me a risk analysis of Tesla"}
        response = client.post("/api/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["interpreted"]["intent"] == "STOCK_ANALYSIS"
        assert data["interpreted"]["asset"] == "TSLA"
        assert data["agents_used"] == ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]
        assert data["saved_analysis_id"] == 7
    finally:
        app.dependency_overrides.clear()


# ==========================================
# History API Endpoints Unit Tests
# ==========================================

def test_get_history_endpoint():
    """Test GET /api/history endpoint returning recent records."""
    mock_repo = MagicMock()
    mock_record = {
        "id": 1,
        "query": "Should I invest in Apple?",
        "asset_type": "stock",
        "asset": "AAPL",
        "news_query": "Apple",
        "recommendation": "buy",
        "confidence": "high",
        "risk_score": 30,
        "risk_level": "low",
        "market_direction": "bullish",
        "news_sentiment": "positive",
        "created_at": "2026-09-15T15:00:00Z"
    }
    mock_repo.get_recent_analyses.return_value = [mock_record]

    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        response = client.get("/api/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert len(data["analyses"]) == 1
        assert data["analyses"][0]["asset"] == "AAPL"
        mock_repo.get_recent_analyses.assert_called_once_with(limit=5)
    finally:
        app.dependency_overrides.clear()


def test_get_history_by_id_endpoint_success():
    """Test GET /api/history/{analysis_id} endpoint returning a single record."""
    mock_repo = MagicMock()
    mock_record = {
        "id": 10,
        "query": "Analyze Bitcoin",
        "asset_type": "crypto",
        "asset": "bitcoin",
        "news_query": "Bitcoin",
        "recommendation": "avoid",
        "confidence": "medium",
        "risk_score": 80,
        "risk_level": "high",
        "market_direction": "bearish",
        "news_sentiment": "positive",
        "agent_activity": '[{"agent": "CryptoAgent", "status": "success", "order": 1, "summary": "bitcoin analysis completed"}]',
        "created_at": "2026-09-15T15:00:00Z"
    }
    mock_repo.get_analysis_by_id.return_value = mock_record

    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        response = client.get("/api/history/10")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["analysis"]["id"] == 10
        assert data["analysis"]["asset"] == "bitcoin"
        assert len(data["analysis"]["agent_activity"]) == 1
        assert data["analysis"]["agent_activity"][0]["agent"] == "CryptoAgent"
        mock_repo.get_analysis_by_id.assert_called_once_with(analysis_id=10)
    finally:
        app.dependency_overrides.clear()


def test_get_history_by_id_older_record_null_agent_activity():
    """Test GET /api/history/{analysis_id} with older record (null agent_activity) returns empty list."""
    mock_repo = MagicMock()
    mock_record = {
        "id": 5,
        "query": "Old Stock Query",
        "asset_type": "stock",
        "asset": "AAPL",
        "news_query": "Apple",
        "recommendation": "buy",
        "agent_activity": None,
        "created_at": "2026-09-01T10:00:00Z"
    }
    mock_repo.get_analysis_by_id.return_value = mock_record

    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        response = client.get("/api/history/5")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["analysis"]["agent_activity"] == []
    finally:
        app.dependency_overrides.clear()


def test_get_history_by_id_endpoint_not_found():
    """Test GET /api/history/{analysis_id} returning 404 when ID is not found."""
    mock_repo = MagicMock()
    mock_repo.get_analysis_by_id.return_value = None

    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        response = client.get("/api/history/999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    finally:
        app.dependency_overrides.clear()


# ==========================================
# Backtest Endpoint Unit Tests (Day 36)
# ==========================================

from backend.routes import get_backtest_engine


def test_backtest_endpoint_success():
    """Test POST /api/backtest endpoint with valid request payload."""
    mock_engine = MagicMock()
    mock_engine.run_backtest.return_value = {
        "success": True,
        "asset": "AAPL",
        "asset_type": "stock",
        "initial_investment": 10000.0,
        "horizon_months": 12,
        "iterations": 500,
        "metrics": {
            "expected_final_value": 11050.0,
            "expected_return_pct": 10.5,
            "bearish_p5_value": 7500.0,
            "bullish_p95_value": 15200.0,
            "volatility_pct": 20.0,
            "max_drawdown_pct": 15.2,
            "value_at_risk_95": 2500.0,
            "sharpe_ratio": 0.35,
            "success_rate_pct": 68.5,
        },
        "trajectory": [{"month": 0, "p5": 10000.0, "p50": 10000.0, "p95": 10000.0}],
        "summary": "Monte Carlo simulation projected median outcome of $11,050.00.",
        "disclaimer": "Educational simulation disclaimer.",
    }

    app.dependency_overrides[get_backtest_engine] = lambda: mock_engine

    try:
        payload = {
            "asset": "AAPL",
            "asset_type": "stock",
            "initial_investment": 10000.0,
            "horizon_months": 12,
            "iterations": 500
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["asset"] == "AAPL"
        assert data["metrics"]["expected_final_value"] == 11050.0
    finally:
        app.dependency_overrides.clear()


def test_backtest_endpoint_invalid_payload():
    """Test POST /api/backtest endpoint handling engine error failure."""
    mock_engine = MagicMock()
    mock_engine.run_backtest.return_value = {
        "success": False,
        "error": "Initial investment must be greater than 0."
    }

    app.dependency_overrides[get_backtest_engine] = lambda: mock_engine

    try:
        payload = {
            "asset": "AAPL",
            "initial_investment": -100.0,
            "horizon_months": 12
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "Initial investment must be greater than 0" in data["detail"]
    finally:
        app.dependency_overrides.clear()


