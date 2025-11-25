# 🎯 AI Interview Simulator

An intelligent interview preparation platform that helps job seekers practice interviews with AI-powered feedback and CV optimization suggestions.

![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **📄 Document Analysis**: Upload your CV (PDF, DOCX, TXT) and job descriptions
- **🤖 AI-Powered Interviews**: Engage in realistic mock interviews with adaptive questioning
- **💡 Smart Feedback**: Receive detailed performance analysis and actionable insights
- **✨ CV Optimization**: Get specific suggestions to tailor your CV for target roles
- **📊 Progress Tracking**: Monitor your interview progress with visual indicators
- **🔒 Session Management**: Resume incomplete sessions anytime

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- Gemini API key ([Get one here](https://ai.google.dev/))

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
   
   # Edit .env and add your API key
   OPENROUTER_API_KEY=your_api_key
   GEMINI_API_KEY=your_api_key_here
   SECRET_KEY=your_random_secret_key
   DATABASE_URL=sqlite:///instance/app.db
   ```

4. **Run the application**
   ```bash
   python app.py

   **OR**

   gunicorn wsgi:app --workers 4
   ```

5. **Open your browser**
   ```
   http://localhost:5000
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
- Answer 8 AI-generated questions tailored to your background and the role
- Questions adapt based on your responses
- Conversational, natural interview flow

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
│  │          Routes                  │  │
│  └──────────┬───────────────────────┘  │
│             ↓                            │
│  ┌──────────────────────────────────┐  │
│  │   Services Layer                 │  │
│  │  • SessionService                │  │
│  │  • DocumentService               │  │
│  │  • InterviewService              │  │
│  │  • FeedbackService               │  │
│  └──────────┬───────────────────────┘  │
│             ↓                            │
│  ┌──────────────────────────────────┐  │
│  │   Repositories Layer             │  │
│  │  • SessionRepository             │  │
│  │  • MessageRepository             │  │
│  │  • FeedbackRepository            │  │
│  │  • FileRepository                │  │
│  └──────────┬───────────────────────┘  │
│             ↓                            │
│  ┌──────────────────────────────────┐  │
│  │   Data Layer                     │  │
│  │  • SQLite Database               │  │
│  │  • SQLAlchemy ORM                │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │                    │
         ↓                    ↓
   ┌──────────┐        ┌──────────┐
   │  Gemini  │        │  HTMX    │
   │   API    │        │ Frontend │
   └──────────┘        └──────────┘
```

## 🛠️ Tech Stack

### Backend
- **Flask**: Lightweight web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Development database (easily upgradeable to PostgreSQL)

### AI Integration
- **Google Gemini API**: Powers interview generation and feedback analysis
- **OpenRouter API**: Additional AI provider for multi-provider support
- **Tenacity**: Retry logic for API reliability

### Frontend
- **HTMX**: Dynamic interactions without complex JavaScript
- **Tailwind CSS**: Utility-first styling
- **Jinja2**: Server-side templating

### Document Processing
- **pdfplumber**: PDF text extraction
- **python-docx**: Word document parsing

## 📁 Project Structure

```
interview-simulator/
├── app.py                      # Main Flask application & routes
├── models.py                   # SQLAlchemy database models
├── exceptions.py               # Custom exception classes
│
├── services/                   # Business logic layer
│   ├── session_service.py
│   ├── document_service.py
│   ├── interview_service.py
│   └── feedback_service.py
│
├── repositories/               # Data access layer
│   ├── session_repository.py
│   ├── message_repository.py
│   ├── feedback_repository.py
│   └── file_repository.py
│
├── client/                     # AI provider abstraction
│   ├── ai_client.py           # Main AI client
│   ├── ai_provider.py         # Provider protocol
│   └── gemini_provider.py     # Gemini implementation
│
├── utils/                      # Utility modules
│   ├── document_parser.py     # Document text extraction
│   └── prompt_templates.py    # AI prompt templates
│
├── templates/                  # HTML templates
│   ├── index.html
│   ├── upload.html
│   ├── interview.html
│   ├── feedback.html
│   └── fragments/             # HTMX partial templates
│
└── tests/                      # Pytest test suite
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov=utils

# Run specific test file
pytest tests/test_interview_service.py
```

## 🔑 Key Design Decisions

### 1. **Layered Architecture**
- **Services**: Business logic and orchestration
- **Repositories**: Database abstraction
- **Separation of Concerns**: Each layer has a single responsibility

### 2. **HTMX Over React/Vue**
- Server-side rendering keeps logic in Python
- Minimal JavaScript complexity
- Fast development with progressive enhancement

### 3. **Provider Pattern for AI**
- `AIProvider` protocol allows easy switching between AI services
- Currently supports Gemini, easily extendable to OpenAI/Anthropic
- Retry logic with exponential backoff

### 4. **Document Parser Abstraction**
- Single interface for multiple file formats
- Graceful error handling for corrupted files
- Fallback encoding support

### 5. **Session-Based State**
- Flask sessions track user's interview sessions
- No authentication required for MVP
- Easy to upgrade to user accounts later

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | *Required* |
| `SECRET_KEY` | Flask session secret | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///instance/app.db` |
| `FLASK_ENV` | Environment mode | `development` |

## 📊 Database Schema

```sql
-- Users (optional, for future auth)
users (id, email, created_at)

-- Interview Sessions
sessions (id, user_id, job_title, company_name, 
          cv_text, job_description_text, created_at)

-- Conversation Messages
messages (id, session_id, role, content, timestamp)

-- Feedback Results
feedback (id, session_id, interview_score, 
          strengths, weaknesses, cv_improvements, created_at)
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
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Run `ruff check .` before committing

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
