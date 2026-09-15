"""
SmartFinancial Advisor (FinSight 2.0) - Backend Application Entry Point

This file initializes the FastAPI backend server and defines initial health-check endpoints.
"""

from fastapi import FastAPI

# Initialize FastAPI application
app = FastAPI(
    title="SmartFinancial Advisor API",
    description="Backend service for FinSight 2.0 multi-agent financial intelligence system.",
    version="0.1.0"
)


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
