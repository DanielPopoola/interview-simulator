import json
import re
from app.exceptions import AIServiceError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from utils.prompt_templates import PromptTemplates


class AIClient:
    def __init__(self, provider_manager):
        self.provider_manager = provider_manager

    def generate_first_question(
        self, cv_text, job_desc, job_title, company_name
    ) -> str:
        prompt = PromptTemplates.first_question_generation(
            cv_text=cv_text,
            job_description=job_desc,
            job_title=job_title,
            company_name=company_name,
        )
        text = self._generate(prompt)

        question = re.sub(
            r"^(Question:|Here\'s a question:)\s*", "", text.strip(), flags=re.I
        ).strip("\"'")

        if not question:
            raise AIServiceError("AI returned empty response")

        return question

    def generate_followup_question(
        self, convo_history, cv_text, job_desc, question_count, max_questions=8
    ) -> str:
        formatted = PromptTemplates.format_conversation_history(convo_history)
        prompt = PromptTemplates.followup_question_generation(
            conversation_history=formatted,
            cv_text=cv_text,
            job_description=job_desc,
            question_count=question_count,
            max_questions=max_questions,
        )
        text = self._generate(prompt)
        question = re.sub(
            r"^(Question:|Follow-up:|Here\'s a question:)\s*",
            "",
            text.strip(),
            flags=re.I,
        ).strip("\"'")
        if not question:
            raise AIServiceError("AI returned empty response")
        return question

    def generate_feedback(self, convo_history, cv_text, job_desc, job_title) -> dict:
        formatted = PromptTemplates.format_conversation_history(convo_history)
        prompt = PromptTemplates.feedback_generation(
            conversation_history=formatted,
            cv_text=cv_text,
            job_description=job_desc,
            job_title=job_title,
        )
        feedback = self._parse_json(self._generate(prompt), expect_list=False)

        required = {"score", "strengths", "weaknesses", "cv_improvements"}
        missing = required - feedback.keys()
        if missing:
            raise AIServiceError(f"Feedback missing keys: {missing}")

        score = feedback.get("score")
        if not isinstance(score, int) or not (1 <= score <= 10):
            raise AIServiceError(f"Invalid score: {score}")

        return feedback

    def _generate(self, prompt: str) -> str:
        try:
            return self.provider_manager.generate_text(prompt)
        except Exception as e:
            raise AIServiceError(f"AI generation failed: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(AIServiceError),
    )
    def _parse_json(self, text: str, expect_list: bool):
        text = re.sub(r"```json\s*|```", "", text)
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
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
