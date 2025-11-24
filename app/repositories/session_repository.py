from app.models import db, Session
from app.exceptions import NotFoundError


class SessionRepository:
    """Handles all database operations for Session model"""

    def create(
        self, job_title: str, company_name: str, user_id: int | None = None
    ) -> Session:
        """Create a new interview session"""
        session = Session(
            job_title=job_title, company_name=company_name, user_id=user_id
        )
        db.session.add(session)
        db.session.commit()
        db.session.refresh(session)
        return session

    def get_by_id(self, session_id: int) -> Session | None:
        return Session.query.get(session_id)

    def update_cv_text(self, session_id: int, cv_text: str) -> Session:
        session = Session.query.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        session.cv_text = cv_text
        db.session.commit()
        return session

    def update_job_description(self, session_id: int, job_description: str) -> Session:
        session = Session.query.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        session.job_description_text = job_description
        db.session.commit()
        return session

    def get_by_ids(self, session_ids: list[int]) -> list[Session]:
        if not session_ids:
            return []

        return (
            Session.query.filter(Session.id.in_(session_ids))
            .options(db.joinedload(Session.messages), db.joinedload(Session.feedback))
            .order_by(Session.created_at.desc())
            .all()
        )

    def get_all(self) -> list[Session]:
        return (
            Session.query.options(
                db.joinedload(Session.messages), db.joinedload(Session.feedback)
            )
            .order_by(Session.created_at.desc())
            .all()
        )

    def delete(self, session_id: int) -> None:
        session = Session.query.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        db.session.delete(session)
        db.session.commit()

    def get_session_with_messages(self, session_id: int) -> Session | None:
        return Session.query.options(db.joinedload(Session.messages)).get(session_id)

    def get_session_with_feedback(self, session_id: int) -> Session | None:
        return Session.query.options(db.joinedload(Session.feedback)).get(session_id)
