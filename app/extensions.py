from flask_sqlalchemy import SQLAlchemy
from client.ai_provider_manager import ProviderManager
from client.gemini_provider import GeminiProvider
from client.openrouter_provider import OpenRouterProvider
from client.ai_client import AIClient
import os


db = SQLAlchemy()

provider_manager = None
ai_client = None


def init_ai_providers(app):
    global provider_manager, ai_client
    openrouter_key = app.config.get('OPENROUTER_API_KEY', '')
    gemini_key = app.config.get('GEMINI_API_KEY', '')

    providers = []

    if openrouter_key:
        providers.append(
            OpenRouterProvider(
                api_key=openrouter_key,
                model_name='openai/gpt-oss-20b:free'
            )
        )
    
    if gemini_key:
        providers.append(
            GeminiProvider(
                api_key=gemini_key,
                model_name='gemini-2.5-flash'
            )
        )

    if not providers:
        app.logger.warning("No AI providers configured! Check your API keys.")
        return
    
    provider_manager = ProviderManager(providers)
    ai_client = AIClient(provider_manager)
    app.logger.info(f"Initialized {len(providers)} AI provider(s)")


def get_ai_client():
    if ai_client is None:
        raise RuntimeError(
            "AI client not initialized. "
            "Did you forget to call init_ai_providers(app)?"
        )
    return ai_client