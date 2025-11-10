from repositories import SessionRepository, MessageRepository
from client.ai_client import AIClient
from exceptions import ValidationError, NotFoundError

class InterviewService:
    MAX_QUESTIONS = 8
    
    def __init__(
        self,
        session_repository: SessionRepository,
        message_repository: MessageRepository,
        ai_client: AIClient
    ):
        self.session_repo = session_repository
        self.message_repo = message_repository
        self.ai_client = ai_client
    
    def start_interview(self, session_id: int) -> str:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")

        if not session.cv_text or not session.job_description_text:
            raise ValidationError("Session is not ready. CV and job description are required.")

        if self.message_repo.count_messages(session_id) > 0:
            raise ValidationError("Interview has already started.")

        first_question = self.ai_client.generate_first_question(
            cv_text=session.cv_text,
            job_desc=session.job_description_text,
            job_title=session.job_title,
            company_name=session.company_name
        )

        self.message_repo.create_message(session_id, "assistant", first_question)
    
        return first_question
    
    def submit_answer(self, session_id: int, answer: str) -> dict:
        if not answer or not answer.strip():
            raise ValidationError("Answer cannot be empty.")

        self.message_repo.create_message(session_id, "user", answer)

        question_count = self.message_repo.count_messages(session_id, role='assistant')
        
        if question_count >= self.MAX_QUESTIONS:
            return {
                'next_question': None,
                'is_complete': True,
                'question_count': question_count
            }

        session = self.session_repo.get_by_id(session_id)
        convo_history = self.message_repo.conversation_to_history(session_id)
        
        next_question = self.ai_client.generate_followup_question(
            convo_history=convo_history,
            cv_text=session.cv_text,
            job_desc=session.job_description_text,
            question_count=question_count,
            max_questions=self.MAX_QUESTIONS
        )
        
        self.message_repo.create_message(session_id, "assistant", next_question)
        
        return {
            'next_question': next_question,
            'is_complete': False,
            'question_count': question_count + 1
        }

    
    def is_interview_complete(self, session_id: int) -> bool:
        question_count = self.message_repo.count_messages(session_id, role='assistant')
        return question_count >= self.MAX_QUESTIONS
    
    def get_interview_progress(self, session_id: int) -> dict:
        question_count = self.message_repo.count_messages(session_id, role='assistant')
        is_started = question_count > 0
        is_complete = self.is_interview_complete(session_id)
        
        return {
            'question_count': question_count,
            'max_questions': self.MAX_QUESTIONS,
            'is_started': is_started,
            'is_complete': is_complete
        }