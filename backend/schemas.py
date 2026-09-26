"""
Pydantic Request and Response Schemas for Backend API

Defines the data validation models for API endpoints.
"""

import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Request payload schema for financial analysis."""
    asset_type: str = Field(
        ...,
        description="Type of asset to analyze: 'stock' or 'crypto'",
        examples=["stock"]
    )
    asset: str = Field(
        ...,
        description="Asset identifier (stock ticker symbol or crypto coin ID)",
        examples=["AAPL"]
    )
    news_query: Optional[str] = Field(
        default="finance",
        description="Search query string for financial news analysis",
        examples=["finance"]
    )


class QueryRequest(BaseModel):
    """Request payload schema for natural language query analysis."""
    query: str = Field(
        ...,
        description="Natural language financial query",
        examples=["Should I invest in Apple?"]
    )


class AgentActivityItem(BaseModel):
    """Schema representing a single agent's execution activity."""
    agent: str = Field(..., description="Name of the executed agent", examples=["StockAgent"])
    status: str = Field(..., description="Execution status: 'success' or 'failed'", examples=["success"])
    order: int = Field(..., description="Execution order sequence (1-based)", examples=[1])
    summary: str = Field(..., description="Short summary of execution result or error", examples=["AAPL market analysis completed"])


class QueryResponse(BaseModel):
    """Response payload schema for POST /api/query."""
    success: bool
    query: str
    interpreted: Optional[dict] = None
    agents_used: List[str] = Field(default_factory=list)
    agent_activity: List[AgentActivityItem] = Field(default_factory=list)
    analysis: Optional[dict] = None
    saved_analysis_id: Optional[int] = None
    error: Optional[str] = None


class AnalysisRecordResponse(BaseModel):
    """Schema representing a single stored financial analysis record."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    asset_type: str
    asset: str
    news_query: Optional[str] = None
    recommendation: Optional[str] = None
    recommendation_score: Optional[int] = None
    confidence: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    market_direction: Optional[str] = None
    news_sentiment: Optional[str] = None
    agent_activity: Optional[List[AgentActivityItem]] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    @field_validator("agent_activity", mode="before")
    @classmethod
    def parse_agent_activity(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        if v is None:
            return []
        return v



class HistoryListResponse(BaseModel):
    """Response schema for GET /api/history."""
    success: bool = True
    count: int
    analyses: List[AnalysisRecordResponse]


class HistoryDetailResponse(BaseModel):
    """Response schema for GET /api/history/{analysis_id}."""
    success: bool = True
    analysis: AnalysisRecordResponse


class BacktestRequest(BaseModel):
    """Request payload schema for POST /api/backtest."""
    asset: str = Field(..., description="Asset ticker symbol or coin ID", examples=["AAPL"])
    asset_type: Optional[str] = Field(default="stock", description="Asset category: 'stock' or 'crypto'", examples=["stock"])
    initial_investment: float = Field(default=10000.0, description="Initial investment amount in USD", examples=[10000.0])
    horizon_months: int = Field(default=12, description="Simulation horizon in months (1-60)", examples=[12])
    iterations: Optional[int] = Field(default=500, description="Number of Monte Carlo simulation trials (10-2000)", examples=[500])
    risk_score: Optional[int] = Field(default=None, description="Optional risk score (0-100) to adjust volatility", examples=[35])
    seed: Optional[int] = Field(default=42, description="Pseudo-random seed for deterministic testing", examples=[42])


class RegisterRequest(BaseModel):
    """Request payload schema for user registration."""
    username: str = Field(..., min_length=3, max_length=30, description="Unique username")
    email: str = Field(..., description="Unique email address")
    password: str = Field(..., min_length=4, description="User password")


class LoginRequest(BaseModel):
    """Request payload schema for user login authentication."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Response schema representing a user profile."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Response schema for successful login returning JWT access token."""
    success: bool = True
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class WatchlistCreateRequest(BaseModel):
    """Request payload schema for adding asset to user watchlist."""
    asset_type: str = Field(..., description="Asset type: 'stock' or 'crypto'")
    asset: str = Field(..., description="Asset ticker symbol or coin ID")
    target_price: Optional[str] = Field(default=None, description="Optional target price alert threshold")
    notes: Optional[str] = Field(default=None, description="Optional watchlist notes")


class WatchlistItemResponse(BaseModel):
    """Response schema representing a single watchlist item."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    asset_type: str
    asset: str
    target_price: Optional[str] = None
    notes: Optional[str] = None
    added_at: Optional[datetime] = None


class WatchlistListResponse(BaseModel):
    """Response schema for GET /api/watchlist."""
    success: bool = True
    count: int
    items: List[WatchlistItemResponse]


class LLMSynthesizeRequest(BaseModel):
    """Request payload schema for POST /api/llm/synthesize."""
    analysis_data: dict = Field(..., description="Multi-agent analysis result dictionary")
    provider: Optional[str] = Field(default="auto", description="Target provider: 'auto', 'openai', 'gemini', 'anthropic', 'offline_fallback'")
    model: Optional[str] = Field(default=None, description="Optional target model identifier")



