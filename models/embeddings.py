from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text


Base = declarative_base()


class Embeddings (Base):
    __tablename__ = 'embedding'
    
    id = Column(BigInteger, primary_key = True, autoincrement = True)
    page_number = Column(Integer, nullable=True)
    source_file = Column(String, nullable=True)
    files_id = Column(Integer, nullable=True)
    sentence_chunk = Column(String, nullable=True)
    type_source = Column(Integer, nullable=True)
    embedding_data = Column(Vector(1536), nullable=True)
    create_time= Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_time= Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))

    
    
     