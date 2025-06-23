from http.client import NOT_FOUND
import os
from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from data.config.settings import Settings
from models.chat import Chat, Scrape
from src.services.rag_chatgpt import RagModel
from datetime import datetime

settings = Settings()

model = RagModel(settings=settings)
router = APIRouter()

upload_folder = 'uploads'
if not(os.path.exists(upload_folder)):
    os.mkdir(upload_folder)

ALLOWED_EXTENSIONS = {'pdf'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_new_file_name():
    s = str(datetime.now())
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')


# @router.get('/test-publisher')
# def test_publisher():
#     model.test_nsq()

@router.post('/send_message')
def send_message(request: Request,chat: Chat = Body(...)):
    user_message = chat.message.lower()
    try:
        data = model.ask(user_message, return_answer_only=False, user_id=request.state.user['id'])
        return JSONResponse(content=data)
    except Exception as e:
        raise e

@router.get('/history-message')
def get_history_message(request: Request):
    return model.get_history_message(request.state.user['id'])


@router.post('/upload', status_code=status.HTTP_200_OK)
async def uploads(request: Request,file: UploadFile = File(description="Upload PDF File", media_type="application/pdf")):
    content = await file.read()

    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No File Uploaded")
    if file.filename == '':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Selected File")
     # Check file size (example: 5MB limit)
    file_size = len(await file.read()) 
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File is too large")
    
    return await model.processing_file(original_file_name=file.filename, content=content, user_id= request.state.user['id'])

@router.post('/scraping')
async def scrape_url(scraping: Scrape = Body(...)):
    return await model.get_text_from_url(scraping.url)


@router.get('/source')
async def get_source(request: Request):
    return await model.get_source(request.state.user['id'])


@router.post('/process-data')
async def process_data_url(request: Request, scraping: Scrape = Body(...)):
    return await model.processing_data(scraping.title, scraping.content, request.state.user['id'])

