import pytest
from exceptions import ValidationError, NotFoundError
from services.feedback_service import FeedbackService


@pytest.fixture
def mock_dependencies():
    class MockSession:
        def __init__(self, id=1, job_title="Engineer", company_name="Google",
                     cv_text="valid cv", job_description_text="valid description"):
            self.id = id
            self.job_title = job_title
            self.company_name = company_name
            self.cv_text = cv_text
            self.job_description_text = job_description_text

    class MockSessionRepo:
        def __init__(self) -> None:
            self.sessions = {1: MockSession()}

        def get_by_id(self, session_id):
            return self.sessions.get(session_id)

    class MockFeedbackRepo:
        def __init__(self):
            self.existing_feedback = set()
            self.created = None
        
        def has_feedback(self, session_id):
            return session_id in self.existing_feedback

        def create_feedback(self, session_id, **kwargs):
            self.created = {"session_id": session_id, **kwargs}
            return self.created
        
        def get_feedback(self, session_id):
            return self.created if self.created and self.created["session_id"] == session_id else None

    class MockMessageRepo:
        def __init__(self):
            self.messages = [{"role": "user", "content": "answer"}]

        def conversation_to_history(self, session_id):
            return self.messages

    class MockAIClient:
        def generate_feedback(self, **kwargs):
            return {
                "score": 8,
                "strengths": "analytical thinking",
                "weaknesses": "over-detailing",
                "cv_improvements": "simplify layout"
            }
    

    return MockSessionRepo(), MockMessageRepo(), MockFeedbackRepo(), MockAIClient()


@pytest.fixture
def feedback_service(mock_dependencies):
    session_repo, message_repo, feedback_repo, ai_client = mock_dependencies
    return FeedbackService(session_repo, message_repo, feedback_repo, ai_client)

class TestFeedbackService:

    def test_generate_feedback_success(self, feedback_service, mock_dependencies):
        _, _, feedback_repo, _ = mock_dependencies

        result = feedback_service.generate_feedback(1)

        assert result["session_id"] == 1
        assert result["score"] == 8
        assert "strengths" in result
        assert feedback_repo.created is not None

    def test_generate_feedback_session_not_found(self, feedback_service, mock_dependencies):
        session_repo, *_ = mock_dependencies
        session_repo.sessions = {}

        with pytest.raises(NotFoundError):
            feedback_service.generate_feedback(99)

    def test_generate_feedback_already_exists(self, feedback_service, mock_dependencies):
        _, _, feedback_repo, _ = mock_dependencies
        feedback_repo.existing_feedback.add(1)

        with pytest.raises(ValidationError, match="already been generated"):
            feedback_service.generate_feedback(1)

    def test_generate_feedback_empty_interview(self, feedback_service, mock_dependencies):
        _, message_repo, _, _ = mock_dependencies
        message_repo.messages = []

        with pytest.raises(ValidationError, match="empty interview"):
            feedback_service.generate_feedback(1)
