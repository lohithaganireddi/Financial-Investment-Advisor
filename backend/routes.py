"""
API Router for Financial Intelligence Endpoints

Defines backend routes for asset analysis, query interpretation, history persistence,
and orchestrator interaction.
"""

import time
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, WebSocket, WebSocketDisconnect
import json
from datetime import datetime, timezone
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
    LLMSynthesizeRequest,
    LLMChatRequest,
    TelemetryMetricsResponse,
)
from agents.orchestrator import Orchestrator
from services.query_interpreter import QueryInterpreter
from services.analysis_repository import AnalysisRepository
from services.backtest_engine import BacktestEngine
from services.user_repository import UserRepository
from services.auth_service import AuthService
from services.llm_service import LLMService
from services.ticker_streamer import TickerStreamManager
from services.telemetry_service import TelemetryService
from services.export_service import ExportService

router = APIRouter(prefix="/api", tags=["Analysis"])

# Shared instances for production requests
_default_orchestrator = Orchestrator()
_default_interpreter = QueryInterpreter()
_default_repository = AnalysisRepository()
_default_backtest_engine = BacktestEngine()
_default_user_repository = UserRepository()
_default_llm_service = LLMService()
_default_stream_manager = TickerStreamManager()
_default_telemetry_service = TelemetryService()
_default_export_service = ExportService()


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


def get_llm_service() -> LLMService:
    """Dependency provider for LLMService instance, easily overridable in tests."""
    return _default_llm_service


def get_stream_manager() -> TickerStreamManager:
    """Dependency provider for TickerStreamManager instance, easily overridable in tests."""
    return _default_stream_manager


def get_telemetry_service() -> TelemetryService:
    """Dependency provider for TelemetryService instance, easily overridable in tests."""
    return _default_telemetry_service


def get_export_service() -> ExportService:
    """Dependency provider for ExportService instance, easily overridable in tests."""
    return _default_export_service






from backend.models import User


def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Optional[User]:
    """Dependency helper to extract user from Authorization Bearer JWT token if present, returning None if unauthenticated."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        payload = AuthService.decode_access_token(token)
        if payload and "sub" in payload:
            try:
                user_id = int(payload["sub"])
                return user_repo.get_user_by_id(user_id)
            except (ValueError, TypeError):
                return None
    return None


@router.post("/analyze", response_model=Dict[str, Any])
def analyze_asset(
    request: AnalyzeRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
    telemetry_service: TelemetryService = Depends(get_telemetry_service),
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
    start_time = time.time()
    result = orchestrator.run(
        asset_type=request.asset_type,
        asset=request.asset,
        news_query=request.news_query or "finance"
    )
    elapsed_ms = (time.time() - start_time) * 1000.0
    intent = "STOCK_ANALYSIS" if request.asset_type.lower() == "stock" else "CRYPTO_ANALYSIS"
    is_success = isinstance(result, dict) and result.get("status") == "success"
    agent_act = result.get("agent_activity", []) if isinstance(result, dict) else []
    telemetry_service.record_execution(
        intent=intent,
        duration_ms=elapsed_ms,
        success=is_success,
        agent_activity=agent_act
    )
    return result


@router.post("/query", response_model=Dict[str, Any])
def analyze_query(
    request: QueryRequest,
    interpreter: QueryInterpreter = Depends(get_query_interpreter),
    orchestrator: Orchestrator = Depends(get_orchestrator),
    repository: AnalysisRepository = Depends(get_repository),
    current_user: Optional[User] = Depends(get_optional_current_user),
    telemetry_service: TelemetryService = Depends(get_telemetry_service),
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
    :param current_user: Optional authenticated User model instance.
    :return: Standardized dictionary containing interpreted request, analysis result,
             agents_used list, and saved ID.
    """
    start_time = time.time()
    interpreted_res = interpreter.interpret(request.query)

    if not interpreted_res.get("success"):
        analysis_res = orchestrator.run_intent(interpreted_res)
        elapsed_ms = (time.time() - start_time) * 1000.0
        telemetry_service.record_execution(
            intent=interpreted_res.get("intent", "UNSUPPORTED"),
            duration_ms=elapsed_ms,
            success=False,
            agent_activity=[]
        )
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
    elapsed_ms = (time.time() - start_time) * 1000.0
    intent = interpreted_res.get("intent", "UNSUPPORTED")
    is_success = isinstance(analysis_res, dict) and analysis_res.get("success", False)
    agent_act = analysis_res.get("agent_activity", []) if isinstance(analysis_res, dict) else []

    telemetry_service.record_execution(
        intent=intent,
        duration_ms=elapsed_ms,
        success=is_success,
        agent_activity=agent_act
    )

    saved_analysis_id = None

    # Persist to DB only for successful stock/crypto full-pipeline analyses
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
            user_id=current_user.id if current_user else None,
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
    repository: AnalysisRepository = Depends(get_repository),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> Dict[str, Any]:
    """
    Retrieve recent saved financial asset analyses ordered newest first.
    If authenticated, returns history records specific to current user.

    :param limit: Maximum number of history records to return (default 10, max 50).
    :param repository: Injected AnalysisRepository instance.
    :param current_user: Optional authenticated user model instance.
    :return: List of Analysis records and count.
    """
    user_id_filter = current_user.id if current_user else None
    records = repository.get_recent_analyses(limit=limit, user_id=user_id_filter)
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


