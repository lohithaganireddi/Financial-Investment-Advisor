"""
Unit Tests for QueryInterpreter Service

Verifies deterministic parsing of natural language queries into structured asset parameters.
"""

from services.query_interpreter import QueryInterpreter


def test_query_interpreter_apple():
    """Test parsing 'Should I invest in Apple?'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("Should I invest in Apple?")
    assert res["success"] is True
    assert res["asset_type"] == "stock"
    assert res["asset"] == "AAPL"
    assert res["news_query"] == "Apple"


def test_query_interpreter_tesla():
    """Test parsing 'Analyze Tesla'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("Analyze Tesla")
    assert res["success"] is True
    assert res["asset_type"] == "stock"
    assert res["asset"] == "TSLA"
    assert res["news_query"] == "Tesla"


def test_query_interpreter_nvidia():
    """Test parsing 'What about NVIDIA?'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("What about NVIDIA?")
    assert res["success"] is True
    assert res["asset_type"] == "stock"
    assert res["asset"] == "NVDA"
    assert res["news_query"] == "NVIDIA"


def test_query_interpreter_bitcoin():
    """Test parsing 'Analyze Bitcoin'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("Analyze Bitcoin")
    assert res["success"] is True
    assert res["asset_type"] == "crypto"
    assert res["asset"] == "bitcoin"
    assert res["news_query"] == "Bitcoin"


def test_query_interpreter_btc_alias():
    """Test parsing 'Is BTC risky?'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("Is BTC risky?")
    assert res["success"] is True
    assert res["asset_type"] == "crypto"
    assert res["asset"] == "bitcoin"
    assert res["news_query"] == "Bitcoin"


def test_query_interpreter_ethereum():
    """Test parsing 'Tell me about Ethereum'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("Tell me about Ethereum")
    assert res["success"] is True
    assert res["asset_type"] == "crypto"
    assert res["asset"] == "ethereum"
    assert res["news_query"] == "Ethereum"


def test_query_interpreter_uppercase_ticker():
    """Test uppercase input 'SHOULD I BUY AAPL?'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("SHOULD I BUY AAPL?")
    assert res["success"] is True
    assert res["asset_type"] == "stock"
    assert res["asset"] == "AAPL"


def test_query_interpreter_lowercase_ticker():
    """Test lowercase input 'analyze msft'."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("analyze msft")
    assert res["success"] is True
    assert res["asset_type"] == "stock"
    assert res["asset"] == "MSFT"


def test_query_interpreter_extra_whitespace():
    """Test input with leading and trailing whitespace."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("   bitcoin   ")
    assert res["success"] is True
    assert res["asset_type"] == "crypto"
    assert res["asset"] == "bitcoin"


def test_query_interpreter_empty_query():
    """Test empty string and whitespace-only input."""
    interpreter = QueryInterpreter()
    for bad in ["", "   "]:
        res = interpreter.interpret(bad)
        assert res["success"] is False
        assert "empty" in res["error"].lower()


def test_query_interpreter_unsupported_company():
    """Test unsupported company query."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("Analyze Ford")
    assert res["success"] is False
    assert "Unable to identify" in res["error"]


def test_query_interpreter_unsupported_crypto():
    """Test unsupported cryptocurrency query."""
    interpreter = QueryInterpreter()
    res = interpreter.interpret("Is Dogecoin good?")
    assert res["success"] is False
    assert "Unable to identify" in res["error"]


def test_query_interpreter_non_string_input():
    """Test non-string inputs."""
    interpreter = QueryInterpreter()
    for bad in [None, 123, [], {}]:
        res = interpreter.interpret(bad)
        assert res["success"] is False
        assert "string" in res["error"].lower()
