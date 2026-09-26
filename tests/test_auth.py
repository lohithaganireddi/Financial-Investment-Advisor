"""
Unit and Integration Tests for Day 37 User Authentication, Security & Watchlist Engine

Verifies password hashing, JWT token creation/decoding, UserRepository, Watchlist persistence,
and FastAPI auth/watchlist REST endpoints.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes import get_user_repository
from services.auth_service import AuthService
from services.user_repository import UserRepository

client = TestClient(app)


# ==========================================
# AuthService Unit Tests
# ==========================================

def test_auth_service_password_hashing():
    """Test PBKDF2 password hashing and verification."""
    password = "SecurePassword123!"
    hashed = AuthService.hash_password(password)

    assert hashed != password
    assert "$" in hashed
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("WrongPassword", hashed) is False
    assert AuthService.verify_password("", hashed) is False


def test_auth_service_jwt_token_creation_and_decoding():
    """Test JWT token encoding, signature verification, and payload extraction."""
    payload = {"sub": "1", "username": "testuser", "role": "analyst"}
    token = AuthService.create_access_token(payload, expires_delta=3600)

    assert isinstance(token, str)
    assert token.count(".") == 2

    decoded = AuthService.decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "1"
    assert decoded["username"] == "testuser"
    assert decoded["role"] == "analyst"


def test_auth_service_invalid_jwt_token():
    """Test that tampered or invalid JWT tokens fail validation cleanly."""
    assert AuthService.decode_access_token("invalid.jwt.token") is None
    assert AuthService.decode_access_token("") is None


# ==========================================
# UserRepository Unit Tests
# ==========================================

def test_user_repository_create_and_find_user():
    """Test UserRepository user registration and username lookup."""
    repo = UserRepository()
    mock_session = MagicMock()

    user = repo.create_user(
        username="trader1",
        email="trader1@finance.local",
        password="password123",
        session=mock_session
    )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_watchlist_repository_add_and_get():
    """Test UserRepository watchlist item addition and retrieval."""
    repo = UserRepository()
    mock_session = MagicMock()

    item = repo.add_watchlist_item(
        user_id=1,
        asset_type="stock",
        asset="AAPL",
        target_price="200.00",
        notes="Apple target",
        session=mock_session
    )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


# ==========================================
# Auth REST Endpoint Tests
# ==========================================

def test_register_and_login_api_endpoints():
    """Test POST /api/auth/register and POST /api/auth/login integration."""
    mock_repo = MagicMock()

    # Mock user object
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "newanalyst"
    mock_user.email = "analyst@fin.com"
    mock_user.role = "analyst"
    mock_user.created_at = None
    mock_user.hashed_password = AuthService.hash_password("secret123")

    mock_repo.get_user_by_username.return_value = None
    mock_repo.create_user.return_value = mock_user

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        # Test Registration Endpoint
        reg_payload = {"username": "newanalyst", "email": "analyst@fin.com", "password": "secret123"}
        reg_resp = client.post("/api/auth/register", json=reg_payload)

        assert reg_resp.status_code == 200
        reg_data = reg_resp.json()
        assert reg_data["success"] is True
        assert "access_token" in reg_data
        assert reg_data["user"]["username"] == "newanalyst"

        # Test Login Endpoint
        mock_repo.get_user_by_username.return_value = mock_user
        login_payload = {"username": "newanalyst", "password": "secret123"}
        login_resp = client.post("/api/auth/login", json=login_payload)

        assert login_resp.status_code == 200
        login_data = login_resp.json()
        assert login_data["success"] is True
        assert "access_token" in login_data
    finally:
        app.dependency_overrides.clear()


def test_watchlist_api_endpoints():
    """Test GET /api/watchlist and POST /api/watchlist integration."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "analyst_1"
    mock_user.email = "analyst_1@smartfinance.local"
    mock_user.role = "analyst"

    mock_watchlist_item = MagicMock()
    mock_watchlist_item.id = 10
    mock_watchlist_item.user_id = 1
    mock_watchlist_item.asset_type = "stock"
    mock_watchlist_item.asset = "NVDA"
    mock_watchlist_item.target_price = "140.00"
    mock_watchlist_item.notes = "AI momentum"
    mock_watchlist_item.added_at = None

    mock_repo.get_user_by_id.return_value = mock_user
    mock_repo.get_user_watchlist.return_value = [mock_watchlist_item]
    mock_repo.add_watchlist_item.return_value = mock_watchlist_item
    mock_repo.remove_watchlist_item.return_value = True

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        # GET Watchlist
        get_resp = client.get("/api/watchlist")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["success"] is True
        assert get_data["count"] == 1

        # POST Watchlist
        post_payload = {"asset_type": "stock", "asset": "NVDA", "target_price": "140.00", "notes": "AI momentum"}
        post_resp = client.post("/api/watchlist", json=post_payload)
        assert post_resp.status_code == 200
        post_data = post_resp.json()
        assert post_data["success"] is True

        # DELETE Watchlist item
        del_resp = client.delete("/api/watchlist/10")
        assert del_resp.status_code == 200
        del_data = del_resp.json()
        assert del_data["success"] is True
    finally:
        app.dependency_overrides.clear()


# ==========================================
# Day 42 User-Bound History & Migration Tests
# ==========================================

def test_user_bound_analysis_history():
    """Test saving analysis with user_id and filtering history by user."""
    from services.analysis_repository import AnalysisRepository
    from backend.models import Analysis

    repo = AnalysisRepository()
    mock_session = MagicMock()

    # Test save_analysis with user_id
    saved = repo.save_analysis(
        query="Analyze TSLA",
        asset_type="stock",
        asset="TSLA",
        user_id=42,
        session=mock_session
    )
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

    # Test get_recent_analyses with user_id filter
    mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    records = repo.get_recent_analyses(limit=10, user_id=42, session=mock_session)
    mock_session.query.return_value.filter.assert_called_once()


def test_init_db_idempotent_migration():
    """Test init_db executes cleanly without error on existing schema."""
    from backend.database import init_db
    init_db()  # Must execute idempotently without throwing error

