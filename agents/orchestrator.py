"""
Orchestrator Module

This module implements the Orchestrator, which coordinates the existing agents
into a single end-to-end workflow for analysing a financial asset.

Workflow
--------
For a "stock" request (run / run_intent with STOCK_ANALYSIS):
    1. StockAgent.analyze_stock(asset)
    2. NewsAgent.analyze_news(news_query)
    3. RiskAgent.analyze_risk(market_data)
    4. PortfolioAgent.generate_recommendation(market_data, risk_data, news_data)

For a "crypto" request (run / run_intent with CRYPTO_ANALYSIS):
    1. CryptoAgent.analyze_crypto(asset)
    2. NewsAgent.analyze_news(news_query)
    3. RiskAgent.analyze_risk(market_data)
    4. PortfolioAgent.generate_recommendation(market_data, risk_data, news_data)

For a "general financial news" request (run_intent with GENERAL_FINANCIAL_NEWS):
    1. NewsAgent.analyze_news(news_query) only.
       StockAgent, CryptoAgent, RiskAgent, and PortfolioAgent are NOT called.

The orchestrator NEVER calls Alpha Vantage, CoinGecko, or NewsData directly.
All external work is delegated to the agents.
"""

from typing import Any, Dict, Optional

from agents.stock_agent import StockAgent
from agents.crypto_agent import CryptoAgent
from agents.news_agent import NewsAgent
from agents.risk_agent import RiskAgent
from agents.portfolio_agent import PortfolioAgent


