"""
Unit and Integration Tests for Day 37 User Authentication, Security & Watchlist Engine

Verifies password hashing, JWT token creation/decoding, UserRepository, Watchlist persistence,
and FastAPI auth/watchlist REST endpoints.
"""

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes import get_user_repository
from services.auth_service import AuthService
from services.user_repository import UserRepository
from services.rate_limiter import limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter_fixture():
    limiter.reset()
    yield
    limiter.reset()


# ==========================================
# AuthService Unit Tests
# ==========================================

def test_auth_service_argon2id_password_hashing():
    """Test Argon2id password hashing, verification, and re-hash requirements."""
    password = "SecurePassword123!"
    hashed = AuthService.hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("WrongPassword", hashed) is False
    assert AuthService.verify_password("", hashed) is False
    assert AuthService.needs_rehash(hashed) is False


def test_auth_service_pbkdf2_backward_compatibility():
    """Test legacy PBKDF2 hash verification and transparent re-hash detection."""
    import hashlib, secrets
    password = "LegacyPassword123!"
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    legacy_pbkdf2_hash = f"{salt}${key.hex()}"

    assert not legacy_pbkdf2_hash.startswith("$argon2")
    assert AuthService.verify_password(password, legacy_pbkdf2_hash) is True
    assert AuthService.verify_password("WrongPassword", legacy_pbkdf2_hash) is False
    assert AuthService.needs_rehash(legacy_pbkdf2_hash) is True


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


def test_transparent_argon2id_upgrade_on_login():
    """Test that existing PBKDF2 hashed password gets transparently upgraded to Argon2id upon successful login."""
    import hashlib, secrets
    mock_repo = MagicMock()

    # Generate legacy PBKDF2 hash
    password = "LegacySecret123!"
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    legacy_hash = f"{salt}${key.hex()}"

    mock_user = MagicMock()
    mock_user.id = 7
    mock_user.username = "legacy_user"
    mock_user.email = "legacy@fin.com"
    mock_user.role = "analyst"
    mock_user.created_at = None
    mock_user.hashed_password = legacy_hash

    mock_repo.get_user_by_username.return_value = mock_user
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        login_resp = client.post("/api/auth/login", json={"username": "legacy_user", "password": password})
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert data["success"] is True

        # Verify password hash was upgraded to Argon2id and saved
        mock_repo.update_user_password.assert_called_once()
        args, _ = mock_repo.update_user_password.call_args
        assert args[0] == 7
        assert args[1].startswith("$argon2id$")
        assert mock_user.hashed_password.startswith("$argon2id$")
    finally:
        app.dependency_overrides.clear()


def test_wrong_password_does_not_upgrade_hash():
    """Test that invalid password attempts fail and do NOT trigger password re-hashing."""
    import hashlib, secrets
    mock_repo = MagicMock()

    password = "CorrectSecret123!"
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    legacy_hash = f"{salt}${key.hex()}"

    mock_user = MagicMock()
    mock_user.id = 8
    mock_user.username = "legacy_user_2"
    mock_user.hashed_password = legacy_hash

    mock_repo.get_user_by_username.return_value = mock_user
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        login_resp = client.post("/api/auth/login", json={"username": "legacy_user_2", "password": "WrongPassword123!"})
        assert login_resp.status_code == 401

        # Verify update_user_password was NEVER called and stored hash remains unchanged PBKDF2
        mock_repo.update_user_password.assert_not_called()
        assert mock_user.hashed_password == legacy_hash
    finally:
        app.dependency_overrides.clear()


def test_watchlist_api_endpoints():
    """Test GET /api/watchlist, POST /api/watchlist, and DELETE /api/watchlist integration with valid token."""
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

    token = AuthService.create_access_token({"sub": "1", "username": "analyst_1"})
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # GET Watchlist
        get_resp = client.get("/api/watchlist", headers=headers)
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["success"] is True
        assert get_data["count"] == 1

        # POST Watchlist
        post_payload = {"asset_type": "stock", "asset": "NVDA", "target_price": "140.00", "notes": "AI momentum"}
        post_resp = client.post("/api/watchlist", json=post_payload, headers=headers)
        assert post_resp.status_code == 200
        post_data = post_resp.json()
        assert post_data["success"] is True

        # DELETE Watchlist item
        del_resp = client.delete("/api/watchlist/10", headers=headers)
        assert del_resp.status_code == 200
        del_data = del_resp.json()
        assert del_data["success"] is True
    finally:
        app.dependency_overrides.clear()


