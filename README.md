# SmartFinancial Advisor (FinSight 2.0) 🚀

Welcome to **SmartFinancial Advisor (FinSight 2.0)**! A deterministic, decision-driven multi-agent financial intelligence system that coordinates specialized AI agents to analyze stocks, cryptocurrency, and market news to deliver actionable portfolio recommendations and risk assessments.

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
- 📊 **Agent Telemetry & Activity Dashboard**: Step-by-step pipeline execution tracking (`agents_used`, duration timing, step status, decision rationales).
- 💾 **Historical Analysis Persistence**: Automatic storage of search queries, risk scores, recommendations, and execution telemetry in SQLite.
- 🖥️ **Multi-Page React Frontend**: 10 distinct pages including Dashboard, Stock Analysis, Crypto Analysis, News, Risk Dashboard, Portfolio Advisor, Agent Activity, Analytics, History, and Settings.
- ⚡ **Real-Time Data Streaming**: WebSockets ticker engine providing live price updates.
- 🤖 **LLM Reasoning Layer**: Hybrid LLM reasoning synthesis with fallback options.
- 🐳 **Dockerization & CI/CD Pipeline**: Multi-container Docker orchestration and GitHub Actions CI workflow.

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
│   ├── llm_service.py          # LLM reasoning synthesis service
│   ├── ticker_streamer.py      # WebSocket real-time ticker stream manager
│   ├── user_repository.py      # User & Watchlist CRUD repository
│   └── analysis_repository.py  # Database CRUD repository
├── frontend/                   # React + Vite Frontend Application
│   ├── src/
│   │   ├── components/         # Header, Sidebar, AgentDashboard, ResultCard, LiveTickerStream, etc.
│   │   ├── context/            # FinancialContext API state provider
│   │   ├── pages/              # 10 Application Pages
│   │   ├── App.jsx             # Main Router Layout
│   │   └── index.css           # Global stylesheet & design system
│   ├── nginx.conf              # Production Nginx reverse proxy configuration
│   ├── Dockerfile              # Multi-stage frontend Dockerfile
│   └── package.json            # Frontend dependencies & scripts
├── tests/                      # Automated Unit & Integration Tests
├── Dockerfile                  # Backend Python Dockerfile
├── docker-compose.yml          # Multi-container orchestration specification
├── .dockerignore               # Docker build exclusions
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions (.env, db, venv, node_modules)
├── CHANGELOG.md                # Version history & milestone records
├── PROJECT_PLAN.md             # Architecture overview & development roadmap
├── README.md                   # Project documentation (You are here!)
└── TODO.md                     # Development task list
```

---

## ⚙️ Setup & Installation Instructions

### Prerequisites
- Python 3.10+ or Docker & Docker Compose
- Node.js 18+ (for local frontend development)

---

### 🐳 Option A: Production Docker Deployment (Recommended)

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

## 🧪 Testing

Run backend Pytest suite:
```bash
.\venv\Scripts\pytest.exe
```
*Verification: 181 unit & integration tests passing.*

Run frontend production build verification:
```bash
cd frontend
npm run build
```

---

## ⚠️ Financial Disclaimer

**SmartFinancial Advisor (FinSight 2.0)** is an educational software project for algorithmic data synthesis and personal finance research. All recommendations, scores, and analysis summaries are generated automatically by software logic and **do not constitute professional financial advice**. Always consult a certified financial advisor before making real-world investment decisions.
