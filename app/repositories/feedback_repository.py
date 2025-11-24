from app.models import db, Feedback


class FeedbackRepository:
    def create_feedback(
        self,
        session_id: int,
        score: int,
        strengths: str,
        weaknesses: str,
        cv_improvements: str,
    ) -> Feedback:
        feedback = Feedback(
            session_id=session_id,
            interview_score=score,
            strengths=strengths,
            weaknesses=weaknesses,
            cv_improvements=cv_improvements,
        )
        db.session.add(feedback)
        db.session.commit()
        db.session.refresh(feedback)
        return feedback

    def get_feedback(self, session_id: int) -> Feedback | None:
        return Feedback.query.filter_by(session_id=session_id).first()

    def has_feedback(self, session_id: int) -> bool:
        return db.session.query(
            Feedback.query.filter_by(session_id=session_id).exists()
        ).scalar()
