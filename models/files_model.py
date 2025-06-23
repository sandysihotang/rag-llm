from sqlalchemy import TIMESTAMP, BigInteger, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import text


Base = declarative_base()


class Files(Base):
    __tablename__ = 'files'
    
    id = Column(BigInteger(), primary_key = True, autoincrement = True)
    user_id=Column(Integer, nullable=True)
    file_name = Column(String, nullable=True)
    original_file_name = Column(String, nullable=True)
    status =Column(Integer, nullable=True)
    type_data=Column(Integer, nullable=True)
    create_time= Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_time= Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'), onupdate=text('now()'))
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "file_name": self.file_name,
            "original_file_name": self.original_file_name,
            "status": self.status,
            "type_data": self.type_data,
            "create_time": f'{self.create_time}',
            "update_time": f'{self.update_time}'
        }
        

    
     