"""
Unit tests for AI Agent Modules

Verifies StockAgent, CryptoAgent, and NewsAgent input validation, service integration, market trend evaluation,
and sentiment analysis using mock services without live network calls.
"""

from unittest.mock import MagicMock
from agents.stock_agent import StockAgent
from agents.crypto_agent import CryptoAgent
from agents.news_agent import NewsAgent
from agents.risk_agent import RiskAgent
from agents.portfolio_agent import PortfolioAgent
from agents.orchestrator import Orchestrator
from agents.analysis_context import AnalysisContext


# ==========================================
# StockAgent Unit Tests
# ==========================================

def test_stock_agent_invalid_symbols():
    """Test that invalid symbol inputs return an error dictionary."""
    agent = StockAgent(service=MagicMock())

    res1 = agent.analyze_stock("")
    assert res1["success"] is False
    assert "Invalid stock symbol" in res1["error"]

    res2 = agent.analyze_stock("   ")
    assert res2["success"] is False
    assert "Invalid stock symbol" in res2["error"]


def test_stock_agent_bullish_analysis():
    """Test StockAgent evaluation of a bullish stock price quote."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": True,
        "data": {
            "symbol": "AAPL",
            "open": 180.00,
            "high": 185.00,
            "low": 179.00,
            "price": 184.50,
            "volume": 50000000,
            "latest_trading_day": "2026-09-15",
            "previous_close": 182.00,
            "change": 2.50,
            "change_percent": "1.3736%"
        }
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("aapl")

    assert result["success"] is True
    assert result["agent"] == "StockAgent"
    assert result["symbol"] == "AAPL"
    assert result["price"] == 184.50
    assert result["change"] == 2.50
    assert result["change_percent"] == 1.3736
    assert result["market_direction"] == "bullish"
    assert "bullish momentum" in result["analysis"]
    assert result["details"]["volume"] == 50000000
    mock_service.get_stock_quote.assert_called_once_with("AAPL")


def test_stock_agent_bearish_analysis():
    """Test StockAgent evaluation of a bearish stock price quote."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": True,
        "data": {
            "symbol": "MSFT",
            "open": 410.00,
            "high": 412.00,
            "low": 402.00,
            "price": 405.00,
            "volume": 25000000,
            "latest_trading_day": "2026-09-15",
            "previous_close": 415.00,
            "change": -10.00,
            "change_percent": "-2.4096%"
        }
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("MSFT")

    assert result["success"] is True
    assert result["symbol"] == "MSFT"
    assert result["price"] == 405.00
    assert result["change"] == -10.00
    assert result["change_percent"] == -2.4096
    assert result["market_direction"] == "bearish"
    assert "bearish pressure" in result["analysis"]


def test_stock_agent_neutral_analysis():
    """Test StockAgent evaluation of a neutral stock price quote."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": True,
        "data": {
            "symbol": "IBM",
            "open": 140.00,
            "high": 141.00,
            "low": 139.50,
            "price": 140.00,
            "volume": 10000000,
            "latest_trading_day": "2026-09-15",
            "previous_close": 140.00,
            "change": 0.00,
            "change_percent": "0.00%"
        }
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("IBM")

    assert result["success"] is True
    assert result["symbol"] == "IBM"
    assert result["price"] == 140.00
    assert result["change"] == 0.00
    assert result["market_direction"] == "neutral"
    assert "neutral market consolidation" in result["analysis"]


def test_stock_agent_unconfigured_service_error():
    """Test that StockAgent propagates service errors gracefully."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {
        "success": False,
        "error": "Missing or unconfigured Alpha Vantage API key. Please set ALPHA_VANTAGE_API_KEY in your .env file."
    }

    agent = StockAgent(service=mock_service)
    result = agent.analyze_stock("AAPL")

    assert result["success"] is False
    assert result["agent"] == "StockAgent"
    assert result["symbol"] == "AAPL"
    assert "Missing or unconfigured Alpha Vantage API key" in result["error"]


def test_stock_agent_dependency_injection():
    """Verify that dependency injection works and default service instantiates cleanly."""
    mock_service = MagicMock()
    mock_service.get_stock_quote.return_value = {"success": False, "error": "Mocked call"}

    agent = StockAgent(service=mock_service)
    assert agent.service == mock_service


# ==========================================
# CryptoAgent Unit Tests
# ==========================================

def test_crypto_agent_invalid_coin_id():
    """Test that invalid coin ID inputs return an error dictionary."""
    agent = CryptoAgent(service=MagicMock())

    res1 = agent.analyze_crypto("")
    assert res1["success"] is False
    assert "Invalid cryptocurrency coin ID" in res1["error"]

    res2 = agent.analyze_crypto("   ")
    assert res2["success"] is False
    assert "Invalid cryptocurrency coin ID" in res2["error"]


def test_crypto_agent_bullish_analysis():
    """Test CryptoAgent evaluation of a bullish cryptocurrency quote."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": True,
        "data": {
            "id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "price": 65000.00,
            "high_24h": 66500.00,
            "low_24h": 64200.00,
            "change_percent_24h": 2.15,
            "market_cap": 1280000000000,
            "volume_24h": 35000000000.0,
            "last_updated": "2026-09-15T12:00:00.000Z"
        }
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto(" BITCOIN ")

    assert result["success"] is True
    assert result["agent"] == "CryptoAgent"
    assert result["coin_id"] == "bitcoin"
    assert result["symbol"] == "BTC"
    assert result["name"] == "Bitcoin"
    assert result["price"] == 65000.00
    assert result["change_percent_24h"] == 2.15
    assert result["market_direction"] == "bullish"
    assert "bullish momentum" in result["analysis"]
    assert result["details"]["market_cap"] == 1280000000000
    mock_service.get_crypto_price.assert_called_once_with("bitcoin")


def test_crypto_agent_bearish_analysis():
    """Test CryptoAgent evaluation of a bearish cryptocurrency quote."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": True,
        "data": {
            "id": "ethereum",
            "symbol": "ETH",
            "name": "Ethereum",
            "price": 3400.00,
            "high_24h": 3550.00,
            "low_24h": 3380.00,
            "change_percent_24h": -3.50,
            "market_cap": 400000000000,
            "volume_24h": 15000000000.0,
            "last_updated": "2026-09-15T12:00:00.000Z"
        }
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto("ETHEREUM")

    assert result["success"] is True
    assert result["coin_id"] == "ethereum"
    assert result["symbol"] == "ETH"
    assert result["price"] == 3400.00
    assert result["change_percent_24h"] == -3.50
    assert result["market_direction"] == "bearish"
    assert "bearish pressure" in result["analysis"]


def test_crypto_agent_neutral_analysis():
    """Test CryptoAgent evaluation of a neutral cryptocurrency quote."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": True,
        "data": {
            "id": "tether",
            "symbol": "USDT",
            "name": "Tether",
            "price": 1.00,
            "high_24h": 1.001,
            "low_24h": 0.999,
            "change_percent_24h": 0.00,
            "market_cap": 110000000000,
            "volume_24h": 50000000000.0,
            "last_updated": "2026-09-15T12:00:00.000Z"
        }
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto("tether")

    assert result["success"] is True
    assert result["coin_id"] == "tether"
    assert result["price"] == 1.00
    assert result["change_percent_24h"] == 0.00
    assert result["market_direction"] == "neutral"
    assert "neutral sideways price action" in result["analysis"]


def test_crypto_agent_unconfigured_service_error():
    """Test that CryptoAgent propagates service configuration errors gracefully."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {
        "success": False,
        "error": "Missing or unconfigured CoinGecko API key. Please set COINGECKO_API_KEY in your .env file."
    }

    agent = CryptoAgent(service=mock_service)
    result = agent.analyze_crypto("bitcoin")

    assert result["success"] is False
    assert result["agent"] == "CryptoAgent"
    assert result["coin_id"] == "bitcoin"
    assert "Missing or unconfigured CoinGecko API key" in result["error"]


def test_crypto_agent_dependency_injection():
    """Verify that dependency injection works and default service instantiates cleanly."""
    mock_service = MagicMock()
    mock_service.get_crypto_price.return_value = {"success": False, "error": "Mocked call"}

    agent = CryptoAgent(service=mock_service)
    assert agent.service == mock_service


# ==========================================
# NewsAgent Unit Tests
# ==========================================

def test_news_agent_invalid_query():
    """Test that invalid query inputs return an error dictionary."""
    agent = NewsAgent(service=MagicMock())

    res1 = agent.analyze_news("")
    assert res1["success"] is False
    assert "Invalid search query" in res1["error"]

    res2 = agent.analyze_news("   ")
    assert res2["success"] is False
    assert "Invalid search query" in res2["error"]


