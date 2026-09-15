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

## [0.29.0] - 2026-09-15 (Day 29: Agent-to-Agent Context & Decision State)

### Added
- Introduced `agents/analysis_context.py` — a new `AnalysisContext` dataclass that represents the shared decision state flowing through the Orchestrator's multi-agent pipeline.
  - Stores `intent`, `asset_type`, `asset`, `original_query`, `news_query`, and each agent's output (`market_data`, `news_data`, `risk_data`, `portfolio_data`).
  - Provides `market_succeeded()`, `news_succeeded()`, `risk_succeeded()`, and `portfolio_succeeded()` status helpers for clean conditional logic.
  - Provides `record_activity()` helper that appends structured activity entries with `agent`, `status`, `order`, `summary`, `decision`, and optional `duration_ms`.
  - Provides `log_decision()` for appending human-readable rationale strings to the internal `decisions` log.
  - Provides `to_response_dict()` that serialises only the existing public API fields, keeping the API contract unchanged.
- Refactored `agents/orchestrator.py` to instantiate `AnalysisContext` at the start of every `run_intent()` call and progressively update it after each agent execution.
- Added context-aware decision wrappers `_ctx_should_fetch_news()`, `_ctx_should_analyze_risk()`, and `_ctx_should_generate_portfolio()` that read directly from the context instead of isolated local variables.
- Added `duration_ms` wall-clock timing to every `agent_activity` entry via `time.monotonic()`.
- Added 15 new Day 29 tests in `tests/test_agents.py` covering:
  - `AnalysisContext` initial state, status helpers, `record_activity()`, `log_decision()`.
  - Full stock and crypto pipeline flows (all four agents, duration tracking).
  - News-only context flow (GENERAL_FINANCIAL_NEWS).
  - Market failure halts downstream agents.
  - News failure stores real failure dict — no fabricated sentiment.
  - Risk failure prevents portfolio execution.
  - PortfolioAgent receives exact context data (market + risk + news).
  - Sequential `order` field validation.
  - API response key backward-compatibility guard.

### Changed
- `Orchestrator.run_intent()` now builds its final response via `AnalysisContext.to_response_dict()`, eliminating manual dict assembly for the success path.
- All decision helpers now have both the original signature (for backward-compatible unit tests) and context-aware wrappers used internally.
- Honest news-failure behaviour from Day 28 preserved: `news_data` remains the real failure dict; `PortfolioAgent` is still skipped when news is unavailable.

## [0.28.0] - 2026-09-15 (Day 28: Advanced Agentic Orchestration)

### Added
- Upgraded `Orchestrator` (`agents/orchestrator.py`) into a decision-driven multi-agent workflow evaluating intermediate agent outputs.
- Added explicit deterministic decision helpers: `should_fetch_news()`, `should_analyze_risk()`, and `should_generate_portfolio_recommendation()`.
- Implemented intelligent failure decisions: market agent failure halts pipeline to prevent ungrounded downstream analysis; news agent failure applies neutral news sentiment fallback so risk and portfolio analysis proceed safely; risk agent failure halts portfolio recommendation to prevent risk-unaware advice.
- Extended `agent_activity` schema with explainable `decision` rationale notes for every executed step.
- Added 4 new decision tests in `tests/test_agents.py` (total test suite expanded to 121 passing tests).

## [0.25.0] - 2026-09-15 (Day 25: Strengthen Natural-Language Query Interpretation)

### Added
- Expanded stock symbol and keyword mappings in `QueryInterpreter` to support Netflix (`NFLX`), AMD (`AMD`), Intel (`INTC`), Coca-Cola (`KO`), and Walmart (`WMT`), alongside existing equities (`AAPL`, `MSFT`, `TSLA`, `NVDA`, `AMZN`, `GOOGL`, `META`).
- Expanded crypto asset mappings to support Cardano (`cardano`), XRP/Ripple (`ripple`), Binance Coin (`binancecoin`), and Polygon (`polygon`), alongside existing crypto assets (`bitcoin`, `ethereum`, `solana`, `dogecoin`).
- Implemented ticker prefix normalization (`$AAPL` -> `AAPL`, `$BTC` -> `bitcoin`) and text punctuation stripping.
- Added boundary-aware regex keyword matching (`\b...\b`) on normalized lowercased query text to prevent substring false positives.
- Implemented explicit asset-specific news query routing (`GENERAL_FINANCIAL_NEWS` with `news_query: <AssetName>`) when explicit news keywords (`news`, `headline`, `headlines`, `article`, `articles`) are present in asset queries.
- Added multi-asset ambiguity detection returning `UNSUPPORTED` with a clear message asking the user to analyze one asset at a time when multiple distinct assets are detected.
- Expanded `tests/test_query_interpreter.py` with comprehensive test coverage for ticker normalization, expanded assets, asset news routing, and multi-asset ambiguity.

