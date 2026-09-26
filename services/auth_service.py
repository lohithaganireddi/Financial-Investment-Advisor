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


class AuthService:
    """
    Service providing user password hashing, verification, and JWT token management.
    """

    _SECRET_KEY = os.getenv("JWT_SECRET_KEY", "smartfinancial_advisor_secure_jwt_secret_key_2026")
    _ALGORITHM = "HS256"
    _ITERATIONS = 100000

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a plaintext password using PBKDF2-HMAC-SHA256 with a 16-byte random salt.

        :param password: Plaintext password string.
        :return: Formatted string 'salt$hash_hex'.
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string.")

        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            cls._ITERATIONS,
        )
        return f"{salt}${key.hex()}"

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a stored 'salt$hash_hex' string.

        :param plain_password: Candidate plaintext password.
        :param hashed_password: Stored hashed password string.
        :return: True if match, False otherwise.
        """
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
    def _b64encode(cls, data: bytes) -> str:
        """Helper to encode bytes into unpadded base64url string."""
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    @classmethod
    def _b64decode(cls, s: str) -> bytes:
        """Helper to decode base64url string with padding."""
        padding = "=" * (4 - (len(s) % 4))
        return base64.urlsafe_b64decode((s + padding).encode("utf-8"))

    @classmethod
    def create_access_token(cls, data: Dict[str, Any], expires_delta: Optional[int] = 86400) -> str:
        """
        Create a signed JWT access token string containing the provided data payload.

        :param data: Claims dictionary to embed in payload (e.g. {'sub': 'user_id', 'username': 'admin'}).
        :param expires_delta: Expiration duration in seconds (default 24 hours).
        :return: Encoded JWT string 'header.payload.signature'.
        """
        header = {"alg": cls._ALGORITHM, "typ": "JWT"}
        header_b64 = cls._b64encode(json.dumps(header).encode("utf-8"))

        payload = data.copy()
        now = int(time.time())
        payload["iat"] = now
        payload["exp"] = now + (expires_delta if expires_delta is not None else 86400)

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
