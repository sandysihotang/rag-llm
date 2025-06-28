
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, select, update
from models.files_model import Files


class FilesRepository():
    
    @staticmethod
    def insert_data_document(session: Session , data: Files):
        try:
            session.add(data)
            session.flush()
            return data.id
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
            
            
    @staticmethod
    def get_data_source(session: Session)->list[Files]:
        data = session.query(Files).where(Files.status == 1).order_by(asc(Files.create_time)).all()
        return data
    
    @staticmethod
    def update_status_file(session: Session, id: int):
        session.query(Files).filter(Files.id == id).update({Files.status : 2}, synchronize_session=False)
        
    @staticmethod
    def get_source_data_by_user_id(session: Session, user_id: int):
        all_source = session.query(Files).filter(Files.user_id == user_id).order_by(desc(Files.create_time)).all()
        return all_source
        
        