def test_news_agent_successful_analysis():
    """Test NewsAgent evaluation of financial news articles."""
    mock_service = MagicMock()
    mock_service.get_financial_news.return_value = {
        "success": True,
        "total_results": 1,
        "data": [
            {
                "article_id": "art_100",
                "title": "Markets Rally Following Strong Growth Reports",
                "link": "https://news.example.com/art_100",
                "description": "Stock indices saw high profit gains and record surges today.",
                "pubDate": "2026-09-15 10:00:00",
                "source": "financial_times"
            }
        ]
    }

    agent = NewsAgent(service=mock_service)
    result = agent.analyze_news("finance", "business", "en")

    assert result["success"] is True
    assert result["agent"] == "NewsAgent"
    assert result["query"] == "finance"
    assert result["category"] == "business"
    assert result["language"] == "en"
    assert result["total_results"] == 1
    assert result["overall_sentiment"] == "positive"
    assert "positive" in result["summary"]
    articles = result["articles"]
    assert len(articles) == 1
    assert articles[0]["article_id"] == "art_100"
    assert articles[0]["published_at"] == "2026-09-15 10:00:00"
    assert articles[0]["sentiment"] == "positive"
    mock_service.get_financial_news.assert_called_once_with(query="finance", category="business", language="en")


def test_news_agent_positive_sentiment():
    """Test NewsAgent positive sentiment scoring across articles."""
    mock_service = MagicMock()
    mock_service.get_financial_news.return_value = {
        "success": True,
        "total_results": 1,
        "data": [
            {
                "article_id": "art_101",
                "title": "Tech Stocks Surge With High Record Growth",
                "link": "https://news.example.com/101",
                "description": "Bullish rally and strong profit gains across the tech sector.",
                "pubDate": "2026-09-15 11:00:00",
                "source": "bloomberg"
            }
        ]
    }

    agent = NewsAgent(service=mock_service)
    result = agent.analyze_news("stocks")

    assert result["success"] is True
    assert result["overall_sentiment"] == "positive"
    assert result["articles"][0]["sentiment"] == "positive"


def test_news_agent_negative_sentiment():
    """Test NewsAgent negative sentiment scoring across articles."""
    mock_service = MagicMock()
    mock_service.get_financial_news.return_value = {
        "success": True,
        "total_results": 1,
        "data": [
            {
                "article_id": "art_102",
                "title": "Markets Plunge Amid Recession Warning",
                "link": "https://news.example.com/102",
                "description": "Severe crash and steep decline as inflation risk rises.",
                "pubDate": "2026-09-15 11:30:00",
                "source": "reuters"
            }
        ]
    }

    agent = NewsAgent(service=mock_service)
    result = agent.analyze_news("recession")

    assert result["success"] is True
    assert result["overall_sentiment"] == "negative"
    assert result["articles"][0]["sentiment"] == "negative"


def test_news_agent_neutral_sentiment():
    """Test NewsAgent neutral sentiment scoring for balanced headlines."""
    mock_service = MagicMock()
    mock_service.get_financial_news.return_value = {
        "success": True,
        "total_results": 1,
        "data": [
            {
                "article_id": "art_103",
                "title": "Central Bank Holds Quarterly Monetary Policy Meeting",
                "link": "https://news.example.com/103",
                "description": "Officials met today to review current benchmark interest rates.",
                "pubDate": "2026-09-15 12:00:00",
                "source": "wsj"
            }
        ]
    }

    agent = NewsAgent(service=mock_service)
    result = agent.analyze_news("central bank")

    assert result["success"] is True
    assert result["overall_sentiment"] == "neutral"
    assert result["articles"][0]["sentiment"] == "neutral"


def test_news_agent_empty_news_results():
    """Test that NewsAgent handles empty article lists gracefully."""
    mock_service = MagicMock()
    mock_service.get_financial_news.return_value = {
        "success": False,
        "error": "No news articles found for query 'unknown_xyz'."
    }

    agent = NewsAgent(service=mock_service)
    result = agent.analyze_news("unknown_xyz")

    assert result["success"] is False
    assert result["agent"] == "NewsAgent"
    assert result["query"] == "unknown_xyz"
    assert "No news articles found" in result["error"]


def test_news_agent_unconfigured_service_error():
    """Test that NewsAgent propagates unconfigured service API key errors cleanly."""
    mock_service = MagicMock()
    mock_service.get_financial_news.return_value = {
        "success": False,
        "error": "Missing or unconfigured NewsData API key. Please set NEWSDATA_API_KEY in your .env file."
    }

    agent = NewsAgent(service=mock_service)
    result = agent.analyze_news("finance")

    assert result["success"] is False
    assert result["agent"] == "NewsAgent"
    assert result["query"] == "finance"
    assert "Missing or unconfigured NewsData API key" in result["error"]


def test_news_agent_dependency_injection():
    """Verify dependency injection works and default service instantiates cleanly."""
    mock_service = MagicMock()
    mock_service.get_financial_news.return_value = {"success": False, "error": "Mocked call"}

    agent = NewsAgent(service=mock_service)
    assert agent.service == mock_service


# ==========================================
# RiskAgent Unit Tests
# ==========================================

def test_risk_agent_invalid_input_type():
    """Test that non-dict input returns a validation error."""
    agent = RiskAgent()

    for bad_input in ["string", 42, None, ["list"], 3.14]:
        result = agent.analyze_risk(bad_input)
        assert result["success"] is False
        assert result["agent"] == "RiskAgent"
        assert "dictionary" in result["error"]


def test_risk_agent_empty_data():
    """Test that an empty dict returns a validation error."""
    agent = RiskAgent()
    result = agent.analyze_risk({})
    assert result["success"] is False
    assert result["agent"] == "RiskAgent"
    assert "empty" in result["error"].lower()


def test_risk_agent_failed_upstream_agent():
    """Test that a failed upstream agent result (success=False) is rejected."""
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": False,
        "agent": "StockAgent",
        "symbol": "AAPL",
        "error": "API key missing"
    })
    assert result["success"] is False
    assert result["agent"] == "RiskAgent"
    assert "failure" in result["error"].lower()


def test_risk_agent_unsupported_agent():
    """Test that an unsupported upstream agent name returns a validation error."""
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": True,
        "agent": "WeatherAgent",
        "symbol": "AAPL",
        "change_percent": 1.5,
        "market_direction": "bullish"
    })
    assert result["success"] is False
    assert result["agent"] == "RiskAgent"
    assert "Unsupported" in result["error"] or "unsupported" in result["error"].lower()


def test_risk_agent_stock_low_risk():
    """
    Test StockAgent input that should produce a low risk score.
    Stock base=30, movement <=2% -> +0, bullish -> +0, no crypto bonus.
    Expected score: 30 -> "low"
    """
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": True,
        "agent": "StockAgent",
        "symbol": "AAPL",
        "change_percent": 1.5,      # |1.5| <= 2 -> +0
        "market_direction": "bullish"  # -> +0
    })
    assert result["success"] is True
    assert result["agent"] == "RiskAgent"
    assert result["asset"] == "AAPL"
    assert result["asset_type"] == "stock"
    assert result["risk_score"] == 30
    assert result["risk_level"] == "low"
    assert result["score_breakdown"]["base_score"] == 30
    assert result["score_breakdown"]["movement_adjustment"] == 0
    assert result["score_breakdown"]["direction_adjustment"] == 0
    assert result["score_breakdown"]["crypto_bonus"] == 0


def test_risk_agent_stock_medium_risk():
    """
    Test StockAgent input that should produce a medium risk score.
    Stock base=30, movement 3.5% (>2 and <=5) -> +15, neutral -> +10, no crypto bonus.
    Expected score: 30 + 15 + 10 = 55 -> "medium"
    """
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": True,
        "agent": "StockAgent",
        "symbol": "MSFT",
        "change_percent": 3.5,       # |3.5| > 2 and <= 5 -> +15
        "market_direction": "neutral"  # -> +10
    })
    assert result["success"] is True
    assert result["risk_score"] == 55
    assert result["risk_level"] == "medium"
    assert result["score_breakdown"]["base_score"] == 30
    assert result["score_breakdown"]["movement_adjustment"] == 15
    assert result["score_breakdown"]["direction_adjustment"] == 10


def test_risk_agent_stock_high_risk():
    """
    Test StockAgent input that should produce a high risk score.
    Stock base=30, movement 7% (>5) -> +30, bearish -> +20, no crypto bonus.
    Expected score: 30 + 30 + 20 = 80 -> "high"
    """
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": True,
        "agent": "StockAgent",
        "symbol": "GME",
        "change_percent": 7.0,       # |7.0| > 5 -> +30
        "market_direction": "bearish"  # -> +20
    })
    assert result["success"] is True
    assert result["risk_score"] == 80
    assert result["risk_level"] == "high"
    assert result["score_breakdown"]["base_score"] == 30
    assert result["score_breakdown"]["movement_adjustment"] == 30
    assert result["score_breakdown"]["direction_adjustment"] == 20
    assert result["score_breakdown"]["crypto_bonus"] == 0


def test_risk_agent_crypto_medium_or_high_risk():
    """
    Test CryptoAgent input producing a high risk score.
    Crypto base=50, movement 3% (>2 and <=5) -> +15, bullish -> +0, crypto bonus +10.
    Expected score: 50 + 15 + 0 + 10 = 75 -> "high"
    """
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": True,
        "agent": "CryptoAgent",
        "coin_id": "bitcoin",
        "change_percent_24h": 3.0,      # |3.0| > 2 and <= 5 -> +15
        "market_direction": "bullish"    # -> +0
    })
    assert result["success"] is True
    assert result["asset"] == "bitcoin"
    assert result["asset_type"] == "crypto"
    assert result["risk_score"] == 75
    assert result["risk_level"] == "high"
    assert result["score_breakdown"]["base_score"] == 50
    assert result["score_breakdown"]["movement_adjustment"] == 15
    assert result["score_breakdown"]["direction_adjustment"] == 0
    assert result["score_breakdown"]["crypto_bonus"] == 10


