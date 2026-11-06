"""
SmartFinancial Advisor (FinSight 2.0) - Backend Application Entry Point

This file initializes the FastAPI backend server, database tables, health-check endpoints,
and includes API route handlers.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from backend.database import init_db
from backend.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Initializes database tables on application startup.
    """
    init_db()
    yield


# Initialize FastAPI application
app = FastAPI(
    title="SmartFinancial Advisor API",
    description="Backend service for FinSight 2.0 multi-agent financial intelligence system.",
    version="0.1.0",
    lifespan=lifespan
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

    env = os.getenv("ENV", "development").lower()
    if env == "production" or request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# Configure CORS with strict allowed origins and environment overrides
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from backend.routes import get_trusted_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_trusted_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Include API routes
app.include_router(api_router)


@app.get("/")
def read_root():
    """
    Root Welcome Endpoint
    Returns a simple greeting and project status message.
    """
    return {
        "message": "Welcome to SmartFinancial Advisor (FinSight 2.0) API",
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    """
    Health Check Endpoint
    Used by clients and monitoring tools to verify the backend server is running.
    """
    return {
        "status": "healthy",
        "service": "smartfinance-backend",
        "version": "0.1.0"
    }
