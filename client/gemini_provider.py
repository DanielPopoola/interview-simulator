from celery_worker import generate_text_task

class GeminiProvider:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.model_name = model_name

    def generate_text_async(self, prompt: str) -> str:
        """
        Calls the Celery task to generate text asynchronously.
        """
        task = generate_text_task.delay(prompt, self.api_key, self.model_name)
        return task.id