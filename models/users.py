from sqlalchemy.sql.expression import text
from sqlalchemy import TIMESTAMP, BigInteger, Column, String
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()


class Users (Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key = True, autoincrement = True)
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    create_time= Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_time= Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

     