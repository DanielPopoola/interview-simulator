# 📚 Interview Simulator - Technical Documentation

> Comprehensive technical guide for developers, maintainers, and contributors

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Patterns](#design-patterns)
3. [Service Layer Details](#service-layer-details)
4. [Repository Layer](#repository-layer)
5. [AI Integration](#ai-integration)
6. [Database Design](#database-design)
7. [Frontend Architecture](#frontend-architecture)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Guide](#deployment-guide)
11. [Performance Considerations](#performance-considerations)
12. [Security Best Practices](#security-best-practices)

---

## Architecture Overview

### Layered Architecture Pattern

The application follows a **clean architecture** approach with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│              Presentation Layer                  │
│  • Flask Routes (app.py)                        │
│  • Templates (Jinja2 + HTMX)                    │
│  • Request/Response handling                     │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│              Business Logic Layer                │
│  • Services (orchestration)                      │
│  • Domain logic                                  │
│  • Validation                                    │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│              Data Access Layer                   │
│  • Repositories (CRUD operations)                │
│  • Database abstraction                          │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│              Infrastructure Layer                │
│  • SQLAlchemy ORM                                │
│  • File system operations                        │
│  • External API clients                          │
└─────────────────────────────────────────────────┘
```

### Why This Architecture?

**Benefits:**
- **Testability**: Each layer can be tested independently with mocks
- **Maintainability**: Changes in one layer don't ripple through others
- **Scalability**: Easy to add new features or swap implementations
- **Clear Dependencies**: Dependencies flow downward (presentation → business → data)

**Example Flow:**
```python
# 1. Route receives request
@app.route('/session/<id>/upload-cv', methods=['POST'])
def upload_cv(session_id):
    file = request.files.get('cv_file')
    
    # 2. Service orchestrates business logic
    document_service.upload_cv(session_id, file)
    
    # 3. Service uses repositories for data access
    # 4. Repositories use SQLAlchemy for database operations
```

---

## Design Patterns

### 1. Repository Pattern

**What**: Abstracts data access logic from business logic

**Why**: 
- Makes code testable (can mock repositories)
- Centralizes database queries
- Easy to switch databases

**Example:**

```python
# repositories/session_repository.py
class SessionRepository:
    def get_by_id(self, session_id: int) -> Session | None:
        return Session.query.get(session_id)
    
    def create(self, job_title: str, company_name: str) -> Session:
        session = Session(job_title=job_title, company_name=company_name)
        db.session.add(session)
        db.session.commit()
        return session
```

**Testing Benefit:**
```python
# In tests, we can mock the repository
class MockSessionRepository:
    def get_by_id(self, session_id):
        return MockSession(id=session_id)
```

### 2. Service Layer Pattern

**What**: Contains business logic and orchestrates operations

**Why**:
- Keeps routes thin and focused on HTTP concerns
- Reusable business logic
- Single place for validation and rules

**Example:**

```python
# services/document_service.py
class DocumentService:
    def upload_cv(self, session_id: int, file) -> Session:
        # 1. Validate session exists
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError()
        
        # 2. Save file temporarily
        file_path = self.file_repo.save_uploaded_file(file)
        
        try:
            # 3. Extract text
            cv_text = DocumentParser.extract_text(file_path)
            
            # 4. Validate content
            if len(cv_text) < 50:
                raise ValidationError("CV too short")
            
            # 5. Update session
            return self.session_repo.update_cv_text(session_id, cv_text)
        finally:
            # 6. Always cleanup
            self.file_repo.delete_file(file_path)
```

### 3. Dependency Injection

**What**: Pass dependencies to objects rather than creating them internally

**Why**:
- Testable (inject mocks)
- Flexible (swap implementations)
- Clear dependencies

**Example:**

```python
# app.py - Wire up dependencies
session_repo = SessionRepository()
message_repo = MessageRepository()
ai_client = AIClient(GeminiProvider(api_key))

interview_service = InterviewService(
    session_repository=session_repo,
    message_repository=message_repo,
    ai_client=ai_client
)
```

### 4. Provider/Strategy Pattern (AI Client)

**What**: Define interface for interchangeable implementations

**Why**:
- Can switch from Gemini to OpenAI easily
- Add new providers without changing existing code

**Example:**

```python
# client/ai_provider.py - Protocol (interface)
class AIProvider(Protocol):
    def generate_text(self, prompt: str) -> str:
        ...

# client/gemini_provider.py - Implementation
class GeminiProvider:
    def generate_text(self, prompt: str) -> str:
        return self.client.models.generate_content(...)

# Easy to add new provider:
class OpenAIProvider:
    def generate_text(self, prompt: str) -> str:
        return openai.ChatCompletion.create(...)
```

---

## Service Layer Details

### SessionService

**Responsibility**: Manage interview session lifecycle

**Key Methods:**

```python
def create_session(self, job_title: str, company_name: str) -> Session:
    """
    Create new interview session with validation
    
    Validates:
    - Non-empty fields
    - Maximum length constraints
    
    Returns: New session object
    """
    
def is_ready_for_interview(self, session_id: int) -> bool:
    """
    Check if session has CV and job description uploaded
    Used to guard interview route
    """
```

**Design Choice**: Session service has minimal dependencies (only SessionRepository) because session creation is simple. More complex services need multiple repositories.

### DocumentService

**Responsibility**: Handle file uploads and text extraction

**Key Methods:**

```python
def upload_cv(self, session_id: int, file) -> Session:
    """
    1. Validate file type (PDF, DOCX, TXT)
    2. Save temporarily
    3. Extract text
    4. Validate extracted content
    5. Store in database
    6. Cleanup temp file
    
    Uses try-finally to ensure cleanup even on errors
    """
```

**Design Choice**: Always cleanup temp files using `try-finally`. This prevents disk space leaks even when exceptions occur.

### InterviewService

**Responsibility**: Orchestrate interview conversation flow

**Key Concept - Question Limits:**

```python
MAX_QUESTIONS = 8

def submit_answer(self, session_id: int, answer: str) -> dict:
    # Save user's answer
    self.message_repo.create_message(session_id, "user", answer)
    
    # Count how many questions asked so far
    question_count = self.message_repo.count_messages(session_id, role='assistant')
    
    # If reached limit, mark complete
    if question_count >= self.MAX_QUESTIONS:
        return {'is_complete': True, 'next_question': None}
    
    # Otherwise, generate next question
    next_question = self.ai_client.generate_followup_question(...)
    
    return {'is_complete': False, 'next_question': next_question}
```

**Why Track Question Count?**
- Prevents infinite interviews
- Provides clear progress to user
- Limits API costs

### FeedbackService

**Responsibility**: Generate and retrieve interview feedback

**Key Method:**

```python
def generate_feedback(self, session_id: int) -> Feedback:
    # 1. Validate session exists
    # 2. Check feedback not already generated (prevent duplicates)
    # 3. Get conversation history
    # 4. Call AI for analysis
    # 5. Store results
    # 6. Return feedback object
```

**Design Choice**: One feedback per session. This prevents accidental regeneration which could cost API calls and confuse users.

---

## Repository Layer

### Why Repositories?

Repositories abstract away SQLAlchemy details. Services don't need to know about `db.session.commit()` or query syntax.

**Benefits:**
- Easier testing (mock repositories, not SQLAlchemy)
- Centralized query logic
- Can switch ORMs if needed

### SessionRepository

**Common Patterns:**

```python
def get_by_id(self, session_id: int) -> Session | None:
    """
    Simple lookup - may return None
    Service decides how to handle missing sessions
    """
    return Session.query.get(session_id)

def update_cv_text(self, session_id: int, cv_text: str) -> Session:
    """
    Update and commit in one operation
    Raises NotFoundError if session missing
    """
    session = Session.query.get(session_id)
    if not session:
        raise NotFoundError(f"Session {session_id} not found")
    
    session.cv_text = cv_text
    db.session.commit()
    return session
```

**Design Choice**: Repository methods are atomic - they commit changes. This keeps services simple and prevents forgetting to commit.

### MessageRepository

**Bulk Operations:**

```python
def create_messages_bulk(self, session_id: int, messages: list[dict]):
    """
    Efficient bulk insert for multiple messages
    Useful if we need to seed conversations
    """
    new_messages = [Message(session_id=session_id, **msg) for msg in messages]
    db.session.bulk_save_objects(new_messages)
    db.session.commit()
```

**Conversation History:**

```python
def conversation_to_history(self, session_id: int) -> list[dict]:
    """
    Convert database messages to format AI expects
    
    Database: [Message(role='user', content='...'), ...]
    AI Format: [{'role': 'user', 'content': '...'}, ...]
    """
    messages = self.get_conversation(session_id)
    return [{"role": m.role, "content": m.content} for m in messages]
```

---

## AI Integration

### Architecture

```
AIClient (high-level interface)
    ↓
AIProvider (protocol/interface)
    ↓
GeminiProvider (implementation)
```

### AIClient

**Purpose**: High-level methods that handle prompt building and response parsing

```python
class AIClient:
    def generate_first_question(self, cv_text, job_desc, job_title, company_name):
        # 1. Build prompt using template
        prompt = PromptTemplates.first_question_generation(...)
        
        # 2. Call provider
        text = self.provider.generate_text(prompt)
        
        # 3. Clean response (remove "Question:" prefix, etc.)
        question = self._clean_question(text)
        
        return question
```

### Prompt Engineering

**First Question Template:**

```python
"""
You are an experienced interviewer starting an interview for {job_title} at {company_name}.

CANDIDATE'S CV:
{cv_text[:2000]}

JOB DESCRIPTION:
{job_description[:2000]}

Your task: Generate ONE opening question to start the interview.

This should be:
- A warm, professional opener
- Related to their most relevant experience
- Encouraging and conversational

Return ONLY the question text.
"""
```

**Why This Format?**
- Clear role definition helps AI understand context
- Truncation ([:2000]) prevents token limits
- Specific instructions ("ONE question", "ONLY text") reduce parsing errors
- Bullet points guide AI behavior

### Retry Logic

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
def generate_text(self, prompt: str) -> str:
    # API call here
```

**Why Retry?**
- Networks fail
- APIs have temporary issues
- Exponential backoff prevents overwhelming server

**Exponential Backoff:**
- 1st retry: wait 2 seconds
- 2nd retry: wait 4 seconds  
- 3rd retry: wait 8 seconds (max 10)

### Response Parsing

**Challenge**: AI sometimes returns JSON wrapped in markdown:

```
```json
{"score": 8, "strengths": "..."}
```
```

**Solution**:

```python
def _parse_json(self, text: str):
    # 1. Remove markdown fences
    text = re.sub(r'```json\s*|```', '', text)
    
    # 2. Find JSON structure
    match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
    
    # 3. Parse
    data = json.loads(match.group(0))
    
    return data
```

---

## Database Design

### Schema Relationships

```
users (1) ──────── (many) sessions
                      │
                      ├───── (many) messages
                      │
                      └───── (one) feedback
```

### Key Design Decisions

**1. Storing CV as Text (not file path)**

```python
class Session(db.Model):
    cv_text = db.Column(db.Text, nullable=True)
```

**Why?**
- No file management issues (lost files, backups)
- Easy database queries (search CV content)
- Simpler deployment (no file storage setup)

**Trade-off**: Large CVs increase database size, but text compresses well.

**2. Cascade Deletes**

```python
class Session(db.Model):
    messages = db.relationship('Message', cascade='all, delete-orphan')
```

**Why?**
- Deleting session auto-deletes related messages
- Prevents orphaned records
- Database stays clean

**3. Nullable user_id**

```python
class Session(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
```

**Why?**
- MVP doesn't require authentication
- Sessions work without user accounts
- Easy to add auth later (make it non-nullable)

### Indexes (Future Optimization)

For production, add:

```python
class Session(db.Model):
    # Index on created_at for "recent sessions" queries
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    
    # Index on user_id for "user's sessions" queries  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
```

---

## Frontend Architecture

### HTMX Pattern

**Traditional Approach (with React):**

```javascript
// 1. User submits form
// 2. JavaScript prevents default
// 3. JavaScript makes fetch() call
// 4. JavaScript updates DOM
// 5. Manage state in React
```

**HTMX Approach:**

```html
<!-- Server returns HTML, HTMX updates DOM -->
<form hx-post="/session/123/message" 
      hx-target="#chat-container" 
      hx-swap="beforeend">
    <textarea name="answer"></textarea>
    <button>Send</button>
</form>
```

**Flow:**
1. User submits form
2. HTMX intercepts, makes AJAX request
3. Server returns HTML fragment
4. HTMX inserts HTML into `#chat-container`

**Benefits:**
- Zero JavaScript to write
- Server controls UI logic
- Progressive enhancement (works without JS)

### Out-of-Band Updates

**Problem**: How to update multiple parts of page from one request?

```html
<!-- Fragment returned by server -->
<div id="new-message">...</div>

<!-- Also update progress bar -->
<div id="progress-bar" hx-swap-oob="true">
    <!-- Updated progress HTML -->
</div>
```

**`hx-swap-oob="true"`** tells HTMX: "Don't insert this where the request came from, update the element with matching ID instead"

**Use Case**: When submitting answer:
- Add new messages to chat
- Update progress counter
- Update progress bar
- Show "complete" button if finished

All from one server response!

### Loading Indicators

```html
<form hx-indicator="#loading-indicator">
    <!-- Form fields -->
</form>

<div id="loading-indicator" class="htmx-indicator">
    Loading...
</div>
```

**How it works:**
- HTMX adds `htmx-request` class during request
- CSS shows indicator: `.htmx-indicator.htmx-request { display: block; }`

---

## Error Handling

### Custom Exception Hierarchy

```python
InterviewSimulatorException (base)
    ├── ValidationError (user input errors)
    ├── NotFoundError (resource doesn't exist)
    ├── DocumentParsingError (file parsing fails)
    └── AIServiceError (AI API issues)
```

**Why Hierarchy?**
- Catch all app errors: `except InterviewSimulatorException`
- Specific handling: `except ValidationError`
- Clear error types in code

### Error Handling in Routes

```python
@app.route('/session/<id>/upload-cv', methods=['POST'])
def upload_cv(session_id):
    try:
        file = request.files.get('cv_file')
        document_service.upload_cv(session_id, file)
        flash("✓ CV uploaded successfully!", "success")
    
    except ValidationError as e:
        flash(str(e), "error")  # User-friendly message
    
    except DocumentParsingError as e:
        flash(f"Could not read file: {e}", "error")
    
    except NotFoundError:
        flash("Session not found", "error")
        return redirect(url_for('index'))
    
    except Exception as e:
        # Unexpected errors - log but don't expose details
        print(f"Error: {e}")
        flash("An error occurred", "error")
    
    return redirect(url_for('upload_page', session_id=session_id))
```

**Pattern:**
1. Specific exceptions first (ValidationError)
2. General exceptions last (Exception)
3. User sees friendly messages
4. Developers see stack traces in logs

### Validation Locations

**Service Layer (Business Rules):**
```python
if len(cv_text) < 50:
    raise ValidationError("CV too short")
```

**Repository Layer (Data Integrity):**
```python
if role not in ['assistant', 'user']:
    raise ValidationError("Invalid role")
```

**Route Layer (HTTP Concerns):**
```python
if not file or not file.filename:
    raise ValidationError("No file provided")
```

---

## Testing Strategy

### Unit Testing Services

**Why Mock Repositories?**
- Test business logic in isolation
- Fast tests (no database)
- Predictable test data

**Example:**

```python
@pytest.fixture
def mock_session_repo():
    class MockSessionRepository:
        def __init__(self):
            self.sessions = {1: MockSession()}
        
        def get_by_id(self, session_id):
            return self.sessions.get(session_id)
    
    return MockSessionRepository()

def test_create_session_validates_empty_title(session_service):
    with pytest.raises(ValidationError, match="cannot be empty"):
        session_service.create_session("", "Google")
```

### Test Organization

```
tests/
├── test_document_parser.py      # Unit tests for parser
├── test_document_service.py     # Service with mocked repos
├── test_interview_service.py    # Service with mocked repos
├── test_feedback_service.py     # Service with mocked repos
└── test_session_service.py      # Service with mocked repos
```

**Philosophy**: Test each layer independently

### Coverage Goals

- **Services**: 90%+ coverage (core business logic)
- **Repositories**: Integration tests with real DB
- **Utilities**: 95%+ coverage (pure functions)

---

## Deployment Guide

### Production Checklist

**Environment Setup:**

```bash
# Required environment variables
GEMINI_API_KEY=your_production_api_key
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=postgresql://user:pass@host:5432/dbname
FLASK_ENV=production
```

**Database Migration (SQLite → PostgreSQL):**

```python
# 1. Install psycopg2
pip install psycopg2-binary

# 2. Update DATABASE_URL in .env
DATABASE_URL=postgresql://...

# 3. Create tables
flask shell
>>> from app import db
>>> db.create_all()

# 4. Migrate data (if needed)
# Export from SQLite, import to PostgreSQL
```

### Docker Deployment

**Production Dockerfile:**

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with gunicorn (production WSGI server)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**Why Gunicorn?**
- Production-ready WSGI server
- Multiple worker processes (handles concurrency)
- Better performance than Flask dev server

### Monitoring

**Key Metrics to Track:**

1. **API Costs**: Log all AI API calls
2. **Response Times**: Track slow endpoints
3. **Error Rates**: Monitor exception frequencies
4. **Database Size**: Track growth (CV texts)

```python
# Add logging
import logging
logging.basicConfig(level=logging.INFO)

@ai_provider.generate_text()
def generate_text(self, prompt):
    logging.info(f"AI API call - prompt length: {len(prompt)}")
    # ... API call
    logging.info(f"AI API response - tokens: {response.usage.tokens}")
```

---

## Performance Considerations

### Database Query Optimization

**Problem**: N+1 queries when loading sessions with messages

**Bad:**
```python
sessions = Session.query.all()
for session in sessions:
    # This triggers a separate query for each session!
    message_count = len(session.messages)
```

**Good:**
```python
# Use joinedload to fetch messages in one query
sessions = Session.query.options(
    db.joinedload(Session.messages)
).all()
```

### AI API Cost Management

**Token Usage:**
- First question: ~500 tokens
- Follow-up: ~800 tokens (includes history)
- Feedback: ~1500 tokens

**Cost Reduction Strategies:**

1. **Truncate Context:**
   ```python
   cv_text[:2000]  # Only send first 2000 chars
   ```

2. **Cache Common Questions:**
   ```python
   # Could cache generic openers by job_title
   CACHED_OPENERS = {
       "Software Engineer": "Tell me about your recent projects..."
   }
   ```

3. **Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, key_func=get_session_id)
   
   @app.route('/session/<id>/message')
   @limiter.limit("10 per minute")  # Prevent abuse
   def send_message():
       ...
   ```

### File Upload Optimization

**Current**: Save → Parse → Delete

**Optimization**: Stream parsing (don't save to disk)

```python
from io import BytesIO

def upload_cv(self, session_id, file):
    # Parse directly from memory
    file_bytes = BytesIO(file.read())
    cv_text = DocumentParser.extract_text_from_stream(file_bytes)
    # No file cleanup needed!
```

---

## Security Best Practices

### 1. Session Ownership

**Current Implementation:**

```python
def check_session_ownership(session_id):
    my_sessions = flask_session.get('my_sessions', [])
    if session_id not in my_sessions:
        abort(403)
```

**Why?**: Prevents users from accessing other users' sessions even without authentication.

### 2. File Upload Security

**Validations:**

```python
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Secure filename (removes path traversal attempts)
from werkzeug.utils import secure_filename
filename = secure_filename(file.filename)
```

### 3. Input Sanitization

**SQL Injection**: Prevented by SQLAlchemy ORM (uses parameterized queries)

**XSS Prevention**: Jinja2 auto-escapes HTML by default

```html
<!-- Safe - Jinja2 escapes user input -->
<p>{{ user_input }}</p>

<!-- Unsafe - only use with trusted data -->
<p>{{ user_input | safe }}</p>
```

### 4. Environment Variables

**Never commit:**
- API keys
- Secret keys
- Database passwords

**Use `.env` file:**
```bash
# .gitignore should include:
.env
```

### 5. Rate Limiting (Future)

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.headers.get('X-Real-IP', request.remote_addr),
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/session/<id>/message')
@limiter.limit("20 per minute")  # Specific endpoint limit
def send_message():
    ...
```

---

## Future Enhancements

### Phase 2 Features

1. **User Authentication**
   - Add login/signup
   - Make user_id non-nullable
   - Personal interview history

2. **Advanced Feedback**
   - Compare against other candidates
   - Industry-specific benchmarks
   - Video recording support

3. **Resume Builder**
   - Generate optimized CVs from feedback
   - Template system
   - Export to PDF

4. **Interview Types**
   - Technical (coding challenges)
   - Behavioral
   - Case studies

### Scaling Considerations

**When to Scale:**
- \>1000 active users
- \>10,000 sessions per day
- Database \>10GB

**Scaling Strategies:**

1. **Database**: Move to PostgreSQL with read replicas
2. **Caching**: Add Redis for session data
3. **Background Jobs**: Use Celery for AI calls
4. **CDN**: Serve static files from CDN
5. **Load Balancing**: Multiple app instances

---

## Troubleshooting

### Common Issues

**1. "AI returned empty response"**

**Cause**: API timeout or rate limit

**Solution**:
- Check API key validity
- Verify internet connection
- Check Gemini API status

**2. "Could not parse PDF"**

**Cause**: Encrypted or image-based PDF

**Solution**:
- Ask user to try DOCX or TXT
- Add OCR support (future)

**3. "Session not found"**

**Cause**: User cleared cookies (lost session tracking)

**Solution**:
- Add user authentication
- Or accept it as MVP limitation

**4. Database locked (SQLite)**

**Cause**: Multiple writes at once

**Solution**:
- Upgrade to PostgreSQL for production
- Or add write-ahead logging:
  ```python
  db.session.execute("PRAGMA journal_mode=WAL")
  ```

---

## Appendix

### Glossary

- **Session**: An interview preparation instance (one job, one CV)
- **Message**: A single turn in interview conversation (question or answer)
- **Feedback**: Analysis and CV suggestions after interview
- **Repository**: Data access layer object
- **Service**: Business logic layer object

### Useful Commands

```bash
# Run development server
python app.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=services --cov=utils

# Lint code
ruff check .

# Auto-fix linting
ruff check . --fix

# Create database tables
flask shell
>>> from app import db
>>> db.create_all()

# Export database
sqlite3 instance/app.db .dump > backup.sql
```

### Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Gemini API Reference](https://ai.google.dev/docs)

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Maintainer**: [Daniel Popoola]