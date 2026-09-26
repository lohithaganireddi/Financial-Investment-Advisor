"""
Unit tests for External Data Services

Verifies AlphaVantageService, CoinGeckoService, and NewsDataService handling of responses, errors, rate limits, and missing API keys using mocks.
Tests do NOT make live network requests or require real API keys.
"""

from unittest.mock import MagicMock, patch
import httpx
from services.alpha_vantage import AlphaVantageService
from services.coingecko import CoinGeckoService
from services.newsdata import NewsDataService


# ==========================================
# Alpha Vantage Service Unit Tests
# ==========================================

def test_alpha_vantage_missing_api_key():
    """Test that missing or placeholder API key returns an error without making network calls."""
    service = AlphaVantageService(api_key="your_alpha_vantage_api_key_here")
    result = service.get_stock_quote("AAPL")

    assert result["success"] is False
    assert "Missing or unconfigured Alpha Vantage API key" in result["error"]


def test_alpha_vantage_empty_symbol():
    """Test that empty stock symbol returns an error."""
    service = AlphaVantageService(api_key="valid_test_key")
    result = service.get_stock_quote("")

    assert result["success"] is False
    assert "Invalid stock symbol" in result["error"]


@patch("httpx.Client.get")
def test_alpha_vantage_successful_stock_quote(mock_get):
    """Test parsing of a successful Alpha Vantage GLOBAL_QUOTE response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "02. open": "180.00",
            "03. high": "185.00",
            "04. low": "179.00",
            "05. price": "184.50",
            "06. volume": "50000000",
            "07. latest trading day": "2026-09-15",
            "08. previous close": "182.00",
            "09. change": "2.50",
            "10. change percent": "1.3736%"
        }
    }
    mock_get.return_value = mock_response

    service = AlphaVantageService(api_key="valid_test_key")
    result = service.get_stock_quote("AAPL")

    assert result["success"] is True
    data = result["data"]
    assert data["symbol"] == "AAPL"
    assert data["price"] == 184.50
    assert data["volume"] == 50000000
    assert data["change_percent"] == "1.3736%"


@patch("httpx.Client.get")
def test_alpha_vantage_rate_limit_note(mock_get):
    """Test handling of Alpha Vantage API rate limit note."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute."
    }
    mock_get.return_value = mock_response

    service = AlphaVantageService(api_key="valid_test_key")
    result = service.get_stock_quote("AAPL")

    assert result["success"] is False
    assert "Rate Limit Exceeded" in result["error"]


@patch("httpx.Client.get")
def test_alpha_vantage_api_error_message(mock_get):
    """Test handling of invalid symbol error message from Alpha Vantage."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "Error Message": "Invalid API call. Please check your parameters."
    }
    mock_get.return_value = mock_response

    service = AlphaVantageService(api_key="valid_test_key")
    result = service.get_stock_quote("INVALID_TICKER")

    assert result["success"] is False
    assert "Alpha Vantage API Error" in result["error"]


@patch("httpx.Client.get")
def test_alpha_vantage_network_connection_error(mock_get):
    """Test handling of network connection failure."""
    mock_get.side_effect = httpx.RequestError("Connection refused")

    service = AlphaVantageService(api_key="valid_test_key")
    result = service.get_stock_quote("AAPL")

    assert result["success"] is False
    assert "Network error connecting to Alpha Vantage" in result["error"]


# ==========================================
# CoinGecko Service Unit Tests
# ==========================================

def test_coingecko_missing_api_key():
    """Test that missing or placeholder CoinGecko API key returns an error without network calls."""
    service = CoinGeckoService(api_key="your_coingecko_api_key_here")
    result = service.get_crypto_price("bitcoin")

    assert result["success"] is False
    assert "Missing or unconfigured CoinGecko API key" in result["error"]


def test_coingecko_empty_coin_id():
    """Test that empty coin ID returns an error."""
    service = CoinGeckoService(api_key="valid_test_key")
    result = service.get_crypto_price("")

    assert result["success"] is False
    assert "Invalid cryptocurrency coin ID" in result["error"]


@patch("httpx.Client.get")
def test_coingecko_successful_crypto_price(mock_get):
    """Test parsing of a successful CoinGecko markets response for bitcoin."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 65000.0,
            "high_24h": 66500.0,
            "low_24h": 64200.0,
            "price_change_percentage_24h": 2.15,
            "market_cap": 1280000000000,
            "total_volume": 35000000000.0,
            "last_updated": "2026-09-15T12:00:00.000Z"
        }
    ]
    mock_get.return_value = mock_response

    service = CoinGeckoService(api_key="valid_test_key")
    result = service.get_crypto_price("bitcoin")

    assert result["success"] is True
    data = result["data"]
    assert data["id"] == "bitcoin"
    assert data["symbol"] == "BTC"
    assert data["name"] == "Bitcoin"
    assert data["price"] == 65000.0
    assert data["change_percent_24h"] == 2.15
    assert data["market_cap"] == 1280000000000


@patch("httpx.Client.get")
def test_coingecko_rate_limit_429(mock_get):
    """Test handling of CoinGecko HTTP 429 rate limit error."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response

    service = CoinGeckoService(api_key="valid_test_key")
    result = service.get_crypto_price("bitcoin")

    assert result["success"] is False
    assert "Rate Limit Exceeded (HTTP 429)" in result["error"]


@patch("httpx.Client.get")
def test_coingecko_invalid_coin_id(mock_get):
    """Test handling of invalid/unknown coin ID returning an empty list."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    service = CoinGeckoService(api_key="valid_test_key")
    result = service.get_crypto_price("invalid_coin_id_xyz")

    assert result["success"] is False
    assert "No market data found for coin ID" in result["error"]


