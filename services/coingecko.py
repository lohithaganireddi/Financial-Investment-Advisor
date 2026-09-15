"""
CoinGecko Cryptocurrency Data Service

This service module handles communication with the CoinGecko API to retrieve crypto market data.
It reads the API key securely from environment variables (.env) and formats response data into a clean structure.
"""

import os
from typing import Any, Dict, Optional
import httpx
from dotenv import load_dotenv

# Ensure environment variables from .env are loaded
load_dotenv()

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"


class CoinGeckoService:
    """Service client for fetching cryptocurrency market data from CoinGecko API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the CoinGecko Service.
        Reads API key from parameters or environment variable COINGECKO_API_KEY.
        """
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")

    def get_crypto_price(self, coin_id: str) -> Dict[str, Any]:
        """
        Fetch real-time cryptocurrency market data for a given coin ID (e.g., 'bitcoin', 'ethereum').

        :param coin_id: Cryptocurrency ID string (e.g., 'bitcoin', 'ethereum', 'solana').
        :return: Clean, structured dictionary containing crypto quote details or error details.
        """
        if not self.api_key or self.api_key.strip() in ("", "your_coingecko_api_key_here"):
            return {
                "success": False,
                "error": "Missing or unconfigured CoinGecko API key. Please set COINGECKO_API_KEY in your .env file."
            }

        if not coin_id or not coin_id.strip():
            return {
                "success": False,
                "error": "Invalid cryptocurrency coin ID provided."
            }

        clean_coin_id = coin_id.strip().lower()
        params = {
            "vs_currency": "usd",
            "ids": clean_coin_id
        }
        headers = {
            "Accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(COINGECKO_BASE_URL, params=params, headers=headers)

                if response.status_code == 429:
                    return {
                        "success": False,
                        "error": "CoinGecko API Rate Limit Exceeded (HTTP 429). Please try again later."
                    }

                response.raise_for_status()
                data = response.json()

            if not isinstance(data, list) or len(data) == 0:
                return {
                    "success": False,
                    "error": f"No market data found for coin ID '{clean_coin_id}'. Verify the coin identifier."
                }

            coin_data = data[0]
            return {
                "success": True,
                "data": {
                    "id": coin_data.get("id", clean_coin_id),
                    "symbol": coin_data.get("symbol", "").upper(),
                    "name": coin_data.get("name", ""),
                    "price": float(coin_data.get("current_price", 0.0) or 0.0),
                    "high_24h": float(coin_data.get("high_24h", 0.0) or 0.0),
                    "low_24h": float(coin_data.get("low_24h", 0.0) or 0.0),
                    "change_percent_24h": float(coin_data.get("price_change_percentage_24h", 0.0) or 0.0),
                    "market_cap": int(coin_data.get("market_cap", 0) or 0),
                    "volume_24h": float(coin_data.get("total_volume", 0.0) or 0.0),
                    "last_updated": coin_data.get("last_updated", "")
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
                "error": f"Network error connecting to CoinGecko: {str(err)}"
            }
        except (ValueError, KeyError, TypeError) as err:
            return {
                "success": False,
                "error": f"Unexpected response format from CoinGecko: {str(err)}"
            }
