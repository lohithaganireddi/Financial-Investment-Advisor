"""
API Router for Financial Intelligence Endpoints

Defines backend routes for asset analysis, query interpretation, history persistence,
and orchestrator interaction.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from backend.schemas import (
    AnalyzeRequest,
    QueryRequest,
    HistoryListResponse,
    HistoryDetailResponse,
    BacktestRequest,
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    WatchlistCreateRequest,
    WatchlistItemResponse,
    WatchlistListResponse,
)
from agents.orchestrator import Orchestrator
from services.query_interpreter import QueryInterpreter
from services.analysis_repository import AnalysisRepository
from services.backtest_engine import BacktestEngine
from services.user_repository import UserRepository
from services.auth_service import AuthService

router = APIRouter(prefix="/api", tags=["Analysis"])

# Shared instances for production requests
_default_orchestrator = Orchestrator()
_default_interpreter = QueryInterpreter()
_default_repository = AnalysisRepository()
_default_backtest_engine = BacktestEngine()
_default_user_repository = UserRepository()


def get_orchestrator() -> Orchestrator:
    """Dependency provider for Orchestrator instance, easily overridable in tests."""
    return _default_orchestrator


def get_query_interpreter() -> QueryInterpreter:
    """Dependency provider for QueryInterpreter instance, easily overridable in tests."""
    return _default_interpreter


def get_repository() -> AnalysisRepository:
    """Dependency provider for AnalysisRepository instance, easily overridable in tests."""
    return _default_repository


def get_backtest_engine() -> BacktestEngine:
    """Dependency provider for BacktestEngine instance, easily overridable in tests."""
    return _default_backtest_engine


def get_user_repository() -> UserRepository:
    """Dependency provider for UserRepository instance, easily overridable in tests."""
    return _default_user_repository




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
    Analyze a financial query by interpreting user intent and dynamically routing
    to the appropriate agent pipeline via Orchestrator.run_intent().

    Routing is fully delegated to the Orchestrator:
    - STOCK_ANALYSIS       → StockAgent + NewsAgent + RiskAgent + PortfolioAgent
    - CRYPTO_ANALYSIS      → CryptoAgent + NewsAgent + RiskAgent + PortfolioAgent
    - GENERAL_FINANCIAL_NEWS → NewsAgent only (no DB persistence)
    - UNSUPPORTED          → Clean structured error, no agents called

    :param request: Validated request containing a natural language query string.
    :param interpreter: Injected QueryInterpreter instance.
    :param orchestrator: Injected Orchestrator instance.
    :param repository: Injected AnalysisRepository instance.
    :return: Standardized dictionary containing interpreted request, analysis result,
             agents_used list, and saved ID.
    """
    interpreted_res = interpreter.interpret(request.query)

    if not interpreted_res.get("success"):
        analysis_res = orchestrator.run_intent(interpreted_res)
        return {
            "success": False,
            "query": request.query,
            "intent": interpreted_res.get("intent", "UNSUPPORTED"),
            "agents_used": [],
            "agent_activity": [],
            "decision_trace": analysis_res.get("decision_trace", []),
            "error": interpreted_res.get("error", "Unable to identify a supported financial asset from the query."),
        }

    # Delegate all routing logic to Orchestrator.run_intent()
    analysis_res = orchestrator.run_intent(interpreted_res)

    saved_analysis_id = None

    # Persist to DB only for successful stock/crypto full-pipeline analyses
    intent = interpreted_res.get("intent")
    if (
        isinstance(analysis_res, dict)
        and analysis_res.get("success")
        and intent in (QueryInterpreter.INTENT_STOCK, QueryInterpreter.INTENT_CRYPTO)
    ):
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
            agent_activity=analysis_res.get("agent_activity"),
        )

        if saved_record is not None:
            saved_analysis_id = saved_record.id

    return {
        "success": True,
        "query": request.query,
        "interpreted": {
            "intent": interpreted_res.get("intent"),
            "asset_type": interpreted_res.get("asset_type"),
            "asset": interpreted_res.get("asset"),
            "news_query": interpreted_res.get("news_query"),
        },
        "agents_used": analysis_res.get("agents_used", []),
        "agent_activity": analysis_res.get("agent_activity", []),
        "decision_trace": analysis_res.get("decision_trace", []),
        "analysis": analysis_res,
        "saved_analysis_id": saved_analysis_id,
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


@router.post("/backtest", response_model=Dict[str, Any])
def run_portfolio_backtest(
    request: BacktestRequest,
    engine: BacktestEngine = Depends(get_backtest_engine)
) -> Dict[str, Any]:
    """
    Execute a Monte Carlo simulation backtest for a portfolio target asset.

    :param request: BacktestRequest containing asset, asset_type, investment amount, horizon, etc.
    :param engine: Injected BacktestEngine instance.
    :return: Monte Carlo simulation report dictionary.
    """
    result = engine.run_backtest(
        asset=request.asset,
        asset_type=request.asset_type or "stock",
        initial_investment=request.initial_investment,
        horizon_months=request.horizon_months,
        iterations=request.iterations or 500,
        risk_score=request.risk_score,
        seed=request.seed
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Backtest execution failed.")
        )
    return result


# ===========================================================================
# Auth & Watchlist Endpoints (Day 37)
# ===========================================================================

def get_current_user_from_token(
    authorization: Optional[str] = Header(None),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Dependency helper to extract user from Authorization Bearer JWT token."""
    user_id = 1
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        payload = AuthService.decode_access_token(token)
        if payload and "sub" in payload:
            user_id = int(payload["sub"])

    user = user_repo.get_user_by_id(user_id)
    if user is None:
        # Fallback to creating a default local analyst user if missing
        user = user_repo.create_user(
            username=f"analyst_{user_id}",
            email=f"analyst_{user_id}@smartfinance.local",
            password="default_analyst_password",
            role="analyst"
        )
        if user is None:
            user = user_repo.get_user_by_username(f"analyst_{user_id}")
    return user


@router.post("/auth/register", response_model=Dict[str, Any])
def register_user(
    request: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Register a new user account."""
    existing_user = user_repo.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered.")

    user = user_repo.create_user(
        username=request.username,
        email=request.email,
        password=request.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Failed to create user account.")

    token = AuthService.create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at
        }
    }


@router.post("/auth/login", response_model=Dict[str, Any])
def login_user(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Authenticate user credentials and return JWT access token."""
    user = user_repo.get_user_by_username(request.username)
    if not user or not AuthService.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = AuthService.create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at
        }
    }


@router.get("/auth/me", response_model=Dict[str, Any])
def get_current_user_profile(
    current_user=Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Retrieve active authenticated user profile."""
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at
        }
    }