class Orchestrator:
    """
    Coordinates StockAgent / CryptoAgent, NewsAgent, RiskAgent, and PortfolioAgent
    into a single end-to-end analysis workflow.

    All agents support dependency injection so the orchestrator is fully testable
    with mock objects — no real API calls are ever made during tests.
    """

    # Supported asset types accepted by the run() method
    _SUPPORTED_ASSET_TYPES = {"stock", "crypto"}

    # Intent constants — must match QueryInterpreter intent values exactly
    INTENT_STOCK = "STOCK_ANALYSIS"
    INTENT_CRYPTO = "CRYPTO_ANALYSIS"
    INTENT_NEWS = "GENERAL_FINANCIAL_NEWS"
    INTENT_UNSUPPORTED = "UNSUPPORTED"

    def __init__(
        self,
        stock_agent: Optional[StockAgent] = None,
        crypto_agent: Optional[CryptoAgent] = None,
        news_agent: Optional[NewsAgent] = None,
        risk_agent: Optional[RiskAgent] = None,
        portfolio_agent: Optional[PortfolioAgent] = None,
    ):
        """
        Initialise the Orchestrator.

        All agent parameters are optional.  When omitted, each agent is
        instantiated with its own default service.  Passing pre-built (or mock)
        agents makes the orchestrator easy to test without live API keys.

        :param stock_agent:     StockAgent instance (or mock).
        :param crypto_agent:    CryptoAgent instance (or mock).
        :param news_agent:      NewsAgent instance (or mock).
        :param risk_agent:      RiskAgent instance (or mock).
        :param portfolio_agent: PortfolioAgent instance (or mock).
        """
        self.stock_agent     = stock_agent     or StockAgent()
        self.crypto_agent    = crypto_agent    or CryptoAgent()
        self.news_agent      = news_agent      or NewsAgent()
        self.risk_agent      = risk_agent      or RiskAgent()
        self.portfolio_agent = portfolio_agent or PortfolioAgent()

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _error(self, message: str) -> Dict[str, Any]:
        """Return a standardised failure response."""
        return {
            "success": False,
            "agent": "Orchestrator",
            "error": message,
        }

    def _run_market_agent(
        self, asset_type: str, asset: str
    ) -> Dict[str, Any]:
        """
        Call the appropriate market agent (StockAgent or CryptoAgent).

        :param asset_type: "stock" or "crypto".
        :param asset:      Ticker symbol or coin ID.
        :return:           Agent result dict.
        """
        if asset_type == "stock":
            return self.stock_agent.analyze_stock(asset)
        else:
            return self.crypto_agent.analyze_crypto(asset)

    # -----------------------------------------------------------------------
    # Intent-based dynamic routing method (Day 20 / Day 21 Activity Tracking)
    # -----------------------------------------------------------------------

    def run_intent(self, interpreted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically route a pre-interpreted query to the appropriate agent pipeline
        based on the intent produced by QueryInterpreter, tracking agent activity.

        Intent routing rules
        --------------------
        STOCK_ANALYSIS       → StockAgent → NewsAgent → RiskAgent → PortfolioAgent
        CRYPTO_ANALYSIS      → CryptoAgent → NewsAgent → RiskAgent → PortfolioAgent
        GENERAL_FINANCIAL_NEWS → NewsAgent only (no market, risk, or portfolio agents)
        UNSUPPORTED / other  → Clean structured error, no agents called

        :param interpreted: Dict returned by QueryInterpreter.interpret(), which must
                            contain at least: intent, success, asset_type, asset,
                            news_query.
        :return: Structured response dict including ``agents_used`` and ``agent_activity``.
        """
        if not isinstance(interpreted, dict):
            return {
                "success": False,
                "agent": "Orchestrator",
                "intent": self.INTENT_UNSUPPORTED,
                "agents_used": [],
                "agent_activity": [],
                "error": "run_intent() requires a dict produced by QueryInterpreter.",
            }

        intent = interpreted.get("intent", self.INTENT_UNSUPPORTED)

        # --- GENERAL_FINANCIAL_NEWS: NewsAgent only -------------------------
        if intent == self.INTENT_NEWS:
            news_query = interpreted.get("news_query") or "finance"
            agents_used = ["NewsAgent"]
            agent_activity = []
            try:
                news_data = self.news_agent.analyze_news(query=news_query)
                if news_data.get("success"):
                    agent_activity.append({
                        "agent": "NewsAgent",
                        "status": "success",
                        "order": 1,
                        "summary": f"Financial news analysis completed for query '{news_query}'",
                    })
                else:
                    agent_activity.append({
                        "agent": "NewsAgent",
                        "status": "failed",
                        "order": 1,
                        "summary": f"NewsAgent failed: {news_data.get('error', 'Unknown error')}",
                    })
            except Exception as exc:
                agent_activity.append({
                    "agent": "NewsAgent",
                    "status": "failed",
                    "order": 1,
                    "summary": f"NewsAgent error: {exc}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "error": f"News agent raised an unexpected error: {exc}",
                }

            return {
                "success": news_data.get("success", False),
                "agent": "Orchestrator",
                "intent": intent,
                "agents_used": agents_used,
                "agent_activity": agent_activity,
                "news_data": news_data,
                "summary": news_data.get("summary", ""),
                "disclaimer": (
                    "This is a software-generated financial news summary, not financial advice."
                ),
                **(
                    {"error": news_data.get("error", "NewsAgent returned a failure response.")}
                    if not news_data.get("success")
                    else {}
                ),
            }

        # --- STOCK_ANALYSIS / CRYPTO_ANALYSIS: full 4-agent pipeline --------
        if intent in (self.INTENT_STOCK, self.INTENT_CRYPTO):
            asset_type = interpreted.get("asset_type", "")
            asset = interpreted.get("asset", "")
            news_query = interpreted.get("news_query") or "finance"
            agents_used = []
            agent_activity = []

            # Step 1: Market agent
            market_agent_name = "StockAgent" if asset_type == "stock" else "CryptoAgent"
            agents_used.append(market_agent_name)
            try:
                market_data = self._run_market_agent(asset_type, asset)
            except Exception as exc:
                agent_activity.append({
                    "agent": market_agent_name,
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"{market_agent_name} error: {exc}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "error": f"Market agent raised an unexpected error: {exc}",
                }

            if not market_data.get("success"):
                agent_activity.append({
                    "agent": market_agent_name,
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"{market_agent_name} failed: {market_data.get('error', 'Market agent returned a failure response.')}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "step": "market_agent",
                    "error": market_data.get("error", "Market agent returned a failure response."),
                    "market_data": market_data,
                }

            agent_activity.append({
                "agent": market_agent_name,
                "status": "success",
                "order": len(agent_activity) + 1,
                "summary": f"{asset} market analysis completed",
            })

            # Step 2: News agent
            agents_used.append("NewsAgent")
            try:
                news_data = self.news_agent.analyze_news(query=news_query)
            except Exception as exc:
                agent_activity.append({
                    "agent": "NewsAgent",
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"NewsAgent error: {exc}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "error": f"News agent raised an unexpected error: {exc}",
                }

            if not news_data.get("success"):
                agent_activity.append({
                    "agent": "NewsAgent",
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"NewsAgent failed: {news_data.get('error', 'News agent returned a failure response.')}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "step": "news_agent",
                    "error": news_data.get("error", "News agent returned a failure response."),
                    "market_data": market_data,
                    "news_data": news_data,
                }

            agent_activity.append({
                "agent": "NewsAgent",
                "status": "success",
                "order": len(agent_activity) + 1,
                "summary": f"Financial news sentiment evaluated ({news_data.get('overall_sentiment', 'neutral')})",
            })

            # Step 3: Risk agent
            agents_used.append("RiskAgent")
            try:
                risk_data = self.risk_agent.analyze_risk(market_data)
            except Exception as exc:
                agent_activity.append({
                    "agent": "RiskAgent",
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"RiskAgent error: {exc}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "error": f"Risk agent raised an unexpected error: {exc}",
                }

            if not risk_data.get("success"):
                agent_activity.append({
                    "agent": "RiskAgent",
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"RiskAgent failed: {risk_data.get('error', 'Risk agent returned a failure response.')}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "step": "risk_agent",
                    "error": risk_data.get("error", "Risk agent returned a failure response."),
                    "market_data": market_data,
                    "news_data": news_data,
                    "risk_data": risk_data,
                }

            agent_activity.append({
                "agent": "RiskAgent",
                "status": "success",
                "order": len(agent_activity) + 1,
                "summary": f"Risk score evaluated: {risk_data.get('risk_score', 0)} ({risk_data.get('risk_level', 'unknown')})",
            })

            # Step 4: Portfolio agent
            agents_used.append("PortfolioAgent")
            try:
                recommendation = self.portfolio_agent.generate_recommendation(
                    market_data=market_data,
                    risk_data=risk_data,
                    news_data=news_data,
                )
            except Exception as exc:
                agent_activity.append({
                    "agent": "PortfolioAgent",
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"PortfolioAgent error: {exc}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "error": f"Portfolio agent raised an unexpected error: {exc}",
                }

            if not recommendation.get("success"):
                agent_activity.append({
                    "agent": "PortfolioAgent",
                    "status": "failed",
                    "order": len(agent_activity) + 1,
                    "summary": f"PortfolioAgent failed: {recommendation.get('error', 'Portfolio agent returned a failure response.')}",
                })
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": agents_used,
                    "agent_activity": agent_activity,
                    "step": "portfolio_agent",
                    "error": recommendation.get("error", "Portfolio agent returned a failure response."),
                    "market_data": market_data,
                    "news_data": news_data,
                    "risk_data": risk_data,
                    "recommendation": recommendation,
                }

            agent_activity.append({
                "agent": "PortfolioAgent",
                "status": "success",
                "order": len(agent_activity) + 1,
                "summary": f"Recommendation generated: {recommendation.get('recommendation', 'unknown').upper()}",
            })

            # Build successful full-pipeline response
            return {
                "success": True,
                "agent": "Orchestrator",
                "intent": intent,
                "agents_used": agents_used,
                "agent_activity": agent_activity,
                "asset": asset,
                "asset_type": asset_type,
                "market_data": market_data,
                "news_data": news_data,
                "risk_data": risk_data,
                "recommendation": recommendation,
                "summary": recommendation.get("summary", ""),
                "disclaimer": recommendation.get(
                    "disclaimer",
                    "This is a software-generated educational recommendation, not financial advice.",
                ),
            }

        # --- UNSUPPORTED / UNKNOWN -------------------------------------------
        return {
            "success": False,
            "agent": "Orchestrator",
            "intent": intent,
            "agents_used": [],
            "agent_activity": [],
            "error": interpreted.get(
                "error",
                "Unsupported or unrecognised intent. No financial agents were executed.",
            ),
        }


    # -----------------------------------------------------------------------
    # Main orchestration method
    # -----------------------------------------------------------------------

    def run(
        self,
        asset_type: str,
        asset: str,
        news_query: str = "finance",
    ) -> Dict[str, Any]:
        """
        Run the full end-to-end financial analysis workflow.

        :param asset_type:  "stock" or "crypto" (case-insensitive).
        :param asset:       Stock ticker (e.g. "AAPL") or crypto coin ID
                            (e.g. "bitcoin").  Whitespace is stripped.
        :param news_query:  Search query forwarded to NewsAgent (defaults to
                            "finance").
        :return: Structured dict containing market_data, news_data, risk_data,
                 recommendation, and a top-level summary, or an error dict on
                 any failure.
        """
        # --- Input validation -------------------------------------------
        if not isinstance(asset_type, str) or not asset_type.strip():
            return self._error(
                "asset_type must be a non-empty string ('stock' or 'crypto')."
            )

        if not isinstance(asset, str) or not asset.strip():
            return self._error(
                "asset must be a non-empty string (ticker symbol or coin ID)."
            )

        clean_asset_type = asset_type.strip().lower()
        clean_asset      = asset.strip()
        clean_query      = news_query.strip() if isinstance(news_query, str) and news_query.strip() else "finance"

        if clean_asset_type not in self._SUPPORTED_ASSET_TYPES:
            return self._error(
                f"Unsupported asset_type: '{clean_asset_type}'. "
                f"Supported types: {sorted(self._SUPPORTED_ASSET_TYPES)}."
            )

        # --- Step 1: Market agent (Stock or Crypto) -------------------------
        try:
            market_data = self._run_market_agent(clean_asset_type, clean_asset)
        except Exception as exc:
            return self._error(f"Market agent raised an unexpected error: {exc}")

        if not market_data.get("success"):
            return {
                "success": False,
                "agent": "Orchestrator",
                "step": "market_agent",
                "error": market_data.get("error", "Market agent returned a failure response."),
                "market_data": market_data,
            }

        # --- Step 2: News agent --------------------------------------------
        try:
            news_data = self.news_agent.analyze_news(query=clean_query)
        except Exception as exc:
            return self._error(f"News agent raised an unexpected error: {exc}")

        if not news_data.get("success"):
            return {
                "success": False,
                "agent": "Orchestrator",
                "step": "news_agent",
                "error": news_data.get("error", "News agent returned a failure response."),
                "market_data": market_data,
                "news_data": news_data,
            }

        # --- Step 3: Risk agent --------------------------------------------
        try:
            risk_data = self.risk_agent.analyze_risk(market_data)
        except Exception as exc:
            return self._error(f"Risk agent raised an unexpected error: {exc}")

        if not risk_data.get("success"):
            return {
                "success": False,
                "agent": "Orchestrator",
                "step": "risk_agent",
                "error": risk_data.get("error", "Risk agent returned a failure response."),
                "market_data": market_data,
                "news_data": news_data,
                "risk_data": risk_data,
            }

        # --- Step 4: Portfolio agent ---------------------------------------
        try:
            recommendation = self.portfolio_agent.generate_recommendation(
                market_data=market_data,
                risk_data=risk_data,
                news_data=news_data,
            )
        except Exception as exc:
            return self._error(f"Portfolio agent raised an unexpected error: {exc}")

        if not recommendation.get("success"):
            return {
                "success": False,
                "agent": "Orchestrator",
                "step": "portfolio_agent",
                "error": recommendation.get("error", "Portfolio agent returned a failure response."),
                "market_data": market_data,
                "news_data": news_data,
                "risk_data": risk_data,
                "recommendation": recommendation,
            }

        # --- Build final successful response --------------------------------
        return {
            "success": True,
            "agent": "Orchestrator",
            "asset": clean_asset,
            "asset_type": clean_asset_type,
            "market_data": market_data,
            "news_data": news_data,
            "risk_data": risk_data,
            "recommendation": recommendation,
            "summary": recommendation.get("summary", ""),
            "disclaimer": recommendation.get(
                "disclaimer",
                "This is a software-generated educational recommendation, not financial advice.",
            ),
        }