def test_risk_agent_bearish_market_increases_risk():
    """
    Test that a bearish market direction increases risk compared to bullish.
    Crypto base=50, movement <=2% -> +0, bearish -> +20, crypto bonus +10.
    Expected score: 50 + 0 + 20 + 10 = 80 -> "high"
    """
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": True,
        "agent": "CryptoAgent",
        "coin_id": "ethereum",
        "change_percent_24h": -1.5,     # |1.5| <= 2 -> +0
        "market_direction": "bearish"    # -> +20
    })
    assert result["success"] is True
    assert result["risk_score"] == 80
    assert result["risk_level"] == "high"
    assert result["market_direction"] == "bearish"
    assert result["score_breakdown"]["direction_adjustment"] == 20
    assert result["score_breakdown"]["crypto_bonus"] == 10


def test_risk_agent_invalid_percentage():
    """Test that a non-parseable percentage string returns a validation error."""
    agent = RiskAgent()
    result = agent.analyze_risk({
        "success": True,
        "agent": "StockAgent",
        "symbol": "AAPL",
        "change_percent": "not-a-number",
        "market_direction": "neutral"
    })
    assert result["success"] is False
    assert result["agent"] == "RiskAgent"
    assert "parse" in result["error"].lower() or "Cannot" in result["error"]



# ==========================================
# PortfolioAgent Unit Tests
# ==========================================

# ---- Shared fixture helpers -----------------------------------------------

def _stock_market_data(direction="bullish"):
    """Return a minimal valid StockAgent output for testing."""
    return {
        "success": True,
        "agent": "StockAgent",
        "symbol": "AAPL",
        "price": 184.5,
        "change": 2.5,
        "change_percent": 1.37,
        "market_direction": direction,
    }

def _risk_data(level="low"):
    """Return a minimal valid RiskAgent output for testing."""
    return {
        "success": True,
        "agent": "RiskAgent",
        "asset": "AAPL",
        "asset_type": "stock",
        "risk_score": 30,
        "risk_level": level,
    }

def _news_data(sentiment="positive"):
    """Return a minimal valid NewsAgent output for testing."""
    return {
        "success": True,
        "agent": "NewsAgent",
        "query": "AAPL",
        "total_results": 5,
        "overall_sentiment": sentiment,
        "articles": [],
    }

# ---- Tests ---------------------------------------------------------------

def test_portfolio_agent_invalid_market_data():
    """Test that non-dict or empty market_data returns a validation error."""
    agent = PortfolioAgent()
    for bad in ["string", 42, None, [], {}]:
        result = agent.generate_recommendation(bad, _risk_data(), _news_data())
        assert result["success"] is False
        assert result["agent"] == "PortfolioAgent"
        assert "market_data" in result["error"]


def test_portfolio_agent_invalid_risk_data():
    """Test that non-dict or empty risk_data returns a validation error."""
    agent = PortfolioAgent()
    for bad in ["string", 42, None, [], {}]:
        result = agent.generate_recommendation(_stock_market_data(), bad, _news_data())
        assert result["success"] is False
        assert result["agent"] == "PortfolioAgent"
        assert "risk_data" in result["error"]


def test_portfolio_agent_invalid_news_data():
    """Test that non-dict or empty news_data returns a validation error."""
    agent = PortfolioAgent()
    for bad in ["string", 42, None, [], {}]:
        result = agent.generate_recommendation(_stock_market_data(), _risk_data(), bad)
        assert result["success"] is False
        assert result["agent"] == "PortfolioAgent"
        assert "news_data" in result["error"]


def test_portfolio_agent_failed_market_agent():
    """Test that a failed market_data (success=False) is rejected."""
    agent = PortfolioAgent()
    bad_market = {
        "success": False,
        "agent": "StockAgent",
        "symbol": "AAPL",
        "error": "API key missing",
    }
    result = agent.generate_recommendation(bad_market, _risk_data(), _news_data())
    assert result["success"] is False
    assert result["agent"] == "PortfolioAgent"
    assert "failure" in result["error"].lower() or "market_data" in result["error"]


def test_portfolio_agent_unsupported_market_agent():
    """Test that an unsupported market agent name returns a validation error."""
    agent = PortfolioAgent()
    bad_market = {
        "success": True,
        "agent": "WeatherAgent",
        "symbol": "AAPL",
        "market_direction": "bullish",
    }
    result = agent.generate_recommendation(bad_market, _risk_data(), _news_data())
    assert result["success"] is False
    assert result["agent"] == "PortfolioAgent"
    assert "WeatherAgent" in result["error"] or "Unsupported" in result["error"]


def test_portfolio_agent_buy_recommendation():
    """
    Test that all-positive signals produce a BUY recommendation with exact score.
    base=50, bullish=+20, low=+15, positive=+15 -> score=100 -> buy
    """
    agent = PortfolioAgent()
    result = agent.generate_recommendation(
        _stock_market_data("bullish"),
        _risk_data("low"),
        _news_data("positive"),
    )
    assert result["success"] is True
    assert result["agent"] == "PortfolioAgent"
    assert result["recommendation_score"] == 100
    assert result["recommendation"] == "buy"
    assert result["confidence"] == "high"
    assert result["asset"] == "AAPL"
    assert result["asset_type"] == "stock"
    assert result["market_direction"] == "bullish"
    assert result["risk_level"] == "low"
    assert result["news_sentiment"] == "positive"
    assert "disclaimer" in result
    assert len(result["factors"]) == 3


def test_portfolio_agent_hold_recommendation():
    """
    Test that neutral signals produce a HOLD recommendation with exact score.
    base=50, neutral=0, medium=0, neutral=0 -> score=50 -> hold
    """
    agent = PortfolioAgent()
    result = agent.generate_recommendation(
        _stock_market_data("neutral"),
        _risk_data("medium"),
        _news_data("neutral"),
    )
    assert result["success"] is True
    assert result["recommendation_score"] == 50
    assert result["recommendation"] == "hold"


def test_portfolio_agent_avoid_recommendation():
    """
    Test that all-negative signals produce an AVOID recommendation with exact score.
    base=50, bearish=-20, high=-20, negative=-15 -> raw=-5 -> capped at 0 -> avoid
    """
    agent = PortfolioAgent()
    result = agent.generate_recommendation(
        _stock_market_data("bearish"),
        _risk_data("high"),
        _news_data("negative"),
    )
    assert result["success"] is True
    assert result["recommendation_score"] == 0
    assert result["recommendation"] == "avoid"
    assert result["confidence"] == "high"


def test_portfolio_agent_high_risk_reduces_score():
    """
    Test that high risk reduces score by 20 vs low risk.
    base=50, bullish=+20, high=-20, positive=+15 -> score=65 -> hold
    """
    agent = PortfolioAgent()
    result = agent.generate_recommendation(
        _stock_market_data("bullish"),
        _risk_data("high"),
        _news_data("positive"),
    )
    assert result["success"] is True
    assert result["recommendation_score"] == 65
    assert result["recommendation"] == "hold"
    assert result["risk_level"] == "high"


def test_portfolio_agent_negative_news_reduces_score():
    """
    Test that negative news reduces score by 15.
    base=50, bullish=+20, low=+15, negative=-15 -> score=70 -> buy
    """
    agent = PortfolioAgent()
    result = agent.generate_recommendation(
        _stock_market_data("bullish"),
        _risk_data("low"),
        _news_data("negative"),
    )
    assert result["success"] is True
    assert result["recommendation_score"] == 70
    assert result["recommendation"] == "buy"
    assert result["news_sentiment"] == "negative"


def test_portfolio_agent_confidence_calculation():
    """Test confidence levels for different signal combinations."""
    agent = PortfolioAgent()

    # 3 positive signals -> high confidence
    r = agent.generate_recommendation(
        _stock_market_data("bullish"), _risk_data("low"), _news_data("positive")
    )
    assert r["confidence"] == "high"

    # 2 positive signals (neutral news) -> medium confidence
    r = agent.generate_recommendation(
        _stock_market_data("bullish"), _risk_data("low"), _news_data("neutral")
    )
    assert r["confidence"] == "medium"

    # Mixed signals (1 positive, 1 negative, 1 neutral) -> low confidence
    r = agent.generate_recommendation(
        _stock_market_data("bullish"), _risk_data("high"), _news_data("neutral")
    )
    assert r["confidence"] == "low"


def test_portfolio_agent_crypto_recommendation():
    """
    Test that CryptoAgent market data works correctly.
    coin_id is the asset identifier; asset_type is crypto.
    base=50, bullish=+20, low=+15, positive=+15 -> score=100 -> buy
    """
    agent = PortfolioAgent()
    crypto_market = {
        "success": True,
        "agent": "CryptoAgent",
        "coin_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "price": 65000.0,
        "change_percent_24h": 3.5,
        "market_direction": "bullish",
    }
    result = agent.generate_recommendation(
        crypto_market,
        _risk_data("low"),
        _news_data("positive"),
    )
    assert result["success"] is True
    assert result["asset"] == "bitcoin"
    assert result["asset_type"] == "crypto"
    assert result["recommendation_score"] == 100
    assert result["recommendation"] == "buy"
    assert result["confidence"] == "high"


