"""
Crypto Agent Module

This module implements the CryptoAgent, which uses the CoinGeckoService to retrieve
cryptocurrency market data, performs directional and trend analysis, and returns a structured output.
"""

from typing import Any, Dict, Optional
from services.coingecko import CoinGeckoService


class CryptoAgent:
    """Autonomous agent for inspecting cryptocurrency quotes and generating market analysis."""

    def __init__(self, service: Optional[CoinGeckoService] = None):
        """
        Initialize the CryptoAgent.
        Supports dependency injection of a custom or mock CoinGeckoService.
        """
        self.service = service or CoinGeckoService()

    def analyze_crypto(self, coin_id: str) -> Dict[str, Any]:
        """
        Analyze a cryptocurrency coin ID by fetching market data and evaluating 24h trend direction.

        :param coin_id: Cryptocurrency ID string (e.g., 'bitcoin', 'ethereum', 'solana').
        :return: Structured dictionary containing crypto analysis results or error details.
        """
        if not coin_id or not isinstance(coin_id, str) or not coin_id.strip():
            return {
                "success": False,
                "agent": "CryptoAgent",
                "coin_id": str(coin_id) if coin_id is not None else "",
                "error": "Invalid cryptocurrency coin ID provided. Must be a non-empty string."
            }

        clean_coin_id = coin_id.strip().lower()

        # Retrieve crypto data using the service layer
        service_response = self.service.get_crypto_price(clean_coin_id)

        if not service_response.get("success"):
            return {
                "success": False,
                "agent": "CryptoAgent",
                "coin_id": clean_coin_id,
                "error": service_response.get("error", "Failed to retrieve cryptocurrency price data.")
            }

        data = service_response.get("data", {})

        price = float(data.get("price", 0.0))
        change_percent_24h = float(data.get("change_percent_24h", 0.0))
        symbol = str(data.get("symbol", "")).upper()
        name = str(data.get("name", clean_coin_id.capitalize()))

        # Determine market direction based on 24h price change
        if change_percent_24h > 0:
            market_direction = "bullish"
            direction_desc = f"up +{change_percent_24h:.2f}%"
            sentiment_summary = "indicating bullish momentum."
        elif change_percent_24h < 0:
            market_direction = "bearish"
            direction_desc = f"down {change_percent_24h:.2f}%"
            sentiment_summary = "indicating bearish pressure."
        else:
            market_direction = "neutral"
            direction_desc = "unchanged (0.00%)"
            sentiment_summary = "indicating neutral sideways price action."

        analysis_text = (
            f"{name} ({symbol}) is currently trading at ${price:,.2f}, {direction_desc} over the last 24 hours, "
            f"{sentiment_summary}"
        )

        return {
            "success": True,
            "agent": "CryptoAgent",
            "coin_id": clean_coin_id,
            "symbol": symbol,
            "name": name,
            "price": price,
            "change_percent_24h": change_percent_24h,
            "market_direction": market_direction,
            "analysis": analysis_text,
            "details": {
                "high_24h": float(data.get("high_24h", 0.0)),
                "low_24h": float(data.get("low_24h", 0.0)),
                "market_cap": int(data.get("market_cap", 0)),
                "volume_24h": float(data.get("volume_24h", 0.0)),
                "last_updated": str(data.get("last_updated", ""))
            }
        }
