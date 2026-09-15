# Project Plan - SmartFinancial Advisor (FinSight 2.0)

## 📌 Executive Summary

**SmartFinancial Advisor (FinSight 2.0)** is a multi-agent financial intelligence system designed to empower users with real-time stock analysis, cryptocurrency tracking, financial news sentiment, risk profiling, and automated portfolio recommendations.

---

## 🏗️ Architectural Vision

The application relies on a decoupled, modular 3-tier architecture:

```text
+-------------------------------------------------------------------+
|                        Frontend Dashboard                         |
|    (Framework choice deferred: Streamlit, React, or Next.js)      |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                         Backend Services                          |
|             (FastAPI / Python Service & Orchestrator)              |
+---------------------------------+---------------------------------+
                                  |
                                  v
+---------------------------------+---------------------------------+
|                        Multi-Agent Engine                         |
|   (Stock, Crypto, News, Risk Analysis, Portfolio Recommendation)   |
+--------+------------------+-------------------+-------------------+
         |                  |                   |
         v                  v                   v
+------------------+ +-----------------+ +------------------+
| Alpha Vantage API| |  CoinGecko API  | |  NewsData API    |
|  (Stock Data)    | |  (Crypto Data)  | |  (Financial News)|
+------------------+ +-----------------+ +------------------+
```

---

## 🤖 Agent Roles & Responsibilities

1. **Stock Price Agent**
   - Integrates with Alpha Vantage API.
   - Fetches real-time price quotes, historical candles, and technical indicators (SMA, RSI).

2. **Crypto Agent**
   - Integrates with CoinGecko API.
   - Tracks crypto asset prices, market caps, trading volume, and market trends.

3. **Financial News Agent**
   - Integrates with NewsData API.
   - Gathers sector news and performs basic sentiment tagging (Bullish, Bearish, Neutral).

4. **Risk Analysis Agent**
   - Evaluates volatility, price drawdown, asset correlation, and risk metrics.
   - Computes composite risk score (Low, Moderate, High).

5. **Portfolio Recommendation Agent**
   - Synthesizes findings from Stock, Crypto, News, and Risk agents.
   - Generates actionable portfolio rebalancing and allocation insights.

---

## 🗺️ Development Roadmap

### Phase 1: Foundation (Day 1 - Completed)
- [x] Project workspace initialization.
- [x] Folder structure creation (`backend/`, `frontend/`, `agents/`, `services/`, `tests/`).
- [x] Documentation & environment configuration (`.env`, `.gitignore`, `README.md`, `PROJECT_PLAN.md`, `TODO.md`, `CHANGELOG.md`).

### Phase 2: Services & API Integrations
- [ ] Build Alpha Vantage service client wrapper.
- [ ] Build CoinGecko service client wrapper.
- [ ] Build NewsData service client wrapper.
- [ ] Add mock mode for API clients to work offline/without consuming credits.

### Phase 3: Agent Architecture & Implementation
- [ ] Evaluate and select multi-agent orchestrator framework (or custom light orchestrator).
- [ ] Implement Stock Price Agent.
- [ ] Implement Crypto Agent.
- [ ] Implement Financial News Agent.
- [ ] Implement Risk Analysis Agent.
- [ ] Implement Portfolio Recommendation Agent.

### Phase 4: Backend API & Database
- [ ] Setup FastAPI web server.
- [ ] Implement REST endpoints for agents and financial queries.
- [ ] Configure database layer (SQLite / PostgreSQL) for portfolio & history tracking.
- [ ] Implement user authentication & session management.

### Phase 5: Frontend Dashboard
- [ ] Select frontend UI framework (Streamlit / React / Next.js).
- [ ] Create interactive financial dashboard layout.
- [ ] Connect frontend to backend API endpoints.
- [ ] Display real-time data, charts, agent insights, and portfolio recommendations.

### Phase 6: Testing, Refinement & Deployment
- [ ] Write unit & integration tests across services and agents.
- [ ] Perform end-to-end user testing.
- [ ] Package with Docker / deployment configuration.
