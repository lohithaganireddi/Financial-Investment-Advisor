# SmartFinancial Advisor (FinSight 2.0) 🚀

Welcome to **SmartFinancial Advisor (FinSight 2.0)**! This is a long-term project designed to build a multi-agent financial intelligence application.

Whether you are looking for real-time stock insights, crypto market trends, financial news summaries, or intelligent portfolio advice, FinSight 2.0 brings together specialized AI agents working together to give you clear financial clarity.

---

## 🎯 What are we building?

Instead of relying on a single AI that tries to do everything, FinSight 2.0 uses **specialized agents**. Think of agents like a team of financial experts working in the same room:

1. 📈 **Stock Price Agent** – Fetches real-time stock prices and market data using the **Alpha Vantage API**.
2. 🪙 **Crypto Agent** – Tracks cryptocurrency market prices and stats using the **CoinGecko API**.
3. 📰 **Financial News Agent** – Gathers market headlines and sentiment using the **NewsData API**.
4. ⚠️ **Risk Analysis Agent** – Evaluates stock/crypto volatile trends, risk scores, and market exposure.
5. 💼 **Portfolio Recommendation Agent** – Synthesizes data from all agents to provide personalized investment recommendations.

---

## 📁 Project Structure

The codebase is organized into clear, modular components so it is easy to read, expand, and maintain week by week:

```text
smartfinance_agenticai/
├── agents/             # Autonomous AI agents (Stock, Crypto, News, Risk, Portfolio)
├── backend/            # API endpoints, data models, and backend services
├── frontend/           # User dashboard (UI framework to be selected in future phase)
├── services/           # Third-party API wrappers (Alpha Vantage, CoinGecko, NewsData)
├── tests/              # Unit tests and integration tests
├── .env                # Local environment variables and API keys (git-ignored)
├── .env.example        # Environment variable template
├── .gitignore          # Files and folders ignored by Git
├── CHANGELOG.md        # Record of updates and progress
├── PROJECT_PLAN.md     # Detailed architecture and long-term project vision
├── README.md           # Project overview and guide (You are here!)
└── TODO.md             # Weekly task list and development roadmap
```

---

## 🔌 API Endpoints & Persistence

The backend provides a FastAPI service with local SQLite persistence (`smartfinance.db`):

- **`GET /`** – API status and documentation link.
- **`GET /health`** – Backend service health check.
- **`POST /api/analyze`** – Direct multi-agent asset analysis endpoint.
- **`POST /api/query`** – Natural language query analysis with **intent routing**: stock and crypto queries run the full multi-agent pipeline and persist to database (including structured `agent_activity`); general financial news queries (`"What's happening in the market?"`) are routed directly to the News Agent without DB persistence. Returns `intent` field (`STOCK_ANALYSIS`, `CRYPTO_ANALYSIS`, `GENERAL_FINANCIAL_NEWS`, or `UNSUPPORTED`).
- **`GET /api/history`** – Retrieve recent saved financial asset analyses (limit 1 to 50), including persisted `agent_activity` sequence logs.
- **`GET /api/history/{id}`** – Retrieve a specific saved analysis record by ID, including its stored `agent_activity` pipeline telemetry.


---

## 🔀 Dynamic Agent Routing

FinSight 2.0 uses **deterministic intent-based routing**. When you send a natural language query, the system:

1. **QueryInterpreter** classifies the query into an intent:
   - **Expanded Equities**: AAPL, MSFT, TSLA, NVDA, AMZN, GOOGL, META, NFLX, AMD, INTC, KO, WMT.
   - **Expanded Crypto**: Bitcoin, Ethereum, Solana, Dogecoin, Cardano, XRP/Ripple, Binance Coin, Polygon.
   - **Smart Normalization & Boundary Matching**: Handles `$AAPL`, punctuation, and exact word boundaries (`\b...\b`).
   - **Explicit News Routing**: Queries matching an asset with explicit news intent (e.g. `"Apple stock news"`) route directly to `GENERAL_FINANCIAL_NEWS` with `news_query`.
   - **Ambiguity Guard**: Queries mentioning multiple distinct assets (e.g. `"Compare Apple and Tesla"`) return `UNSUPPORTED` with a helpful message.
2. **Orchestrator.run_intent()** selects and executes the correct agent pipeline.
3. Every response includes an **`agents_used`** list and a structured **`agent_activity`** array recording step-by-step execution details (`agent`, `status`, `order`, `summary`).

| Intent | Agents Executed | DB Persist? |
|--------|----------------|-------------|
| `STOCK_ANALYSIS` | StockAgent → NewsAgent → RiskAgent → PortfolioAgent | ✅ Yes |
| `CRYPTO_ANALYSIS` | CryptoAgent → NewsAgent → RiskAgent → PortfolioAgent | ✅ Yes |
| `GENERAL_FINANCIAL_NEWS` | NewsAgent only | ❌ No |
| `UNSUPPORTED` | None | ❌ No |

This architecture keeps routing logic in one place (the Orchestrator), tracking real-time execution status for the frontend Agent Activity Dashboard (`AgentDashboard.jsx`).

The **Agent Activity Dashboard** visualizes:
- **Analysis Context Banner**: Displays active asset identifier, analysis type, user prompt query, recommendation badge, and risk level.
- **Executed Pipeline Flow**: Dynamic horizontal flow bar (`Agent A → Agent B → Agent C → Agent D`) with human-friendly display names (`Stock Price Agent`, `Crypto Agent`, `Financial News Agent`, `Risk Analysis Agent`, `Portfolio Recommendation Agent`).
- **Summary Metrics**: Total Agents Executed, Successful, Failed, and Pipeline Status.
- **Vertical Execution Timeline**: Step-by-step sequence (`#1` → `#2` → `#3` → `#4`) with status markers and agent icons.
- **Agent Telemetry Table**: Agent names, status badges, sequence numbers, and execution summaries.
- **Tab Navigation**: Seamless toggling between **Financial Intelligence Dashboard** and **Agent Activity Dashboard**.






## ⚙️ Getting Started (Day 1 Foundation)

1. **Clone or open the repository**:
   Open this folder in your favorite code editor (VS Code, Cursor, Antigravity, etc.).

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` (if not already present):
   ```bash
   cp .env.example .env
   ```
   *Note: Never hardcode API keys directly into code! Always keep your keys inside `.env`.*

3. **Explore the Roadmap**:
   Check `PROJECT_PLAN.md` for the architectural overview and `TODO.md` to see upcoming development tasks.

---

## 📜 Development Guidelines
- **Modularity First**: Keep agents, backend routes, and services separated.
- **Security First**: Keep API keys in `.env` and never check sensitive files into version control.
- **Incremental Steps**: Build one layer at a time (APIs -> Agents -> Backend -> Frontend -> Auth).

---

## 📄 License
This project is open-source and intended for educational and personal finance research purposes.