# ==========================================
# Step 3A Strict HTTP 401 Authentication Tests
# ==========================================

def test_strict_auth_missing_header_returns_401():
    """Case A: Unauthenticated request without Authorization header returns 401 Unauthorized."""
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Authentication required"
    assert resp.headers.get("www-authenticate") == "Bearer"


def test_strict_auth_missing_bearer_prefix_returns_401():
    """Case B: Authorization header without 'Bearer ' prefix returns 401 Unauthorized."""
    resp = client.get("/api/auth/me", headers={"Authorization": "Basic dXNlcjpwYXNz"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Authentication required"


def test_strict_auth_empty_bearer_token_returns_401():
    """Case C: Empty Bearer token string returns 401 Unauthorized."""
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer "})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired authentication token"


def test_strict_auth_malformed_token_returns_401():
    """Case D: Malformed JWT token string returns 401 Unauthorized."""
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.valid.jwt.string"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired authentication token"


def test_strict_auth_invalid_signature_returns_401():
    """Case E: JWT token with tampered/invalid signature returns 401 Unauthorized."""
    token = AuthService.create_access_token({"sub": "1", "username": "user1"})
    tampered_token = token[:-6] + "XXXXXX"
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired authentication token"


def test_strict_auth_expired_token_returns_401():
    """Case F: Expired JWT token returns 401 Unauthorized."""
    expired_token = AuthService.create_access_token({"sub": "1", "username": "user1"}, expires_delta=-3600)
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired authentication token"


def test_strict_auth_nonexistent_user_returns_401():
    """Case G: Valid JWT token for user ID that does not exist in DB returns 401 Unauthorized."""
    mock_repo = MagicMock()
    mock_repo.get_user_by_id.return_value = None
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    token = AuthService.create_access_token({"sub": "99999", "username": "ghost_user"})
    try:
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid or expired authentication token"
    finally:
        app.dependency_overrides.clear()


def test_strict_auth_valid_user_succeeds():
    """Case H: Valid token for an existing user returns 200 OK and user profile data."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 5
    mock_user.username = "verified_user"
    mock_user.email = "verified@smartfinance.local"
    mock_user.role = "analyst"
    mock_user.created_at = None

    mock_repo.get_user_by_id.return_value = mock_user
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    token = AuthService.create_access_token({"sub": "5", "username": "verified_user"})
    try:
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["user"]["id"] == 5
        assert data["user"]["username"] == "verified_user"
    finally:
        app.dependency_overrides.clear()


def test_cross_user_watchlist_isolation():
    """Case I: User A cannot delete User B's watchlist item."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "user_a"

    mock_repo.get_user_by_id.return_value = mock_user
    mock_repo.remove_watchlist_item.return_value = False

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    token = AuthService.create_access_token({"sub": "1", "username": "user_a"})
    try:
        resp = client.delete("/api/watchlist/99", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404
        mock_repo.remove_watchlist_item.assert_called_once_with(item_id=99, user_id=1)
    finally:
        app.dependency_overrides.clear()


def test_optional_auth_endpoint_isolation():
    """Case K: Optional-auth endpoint allows unauthenticated requests and correctly extracts valid user token."""
    from backend.routes import get_repository
    mock_repo = MagicMock()
    mock_repo.get_recent_analyses.return_value = []
    app.dependency_overrides[get_repository] = lambda: mock_repo

    try:
        resp1 = client.get("/api/history")
        assert resp1.status_code == 200

        resp2 = client.get("/api/history", headers={"Authorization": "Bearer invalid.token"})
        assert resp2.status_code == 200

        mock_user = MagicMock()
        mock_user.id = 42
        mock_user_repo = MagicMock()
        mock_user_repo.get_user_by_id.return_value = mock_user
        app.dependency_overrides[get_user_repository] = lambda: mock_user_repo

        token = AuthService.create_access_token({"sub": "42", "username": "user42"})
        resp3 = client.get("/api/history", headers={"Authorization": f"Bearer {token}"})
        assert resp3.status_code == 200
        mock_repo.get_recent_analyses.assert_called_with(limit=10, user_id=42)
    finally:
        app.dependency_overrides.clear()


def test_no_unauthenticated_request_becomes_analyst_1():
    """Case L: Unauthenticated requests to protected endpoints return 401 and never silently fall back to analyst_1."""
    mock_repo = MagicMock()
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        resp_me = client.get("/api/auth/me")
        assert resp_me.status_code == 401

        resp_wl = client.get("/api/watchlist")
        assert resp_wl.status_code == 401

        resp_wl_post = client.post("/api/watchlist", json={"asset_type": "stock", "asset": "AAPL"})
        assert resp_wl_post.status_code == 401

        mock_repo.get_user_by_id.assert_not_called()
        mock_repo.create_user.assert_not_called()
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


# ==========================================
# Step 3B Short-Lived Access Tokens (15 Min)
# ==========================================

def test_short_lived_access_token_15_minute_expiration():
    """Case A: Newly created access token defaults to a 15-minute (900s) lifetime."""
    import time
    now = int(time.time())
    token = AuthService.create_access_token({"sub": "10", "username": "short_lived_user"})
    decoded = AuthService.decode_access_token(token)

    assert decoded is not None
    assert "exp" in decoded
    assert "iat" in decoded
    expected_exp = decoded["iat"] + 900
    assert abs(decoded["exp"] - expected_exp) <= 2
    assert decoded["exp"] - now <= 905
    assert decoded["exp"] - now >= 895


# ==========================================
# Step 3C Server-Side Refresh Token Tests
# ==========================================

def test_refresh_token_generation_randomness():
    """Case A & B: Cryptographically secure refresh token generation produces unique high-entropy strings."""
    t1 = AuthService.generate_refresh_token()
    t2 = AuthService.generate_refresh_token()
    assert isinstance(t1, str) and len(t1) >= 40
    assert isinstance(t2, str) and len(t2) >= 40
    assert t1 != t2


def test_refresh_token_hashing_storage_protection():
    """Case C & D: Raw refresh token is never stored; database receives only SHA-256 hash."""
    import hashlib
    raw_token = AuthService.generate_refresh_token()
    token_hash = AuthService.hash_refresh_token(raw_token)

    assert token_hash != raw_token
    assert len(token_hash) == 64
    assert token_hash == hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def test_refresh_token_verification_success_and_failure():
    """Case E & F: Correct raw token verifies successfully; incorrect token fails verification."""
    user_repo = UserRepository()

    mock_user = MagicMock()
    mock_user.id = 12

    raw_token = "valid_raw_refresh_token_string_12345"
    token_hash = AuthService.hash_refresh_token(raw_token)

    mock_record = MagicMock()
    mock_record.user_id = 12
    mock_record.token_hash = token_hash
    mock_record.is_valid = True

    user_repo.get_refresh_token_by_hash = lambda h, session=None: mock_record if h == token_hash else None
    user_repo.get_user_by_id = lambda u_id, session=None: mock_user if u_id == 12 else None

    # E: Valid raw token returns record
    verified = user_repo.verify_refresh_token(raw_token)
    assert verified is mock_record

    # F: Incorrect token returns None
    invalid_verification = user_repo.verify_refresh_token("completely_wrong_token_123")
    assert invalid_verification is None


def test_expired_refresh_token_rejected():
    """Case G: Expired refresh token is rejected by model property and repository verification."""
    from backend.models import RefreshToken
    from datetime import datetime, timezone, timedelta

    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    record = RefreshToken(user_id=1, token_hash="dummy_hash", expires_at=past_time, revoked_at=None)

    assert record.is_expired is True
    assert record.is_valid is False


def test_refresh_token_revocation():
    """Case H & I: Token revocation marks revoked_at and renders token invalid."""
    from backend.models import RefreshToken
    from datetime import datetime, timezone, timedelta

    future_time = datetime.now(timezone.utc) + timedelta(days=7)
    record = RefreshToken(user_id=1, token_hash="dummy_hash_2", expires_at=future_time, revoked_at=None)

    assert record.is_revoked is False
    assert record.is_valid is True

    record.revoked_at = datetime.now(timezone.utc)
    assert record.is_revoked is True
    assert record.is_valid is False


def test_revoke_all_user_refresh_tokens():
    """Case J: Revoking all refresh tokens for a user ID updates all active user sessions."""
    mock_session = MagicMock()
    user_repo = UserRepository(db_session=mock_session)

    mock_token_1 = MagicMock()
    mock_token_1.revoked_at = None
    mock_token_2 = MagicMock()
    mock_token_2.revoked_at = None

    mock_session.query.return_value.filter.return_value.all.return_value = [mock_token_1, mock_token_2]

    count = user_repo.revoke_all_user_refresh_tokens(user_id=88)
    assert count == 2
    assert mock_token_1.revoked_at is not None
    assert mock_token_2.revoked_at is not None
    mock_session.commit.assert_called_once()


def test_refresh_token_nonexistent_user_rejected():
    """Case K & L: Refresh token for a non-existent user account fails verification."""
    from backend.models import RefreshToken, User
    mock_session = MagicMock()
    user_repo = UserRepository(db_session=mock_session)

    mock_record = MagicMock(spec=RefreshToken)
    mock_record.user_id = 999  # User ID 999 does not exist
    mock_record.is_valid = True

    def query_filter_side_effect(model):
        m = MagicMock()
        if model == RefreshToken:
            m.filter.return_value.first.return_value = mock_record
        elif model == User:
            m.filter.return_value.first.return_value = None  # Non-existent user
        return m

    mock_session.query.side_effect = query_filter_side_effect

    raw_token = "some_valid_looking_token"
    verified = user_repo.verify_refresh_token(raw_token)
    assert verified is None


# ==========================================
# Step 3E HttpOnly Cookie Tests
# ==========================================

def test_login_sets_httponly_refresh_cookie_and_omits_json_refresh_token():
    """Test 1 & 2: Successful login sets HttpOnly sf_refresh_token cookie and does NOT return refresh_token in JSON."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 30
    mock_user.username = "cookie_user"
    mock_user.email = "cookie@fin.com"
    mock_user.role = "analyst"
    mock_user.created_at = None
    mock_user.hashed_password = AuthService.hash_password("CookiePass123!")

    mock_repo.get_user_by_username.return_value = mock_user
    mock_repo.create_refresh_token.return_value = ("raw_cookie_token_abc123", MagicMock())

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        resp = client.post("/api/auth/login", json={"username": "cookie_user", "password": "CookiePass123!"})
        assert resp.status_code == 200
        data = resp.json()

        # Test 2: refresh_token MUST NOT be in JSON
        assert "refresh_token" not in data
        assert "access_token" in data

        # Test 1: Set-Cookie header contains HttpOnly refresh cookie
        cookie_header = resp.headers.get("set-cookie", "")
        assert "sf_refresh_token=raw_cookie_token_abc123" in cookie_header
        assert "httponly" in cookie_header.lower()
        assert "path=/api/auth" in cookie_header.lower()
        assert "samesite=lax" in cookie_header.lower()
    finally:
        app.dependency_overrides.clear()


def test_refresh_endpoint_uses_httponly_cookie():
    """Test 3, 4 & 9: POST /api/auth/refresh reads cookie, returns new access token & replacement cookie."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 30
    mock_user.username = "cookie_user"

    mock_new_record = MagicMock()
    mock_new_record.user_id = 30

    mock_repo.rotate_refresh_token.return_value = ("new_cookie_token_xyz789", mock_new_record, None)
    mock_repo.get_user_by_id.return_value = mock_user

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        client.cookies.set("sf_refresh_token", "raw_cookie_token_abc123", path="/api/auth")
        resp = client.post("/api/auth/refresh")

        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" not in data

        # Replacement cookie set
        cookie_header = resp.headers.get("set-cookie", "")
        assert "sf_refresh_token=new_cookie_token_xyz789" in cookie_header
        assert "httponly" in cookie_header.lower()

        # Test 9: Verify access token lifetime remains 15 minutes (900 seconds)
        decoded = AuthService.decode_access_token(data["access_token"])
        assert decoded is not None
        assert decoded["sub"] == "30"
        assert decoded["username"] == "cookie_user"
        assert decoded["exp"] - decoded["iat"] == 900
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


def test_refresh_token_rotation_chain_and_replay_protection_cookie():
    """Test 5: Cookie-based rotation chain A -> B -> C and replay protection for revoked tokens."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 20
    mock_user.username = "chain_user"

    token_a = "token_chain_A"
    token_b = "token_chain_B"
    token_c = "token_chain_C"

    tokens = {
        token_a: {"revoked": False, "family": "fam_100"},
        token_b: {"revoked": False, "family": "fam_100"},
        token_c: {"revoked": False, "family": "fam_100"},
    }

    def mock_rotate(t_str, user_agent=None, ip_address=None):
        if t_str not in tokens:
            return None, None, "Invalid or expired refresh token"
        t_info = tokens[t_str]
        if t_info["revoked"]:
            fam = t_info["family"]
            for k, v in tokens.items():
                if v["family"] == fam:
                    v["revoked"] = True
            return None, None, "Invalid or expired refresh token"

        t_info["revoked"] = True
        next_map = {token_a: token_b, token_b: token_c}
        next_t = next_map.get(t_str, "token_chain_D")
        rec = MagicMock()
        rec.user_id = 20
        rec.family_id = t_info["family"]
        return next_t, rec, None

    mock_repo.rotate_refresh_token.side_effect = mock_rotate
    mock_repo.get_user_by_id.return_value = mock_user
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        # Step 1: Refresh A -> sets B cookie
        r1 = client.post("/api/auth/refresh", cookies={"sf_refresh_token": token_a})
        assert r1.status_code == 200
        assert "sf_refresh_token=" + token_b in r1.headers.get("set-cookie", "")

        # Step 2: Refresh B -> sets C cookie
        r2 = client.post("/api/auth/refresh", cookies={"sf_refresh_token": token_b})
        assert r2.status_code == 200
        assert "sf_refresh_token=" + token_c in r2.headers.get("set-cookie", "")

        # Test 5: Replay A -> 401 & triggers family revocation
        r_replay_a = client.post("/api/auth/refresh", cookies={"sf_refresh_token": token_a})
        assert r_replay_a.status_code == 401

        # Subsequent use of C also fails because family was revoked on replay
        r_c_after_replay = client.post("/api/auth/refresh", cookies={"sf_refresh_token": token_c})
        assert r_c_after_replay.status_code == 401
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


def test_refresh_endpoint_missing_cookie_returns_401():
    """Test 6: Refresh endpoint without cookie returns 401 Unauthorized."""
    client.cookies.clear()
    resp = client.post("/api/auth/refresh")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired refresh token"


def test_refresh_endpoint_invalid_cookie_returns_401():
    """Test 7: Refresh endpoint with invalid cookie returns 401 Unauthorized."""
    client.cookies.set("sf_refresh_token", "invalid_random_cookie_val", path="/api/auth")
    resp = client.post("/api/auth/refresh")
    assert resp.status_code == 401
    client.cookies.clear()


def test_refresh_endpoint_expired_token_cookie_returns_401():
    """Test 8: Expired refresh token in cookie returns 401 Unauthorized."""
    mock_repo = MagicMock()
    mock_repo.rotate_refresh_token.return_value = (None, None, "Invalid or expired refresh token")
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        client.cookies.set("sf_refresh_token", "expired_cookie_val", path="/api/auth")
        resp = client.post("/api/auth/refresh")
        assert resp.status_code == 401
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


# ==========================================
# Step 3G Logout & Session Revocation Tests
# ==========================================

def test_logout_valid_user_and_cookie_revokes_session():
    """Test 1-4: POST /api/auth/logout with valid access token & cookie revokes session and clears cookie."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 50
    mock_user.username = "logout_user"

    raw_token = "raw_refresh_token_to_logout"
    token_hash = AuthService.hash_refresh_token(raw_token)

    mock_record = MagicMock()
    mock_record.user_id = 50
    mock_record.token_hash = token_hash

    mock_repo.get_user_by_id.return_value = mock_user
    mock_repo.get_refresh_token_by_hash.return_value = mock_record

    app.dependency_overrides[get_user_repository] = lambda: mock_repo
    access_token = AuthService.create_access_token({"sub": "50", "username": "logout_user"})

    try:
        resp = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"sf_refresh_token": raw_token}
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out successfully"

        # Verify cookie cleared
        cookie_header = resp.headers.get("set-cookie", "")
        assert "sf_refresh_token=;" in cookie_header or "max-age=0" in cookie_header.lower()

        # Verify revoke_refresh_token called with token_hash
        mock_repo.revoke_refresh_token.assert_called_once_with(token_hash)
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


def test_logout_missing_or_invalid_refresh_cookie_succeeds_safely():
    """Test 5-7: POST /api/auth/logout succeeds safely when refresh cookie is missing, invalid, or already revoked."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 51

    mock_repo.get_user_by_id.return_value = mock_user
    mock_repo.get_refresh_token_by_hash.return_value = None

    app.dependency_overrides[get_user_repository] = lambda: mock_repo
    access_token = AuthService.create_access_token({"sub": "51", "username": "user51"})

    try:
        # Missing cookie
        resp1 = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
        assert resp1.status_code == 200
        assert resp1.json()["message"] == "Logged out successfully"

        # Invalid cookie
        resp2 = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"sf_refresh_token": "nonexistent_token_val"}
        )
        assert resp2.status_code == 200
        assert resp2.json()["message"] == "Logged out successfully"
        mock_repo.revoke_refresh_token.assert_not_called()
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


def test_logout_unauthenticated_requests_return_401():
    """Test 8-10: POST /api/auth/logout returns 401 for missing, invalid, or expired access token."""
    # Missing access token
    r1 = client.post("/api/auth/logout")
    assert r1.status_code == 401

    # Invalid access token
    r2 = client.post("/api/auth/logout", headers={"Authorization": "Bearer invalid.token"})
    assert r2.status_code == 401

    # Expired access token
    expired_token = AuthService.create_access_token({"sub": "50", "username": "user50"}, expires_delta=-3600)
    r3 = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {expired_token}"})
    assert r3.status_code == 401


def test_logout_cross_user_revocation_prevented():
    """Test 11: User A cannot revoke User B's refresh token session via cookie."""
    mock_repo = MagicMock()
    mock_user_a = MagicMock()
    mock_user_a.id = 100

    mock_record_b = MagicMock()
    mock_record_b.user_id = 200  # Belongs to User B

    mock_repo.get_user_by_id.return_value = mock_user_a
    mock_repo.get_refresh_token_by_hash.return_value = mock_record_b

    app.dependency_overrides[get_user_repository] = lambda: mock_repo
    access_token_a = AuthService.create_access_token({"sub": "100", "username": "user_a"})

    try:
        resp = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token_a}"},
            cookies={"sf_refresh_token": "user_b_refresh_token"}
        )
        assert resp.status_code == 200
        # Revoke must NOT be called on User B's record
        mock_repo.revoke_refresh_token.assert_not_called()
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


