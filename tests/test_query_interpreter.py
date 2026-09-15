"""
Unit Tests for QueryInterpreter Service (Day 19 Intent Routing)

Verifies intent classification (STOCK_ANALYSIS, CRYPTO_ANALYSIS, GENERAL_FINANCIAL_NEWS, UNSUPPORTED)
and asset symbol extraction across equities, crypto, general news, case insensitivity, and invalid inputs.
"""

from services.query_interpreter import QueryInterpreter


def test_query_interpreter_stock_intents():
    """Test stock intent classification and asset symbol extraction."""
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


def test_query_interpreter_general_financial_news():
    """Test classification of general financial news queries without specific asset."""
    interpreter = QueryInterpreter()

    queries = [
        "What is happening in the financial market?",
        "Tell me about the latest financial news",
        "Show me market headlines",
        "Give me economy news"
    ]

    for q in queries:
        res = interpreter.interpret(q)
        assert res["success"] is True
        assert res["intent"] == QueryInterpreter.INTENT_NEWS
        assert res["asset_type"] is None
        assert res["asset"] is None
        assert res["news_query"] == "finance"


def test_query_interpreter_unsupported_queries():
    """Test unsupported and unknown queries return clear structured error responses."""
    interpreter = QueryInterpreter()

    res = interpreter.interpret("Tell me about Ford stock")
    assert res["success"] is False
    assert res["intent"] == QueryInterpreter.INTENT_UNSUPPORTED
    assert "Unable to identify a supported asset or intent" in res["error"]
    assert "FinSight 2.0 currently supports" in res["error"]


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
