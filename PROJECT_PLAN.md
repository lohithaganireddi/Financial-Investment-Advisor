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

### Phase 1: V1.0 Core System (Days 1 – 30) - COMPLETED ✅
- [x] **Project Workspace & Foundation** (Days 1–5): Modular structure (`agents/`, `backend/`, `frontend/`, `services/`, `tests/`), configuration (`.env`, `.gitignore`).
- [x] **API Services & Integration** (Days 6–10): Client wrappers for Alpha Vantage (Stock), CoinGecko (Crypto), and NewsData (Financial News) with fallback handling.
- [x] **Specialized AI Agents** (Days 11–18): `StockAgent`, `CryptoAgent`, `NewsAgent`, `RiskAgent`, and `PortfolioAgent`.
- [x] **Orchestrator & Query Interpreter** (Days 19–25): Deterministic query interpretation layer, intent routing (`STOCK_ANALYSIS`, `CRYPTO_ANALYSIS`, `GENERAL_FINANCIAL_NEWS`, `UNSUPPORTED`), and dynamic agent orchestration.
- [x] **Multi-Page Frontend Architecture** (Days 26–27): 10-page React + Vite frontend connected to backend REST API.
- [x] **Decision-Driven Agent Pipeline & Shared Context** (Days 28–29): `AnalysisContext` shared decision state, intermediate evaluation, honest failure handling (no fabricated news), and step telemetry.
- [x] **V1.0 Finalization & Stabilization** (Day 30): Complete test verification, documentation finalization, and security check.

---

### Phase 2: Future Development Phase (Days 31 – 45) - PLANNED 🔮
- [ ] **LLM & Autonomous Reasoning Integration**: Integrate Large Language Models (OpenAI / Gemini / Anthropic) for conversational financial analysis.
- [ ] **Advanced Portfolio Analytics**: Interactive asset allocation charts, Monte Carlo simulations, and historical backtesting.
- [ ] **User Authentication & Profiles**: JWT-based authentication, user account management, and saved watchlist preferences.
- [ ] **Real-Time Data Streaming**: WebSockets for live stock/crypto ticker price updates.
- [ ] **Production Deployment**: Docker containerization, CI/CD pipeline, and cloud deployment setup.

