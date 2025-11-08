from repositories import FileRepository, SessionRepository
from utils.document_parser import DocumentParser
from models import Session
from exceptions import ValidationError, NotFoundError


class DocumentService:
    def __init__(
            self,
            session_repository: SessionRepository,
            file_repository: FileRepository
    ):
        self.session_repo = session_repository
        self.file_repo = file_repository

    def upload_cv(self, session_id: int, file) -> Session:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")
        
        file_path = self.file_repo.save_uploaded_file(file)

        try:
            cv_text = DocumentParser.extract_text(file_path)
            if not cv_text or len(cv_text.strip()) < 50:
                raise ValidationError(
                    "CV seems too short. Please upload a complete CV "
                    "(at least 50 characters)"
                )
            updated_session = self.session_repo.update_cv_text(session_id, cv_text)
            
            return updated_session
        finally:
            self.file_repo.delete_file(file_path)


    def upload_job_description(self, session_id: int, text: str) -> Session:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")
        
        text = text.strip()
        
        if not text:
            raise ValidationError("Job description cannot be empty")
        
        if len(text) < 50:
            raise ValidationError(
                "Job description seems too short. "
                "Please provide a complete job description (at least 50 characters)"
            )
        
        if len(text) > 10000:
            raise ValidationError(
                "Job description too long (max 10,000 characters)"
            )
        
        updated_session = self.session_repo.update_job_description(session_id, text)
        
        return updated_session