## [0.24.0] - 2026-09-15 (Day 24: Improve Agent Activity Dashboard with Analysis Context)

### Added
- Updated `AgentDashboard.jsx` to receive analysis context props (`query`, `asset`, `asset_type`, `intent`, `recommendation`, `risk_level`, `saved_id`).
- Added a top Context Banner displaying the active asset identifier, analysis type, user query prompt, recommendation badge, and risk level.
- Added friendly human-readable display names for all agents (`Stock Price Agent`, `Crypto Agent`, `Financial News Agent`, `Risk Analysis Agent`, `Portfolio Recommendation Agent`) while preserving raw backend system IDs (`StockAgent`, etc.).
- Built a dynamic horizontal **Executed Pipeline Flow** summary bar showing step-by-step agent sequence (`Agent A → Agent B → Agent C → Agent D`).
- Updated `App.jsx` to construct `analysisContext` from `result` state and pass it into `<AgentDashboard />`.
- Ensured news-only analyses (`GENERAL_FINANCIAL_NEWS`) display only the `Financial News Agent` across flow, metrics, timeline, and telemetry table.
- Verified build with `npm run build` (0 errors) and Python test suite (`pytest`, 112 tests passing).

---

## [0.23.0] - 2026-09-15 (Day 23: Persist Agent Activity in Analysis History)

### Added
- Added `agent_activity` column (`Text, nullable=True`) to the `Analysis` SQLAlchemy database model in `backend/models.py`.
- Updated `AnalysisRepository.save_analysis()` to serialize structured `agent_activity` lists into JSON text when storing records in SQLite.
- Updated `AnalysisRecordResponse` in `backend/schemas.py` with a `@field_validator` that deserializes stored JSON string back into a list of `AgentActivityItem` objects automatically.
- Updated `POST /api/query` in `backend/routes.py` to persist the real `agent_activity` returned by `Orchestrator.run_intent()`.
- Updated `GET /api/history` and `GET /api/history/{id}` to include parsed `agent_activity` in responses, maintaining full backward compatibility for older records (which default safely to `[]`).
- Updated `handleSelectHistoryRecord` in `frontend/src/App.jsx` to pass stored historical `agent_activity` to `ResultCard` and `AgentDashboard`.
- Added unit tests in `tests/test_database.py` and `tests/test_api.py` for saving/reading `agent_activity`, JSON parsing, and backward-compatibility with older NULL records.

---

## [0.22.0] - 2026-09-15 (Day 22: Agent Activity Dashboard)

### Added
- Created `frontend/src/components/AgentDashboard.jsx` providing a dedicated Agent Activity Dashboard view.
- Added top Summary Cards grid dynamically calculating `Total Agents Executed`, `Successful`, `Failed`, and `Pipeline Status` (COMPLETED / PARTIAL FAILURE / FAILED / NO ACTIVITY).
- Built a vertical execution timeline displaying sequential execution steps (`#1`, `#2`, `#3`, `#4`) with visual connecting lines and Lucide icons (`TrendingUp`, `Coins`, `Newspaper`, `ShieldAlert`, `Briefcase`, `Bot`, `CheckCircle2`, `XCircle`).
- Added an **Agent Details & Telemetry** table displaying agent name, execution order, success/failed status badges, and execution summaries.
- Created an Empty State ("No agent activity available") displayed when no query has been run or historical records without activity are viewed.
- Updated `frontend/src/App.jsx` with tab navigation allowing users to toggle between the **Financial Intelligence Dashboard** and the **Agent Activity Dashboard**.
- Verified build with `npm run build` (0 errors) and Python test suite (`pytest`, 110 tests passing).

---

## [0.21.0] - 2026-09-15 (Day 21: Agent Activity Tracking)

### Added
- Updated `Orchestrator.run_intent()` to track structured `agent_activity` for every executed agent step.
- Each item in `agent_activity` records `agent` name, `status` ("success" or "failed"), `order` (1-based sequence integer), and a short result/error `summary`.
- Failed steps record status as "failed", include an error summary, and halt execution cleanly.
- `GENERAL_FINANCIAL_NEWS` records only `NewsAgent`; `UNSUPPORTED` or unknown intents record an empty `agent_activity` list.
- Preserved existing `agents_used` field alongside `agent_activity`.
- Updated `backend/schemas.py` with `AgentActivityItem` and `QueryResponse` Pydantic models.
- Updated `POST /api/query` in `backend/routes.py` to return the new top-level `agent_activity` field.
- Updated `ResultCard.jsx` in frontend to render a clean "Agent Execution Activity" tracker feed.
- Updated agent unit tests (`tests/test_agents.py`) and API tests (`tests/test_api.py`) verifying `agent_activity` tracking behavior across all routing paths.

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
