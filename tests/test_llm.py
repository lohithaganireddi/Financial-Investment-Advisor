"""
Unit and Integration Tests for Day 38 LLM & Autonomous Financial Reasoning Service

Verifies LLMService provider selection, offline fallback synthesis, risk warnings,
key takeaways generation, and FastAPI POST /api/llm/synthesize endpoint.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes import get_llm_service
from services.llm_service import LLMService

client = TestClient(app)


# ==========================================
# LLMService Unit Tests
# ==========================================

def test_llm_service_offline_fallback_synthesis():
    """Test deterministic hybrid LLM synthesis in offline mode."""
    service = LLMService()

    sample_analysis = {
        "asset": "AAPL",
        "asset_type": "stock",
        "market_data": {"symbol": "AAPL", "market_direction": "bullish", "price": 184.50},
        "risk_data": {"risk_score": 30, "risk_level": "low"},
        "news_data": {"overall_sentiment": "positive"},
        "recommendation": {
            "recommendation": "buy",
            "confidence": "high",
            "recommendation_score": 85,
        }
    }

    res = service.synthesize_reasoning(sample_analysis, provider="auto")

    assert res["success"] is True
    assert res["provider"] == "offline_fallback"
    assert res["model"] == "smartfinance-hybrid-reasoner-v1"
    assert res["asset"] == "AAPL"
    assert "executive_summary" in res
    assert "AAPL" in res["executive_summary"]
    assert "BULLISH" in res["executive_summary"]
    assert isinstance(res["key_takeaways"], list)
    assert len(res["key_takeaways"]) == 4
    assert "Low Risk Profile" in res["risk_warning"]


def test_llm_service_high_risk_warning():
    """Test high-risk warning generation in LLM synthesis."""
    service = LLMService()

    sample_analysis = {
        "asset": "TSLA",
        "asset_type": "stock",
        "market_data": {"market_direction": "bearish"},
        "risk_data": {"risk_score": 85, "risk_level": "high"},
        "news_data": {"overall_sentiment": "negative"},
        "recommendation": {"recommendation": "avoid", "confidence": "high", "recommendation_score": 20}
    }

    res = service.synthesize_reasoning(sample_analysis, provider="offline_fallback")

    assert res["success"] is True
    assert "High Risk Warning" in res["risk_warning"]
    assert "TSLA" in res["risk_warning"]


def test_llm_service_invalid_input():
    """Test LLMService validation on empty input dictionary."""
    service = LLMService()

    res_empty = service.synthesize_reasoning({})
    assert res_empty["success"] is False
    assert "Analysis data must be a non-empty dictionary" in res_empty["error"]

    res_none = service.synthesize_reasoning(None)  # type: ignore
    assert res_none["success"] is False


def test_llm_service_provider_override():
    """Test provider specification routing with configured API keys."""
    service = LLMService(openai_api_key="sk-valid-test-key", gemini_api_key="valid-gemini-key")
    sample = {"asset": "BTC", "asset_type": "crypto"}

    res_openai = service.synthesize_reasoning(sample, provider="openai")
    assert res_openai["success"] is True
    assert res_openai["provider"] == "openai"
    assert res_openai["model"] == "gpt-4o-mini"

    res_gemini = service.synthesize_reasoning(sample, provider="gemini")
    assert res_gemini["success"] is True
    assert res_gemini["provider"] == "gemini"
    assert res_gemini["model"] == "gemini-1.5-flash"



# ==========================================
# LLM Endpoint Integration Tests
# ==========================================

def test_llm_synthesize_endpoint_success():
    """Test POST /api/llm/synthesize REST endpoint."""
    mock_service = MagicMock()
    mock_service.synthesize_reasoning.return_value = {
        "success": True,
        "provider": "offline_fallback",
        "model": "smartfinance-hybrid-reasoner-v1",
        "asset": "AAPL",
        "executive_summary": "Autonomous reasoning summary for AAPL.",
        "key_takeaways": ["Takeaway 1", "Takeaway 2"],
        "risk_warning": "Low risk warning.",
        "disclaimer": "Educational disclaimer.",
    }

    app.dependency_overrides[get_llm_service] = lambda: mock_service

    try:
        payload = {
            "analysis_data": {"asset": "AAPL", "asset_type": "stock"},
            "provider": "auto"
        }
        response = client.post("/api/llm/synthesize", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["asset"] == "AAPL"
        assert data["executive_summary"] == "Autonomous reasoning summary for AAPL."
    finally:
        app.dependency_overrides.clear()


def test_llm_synthesize_endpoint_error():
    """Test POST /api/llm/synthesize returning 400 on synthesis failure."""
    mock_service = MagicMock()
    mock_service.synthesize_reasoning.return_value = {
        "success": False,
        "error": "Analysis data must be a non-empty dictionary."
    }

    app.dependency_overrides[get_llm_service] = lambda: mock_service

    try:
        payload = {"analysis_data": {}, "provider": "auto"}
        response = client.post("/api/llm/synthesize", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "Analysis data must be a non-empty dictionary" in data["detail"]
    finally:
        app.dependency_overrides.clear()
