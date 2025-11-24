import time

from exceptions import AIServiceError


class ProviderManager:
    def __init__(self, providers):
        self.providers = providers
        self.fail_count = {p: 0 for p in providers}
        self.open_until = {p: 0 for p in providers}

    def _is_available(self, provider):
        return time.time() >= self.open_until[provider]

    def generate(self, prompt):
        last_error = None

        for provider in self.providers:
            if not self._is_available(provider):
                continue

            try:
                return provider.generate(prompt)
            except Exception as e:
                last_error = e
                self.fail_count[provider] += 1

                if self.fail_count[provider] >= 3:
                    self.open_until[provider] = time.time() + 120

        raise AIServiceError(f"All providers failed: {last_error}")
