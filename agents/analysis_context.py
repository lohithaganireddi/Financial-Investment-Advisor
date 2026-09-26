"""
Analysis Context Module

This module defines the AnalysisContext dataclass, which represents the shared
decision state that flows through the Orchestrator's multi-agent pipeline.

The context is created at the start of each analysis request and progressively
updated after each agent executes.  Downstream decision helpers read directly
from the context rather than relying on isolated local variables, making the
agent-to-agent information flow explicit, inspectable, and easy to test.

Design Principles
-----------------
- Pure Python stdlib only (dataclasses + typing).  No new dependencies.
- All agent outputs are stored truthfully.  No synthetic data is ever injected.
- A failed-agent result is stored as the raw failure dict (success=False).
- The context is an internal orchestration detail; it is NOT serialised into
  the API response verbatim.  Only the fields the API already returns are
  exposed via to_response_dict().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AnalysisContext:
    """
    Shared analysis state that flows through the Orchestrator pipeline.

    Fields
    ------
    intent          Orchestrator intent constant (e.g. 'STOCK_ANALYSIS').
    asset_type      'stock' or 'crypto' (lower-case).
    asset           Ticker symbol or coin ID (e.g. 'AAPL', 'bitcoin').
    original_query  Raw user query string (empty for direct /api/analyze calls).
    news_query      Search string forwarded to NewsAgent.

    market_data     Output from StockAgent or CryptoAgent; None if not yet run.
    news_data       Output from NewsAgent; None if not yet run.
    risk_data       Output from RiskAgent; None if not yet run.
    portfolio_data  Output from PortfolioAgent; None if not yet run.

    agents_used     Ordered list of agent names that were invoked.
    agent_activity  Ordered list of activity dicts (one per agent invocation).
    decisions       Human-readable log of orchestrator decision rationales.
    """

    # --- Routing & identity -------------------------------------------------
    intent: str = ""
    asset_type: str = ""
    asset: str = ""
    original_query: str = ""
    news_query: str = ""

    # --- Agent outputs (None = agent was not yet invoked) -------------------
    market_data: Optional[Dict[str, Any]] = None
    news_data: Optional[Dict[str, Any]] = None
    risk_data: Optional[Dict[str, Any]] = None
    portfolio_data: Optional[Dict[str, Any]] = None

    # --- Execution trace ----------------------------------------------------
    agents_used: List[str] = field(default_factory=list)
    agent_activity: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)

    # --- Evolving Decision State (Day 31) -----------------------------------
    market_summary: Optional[str] = None
    news_summary: Optional[str] = None
    risk_summary: Optional[str] = None
    recommendation_summary: Optional[str] = None

    decision_flags: Dict[str, bool] = field(default_factory=dict)
    confidence_factors: List[str] = field(default_factory=list)

    # -----------------------------------------------------------------------
    # Status helpers
    # -----------------------------------------------------------------------

    def market_succeeded(self) -> bool:
        """Return True if the market agent ran and its output reports success."""
        return isinstance(self.market_data, dict) and bool(self.market_data.get("success"))

    def news_succeeded(self) -> bool:
        """Return True if the news agent ran and its output reports success."""
        return isinstance(self.news_data, dict) and bool(self.news_data.get("success"))

    def risk_succeeded(self) -> bool:
        """Return True if the risk agent ran and its output reports success."""
        return isinstance(self.risk_data, dict) and bool(self.risk_data.get("success"))

    def portfolio_succeeded(self) -> bool:
        """Return True if the portfolio agent ran and its output reports success."""
        return isinstance(self.portfolio_data, dict) and bool(self.portfolio_data.get("success"))

    def update_decision_flags(self) -> Dict[str, bool]:
        """
        Dynamically populate deterministic decision flags based on actual upstream agent outputs.
        Only flags for which valid data exists are created.
        """
        flags: Dict[str, bool] = {}

        if self.market_succeeded():
            direction = str(self.market_data.get("market_direction", "")).lower()
            if direction == "bullish":
                flags["market_bullish"] = True
            elif direction == "bearish":
                flags["market_bearish"] = True
            elif direction == "neutral":
                flags["market_neutral"] = True

        if self.news_succeeded():
            sentiment = str(self.news_data.get("overall_sentiment", "")).lower()
            if sentiment == "positive":
                flags["news_positive"] = True
            elif sentiment == "negative":
                flags["news_negative"] = True
            elif sentiment == "neutral":
                flags["news_neutral"] = True

        if self.risk_succeeded():
            risk_lvl = str(self.risk_data.get("risk_level", "")).lower()
            if risk_lvl == "high":
                flags["high_risk"] = True
            elif risk_lvl == "medium":
                flags["medium_risk"] = True
            elif risk_lvl == "low":
                flags["low_risk"] = True

        if self.intent in ("STOCK_ANALYSIS", "CRYPTO_ANALYSIS"):
            if self.market_succeeded() and self.risk_succeeded() and self.news_succeeded():
                flags["recommendation_allowed"] = True
                flags["recommendation_blocked"] = False
            else:
                flags["recommendation_allowed"] = False
                flags["recommendation_blocked"] = True

        self.decision_flags = flags
        return flags

    # -----------------------------------------------------------------------
    # Activity recording
    # -----------------------------------------------------------------------

    def record_activity(
        self,
        agent: str,
        status: str,
        summary: str,
        decision: str,
        duration_ms: Optional[int] = None,
    ) -> None:
        """
        Append a structured activity entry to agent_activity.

        :param agent:       Name of the agent (e.g. 'StockAgent').
        :param status:      'success' or 'failed'.
        :param summary:     Human-readable one-line result summary.
        :param decision:    Orchestrator rationale for this step.
        :param duration_ms: Optional wall-clock execution time in milliseconds.
        """
        entry: Dict[str, Any] = {
            "agent": agent,
            "status": status,
            "order": len(self.agent_activity) + 1,
            "summary": summary,
            "decision": decision,
        }
        if duration_ms is not None:
            entry["duration_ms"] = duration_ms
        self.agent_activity.append(entry)

    def log_decision(self, rationale: str) -> None:
        """Append a plain-text rationale string to the decisions log."""
        self.decisions.append(rationale)

    # -----------------------------------------------------------------------
    # Response serialisation
    # -----------------------------------------------------------------------

    def to_response_dict(self) -> Dict[str, Any]:
        """
        Produce the standard Orchestrator response dictionary from the context.

        Only fields already returned by the existing API are included so the
        API contract remains unchanged.  Internal fields such as ``decisions``
        are intentionally omitted from the public response.
        """
        recommendation = self.portfolio_data if self.portfolio_succeeded() else None
        return {
            "success": True,
            "agent": "Orchestrator",
            "intent": self.intent,
            "asset": self.asset,
            "asset_type": self.asset_type,
            "agents_used": list(self.agents_used),
            "agent_activity": list(self.agent_activity),
            "market_data": self.market_data,
            "news_data": self.news_data,
            "risk_data": self.risk_data,
            "recommendation": recommendation,
            "summary": recommendation.get("summary", "") if recommendation else "",
            "disclaimer": (
                recommendation.get(
                    "disclaimer",
                    "This is a software-generated educational recommendation, not financial advice.",
                )
                if recommendation
                else ""
            ),
        }
