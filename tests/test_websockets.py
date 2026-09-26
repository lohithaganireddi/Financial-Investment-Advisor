"""
Unit and Integration Tests for Day 39 Real-Time Data Streaming & WebSocket Ticker Engine

Verifies TickerStreamManager subscription management, safe fallback streaming,
and FastAPI WebSocket connection handling via TestClient.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes import get_stream_manager
from services.ticker_streamer import TickerStreamManager

client = TestClient(app)


# ==========================================
# TickerStreamManager Service Unit Tests
# ==========================================

def test_ticker_stream_manager_unit_subscriptions():
    """Test TickerStreamManager subscription and unsubscription logic."""
    stock_mock = MagicMock()
    crypto_mock = MagicMock()

    stock_mock.get_stock_quote.return_value = {
        "success": True,
        "symbol": "AAPL",
        "price": 185.00,
        "change_percent": 1.5,
        "market_direction": "bullish"
    }

    manager = TickerStreamManager(stock_service=stock_mock, crypto_service=crypto_mock)
    mock_ws = MagicMock()

    key1 = manager.subscribe(mock_ws, "stock", "AAPL")
    assert key1 == "stock:AAPL"
    assert "stock:AAPL" in manager.get_subscriptions(mock_ws)

    key2 = manager.subscribe(mock_ws, "crypto", "bitcoin")
    assert key2 == "crypto:bitcoin"

    manager.unsubscribe(mock_ws, "stock", "AAPL")
    assert "stock:AAPL" not in manager.get_subscriptions(mock_ws)
    assert "crypto:bitcoin" in manager.get_subscriptions(mock_ws)


def test_ticker_stream_manager_fetch_quote():
    """Test TickerStreamManager quote fetching with mock stock and crypto services."""
    stock_mock = MagicMock()
    crypto_mock = MagicMock()

    stock_mock.get_stock_quote.return_value = {
        "success": True,
        "symbol": "MSFT",
        "price": 420.00,
        "change_percent": 2.1,
        "market_direction": "bullish"
    }

    manager = TickerStreamManager(stock_service=stock_mock, crypto_service=crypto_mock)
    quote = manager.fetch_ticker_quote("stock", "MSFT")

    assert quote["type"] == "ticker_update"
    assert quote["asset_type"] == "stock"
    assert quote["symbol"] == "MSFT"
    assert quote["price"] == 420.00
    assert quote["status"] == "ok"


# ==========================================
# WebSocket Endpoint Integration Tests
# ==========================================

def test_websocket_endpoint_ping_pong():
    """Test WebSocket client connection and ping/pong action."""
    with client.websocket_connect("/api/ws/ticker") as websocket:
        websocket.send_json({"action": "ping"})
        data = websocket.receive_json()

        assert data["type"] == "pong"
        assert "timestamp" in data


def test_websocket_endpoint_subscribe_stock():
    """Test WebSocket stock ticker subscription and immediate quote reception."""
    stock_mock = MagicMock()
    crypto_mock = MagicMock()

    stock_mock.get_stock_quote.return_value = {
        "success": True,
        "symbol": "AAPL",
        "price": 184.50,
        "change_percent": 1.37,
        "market_direction": "bullish"
    }

    real_manager = TickerStreamManager(stock_service=stock_mock, crypto_service=crypto_mock)
    app.dependency_overrides[get_stream_manager] = lambda: real_manager

    try:
        with client.websocket_connect("/api/ws/ticker") as websocket:
            websocket.send_json({"action": "subscribe", "asset_type": "stock", "symbol": "AAPL"})
            data = websocket.receive_json()

            assert data["type"] == "ticker_update"
            assert data["asset_type"] == "stock"
            assert data["symbol"] == "AAPL"
            assert data["price"] == 184.50
    finally:
        app.dependency_overrides.clear()


def test_websocket_endpoint_unsubscribe():
    """Test WebSocket unsubscription action."""
    real_manager = TickerStreamManager()
    app.dependency_overrides[get_stream_manager] = lambda: real_manager

    try:
        with client.websocket_connect("/api/ws/ticker") as websocket:
            websocket.send_json({"action": "unsubscribe", "asset_type": "stock", "symbol": "AAPL"})
            data = websocket.receive_json()

            assert data["type"] == "unsubscribed"
            assert data["symbol"] == "AAPL"
    finally:
        app.dependency_overrides.clear()