# ==========================================
# Orchestrator Unit Tests
# ==========================================

# ---- Shared mock builders -----------------------------------------------

def _make_stock_market_data(direction="bullish"):
    """Minimal valid StockAgent output."""
    return {
        "success": True,
        "agent": "StockAgent",
        "symbol": "AAPL",
        "price": 184.5,
        "change": 2.5,
        "change_percent": 1.37,
        "market_direction": direction,
    }

def _make_crypto_market_data(direction="bullish"):
    """Minimal valid CryptoAgent output."""
    return {
        "success": True,
        "agent": "CryptoAgent",
        "coin_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "price": 65000.0,
        "change_percent_24h": 3.5,
        "market_direction": direction,
    }

def _make_news_data(sentiment="positive"):
    """Minimal valid NewsAgent output."""
    return {
        "success": True,
        "agent": "NewsAgent",
        "query": "finance",
        "total_results": 3,
        "overall_sentiment": sentiment,
        "articles": [],
    }

def _make_risk_data(level="low"):
    """Minimal valid RiskAgent output."""
    return {
        "success": True,
        "agent": "RiskAgent",
        "asset": "AAPL",
        "asset_type": "stock",
        "risk_score": 30,
        "risk_level": level,
    }

def _make_recommendation(score=100, rec="buy", confidence="high"):
    """Minimal valid PortfolioAgent output."""
    return {
        "success": True,
        "agent": "PortfolioAgent",
        "asset": "AAPL",
        "asset_type": "stock",
        "recommendation_score": score,
        "recommendation": rec,
        "confidence": confidence,
        "market_direction": "bullish",
        "risk_level": "low",
        "news_sentiment": "positive",
        "factors": ["Market direction is bullish.", "Risk level is low.", "Financial news sentiment is positive."],
        "summary": "Based on bullish market conditions, low risk, and positive financial news sentiment, the system recommends BUY for AAPL with high confidence.",
        "disclaimer": "This is a software-generated educational recommendation, not financial advice.",
    }

def _make_orchestrator(
    market_result=None,
    news_result=None,
    risk_result=None,
    recommendation_result=None,
    asset_type="stock",
):
    """
    Build an Orchestrator whose agents are all replaced with MagicMocks.
    Returns (orchestrator, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio).
    """
    mock_stock     = MagicMock()
    mock_crypto    = MagicMock()
    mock_news      = MagicMock()
    mock_risk      = MagicMock()
    mock_portfolio = MagicMock()

    if market_result is not None:
        if asset_type == "stock":
            mock_stock.analyze_stock.return_value = market_result
        else:
            mock_crypto.analyze_crypto.return_value = market_result

    if news_result is not None:
        mock_news.analyze_news.return_value = news_result

    if risk_result is not None:
        mock_risk.analyze_risk.return_value = risk_result

    if recommendation_result is not None:
        mock_portfolio.generate_recommendation.return_value = recommendation_result

    orch = Orchestrator(
        stock_agent=mock_stock,
        crypto_agent=mock_crypto,
        news_agent=mock_news,
        risk_agent=mock_risk,
        portfolio_agent=mock_portfolio,
    )
    return orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio


# ---- Tests ---------------------------------------------------------------

def test_orchestrator_invalid_asset_type():
    """Non-string or empty asset_type returns a validation error."""
    orch, *_ = _make_orchestrator()
    for bad in ["", "   ", 42, None]:
        result = orch.run(bad, "AAPL")
        assert result["success"] is False
        assert result["agent"] == "Orchestrator"
        assert "asset_type" in result["error"].lower() or "Unsupported" in result["error"]


def test_orchestrator_unsupported_asset_type():
    """An unrecognised asset_type string returns an error naming the bad value."""
    orch, *_ = _make_orchestrator()
    result = orch.run("futures", "AAPL")
    assert result["success"] is False
    assert result["agent"] == "Orchestrator"
    assert "futures" in result["error"]


def test_orchestrator_invalid_asset():
    """Empty or whitespace-only asset string returns a validation error."""
    orch, *_ = _make_orchestrator()
    for bad in ["", "   ", None, 123]:
        result = orch.run("stock", bad)
        assert result["success"] is False
        assert result["agent"] == "Orchestrator"
        assert "asset" in result["error"].lower()


def test_orchestrator_failed_market_agent():
    """A failed StockAgent result is surfaced with step='market_agent'."""
    failed_market = {"success": False, "agent": "StockAgent", "symbol": "AAPL", "error": "API key missing"}
    orch, *_ = _make_orchestrator(market_result=failed_market, asset_type="stock")
    result = orch.run("stock", "AAPL")
    assert result["success"] is False
    assert result["agent"] == "Orchestrator"
    assert result.get("step") == "market_agent"
    assert "API key missing" in result["error"]


def test_orchestrator_failed_news_agent():
    """
    A failed NewsAgent is logged as failed in agent_activity.
    Pipeline continues to RiskAgent (market data is sufficient for risk analysis).
    PortfolioAgent is SKIPPED — news context is unavailable and fabricating sentiment
    is not acceptable for a financial intelligence application.
    Overall result is still success=True (market + risk data are valid partial outputs).
    """
    failed_news = {"success": False, "agent": "NewsAgent", "query": "AAPL", "error": "News API unavailable"}
    orch, _, _, _, mock_risk, mock_portfolio = _make_orchestrator(
        market_result=_make_stock_market_data(),
        news_result=failed_news,
        risk_result=_make_risk_data(),
        recommendation_result=_make_recommendation(),
        asset_type="stock",
    )
    result = orch.run("stock", "AAPL")
    assert result["success"] is True
    assert "market_data" in result
    assert "risk_data" in result
    # PortfolioAgent must NOT have been called — no fabricated news to score
    mock_portfolio.generate_recommendation.assert_not_called()
    # news_data should reflect the real failure — not a synthetic success
    assert result["news_data"]["success"] is False
    # Activity: StockAgent success, NewsAgent failed, RiskAgent success; NO PortfolioAgent
    activity = result["agent_activity"]
    assert activity[1]["agent"] == "NewsAgent"
    assert activity[1]["status"] == "failed"
    assert "fabricating news sentiment is not acceptable" in activity[1]["decision"]
    assert activity[2]["agent"] == "RiskAgent"
    assert activity[2]["status"] == "success"
    assert all(a["agent"] != "PortfolioAgent" for a in activity)


def test_orchestrator_failed_risk_agent():
    """A failed RiskAgent result is surfaced with step='risk_agent'."""
    failed_risk = {"success": False, "agent": "RiskAgent", "error": "Missing percentage field"}
    orch, *_ = _make_orchestrator(
        market_result=_make_stock_market_data(),
        news_result=_make_news_data(),
        risk_result=failed_risk,
        asset_type="stock",
    )
    result = orch.run("stock", "AAPL")
    assert result["success"] is False
    assert result.get("step") == "risk_agent"
    assert "Missing percentage field" in result["error"]


def test_orchestrator_failed_portfolio_agent():
    """A failed PortfolioAgent result is surfaced with step='portfolio_agent'."""
    failed_rec = {"success": False, "agent": "PortfolioAgent", "error": "Unsupported market agent"}
    orch, *_ = _make_orchestrator(
        market_result=_make_stock_market_data(),
        news_result=_make_news_data(),
        risk_result=_make_risk_data(),
        recommendation_result=failed_rec,
        asset_type="stock",
    )
    result = orch.run("stock", "AAPL")
    assert result["success"] is False
    assert result.get("step") == "portfolio_agent"


def test_orchestrator_successful_stock_workflow():
    """
    Full happy-path for a stock: verify all four agent calls are made in order
    and the final response contains all expected top-level keys.
    """
    market = _make_stock_market_data("bullish")
    news   = _make_news_data("positive")
    risk   = _make_risk_data("low")
    rec    = _make_recommendation(100, "buy", "high")

    orch, mock_stock, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator(
        market_result=market,
        news_result=news,
        risk_result=risk,
        recommendation_result=rec,
        asset_type="stock",
    )

    result = orch.run("stock", "AAPL")

    assert result["success"] is True
    assert result["agent"] == "Orchestrator"
    assert result["asset"] == "AAPL"
    assert result["asset_type"] == "stock"
    assert "market_data" in result
    assert "news_data" in result
    assert "risk_data" in result
    assert "recommendation" in result
    assert result["recommendation"]["recommendation"] == "buy"
    assert result["recommendation"]["confidence"] == "high"
    assert "summary" in result
    assert "disclaimer" in result

    # Verify each agent was called exactly once with the correct argument
    mock_stock.analyze_stock.assert_called_once_with("AAPL")
    mock_news.analyze_news.assert_called_once_with(query="finance")
    mock_risk.analyze_risk.assert_called_once_with(market)
    mock_portfolio.generate_recommendation.assert_called_once_with(
        market_data=market, risk_data=risk, news_data=news
    )


