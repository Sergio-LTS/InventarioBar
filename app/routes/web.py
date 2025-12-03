# app/routes/web.py
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .. import crud, schemas
from ..services.supabase_storage import upload_image_to_supabase  # usamos SOLO este

router = APIRouter(prefix="/web", tags=["Web"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/productos", response_class=HTMLResponse)
async def pagina_productos(request: Request, db: AsyncSession = Depends(get_db)):
    productos = await crud.list_productos(db)
    return templates.TemplateResponse(
        "productos.html",
        {"request": request, "productos": productos},
    )

@router.get("/productos/nuevo", response_class=HTMLResponse)
async def form_producto(request: Request):
    return templates.TemplateResponse("productos_form.html", {"request": request})

@router.post("/productos/nuevo")
async def crear_producto_web(
    request: Request,
    nombre: str = Form(...),
    categoria: str = Form(...),
    marca: str = Form(...),
    cantidad: int = Form(...),
    precio_venta: float = Form(...),
    imagen: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    imagen_url = None
    if imagen and imagen.filename:
        try:
            imagen_url = await upload_image_to_supabase(imagen, folder="productos")
        except Exception as e:
            # Si falla la subida, seguimos sin imagen para no romper el flujo
            print(f"[WARN] No se pudo subir imagen: {e}")

    data = schemas.ProductoCreate(
        nombre=nombre,
        categoria=categoria,
        marca=marca,
        cantidad=cantidad,
        precio_venta=precio_venta,
        imagen_url=imagen_url,
    )
    await crud.create_producto(db, data)
    return RedirectResponse(url="/web/productos", status_code=303)
