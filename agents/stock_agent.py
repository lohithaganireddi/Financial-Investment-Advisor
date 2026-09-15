"""
Stock Price Agent Module

This module implements the StockAgent, which uses the AlphaVantageService to retrieve
stock price data, performs market sentiment and directional analysis, and returns a structured output.
"""

from typing import Any, Dict, Optional
from services.alpha_vantage import AlphaVantageService


class StockAgent:
    """Autonomous agent for inspecting equity stock quotes and generating market analysis."""

    def __init__(self, service: Optional[AlphaVantageService] = None):
        """
        Initialize the StockAgent.
        Supports dependency injection of a custom or mock AlphaVantageService.
        """
        self.service = service or AlphaVantageService()

    def _parse_change_percent(self, change_percent_raw: Any) -> float:
        """
        Safely convert a change percentage string (e.g., '1.3736%') or number to a float.
        """
        if isinstance(change_percent_raw, (int, float)):
            return round(float(change_percent_raw), 4)

        if isinstance(change_percent_raw, str):
            clean_str = change_percent_raw.replace("%", "").strip()
            try:
                return round(float(clean_str), 4)
            except ValueError:
                return 0.0

        return 0.0

    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze a stock ticker symbol by fetching price quote data and evaluating market direction.

        :param symbol: Stock ticker string (e.g., 'AAPL', 'MSFT').
        :return: Structured dictionary containing analysis results or error details.
        """
        if not symbol or not isinstance(symbol, str) or not symbol.strip():
            return {
                "success": False,
                "agent": "StockAgent",
                "symbol": str(symbol) if symbol is not None else "",
                "error": "Invalid stock symbol provided. Must be a non-empty string."
            }

        clean_symbol = symbol.strip().upper()

        # Retrieve quote data using the service layer
        service_response = self.service.get_stock_quote(clean_symbol)

        if not service_response.get("success"):
            return {
                "success": False,
                "agent": "StockAgent",
                "symbol": clean_symbol,
                "error": service_response.get("error", "Failed to retrieve stock quote data.")
            }

        data = service_response.get("data", {})

        price = float(data.get("price", 0.0))
        change = float(data.get("change", 0.0))
        change_percent_raw = data.get("change_percent", "0.0%")
        change_percent = self._parse_change_percent(change_percent_raw)

        # Determine market direction
        if change > 0:
            market_direction = "bullish"
            direction_desc = f"up +${change:.2f} (+{change_percent}%)"
            sentiment_summary = "indicating bullish momentum."
        elif change < 0:
            market_direction = "bearish"
            direction_desc = f"down -${abs(change):.2f} ({change_percent}%)"
            sentiment_summary = "indicating bearish pressure."
        else:
            market_direction = "neutral"
            direction_desc = "unchanged ($0.00)"
            sentiment_summary = "indicating neutral market consolidation."

        analysis_text = (
            f"{clean_symbol} is currently trading at ${price:.2f}, {direction_desc} for the session, "
            f"{sentiment_summary}"
        )

        return {
            "success": True,
            "agent": "StockAgent",
            "symbol": clean_symbol,
            "price": price,
            "change": change,
            "change_percent": change_percent,
            "market_direction": market_direction,
            "analysis": analysis_text,
            "details": {
                "open": float(data.get("open", 0.0)),
                "high": float(data.get("high", 0.0)),
                "low": float(data.get("low", 0.0)),
                "previous_close": float(data.get("previous_close", 0.0)),
                "volume": int(data.get("volume", 0)),
                "latest_trading_day": str(data.get("latest_trading_day", ""))
            }
        }
