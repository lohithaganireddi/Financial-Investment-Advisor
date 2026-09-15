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

## [0.10.0] - 2026-09-15 (Day 10: Portfolio Recommendation Agent Module)

### Added
- Created `agents/portfolio_agent.py` implementing `PortfolioAgent` with a deterministic recommendation scoring formula.
- `PortfolioAgent.generate_recommendation(market_data, risk_data, news_data)` combines StockAgent/CryptoAgent, RiskAgent, and NewsAgent outputs into a structured buy/hold/avoid recommendation.
- Scoring rules: base=50, market direction (bullish=+20, neutral=0, bearish=-20), risk level (low=+15, medium=0, high=-20), news sentiment (positive=+15, neutral=0, negative=-15), capped 0-100.
- Confidence logic: 3 aligned signals → "high", 2 aligned → "medium", otherwise → "low".
- Full input validation: rejects non-dict, empty, failed upstream inputs, unsupported market agent, and missing required fields.
- Output includes `recommendation_score`, `recommendation`, `confidence`, `factors`, `summary`, and educational `disclaimer`.
- Exported `PortfolioAgent` from `agents/__init__.py`.
- Updated `tests/test_agents.py` with 12 new mock unit tests for `PortfolioAgent` (60 total unit tests passing across project).
- Updated `TODO.md` tracking Phase 3 progress.

---

## [0.9.0] - 2026-09-15 (Day 9: Risk Analysis Agent Module)

### Added
- Created `agents/risk_agent.py` implementing `RiskAgent` with a deterministic scoring formula for market risk classification.
- `RiskAgent.analyze_risk(data)` accepts structured output from `StockAgent` or `CryptoAgent` and returns a risk score (0–100), risk level ("low"/"medium"/"high"), and a full `score_breakdown` dict.
- Scoring rules: base score (Stock=30, Crypto=50) + movement adjustment (≤2%→+0, >2–5%→+15, >5%→+30) + direction adjustment (bullish→+0, neutral→+10, bearish→+20) + crypto bonus (+10), capped at 100.
- Safe percentage parsing supporting both float values and string format (e.g., `"1.3736%"`).
- Full input validation: rejects non-dict, empty dict, failed upstream, unsupported agent, missing asset identifier, missing or unparseable percentage field.
- Exported `RiskAgent` from `agents/__init__.py`.
- Updated `tests/test_agents.py` with 10 new mock unit tests for `RiskAgent` (48 total unit tests passing across project).
- Updated `TODO.md` tracking Phase 3 progress.

---

## [0.8.0] - 2026-09-15 (Day 8: Financial News Agent Module)

### Added
- Created `agents/news_agent.py` implementing `NewsAgent` using dependency injection with `NewsDataService`.
- Implemented deterministic financial sentiment analysis scoring article titles and descriptions against positive/negative financial lexicons.
- Mapped `pubDate` to `published_at` in structured article payload for standardized orchestrator consumption.
- Exported `NewsAgent` from `agents/__init__.py`.
- Updated `tests/test_agents.py` with 8 new mock unit tests for `NewsAgent` (38 total unit tests passing across project).
- Updated `TODO.md` tracking Phase 3 progress.

---

## [0.7.0] - 2026-09-15 (Day 7: Cryptocurrency Agent Module)

### Added
- Created `agents/crypto_agent.py` implementing `CryptoAgent` using dependency injection with `CoinGeckoService`.
- Implemented coin ID validation/lowercase normalization (`" BITCOIN "` -> `"bitcoin"`), 24h market direction evaluation (`bullish`, `bearish`, `neutral`), and text analysis synthesis.
- Exported `CryptoAgent` from `agents/__init__.py`.
- Updated `tests/test_agents.py` with 6 new mock unit tests for `CryptoAgent` (30 total unit tests passing).
- Updated `TODO.md` tracking Phase 3 progress.

---

## [0.6.0] - 2026-09-15 (Day 6: Stock Price Agent Module)

### Added
- Created `agents/stock_agent.py` implementing `StockAgent` using dependency injection with `AlphaVantageService`.
- Implemented ticker validation, price change parsing (e.g. converting `"1.3736%"` to `1.3736`), market direction evaluation (`bullish`, `bearish`, `neutral`), and text analysis synthesis.
- Exported `StockAgent` from `agents/__init__.py`.
- Created `tests/test_agents.py` with 6 unit tests using mock services (24 total unit tests passing).
- Updated `TODO.md` tracking Phase 3 progress.

---

## [0.5.0] - 2026-09-15 (Day 5: NewsData Financial News Service Layer)

### Added
- Created `services/newsdata.py` client wrapper for NewsData.io financial news API.
- Implemented secure API key reading from `.env` (`NEWSDATA_API_KEY`) and default parameters (`query="finance"`, `category="business"`, `language="en"`).
- Implemented error handling for missing/placeholder API keys, empty queries, HTTP 429 rate limits, API payload error statuses, and network failures.
- Updated `tests/test_services.py` with 6 new mock unit tests for `NewsDataService` (18 total tests passing).
- Updated `TODO.md` completing Phase 2 external services layer.

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
