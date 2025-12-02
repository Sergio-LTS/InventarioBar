# app/routes/web.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .. import crud

router = APIRouter(prefix="/web", tags=["Web"], include_in_schema=False)

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(req: Request):
    return templates.TemplateResponse("home.html", {"request": req})

@router.get("/productos", response_class=HTMLResponse)
async def pagina_productos(req: Request, db: AsyncSession = Depends(get_db)):
    productos = await crud.list_productos(db)
    return templates.TemplateResponse(
        "productos/list.html",
        {"request": req, "productos": productos},
    )
