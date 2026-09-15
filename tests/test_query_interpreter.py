"""
Unit Tests for QueryInterpreter Service (Day 25 Enhanced Intent Routing)

Verifies intent classification, expanded stock/crypto mappings, ticker symbol normalization ($AAPL),
explicit asset-news routing, multi-asset ambiguity detection, and unknown query responses.
"""

from services.query_interpreter import QueryInterpreter


def test_query_interpreter_stock_intents():
    """Test standard stock intent classification and asset symbol extraction."""
    interpreter = QueryInterpreter()

    # Apple
    res1 = interpreter.interpret("Should I invest in Apple?")
    assert res1["success"] is True
    assert res1["intent"] == QueryInterpreter.INTENT_STOCK
    assert res1["asset_type"] == "stock"
    assert res1["asset"] == "AAPL"
    assert res1["news_query"] == "Apple"

    # Microsoft
    res2 = interpreter.interpret("Analyze Microsoft stock")
    assert res2["success"] is True
    assert res2["intent"] == QueryInterpreter.INTENT_STOCK
    assert res2["asset"] == "MSFT"

    # Tesla
    res3 = interpreter.interpret("What is happening with Tesla?")
    assert res3["success"] is True
    assert res3["intent"] == QueryInterpreter.INTENT_STOCK
    assert res3["asset"] == "TSLA"

    # Nvidia
    res4 = interpreter.interpret("Analyze NVDA")
    assert res4["success"] is True
    assert res4["intent"] == QueryInterpreter.INTENT_STOCK
    assert res4["asset"] == "NVDA"

    # Amazon
    res5 = interpreter.interpret("Tell me about Amazon")
    assert res5["success"] is True
    assert res5["intent"] == QueryInterpreter.INTENT_STOCK
    assert res5["asset"] == "AMZN"

    # Google / Alphabet
    res6 = interpreter.interpret("Should I buy Alphabet?")
    assert res6["success"] is True
    assert res6["intent"] == QueryInterpreter.INTENT_STOCK
    assert res6["asset"] == "GOOGL"

    # Meta
    res7 = interpreter.interpret("What about Meta stock?")
    assert res7["success"] is True
    assert res7["intent"] == QueryInterpreter.INTENT_STOCK
    assert res7["asset"] == "META"


def test_query_interpreter_new_stock_mappings():
    """Test Day 25 added stock asset mappings (Netflix, AMD, Intel, Coca-Cola, Walmart)."""
    interpreter = QueryInterpreter()

    # Netflix / NFLX
    res_nflx = interpreter.interpret("Analyze Netflix")
    assert res_nflx["success"] is True
    assert res_nflx["intent"] == QueryInterpreter.INTENT_STOCK
    assert res_nflx["asset"] == "NFLX"

    # AMD
    res_amd = interpreter.interpret("Should I invest in AMD?")
    assert res_amd["success"] is True
    assert res_amd["asset"] == "AMD"

    # Intel / INTC
    res_intc = interpreter.interpret("Check INTC stock")
    assert res_intc["success"] is True
    assert res_intc["asset"] == "INTC"

    # Coca-Cola / Coke / KO
    res_ko = interpreter.interpret("How is Coca-Cola doing?")
    assert res_ko["success"] is True
    assert res_ko["asset"] == "KO"

    # Walmart / WMT
    res_wmt = interpreter.interpret("Analyze WMT")
    assert res_wmt["success"] is True
    assert res_wmt["asset"] == "WMT"


def test_query_interpreter_crypto_intents():
    """Test crypto intent classification and coin ID extraction."""
    interpreter = QueryInterpreter()

    # Bitcoin
    res1 = interpreter.interpret("Should I buy bitcoin?")
    assert res1["success"] is True
    assert res1["intent"] == QueryInterpreter.INTENT_CRYPTO
    assert res1["asset_type"] == "crypto"
    assert res1["asset"] == "bitcoin"
    assert res1["news_query"] == "Bitcoin"

    # Ethereum
    res2 = interpreter.interpret("Analyze Ethereum")
    assert res2["success"] is True
    assert res2["intent"] == QueryInterpreter.INTENT_CRYPTO
    assert res2["asset"] == "ethereum"

    # Solana
    res3 = interpreter.interpret("Is SOL a good crypto?")
    assert res3["success"] is True
    assert res3["intent"] == QueryInterpreter.INTENT_CRYPTO
    assert res3["asset"] == "solana"

    # Dogecoin
    res4 = interpreter.interpret("Is Dogecoin good?")
    assert res4["success"] is True
    assert res4["intent"] == QueryInterpreter.INTENT_CRYPTO
    assert res4["asset"] == "dogecoin"


