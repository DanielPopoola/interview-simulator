import json
import re
from exceptions import AIServiceError
from utils.prompt_templates import PromptTemplates
from .ai_provider import AIProvider
from celery.result import AsyncResult

class AIClient:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def generate_interview_questions(self, cv_text, job_desc, job_title, company_name) -> str:
        prompt = PromptTemplates.interview_question_generation(
            cv_text=cv_text,
            job_description=job_desc,
            job_title=job_title,
            company_name=company_name,
        )
        return self._generate(prompt)
    
    def generate_followup_question(self, convo_history, cv_text, job_desc, question_count, max_questions=8) -> str:
        formatted = PromptTemplates.format_conversation_history(convo_history)
        prompt = PromptTemplates.followup_question_generation(
            conversation_history=formatted,
            cv_text=cv_text,
            job_description=job_desc,
            question_count=question_count,
            max_questions=max_questions,
        )
        return self._generate(prompt)
    
    def generate_feedback(self, convo_history, cv_text, job_desc, job_title) -> str:
        formatted = PromptTemplates.format_conversation_history(convo_history)
        prompt = PromptTemplates.feedback_generation(
            conversation_history=formatted,
            cv_text=cv_text,
            job_description=job_desc,
            job_title=job_title,
        )
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        try:
            return self.provider.generate_text_async(prompt=prompt)
        except Exception as e:
            raise AIServiceError(f"Generation failed: {e}")

    def get_task_result(self, task_id: str):
        result = AsyncResult(task_id)
        if result.ready():
            if result.successful():
                return result.get()
            else:
                raise AIServiceError(f"Task failed: {result.info}")
        else:
            return None

    def _parse_json(self, text: str, expect_list: bool):
        text = re.sub(r'```json\s*|```', '', text)
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if not match:
            raise AIServiceError("No JSON structure found in response")

        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as e:
            raise AIServiceError(f"Invalid JSON: {e}")

        if expect_list and not isinstance(data, list):
            raise AIServiceError("Expected JSON array")
        if not expect_list and not isinstance(data, dict):
            raise AIServiceError("Expected JSON object")

        return data
