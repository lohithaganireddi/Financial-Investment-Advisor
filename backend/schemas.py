"""
Pydantic Request and Response Schemas for Backend API

Defines the data validation models for API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


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
    created_at: Optional[datetime] = None


class HistoryListResponse(BaseModel):
    """Response schema for GET /api/history."""
    success: bool = True
    count: int
    analyses: List[AnalysisRecordResponse]


class HistoryDetailResponse(BaseModel):
    """Response schema for GET /api/history/{analysis_id}."""
    success: bool = True
    analysis: AnalysisRecordResponse
