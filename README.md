# SmartFinancial Advisor (FinSight 2.0) 🚀

Welcome to **SmartFinancial Advisor (FinSight 2.0)**! A deterministic, decision-driven multi-agent financial intelligence system that coordinates specialized AI agents to analyze stocks, cryptocurrency, and market news to deliver actionable portfolio recommendations, risk assessments, real-time ticker streaming, multi-turn LLM financial assistance, and print-ready executive reports.

---

## 🎯 What Does FinSight 2.0 Do?

FinSight 2.0 turns complex financial queries into clear, structured insights by coordinating a team of specialized software agents. Users can ask natural language questions or query assets directly through a multi-page web dashboard.

### 💡 Problem It Solves
- **Fragmented Data**: Investors usually have to gather stock prices, crypto trends, news headlines, and risk metrics across multiple separate platforms.
- **Overwhelming Information**: Raw financial market data lacks context and automated risk synthesis.
- **Single-Point AI Bottlenecks**: Generic language models can produce ungrounded financial advice. FinSight 2.0 uses a **decision-driven multi-agent workflow** with strict failure guards to keep every analysis grounded in verified market data.

---

## ✨ Key Features

- 📈 **Equities & Crypto Analysis**: Real-time market data retrieval for major equities and cryptocurrencies.
- 📰 **Financial News Sentiment**: Aggregate sentiment scoring (positive, negative, neutral) from recent financial news headlines.
- ⚠️ **Composite Risk Assessment**: Rule-based risk scoring incorporating price movement volatility, market direction, and asset type premiums.
- 💼 **Automated Portfolio Recommendations**: Synthesized `BUY`, `HOLD`, or `AVOID` guidance with confidence metrics and decision factors.
- 🔀 **Intent-Based Query Routing**: Natural language interpretation supporting equity tickers (`$AAPL`, `Tesla`), crypto coins (`Bitcoin`, `Solana`), news requests, and ambiguity detection.
- 🔒 **User Authentication & Data Privacy**: JWT authentication with user registration, secure login, protected routes (`ProtectedRoute`), and user-isolated analysis history and watchlists.
- 👁️ **Watchlist Live Monitoring**: Real-time price tracking via WebSockets with target price alert badges and instant AI analysis triggers.
- 💬 **Multi-Turn Conversational LLM Assistant**: Context-grounded multi-turn financial Q&A (`LLMChatAssistant`) powered by hybrid provider synthesis with offline fallback.
- 📊 **System Telemetry & Performance Monitoring**: Pipeline latency tracking, request volume, health indicators, intent distribution, and per-agent execution statistics.
- 📄 **Executive Financial Report Exporter**: One-click structured JSON payload export and print-ready HTML executive financial report generation (printable or saveable as PDF via browser print-to-PDF).
- 🎲 **Monte Carlo Backtesting Engine**: Portfolio simulation engine computing Sharpe ratio, Value at Risk (VaR 95%), max drawdown, and trajectory percentiles.
- 🐳 **Production-Ready Docker & CI/CD Setup**: Multi-container Docker orchestration (FastAPI + Nginx SPA reverse proxy) and GitHub Actions CI workflow.

---

## 🏗️ Multi-Agent Architecture

