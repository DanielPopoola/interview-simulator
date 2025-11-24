from flask import Blueprint, request, redirect, url_for, flash, session as flask_session
from ..services.session_service import SessionService
from ..repositories.session_repository import SessionRepository


bp = Blueprint("session", __name__)

session_repo = SessionRepository()
session_service = SessionService(session_repo)


@bp.route("/")
def index():
    my_session_ids = flask_session.get("my_sessions", [])
    recent_sessions = session_service.get_sessions_by_ids(my_session_ids)[:5]
    return "TODO: render index with recent_sessions"


@bp.route("/session/create", methods=["POST"])
def create_session():
    try:
        job_title = request.form.get("job_title", "")
        company_name = request.form.get("company_name", "")
        new_session = session_service.create_session(job_title, company_name)

        if "my_sessions" not in flask_session:
            flask_session["my_sessions"] = []
            flask_session["my_sessions"].append(new_session.id)

        return redirect(url_for("session.upload_page", session_id=new_session.id))

    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("session.index"))

    except Exception:
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for("session.index"))
