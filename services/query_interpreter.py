"""
Query Interpreter Module

This module implements the QueryInterpreter, which converts simple natural-language
financial queries into structured inputs required by the Orchestrator.
Uses deterministic keyword and alias mapping without external LLM dependencies.
"""

import re
from typing import Any, Dict, Optional


class QueryInterpreter:
    """
    Parses user natural language queries into structured asset analysis requests.
    """

    # Supported Stocks Mapping
    # Maps keywords/aliases to (symbol, display_name/news_query)
    _STOCK_MAP = {
        "apple": ("AAPL", "Apple"),
        "aapl": ("AAPL", "Apple"),
        "microsoft": ("MSFT", "Microsoft"),
        "msft": ("MSFT", "Microsoft"),
        "tesla": ("TSLA", "Tesla"),
        "tsla": ("TSLA", "Tesla"),
        "amazon": ("AMZN", "Amazon"),
        "amzn": ("AMZN", "Amazon"),
        "google": ("GOOGL", "Google"),
        "alphabet": ("GOOGL", "Google"),
        "googl": ("GOOGL", "Google"),
        "goog": ("GOOGL", "Google"),
        "nvidia": ("NVDA", "NVIDIA"),
        "nvda": ("NVDA", "NVIDIA"),
        "meta": ("META", "Meta"),
    }

    # Supported Cryptocurrencies Mapping
    # Maps keywords/aliases to (coin_id, display_name/news_query)
    _CRYPTO_MAP = {
        "bitcoin": ("bitcoin", "Bitcoin"),
        "btc": ("bitcoin", "Bitcoin"),
        "ethereum": ("ethereum", "Ethereum"),
        "eth": ("ethereum", "Ethereum"),
        "solana": ("solana", "Solana"),
        "sol": ("solana", "Solana"),
    }

    def interpret(self, query: Any) -> Dict[str, Any]:
        """
        Interpret a natural language financial query string.

        :param query: Natural language input string (e.g., "Should I invest in Apple?").
        :return: Standardized dict with success, asset_type, asset, news_query, original_query,
                 or an error dict on failure.
        """
        # Validate query type and content
        if not isinstance(query, str):
            return {
                "success": False,
                "error": "Query must be a non-empty string."
            }

        cleaned_query = query.strip()
        if not cleaned_query:
            return {
                "success": False,
                "error": "Query cannot be empty or whitespace only."
            }

        # Normalize query text by converting to lowercase and stripping special punctuation
        # Replace non-alphanumeric chars with spaces to easily extract word tokens
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

        # If both or neither match, check ambiguity or missing asset
        if matched_stock and matched_crypto:
            # Handle potential collision (if both are present in the same query)
            # Prioritize based on explicit order or return unsupported/ambiguous if conflicting
            return {
                "success": False,
                "error": "Ambiguous query containing multiple distinct asset types."
            }

        if matched_stock:
            symbol, news_name = matched_stock
            return {
                "success": True,
                "asset_type": "stock",
                "asset": symbol,
                "news_query": news_name,
                "original_query": cleaned_query
            }

        if matched_crypto:
            coin_id, news_name = matched_crypto
            return {
                "success": True,
                "asset_type": "crypto",
                "asset": coin_id,
                "news_query": news_name,
                "original_query": cleaned_query
            }

        return {
            "success": False,
            "error": "Unable to identify a supported financial asset from the query."
        }
