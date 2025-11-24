import pytest
from app.exceptions import ValidationError, NotFoundError
from app.services.interview_service import InterviewService


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
           
    class MockMessageRepo:
        def __init__(self):
            self.messages = []
            self.count_by_role = {"assistant": 0, "user": 0}

        def create_message(self, session_id, role, content):
            self.messages.append({"session_id": session_id, "role": role, "content": content})
            if role in self.count_by_role:
                self.count_by_role[role] += 1

        def count_messages(self, session_id, role=None):
            if role:
                return self.count_by_role.get(role, 0)
            return len(self.messages)

        def conversation_to_history(self, session_id):
            return [{"role": m["role"], "content": m["content"]} for m in self.messages]
        
    class MockAIClient:
        def __init__(self):
            self.first_called = False
            self.followup_called = False

        def generate_first_question(self, **kwargs):
            self.first_called = True
            return "What is your greatest strength?"

        def generate_followup_question(self, **kwargs):
            self.followup_called = True
            return "Tell me about a challenge you faced at work."
        
    return MockSessionRepo(), MockMessageRepo(), MockAIClient()


@pytest.fixture
def interview_service(mock_dependencies):
    session_repo, message_repo, ai_client = mock_dependencies
    return InterviewService(session_repo, message_repo, ai_client)


class TestInterviewService:

    def test_start_interview_success(self, interview_service, mock_dependencies):
        _, msg_repo, ai_client = mock_dependencies

        question = interview_service.start_interview(1)

        assert question == "What is your greatest strength?"
        assert ai_client.first_called
        assert len(msg_repo.messages) == 1
        assert msg_repo.messages[0]["role"] == "assistant"

    def test_start_interview_session_not_found(self, interview_service):
        with pytest.raises(NotFoundError):
            interview_service.start_interview(999)

    def test_start_interview_not_ready(self, interview_service, mock_dependencies):
        session_repo, _, _ = mock_dependencies
        session_repo.sessions[1].cv_text = None

        with pytest.raises(ValidationError, match="Session is not ready"):
            interview_service.start_interview(1)

    def test_start_interview_already_started(self, interview_service, mock_dependencies):
        _, msg_repo, _ = mock_dependencies
        msg_repo.count_messages = lambda session_id: 1

        with pytest.raises(ValidationError, match="already started"):
            interview_service.start_interview(1)

    def test_submit_answer_success(self, interview_service, mock_dependencies):
        _, msg_repo, ai_client = mock_dependencies

        result = interview_service.submit_answer(1, "My strength is problem solving")

        assert ai_client.followup_called
        assert not result["is_complete"]
        assert result["question_count"] == 1
        assert msg_repo.messages[0]["role"] == "user"
        assert msg_repo.messages[-1]["role"] == "assistant"

    def test_submit_answer_empty(self, interview_service):
        with pytest.raises(ValidationError, match="cannot be empty"):
            interview_service.submit_answer(1, "   ")

    def test_submit_answer_complete_interview(self, interview_service, mock_dependencies):
        _, msg_repo, ai_client = mock_dependencies
        msg_repo.count_by_role["assistant"] = 8

        result = interview_service.submit_answer(1, "final answer")

        assert result["is_complete"]
        assert result["next_question"] is None
        assert not ai_client.followup_called

    def test_is_interview_complete_true(self, interview_service, mock_dependencies):
        _, msg_repo, _ = mock_dependencies
        msg_repo.count_by_role["assistant"] = 8

        assert interview_service.is_interview_complete(1) is True

    def test_is_interview_complete_false(self, interview_service, mock_dependencies):
        _, msg_repo, _ = mock_dependencies
        msg_repo.count_by_role["assistant"] = 3

        assert interview_service.is_interview_complete(1) is False

    def test_get_interview_progress(self, interview_service, mock_dependencies):
        _, msg_repo, _ = mock_dependencies
        msg_repo.count_by_role["assistant"] = 5

        progress = interview_service.get_interview_progress(1)

        assert progress["question_count"] == 5
        assert progress["is_started"]
        assert not progress["is_complete"]
        assert progress["max_questions"] == interview_service.MAX_QUESTIONS