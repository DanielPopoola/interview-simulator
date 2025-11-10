from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import db
from repositories import FileRepository, SessionRepository, MessageRepository, FeedbackRepository
from services import DocumentService, InterviewService, SessionService, FeedbackService
from exceptions import (
    ValidationError, 
    NotFoundError, 
    DocumentParsingError, 
    InterviewSimulatorException,
    AIServiceError
)
import os


from client.ai_client import AIClient
from client.gemini_provider import GeminiProvider

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview_simulator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Repositories
session_repository = SessionRepository()
file_repository = FileRepository(app.config['UPLOAD_FOLDER'])
message_repository = MessageRepository()
feedback_repository = FeedbackRepository()

# AI Client
gemini_provider = GeminiProvider(
    api_key=os.getenv('GEMINI_API_KEY', ""),
    model_name='gemini-2.5-flash'
)
ai_client = AIClient(gemini_provider)

# Services
session_service = SessionService(session_repository)
document_service = DocumentService(session_repository, file_repository)
interview_service = InterviewService(session_repository, message_repository, ai_client)
feedback_service = FeedbackService(session_repository, message_repository, feedback_repository, ai_client)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/session/create', methods=['POST'])
def create_session():
    try:
        job_title = request.form.get('job_title', '')
        company_name = request.form.get('company_name', '')
        
        session = session_service.create_session(job_title, company_name)
        
        return redirect(url_for('upload_page', session_id=session.id))
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))
    
    except Exception as e:
        print(f"Error creating session: {e}")
        flash("An error occurred. Please try again.", 'error')
        return redirect(url_for('index'))


@app.route('/session/<int:session_id>/upload')
def upload_page(session_id):
    try:
        session = session_service.get_session(session_id)
        return render_template('upload.html', session=session)
    
    except ValueError:
        abort(404)

@app.route('/session/<int:session_id>/upload-cv', methods=['POST'])
def upload_cv(session_id):
    try:
        file = request.files.get('cv_file')
        
        if not file:
            raise ValidationError("No file was uploaded")
        
        document_service.upload_cv(session_id, file)
        flash("✓ CV uploaded and processed successfully!", "success")
    
    except ValidationError as e:
        flash(str(e), "error")
    except DocumentParsingError as e:
        flash(f"Could not read file: {str(e)}", "error")
    except NotFoundError:
        flash("Session not found", "error")
        return redirect(url_for('index'))
    except InterviewSimulatorException as e:
        flash("An error occurred processing your CV", "error")
        print(f"Unexpected error in upload_cv: {e}")

    return redirect(url_for('upload_page', session_id=session_id))


@app.route('/session/<int:session_id>/upload-job', methods=['POST'])
def upload_job_description(session_id):

    try:
        job_description = request.form.get('job_description', '')
        
        document_service.upload_job_description(session_id, job_description)
        flash("✓ Job description saved successfully!", "success")
    
    except ValidationError as e:
        flash(str(e), "error")
    
    except NotFoundError:
        flash("Session not found", "error")
        return redirect(url_for('index'))
    except InterviewSimulatorException as e:
        flash("An error occurred saving job description", "error")
        print(f"Unexpected error in upload_job_description: {e}")
    
    return redirect(url_for('upload_page', session_id=session_id))


@app.route('/session/<int:session_id>/interview')
async def interview_page(session_id):
    try:
        session = session_service.get_session(session_id)
        if not session_service.is_ready_for_interview(session_id):
            flash("Please upload your CV and the job description to start the interview.", "warning")
            return redirect(url_for('upload_page', session_id=session_id))

        progress = interview_service.get_interview_progress(session_id)
        if not progress['is_started']:
            await interview_service.start_interview(session_id)
        
        conversation = message_repository.get_conversation(session_id)
        
        return render_template(
            'interview.html',
            session=session,
            conversation=conversation,
            progress=progress
        )
    except NotFoundError:
        abort(404)
    except (ValidationError, AIServiceError) as e:
        flash(str(e), 'error')
        return redirect(url_for('upload_page', session_id=session_id))

@app.route('/session/<int:session_id>/message', methods=['POST'])
def send_message(session_id):
    try:
        answer = request.form.get('answer', '')
        result = interview_service.submit_answer(session_id, answer)
        
        user_message = message_repository.get_conversation(session_id)[-2]
        ai_message = message_repository.get_conversation(session_id)[-1]

        return render_template(
            'fragments/chat_messages.html',
            user_message=user_message,
            ai_message=ai_message,
            progress=result
        )
    except (ValidationError, NotFoundError, AIServiceError) as e:
        return render_template('fragments/error.html', message=str(e))

@app.route('/session/<int:session_id>/complete', methods=['POST'])
async def complete_interview(session_id):
    try:
        await feedback_service.generate_feedback(session_id)
        return redirect(url_for('feedback_page', session_id=session_id))
    except (ValidationError, NotFoundError, AIServiceError) as e:
        flash(str(e), 'error')
        return redirect(url_for('interview_page', session_id=session_id))

@app.route('/session/<int:session_id>/feedback')
def feedback_page(session_id):
    try:
        feedback = feedback_service.get_feedback(session_id)
        session = session_service.get_session(session_id)
        return render_template('feedback.html', feedback=feedback, session=session)
    except NotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)