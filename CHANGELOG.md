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

## [0.20.0] - 2026-09-15 (Day 20: Dynamic Agent Routing)

### Added
- Added `Orchestrator.run_intent(interpreted)` — a new public method that accepts the pre-interpreted dict from `QueryInterpreter` and dynamically selects which agents to execute based on intent.
- Added intent constants to `Orchestrator` (`INTENT_STOCK`, `INTENT_CRYPTO`, `INTENT_NEWS`, `INTENT_UNSUPPORTED`) matching `QueryInterpreter` exactly.
- Routing rules inside `run_intent()`:
  - `STOCK_ANALYSIS` → StockAgent → NewsAgent → RiskAgent → PortfolioAgent
  - `CRYPTO_ANALYSIS` → CryptoAgent → NewsAgent → RiskAgent → PortfolioAgent
  - `GENERAL_FINANCIAL_NEWS` → NewsAgent only (no market, risk, or portfolio agents called)
  - `UNSUPPORTED` / unknown → clean structured error, no agents executed
- All `run_intent()` responses include `"agents_used"` list naming each agent that was actually executed.
- Refactored `POST /api/query` in `backend/routes.py` to delegate all routing to `orchestrator.run_intent()` (single routing authority). Route response now includes top-level `agents_used` field.
- DB persistence in `POST /api/query` is now explicitly restricted to `STOCK_ANALYSIS` and `CRYPTO_ANALYSIS` intents only; `GENERAL_FINANCIAL_NEWS` responses are never persisted.
- Existing `run()` method is completely unchanged — `POST /api/analyze` is unaffected.
- Added 11 comprehensive `run_intent()` unit tests to `tests/test_agents.py` covering all intents, partial pipeline failures, `agents_used` increments, invalid input, and a contract test verifying Orchestrator/QueryInterpreter constants match.
- Updated `tests/test_api.py` to mock `orchestrator.run_intent()` and assert `agents_used` in API responses.

---

## [0.19.0] - 2026-09-15 (Day 19: Query Intent Routing)

### Added
- Refactored `services/query_interpreter.py` to classify query intent into four categories: `STOCK_ANALYSIS`, `CRYPTO_ANALYSIS`, `GENERAL_FINANCIAL_NEWS`, and `UNSUPPORTED`.
- Added `intent` field to all `QueryInterpreter.interpret()` response dictionaries.
- Added Dogecoin (`dogecoin`/`doge`) support to `_CRYPTO_MAP`.
- Added `_NEWS_KEYWORDS` set for general financial news detection (`news`, `market`, `financial`, `economy`, etc.).
- Modified `POST /api/query` route in `backend/routes.py` to route `GENERAL_FINANCIAL_NEWS` queries directly to `NewsAgent.analyze_news()` without running the full Orchestrator pipeline or persisting to database.
- For `GENERAL_FINANCIAL_NEWS`, `saved_analysis_id` is returned as `null` (news summaries are not persisted).
- `UNSUPPORTED` error message now lists all currently supported assets and intents for user clarity.
- Rewrote `tests/test_query_interpreter.py` with grouped test functions covering all intents, Dogecoin, case-insensitivity, whitespace, and invalid inputs.
- Added `test_query_endpoint_general_financial_news` and `test_query_endpoint_stock_response_includes_intent` to `tests/test_api.py` (99 total unit tests passing).

---

## [0.17.0] - 2026-09-15 (Day 17: Frontend Dashboard Foundation)

### Added
- Selected React + Vite for the frontend framework and scaffolded `frontend/` directory.
- Created `frontend/src/components/Header.jsx` with application brand header and online status badge.
- Created `frontend/src/components/AnalysisForm.jsx` supporting both Structured Asset Analysis (`POST /api/analyze`) and Natural Language Query Analysis (`POST /api/query`).
- Created `frontend/src/components/ResultCard.jsx` for rendering recommendation badges (BUY/HOLD/AVOID), confidence rating, price metrics, risk breakdown, news sentiment, key factors, executive summary, and disclaimer.
- Created `frontend/src/components/HistoryList.jsx` for rendering recent SQLite database records (`GET /api/history`) with interactive record details lookup (`GET /api/history/{id}`).
- Configured safe local CORS middleware in `backend/main.py` for localhost development origins (`http://localhost:5173`, `http://127.0.0.1:5173`).
- Verified zero-error compilation with `npm run build` and verified all 104 Python unit & integration tests pass cleanly.
- Updated `TODO.md` tracking Phase 5 progress.

