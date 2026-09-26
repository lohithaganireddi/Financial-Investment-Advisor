"""
User Repository Module

Provides database operations for User management and Watchlist persistence.
Encapsulates SQLAlchemy database logic for users and watchlists.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import User, Watchlist
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
