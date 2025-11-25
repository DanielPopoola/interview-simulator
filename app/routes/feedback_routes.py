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
    from ..extensions import get_ai_client

    session_repo = SessionRepository()
    message_repo = MessageRepository()
    feedback_repo = FeedbackRepository()
    ai_client = get_ai_client()
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
