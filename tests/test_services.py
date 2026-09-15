"""
Unit tests for External Data Services

Verifies AlphaVantageService and CoinGeckoService handling of responses, errors, rate limits, and missing API keys using mocks.
Tests do NOT make live network requests or require real API keys.
"""

from unittest.mock import MagicMock, patch
import httpx
from services.alpha_vantage import AlphaVantageService
from services.coingecko import CoinGeckoService


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