def test_orchestrator_successful_crypto_workflow():
    """
    Full happy-path for a crypto asset: CryptoAgent is used (not StockAgent).
    """
    market = _make_crypto_market_data("bullish")
    news   = _make_news_data("positive")
    risk   = {
        "success": True, "agent": "RiskAgent",
        "asset": "bitcoin", "asset_type": "crypto",
        "risk_score": 75, "risk_level": "high",
    }
    rec = {
        "success": True, "agent": "PortfolioAgent",
        "asset": "bitcoin", "asset_type": "crypto",
        "recommendation_score": 65, "recommendation": "hold",
        "confidence": "medium", "market_direction": "bullish",
        "risk_level": "high", "news_sentiment": "positive",
        "factors": [], "summary": "hold bitcoin", "disclaimer": "Not advice.",
    }

    orch, _, mock_crypto, mock_news, mock_risk, _ = _make_orchestrator(
        market_result=market,
        news_result=news,
        risk_result=risk,
        recommendation_result=rec,
        asset_type="crypto",
    )

    result = orch.run("crypto", "bitcoin")

    assert result["success"] is True
    assert result["asset"] == "bitcoin"
    assert result["asset_type"] == "crypto"
    assert result["recommendation"]["recommendation"] == "hold"
    mock_crypto.analyze_crypto.assert_called_once_with("bitcoin")
    mock_news.analyze_news.assert_called_once_with(query="finance")


def test_orchestrator_asset_type_case_insensitive():
    """'STOCK' and '  Crypto  ' should both be accepted and normalised."""
    market_s = _make_stock_market_data()
    market_c = _make_crypto_market_data()
    news     = _make_news_data()
    risk     = _make_risk_data()
    rec      = _make_recommendation()

    # Test uppercase STOCK
    orch_s, mock_stock, _, _, _, _ = _make_orchestrator(
        market_result=market_s, news_result=news,
        risk_result=risk, recommendation_result=rec, asset_type="stock",
    )
    result_s = orch_s.run("STOCK", "AAPL")
    assert result_s["success"] is True
    assert result_s["asset_type"] == "stock"

    # Test mixed-case + spaces CRYPTO
    orch_c, _, mock_crypto, _, _, _ = _make_orchestrator(
        market_result=market_c, news_result=news,
        risk_result=risk, recommendation_result=rec, asset_type="crypto",
    )
    result_c = orch_c.run("  Crypto  ", "bitcoin")
    assert result_c["success"] is True
    assert result_c["asset_type"] == "crypto"


def test_orchestrator_custom_news_query():
    """A custom news_query is forwarded to NewsAgent correctly."""
    market = _make_stock_market_data()
    news   = _make_news_data()
    risk   = _make_risk_data()
    rec    = _make_recommendation()

    orch, _, _, mock_news, _, _ = _make_orchestrator(
        market_result=market, news_result=news,
        risk_result=risk, recommendation_result=rec, asset_type="stock",
    )

    orch.run("stock", "AAPL", news_query="Apple earnings")
    mock_news.analyze_news.assert_called_once_with(query="Apple earnings")


def test_orchestrator_dependency_injection():
    """Verify that injected mock agents are stored and used by the orchestrator."""
    mock_stock     = MagicMock()
    mock_crypto    = MagicMock()
    mock_news      = MagicMock()
    mock_risk      = MagicMock()
    mock_portfolio = MagicMock()

    orch = Orchestrator(
        stock_agent=mock_stock,
        crypto_agent=mock_crypto,
        news_agent=mock_news,
        risk_agent=mock_risk,
        portfolio_agent=mock_portfolio,
    )

    assert orch.stock_agent     is mock_stock
    assert orch.crypto_agent    is mock_crypto
    assert orch.news_agent      is mock_news
    assert orch.risk_agent      is mock_risk
    assert orch.portfolio_agent is mock_portfolio


def test_orchestrator_market_agent_exception_handled():
    """An exception raised inside StockAgent is caught and returned as an error."""
    mock_stock = MagicMock()
    mock_stock.analyze_stock.side_effect = RuntimeError("Unexpected crash")

    orch = Orchestrator(stock_agent=mock_stock)
    result = orch.run("stock", "AAPL")

    assert result["success"] is False
    assert result["agent"] == "Orchestrator"
    assert "Unexpected crash" in result["error"]


# ==========================================
# Orchestrator.run_intent() — Day 20 Dynamic Routing Tests
# ==========================================

def _make_orchestrator_for_intent(
    stock_result=None,
    crypto_result=None,
    news_result=None,
    risk_result=None,
    portfolio_result=None,
):
    """
    Build an Orchestrator with all agents mocked.
    Returns (orchestrator, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio).
    """
    mock_stock     = MagicMock()
    mock_crypto    = MagicMock()
    mock_news      = MagicMock()
    mock_risk      = MagicMock()
    mock_portfolio = MagicMock()

    if stock_result is not None:
        mock_stock.analyze_stock.return_value = stock_result
    if crypto_result is not None:
        mock_crypto.analyze_crypto.return_value = crypto_result
    if news_result is not None:
        mock_news.analyze_news.return_value = news_result
    if risk_result is not None:
        mock_risk.analyze_risk.return_value = risk_result
    if portfolio_result is not None:
        mock_portfolio.generate_recommendation.return_value = portfolio_result

    orch = Orchestrator(
        stock_agent=mock_stock,
        crypto_agent=mock_crypto,
        news_agent=mock_news,
        risk_agent=mock_risk,
        portfolio_agent=mock_portfolio,
    )
    return orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio


def test_run_intent_stock_analysis_all_four_agents_called():
    """
    STOCK_ANALYSIS intent must call StockAgent, NewsAgent, RiskAgent, PortfolioAgent.
    agents_used and agent_activity must contain exactly those four agents in order with status 'success'.
    """
    orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data("bullish"),
        news_result=_make_news_data("positive"),
        risk_result=_make_risk_data("low"),
        portfolio_result=_make_recommendation(100, "buy", "high"),
    )

    interpreted = {
        "success": True,
        "intent": "STOCK_ANALYSIS",
        "asset_type": "stock",
        "asset": "AAPL",
        "news_query": "Apple",
    }

    result = orch.run_intent(interpreted)

    assert result["success"] is True
    assert result["intent"] == "STOCK_ANALYSIS"
    assert result["agents_used"] == ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]
    
    activity = result["agent_activity"]
    assert len(activity) == 4
    assert [a["agent"] for a in activity] == ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]
    assert [a["order"] for a in activity] == [1, 2, 3, 4]
    assert all(a["status"] == "success" for a in activity)
    assert "AAPL market analysis completed" in activity[0]["summary"]

    assert "market_data" in result
    assert "news_data" in result
    assert "risk_data" in result
    assert "recommendation" in result
    assert result["asset"] == "AAPL"
    assert result["asset_type"] == "stock"

    mock_stock.analyze_stock.assert_called_once_with("AAPL")
    mock_news.analyze_news.assert_called_once_with(query="Apple")
    mock_risk.analyze_risk.assert_called_once()
    mock_portfolio.generate_recommendation.assert_called_once()
    mock_crypto.analyze_crypto.assert_not_called()


