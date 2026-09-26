"""
Portfolio Recommendation Agent Module

This module implements the PortfolioAgent, which combines output from a market agent
(StockAgent or CryptoAgent), the RiskAgent, and the NewsAgent to generate a simple,
deterministic buy/hold/avoid recommendation without making any external API calls.

Recommendation Scoring Rules:
    Start: score = 50

    Market direction:
        - bullish  -> +20
        - neutral  ->   0
        - bearish  -> -20

    Risk level:
        - low      -> +15
        - medium   ->   0
        - high     -> -20

    News sentiment:
        - positive -> +15
        - neutral  ->   0
        - negative -> -15

    Score capped between 0 and 100.

    Recommendation:
        - score >= 70  -> "buy"
        - score >= 50  -> "hold"
        - score <  50  -> "avoid"

Confidence Logic:
    Positive signals: bullish direction + low risk + positive news
    Negative signals: bearish direction + high risk + negative news

    3 signals on one side -> "high"
    2 signals on one side -> "medium"
    Otherwise             -> "low"
"""

from typing import Any, Dict, List


class PortfolioAgent:
    """
    Deterministic portfolio recommendation agent.

    Combines market data (StockAgent / CryptoAgent), risk data (RiskAgent),
    and news data (NewsAgent) into a structured buy/hold/avoid recommendation.
    No external API calls are made.
    """

    # -----------------------------------------------------------------------
    # Supported upstream market agents
    # -----------------------------------------------------------------------
    _SUPPORTED_MARKET_AGENTS = {"StockAgent", "CryptoAgent"}

    # Asset identifier field for each supported market agent
    _ASSET_FIELD: Dict[str, str] = {
        "StockAgent": "symbol",
        "CryptoAgent": "coin_id",
    }

    # Asset type label for each supported market agent
    _ASSET_TYPE: Dict[str, str] = {
        "StockAgent": "stock",
        "CryptoAgent": "crypto",
    }

    # -----------------------------------------------------------------------
    # Scoring constants — kept as named constants for readability
    # -----------------------------------------------------------------------
    _BASE_SCORE = 50

    _DIRECTION_SCORE: Dict[str, int] = {
        "bullish": +20,
        "neutral":   0,
        "bearish": -20,
    }

    _RISK_SCORE: Dict[str, int] = {
        "low":    +15,
        "medium":   0,
        "high":   -20,
    }

    _NEWS_SCORE: Dict[str, int] = {
        "positive": +15,
        "neutral":    0,
        "negative": -15,
    }

    # -----------------------------------------------------------------------
    # Disclaimer (shown in every successful response)
    # -----------------------------------------------------------------------
    _DISCLAIMER = (
        "This is a software-generated educational recommendation, not financial advice."
    )

    # -----------------------------------------------------------------------
    # Validation helpers
    # -----------------------------------------------------------------------

    def _validate_input(self, data: Any, label: str) -> str:
        """
        Return an error string if `data` is not a valid non-empty dict with success=True,
        or an empty string if it is valid.
        """
        if not isinstance(data, dict):
            return f"{label} must be a dictionary."
        if not data:
            return f"{label} is empty. Provide a valid agent result."
        if not data.get("success"):
            return f"{label} reported failure. Cannot generate recommendation on failed data."
        return ""

    # -----------------------------------------------------------------------
    # Scoring helpers
    # -----------------------------------------------------------------------

    def _recommendation(self, score: int) -> str:
        """Map a final recommendation score to a buy/hold/avoid label."""
        if score >= 70:
            return "buy"
        elif score >= 50:
            return "hold"
        else:
            return "avoid"

    def _confidence(
        self,
        market_direction: str,
        risk_level: str,
        news_sentiment: str,
    ) -> str:
        """
        Calculate confidence from signal agreement.

        Positive signals (support a buy): bullish direction, low risk, positive news.
        Negative signals (support an avoid): bearish direction, high risk, negative news.

        3 matching signals on one side -> "high"
        2 matching signals on one side -> "medium"
        Otherwise                       -> "low"
        """
        positive_signals = sum([
            market_direction == "bullish",
            risk_level == "low",
            news_sentiment == "positive",
        ])
        negative_signals = sum([
            market_direction == "bearish",
            risk_level == "high",
            news_sentiment == "negative",
        ])

        dominant = max(positive_signals, negative_signals)
        if dominant >= 3:
            return "high"
        elif dominant >= 2:
            return "medium"
        else:
            return "low"

    # -----------------------------------------------------------------------
    # Main method
    # -----------------------------------------------------------------------

    def generate_recommendation(
        self,
        market_data: dict,
        risk_data: dict,
        news_data: dict,
    ) -> Dict[str, Any]:
        """
        Generate a portfolio recommendation from three agent outputs.

        :param market_data: Output from StockAgent.analyze_stock() or
                            CryptoAgent.analyze_crypto().
        :param risk_data:   Output from RiskAgent.analyze_risk().
        :param news_data:   Output from NewsAgent.analyze_news().
        :return: Structured recommendation dict or error dict on validation failure.
        """
        # --- Validate all three inputs -------------------------------------
        for data, label in [
            (market_data, "market_data"),
            (risk_data,   "risk_data"),
            (news_data,   "news_data"),
        ]:
            err = self._validate_input(data, label)
            if err:
                return {
                    "success": False,
                    "agent": "PortfolioAgent",
                    "error": err,
                    "factors": ["recommendation restricted because of missing data"],
                }

        # --- Validate market agent type ------------------------------------
        market_agent = market_data.get("agent")
        if market_agent not in self._SUPPORTED_MARKET_AGENTS:
            return {
                "success": False,
                "agent": "PortfolioAgent",
                "error": (
                    f"Unsupported market agent: '{market_agent}'. "
                    f"Supported: {sorted(self._SUPPORTED_MARKET_AGENTS)}."
                ),
                "factors": ["recommendation restricted because of unsupported market agent"],
            }

        # --- Extract asset identifier -------------------------------------
        asset_field = self._ASSET_FIELD[market_agent]
        asset = market_data.get(asset_field)
        if not asset:
            return {
                "success": False,
                "agent": "PortfolioAgent",
                "error": f"Missing asset identifier field '{asset_field}' in market_data.",
                "factors": ["recommendation restricted because of missing asset identifier"],
            }

        asset_type = self._ASSET_TYPE[market_agent]

        # --- Extract required market fields --------------------------------
        market_direction = str(market_data.get("market_direction", "")).lower()
        if not market_direction:
            return {
                "success": False,
                "agent": "PortfolioAgent",
                "error": "Missing 'market_direction' in market_data.",
                "factors": ["recommendation restricted because of missing market direction"],
            }

        # --- Extract required risk fields ----------------------------------
        risk_level = str(risk_data.get("risk_level", "")).lower()
        if not risk_level:
            return {
                "success": False,
                "agent": "PortfolioAgent",
                "error": "Missing 'risk_level' in risk_data.",
                "factors": ["recommendation restricted because of missing risk level"],
            }

        # --- Extract required news sentiment field -------------------------
        news_sentiment = str(news_data.get("overall_sentiment", "")).lower()
        if not news_sentiment:
            return {
                "success": False,
                "agent": "PortfolioAgent",
                "error": "Missing 'overall_sentiment' in news_data.",
                "factors": ["recommendation restricted because of missing news sentiment"],
            }

        # --- Compute recommendation score ----------------------------------
        # Start from base and apply each signal adjustment
        direction_adj = self._DIRECTION_SCORE.get(market_direction, 0)
        risk_adj      = self._RISK_SCORE.get(risk_level, 0)
        news_adj      = self._NEWS_SCORE.get(news_sentiment, 0)

        raw_score = self._BASE_SCORE + direction_adj + risk_adj + news_adj
        final_score = max(0, min(raw_score, 100))  # cap between 0 and 100

        recommendation = self._recommendation(final_score)
        confidence = self._confidence(market_direction, risk_level, news_sentiment)

        # --- Build human-readable structured factors list ------------------
        factors: List[str] = []

        if market_direction == "bullish":
            factors.append("positive market signal")
        elif market_direction == "bearish":
            factors.append("negative market signal")
        else:
            factors.append("neutral market signal")

        if news_sentiment == "positive":
            factors.append("positive news signal")
        elif news_sentiment == "negative":
            factors.append("negative news signal")
        else:
            factors.append("neutral news signal")

        if risk_level == "high":
            factors.append("elevated risk")
        elif risk_level == "medium":
            factors.append("moderate risk")
        else:
            factors.append("low risk factor")

        if confidence == "high":
            factors.append("high signal agreement")
        elif confidence == "medium":
            factors.append("moderate signal agreement")
        else:
            factors.append("mixed signal agreement")

        # --- Build deterministic summary sentence -------------------------
        asset_display = asset.upper() if asset_type == "stock" else asset.lower()
        summary = (
            f"Based on {market_direction} market conditions, {risk_level} risk, and "
            f"{news_sentiment} financial news sentiment, the system recommends "
            f"{recommendation.upper()} for {asset_display} with {confidence} confidence."
        )

        return {
            "success": True,
            "agent": "PortfolioAgent",
            "asset": asset,
            "asset_type": asset_type,
            "recommendation_score": final_score,
            "recommendation": recommendation,
            "confidence": confidence,
            "market_direction": market_direction,
            "risk_level": risk_level,
            "news_sentiment": news_sentiment,
            "factors": factors,
            "summary": summary,
            "disclaimer": self._DISCLAIMER,
        }