def test_query_interpreter_new_crypto_mappings():
    """Test Day 25 added crypto mappings (Cardano, XRP, Binance Coin, Polygon)."""
    interpreter = QueryInterpreter()

    # Cardano / ADA
    res_ada = interpreter.interpret("Analyze Cardano")
    assert res_ada["success"] is True
    assert res_ada["intent"] == QueryInterpreter.INTENT_CRYPTO
    assert res_ada["asset"] == "cardano"

    # XRP / Ripple
    res_xrp = interpreter.interpret("Should I buy XRP?")
    assert res_xrp["success"] is True
    assert res_xrp["asset"] == "ripple"

    # Binance Coin / BNB
    res_bnb = interpreter.interpret("Check BNB crypto")
    assert res_bnb["success"] is True
    assert res_bnb["asset"] == "binancecoin"

    # Polygon / MATIC
    res_matic = interpreter.interpret("Is Polygon a good investment?")
    assert res_matic["success"] is True
    assert res_matic["asset"] == "polygon"


def test_query_interpreter_ticker_prefix_normalization():
    """Test normalization of $ prefixed ticker symbols ($AAPL, $TSLA, $BTC)."""
    interpreter = QueryInterpreter()

    res1 = interpreter.interpret("Analyze $AAPL")
    assert res1["success"] is True
    assert res1["intent"] == QueryInterpreter.INTENT_STOCK
    assert res1["asset"] == "AAPL"

    res2 = interpreter.interpret("Should I buy $TSLA?")
    assert res2["success"] is True
    assert res2["intent"] == QueryInterpreter.INTENT_STOCK
    assert res2["asset"] == "TSLA"

    res3 = interpreter.interpret("Check $BTC")
    assert res3["success"] is True
    assert res3["intent"] == QueryInterpreter.INTENT_CRYPTO
    assert res3["asset"] == "bitcoin"


def test_query_interpreter_explicit_asset_news_queries():
    """Test explicit requests for news about a specific asset route to GENERAL_FINANCIAL_NEWS."""
    interpreter = QueryInterpreter()

    res1 = interpreter.interpret("Latest news about Tesla")
    assert res1["success"] is True
    assert res1["intent"] == QueryInterpreter.INTENT_NEWS
    assert res1["news_query"] == "Tesla"
    assert res1["asset"] is None

    res2 = interpreter.interpret("Apple stock news")
    assert res2["success"] is True
    assert res2["intent"] == QueryInterpreter.INTENT_NEWS
    assert res2["news_query"] == "Apple"

    res3 = interpreter.interpret("Bitcoin news")
    assert res3["success"] is True
    assert res3["intent"] == QueryInterpreter.INTENT_NEWS
    assert res3["news_query"] == "Bitcoin"

    res4 = interpreter.interpret("Ethereum headlines")
    assert res4["success"] is True
    assert res4["intent"] == QueryInterpreter.INTENT_NEWS
    assert res4["news_query"] == "Ethereum"


def test_query_interpreter_general_financial_news():
    """Test classification of general financial news queries without specific asset."""
    interpreter = QueryInterpreter()

    queries = [
        "What is happening in the financial market?",
        "Tell me about the latest financial news",
        "Show me market headlines",
        "Give me economy news",
        "Show me business news",
        "Any news about inflation?",
        "Latest stock market news"
    ]

    for q in queries:
        res = interpreter.interpret(q)
        assert res["success"] is True
        assert res["intent"] == QueryInterpreter.INTENT_NEWS
        assert res["asset_type"] is None
        assert res["asset"] is None


def test_query_interpreter_multiple_asset_ambiguity():
    """Test that queries mentioning multiple distinct assets return an UNSUPPORTED error."""
    interpreter = QueryInterpreter()

    res1 = interpreter.interpret("Compare Apple and Tesla")
    assert res1["success"] is False
    assert res1["intent"] == QueryInterpreter.INTENT_UNSUPPORTED
    assert "Ambiguous query containing multiple distinct financial assets" in res1["error"]

    res2 = interpreter.interpret("Should I buy AAPL or BTC?")
    assert res2["success"] is False
    assert res2["intent"] == QueryInterpreter.INTENT_UNSUPPORTED
    assert "Ambiguous query containing multiple distinct financial assets" in res2["error"]


def test_query_interpreter_unsupported_queries():
    """Test unsupported and unknown queries return clear structured error responses."""
    interpreter = QueryInterpreter()

    res = interpreter.interpret("Tell me about Ford stock")
    assert res["success"] is False
    assert res["intent"] == QueryInterpreter.INTENT_UNSUPPORTED
    assert "Unable to identify a supported financial asset" in res["error"]


def test_query_interpreter_case_insensitivity_and_whitespace():
    """Test case insensitivity and extra whitespace handling."""
    interpreter = QueryInterpreter()

    res1 = interpreter.interpret("   SHOULD I BUY AAPL?   ")
    assert res1["success"] is True
    assert res1["intent"] == QueryInterpreter.INTENT_STOCK
    assert res1["asset"] == "AAPL"

    res2 = interpreter.interpret("  analyze BITCOIN   ")
    assert res2["success"] is True
    assert res2["intent"] == QueryInterpreter.INTENT_CRYPTO
    assert res2["asset"] == "bitcoin"


def test_query_interpreter_empty_and_invalid_inputs():
    """Test empty, whitespace-only, and non-string inputs."""
    interpreter = QueryInterpreter()

    for bad in ["", "   ", None, 123, [], {}]:
        res = interpreter.interpret(bad)
        assert res["success"] is False
        assert res["intent"] == QueryInterpreter.INTENT_UNSUPPORTED
        assert "error" in res