@patch("httpx.Client.get")
def test_coingecko_network_error(mock_get):
    """Test handling of network connection failure."""
    mock_get.side_effect = httpx.RequestError("Connection timeout")

    service = CoinGeckoService(api_key="valid_test_key")
    result = service.get_crypto_price("bitcoin")

    assert result["success"] is False
    assert "Network error connecting to CoinGecko" in result["error"]


# ==========================================
# NewsData Service Unit Tests
# ==========================================

def test_newsdata_missing_api_key():
    """Test that missing or placeholder NewsData API key returns an error without network calls."""
    service = NewsDataService(api_key="your_newsdata_api_key_here")
    result = service.get_financial_news("finance")

    assert result["success"] is False
    assert "Missing or unconfigured NewsData API key" in result["error"]


def test_newsdata_empty_query():
    """Test that empty search query returns an error."""
    service = NewsDataService(api_key="valid_test_key")
    result = service.get_financial_news("")

    assert result["success"] is False
    assert "Invalid search query" in result["error"]


@patch("httpx.Client.get")
def test_newsdata_successful_news_fetch(mock_get):
    """Test parsing of a successful NewsData.io news articles response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": "success",
        "totalResults": 1,
        "results": [
            {
                "article_id": "art_123",
                "title": "Stock Markets Reach All-Time Highs",
                "link": "https://news.example.com/article123",
                "description": "Financial markets saw strong gains today following positive economic reports...",
                "pubDate": "2026-09-15 10:00:00",
                "source_id": "financial_times"
            }
        ]
    }
    mock_get.return_value = mock_response

    service = NewsDataService(api_key="valid_test_key")
    result = service.get_financial_news("finance")

    assert result["success"] is True
    assert result["total_results"] == 1
    articles = result["data"]
    assert len(articles) == 1
    assert articles[0]["article_id"] == "art_123"
    assert articles[0]["title"] == "Stock Markets Reach All-Time Highs"
    assert articles[0]["source"] == "financial_times"


@patch("httpx.Client.get")
def test_newsdata_rate_limit_429(mock_get):
    """Test handling of NewsData HTTP 429 rate limit error."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response

    service = NewsDataService(api_key="valid_test_key")
    result = service.get_financial_news("finance")

    assert result["success"] is False
    assert "Rate Limit Exceeded (HTTP 429)" in result["error"]


@patch("httpx.Client.get")
def test_newsdata_api_error_response(mock_get):
    """Test handling of NewsData API payload error response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": "error",
        "results": {
            "message": "Invalid API Key",
            "code": "Unauthorized"
        }
    }
    mock_get.return_value = mock_response

    service = NewsDataService(api_key="valid_test_key")
    result = service.get_financial_news("finance")

    assert result["success"] is False
    assert "NewsData API Error: Invalid API Key" in result["error"]


@patch("httpx.Client.get")
def test_newsdata_network_error(mock_get):
    """Test handling of network connection failure."""
    mock_get.side_effect = httpx.RequestError("Connection timeout")

    service = NewsDataService(api_key="valid_test_key")
    result = service.get_financial_news("finance")

    assert result["success"] is False
    assert "Network error connecting to NewsData" in result["error"]


# ==========================================
# BacktestEngine Service Unit Tests (Day 36)
# ==========================================

from services.backtest_engine import BacktestEngine


def test_backtest_engine_success_stock():
    """Test successful Monte Carlo simulation for stock asset with seed reproducibility."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        asset="AAPL",
        asset_type="stock",
        initial_investment=10000.0,
        horizon_months=12,
        iterations=500,
        seed=42,
    )

    assert res["success"] is True
    assert res["asset"] == "AAPL"
    assert res["asset_type"] == "stock"
    assert res["initial_investment"] == 10000.0
    assert res["horizon_months"] == 12
    assert res["iterations"] == 500

    metrics = res["metrics"]
    assert "expected_final_value" in metrics
    assert "expected_return_pct" in metrics
    assert "bearish_p5_value" in metrics
    assert "bullish_p95_value" in metrics
    assert "value_at_risk_95" in metrics
    assert "sharpe_ratio" in metrics
    assert "success_rate_pct" in metrics

    assert len(res["trajectory"]) == 13  # Month 0 to Month 12
    assert res["trajectory"][0]["month"] == 0
    assert res["trajectory"][0]["p50"] == 10000.0


def test_backtest_engine_crypto_with_risk_score():
    """Test crypto simulation adjusted with risk score volatility multiplier."""
    engine = BacktestEngine()
    res = engine.run_backtest(
        asset="bitcoin",
        asset_type="crypto",
        initial_investment=5000.0,
        horizon_months=6,
        iterations=300,
        risk_score=75,
        seed=100,
    )

    assert res["success"] is True
    assert res["asset"] == "BITCOIN"
    assert res["asset_type"] == "crypto"
    assert len(res["trajectory"]) == 7


def test_backtest_engine_invalid_inputs():
    """Test BacktestEngine error validation on invalid parameters."""
    engine = BacktestEngine()

    res_empty_asset = engine.run_backtest(asset="")
    assert res_empty_asset["success"] is False
    assert "Asset symbol or name must be a non-empty string" in res_empty_asset["error"]

    res_neg_inv = engine.run_backtest(asset="AAPL", initial_investment=-500)
    assert res_neg_inv["success"] is False
    assert "Initial investment must be greater than 0" in res_neg_inv["error"]

    res_bad_horizon = engine.run_backtest(asset="AAPL", horizon_months=100)
    assert res_bad_horizon["success"] is False
    assert "Horizon months must be between 1 and 60" in res_bad_horizon["error"]

    res_bad_iter = engine.run_backtest(asset="AAPL", iterations=5)
    assert res_bad_iter["success"] is False
    assert "Iterations must be an integer between 10 and 2000" in res_bad_iter["error"]

