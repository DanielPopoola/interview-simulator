from flask import Blueprint, render_template


bp = Blueprint("feedback", __name__, url_prefix="/session")


@bp.route("/<int:session_id>/feedback")
def feedback_page(session_id):
    return render_template("feedback.html")
