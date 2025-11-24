from flask import redirect, url_for, flash
from ..exceptions import ValidationError, NotFoundError, AIServiceError


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(e):
        flash(str(e), "error")
        return redirect(url_for("session.index"))

    @app.errorhandler(NotFoundError)
    def handle_notfound(e):
        return ("Not Found", 404)

    @app.errorhandler(AIServiceError)
    def handle_ai_error(e):
        flash("AI error: " + str(e), "error")
        return redirect(url_for("session.index"))
