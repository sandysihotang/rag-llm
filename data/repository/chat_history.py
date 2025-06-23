from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from models.chat_history import ChatHistory

class ChatHistoryRepository:
    @staticmethod
    def insert_new_chat(session: Session, data: ChatHistory):
        try:
            session.add(data)
            session.flush()
            return data
        except Exception as e:
            session.rollback()
            raise e
        
    @staticmethod
    def get_history_message(session: Session, user_id: int):
        try:
            data= session.query(ChatHistory).where(ChatHistory.user_id == user_id).order_by(desc(ChatHistory.create_time)).all()
            return data
        except Exception as e:
            session.rollback()
            raise e
    
    @staticmethod
    def get_history_message_for_context(session: Session, user_id: int, limit: int = 2):
        try:
            data = session.query(ChatHistory).where(ChatHistory.user_id == user_id).order_by(desc(ChatHistory.create_time)).limit(limit=limit).all()
            return data
        except Exception as e:
            session.rollback()
            raise e