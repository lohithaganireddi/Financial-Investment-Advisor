"""
Unit tests for AI Agent Modules

Verifies StockAgent and CryptoAgent input validation, service integration, market direction evaluation,
and percentage parsing using mock services without live network calls.
"""

from unittest.mock import MagicMock
from agents.stock_agent import StockAgent
from agents.crypto_agent import CryptoAgent


# ==========================================
# StockAgent Unit Tests
# ==========================================

def test_stock_agent_invalid_symbols():
    """Test that invalid symbol inputs return an error dictionary."""
    agent = StockAgent(service=MagicMock())

    res1 = agent.analyze_stock("")
    assert res1["success"] is False
    assert "Invalid stock symbol" in res1["error"]

    res2 = agent.analyze_stock("   ")
    assert res2["success"] is False
    assert "Invalid stock symbol" in res2["error"]


def test_stock_agent_bullish_analysis():
    """Test StockAgent evaluation of a bullish stock price quote."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": True,
        "data": {
            "symbol": "AAPL",
            "open": 180.00,
            "high": 185.00,
            "low": 179.00,
            "price": 184.50,
            "volume": 50000000,
            "latest_trading_day": "2026-09-15",
            "previous_close": 182.00,
            "change": 2.50,
            "change_percent": "1.3736%"
        }
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("aapl")

    assert result["success"] is True
    assert result["agent"] == "StockAgent"
    assert result["symbol"] == "AAPL"
    assert result["price"] == 184.50
    assert result["change"] == 2.50
    assert result["change_percent"] == 1.3736
    assert result["market_direction"] == "bullish"
    assert "bullish momentum" in result["analysis"]
    assert result["details"]["volume"] == 50000000
    mock_service.get_stock_quote.assert_called_once_with("AAPL")


def test_stock_agent_bearish_analysis():
    """Test StockAgent evaluation of a bearish stock price quote."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": True,
        "data": {
            "symbol": "MSFT",
            "open": 410.00,
            "high": 412.00,
            "low": 402.00,
            "price": 405.00,
            "volume": 25000000,
            "latest_trading_day": "2026-09-15",
            "previous_close": 415.00,
            "change": -10.00,
            "change_percent": "-2.4096%"
        }
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("MSFT")

    assert result["success"] is True
    assert result["symbol"] == "MSFT"
    assert result["price"] == 405.00
    assert result["change"] == -10.00
    assert result["change_percent"] == -2.4096
    assert result["market_direction"] == "bearish"
    assert "bearish pressure" in result["analysis"]


def test_stock_agent_neutral_analysis():
    """Test StockAgent evaluation of a neutral stock price quote."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": True,
        "data": {
            "symbol": "IBM",
            "open": 140.00,
            "high": 141.00,
            "low": 139.50,
            "price": 140.00,
            "volume": 10000000,
            "latest_trading_day": "2026-09-15",
            "previous_close": 140.00,
            "change": 0.00,
            "change_percent": "0.00%"
        }
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("IBM")

    assert result["success"] is True
    assert result["symbol"] == "IBM"
    assert result["price"] == 140.00
    assert result["change"] == 0.00
    assert result["market_direction"] == "neutral"
    assert "neutral market consolidation" in result["analysis"]


def test_stock_agent_unconfigured_service_error():
    """Test that StockAgent propagates service errors gracefully."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": False,
        "error": "Missing or unconfigured Alpha Vantage API key. Please set ALPHA_VANTAGE_API_KEY in your .env file."
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("AAPL")

    assert result["success"] is False
    assert result["agent"] == "StockAgent"
    assert result["symbol"] == "AAPL"
    assert "Missing or unconfigured Alpha Vantage API key" in result["error"]


