from client.ai_client import AIClient
from models import Feedback
from repositories import FeedbackRepository, MessageRepository, SessionRepository
from exceptions import ValidationError, NotFoundError


class FeedbackService:
    def __init__(
        self,
        session_repository: SessionRepository,
        message_repository: MessageRepository,
        feedback_repository: FeedbackRepository,
        ai_client: AIClient,
    ):
        self.session_repo = session_repository
        self.message_repo = message_repository
        self.feedback_repo = feedback_repository
        self.ai_client = ai_client

    def generate_feedback(self, session_id: int) -> Feedback:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        if self.feedback_repo.has_feedback(session_id):
            raise ValidationError(
                "Feedback has already been generated for this session."
            )

        conversation_history = self.message_repo.conversation_to_history(session_id)
        if not conversation_history:
            raise ValidationError("Cannot generate feedback for an empty interview.")

        feedback_data = self.ai_client.generate_feedback(
            convo_history=conversation_history,
            cv_text=session.cv_text,
            job_desc=session.job_description_text,
            job_title=session.job_title,
        )

        return self.feedback_repo.create_feedback(
            session_id=session_id, **feedback_data
        )

    def get_feedback(self, session_id: int) -> Feedback:
        feedback = self.feedback_repo.get_feedback(session_id)
        if not feedback:
            raise NotFoundError(f"Feedback for session {session_id} not found.")
        return feedback
