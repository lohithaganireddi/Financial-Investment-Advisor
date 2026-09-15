"""
API Router for Financial Intelligence Endpoints

Defines backend routes for asset analysis and orchestrator interaction.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from backend.schemas import AnalyzeRequest
from agents.orchestrator import Orchestrator

router = APIRouter(prefix="/api", tags=["Analysis"])

# Shared Orchestrator instance for production requests
_default_orchestrator = Orchestrator()


def get_orchestrator() -> Orchestrator:
    """Dependency provider for Orchestrator instance, easily overridable in tests."""
    return _default_orchestrator


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