```text
User Request / Query
       │
       ▼
Query Interpreter
  (Natural language intent & asset classification)
       │
       ▼
Shared Analysis Context  ◄──────────────────────────────────────┐
       │                                                         │
       ├──────► Market Agent (StockAgent / CryptoAgent) ─────────┤ (Updates
       │              │ (Requires successful market data)        │  Shared
       ├──────► Financial News Agent (NewsAgent) ────────────────┤  Context)
       │              │ (Honest failure handling)                │
       ├──────► Risk Analysis Agent (RiskAgent) ─────────────────┤
       │              │ (Requires market data)                   │
       └──────► Portfolio Recommendation Agent (PortfolioAgent) ─┘
                      (Gated on verified market, risk & news data)
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.13, FastAPI, SQLAlchemy, SQLite, Pydantic v2, Uvicorn, WebSockets.
- **Frontend**: React 18, Vite, React Router DOM v7, Lucide Icons, Nginx.
- **External Services**: Alpha Vantage API (Stocks), CoinGecko API (Crypto), NewsData API (News), LLM Services (OpenAI/Gemini/Anthropic).
- **Containerization & CI/CD**: Docker, Docker Compose, Nginx Reverse Proxy, GitHub Actions.
- **Testing**: Pytest, FastAPI TestClient, unittest.mock.

---

## 📁 Project Structure

```text
smartfinance_agenticai/
├── .github/workflows/         # CI/CD Workflows
│   └── ci.yml                 # Automated pytest & frontend build workflow
├── agents/                     # Multi-Agent Intelligence Engine
│   ├── analysis_context.py     # Shared AnalysisContext state & telemetry
│   ├── orchestrator.py         # Dynamic pipeline orchestrator & decision guards
│   ├── stock_agent.py          # Stock quote & sentiment agent
│   ├── crypto_agent.py         # Crypto quote & trend agent
│   ├── news_agent.py           # Financial news & sentiment agent
│   ├── risk_agent.py           # Volatility & risk scoring agent
│   └── portfolio_agent.py      # Recommendation synthesis agent
├── backend/                    # FastAPI Backend Application
│   ├── main.py                 # App entry point & middleware
│   ├── routes.py               # REST & WebSocket API endpoints
│   ├── database.py             # SQLAlchemy engine & SQLite schema migration
│   ├── models.py               # Database ORM models
│   └── schemas.py              # Pydantic request/response validation schemas
├── services/                   # Service & Repository Layer
│   ├── alpha_vantage.py        # Alpha Vantage API client wrapper
│   ├── coingecko.py            # CoinGecko API client wrapper
│   ├── newsdata.py             # NewsData API client wrapper
│   ├── query_interpreter.py    # Natural language intent classifier & parser
│   ├── backtest_engine.py      # Monte Carlo simulation engine
│   ├── auth_service.py         # JWT & Password authentication service
│   ├── llm_service.py          # LLM reasoning & chat synthesis service
│   ├── ticker_streamer.py      # WebSocket real-time ticker stream manager
│   ├── telemetry_service.py    # System performance telemetry manager
│   ├── export_service.py       # JSON payload & HTML report export generator
│   ├── user_repository.py      # User & Watchlist CRUD repository
│   └── analysis_repository.py  # Database CRUD repository
├── frontend/                   # React + Vite Frontend Application
│   ├── src/
│   │   ├── components/         # Header, Sidebar, AgentDashboard, ResultCard, LiveTickerStream, WatchlistWidget, LLMChatAssistant, ExportReportModal, ProtectedRoute
│   │   ├── context/            # AuthContext & FinancialContext API state providers
│   │   ├── pages/              # 11 Application Pages (Home, Stock, Crypto, News, Risk, Portfolio, Agents, Analytics, History, Settings, Login)
│   │   ├── App.jsx             # Main Router Layout & Auth Protection
│   │   └── index.css           # Global stylesheet & design system
│   ├── nginx.conf              # Production Nginx reverse proxy configuration
│   ├── Dockerfile              # Multi-stage frontend Dockerfile
│   └── package.json            # Frontend dependencies & scripts
├── tests/                      # Automated Unit & Integration Tests (191 tests)
├── Dockerfile                  # Backend Python Dockerfile
├── docker-compose.yml          # Multi-container orchestration specification
├── .dockerignore               # Docker build exclusions
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions (.env, db, venv, node_modules)
├── CHANGELOG.md                # Version history & milestone records
├── PROJECT_PLAN.md             # Architecture overview & development roadmap
├── README.md                   # Project documentation (You are here!)
├── TODO.md                     # Development task list
└── requirements.txt            # Python dependencies
```

---

## ⚙️ Setup & Installation Instructions

### Prerequisites
- Python 3.10+ or Docker & Docker Compose
- Node.js 18+ (for local frontend development)

---

### 🐳 Option A: Production Docker Container Deployment (Recommended)

1. **Clone repository & prepare environment**:
   ```bash
   cp .env.example .env
   ```

2. **Build and launch with Docker Compose**:
   ```bash
   docker compose up --build -d
   ```

3. **Access Services**:
   - **Frontend Dashboard**: [http://localhost:80](http://localhost:80)
   - **Backend REST API**: [http://localhost:8000](http://localhost:8000)
   - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

4. **Stop Containers**:
   ```bash
   docker compose down
   ```

---

### 💻 Option B: Local Manual Setup

1. **Backend Setup**:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access local frontend at [http://localhost:5173](http://localhost:5173).

---

## 🧪 Testing & Verification

Run backend Pytest suite:
```bash
.\venv\Scripts\pytest.exe
```
*Verification: 191 unit & integration tests passing.*

Run frontend production build verification:
```bash
cd frontend
npm run build
```

---

## 🔍 Example Queries & System Outputs

| Query Scenario | Natural Language Query | Agents Executed | Output Recommendation | Decision Trace Behavior |
| :--- | :--- | :--- | :---: | :--- |
| **Stock Analysis** | `"Analyze Apple stock $AAPL"` | `StockAgent` → `NewsAgent` → `RiskAgent` → `PortfolioAgent` | **`BUY`** | Full 5-step pipeline execution; calculates composite risk score (25) and generates `BUY` with high confidence. |
| **Crypto Analysis** | `"How is Bitcoin performing?"` | `CryptoAgent` → `NewsAgent` → `RiskAgent` → `PortfolioAgent` | **`AVOID`** | 24h market trend evaluation; applies crypto risk premium (+10) and flags high volatility. |
| **Financial News** | `"What is the latest stock market news?"` | `NewsAgent` | *N/A (News Only)* | Routes strictly to `NewsAgent`; bypasses database persistence and portfolio recommendation. |
| **Unsupported Query** | `"Tell me a funny joke"` | *None* | **`UNSUPPORTED`** | Halts execution immediately at Query Interpreter stage without calling market APIs. |
| **News API Failure** | `"Analyze Tesla"` (News API Offline) | `StockAgent` → `NewsAgent` → `RiskAgent` | **`UNAVAILABLE`** | Preserves valid market & risk scores; blocks `PortfolioAgent` to prevent ungrounded recommendations. |

---

## 🛡️ Security, Sanitization & Error Handling

- **Credential & Secret Protection**: All external API keys (`ALPHA_VANTAGE_API_KEY`, `NEWS_DATA_API_KEY`) and JWT secrets (`SECRET_KEY`) are managed exclusively via environment variables (`.env`). User-facing error messages sanitize system tracebacks, internal file paths, and authorization headers.
- **Route Protection Guards**: `ProtectedRoute` verifies JWT token authenticity before granting access to dashboard routes (`/stocks`, `/crypto`, `/news`, `/risk`, `/portfolio`, `/agents`, `/analytics`, `/history`, `/settings`). Unauthenticated requests automatically redirect to `/login`.
- **User Data Isolation**: User analysis records and watchlists are strictly bound by `user_id`. Report exports check account ownership, returning `403 Forbidden` for unauthorized export requests.

---

## 💡 System Limitations & Future Improvements

### Current Limitations
- **Educational Scope**: Software recommendations are computed deterministically via rule-based algorithms and do not execute live broker transactions.
- **API Rate Limits**: Third-party free-tier APIs (Alpha Vantage, CoinGecko, NewsData) enforce request rate limits.

### Future Improvements
- 🔗 **Direct Brokerage Integration**: Connect Alpaca or Interactive Brokers APIs for automated paper trading execution.
- 🌍 **Multi-Currency Support**: Expand price quotes and portfolio valuation beyond USD to EUR, GBP, and JPY.
- 📊 **Custom Macroeconomic Risk Models**: Incorporate Federal Reserve interest rate benchmarks and inflation metrics into `RiskAgent` scoring.

---

## ⚠️ Financial Disclaimer

**SmartFinancial Advisor (FinSight 2.0)** is an educational software project for algorithmic data synthesis and personal finance research. All recommendations, scores, and analysis summaries are generated automatically by software logic and **do not constitute professional financial advice**. Always consult a certified financial advisor before making real-world investment decisions.

