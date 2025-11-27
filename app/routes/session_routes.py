from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask import session as flask_session
from ..services.session_service import SessionService
from ..repositories.session_repository import SessionRepository
from ..exceptions import ValidationError


bp = Blueprint("session", __name__)


def _get_session_service():
    return SessionService(SessionRepository())


@bp.route("/")
def index():
    my_session_ids = flask_session.get("my_sessions", [])

    session_service = _get_session_service()
    recent_sessions = session_service.get_sessions_by_ids(my_session_ids)
    recent_sessions = recent_sessions[:5]
    return render_template("index.html", recent_sessions=recent_sessions)


@bp.route("/session/create", methods=["POST"])
def create_session():
    try:
        job_title = request.form.get("job_title", "")
        company_name = request.form.get("company_name", "")

        session_service = _get_session_service()
        new_session = session_service.create_session(job_title, company_name)

        my_sessions = flask_session.get("my_sessions", [])
        my_sessions.append(new_session.id)
        flask_session["my_sessions"] = my_sessions  # Reassign to trigger save
        flask_session.modified = True

        return redirect(url_for("document.upload_page", session_id=new_session.id))

    except ValidationError as e:
        flash(str(e), "error")
        return redirect(url_for("session.index"))

    except Exception as e:
        print(f"Error creating session: {e}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for("session.index"))
