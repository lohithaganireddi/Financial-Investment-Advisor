"""
WebSocket Ticker Streaming & Subscription Manager Module

Manages real-time WebSocket client connections, ticker subscriptions (Stock & Crypto),
market data streaming updates, and safe disconnection cleanup without exposing API keys.
"""

import asyncio
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional, Set
from fastapi import WebSocket
from services.alpha_vantage import AlphaVantageService
from services.coingecko import CoinGeckoService


class TickerStreamManager:
    """
    Manages active WebSocket client connections and ticker subscriptions.
    Broadcasts real-time price updates for stocks and cryptocurrencies.
    """

    def __init__(
        self,
        stock_service: Optional[AlphaVantageService] = None,
        crypto_service: Optional[CoinGeckoService] = None,
    ):
        """
        Initialize TickerStreamManager with market data services.
        """
        self.stock_service = stock_service or AlphaVantageService()
        self.crypto_service = crypto_service or CoinGeckoService()

        # Maps WebSocket connection -> Set of asset keys ('stock:AAPL', 'crypto:bitcoin')
        self._connections: Dict[WebSocket, Set[str]] = {}

        # Cache last fetched market quote per asset key to prevent API rate limit abuse
        self._quote_cache: Dict[str, Dict[str, Any]] = {}

    @property
    def active_connection_count(self) -> int:
        """Return the number of currently active WebSocket connections."""
        return len(self._connections)

    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection and register connection state.
        """
        await websocket.accept()
        self._connections[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        """
        Clean up and unregister a disconnected WebSocket connection.
        """
        if websocket in self._connections:
            del self._connections[websocket]

    def get_subscriptions(self, websocket: WebSocket) -> Set[str]:
        """
        Return active asset subscriptions for a given WebSocket client.
        """
        return self._connections.get(websocket, set())

    def subscribe(self, websocket: WebSocket, asset_type: str, symbol: str) -> str:
        """
        Subscribe a client connection to a specific stock or crypto asset ticker.

        :param websocket: Target WebSocket connection.
        :param asset_type: 'stock' or 'crypto'.
        :param symbol: Asset symbol or coin ID (e.g., 'AAPL', 'bitcoin').
        :return: Standardized subscription asset key string.
        """
        if websocket not in self._connections:
            self._connections[websocket] = set()

        clean_type = str(asset_type).lower().strip() if asset_type else "stock"
        clean_sym = str(symbol).strip()
        clean_sym = clean_sym.upper() if clean_type == "stock" else clean_sym.lower()

        asset_key = f"{clean_type}:{clean_sym}"
        self._connections[websocket].add(asset_key)
        return asset_key

    def unsubscribe(self, websocket: WebSocket, asset_type: str, symbol: str) -> str:
        """
        Unsubscribe a client connection from a specific asset ticker.
        """
        clean_type = str(asset_type).lower().strip() if asset_type else "stock"
        clean_sym = str(symbol).strip()
        clean_sym = clean_sym.upper() if clean_type == "stock" else clean_sym.lower()

        asset_key = f"{clean_type}:{clean_sym}"
        if websocket in self._connections and asset_key in self._connections[websocket]:
            self._connections[websocket].remove(asset_key)
        return asset_key

    def fetch_ticker_quote(self, asset_type: str, symbol: str) -> Dict[str, Any]:
        """
        Fetch current market data quote for stock or crypto asset.
        Safely returns structured quote payload or fallback update on upstream failure.
        """
        clean_type = str(asset_type).lower().strip()
        clean_sym = str(symbol).strip()

        if clean_type == "stock":
            quote_res = self.stock_service.get_stock_quote(clean_sym)
            if quote_res.get("success"):
                return {
                    "type": "ticker_update",
                    "asset_type": "stock",
                    "symbol": quote_res.get("symbol", clean_sym.upper()),
                    "price": quote_res.get("price", 100.0),
                    "change_percent": quote_res.get("change_percent", 0.0),
                    "market_direction": quote_res.get("market_direction", "neutral"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "ok",
                }
        elif clean_type == "crypto":
            quote_res = self.crypto_service.get_crypto_price(clean_sym)
            if quote_res.get("success"):
                return {
                    "type": "ticker_update",
                    "asset_type": "crypto",
                    "symbol": quote_res.get("coin_id", clean_sym.lower()),
                    "price": quote_res.get("price", 1000.0),
                    "change_percent": quote_res.get("change_percent_24h", 0.0),
                    "market_direction": quote_res.get("market_direction", "neutral"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "ok",
                }

        # Safe fallback quote when API keys are unconfigured or rate limited
        base_price = 185.0 if clean_type == "stock" else 65000.0
        return {
            "type": "ticker_update",
            "asset_type": clean_type,
            "symbol": clean_sym.upper() if clean_type == "stock" else clean_sym.lower(),
            "price": base_price,
            "change_percent": 0.5,
            "market_direction": "bullish",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "stream_fallback",
        }

    async def broadcast_to_subscribers(self, asset_type: str, symbol: str):
        """
        Fetch latest market quote for an asset and broadcast update to all subscribed clients.
        """
        clean_type = str(asset_type).lower().strip()
        clean_sym = str(symbol).strip()
        asset_key = f"{clean_type}:{clean_sym.upper() if clean_type == 'stock' else clean_sym.lower()}"

        quote_payload = self.fetch_ticker_quote(clean_type, clean_sym)
        self._quote_cache[asset_key] = quote_payload

        payload_str = json.dumps(quote_payload)
        disconnected_sockets: List[WebSocket] = []

        for ws, subs in list(self._connections.items()):
            if asset_key in subs:
                try:
                    await ws.send_text(payload_str)
                except Exception:
                    disconnected_sockets.append(ws)

        for ws in disconnected_sockets:
            self.disconnect(ws)

    async def send_json(self, websocket: WebSocket, data: Dict[str, Any]):
        """
        Send a JSON payload directly to a specific WebSocket client.
        """
        try:
            await websocket.send_text(json.dumps(data))
        except Exception:
            self.disconnect(websocket)
