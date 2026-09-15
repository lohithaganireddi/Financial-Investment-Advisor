"""
SmartFinancial Advisor (FinSight 2.0) - Backend Application Entry Point

This file initializes the FastAPI backend server, database tables, health-check endpoints,
and includes API route handlers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
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

# Configure CORS for local development
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
