
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db              # tu dependency actual
from .. import crud, schemas
from ..supabase_client import upload_image

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/web", tags=["Web"])

@router.get("/productos")
async def pagina_productos(request: Request, db: AsyncSession = Depends(get_db)):
    productos = await crud.list_productos(db)
    return templates.TemplateResponse(
        "productos.html",
        {"request": request, "productos": productos},
    )

@router.post("/productos/nuevo")
async def crear_producto_web(
    request: Request,
    nombre: str = Form(...),
    categoria: str = Form(None),
    marca: str = Form(None),
    cantidad: int = Form(...),
    precio_venta: float = Form(...),
    imagen: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    url = await upload_image(imagen) if imagen else None
    data = schemas.ProductoCreate(
        nombre=nombre,
        categoria=categoria,
        marca=marca,
        cantidad=cantidad,
        precio_venta=precio_venta,
        imagen_url=url,
    )
    await crud.create_producto(db, data)
    return RedirectResponse(url="/web/productos", status_code=status.HTTP_302_FOUND)
