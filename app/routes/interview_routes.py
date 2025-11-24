from flask import Blueprint, render_template, abort
from ..repositories.session_repository import SessionRepository
from ..repositories.message_repository import MessageRepository
from ...client.ai_client import AIClient
from ...client.ai_provider_manager import ProviderManager
from ...client.openrouter_provider import OpenRouterProvider


bp = Blueprint("interview", __name__, url_prefix="/session")


# provider wiring — keep light here
providers = [OpenRouterProvider()]
provider_manager = ProviderManager(providers)
ai_client = AIClient(provider_manager)


# lightweight service instances
session_repo = SessionRepository()
message_repo = MessageRepository()


@bp.route("/<int:session_id>/interview")
def interview_page(session_id):
    # minimal example — integrate with your session_service and interview_service
    try:
        # permission check moved to decorator in a future step
        progress = {"is_started": False}
        # start interview if needed
        return render_template(
            "interview.html", session_id=session_id, progress=progress
        )
    except Exception:
        abort(404)
