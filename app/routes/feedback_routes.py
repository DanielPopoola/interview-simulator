from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask import session as flask_session
from ..services.feedback_service import FeedbackService
from ..services.session_service import SessionService
from ..repositories.session_repository import SessionRepository
from ..repositories.message_repository import MessageRepository
from ..repositories.feedback_repository import FeedbackRepository
from ..exceptions import ValidationError, NotFoundError, AIServiceError


bp = Blueprint("feedback", __name__, url_prefix="/session")


def _get_feedback_service():
    from client.ai_client import AIClient
    from client.ai_provider_manager import ProviderManager
    from client.gemini_provider import GeminiProvider
    from client.openrouter_provider import OpenRouterProvider
    import os

    providers = [
        OpenRouterProvider(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            model_name="openai/gpt-oss-20b:free",
        ),
        GeminiProvider(
            api_key=os.getenv("GEMINI_API_KEY", ""), model_name="gemini-2.5-flash"
        ),
    ]

    provider_manager = ProviderManager(providers)
    ai_client = AIClient(provider_manager)

    session_repo = SessionRepository()
    message_repo = MessageRepository()
    feedback_repo = FeedbackRepository()

    return FeedbackService(session_repo, message_repo, feedback_repo, ai_client)


def _get_session_service():
    return SessionService(SessionRepository())


def _check_session_ownership(session_id):
    my_sessions = flask_session.get("my_sessions", [])
    if session_id not in my_sessions:
        abort(403, "You don't have access to this session")


@bp.route("/<int:session_id>/complete", methods=["POST"])
def complete_interview(session_id):
    _check_session_ownership(session_id)

    try:
        feedback_service = _get_feedback_service()
        feedback_service.generate_feedback(session_id)
        return redirect(url_for("feedback.feedback_page", session_id=session_id))
    except (ValidationError, NotFoundError, AIServiceError) as e:
        flash(str(e), "error")
        return redirect(url_for("interview.interview_page", session_id=session_id))


@bp.route("/<int:session_id>/feedback")
def feedback_page(session_id):
    _check_session_ownership(session_id)

    try:
        feedback_service = _get_feedback_service()
        session_service = _get_session_service()

        feedback = feedback_service.get_feedback(session_id)
        session = session_service.get_session(session_id)

        return render_template("feedback.html", feedback=feedback, session=session)
    except NotFoundError:
        abort(404)
