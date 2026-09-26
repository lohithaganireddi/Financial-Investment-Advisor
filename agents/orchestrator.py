"""
Orchestrator Module

This module implements the decision-driven Orchestrator, which dynamically coordinates
specialized AI agents (StockAgent / CryptoAgent, NewsAgent, RiskAgent, PortfolioAgent)
into a decision-driven multi-agent workflow for analyzing financial assets.

Architecture (Day 29)
---------------------
An AnalysisContext is created at the start of each run_intent() call.
The context is passed by reference through the pipeline; each agent execution
updates it with its result.  Downstream decision functions read from the context,
making the agent-to-agent information flow explicit and testable.

Agentic Workflow & Decision Logic
---------------------------------
1. Intent Classification:
   - STOCK_ANALYSIS         -> StockAgent (required) -> NewsAgent -> RiskAgent -> PortfolioAgent
   - CRYPTO_ANALYSIS        -> CryptoAgent (required) -> NewsAgent -> RiskAgent -> PortfolioAgent
   - GENERAL_FINANCIAL_NEWS -> NewsAgent only
   - UNSUPPORTED            -> Zero agents executed; clean structured error returned.

2. Decision Functions (deterministic, read from AnalysisContext):
   - should_fetch_news(intent, news_query)
   - should_analyze_risk(intent, market_data)
   - should_generate_portfolio_recommendation(intent, market_data, risk_data, news_data)

3. Failure Handling:
   - Market Agent Failure -> HALT. RiskAgent and PortfolioAgent are NOT executed.
   - News Agent Failure   -> CONTINUE to RiskAgent (market data is sufficient).
                             PortfolioAgent is SKIPPED - news context is unavailable
                             and fabricating sentiment is not acceptable for a financial
                             intelligence application.  news_data is preserved as the
                             raw failure dict; no synthetic success flag is injected.
   - Risk Agent Failure   -> HALT. PortfolioAgent requires verified risk metrics.
"""

import time
from typing import Any, Dict, Optional

from agents.analysis_context import AnalysisContext
from agents.stock_agent import StockAgent
from agents.crypto_agent import CryptoAgent
from agents.news_agent import NewsAgent
from agents.risk_agent import RiskAgent
from agents.portfolio_agent import PortfolioAgent


