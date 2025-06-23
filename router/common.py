from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def chat(request: Request):
    return templates.TemplateResponse("chat.html",{"request": request})

@router.get("/admin")
async def admin(request: Request):
    return templates.TemplateResponse("admin.html",{"request": request})

