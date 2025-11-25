# 🎯 AI Interview Simulator

An intelligent interview preparation platform that helps job seekers practice interviews with AI-powered feedback and CV optimization suggestions.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **📄 Document Analysis**: Upload your CV (PDF, DOCX, TXT) and job descriptions
- **🤖 AI-Powered Interviews**: Engage in realistic mock interviews with adaptive questioning from multiple AI providers (Gemini, OpenRouter).
- **💡 Smart Feedback**: Receive detailed performance analysis and actionable insights.
- **✨ CV Optimization**: Get specific suggestions to tailor your CV for target roles.
- **📊 Progress Tracking**: Monitor your interview progress with visual indicators.
- **🔒 Session Management**: Resume incomplete sessions anytime.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- An AI provider API key (e.g., Gemini - [Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DanielPopoola/interview-simulator.git
   cd interview-simulator
   ```

2. **Set up environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env and add your API key(s)
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   SECRET_KEY=your_random_secret_key
   DATABASE_URL=sqlite:///instance/app.db
   ```

4. **Run the application**
   ```bash
   flask run
   ```

5. **Open your browser**
   ```
   http://127.0.0.1:5000
   ```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8000
```

## 📖 How It Works

### 1. Create Session
Start by entering the job title and company name you're preparing for.

### 2. Upload Documents
- **CV Upload**: Upload your resume (PDF, DOCX, or TXT format)
- **Job Description**: Paste the full job posting

### 3. Interview Practice
- Answer up to 8 AI-generated questions tailored to your background and the role.
- Questions adapt based on your responses.
- Conversational, natural interview flow.

### 4. Get Feedback
Receive comprehensive analysis including:
- **Performance Score** (1-10)
- **Strengths**: What you did well
- **Areas to Improve**: Specific suggestions
- **CV Optimization**: Tailored recommendations for the role

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Flask Application               │
│  ┌──────────────────────────────────┐  │
│  │     Routes (app/routes)          │  │
│  └──────────┬───────────────────────┘  │
│             ↓                            │
│  ┌──────────────────────────────────┐  │
│  │   Services Layer (app/services)  │  │
│  │  • SessionService                │  │
│  │  • DocumentService               │  │
│  │  • InterviewService              │  │
│  │  • FeedbackService               │  │
│  └──────────┬───────────────────────┘  │
│             ↓                            │
│  ┌──────────────────────────────────┐  │
│  │   Repositories (app/repositories)│  │
│  │  • SessionRepository             │  │
│  │  • MessageRepository             │  │
│  │  • FeedbackRepository            │  │
│  │  • FileRepository                │  │
│  └──────────┬───────────────────────┘  │
│             ↓                            │
│  ┌──────────────────────────────────┐  │
│  │   Data Layer (app/models)        │  │
│  │  • SQLite Database               │  │
│  │  • SQLAlchemy ORM                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │                    │
         ↓                    ↓
   ┌──────────┐        ┌──────────┐
   │ AI Client│        │  HTMX    │
   │(client/) │        │ Frontend │
   └──────────┘        └──────────┘
```

## 🛠️ Tech Stack

### Backend
- **Flask**: Lightweight web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Development database

### AI Integration
- **Google Gemini & OpenRouter**: Powers interview generation and feedback analysis.
- **Provider Pattern**: Easily switch between or add new AI providers.
- **Tenacity**: Retry logic for API reliability.

### Frontend
- **HTMX**: Dynamic interactions without complex JavaScript.
- **Jinja2**: Server-side templating.
- **CSS**: Custom styling with `main.css`.

### Document Processing
- **pdfplumber**: PDF text extraction
- **python-docx**: Word document parsing

## 📁 Project Structure

```
interview-simulator/
├── app/
│   ├── __init__.py               # App factory
│   ├── config.py                 # Configuration
│   ├── models.py                 # Database models
│   ├── exceptions.py             # Custom exceptions
│   ├── services/                 # Business logic
│   ├── repositories/             # Data access
│   └── routes/                   # Flask routes
│
├── client/                     # AI provider abstraction
│   ├── ai_client.py              # Main AI client
│   ├── ai_provider.py            # Provider protocol
│   ├── gemini_provider.py        # Gemini implementation
│   └── openrouter_provider.py    # OpenRouter implementation
│
├── utils/                      # Utility modules
│   ├── document_parser.py        # Document text extraction
│   └── prompt_templates.py       # AI prompt templates
│
├── templates/                  # HTML templates
│   ├── index.html
│   ├── upload.html
│   ├── interview.html
│   ├── feedback.html
│   └── fragments/                # HTMX partial templates
│
├── tests/                      # Pytest test suite
├── wsgi.py                     # WSGI entry point
└── requirements.txt
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_interview_service.py
```

## 🔑 Key Design Decisions

### 1. **Layered Architecture**
- **Services**: Business logic and orchestration.
- **Repositories**: Database abstraction.
- **Separation of Concerns**: Each layer has a single responsibility.

### 2. **HTMX Over React/Vue**
- Server-side rendering keeps logic in Python.
- Minimal JavaScript complexity.
- Fast development with progressive enhancement.

### 3. **Provider Pattern for AI**
- `AIProvider` protocol allows easy switching between AI services.
- Currently supports Gemini and OpenRouter, and is easily extendable.
- Retry logic with exponential backoff.

### 4. **Document Parser Abstraction**
- Single interface for multiple file formats.
- Graceful error handling for corrupted files.

### 5. **Session-Based State**
- Flask sessions track user's interview sessions.
- No authentication required for MVP.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `OPENROUTER_API_KEY` | OpenRouter API key | Optional |
| `ACTIVE_PROVIDERS` | Comma-separated list of active providers | `openrouter,gemini` |
| `SECRET_KEY` | Flask session secret | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///dev.db` |

## 📊 Database Schema

```sql
-- Users (optional, for future auth)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Interview Sessions
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_title VARCHAR(200) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    cv_text TEXT,
    job_description_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Conversation Messages
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    role VARCHAR(20) NOT NULL, -- 'assistant', 'user'
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Feedback Results
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    interview_score INTEGER,
    strengths TEXT,
    weaknesses TEXT,
    cv_improvements TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🚦 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Homepage with recent sessions |
| `POST` | `/session/create` | Create new interview session |
| `GET` | `/session/<id>/upload` | Upload page for CV and job description |
| `POST` | `/session/<id>/upload-cv` | Upload CV file |
| `POST` | `/session/<id>/upload-job` | Submit job description |
| `GET` | `/session/<id>/interview` | Interview interface |
| `POST` | `/session/<id>/message` | Submit interview answer (HTMX) |
| `POST` | `/session/<id>/complete` | Generate feedback |
| `GET` | `/session/<id>/feedback` | View results |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guidelines.
- Write tests for new features.
- Update documentation as needed.
- Run `ruff check .` before committing.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for powering the AI capabilities
- **Flask** community for excellent documentation
- **HTMX** for simplifying frontend interactions

## 📧 Contact

Daniel Popoola - [@iamuchihadan](https://x.com/iamuchihda) - iamuchihdadaniel236@gmail.com

Project Link: [https://github.com/DanielPopoola/interview-simulator](https://github.com/DanielPopoola/interview-simulator)

---

**Built with ❤️ to help job seekers succeed in their interviews**
