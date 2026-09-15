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

### 🤖 Specialized Agents

1. **Stock Price Agent (`StockAgent`)**: Interacts with the **Alpha Vantage API** to fetch stock quotes, percentage changes, and directional trend summaries.
2. **Crypto Agent (`CryptoAgent`)**: Interacts with the **CoinGecko API** to retrieve 24-hour cryptocurrency price action, market cap, and volume statistics.
3. **Financial News Agent (`NewsAgent`)**: Interacts with the **NewsData API** to analyze business news headlines and calculate keyword sentiment scores.
4. **Risk Analysis Agent (`RiskAgent`)**: Evaluates market movement volatility and trend direction to compute a composite risk score (0–100) and risk level (`low`, `medium`, `high`).
5. **Portfolio Recommendation Agent (`PortfolioAgent`)**: Combines market direction, risk levels, and news sentiment into a final recommendation score, action (`buy`, `hold`, `avoid`), and confidence level.

### 🧠 Shared `AnalysisContext` & Decision Pipeline

The system uses a shared `AnalysisContext` dataclass (`agents/analysis_context.py`) that maintains state throughout execution:
- **`market_data`**, **`news_data`**, **`risk_data`**, and **`portfolio_data`** are populated progressively.
- Downstream decision helpers inspect context state before invoking dependent agents:
  - `should_fetch_news`: Evaluates for stock, crypto, or news intent with valid search queries.
  - `should_analyze_risk`: Requires verified, successful market data.
  - `should_generate_portfolio_recommendation`: Requires successful market data, risk data, AND real news data.
- **Honest Failure Policy**: If `NewsAgent` fails, `news_data` preserves the raw failure dict. The pipeline continues to `RiskAgent` (market data is sufficient), but `PortfolioAgent` is skipped to avoid fabricating neutral news sentiment.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, SQLite, Pydantic v2.
- **Frontend**: React 18, Vite, React Router DOM v6, Custom CSS with CSS Variables.
- **External Services**: Alpha Vantage API (Stocks), CoinGecko API (Crypto), NewsData API (News).
- **Testing**: Pytest, FastAPI TestClient, unittest.mock.

---

## 📁 Project Structure

```text
smartfinance_agenticai/
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
│   ├── routes.py               # REST API endpoints (/api/analyze, /api/query, /api/history)
│   ├── database.py             # SQLAlchemy engine & SQLite schema migration
│   ├── models.py               # Database ORM models
│   └── schemas.py              # Pydantic request/response validation schemas
├── services/                   # Service & Repository Layer
│   ├── alpha_vantage.py        # Alpha Vantage API client wrapper
│   ├── coingecko.py            # CoinGecko API client wrapper
│   ├── newsdata.py             # NewsData API client wrapper
│   ├── query_interpreter.py    # Natural language intent classifier & parser
│   └── analysis_repository.py  # Database CRUD repository
├── frontend/                   # React + Vite Frontend Application
│   ├── src/
│   │   ├── components/         # Header, Sidebar, AgentDashboard, ResultCard, etc.
│   │   ├── context/            # FinancialContext API state provider
│   │   ├── pages/              # 10 Application Pages (Home, Stocks, Crypto, etc.)
│   │   ├── App.jsx             # Main Router Layout
│   │   └── index.css           # Global stylesheet & design system
│   └── package.json            # Frontend dependencies & scripts
├── tests/                      # Automated Unit & Integration Tests
│   ├── test_agents.py          # Agent & AnalysisContext unit tests
│   ├── test_api.py             # Backend API endpoint tests
│   ├── test_query_interpreter.py # Intent classifier tests
│   └── test_services.py        # External API client wrapper tests
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions (.env, db, venv, node_modules)
├── CHANGELOG.md                # Version history & milestone records
├── PROJECT_PLAN.md             # Architecture overview & development roadmap
├── README.md                   # Project documentation (You are here!)
└── TODO.md                     # Completed V1.0 tasks & future roadmap
```

---

## ⚙️ Setup & Installation Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher & npm

### 1. Environment Configuration

Copy `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```

Configure your API keys in `.env` (the application works with fallback/mock data if keys are omitted):
```ini
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWSDATA_API_KEY=your_newsdata_key
DATABASE_URL=sqlite:///./smartfinance.db
```

*Note: Never commit `.env` or hardcode API keys! `.env` is git-ignored.*

### 2. Backend Setup & Running

```bash
# Create and activate Python virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend server
uvicorn backend.main:app --reload --port 8000
```
Backend API interactive documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Frontend Setup & Running

```bash
# Navigate to frontend directory
cd frontend

# Install Node packages
npm install

# Start Vite development server
npm run dev
```
Frontend web application will be available at [http://localhost:5173](http://localhost:5173).

---

## 🧪 Testing

Run the backend test suite:
```bash
.\venv\Scripts\pytest.exe -q
```
*Verification: 138 unit and integration tests passing.*

Run the frontend production build test:
```bash
cd frontend
npm run build
```
*Verification: Vite build compiles with 0 errors.*

---

## 💬 Example Queries

- **Equities Analysis**: `"Should I invest in Apple?"` or `"Analyze TSLA"`
- **Cryptocurrency Analysis**: `"What is the risk of Bitcoin?"` or `"Tell me about Ethereum"`
- **General News Query**: `"Latest financial news"`
- **Specific Asset News**: `"Apple stock news"`
- **Ambiguous Multi-Asset Query**: `"Compare Apple and Tesla"` *(Returns UNSUPPORTED with multi-asset single-asset guidance)*

---

## ⚠️ Financial Disclaimer

**SmartFinancial Advisor (FinSight 2.0)** is an educational software project for algorithmic data synthesis and personal finance research. All recommendations, scores, and analysis summaries are generated automatically by software logic and **do not constitute professional financial advice**. Always consult a certified financial advisor before making real-world investment decisions.
