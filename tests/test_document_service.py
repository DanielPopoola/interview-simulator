import pytest
from app.exceptions import ValidationError, NotFoundError
from app.services.document_service import DocumentService


@pytest.fixture
def mock_dependencies(monkeypatch):
    class MockSession:
        def __init__(self, id=1, cv_text=None, job_description_text=None):
            self.id = id
            self.cv_text = cv_text
            self.job_description_text = job_description_text

    class MockSessionRepository:
        def __init__(self):
            self.sessions=  {1: MockSession()}

        def get_by_id(self, session_id):
            return self.sessions.get(session_id)
        
        def update_cv_text(self, session_id, cv_text):
            s = self.sessions.get(session_id)
            if not s:
                raise NotFoundError()
            s.cv_text = cv_text
            return s
        
        def update_job_description(self, session_id, text):
            s = self.sessions.get(session_id)
            if not s:
                raise NotFoundError()
            s.job_description_text = text
            return s
        
    class MockFileRepository:
        def __init__(self):
            self.deleted_files = []
            self.saved_files = []

        def save_uploaded_file(self, file):
            path = f"/tmp/{file.filename}"
            self.saved_files.append(path)
            return path

        def delete_file(self, path):
            self.deleted_files.append(path)

    class MockParser:
        @staticmethod
        def extract_text(path):
            return "A" * 200
        

    monkeypatch.setattr("services.document_service.DocumentParser", MockParser)

    return MockSessionRepository(), MockFileRepository()


@pytest.fixture
def document_service(mock_dependencies):
    session_repo, file_repo = mock_dependencies
    return DocumentService(session_repo, file_repo)


class DummyFile:
    def __init__(self, filename="cv.pdf"):
        self.filename = filename
    def save(self, path):
        pass


class TestDocumentService:
    def test_upload_cv_success(self, document_service, mock_dependencies):
        _, file_repo = mock_dependencies
        file = DummyFile()

        result = document_service.upload_cv(1, file)

        assert result.cv_text.startswith("A")
        assert len(file_repo.deleted_files) == 1
        assert file_repo.saved_files

    def test_upload_cv_session_not_found(self, document_service):
        with pytest.raises(NotFoundError):
            document_service.upload_cv(99, DummyFile())

    def test_upload_cv_invalid_text_short(self, document_service, monkeypatch):
        monkeypatch.setattr("services.document_service.DocumentParser.extract_text", lambda _: "too short")

        with pytest.raises(ValidationError, match="too short"):
            document_service.upload_cv(1, DummyFile())

    def test_upload_cv_always_deletes_file_on_error(self, document_service, mock_dependencies, monkeypatch):
        _, file_repo = mock_dependencies
        monkeypatch.setattr("services.document_service.DocumentParser.extract_text", lambda _: "too short")

        with pytest.raises(ValidationError):
            document_service.upload_cv(1, DummyFile())

        assert len(file_repo.deleted_files) == 1

    def test_upload_job_description_success(self, document_service):
        text = "This is a long enough job description text for testing purposes."
        session = document_service.upload_job_description(1, text)
        assert len(session.job_description_text) >= 50

    def test_upload_job_description_not_found(self, document_service):
        with pytest.raises(NotFoundError):
            document_service.upload_job_description(99, "Valid long description text" * 3)

    def test_upload_job_description_empty_text(self, document_service):
        with pytest.raises(ValidationError, match="cannot be empty"):
            document_service.upload_job_description(1, "   ")

    def test_upload_job_description_too_short(self, document_service):
        with pytest.raises(ValidationError, match="too short"):
            document_service.upload_job_description(1, "short text")

    def test_upload_job_description_too_long(self, document_service):
        text = "x" * 10001
        with pytest.raises(ValidationError, match="too long"):
            document_service.upload_job_description(1, text)