@router.post("/llm/synthesize", response_model=Dict[str, Any])
def synthesize_llm_reasoning(
    request: LLMSynthesizeRequest,
    llm_service: LLMService = Depends(get_llm_service)
) -> Dict[str, Any]:
    """
    Synthesize autonomous natural language LLM reasoning from multi-agent analysis outputs.

    :param request: LLMSynthesizeRequest containing analysis_data, provider, and optional model.
    :param llm_service: Injected LLMService instance.
    :return: Synthesized reasoning dictionary with executive summary and key takeaways.
    """
    result = llm_service.synthesize_reasoning(
        analysis_data=request.analysis_data,
        provider=request.provider or "auto",
        model=request.model
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "LLM reasoning synthesis failed.")
        )
    return result


@router.post("/llm/chat", response_model=Dict[str, Any])
def chat_llm_financial_assistant(
    request: LLMChatRequest,
    llm_service: LLMService = Depends(get_llm_service)
) -> Dict[str, Any]:
    """
    Multi-turn conversational LLM financial assistant endpoint.
    Processes user follow-up questions grounded in active analysis context.

    :param request: LLMChatRequest containing messages list, analysis_context, provider, and optional model.
    :param llm_service: Injected LLMService instance.
    :return: Chat synthesis response dictionary containing assistant reply, provider, and model.
    """
    messages_dicts = [m.model_dump() for m in request.messages]
    result = llm_service.chat_synthesis(
        messages=messages_dicts,
        analysis_context=request.analysis_context,
        provider=request.provider or "auto",
        model=request.model
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "LLM chat synthesis failed.")
        )
    return result


@router.get("/telemetry/metrics", response_model=TelemetryMetricsResponse)
def get_telemetry_metrics(
    telemetry_service: TelemetryService = Depends(get_telemetry_service)
) -> Dict[str, Any]:
    """
    Retrieve aggregate multi-agent telemetry metrics, pipeline latency, agent health,
    and intent distribution.
    """
    return telemetry_service.get_metrics()


@router.get("/export/{analysis_id}")
def export_analysis_report(
    analysis_id: int,
    format: str = Query(default="json", description="Export format: 'json' or 'html'"),
    repository: AnalysisRepository = Depends(get_repository),
    export_service: ExportService = Depends(get_export_service),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Export a saved financial analysis record as structured JSON or print-ready HTML.
    Enforces user ownership security checks if requested by an authenticated user.
    """
    record = repository.get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Analysis record #{analysis_id} not found.")

    # Day 42 Security Check: If record is bound to a user, enforce ownership
    if record.user_id is not None:
        if current_user and current_user.id != record.user_id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to export this report.")

    analysis_dict = {
        "id": record.id,
        "user_id": record.user_id,
        "query": record.query,
        "asset": record.asset,
        "asset_type": record.asset_type,
        "news_query": record.news_query,
        "recommendation": record.recommendation,
        "recommendation_score": record.recommendation_score,
        "confidence": record.confidence,
        "risk_score": record.risk_score,
        "risk_level": record.risk_level,
        "market_direction": record.market_direction,
        "news_sentiment": record.news_sentiment,
        "agent_activity": record.agent_activity,
        "created_at": record.created_at,
    }

    if str(format).lower() == "html":
        html_content = export_service.generate_html_report(analysis_dict)
        return Response(content=html_content, media_type="text/html")

    return export_service.generate_json_export(analysis_dict)


@router.websocket("/ws/ticker")
async def websocket_ticker_endpoint(
    websocket: WebSocket,
    stream_manager: TickerStreamManager = Depends(get_stream_manager)
):
    """
    Real-Time WebSocket Ticker Streaming Endpoint.

    Handles WebSocket client connections, client subscriptions, periodic price updates,
    ping/pong heartbeat checks, and clean disconnection handling.
    """
    await stream_manager.connect(websocket)
    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
            except Exception:
                await stream_manager.send_json(websocket, {
                    "type": "error",
                    "error": "Invalid JSON payload."
                })
                continue

            action = str(msg.get("action", "")).lower()

            if action == "ping":
                await stream_manager.send_json(websocket, {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif action == "subscribe":
                asset_type = msg.get("asset_type", "stock")
                symbol = msg.get("symbol", "AAPL")
                stream_manager.subscribe(websocket, asset_type, symbol)

                # Send initial price quote payload immediately upon subscription
                quote = stream_manager.fetch_ticker_quote(asset_type, symbol)
                await stream_manager.send_json(websocket, quote)
            elif action == "unsubscribe":
                asset_type = msg.get("asset_type", "stock")
                symbol = msg.get("symbol", "AAPL")
                stream_manager.unsubscribe(websocket, asset_type, symbol)
                await stream_manager.send_json(websocket, {
                    "type": "unsubscribed",
                    "asset_type": asset_type,
                    "symbol": symbol
                })
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket)
    except Exception:
        stream_manager.disconnect(websocket)




