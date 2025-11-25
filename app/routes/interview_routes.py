from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask import session as flask_session
from ..services.interview_service import InterviewService
from ..services.session_service import SessionService
from ..repositories.session_repository import SessionRepository
from ..repositories.message_repository import MessageRepository
from ..exceptions import ValidationError, NotFoundError, AIServiceError


bp = Blueprint("interview", __name__, url_prefix="/session")


def _get_interview_service():
    from ..extensions import get_ai_client

    session_repo = SessionRepository()
    message_repo = MessageRepository()
    ai_client = get_ai_client()
    return InterviewService(session_repo, message_repo, ai_client)


def _get_session_service():
    return SessionService(SessionRepository())


def _check_session_ownership(session_id):
    my_sessions = flask_session.get("my_sessions", [])
    if session_id not in my_sessions:
        abort(403, "You don't have access to this session")


@bp.route("/<int:session_id>/interview")
def interview_page(session_id):
    _check_session_ownership(session_id)

    try:
        session_service = _get_session_service()
        interview_service = _get_interview_service()

        session = session_service.get_session(session_id)

        if not session_service.is_ready_for_interview(session_id):
            flash(
                "Please upload your CV and the job description to start the interview.",
                "warning",
            )
            return redirect(url_for("document.upload_page", session_id=session_id))

        progress = interview_service.get_interview_progress(session_id)

        if not progress["is_started"]:
            interview_service.start_interview(session_id)

        message_repo = MessageRepository()
        conversation = message_repo.get_conversation(session_id)

        return render_template(
            "interview.html",
            session=session,
            conversation=conversation,
            progress=progress,
        )

    except NotFoundError:
        abort(404)
    except (ValidationError, AIServiceError) as e:
        flash(str(e), "error")
        return redirect(url_for("document.upload_page", session_id=session_id))


@bp.route("/<int:session_id>/message", methods=["POST"])
def send_message(session_id):
    _check_session_ownership(session_id)

    try:
        answer = request.form.get("answer", "")

        interview_service = _get_interview_service()
        result = interview_service.submit_answer(session_id, answer)

        message_repo = MessageRepository()
        conversation = message_repo.get_conversation(session_id)

        if result["is_complete"]:
            user_message = conversation[-1]
            ai_message = None
        else:
            user_message = conversation[-2]
            ai_message = conversation[-1]

        return render_template(
            "fragments/chat_messages.html",
            user_message=user_message,
            ai_message=ai_message,
            progress=result,
            session_id=session_id,
        )

    except (ValidationError, NotFoundError, AIServiceError) as e:
        return render_template("fragments/error.html", message=str(e))
