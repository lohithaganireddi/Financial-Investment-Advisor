# Changelog

All notable changes to the **SmartFinancial Advisor (FinSight 2.0)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- External API client wrappers for Alpha Vantage, CoinGecko, and NewsData.
- Agent implementations for Stock, Crypto, News, Risk, and Portfolio analysis.
- Backend API routes and database setup.
- Frontend UI dashboard development.

---

## [0.4.0] - 2026-09-15 (Day 4: CoinGecko Crypto Data Service Layer)

### Added
- Created `services/coingecko.py` client wrapper for CoinGecko market data API.
- Implemented secure API key reading from `.env` (`COINGECKO_API_KEY`) and authentication via `x-cg-demo-api-key` header.
- Implemented strict error handling for unconfigured keys, empty coin IDs, HTTP 429 rate limits, empty market payloads, and network failures.
- Updated `tests/test_services.py` with 6 new mock unit tests for `CoinGeckoService` (12 total tests passing).
- Updated `TODO.md` tracking Phase 2 progress.

---

## [0.3.0] - 2026-09-15 (Day 3: Alpha Vantage Service Layer)

### Added
- Installed `httpx` (0.28.1) and `pytest` (9.1.1) in virtual environment `venv`.
- Created `services/alpha_vantage.py` handling `GLOBAL_QUOTE` queries to Alpha Vantage API.
- Implemented secure API key reading from `.env` (`ALPHA_VANTAGE_API_KEY`).
- Implemented comprehensive error handling for missing API keys, rate limits, invalid symbols, network failures, and HTTP errors.
- Created `tests/test_services.py` with 6 automated mock unit tests verifying response formatting and error handling without live network calls.
- Updated `requirements.txt` with `httpx` and `pytest`.

---

## [0.2.0] - 2026-09-15 (Day 2: Backend Foundation & Health Check API)

### Added
- Installed `fastapi` (0.141.1) and `uvicorn[standard]` (0.53.0) inside project `venv`.
- Created `requirements.txt` documenting core backend dependencies.
- Created `backend/main.py` entry point with a minimal FastAPI application instance.
- Implemented `GET /` root welcome endpoint returning API metadata and docs link.
- Implemented `GET /health` service health check endpoint returning JSON status.
- Verified live server responses and interactive OpenAPI documentation at `/docs`.

---

## [0.1.0] - 2026-09-15 (Day 1: Project Foundation)

### Added
- Created clean, scalable folder architecture: `backend/`, `frontend/`, `agents/`, `services/`, `tests/`.
- Inspected system Python installation (`Python 3.13.6`) and verified `pip 26.2.1`.
- Created isolated virtual environment (`venv`) in project root without global package installations.
- Created package initialization files (`__init__.py`) across `backend/`, `agents/`, `services/`, `tests/`.
- Added placeholder file `.gitkeep` for `frontend/` directory.
- Added beginner-friendly `README.md` introducing the project, agent roles, and directory layout.
- Added `PROJECT_PLAN.md` documenting architecture vision, multi-agent design, and multi-week roadmap.
- Added `TODO.md` tracking completed Day 1 tasks and upcoming development phases.
- Added `CHANGELOG.md` for project version tracking.
- Added `.env` with safe placeholder variable names (no real API keys or hardcoded secrets).
- Added `.env.example` template file for environment configuration.
- Added `.gitignore` to prevent committing `.env`, virtual environments, and temporary files.
