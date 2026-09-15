"""
Orchestrator Module

This module implements the decision-driven Orchestrator, which dynamically coordinates
specialized AI agents (StockAgent / CryptoAgent, NewsAgent, RiskAgent, PortfolioAgent)
into a decision-driven multi-agent workflow for analyzing financial assets.

Agentic Workflow & Decision Logic
---------------------------------
1. Intent Classification:
   - STOCK_ANALYSIS       → StockAgent (required) → NewsAgent → RiskAgent → PortfolioAgent
   - CRYPTO_ANALYSIS      → CryptoAgent (required) → NewsAgent → RiskAgent → PortfolioAgent
   - GENERAL_FINANCIAL_NEWS → NewsAgent only
   - UNSUPPORTED          → Zero agents executed, clean structured error returned.

2. Decision Functions:
   - should_fetch_news(intent, news_query)
   - should_analyze_risk(intent, market_data)
   - should_generate_portfolio_recommendation(intent, market_data, risk_data, news_data)

3. Intermediate Evaluation & Failure Decisions:
   - Market Agent Failure  → HALT. RiskAgent and PortfolioAgent are NOT executed.
   - News Agent Failure    → CONTINUE to RiskAgent (market data is sufficient).
                             PortfolioAgent is SKIPPED — news context is unavailable
                             and fabricating sentiment is not acceptable for a financial
                             intelligence application.  news_data is preserved as the
                             raw failure dict; no synthetic "success" flag is injected.
   - Risk Agent Failure    → HALT. PortfolioAgent requires verified risk metrics; recommendation is NOT generated.
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
    into a decision-driven multi-agent workflow.

    All agents support dependency injection so the orchestrator is fully testable
    with mock objects without live network calls.
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
        Initialise the Orchestrator with injected or default agent instances.

        :param stock_agent:     StockAgent instance (or mock).
        :param crypto_agent:    CryptoAgent instance (or mock).
        :param news_agent:      NewsAgent instance (or mock).
        :param risk_agent:      RiskAgent instance (or mock).
        :param portfolio_agent: PortfolioAgent instance (or mock).
        """
        self.stock_agent = stock_agent or StockAgent()
        self.crypto_agent = crypto_agent or CryptoAgent()
        self.news_agent = news_agent or NewsAgent()
        self.risk_agent = risk_agent or RiskAgent()
        self.portfolio_agent = portfolio_agent or PortfolioAgent()

    # -----------------------------------------------------------------------
    # Decision Functions (Deterministic & Explainable)
    # -----------------------------------------------------------------------

    def should_fetch_news(self, intent: str, news_query: Optional[str] = None) -> bool:
        """
        Decide whether NewsAgent should be executed.

        News context is fetched for STOCK_ANALYSIS, CRYPTO_ANALYSIS, or GENERAL_FINANCIAL_NEWS
        when a valid news query string is present.
        """
        if intent not in (self.INTENT_STOCK, self.INTENT_CRYPTO, self.INTENT_NEWS):
            return False
        return bool(news_query and isinstance(news_query, str) and news_query.strip())

    def should_analyze_risk(
        self, intent: str, market_data: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Decide whether RiskAgent should be executed.

        Risk analysis requires successful market data for STOCK_ANALYSIS or CRYPTO_ANALYSIS.
        It is NOT executed for GENERAL_FINANCIAL_NEWS or when market data failed/missing.
        """
        if intent not in (self.INTENT_STOCK, self.INTENT_CRYPTO):
            return False
        if not isinstance(market_data, dict) or not market_data.get("success"):
            return False
        return True

    def should_generate_portfolio_recommendation(
        self,
        intent: str,
        market_data: Optional[Dict[str, Any]],
        risk_data: Optional[Dict[str, Any]],
        news_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Decide whether PortfolioAgent should be executed.

        Portfolio recommendation requires:
          - STOCK_ANALYSIS or CRYPTO_ANALYSIS intent
          - Successful market data
          - Successful risk analysis
          - Successful news data (PortfolioAgent uses real news sentiment; fabricating
            unavailable news as neutral is not acceptable for a financial application)

        If news_data is None or reports failure, the portfolio recommendation is skipped.
        """
        if intent not in (self.INTENT_STOCK, self.INTENT_CRYPTO):
            return False
        if not isinstance(market_data, dict) or not market_data.get("success"):
            return False
        if not isinstance(risk_data, dict) or not risk_data.get("success"):
            return False
        if not isinstance(news_data, dict) or not news_data.get("success"):
            return False
        return True

    # -----------------------------------------------------------------------
    # Internal error helper
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
        """Call StockAgent or CryptoAgent based on asset_type."""
        if asset_type == "stock":
            return self.stock_agent.analyze_stock(asset)
        else:
            return self.crypto_agent.analyze_crypto(asset)

    # -----------------------------------------------------------------------
    # Decision-Driven Intent Workflow Method
    # -----------------------------------------------------------------------

    def run_intent(self, interpreted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically route a pre-interpreted query through a decision-driven agent workflow
        evaluating intermediate outputs and recording activity telemetry.

        :param interpreted: Dict returned by QueryInterpreter.interpret().
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

        # --- UNSUPPORTED: Zero agents executed -----------------------------
        if intent == self.INTENT_UNSUPPORTED:
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
                        "decision": "News context retrieved for general news request.",
                    })
                else:
                    agent_activity.append({
                        "agent": "NewsAgent",
                        "status": "failed",
                        "order": 1,
                        "summary": f"NewsAgent failed: {news_data.get('error', 'Unknown error')}",
                        "decision": "NewsAgent returned failure response.",
                    })
            except Exception as exc:
                agent_activity.append({
                    "agent": "NewsAgent",
                    "status": "failed",
                    "order": 1,
                    "summary": f"NewsAgent error: {exc}",
                    "decision": "NewsAgent raised exception.",
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

        # --- STOCK_ANALYSIS / CRYPTO_ANALYSIS: Decision Pipeline ----------
        if intent in (self.INTENT_STOCK, self.INTENT_CRYPTO):
            asset_type = interpreted.get("asset_type", "")
            asset = interpreted.get("asset", "")
            news_query = interpreted.get("news_query") or "finance"
            agents_used = []
            agent_activity = []

            # Step 1: Execute required Market Agent
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
                    "decision": "Market agent exception; halting dependent pipeline.",
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
                    "decision": "Market data fetch failed; halting risk and portfolio agents.",
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
                "decision": "Market data verified; proceeding to news and risk evaluation.",
            })

            # Step 2: Evaluate and execute News Agent
            news_data = None
            if self.should_fetch_news(intent, news_query):
                agents_used.append("NewsAgent")
                try:
                    res_news = self.news_agent.analyze_news(query=news_query)
                    if res_news.get("success"):
                        news_data = res_news
                        agent_activity.append({
                            "agent": "NewsAgent",
                            "status": "success",
                            "order": len(agent_activity) + 1,
                            "summary": f"Financial news sentiment evaluated ({news_data.get('overall_sentiment', 'neutral')})",
                            "decision": "News sentiment integrated into pipeline.",
                        })
                    else:
                        news_data = res_news  # preserve real failure dict — no fabrication
                        agent_activity.append({
                            "agent": "NewsAgent",
                            "status": "failed",
                            "order": len(agent_activity) + 1,
                            "summary": f"NewsAgent failed: {res_news.get('error', 'News agent returned a failure response.')}",
                            "decision": (
                                "NewsAgent failed; news context is unavailable. "
                                "Continuing to RiskAgent. "
                                "PortfolioAgent will be skipped — fabricating news sentiment is not acceptable."
                            ),
                        })
                except Exception as exc:
                    news_data = {"success": False, "agent": "NewsAgent", "error": str(exc)}
                    agent_activity.append({
                        "agent": "NewsAgent",
                        "status": "failed",
                        "order": len(agent_activity) + 1,
                        "summary": f"NewsAgent error: {exc}",
                        "decision": (
                            "NewsAgent raised an exception; news context is unavailable. "
                            "Continuing to RiskAgent. "
                            "PortfolioAgent will be skipped — fabricating news sentiment is not acceptable."
                        ),
                    })

            # Step 3: Evaluate and execute Risk Agent
            risk_data = None
            if self.should_analyze_risk(intent, market_data):
                agents_used.append("RiskAgent")
                try:
                    res_risk = self.risk_agent.analyze_risk(market_data)
                    if res_risk.get("success"):
                        risk_data = res_risk
                        agent_activity.append({
                            "agent": "RiskAgent",
                            "status": "success",
                            "order": len(agent_activity) + 1,
                            "summary": f"Risk score evaluated: {risk_data.get('risk_score', 0)} ({risk_data.get('risk_level', 'unknown')})",
                            "decision": "Risk metrics verified; proceeding to portfolio recommendation.",
                        })
                    else:
                        agent_activity.append({
                            "agent": "RiskAgent",
                            "status": "failed",
                            "order": len(agent_activity) + 1,
                            "summary": f"RiskAgent failed: {res_risk.get('error', 'Risk agent returned a failure response.')}",
                            "decision": "Risk analysis failed; halting portfolio recommendation as risk metrics are required.",
                        })
                        return {
                            "success": False,
                            "agent": "Orchestrator",
                            "intent": intent,
                            "agents_used": agents_used,
                            "agent_activity": agent_activity,
                            "step": "risk_agent",
                            "error": res_risk.get("error", "Risk agent returned a failure response."),
                            "market_data": market_data,
                            "news_data": news_data,
                            "risk_data": res_risk,
                        }
                except Exception as exc:
                    agent_activity.append({
                        "agent": "RiskAgent",
                        "status": "failed",
                        "order": len(agent_activity) + 1,
                        "summary": f"RiskAgent error: {exc}",
                        "decision": "RiskAgent exception; halting portfolio recommendation.",
                    })
                    return {
                        "success": False,
                        "agent": "Orchestrator",
                        "intent": intent,
                        "agents_used": agents_used,
                        "agent_activity": agent_activity,
                        "error": f"Risk agent raised an unexpected error: {exc}",
                    }

            # Step 4: Evaluate and execute Portfolio Agent
            recommendation = None
            if self.should_generate_portfolio_recommendation(intent, market_data, risk_data, news_data):
                agents_used.append("PortfolioAgent")
                try:
                    res_rec = self.portfolio_agent.generate_recommendation(
                        market_data=market_data,
                        risk_data=risk_data,
                        news_data=news_data,
                    )
                    if res_rec.get("success"):
                        recommendation = res_rec
                        agent_activity.append({
                            "agent": "PortfolioAgent",
                            "status": "success",
                            "order": len(agent_activity) + 1,
                            "summary": f"Recommendation generated: {recommendation.get('recommendation', 'unknown').upper()}",
                            "decision": "Recommendation synthesized from market, risk, and news outputs.",
                        })
                    else:
                        agent_activity.append({
                            "agent": "PortfolioAgent",
                            "status": "failed",
                            "order": len(agent_activity) + 1,
                            "summary": f"PortfolioAgent failed: {res_rec.get('error', 'Portfolio agent returned a failure response.')}",
                            "decision": "Portfolio recommendation failed.",
                        })
                        return {
                            "success": False,
                            "agent": "Orchestrator",
                            "intent": intent,
                            "agents_used": agents_used,
                            "agent_activity": agent_activity,
                            "step": "portfolio_agent",
                            "error": res_rec.get("error", "Portfolio agent returned a failure response."),
                            "market_data": market_data,
                            "news_data": news_data,
                            "risk_data": risk_data,
                            "recommendation": res_rec,
                        }
                except Exception as exc:
                    agent_activity.append({
                        "agent": "PortfolioAgent",
                        "status": "failed",
                        "order": len(agent_activity) + 1,
                        "summary": f"PortfolioAgent error: {exc}",
                        "decision": "PortfolioAgent exception.",
                    })
                    return {
                        "success": False,
                        "agent": "Orchestrator",
                        "intent": intent,
                        "agents_used": agents_used,
                        "agent_activity": agent_activity,
                        "error": f"Portfolio agent raised an unexpected error: {exc}",
                    }

            # Build successful response
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
                "summary": recommendation.get("summary", "") if recommendation else "",
                "disclaimer": recommendation.get(
                    "disclaimer",
                    "This is a software-generated educational recommendation, not financial advice.",
                ) if recommendation else "",
            }

        # --- UNSUPPORTED FALLBACK ------------------------------------------
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
    # Main run() method (Delegates to decision-driven run_intent)
    # -----------------------------------------------------------------------

    def run(
        self,
        asset_type: str,
        asset: str,
        news_query: str = "finance",
    ) -> Dict[str, Any]:
        """
        Run the decision-driven financial analysis workflow.

        :param asset_type: "stock" or "crypto" (case-insensitive).
        :param asset:      Stock ticker (e.g. "AAPL") or crypto coin ID (e.g. "bitcoin").
        :param news_query: Search query forwarded to NewsAgent (defaults to "finance").
        :return: Structured analysis result dictionary.
        """
        if not isinstance(asset_type, str) or not asset_type.strip():
            return self._error(
                "asset_type must be a non-empty string ('stock' or 'crypto')."
            )

        if not isinstance(asset, str) or not asset.strip():
            return self._error(
                "asset must be a non-empty string (ticker symbol or coin ID)."
            )

        clean_asset_type = asset_type.strip().lower()
        clean_asset = asset.strip()
        clean_query = (
            news_query.strip()
            if isinstance(news_query, str) and news_query.strip()
            else "finance"
        )

        if clean_asset_type not in self._SUPPORTED_ASSET_TYPES:
            return self._error(
                f"Unsupported asset_type: '{clean_asset_type}'. "
                f"Supported types: {sorted(self._SUPPORTED_ASSET_TYPES)}."
            )

        interpreted = {
            "success": True,
            "intent": self.INTENT_STOCK if clean_asset_type == "stock" else self.INTENT_CRYPTO,
            "asset_type": clean_asset_type,
            "asset": clean_asset,
            "news_query": clean_query,
        }

        return self.run_intent(interpreted)
