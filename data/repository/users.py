
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.files_model import Files
from models.users import Users


class UsersRepository():
    
    @staticmethod
    def insert_new_user(session: Session , data: Users):
        try:
            session.add(data)
            session.flush()
            return data.id
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
            
            
    @staticmethod
    def get_data_email(session: Session, email: str):
        stmt = (select(Users).where(Users.email == email))
        file_data = session.scalars(stmt).first()
        return file_data