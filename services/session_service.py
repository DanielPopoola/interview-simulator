from repositories.session_repository import SessionRepository
from models import Session
from exceptions import  ValidationError, NotFoundError


class SessionService:
    def __init__(self, session_repository: SessionRepository):
        self.session_repo = session_repository
    
    def create_session(self, job_title: str, company_name: str) -> Session:
        if not job_title or not job_title.strip():
            raise ValidationError("Job title cannot be empty")
        
        if not company_name or not company_name.strip():
            raise ValidationError("Company name cannot be empty")
        
        if len(job_title) > 200:
            raise ValidationError("Job title too long (max 200 characters)")
        
        return self.session_repo.create(
            job_title=job_title.strip(),
            company_name=company_name.strip()
        )
    
    def get_session(self, session_id: int) -> Session:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")
        return session
    
    def is_ready_for_interview(self, session_id: int) -> bool:
        session = self.get_session(session_id)
        return bool(session.cv_text and session.job_description_text)

    def get_all_sessions(self) -> list[Session]:
        return self.session_repo.get_all()
    
    def delete_session(self, session_id: int) -> None:
        self.session_repo.delete(session_id)

    def get_sessions_by_ids(self, session_ids: list[int]) -> list[Session]:
        return self.session_repo.get_by_ids(session_ids)
    
    def get_full_session_details(self, session_id: int) -> dict:
        session_with_messages = self.session_repo.get_session_with_messages(session_id)
        if not session_with_messages:
            raise NotFoundError(f"Session {session_id} not found")

        session_with_feedback = self.session_repo.get_session_with_feedback(session_id)
        
        return {
            "session": session_with_messages,
            "messages": session_with_messages.messages,
            "feedback": session_with_feedback.feedback if session_with_feedback else None
        }
