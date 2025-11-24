from .document_routes import bp as document_bp
from .session_routes import bp as session_bp
from .interview_routes import bp as interview_bp
from .feedback_routes import bp as feedback_bp
from .errors import register_error_handlers


def register_routes(app):
    app.register_blueprint(session_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(document_bp)
    register_error_handlers(app)
