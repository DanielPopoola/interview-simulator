import time

from app.exceptions import AIServiceError
from .ai_provider import AIProvider


class ProviderManager:
    def __init__(self, providers: list[AIProvider]):
        self.providers = providers
        self.fail_count = {p: 0 for p in providers}
        self.open_until = {p: 0 for p in providers}

    def _is_available(self, provider):
        return time.time() >= self.open_until[provider]

    def generate_text(self, prompt):
        last_error = None

        for provider in self.providers:
            if not self._is_available(provider):
                continue

            try:    
                return provider.generate_text(prompt)
            except Exception as e:
                last_error = e
                self.fail_count[provider] += 1

                if self.fail_count[provider] >= 3:
                    self.open_until[provider] = time.time() + 120.0

        raise AIServiceError(f"All providers failed: {last_error}")
