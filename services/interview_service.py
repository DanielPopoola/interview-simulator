from models import db, Session, Message
from repositories import SessionRepository, MessageRepository
from client.ai_client import AIClient
from exceptions import NotFoundError, ValidationError, AIServiceError
import json

class InterviewService:
    MAX_QUESTIONS = 8

    def __init__(
        self,
        session_repository: SessionRepository,
        message_repository: MessageRepository,
        ai_client: AIClient,
    ):
        self.session_repo = session_repository
        self.message_repo = message_repository
        self.ai_client = ai_client

    def start_interview(self, session_id: int) -> str:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError("Session not found")

        if self.message_repo.get_conversation(session_id):
            raise ValidationError("Interview has already started.")

        task_id = self.ai_client.generate_interview_questions(
            cv_text=session.cv_text,
            job_desc=session.job_description_text,
            job_title=session.job_title,
            company_name=session.company_name,
        )
        
        session.task_id = task_id
        self.session_repo.update(session)
        return task_id

    def get_interview_progress(self, session_id: int) -> dict:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError("Session not found")

        convo = self.message_repo.get_conversation(session_id)
        
        user_messages = [m for m in convo if m.role == "user"]
        question_count = len(user_messages)
        
        is_started = bool(convo)
        is_complete = question_count >= self.MAX_QUESTIONS

        return {
            "is_started": is_started,
            "is_complete": is_complete,
            "question_count": question_count,
            "max_questions": self.MAX_QUESTIONS,
        }

    def submit_answer(self, session_id: int, answer: str) -> str:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError("Session not found")

        if not answer or not answer.strip():
            raise ValidationError("Answer cannot be empty")

        self.message_repo.add_message(session_id, "user", answer)
        
        progress = self.get_interview_progress(session_id)
        if progress["is_complete"]:
            self.message_repo.add_message(
                session_id, "assistant", "Thanks for your answers! The interview is now complete."
            )
            return "complete"

        convo_history = self.message_repo.get_conversation(session_id)
        
        task_id = self.ai_client.generate_followup_question(
            convo_history=convo_history,
            cv_text=session.cv_text,
            job_desc=session.job_description_text,
            question_count=progress['question_count'],
            max_questions=self.MAX_QUESTIONS
        )
        
        session.task_id = task_id
        self.session_repo.update(session)
        return task_id

    def get_task_result(self, task_id: str, session_id: int, type: str):
        result = self.ai_client.get_task_result(task_id)
        if result:
            if type == 'start':
                questions = self.ai_client._parse_json(result, expect_list=True)
                if not (4 <= len(questions) <= 10):
                    raise AIServiceError(f"Unexpected question count: {len(questions)}")
                
                first_question = questions[0]
                self.message_repo.add_message(session_id, "assistant", first_question)
                
                remaining_questions = questions[1:]
                session = self.session_repo.get_by_id(session_id)
                session.remaining_questions = json.dumps(remaining_questions)
                self.session_repo.update(session)
                return {"status": "SUCCESS", "question": first_question}
            elif type == 'answer':
                question = self.ai_client._parse_json(result, expect_list=False)
                self.message_repo.add_message(session_id, "assistant", question)
                return {"status": "SUCCESS", "question": question}
        return {"status": "PENDING"}