---

## [0.16.0] - 2026-09-15 (Day 16: SQLite Database Persistence & History API)

### Added
- Installed `sqlalchemy==2.0.53` and configured SQLite database connection in `backend/database.py`.
- Created `Analysis` model in `backend/models.py` for persisting structured analysis results (`query`, `asset_type`, `asset`, `recommendation`, `confidence`, `risk_score`, `risk_level`, `market_direction`, `news_sentiment`, `created_at`).
- Created `services/analysis_repository.py` with `AnalysisRepository` layer for clean database operations (`save_analysis`, `get_recent_analyses`, `get_analysis_by_id`).
- Modified `POST /api/query` to automatically persist successful Orchestrator analysis results and return `saved_analysis_id`.
- Added `GET /api/history` and `GET /api/history/{analysis_id}` REST endpoints in `backend/routes.py`.
- Updated `backend/schemas.py` with `AnalysisRecordResponse`, `HistoryListResponse`, and `HistoryDetailResponse` schemas.
- Created `tests/test_database.py` with 6 isolated database unit tests and updated `tests/test_api.py` with 6 persistence/history integration tests (104 total unit tests passing across project).
- Updated `.gitignore` to protect `smartfinance.db`, `TODO.md`, and `README.md`.

---

## [0.15.0] - 2026-09-15 (Day 15: User Query Interpretation Layer)

### Added
- Created `services/query_interpreter.py` implementing `QueryInterpreter` for deterministic parsing of natural language user queries into structured asset parameters.
- Supported mapping for major equities (Apple → AAPL, Microsoft → MSFT, Tesla → TSLA, Amazon → AMZN, Google/Alphabet → GOOGL, NVIDIA → NVDA, Meta → META) and crypto assets (Bitcoin/BTC → bitcoin, Ethereum/ETH → ethereum, Solana/SOL → solana).
- Added `QueryRequest` schema to `backend/schemas.py`.
- Created `POST /api/query` route in `backend/routes.py` linking query interpretation with `Orchestrator` workflow while preserving `POST /api/analyze`.
- Created `tests/test_query_interpreter.py` with 13 unit tests and updated `tests/test_api.py` with 5 unit tests for `POST /api/query` (98 total unit tests passing across project).
- Updated `TODO.md` tracking Phase 4 progress.

---

## [0.12.0] - 2026-09-15 (Day 12: Backend API Integration)

### Added
- Created `backend/schemas.py` defining Pydantic request model `AnalyzeRequest` for input validation.
- Created `backend/routes.py` with `POST /api/analyze` route connecting FastAPI to the multi-agent `Orchestrator`.
- Integrated `api_router` into `backend/main.py` while preserving existing `GET /` and `GET /health` endpoints.
- Implemented dependency provider `get_orchestrator` enabling test isolation without hardcoding or global state mutation.
- Created `tests/test_api.py` with 7 comprehensive unit/integration tests for API endpoints using FastAPI `TestClient` and mock Orchestrator (80 total unit tests passing across project).
- Updated `TODO.md` tracking Phase 4 progress.

---

## [0.11.0] - 2026-09-15 (Day 11: Multi-Agent Orchestrator)

### Added
- Created `agents/orchestrator.py` implementing `Orchestrator` — coordinates StockAgent/CryptoAgent, NewsAgent, RiskAgent, and PortfolioAgent into a single end-to-end workflow.
- `Orchestrator.run(asset_type, asset, news_query)` supports "stock" and "crypto" asset types (case-insensitive).
- All agents support dependency injection enabling full mock-based testing without live API calls.
- Safe exception handling at every agent step; failures include a `step` field identifying where the workflow stopped.
- Final response preserves `market_data`, `news_data`, `risk_data`, and `recommendation` from individual agents.
- Orchestrator never calls external services directly — delegates all work to existing agents.
- Exported `Orchestrator` from `agents/__init__.py`.
- Updated `tests/test_agents.py` with 12 new mock unit tests for `Orchestrator` (72 total unit tests passing across project).
- Updated `TODO.md` tracking Phase 3 as complete.

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
