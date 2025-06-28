from fastapi import Body, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPBearer,HTTPBasic
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime, timedelta
import jwt 
import os
from dotenv import load_dotenv

from data.config.settings import Settings
from models.chat import User
from src.services.user_service import UserService
load_dotenv(dotenv_path='./.env')

router = APIRouter()
security = HTTPBearer()
SECRET_KEY = os.getenv(key='SECRET_KEY')
ALGORITHM = os.getenv(key='ALGORITHM')
TOKEN_EXPIRY_MINUTES = 30

settings = Settings()



user_service = UserService(settings=settings)

def generate_token(id: int):
    payload = {
        "id": id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(user:User = Body(...), session: Session = Depends(settings.getConnectionDB())): 
    try:
        is_valid, user_id = user_service.get_user(email=user.email, password=user.password, session=session)
        if(is_valid == False):
            raise HTTPException(status_code=400, detail="Incorrect credentials")
        token = generate_token(user_id)
        content = {'token': token}
        return JSONResponse(content=content, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Authorization user Failed")

@router.post("/register")
def register(user:User = Body(...), session: Session = Depends(settings.getConnectionDB())):
    try:
        new_user = user_service.register_user(email=user.email, password=user.password, session= session)
        token = generate_token(new_user.id)
        content = {'token': token}
        return JSONResponse(content=content, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'{e}')