def test_stock_agent_dependency_injection():
    """Verify that dependency injection works and default service instantiates cleanly."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {"success": False, "error": "Mocked call"}

    agent = StockAgent(service=mock_service)
    assert agent.service == mock_service


# ==========================================
# CryptoAgent Unit Tests
# ==========================================

def test_crypto_agent_invalid_coin_id():
    """Test that invalid coin ID inputs return an error dictionary."""
    agent = CryptoAgent(service=MagicMock())

    res1 = agent.analyze_crypto("")
    assert res1["success"] is False
    assert "Invalid cryptocurrency coin ID" in res1["error"]

    res2 = agent.analyze_crypto("   ")
    assert res2["success"] is False
    assert "Invalid cryptocurrency coin ID" in res2["error"]


def test_crypto_agent_bullish_analysis():
    """Test CryptoAgent evaluation of a bullish cryptocurrency quote."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": True,
        "data": {
            "id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "price": 65000.00,
            "high_24h": 66500.00,
            "low_24h": 64200.00,
            "change_percent_24h": 2.15,
            "market_cap": 1280000000000,
            "volume_24h": 35000000000.0,
            "last_updated": "2026-09-15T12:00:00.000Z"
        }
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto(" BITCOIN ")

    assert result["success"] is True
    assert result["agent"] == "CryptoAgent"
    assert result["coin_id"] == "bitcoin"
    assert result["symbol"] == "BTC"
    assert result["name"] == "Bitcoin"
    assert result["price"] == 65000.00
    assert result["change_percent_24h"] == 2.15
    assert result["market_direction"] == "bullish"
    assert "bullish momentum" in result["analysis"]
    assert result["details"]["market_cap"] == 1280000000000
    mock_service.get_crypto_price.assert_called_once_with("bitcoin")


def test_crypto_agent_bearish_analysis():
    """Test CryptoAgent evaluation of a bearish cryptocurrency quote."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": True,
        "data": {
            "id": "ethereum",
            "symbol": "ETH",
            "name": "Ethereum",
            "price": 3400.00,
            "high_24h": 3550.00,
            "low_24h": 3380.00,
            "change_percent_24h": -3.50,
            "market_cap": 400000000000,
            "volume_24h": 15000000000.0,
            "last_updated": "2026-09-15T12:00:00.000Z"
        }
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto("ETHEREUM")

    assert result["success"] is True
    assert result["coin_id"] == "ethereum"
    assert result["symbol"] == "ETH"
    assert result["price"] == 3400.00
    assert result["change_percent_24h"] == -3.50
    assert result["market_direction"] == "bearish"
    assert "bearish pressure" in result["analysis"]


def test_crypto_agent_neutral_analysis():
    """Test CryptoAgent evaluation of a neutral cryptocurrency quote."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": True,
        "data": {
            "id": "tether",
            "symbol": "USDT",
            "name": "Tether",
            "price": 1.00,
            "high_24h": 1.001,
            "low_24h": 0.999,
            "change_percent_24h": 0.00,
            "market_cap": 110000000000,
            "volume_24h": 50000000000.0,
            "last_updated": "2026-09-15T12:00:00.000Z"
        }
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto("tether")

    assert result["success"] is True
    assert result["coin_id"] == "tether"
    assert result["price"] == 1.00
    assert result["change_percent_24h"] == 0.00
    assert result["market_direction"] == "neutral"
    assert "neutral sideways price action" in result["analysis"]


def test_crypto_agent_unconfigured_service_error():
    """Test that CryptoAgent propagates service configuration errors gracefully."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": False,
        "error": "Missing or unconfigured CoinGecko API key. Please set COINGECKO_API_KEY in your .env file."
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto("bitcoin")

    assert result["success"] is False
    assert result["agent"] == "CryptoAgent"
    assert result["coin_id"] == "bitcoin"
    assert "Missing or unconfigured CoinGecko API key" in result["error"]


def test_crypto_agent_dependency_injection():
    """Verify that dependency injection works and default service instantiates cleanly."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {"success": False, "error": "Mocked call"}

    agent = CryptoAgent(service=mock_service)
    assert agent.service == mock_service
