from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class GeminiProvider:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        if not api_key:
            raise ValueError("API key is required")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        generation_config = {
            'temperature': temperature,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': max_tokens,
        }

        response = self.client.models.generate_content(
            model=self.model_name, contents=prompt,
            config=generation_config
        )

        if not response.parts:
            raise RuntimeError("Gemini response was blocked or empty")
    
        text = response.text
        if not text:
            raise RuntimeError("Gemini returned empty response")
        
        return text