@router.get("/watchlist", response_model=Dict[str, Any])
def get_watchlist(
    current_user=Depends(get_current_user_from_token),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Retrieve saved watchlist assets for the current user."""
    items = user_repo.get_user_watchlist(user_id=current_user.id)
    return {
        "success": True,
        "count": len(items),
        "items": items
    }


@router.post("/watchlist", response_model=Dict[str, Any])
def add_to_watchlist(
    request: WatchlistCreateRequest,
    current_user=Depends(get_current_user_from_token),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Add an asset to current user's saved watchlist."""
    item = user_repo.add_watchlist_item(
        user_id=current_user.id,
        asset_type=request.asset_type,
        asset=request.asset,
        target_price=request.target_price,
        notes=request.notes
    )
    if not item:
        raise HTTPException(status_code=400, detail="Failed to add item to watchlist.")
    return {
        "success": True,
        "item": item
    }


@router.delete("/watchlist/{item_id}", response_model=Dict[str, Any])
def remove_from_watchlist(
    item_id: int,
    current_user=Depends(get_current_user_from_token),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """Delete a watchlist item by item ID for current user."""
    success = user_repo.remove_watchlist_item(item_id=item_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Watchlist item #{item_id} not found.")
    return {
        "success": True,
        "message": f"Watchlist item #{item_id} removed."
    }