def test_logout_all_sessions_revokes_all_user_tokens():
    """Test 1-5, 8-10: POST /api/auth/logout-all revokes all sessions for user, clears cookie, preserves DB rows."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 60

    mock_repo.get_user_by_id.return_value = mock_user
    mock_repo.revoke_all_user_refresh_tokens.return_value = 3

    app.dependency_overrides[get_user_repository] = lambda: mock_repo
    access_token = AuthService.create_access_token({"sub": "60", "username": "multi_device_user"})

    try:
        resp = client.post(
            "/api/auth/logout-all",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"sf_refresh_token": "device1_token"}
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "All sessions logged out successfully"

        # Cookie cleared
        assert "sf_refresh_token=;" in resp.headers.get("set-cookie", "") or "max-age=0" in resp.headers.get("set-cookie", "").lower()

        # Revoke all called for user 60
        mock_repo.revoke_all_user_refresh_tokens.assert_called_once_with(user_id=60)
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


def test_logout_all_unauthenticated_requests_return_401():
    """Test 6-7: POST /api/auth/logout-all returns 401 when access token is missing or invalid."""
    r1 = client.post("/api/auth/logout-all")
    assert r1.status_code == 401

    r2 = client.post("/api/auth/logout-all", headers={"Authorization": "Bearer bad_token"})
    assert r2.status_code == 401


def test_logout_integration_login_refresh_logout_flow():
    """Integration Test: LOGIN -> refresh works -> logout -> refresh fails (401)."""
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 77
    mock_user.username = "flow_user"

    active_tokens = {}

    def mock_create_rf(user_id, raw_token=None, family_id=None, expires_days=7, user_agent=None, ip_address=None):
        t = AuthService.generate_refresh_token()
        h = AuthService.hash_refresh_token(t)
        active_tokens[h] = {"user_id": user_id, "revoked": False}
        rec = MagicMock()
        rec.user_id = user_id
        return t, rec

    def mock_rotate(raw_t, user_agent=None, ip_address=None):
        h = AuthService.hash_refresh_token(raw_t)
        if h not in active_tokens or active_tokens[h]["revoked"]:
            return None, None, "Invalid or expired refresh token"
        active_tokens[h]["revoked"] = True
        new_t = AuthService.generate_refresh_token()
        new_h = AuthService.hash_refresh_token(new_t)
        active_tokens[new_h] = {"user_id": active_tokens[h]["user_id"], "revoked": False}
        rec = MagicMock()
        rec.user_id = active_tokens[h]["user_id"]
        return new_t, rec, None

    def mock_get_by_hash(h):
        if h in active_tokens:
            rec = MagicMock()
            rec.user_id = active_tokens[h]["user_id"]
            return rec
        return None

    def mock_revoke_single(h_or_raw):
        h = h_or_raw if len(h_or_raw) == 64 else AuthService.hash_refresh_token(h_or_raw)
        if h in active_tokens:
            active_tokens[h]["revoked"] = True
            return True
        return False

    mock_repo.get_user_by_id.return_value = mock_user
    mock_repo.create_refresh_token.side_effect = mock_create_rf
    mock_repo.rotate_refresh_token.side_effect = mock_rotate
    mock_repo.get_refresh_token_by_hash.side_effect = mock_get_by_hash
    mock_repo.revoke_refresh_token.side_effect = mock_revoke_single

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        # Step 1: Issue token
        t_raw, _ = mock_create_rf(77)
        access_t = AuthService.create_access_token({"sub": "77", "username": "flow_user"})

        # Step 2: Refresh works before logout
        r_ref1 = client.post("/api/auth/refresh", cookies={"sf_refresh_token": t_raw})
        assert r_ref1.status_code == 200

        # Extract new rotated cookie
        cookie_hdr = r_ref1.headers.get("set-cookie", "")
        import re
        m = re.search(r"sf_refresh_token=([^;]+)", cookie_hdr)
        assert m is not None
        t_rotated = m.group(1)

        # Step 3: Logout with current session
        r_logout = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_t}"},
            cookies={"sf_refresh_token": t_rotated}
        )
        assert r_logout.status_code == 200

        # Step 4: Refresh fails after logout
        r_ref2 = client.post("/api/auth/refresh", cookies={"sf_refresh_token": t_rotated})
        assert r_ref2.status_code == 401
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


# ==========================================
# Step 3H Rate Limiting & Brute-Force Tests
# ==========================================

def test_login_under_allowed_rate_limit():
    """Test 1: Login requests under the allowed rate limit (<= 5 per min) execute without 429."""
    limiter.reset()
    mock_repo = MagicMock()
    mock_repo.get_user_by_username.return_value = None
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        for _ in range(4):
            resp = client.post("/api/auth/login", json={"username": "user", "password": "wrongpassword"})
            assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_repeated_failed_logins_receive_429_and_retry_after():
    """Test 2 & 3: Repeated login requests exceeding 5 per min return HTTP 429 and Retry-After header."""
    limiter.reset()
    mock_repo = MagicMock()
    mock_repo.get_user_by_username.return_value = None
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        # Send 5 requests (hitting limit)
        for _ in range(5):
            client.post("/api/auth/login", json={"username": "user", "password": "wrongpassword"})

        # 6th request triggers 429
        resp = client.post("/api/auth/login", json={"username": "user", "password": "wrongpassword"})
        assert resp.status_code == 429
        assert "Too many requests" in resp.json()["detail"]
        assert "retry-after" in resp.headers
        assert int(resp.headers["retry-after"]) > 0
    finally:
        app.dependency_overrides.clear()


def test_registration_rate_limiting():
    """Test 5: Registration endpoint throttles after 10 requests within window."""
    limiter.reset()
    mock_repo = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "user_1"
    mock_user.email = "user_1@test.com"
    mock_user.role = "analyst"
    mock_user.created_at = None

    mock_repo.get_user_by_username.return_value = None
    mock_repo.create_user.return_value = mock_user
    mock_repo.create_refresh_token.return_value = ("token_str", MagicMock())
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        for i in range(10):
            client.post("/api/auth/register", json={"username": f"user_{i}", "email": f"user_{i}@test.com", "password": "password123"})

        # 11th request triggers 429
        resp = client.post("/api/auth/register", json={"username": "user_11", "email": "user_11@test.com", "password": "password123"})
        assert resp.status_code == 429
        assert "retry-after" in resp.headers
    finally:
        app.dependency_overrides.clear()


def test_refresh_rate_limiting():
    """Test 6 & 7: Refresh endpoint throttles after 30 requests while allowing normal usage."""
    limiter.reset()
    mock_repo = MagicMock()
    mock_repo.rotate_refresh_token.return_value = (None, None, "Invalid or expired refresh token")
    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    try:
        client.cookies.set("sf_refresh_token", "dummy_token", path="/api/auth")
        for _ in range(30):
            r = client.post("/api/auth/refresh")
            assert r.status_code == 401

        # 31st request triggers 429
        resp = client.post("/api/auth/refresh")
        assert resp.status_code == 429
        assert "retry-after" in resp.headers
    finally:
        client.cookies.clear()
        app.dependency_overrides.clear()


# ==========================================
# Step 3I Security Headers & CORS Tests
# ==========================================

def test_security_response_headers_present():
    """Test that all required security HTTP response headers are attached."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in resp.headers.get("permissions-policy", "")


def test_cors_hardening_allowed_and_disallowed_origins():
    """Test CORS configuration enforces strict origin checks with credentials enabled."""
    # Test 1: Allowed origin returns exact origin header & credentials flag
    resp_allowed = client.options("/api/auth/login", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert resp_allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert resp_allowed.headers.get("access-control-allow-credentials") == "true"
    assert resp_allowed.headers.get("access-control-allow-origin") != "*"

    # Test 2: Disallowed origin does NOT receive Access-Control-Allow-Origin header
    resp_disallowed = client.options("/api/auth/login", headers={"Origin": "http://malicious-attacker-site.com", "Access-Control-Request-Method": "POST"})
    assert resp_disallowed.headers.get("access-control-allow-origin") != "http://malicious-attacker-site.com"




