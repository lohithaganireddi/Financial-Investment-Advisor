"""
API Router for Financial Intelligence Endpoints

Defines backend routes for asset analysis, query interpretation, history persistence,
and orchestrator interaction.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.schemas import (
    AnalyzeRequest,
    QueryRequest,
    HistoryListResponse,
    HistoryDetailResponse,
)
from agents.orchestrator import Orchestrator
from services.query_interpreter import QueryInterpreter
from services.analysis_repository import AnalysisRepository

router = APIRouter(prefix="/api", tags=["Analysis"])

# Shared instances for production requests
_default_orchestrator = Orchestrator()
_default_interpreter = QueryInterpreter()
_default_repository = AnalysisRepository()


def get_orchestrator() -> Orchestrator:
    """Dependency provider for Orchestrator instance, easily overridable in tests."""
    return _default_orchestrator


def get_query_interpreter() -> QueryInterpreter:
    """Dependency provider for QueryInterpreter instance, easily overridable in tests."""
    return _default_interpreter


def get_repository() -> AnalysisRepository:
    """Dependency provider for AnalysisRepository instance, easily overridable in tests."""
    return _default_repository


@router.post("/analyze", response_model=Dict[str, Any])
def analyze_asset(
    request: AnalyzeRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Analyze a financial asset (stock or crypto).

    Executes the multi-agent workflow via Orchestrator combining:
    - Market Data Agent (StockAgent or CryptoAgent)
    - News Agent (NewsAgent)
    - Risk Analysis Agent (RiskAgent)
    - Portfolio Recommendation Agent (PortfolioAgent)

    :param request: Validated request containing asset_type, asset, and optional news_query.
    :param orchestrator: Injected Orchestrator instance.
    :return: Standardized analysis and portfolio recommendation response.
    """
    result = orchestrator.run(
        asset_type=request.asset_type,
        asset=request.asset,
        news_query=request.news_query or "finance"
    )
    return result


@router.post("/query", response_model=Dict[str, Any])
def analyze_query(
    request: QueryRequest,
    interpreter: QueryInterpreter = Depends(get_query_interpreter),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    repository: AnalysisRepository = Depends(get_repository)
) -> Dict[str, Any]:
    """
    Analyze a financial query by interpreting user intent and routing to the Orchestrator or News Agent.

    :param request: Validated request containing a natural language query string.
    :param interpreter: Injected QueryInterpreter instance.
    :param orchestrator: Injected Orchestrator instance.
    :param repository: Injected AnalysisRepository instance.
    :return: Standardized dictionary containing interpreted request, analysis result, and saved ID.
    """
    interpreted_res = interpreter.interpret(request.query)

    if not interpreted_res.get("success"):
        return {
            "success": False,
            "query": request.query,
            "error": interpreted_res.get("error", "Unable to identify a supported financial asset from the query.")
        }

    # Route General Financial News queries directly to News Agent
    if interpreted_res.get("intent") == QueryInterpreter.INTENT_NEWS:
        news_res = orchestrator.news_agent.analyze_news(query=interpreted_res.get("news_query", "finance"))
        return {
            "success": True,
            "query": request.query,
            "interpreted": {
                "intent": interpreted_res["intent"],
                "asset_type": None,
                "asset": None,
                "news_query": interpreted_res["news_query"]
            },
            "analysis": {
                "success": news_res.get("success", True),
                "agent": "NewsAgent",
                "summary": news_res.get("summary", ""),
                "news_data": news_res,
                "disclaimer": "This is a software-generated financial news summary, not financial advice."
            },
            "saved_analysis_id": None
        }

    # Route Stock / Crypto queries to Orchestrator workflow
    analysis_res = orchestrator.run(
        asset_type=interpreted_res["asset_type"],
        asset=interpreted_res["asset"],
        news_query=interpreted_res["news_query"]
    )

    saved_analysis_id = None

    # Persist in database only if the orchestrator analysis completed successfully
    if isinstance(analysis_res, dict) and analysis_res.get("success"):
        recommendation_data = analysis_res.get("recommendation", {})
        risk_data = analysis_res.get("risk_data", {})
        market_data = analysis_res.get("market_data", {})
        news_data = analysis_res.get("news_data", {})

        saved_record = repository.save_analysis(
            query=request.query,
            asset_type=interpreted_res["asset_type"],
            asset=interpreted_res["asset"],
            news_query=interpreted_res["news_query"],
            recommendation=recommendation_data.get("recommendation") if isinstance(recommendation_data, dict) else None,
            recommendation_score=recommendation_data.get("recommendation_score") if isinstance(recommendation_data, dict) else None,
            confidence=recommendation_data.get("confidence") if isinstance(recommendation_data, dict) else None,
            risk_score=risk_data.get("risk_score") if isinstance(risk_data, dict) else None,
            risk_level=risk_data.get("risk_level") if isinstance(risk_data, dict) else None,
            market_direction=market_data.get("market_direction") if isinstance(market_data, dict) else None,
            news_sentiment=news_data.get("overall_sentiment") if isinstance(news_data, dict) else None,
        )

        if saved_record is not None:
            saved_analysis_id = saved_record.id

    return {
        "success": True,
        "query": request.query,
        "interpreted": {
            "intent": interpreted_res.get("intent", "STOCK_ANALYSIS"),
            "asset_type": interpreted_res["asset_type"],
            "asset": interpreted_res["asset"],
            "news_query": interpreted_res["news_query"]
        },
        "analysis": analysis_res,
        "saved_analysis_id": saved_analysis_id
    }


@router.get("/history", response_model=HistoryListResponse)
def get_analysis_history(
    limit: int = Query(default=10, ge=1, le=50, description="Number of recent records to retrieve (1-50)"),
    repository: AnalysisRepository = Depends(get_repository)
) -> Dict[str, Any]:
    """
    Retrieve recent saved financial asset analyses ordered newest first.

    :param limit: Maximum number of history records to return (default 10, max 50).
    :param repository: Injected AnalysisRepository instance.
    :return: List of Analysis records and count.
    """
    records = repository.get_recent_analyses(limit=limit)
    return {
        "success": True,
        "count": len(records),
        "analyses": records
    }


@router.get("/history/{analysis_id}", response_model=HistoryDetailResponse)
def get_analysis_by_id(
    analysis_id: int,
    repository: AnalysisRepository = Depends(get_repository)
) -> Dict[str, Any]:
    """
    Retrieve a single saved financial asset analysis record by integer ID.

    :param analysis_id: Analysis record integer primary key ID.
    :param repository: Injected AnalysisRepository instance.
    :return: Analysis record details or 404 error if not found.
    """
    record = repository.get_analysis_by_id(analysis_id=analysis_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis record with ID {analysis_id} not found."
        )
    return {
        "success": True,
        "analysis": record
    }
