"""
Analysis Repository Module

Provides database operations for persisting and retrieving Analysis records.
Encapsulates SQLAlchemy logic away from API routes.
"""

import json
from typing import Any, List, Optional
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Analysis


class AnalysisRepository:
    """
    Repository for managing Analysis database persistence and queries.
    """

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the AnalysisRepository.
        Supports dependency injection of a custom or mock Session.
        """
        self._external_session = db_session

    def _get_session(self) -> Session:
        """Return the injected session or create a new local session."""
        return self._external_session or SessionLocal()

    def save_analysis(
        self,
        query: str,
        asset_type: str,
        asset: str,
        news_query: Optional[str] = None,
        recommendation: Optional[str] = None,
        recommendation_score: Optional[int] = None,
        confidence: Optional[str] = None,
        risk_score: Optional[int] = None,
        risk_level: Optional[str] = None,
        market_direction: Optional[str] = None,
        news_sentiment: Optional[str] = None,
        agent_activity: Optional[Any] = None,
        user_id: Optional[int] = None,
        session: Optional[Session] = None
    ) -> Optional[Analysis]:
        """
        Save a completed financial analysis to the database.

        :return: Saved Analysis instance, or None if database save fails.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        activity_json = None
        if agent_activity is not None:
            if isinstance(agent_activity, str):
                activity_json = agent_activity
            else:
                try:
                    activity_json = json.dumps(agent_activity)
                except Exception:
                    activity_json = None

        try:
            record = Analysis(
                query=query,
                asset_type=asset_type,
                asset=asset,
                news_query=news_query,
                recommendation=recommendation,
                recommendation_score=recommendation_score,
                confidence=confidence,
                risk_score=risk_score,
                risk_level=risk_level,
                market_direction=market_direction,
                news_sentiment=news_sentiment,
                agent_activity=activity_json,
                user_id=user_id
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
        except Exception as exc:
            db.rollback()
            return None
        finally:
            if close_needed:
                db.close()


    def get_recent_analyses(
        self,
        limit: int = 10,
        user_id: Optional[int] = None,
        session: Optional[Session] = None
    ) -> List[Analysis]:
        """
        Retrieve recent saved financial analyses, ordered newest first.

        :param limit: Number of records to return (default 10, maximum 50).
        :param user_id: Optional integer user ID filter.
        :return: List of Analysis instances.
        """
        clean_limit = max(1, min(limit, 50))
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            query_obj = db.query(Analysis)
            if user_id is not None:
                query_obj = query_obj.filter(Analysis.user_id == user_id)
            records = (
                query_obj
                .order_by(Analysis.created_at.desc(), Analysis.id.desc())
                .limit(clean_limit)
                .all()
            )
            return records
        except Exception:
            return []
        finally:
            if close_needed:
                db.close()

    def get_analysis_by_id(
        self,
        analysis_id: int,
        session: Optional[Session] = None
    ) -> Optional[Analysis]:
        """
        Retrieve a single Analysis record by primary key ID.

        :param analysis_id: Analysis record integer ID.
        :return: Analysis instance if found, or None.
        """
        db = session or self._external_session or SessionLocal()
        close_needed = (session is None and self._external_session is None)

        try:
            record = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            return record
        except Exception:
            return None
        finally:
            if close_needed:
                db.close()
