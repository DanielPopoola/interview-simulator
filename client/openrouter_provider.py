import requests
import json
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class OpenRouterProvider:
    def __init__(self, api_key: str, model_name: str = "openai/gpt-oss-20b:free"):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (requests.RequestException, ConnectionError, TimeoutError)
        ),
    )
    def generate_text(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "extra_body": {"reasoning": {"enabled": True}},
        }

        response = requests.post(
            self.endpoint, headers=self._headers, data=json.dumps(payload)
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error: {response.status_code} - {response.text}"
            )

        data = response.json()
        try:
            message = data["choices"][0]["message"]
            text = message.get("content")
        except (KeyError, IndexError):
            raise RuntimeError("Malformed response from OpenRouter API")

        if not text:
            raise RuntimeError("OpenRouter returned empty response")

        return text
