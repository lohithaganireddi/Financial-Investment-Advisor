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
        "facebook": ("META", "Meta"),
        "netflix": ("NFLX", "Netflix"),
        "nflx": ("NFLX", "Netflix"),
        "amd": ("AMD", "AMD"),
        "intel": ("INTC", "Intel"),
        "intc": ("INTC", "Intel"),
        "coca-cola": ("KO", "Coca-Cola"),
        "cocacola": ("KO", "Coca-Cola"),
        "coke": ("KO", "Coca-Cola"),
        "ko": ("KO", "Coca-Cola"),
        "walmart": ("WMT", "Walmart"),
        "wmt": ("WMT", "Walmart"),
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
        "cardano": ("cardano", "Cardano"),
        "ada": ("cardano", "Cardano"),
        "xrp": ("ripple", "XRP"),
        "ripple": ("ripple", "Ripple"),
        "binance coin": ("binancecoin", "Binance Coin"),
        "binancecoin": ("binancecoin", "Binance Coin"),
        "bnb": ("binancecoin", "Binance Coin"),
        "polygon": ("polygon", "Polygon"),
        "matic": ("polygon", "Polygon"),
    }

    # Explicit keywords indicating a request for news articles/headlines rather than full analysis
    _EXPLICIT_NEWS_KEYWORDS = {
        "news", "headline", "headlines", "article", "articles"
    }

    # General keywords that indicate general financial news queries (when no specific asset is present)
    _GENERAL_NEWS_KEYWORDS = {
        "news", "headline", "headlines", "market", "markets", "financial",
        "finance", "economy", "economic", "stocks", "crypto", "business", "inflation"
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

        # Normalize query: replace $TICKER with TICKER, lowercase, collapse whitespace
        normalized = re.sub(r"\$([a-zA-Z0-9]+)", r"\1", cleaned_query).lower()
        normalized = re.sub(r"\s+", " ", normalized)

        # Match stocks and cryptos using boundary-aware regex to prevent substring false-positives
        matched_stocks = {}  # symbol -> (symbol, news_name)
        for keyword, data in self._STOCK_MAP.items():
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, normalized):
                matched_stocks[data[0]] = data

        matched_cryptos = {}  # coin_id -> (coin_id, news_name)
        for keyword, data in self._CRYPTO_MAP.items():
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, normalized):
                matched_cryptos[data[0]] = data

        all_matched_assets = list(matched_stocks.values()) + list(matched_cryptos.values())

        # Ambiguity check: multiple distinct assets found in query
        if len(all_matched_assets) > 1:
            names = [item[1] for item in all_matched_assets]
            names_str = ", ".join(f"'{n}'" for n in names)
            return {
                "success": False,
                "intent": self.INTENT_UNSUPPORTED,
                "error": f"Ambiguous query containing multiple distinct financial assets ({names_str}). Please analyze one asset at a time.",
                "original_query": cleaned_query
            }

        # Explicit news indicator check
        has_explicit_news = any(
            re.search(r"\b" + re.escape(nk) + r"\b", normalized) for nk in self._EXPLICIT_NEWS_KEYWORDS
        )

        # Single matched asset found
        if len(all_matched_assets) == 1:
            asset_id, news_name = all_matched_assets[0]
            is_stock = all_matched_assets[0] in matched_stocks.values()

            # If the user explicitly asked for news about this asset (e.g. "Apple stock news", "Latest news about Tesla")
            if has_explicit_news:
                return {
                    "success": True,
                    "intent": self.INTENT_NEWS,
                    "asset_type": None,
                    "asset": None,
                    "news_query": news_name,
                    "confidence": "high",
                    "original_query": cleaned_query
                }

            if is_stock:
                return {
                    "success": True,
                    "intent": self.INTENT_STOCK,
                    "asset_type": "stock",
                    "asset": asset_id,
                    "news_query": news_name,
                    "confidence": "high",
                    "original_query": cleaned_query
                }
            else:
                return {
                    "success": True,
                    "intent": self.INTENT_CRYPTO,
                    "asset_type": "crypto",
                    "asset": asset_id,
                    "news_query": news_name,
                    "confidence": "high",
                    "original_query": cleaned_query
                }

        # General financial news check (when no specific asset is matched)
        tokens = set(re.findall(r"\b[a-zA-Z0-9\-]+\b", normalized))
        for token in tokens:
            if token in self._GENERAL_NEWS_KEYWORDS:
                return {
                    "success": True,
                    "intent": self.INTENT_NEWS,
                    "asset_type": None,
                    "asset": None,
                    "news_query": "finance",
                    "confidence": "high",
                    "original_query": cleaned_query
                }

        # Unsupported / Unknown Query
        return {
            "success": False,
            "intent": self.INTENT_UNSUPPORTED,
            "error": (
                "Unable to identify a supported financial asset or intent from the query. "
                "FinSight 2.0 currently supports stock analysis, crypto analysis, and general financial news."
            ),
            "original_query": cleaned_query
        }