def test_run_intent_crypto_analysis_all_four_agents_called():
    """
    CRYPTO_ANALYSIS intent must call CryptoAgent, NewsAgent, RiskAgent, PortfolioAgent.
    StockAgent must NOT be called. agent_activity must record all 4 in order.
    """
    crypto_risk = {
        "success": True, "agent": "RiskAgent",
        "asset": "bitcoin", "asset_type": "crypto",
        "risk_score": 75, "risk_level": "high",
    }
    crypto_rec = {
        "success": True, "agent": "PortfolioAgent",
        "asset": "bitcoin", "asset_type": "crypto",
        "recommendation_score": 65, "recommendation": "hold",
        "confidence": "medium", "market_direction": "bullish",
        "risk_level": "high", "news_sentiment": "positive",
        "factors": [], "summary": "hold bitcoin", "disclaimer": "Not advice.",
    }

    orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        crypto_result=_make_crypto_market_data("bullish"),
        news_result=_make_news_data("positive"),
        risk_result=crypto_risk,
        portfolio_result=crypto_rec,
    )

    interpreted = {
        "success": True,
        "intent": "CRYPTO_ANALYSIS",
        "asset_type": "crypto",
        "asset": "bitcoin",
        "news_query": "Bitcoin",
    }

    result = orch.run_intent(interpreted)

    assert result["success"] is True
    assert result["intent"] == "CRYPTO_ANALYSIS"
    assert result["agents_used"] == ["CryptoAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]

    activity = result["agent_activity"]
    assert len(activity) == 4
    assert [a["agent"] for a in activity] == ["CryptoAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]
    assert [a["order"] for a in activity] == [1, 2, 3, 4]
    assert all(a["status"] == "success" for a in activity)
    assert "bitcoin market analysis completed" in activity[0]["summary"]

    assert result["asset"] == "bitcoin"
    assert result["asset_type"] == "crypto"

    mock_crypto.analyze_crypto.assert_called_once_with("bitcoin")
    mock_news.analyze_news.assert_called_once_with(query="Bitcoin")
    mock_risk.analyze_risk.assert_called_once()
    mock_portfolio.generate_recommendation.assert_called_once()
    mock_stock.analyze_stock.assert_not_called()


def test_run_intent_general_financial_news_only_news_agent_called():
    """
    GENERAL_FINANCIAL_NEWS must call NewsAgent ONLY.
    StockAgent, CryptoAgent, RiskAgent, PortfolioAgent must NOT be called.
    agent_activity must contain only NewsAgent.
    """
    orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        news_result={
            "success": True,
            "agent": "NewsAgent",
            "query": "finance",
            "total_results": 5,
            "overall_sentiment": "neutral",
            "summary": "Mixed signals in the market today.",
            "articles": [],
        }
    )

    interpreted = {
        "success": True,
        "intent": "GENERAL_FINANCIAL_NEWS",
        "asset_type": None,
        "asset": None,
        "news_query": "finance",
    }

    result = orch.run_intent(interpreted)

    assert result["success"] is True
    assert result["intent"] == "GENERAL_FINANCIAL_NEWS"
    assert result["agents_used"] == ["NewsAgent"]
    
    activity = result["agent_activity"]
    assert len(activity) == 1
    assert activity[0]["agent"] == "NewsAgent"
    assert activity[0]["order"] == 1
    assert activity[0]["status"] == "success"

    assert "news_data" in result
    assert "disclaimer" in result

    mock_news.analyze_news.assert_called_once_with(query="finance")
    mock_stock.analyze_stock.assert_not_called()
    mock_crypto.analyze_crypto.assert_not_called()
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_run_intent_unsupported_returns_clean_error_no_agents_called():
    """
    UNSUPPORTED intent must return a clean structured error.
    No financial agents must be called. agents_used and agent_activity must be empty lists.
    """
    orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent()

    interpreted = {
        "success": False,
        "intent": "UNSUPPORTED",
        "error": "Unable to identify a supported asset.",
    }

    result = orch.run_intent(interpreted)

    assert result["success"] is False
    assert result["intent"] == "UNSUPPORTED"
    assert result["agents_used"] == []
    assert result["agent_activity"] == []
    assert "error" in result

    mock_stock.analyze_stock.assert_not_called()
    mock_crypto.analyze_crypto.assert_not_called()
    mock_news.analyze_news.assert_not_called()
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_run_intent_unknown_intent_no_agents_called():
    """An unknown intent string must return a clean error; no agents called, agent_activity empty."""
    orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent()

    result = orch.run_intent({"intent": "FUTURES_TRADING", "success": True})

    assert result["success"] is False
    assert result["agents_used"] == []
    assert result["agent_activity"] == []
    assert "error" in result
    mock_stock.analyze_stock.assert_not_called()
    mock_crypto.analyze_crypto.assert_not_called()
    mock_news.analyze_news.assert_not_called()
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_run_intent_invalid_non_dict_input():
    """Passing a non-dict to run_intent returns a clean error with agents_used=[] and agent_activity=[]."""
    orch, *_ = _make_orchestrator_for_intent()
    for bad in [None, "string", 42, ["list"]]:
        result = orch.run_intent(bad)
        assert result["success"] is False
        assert result["agents_used"] == []
        assert result["agent_activity"] == []
        assert "error" in result


def test_run_intent_stock_response_has_all_standard_keys():
    """Full STOCK_ANALYSIS response includes all keys expected downstream by routes.py."""
    orch, *_ = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data("bullish"),
        news_result=_make_news_data("positive"),
        risk_result=_make_risk_data("low"),
        portfolio_result=_make_recommendation(100, "buy", "high"),
    )
    interpreted = {
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    }

    result = orch.run_intent(interpreted)

    for key in ("success", "agent", "intent", "agents_used", "agent_activity", "asset", "asset_type",
                "market_data", "news_data", "risk_data", "recommendation", "summary", "disclaimer"):
        assert key in result, f"Missing key in run_intent stock response: {key}"
    assert result["recommendation"]["recommendation"] == "buy"


def test_run_intent_general_news_failed_news_agent():
    """A failing NewsAgent for GENERAL_FINANCIAL_NEWS propagates error; agents_used=['NewsAgent'], agent_activity recorded as failed."""
    orch, _, _, mock_news, *_ = _make_orchestrator_for_intent(
        news_result={"success": False, "agent": "NewsAgent", "error": "API key missing"}
    )
    interpreted = {
        "success": True, "intent": "GENERAL_FINANCIAL_NEWS",
        "asset_type": None, "asset": None, "news_query": "finance",
    }

    result = orch.run_intent(interpreted)

    assert result["success"] is False
    assert result["agents_used"] == ["NewsAgent"]
    activity = result["agent_activity"]
    assert len(activity) == 1
    assert activity[0]["agent"] == "NewsAgent"
    assert activity[0]["status"] == "failed"
    assert activity[0]["order"] == 1
    assert "API key missing" in activity[0]["summary"]
    assert "API key missing" in result["error"]
    mock_news.analyze_news.assert_called_once_with(query="finance")


def test_run_intent_stock_failed_market_agent_stops_pipeline():
    """
    StockAgent failure in STOCK_ANALYSIS: agents_used=[StockAgent], agent_activity records StockAgent failed.
    NewsAgent, RiskAgent, PortfolioAgent are NOT called.
    """
    orch, mock_stock, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result={"success": False, "agent": "StockAgent", "error": "API rate limit exceeded"}
    )
    interpreted = {
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    }

    result = orch.run_intent(interpreted)

    assert result["success"] is False
    assert result["agents_used"] == ["StockAgent"]
    activity = result["agent_activity"]
    assert len(activity) == 1
    assert activity[0]["agent"] == "StockAgent"
    assert activity[0]["status"] == "failed"
    assert activity[0]["order"] == 1
    assert "API rate limit" in activity[0]["summary"]
    assert result["step"] == "market_agent"
    assert "API rate limit exceeded" in result["error"]
    mock_news.analyze_news.assert_not_called()
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_run_intent_stock_news_failure_continuation_behavior():
    """
    NewsAgent failure in STOCK_ANALYSIS:
    - StockAgent runs and succeeds.
    - NewsAgent runs and fails; its raw failure dict is preserved (no synthetic success injected).
    - RiskAgent runs — market data is sufficient for risk analysis.
    - PortfolioAgent is SKIPPED — news context unavailable; fabricating sentiment is not acceptable.
    - Overall success=True (market + risk data are valid partial outputs).
    """
    orch, _, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data("bullish"),
        news_result={"success": False, "agent": "NewsAgent", "error": "No articles found"},
        risk_result=_make_risk_data("low"),
        portfolio_result=_make_recommendation(100, "buy"),
    )
    interpreted = {
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    }

    result = orch.run_intent(interpreted)

    assert result["success"] is True
    # PortfolioAgent must NOT appear in agents_used
    assert result["agents_used"] == ["StockAgent", "NewsAgent", "RiskAgent"]
    activity = result["agent_activity"]
    assert len(activity) == 3
    assert activity[0]["status"] == "success"
    assert activity[1]["agent"] == "NewsAgent"
    assert activity[1]["status"] == "failed"
    assert "fabricating news sentiment is not acceptable" in activity[1]["decision"]
    assert activity[2]["agent"] == "RiskAgent"
    assert activity[2]["status"] == "success"
    # news_data must be the real failure dict — not a synthetic success
    assert result["news_data"]["success"] is False
    # RiskAgent called (market data available); PortfolioAgent NOT called (no real news)
    mock_risk.analyze_risk.assert_called_once()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_run_intent_intent_constants_match_query_interpreter():
    """
    Orchestrator intent constants must exactly match QueryInterpreter intent values.
    This test guards the routing contract so any future mismatch fails loudly.
    """
    from services.query_interpreter import QueryInterpreter

    assert Orchestrator.INTENT_STOCK       == QueryInterpreter.INTENT_STOCK
    assert Orchestrator.INTENT_CRYPTO      == QueryInterpreter.INTENT_CRYPTO
    assert Orchestrator.INTENT_NEWS        == QueryInterpreter.INTENT_NEWS
    assert Orchestrator.INTENT_UNSUPPORTED == QueryInterpreter.INTENT_UNSUPPORTED


# ==========================================
# Day 28: Agentic Orchestration Decision Tests
# ==========================================

