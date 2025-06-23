from pydantic import BaseModel


class Chat(BaseModel):
    message: str
    
class Scrape(BaseModel):
    url: str | None = None
    title: str | None = None
    content: str | None = None
    
class User(BaseModel):
    email: str
    password:str