class Orchestrator:
    """
    Coordinates StockAgent / CryptoAgent, NewsAgent, RiskAgent, and PortfolioAgent
    into a decision-driven multi-agent workflow backed by a shared AnalysisContext.

    All agents support dependency injection so the orchestrator is fully testable
    with mock objects without live network calls.
    """

    # Supported asset types accepted by the run() method
    _SUPPORTED_ASSET_TYPES = {"stock", "crypto"}

    # Intent constants - must match QueryInterpreter intent values exactly
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
    # Context-aware decision helpers (read from AnalysisContext)
    # -----------------------------------------------------------------------

    def _ctx_should_fetch_news(self, ctx: AnalysisContext) -> bool:
        """Context-aware wrapper around should_fetch_news."""
        return self.should_fetch_news(ctx.intent, ctx.news_query)

    def _ctx_should_analyze_risk(self, ctx: AnalysisContext) -> bool:
        """Context-aware wrapper around should_analyze_risk."""
        return self.should_analyze_risk(ctx.intent, ctx.market_data)

    def _ctx_should_generate_portfolio(self, ctx: AnalysisContext) -> bool:
        """Context-aware wrapper around should_generate_portfolio_recommendation."""
        return self.should_generate_portfolio_recommendation(
            ctx.intent, ctx.market_data, ctx.risk_data, ctx.news_data
        )

    # -----------------------------------------------------------------------
    # Decision-Driven Intent Workflow Method
    # -----------------------------------------------------------------------

    def run_intent(self, interpreted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically route a pre-interpreted query through a decision-driven agent workflow,
        updating a shared AnalysisContext after each step.

        :param interpreted: Dict returned by QueryInterpreter.interpret().
        :return: Structured response dict including agents_used and agent_activity.
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
            ctx = AnalysisContext(
                intent=intent,
                news_query=news_query,
                original_query=interpreted.get("query", ""),
            )
            ctx.agents_used.append("NewsAgent")
            t0 = time.monotonic()
            try:
                news_data = self.news_agent.analyze_news(query=news_query)
                duration_ms = int((time.monotonic() - t0) * 1000)
                ctx.news_data = news_data
                if news_data.get("success"):
                    ctx.record_activity(
                        agent="NewsAgent",
                        status="success",
                        summary=f"Financial news analysis completed for query '{news_query}'",
                        decision="News context retrieved for general news request.",
                        duration_ms=duration_ms,
                    )
                else:
                    ctx.record_activity(
                        agent="NewsAgent",
                        status="failed",
                        summary=f"NewsAgent failed: {news_data.get('error', 'Unknown error')}",
                        decision="NewsAgent returned failure response.",
                        duration_ms=duration_ms,
                    )
            except Exception as exc:
                duration_ms = int((time.monotonic() - t0) * 1000)
                ctx.news_data = {"success": False, "agent": "NewsAgent", "error": str(exc)}
                ctx.record_activity(
                    agent="NewsAgent",
                    status="failed",
                    summary=f"NewsAgent error: {exc}",
                    decision="NewsAgent raised exception.",
                    duration_ms=duration_ms,
                )
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": ctx.agents_used,
                    "agent_activity": ctx.agent_activity,
                    "error": f"News agent raised an unexpected error: {exc}",
                }

            news_data = ctx.news_data
            return {
                "success": news_data.get("success", False),
                "agent": "Orchestrator",
                "intent": intent,
                "agents_used": ctx.agents_used,
                "agent_activity": ctx.agent_activity,
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

            # Initialise shared context for this analysis run
            ctx = AnalysisContext(
                intent=intent,
                asset_type=asset_type,
                asset=asset,
                news_query=news_query,
                original_query=interpreted.get("query", ""),
            )
            ctx.log_decision(f"Intent resolved to {intent}; beginning decision-driven pipeline for asset '{asset}'.")

            market_agent_name = "StockAgent" if asset_type == "stock" else "CryptoAgent"
            ctx.agents_used.append(market_agent_name)
            ctx.log_decision(f"Executing market analysis via {market_agent_name}.")

            # Step 1: Execute required Market Agent -------------------------
            t0 = time.monotonic()
            try:
                market_data = self._run_market_agent(asset_type, asset)
                duration_ms = int((time.monotonic() - t0) * 1000)
            except Exception as exc:
                duration_ms = int((time.monotonic() - t0) * 1000)
                ctx.update_decision_flags()
                ctx.record_activity(
                    agent=market_agent_name,
                    status="failed",
                    summary=f"{market_agent_name} error: {exc}",
                    decision="Market agent exception; halting dependent pipeline.",
                    duration_ms=duration_ms,
                )
                ctx.log_decision(f"{market_agent_name} raised exception: {exc}. Halting pipeline.")
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": ctx.agents_used,
                    "agent_activity": ctx.agent_activity,
                    "error": f"Market agent raised an unexpected error: {exc}",
                }

            ctx.market_data = market_data

            if not ctx.market_succeeded():
                ctx.update_decision_flags()
                ctx.record_activity(
                    agent=market_agent_name,
                    status="failed",
                    summary=f"{market_agent_name} failed: {market_data.get('error', 'Market agent returned a failure response.')}",
                    decision="Market data fetch failed; halting risk and portfolio agents.",
                    duration_ms=duration_ms,
                )
                ctx.log_decision(f"{market_agent_name} failed. Halting risk and portfolio analysis.")
                return {
                    "success": False,
                    "agent": "Orchestrator",
                    "intent": intent,
                    "agents_used": ctx.agents_used,
                    "agent_activity": ctx.agent_activity,
                    "step": "market_agent",
                    "error": market_data.get("error", "Market agent returned a failure response."),
                    "market_data": market_data,
                }

            ctx.market_summary = market_data.get("analysis", "")
            ctx.update_decision_flags()

            direction = market_data.get("market_direction", "unknown")
            chg_pct = market_data.get("change_percent", 0.0) if asset_type == "stock" else market_data.get("change_percent_24h", 0.0)

            ctx.record_activity(
                agent=market_agent_name,
                status="success",
                summary=f"{asset} market analysis completed ({direction})",
                decision=f"Market analysis succeeded with {direction} direction ({chg_pct:+.2f}% change). Proceeding to news and risk evaluation.",
                duration_ms=duration_ms,
            )
            ctx.log_decision(f"{market_agent_name} succeeded ({direction}). Market decision flags updated.")

            # Step 2: Context-driven News Agent decision --------------------
            if self._ctx_should_fetch_news(ctx):
                ctx.agents_used.append("NewsAgent")
                ctx.log_decision(f"News fetch enabled for query '{news_query}'. Invoking NewsAgent.")
                t0 = time.monotonic()
                try:
                    res_news = self.news_agent.analyze_news(query=news_query)
                    duration_ms = int((time.monotonic() - t0) * 1000)
                    ctx.news_data = res_news
                    if res_news.get("success"):
                        ctx.news_summary = res_news.get("summary", "")
                        ctx.update_decision_flags()
                        sentiment = res_news.get("overall_sentiment", "neutral")
                        count = res_news.get("total_results", 0)
                        ctx.record_activity(
                            agent="NewsAgent",
                            status="success",
                            summary=f"Financial news sentiment evaluated ({sentiment})",
                            decision=f"News sentiment evaluated as {sentiment} across {count} articles for query '{news_query}'. News flags updated.",
                            duration_ms=duration_ms,
                        )
                        ctx.log_decision(f"NewsAgent succeeded ({sentiment} sentiment). Updated news decision flags.")
                    else:
                        ctx.update_decision_flags()
                        ctx.record_activity(
                            agent="NewsAgent",
                            status="failed",
                            summary=f"NewsAgent failed: {res_news.get('error', 'News agent returned a failure response.')}",
                            decision=(
                                "NewsAgent failed; news context is unavailable. "
                                "Continuing to RiskAgent. "
                                "PortfolioAgent will be skipped — fabricating news sentiment is not acceptable."
                            ),
                            duration_ms=duration_ms,
                        )
                        ctx.log_decision("NewsAgent failed. Portfolio recommendation will be blocked because valid news context is required.")
                except Exception as exc:
                    duration_ms = int((time.monotonic() - t0) * 1000)
                    ctx.news_data = {"success": False, "agent": "NewsAgent", "error": str(exc)}
                    ctx.update_decision_flags()
                    ctx.record_activity(
                        agent="NewsAgent",
                        status="failed",
                        summary=f"NewsAgent error: {exc}",
                        decision=(
                            "NewsAgent raised an exception; news context is unavailable. "
                            "Continuing to RiskAgent. "
                            "PortfolioAgent will be skipped — fabricating news sentiment is not acceptable."
                        ),
                        duration_ms=duration_ms,
                    )
                    ctx.log_decision(f"NewsAgent raised exception ({exc}). Portfolio recommendation will be blocked.")
            else:
                ctx.log_decision("News fetch skipped because no valid news query was provided.")

            # Step 3: Context-driven Risk Agent decision --------------------
            if self._ctx_should_analyze_risk(ctx):
                ctx.agents_used.append("RiskAgent")
                news_status_str = "with news context" if ctx.news_succeeded() else "(news context unavailable)"
                ctx.log_decision(f"Invoking RiskAgent using market data {news_status_str}.")
                t0 = time.monotonic()
                try:
                    res_risk = self.risk_agent.analyze_risk(ctx.market_data, news_data=ctx.news_data)
                    duration_ms = int((time.monotonic() - t0) * 1000)
                    ctx.risk_data = res_risk
                    if res_risk.get("success"):
                        ctx.risk_summary = res_risk.get("analysis", "")
                        ctx.update_decision_flags()
                        r_score = res_risk.get("risk_score", 0)
                        r_level = res_risk.get("risk_level", "unknown")
                        news_note = f"news sentiment {ctx.news_data.get('overall_sentiment')}" if ctx.news_succeeded() else "no news context"
                        ctx.record_activity(
                            agent="RiskAgent",
                            status="success",
                            summary=f"Risk score evaluated: {r_score} ({r_level})",
                            decision=f"Risk evaluated as {r_level} (score: {r_score}/100) based on market direction '{direction}' and {news_note}.",
                            duration_ms=duration_ms,
                        )
                        ctx.log_decision(f"RiskAgent succeeded (score {r_score}, level {r_level}). Risk decision flags updated.")
                    else:
                        ctx.update_decision_flags()
                        ctx.record_activity(
                            agent="RiskAgent",
                            status="failed",
                            summary=f"RiskAgent failed: {res_risk.get('error', 'Risk agent returned a failure response.')}",
                            decision="Risk analysis failed; halting portfolio recommendation as risk metrics are required.",
                            duration_ms=duration_ms,
                        )
                        ctx.log_decision("RiskAgent failed. Halting portfolio recommendation.")
                        return {
                            "success": False,
                            "agent": "Orchestrator",
                            "intent": intent,
                            "agents_used": ctx.agents_used,
                            "agent_activity": ctx.agent_activity,
                            "step": "risk_agent",
                            "error": res_risk.get("error", "Risk agent returned a failure response."),
                            "market_data": ctx.market_data,
                            "news_data": ctx.news_data,
                            "risk_data": res_risk,
                        }
                except Exception as exc:
                    duration_ms = int((time.monotonic() - t0) * 1000)
                    ctx.update_decision_flags()
                    ctx.record_activity(
                        agent="RiskAgent",
                        status="failed",
                        summary=f"RiskAgent error: {exc}",
                        decision="RiskAgent exception; halting portfolio recommendation.",
                        duration_ms=duration_ms,
                    )
                    ctx.log_decision(f"RiskAgent raised exception ({exc}). Halting portfolio recommendation.")
                    return {
                        "success": False,
                        "agent": "Orchestrator",
                        "intent": intent,
                        "agents_used": ctx.agents_used,
                        "agent_activity": ctx.agent_activity,
                        "error": f"Risk agent raised an unexpected error: {exc}",
                    }
            else:
                ctx.log_decision("RiskAgent skipped because prerequisite market data is unavailable or failed.")

            # Step 4: Context-driven Portfolio Agent decision ---------------
            if self._ctx_should_generate_portfolio(ctx):
                ctx.agents_used.append("PortfolioAgent")
                ctx.log_decision("All prerequisites met (market, news, risk). Invoking PortfolioAgent.")
                t0 = time.monotonic()
                try:
                    res_rec = self.portfolio_agent.generate_recommendation(
                        market_data=ctx.market_data,
                        risk_data=ctx.risk_data,
                        news_data=ctx.news_data,
                    )
                    duration_ms = int((time.monotonic() - t0) * 1000)
                    ctx.portfolio_data = res_rec
                    if res_rec.get("success"):
                        ctx.recommendation_summary = res_rec.get("summary", "")
                        ctx.confidence_factors = list(res_rec.get("factors", []))
                        ctx.update_decision_flags()
                        rec_str = str(res_rec.get("recommendation", "unknown")).upper()
                        rec_score = res_rec.get("recommendation_score", 0)
                        conf_str = res_rec.get("confidence", "unknown")
                        ctx.record_activity(
                            agent="PortfolioAgent",
                            status="success",
                            summary=f"Recommendation generated: {rec_str}",
                            decision=f"Recommendation {rec_str} (score: {rec_score}/100) synthesized from market '{res_rec.get('market_direction')}', risk '{res_rec.get('risk_level')}', and news '{res_rec.get('news_sentiment')}' with {conf_str} confidence.",
                            duration_ms=duration_ms,
                        )
                        ctx.log_decision(f"PortfolioAgent succeeded (recommendation {rec_str}, confidence {conf_str}). Context complete.")
                    else:
                        ctx.update_decision_flags()
                        ctx.record_activity(
                            agent="PortfolioAgent",
                            status="failed",
                            summary=f"PortfolioAgent failed: {res_rec.get('error', 'Portfolio agent returned a failure response.')}",
                            decision="Portfolio recommendation failed.",
                            duration_ms=duration_ms,
                        )
                        ctx.log_decision("PortfolioAgent failed to generate recommendation.")
                        return {
                            "success": False,
                            "agent": "Orchestrator",
                            "intent": intent,
                            "agents_used": ctx.agents_used,
                            "agent_activity": ctx.agent_activity,
                            "step": "portfolio_agent",
                            "error": res_rec.get("error", "Portfolio agent returned a failure response."),
                            "market_data": ctx.market_data,
                            "news_data": ctx.news_data,
                            "risk_data": ctx.risk_data,
                            "recommendation": res_rec,
                        }
                except Exception as exc:
                    duration_ms = int((time.monotonic() - t0) * 1000)
                    ctx.update_decision_flags()
                    ctx.record_activity(
                        agent="PortfolioAgent",
                        status="failed",
                        summary=f"PortfolioAgent error: {exc}",
                        decision="PortfolioAgent exception.",
                        duration_ms=duration_ms,
                    )
                    ctx.log_decision(f"PortfolioAgent raised exception ({exc}).")
                    return {
                        "success": False,
                        "agent": "Orchestrator",
                        "intent": intent,
                        "agents_used": ctx.agents_used,
                        "agent_activity": ctx.agent_activity,
                        "error": f"Portfolio agent raised an unexpected error: {exc}",
                    }
            else:
                ctx.update_decision_flags()
                if not ctx.news_succeeded():
                    ctx.log_decision("Portfolio recommendation skipped: required news data is missing or failed.")
                else:
                    ctx.log_decision("Portfolio recommendation skipped: prerequisite market or risk data is missing or failed.")

            # Build successful response from context -------------------------
            return ctx.to_response_dict()

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
