from celery import Celery
from dotenv import load_dotenv
import os
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"

celery = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

@celery.task
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
def generate_text_task(prompt: str, api_key: str, model_name: str = "gemini-2.5-flash") -> str:
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model=MODEL_NAME, contents=prompt
    )

    if not response.parts:
        raise RuntimeError("Gemini response was blocked or empty")

    text = response.text
    if not text:
        raise RuntimeError("Gemini returned empty response")
    
    return text