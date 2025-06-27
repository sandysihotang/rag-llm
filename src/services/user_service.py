

from fastapi import HTTPException,status
from data.config.settings import Settings
from cryptography.fernet import Fernet

from data.repository.users import UsersRepository
from models.users import Users

class UserService():
    def __init__(self, settings: Settings) -> None:
        self.session = settings.getConnectionDB()
        self.key_password = settings.get_key_password()
        pass
    
    def register_user(self, email: str, password: str):
        
        try:
            fernet = Fernet(self.key_password)
        except Exception as e:
            raise e
        enc_password = fernet.encrypt(password.encode())
        user = Users(email=email, password=enc_password.decode("utf-8"))
        try:
            user_check = UsersRepository.get_data_email(self.session, email=email)
            if (user_check != None):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email Already Exist")
            new_id = UsersRepository.insert_new_user(self.session, user)
            user.id = new_id
            self.session.commit()
            return user
        except Exception as e:
            print(f'Error: {e}')
            self.session.rollback()
            raise e
    def get_user(self, email:str, password: str):
        try:
            user = UsersRepository.get_data_email(self.session, email=email)
            if(user.id == 0):
                return False, 0
            fernet = Fernet(self.key_password)
            decrypt_password = fernet.decrypt(user.password).decode()
            return password==decrypt_password, user.id
        except Exception as e:
            print(f'Error: {e}')
            raise e
            
        
    