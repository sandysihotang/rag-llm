from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn
from router import chat, users
from router.middleware.middleware import JWTAuthMiddleware
from data.config.settings import Settings
from src.services.document_service import DocumentService


settings = Settings()
document_service = DocumentService(settings=settings)

app = FastAPI()

app.add_middleware(JWTAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(chat.router, prefix="/api", tags=["api"])
app.include_router(users.router,prefix='/user' ,tags=['users'])

@app.get("/")
async def welcome_users():
    return JSONResponse(content={'detail': "welcome to chat repository!"})

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)