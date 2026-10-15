"""
User Repository Module

Provides database operations for User management and Watchlist persistence.
Encapsulates SQLAlchemy database logic for users and watchlists.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, Watchlist, RefreshToken
from services.auth_service import AuthService


class UserRepository:
    """
    Repository for managing User accounts and Watchlist database operations.
    """

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize UserRepository.
        Supports dependency injection of custom Session.
        """
        self._external_session = db_session

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "analyst",
        session: Optional[Session] = None
    ) -> Optional[User]:
        """
        Register a new user account.

        :param username: Unique username string.
        :param email: Unique email address string.
        :param password: Plaintext password.
        :param role: User role (default 'analyst').
        :return: Created User instance or None if registration fails/exists.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            hashed_pwd = AuthService.hash_password(password)
            user = User(
                username=username.strip().lower(),
                email=email.strip().lower(),
                hashed_password=hashed_pwd,
                role=role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            return None
        finally:
            if close_needed:
                db.close()

    def get_user_by_username(
        self,
        username: str,
        session: Optional[Session] = None
    ) -> Optional[User]:
        """
        Find user record by username string.

        :param username: Username to search.
        :return: User instance if found, None otherwise.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            user = db.query(User).filter(User.username == username.strip().lower()).first()
            return user
        except Exception:
            return None
        finally:
            if close_needed:
                db.close()

    def get_user_by_id(
        self,
        user_id: int,
        session: Optional[Session] = None
    ) -> Optional[User]:
        """
        Find user record by integer primary key ID.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user
        except Exception:
            return None
        finally:
            if close_needed:
                db.close()

    def update_user_password(
        self,
        user_id: int,
        new_hashed_password: str,
        session: Optional[Session] = None
    ) -> bool:
        """
        Update stored password hash for a user account (used for transparent Argon2id upgrades).

        :param user_id: ID of target user.
        :param new_hashed_password: New hashed password string.
        :return: True if update succeeded, False otherwise.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                return False

            user.hashed_password = new_hashed_password
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            if close_needed:
                db.close()

    def add_watchlist_item(
        self,
        user_id: int,
        asset_type: str,
        asset: str,
        target_price: Optional[str] = None,
        notes: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Optional[Watchlist]:
        """
        Add an asset item to a user's watchlist.

        :return: Created Watchlist instance or None.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            item = Watchlist(
                user_id=user_id,
                asset_type=asset_type.lower(),
                asset=asset.upper(),
                target_price=target_price,
                notes=notes
            )
            db.add(item)
            db.commit()
            db.refresh(item)
            return item
        except Exception:
            db.rollback()
            return None
        finally:
            if close_needed:
                db.close()

    def get_user_watchlist(
        self,
        user_id: int,
        session: Optional[Session] = None
    ) -> List[Watchlist]:
        """
        Retrieve all watchlist items for a specific user ID ordered newest first.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            items = (
                db.query(Watchlist)
                .filter(Watchlist.user_id == user_id)
                .order_by(Watchlist.added_at.desc())
                .all()
            )
            return items
        except Exception:
            return []
        finally:
            if close_needed:
                db.close()

    def remove_watchlist_item(
        self,
        item_id: int,
        user_id: int,
        session: Optional[Session] = None
    ) -> bool:
        """
        Remove a watchlist item by item ID for a user.

        :return: True if item was deleted, False otherwise.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            item = db.query(Watchlist).filter(
                Watchlist.id == item_id,
                Watchlist.user_id == user_id
            ).first()

            if item is None:
                return False

            db.delete(item)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            if close_needed:
                db.close()

    def create_refresh_token(
        self,
        user_id: int,
        raw_token: Optional[str] = None,
        family_id: Optional[str] = None,
        expires_days: int = 7,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Tuple[Optional[str], Optional[RefreshToken]]:
        """
        Issue a new refresh token for a user.
        Generates a high-entropy random token, computes its SHA-256 hash, and saves only the hash to DB.

        :param user_id: ID of recipient user account.
        :param raw_token: Optional pre-generated raw token string (generates new token if None).
        :param family_id: Optional session family identifier string.
        :param expires_days: Expiration duration in days (default 7).
        :param user_agent: Optional client browser User-Agent header string.
        :param ip_address: Optional client IP address string.
        :return: Tuple of (raw_token_string, created_RefreshToken_model_instance).
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            token_str = raw_token or AuthService.generate_refresh_token()
            token_hash = AuthService.hash_refresh_token(token_str)
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
            fam_id = family_id or token_hash

            record = RefreshToken(
                user_id=user_id,
                token_hash=token_hash,
                family_id=fam_id,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=expires_at
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return token_str, record
        except Exception:
            db.rollback()
            return None, None
        finally:
            if close_needed:
                db.close()

    def get_refresh_token_by_hash(
        self,
        token_hash: str,
        session: Optional[Session] = None
    ) -> Optional[RefreshToken]:
        """Find a refresh token DB record by its SHA-256 hash string."""
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            return db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        except Exception:
            return None
        finally:
            if close_needed:
                db.close()

    def verify_refresh_token(
        self,
        raw_token: str,
        session: Optional[Session] = None
    ) -> Optional[RefreshToken]:
        """
        Verify a presented raw refresh token string.
        Hashes token, finds DB record, and ensures it is active (not revoked, not expired, user exists).

        :param raw_token: Candidate raw refresh token string.
        :return: Valid RefreshToken record instance, or None if invalid/expired/revoked/missing.
        """
        if not raw_token or not isinstance(raw_token, str):
            return None

        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            token_hash = AuthService.hash_refresh_token(raw_token)
            record = self.get_refresh_token_by_hash(token_hash, session=db)

            if record is None or not record.is_valid:
                return None

            # Verify associated user account still exists
            user = self.get_user_by_id(record.user_id, session=db)
            if user is None:
                return None

            return record
        except Exception:
            return None
        finally:
            if close_needed:
                db.close()

    def revoke_refresh_token(
        self,
        token_hash_or_raw: str,
        session: Optional[Session] = None
    ) -> bool:
        """
        Revoke a single refresh token record by token string or token hash.

        :param token_hash_or_raw: Raw refresh token string or SHA-256 token hash string.
        :return: True if successfully revoked, False otherwise.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            # If 64 chars hex string, assume hash; otherwise compute hash from raw token
            if len(token_hash_or_raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in token_hash_or_raw):
                target_hash = token_hash_or_raw
            else:
                target_hash = AuthService.hash_refresh_token(token_hash_or_raw)

            record = db.query(RefreshToken).filter(RefreshToken.token_hash == target_hash).first()
            if record is None:
                return False

            record.revoked_at = datetime.now(timezone.utc)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            if close_needed:
                db.close()

    def revoke_all_user_refresh_tokens(
        self,
        user_id: int,
        session: Optional[Session] = None
    ) -> int:
        """
        Revoke all active refresh tokens for a specified user ID (e.g. on logout-all or security reset).

        :param user_id: Target user ID integer.
        :return: Number of token sessions revoked.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            now = datetime.now(timezone.utc)
            records = db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at == None
            ).all()

            count = len(records)
            for r in records:
                r.revoked_at = now

            db.commit()
            return count
        except Exception:
            db.rollback()
            return 0
        finally:
            if close_needed:
                db.close()

    def update_refresh_token_last_used(
        self,
        token_hash: str,
        session: Optional[Session] = None
    ) -> bool:
        """Update last_used_at timestamp for a refresh token session."""
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
            if record is None:
                return False

            record.last_used_at = datetime.now(timezone.utc)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            if close_needed:
                db.close()

    def revoke_refresh_token_family(
        self,
        family_id: str,
        session: Optional[Session] = None
    ) -> int:
        """
        Revoke all refresh tokens belonging to a family rotation chain (used for replay attack mitigation).

        :param family_id: Family identifier string.
        :return: Count of revoked token records.
        """
        if not family_id or not isinstance(family_id, str):
            return 0

        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            now = datetime.now(timezone.utc)
            records = db.query(RefreshToken).filter(
                RefreshToken.family_id == family_id,
                RefreshToken.revoked_at == None
            ).all()

            count = len(records)
            for r in records:
                r.revoked_at = now

            db.commit()
            return count
        except Exception:
            db.rollback()
            return 0
        finally:
            if close_needed:
                db.close()

    def rotate_refresh_token(
        self,
        raw_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        session: Optional[Session] = None
    ) -> Tuple[Optional[str], Optional[RefreshToken], Optional[str]]:
        """
        Execute single-use refresh token rotation with replay protection and family revocation.

        :param raw_token: Client-provided raw refresh token string.
        :param user_agent: Optional client browser User-Agent header.
        :param ip_address: Optional client IP address string.
        :return: Tuple of (new_raw_refresh_token, new_RefreshToken_model, error_detail_string).
        """
        if not raw_token or not isinstance(raw_token, str):
            return None, None, "Invalid or expired refresh token"

        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            token_hash = AuthService.hash_refresh_token(raw_token)
            old_record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

            if old_record is None:
                return None, None, "Invalid or expired refresh token"

            # Replay protection: if token is already revoked, revoke the entire token family
            if old_record.is_revoked:
                if old_record.family_id:
                    now = datetime.now(timezone.utc)
                    db.query(RefreshToken).filter(
                        RefreshToken.family_id == old_record.family_id,
                        RefreshToken.revoked_at == None
                    ).update({"revoked_at": now}, synchronize_session=False)
                    db.commit()
                return None, None, "Invalid or expired refresh token"

            if old_record.is_expired:
                return None, None, "Invalid or expired refresh token"

            # Verify associated user account still exists
            user = db.query(User).filter(User.id == old_record.user_id).first()
            if user is None:
                return None, None, "Invalid or expired refresh token"

            now = datetime.now(timezone.utc)
            # 1. Revoke old token
            old_record.revoked_at = now

            # 2. Issue new refresh token in same family
            family = old_record.family_id or old_record.token_hash
            new_raw_token = AuthService.generate_refresh_token()
            new_hash = AuthService.hash_refresh_token(new_raw_token)
            expires_at = now + timedelta(days=AuthService.REFRESH_TOKEN_EXPIRE_DAYS)

            new_record = RefreshToken(
                user_id=old_record.user_id,
                token_hash=new_hash,
                family_id=family,
                user_agent=user_agent or old_record.user_agent,
                ip_address=ip_address or old_record.ip_address,
                expires_at=expires_at,
                created_at=now
            )
            db.add(new_record)
            db.flush()

            # 3. Link old token to replacement token ID
            old_record.replaced_by_id = new_record.id

            db.commit()
            db.refresh(new_record)

            return new_raw_token, new_record, None
        except Exception:
            db.rollback()
            return None, None, "Invalid or expired refresh token"
        finally:
            if close_needed:
                db.close()
