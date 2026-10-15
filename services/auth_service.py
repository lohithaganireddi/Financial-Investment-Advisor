"""
Authentication & Security Service Module

Provides secure PBKDF2 password hashing, salt verification, and HMAC-SHA256 JWT token creation/decoding
without external binary dependencies.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict, Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError


class AuthService:
    """
    Service providing user password hashing, verification, and JWT token management.
    """

    _SECRET_KEY = os.getenv("JWT_SECRET_KEY", "smartfinancial_advisor_secure_jwt_secret_key_2026")
    _ALGORITHM = "HS256"
    _ITERATIONS = 100000
    _ph = PasswordHasher()

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a plaintext password using Argon2id with secure memory-hard parameters.

        :param password: Plaintext password string.
        :return: Encoded Argon2id hash string starting with '$argon2id$'.
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string.")

        return cls._ph.hash(password)

    @classmethod
    def _verify_pbkdf2(cls, plain_password: str, hashed_password: str) -> bool:
        """Helper to verify legacy PBKDF2-HMAC-SHA256 password hashes."""
        if not plain_password or not hashed_password or "$" not in hashed_password:
            return False

        try:
            salt, stored_hash = hashed_password.split("$", 1)
            candidate_key = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                cls._ITERATIONS,
            )
            return hmac.compare_digest(candidate_key.hex(), stored_hash)
        except Exception:
            return False

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a stored hash string.
        Supports both modern Argon2id hashes and legacy PBKDF2 hashes.

        :param plain_password: Candidate plaintext password.
        :param hashed_password: Stored hashed password string.
        :return: True if match, False otherwise.
        """
        if not plain_password or not hashed_password:
            return False

        if hashed_password.startswith("$argon2"):
            try:
                return cls._ph.verify(hashed_password, plain_password)
            except (VerifyMismatchError, InvalidHashError, Exception):
                return False

        return cls._verify_pbkdf2(plain_password, hashed_password)

    @classmethod
    def needs_rehash(cls, hashed_password: str) -> bool:
        """
        Check if a stored password hash needs to be upgraded/re-hashed to Argon2id.

        :param hashed_password: Stored hashed password string.
        :return: True if legacy hash or outdated parameters, False otherwise.
        """
        if not hashed_password or not isinstance(hashed_password, str):
            return False

        if not hashed_password.startswith("$argon2"):
            return True

        try:
            return cls._ph.check_needs_rehash(hashed_password)
        except Exception:
            return True

    @classmethod
    def _b64encode(cls, data: bytes) -> str:
        """Helper to encode bytes into unpadded base64url string."""
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    @classmethod
    def _b64decode(cls, s: str) -> bytes:
        """Helper to decode base64url string with padding."""
        padding = "=" * (4 - (len(s) % 4))
        return base64.urlsafe_b64decode((s + padding).encode("utf-8"))

    _ACCESS_TOKEN_EXPIRE_SECONDS = 900  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days configuration constant
    _REFRESH_TOKEN_EXPIRE_SECONDS = REFRESH_TOKEN_EXPIRE_DAYS * 86400  # 604,800 seconds

    @classmethod
    def generate_refresh_token(cls) -> str:
        """
        Generate a cryptographically secure random refresh token string.
        Uses secrets.token_urlsafe(32) providing 256 bits of entropy.

        :return: High-entropy raw refresh token string.
        """
        return secrets.token_urlsafe(32)

    @classmethod
    def hash_refresh_token(cls, raw_token: str) -> str:
        """
        Compute a secure SHA-256 one-way hash of a raw refresh token.

        :param raw_token: Plaintext refresh token string.
        :return: Hex-encoded SHA-256 hash string.
        """
        if not raw_token or not isinstance(raw_token, str):
            raise ValueError("Raw refresh token must be a non-empty string.")
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def create_access_token(cls, data: Dict[str, Any], expires_delta: Optional[int] = 900) -> str:
        """
        Create a signed JWT access token string containing the provided data payload.

        :param data: Claims dictionary to embed in payload (e.g. {'sub': 'user_id', 'username': 'admin'}).
        :param expires_delta: Expiration duration in seconds (default 15 minutes / 900 seconds).
        :return: Encoded JWT string 'header.payload.signature'.
        """
        header = {"alg": cls._ALGORITHM, "typ": "JWT"}
        header_b64 = cls._b64encode(json.dumps(header).encode("utf-8"))

        payload = data.copy()
        now = int(time.time())
        payload["iat"] = now
        payload["exp"] = now + (expires_delta if expires_delta is not None else cls._ACCESS_TOKEN_EXPIRE_SECONDS)

        payload_b64 = cls._b64encode(json.dumps(payload).encode("utf-8"))

        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = hmac.new(
            cls._SECRET_KEY.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        signature_b64 = cls._b64encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    @classmethod
    def decode_access_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify signature and decode a JWT token string.

        :param token: JWT token string 'header.payload.signature'.
        :return: Payload dictionary if valid and unexpired, None otherwise.
        """
        if not token or not isinstance(token, str) or token.count(".") != 2:
            return None

        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
            signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

            expected_sig = hmac.new(
                cls._SECRET_KEY.encode("utf-8"),
                signing_input,
                hashlib.sha256,
            ).digest()

            actual_sig = cls._b64decode(signature_b64)
            if not hmac.compare_digest(expected_sig, actual_sig):
                return None

            payload = json.loads(cls._b64decode(payload_b64).decode("utf-8"))
            now = int(time.time())
            if "exp" in payload and payload["exp"] < now:
                return None

            return payload
        except Exception:
            return None
