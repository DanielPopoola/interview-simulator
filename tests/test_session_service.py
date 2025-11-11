import pytest
from exceptions import ValidationError, NotFoundError
from services.session_service import SessionService


@pytest.fixture
def mock_session_repo():
    class MockSession:
        def __init__(self, id=1, job_title="Engineer", company_name="Google",
                      cv_text=None, 
                      job_description_text=None):
            self.id = id
            self.job_title = job_title
            self.company_name = company_name
            self.cv_text = cv_text
            self.job_description_text = job_description_text
            self.messages = ["msg1"]
            self.feedback = "positive"

    class MockSessionRepository:
        def __init__(self):
            self.sessions = {1: MockSession()}

        def create(self, job_title, company_name, user_id=None):
            return MockSession(job_title=job_title, company_name=company_name)

        def get_by_id(self, session_id):
            return self.sessions.get(session_id)

        def get_all(self):
            return list(self.sessions.values())

        def delete(self, session_id):
            if session_id not in self.sessions:
                raise NotFoundError("Session not found")
            del self.sessions[session_id]

        def get_session_with_messages(self, session_id):
            return self.sessions.get(session_id)

        def get_session_with_feedback(self, session_id):
            return self.sessions.get(session_id)

    return MockSessionRepository()


@pytest.fixture
def session_service(mock_session_repo):
    return SessionService(mock_session_repo)


class TestSessionService:
    def test_create_session_with_valid_data(self, session_service):
        session = session_service.create_session("Software Engineer", "Google")
        assert session.job_title == "Software Engineer"
        assert session.company_name == "Google"

    def test_create_session_strips_whitespace(self, session_service):
        session = session_service.create_session("  Engineer  ", "  Google  ")
        assert session.job_title == "Engineer"
        assert session.company_name == "Google"

    def test_create_session_with_empty_job_title(self, session_service):
        with pytest.raises(ValidationError, match="Job title cannot be empty"):
            session_service.create_session("", "Google")

    def test_create_session_with_empty_company_name(self, session_service):
        with pytest.raises(ValidationError, match="Company name cannot be empty"):
            session_service.create_session("Engineer", "")

    def test_create_session_with_too_long_job_title(self, session_service):
        with pytest.raises(ValidationError, match="Job title too long"):
            session_service.create_session("x" * 201, "Google")

    # --- RETRIEVE TESTS ---

    def test_get_session_returns_existing(self, session_service):
        session = session_service.get_session(1)
        assert session.job_title == "Engineer"

    def test_get_session_not_found_raises(self, session_service):
        with pytest.raises(NotFoundError, match="not found"):
            session_service.get_session(99)

    def test_get_all_sessions(self, session_service):
        sessions = session_service.get_all_sessions()
        assert len(sessions) == 1
        assert sessions[0].company_name == "Google"

    # --- DELETE TESTS ---

    def test_delete_existing_session(self, session_service, mock_session_repo):
        session_service.delete_session(1)
        assert 1 not in mock_session_repo.sessions

    def test_delete_nonexistent_session_raises(self, session_service):
        with pytest.raises(NotFoundError):
            session_service.delete_session(99)

    # --- READINESS TESTS ---

    def test_is_ready_for_interview_false_initially(self, session_service):
        assert session_service.is_ready_for_interview(1) is False

    def test_is_ready_for_interview_true_when_fields_present(self, session_service, mock_session_repo):
        s = mock_session_repo.sessions[1]
        s.cv_text = "cv"
        s.job_description_text = "desc"
        assert session_service.is_ready_for_interview(1) is True

    # --- FULL DETAILS TESTS ---

    def test_get_full_session_details_success(self, session_service):
        details = session_service.get_full_session_details(1)
        assert "session" in details
        assert details["messages"] == ["msg1"]
        assert details["feedback"] == "positive"

    def test_get_full_session_details_not_found(self, session_service, mock_session_repo):
        mock_session_repo.sessions.pop(1)
        with pytest.raises(NotFoundError, match="not found"):
            session_service.get_full_session_details(1)
