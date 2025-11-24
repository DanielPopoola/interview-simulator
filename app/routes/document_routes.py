from flask import Blueprint, request, redirect, url_for, flash
from flask import session as flask_session
from ..services.document_service import DocumentService
from ..repositories.session_repository import SessionRepository
from ..repositories.file_repository import FileRepository
from ..exceptions import ValidationError, NotFoundError, DocumentParsingError


bp = Blueprint("document", __name__, url_prefix="/session")


def _get_document_service():
    from flask import current_app

    session_repo = SessionRepository()
    file_repo = FileRepository(current_app.config["UPLOAD_FOLDER"])
    return DocumentService(session_repo, file_repo)


def _check_session_ownership(session_id):
    my_sessions = flask_session.get("my_sessions", [])
    if session_id not in my_sessions:
        from flask import abort

        abort(403, "You don't have access to this session")


@bp.route("/<int:session_id>/upload")
def upload_page(session_id):
    _check_session_ownership(session_id)

    try:
        from ..services.session_service import SessionService
        from ..repositories.session_repository import SessionRepository

        session_service = SessionService(SessionRepository())
        session = session_service.get_session(session_id)

        from flask import render_template

        return render_template("upload.html", session=session)
    except NotFoundError:
        from flask import abort

        abort(404)


@bp.route("/<int:session_id>/upload-cv", methods=["POST"])
def upload_cv(session_id):
    _check_session_ownership(session_id)

    try:
        file = request.files.get("cv_file")

        if not file:
            raise ValidationError("No file was uploaded")

        document_service = _get_document_service()
        document_service.upload_cv(session_id, file)

        flash("CV uploaded and processed successfully!", "success")

    except ValidationError as e:
        flash(str(e), "error")
    except DocumentParsingError as e:
        flash(f"Could not read file: {str(e)}", "error")
    except NotFoundError:
        flash("Session not found", "error")
        return redirect(url_for("session.index"))
    except Exception as e:
        flash("An error occurred processing your CV", "error")
        print(f"Unexpected error in upload_cv: {e}")

    return redirect(url_for("document.upload_page", session_id=session_id))


@bp.route("/<int:session_id>/upload-job", methods=["POST"])
def upload_job_description(session_id):
    _check_session_ownership(session_id)

    try:
        job_description = request.form.get("job_description", "")

        document_service = _get_document_service()
        document_service.upload_job_description(session_id, job_description)

        flash("Job description saved successfully!", "success")

    except ValidationError as e:
        flash(str(e), "error")
    except NotFoundError:
        flash("Session not found", "error")
        return redirect(url_for("session.index"))
    except Exception as e:
        flash("An error occurred saving job description", "error")
        print(f"Unexpected error in upload_job_description: {e}")

    return redirect(url_for("document.upload_page", session_id=session_id))
