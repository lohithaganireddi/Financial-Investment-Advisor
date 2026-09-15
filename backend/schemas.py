"""
Pydantic Request and Response Schemas for Backend API

Defines the data validation models for API endpoints.
"""

from typing import Optional
from pydantic import BaseModel, Field


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
