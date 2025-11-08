from models import db, Message, Session
from exceptions import ValidationError, NotFoundError


class MessageRepository:
    def create_message(self, session_id: int, role: str, content: str) -> Message:
        session = Session.query.get(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")
        
        valid_roles = ['assistant', 'user']
        if role not in valid_roles:
            raise ValidationError(f"Invalid role assignment. Valid roles are {' '.join(valid_roles)}")
        
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
        )
        db.session.add(message)
        db.session.commit()
        db.session.refresh(message)
        return message
    

    def create_messages_bulk(self, session_id: int, messages: list[dict]) -> list[Message]:
        new_messages = [Message(session_id=session_id, **msg) for msg in messages]
        db.session.bulk_save_objects(new_messages, return_defaults=True)
        db.session.commit()
        return new_messages

    def get_conversation(self, session_id: int) -> list[Message]:
        return Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.asc()).all()

    def count_messages(self, session_id: int, role: str = None) -> int:
        query = Message.query.filter_by(session_id=session_id)
        if role:
            query = query.filter_by(role=role)
        return query.count()

    def conversation_to_history(self, session_id: int) -> list[dict]:
        messages = self.get_conversation(session_id)
        return [{"role": m.role, "content": m.content} for m in messages]