def test_day28_decision_helpers():
    """Test deterministic decision functions on Orchestrator."""
    orch = Orchestrator()

    # should_fetch_news
    assert orch.should_fetch_news("STOCK_ANALYSIS", "Apple") is True
    assert orch.should_fetch_news("CRYPTO_ANALYSIS", "Bitcoin") is True
    assert orch.should_fetch_news("GENERAL_FINANCIAL_NEWS", "finance") is True
    assert orch.should_fetch_news("UNSUPPORTED", "anything") is False
    assert orch.should_fetch_news("STOCK_ANALYSIS", "") is False

    # should_analyze_risk
    assert orch.should_analyze_risk("STOCK_ANALYSIS", {"success": True}) is True
    assert orch.should_analyze_risk("CRYPTO_ANALYSIS", {"success": True}) is True
    assert orch.should_analyze_risk("STOCK_ANALYSIS", {"success": False}) is False
    assert orch.should_analyze_risk("GENERAL_FINANCIAL_NEWS", {"success": True}) is False

    # should_generate_portfolio_recommendation — now requires successful news_data too
    assert orch.should_generate_portfolio_recommendation("STOCK_ANALYSIS", {"success": True}, {"success": True}, {"success": True}) is True
    assert orch.should_generate_portfolio_recommendation("STOCK_ANALYSIS", {"success": True}, {"success": True}, {"success": False}) is False
    assert orch.should_generate_portfolio_recommendation("STOCK_ANALYSIS", {"success": True}, {"success": True}, None) is False
    assert orch.should_generate_portfolio_recommendation("STOCK_ANALYSIS", {"success": True}, {"success": False}, {"success": True}) is False
    assert orch.should_generate_portfolio_recommendation("STOCK_ANALYSIS", {"success": False}, {"success": True}, {"success": True}) is False
    assert orch.should_generate_portfolio_recommendation("GENERAL_FINANCIAL_NEWS", {"success": True}, {"success": True}, {"success": True}) is False


def test_day28_market_failure_halts_pipeline():
    """When StockAgent fails, RiskAgent and PortfolioAgent are NOT called."""
    orch, mock_stock, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result={"success": False, "agent": "StockAgent", "error": "Symbol not found"}
    )
    res = orch.run_intent({"success": True, "intent": "STOCK_ANALYSIS", "asset_type": "stock", "asset": "INVALID"})

    assert res["success"] is False
    assert res["agents_used"] == ["StockAgent"]
    assert len(res["agent_activity"]) == 1
    assert res["agent_activity"][0]["status"] == "failed"
    assert "halting" in res["agent_activity"][0]["decision"]
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_day28_risk_failure_halts_portfolio():
    """When RiskAgent fails, PortfolioAgent is NOT called."""
    orch, _, _, _, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data(),
        news_result=_make_news_data(),
        risk_result={"success": False, "agent": "RiskAgent", "error": "Invalid metrics"},
    )
    res = orch.run_intent({"success": True, "intent": "STOCK_ANALYSIS", "asset_type": "stock", "asset": "AAPL", "news_query": "Apple"})

    assert res["success"] is False
    assert res["agents_used"] == ["StockAgent", "NewsAgent", "RiskAgent"]
    assert len(res["agent_activity"]) == 3
    assert res["agent_activity"][2]["status"] == "failed"
    mock_portfolio.generate_recommendation.assert_not_called()


def test_day28_unsupported_query_executes_zero_agents():
    """UNSUPPORTED query executes zero agents."""
    orch, mock_stock, mock_crypto, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent()
    res = orch.run_intent({"success": False, "intent": "UNSUPPORTED", "error": "Unknown asset"})

    assert res["success"] is False
    assert res["agents_used"] == []
    assert res["agent_activity"] == []
    mock_stock.analyze_stock.assert_not_called()
    mock_crypto.analyze_crypto.assert_not_called()
    mock_news.analyze_news.assert_not_called()
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


# ==========================================
# Day 28 Review: Honest NewsAgent Failure Tests
# ==========================================

def test_day28_news_exception_no_synthetic_data():
    """
    When NewsAgent raises an exception (not just a failure return):
    - news_data in result must NOT be a synthetic success dict.
    - news_data.success must be False.
    - PortfolioAgent must NOT be called.
    - RiskAgent MUST still be called (market data is sufficient for risk).
    - activity for NewsAgent must be 'failed' with no fake sentiment.
    """
    orch, _, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data("bullish"),
        risk_result=_make_risk_data("low"),
        portfolio_result=_make_recommendation(100, "buy"),
    )
    mock_news.analyze_news.side_effect = RuntimeError("Network timeout")

    interpreted = {
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    }
    result = orch.run_intent(interpreted)

    assert result["success"] is True
    # news_data must be a real failure record — not a synthetic {"success": True, "overall_sentiment": "neutral"}
    assert isinstance(result["news_data"], dict)
    assert result["news_data"]["success"] is False
    assert "news_data" in result
    assert result["news_data"].get("overall_sentiment") is None, (
        "Orchestrator must NOT invent news sentiment when NewsAgent raises an exception"
    )
    # PortfolioAgent NOT called — no fabricated news to score
    mock_portfolio.generate_recommendation.assert_not_called()
    # RiskAgent called — market data is valid
    mock_risk.analyze_risk.assert_called_once()
    # agents_used: StockAgent, NewsAgent, RiskAgent — no PortfolioAgent
    assert result["agents_used"] == ["StockAgent", "NewsAgent", "RiskAgent"]
    # NewsAgent activity entry must reflect failure
    activity = result["agent_activity"]
    news_act = next((a for a in activity if a["agent"] == "NewsAgent"), None)
    assert news_act is not None
    assert news_act["status"] == "failed"
    assert "fabricating news sentiment is not acceptable" in news_act["decision"]


def test_day28_crypto_news_failure_portfolio_skipped():
    """
    Same honest behaviour for CRYPTO_ANALYSIS: when news fails,
    RiskAgent runs, PortfolioAgent is skipped, news_data is the real failure dict.
    """
    orch, _, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        crypto_result=_make_crypto_market_data("bullish"),
        news_result={"success": False, "agent": "NewsAgent", "error": "Rate limit exceeded"},
        risk_result=_make_risk_data("medium"),
        portfolio_result=_make_recommendation(65, "hold"),
    )
    interpreted = {
        "success": True, "intent": "CRYPTO_ANALYSIS",
        "asset_type": "crypto", "asset": "bitcoin", "news_query": "bitcoin",
    }
    result = orch.run_intent(interpreted)

    assert result["success"] is True
    assert result["agents_used"] == ["CryptoAgent", "NewsAgent", "RiskAgent"]
    assert result["news_data"]["success"] is False
    mock_risk.analyze_risk.assert_called_once()
    mock_portfolio.generate_recommendation.assert_not_called()
    activity = result["agent_activity"]
    news_act = next((a for a in activity if a["agent"] == "NewsAgent"), None)
    assert news_act["status"] == "failed"
    assert all(a["agent"] != "PortfolioAgent" for a in activity)


# ==========================================
# Day 29: Shared AnalysisContext Tests
# ==========================================

# ---- AnalysisContext unit tests (isolated) --------------------------------

def test_day29_analysis_context_initial_state():
    """A freshly created AnalysisContext has safe, empty defaults."""
    ctx = AnalysisContext()
    assert ctx.intent == ""
    assert ctx.asset_type == ""
    assert ctx.asset == ""
    assert ctx.original_query == ""
    assert ctx.news_query == ""
    assert ctx.market_data is None
    assert ctx.news_data is None
    assert ctx.risk_data is None
    assert ctx.portfolio_data is None
    assert ctx.agents_used == []
    assert ctx.agent_activity == []
    assert ctx.decisions == []


def test_day29_context_market_succeeded_helper():
    """market_succeeded() returns True only when market_data.success is True."""
    ctx = AnalysisContext()
    assert ctx.market_succeeded() is False           # None → False

    ctx.market_data = {"success": False, "agent": "StockAgent", "error": "x"}
    assert ctx.market_succeeded() is False           # explicit failure → False

    ctx.market_data = {"success": True, "agent": "StockAgent"}
    assert ctx.market_succeeded() is True            # real success → True


def test_day29_context_news_succeeded_helper():
    """news_succeeded() returns True only when news_data.success is True."""
    ctx = AnalysisContext()
    assert ctx.news_succeeded() is False

    ctx.news_data = {"success": False, "agent": "NewsAgent", "error": "timeout"}
    assert ctx.news_succeeded() is False

    ctx.news_data = {"success": True, "agent": "NewsAgent", "overall_sentiment": "positive"}
    assert ctx.news_succeeded() is True


def test_day29_context_risk_succeeded_helper():
    """risk_succeeded() returns True only when risk_data.success is True."""
    ctx = AnalysisContext()
    assert ctx.risk_succeeded() is False

    ctx.risk_data = {"success": False, "agent": "RiskAgent", "error": "bad input"}
    assert ctx.risk_succeeded() is False

    ctx.risk_data = {"success": True, "agent": "RiskAgent", "risk_level": "low"}
    assert ctx.risk_succeeded() is True


def test_day29_context_record_activity():
    """record_activity() appends correctly ordered entries with all required keys."""
    ctx = AnalysisContext()
    ctx.record_activity(
        agent="StockAgent",
        status="success",
        summary="AAPL market analysis completed",
        decision="Market data verified.",
        duration_ms=120,
    )
    ctx.record_activity(
        agent="NewsAgent",
        status="failed",
        summary="NewsAgent failed: timeout",
        decision="NewsAgent failed; PortfolioAgent will be skipped.",
    )
    assert len(ctx.agent_activity) == 2
    first = ctx.agent_activity[0]
    assert first["agent"] == "StockAgent"
    assert first["status"] == "success"
    assert first["order"] == 1
    assert first["duration_ms"] == 120

    second = ctx.agent_activity[1]
    assert second["agent"] == "NewsAgent"
    assert second["status"] == "failed"
    assert second["order"] == 2
    assert "duration_ms" not in second   # omitted when not provided


