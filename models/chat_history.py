
from datetime import datetime
from sqlite3 import Date
from sqlalchemy import  BigInteger, Column, DateTime, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


class ChatHistory (Base):
    __tablename__ = 'chat_history'
    
    id = Column(BigInteger, primary_key = True, autoincrement = True)
    user_id = Column(Integer, nullable=True)
    messages = Column(String, nullable=True)
    messages_from = Column(Integer, nullable=True)
    reference = Column(JSONB, nullable=True)
    context_answer = Column(String, nullable=True)
    create_time: datetime = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    update_time: datetime = Column(DateTime(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))
    
    def to_dict(self):
        """Converts the SQLAlchemy object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'messages': self.messages,
            'messages_from': self.messages_from,
            'reference': self.reference,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
     