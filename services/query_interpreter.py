"""
Query Interpreter Module

This module implements the QueryInterpreter, which parses natural-language financial queries,
classifies user intent (STOCK_ANALYSIS, CRYPTO_ANALYSIS, GENERAL_FINANCIAL_NEWS, UNSUPPORTED),
and extracts asset symbols/IDs for routing to the Orchestrator or News Agent.
Deterministic implementation without external LLM dependencies.
"""

import re
from typing import Any, Dict, Optional


class QueryInterpreter:
    """
    Parses and classifies natural language user queries into structured financial analysis requests.
    """

    # Intent Constants
    INTENT_STOCK = "STOCK_ANALYSIS"
    INTENT_CRYPTO = "CRYPTO_ANALYSIS"
    INTENT_NEWS = "GENERAL_FINANCIAL_NEWS"
    INTENT_UNSUPPORTED = "UNSUPPORTED"

    # Supported Stocks Mapping: keyword/alias -> (symbol, news_query_name)
    _STOCK_MAP = {
        "apple": ("AAPL", "Apple"),
        "aapl": ("AAPL", "Apple"),
        "microsoft": ("MSFT", "Microsoft"),
        "msft": ("MSFT", "Microsoft"),
        "tesla": ("TSLA", "Tesla"),
        "tsla": ("TSLA", "Tesla"),
        "nvidia": ("NVDA", "NVIDIA"),
        "nvda": ("NVDA", "NVIDIA"),
        "amazon": ("AMZN", "Amazon"),
        "amzn": ("AMZN", "Amazon"),
        "google": ("GOOGL", "Google"),
        "alphabet": ("GOOGL", "Google"),
        "googl": ("GOOGL", "Google"),
        "goog": ("GOOGL", "Google"),
        "meta": ("META", "Meta"),
    }

    # Supported Cryptocurrencies Mapping: keyword/alias -> (coin_id, news_query_name)
    _CRYPTO_MAP = {
        "bitcoin": ("bitcoin", "Bitcoin"),
        "btc": ("bitcoin", "Bitcoin"),
        "ethereum": ("ethereum", "Ethereum"),
        "eth": ("ethereum", "Ethereum"),
        "solana": ("solana", "Solana"),
        "sol": ("solana", "Solana"),
        "dogecoin": ("dogecoin", "Dogecoin"),
        "doge": ("dogecoin", "Dogecoin"),
    }

    # Keywords that indicate general financial news queries (when no specific asset is present)
    _NEWS_KEYWORDS = {
        "news", "headline", "headlines", "market", "markets", "financial",
        "finance", "economy", "economic", "stocks", "crypto"
    }

    def interpret(self, query: Any) -> Dict[str, Any]:
        """
        Interpret and classify a natural language financial query string.

        :param query: Natural language input string (e.g. "Should I invest in Apple?").
        :return: Dict containing intent, asset_type, asset, news_query, original_query,
                 and success status.
        """
        if not isinstance(query, str):
            return {
                "success": False,
                "intent": self.INTENT_UNSUPPORTED,
                "error": "Query must be a non-empty string."
            }

        cleaned_query = query.strip()
        if not cleaned_query:
            return {
                "success": False,
                "intent": self.INTENT_UNSUPPORTED,
                "error": "Query cannot be empty or whitespace only."
            }

        # Extract word tokens in lowercase
        words = re.findall(r"\b[a-zA-Z0-9]+\b", cleaned_query.lower())

        matched_stock = None
        matched_crypto = None

        # Check for stock keyword matches
        for word in words:
            if word in self._STOCK_MAP:
                matched_stock = self._STOCK_MAP[word]
                break

        # Check for crypto keyword matches
        for word in words:
            if word in self._CRYPTO_MAP:
                matched_crypto = self._CRYPTO_MAP[word]
                break

        # Handle ambiguous query containing conflicting stock & crypto assets
        if matched_stock and matched_crypto:
            return {
                "success": False,
                "intent": self.INTENT_UNSUPPORTED,
                "error": "Ambiguous query containing multiple distinct asset types."
            }

        # Handle Stock Analysis intent
        if matched_stock:
            symbol, news_name = matched_stock
            return {
                "success": True,
                "intent": self.INTENT_STOCK,
                "asset_type": "stock",
                "asset": symbol,
                "news_query": news_name,
                "original_query": cleaned_query
            }

        # Handle Crypto Analysis intent
        if matched_crypto:
            coin_id, news_name = matched_crypto
            return {
                "success": True,
                "intent": self.INTENT_CRYPTO,
                "asset_type": "crypto",
                "asset": coin_id,
                "news_query": news_name,
                "original_query": cleaned_query
            }

        # Handle General Financial News intent (when news/market keywords are present)
        for word in words:
            if word in self._NEWS_KEYWORDS:
                return {
                    "success": True,
                    "intent": self.INTENT_NEWS,
                    "asset_type": None,
                    "asset": None,
                    "news_query": "finance",
                    "original_query": cleaned_query
                }

        # Handle Unsupported / Unknown Query
        return {
            "success": False,
            "intent": self.INTENT_UNSUPPORTED,
            "error": (
                "Unable to identify a supported asset or intent from the query. "
                "FinSight 2.0 currently supports stock analysis (Apple, Microsoft, Tesla, Nvidia, Amazon, Google, Meta), "
                "crypto analysis (Bitcoin, Ethereum, Solana, Dogecoin), and general financial news."
            )
        }
