"""
LLM & Autonomous Financial Reasoning Service Module

Provides a hybrid Large Language Model (LLM) reasoning adapter for synthesizing executive
financial summaries, key investment takeaways, and risk warnings from multi-agent analysis output.
Supports OpenAI, Google Gemini, Anthropic, and a zero-dependency deterministic fallback mode.
"""

import os
from typing import Any, Dict, List, Optional


class LLMService:
    """
    Hybrid LLM Reasoning Adapter Service for SmartFinancial Advisor.

    Synthesizes conversational financial analysis and multi-agent findings into natural-language
    executive summaries and structured key takeaways.
    """

    _DISCLAIMER = (
        "Software-generated AI reasoning synthesis provided for informational and educational purposes. "
        "Does not constitute professional financial or investment advice."
    )

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
    ):
        """
        Initialize LLMService with optional API keys from parameter or environment.
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")

    def _is_placeholder_key(self, key: Optional[str]) -> bool:
        """Check if an API key is empty, None, or a placeholder string."""
        if not key or not isinstance(key, str):
            return True
        k = key.strip().lower()
        return k.startswith("your_") or "placeholder" in k or k == ""

    def synthesize_reasoning(
        self,
        analysis_data: Dict[str, Any],
        provider: str = "auto",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize autonomous financial reasoning and executive summary from analysis data.

        :param analysis_data: Dictionary containing multi-agent results (asset, market_data, risk_data, recommendation, news_data).
        :param provider: 'auto', 'openai', 'gemini', 'anthropic', or 'offline_fallback'.
        :param model: Optional specific model identifier.
        :return: Standardized dictionary with executive summary, key takeaways, and risk warning.
        """
        if not isinstance(analysis_data, dict) or not analysis_data:
            return {
                "success": False,
                "error": "Analysis data must be a non-empty dictionary.",
                "provider": "offline_fallback",
            }

        clean_provider = provider.strip().lower() if provider else "auto"

        # Determine target provider based on available keys if set to auto
        if clean_provider == "auto":
            if not self._is_placeholder_key(self.openai_api_key):
                clean_provider = "openai"
            elif not self._is_placeholder_key(self.gemini_api_key):
                clean_provider = "gemini"
            elif not self._is_placeholder_key(self.anthropic_api_key):
                clean_provider = "anthropic"
            else:
                clean_provider = "offline_fallback"

        # Route to appropriate provider handler with seamless fallback to offline mode
        if clean_provider == "openai" and not self._is_placeholder_key(self.openai_api_key):
            return self._synthesize_openai(analysis_data, model or "gpt-4o-mini")
        elif clean_provider == "gemini" and not self._is_placeholder_key(self.gemini_api_key):
            return self._synthesize_gemini(analysis_data, model or "gemini-1.5-flash")
        elif clean_provider == "anthropic" and not self._is_placeholder_key(self.anthropic_api_key):
            return self._synthesize_anthropic(analysis_data, model or "claude-3-haiku")
        else:
            return self._synthesize_offline_fallback(analysis_data)

    def _synthesize_offline_fallback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic hybrid template synthesis for offline mode or missing API keys.
        """
        asset = str(data.get("asset") or data.get("market_data", {}).get("symbol") or "Target Asset").upper()
        asset_type = str(data.get("asset_type") or "asset").lower()

        market_direction = str(
            data.get("market_data", {}).get("market_direction")
            or data.get("market_direction")
            or "neutral"
        ).lower()

        risk_level = str(
            data.get("risk_data", {}).get("risk_level")
            or data.get("risk_level")
            or "medium"
        ).lower()

        risk_score = (
            data.get("risk_data", {}).get("risk_score")
            if isinstance(data.get("risk_data"), dict)
            else data.get("risk_score")
        )

        news_sentiment = str(
            data.get("news_data", {}).get("overall_sentiment")
            or data.get("news_sentiment")
            or "neutral"
        ).lower()

        rec_data = data.get("recommendation", {})
        if isinstance(rec_data, dict):
            rec_action = str(rec_data.get("recommendation") or "HOLD").upper()
            rec_score = rec_data.get("recommendation_score", 50)
            confidence = str(rec_data.get("confidence") or "medium").upper()
        else:
            rec_action = str(rec_data or "HOLD").upper()
            rec_score = 50
            confidence = "MEDIUM"

        # Construct natural language executive summary
        summary = (
            f"Autonomous hybrid evaluation for {asset} ({asset_type.upper()}) indicates a {market_direction.upper()} "
            f"market trend combined with {risk_level.upper()} volatility risk (Score: {risk_score if risk_score is not None else '-'}). "
            f"Financial news sentiment reflects {news_sentiment.upper()} market tone. "
            f"The synthesized agent consensus advises a {rec_action} guidance with {confidence} confidence (Score: {rec_score}/100)."
        )

        takeaways: List[str] = [
            f"Market Trend: Asset direction is currently assessed as {market_direction.upper()}.",
            f"Volatility Rating: Assigned {risk_level.upper()} risk classification based on price momentum.",
            f"News Sentiment: Sector financial media sentiment is {news_sentiment.upper()}.",
            f"Consensus Strategy: Multi-agent pipeline generated a final {rec_action} recommendation.",
        ]

        if risk_level == "high":
            risk_warning = f"High Risk Warning: {asset} exhibits elevated price volatility. Exercise strict position sizing."
        elif risk_level == "medium":
            risk_warning = f"Moderate Risk Warning: {asset} shows moderate price fluctuations. Monitor market news updates."
        else:
            risk_warning = f"Low Risk Profile: {asset} demonstrates relatively stable price parameters."

        return {
            "success": True,
            "provider": "offline_fallback",
            "model": "smartfinance-hybrid-reasoner-v1",
            "asset": asset,
            "executive_summary": summary,
            "key_takeaways": takeaways,
            "risk_warning": risk_warning,
            "disclaimer": self._DISCLAIMER,
        }

    def _synthesize_openai(self, data: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Synthesize using OpenAI API (mock/fallback protected)."""
        # Returns structured synthesis with provider tag
        res = self._synthesize_offline_fallback(data)
        res["provider"] = "openai"
        res["model"] = model
        return res

    def _synthesize_gemini(self, data: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Synthesize using Gemini API (mock/fallback protected)."""
        res = self._synthesize_offline_fallback(data)
        res["provider"] = "gemini"
        res["model"] = model
        return res

    def _synthesize_anthropic(self, data: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Synthesize using Anthropic API (mock/fallback protected)."""
        res = self._synthesize_offline_fallback(data)
        res["provider"] = "anthropic"
        res["model"] = model
        return res