def test_day29_context_log_decision():
    """log_decision() accumulates rationale strings in decisions list."""
    ctx = AnalysisContext()
    ctx.log_decision("Step A: market verified.")
    ctx.log_decision("Step B: news failed; portfolio skipped.")
    assert len(ctx.decisions) == 2
    assert ctx.decisions[0] == "Step A: market verified."
    assert ctx.decisions[1] == "Step B: news failed; portfolio skipped."


# ---- Pipeline integration tests (via Orchestrator with mocks) -----------

def test_day29_stock_context_flows_through_all_agents():
    """
    Full STOCK_ANALYSIS pipeline:
    - All four agents succeed.
    - agents_used lists all four in order.
    - agent_activity has 4 entries, all 'success'.
    - Final response contains market_data, news_data, risk_data, recommendation.
    - duration_ms present on every activity entry (orchestrator adds it).
    """
    orch, _, _, _, _, _ = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data("bullish"),
        news_result=_make_news_data("positive"),
        risk_result=_make_risk_data("low"),
        portfolio_result=_make_recommendation(85, "buy"),
    )
    result = orch.run_intent({
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    })

    assert result["success"] is True
    assert result["agents_used"] == ["StockAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]
    activity = result["agent_activity"]
    assert len(activity) == 4
    assert all(a["status"] == "success" for a in activity)
    assert all("duration_ms" in a for a in activity)   # Day 29: duration tracked
    assert result["market_data"]["success"] is True
    assert result["news_data"]["success"] is True
    assert result["risk_data"]["success"] is True
    assert result["recommendation"]["success"] is True
    assert result["recommendation"]["recommendation"] == "buy"


def test_day29_crypto_context_flows_through_all_agents():
    """
    Full CRYPTO_ANALYSIS pipeline:
    - CryptoAgent is first; all four agents succeed.
    - Context updated correctly with crypto market data.
    """
    orch, _, _, _, _, _ = _make_orchestrator_for_intent(
        crypto_result=_make_crypto_market_data("bullish"),
        news_result=_make_news_data("positive"),
        risk_result=_make_risk_data("medium"),
        portfolio_result=_make_recommendation(65, "hold"),
    )
    result = orch.run_intent({
        "success": True, "intent": "CRYPTO_ANALYSIS",
        "asset_type": "crypto", "asset": "bitcoin", "news_query": "bitcoin",
    })

    assert result["success"] is True
    assert result["agents_used"] == ["CryptoAgent", "NewsAgent", "RiskAgent", "PortfolioAgent"]
    activity = result["agent_activity"]
    assert len(activity) == 4
    assert activity[0]["agent"] == "CryptoAgent"
    assert activity[0]["status"] == "success"
    assert result["market_data"]["agent"] == "CryptoAgent"
    assert result["recommendation"]["recommendation"] == "hold"


def test_day29_news_only_context():
    """
    GENERAL_FINANCIAL_NEWS: only NewsAgent runs.
    - agents_used = ['NewsAgent']
    - agent_activity has 1 entry
    - result carries news_data
    """
    orch, _, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        news_result=_make_news_data("neutral"),
    )
    result = orch.run_intent({
        "success": True, "intent": "GENERAL_FINANCIAL_NEWS",
        "news_query": "cryptocurrency",
    })

    assert result["success"] is True
    assert result["agents_used"] == ["NewsAgent"]
    assert len(result["agent_activity"]) == 1
    assert result["agent_activity"][0]["agent"] == "NewsAgent"
    assert result["agent_activity"][0]["status"] == "success"
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_day29_market_failure_stops_downstream():
    """
    When the market agent fails:
    - Context stores the failure in market_data.
    - Pipeline halts; NewsAgent, RiskAgent, PortfolioAgent are NOT called.
    - agents_used = ['StockAgent'] only.
    """
    orch, _, _, mock_news, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result={"success": False, "agent": "StockAgent", "error": "Invalid symbol"},
    )
    result = orch.run_intent({
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "INVALID", "news_query": "INVALID",
    })

    assert result["success"] is False
    assert result["agents_used"] == ["StockAgent"]
    assert len(result["agent_activity"]) == 1
    assert result["agent_activity"][0]["status"] == "failed"
    assert "halting" in result["agent_activity"][0]["decision"]
    mock_news.analyze_news.assert_not_called()
    mock_risk.analyze_risk.assert_not_called()
    mock_portfolio.generate_recommendation.assert_not_called()


def test_day29_news_failure_no_fabrication():
    """
    When NewsAgent fails:
    - news_data in context is the real failure dict (success=False).
    - No synthetic 'neutral' sentiment is injected.
    - RiskAgent still runs (market data is sufficient).
    - PortfolioAgent is NOT called (no real news).
    - Activity correctly records all three steps.
    """
    orch, _, _, _, mock_risk, mock_portfolio = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data("bullish"),
        news_result={"success": False, "agent": "NewsAgent", "error": "Rate limit"},
        risk_result=_make_risk_data("low"),
        portfolio_result=_make_recommendation(85, "buy"),
    )
    result = orch.run_intent({
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    })

    assert result["success"] is True
    # news_data must be the real failure dict — not a synthetic success
    assert result["news_data"]["success"] is False
    assert result["news_data"].get("overall_sentiment") is None
    # PortfolioAgent NOT called
    mock_portfolio.generate_recommendation.assert_not_called()
    assert "PortfolioAgent" not in result["agents_used"]
    # RiskAgent called
    mock_risk.analyze_risk.assert_called_once()
    # Activity: 3 entries (StockAgent, NewsAgent, RiskAgent)
    activity = result["agent_activity"]
    assert len(activity) == 3
    news_act = next(a for a in activity if a["agent"] == "NewsAgent")
    assert news_act["status"] == "failed"
    assert "fabricating news sentiment is not acceptable" in news_act["decision"]


def test_day29_risk_failure_prevents_portfolio():
    """
    When RiskAgent fails:
    - risk_data stored as failure dict in context.
    - PortfolioAgent is NOT called.
    - Result is success=False with step='risk_agent'.
    """
    orch, _, _, _, _, mock_portfolio = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data("bullish"),
        news_result=_make_news_data("positive"),
        risk_result={"success": False, "agent": "RiskAgent", "error": "Corrupt metrics"},
        portfolio_result=_make_recommendation(85, "buy"),
    )
    result = orch.run_intent({
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    })

    assert result["success"] is False
    assert result.get("step") == "risk_agent"
    assert "Corrupt metrics" in result["error"]
    mock_portfolio.generate_recommendation.assert_not_called()
    assert "PortfolioAgent" not in result["agents_used"]


def test_day29_portfolio_receives_correct_context_data():
    """
    PortfolioAgent.generate_recommendation() must be called with the exact
    market_data, risk_data, and news_data that were stored in the context —
    not copies of local variables from a previous implementation.
    """
    stock_result = _make_stock_market_data("bullish")
    news_result = _make_news_data("positive")
    risk_result = _make_risk_data("low")
    portfolio_result = _make_recommendation(85, "buy")

    orch, _, _, _, _, mock_portfolio = _make_orchestrator_for_intent(
        stock_result=stock_result,
        news_result=news_result,
        risk_result=risk_result,
        portfolio_result=portfolio_result,
    )
    mock_portfolio.generate_recommendation.return_value = portfolio_result

    result = orch.run_intent({
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    })

    assert result["success"] is True
    # Verify PortfolioAgent received the exact data from the context
    call_kwargs = mock_portfolio.generate_recommendation.call_args
    assert call_kwargs.kwargs["market_data"] == stock_result
    assert call_kwargs.kwargs["news_data"] == news_result
    assert call_kwargs.kwargs["risk_data"] == risk_result


def test_day29_agent_activity_order_field_is_sequential():
    """
    agent_activity order field must be sequential (1, 2, 3, 4) regardless
    of which agents ran, ensuring dashboard display is always coherent.
    """
    orch, _, _, _, _, _ = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data(),
        news_result=_make_news_data(),
        risk_result=_make_risk_data(),
        portfolio_result=_make_recommendation(),
    )
    result = orch.run_intent({
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    })

    orders = [a["order"] for a in result["agent_activity"]]
    assert orders == list(range(1, len(orders) + 1))


def test_day29_existing_api_response_keys_preserved():
    """
    The API response must still contain the same top-level keys it has always
    returned so that /api/analyze and /api/query remain backward compatible.
    """
    orch, _, _, _, _, _ = _make_orchestrator_for_intent(
        stock_result=_make_stock_market_data(),
        news_result=_make_news_data(),
        risk_result=_make_risk_data(),
        portfolio_result=_make_recommendation(),
    )
    result = orch.run_intent({
        "success": True, "intent": "STOCK_ANALYSIS",
        "asset_type": "stock", "asset": "AAPL", "news_query": "Apple",
    })

    for key in ("success", "agent", "intent", "asset", "asset_type",
                "agents_used", "agent_activity",
                "market_data", "news_data", "risk_data", "recommendation",
                "summary", "disclaimer"):
        assert key in result, f"Missing expected API response key: '{key}'"

