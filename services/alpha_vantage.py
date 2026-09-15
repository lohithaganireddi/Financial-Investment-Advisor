"""
Alpha Vantage Financial Data Service

This service module handles communication with the Alpha Vantage API to retrieve stock price data.
It reads the API key securely from environment variables (.env) and formats response data into a clean structure.
"""

import os
from typing import Any, Dict, Optional
import httpx
from dotenv import load_dotenv

# Ensure environment variables from .env are loaded
load_dotenv()

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageService:
    """Service client for fetching stock market data from Alpha Vantage API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Alpha Vantage Service.
        Reads API key from parameters or environment variable ALPHA_VANTAGE_API_KEY.
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")

    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch real-time stock quote data for a given ticker symbol using Alpha Vantage GLOBAL_QUOTE.

        :param symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'IBM').
        :return: Clean, structured dictionary containing stock quote details or error details.
        """
        if not self.api_key or self.api_key.strip() in ("", "your_alpha_vantage_api_key_here"):
            return {
                "success": False,
                "error": "Missing or unconfigured Alpha Vantage API key. Please set ALPHA_VANTAGE_API_KEY in your .env file."
            }

        if not symbol or not symbol.strip():
            return {
                "success": False,
                "error": "Invalid stock symbol provided."
            }

        clean_symbol = symbol.strip().upper()
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": clean_symbol,
            "apikey": self.api_key
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(ALPHA_VANTAGE_BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

            # Handle Alpha Vantage API message responses (rate limit notes, error messages, information)
            if "Note" in data:
                return {
                    "success": False,
                    "error": f"Alpha Vantage API Rate Limit Exceeded: {data['Note']}"
                }

            if "Error Message" in data:
                return {
                    "success": False,
                    "error": f"Alpha Vantage API Error: {data['Error Message']}"
                }

            if "Information" in data:
                return {
                    "success": False,
                    "error": f"Alpha Vantage API Info: {data['Information']}"
                }

            # Parse standard GLOBAL_QUOTE response
            global_quote = data.get("Global Quote", {})
            if not global_quote:
                return {
                    "success": False,
                    "error": f"No data found for symbol '{clean_symbol}'. Verify the ticker symbol."
                }

            # Extract and format quote fields cleanly
            return {
                "success": True,
                "data": {
                    "symbol": global_quote.get("01. symbol", clean_symbol),
                    "open": float(global_quote.get("02. open", 0.0)),
                    "high": float(global_quote.get("03. high", 0.0)),
                    "low": float(global_quote.get("04. low", 0.0)),
                    "price": float(global_quote.get("05. price", 0.0)),
                    "volume": int(global_quote.get("06. volume", 0)),
                    "latest_trading_day": global_quote.get("07. latest trading day", ""),
                    "previous_close": float(global_quote.get("08. previous close", 0.0)),
                    "change": float(global_quote.get("09. change", 0.0)),
                    "change_percent": global_quote.get("10. change percent", "0.0%").strip()
                }
            }

        except httpx.HTTPStatusError as err:
            return {
                "success": False,
                "error": f"HTTP Error {err.response.status_code}: {err.response.text}"
            }
        except httpx.RequestError as err:
            return {
                "success": False,
                "error": f"Network error connecting to Alpha Vantage: {str(err)}"
            }
        except (ValueError, KeyError) as err:
            return {
                "success": False,
                "error": f"Unexpected response format from Alpha Vantage: {str(err)}"
            }
