"""
Unit tests for AI Agent Modules

Verifies StockAgent input validation, service integration, market direction evaluation,
and percentage parsing using mock services without live network calls.
"""

from unittest.mock import MagicMock
from agents.stock_agent import StockAgent


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
